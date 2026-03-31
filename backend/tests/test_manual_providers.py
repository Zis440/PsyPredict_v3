"""
test_manual_providers.py — Manual Integration Test for LLM Providers

NOT a pytest test — run directly to compare both providers side by side.

Usage:
    # Test Groq (needs GROQ_API_KEY set in .env or environment)
    LLM_PROVIDER=groq python tests/test_manual_providers.py

    # Test Ollama (needs ollama serve running with llama3 pulled)
    LLM_PROVIDER=ollama python tests/test_manual_providers.py

    # Test both (Ollama must be running + GROQ_API_KEY set)
    python tests/test_manual_providers.py --both
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
import time

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


TEST_PROMPT = "I've been feeling really anxious about my upcoming exams. I can't sleep and keep thinking about failing."
TEST_FACE_EMOTION = "fear"


async def test_provider(provider_name: str) -> dict:
    """Test a single provider and return results."""
    print(f"\n{'='*60}")
    print(f"  Testing: {provider_name.upper()}")
    print(f"{'='*60}\n")

    # Force the provider
    os.environ["LLM_PROVIDER"] = provider_name

    # Clear caches so factory picks up new env
    from app.config import get_settings
    from app.services.llm_provider import get_llm_client

    get_settings.cache_clear()
    get_llm_client.cache_clear()

    client = get_llm_client()
    print(f"  Provider: {client.provider_name}")
    print(f"  Model:    {client.model_name}")
    print(f"  Base URL: {client.base_url}")

    # Health check
    reachable = await client.is_reachable()
    print(f"  Reachable: {'✅ Yes' if reachable else '❌ No'}")

    if not reachable:
        print(f"\n  ⚠️  {provider_name} is not reachable. Skipping generation test.")
        return {"provider": provider_name, "reachable": False}

    # Generate response
    print(f"\n  Prompt: \"{TEST_PROMPT}\"")
    print(f"  Face emotion: {TEST_FACE_EMOTION}\n")

    start = time.time()
    reply, report = await client.generate(
        user_text=TEST_PROMPT,
        face_emotion=TEST_FACE_EMOTION,
    )
    elapsed = time.time() - start

    print(f"  ── Response ({elapsed:.2f}s) ──")
    print(f"  {reply[:300]}{'...' if len(reply) > 300 else ''}")
    print(f"\n  ── PsychReport ──")
    print(f"  Risk: {report.risk_classification.value}")
    print(f"  Emotional state: {report.emotional_state_summary}")
    print(f"  Confidence: {report.confidence_score}")
    print(f"  Distortions: {report.cognitive_distortions}")
    print(f"  Interventions: {report.suggested_interventions}")
    print(f"  Service degraded: {report.service_degraded}")

    return {
        "provider": provider_name,
        "reachable": True,
        "elapsed": elapsed,
        "reply_length": len(reply),
        "risk": report.risk_classification.value,
        "confidence": report.confidence_score,
        "degraded": report.service_degraded,
    }


async def main():
    both = "--both" in sys.argv
    provider = os.environ.get("LLM_PROVIDER", "ollama")

    results = []

    if both:
        for p in ["groq", "ollama"]:
            try:
                result = await test_provider(p)
                results.append(result)
            except Exception as e:
                print(f"\n  ❌ Error testing {p}: {e}")
                results.append({"provider": p, "error": str(e)})
    else:
        try:
            result = await test_provider(provider)
            results.append(result)
        except Exception as e:
            print(f"\n  ❌ Error: {e}")
            results.append({"provider": provider, "error": str(e)})

    # Summary
    print(f"\n{'='*60}")
    print("  SUMMARY")
    print(f"{'='*60}")
    for r in results:
        status = "✅" if r.get("reachable") else "❌"
        elapsed = f"{r.get('elapsed', 0):.2f}s" if r.get("elapsed") else "N/A"
        risk = r.get("risk", "N/A")
        print(f"  {status} {r['provider']:10s} | Time: {elapsed:8s} | Risk: {risk}")

    print()


if __name__ == "__main__":
    asyncio.run(main())
