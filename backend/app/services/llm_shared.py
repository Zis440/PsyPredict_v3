"""
llm_shared.py — Shared LLM utilities for PsyPredict

Extracted from ollama_engine.py so both GroqClient and OllamaClient
share identical prompt construction, response parsing, and constants.
"""
from __future__ import annotations

import json
import logging
from typing import List, Optional

from app.schemas import (
    ConversationMessage,
    PsychReport,
    RiskLevel,
    fallback_report,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# System Prompt (used by both providers)
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are PsyPredict — a licensed clinical psychologist with deep expertise in CBT, DBT, psychodynamic therapy, and the psychological wisdom of the Bhagavad Gita. You combine modern evidence-based psychology with ancient Vedic insight to help each person heal.

Your role is twofold:
1. Respond as a warm, deeply insightful psychologist who truly understands human suffering.
2. Provide a structured backend psychological assessment in JSON format.

== CONVERSATIONAL RESPONSE RULES ==
- ALWAYS give a full, thoughtful, deeply empathetic response FIRST (before the JSON block).
- Responses must be at least 4-7 sentences. Never one-liners or generic platitudes.
- Validate the user's feelings FIRST. Reflect back what they shared. Show you truly listened.
- Do NOT start with "I'm here to help" or generic openers. Be specific to what they said.
- Use warm, humanizing language — like a wise, caring psychologist talking to someone they deeply care about.
- If the situation involves trauma, grief, betrayal, or crisis — respond with appropriate gravity, compassion, and clinical depth.

== GITA SHLOKA INTEGRATION RULES ==
- When a Gita shloka is provided in the GITA WISDOM CONTEXT below, you MUST weave it into your response naturally.
- Quote the shloka reference (e.g., "Gita, Chapter 2, Verse 47") and explain it in SIMPLE, HUMANIZED language.
- Include the original SANSKRIT TERM (e.g., Titiksha, Sthita-prajna, Vairagya) alongside plain English meaning.
- Explain HOW this ancient wisdom DIRECTLY applies to the user's SPECIFIC situation — not generic advice.
- Use real-life analogies, metaphors, or stories to make the shloka relatable and memorable.
- NEVER repeat the same shloka explanation verbatim across responses. Use fresh angles, analogies, and framing each time.
- If no shloka is provided, you may still reference Gita wisdom from your knowledge, but always be specific.

== PATIENT HISTORY & ADAPTIVE RULES ==
- If PATIENT HISTORY is provided below, use it to personalize your response.
- Reference progress or patterns you notice (e.g., "I can see from our past conversations that...").
- Adapt your therapeutic approach based on what has worked or not worked before.
- If the patient is improving, acknowledge and reinforce the progress.
- If the patient is recurring in distress, gently explore deeper root causes.
- Be a psychologist who REMEMBERS — this builds trust and therapeutic alliance.

== THERAPEUTIC DEPTH ==
- End each response with ONE concrete, actionable psychological homework (e.g., "Tonight, try writing down three things that went well today — even small ones.").
- Use CBT reframing, DBT distress tolerance, or psychodynamic insight as appropriate.
- Vary your therapeutic approach across responses — don't always use the same framework.
- Be DIVERSE in your analogies, tone, and framing. Never give a formulaic or robotic answer.

== JSON ASSESSMENT RULES ==
After your conversational response, add the marker: ---JSON---
Then provide the PsychReport JSON.

1. Output ONLY valid JSON conforming exactly to the PsychReport schema below.
2. Do NOT fabricate clinical diagnoses. Infer only from the evidence provided.
3. cognitive_distortions must reference recognized CBT distortion labels only.
4. suggested_interventions must be concrete and clinically actionable.
5. confidence_score reflects YOUR confidence in this assessment (0.0 to 1.0).
6. crisis_triggered MUST be false — crisis detection is handled by a separate layer.
7. service_degraded MUST be false.

PSYCH_REPORT_SCHEMA:
{
  "risk_classification": "<MINIMAL|LOW|MODERATE|HIGH|CRITICAL>",
  "emotional_state_summary": "<string>",
  "behavioral_inference": "<string>",
  "cognitive_distortions": ["<string>", ...],
  "suggested_interventions": ["<string>", ...],
  "confidence_score": <float 0.0-1.0>,
  "crisis_triggered": false,
  "crisis_resources": null,
  "service_degraded": false
}

Output format:
<Your full, empathetic psychologist response here — 4-7 sentences minimum, with Gita shloka woven in naturally>
---JSON---
{ ...psych report json... }
"""

# ---------------------------------------------------------------------------
# FACE → DISTRESS SCORE mapping
# ---------------------------------------------------------------------------

FACE_DISTRESS_MAP: dict[str, float] = {
    "fear": 0.80,
    "sad": 0.70,
    "angry": 0.50,
    "disgust": 0.40,
    "surprised": 0.30,
    "neutral": 0.20,
    "happy": 0.05,
}


# ---------------------------------------------------------------------------
# Context Window Trimming
# ---------------------------------------------------------------------------

def trim_history(
    history: List[ConversationMessage],
    max_turns: int,
) -> List[ConversationMessage]:
    """Keep only the last `max_turns` pairs of messages."""
    if len(history) <= max_turns * 2:
        return history
    return history[-(max_turns * 2):]


# ---------------------------------------------------------------------------
# Messages Builder (chat-completion format used by both Groq and Ollama)
# ---------------------------------------------------------------------------

def build_messages(
    user_text: str,
    face_emotion: str,
    history: List[ConversationMessage],
    max_turns: int,
    text_emotion_summary: Optional[str] = None,
    patient_profile: Optional[str] = None,
    gita_context: Optional[str] = None,
) -> list:
    """
    Builds the messages array for chat-completions-style APIs.
    Works for both Groq (OpenAI-compatible) and Ollama (/api/chat).

    System prompt is a dedicated system message, with optional patient
    history and Gita context appended. History becomes alternating
    user/assistant messages. Multimodal context is appended to the
    final user message.
    """
    # Build system message with optional adaptive context
    system_content = SYSTEM_PROMPT

    if patient_profile:
        system_content += (
            f"\n\nPATIENT HISTORY (Adaptive Context — use this to personalize your response):\n"
            f"{patient_profile}"
        )

    if gita_context:
        system_content += (
            f"\n\nGITA WISDOM CONTEXT (weave this shloka into your response naturally):\n"
            f"{gita_context}"
        )

    messages = [{"role": "system", "content": system_content}]

    # Conversation history (trimmed)
    trimmed = trim_history(history, max_turns)
    for msg in trimmed:
        messages.append({
            "role": msg.role.value,
            "content": msg.content,
        })

    # Multimodal context appended to the current user message
    face_distress = FACE_DISTRESS_MAP.get(face_emotion.lower(), 0.20)
    multimodal_ctx = (
        f"\n\n[MULTIMODAL CONTEXT]\n"
        f"Face emotion (webcam): {face_emotion} (distress score: {face_distress:.2f})\n"
    )
    if text_emotion_summary:
        multimodal_ctx += f"Text emotion (DistilBERT): {text_emotion_summary}\n"

    final_user_content = user_text + multimodal_ctx
    messages.append({"role": "user", "content": final_user_content})

    return messages


# ---------------------------------------------------------------------------
# Parse LLM Output → (reply_text, PsychReport)
# ---------------------------------------------------------------------------

def parse_response(raw: str) -> tuple[str, PsychReport]:
    """
    Splits the LLM output on the ---JSON--- marker.
    Returns (conversational_reply, PsychReport).
    Falls back gracefully if JSON parsing fails.
    """
    marker = "---JSON---"
    if marker in raw:
        parts = raw.split(marker, 1)
        reply_text = parts[0].strip()
        json_block = parts[1].strip()
    else:
        reply_text = ""
        json_block = raw.strip()

    # Strip markdown code fences if present
    if json_block.startswith("```"):
        lines = json_block.split("\n")
        json_block = "\n".join(
            l for l in lines if not l.startswith("```")
        ).strip()

    try:
        data = json.loads(json_block)
        report = PsychReport(**data)
    except (json.JSONDecodeError, ValueError, KeyError) as exc:
        logger.warning(
            "Failed to parse PsychReport from LLM output: %s | raw=%r",
            exc,
            json_block[:500],
        )
        report = fallback_report()
        if not reply_text:
            reply_text = raw.strip()

    return reply_text, report


# ---------------------------------------------------------------------------
# Tone Directives — Dynamic personality modulation
# ---------------------------------------------------------------------------

_TONE_DIRECTIVES = {
    "warm": (
        "Use a warm, nurturing, and deeply empathetic tone. "
        "Speak as a caring mentor who makes the patient feel safe and validated. "
        "Use gentle language, soft metaphors, and express genuine emotional concern."
    ),
    "formal": (
        "Use a professional, clinical, and structured tone. "
        "Maintain appropriate therapeutic boundaries. "
        "Use evidence-based terminology and frame responses in clinical terms. "
        "Be supportive but maintain professional distance."
    ),
    "motivational": (
        "Use an energetic, empowering, and action-oriented tone. "
        "Celebrate strengths, highlight resilience, and inspire change. "
        "Use motivational interviewing techniques and focus on possibilities."
    ),
    "calm": (
        "Use a calm, meditative, and grounding tone. "
        "Speak slowly and softly — like guiding a meditation. "
        "Focus on breath, mindfulness, and present-moment awareness. "
        "Use the Gita's wisdom about inner peace prominently."
    ),
    "structured": (
        "Use a highly organized and step-by-step tone. "
        "Break down insights into clear numbered lists. "
        "Provide exactly what to do, when, and how. "
        "Minimize abstract language; maximize concrete, actionable guidance."
    ),
}

_VERBOSITY_DIRECTIVES = {
    "concise": (
        "Keep your response CONCISE (3-4 sentences for the main response). "
        "Be direct and impactful. Every word should count."
    ),
    "moderate": (
        "Provide a MODERATE-length response (5-7 sentences). "
        "Balance depth with brevity."
    ),
    "detailed": (
        "Provide a DETAILED, thorough response (7-10 sentences). "
        "Explore multiple angles, provide rich context, and go deep."
    ),
}

_FRAMEWORK_DIRECTIVES = {
    "cbt": (
        "Prioritize Cognitive Behavioral Therapy (CBT) techniques. "
        "Focus on identifying and reframing cognitive distortions, "
        "behavioral activation, and thought records."
    ),
    "dbt": (
        "Prioritize Dialectical Behavior Therapy (DBT) techniques. "
        "Focus on distress tolerance, emotion regulation, "
        "interpersonal effectiveness, and mindfulness."
    ),
    "psychodynamic": (
        "Use a psychodynamic/insight-oriented approach. "
        "Explore unconscious patterns, attachment styles, "
        "and how past experiences shape current feelings."
    ),
    "gita": (
        "HEAVILY emphasize Bhagavad Gita philosophical insights. "
        "Lead with Gita wisdom and weave multiple shlokas naturally. "
        "Use Sanskrit terms extensively with explanations. "
        "Frame every situation through the lens of Dharma, Karma, and Self-realization."
    ),
    "auto": "",  # Let the LLM choose based on context
}


def build_adaptive_system_prompt(
    patient_preferences: Optional[dict] = None,
    session_context: Optional[dict] = None,
    gita_candidates: Optional[str] = None,
    patient_profile: Optional[str] = None,
    avg_feedback: Optional[float] = None,
) -> str:
    """
    Build a dynamically personalized system prompt based on patient
    preferences, session history, and context.

    Args:
        patient_preferences: Dict with preferred_tone, verbosity, framework_preference, topics_to_avoid
        session_context: Dict with session_number, time_since_last, risk_trend
        gita_candidates: Formatted string with multiple Gita shlokas
        patient_profile: Compact profile string from PatientMemoryEngine
        avg_feedback: Average feedback rating (1-5) from previous sessions

    Returns:
        Complete system prompt string
    """
    prompt_parts = [SYSTEM_PROMPT]

    # --- Tone & Style Modulation ---
    if patient_preferences:
        tone = patient_preferences.get("preferred_tone", "warm")
        verbosity = patient_preferences.get("verbosity", "moderate")
        framework = patient_preferences.get("framework_preference", "auto")
        topics_to_avoid = patient_preferences.get("topics_to_avoid", [])

        style_section = "\n\n== PERSONALIZATION DIRECTIVES (adapt your style to this patient) =="

        if tone in _TONE_DIRECTIVES:
            style_section += f"\nTone: {_TONE_DIRECTIVES[tone]}"
        if verbosity in _VERBOSITY_DIRECTIVES:
            style_section += f"\nLength: {_VERBOSITY_DIRECTIVES[verbosity]}"
        if framework in _FRAMEWORK_DIRECTIVES and _FRAMEWORK_DIRECTIVES[framework]:
            style_section += f"\nFramework: {_FRAMEWORK_DIRECTIVES[framework]}"
        if topics_to_avoid:
            style_section += (
                f"\n[WARNING] TOPICS TO AVOID: {', '.join(topics_to_avoid)}. "
                f"Do NOT bring up these topics unless the patient specifically raises them."
            )

        prompt_parts.append(style_section)

    # --- Session Context ---
    if session_context:
        session_num = session_context.get("session_number", 0)
        time_since = session_context.get("time_since_last", "")
        risk_trend = session_context.get("risk_trend", "")

        ctx_section = "\n\n== SESSION CONTEXT =="
        if session_num > 0:
            ctx_section += f"\nThis is session #{session_num} with this patient."
        if time_since:
            ctx_section += f"\nTime since last session: {time_since}."
        if risk_trend:
            ctx_section += f"\nRisk trajectory: {risk_trend}."

        if session_num == 1:
            ctx_section += (
                "\nThis is the patient's FIRST session. Be especially welcoming, "
                "establish rapport, and avoid deep probing. Focus on making them feel safe."
            )
        elif session_num > 5 and risk_trend == "improving":
            ctx_section += (
                "\nThis is a returning patient showing improvement. "
                "Acknowledge progress, reinforce positive changes, and explore deeper growth."
            )

        prompt_parts.append(ctx_section)

    # --- Feedback Adjustment ---
    if avg_feedback is not None:
        if avg_feedback < 2.5:
            prompt_parts.append(
                "\n\n== ADJUSTMENT NOTE ==\n"
                "Previous responses have received low ratings from this patient. "
                "Try a DIFFERENT approach — vary your tone, depth, and framework. "
                "Be more responsive to their specific needs and less formulaic."
            )
        elif avg_feedback >= 4.5:
            prompt_parts.append(
                "\n\n== ADJUSTMENT NOTE ==\n"
                "This patient has responded very positively to your approach. "
                "Continue with a similar style while maintaining freshness."
            )

    # --- Patient History ---
    if patient_profile:
        prompt_parts.append(
            f"\n\nPATIENT HISTORY (Adaptive Context — use this to personalize your response):\n"
            f"{patient_profile}"
        )

    # --- Gita Context ---
    if gita_candidates:
        prompt_parts.append(
            f"\n\nGITA WISDOM CONTEXT (choose the most relevant shloka and weave it naturally):\n"
            f"{gita_candidates}"
        )

    return "".join(prompt_parts)


def build_adaptive_messages(
    user_text: str,
    face_emotion: str,
    history: List[ConversationMessage],
    max_turns: int,
    text_emotion_summary: Optional[str] = None,
    patient_profile: Optional[str] = None,
    gita_context: Optional[str] = None,
    patient_preferences: Optional[dict] = None,
    session_context: Optional[dict] = None,
    avg_feedback: Optional[float] = None,
) -> list:
    """
    Enhanced build_messages that uses adaptive system prompt.

    This is the v1.4 replacement for build_messages() — it includes
    tone modulation, verbosity control, framework preferences, and
    session context awareness.
    """
    system_content = build_adaptive_system_prompt(
        patient_preferences=patient_preferences,
        session_context=session_context,
        gita_candidates=gita_context,
        patient_profile=patient_profile,
        avg_feedback=avg_feedback,
    )

    messages = [{"role": "system", "content": system_content}]

    # Conversation history (trimmed)
    trimmed = trim_history(history, max_turns)
    for msg in trimmed:
        messages.append({
            "role": msg.role.value,
            "content": msg.content,
        })

    # Multimodal context appended to the current user message
    face_distress = FACE_DISTRESS_MAP.get(face_emotion.lower(), 0.20)
    multimodal_ctx = (
        f"\n\n[MULTIMODAL CONTEXT]\n"
        f"Face emotion (webcam): {face_emotion} (distress score: {face_distress:.2f})\n"
    )
    if text_emotion_summary:
        multimodal_ctx += f"Text emotion (DistilBERT): {text_emotion_summary}\n"

    final_user_content = user_text + multimodal_ctx
    messages.append({"role": "user", "content": final_user_content})

    return messages

