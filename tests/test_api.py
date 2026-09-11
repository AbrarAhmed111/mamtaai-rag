"""
Tests for Phase 1 Minimal Chat API using LangChain (main.py).
"""

import pytest
from httpx import ASGITransport, AsyncClient
from unittest.mock import patch, AsyncMock
from langchain_core.messages import AIMessage

from main import app


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.asyncio
async def test_health():
    """Test health check endpoint returns healthy status."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}


@pytest.mark.asyncio
async def test_chat_validation_error():
    """Test that empty messages array returns 422 Unprocessable Entity."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/chat", json={"messages": []})
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_chat_success_mocked():
    """Test POST /chat with a mocked LangChain ChatOpenAI response."""
    mock_ai_message = AIMessage(
        content="Hello! I am a LangChain-powered assistant.",
        usage_metadata={
            "input_tokens": 12,
            "output_tokens": 9,
            "total_tokens": 21,
        },
    )

    with patch("main.ChatOpenAI.ainvoke", new_callable=AsyncMock) as mock_ainvoke:
        mock_ainvoke.return_value = mock_ai_message

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            payload = {
                "messages": [
                    {"role": "user", "content": "Hi there!"}
                ]
            }
            response = await client.post("/chat", json=payload)
            assert response.status_code == 200
            data = response.json()
            assert data["reply"] == "Hello! I am a LangChain-powered assistant."
            assert data["usage"]["total_tokens"] == 21
            assert data["usage"]["prompt_tokens"] == 12
            assert data["usage"]["completion_tokens"] == 9
