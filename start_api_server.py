#!/usr/bin/env python3
"""
Start the LLM FastAPI Backend server from project root.
Usage:
    uv run python start_api_server.py
    # or
    uv run uvicorn api.main:app --reload
"""
import sys
import os

# Ensure the project root is in the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

if __name__ == "__main__":
    import uvicorn
    from config import get_settings

    settings = get_settings()

    print(f"""
╔════════════════════════════════════════════════════════════════╗
║                LLM FastAPI Backend Template                    ║
║                   Powered by UV & FastAPI                      ║
╚════════════════════════════════════════════════════════════════╝

🚀 Starting LLM API server...

Access Points:
  🌐 Service Info          → http://localhost:{settings.PORT}/
  📚 Interactive Docs      → http://localhost:{settings.PORT}/docs
  📖 Alternative ReDoc     → http://localhost:{settings.PORT}/redoc
  💚 Health Check          → http://localhost:{settings.PORT}/health

LLM Configuration:
  🤖 Default Model         → {settings.LLM_DEFAULT_MODEL}
  🔗 Base URL              → {settings.LLM_BASE_URL or 'https://api.openai.com/v1 (default)'}

Commands:
  Run with UV:            uv run uvicorn api.main:app --reload
  Run Tests:              uv run pytest

Press CTRL+C to stop the server
════════════════════════════════════════════════════════════════
    """)

    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=True,
        log_level="info",
    )
