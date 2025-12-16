import axios from "axios";

// ✅ Use Vite environment variable
const BASE_URL = import.meta.env.VITE_BACKEND_URL;

if (!BASE_URL) {
  throw new Error("❌ VITE_BACKEND_URL is not defined");
}

// Create a configured instance of axios
const apiClient = axios.create({
  baseURL: `${BASE_URL}/api`,
});

// --- API Functions ---

// 1. Send Image for Emotion Detection
export const predictEmotion = async (imageFile: File) => {
  const formData = new FormData();
  formData.append("file", imageFile);

  const response = await apiClient.post("/predict/emotion", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });

  return response.data;
};

// 2. Get Advice from the Gita
export const getGitaAdvice = async (condition: string) => {
  const response = await apiClient.get(
    `/get_advice?condition=${encodeURIComponent(condition)}`
  );
  return response.data;
};

// 3. Send Message to AI Therapist
export const sendChatMessage = async (
  message: string,
  emotion: string,
  history: any[]
) => {
  const response = await apiClient.post("/chat", {
    message,
    emotion,
    history,
  });
  return response.data;
};
