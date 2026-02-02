import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const apiService = {
  // Upload CSV file
  uploadCSV: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post('/upload/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Get upload history (last 5 datasets)
  getHistory: async () => {
    const response = await api.get('/history/');
    return response.data;
  },

  // Get specific dataset details
  getDataset: async (datasetId) => {
    const response = await api.get(`/datasets/${datasetId}/`);
    return response.data;
  },

  // Delete a dataset
  deleteDataset: async (datasetId) => {
    const response = await api.delete(`/datasets/${datasetId}/delete/`);
    return response.data;
  },

  // Generate PDF report with authentication
  generateReport: async (datasetId, username, password) => {
    const response = await api.post(
      `/report/${datasetId}/`,
      { username, password },
      { responseType: 'blob' }
    );
    return response.data;
  },

  // Get latest summary
  getLatestSummary: async () => {
    const response = await api.get('/latest/');
    return response.data;
  },
};

export default apiService;
