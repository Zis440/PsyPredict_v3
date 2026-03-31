"""
progress_tracker.py — Patient Progress Analysis Engine

Periodically analyzes patient session data to:
  - Compute rolling averages of risk scores and emotion distributions
  - Detect significant changes (improvement/deterioration)
  - Flag critical patterns (escalating risk, recurring crisis)
  - Generate progress snapshots for the dashboard

Can be called on-demand per patient or as a batch job.
"""
from __future__ import annotations

import json
import logging
from collections import Counter
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Risk level numeric mapping
RISK_SCORES = {
    "MINIMAL": 0.0,
    "LOW": 0.25,
    "MODERATE": 0.5,
    "HIGH": 0.75,
    "CRITICAL": 1.0,
}


def analyze_patient_progress(
    user_id: str,
    sessions: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Analyze a patient's session history and generate a progress report.

    Args:
        user_id: Patient identifier
        sessions: List of session dicts with keys:
            dominant_emotion, risk_level, fusion_score, created_at,
            cognitive_distortions, user_message

    Returns:
        Dict with progress metrics, trends, and recommendations
    """
    if not sessions:
        return {
            "user_id": user_id,
            "status": "no_data",
            "sessions_analyzed": 0,
        }

    total = len(sessions)

    # --- Emotion Analysis ---
    emotion_counts = Counter()
    for s in sessions:
        emo = s.get("dominant_emotion", "neutral")
        if emo:
            emotion_counts[emo] += 1

    top_emotions = emotion_counts.most_common(5)

    # --- Risk Trajectory ---
    risk_values = []
    for s in sessions:
        rl = s.get("risk_level", "MINIMAL")
        risk_values.append(RISK_SCORES.get(rl, 0.0))

    avg_risk = sum(risk_values) / len(risk_values) if risk_values else 0.0

    # Recent vs. older risk comparison
    improvement_score = 0.0
    if len(risk_values) >= 4:
        half = len(risk_values) // 2
        older_avg = sum(risk_values[:half]) / half
        recent_avg = sum(risk_values[half:]) / (len(risk_values) - half)
        improvement_score = round(older_avg - recent_avg, 3)  # positive = improving

    # --- Distortion Patterns ---
    distortion_counts = Counter()
    for s in sessions:
        try:
            distortions = s.get("cognitive_distortions", [])
            if isinstance(distortions, str):
                distortions = json.loads(distortions)
            for d in distortions:
                distortion_counts[d] += 1
        except (json.JSONDecodeError, TypeError):
            pass

    recurring_distortions = distortion_counts.most_common(5)

    # --- Crisis Detection ---
    crisis_count = sum(1 for rv in risk_values if rv >= 0.75)
    crisis_rate = crisis_count / total if total > 0 else 0.0

    # --- Engagement Metrics ---
    if total >= 2:
        first_dt = _parse_date(sessions[0].get("created_at", ""))
        last_dt = _parse_date(sessions[-1].get("created_at", ""))
        if first_dt and last_dt:
            days_span = max((last_dt - first_dt).days, 1)
            sessions_per_week = (total / days_span) * 7
        else:
            sessions_per_week = 0
    else:
        sessions_per_week = 0

    # --- Status Classification ---
    if improvement_score > 0.15:
        status = "improving"
    elif improvement_score < -0.15:
        status = "declining"
    else:
        status = "stable"

    # --- Build Report ---
    return {
        "user_id": user_id,
        "status": status,
        "sessions_analyzed": total,
        "avg_risk_score": round(avg_risk, 3),
        "improvement_score": round(improvement_score, 3),
        "top_emotions": [{"emotion": e, "count": c} for e, c in top_emotions],
        "recurring_distortions": [{"distortion": d, "count": c} for d, c in recurring_distortions],
        "crisis_rate": round(crisis_rate, 3),
        "crisis_count": crisis_count,
        "sessions_per_week": round(sessions_per_week, 1),
        "dominant_emotions": [e for e, _ in top_emotions[:3]],
        "recommendations": _generate_recommendations(
            status, avg_risk, crisis_rate, top_emotions, recurring_distortions
        ),
    }


def _generate_recommendations(
    status: str,
    avg_risk: float,
    crisis_rate: float,
    top_emotions: List[Tuple[str, int]],
    recurring_distortions: List[Tuple[str, int]],
) -> List[str]:
    """Generate clinical-style recommendations based on progress data."""
    recs = []

    if status == "improving":
        recs.append("Patient showing improvement. Continue current therapeutic approach.")
    elif status == "declining":
        recs.append("Patient risk trend is worsening. Consider deepening intervention or escalation.")

    if crisis_rate > 0.3:
        recs.append(
            f"High crisis rate ({crisis_rate:.0%}). Safety planning and crisis resources should be prioritized."
        )

    if avg_risk > 0.6:
        recs.append("Sustained elevated risk. Consider more frequent sessions or medication review.")

    # Emotion-specific recommendations
    emotion_set = {e for e, _ in top_emotions[:3]}
    if "sadness" in emotion_set or "sad" in emotion_set:
        recs.append("Persistent sadness pattern. CBT or behavioral activation approaches recommended.")
    if "anger" in emotion_set:
        recs.append("Recurring anger. Consider DBT or anger management techniques.")
    if "fear" in emotion_set or "anxiety" in emotion_set:
        recs.append("Ongoing anxiety/fear. Exposure-based or mindfulness interventions may help.")

    # Distortion-specific recommendations
    for dist, count in recurring_distortions[:3]:
        if count >= 3:
            recs.append(f"Recurring distortion '{dist}' ({count}x). Target directly in CBT sessions.")

    if not recs:
        recs.append("Continue monitoring. Insufficient data for specific recommendations.")

    return recs


def _parse_date(date_str: str) -> Optional[datetime]:
    """Parse an ISO date string."""
    try:
        return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None


async def generate_and_save_snapshot(user_id: str) -> bool:
    """
    Analyze patient progress and save a snapshot.
    Called periodically or on-demand.
    """
    try:
        from app.services.patient_memory import get_patient_memory
        memory = get_patient_memory()

        if memory.backend != "sqlite":
            return False

        # Fetch all sessions
        conn = memory._get_conn()
        try:
            rows = conn.execute(
                """SELECT dominant_emotion, risk_level, fusion_score,
                          cognitive_distortions, user_message, created_at
                   FROM sessions WHERE user_id = ?
                   ORDER BY created_at ASC""",
                (user_id,),
            ).fetchall()
        finally:
            conn.close()

        if not rows:
            return False

        sessions = []
        for r in rows:
            sessions.append({
                "dominant_emotion": r["dominant_emotion"],
                "risk_level": r["risk_level"],
                "fusion_score": r["fusion_score"],
                "cognitive_distortions": r["cognitive_distortions"],
                "user_message": r["user_message"],
                "created_at": r["created_at"],
            })

        report = analyze_patient_progress(user_id, sessions)

        # Save snapshot
        now = datetime.now(timezone.utc).isoformat()
        first = sessions[0]["created_at"] if sessions else now
        last = sessions[-1]["created_at"] if sessions else now

        summary = (
            f"Status: {report['status']}. "
            f"Avg risk: {report['avg_risk_score']:.2f}. "
            f"Improvement: {report['improvement_score']:+.2f}. "
            f"Sessions: {report['sessions_analyzed']}. "
            f"Crisis rate: {report['crisis_rate']:.0%}."
        )

        return memory.save_progress_snapshot(
            user_id=user_id,
            period_start=first,
            period_end=last,
            avg_risk_score=report["avg_risk_score"],
            dominant_emotions=report["dominant_emotions"],
            sessions_count=report["sessions_analyzed"],
            improvement_score=report["improvement_score"],
            summary=summary,
        )

    except Exception as exc:
        logger.error("Failed to generate progress snapshot: %s", exc)
        return False
