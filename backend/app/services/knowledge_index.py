"""
knowledge_index.py — Semantic Knowledge Retrieval via FAISS

Builds an in-memory FAISS index over MEDICATION.csv rows using
sentence-transformers embeddings. At query time, encodes the user
message + detected emotion into a vector and retrieves the top-k
most relevant conditions, remedies, and Gita shlokas.

Falls back to the legacy exact-match remedy_engine if the embedding
model or FAISS fails to load.
"""
from __future__ import annotations

import json
import logging
import os
import pickle
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# Lazy imports — only loaded when actually needed
_faiss = None
_SentenceTransformer = None


def _import_faiss():
    global _faiss
    if _faiss is None:
        import faiss
        _faiss = faiss
    return _faiss


def _import_st():
    global _SentenceTransformer
    if _SentenceTransformer is None:
        from sentence_transformers import SentenceTransformer
        _SentenceTransformer = SentenceTransformer
    return _SentenceTransformer


# ---------------------------------------------------------------------------
# KnowledgeResult
# ---------------------------------------------------------------------------

class KnowledgeResult:
    """Structured result from a semantic search query."""

    def __init__(
        self,
        condition: str,
        symptoms: str,
        treatments: str,
        medications: str,
        dosage: str,
        gita_remedy: str,
        relevance_score: float,
    ):
        self.condition = condition
        self.symptoms = symptoms
        self.treatments = treatments
        self.medications = medications
        self.dosage = dosage
        self.gita_remedy = gita_remedy
        self.relevance_score = relevance_score

    def to_dict(self) -> Dict[str, Any]:
        return {
            "condition": self.condition,
            "symptoms": self.symptoms,
            "treatments": self.treatments,
            "medications": self.medications,
            "dosage": self.dosage,
            "gita_remedy": self.gita_remedy,
            "relevance_score": round(self.relevance_score, 4),
        }

    def to_gita_context(self) -> str:
        """Format this result as a Gita context string for LLM injection."""
        return (
            f"Condition: {self.condition}\n"
            f"Gita Insight: {self.gita_remedy}\n"
        )


# ---------------------------------------------------------------------------
# KnowledgeIndex
# ---------------------------------------------------------------------------

