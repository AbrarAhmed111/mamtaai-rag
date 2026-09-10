"""
Embeddings Router
Generates dense vector embeddings for semantic search, retrieval, and RAG pipelines.
"""

from fastapi import APIRouter, HTTPException, status
from openai import AuthenticationError, RateLimitError, APIError

from schemas.llm import EmbeddingRequest, EmbeddingResponse
from services.llm import generate_embeddings_vectors

router = APIRouter(prefix="/embeddings", tags=["Embeddings"])


@router.post("", response_model=EmbeddingResponse, summary="Generate Vector Embeddings")
async def create_embeddings(request: EmbeddingRequest):
    """
    Generate vector embeddings for one or more strings of text.
    """
    try:
        texts = [request.input] if isinstance(request.input, str) else request.input
        embeddings, dimensions, total_tokens = await generate_embeddings_vectors(
            texts=texts,
            model=request.model,
        )

        from config import get_settings
        settings = get_settings()
        used_model = request.model or settings.EMBEDDING_MODEL

        return EmbeddingResponse(
            model=used_model,
            embeddings=embeddings,
            dimensions=dimensions,
            total_tokens=total_tokens,
        )
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"LLM Provider Authentication Failed: Ensure your LLM_API_KEY is set. ({str(e)})"
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
            detail=f"Failed to generate embeddings: {str(e)}"
        )
