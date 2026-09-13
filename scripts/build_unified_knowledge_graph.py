"""
build_unified_knowledge_graph.py — Builds the Multi-Scriptural Psychological Knowledge Graph

Constructs an interconnected directed graph (networkx.DiGraph) linking:
  - Scriptures (Gita, Upanishads, Mahabharata, Vedas, Ramayana)
  - Passages & Verses (602+ entries)
  - Emotional Distress States (Anxiety, Depression, Anger, Grief, Envy, Burnout, etc.)
  - Root Causes (Attachment, Overthinking, Resistance, Comparison, etc.)
  - Philosophical Principles (Nishkama Karma, Titiksha, Samatvam, Sakshi-Bhava, etc.)
  - Modern Clinical Analogues (CBT, ACT, DBT, Behavioral Activation)
  - Gentle Everyday Metaphors (Warm, low-cognitive-load patient explanations)
  - Gentle Micro-Actions (Concrete, doable self-care steps)

Outputs:
  backend/app/data/unified_knowledge_graph.json
"""
import sys
import os
import json
import logging
from typing import Dict, Any

try:
    import networkx as nx
    from networkx.readwrite import json_graph
except ImportError:
    print("Error: networkx is required. Run: pip install networkx")
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
INPUT_JSON = os.path.join(WORKSPACE_ROOT, "backend", "app", "data", "unified_scriptural_knowledge.json")
OUTPUT_GRAPH = os.path.join(WORKSPACE_ROOT, "backend", "app", "data", "unified_knowledge_graph.json")


def build_graph():
    if not os.path.exists(INPUT_JSON):
        logger.error("Input file not found: %s. Run ingest_all_knowledge_materials.py first.", INPUT_JSON)
        return False

    with open(INPUT_JSON, "r", encoding="utf-8") as f:
        records = json.load(f)

    logger.info("Building knowledge graph from %d scriptural records...", len(records))
    G = nx.DiGraph()

    for idx, rec in enumerate(records):
        scripture_name = rec.get("scripture", "Ancient Scripture")
        citation = rec.get("citation", f"Passage {idx}")
        passage_id = f"passage_{idx}"
        
        # 1. Scripture Node
        if not G.has_node(scripture_name):
            G.add_node(scripture_name, type="Scripture", label=scripture_name)

        # 2. Passage Node
        G.add_node(
            passage_id,
            type="Passage",
            label=citation,
            citation=citation,
            text=rec.get("text", "")[:300],  # Concise preview
            full_text=rec.get("text", ""),
            scripture=scripture_name,
            theme=rec.get("psychological_theme", ""),
        )
        G.add_edge(scripture_name, passage_id, relation="CONTAINS")

        # 3. Principle Node
        principle = rec.get("philosophical_principle")
        if principle:
            principle_id = f"principle_{principle.lower().replace(' ', '_')[:30]}"
            if not G.has_node(principle_id):
                G.add_node(principle_id, type="PhilosophicalPrinciple", label=principle)
            G.add_edge(passage_id, principle_id, relation="TEACHES")

        # 4. Root Cause Node
        root_cause = rec.get("root_cause")
        if root_cause:
            cause_id = f"cause_{root_cause.lower().replace(' ', '_')[:30]}"
            if not G.has_node(cause_id):
                G.add_node(cause_id, type="RootCause", label=root_cause)
            if principle:
                G.add_edge(principle_id, cause_id, relation="COUNTERS")

        # 5. Clinical Analogue Node
        cbt = rec.get("cbt_parallel")
        if cbt:
            cbt_id = f"clinical_{cbt.lower().replace(' ', '_')[:30]}"
            if not G.has_node(cbt_id):
                G.add_node(cbt_id, type="ClinicalAnalogue", label=cbt)
            if principle:
                G.add_edge(principle_id, cbt_id, relation="MAPS_TO")

        # 6. Patient Metaphor Node (Crucial for gentle, low-cognitive-load explanation)
        metaphor = rec.get("patient_metaphor")
        if metaphor:
            metaphor_id = f"metaphor_{idx}"
            G.add_node(metaphor_id, type="PatientMetaphor", text=metaphor, label=metaphor[:50] + "...")
            G.add_edge(passage_id, metaphor_id, relation="EXPLAINED_BY")

        # 7. Gentle Action Node (Micro-coping step)
        action = rec.get("gentle_action")
        if action:
            action_id = f"action_{idx}"
            G.add_node(action_id, type="GentleAction", text=action, label=action[:50] + "...")
            G.add_edge(passage_id, action_id, relation="PRESCRIBES")

        # 8. Target Emotions Nodes & Connections
        target_emotions = rec.get("target_emotions", [])
        for emo in target_emotions:
            emo_clean = emo.strip().lower()
            if not emo_clean:
                continue
            emo_id = f"emotion_{emo_clean}"
            if not G.has_node(emo_id):
                G.add_node(emo_id, type="EmotionalDistress", label=emo_clean)
            
            # Connect Emotion -> Passage
            G.add_edge(emo_id, passage_id, relation="ADDRESSED_BY")
            # Connect Emotion -> Root Cause
            if root_cause:
                G.add_edge(emo_id, cause_id, relation="ROOTED_IN")

    logger.info("Knowledge Graph built successfully:")
    logger.info("  Total Nodes: %d", G.number_of_nodes())
    logger.info("  Total Edges: %d", G.number_of_edges())

    # Save graph as node-link JSON format
    data = json_graph.node_link_data(G)
    os.makedirs(os.path.dirname(OUTPUT_GRAPH), exist_ok=True)
    with open(OUTPUT_GRAPH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    logger.info("[SUCCESS] Exported Knowledge Graph to: %s", OUTPUT_GRAPH)
    return True


if __name__ == "__main__":
    build_graph()