class KnowledgeIndex:
    """
    Semantic index over MEDICATION.csv using FAISS + sentence-transformers.

    Usage:
        index = KnowledgeIndex()
        await index.build()  # Call once at startup
        results = index.search("I feel anxious and can't sleep", top_k=3)
    """

    def __init__(
        self,
        csv_path: Optional[str] = None,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        cache_dir: str = "",
    ):
        if csv_path is None:
            base = os.path.dirname(os.path.abspath(__file__))
            csv_path = os.path.join(base, "..", "ml_assets", "MEDICATION.csv")

        self._csv_path = csv_path
        self._model_name = model_name
        self._cache_dir = cache_dir or os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "..", "data", "index_cache"
        )

        self._model = None
        self._index = None
        self._df: Optional[pd.DataFrame] = None
        self._documents: List[str] = []  # Searchable text per row
        self._ready = False

    @property
    def is_ready(self) -> bool:
        return self._ready

    def build(self) -> bool:
        """
        Build (or load from cache) the FAISS index.
        Should be called once at startup. Synchronous to work in lifespan.
        """
        try:
            faiss = _import_faiss()
            SentenceTransformer = _import_st()

            # Load CSV
            self._df = pd.read_csv(self._csv_path)
            logger.info(
                "Knowledge index: Loaded %d rows from %s",
                len(self._df), self._csv_path,
            )

            # Build searchable text for each row
            self._documents = []
            for _, row in self._df.iterrows():
                # Combine condition + symptoms + Gita remedy for richer embedding
                parts = [
                    str(row.get("Mental Condition", "")),
                    str(row.get("Symptoms", "")),
                    str(row.get("Advanced Remedies", ""))[:200],  # Truncate Gita text
                ]
                self._documents.append(" ".join(p for p in parts if p and p != "nan"))

            # Try loading cached embeddings
            cache_path = self._get_cache_path()
            embeddings = self._load_cache(cache_path)

            if embeddings is None:
                # Compute embeddings
                logger.info("Knowledge index: Computing embeddings with %s...", self._model_name)
                self._model = SentenceTransformer(self._model_name, device="cpu")
                embeddings = self._model.encode(
                    self._documents,
                    show_progress_bar=False,
                    batch_size=64,
                    normalize_embeddings=True,
                )
                # Cache to disk
                self._save_cache(cache_path, embeddings)
                logger.info("Knowledge index: Embeddings cached to %s", cache_path)
            else:
                # Still need model for query encoding
                logger.info("Knowledge index: Loaded cached embeddings from %s", cache_path)
                self._model = SentenceTransformer(self._model_name, device="cpu")

            # Build FAISS index (Inner Product for cosine similarity with normalized vectors)
            dim = embeddings.shape[1]
            self._index = faiss.IndexFlatIP(dim)
            self._index.add(embeddings.astype(np.float32))

            self._ready = True
            logger.info(
                "[OK] Knowledge index ready: %d documents, dim=%d",
                len(self._documents), dim,
            )
            return True

        except ImportError as exc:
            logger.warning(
                "Knowledge index: Missing dependency (%s). "
                "Falling back to exact-match remedy lookup. "
                "Install with: pip install faiss-cpu sentence-transformers",
                exc,
            )
            return False
        except Exception as exc:
            logger.error("Knowledge index: Failed to build: %s", exc)
            return False

    def search(
        self,
        query: str,
        top_k: int = 3,
        emotion: Optional[str] = None,
    ) -> List[KnowledgeResult]:
        """
        Search the knowledge index for relevant conditions and remedies.

        Args:
            query: User message or search text
            top_k: Number of results to return
            emotion: Detected emotion to include in search context

        Returns:
            List of KnowledgeResult ordered by relevance
        """
        if not self._ready or self._model is None or self._index is None:
            return self._fallback_search(query, top_k, emotion)

        try:
            # Build search query with emotion context
            search_text = query
            if emotion and emotion != "neutral":
                search_text = f"{emotion}: {query}"

            # Encode query
            query_embedding = self._model.encode(
                [search_text],
                normalize_embeddings=True,
            ).astype(np.float32)

            # Search FAISS
            scores, indices = self._index.search(query_embedding, min(top_k * 2, len(self._documents)))

            # De-duplicate by condition (the CSV has multiple rows per condition)
            seen_conditions = set()
            results = []

            for score, idx in zip(scores[0], indices[0]):
                if idx < 0 or idx >= len(self._df):
                    continue

                row = self._df.iloc[idx]
                condition = str(row.get("Mental Condition", "Unknown"))

                # Skip duplicate conditions
                if condition in seen_conditions:
                    continue
                seen_conditions.add(condition)

                results.append(KnowledgeResult(
                    condition=condition,
                    symptoms=str(row.get("Symptoms", "")),
                    treatments=str(row.get("Recommended Treatments", "")),
                    medications=str(row.get("Medications", "")),
                    dosage=str(row.get("Dosage", "")),
                    gita_remedy=str(row.get("Advanced Remedies", "")),
                    relevance_score=float(score),
                ))

                if len(results) >= top_k:
                    break

            return results

        except Exception as exc:
            logger.error("Knowledge search failed: %s", exc)
            return []

    def _fallback_search(
        self,
        query: str,
        top_k: int = 3,
        emotion: Optional[str] = None,
    ) -> List[KnowledgeResult]:
        """Fast keyword/lexical search directly over MEDICATION.csv without FAISS."""
        if self._df is None:
            if os.path.exists(self._csv_path):
                try:
                    self._df = pd.read_csv(self._csv_path)
                except Exception:
                    return []
            else:
                return []

        tokens = set(query.lower().split())
        if emotion and emotion != "neutral":
            tokens.add(emotion.lower())

        stopwords = {"i", "me", "my", "feel", "feeling", "am", "is", "a", "the", "and", "to", "in", "it", "of", "so"}
        keywords = [t for t in tokens if len(t) > 2 and t not in stopwords]
        if not keywords:
            keywords = ["anxiety", "depression", "stress"]

        results = []
        seen_conditions = set()

        for idx, row in self._df.iterrows():
            cond = str(row.get("Mental Condition", ""))
            symp = str(row.get("Symptoms", ""))
            text = f"{cond} {symp}".lower()
            matches = sum(1 for kw in keywords if kw in text)
            if matches > 0 and cond not in seen_conditions:
                seen_conditions.add(cond)
                score = min(0.5 + (matches * 0.15), 0.98)
                results.append((
                    score,
                    KnowledgeResult(
                        condition=cond,
                        symptoms=symp,
                        treatments=str(row.get("Recommended Treatments", "")),
                        medications=str(row.get("Medications", "")),
                        dosage=str(row.get("Dosage", "")),
                        gita_remedy=str(row.get("Advanced Remedies", "")),
                        relevance_score=score,
                    )
                ))

        results.sort(key=lambda x: x[0], reverse=True)
        return [r[1] for r in results[:top_k]]

    def get_gita_context(
        self,
        query: str,
        emotion: Optional[str] = None,
        top_k: int = 2,
    ) -> Optional[str]:
        """
        Get formatted Gita context for LLM prompt injection.

        Returns a string with top-k Gita insights relevant to the query.
        """
        results = self.search(query, top_k=top_k, emotion=emotion)
        if not results:
            return None

        parts = []
        for i, r in enumerate(results, 1):
            if r.gita_remedy and r.gita_remedy != "nan":
                parts.append(
                    f"[Gita Insight {i} — {r.condition}]\n{r.gita_remedy}"
                )

        return "\n\n".join(parts) if parts else None

    # --- Cache Management -------------------------------------------------------

    def _get_cache_path(self) -> str:
        os.makedirs(self._cache_dir, exist_ok=True)
        return os.path.join(self._cache_dir, "medication_embeddings.pkl")

    def _load_cache(self, path: str) -> Optional[np.ndarray]:
        try:
            if os.path.exists(path):
                with open(path, "rb") as f:
                    data = pickle.load(f)
                # Validate cache shape matches current document count
                if isinstance(data, np.ndarray) and data.shape[0] == len(self._documents):
                    return data
                logger.info("Knowledge index: Cache shape mismatch, rebuilding...")
        except Exception as exc:
            logger.warning("Knowledge index: Failed to load cache: %s", exc)
        return None

    def _save_cache(self, path: str, embeddings: np.ndarray) -> None:
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "wb") as f:
                pickle.dump(embeddings, f)
        except Exception as exc:
            logger.warning("Knowledge index: Failed to save cache: %s", exc)


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

_index: Optional[KnowledgeIndex] = None


def get_knowledge_index() -> KnowledgeIndex:
    """Get or create the knowledge index singleton."""
    global _index
    if _index is None:
        from app.config import get_settings
        settings = get_settings()
        _index = KnowledgeIndex(
            model_name=settings.KNOWLEDGE_EMBEDDING_MODEL,
            cache_dir=settings.KNOWLEDGE_INDEX_CACHE_DIR,
        )
    return _index
