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
      <div v-else class="empty-results">
        Run tests to display results
      </div>
    </div>
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
    selectContainer(container) {
      // Set the selectedContainer data property to the clicked Docker container
      // Make a request to the Python backend to check if test results are available for the selected container
      // Update the testResultsAvailable, score, and labels data properties based on the received data
    },
    runTests() {
      // Make a request to the Python backend to run tests for the selected Docker container
      // Update the testResultsAvailable, score, and labels data properties based on the received data
    },
  },
};
</script>

<style scoped>
.container {
  display: flex;
  background-color: #f8f8f8; /* Change background color here */
}

.sidebar {
  width: 20%;
  background-color: #fff; /* Change background color here */
  padding: 20px;
}

.docker-list {
  height: calc(100vh - 60px);
  overflow-y: auto;
}

.docker-item {
  color: blue; /* Change text color here */
  margin-bottom: 10px;
  cursor: pointer;
}
.empty-results {
  color: black; /* Set the text color to a light color (e.g., white) */
}

.empty-list {
  text-align: center;
  color: black; /* Change text color here */
  margin-top: 10px;
}

.main-panel {
  flex-grow: 1;
  padding: 20px;
  background-color: #ffffff; /* Change background color here */
}

/* Rest of the styles... */

</style>

