"""
FastAPI Application Entrypoint
Configures the app, sets up CORS middleware, and mounts domain routers.
All business logic is delegated to services and domain route handlers.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import get_settings
from api.router import api_router

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    description="MumtaAI Product Guide & Support Chatbot API with Intent Detection & Multi-Provider LLM Gateway.",
    version=settings.API_VERSION,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


@app.get("/", tags=["General"], summary="Root Service Information")
async def root():
    """Returns basic service metadata and documentation links."""
    return {
        "service": settings.APP_NAME,
        "version": settings.API_VERSION,
        "environment": settings.ENVIRONMENT,
        "endpoints": {
            "chat": "/api/chat",
            "health": "/health",
            "docs": "/docs",
        },
    }


# Mount all feature and domain routers centrally
app.include_router(api_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=True,
    )
