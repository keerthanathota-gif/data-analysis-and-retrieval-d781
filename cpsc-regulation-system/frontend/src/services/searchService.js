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

export const searchService = {
  async searchRegulations(query, level = 'all', topK = 20) {
    const response = await api.post('/search/query', {
      query,
      level,
      top_k: topK
    });
    return response.data;
  },

  async findSimilarSections(name, searchType = 'section', topK = 20) {
    const response = await api.get(`/search/similar/${name}`, {
      params: { search_type: searchType, top_k: topK }
    });
    return response.data;
  },

  async getSectionDetails(sectionId) {
    const response = await api.get(`/search/section/${sectionId}`);
    return response.data;
  },

  async getSectionsList(skip = 0, limit = 50) {
    const response = await api.get('/search/sections', {
      params: { skip, limit }
    });
    return response.data;
  }
};