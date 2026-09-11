"""
API Integration Tests (tests/test_api.py).
Verifies /health and /chat endpoints with Intent Detection and Gateway mocking.
"""

import pytest
from httpx import ASGITransport, AsyncClient
from unittest.mock import patch, AsyncMock

from main import app
from schemas.chat import ChatResponse, UsageInfo, ProviderStatusEventSchema
from services.gateway import ProviderStatusEvent

PATCH_CHAT_SERVICE = "services.chat_service.chat_service.process_chat"
PATCH_GATEWAY_GENERATE = "services.gateway.LLMGateway.generate"


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.asyncio
async def test_root():
    """Test root endpoint returns service info."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "service" in data
        assert "endpoints" in data


@pytest.mark.asyncio
async def test_health():
    """Test health check endpoint."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "configured_deployments" in data


@pytest.mark.asyncio
async def test_chat_validation_error():
    """Test that empty messages array returns 422."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/chat", json={"messages": []})
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_chat_intent_detection_bypasses_gateway():
    """
    When user sends a simple greeting ('Hello!'), the Intent Detector intercepts it:
    - Returns canned response
    - 0 tokens used
    - Gateway.generate is NOT called
    """
    with patch(PATCH_GATEWAY_GENERATE, new_callable=AsyncMock) as mock_gen:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            payload = {
                "messages": [
                    {"role": "user", "content": "Hello!"}
                ]
            }
            response = await client.post("/chat", json=payload)
            assert response.status_code == 200
            data = response.json()
            assert data["provider"] == "canned_response"
            assert data["model"] == "rule_based"
            assert data["intent"] == "greeting"
            assert data["usage"]["total_tokens"] == 0
            assert "MumtaAI" in data["reply"]
            mock_gen.assert_not_called()


@pytest.mark.asyncio
async def test_chat_domain_query_reaches_gateway():
    """
    When user sends a MumtaAI product query ('How do I pair my oximeter?'):
    - Gateway.generate IS called
    - Intent is classified as 'oximeter'
    - Returns answer from gateway
    """
    mock_events = [
        ProviderStatusEvent(
            type="provider_status",
            status="switched",
            message="Switched to Groq successfully.",
            provider="Groq",
        ),
    ]
    mock_return = (
        "To pair your oximeter, turn on Bluetooth and tap Pair in the app.",
        "Groq",
        "llama-3.3-70b-versatile",
        {"prompt_tokens": 15, "completion_tokens": 18, "total_tokens": 33},
        mock_events,
    )

    with patch(PATCH_GATEWAY_GENERATE, new_callable=AsyncMock) as mock_gen:
        mock_gen.return_value = mock_return

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            payload = {
                "messages": [
                    {"role": "user", "content": "How do I pair my oximeter?"}
                ]
            }
            response = await client.post("/chat", json=payload)
            assert response.status_code == 200
            data = response.json()
            assert data["provider"] == "Groq"
            assert data["intent"] == "oximeter"
            assert data["usage"]["total_tokens"] == 33
            assert len(data["status_events"]) == 1
            mock_gen.assert_called_once()
