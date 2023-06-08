<template>
  <div class="container">
    <div class="sidebar">
      <div v-if="dockerListLoaded && dockerList.length > 0" class="docker-list">
        <div v-for="(item, index) in dockerList" :key="item[1]" @click="selectContainer(item[1])" :class="{ 'docker-item': true, 'selected': item[1] === selectedContainer }">
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
          <div class="no-results">No results present for {{ selectedContainer.name }}</div>
          <div v-if="labels.length > 0">
            <div v-for="(label, index) in labels" :key="index">
              <input type="checkbox" :id="'checkbox-' + index" v-model="selectedCheckboxes" :value="label" @change="updateRunButtonStatus">
              <label :for="'checkbox-' + index">{{ label }}</label>
            </div>
            <button class="run-tests-button" :class="{ 'disabled': !isRunButtonActive }" @click="runTests">Run Tests</button>
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
      dockerList: [], // List of Docker containers
      selectedContainer: null, // Selected Docker container
      testResultsAvailable: false, // Boolean indicating if test results are available
      dockerListLoaded: false,
      score: 0, // Robustness score
      labels: [], // Array of labels for the boxes
      selectedCheckboxes: [], // Array to store the selected checkbox labels
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
      } catch (error) {
        console.error(error);
      }
    },
    async loadDockerContainers() {
      try {
        const response = await this.$axios.get('/api/docker-containers'); // Update the URL with the correct backend URL
        this.dockerList = response.data;
        this.dockerListLoaded = true; // Set the flag to indicate that the data has been loaded
      } catch (error) {
        console.error(error);
      }
    },
    selectContainer(container) {
      this.selectedContainer = container;
      this.loadTestResults(container);
    },
    async loadTestResults(container) {
      // Implement your logic to load test results based on the selected container
    },
    async runTests() {
      try {
        const transformations = this.selectedCheckboxes;
        const response = await this.$axios.post('/api/run-tests', {
          image_path: 'Assets/website.png', // Replace with the actual image path value
          transformations,
          container_name: this.selectedContainer.name,
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
    openAddDockerDialog() {
      // Show a dialog for the user to provide a .tar file and container name
      // Send the selected file and container name to the Python backend for processing
      // Update the dockerList data property if the operation is successful
    },
  },
  computed: {
    isRunButtonActive() {
      return this.selectedCheckboxes.length > 0;
    },
  },
};
</script>
<style scoped>
.docker-item {
  color: #ffffff; /* Change the text color to white */
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
  background-color: #333333; /* Change the sidebar background color to dark gray */
  padding: 20px;
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
  color: #ffffff; /* Change the text color of the button to white */
  border: none;
  cursor: pointer;
}

.add-docker-button {
  position: fixed;
  bottom: 20px;
  right: 20px;
  padding: 10px 20px;
  background-color: #007bff;
  color: #ffffff; /* Change the text color of the button to white */
  border: none;
  cursor: pointer;
}
.run-tests-button.disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}


input[type="checkbox"] {
  margin-right: 8px;
}
</style>