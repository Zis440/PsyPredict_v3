import json
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Query
from app.schemas import MasterReport, ExecutiveScores, UserSegment
from app.services.patient_memory import get_patient_memory
from app.services.llm_orchestrator import get_orchestrator
import httpx

router = APIRouter()
logger = logging.getLogger(__name__)

MASTER_REPORT_PROMPT = """You are PsyPredict, an elite psychological profiler and clinical analyst.
Based on the provided patient data, generate a comprehensive 'Master Psychological Report' conforming EXACTLY to the JSON schema below.
The user is in the '{segment}' segment. Tailor your language, analysis, and examples specifically to this context (e.g., academic life and studies for students vs. corporate life and management for professionals).
Also, include a 'Bhagavad Gita Wisdom' section at the end that provides spiritual guidance tailored to their current struggles based on the Gita (e.g., Nishkama Karma, Svadharma).
Evaluate the patient across 15 distinct executive scores (0-100) and provide deep, insightful, and highly actionable analysis in human-friendly language. 
Avoid robotic psychometric jargon. Be supportive and encouraging.

DATA:
Mind Model (Traits/Stressors): {mind_model}
Semantic Facts: {semantic_facts}
Episodic Timeline (Recent Events): {timeline}

Provide the output strictly as a JSON object matching this schema:
{
  "executive_summary": "Overall summary...",
  "scores": {
    "personality_health": {"score": 85, "confidence": 92, "evidence": ["Consistent Likert responses", "Chat history shows resilience"]},
    "mental_wellness": {"score": 70, "confidence": 88, "evidence": ["Reported stress in Writing Task"]},
    "emotional_intelligence": {"score": 75, "confidence": 90, "evidence": ["High score on Emotion detection"]},
    "communication": {"score": 80, "confidence": 85, "evidence": []},
    "behavioral_stability": {"score": 60, "confidence": 80, "evidence": []},
    "stress": {"score": 40, "confidence": 95, "evidence": []},
    "anxiety": {"score": 45, "confidence": 90, "evidence": []},
    "resilience": {"score": 80, "confidence": 85, "evidence": []},
    "leadership": {"score": 75, "confidence": 88, "evidence": []},
    "growth_potential": {"score": 90, "confidence": 92, "evidence": []},
    "career_readiness": {"score": 80, "confidence": 89, "evidence": []},
    "team_compatibility": {"score": 85, "confidence": 91, "evidence": []},
    "skill_proficiency": {"score": 80, "confidence": 85, "evidence": []},
    "role_fitment": {"score": 85, "confidence": 87, "evidence": []},
    "overall_intelligence_index": {"score": 78, "confidence": 90, "evidence": []}
  },
  "personality_profile": "Analysis...",
  "emotional_intelligence_analysis": "Analysis...",
  "mental_wellness_analysis": "Analysis...",
  "behavioral_analysis": "Analysis...",
  "communication_analysis": "Analysis...",
  "leadership_analysis": "Analysis...",
  "conflict_analysis": "Analysis...",
  "career_analysis": "Analysis...",
  "skill_assessment_results": "Analysis...",
  "growth_potential_analysis": "Analysis...",
  "relationship_health_analysis": "Analysis...",
  "life_purpose_analysis": "Analysis...",
  "cognitive_patterns_analysis": "Analysis...",
  "spiritual_wellbeing_analysis": "Analysis...",
  "strengths": ["Strength 1"],
  "weaknesses": ["Weakness 1"],
  "development_areas": ["Area 1"],
  "risk_indicators": ["Indicator 1"],
  "recommendations": ["Rec 1"],
  "improvement_roadmap": "Roadmap...",
  "action_plan": "Plan...",
  "future_growth_predictions": "Predictions...",
  "bhagavad_gita_wisdom": "Wisdom..."
}
"""

