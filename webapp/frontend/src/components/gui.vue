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
          <div class="graph-container">
            <div v-for="label in labels" :key="label">
              <div class="graph-label">{{ label }}</div>
              <div class="graph">
                <!-- Display graphs here -->
              </div>
            </div>
          </div>
        </div>
        <div v-else>
          <div class="no-results">No results for {{ findNameForContainer(selectedContainer)}}. Run the Tests below!</div>
          <div v-if="labels.length > 0">
            <div class="title-container">
              <div class="checkbox-title">Parameters</div>
              <div class="slider-title">Accuracy</div>
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
            <button class="run-tests-button" :class="{ 'disabled': !isRunButtonActive }" @click="runTests">Run Tests
            </button>
          </div>
        </div>
      </div>
      <div v-else class="empty-results">
        Run tests to display results
      </div>
    </div>
    <button class="add-docker-button" @click="openAddDockerDialog">Add Docker Container</button>
  </div>
</template>

<script>
export default {
  data() {
    return {
      dockerList: [], // 2d List of Docker containers [0] is name and [1] is unique id
      selectedContainer: null, // Selected Docker container
      testResultsAvailable: false, // Boolean indicating if test results are available
      dockerListLoaded: false,
      score: 0, // Robustness score
      labels: [], // Array of labels for the boxes
      checkboxes: [], // Array to store the selected checkbox labels
      sliderValues: [], // Add sliderValues property
      defaultSliderValue: 1,
    };
  },
  created() {
    // Execute loadDockerContainers method before creating the component
    this.loadDockerContainers();
    this.loadTransformationLabels();
  },
  methods: {
    async loadTransformationLabels() {
      try {
        const response = await this.$axios.get('/api/available-transformations'); // Update the URL with the correct backend URL
        this.labels = response.data; // Set the labels array with the received data
        this.initializeCheckboxes()
        this.initializeSliderValues()
      } catch (error) {
        console.error(error);
      }

    },
    initializeCheckboxes() {
      this.checkboxes = Array.from({length: this.labels.length}, () => 0);
    },
    initializeSliderValues() {
      this.sliderValues = Array.from({length: this.labels.length}, () => this.defaultSliderValue);
    },
    updateCheckboxes(value, index) {
      this.checkboxes[index] = value;
    },
    updateSliderValue(value, index) {
      // Update the slider value in the sliderValues array
      this.sliderValues[index] = value;
      //this.updateRunButtonStatus();
    },
    async loadDockerContainers() {
      try {
        const response = await this.$axios.get('/api/docker-containers'); // Update the URL with the correct backend URL
        this.dockerList = response.data;
        console.log(this.dockerList)
        this.dockerListLoaded = true; // Set the flag to indicate that the data has been loaded
      } catch (error) {
        console.error(error);
      }
    },
    selectContainer(container) {
      this.selectedContainer = container;
      console.log(this.selectedContainer)
      this.loadTestResults(container);
    },
    findNameForContainer(container_id){
      return this.dockerList.find(arr => arr[1] === container_id)[0];
    },
    async loadTestResults(container) {
      // Implement your logic to load test results based on the selected container
      const response = await this.$axios.post('/api/load-container-results', {
        container: container,
      });
      if(response.status=200&&response.data==null){
        this.testResultsAvailable=false;
      }else if(reponse.status=200&&response.data!=null){
        this.testResultsAvailable=true;
      }else{
        console.error(response)
      }


    },
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

        const response = await this.$axios.post('/api/run-tests', {
          image_path: 'storage/Assets/website.png', // Replace with the actual image path value
          transformations: transformationArray,
          container_name: containerName,
        }); // Update the URL with the correct backend URL and endpoint

        // Handle the response as per your requirements
        // Update the testResultsAvailable, score, and labels data properties based on the received data
        this.testResultsAvailable = true;
        this.score = response.data.score;
        // Update other necessary data based on the received response
      } catch (error) {
        console.error(error);
      }
    },
    async openAddDockerDialog() {
      try {
        // Open file dialog to select a .tar file
        const fileInput = document.createElement('input');
        fileInput.type = 'file';
        fileInput.accept = '.tar';
        fileInput.addEventListener('change', async () => {
          const file = fileInput.files[0];
          if (!file) return;

          // Ask the user for the container name
          const containerName = prompt('Enter the name for the Docker container');
          if (!containerName) return;

          try {
            // Create form data to send the file and container name to the backend
            const formData = new FormData();
            formData.append('file', file);
            formData.append('name', containerName);

            // Send request to add the Docker container
            const response = await this.$axios.post('/api/add-docker-container', formData, {
              headers: {
                'Content-Type': 'multipart/form-data',
              },
            });

            // Check the response for success and update the dockerList
            if (response.data.message === 'Docker container added successfully') {
              await this.loadDockerContainers();
            } else {
              console.error(response.data.message);
            }
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
    },
  },
  computed: {
    isRunButtonActive() {
      return this.checkboxes.includes(1);
    },
  },
};
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

.add-docker-button {
  position: fixed;
  bottom: 20px;
  right: 20px;
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
</style>