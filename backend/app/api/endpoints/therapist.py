"""
therapist.py — PsyPredict AI Therapist Endpoint (FastAPI) v1.4

Full inference pipeline with dual-LLM orchestration:
  1. Input sanitization + validation (Pydantic)
  2. Text emotion classification (DistilBERT)
  3. Crisis evaluation (zero-shot NLI) — override if triggered
  4. Multimodal fusion (text + face)
  5. Patient memory + preferences retrieval (adaptive learning)
  6. Semantic knowledge retrieval (FAISS) + Gita shloka context
  7. Dual-LLM orchestrated generation (Ollama/Groq with intelligent routing)
  8. PsychReport JSON schema validation
  9. Session save + background summarization
  10. Streaming response via orchestrator
"""
from __future__ import annotations

import asyncio
import logging
from typing import AsyncIterator

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.schemas import (
    ChatRequest,
    ChatResponse,
    PsychReport,
    RemedyResponse,
    RoutingMetadata,
)
from app.services.ollama_engine import ollama_engine, orchestrator
from app.services.text_emotion_engine import text_emotion_engine
from app.services.crisis_engine import crisis_engine
from app.services.fusion_engine import fusion_engine
from app.services.remedy_engine import remedy_engine
from app.services.patient_memory import get_patient_memory
from app.config import get_settings

logger = logging.getLogger(__name__)

router = APIRouter()

# Map risk levels to CSV conditions — enriched for diversity
RISK_TO_CONDITION: dict[str, str] = {
    "critical": "Suicidal Ideation",
    "high": "Depression",
    "moderate": "Anxiety",
    "low": "Stress",
    "minimal": "Stress",
}

# Map emotions to CSV conditions — enriched and more accurate
EMOTION_TO_CONDITION: dict[str, str] = {
    "sad": "Depression",
    "sadness": "Depression",
    "fear": "Anxiety",
    "angry": "Anger Management",
    "anger": "Anger Management",
    "disgust": "OCD",
    "surprised": "Panic Disorder",
    "surprise": "Panic Disorder",
    "neutral": "Stress",
    "happy": "Stress",
    "joy": "Stress",
    "love": "Stress",
}


# ---------------------------------------------------------------------------
# POST /api/chat
# ---------------------------------------------------------------------------

