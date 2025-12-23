import { API_BASE_URL } from '../utils/constants';

export const uploadFile = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE_URL}/upload`, {
    method: 'POST',
    body: formData
  });

  if (!response.ok) {
    throw new Error('Upload failed');
  }

  return response.json();
};

export const getCompleteAnalysis = async (file) => {
  const formData = new FormData();
  // 'file' must match the key name in your Postman screenshot
  formData.append('file', file); 

  const response = await fetch(`${API_BASE_URL}/complete`, {
    method: 'POST',
    // DO NOT add headers: { 'Content-Type': 'multipart/form-data' }
    // Let the browser set it so it includes the correct "boundary"
    body: formData,
  });

  if (!response.ok) {
    const errorBody = await response.json();
    throw new Error(errorBody.detail || 'Analysis failed');
  }

  return response.json();
};