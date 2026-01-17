"""Unit tests for mock OpenAI service."""
import pytest
from app.services.mock_openai import MockOpenAIService


@pytest.fixture
def mock_openai():
    """Create mock OpenAI service instance."""
    return MockOpenAIService()


@pytest.mark.asyncio
async def test_generate_response_with_context(mock_openai):
    """Test response generation with sufficient context."""
    prompt = """
    Context from knowledge base:
    To enroll in ICL, you need a valid visa and insurance.
    
    Student's question: What are the requirements?
    """
    
    response = await mock_openai.generate_response(prompt)
    
    assert response is not None
    assert len(response) > 0
    assert "requirements" in response.lower() or "visa" in response.lower() or "insurance" in response.lower()


@pytest.mark.asyncio
async def test_generate_response_insufficient_context(mock_openai):
    """Test response when context is insufficient."""
    prompt = """
    Context from knowledge base:
    Short context.
    
    Student's question: What are the requirements?
    """
    
    response = await mock_openai.generate_response(prompt)
    
    assert "don't have enough information" in response.lower()


@pytest.mark.asyncio
async def test_generate_response_no_context(mock_openai):
    """Test response with no context."""
    prompt = """
    Student's question: What are the requirements?
    """
    
    response = await mock_openai.generate_response(prompt)
    
    assert "don't have enough information" in response.lower()


@pytest.mark.asyncio
async def test_generate_response_max_tokens(mock_openai):
    """Test that response respects max_tokens limit."""
    prompt = """
    Context from knowledge base:
    """ + "A" * 1000 + """
    
    Student's question: What is this?
    """
    
    response = await mock_openai.generate_response(prompt, max_tokens=50)
    
    assert len(response) <= 53  # 50 + "..."


@pytest.mark.asyncio
async def test_extract_query_from_prompt(mock_openai):
    """Test extracting query from prompt."""
    prompt = """
    Context: Some context here.
    
    Student's question: What are the requirements?
    
    Provide response:
    """
    
    query = mock_openai._extract_query_from_prompt(prompt)
    
    assert "requirements" in query.lower()


@pytest.mark.asyncio
async def test_extract_context_from_prompt(mock_openai):
    """Test extracting context from prompt."""
    prompt = """
    Context from knowledge base:
    This is the context information about enrolment.
    
    Student's question: What are the requirements?
    """
    
    context = mock_openai._extract_context_from_prompt(prompt)
    
    assert "enrolment" in context.lower()
    assert "context" in context.lower()


@pytest.mark.asyncio
async def test_generate_response_admission_keyword(mock_openai):
    """Test response generation for admission-related queries."""
    prompt = """
    Context from knowledge base:
    Admission requirements include diploma, GPA, and English test scores.
    
    Student's question: What are the admission requirements?
    """
    
    response = await mock_openai.generate_response(prompt)
    
    assert "admission" in response.lower() or "requirements" in response.lower() or "diploma" in response.lower()


@pytest.mark.asyncio
async def test_generate_response_tuition_keyword(mock_openai):
    """Test response generation for tuition-related queries."""
    prompt = """
    Context from knowledge base:
    Annual tuition is $15,000 with additional fees.
    
    Student's question: How much does tuition cost?
    """
    
    response = await mock_openai.generate_response(prompt)
    
    assert "tuition" in response.lower() or "cost" in response.lower() or "$" in response


@pytest.mark.asyncio
async def test_generate_response_visa_keyword(mock_openai):
    """Test response generation for visa-related queries."""
    prompt = """
    Context from knowledge base:
    International students need an F-1 student visa.
    
    Student's question: What visa do I need?
    """
    
    response = await mock_openai.generate_response(prompt)
    
    assert "visa" in response.lower() or "f-1" in response.lower() or "international" in response.lower()
