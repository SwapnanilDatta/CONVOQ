import { API_BASE_URL } from '../utils/constants';

// export const uploadFile = async (file) => {
//   const formData = new FormData();
//   formData.append('file', file);

//   const response = await fetch(`${API_BASE_URL}/upload`, {
//     method: 'POST',
//     body: formData
//   });

//   if (!response.ok) {
//     throw new Error('Upload failed');
//   }

//   return response.json();
// };

import axios from 'axios';

export const getCompleteAnalysis = async (file, token) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await axios.post(`${API_BASE_URL}/complete`, formData, {
    headers: {
    
      'Authorization': `Bearer ${token}`, 
      'Content-Type': 'multipart/form-data',
    },
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

export const getUsageStats = async (token) => {
  const response = await fetch(`${API_BASE_URL}/usage`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) throw new Error('Failed to fetch usage stats');
  return response.json();
};