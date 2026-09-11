"""
MumtaAI Application Entrypoint Runner.
Usage:
    uv run python run.py
"""

import os
import uvicorn
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    print(f"\n🚀 Starting MumtaAI API server at http://localhost:{port}")
    print(f"📖 Interactive API Docs available at http://localhost:{port}/docs\n")
    uvicorn.run("src.main:app", host="0.0.0.0", port=port, reload=True)
