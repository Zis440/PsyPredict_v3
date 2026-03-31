"""
test_llm_clients.py — Unit Tests for PsyPredict LLM Abstraction Layer

Tests cover:
  - GroqClient and OllamaClient generate/stream/health methods (mocked HTTP)
  - Provider factory (llm_provider.py)
  - Shared utilities (parse_response, build_messages, trim_history)
  - Fallback behaviour

Run:
    cd backend
    pip install pytest pytest-asyncio
    pytest tests/test_llm_clients.py -v
"""
from __future__ import annotations

import json
import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Shared utility tests (no mocking needed)
# ---------------------------------------------------------------------------


class TestParseResponse:
    """Tests for llm_shared.parse_response"""

    def test_valid_json_with_marker(self):
        from app.services.llm_shared import parse_response

        raw = (
            "I understand you're feeling overwhelmed. Let's work through this together.\n\n"
            "---JSON---\n"
            '{"risk_classification": "LOW", "emotional_state_summary": "Mild stress", '
            '"behavioral_inference": "Seeking support", "cognitive_distortions": ["catastrophizing"], '
            '"suggested_interventions": ["journaling"], "confidence_score": 0.8, '
            '"crisis_triggered": false, "crisis_resources": null, "service_degraded": false}'
        )
        reply, report = parse_response(raw)

        assert "feeling overwhelmed" in reply
        assert report.risk_classification.value == "LOW"
        assert report.emotional_state_summary == "Mild stress"
        assert report.confidence_score == 0.8
        assert not report.service_degraded

    def test_valid_json_with_code_fences(self):
        from app.services.llm_shared import parse_response

        raw = (
            "Here is my response.\n\n"
            "---JSON---\n"
            "```json\n"
            '{"risk_classification": "MINIMAL", "emotional_state_summary": "Calm", '
            '"behavioral_inference": "Stable", "cognitive_distortions": [], '
            '"suggested_interventions": [], "confidence_score": 0.9, '
            '"crisis_triggered": false, "crisis_resources": null, "service_degraded": false}\n'
            "```"
        )
        reply, report = parse_response(raw)
        assert report.risk_classification.value == "MINIMAL"

    def test_no_json_marker(self):
        from app.services.llm_shared import parse_response

        raw = "This is just a plain text response without any JSON."
        reply, report = parse_response(raw)

        # Should use fallback report
        assert report.service_degraded is True
        assert reply == raw.strip()

    def test_invalid_json(self):
        from app.services.llm_shared import parse_response

        raw = "Some response\n---JSON---\n{invalid json here}"
        reply, report = parse_response(raw)

        assert report.service_degraded is True
        assert reply == "Some response"


class TestBuildMessages:
    """Tests for llm_shared.build_messages"""

    def test_basic_message_structure(self):
        from app.services.llm_shared import build_messages

        messages = build_messages(
            user_text="I feel sad",
            face_emotion="sad",
            history=[],
            max_turns=10,
        )

        assert len(messages) == 2  # system + user
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "user"
        assert "I feel sad" in messages[1]["content"]
        assert "MULTIMODAL CONTEXT" in messages[1]["content"]

    def test_with_history(self):
        from app.schemas import ConversationMessage, MessageRole
        from app.services.llm_shared import build_messages

        history = [
            ConversationMessage(role=MessageRole.USER, content="Hello"),
            ConversationMessage(role=MessageRole.ASSISTANT, content="Hi there"),
        ]

        messages = build_messages(
            user_text="How are you?",
            face_emotion="neutral",
            history=history,
            max_turns=10,
        )

        assert len(messages) == 4  # system + 2 history + user
        assert messages[1]["content"] == "Hello"
        assert messages[2]["content"] == "Hi there"

    def test_with_patient_profile_and_gita(self):
        from app.services.llm_shared import build_messages

        messages = build_messages(
            user_text="I need help",
            face_emotion="neutral",
            history=[],
            max_turns=10,
            patient_profile="Patient shows recurring anxiety patterns.",
            gita_context="Chapter 2, Verse 47: Focus on action, not results.",
        )

        system_msg = messages[0]["content"]
        assert "Patient shows recurring anxiety" in system_msg
        assert "Chapter 2, Verse 47" in system_msg

    def test_face_distress_score(self):
        from app.services.llm_shared import build_messages

        messages = build_messages(
            user_text="test",
            face_emotion="fear",
            history=[],
            max_turns=10,
        )

        assert "distress score: 0.80" in messages[-1]["content"]


