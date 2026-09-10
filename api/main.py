"""
LLM FastAPI Application
Entrypoint for the FastAPI application, middleware configuration, and router mounting.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from api.routers import chat_router, structured_router, embeddings_router

settings = get_settings()

tags_metadata = [
    {
        "name": "General",
        "description": "Health checks, root metadata, and connectivity tests.",
    },
    {
        "name": "Chat",
        "description": "Standard JSON chat completions and real-time SSE token streaming.",
    },
    {
        "name": "Structured Extraction",
        "description": "Typed Pydantic-validated JSON extraction from unstructured text.",
    },
    {
        "name": "Embeddings",
        "description": "Dense vector embeddings generation for search and RAG.",
    },
]

app = FastAPI(
    title=settings.APP_NAME,
    description="""
A clean, production-ready FastAPI template for LLM-powered applications.

### Supported Features:
- 💬 **Standard Chat**: Multi-turn conversation completion.
- ⚡ **Token Streaming**: Real-time Server-Sent Events (SSE) streaming.
- 📋 **Structured Outputs**: Pydantic schema validation using OpenAI-compatible JSON mode / function calling.
- 🔍 **Vector Embeddings**: Generate text embeddings for semantic search & RAG.
- 🔄 **Multi-Provider**: Drop-in compatible with OpenAI, Groq, DeepSeek, Ollama, OpenRouter, and more.
    """,
    version=settings.API_VERSION,
    openapi_tags=tags_metadata,
)

# CORS Middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["General"], summary="Root Information & Endpoints")
async def root():
    """Returns basic service status, configuration metadata, and interactive doc links."""
    return {
        "service": settings.APP_NAME,
        "version": settings.API_VERSION,
        "environment": settings.ENVIRONMENT,
        "docs": f"{settings.BASE_URL}/docs",
        "redoc": f"{settings.BASE_URL}/redoc",
        "health": f"{settings.BASE_URL}/health",
        "configured_llm": {
            "default_model": settings.LLM_DEFAULT_MODEL,
            "base_url": settings.LLM_BASE_URL or "https://api.openai.com/v1 (default)",
            "embedding_model": settings.EMBEDDING_MODEL,
        },
        "endpoints": {
            "chat": f"{settings.BASE_URL}/api/chat",
            "chat_stream": f"{settings.BASE_URL}/api/chat/stream",
            "quick_prompt": f"{settings.BASE_URL}/api/chat/prompt",
            "structured_entities": f"{settings.BASE_URL}/api/structured/entities",
            "embeddings": f"{settings.BASE_URL}/api/embeddings",
        },
    }


@app.get("/health", tags=["General"], summary="Health Check")
async def health_check():
    """Simple health check endpoint for monitoring, load balancers, and uptime checks."""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.API_VERSION,
        "environment": settings.ENVIRONMENT,
    }


@app.get("/api/ping", tags=["General"], summary="Ping")
async def ping():
    """Quick connectivity test endpoint."""
    return {"pong": True}


# Mount LLM routers under /api
app.include_router(chat_router, prefix="/api")
app.include_router(structured_router, prefix="/api")
app.include_router(embeddings_router, prefix="/api")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=True,
        log_level="info",
    )
