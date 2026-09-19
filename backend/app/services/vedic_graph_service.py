"""
vedic_graph_service.py — In-Memory Knowledge Graph Service for Vedic & Epic Psychology

Loads and queries the unified scriptural knowledge graph (1,972 nodes, 4,395 edges)
linking Bhagavad Gita, Upanishads, Mahabharata, Four Vedas, and Valmiki Ramayana
to human emotional distress, root causes, gentle everyday metaphors, and clinical coping parallels.
"""
from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Lazy import networkx
_nx = None
_json_graph = None


def _import_nx():
    global _nx, _json_graph
    if _nx is None:
        import networkx as nx
        from networkx.readwrite import json_graph
        _nx = nx
        _json_graph = json_graph
    return _nx, _json_graph


class ScripturalGuidance:
    """Structured guidance extracted from a graph pathway."""

    def __init__(
        self,
        scripture: str,
        citation: str,
        text: str,
        theme: str,
        principle: str,
        root_cause: str,
        clinical_parallel: str,
        patient_metaphor: str,
        gentle_action: str,
        relevance_score: float = 1.0,
    ):
        self.scripture = scripture
        self.citation = citation
        self.text = text
        self.theme = theme
        self.principle = principle
        self.root_cause = root_cause
        self.clinical_parallel = clinical_parallel
        self.patient_metaphor = patient_metaphor
        self.gentle_action = gentle_action
        self.relevance_score = relevance_score

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scripture": self.scripture,
            "citation": self.citation,
            "text": self.text,
            "theme": self.theme,
            "principle": self.principle,
            "root_cause": self.root_cause,
            "clinical_parallel": self.clinical_parallel,
            "patient_metaphor": self.patient_metaphor,
            "gentle_action": self.gentle_action,
            "relevance_score": self.relevance_score,
        }

    def to_prompt_context(self) -> str:
        """
        Formats guidance cleanly for the LLM system prompt.
        Emphasizes the simple metaphor and gentle action for patient accessibility,
        without priming the LLM to recite source scripture names or verse numbers.
        """
        lines = [
            f"Psychological Insight: \"{self.text}\"",
        ]
        if self.patient_metaphor:
            lines.append(f"Everyday Metaphor: {self.patient_metaphor}")
        if self.root_cause:
            lines.append(f"Psychological Mechanism: {self.root_cause}")
        if self.principle:
            lines.append(f"Guiding Principle: {self.principle}")
        if self.clinical_parallel:
            lines.append(f"Modern Therapeutic Parallel: {self.clinical_parallel}")
        if self.gentle_action:
            lines.append(f"Gentle Micro-Step: {self.gentle_action}")
        lines.append(f"(Background reference for context only: {self.scripture} {self.citation} — do not recite source or verse numbers)")
        return "\n".join(lines)