class TestTrimHistory:
    """Tests for llm_shared.trim_history"""

    def test_no_trimming_needed(self):
        from app.schemas import ConversationMessage, MessageRole
        from app.services.llm_shared import trim_history

        history = [
            ConversationMessage(role=MessageRole.USER, content="a"),
            ConversationMessage(role=MessageRole.ASSISTANT, content="b"),
        ]
        result = trim_history(history, max_turns=5)
        assert len(result) == 2

    def test_trimming(self):
        from app.schemas import ConversationMessage, MessageRole
        from app.services.llm_shared import trim_history

        history = [
            ConversationMessage(
                role=MessageRole.USER if i % 2 == 0 else MessageRole.ASSISTANT,
                content=f"msg-{i}",
            )
            for i in range(20)
        ]
        result = trim_history(history, max_turns=3)
        assert len(result) == 6  # 3 turns × 2 messages
        assert result[0].content == "msg-14"


# ---------------------------------------------------------------------------
# Provider factory tests
# ---------------------------------------------------------------------------

class TestLLMProviderFactory:
    """Tests for llm_provider.get_llm_client"""

    def test_groq_provider(self):
        from app.services.llm_provider import get_llm_client

        # Clear the lru_cache
        get_llm_client.cache_clear()

        with patch.dict(os.environ, {"LLM_PROVIDER": "groq"}, clear=False):
            # Also need to clear settings cache
            from app.config import get_settings
            get_settings.cache_clear()

            client = get_llm_client()
            assert client.provider_name == "groq"

        # Clean up caches
        get_llm_client.cache_clear()
        from app.config import get_settings
        get_settings.cache_clear()

    def test_ollama_provider(self):
        from app.services.llm_provider import get_llm_client

        get_llm_client.cache_clear()

        with patch.dict(os.environ, {"LLM_PROVIDER": "ollama"}, clear=False):
            from app.config import get_settings
            get_settings.cache_clear()

            client = get_llm_client()
            assert client.provider_name == "ollama"

        get_llm_client.cache_clear()
        from app.config import get_settings
        get_settings.cache_clear()

    def test_unknown_provider_falls_back_to_groq(self):
        from app.services.llm_provider import get_llm_client

        get_llm_client.cache_clear()

        with patch.dict(os.environ, {"LLM_PROVIDER": "xyzinvalid"}, clear=False):
            from app.config import get_settings
            get_settings.cache_clear()

            client = get_llm_client()
            assert client.provider_name == "groq"

        get_llm_client.cache_clear()
        from app.config import get_settings
        get_settings.cache_clear()


# ---------------------------------------------------------------------------
# GroqClient tests (mocked HTTP)
# ---------------------------------------------------------------------------


class TestGroqClient:
    """Tests for GroqClient with mocked HTTP responses."""

    @pytest.mark.asyncio
    async def test_generate_success(self):
        from app.services.groq_client import GroqClient

        mock_response_data = {
            "choices": [{
                "message": {
                    "content": (
                        "I hear your pain.\n\n"
                        "---JSON---\n"
                        '{"risk_classification": "LOW", "emotional_state_summary": "Sad", '
                        '"behavioral_inference": "Seeking help", "cognitive_distortions": [], '
                        '"suggested_interventions": ["journaling"], "confidence_score": 0.75, '
                        '"crisis_triggered": false, "crisis_resources": null, "service_degraded": false}'
                    )
                }
            }]
        }

        client = GroqClient()

        with patch.object(client, "_settings") as mock_settings:
            mock_settings.GROQ_API_KEY = "test_key"
            mock_settings.GROQ_MODEL = "llama-3.3-70b-versatile"
            mock_settings.MAX_CONTEXT_TURNS = 10
            mock_settings.OLLAMA_TIMEOUT_S = 30
            mock_settings.OLLAMA_RETRIES = 1
            mock_settings.OLLAMA_RETRY_DELAY_S = 0.1

            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = mock_response_data
            mock_resp.raise_for_status = MagicMock()

            mock_client = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_resp)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)

            with patch.object(client, "_make_client", return_value=mock_client):
                reply, report = await client.generate("I feel sad")

                assert "I hear your pain" in reply
                assert report.risk_classification.value == "LOW"
                assert report.confidence_score == 0.75

    @pytest.mark.asyncio
    async def test_generate_no_api_key(self):
        from app.services.groq_client import GroqClient

        client = GroqClient()

        with patch.object(client, "_settings") as mock_settings:
            mock_settings.GROQ_API_KEY = ""

            reply, report = await client.generate("test")

            assert "not configured" in reply
            assert report.service_degraded is True

    @pytest.mark.asyncio
    async def test_health_check_success(self):
        from app.services.groq_client import GroqClient

        client = GroqClient()

        with patch.object(client, "_settings") as mock_settings:
            mock_settings.GROQ_API_KEY = "test_key"
            mock_settings.OLLAMA_TIMEOUT_S = 30

            mock_resp = AsyncMock()
            mock_resp.status_code = 200

            mock_client = AsyncMock()
            mock_client.get.return_value = mock_resp
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)

            with patch.object(client, "_make_client", return_value=mock_client):
                result = await client.is_reachable()
                assert result is True

    @pytest.mark.asyncio
    async def test_health_check_no_key(self):
        from app.services.groq_client import GroqClient

        client = GroqClient()

        with patch.object(client, "_settings") as mock_settings:
            mock_settings.GROQ_API_KEY = ""

            result = await client.is_reachable()
            assert result is False


