<template>
  <div class="container">
    <div class="sidebar">
      <div v-if="dockerListLoaded && dockerList.length > 0" class="docker-list">
        <div v-for="(item, index) in dockerList" :key="item[1]" @click="selectContainer(item[1])" class="docker-item">
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
          <button class="run-tests-button" @click="runTests">Run Tests</button>
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
    };
  },
  created() {
    // Execute loadDockerContainers method before creating the component
    this.loadDockerContainers();
  },
  methods: {
    async loadDockerContainers() {
      try {
        const response = await this.$axios.get('/api/docker-containers'); // Update the URL with the correct backend URL
        this.dockerList = response.data;
        this.dockerListLoaded = true; // Set the flag to indicate that the data has been loaded
        console.log(this.dockerList)
        console.log(this.dockerList.length)

      } catch (error) {
        console.error(error);
      }
    },
    selectContainer(container) {
      this.selectedContainer = container;
      this.loadTestResults(container);
    },
    async loadTestResults(container) {
      try {
        const response = await this.$axios.post('/api/run-tests', {
          container: container.name
        }); // Update the URL with the correct backend URL and endpoint
        this.testResultsAvailable = true;
        this.score = response.data.score;
        // Update other necessary data based on the received response
      } catch (error) {
        console.error(error);
      }
    },
    runTests() {
      // Make a request to the Python backend to run tests for the selected Docker container
      // Update the testResultsAvailable, score, and labels data properties based on the received data
    },
    openAddDockerDialog() {
      // Show a dialog for the user to provide a .tar file and container name
      // Send the selected file and container name to the Python backend for processing
      // Update the dockerList data property if the operation is successful
    },
  },
};
</script>

<style scoped>


.docker-item {
  color: #000000;
  display: flex;
  align-items: center;
  justify-content: center; /* Center the text horizontally */
  padding: 10px 0; /* Add vertical padding for spacing */
  border-bottom: 1px solid #ccc; /* Add border-bottom to all Docker items */
}

.docker-item:last-child {
  border-bottom: none; /* Remove border-bottom for the last Docker item */
}

.docker-item-text {
  font-family: Arial, sans-serif;
  font-size: 14px;
  text-align: center; /* Center the text vertically */
}

.container {
  display: flex;
}

.sidebar {
  width: 20%;
  background-color: #f2f2f2;
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
  color: #fff;
  border: none;
  cursor: pointer;
}

.add-docker-button {
  position: fixed;
  bottom: 20px;
  right: 20px;
  padding: 10px 20px;
  background-color: #007bff;
  color: #fff;
  border: none;
  cursor: pointer;
}
</style>