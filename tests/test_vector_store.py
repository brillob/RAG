"""Unit tests for vector store (ChromaDB wrapper)."""
import pytest
from unittest.mock import Mock, MagicMock, patch
from app.services.vector_store import VectorStore


@pytest.fixture
def mock_chromadb():
    """Mock ChromaDB client and collection."""
    mock_collection = MagicMock()
    mock_collection.count.return_value = 0
    mock_collection.query.return_value = {
        'documents': [[]],
        'distances': [[]],
        'metadatas': [[]],
        'ids': [[]]
    }
    
    mock_client = MagicMock()
    mock_client.get_collection.side_effect = Exception("Collection not found")
    mock_client.create_collection.return_value = mock_collection
    
    return mock_client, mock_collection


@pytest.fixture
def vector_store(mock_chromadb, temp_dir):
    """Create vector store with mocked ChromaDB."""
    mock_client, mock_collection = mock_chromadb
    
    with patch('app.services.vector_store.chromadb.PersistentClient', return_value=mock_client):
        with patch('app.config.settings') as mock_settings:
            mock_settings.vector_db_path = temp_dir
            store = VectorStore(collection_name="test_collection", persist_directory=temp_dir)
            store.collection = mock_collection
            store.client = mock_client
            return store, mock_collection


def test_vector_store_initialization(vector_store):
    """Test vector store initialization."""
    store, mock_collection = vector_store
    assert store is not None
    assert store.collection is not None


def test_add_documents(vector_store):
    """Test adding documents to vector store."""
    store, mock_collection = vector_store
    
    texts = ["Document 1", "Document 2"]
    metadatas = [{"source": "test1"}, {"source": "test2"}]
    ids = ["doc1", "doc2"]
    
    store.add_documents(texts, metadatas, ids)
    
    mock_collection.add.assert_called_once_with(
        documents=texts,
        metadatas=metadatas,
        ids=ids
    )


def test_add_documents_without_ids(vector_store):
    """Test adding documents without providing IDs."""
    store, mock_collection = vector_store
    
    texts = ["Document 1", "Document 2"]
    
    store.add_documents(texts)
    
    # Should generate IDs automatically
    call_args = mock_collection.add.call_args
    assert call_args is not None
    assert len(call_args[1]['ids']) == 2


def test_add_documents_empty_list(vector_store):
    """Test adding empty document list."""
    store, mock_collection = vector_store
    
    store.add_documents([])
    
    # Should not call add
    mock_collection.add.assert_not_called()


def test_search(vector_store):
    """Test searching the vector store."""
    store, mock_collection = vector_store
    
    # Mock search results
    mock_collection.query.return_value = {
        'documents': [['Result 1', 'Result 2']],
        'distances': [[0.1, 0.2]],
        'metadatas': [[{'title': 'Doc1'}, {'title': 'Doc2'}]],
        'ids': [['id1', 'id2']]
    }
    
    results = store.search("test query", n_results=2)
    
    assert len(results) == 2
    assert results[0]['content'] == 'Result 1'
    assert results[0]['score'] > 0
    assert 'metadata' in results[0]
    mock_collection.query.assert_called_once()


def test_search_no_results(vector_store):
    """Test search with no results."""
    store, mock_collection = vector_store
    
    mock_collection.query.return_value = {
        'documents': [[]],
        'distances': [[]],
        'metadatas': [[]],
        'ids': [[]]
    }
    
    results = store.search("query with no results")
    
    assert len(results) == 0


def test_search_with_metadata_filter(vector_store):
    """Test search with metadata filter."""
    store, mock_collection = vector_store
    
    filter_metadata = {'source': 'handbook.pdf'}
    
    store.search("test", filter_metadata=filter_metadata)
    
    call_args = mock_collection.query.call_args
    assert call_args[1]['where'] == filter_metadata


def test_count(vector_store):
    """Test getting document count."""
    store, mock_collection = vector_store
    
    mock_collection.count.return_value = 42
    
    count = store.count()
    
    assert count == 42
    mock_collection.count.assert_called_once()


def test_count_exception(vector_store):
    """Test count when collection doesn't exist."""
    store, mock_collection = vector_store
    
    mock_collection.count.side_effect = Exception("Error")
    
    count = store.count()
    
    assert count == 0


def test_reset(vector_store):
    """Test resetting the collection."""
    store, mock_collection = vector_store
    
    store.reset()
    
    # Should delete and recreate
    store.client.delete_collection.assert_called_once()
    store.client.create_collection.assert_called_once()


def test_delete_collection(vector_store):
    """Test deleting the collection."""
    store, mock_collection = vector_store
    
    store.delete_collection()
    
    store.client.delete_collection.assert_called_once_with(name=store.collection_name)


def test_delete_collection_error(vector_store):
    """Test delete collection with error."""
    store, mock_collection = vector_store
    
    store.client.delete_collection.side_effect = Exception("Error")
    
    # Should handle error gracefully
    store.delete_collection()
    # No exception should be raised


def test_search_score_calculation(vector_store):
    """Test that search scores are calculated correctly."""
    store, mock_collection = vector_store
    
    mock_collection.query.return_value = {
        'documents': [['Result 1', 'Result 2']],
        'distances': [[0.2, 0.5]],  # Lower distance = higher similarity
        'metadatas': [[{}, {}]],
        'ids': [['id1', 'id2']]
    }
    
    results = store.search("test")
    
    # Score should be 1.0 - distance
    assert results[0]['score'] == 0.8  # 1.0 - 0.2
    assert results[1]['score'] == 0.5  # 1.0 - 0.5


def test_search_without_distances(vector_store):
    """Test search when distances are not returned."""
    store, mock_collection = vector_store
    
    mock_collection.query.return_value = {
        'documents': [['Result 1']],
        'metadatas': [[{}]],
        'ids': [['id1']]
    }
    
    results = store.search("test")
    
    assert len(results) == 1
    assert results[0]['score'] == 0.0  # Default when no distances
