"""
API Routes Package.
"""
from api.routes.health import router as health_router
from api.routes.chat import router as chat_router

__all__ = ["health_router", "chat_router"]
