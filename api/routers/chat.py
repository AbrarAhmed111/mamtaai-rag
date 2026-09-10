"""
Chat Router
Handles standard chat completions and real-time Server-Sent Events (SSE) streaming.
"""

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from openai import AuthenticationError, RateLimitError, APIError

from schemas.llm import ChatMessage, ChatRequest, ChatResponse, QuickPromptRequest
from services.llm import generate_chat, stream_chat

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("", response_model=ChatResponse, summary="Standard Chat Completion")
async def chat_completion(request: ChatRequest):
    """
    Generate a complete LLM chat completion from a conversation history.
    """
    try:
        response = await generate_chat(
            messages=request.messages,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            system_prompt=request.system_prompt,
        )
        return response
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"LLM Provider Authentication Failed: Ensure your LLM_API_KEY is configured correctly. ({str(e)})"
        )
    except RateLimitError as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"LLM Provider Rate Limit: {str(e)}"
        )
    except APIError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"LLM Provider Error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate completion: {str(e)}"
        )


@router.post("/stream", summary="Streaming Chat Completion (SSE)")
async def chat_stream(request: ChatRequest):
    """
    Stream tokens in real-time as Server-Sent Events (SSE).
    Content-Type: `text/event-stream`.
    Each event has the format: `data: {"content": "token"}\n\n` followed by `data: [DONE]\n\n`.
    """
    try:
        generator = stream_chat(
            messages=request.messages,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            system_prompt=request.system_prompt,
        )
        return StreamingResponse(
            generator,
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initiate stream: {str(e)}"
        )


@router.post("/prompt", response_model=ChatResponse, summary="Quick Single-Turn Prompt")
async def quick_prompt(request: QuickPromptRequest):
    """
    Convenience endpoint for simple one-shot prompts without building a full message history.
    """
    messages = [ChatMessage(role="user", content=request.prompt)]
    return await chat_completion(
        ChatRequest(
            messages=messages,
            model=request.model,
            temperature=request.temperature,
            system_prompt=request.system_prompt,
        )
    )
