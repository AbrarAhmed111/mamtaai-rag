"""
Chatbot API Endpoints.
Thin route handlers delegating to chat_service.
"""

from fastapi import APIRouter, HTTPException, status
from schemas.chat import ChatRequest, ChatResponse, FastPromptsResponse
from services.chat_service import chat_service

router = APIRouter(prefix="/chat", tags=["Chatbot"])


@router.get("/fast-prompts", response_model=FastPromptsResponse, summary="Get Product Fast Prompts")
async def get_fast_prompts() -> FastPromptsResponse:
    """
    Returns curated, product-focused fast prompts / suggestion chips for the chatbot UI.
    Contains strictly platform & product questions (no individual personal account queries).
    """
    return chat_service.get_fast_prompts()


@router.post("", response_model=ChatResponse, summary="Chat Completion with Intent Detection & Gateway")
async def chat_endpoint(request: ChatRequest) -> ChatResponse:
    """
    Main Chat Completion Endpoint:
    - Automatically checks intent (bypasses LLM for conversational greetings/thanks).
    - Routes domain requests through the LLM Gateway with multi-provider failover.
    """
    try:
        return await chat_service.process_chat(request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat Execution Failed: {str(e)}",
        )

