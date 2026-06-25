import json
from fastapi import APIRouter, HTTPException
from app.services.patient_memory import get_patient_memory

router = APIRouter()

@router.get("/mind-model/{user_id}")
async def get_mind_model(user_id: str):
    """
    Retrieve the current Mind Model, episodic timeline, and semantic facts for the Analytics Dashboard.
    """
    mem = get_patient_memory()
    if mem.backend != "sqlite":
        raise HTTPException(status_code=500, detail="Mind model analytics requires SQLite backend")
    
    data = {
        "personality_traits": [],
        "stressors": [],
        "semantic_facts": [],
        "episodic_timeline": []
    }
    
    try:
        conn = mem._get_conn()
        
        # 1. Mind Model
        row = conn.execute("SELECT personality_traits, stressors FROM user_mind_model WHERE user_id = ?", (user_id,)).fetchone()
        if row:
            data["personality_traits"] = json.loads(row["personality_traits"] or "[]")
            data["stressors"] = json.loads(row["stressors"] or "[]")
            
        # 2. Episodic Timeline
        timeline_rows = conn.execute("SELECT timestamp, event_summary, emotional_shift, unresolved_topics FROM episodic_timeline WHERE user_id = ? ORDER BY timestamp DESC", (user_id,)).fetchall()
        for trow in timeline_rows:
            data["episodic_timeline"].append({
                "timestamp": trow["timestamp"],
                "event_summary": trow["event_summary"],
                "emotional_shift": json.loads(trow["emotional_shift"] or "{}"),
                "unresolved_topics": json.loads(trow["unresolved_topics"] or "[]")
            })
            
        # 3. Semantic Facts
        if hasattr(mem, "chroma_client") and mem.chroma_client:
            try:
                collection = mem.chroma_client.get_collection(name=f"patient_{user_id}_memories")
                results = collection.get()
                if results and "documents" in results:
                    data["semantic_facts"] = results["documents"]
            except Exception:
                pass
                
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if 'conn' in locals():
            conn.close()
