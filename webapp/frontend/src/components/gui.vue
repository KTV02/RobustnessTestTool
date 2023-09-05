<template>
  <div class="container">
    <div class="sidebar">
      <div v-if="dockerListLoaded && dockerList.length > 0" class="docker-list">
        <div v-for="(item, index) in dockerList" :key="item[1]" @click="selectContainer(item[1])"
             :class="{ 'docker-item': true, 'selected': item[1] === selectedContainer }">
          <div class="docker-item-text">{{ item[0] }}</div>
        </div>
      </div>
      <div v-else class="empty-list">
        {{ dockerListLoaded ? 'No Docker containers available' : 'Loading Docker containers...' }}
      </div>
    </div>
    <div class="main-panel">
      <div v-if="selectedContainer">
        <div v-if="testResultsAvailable">
          <div class="score">{{ score }}</div>
          <div>
            <div v-for="(label, index) in currentLabels.slice(1)" :key="index">
              <h3>{{ label }}</h3>
              <canvas :id="'chart-' + label" width="400" height="300"></canvas>
            </div>
          </div>
        </div>
        <div v-else>
          <div class="no-results">No results for {{ findNameForContainer(selectedContainer) }}. Run the Tests below!
          </div>
          <button @click="setTestImage">Upload Test Images</button>

          <br>
          <button @click="setGroundTruth">Upload Ground Truths</button>
          <br><br>
          <!-- Info Box -->
          <div class="info-box">
            <h4>Image Formatting Guidelines:</h4>
            <ul>
              <li>Images must be JPG or PNG</li>
              <li><strong>Format for Images&GroundTruths:</strong> <br> imagename, imagename1,...,imagenameX</li>
              <li>Images&GroundTruths must be inside their respective .tar folder</li>

            </ul>
          </div>
          <br>
          <div v-if="labels.length > 0">
            <div class="title-container">
              <div class="checkbox-title">Parameters</div>
              <div class="slider-title">Sampling Steps</div>
            </div>

            <div v-for="(label, index) in labels" :key="index">
              <div class="checkbox-container">
                <div class="checkbox-label">
                  <input type="checkbox" :id="'checkbox-' + index" v-model="checkboxes" :value="label"
                         @change="updateCheckboxes($event.target.checked ? 1 : 0, index)">
                  <label :for="'checkbox-' + index">{{ label }}</label>
                </div>
                <div class="slider-container">
                  <input type="range" min="1" max="10" v-model="sliderValues[index]"
                         @input="updateSliderValue($event.target.value, index)"/>
                </div>
              </div>
            </div>
            <button class="run-tests-button"
                    :class="{ 'disabled': !isRunButtonActive||isTransformingImages||!testImageSet||!groundTruthSet}"
                    @click="runTests">Run Tests
            </button>
            <div v-if="isTransformingImages">
              <p>Transforming Testdata...</p>
            </div>
            <div v-if="transformSuccess">
              <p>Transforming Testdata &#x2705;</p>
            </div>
            <div v-if="transformFailure">
              <p>Transforming Testdata &#x2717;</p>
            </div>
            <div v-if="checkingImage">
              <p>Checking if image already present...</p>
            </div>
            <div v-if="isBuildingDocker">
              <p>Building Docker...</p>
            </div>
            <div v-if="buildingSuccess">
              <p>Building Docker &#x2705;</p>
            </div>
            <div v-if="buildingFailure">
              <p>Building Docker &#x2717;</p>
            </div>
            <div v-if="imageAlreadyPresent">
              <p>Docker Image already present on Server &#x2705;</p>
            </div>
            <div v-if="isRunningTests">
              <p>Running Tests...</p>
            </div>
            <loader v-if="isTransformingImages|| isBuildingDocker || isRunningTests"/>
          </div>
        </div>
      </div>
      <div v-else class="empty-results">
        Run tests to display results
      </div>
    </div>
    <div class="button-container">
      <button class="add-docker-button" :class="{ 'disabled': isTransformingImages||isRunningTests}"
              @click="openAddDockerDialog">Add Docker Container
      </button>
      <button class="delete-docker-button"
              :class="{ 'disabled': isTransformingImages||isRunningTests||selectedContainer==null}"
              @click="openDeleteDockerDialog">Delete Container
      </button>
    </div>

  </div>
</template>

<script>
import Loader from 'vue-spinner/src/ClipLoader.vue'
import {Chart, registerables} from 'chart.js';

Chart.register(...registerables);

