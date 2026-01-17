"""Unit tests for RAG service."""
import pytest
from unittest.mock import Mock, MagicMock, patch, AsyncMock
from app.services.rag_service import RAGService
from app.services.pdf_processor import ChunkingStrategy


@pytest.fixture
def rag_service_local(mock_vector_store, mock_conversation_memory, mock_language_detector, mock_openai_service):
    """Create RAG service in local mode with mocked dependencies."""
    with patch('app.services.rag_service.VectorStore', return_value=mock_vector_store), \
         patch('app.services.rag_service.EmbeddingService'), \
         patch('app.services.rag_service.MockOpenAIService', return_value=mock_openai_service), \
         patch('app.services.rag_service.LanguageDetector', return_value=mock_language_detector), \
         patch('app.services.rag_service.get_conversation_memory', return_value=mock_conversation_memory), \
         patch('app.config.settings') as mock_settings:
        mock_settings.is_local_mode.return_value = True
        mock_settings.enable_conversation_memory = True
        mock_settings.max_conversation_history = 10
        mock_settings.max_response_length = 1000
        mock_settings.min_confidence_score = 0.7
        
        service = RAGService()
        service.vector_store = mock_vector_store
        service.mock_openai = mock_openai_service
        service.language_detector = mock_language_detector
        service.conversation_memory = mock_conversation_memory
        return service


@pytest.mark.asyncio
async def test_process_query_new_conversation(rag_service_local):
    """Test processing a new query without conversation_id."""
    result = await rag_service_local.process_query(
        query="What are the enrolment requirements?",
        language="auto",
        student_id="student123"
    )
    
    assert result["response"] is not None
    assert result["language"] == "en"
    assert result["confidence"] > 0
    assert result["conversation_id"] is not None
    assert "sources" in result
    rag_service_local.conversation_memory.create_conversation.assert_called_once()


@pytest.mark.asyncio
async def test_process_query_with_conversation_id(rag_service_local):
    """Test processing a query with existing conversation_id."""
    conversation_id = "existing-conv-id"
    result = await rag_service_local.process_query(
        query="Do I need insurance?",
        conversation_id=conversation_id
    )
    
    assert result["conversation_id"] == conversation_id
    rag_service_local.conversation_memory.get_context_string.assert_called_once()
    rag_service_local.conversation_memory.add_message.assert_called()


@pytest.mark.asyncio
async def test_process_query_language_detection(rag_service_local):
    """Test automatic language detection."""
    rag_service_local.language_detector.detect_language.return_value = "es"
    
    result = await rag_service_local.process_query(
        query="¿Cuáles son los requisitos?",
        language="auto"
    )
    
    assert result["language"] == "es"
    rag_service_local.language_detector.detect_language.assert_called_once()


@pytest.mark.asyncio
async def test_process_query_no_search_results(rag_service_local):
    """Test handling when no search results are found."""
    rag_service_local.vector_store.search.return_value = []
    
    result = await rag_service_local.process_query(
        query="Random question with no results"
    )
    
    assert "don't have enough information" in result["response"].lower()
    assert result["confidence"] == 0.0
    assert result["sources"] == []


@pytest.mark.asyncio
async def test_process_query_with_conversation_context(rag_service_local):
    """Test that conversation context is included in response generation."""
    conversation_id = "test-conv-id"
    rag_service_local.conversation_memory.get_context_string.return_value = "Previous: Student asked about visas"
    
    result = await rag_service_local.process_query(
        query="What about insurance?",
        conversation_id=conversation_id
    )
    
    # Verify conversation context was retrieved
    rag_service_local.conversation_memory.get_context_string.assert_called_once()
    # Verify response was stored
    assert rag_service_local.conversation_memory.add_message.call_count >= 2


def test_build_context(rag_service_local, sample_search_results):
    """Test context building from search results."""
    context = rag_service_local._build_context(sample_search_results)
    
    assert "Enrolment Requirements" in context
    assert "Visa Information" in context
    assert "ICL Student Handbook" in context
    assert len(context) > 0


def test_calculate_confidence(rag_service_local, sample_search_results):
    """Test confidence score calculation."""
    confidence = rag_service_local._calculate_confidence(sample_search_results)
    
    assert 0.0 <= confidence <= 1.0
    assert confidence > 0  # Should have some confidence with results


def test_calculate_confidence_no_results(rag_service_local):
    """Test confidence calculation with no results."""
    confidence = rag_service_local._calculate_confidence([])
    assert confidence == 0.0


def test_calculate_confidence_multiple_results(rag_service_local):
    """Test confidence boost with multiple results."""
    results = [
        {'score': 0.8},
        {'score': 0.7},
        {'score': 0.6},
        {'score': 0.5}
    ]
    confidence = rag_service_local._calculate_confidence(results)
    assert confidence > 0


def test_apply_guardrails_valid_response(rag_service_local):
    """Test guardrails with valid response."""
    response = "This is a valid response with enough information."
    context = "Some context information here."
    
    result = rag_service_local._apply_guardrails(response, context, "test query")
    assert result == response


def test_apply_guardrails_too_long(rag_service_local):
    """Test guardrails truncating long responses."""
    long_response = "A" * 2000
    context = "Context"
    
    with patch('app.config.settings.max_response_length', 100):
        result = rag_service_local._apply_guardrails(long_response, context, "test")
        assert len(result) <= 103  # 100 + "..."


def test_apply_guardrails_too_short(rag_service_local):
    """Test guardrails handling very short responses."""
    short_response = "OK"
    context = "Some context"
    
    result = rag_service_local._apply_guardrails(short_response, context, "test")
    assert len(result) > len(short_response)
    assert "don't have enough information" in result.lower()


@pytest.mark.asyncio
async def test_generate_response_local(rag_service_local):
    """Test local response generation."""
    query = "What are the requirements?"
    context = "Context about enrolment requirements."
    conversation_context = "Previous conversation"
    
    response = await rag_service_local._generate_response_local(
        query, context, "en", conversation_context
    )
    
    assert response is not None
    assert len(response) > 0
    rag_service_local.mock_openai.generate_response.assert_called_once()


@pytest.mark.asyncio
async def test_generate_response_local_without_conversation(rag_service_local):
    """Test local response generation without conversation context."""
    query = "What are the requirements?"
    context = "Context about enrolment requirements."
    
    response = await rag_service_local._generate_response_local(
        query, context, "en", ""
    )
    
    assert response is not None


@pytest.mark.asyncio
async def test_process_query_error_handling(rag_service_local):
    """Test error handling in process_query."""
    rag_service_local.vector_store.search.side_effect = Exception("Search error")
    
    result = await rag_service_local.process_query("test query")
    
    assert "error" in result["response"].lower() or "apologize" in result["response"].lower()
    assert result["confidence"] == 0.0


def test_rag_service_initialization_local_mode():
    """Test RAG service initialization in local mode."""
    with patch('app.config.settings') as mock_settings, \
         patch('app.services.rag_service.VectorStore'), \
         patch('app.services.rag_service.EmbeddingService'), \
         patch('app.services.rag_service.MockOpenAIService'), \
         patch('app.services.rag_service.LanguageDetector'), \
         patch('app.services.rag_service.get_conversation_memory'):
        mock_settings.is_local_mode.return_value = True
        mock_settings.enable_conversation_memory = True
        
        service = RAGService()
        assert service.is_local is True
        assert service.vector_store is not None
        assert service.mock_openai is not None
