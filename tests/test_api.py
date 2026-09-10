"""
Tests for API endpoints.
"""

import pytest
from httpx import ASGITransport, AsyncClient
from unittest.mock import patch, AsyncMock

from api.main import app
from schemas.llm import ChatResponse, UsageInfo, StructuredEntitiesResponse, EntityExtractionItem


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.asyncio
async def test_health_endpoint():
    """Test health check endpoint returns 200 OK and healthy status."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_root_endpoint():
    """Test root endpoint provides info and endpoint links."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "configured_llm" in data
        assert "endpoints" in data


@pytest.mark.asyncio
async def test_ping_endpoint():
    """Test ping returns pong."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/ping")
        assert response.status_code == 200
        assert response.json() == {"pong": True}


@pytest.mark.asyncio
async def test_chat_validation_error():
    """Test that empty messages array fails validation with 422."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/chat", json={"messages": []})
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_chat_completion_mocked():
    """Test standard chat endpoint with mocked LLM service."""
    mock_response = ChatResponse(
        id="chatcmpl-test12345",
        model="gpt-4o-mini",
        role="assistant",
        content="Hello! How can I assist you today?",
        finish_reason="stop",
        usage=UsageInfo(prompt_tokens=10, completion_tokens=8, total_tokens=18),
    )

    with patch("api.routers.chat.generate_chat", new_callable=AsyncMock) as mock_generate:
        mock_generate.return_value = mock_response

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            payload = {
                "messages": [
                    {"role": "user", "content": "Hello!"}
                ]
            }
            response = await client.post("/api/chat", json=payload)
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == "chatcmpl-test12345"
            assert data["content"] == "Hello! How can I assist you today?"
            assert data["role"] == "assistant"


@pytest.mark.asyncio
async def test_structured_entities_mocked():
    """Test structured entity extraction with mocked output."""
    mock_extracted = StructuredEntitiesResponse(
        summary="Test company overview",
        sentiment="positive",
        entities=[
            EntityExtractionItem(name="Google", category="Organization", details="Tech company")
        ],
        key_points=["Innovative AI products"]
    )

    with patch("api.routers.structured.extract_structured_data", new_callable=AsyncMock) as mock_extract:
        mock_extract.return_value = mock_extracted

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            payload = {
                "text": "Google is building innovative AI products."
            }
            response = await client.post("/api/structured/entities", json=payload)
            assert response.status_code == 200
            data = response.json()
            assert data["summary"] == "Test company overview"
            assert data["sentiment"] == "positive"
            assert len(data["entities"]) == 1
            assert data["entities"][0]["name"] == "Google"
