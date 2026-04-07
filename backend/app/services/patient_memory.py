"""
Patient Memory Engine — Dual-mode (SQLite local + Supabase cloud)

Provides per-patient adaptive learning by tracking:
  - Recurring emotions across sessions
  - Risk classification trends (improving/worsening)
  - Cognitive distortions history
  - Interventions tried
  - Conversation themes

Generates a compact profile string (≤500 tokens) injected into the LLM prompt
so the model becomes progressively more accustomed to each patient.
"""

import json
import logging
import sqlite3
import os
import time
from collections import Counter
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# SQLite Schema
# ---------------------------------------------------------------------------

_SQLITE_SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    conversation_id TEXT,
    created_at TEXT NOT NULL,
    dominant_emotion TEXT,
    risk_level TEXT,
    fusion_score REAL,
    cognitive_distortions TEXT,  -- JSON array
    interventions TEXT,          -- JSON array
    summary TEXT,
    user_message TEXT
);

CREATE TABLE IF NOT EXISTS patient_profiles (
    user_id TEXT PRIMARY KEY,
    emotional_patterns TEXT,    -- JSON: {"sad": 5, "anxious": 3, ...}
    risk_trend TEXT,            -- "improving", "stable", "worsening"
    recurring_themes TEXT,      -- JSON array of theme strings
    sessions_count INTEGER DEFAULT 0,
    last_updated TEXT
);

CREATE TABLE IF NOT EXISTS patient_preferences (
    user_id TEXT PRIMARY KEY,
    preferred_tone TEXT DEFAULT 'warm',
    verbosity TEXT DEFAULT 'moderate',
    framework_preference TEXT DEFAULT 'auto',
    topics_to_avoid TEXT,          -- JSON array
    engagement_score REAL DEFAULT 0.5,
    last_updated TEXT
);

CREATE TABLE IF NOT EXISTS progress_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    snapshot_date TEXT NOT NULL,
    period_start TEXT,
    period_end TEXT,
    avg_risk_score REAL,
    dominant_emotions TEXT,     -- JSON array
    sessions_count INTEGER,
    improvement_score REAL,    -- -1 to 1
    summary TEXT,
    created_at TEXT
);

CREATE TABLE IF NOT EXISTS session_feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    session_id INTEGER,
    message_id TEXT,
    rating INTEGER,
    comment TEXT,
    created_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_created ON sessions(created_at);
