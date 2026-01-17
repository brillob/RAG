"""Unit tests for embeddings service."""
import pytest
import numpy as np
from unittest.mock import patch, MagicMock
from app.services.embeddings import EmbeddingService


@pytest.fixture
def mock_sentence_transformer():
    """Mock SentenceTransformer."""
    mock_model = MagicMock()
    mock_model.encode.return_value = np.array([
        [0.1, 0.2, 0.3] * 128,  # 384 dim
        [0.2, 0.3, 0.4] * 128
    ])
    return mock_model


def test_embedding_service_initialization(mock_sentence_transformer):
    """Test embedding service initialization."""
    with patch('app.services.embeddings.SentenceTransformer', return_value=mock_sentence_transformer):
        with patch('app.config.settings') as mock_settings:
            mock_settings.embedding_model = "all-MiniLM-L6-v2"
            
            service = EmbeddingService()
            
            assert service.model is not None
            assert service.model_name == "all-MiniLM-L6-v2"


def test_embedding_service_initialization_with_model_name(mock_sentence_transformer):
    """Test embedding service with custom model name."""
    with patch('app.services.embeddings.SentenceTransformer', return_value=mock_sentence_transformer):
        service = EmbeddingService(model_name="paraphrase-multilingual-MiniLM-L12-v2")
        
        assert service.model_name == "paraphrase-multilingual-MiniLM-L12-v2"


def test_encode(mock_sentence_transformer):
    """Test encoding text list."""
    with patch('app.services.embeddings.SentenceTransformer', return_value=mock_sentence_transformer):
        service = EmbeddingService()
        
        texts = ["Text 1", "Text 2"]
        embeddings = service.encode(texts)
        
        assert embeddings.shape[0] == 2
        assert embeddings.shape[1] == 384
        mock_sentence_transformer.encode.assert_called_once()


def test_encode_empty_list(mock_sentence_transformer):
    """Test encoding empty list."""
    with patch('app.services.embeddings.SentenceTransformer', return_value=mock_sentence_transformer):
        service = EmbeddingService()
        
        embeddings = service.encode([])
        
        assert embeddings.shape[0] == 0


def test_encode_query(mock_sentence_transformer):
    """Test encoding single query."""
    with patch('app.services.embeddings.SentenceTransformer', return_value=mock_sentence_transformer):
        service = EmbeddingService()
        
        embedding = service.encode_query("What are the requirements?")
        
        assert embedding.shape[0] == 384
        assert len(embedding) == 384


def test_get_embedding_dimension(mock_sentence_transformer):
    """Test getting embedding dimension."""
    with patch('app.services.embeddings.SentenceTransformer', return_value=mock_sentence_transformer):
        service = EmbeddingService()
        
        dim = service.get_embedding_dimension()
        
        assert dim == 384


def test_encode_batch_size(mock_sentence_transformer):
    """Test encoding with custom batch size."""
    with patch('app.services.embeddings.SentenceTransformer', return_value=mock_sentence_transformer):
        service = EmbeddingService()
        
        texts = ["Text"] * 100
        service.encode(texts, batch_size=10)
        
        # Verify batch_size was used
        call_kwargs = mock_sentence_transformer.encode.call_args[1]
        assert call_kwargs['batch_size'] == 10


def test_embedding_service_import_error():
    """Test handling when sentence-transformers is not available."""
    with patch('app.services.embeddings.SENTENCE_TRANSFORMERS_AVAILABLE', False):
        with pytest.raises(ImportError):
            EmbeddingService()
