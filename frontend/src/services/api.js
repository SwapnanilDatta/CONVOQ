import { API_BASE_URL } from '../utils/constants';
import axios from 'axios';

// Fast Analysis
export const getCompleteAnalysis = async (file, token, dateFormat = 'auto') => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('date_format', dateFormat);

  const response = await axios.post(`${API_BASE_URL}/analyze/fast`, formData, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
};

// Deep Analysis
export const getDeepAnalysis = async (cacheKey, analysisId, token) => {
  const response = await axios.post(`${API_BASE_URL}/analyze/deep`, {
    cache_key: cacheKey,
    analysis_id: analysisId
  }, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  });

  return response.data;
};

export const getHistory = async (token) => {
  const response = await fetch(`${API_BASE_URL}/history`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) throw new Error('Failed to fetch history');
  return response.json();
};