# ---------------------------------------------------------------------------
# OllamaClient tests (mocked HTTP)
# ---------------------------------------------------------------------------


class TestOllamaClient:
    """Tests for OllamaClient with mocked HTTP responses."""

    @pytest.mark.asyncio
    async def test_generate_success(self):
        from app.services.ollama_client import OllamaClient

        mock_response_data = {
            "message": {
                "role": "assistant",
                "content": (
                    "You seem stressed.\n\n"
                    "---JSON---\n"
                    '{"risk_classification": "MODERATE", "emotional_state_summary": "Stressed", '
                    '"behavioral_inference": "Overwhelmed", "cognitive_distortions": ["catastrophizing"], '
                    '"suggested_interventions": ["breathing exercises"], "confidence_score": 0.7, '
                    '"crisis_triggered": false, "crisis_resources": null, "service_degraded": false}'
                )
            },
            "done": True,
        }

        client = OllamaClient()

        with patch.object(client, "_settings") as mock_settings:
            mock_settings.OLLAMA_BASE_URL = "http://localhost:11434"
            mock_settings.OLLAMA_MODEL_NAME = "llama3"
            mock_settings.MAX_CONTEXT_TURNS = 10
            mock_settings.OLLAMA_TIMEOUT_S = 120
            mock_settings.OLLAMA_RETRIES = 1
            mock_settings.OLLAMA_RETRY_DELAY_S = 0.1

            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = mock_response_data
            mock_resp.raise_for_status = MagicMock()

            mock_client = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_resp)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)

            with patch.object(client, "_make_client", return_value=mock_client):
                reply, report = await client.generate("I'm overwhelmed with work")

                assert "stressed" in reply.lower()
                assert report.risk_classification.value == "MODERATE"
                assert "catastrophizing" in report.cognitive_distortions

    @pytest.mark.asyncio
    async def test_health_check_success(self):
        from app.services.ollama_client import OllamaClient

        client = OllamaClient()

        with patch.object(client, "_settings") as mock_settings:
            mock_settings.OLLAMA_BASE_URL = "http://localhost:11434"
            mock_settings.OLLAMA_TIMEOUT_S = 120

            mock_resp = AsyncMock()
            mock_resp.status_code = 200

            mock_client = AsyncMock()
            mock_client.get.return_value = mock_resp
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)

            with patch.object(client, "_make_client", return_value=mock_client):
                result = await client.is_reachable()
                assert result is True

    @pytest.mark.asyncio
    async def test_health_check_unreachable(self):
        import httpx
        from app.services.ollama_client import OllamaClient

        client = OllamaClient()

        with patch.object(client, "_settings") as mock_settings:
            mock_settings.OLLAMA_BASE_URL = "http://localhost:11434"
            mock_settings.OLLAMA_TIMEOUT_S = 120

            mock_client = AsyncMock()
            mock_client.get.side_effect = httpx.ConnectError("Connection refused")
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)

            with patch.object(client, "_make_client", return_value=mock_client):
                result = await client.is_reachable()
                assert result is False
