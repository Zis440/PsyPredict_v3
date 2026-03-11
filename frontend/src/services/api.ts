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

// --- Types ---

export interface EmotionLabel {
  label: string;
  score: number;
}

export interface CrisisResource {
  name: string;
  contact: string;
  available: string;
}

export interface PsychReport {
  risk_classification: "MINIMAL" | "LOW" | "MODERATE" | "HIGH" | "CRITICAL";
  emotional_state_summary: string;
  behavioral_inference: string;
  cognitive_distortions: string[];
  suggested_interventions: string[];
  confidence_score: number;
  crisis_triggered: boolean;
  crisis_resources: CrisisResource[] | null;
  service_degraded: boolean;
}

export interface RemedyData {
  condition: string;
  symptoms: string;
  treatments: string;
  medications: string;
  dosage: string;
  gita_remedy: string;
}

export interface ChatResponse {
  response: string;
  report: PsychReport;
  text_emotion: EmotionLabel[] | null;
  fusion_risk_score: number | null;
  remedy: RemedyData | null;
}

export interface TextAnalysisResponse {
  emotions: EmotionLabel[];
  dominant: string;
  crisis_risk: number;
  crisis_triggered: boolean;
}

export interface HealthResponse {
  status: string;
  ollama_reachable: boolean;
  ollama_model: string;
  distilbert_loaded: boolean;
  version: string;
}

// --- API Functions ---

// 1. Send Image for Emotion Detection (unchanged)
export const predictEmotion = async (imageFile: File) => {
  const formData = new FormData();
  formData.append("file", imageFile);

  const response = await apiClient.post("/predict/emotion", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });

  return response.data;
};

// 2. Get Remedy / Advice (unchanged)
export const getGitaAdvice = async (condition: string) => {
  const response = await apiClient.get(
    `/get_advice?condition=${encodeURIComponent(condition)}`
  );
  return response.data;
};

// 3. Send Message to AI Therapist (standard)
export const sendChatMessage = async (
  message: string,
  emotion: string,
  history: Array<{ role: string; content: string }>
): Promise<ChatResponse> => {
  const response = await apiClient.post("/chat", {
    message,
    emotion,
    history,
  });
  return response.data;
};

// 4. Stream Message to AI Therapist
export async function* streamChatMessage(
  message: string,
  emotion: string,
  history: Array<{ role: string; content: string }>
): AsyncIterableIterator<string> {
  const controller = new AbortController();
  // 300-second timeout — llama3 on CPU can take 2-3 min to generate a full response
  const timeoutId = setTimeout(() => controller.abort(), 300_000);

  let response: Response;
  try {
    response = await fetch(`${BASE_URL}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, emotion, history, stream: true }),
      signal: controller.signal,
    });
  } catch (err: any) {
    clearTimeout(timeoutId);
    if (err?.name === "AbortError") {
      throw new Error("Request timed out after 300 seconds. The model may be overloaded.");
    }
    throw err;
  }

  if (!response.ok || !response.body) {
    clearTimeout(timeoutId);
    throw new Error(`Stream request failed with status ${response.status}`);
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  try {
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      yield decoder.decode(value, { stream: true });
    }
  } finally {
    clearTimeout(timeoutId);
    reader.releaseLock();
  }
}

// 4. Standalone text emotion + crisis analysis (new)
export const analyzeText = async (
  text: string
): Promise<TextAnalysisResponse> => {
  const response = await apiClient.post("/analyze/text", { text });
  return response.data;
};

// 5. Health check (new)
export const getHealth = async (): Promise<HealthResponse> => {
  const response = await apiClient.get("/health");
  return response.data;
};
