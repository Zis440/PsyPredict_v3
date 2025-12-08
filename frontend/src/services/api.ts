import axios from 'axios';

// Create a configured instance of axios
const apiClient = axios.create({
  baseURL: '/api', // We only need '/api' because of the proxy above!
  headers: {
    'Content-Type': 'application/json',
  },
});

// --- API Functions ---

// 1. Send Image for Emotion Detection
export const predictEmotion = async (imageFile: File) => {
  const formData = new FormData();
  formData.append('file', imageFile);

  const response = await apiClient.post('/predict/emotion', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data; // Returns { emotion: "happy", confidence: 99.9 }
};

// 2. Get Advice from the Gita
export const getGitaAdvice = async (condition: string) => {
  const response = await apiClient.get(`/get_advice?condition=${condition}`);
  return response.data;
};

// 3. Send Message to AI Therapist
export const sendChatMessage = async (message: string, emotion: string, history: any[]) => {
  const response = await apiClient.post('/chat', {
    message,
    emotion,
    history
  });
  return response.data; // Returns { response: "Hello, I am PsyPredict..." }
};