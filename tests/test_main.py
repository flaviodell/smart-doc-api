import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app
from app.services.ai_service import AIService

client = TestClient(app)


# ---------------------------------------------------------------------------
# Root
# ---------------------------------------------------------------------------

def test_read_root():
    """Verify that the root endpoint is reachable."""
    response = client.get("/")
    assert response.status_code == 200
    assert "running" in response.json()["message"].lower()


# ---------------------------------------------------------------------------
# Unit tests — no external calls, AIService mocked
# ---------------------------------------------------------------------------

def test_ai_service_invalid_task():
    """Verify handling of unsupported tasks (no external call needed)."""
    response_text, model = AIService.process_task(task="invalid", text="test")
    assert "non supportato" in response_text.lower()
    assert model == "none"


def test_ai_service_qa_missing_question():
    """Verify that qa task without question returns a descriptive error."""
    response_text, model = AIService.process_task(task="qa", text="some context")
    assert "question" in response_text.lower()


@patch("app.api.endpoints.cache")
@patch("app.api.endpoints.AIService.process_task")
def test_process_endpoint_summarize(mock_process, mock_cache):
    """
    Test the /process endpoint for summarize without calling Groq.
    AIService and Redis are mocked so the test is fast and offline-safe.
    """
    mock_cache.get.return_value = None
    mock_process.return_value = ("This is a summary.", "llama-3.1-8b-instant")

    payload = {"text": "Un testo lungo da riassumere.", "task": "summarize"}
    response = client.post("/ai/process", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["task"] == "summarize"
    assert data["status"] == "success (new)"
    assert "summary" in data["response"].lower()


@patch("app.api.endpoints.cache")
def test_cache_hit_returns_cached_id(mock_cache):
    """
    When Redis returns a cached value the endpoint must return id='from_cache'
    without calling AIService at all.
    """
    mock_cache.get.return_value = "cached answer"

    payload = {"text": "Cache consistency test", "task": "summarize"}
    response = client.post("/ai/process", json=payload)

    assert response.status_code == 200
    assert response.json()["id"] == "from_cache"
    assert response.json()["status"] == "success (cached)"


@patch("app.api.endpoints.cache")
@patch("app.api.endpoints.AIService.process_task")
def test_process_endpoint_qa(mock_process, mock_cache):
    """Test the /process endpoint for qa task with mocked service."""
    mock_cache.get.return_value = None
    mock_process.return_value = ("Il sole è una stella.", "llama-3.1-8b-instant")

    payload = {"text": "Il sole è una stella.", "task": "qa", "question": "Cos'è il sole?"}
    response = client.post("/ai/process", json=payload)

    assert response.status_code == 200
    assert response.json()["task"] == "qa"


def test_history_endpoint():
    """Verify that the history endpoint returns a list."""
    response = client.get("/ai/history")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


# ---------------------------------------------------------------------------
# Integration tests — marked explicitly, require real API keys and services
# ---------------------------------------------------------------------------

@pytest.mark.integration
def test_ai_service_summarize_real():
    """INTEGRATION: calls Groq API for real. Requires GROQ_API_KEY."""
    text = "Questo è un testo di prova che deve essere riassunto."
    result, model = AIService.process_task(task="summarize", text=text)
    assert result is not None
    assert len(result) > 0
    assert model == "llama-3.1-8b-instant"


@pytest.mark.integration
def test_api_classification_real():
    """INTEGRATION: calls HuggingFace model for real. Requires internet."""
    payload = {"text": "L'inflazione aumenta i prezzi.", "task": "classify"}
    response = client.post("/ai/process", json=payload)
    assert response.status_code == 200
    assert "economia" in response.json()["response"].lower()