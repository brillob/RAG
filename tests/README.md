# Test Suite Documentation

Comprehensive unit test suite for the RAG Student Support System with 90%+ code coverage.

## Test Coverage

The test suite covers all major business logic components:

### ✅ Core Services (90%+ Coverage)

1. **RAG Service** (`test_rag_service.py`)
   - Query processing with/without conversation_id
   - Language detection integration
   - Context building
   - Confidence calculation
   - Guardrails application
   - Error handling
   - Local and Azure mode initialization

2. **PDF Processor** (`test_pdf_processor.py`)
   - All 4 chunking strategies (sentence, semantic, section, recursive)
   - PDF text extraction (pdfplumber and pypdf)
   - Section extraction
   - Edge cases (empty text, whitespace, etc.)

3. **Vector Store** (`test_vector_store.py`)
   - Document addition
   - Semantic search
   - Metadata filtering
   - Collection management (reset, delete)
   - Error handling

4. **Conversation Memory** (`test_conversation_memory.py`)
   - Conversation creation
   - Message storage and retrieval
   - History management
   - TTL expiration
   - Context string formatting
   - Singleton pattern

5. **Language Detector** (`test_language_detector.py`)
   - Language detection
   - Supported language validation
   - Error handling
   - Language name mapping

6. **Embeddings Service** (`test_embeddings.py`)
   - Embedding generation
   - Batch processing
   - Dimension detection
   - Import error handling

7. **Mock OpenAI** (`test_mock_openai.py`)
   - Response generation
   - Context extraction
   - Query extraction
   - Keyword-based responses

8. **Configuration** (`test_config.py`)
   - Settings loading
   - Mode detection
   - Environment variable parsing
   - Default values

9. **API Endpoints** (`test_api.py`, `test_api_extended.py`)
   - Health check
   - Query endpoint
   - Authentication
   - Validation
   - Error handling

## Running Tests

### Run All Tests
```bash
pytest
```

### Run with Coverage Report
```bash
pytest --cov=app --cov-report=html
```

### Run Specific Test File
```bash
pytest tests/test_rag_service.py
```

### Run Specific Test
```bash
pytest tests/test_rag_service.py::test_process_query_new_conversation
```

### Run with Verbose Output
```bash
pytest -v
```

### Run with Coverage and Fail if Below 90%
```bash
pytest --cov=app --cov-fail-under=90
```

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures
├── test_api.py              # Basic API tests
├── test_api_extended.py     # Extended API tests
├── test_config.py           # Configuration tests
├── test_conversation_memory.py  # Memory management tests
├── test_embeddings.py       # Embedding service tests
├── test_language_detector.py # Language detection tests
├── test_mock_openai.py      # Mock OpenAI tests
├── test_pdf_processor.py    # PDF processing tests
├── test_rag_service.py      # RAG service tests
└── test_vector_store.py     # Vector store tests
```

## Fixtures

Common fixtures in `conftest.py`:
- `temp_dir`: Temporary directory for test files
- `mock_vector_store`: Mocked vector store
- `mock_conversation_memory`: Mocked conversation memory
- `mock_language_detector`: Mocked language detector
- `mock_openai_service`: Mocked OpenAI service
- `sample_pdf_text`: Sample PDF text
- `sample_chunks`: Sample text chunks
- `sample_search_results`: Sample search results

## Test Categories

### Unit Tests
- Test individual components in isolation
- Use mocks for dependencies
- Fast execution
- High coverage

### Integration Tests (Future)
- Test component interactions
- Use real services where possible
- Slower execution
- End-to-end scenarios

## Coverage Goals

- **Overall Coverage**: 90%+
- **Business Logic**: 95%+
- **Critical Paths**: 100%

## Writing New Tests

When adding new features:

1. **Add tests first** (TDD approach)
2. **Test happy paths** and **error cases**
3. **Use fixtures** for common setup
4. **Mock external dependencies**
5. **Test edge cases** (empty inputs, None values, etc.)
6. **Maintain 90%+ coverage**

### Example Test Template

```python
def test_feature_name():
    """Test description."""
    # Arrange
    service = Service()
    
    # Act
    result = service.method()
    
    # Assert
    assert result is not None
    assert result.expected_property == expected_value
```

## Continuous Integration

Tests should be run:
- Before committing code
- In CI/CD pipeline
- Before deploying to production

## Coverage Reports

After running tests with coverage:
- HTML report: `htmlcov/index.html`
- Terminal report: Shown in console
- XML report: `coverage.xml` (for CI tools)

## Notes

- All async tests use `@pytest.mark.asyncio`
- Mocks are used to avoid external API calls
- Tests are isolated and can run in any order
- No test dependencies on external services