@router.post("/chat")
async def chat(req: ChatRequest):  # type: ignore[misc]
    """
    Main inference endpoint with dual-LLM orchestration.
    Routes between Ollama (local) and Groq (cloud) based on
    task type, privacy, and provider availability.

    Returns structured PsychReport + conversational reply + remedy + routing metadata.
    """
    settings = get_settings()
    user_text = req.message
    face_emotion = req.emotion or "neutral"
    history = req.history
    user_id = req.user_id

    # ── Step 1: Text Emotion Classification ────────────────────────────────
    text_labels = await text_emotion_engine.classify(user_text)
    dominant_text_emotion = text_labels[0].label if text_labels else "neutral"
    text_emotion_summary = text_emotion_engine.summary_string(text_labels)

    logger.info(
        "Text emotion: %s | Face emotion: %s | User: %s",
        text_emotion_summary,
        face_emotion,
        user_id or "anonymous",
    )

    # ── Step 2: Crisis Evaluation (OVERRIDE LAYER) ──────────────────────────
    crisis_score, crisis_triggered = await crisis_engine.evaluate(user_text)

    if crisis_triggered:
        reply, report = crisis_engine.build_crisis_report(crisis_score)
        remedy_data = remedy_engine.get_remedy("Suicidal Ideation") or remedy_engine.get_remedy("Anxiety")
        remedy = RemedyResponse(**remedy_data) if remedy_data and "error" not in remedy_data else None

        # Save crisis session to patient memory
        if user_id:
            try:
                mem = get_patient_memory()
                mem.save_session(
                    user_id=user_id,
                    dominant_emotion="crisis",
                    risk_level="CRITICAL",
                    fusion_score=float(crisis_score),
                    cognitive_distortions=["Hopelessness", "All-or-nothing thinking"],
                    interventions=["Crisis line referral"],
                    summary="Crisis triggered — immediate support provided",
                    user_message=user_text[:200],
                )
            except Exception as e:
                logger.warning("Failed to save crisis session to memory: %s", e)

        return ChatResponse(
            response=reply,
            report=report,
            text_emotion=text_labels,
            fusion_risk_score=float(crisis_score),
            remedy=remedy,
            routing=RoutingMetadata(
                provider_used="crisis_engine",
                task_type="crisis_override",
                latency_ms=0.0,
            ),
        )

    # ── Step 3: Multimodal Fusion ────────────────────────────────────────────
    fusion = fusion_engine.compute(
        dominant_text_emotion=dominant_text_emotion,
        face_emotion=face_emotion,
    )
    logger.info("Fusion risk score: %.4f (dominant: %s)", fusion.final_risk_score, fusion.dominant_modality)

    # ── Step 4: Patient Memory + Preferences Retrieval ───────────────────────
    patient_profile = None
    patient_preferences = None
    session_context = None
    avg_feedback = None
    semantic_memories = None

    if user_id:
        try:
            mem = get_patient_memory()
            enhanced = mem.get_enhanced_profile(user_id)
            if enhanced:
                patient_profile = enhanced.get("profile_string")
                patient_preferences = enhanced.get("preferences")
                avg_feedback = enhanced.get("avg_feedback_rating")

                if patient_profile:
                    logger.info("Enhanced profile loaded for user %s (%d chars)", user_id, len(patient_profile))

                # Build session context
                progress = mem.get_progress(user_id)
                if progress:
                    session_context = {
                        "session_number": progress.get("total_sessions", 0) + 1,
                        "risk_trend": progress.get("summary", "unknown"),
                    }
                
                # Fetch semantic memories
                if hasattr(mem, "query_semantic_memories"):
                    memories = mem.query_semantic_memories(user_id, user_text, n_results=3)
                    if memories:
                        semantic_memories = "\n- ".join([m["text"] for m in memories])
                        if semantic_memories:
                            semantic_memories = "- " + semantic_memories
                            logger.info("Semantic memories retrieved for user %s", user_id)
        except Exception as e:
            logger.warning("Patient memory retrieval failed: %s", e)

    # ── Step 5: Semantic Knowledge Retrieval + Gita Context ──────────────────
    gita_context = None
    remedy = None

    # Try semantic search first (FAISS)
    if settings.KNOWLEDGE_INDEX_ENABLED:
        try:
            from app.services.knowledge_index import get_knowledge_index
            ki = get_knowledge_index()
            if ki.is_ready:
                # Get semantically relevant Gita context
                gita_context = ki.get_gita_context(
                    query=user_text,
                    emotion=dominant_text_emotion,
                    top_k=2,
                )
                # Get top remedy result for structured response
                results = ki.search(user_text, top_k=1, emotion=dominant_text_emotion)
                if results:
                    r = results[0]
                    try:
                        remedy = RemedyResponse(
                            condition=r.condition,
                            symptoms=r.symptoms,
                            treatments=r.treatments,
                            medications=r.medications,
                            dosage=r.dosage,
                            gita_remedy=r.gita_remedy,
                        )
                    except Exception:
                        pass
        except Exception as e:
            logger.warning("Semantic search failed, falling back to exact-match: %s", e)

    # Fallback to exact-match if semantic search didn't produce results
    if remedy is None:
        condition = EMOTION_TO_CONDITION.get(dominant_text_emotion.lower(), "Anxiety")
        remedy_raw = remedy_engine.get_remedy(condition)
        if remedy_raw and "error" not in remedy_raw:
            try:
                remedy = RemedyResponse(**remedy_raw)
                if not gita_context:
                    gita_remedy_text = remedy_raw.get("gita_remedy", "")
                    if gita_remedy_text:
                        gita_context = f"Condition: {remedy_raw.get('condition', condition)}\nGita Wisdom: {gita_remedy_text}"
            except Exception as e:
                logger.warning("Could not build RemedyResponse: %s", e)

    # ── Step 6: Route through Orchestrator ────────────────────────────────────
    use_orchestrator = settings.LLM_ORCHESTRATOR_ENABLED

    if req.stream:
        # Streaming response
        async def stream_generator():
            import json as _json
            import time as _time

            if use_orchestrator:
                async for token in orchestrator.generate_stream(
                    user_text=user_text,
                    face_emotion=face_emotion,
                    history=history,
                    text_emotion_summary=text_emotion_summary,
                    patient_profile=patient_profile,
                    semantic_memories=semantic_memories,
                    gita_context=gita_context,
                ):
                    yield token
            else:
                _start = _time.monotonic()
                async for token in ollama_engine.generate_stream(
                    user_text=user_text,
                    face_emotion=face_emotion,
                    history=history,
                    text_emotion_summary=text_emotion_summary,
                    patient_profile=patient_profile,
                    semantic_memories=semantic_memories,
                    gita_context=gita_context,
                ):
                    yield token
                _elapsed = (_time.monotonic() - _start) * 1000
                yield "\n---ROUTING---\n" + _json.dumps({
                    "provider_used": ollama_engine.provider_name,
                    "task_type": "routine_chat",
                    "latency_ms": round(_elapsed, 1),
                })

        return StreamingResponse(stream_generator(), media_type="text/plain")

    # Non-streaming generation
    routing_meta = None
    if use_orchestrator:
        from app.services.llm_orchestrator import TaskType
        reply, report, decision = await orchestrator.generate(
            user_text=user_text,
            face_emotion=face_emotion,
            history=history,
            text_emotion_summary=text_emotion_summary,
            patient_profile=patient_profile,
            semantic_memories=semantic_memories,
            gita_context=gita_context,
            task_type=TaskType.ROUTINE_CHAT,
        )
        routing_meta = RoutingMetadata(
            provider_used=decision.provider_used,
            task_type=decision.task_type,
            latency_ms=decision.latency_ms,
            fallback_used=decision.fallback_used,
            fallback_provider=decision.fallback_provider,
            pii_scrubbed=decision.pii_scrubbed,
            pii_types=decision.pii_types,
            error=decision.error,
        )
    else:
        reply, report = await ollama_engine.generate(
            user_text=user_text,
            face_emotion=face_emotion,
            history=history,
            text_emotion_summary=text_emotion_summary,
            patient_profile=patient_profile,
            semantic_memories=semantic_memories,
            gita_context=gita_context,
        )

    # ── Step 7: Save Session + Background Summarization ──────────────────────
    if user_id:
        try:
            mem = get_patient_memory()
            mem.save_session(
                user_id=user_id,
                dominant_emotion=dominant_text_emotion,
                risk_level=report.risk_classification.value,
                fusion_score=float(fusion.final_risk_score),
                cognitive_distortions=report.cognitive_distortions,
                interventions=report.suggested_interventions,
                summary=report.emotional_state_summary,
                user_message=user_text[:200],
            )
        except Exception as e:
            logger.warning("Failed to save session to patient memory: %s", e)

        # Fire-and-forget background summarization
        if settings.SESSION_SUMMARY_ENABLED:
            try:
                from app.services.session_summarizer import summarize_and_save
                asyncio.create_task(
                    summarize_and_save(
                        user_id=user_id,
                        user_message=user_text[:500],
                        risk_level=report.risk_classification.value,
                        emotion=dominant_text_emotion,
                        distortions=report.cognitive_distortions,
                    )
                )
            except Exception as e:
                logger.debug("Background summarization task creation failed: %s", e)

        # Fire-and-forget reflection engine
        try:
            from app.services.reflection_engine import run_reflection
            asyncio.create_task(
                run_reflection(
                    user_id=user_id,
                    user_message=user_text[:500],
                    risk_level=report.risk_classification.value,
                    emotion=dominant_text_emotion
                )
            )
        except Exception as e:
            logger.debug("Background reflection task creation failed: %s", e)

    return ChatResponse(
        response=reply,
        report=report,
        text_emotion=text_labels,
        fusion_risk_score=float(fusion.final_risk_score),
        remedy=remedy,
        routing=routing_meta,
    )
