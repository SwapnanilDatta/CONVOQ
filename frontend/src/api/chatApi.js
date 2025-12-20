const BASE_URL = "http://127.0.0.1:8000";

export const uploadChatFile = async (file) => {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${BASE_URL}/upload`, {
    method: "POST",
    body: formData,
  });
  return response.json();
};

export const analyzeReplyTime = async (file) => {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${BASE_URL}/analyze/reply-time`, {
    method: "POST",
    body: formData,
  });
  return response.json();
};

export const analyzeSentiment = async (file) => {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${BASE_URL}/analyze/sentiment`, {
    method: "POST",
    body: formData,
  });
  return response.json();
};