CREATE INDEX IF NOT EXISTS idx_progress_user ON progress_snapshots(user_id);
CREATE INDEX IF NOT EXISTS idx_feedback_user ON session_feedback(user_id);
"""


class PatientMemoryEngine:
    """Dual-backend patient memory: SQLite (local) or Supabase (cloud)."""

    def __init__(self, backend: str = "sqlite", sqlite_path: str = "", supabase_url: str = "", supabase_key: str = "", max_sessions: int = 20):
        self.backend = backend
        self.max_sessions = max_sessions
        self._cache: Dict[str, tuple[str, float]] = {}  # user_id -> (profile_str, timestamp)
        self._cache_ttl = 300  # 5 min TTL

        if backend == "sqlite":
            # Ensure data dir exists
            if not sqlite_path:
                base = os.path.dirname(os.path.abspath(__file__))
                data_dir = os.path.join(base, "..", "data")
                os.makedirs(data_dir, exist_ok=True)
                sqlite_path = os.path.join(data_dir, "patient_memory.db")

            self._db_path = sqlite_path
            self._init_sqlite()
            logger.info("[OK] PatientMemory initialized (SQLite: %s)", sqlite_path)
        elif backend == "supabase":
            try:
                from supabase import create_client
                self._supabase = create_client(supabase_url, supabase_key)
                logger.info("[OK] PatientMemory initialized (Supabase)")
            except ImportError:
                logger.warning("supabase package not installed, falling back to SQLite")
                self.backend = "sqlite"
                base = os.path.dirname(os.path.abspath(__file__))
                data_dir = os.path.join(base, "..", "data")
                os.makedirs(data_dir, exist_ok=True)
                self._db_path = os.path.join(data_dir, "patient_memory.db")
                self._init_sqlite()
            except Exception as exc:
                logger.warning("Supabase init failed (%s), falling back to SQLite", exc)
                self.backend = "sqlite"
                base = os.path.dirname(os.path.abspath(__file__))
                data_dir = os.path.join(base, "..", "data")
                os.makedirs(data_dir, exist_ok=True)
                self._db_path = os.path.join(data_dir, "patient_memory.db")
                self._init_sqlite()
        else:
            logger.warning("Unknown backend '%s', defaulting to SQLite", backend)
            self.backend = "sqlite"
            base = os.path.dirname(os.path.abspath(__file__))
            data_dir = os.path.join(base, "..", "data")
            os.makedirs(data_dir, exist_ok=True)
            self._db_path = os.path.join(data_dir, "patient_memory.db")
            self._init_sqlite()

    # --- SQLite ----------------------------------------------------------------

    def _init_sqlite(self):
        """Create tables if they don't exist."""
        conn = sqlite3.connect(self._db_path)
        conn.executescript(_SQLITE_SCHEMA)
        conn.commit()
        conn.close()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        return conn

    # --- Save Session ----------------------------------------------------------

    def save_session(
        self,
        user_id: str,
        conversation_id: Optional[str] = None,
        dominant_emotion: Optional[str] = None,
        risk_level: Optional[str] = None,
        fusion_score: Optional[float] = None,
        cognitive_distortions: Optional[List[str]] = None,
        interventions: Optional[List[str]] = None,
        summary: Optional[str] = None,
        user_message: Optional[str] = None,
    ):
        """Save this interaction to patient history."""
        if not user_id:
            return

        # Invalidate cache for this user
        self._cache.pop(user_id, None)

        now = datetime.now(timezone.utc).isoformat()

        if self.backend == "sqlite":
            conn = self._get_conn()
            try:
                conn.execute(
                    """INSERT INTO sessions
                       (user_id, conversation_id, created_at, dominant_emotion,
                        risk_level, fusion_score, cognitive_distortions,
                        interventions, summary, user_message)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        user_id,
                        conversation_id,
                        now,
                        dominant_emotion,
                        risk_level,
                        fusion_score,
                        json.dumps(cognitive_distortions or []),
                        json.dumps(interventions or []),
                        summary,
                        user_message,
                    ),
                )
                conn.commit()
                # Update the profile
                self._rebuild_profile_sqlite(conn, user_id)
            except Exception as exc:
                logger.error("Failed to save session (SQLite): %s", exc)
            finally:
                conn.close()
        else:
            # Supabase mode: frontend already saves messages, so we only track profile metadata
            # We store a lightweight summary in a local SQLite as a hybrid cache
            pass

    def _rebuild_profile_sqlite(self, conn: sqlite3.Connection, user_id: str):
        """Rebuild the patient profile from all session history."""
        rows = conn.execute(
            """SELECT dominant_emotion, risk_level, fusion_score,
                      cognitive_distortions, interventions, summary, user_message, created_at
               FROM sessions WHERE user_id = ?
               ORDER BY created_at DESC LIMIT ?""",
            (user_id, self.max_sessions),
        ).fetchall()

        if not rows:
            return

        # Emotion patterns
        emotion_counts = Counter()
        risk_levels = []
        all_distortions = Counter()
        all_interventions = set()
        themes = []

        for row in rows:
            if row["dominant_emotion"]:
                emotion_counts[row["dominant_emotion"]] += 1
            if row["risk_level"]:
                risk_levels.append(row["risk_level"])
            try:
                distortions = json.loads(row["cognitive_distortions"] or "[]")
                for d in distortions:
                    all_distortions[d] += 1
            except (json.JSONDecodeError, TypeError):
                pass
            try:
                interventions = json.loads(row["interventions"] or "[]")
                all_interventions.update(interventions)
            except (json.JSONDecodeError, TypeError):
                pass
            if row["user_message"]:
                # Extract short theme from user message (first 100 chars)
                themes.append(row["user_message"][:100])

        # Risk trend analysis
        risk_order = {"MINIMAL": 0, "LOW": 1, "MODERATE": 2, "HIGH": 3, "CRITICAL": 4}
        if len(risk_levels) >= 3:
            recent = [risk_order.get(r, 2) for r in risk_levels[:3]]
            older = [risk_order.get(r, 2) for r in risk_levels[-3:]]
            avg_recent = sum(recent) / len(recent)
            avg_older = sum(older) / len(older)
            if avg_recent < avg_older - 0.3:
                risk_trend = "improving"
            elif avg_recent > avg_older + 0.3:
                risk_trend = "worsening"
            else:
                risk_trend = "stable"
        elif risk_levels:
            risk_trend = "insufficient_data"
        else:
            risk_trend = "unknown"

        now = datetime.now(timezone.utc).isoformat()
        conn.execute(
            """INSERT OR REPLACE INTO patient_profiles
               (user_id, emotional_patterns, risk_trend, recurring_themes,
                sessions_count, last_updated)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                user_id,
                json.dumps(dict(emotion_counts.most_common(10))),
                risk_trend,
                json.dumps(themes[:10]),
                len(rows),
                now,
            ),
        )
        conn.commit()

    # --- Get Patient Profile ---------------------------------------------------

    def get_patient_profile(self, user_id: str) -> Optional[str]:
        """
        Returns a compact natural-language profile string for LLM injection.
        Returns None if user has no history.
        """
        if not user_id:
            return None

        # Check cache
        cached = self._cache.get(user_id)
        if cached and (time.time() - cached[1]) < self._cache_ttl:
            return cached[0]

        profile_str = self._build_profile_string(user_id)
        if profile_str:
            self._cache[user_id] = (profile_str, time.time())
        return profile_str

    def _build_profile_string(self, user_id: str) -> Optional[str]:
        """Build a natural-language profile from stored data."""
        if self.backend == "sqlite":
            return self._build_profile_sqlite(user_id)
        else:
            return self._build_profile_supabase(user_id)

    def _build_profile_sqlite(self, user_id: str) -> Optional[str]:
        conn = self._get_conn()
        try:
            profile = conn.execute(
                "SELECT * FROM patient_profiles WHERE user_id = ?", (user_id,)
            ).fetchone()

            if not profile:
                return None

            sessions_count = profile["sessions_count"]
            if sessions_count == 0:
                return None

            # Parse stored data
            try:
                emotional_patterns = json.loads(profile["emotional_patterns"] or "{}")
            except (json.JSONDecodeError, TypeError):
                emotional_patterns = {}

            risk_trend = profile["risk_trend"] or "unknown"

            # Get recent sessions for more specific context
            recent = conn.execute(
                """SELECT dominant_emotion, risk_level, cognitive_distortions,
                          interventions, user_message, created_at
                   FROM sessions WHERE user_id = ?
                   ORDER BY created_at DESC LIMIT 5""",
                (user_id,),
            ).fetchall()

            # Build compact profile
            parts = []
            parts.append(f"This patient has had {sessions_count} previous session(s) with you.")

            # Emotional patterns
            if emotional_patterns:
                top_emotions = list(emotional_patterns.items())[:5]
                emotion_str = ", ".join(f"{e} ({c}x)" for e, c in top_emotions)
                parts.append(f"Recurring emotional patterns: {emotion_str}.")

            # Risk trend
            trend_map = {
                "improving": "Their overall risk level has been IMPROVING over recent sessions — positive progress.",
                "worsening": "Their risk level has been WORSENING — they may need deeper intervention or escalation.",
                "stable": "Their risk level has been stable across sessions.",
                "insufficient_data": "Not enough sessions yet to determine a risk trend.",
            }
            if risk_trend in trend_map:
                parts.append(trend_map[risk_trend])

            # Recent cognitive distortions
            recent_distortions = set()
            for row in recent:
                try:
                    distortions = json.loads(row["cognitive_distortions"] or "[]")
                    recent_distortions.update(distortions)
                except (json.JSONDecodeError, TypeError):
                    pass
            if recent_distortions:
                parts.append(f"Recent cognitive distortions identified: {', '.join(list(recent_distortions)[:5])}.")

            # Recent session topics
            if recent and recent[0]["user_message"]:
                last_msg = recent[0]["user_message"][:150]
                parts.append(f"In their most recent session, they said: \"{last_msg}\"")

            return " ".join(parts)

        except Exception as exc:
            logger.error("Failed to build patient profile (SQLite): %s", exc)
            return None
        finally:
            conn.close()

    def _build_profile_supabase(self, user_id: str) -> Optional[str]:
        """Build profile from Supabase messages table metadata."""
        try:
            # Fetch recent messages for this user
            result = self._supabase.table("messages").select("content, metadata, created_at") \
                .eq("user_id", user_id) \
                .order("created_at", desc=True) \
                .limit(self.max_sessions * 2) \
                .execute()

            if not result.data:
                return None

            # Analyze messages
            emotion_counts = Counter()
            risk_levels = []
            distortions = set()
            user_messages = []
            session_count = 0

            for msg in result.data:
                meta = msg.get("metadata") or {}
                role = meta.get("role", "user")

                if role == "user":
                    user_messages.append(msg.get("content", "")[:100])
                    if meta.get("emotion"):
                        emotion_counts[meta["emotion"]] += 1
                    session_count += 1

                elif role == "assistant":
                    report = meta.get("report", {})
                    if report.get("risk_classification"):
                        risk_levels.append(report["risk_classification"])
                    for d in report.get("cognitive_distortions", []):
                        distortions.add(d)

            if session_count == 0:
                return None

            # Build profile
            parts = [f"This patient has had approximately {session_count} previous interactions with you."]

            if emotion_counts:
                top = emotion_counts.most_common(5)
                parts.append(f"Recurring emotions: {', '.join(f'{e} ({c}x)' for e, c in top)}.")

            # Risk trend
            risk_order = {"MINIMAL": 0, "LOW": 1, "MODERATE": 2, "HIGH": 3, "CRITICAL": 4}
            if len(risk_levels) >= 3:
                recent_avg = sum(risk_order.get(r, 2) for r in risk_levels[:3]) / 3
                older_avg = sum(risk_order.get(r, 2) for r in risk_levels[-3:]) / 3
                if recent_avg < older_avg - 0.3:
                    parts.append("Their risk level has been IMPROVING — positive progress.")
                elif recent_avg > older_avg + 0.3:
                    parts.append("Their risk level has been WORSENING — needs deeper intervention.")
                else:
                    parts.append("Their risk level has been stable.")

            if distortions:
                parts.append(f"Previously identified cognitive distortions: {', '.join(list(distortions)[:5])}.")

            if user_messages:
                parts.append(f"Recent concern: \"{user_messages[0]}\"")

            return " ".join(parts)

        except Exception as exc:
            logger.error("Failed to build patient profile (Supabase): %s", exc)
            return None


    # --- Patient Preferences ----------------------------------------------------

    def get_preferences(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get patient preferences."""
        if not user_id or self.backend != "sqlite":
            return None
        conn = self._get_conn()
        try:
            row = conn.execute(
                "SELECT * FROM patient_preferences WHERE user_id = ?", (user_id,)
            ).fetchone()
            if not row:
                return None
            topics = []
            try:
                topics = json.loads(row["topics_to_avoid"] or "[]")
            except (json.JSONDecodeError, TypeError):
                pass
            return {
                "user_id": row["user_id"],
                "preferred_tone": row["preferred_tone"] or "warm",
                "verbosity": row["verbosity"] or "moderate",
                "framework_preference": row["framework_preference"] or "auto",
                "topics_to_avoid": topics,
                "engagement_score": row["engagement_score"] or 0.5,
                "last_updated": row["last_updated"],
            }
        except Exception as exc:
            logger.error("Failed to get preferences: %s", exc)
            return None
        finally:
            conn.close()

    def update_preferences(
        self,
        user_id: str,
        preferred_tone: Optional[str] = None,
        verbosity: Optional[str] = None,
        framework_preference: Optional[str] = None,
        topics_to_avoid: Optional[List[str]] = None,
    ) -> bool:
        """Update patient preferences (upsert)."""
        if not user_id or self.backend != "sqlite":
            return False
        conn = self._get_conn()
        try:
            existing = conn.execute(
                "SELECT * FROM patient_preferences WHERE user_id = ?", (user_id,)
            ).fetchone()
            now = datetime.now(timezone.utc).isoformat()

            if existing:
                updates = []
                params = []
                if preferred_tone is not None:
                    updates.append("preferred_tone = ?")
                    params.append(preferred_tone)
                if verbosity is not None:
                    updates.append("verbosity = ?")
                    params.append(verbosity)
                if framework_preference is not None:
                    updates.append("framework_preference = ?")
                    params.append(framework_preference)
                if topics_to_avoid is not None:
                    updates.append("topics_to_avoid = ?")
                    params.append(json.dumps(topics_to_avoid))
                if updates:
                    updates.append("last_updated = ?")
                    params.append(now)
                    params.append(user_id)
                    conn.execute(
                        f"UPDATE patient_preferences SET {', '.join(updates)} WHERE user_id = ?",
                        params,
                    )
            else:
                conn.execute(
                    """INSERT INTO patient_preferences
                       (user_id, preferred_tone, verbosity, framework_preference, topics_to_avoid, last_updated)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (
                        user_id,
                        preferred_tone or "warm",
                        verbosity or "moderate",
                        framework_preference or "auto",
                        json.dumps(topics_to_avoid or []),
                        now,
                    ),
                )
            conn.commit()
            self._cache.pop(user_id, None)  # Invalidate cache
            return True
        except Exception as exc:
            logger.error("Failed to update preferences: %s", exc)
            return False
        finally:
            conn.close()

    # --- Progress Tracking ------------------------------------------------------

    def get_progress(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get patient progress data for the progress dashboard."""
        if not user_id or self.backend != "sqlite":
            return None
        conn = self._get_conn()
        try:
            # Get session data
            sessions = conn.execute(
                """SELECT dominant_emotion, risk_level, fusion_score, created_at
                   FROM sessions WHERE user_id = ?
                   ORDER BY created_at ASC""",
                (user_id,),
            ).fetchall()

            if not sessions:
                return None

            risk_order = {"MINIMAL": 0.0, "LOW": 0.25, "MODERATE": 0.5, "HIGH": 0.75, "CRITICAL": 1.0}

            # Build trends
            emotion_trend = []
            risk_trend = []
            for s in sessions:
                entry = {
                    "date": s["created_at"],
                    "emotion": s["dominant_emotion"] or "neutral",
                }
                emotion_trend.append(entry)
                risk_trend.append({
                    "date": s["created_at"],
                    "risk": s["risk_level"] or "MINIMAL",
                    "score": risk_order.get(s["risk_level"] or "MINIMAL", 0.0),
                    "fusion_score": s["fusion_score"],
                })

            # Get snapshots
            snapshots = conn.execute(
                """SELECT * FROM progress_snapshots WHERE user_id = ?
                   ORDER BY snapshot_date DESC LIMIT 10""",
                (user_id,),
            ).fetchall()

            snapshot_list = []
            for snap in snapshots:
                dominant_emos = []
                try:
                    dominant_emos = json.loads(snap["dominant_emotions"] or "[]")
                except (json.JSONDecodeError, TypeError):
                    pass
                snapshot_list.append({
                    "snapshot_date": snap["snapshot_date"],
                    "period_start": snap["period_start"],
                    "period_end": snap["period_end"],
                    "avg_risk_score": snap["avg_risk_score"] or 0.0,
                    "dominant_emotions": dominant_emos,
                    "sessions_count": snap["sessions_count"] or 0,
                    "improvement_score": snap["improvement_score"] or 0.0,
                    "summary": snap["summary"] or "",
                })

            # Get profile for current risk level
            profile = conn.execute(
                "SELECT * FROM patient_profiles WHERE user_id = ?", (user_id,)
            ).fetchone()

            return {
                "user_id": user_id,
                "total_sessions": len(sessions),
                "first_session": sessions[0]["created_at"] if sessions else None,
                "last_session": sessions[-1]["created_at"] if sessions else None,
                "current_risk_level": sessions[-1]["risk_level"] or "MINIMAL" if sessions else "MINIMAL",
                "emotion_trend": emotion_trend,
                "risk_trend": risk_trend,
                "snapshots": snapshot_list,
                "summary": profile["risk_trend"] if profile else "unknown",
            }
        except Exception as exc:
            logger.error("Failed to get progress: %s", exc)
            return None
        finally:
            conn.close()

    def save_progress_snapshot(
        self,
        user_id: str,
        period_start: str,
        period_end: str,
        avg_risk_score: float,
        dominant_emotions: List[str],
        sessions_count: int,
        improvement_score: float,
        summary: str,
    ) -> bool:
        """Save a progress snapshot."""
        if not user_id or self.backend != "sqlite":
            return False
        conn = self._get_conn()
        try:
            now = datetime.now(timezone.utc).isoformat()
            conn.execute(
                """INSERT INTO progress_snapshots
                   (user_id, snapshot_date, period_start, period_end,
                    avg_risk_score, dominant_emotions, sessions_count,
                    improvement_score, summary, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    user_id, now, period_start, period_end,
                    avg_risk_score, json.dumps(dominant_emotions),
                    sessions_count, improvement_score, summary, now,
                ),
            )
            conn.commit()
            return True
        except Exception as exc:
            logger.error("Failed to save progress snapshot: %s", exc)
            return False
        finally:
            conn.close()

    # --- Session Feedback -------------------------------------------------------

    def save_feedback(
        self,
        user_id: str,
        rating: int,
        session_id: Optional[int] = None,
        message_id: Optional[str] = None,
        comment: Optional[str] = None,
    ) -> bool:
        """Save session feedback."""
        if not user_id or self.backend != "sqlite":
            return False
        conn = self._get_conn()
        try:
            now = datetime.now(timezone.utc).isoformat()
            conn.execute(
                """INSERT INTO session_feedback
                   (user_id, session_id, message_id, rating, comment, created_at)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (user_id, session_id, message_id, rating, comment, now),
            )
            conn.commit()
            return True
        except Exception as exc:
            logger.error("Failed to save feedback: %s", exc)
            return False
        finally:
            conn.close()

    def get_avg_feedback(self, user_id: str) -> Optional[float]:
        """Get average feedback rating for a patient."""
        if not user_id or self.backend != "sqlite":
            return None
        conn = self._get_conn()
        try:
            row = conn.execute(
                "SELECT AVG(rating) as avg_rating FROM session_feedback WHERE user_id = ?",
                (user_id,),
            ).fetchone()
            return row["avg_rating"] if row and row["avg_rating"] else None
        except Exception as exc:
            logger.error("Failed to get avg feedback: %s", exc)
            return None
        finally:
            conn.close()

    # --- Enhanced Profile (with preferences) ------------------------------------

    def get_enhanced_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Returns both the LLM-injectable profile string AND structured preference data.
        Used by the adaptive prompt builder.
        """
        profile_str = self.get_patient_profile(user_id)
        preferences = self.get_preferences(user_id)
        avg_feedback = self.get_avg_feedback(user_id)

        return {
            "profile_string": profile_str,
            "preferences": preferences or {
                "preferred_tone": "warm",
                "verbosity": "moderate",
                "framework_preference": "auto",
                "topics_to_avoid": [],
                "engagement_score": 0.5,
            },
            "avg_feedback_rating": avg_feedback,
        }


# ---------------------------------------------------------------------------
# Module-level singleton (initialized by main.py or on first import)
# ---------------------------------------------------------------------------
_engine: Optional[PatientMemoryEngine] = None


def get_patient_memory() -> PatientMemoryEngine:
    """Get or create the patient memory engine singleton."""
    global _engine
    if _engine is None:
        # Default to SQLite with auto-detected path
        _engine = PatientMemoryEngine(backend="sqlite")
    return _engine


def init_patient_memory(
    backend: str = "sqlite",
    sqlite_path: str = "",
    supabase_url: str = "",
    supabase_key: str = "",
    max_sessions: int = 20,
) -> PatientMemoryEngine:
    """Initialize the patient memory engine with specific settings."""
    global _engine
    _engine = PatientMemoryEngine(
        backend=backend,
        sqlite_path=sqlite_path,
        supabase_url=supabase_url,
        supabase_key=supabase_key,
        max_sessions=max_sessions,
    )
    return _engine