export default {
  components: {
    Loader,
  },
  data() {
    return {
      isTransformingImages: false,
      dockerList: [], // 2d List of Docker containers [0] is name and [1] is unique id
      selectedContainer: null, // Selected Docker container
      testResultsAvailable: false, // Boolean indicating if test results are available
      dockerListLoaded: false,
      score: 0, // Robustness score
      labels: [], // Array of labels for the boxes
      checkboxes: [], // Array to store the selected checkbox labels
      sliderValues: [], // Add sliderValues property
      defaultSliderValue: 1,
      testImage: "",
      groundTruth: "",
      testImageSet: false,
      groundTruthSet: false,
      isRunningTests: false,
      transformSuccess: false,
      buildingFailure: false,
      transformFailure: false,
      isBuildingDocker: false,
      buildingSuccess: false,
      tarDataUrl: "",
      imageAlreadyPresent: false,
      checkingImage: false,
      currentTransformations: [],
      numberOfMetrics: 4,
      currentLabels: [],
      currentCharts: [],
      currentMetrics: [],
    };
  },
  created() {
    // Execute loadDockerContainers method before creating the component
    this.loadDockerContainers();
    this.loadTransformationLabels();
  },
  methods: {
    async setTestImageFrontend(event) {
      const file = event.target.files[0];
      if (file) {
        // Create a new FileReader instance
        const reader = new FileReader();

        // Set up the onload event handler
        reader.onload = () => {
          // Access the data URL result
          this.testImage = reader.result;
          console.log("Testimage: " + this.testImage)
        };

        // Read the file and convert it to a data URL
        reader.readAsDataURL(file);
      }
    },
    async openDeleteDockerDialog() {
      if (!this.isRunningTests || !this.isTransformingImages || this.selectedContainer != null) {
        await this.loadDockerContainers()

        const userConfirmed = window.confirm("Really delete this container?");

        if (userConfirmed) {
          try {
            console.log(this.selectedContainer)
            const response = await this.$axios.delete('/api/delete-docker-container', {
              data: {
                container: this.selectedContainer,
              }
            }); // Update the URL with the correct backend endpoint
            let success = response.data;
            console.log(success);
            if (success == null) {
              alert("No response from Backend! Operation failed")
            } else if (success) {
              this.selectedContainer = null
              await this.loadDockerContainers()
              alert("container successfully deleted")

            } else {
              alert(success)
            }

            // Perform any other actions you'd like to take upon successful deletion,
            // such as updating the UI
          } catch (error) {
            console.error(error);

            // Perform any other actions you'd like to take upon failure,
            // such as showing an error message to the user
          }
        } else {
          console.log("User cancelled the deletion.");
        }
        // Logic for deleting the Docker container
      } else {
        console.log("Delete button deactivated right now! Check conditions")
      }
    }
    ,
    async setTestImage(event) {
      const container = this.selectedContainer
      try {
        const response = await this.$axios.put('/api/set-test-images', {
          container: container,
        }); // Update the URL with the correct backend URL
        let success = response.data;
        console.log(success)
        if (success === "success") {
          this.testImageSet = true
        } else {
          alert(success)
        }
      } catch (error) {
        console.error(error);
      }
    },
    async setGroundTruth(event) {
      const container = this.selectedContainer
      try {
        const response = await this.$axios.put('/api/set-ground-truth', {
          container: container,
        }); // Update the URL with the correct backend URL
        let success = response.data;
        if (success === "success") {
          this.groundTruthSet = true
        } else {
          alert(success)
        }
      } catch (error) {
        console.error(error);
      }
    },
    plotData() {
      //this.currentTransformations=Array.from(this.currentTransformations)
      console.log(this.currentTransformations)
      console.log(typeof this.currentTransformations)
      let metricCounter = 0
      this.currentTransformations.forEach((transformation, index) => {
        let values = transformation.map(subArray => subArray[0]);
        let steps = Array.from({length: values.length + 1}, (_, index) => index);
        if (this.currentLabels[index] != "base") {
          const chartData = {
            labels: steps,
            datasets: [
              {
                label: 'Data',
                data: values,
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderColor: 'rgba(75, 0, 192, 1)',
                borderWidth: 1,
              },
            ],
          };
          let metricString = "Metrics not available"
          //check if metrics are available and correct amount of metrics
          if (this.currentMetrics != null && this.currentMetrics.length % this.numberOfMetrics === 0) {
            metricString = 'Average:' + this.currentMetrics[metricCounter * this.numberOfMetrics] + ' Standard Deviation:' + this.currentMetrics[(metricCounter + 1) * this.numberOfMetrics] + ' Median:' + this.currentMetrics[(metricCounter + 2) * this.numberOfMetrics] + ' IQR:' + this.currentMetrics[(metricCounter + 3) * this.numberOfMetrics]
          }

          const chartOptions = {
            responsive: true,
            plugins: {
              subtitle: {
                display: true,
                text: metricString
              }
            }
          };
          console.log(`chart-${this.currentLabels[index]}`)
          this.$nextTick(() => {
            const cc = new Chart(`chart-${this.currentLabels[index]}`, {
              type: 'line', // You can choose the chart type based on your requirement
              data: chartData,
              options: chartOptions,
            });
            this.currentCharts.push(cc)
          });
        }
        metricCounter++
      });
    },
    async loadTransformationLabels() {
      try {
        const response = await this.$axios.get('/api/available-transformations'); // Update the URL with the correct backend URL
        this.labels = response.data; // Set the labels array with the received data
        this.initializeCheckboxes()
        this.initializeSliderValues()
      } catch (error) {
        console.error(error);
      }

    }
    ,
    initializeCheckboxes() {
      this.checkboxes = Array.from({length: this.labels.length}, () => 0);
    }
    ,
    initializeSliderValues() {
      this.sliderValues = Array.from({length: this.labels.length}, () => this.defaultSliderValue);
    }
    ,
    updateCheckboxes(value, index) {
      this.checkboxes[index] = value;
    }
    ,
    updateSliderValue(value, index) {
      // Update the slider value in the sliderValues array
      this.sliderValues[index] = value;
      //this.updateRunButtonStatus();
    }
    ,
    async loadDockerContainers() {
      try {
        const response = await this.$axios.get('/api/get-docker-containers'); // Update the URL with the correct backend URL
        this.dockerList = response.data;
        console.log(this.dockerList)
        this.dockerListLoaded = true; // Set the flag to indicate that the data has been loaded
      } catch (error) {
        console.error(error);
      }
    }
    ,
    selectContainer(container) {

      this.selectedContainer = container;
      console.log(this.selectedContainer)
      console.log(document.readyState)
      this.currentCharts.forEach(chart => {
        chart.destroy();
      });
      this.currentCharts = []; // Clear the array
      this.loadTestResults(container);


    }
    ,
    findNameForContainer(container_id) {
      return this.dockerList.find(arr => arr[1] === container_id)[0];
    }
    ,
    async loadTestResults(container) {
      // Implement your logic to load test results based on the selected container
      console.log(container)
      const response = await this.$axios.post('/api/load-container-results', {
        container: container,
      });
      if (response.status === 200 && (response.data == null || response.data == "False")) {
        this.testResultsAvailable = false;
      } else if (response.status === 200 && response.data != null) {
        console.log("response data")
        console.log(response.data)
        this.currentTransformations = JSON.parse(response.data["data"]);
        this.currentLabels = JSON.parse(response.data["labels"])
        this.currentMetrics = JSON.parse(response.data["metrics"])
        console.log(this.currentLabels)
        console.log(typeof this.currentLabels)
        this.testResultsAvailable = true;
        this.plotData()
      } else {
        console.error(response)
      }


    }
    ,
    async runTests() {

      try {
        //This takes the indexes of labels and sliderValues only when the corresponding checkbox is checked
        const transformationArray = this.checkboxes.reduce((result, checkbox, index) => {
          if (checkbox === 1) {
            result.push([this.labels[index], this.sliderValues[index]]);
          }
          return result;
        }, []);
        const containerName = this.selectedContainer;
        const testImageUrl = this.testImage

        //Transform Testimage
        this.isTransformingImages = true;
        const transformResponse = await this.$axios.post('/api/transform-images', {
          transformations: transformationArray,
          container_name: containerName,
        }); // Update the URL with the correct backend URL and endpoint
        this.isTransformingImages = false;

        console.log(transformResponse.status);
        if (transformResponse.status === 200) {
          let responseContent = transformResponse.data
          console.log(responseContent)
          if (responseContent == null || (typeof responseContent === 'string' && String(responseContent) !== 'True') || (typeof responseContent === 'string' && String(responseContent) === 'False')) {
            alert(String(responseContent))
            this.transformFailure = true;
            throw new Error(String(responseContent))
          }
          this.transformSuccess = true;

          this.checkingImage = true;
          //check if image for tar already exists on server
          const image_response = await this.$axios.post('/api/image-exists', {
            container_name: containerName,
          });
          this.checkingImage = false;
          console.log(image_response)
          if (image_response.data === "False") {
            this.isBuildingDocker = true;
            await new Promise(resolve => setTimeout(resolve, 3000));
            const buildResponse = await this.$axios.post('/api/build-docker', {
              container_name: containerName,
            });
            this.isBuildingDocker = false;
            let responseContent = transformResponse.data
            if (responseContent == null || !(buildResponse.status === 200) || typeof responseContent === 'string' || !responseContent) {
              alert("Error while transforming images")
              this.transformFailure = true;
              throw new Error(String(responseContent))
            }
            this.buildingSuccess = true;


          } else if (image_response.data === "True") {
            this.imageAlreadyPresent = true;
            this.isRunningTests = true;
            await new Promise(resolve => setTimeout(resolve, 3000));
            const testResponse = await this.$axios.post('/api/run-tests', {
              container_name: containerName,
            });
            this.isRunningTests = false;
            if (testResponse.status === 200) {
              this.testResultsAvailable = true;
              this.score = testResponse.data.score;
              await this.loadTestResults(containerName)
              // Update other necessary data based on the received response

            } else {
              alert("An Error occurred while running Tests")
            }
            await new Promise(resolve => setTimeout(resolve, 3000));

          } else {
            alert("An Error occurred while building docker container")
          }
        } else {
          alert("An Error occurred while transforming Images")
        }


      } catch (error) {
        console.error(error);
      }
    }
    ,
    async openAddDockerDialog() {
      if (!this.isRunningTests || !this.isTransformingImages) {
        try {
          // Ask the user for the container name
          const containerName = prompt('Enter the name for the Docker container');
          if (!containerName) return;
          console.log("The entered container name is: "+containerName)
          // Send the FormData object to the server using Axios
          const response = await this.$axios.put('/api/add-docker-container',{
                name: containerName,
          });
          // Handle the response

          // Check the response for success and update the dockerList
          alert(response.data.message)
          await this.loadDockerContainers();
        } catch (error) {
          alert("Adding container failed!")
          console.error(error);
        }

      } else {
        console.log("Add Docker Button deactivated right now! Check conditions")
      }

    }
    ,
    async openAddDockerDialogFrontend() {
      //LEGACY CODE - Frontend MODE
      if (!this.isRunningTests || !this.isTransformingImages) {
        try {


          // Open file dialog to select a .tar file
          const fileInput = document.createElement('input');
          fileInput.type = 'file';
          fileInput.accept = '.tar, .txt';
          fileInput.addEventListener('change', async () => {
            const file = fileInput.files[0];
            if (!file) return;

            // Ask the user for the container name
            const containerName = prompt('Enter the name for the Docker container');
            if (!containerName) return;

            try {
              // Create a FormData object and append the file to it
              const formData = new FormData();

              //TEMPORARY

              formData.append('tarfile', file);

              // Append the container name to the FormData object
              formData.append('container_name', containerName);
              console.log(formData)
              // Send the FormData object to the server using Axios
              const response = await this.$axios.put('/api/add-docker-container', formData, {
                headers: {
                  'Content-Type': 'multipart/form-data',
                },
              });
              // Handle the response

              // Check the response for success and update the dockerList
              alert(response.data.message)
              await this.loadDockerContainers();
            } catch (error) {
              alert("Adding container failed!")
              console.error(error);
            }
          });

          // Trigger the file input dialog
          fileInput.click();
        } catch (error) {
          console.error(error);
        }
      } else {
        console.log("Add Docker Button deactivated right now! Check conditions")
      }
    }
    ,
  }
  ,
  computed: {
    isRunButtonActive() {
      return this.checkboxes.includes(1);
    }
    ,
  }
  ,
}
;
</script>
<style scoped>
.docker-item {
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 10px 0;
  border-bottom: 1px solid #ccc;
}

