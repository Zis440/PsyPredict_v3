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


class UserSegment(str, Enum):
    STUDENT = "student"
    PROFESSIONAL = "professional"


class PackageType(str, Enum):
    PACKAGE_1_WELLBEING = "pkg1_wellbeing"
    PACKAGE_2_WORKFORCE = "pkg2_workforce"
    PACKAGE_3_JOBFIT = "pkg3_jobfit"


class TaskType(str, Enum):
    """Types of LLM tasks with different routing priorities."""
    ROUTINE_CHAT = "routine_chat"
    LONG_FORM_SUMMARY = "long_form_summary"
    PROGRESS_ANALYSIS = "progress_analysis"
    KNOWLEDGE_RETRIEVAL = "knowledge_retrieval"


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
        description="True if LLM was unreachable and fallback was used"
    )


# ---------------------------------------------------------------------------
# Fallback Report (used when LLM provider is unavailable)
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
# Remedy Endpoint
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


class RoutingMetadata(BaseModel):
    """Metadata about how a request was routed between LLM providers."""
    provider_used: str = Field(description="Which LLM provider handled this request")
    task_type: str = Field(description="Task classification that drove routing")
    latency_ms: float = Field(description="Total inference latency in milliseconds")
    fallback_used: bool = Field(default=False, description="Whether a fallback provider was used")
    fallback_provider: Optional[str] = Field(default=None, description="Original provider that failed")
    pii_scrubbed: bool = Field(default=False, description="Whether PII was redacted before cloud call")
    pii_types: List[str] = Field(default_factory=list, description="Types of PII detected and scrubbed")
    error: Optional[str] = Field(default=None, description="Error message if routing failed")


class ChatResponse(BaseModel):
    response: str = Field(description="Conversational reply text")
    report: PsychReport
    text_emotion: Optional[List[EmotionLabel]] = None
    fusion_risk_score: Optional[float] = None
    remedy: Optional[RemedyResponse] = None  # CSV-based remedy data
    routing: Optional[RoutingMetadata] = None  # LLM routing info


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
# Health Endpoint
# ---------------------------------------------------------------------------

class HealthResponse(BaseModel):
    status: str
    llm_provider: str = "groq"
    llm_reachable: bool
    llm_model: str
    distilbert_loaded: bool
    version: str = "1.4.0"


# ---------------------------------------------------------------------------
# LLM Status Endpoint
# ---------------------------------------------------------------------------

class LLMStatusResponse(BaseModel):
    provider: str
    reachable: bool
    model: str
    base_url: str
    fallback_available: bool


# ---------------------------------------------------------------------------
# Patient Preferences
# ---------------------------------------------------------------------------

class PatientPreferences(BaseModel):
    """Patient's therapeutic preferences for adaptive personalization."""
    user_id: str
    segment: UserSegment = Field(default=UserSegment.PROFESSIONAL, description="User segment for contextual assessments")
    preferred_tone: str = Field(default="warm", description="warm, formal, motivational, calm, structured")
    verbosity: str = Field(default="moderate", description="concise, moderate, detailed")
    framework_preference: str = Field(default="auto", description="cbt, dbt, psychodynamic, gita, auto")
    topics_to_avoid: List[str] = Field(default_factory=list)
    engagement_score: float = Field(default=0.5, ge=0.0, le=1.0)
    last_updated: Optional[str] = None


