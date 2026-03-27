"""
schemas.py — PsyPredict Pydantic Data Models
All request/response bodies are validated via these schemas.
No unstructured dicts pass through the API layer.
"""
from __future__ import annotations
from typing import List, Optional, Any, Dict
from enum import Enum
from pydantic import BaseModel, Field, field_validator
import re


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class RiskLevel(str, Enum):
    MINIMAL = "MINIMAL"
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"


# ---------------------------------------------------------------------------
# Shared Sub-models
# ---------------------------------------------------------------------------

class ConversationMessage(BaseModel):
    role: MessageRole
    content: str


class EmotionLabel(BaseModel):
    label: str
    score: float = Field(ge=0.0, le=1.0)


class CrisisResource(BaseModel):
    name: str
    contact: str
    available: str = "24/7"


# ---------------------------------------------------------------------------
# PsychReport — Core Structured Output
# ---------------------------------------------------------------------------

class PsychReport(BaseModel):
    """
    Structured psychological assessment output.
    Produced by the LLM layer and validated against this schema.
    """
    risk_classification: RiskLevel = Field(
        description="Overall risk level based on text + multimodal fusion"
    )
    emotional_state_summary: str = Field(
        description="Concise summary of detected emotional state (1-2 sentences)"
    )
    behavioral_inference: str = Field(
        description="Inferred behavioral patterns from the conversation"
    )
    cognitive_distortions: List[str] = Field(
        default_factory=list,
        description="List of detected cognitive distortions (e.g. catastrophizing, black-and-white thinking)"
    )
    suggested_interventions: List[str] = Field(
        default_factory=list,
        description="Clinical-style intervention suggestions"
    )
    confidence_score: float = Field(
        ge=0.0, le=1.0,
        description="Aggregate confidence of this assessment (0.0–1.0)"
    )
    crisis_triggered: bool = Field(
        default=False,
        description="True if crisis override layer activated"
    )
    crisis_resources: Optional[List[CrisisResource]] = Field(
        default=None,
        description="Emergency resources, populated only when crisis_triggered=True"
    )
    service_degraded: bool = Field(
        default=False,
        description="True if Ollama was unreachable and fallback was used"
    )


# ---------------------------------------------------------------------------
# Fallback Report (used when Ollama is unavailable)
# ---------------------------------------------------------------------------

def fallback_report() -> PsychReport:
    return PsychReport(
        risk_classification=RiskLevel.MINIMAL,
        emotional_state_summary="Assessment unavailable — inference service is currently offline.",
        behavioral_inference="Unable to infer behavioral patterns at this time.",
        cognitive_distortions=[],
        suggested_interventions=["Please try again shortly."],
        confidence_score=0.0,
        crisis_triggered=False,
        service_degraded=True,
    )


# ---------------------------------------------------------------------------
# Remedy Endpoint  (must be defined BEFORE ChatResponse which references it)
# ---------------------------------------------------------------------------

class RemedyResponse(BaseModel):
    condition: str
    symptoms: str
    treatments: str
    medications: str
    dosage: str
    gita_remedy: str


# ---------------------------------------------------------------------------
# Facial / Emotion Endpoint
# ---------------------------------------------------------------------------

class EmotionResponse(BaseModel):
    emotion: Optional[str] = None
    confidence: Optional[float] = None
    face_box: Optional[List[int]] = None
    message: Optional[str] = None
    error: Optional[str] = None


# ---------------------------------------------------------------------------
# Chat Endpoint
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    emotion: Optional[str] = Field(default="neutral", description="Face emotion from webcam")
    history: List[ConversationMessage] = Field(default_factory=list)
    stream: bool = Field(default=False, description="Enable streaming response")
    user_id: Optional[str] = Field(default=None, description="Patient user ID for adaptive memory")

    @field_validator("message")
    @classmethod
    def sanitize_message(cls, v: str) -> str:
        # Strip HTML tags
        v = re.sub(r"<[^>]+>", "", v)
        # Collapse whitespace
        v = " ".join(v.split())
        return v.strip()

    @field_validator("emotion")
    @classmethod
    def normalize_emotion(cls, v: str) -> str:
        return v.lower().strip() if v else "neutral"


# ---------------------------------------------------------------------------
# Text Analysis Endpoint
# ---------------------------------------------------------------------------

class TextAnalysisRequest(BaseModel):
    text: str = Field(min_length=1, max_length=2000)

    @field_validator("text")
    @classmethod
    def sanitize_text(cls, v: str) -> str:
        v = re.sub(r"<[^>]+>", "", v)
        return " ".join(v.split()).strip()


class TextAnalysisResponse(BaseModel):
    emotions: List[EmotionLabel]
    dominant: str
    crisis_risk: float = Field(ge=0.0, le=1.0)
    crisis_triggered: bool


# ---------------------------------------------------------------------------
<<<<<<< HEAD
# Facial / Emotion Endpoint
# ---------------------------------------------------------------------------

class EmotionResponse(BaseModel):
    emotion: Optional[str] = None
    confidence: Optional[float] = None
    face_box: Optional[List[int]] = None
    message: Optional[str] = None
    error: Optional[str] = None


# ---------------------------------------------------------------------------
# Remedy Endpoint
# ---------------------------------------------------------------------------

class RemedyResponse(BaseModel):
    condition: str
    symptoms: str
    treatments: str
    medications: str
    dosage: str
    gita_remedy: str


# --- ChatResponse (defined AFTER RemedyResponse to avoid forward-reference) ---

class ChatResponse(BaseModel):
    response: str = Field(description="Conversational reply text")
    report: PsychReport
    text_emotion: Optional[List[EmotionLabel]] = None
    fusion_risk_score: Optional[float] = None
    remedy: Optional[RemedyResponse] = None  # CSV-based remedy data


# ---------------------------------------------------------------------------
=======
>>>>>>> e0df7c7515413c00067c58471d916a2c19ab0679
# Health Endpoint
# ---------------------------------------------------------------------------

class HealthResponse(BaseModel):
    status: str
    ollama_reachable: bool
    ollama_model: str
    distilbert_loaded: bool
    version: str = "2.0.0"
