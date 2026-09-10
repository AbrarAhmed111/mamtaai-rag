"""
Routers Package
Exports chat, structured extraction, and embeddings routers.
"""

from api.routers.chat import router as chat_router
from api.routers.structured import router as structured_router
from api.routers.embeddings import router as embeddings_router

__all__ = [
    "chat_router",
    "structured_router",
    "embeddings_router",
]
