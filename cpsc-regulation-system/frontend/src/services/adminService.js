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

export const adminService = {
  async getStats() {
    const response = await api.get('/admin/stats');
    return response.data;
  },

  async getUsers(skip = 0, limit = 100) {
    const response = await api.get('/admin/users', {
      params: { skip, limit }
    });
    return response.data;
  },

  async updateUserRole(userId, newRole) {
    const response = await api.put(`/admin/users/${userId}/role`, { new_role: newRole });
    return response.data;
  },

  async activateUser(userId) {
    const response = await api.put(`/admin/users/${userId}/activate`);
    return response.data;
  },

  async deactivateUser(userId) {
    const response = await api.put(`/admin/users/${userId}/deactivate`);
    return response.data;
  },

  async getActivityLogs(userId = null, skip = 0, limit = 100) {
    const response = await api.get('/admin/activity-logs', {
      params: { user_id: userId, skip, limit }
    });
    return response.data;
  },

  async runPipeline(urls) {
    const response = await api.post('/admin/pipeline/run', { urls });
    return response.data;
  },

  async getPipelineStatus() {
    const response = await api.get('/admin/pipeline/status');
    return response.data;
  },

  async resetPipeline() {
    const response = await api.post('/admin/pipeline/reset');
    return response.data;
  },

  async runAnalysis(level) {
    const response = await api.post('/admin/analysis/run', null, {
      params: { level }
    });
    return response.data;
  },

  async runClustering(level, nClusters = null) {
    const response = await api.post('/admin/clustering/run', null, {
      params: { level, n_clusters: nClusters }
    });
    return response.data;
  }
};