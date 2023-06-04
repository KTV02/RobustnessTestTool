import './assets/main.css';
import { createApp } from 'vue';
import App from './App.vue';
import axios from 'axios';

const app = createApp(App);

// Set the base URL for Axios requests
axios.defaults.baseURL = 'http://localhost:5000';

// Set Axios as a global property in Vue
app.config.globalProperties.$axios = axios;

app.mount('#app');