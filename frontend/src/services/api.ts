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

export interface RoutingMetadata {
  provider_used: string;
  task_type: string;
  latency_ms: number;
  fallback_used: boolean;
  fallback_provider: string | null;
  pii_scrubbed: boolean;
  pii_types: string[];
  error: string | null;
}

export interface ChatResponse {
  response: string;
  report: PsychReport;
  text_emotion: EmotionLabel[] | null;
  fusion_risk_score: number | null;
  remedy: RemedyData | null;
  routing: RoutingMetadata | null;
}

export interface TextAnalysisResponse {
  emotions: EmotionLabel[];
  dominant: string;
  crisis_risk: number;
  crisis_triggered: boolean;
}

export interface HealthResponse {
  status: string;
  version: string;
  orchestrator_enabled?: boolean;
  llm_local?: { provider: string; reachable: boolean; model: string };
  llm_cloud?: { provider: string; reachable: boolean; model: string };
  llm_provider?: string;
  llm_reachable?: boolean;
  llm_model?: string;
  distilbert_loaded: boolean;
  knowledge_index_ready?: boolean;
}

export interface PatientPreferences {
  user_id: string;
  preferred_tone: string;
  verbosity: string;
  framework_preference: string;
  topics_to_avoid: string[];
  engagement_score: number;
  last_updated: string | null;
}

export interface PatientProgress {
  user_id: string;
  total_sessions: number;
  first_session: string | null;
  last_session: string | null;
  current_risk_level: string;
  emotion_trend: Array<{ date: string; emotion: string }>;
  risk_trend: Array<{ date: string; risk: string; score: number; fusion_score: number | null }>;
  snapshots: Array<{
    snapshot_date: string;
    period_start: string | null;
    period_end: string | null;
    avg_risk_score: number;
    dominant_emotions: string[];
    sessions_count: number;
    improvement_score: number;
    summary: string;
  }>;
  summary: string;
}

export interface OrchestratorStatus {
  orchestrator_enabled: boolean;
  local: { provider: string; available: boolean; model: string; base_url: string };
  cloud: { provider: string; available: boolean; model: string; base_url: string };
  stats: {
    total_requests: number;
    local_requests: number;
    cloud_requests: number;
    fallback_count: number;
    pii_scrub_count: number;
    avg_local_latency_ms: number;
    avg_cloud_latency_ms: number;
    local_errors: number;
    cloud_errors: number;
  };
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
  history: Array<{ role: string; content: string }>,
  user_id?: string
): Promise<ChatResponse> => {
  const response = await apiClient.post("/chat", {
    message,
    emotion,
    history,
    user_id,
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

// 5. Standalone text emotion + crisis analysis
export const analyzeText = async (
  text: string
): Promise<TextAnalysisResponse> => {
  const response = await apiClient.post("/analyze/text", { text });
  return response.data;
};

// 6. Health check
export const getHealth = async (): Promise<HealthResponse> => {
  const response = await apiClient.get("/health");
  return response.data;
};

// 7. Patient Progress
export const getPatientProgress = async (userId: string): Promise<PatientProgress> => {
  const response = await apiClient.get(`/patient/${userId}/progress`);
  return response.data;
};

export const generateProgressSnapshot = async (userId: string): Promise<void> => {
  await apiClient.post(`/patient/${userId}/snapshot`);
};

// 8. Patient Preferences
export const getPatientPreferences = async (userId: string): Promise<PatientPreferences> => {
  const response = await apiClient.get(`/patient/${userId}/preferences`);
  return response.data;
};

export const updatePatientPreferences = async (
  userId: string,
  update: {
    preferred_tone?: string;
    verbosity?: string;
    framework_preference?: string;
    topics_to_avoid?: string[];
  }
): Promise<void> => {
  await apiClient.put(`/patient/${userId}/preferences`, update);
};

// 9. Session Feedback
export const submitSessionFeedback = async (
  userId: string,
  feedback: { rating: number; comment?: string; message_id?: string }
): Promise<void> => {
  await apiClient.post(`/patient/${userId}/feedback`, feedback);
};

// 10. Orchestrator Status
export const getOrchestratorStatus = async (): Promise<OrchestratorStatus> => {
  const response = await apiClient.get("/orchestrator/status");
  return response.data;
};

