"""
Health check endpoints.
"""

from fastapi import APIRouter
from services import gateway
from core.config import get_settings

settings = get_settings()
router = APIRouter(tags=["Health"])


@router.get("/health", summary="Health Check")
async def health_check():
    """Returns application status and available LLM deployment counts."""
    available_count = len(gateway.get_available_deployments())
    total_count = len(gateway.deployments)
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.API_VERSION,
        "configured_deployments": total_count,
        "available_deployments": available_count,
    }