class PatientPreferencesUpdate(BaseModel):
    """Request body for updating patient preferences."""
    preferred_tone: Optional[str] = None
    verbosity: Optional[str] = None
    framework_preference: Optional[str] = None
    topics_to_avoid: Optional[List[str]] = None

    @field_validator("preferred_tone")
    @classmethod
    def validate_tone(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            allowed = {"warm", "formal", "motivational", "calm", "structured"}
            if v.lower() not in allowed:
                raise ValueError(f"Tone must be one of: {allowed}")
            return v.lower()
        return v

    @field_validator("verbosity")
    @classmethod
    def validate_verbosity(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            allowed = {"concise", "moderate", "detailed"}
            if v.lower() not in allowed:
                raise ValueError(f"Verbosity must be one of: {allowed}")
            return v.lower()
        return v

    @field_validator("framework_preference")
    @classmethod
    def validate_framework(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            allowed = {"cbt", "dbt", "psychodynamic", "gita", "auto"}
            if v.lower() not in allowed:
                raise ValueError(f"Framework must be one of: {allowed}")
            return v.lower()
        return v


# ---------------------------------------------------------------------------
# Progress Tracking
# ---------------------------------------------------------------------------

class ProgressSnapshot(BaseModel):
    """A snapshot of patient progress over a time period."""
    snapshot_date: str
    period_start: Optional[str] = None
    period_end: Optional[str] = None
    avg_risk_score: float = Field(ge=0.0, le=1.0)
    dominant_emotions: List[str] = Field(default_factory=list)
    sessions_count: int = 0
    improvement_score: float = Field(default=0.0, ge=-1.0, le=1.0)
    summary: str = ""


class PatientProgressResponse(BaseModel):
    """Full progress response for a patient."""
    user_id: str
    total_sessions: int
    first_session: Optional[str] = None
    last_session: Optional[str] = None
    current_risk_level: str = "MINIMAL"
    emotion_trend: List[Dict[str, Any]] = Field(default_factory=list)
    risk_trend: List[Dict[str, Any]] = Field(default_factory=list)
    snapshots: List[ProgressSnapshot] = Field(default_factory=list)
    summary: str = ""


class SessionFeedback(BaseModel):
    """Feedback for a specific session/message."""
    rating: int = Field(ge=1, le=5, description="1-5 star rating")
    comment: Optional[str] = Field(default=None, max_length=500)
    message_id: Optional[str] = None


# ---------------------------------------------------------------------------
# Assessment Schemas (SJT, Writing, Visual)
# ---------------------------------------------------------------------------

class AssessmentType(str, Enum):
    SJT = "SJT"
    WRITING = "WRITING"
    VISUAL = "VISUAL"

class AssessmentScenario(BaseModel):
    id: str
    type: AssessmentType
    title: str
    description: str
    image_url: Optional[str] = None
    questions: List[str]

class AssessmentResult(BaseModel):
    scenario_id: str
    user_response: str
    analysis: str
    scores: Dict[str, float]  # e.g., "empathy": 0.8
    timestamp: str

# ---------------------------------------------------------------------------
# Assessment Segments and Packages
# ---------------------------------------------------------------------------

class DomainScore(BaseModel):
    domain_name: str
    score: float = Field(ge=0.0, le=100.0)
    confidence: float = Field(default=85.0, ge=0.0, le=100.0)
    evidence: List[str] = Field(default_factory=list)

class DetailedPDFReport(BaseModel):
    role_fitment_score: float = Field(ge=0.0, le=100.0)
    growth_potential_score: float = Field(ge=0.0, le=100.0)
    executive_summary: List[str] = Field(default_factory=list)
    key_strengths: List[str] = Field(default_factory=list)
    development_areas: List[str] = Field(default_factory=list)
    coworking_insights: Dict[str, str] = Field(default_factory=dict)
    personality_insights: Dict[str, List[str]] = Field(default_factory=dict)

class PackageResult(BaseModel):
    user_id: str
    package_type: PackageType
    segment: UserSegment
    timestamp: str
    validity_score: float = Field(ge=0.0, le=100.0)
    domain_scores: List[DomainScore]
    final_risk_level: Optional[RiskLevel] = None
    detailed_report: Optional[DetailedPDFReport] = None
    raw_answers: List[Dict[str, Any]] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Master Report
# ---------------------------------------------------------------------------

class MetricScore(BaseModel):
    score: float = Field(ge=0, le=100)
    confidence: float = Field(ge=0, le=100)
    evidence: List[str] = Field(default_factory=list)

class ExecutiveScores(BaseModel):
    personality_health: MetricScore
    mental_wellness: MetricScore
    emotional_intelligence: MetricScore
    communication: MetricScore
    behavioral_stability: MetricScore
    stress: MetricScore
    anxiety: MetricScore
    resilience: MetricScore
    leadership: MetricScore
    growth_potential: MetricScore
    career_readiness: MetricScore
    team_compatibility: MetricScore
    skill_proficiency: MetricScore
    role_fitment: MetricScore
    overall_intelligence_index: MetricScore

class MasterReport(BaseModel):
    user_id: str
    generated_at: str
    executive_summary: str
    scores: ExecutiveScores
    personality_profile: str
    emotional_intelligence_analysis: str
    mental_wellness_analysis: str
    behavioral_analysis: str
    communication_analysis: str
    leadership_analysis: str
    conflict_analysis: str
    career_analysis: str
    skill_assessment_results: str
    growth_potential_analysis: str
    relationship_health_analysis: str = ""
    life_purpose_analysis: str = ""
    cognitive_patterns_analysis: str = ""
    spiritual_wellbeing_analysis: str = ""
    strengths: List[str]
    weaknesses: List[str]
    development_areas: List[str]
    risk_indicators: List[str]
    recommendations: List[str]
    improvement_roadmap: str
    action_plan: str
    future_growth_predictions: str
    bhagavad_gita_wisdom: str
    raw_responses: List[Dict[str, Any]] = Field(default_factory=list)
