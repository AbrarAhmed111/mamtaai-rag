"""
Chat Service Layer
Encapsulates chatbot business logic:
1. Intent detection (zero-LLM, offline rule-based)
2. Canned response dispatch for conversational shortcuts
3. LLM Gateway invocation with automatic failover for product queries
"""

from typing import List
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage

from schemas.chat import (
    ChatMessage,
    ChatRequest,
    ChatResponse,
    UsageInfo,
    ProviderStatusEventSchema,
)
from services.gateway import LLMGateway
from services.intent_detector import detect_intent, get_canned_response
from core.config import get_settings

settings = get_settings()

# Initialize the LLM Gateway instance
gateway = LLMGateway(
    max_attempts=settings.GATEWAY_MAX_ATTEMPTS,
    cooldown_seconds=settings.GATEWAY_COOLDOWN_SECONDS,
)


def to_langchain_message(msg: ChatMessage) -> BaseMessage:
    """Map ChatMessage schema to LangChain message abstractions."""
    if msg.role == "system":
        return SystemMessage(content=msg.content)
    elif msg.role == "assistant":
        return AIMessage(content=msg.content)
    else:
        return HumanMessage(content=msg.content)


class ChatService:
    """Service handling conversational routing and LLM execution."""

    def __init__(self, gateway_instance: LLMGateway = gateway):
        self.gateway = gateway_instance

    async def process_chat(self, request: ChatRequest) -> ChatResponse:
        """
        Process incoming chat messages:
        - Extracts latest user message.
        - Evaluates intent.
        - Returns canned answer if conversational.
        - Otherwise routes through the multi-provider LLM gateway.
        """
        latest_user_content = next(
            (m.content for m in reversed(request.messages) if m.role == "user"),
            request.messages[-1].content,
        )

        # 1. Intent Detection (Zero LLM, Zero Cost)
        intent_result = detect_intent(latest_user_content)

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

        # 2. Substantive MumtaAI Query -> LLM Gateway
        langchain_messages = [to_langchain_message(m) for m in request.messages]

        reply, provider_name, model_name, usage, status_events = await self.gateway.generate(
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


# Singleton service instance
chat_service = ChatService()
