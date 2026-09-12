"""
Chat Service Layer
Encapsulates chatbot business logic:
1. Intent detection (zero-LLM, offline rule-based)
2. Canned response dispatch for conversational shortcuts
3. LLM Gateway invocation with automatic failover for product queries
"""

import logging
from typing import List
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage

from schemas.chat import (
    ChatMessage,
    ChatRequest,
    ChatResponse,
    UsageInfo,
    ProviderStatusEventSchema,
    FastPrompt,
    FastPromptsResponse,
)
from services.gateway import LLMGateway
from services.intent_detector import detect_intent, get_canned_response
from core.config import get_settings

logger = logging.getLogger("ChatService")
settings = get_settings()

# Initialize the LLM Gateway instance
gateway = LLMGateway(
    max_attempts=settings.GATEWAY_MAX_ATTEMPTS,
    cooldown_seconds=settings.GATEWAY_COOLDOWN_SECONDS,
)

PRODUCT_SYSTEM_PROMPT = (
    "You are the official MumtaAI Product Guide & Support Assistant. "
    "Your purpose is to provide clear, helpful, and accurate guidance about MumtaAI's product features, "
    "smart Bluetooth oximeter setup, acoustic cry analysis, caregiver sharing, and subscription tiers.\n\n"
    "CRITICAL SCOPE BOUNDARY:\n"
    "- You are strictly a product knowledge and documentation assistant.\n"
    "- You DO NOT have access to individual user account records, private databases, personal baby vitals, or billing details.\n"
    "- If a user asks about their specific personal account details (such as 'What is my baby's current SpO2?', 'Update my password', 'Show my recent cry logs'), "
    "politely clarify that you provide product guidance only and do not have access to private account data. Direct them to their Dashboard or Settings page."
)

PRODUCT_FAST_PROMPTS: List[FastPrompt] = [
    FastPrompt(
        label="What is MumtaAI?",
        prompt="What is MumtaAI and how does it help parents track infant health?",
        category="Overview",
    ),
    FastPrompt(
        label="Pair Smart Oximeter",
        prompt="How do I pair my smart Bluetooth oximeter with MumtaAI?",
        category="Hardware",
    ),
    FastPrompt(
        label="Cry Analysis Guide",
        prompt="How does acoustic cry analysis work and what cry types are recognized?",
        category="Features",
    ),
    FastPrompt(
        label="Subscription Plans",
        prompt="What are the differences between the Free, Plus, and Pro subscription plans?",
        category="Pricing",
    ),
    FastPrompt(
        label="Caregiver Sharing",
        prompt="How do caregiver permissions and family sharing work in MumtaAI?",
        category="Features",
    ),
    FastPrompt(
        label="Oximeter Alert Thresholds",
        prompt="What SpO2 and pulse rate alert thresholds does MumtaAI monitor?",
        category="Hardware",
    ),
]


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

    def get_fast_prompts(self) -> FastPromptsResponse:
        """Returns product-focused fast prompt suggestions for the chatbot UI."""
        return FastPromptsResponse(prompts=PRODUCT_FAST_PROMPTS)

    async def process_chat(self, request: ChatRequest) -> ChatResponse:
        """
        Process incoming chat messages:
        - Filters out empty messages (e.g. frontend typing indicator placeholders).
        - Extracts latest user message.
        - Evaluates intent.
        - Returns canned answer if conversational.
        - Otherwise routes through the multi-provider LLM gateway.
        """
        # Filter out empty placeholder messages from frontend UI state
        clean_messages = [m for m in request.messages if m.content and m.content.strip()]
        if not clean_messages:
            clean_messages = [ChatMessage(role="user", content="Hello")]

        latest_user_content = next(
            (m.content for m in reversed(clean_messages) if m.role == "user"),
            clean_messages[-1].content,
        )

        logger.info(f"📨 Incoming Query: \"{latest_user_content}\"")

        # 1. Intent Detection (Zero LLM, Zero Cost)
        intent_result = detect_intent(latest_user_content)

        if not intent_result.should_use_llm:
            logger.info(
                f"⚡ [INTENT DETECTED: '{intent_result.intent}'] (Confidence: {intent_result.confidence:.2f}) "
                f"-> Used: [LOCAL CANNED TEXT] | Cloud Model: NONE (0 Tokens consumed)"
            )
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
        logger.info(
            f"☁️ [INTENT DETECTED: '{intent_result.intent}'] (Confidence: {intent_result.confidence:.2f}) "
            f"-> Used: [CLOUD MODEL] | Routing to LLM Gateway across configured providers..."
        )

        langchain_messages: List[BaseMessage] = []
        # Prepend product system prompt if not present
        has_system = any(m.role == "system" for m in clean_messages)
        if not has_system:
            langchain_messages.append(SystemMessage(content=PRODUCT_SYSTEM_PROMPT))

        langchain_messages.extend([to_langchain_message(m) for m in clean_messages])

        reply, provider_name, model_name, usage, status_events = await self.gateway.generate(
            messages=langchain_messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )

        logger.info(
            f"✅ [CLOUD MODEL COMPLETED] Provider: {provider_name} | Model: {model_name} "
            f"| Total Tokens: {usage.get('total_tokens', 0)} (Prompt: {usage.get('prompt_tokens', 0)}, Completion: {usage.get('completion_tokens', 0)})"
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

