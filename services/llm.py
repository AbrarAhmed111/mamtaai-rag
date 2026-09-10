"""
Unified LLM Service
Provides high-level async methods for:
- Standard chat completions
- Real-time streaming completions (Server-Sent Events / SSE)
- Pydantic structured data extraction
- Vector embeddings generation

Works with OpenAI, Groq, DeepSeek, Ollama, OpenRouter, and any OpenAI-compatible provider.
"""

import json
from typing import AsyncGenerator, List, Optional, Type, TypeVar
from pydantic import BaseModel
from openai import AsyncOpenAI, APIError, AuthenticationError, RateLimitError

from config import get_settings
from schemas.llm import ChatMessage, ChatResponse, UsageInfo
from services.prompts import build_chat_messages, DEFAULT_SYSTEM_PROMPT

T = TypeVar("T", bound=BaseModel)


def get_llm_client() -> AsyncOpenAI:
    """Initialize and return an AsyncOpenAI client configured from settings."""
    settings = get_settings()
    
    # If base_url is specified (e.g. Groq, Ollama, DeepSeek), pass it
    kwargs = {
        "api_key": settings.LLM_API_KEY,
    }
    if settings.LLM_BASE_URL:
        kwargs["base_url"] = settings.LLM_BASE_URL

    return AsyncOpenAI(**kwargs)


async def generate_chat(
    messages: List[ChatMessage],
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    system_prompt: Optional[str] = None,
) -> ChatResponse:
    """
    Generate a non-streaming chat completion.
    """
    settings = get_settings()
    client = get_llm_client()
    
    chosen_model = model or settings.LLM_DEFAULT_MODEL
    chosen_temp = temperature if temperature is not None else settings.LLM_TEMPERATURE
    chosen_max_tokens = max_tokens or settings.LLM_MAX_TOKENS

    # Convert Pydantic messages to dict format and inject system prompt if provided
    raw_msgs = [m.model_dump() for m in messages]
    formatted_msgs = build_chat_messages(raw_msgs, system_prompt or DEFAULT_SYSTEM_PROMPT)

    response = await client.chat.completions.create(
        model=chosen_model,
        messages=formatted_msgs,
        temperature=chosen_temp,
        max_tokens=chosen_max_tokens,
    )

    choice = response.choices[0]
    usage = response.usage

    return ChatResponse(
        id=response.id,
        model=response.model,
        role=choice.message.role or "assistant",
        content=choice.message.content or "",
        finish_reason=choice.finish_reason,
        usage=UsageInfo(
            prompt_tokens=usage.prompt_tokens if usage else 0,
            completion_tokens=usage.completion_tokens if usage else 0,
            total_tokens=usage.total_tokens if usage else 0,
        ) if usage else None,
    )


async def stream_chat(
    messages: List[ChatMessage],
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    system_prompt: Optional[str] = None,
) -> AsyncGenerator[str, None]:
    """
    Stream chat completion tokens in Server-Sent Events (SSE) format:
    `data: {"content": "token"}\n\n`
    Ends with `data: [DONE]\n\n`.
    """
    settings = get_settings()
    client = get_llm_client()

    chosen_model = model or settings.LLM_DEFAULT_MODEL
    chosen_temp = temperature if temperature is not None else settings.LLM_TEMPERATURE
    chosen_max_tokens = max_tokens or settings.LLM_MAX_TOKENS

    raw_msgs = [m.model_dump() for m in messages]
    formatted_msgs = build_chat_messages(raw_msgs, system_prompt or DEFAULT_SYSTEM_PROMPT)

    stream = await client.chat.completions.create(
        model=chosen_model,
        messages=formatted_msgs,
        temperature=chosen_temp,
        max_tokens=chosen_max_tokens,
        stream=True,
    )

    async for chunk in stream:
        if chunk.choices and len(chunk.choices) > 0:
            delta = chunk.choices[0].delta
            content = delta.content or ""
            if content:
                payload = json.dumps({"content": content, "finish_reason": chunk.choices[0].finish_reason})
                yield f"data: {payload}\n\n"

    yield "data: [DONE]\n\n"


async def extract_structured_data(
    prompt: str,
    response_model: Type[T],
    system_prompt: Optional[str] = None,
    model: Optional[str] = None,
) -> T:
    """
    Extract structured data validated by a Pydantic schema using OpenAI's structured outputs API.
    """
    settings = get_settings()
    client = get_llm_client()
    chosen_model = model or settings.LLM_DEFAULT_MODEL

    sys_prompt = system_prompt or "You extract structured information exactly matching the requested schema."
    messages = [
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": prompt},
    ]

    completion = await client.beta.chat.completions.parse(
        model=chosen_model,
        messages=messages,
        response_format=response_model,
    )

    parsed = completion.choices[0].message.parsed
    if parsed is None:
        raise ValueError("Model failed to return output matching schema.")
    return parsed


async def generate_embeddings_vectors(
    texts: List[str],
    model: Optional[str] = None,
) -> tuple[List[List[float]], int, int]:
    """
    Generate vector embeddings for input strings.
    Returns (embeddings_list, dimensions, total_tokens).
    """
    settings = get_settings()
    client = get_llm_client()
    chosen_model = model or settings.EMBEDDING_MODEL

    response = await client.embeddings.create(
        model=chosen_model,
        input=texts,
    )

    embeddings = [item.embedding for item in response.data]
    dims = len(embeddings[0]) if embeddings else 0
    total_tokens = response.usage.total_tokens if response.usage else 0

    return embeddings, dims, total_tokens
