# Smart Doc API

![CI](https://github.com/flaviodell/smart-doc-api/actions/workflows/ci.yml/badge.svg) 

[![Live Demo](https://img.shields.io/badge/live-demo-brightgreen)](https://smart-doc-api.onrender.com/docs)

A production-ready REST API that exposes AI capabilities (summarization, Q&A, text classification) built with FastAPI, PostgreSQL, Redis, and Docker. Designed to demonstrate end-to-end AI engineering skills: from model integration to containerized deployment with CI/CD.

---

## What it demonstrates

- **FastAPI** backend with async endpoints and auto-generated Swagger UI
- **RAG-style AI pipeline**: Groq LLM (Llama 3.1 8B) for summarization, Q&A and zero-shot classification
- **PostgreSQL** persistence for interaction history and performance metrics
- **Redis** caching layer — repeated requests are served in <10ms without calling the LLM
- **Structured logging** with loguru — timestamped, leveled, written to stdout and rotating file
- **Docker Compose** orchestration of 3 services (app, PostgreSQL, Redis)
- **GitHub Actions & Render** CI/CD pipeline — runs automated tests on every push and deploys the Dockerized app to a public URL

---

## Architecture
```
Client
  │
  ▼
Render (cloud deployment)
  │
  ▼
FastAPI (port 8000)
  │
  ├── Redis cache ──► cache hit → return immediately
  │
  ├── AIService
  │     └── Groq API (summarize, qa, classify) — Llama 3.1 8B
  │
  └── PostgreSQL
        ├── ai_interactions — full request/response history
        └── ai_metrics — latency, cache hit rate, model usage
```
 
**CI/CD flow:**
```
push to main
  │
  ▼
GitHub Actions — pytest (7 tests)
  │
  ├── tests fail → stop, no deploy
  │
  └── tests pass
        │
        ▼
      Render auto-deploy → live at https://smart-doc-api.onrender.com
```
 
---

## Tech stack

| Component | Technology |
|---|---|
| Backend | FastAPI + uvicorn |
| AI — LLM | Llama 3.1 8B via Groq API |
| AI — Classification | Zero-shot classification via Groq API (Llama 3.1 8B) |
| Database | PostgreSQL 15 + SQLAlchemy |
| Cache | Redis 7 |
| Logging | loguru |
| Testing | pytest + unittest.mock |
| Containerization | Docker / Docker Compose |
| CI/CD | GitHub Actions + Render (PaaS) |

---

## Setup & Installation

### Prerequisites
- Python 3.11+
- A [Groq API key](https://console.groq.com) (free tier available)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (optional, for containerized setup)

### Option 1 — Local setup
```bash
# 1. Clone the repository
git clone https://github.com/flaviodell/smart-doc-api.git
cd smart-doc-api

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env
# Edit .env and add your Groq API key

# 5. Start PostgreSQL and Redis via Docker
docker compose up db redis -d

# 6. Run the application
uvicorn app.main:app --reload
```

Open your browser at `http://localhost:8000/docs`.

### Option 2 — Docker
```bash
# 1. Clone the repository
git clone https://github.com/flaviodell/smart-doc-api.git
cd smart-doc-api

# 2. Configure environment variables
cp .env.example .env
# Edit .env and add your Groq API key

# 3. Build and start all services
docker compose up --build
```

Open your browser at `http://localhost:8000/docs`.

To stop:
```bash
docker compose down
```

---

## API endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Health check |
| GET | `/health` | Service status |
| POST | `/ai/process` | Run AI task (summarize, qa, classify) |
| GET | `/ai/history` | Recent interaction history from PostgreSQL |
| GET | `/ai/metrics` | Aggregate performance metrics (latency, cache hit rate) |

### Example request
```bash
# Live demo
curl -X POST https://smart-doc-api.onrender.com/ai/process \
  -H "Content-Type: application/json" \
  -d '{
    "text": "The French Revolution was a period of radical political and social transformation in France between 1789 and 1799, culminating in the rise of Napoleon Bonaparte.",
    "task": "summarize"
  }'
 
# Local
curl -X POST http://localhost:8000/ai/process \
  -H "Content-Type: application/json" \
  -d '{
    "text": "The French Revolution was a period of radical political and social transformation in France between 1789 and 1799, culminating in the rise of Napoleon Bonaparte.",
    "task": "summarize"
  }'
```

### Example response
```json
{
  "id": 1,
  "task": "summarize",
  "response": "The French Revolution transformed France politically and socially from 1789 to 1799, ending with Napoleon's rise to power.",
  "status": "success (new)"
}
```

---

## Running tests
```bash
pytest -v
```

7 unit and integration tests covering: root endpoint, invalid task handling, mocked summarize and Q&A endpoints, cache hit logic, and history endpoint.

To run integration tests (requires real API keys and running services):
```bash
pytest -v -m integration
```

---

## Project structure
```
smart-doc-api/
├── app/
│   ├── api/
│   │   └── endpoints.py       # FastAPI routes
│   ├── core/
│   │   ├── config.py          # Settings via pydantic-settings
│   │   ├── database.py        # SQLAlchemy engine and session
│   │   └── logging.py         # loguru configuration
│   ├── models/
│   │   └── interaction.py     # SQLAlchemy models (AIInteraction, AIMetric)
│   ├── schemas/
│   │   └── request.py         # Pydantic request schemas
│   ├── services/
│   │   └── ai_service.py      # AI logic (Groq)
│   └── main.py                # FastAPI app entry point
├── tests/
│   └── test_main.py           # pytest test suite
├── .github/workflows/
│   └── ci.yml                 # GitHub Actions CI/CD pipeline
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

---

## License

MIT