.docker-item.selected {
  background-color: #6f6e6e;
}

.docker-item:last-child {
  border-bottom: none;
}

.docker-item-text {
  font-family: Arial, sans-serif;
  font-size: 14px;
  text-align: center;
  cursor: pointer;
}

.container {
  display: flex;
}

.sidebar {
  width: 20%;
  background-color: #333333;
//padding: 20px;
}

.docker-list {
  margin-bottom: 20px;
}

.empty-list {
  color: #999999;
}

.main-panel {
  width: 80%;
  padding: 20px;
}

.empty-results {
  color: #999999;
  text-align: center;
  font-size: 20px;
}

.no-results {
  margin-bottom: 20px;
}

.run-tests-button {
  padding: 10px 20px;
  background-color: #007bff;
  color: #ffffff;
  border: none;
  cursor: pointer;
}

.run-tests-button.disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.checkbox-container {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  flex: 1;
}

.slider-container {
  flex: 1;
  margin-left: 8px;
}

.title-container {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.checkbox-title,
.slider-title {
  color: blue;
  flex: 1;
  font-weight: bold;
}

.checkbox-title {
  flex: 1;
}

.slider-title {
  flex: 1;
  text-align: right;
}

input[type="range"] {
  width: 100%;
}

input[type="checkbox"] {
  margin-right: 8px;
}

.delete-docker-button {
  background-color: red;
  color: white;
  border: none;
  padding: 10px 20px;
  margin: 5px;
  cursor: pointer;
}

.add-docker-button {
  background-color: #007bff;
  color: white;
  border: none;
  cursor: pointer;
  padding: 10px 20px;
  margin: 5px;
}

.button-container {
  display: inline-block;
  position: fixed;
  bottom: 20px;
  right: 20px;
}

.add-docker-button.disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.delete-docker-button.disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}


</style>