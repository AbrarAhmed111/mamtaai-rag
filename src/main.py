"""
Phase 1: LLM Chat API with Intent Detector & LLM Gateway Layer

Architecture:
User message
    │
    ▼
Intent Detector (Zero-LLM, Rule-Based)
    │
    ├── should_use_llm == False ──► Canned Response (Zero tokens, 0ms external latency)
    │
    └── should_use_llm == True  ──► LLM Gateway (Multi-provider fallback across Gemini x4, Groq, OpenAI, Mistral, Cerebras)
"""

import os
from typing import List, Optional
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage

from gateway import LLMGateway, ProviderStatusEvent
from intent_detector import detect_intent, get_canned_response

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
    """Chat completion response including provider info, intent, and fallback events."""
    reply: str
    provider: str
    model: str
    usage: UsageInfo
    intent: Optional[str] = Field(None, description="Detected user intent")
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
    title="MumtaAI - LLM Gateway with Intent Detection",
    description="User-facing chatbot backend with offline intent detection and multi-provider failover.",
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
    Main Chat Endpoint:
    1. Runs code-based Intent Detector on latest user message.
    2. If conversational (greeting, thanks, goodbye, etc.) -> returns zero-token canned response.
    3. If MumtaAI product query or unknown -> invokes LLM Gateway with automatic fallback.
    """
    try:
        # Extract the latest user message from conversation history
        latest_user_content = next(
            (m.content for m in reversed(request.messages) if m.role == "user"),
            request.messages[-1].content,
        )

        # ---------------------------------------------------------------------
        # STEP 1: Code-Based Intent Detection (Zero LLM / Zero Token)
        # ---------------------------------------------------------------------
        intent_result = detect_intent(latest_user_content)

        # If safe to bypass LLM/RAG (e.g. greeting, thanks, goodbye, acknowledgement)
        if not intent_result.should_use_llm:
            canned_reply = get_canned_response(intent_result.intent)
            return ChatResponse(
                reply=canned_reply,
                provider="canned_response",
                model="rule_based",
                usage=UsageInfo(prompt_tokens=0, completion_tokens=0, total_tokens=0),
                intent=intent_result.intent,
                status_events=[],
            )

        # ---------------------------------------------------------------------
        # STEP 2: Substantive MumtaAI or Unknown Query -> LLM Gateway Pipeline
        # ---------------------------------------------------------------------
        langchain_messages = [to_langchain_message(m) for m in request.messages]

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
            intent=intent_result.intent,
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
        raise HTTPException(status_code=500, detail=f"Chat Execution Error: {str(e)}")


# -----------------------------------------------------------------------------
# 5. Local Development Server Runner
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    print(f"\n🚀 MumtaAI Chat Server running at http://localhost:{port}")
    print(f"📖 Interactive API Docs available at http://localhost:{port}/docs\n")
    uvicorn.run("src.main:app", host="0.0.0.0", port=port, reload=True)