@router.post("/generate/{user_id}", response_model=MasterReport)
async def generate_master_report(
    user_id: str, 
    segment: UserSegment = Query(UserSegment.PROFESSIONAL, description="Target segment")
):
    mem = get_patient_memory()
    if mem.backend != "sqlite":
        raise HTTPException(status_code=500, detail="Master reporting requires SQLite backend")

    # Gather Data
    mind_model = "{}"
    timeline = "[]"
    semantic_facts = "[]"
    try:
        conn = mem._get_conn()
        row = conn.execute("SELECT * FROM user_mind_model WHERE user_id = ?", (user_id,)).fetchone()
        if row:
            mind_model = json.dumps({
                "traits": json.loads(row["personality_traits"] or "[]"),
                "stressors": json.loads(row["stressors"] or "[]")
            })
        
        t_rows = conn.execute("SELECT * FROM episodic_timeline WHERE user_id = ? ORDER BY timestamp DESC LIMIT 10", (user_id,)).fetchall()
        t_data = []
        for r in t_rows:
            t_data.append({"summary": r["event_summary"], "shift": r["emotional_shift"]})
        timeline = json.dumps(t_data)
        
        if hasattr(mem, "chroma_client") and mem.chroma_client:
            try:
                collection = mem.chroma_client.get_collection(name=f"patient_{user_id}_memories")
                res = collection.get()
                if res and "documents" in res:
                    semantic_facts = json.dumps(res["documents"])
            except Exception:
                pass
    finally:
        if 'conn' in locals():
            conn.close()
            
    # LLM Call
    orchestrator = get_orchestrator()
    prompt = MASTER_REPORT_PROMPT.format(
        segment=segment.value.title(),
        mind_model=mind_model, 
        semantic_facts=semantic_facts, 
        timeline=timeline
    )
    
    url = ""
    base_url = None
    model_name = None
    headers = {}
    if orchestrator._cloud_available and orchestrator._cloud:
        base_url = orchestrator._cloud.base_url
        model_name = orchestrator._cloud.model_name
        url = f"{base_url}/chat/completions"
        headers = {"Authorization": f"Bearer {orchestrator._settings.GROQ_API_KEY}"}
    elif orchestrator._local_available and orchestrator._local:
        base_url = orchestrator._local.base_url
        model_name = orchestrator._local.model_name
        url = f"{base_url}/api/chat"
    else:
        raise HTTPException(status_code=503, detail="No LLM available for report generation")
        
    messages = [
        {"role": "system", "content": "You are a senior clinical psychologist. Output valid JSON."},
        {"role": "user", "content": prompt}
    ]
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            if "groq" in url:
                payload = {"model": model_name, "messages": messages, "response_format": {"type": "json_object"}}
                resp = await client.post(url, headers=headers, json=payload)
            else:
                payload = {"model": model_name, "messages": messages, "stream": False, "format": "json", "options": {"num_ctx": 8192}}
                resp = await client.post(url, json=payload)
                
            resp.raise_for_status()
            data = resp.json()
            if "groq" in url:
                content = data["choices"][0]["message"]["content"]
            else:
                content = data.get("message", {}).get("content", "")
                
            # Strip markdown wrappers if present (Llama 3 often wraps output)
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
                
            report_data = json.loads(content)
            now = datetime.now(timezone.utc).isoformat()
            
            # Save the latest scores to DB
            try:
                scores = report_data.get("scores", {})
                conn = mem._get_conn()
                
                # Check if user exists
                row = conn.execute("SELECT user_id FROM user_mind_model WHERE user_id = ?", (user_id,)).fetchone()
                if not row:
                    # Insert a new row with default values before updating
                    conn.execute("INSERT INTO user_mind_model (user_id, last_updated) VALUES (?, ?)", (user_id, now))
                
                updates = ", ".join([f"{k} = ?" for k in scores.keys()])
                # Extract the 'score' float from the MetricScore dict for the DB
                params = [v.get("score", 50.0) if isinstance(v, dict) else v for v in scores.values()] + [now, user_id]
                conn.execute(f"UPDATE user_mind_model SET {updates}, last_updated = ? WHERE user_id = ?", params)
                conn.commit()
            except Exception as e:
                logger.error(f"Failed to update scores: {e}")
            finally:
                if 'conn' in locals():
                    conn.close()
            # Fetch latest raw responses
            raw_responses = mem.get_latest_assessment_results(user_id)
                    
            return MasterReport(
                user_id=user_id,
                generated_at=now,
                raw_responses=raw_responses,
                **report_data
            )
    except Exception as e:
        logger.error(f"Master Report generation failed: {e}")
        raise HTTPException(status_code=500, detail="Report generation failed. Please try again.")
