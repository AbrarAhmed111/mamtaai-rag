"""
API Integration Tests (tests/test_api.py).
Verifies /health and /chat endpoints using mocks.
"""

import pytest
from httpx import ASGITransport, AsyncClient
from unittest.mock import patch, AsyncMock

try:
    from src.gateway import ProviderStatusEvent
    from src.main import app
    PATCH_TARGET = "src.main.gateway.generate"
except ImportError:
    from gateway import ProviderStatusEvent
    from main import app
    PATCH_TARGET = "main.gateway.generate"


@pytest.fixture
def anyio_backend():
    return "asyncio"


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
async def test_chat_success_mocked():
    """Test POST /chat with a mocked Gateway execution."""
    mock_events = [
        ProviderStatusEvent(
            type="provider_status",
            status="fallback",
            message="Gemini #1 has reached its current API limit. Switching to another provider...",
            provider="Gemini #1",
        ),
        ProviderStatusEvent(
            type="provider_status",
            status="switched",
            message="Switched to Groq successfully.",
            provider="Groq",
        ),
    ]

    mock_return = (
        "Hello from Groq!",
        "Groq",
        "llama-3.3-70b-versatile",
        {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
        mock_events,
    )

    with patch(PATCH_TARGET, new_callable=AsyncMock) as mock_gen:
        mock_gen.return_value = mock_return

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            payload = {
                "messages": [
                    {"role": "user", "content": "Hello!"}
                ]
            }
            response = await client.post("/chat", json=payload)
            assert response.status_code == 200
            data = response.json()
            assert data["reply"] == "Hello from Groq!"
            assert data["provider"] == "Groq"
            assert data["model"] == "llama-3.3-70b-versatile"
            assert len(data["status_events"]) == 2
            assert data["status_events"][0]["status"] == "fallback"
            assert data["status_events"][1]["status"] == "switched"
