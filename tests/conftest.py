"""Pytest configuration and fixtures."""
import pytest
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Set test environment variables before importing app modules
os.environ["MODE"] = "local"
os.environ["ENABLE_CONVERSATION_MEMORY"] = "true"
os.environ["LOG_LEVEL"] = "DEBUG"


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def mock_vector_store():
    """Mock vector store for testing."""
    mock = MagicMock()
    mock.search.return_value = [
        {
            'content': 'Test content about enrolment requirements',
            'score': 0.9,
            'metadata': {'title': 'Enrolment', 'source': 'handbook.pdf'},
            'id': 'chunk_1'
        },
        {
            'content': 'Additional information about visas',
            'score': 0.8,
            'metadata': {'title': 'Visas', 'source': 'handbook.pdf'},
            'id': 'chunk_2'
        }
    ]
    mock.count.return_value = 10
    return mock


@pytest.fixture
def mock_conversation_memory():
    """Mock conversation memory for testing."""
    mock = MagicMock()
    mock.create_conversation.return_value = "test-conv-id-123"
    mock.get_context_string.return_value = "Previous conversation:\nStudent: Hello\nAssistant: Hi there"
    mock.get_history.return_value = [
        {'role': 'user', 'content': 'Hello', 'timestamp': '2024-01-01T00:00:00'},
        {'role': 'assistant', 'content': 'Hi there', 'timestamp': '2024-01-01T00:00:01'}
    ]
    return mock


@pytest.fixture
def mock_language_detector():
    """Mock language detector for testing."""
    mock = MagicMock()
    mock.detect_language.return_value = "en"
    mock.is_supported.return_value = True
    mock.get_language_name.return_value = "English"
    return mock


@pytest.fixture
def mock_openai_service():
    """Mock OpenAI service for testing."""
    mock = MagicMock()
    async def generate_response(prompt, max_tokens=500, temperature=0.3):
        return "This is a test response based on the provided context."
    mock.generate_response = generate_response
    return mock


@pytest.fixture
def sample_pdf_text():
    """Sample PDF text for testing."""
    return """
    Welcome to ICL Graduate Business School
    
    Enrolment Requirements
    
    To enroll in ICL Graduate Business Programmes, both domestic and international students are required to:
    - Have a valid visa to study in New Zealand (international students)
    - Have suitable travel/medical insurance
    - Have enough funds for onward travel or to sustain you while studying
    
    Visa Information
    
    As an international student, you are required by law to hold a valid visa for the duration of your study.
    You must show a copy of your valid visa to ICL before the first day of your class.
    
    Student Support
    
    Our Student Support Team provides you with the highest level of support and care.
    Contact: studentsupport@icl.ac.nz
    """


@pytest.fixture
def sample_chunks():
    """Sample text chunks for testing."""
    return [
        {
            'id': 'chunk_1',
            'text': 'To enroll in ICL Graduate Business Programmes, both domestic and international students are required to have a valid visa.',
            'chunk_index': 0,
            'strategy': 'sentence'
        },
        {
            'id': 'chunk_2',
            'text': 'As an international student, you are required by law to hold a valid visa for the duration of your study.',
            'chunk_index': 1,
            'strategy': 'sentence'
        }
    ]


@pytest.fixture
def sample_search_results():
    """Sample search results for testing."""
    return [
        {
            'content': 'To enroll in ICL Graduate Business Programmes, both domestic and international students are required to have a valid visa.',
            'title': 'Enrolment Requirements',
            'source': 'ICL Student Handbook',
            'score': 0.95,
            'metadata': {'chunk_id': 'chunk_1'}
        },
        {
            'content': 'As an international student, you are required by law to hold a valid visa for the duration of your study.',
            'title': 'Visa Information',
            'source': 'ICL Student Handbook',
            'score': 0.85,
            'metadata': {'chunk_id': 'chunk_2'}
        }
    ]
