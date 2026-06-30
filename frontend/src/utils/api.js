import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const dashboardAPI = {
  getSummary: (datasetId) => api.get(`/api/dashboard/summary${datasetId ? `?dataset_id=${datasetId}` : ''}`),
};

export const uploadAPI = {
  upload: (file, onUploadProgress) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/api/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress,
    });
  },
};

export const predictAPI = {
  getMetrics: () => api.get('/api/predict/metrics'),
  retrain: () => api.post('/api/predict/train'),
};

export const recommendAPI = {
  getRecommendations: (datasetId) => api.get(`/api/recommendations${datasetId ? `?dataset_id=${datasetId}` : ''}`),
  getDistribution: (datasetId) => api.get(`/api/recommendations/distribution${datasetId ? `?dataset_id=${datasetId}` : ''}`),
  analyzePoint: (pointData) => api.post('/api/recommendations/analyze', pointData),
};

export const mapAPI = {
  getHotspots: (datasetId) => api.get(`/api/map/hotspots${datasetId ? `?dataset_id=${datasetId}` : ''}`),
  getDistricts: (datasetId) => api.get(`/api/map/districts${datasetId ? `?dataset_id=${datasetId}` : ''}`),
};

export const historyAPI = {
  getHistory: () => api.get('/api/history'),
  deleteDataset: (id) => api.delete(`/api/history/${id}`),
};

export const chatAPI = {
  sendMessage: (question, sessionId = 'default', selectedLocation = null) => api.post('/api/chat', { question, session_id: sessionId, selected_location: selectedLocation }),
  getHistory: (sessionId = 'default') => api.get(`/api/chat/history?session_id=${sessionId}`),
  clearHistory: (sessionId = 'default') => api.delete(`/api/chat/history?session_id=${sessionId}`),
};

export const reportAPI = {
  downloadReport: (datasetId) => {
    return axios({
      url: `${API_BASE_URL}/api/report/download${datasetId ? `?dataset_id=${datasetId}` : ''}`,
      method: 'GET',
      responseType: 'blob', // important for files
    });
  },
};

export default api;
