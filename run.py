"""
MumtaAI Application Entrypoint Runner.
Usage:
    uv run python run.py
"""

import os
import sys
import uvicorn
from dotenv import load_dotenv

# Ensure 'src' is in python path
src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

load_dotenv()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    print(f"\n🚀 Starting MumtaAI API server at http://localhost:{port}")
    print(f"📖 Interactive API Docs available at http://localhost:{port}/docs\n")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        reload_includes=["*.py", ".env", "*.env"],
        app_dir=src_dir,
    )

