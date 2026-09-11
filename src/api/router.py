"""
Central API Router Aggregator.
Registers all domain/feature routers and exports a unified api_router.
"""

from fastapi import APIRouter
from api.routes.health import router as health_router
from api.routes.chat import router as chat_router

api_router = APIRouter()

# Include Domain Routers
api_router.include_router(health_router)
api_router.include_router(chat_router)

# Also expose under /api prefix for standard REST convention: /api/chat, /api/health
api_router.include_router(chat_router, prefix="/api")
api_router.include_router(health_router, prefix="/api")

__all__ = ["api_router"]
