import axios from 'axios';

// Create axios instance with default config
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:5001',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Default API key for development
const DEFAULT_API_KEY = 'dev-key-bf2790480a957082962da276a43f652e';

// Request interceptor to add API key
api.interceptors.request.use(
  (config) => {
    const apiKey = localStorage.getItem('apiKey') || DEFAULT_API_KEY;
    if (apiKey) {
      config.headers['X-API-Key'] = apiKey;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('apiKey');
      localStorage.removeItem('sessionToken');
    }
    return Promise.reject(error);
  }
);

// API Methods
export const authAPI = {
  authenticate: async (apiKey) => {
    const response = await api.post('/api/auth', { api_key: apiKey });
    return response.data;
  },
};

export const alertAPI = {
  sendBusinessAlert: async (data) => {
    const response = await api.post('/api/send_business', data);
    return response.data;
  },
  
  sendLeisureAlert: async (data) => {
    const response = await api.post('/api/send_leisure', data);
    return response.data;
  },
};

export const groupAPI = {
  getGroups: async () => {
    const response = await api.get('/api/groups');
    return response.data;
  },
};

export const scriptAPI = {
  getScripts: async () => {
    const response = await api.get('/api/scripts');
    return response.data;
  },
};

export default api; 