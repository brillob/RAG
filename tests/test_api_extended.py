"""Extended API tests."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from app.main import app

client = TestClient(app)


def test_query_endpoint_success():
    """Test successful query processing."""
    with patch('app.main.rag_service') as mock_rag:
        mock_rag.process_query = AsyncMock(return_value={
            "response": "Test response",
            "language": "en",
            "confidence": 0.9,
            "sources": ["chunk_1"],
            "query_id": "test-query-id",
            "conversation_id": "test-conv-id"
        })
        
        response = client.post(
            "/api/v1/query",
            json={
                "query": "What are the requirements?",
                "language": "auto"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["response"] == "Test response"
        assert data["language"] == "en"
        assert data["confidence"] == 0.9


def test_query_endpoint_with_conversation_id():
    """Test query with conversation_id."""
    with patch('app.main.rag_service') as mock_rag:
        mock_rag.process_query = AsyncMock(return_value={
            "response": "Follow-up response",
            "language": "en",
            "confidence": 0.85,
            "sources": [],
            "query_id": "test-query-id",
            "conversation_id": "existing-conv-id"
        })
        
        response = client.post(
            "/api/v1/query",
            json={
                "query": "Do I need insurance?",
                "conversation_id": "existing-conv-id"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["conversation_id"] == "existing-conv-id"


def test_query_endpoint_api_key_required():
    """Test API key authentication."""
    with patch('app.config.settings') as mock_settings:
        mock_settings.api_key = "test-api-key"
        
        response = client.post(
            "/api/v1/query",
            json={"query": "test"},
            headers={}  # No API key
        )
        
        # Should require API key
        assert response.status_code == 401


def test_query_endpoint_invalid_api_key():
    """Test with invalid API key."""
    with patch('app.config.settings') as mock_settings:
        mock_settings.api_key = "correct-key"
        
        response = client.post(
            "/api/v1/query",
            json={"query": "test"},
            headers={"X-API-Key": "wrong-key"}
        )
        
        assert response.status_code == 401


def test_query_endpoint_valid_api_key():
    """Test with valid API key."""
    with patch('app.config.settings') as mock_settings, \
         patch('app.main.rag_service') as mock_rag:
        mock_settings.api_key = "test-key"
        mock_rag.process_query = AsyncMock(return_value={
            "response": "Response",
            "language": "en",
            "confidence": 0.9,
            "sources": [],
            "query_id": "id",
            "conversation_id": "conv-id"
        })
        
        response = client.post(
            "/api/v1/query",
            json={"query": "test"},
            headers={"X-API-Key": "test-key"}
        )
        
        assert response.status_code == 200


def test_query_endpoint_no_api_key_when_not_configured():
    """Test that API works without key when not configured."""
    with patch('app.config.settings') as mock_settings, \
         patch('app.main.rag_service') as mock_rag:
        mock_settings.api_key = None
        mock_rag.process_query = AsyncMock(return_value={
            "response": "Response",
            "language": "en",
            "confidence": 0.9,
            "sources": [],
            "query_id": "id",
            "conversation_id": "conv-id"
        })
        
        response = client.post(
            "/api/v1/query",
            json={"query": "test"}
        )
        
        assert response.status_code == 200


def test_query_endpoint_validation_error():
    """Test request validation."""
    response = client.post(
        "/api/v1/query",
        json={}  # Missing required 'query' field
    )
    
    assert response.status_code == 422  # Validation error


def test_query_endpoint_empty_query():
    """Test with empty query string."""
    response = client.post(
        "/api/v1/query",
        json={"query": ""}  # Empty string
    )
    
    assert response.status_code == 422  # Validation error


def test_query_endpoint_server_error():
    """Test handling of server errors."""
    with patch('app.main.rag_service') as mock_rag:
        mock_rag.process_query = AsyncMock(side_effect=Exception("Server error"))
        
        response = client.post(
            "/api/v1/query",
            json={"query": "test"}
        )
        
        assert response.status_code == 500
        assert "error" in response.json()["detail"].lower()


def test_root_endpoint():
    """Test root endpoint."""
    response = client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    assert "service" in data
    assert "version" in data
    assert "endpoints" in data
