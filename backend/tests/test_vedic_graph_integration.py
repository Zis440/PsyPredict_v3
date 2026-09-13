"""
test_vedic_graph_integration.py — Integration tests for Vedic & Epic Knowledge Graph in PsyPredict
"""
import sys
import os


# Ensure backend in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.vedic_graph_service import get_vedic_graph_service
from app.services.knowledge_index import get_knowledge_index
from app.services.llm_shared import build_messages, SYSTEM_PROMPT
from app.schemas import ConversationMessage, MessageRole



def test_vedic_graph_service_loaded():
    service = get_vedic_graph_service()
    assert service.is_ready is True
    assert service._graph is not None
    # We built a graph with 1,972 nodes and 4,395 edges
    assert service._graph.number_of_nodes() >= 1000
    assert service._graph.number_of_edges() >= 2000


def test_vedic_guidance_for_diverse_emotions():
    service = get_vedic_graph_service()

    test_cases = [
        ("I feel panicked and terrified of failing my exam", "anxiety"),
        ("I cannot sleep at night, my thoughts are racing", "insomnia"),
        ("I feel completely burned out and exhausted", "burnout"),
        ("I feel so lonely and isolated from everyone", "loneliness"),
        ("I am so angry and full of resentment", "anger"),
    ]

    for query, emotion in test_cases:
        guidance = service.find_guidance(query, emotion=emotion, top_k=2)
        assert len(guidance) > 0, f"Expected guidance for emotion: {emotion}"
        top = guidance[0]
        assert top.scripture != ""
        assert top.citation != ""
        assert top.patient_metaphor != ""
        assert top.gentle_action != ""


def test_knowledge_index_integration():
    ki = get_knowledge_index()
    context = ki.get_gita_context(
        query="I have terrible exam anxiety and fear of failure",
        emotion="anxiety",
        top_k=2,
    )
    assert context is not None
    assert ("Insight — " in context or "Remedy" in context)
    assert "Gentle Metaphor for Patient" in context


def test_patient_accessibility_rules_in_system_prompt():
    assert "CRITICAL PATIENT ACCESSIBILITY & SIMPLICITY RULES (ANTI-OVERWHELM)" in SYSTEM_PROMPT
    assert "SPEAK IN CLEAR, GENTLE, SIMPLE LANGUAGE" in SYSTEM_PROMPT
    assert "USE SIMPLE EVERYDAY METAPHORS" in SYSTEM_PROMPT
    assert "LOW COGNITIVE LOAD" in SYSTEM_PROMPT


def test_chat_prompt_generation_with_wisdom_context():
    ki = get_knowledge_index()
    context = ki.get_gita_context(
        query="I cannot sleep at night because I am overthinking",
        emotion="insomnia",
        top_k=1,
    )

    history = [ConversationMessage(role=MessageRole.USER, content="I cannot sleep, I am restless")]
    messages = build_messages(
        user_text="I cannot sleep, I am restless",
        face_emotion="neutral",
        history=history,
        max_turns=5,
        gita_context=context,
    )


    system_msg = messages[0]["content"]
    assert "ANCIENT SCRIPTURAL & GITA WISDOM CONTEXT" in system_msg
    assert "Gentle Metaphor for Patient" in system_msg


if __name__ == "__main__":
    print("Running Vedic Graph Integration Tests...")
    test_vedic_graph_service_loaded()
    print("  [PASS] test_vedic_graph_service_loaded")
    test_vedic_guidance_for_diverse_emotions()
    print("  [PASS] test_vedic_guidance_for_diverse_emotions")
    test_knowledge_index_integration()
    print("  [PASS] test_knowledge_index_integration")
    test_patient_accessibility_rules_in_system_prompt()
    print("  [PASS] test_patient_accessibility_rules_in_system_prompt")
    test_chat_prompt_generation_with_wisdom_context()
    print("  [PASS] test_chat_prompt_generation_with_wisdom_context")
    print("\nALL 5 INTEGRATION TESTS PASSED SUCCESSFULLY!")