class VedicKnowledgeGraphService:
    """
    Singleton service managing the multi-scriptural knowledge graph.
    """

    def __init__(self, graph_path: Optional[str] = None):
        if graph_path is None:
            base = os.path.dirname(os.path.abspath(__file__))
            graph_path = os.path.join(base, "..", "data", "unified_knowledge_graph.json")
        self._graph_path = graph_path
        self._graph = None
        self._ready = False

    @property
    def is_ready(self) -> bool:
        return self._ready and self._graph is not None

    def load(self) -> bool:
        """Loads graph into memory if available."""
        if not os.path.exists(self._graph_path):
            logger.warning("Vedic graph not found at %s. Graph features will be bypassed.", self._graph_path)
            return False

        try:
            nx, json_graph = _import_nx()
            with open(self._graph_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            try:
                self._graph = json_graph.node_link_graph(data, edges="links")
            except TypeError:
                self._graph = json_graph.node_link_graph(data)

            self._ready = True
            logger.info(
                "[OK] Vedic Knowledge Graph loaded: %d nodes, %d edges",
                self._graph.number_of_nodes(),
                self._graph.number_of_edges(),
            )
            return True
        except Exception as exc:
            logger.error("Failed to load Vedic Knowledge Graph: %s", exc)
            return False

    def find_guidance(
        self,
        query: str,
        emotion: Optional[str] = None,
        top_k: int = 2,
    ) -> List[ScripturalGuidance]:
        """
        Traverses the graph based on user emotion and query text to retrieve
        holistic scriptural guidance with patient metaphors.
        """
        if not self._ready or self._graph is None:
            return []

        query_lower = query.lower()
        emo_lower = (emotion or "").lower().strip()

        # Map common user words to emotion node keys
        emotion_aliases = {
            "anxiety": ["anxiety", "fear", "panic", "worry", "stress"],
            "depression": ["depression", "sadness", "hopelessness", "grief", "despair"],
            "anger": ["anger", "rage", "irritability", "resentment", "frustration"],
            "insomnia": ["insomnia", "sleeplessness", "nightmares", "racing thoughts"],
            "burnout": ["burnout", "exhaustion", "overwork", "fatigue"],
            "loneliness": ["loneliness", "isolation", "alienation", "rejection"],
            "envy": ["envy", "jealousy", "comparison", "insecurity"],
            "grief": ["grief", "loss", "bereavement", "heartbreak"],
            "trauma": ["trauma", "shock", "intimidation", "helplessness"],
        }

        matched_emotions = set()
        if emo_lower:
            matched_emotions.add(emo_lower)
            for k, aliases in emotion_aliases.items():
                if emo_lower in aliases:
                    matched_emotions.add(k)

        for k, aliases in emotion_aliases.items():
            for alias in aliases:
                if alias in query_lower:
                    matched_emotions.add(k)
                    break

        candidate_passages = []

        # Find passages directly connected to matched emotions
        for emo in matched_emotions:
            node_id = f"emotion_{emo}"
            if self._graph.has_node(node_id):
                for neighbor in self._graph.neighbors(node_id):
                    edge_data = self._graph.get_edge_data(node_id, neighbor)
                    if edge_data and edge_data.get("relation") == "ADDRESSED_BY":
                        candidate_passages.append(neighbor)

        # If no emotion matched, find passages whose themes match query keywords
        if not candidate_passages:
            for node, data in self._graph.nodes(data=True):
                if data.get("type") == "Passage":
                    text = data.get("full_text", "").lower()
                    theme = data.get("theme", "").lower()
                    if any(w in text or w in theme for w in query_lower.split() if len(w) > 3):
                        candidate_passages.append(node)
                        if len(candidate_passages) >= top_k * 3:
                            break

        results: List[ScripturalGuidance] = []
        seen_citations = set()

        for passage_id in candidate_passages:
            if not self._graph.has_node(passage_id):
                continue
            pdata = self._graph.nodes[passage_id]
            citation = pdata.get("citation", "")
            if citation in seen_citations:
                continue
            seen_citations.add(citation)

            # Traverse 1 hop to get principle, root cause, metaphor, and action
            principle = ""
            root_cause = ""
            clinical = ""
            metaphor = ""
            action = ""

            for neighbor in self._graph.neighbors(passage_id):
                ndata = self._graph.nodes[neighbor]
                ntype = ndata.get("type")
                if ntype == "PhilosophicalPrinciple":
                    principle = ndata.get("label", "")
                    # Check 1 hop from principle to root cause and clinical analogue
                    for p_neighbor in self._graph.neighbors(neighbor):
                        p_ndata = self._graph.nodes[p_neighbor]
                        if p_ndata.get("type") == "RootCause" and not root_cause:
                            root_cause = p_ndata.get("label", "")
                        elif p_ndata.get("type") == "ClinicalAnalogue" and not clinical:
                            clinical = p_ndata.get("label", "")
                elif ntype == "PatientMetaphor":
                    metaphor = ndata.get("text", "")
                elif ntype == "GentleAction":
                    action = ndata.get("text", "")

            # Prioritize passages that have rich patient metaphors
            score = 1.0
            if metaphor:
                score += 1.5
            if action:
                score += 1.0
            if pdata.get("scripture") != "Bhagavad Gita":
                score += 0.2  # Diverse multi-scripture boost

            results.append(
                ScripturalGuidance(
                    scripture=pdata.get("scripture", "Vedic Wisdom"),
                    citation=citation,
                    text=pdata.get("full_text", pdata.get("text", "")),
                    theme=pdata.get("theme", ""),
                    principle=principle,
                    root_cause=root_cause,
                    clinical_parallel=clinical,
                    patient_metaphor=metaphor,
                    gentle_action=action,
                    relevance_score=score,
                )
            )

        results.sort(key=lambda r: r.relevance_score, reverse=True)
        return results[:top_k]


# Singleton instance
_vedic_service: Optional[VedicKnowledgeGraphService] = None


def get_vedic_graph_service() -> VedicKnowledgeGraphService:
    global _vedic_service
    if _vedic_service is None:
        _vedic_service = VedicKnowledgeGraphService()
        _vedic_service.load()
    return _vedic_service
