<template>
  <div class="container">
    <div class="sidebar">
      <div class="docker-list" v-if="dockerList.length > 0">
        <div v-for="item in dockerList" :key="item.name" @click="selectContainer(item)">
          {{ item.name }}
        </div>
      </div>
      <div class="empty-list" v-else>
        No Docker containers available
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
          <div class="no-results">No results present, run the tests</div>
          <button class="run-tests-button" @click="runTests">Run Tests</button>
        </div>
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
      score: 0, // Robustness score
      labels: [], // Array of labels for the boxes
    };
  },
  mounted() {
    // Fetch initial Docker container list from the backend
    this.loadDockerContainers();
  },
  methods: {
    async loadDockerContainers() {
      try {
        const response = await this.$axios.get('/api/docker-containers');
        this.dockerList = response.data;
      } catch (error) {
        console.error(error);
      }
    },
    openFileDialog() {
      // Open file dialog to select a .tar file
      // Send the selected file to the Python backend for processing
      // Update the dockerList data property if the operation is successful
    },
    selectContainer(container) {
      // Set the selectedContainer data property to the clicked Docker container
      // Make a request to the Python backend to check if test results are available for the selected container
      // Update the testResultsAvailable, score, and labels data properties based on the received data
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
.container {
  display: flex;
}

.sidebar {
  width: 20%;
  background-color: #f2f2f2;
  padding: 20px;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
}

.docker-list {
  flex-grow: 1;
  overflow-y: auto;
}

.empty-list {
  text-align: center;
  color: #888;
  margin-top: 10px;
}

.main-panel {
  width: 80%;
  padding: 20px;
}

.add-docker-button {
  position: fixed;
  top: 20px;
  right: 20px;
}
</style>