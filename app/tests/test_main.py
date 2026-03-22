"""Tests for the Insight-Agent API."""

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_analyze_text_basic():
    """Test basic text analysis."""
    response = client.post("/analyze", json={"text": "I love cloud engineering!"})
    assert response.status_code == 200
    data = response.json()
    assert data["original_text"] == "I love cloud engineering!"
    assert data["word_count"] == 4
    assert data["character_count"] == 25


def test_analyze_text_single_word():
    """Test analysis with a single word."""
    response = client.post("/analyze", json={"text": "Hello"})
    assert response.status_code == 200
    data = response.json()
    assert data["word_count"] == 1
    assert data["character_count"] == 5


def test_analyze_text_multiple_spaces():
    """Test analysis with multiple spaces between words."""
    response = client.post("/analyze", json={"text": "Hello   World"})
    assert response.status_code == 200
    data = response.json()
    assert data["word_count"] == 2
    assert data["character_count"] == 13


def test_analyze_text_empty_string():
    """Test that empty string is rejected."""
    response = client.post("/analyze", json={"text": ""})
    assert response.status_code == 422  # Validation error


def test_analyze_text_missing_field():
    """Test that missing text field returns error."""
    response = client.post("/analyze", json={})
    assert response.status_code == 422


def test_analyze_text_with_newlines():
    """Test analysis with newlines."""
    response = client.post("/analyze", json={"text": "Hello\nWorld"})
    assert response.status_code == 200
    data = response.json()
    assert data["word_count"] == 2
    assert data["character_count"] == 11


def test_analyze_text_unicode():
    """Test analysis with unicode characters."""
    response = client.post("/analyze", json={"text": "Hello 世界"})
    assert response.status_code == 200
    data = response.json()
    assert data["word_count"] == 2
    assert data["character_count"] == 8
