"""
Structured Output Router
Demonstrates how to extract typed, validated Pydantic models from unstructured text using LLMs.
"""

from fastapi import APIRouter, HTTPException, status
from openai import AuthenticationError, RateLimitError, APIError

from schemas.llm import StructuredExtractionRequest, StructuredEntitiesResponse
from services.llm import extract_structured_data
from services.prompts import STRUCTURED_EXTRACTION_SYSTEM_PROMPT

router = APIRouter(prefix="/structured", tags=["Structured Extraction"])


@router.post("/entities", response_model=StructuredEntitiesResponse, summary="Extract Structured Entities & Summary")
async def extract_entities(request: StructuredExtractionRequest):
    """
    Parse unstructured text and return guaranteed schema-compliant JSON containing:
    - Summary
    - Overall sentiment
    - Named entities with categories and descriptions
    - Key takeaways
    """
    try:
        prompt = request.text
        if request.instructions:
            prompt = f"Instructions: {request.instructions}\n\nText to analyze:\n{request.text}"

        result = await extract_structured_data(
            prompt=prompt,
            response_model=StructuredEntitiesResponse,
            system_prompt=STRUCTURED_EXTRACTION_SYSTEM_PROMPT,
            model=request.model,
        )
        return result
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
            detail=f"Extraction failed: {str(e)}"
        )
