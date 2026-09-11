<div align="center">

<a href="https://www.abrarahmed.pro" target="_blank">
  <img src="https://www.abrarahmed.pro/assets/devAbby-fulllogo-C9-MX7QK.png" alt="Built by Abrar Ahmed" height="65" />
</a>

# 🤱 MumtaAI — RAG Chatbot Backend

**A production-grade, modular FastAPI backend for the MumtaAI Product Guide & Support Assistant.**  
Built with deterministic intent detection, a multi-provider LLM gateway with automatic failover, and managed via [uv](https://docs.astral.sh/uv/).

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Package Manager](https://img.shields.io/badge/managed%20by-uv-DE5FE9.svg?logo=astral&logoColor=white)](https://docs.astral.sh/uv/)
[![Author](https://img.shields.io/badge/author-Abrar%20Ahmed-black.svg)](https://www.abrarahmed.pro)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

---

## 📖 Overview

**MumtaAI** is an intelligent assistant designed to help parents and caregivers navigate the MumtaAI platform — covering baby profiles, smart oximeter pairing, cry analysis, activity logs, caregiver permissions, subscription tiers, and privacy guidelines.

This backend represents the foundation of the MumtaAI system, featuring:
1. **Offline Intent Detection:** Eliminates unnecessary LLM API calls by safely intercepting common conversational queries (greetings, thanks, goodbyes) with zero token costs and zero latency.
2. **Multi-Provider LLM Gateway:** Automatically fails over between multiple free-tier providers and multiple Gemini keys upon encountering rate limits (`429`), quota exhaustion, or temporary provider outages.
3. **Domain-Driven Architecture:** Organized by features/domains (`api/`, `services/`, `schemas/`, `core/`), keeping route handlers thin and business logic cleanly encapsulated.

---

## ✨ Core Features

- ⚡ **Powered by `uv`**: Ultra-fast environment setup and deterministic dependency resolution.
- 🎯 **Deterministic Intent Detector**:
  - Code-based pattern matching (no external APIs or LLMs).
  - 10+ conversational intents with instant canned responses.
  - **Strict Priority Rule:** MumtaAI product queries *always* take precedence over conversational words (e.g., *"Hi, how do I pair my oximeter?"* routes to the LLM/RAG pipeline, never to a generic greeting).
  - Conservative fallback: ambiguous inputs default to the LLM.
- 🛡️ **LLM Gateway & Automatic Failover**:
  - Supports **Gemini** (up to 4 independent API keys), **Groq**, **OpenAI**, **Mistral**, and **Cerebras**.
  - Intelligent error classification: fails over on `429` (rate limits), quota exhaustion, and `5xx` errors.
  - Temporary cooldowns: avoids repeatedly hammering a provider that recently rate-limited.
  - Real-time status events: transparently informs clients of provider transitions without exposing API keys.
- 🏗️ **Feature-Oriented FastAPI Structure**:
  - `src/api/routes/`: Thin route controllers grouped by domain (`chat.py`, `health.py`).
  - `src/services/`: Pure business logic (`chat_service.py`, `gateway.py`, `intent_detector/`).
  - `src/schemas/`: Typed Pydantic models for contracts and responses.
  - `src/core/`: Strongly-typed configuration via `pydantic-settings`.

---

## 📁 Project Structure

```text
mamtaai-rag/
├── src/                          # Application source code
│   ├── api/                      # HTTP layer (FastAPI routers)
│   │   ├── routes/               # Domain-specific route controllers
│   │   │   ├── chat.py           # POST /api/chat endpoint
│   │   │   └── health.py         # GET /health endpoint
│   │   └── router.py             # Central API router aggregator
│   │
│   ├── core/                     # Core system infrastructure
│   │   └── config.py             # Application settings & environment loader
│   │
│   ├── schemas/                  # Pydantic data contracts
│   │   └── chat.py               # ChatRequest, ChatResponse, UsageInfo, etc.
│   │
│   ├── services/                 # Business logic & AI infrastructure
│   │   ├── chat_service.py       # Chat workflow orchestrator
│   │   ├── gateway.py            # Multi-provider failover LLM Gateway
│   │   └── intent_detector/      # Standalone deterministic intent detector
│   │       ├── detector.py       # Two-stage priority matching engine
│   │       ├── normalizer.py     # Text cleaning & character normalization
│   │       ├── canned_responses.py # Decoupled support canned responses
│   │       └── types.py          # IntentResult and category constants
│   │
│   └── main.py                   # Declarative FastAPI entrypoint
│
├── tests/                        # Offline automated unit test suite
│   ├── test_api.py               # Endpoint & routing integration tests
│   ├── test_gateway.py           # Gateway failover, cooldown, and error tests
│   └── test_intent_detector.py   # Intent classification & priority tests
│
├── docs/                         # Architecture guides & roadmap documentation
├── documents/                    # Knowledge base documents for future RAG phases
├── .env                          # Local environment variables & provider keys
├── pyproject.toml                # UV project configuration & pytest settings
├── requirements.txt              # Standard human-readable dependencies list
└── run.py                        # Single-command runner script
```

---

## ⚡ Quickstart

### 1. Prerequisites
Install [uv](https://docs.astral.sh/uv/) if you haven't already:
```bash
# Windows (PowerShell):
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS/Linux:
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env` (or configure your keys):
```env
PORT=8000
ALLOWED_ORIGINS=*

# Gemini Deployments (Multiple free-tier keys supported)
GOOGLE_API_KEY1=AIzaSy...
GOOGLE_API_KEY2=AIzaSy...
GOOGLE_API_KEY3=AIzaSy...
GOOGLE_API_KEY4=AIzaSy...

# CORS Allowed Origins (Frontend Dev & Production)
ALLOWED_ORIGINS=http://localhost:3000,https://mamtaai.vercel.app

# Other Providers
GROQ_API_KEY=gsk_...
OPENAI_API_KEY=sk-proj-...
MISTRAL_API_KEY=...
CEREBRAS_API_KEY=csk-...
```

---

## 🏃 Running the Server

### Option 1: Using the runner script (Recommended)
```bash
uv run python run.py
```

### Option 2: Using Uvicorn directly
```bash
uv run uvicorn main:app --reload --app-dir src
```

Once running, access the services:
- **API Root**: [http://localhost:8000/](http://localhost:8000/)
- **Interactive Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Alternative ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)
- **Chat Endpoint**: `POST http://localhost:8000/api/chat`

---

## 📡 API Usage & Examples

### 1. Conversational Intent (Zero-Token Canned Bypass)
Messages like greetings, thanks, and goodbyes are intercepted immediately:
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Hi there!"}
    ]
  }'
```
**Response:**
```json
{
  "reply": "Hello! I am your MumtaAI Product Guide & Support Assistant. How can I help you with your account, baby profiles, cry analysis, or oximeter today?",
  "provider": "canned_response",
  "model": "rule_based",
  "intent": "greeting",
  "usage": {
    "prompt_tokens": 0,
    "completion_tokens": 0,
    "total_tokens": 0
  },
  "status_events": []
}
```

### 2. MumtaAI Product Query (Forwarded to LLM Gateway)
Substantive queries are routed through the failover gateway:
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "How do I pair my smart oximeter?"}
    ]
  }'
```
**Response:**
```json
{
  "reply": "To pair your MumtaAI oximeter, turn on Bluetooth...",
  "provider": "Gemini #1",
  "model": "gemini-1.5-flash",
  "intent": "oximeter",
  "usage": {
    "prompt_tokens": 18,
    "completion_tokens": 42,
    "total_tokens": 60
  },
  "status_events": []
}
```

### 3. Failover in Action
If a provider hits a `429` rate limit, the gateway automatically switches to the next available deployment:
```json
{
  "reply": "Here is how cry analysis works...",
  "provider": "Groq",
  "model": "llama-3.3-70b-versatile",
  "intent": "cry_analysis",
  "usage": {
    "prompt_tokens": 22,
    "completion_tokens": 58,
    "total_tokens": 80
  },
  "status_events": [
    {
      "type": "provider_status",
      "status": "fallback",
      "message": "Gemini #1 has reached its current API limit or is unavailable. Switching to another provider...",
      "provider": "Gemini #1"
    },
    {
      "type": "provider_status",
      "status": "switched",
      "message": "Switched to Groq successfully.",
      "provider": "Groq"
    }
  ]
}
```

---

## 🧪 Testing

Run the offline unit test suite with `uv`:
```bash
uv run python -m pytest
```

---

## 👨‍💻 Author & Credits

Built with ❤️ by **[Abrar Ahmed](https://www.abrarahmed.pro)**

<a href="https://www.abrarahmed.pro" target="_blank">
  <img src="https://www.abrarahmed.pro/assets/devAbby-fulllogo-C9-MX7QK.png" alt="devAbby logo" height="50" />
</a>

- **Portfolio**: [abrarahmed.pro](https://www.abrarahmed.pro)
- **GitHub**: [@AbrarAhmed111](https://github.com/AbrarAhmed111)

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
