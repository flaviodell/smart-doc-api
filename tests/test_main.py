import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.ai_service import AIService

client = TestClient(app)

def test_read_root():
    """Verify that the root endpoint is reachable."""
    response = client.get("/")
    assert response.status_code == 200
    assert "running" in response.json()["message"].lower()

# --- Unit Tests ---

def test_ai_service_summarize():
    """Test the summarization logic directly."""
    text = "Questo è un testo di prova che deve essere riassunto."
    result = AIService.process_task(task="summarize", text=text)
    assert result is not None
    assert len(result) > 0

def test_ai_service_invalid_task():
    """Verify handling of unsupported tasks."""
    result = AIService.process_task(task="invalid", text="test")
    assert "non supportato" in result.lower()

# --- Integration Tests ---

def test_api_qa_flow():
    """Test the full Question & Answer API flow."""
    payload = {
        "text": "Il sole è una stella.",
        "task": "qa",
        "question": "Cos'è il sole?"
    }
    response = client.post("/ai/process", json=payload)
    assert response.status_code == 200
    assert "stella" in response.json()["response"].lower()

@pytest.mark.parametrize("text,expected_label", [
    ("L'inflazione aumenta i prezzi.", "economia"),
    ("Il mercato azionario è in calo oggi.", "economia"),
    ("Le banche hanno alzato i tassi.", "economia"),
])
def test_api_classification_multiple_examples(text, expected_label):
    """
    Test the classification flow with multiple examples to ensure 
    robustness across different phrasings of the same category.
    """
    payload = {
        "text": text,
        "task": "classify"
    }
    response = client.post("/ai/process", json=payload)
    assert response.status_code == 200
    assert expected_label in response.json()["response"].lower()

def test_cache_logic():
    """Check if Redis cache returns the 'from_cache' ID on repeated requests."""
    payload = {"text": "Cache consistency test", "task": "summarize"}
    
    # First call: Populate cache
    client.post("/ai/process", json=payload)
    
    # Second call: Retrieve from cache
    response = client.post("/ai/process", json=payload)
    assert response.json()["id"] == "from_cache"
    