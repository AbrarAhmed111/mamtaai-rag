"""
Phase 1: LLM Chat API with LLM Gateway Layer

Features:
- Multi-provider support (Gemini x4, Groq, OpenAI, Mistral, Cerebras)
- Automatic fallback on rate limits (429), quota exhaustion, or temporary outages
- Cooldown tracking to prevent repeatedly hitting rate-limited providers
- User-facing provider status events ("fallback", "switched")
- Zero API key leakage
"""

import os
from typing import List, Optional
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from gateway import LLMGateway, ProviderStatusEvent

# -----------------------------------------------------------------------------
# 1. Environment & Gateway Setup
# -----------------------------------------------------------------------------
load_dotenv()

# Initialize the LLM Gateway with multiple provider deployments and cooldown tracking
gateway = LLMGateway(max_attempts=5, cooldown_seconds=60)


# -----------------------------------------------------------------------------
# 2. Request & Response Schemas
# -----------------------------------------------------------------------------
class ChatMessage(BaseModel):
    """Represents a single message in conversation."""
    role: str = Field(default="user", description="Sender role: user, assistant, or system")
    content: str = Field(..., min_length=1, description="Message text content")


class ChatRequest(BaseModel):
    """Request payload from client."""
    messages: List[ChatMessage] = Field(..., min_length=1, description="Conversation messages")
    temperature: Optional[float] = Field(0.7, ge=0.0, le=2.0, description="Creativity temperature")
    max_tokens: Optional[int] = Field(None, gt=0, description="Max tokens to generate")


class ProviderStatusEventSchema(BaseModel):
    """Structured status event emitted when a provider switches or fails over."""
    type: str = "provider_status"
    status: str = Field(..., description="Event status: 'fallback' or 'switched'")
    message: str = Field(..., description="User-facing status message")
    provider: str = Field(..., description="Name of the provider deployment")


class UsageInfo(BaseModel):
    """Token usage reporting."""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class ChatResponse(BaseModel):
    """Chat completion response including provider info and fallback events."""
    reply: str
    provider: str
    model: str
    usage: UsageInfo
    status_events: List[ProviderStatusEventSchema] = []


# -----------------------------------------------------------------------------
# 3. Message Conversion Helper
# -----------------------------------------------------------------------------
def to_langchain_message(msg: ChatMessage) -> BaseMessage:
    """Map incoming message schema to LangChain message abstractions."""
    if msg.role == "system":
        return SystemMessage(content=msg.content)
    elif msg.role == "assistant":
        return AIMessage(content=msg.content)
    else:
        return HumanMessage(content=msg.content)


# -----------------------------------------------------------------------------
# 4. FastAPI Application
# -----------------------------------------------------------------------------
app = FastAPI(
    title="MumtaAI - LLM Gateway",
    description="LLM Chat Gateway with multi-provider fallback and cooldown management.",
    version="1.0.0",
)


@app.get("/health")
async def health():
    """Health check endpoint."""
    available_count = len(gateway.get_available_deployments())
    total_count = len(gateway.deployments)
    return {
        "status": "healthy",
        "configured_deployments": total_count,
        "available_deployments": available_count,
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Main Chat Endpoint backed by LLM Gateway:
    Receives request -> Gateway executes with automatic fallback -> Returns answer + status events.
    """
    try:
        # Convert request messages to LangChain messages
        langchain_messages = [to_langchain_message(m) for m in request.messages]

        # Execute through the LLM Gateway
        reply, provider_name, model_name, usage, status_events = await gateway.generate(
            messages=langchain_messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )

        return ChatResponse(
            reply=reply,
            provider=provider_name,
            model=model_name,
            usage=UsageInfo(**usage),
            status_events=[
                ProviderStatusEventSchema(
                    type=ev.type,
                    status=ev.status,
                    message=ev.message,
                    provider=ev.provider,
                )
                for ev in status_events
            ],
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM Gateway Error: {str(e)}")


# -----------------------------------------------------------------------------
# 5. Local Development Server Runner
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    print(f"\n🚀 MumtaAI LLM Gateway running at http://localhost:{port}")
    print(f"📖 Interactive API Docs available at http://localhost:{port}/docs\n")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
