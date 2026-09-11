"""
Central API Router Aggregator.
Registers all domain/feature routers and exports a unified api_router.
"""

from fastapi import APIRouter
from api.routes.health import router as health_router
from api.routes.chat import router as chat_router

api_router = APIRouter()

# Health check endpoint: GET /health
api_router.include_router(health_router)

# Feature & Domain routes with /api prefix: POST /api/chat
api_router.include_router(chat_router, prefix="/api")

__all__ = ["api_router"]
