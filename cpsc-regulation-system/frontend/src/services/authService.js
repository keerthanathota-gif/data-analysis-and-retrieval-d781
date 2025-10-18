import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle token expiration
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authService = {
  async login(username, password) {
    const response = await api.post('/auth/login', { username, password });
    return response.data;
  },

  async adminLogin(username, password) {
    const response = await api.post('/auth/admin-login', { username, password });
    return response.data;
  },

  async signup(userData) {
    const response = await api.post('/auth/signup', userData);
    return response.data;
  },

  async getCurrentUser() {
    const response = await api.get('/auth/me');
    return response.data;
  },

  async updateUser(userData) {
    const response = await api.put('/auth/me', userData);
    return response.data;
  },

  async logout() {
    const response = await api.post('/auth/logout');
    return response.data;
  }
  ,

  async oauthStart(provider) {
    const response = await api.get('/auth/oauth/start', { params: { provider } });
    return response.data; // { provider, state }
  },

  async oauthCallback(payload) {
    const response = await api.post('/auth/oauth/callback', payload);
    return response.data;
  }
};