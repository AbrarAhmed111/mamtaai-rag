"""
Unit tests for LLM Gateway layer (tests/test_gateway.py).
Tests fallback, error classification, cooldown tracking, and status events using offline mocks.
"""

import pytest
import time
from unittest.mock import patch, AsyncMock
from langchain_core.messages import HumanMessage, AIMessage

from services.gateway import LLMGateway, ProviderDeployment, ErrorClassifier, ProviderStatusEvent

PATCH_AINVOKE = "services.gateway.ChatOpenAI.ainvoke"


@pytest.fixture
def mock_gateway():
    """Create a gateway with 3 test deployments."""
    gw = LLMGateway(max_attempts=3, cooldown_seconds=5)
    # Manually configure test deployments
    gw.deployments = [
        ProviderDeployment(
            name="Gemini #1",
            provider="gemini",
            api_key="mock-key-1",
            base_url="https://mock.gemini.api/v1",
            default_model="gemini-1.5-flash",
            cooldown_seconds=5,
        ),
        ProviderDeployment(
            name="Gemini #2",
            provider="gemini",
            api_key="mock-key-2",
            base_url="https://mock.gemini.api/v1",
            default_model="gemini-1.5-flash",
            cooldown_seconds=5,
        ),
        ProviderDeployment(
            name="Groq",
            provider="groq",
            api_key="mock-groq-key",
            base_url="https://mock.groq.api/v1",
            default_model="llama-3.3-70b-versatile",
            cooldown_seconds=5,
        ),
    ]
    return gw


@pytest.mark.asyncio
async def test_gateway_first_provider_success(mock_gateway):
    """When first provider succeeds, return answer with zero status events."""
    mock_ai_resp = AIMessage(
        content="Success from Gemini 1",
        usage_metadata={"input_tokens": 10, "output_tokens": 5, "total_tokens": 15},
    )

    with patch(PATCH_AINVOKE, new_callable=AsyncMock) as mock_invoke:
        mock_invoke.return_value = mock_ai_resp

        messages = [HumanMessage(content="Hello!")]
        reply, provider, model, usage, events = await mock_gateway.generate(messages)

        assert reply == "Success from Gemini 1"
        assert provider == "Gemini #1"
        assert model == "gemini-1.5-flash"
        assert usage["total_tokens"] == 15
        assert len(events) == 0  # No fallback occurred


@pytest.mark.asyncio
async def test_gateway_fallback_on_429(mock_gateway):
    """
    When Gemini #1 hits 429 rate limit, fallback to Gemini #2.
    Assert status events contain 'fallback' and 'switched'.
    """
    mock_ai_resp = AIMessage(
        content="Success from Gemini 2",
        usage_metadata={"input_tokens": 10, "output_tokens": 8, "total_tokens": 18},
    )

    call_count = 0

    async def side_effect(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise Exception("HTTP 429 Too Many Requests: Resource has been exhausted (quota exceeded)")
        return mock_ai_resp

    with patch(PATCH_AINVOKE, side_effect=side_effect):
        messages = [HumanMessage(content="Hello!")]
        reply, provider, model, usage, events = await mock_gateway.generate(messages)

        assert reply == "Success from Gemini 2"
        assert provider == "Gemini #2"
        assert len(events) == 2

        # Event 1: Fallback from Gemini #1
        assert events[0].status == "fallback"
        assert "Gemini #1 has reached its current API limit" in events[0].message
        assert events[0].provider == "Gemini #1"

        # Event 2: Switched to Gemini #2
        assert events[1].status == "switched"
        assert "Switched to Gemini #2 successfully." in events[1].message
        assert events[1].provider == "Gemini #2"


@pytest.mark.asyncio
async def test_gateway_cooldown_skips_failed_provider(mock_gateway):
    """
    After Gemini #1 hits 429, it should be in cooldown and skipped on the next request.
    """
    # Put Gemini #1 in cooldown
    mock_gateway.deployments[0].mark_cooldown(seconds=10)

    # Verify Gemini #1 is not available
    available = mock_gateway.get_available_deployments()
    assert len(available) == 2
    assert available[0].name == "Gemini #2"
    assert available[1].name == "Groq"


@pytest.mark.asyncio
async def test_gateway_non_retryable_error(mock_gateway):
    """
    A 400 Bad Request error should NOT trigger fallback; it must raise immediately.
    """
    with patch(PATCH_AINVOKE, side_effect=Exception("400 Bad Request: Invalid prompt format")):
        messages = [HumanMessage(content="Bad input")]
        with pytest.raises(Exception) as exc_info:
            await mock_gateway.generate(messages)
        assert "400 Bad Request" in str(exc_info.value)


@pytest.mark.asyncio
async def test_error_classifier():
    """Verify classification of different error types."""
    # Rate limits & quotas
    assert ErrorClassifier.is_retryable(Exception("429 Too Many Requests"))[0] is True
    assert ErrorClassifier.is_retryable(Exception("Quota exceeded for quota metric"))[0] is True
    assert ErrorClassifier.is_retryable(Exception("503 Service Unavailable"))[0] is True

    # Non-retryable
    assert ErrorClassifier.is_retryable(Exception("401 Unauthorized: Invalid API Key"))[0] is False
    assert ErrorClassifier.is_retryable(Exception("400 Bad Request"))[0] is False
