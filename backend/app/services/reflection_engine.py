import logging
import json
from typing import Optional
from datetime import datetime, timezone
from app.services.patient_memory import get_patient_memory

logger = logging.getLogger(__name__)

_REFLECTION_PROMPT = """You are an internal reflection engine for an AI therapist.
Analyze the following interaction and extract key psychological facts, stressors, and traits about the patient.
Return a JSON object with the following structure exactly (output only JSON):
{
  "new_facts": ["fact 1", "fact 2"],
  "stressors": ["stressor 1"],
  "personality_traits": ["trait 1"],
  "emotional_shift": {"start": "anxious", "end": "calm"},
  "unresolved_topics": ["topic 1"]
}

Patient message: "{user_message}"
Risk level: {risk_level}, Emotion: {emotion}
"""

async def run_reflection(user_id: str, user_message: str, risk_level: str, emotion: str) -> None:
    try:
        from app.services.llm_orchestrator import get_orchestrator
        import httpx

        orchestrator = get_orchestrator()
        
        # Determine client to use
        base_url = None
        model_name = None
        url = ""
        if orchestrator._local_available and orchestrator._local:
            base_url = orchestrator._local.base_url
            model_name = orchestrator._local.model_name
            url = f"{base_url}/api/chat"
        elif orchestrator._cloud_available and orchestrator._cloud:
            base_url = orchestrator._cloud.base_url
            model_name = orchestrator._cloud.model_name
            url = f"{base_url}/chat/completions"
        else:
            return

        prompt = _REFLECTION_PROMPT.format(
            user_message=user_message[:500],
            risk_level=risk_level,
            emotion=emotion
        )

        messages = [
            {"role": "system", "content": "You are a clinical analysis engine. Output ONLY valid JSON."},
            {"role": "user", "content": prompt}
        ]

        async with httpx.AsyncClient(timeout=30.0) as client:
            if "groq" in url:
                headers = {"Authorization": f"Bearer {orchestrator._settings.GROQ_API_KEY}"}
                response = await client.post(url, headers=headers, json={"model": model_name, "messages": messages, "response_format": {"type": "json_object"}})
            else:
                response = await client.post(url, json={"model": model_name, "messages": messages, "stream": False, "format": "json"})

            if response.status_code == 200:
                data = response.json()
                content = ""
                if "groq" in url:
                    content = data["choices"][0]["message"]["content"]
                else:
                    content = data.get("message", {}).get("content", "")
                
                try:
                    analysis = json.loads(content)
                    _update_memory(user_id, user_message, analysis)
                except json.JSONDecodeError:
                    logger.error("Failed to parse reflection JSON: %s", content)

    except Exception as exc:
        logger.error("Reflection engine failed: %s", exc)

def _update_memory(user_id: str, user_message: str, analysis: dict):
    mem = get_patient_memory()
    now = datetime.now(timezone.utc).isoformat()
    
    # 1. Add Semantic Memories
    if hasattr(mem, "add_semantic_memory"):
        for fact in analysis.get("new_facts", []):
            mem.add_semantic_memory(user_id, fact, category="fact")
            
    # 2. Update Episodic Timeline and Mind Model
    if mem.backend == "sqlite":
        import sqlite3
        conn = mem._get_conn()
        try:
            conn.execute(
                '''INSERT INTO episodic_timeline 
                   (user_id, timestamp, event_summary, emotional_shift, unresolved_topics)
                   VALUES (?, ?, ?, ?, ?)''',
                (user_id, now, user_message[:200], json.dumps(analysis.get("emotional_shift", {})), json.dumps(analysis.get("unresolved_topics", [])))
            )
            
            # 3. Update User Mind Model
            mind_model = conn.execute("SELECT * FROM user_mind_model WHERE user_id = ?", (user_id,)).fetchone()
            if mind_model:
                traits = json.loads(mind_model["personality_traits"] or "[]")
                stressors = json.loads(mind_model["stressors"] or "[]")
                
                traits = list(set(traits + analysis.get("personality_traits", [])))
                stressors = list(set(stressors + analysis.get("stressors", [])))
                
                conn.execute(
                    '''UPDATE user_mind_model SET personality_traits = ?, stressors = ?, last_updated = ? WHERE user_id = ?''',
                    (json.dumps(traits), json.dumps(stressors), now, user_id)
                )
            else:
                conn.execute(
                    '''INSERT INTO user_mind_model (user_id, personality_traits, stressors, last_updated)
                       VALUES (?, ?, ?, ?)''',
                    (user_id, json.dumps(analysis.get("personality_traits", [])), json.dumps(analysis.get("stressors", [])), now)
                )
            conn.commit()
            logger.info("Reflection engine updated memory for user %s", user_id)
        except Exception as exc:
            logger.error("Failed to save reflection to db: %s", exc)
        finally:
            conn.close()
