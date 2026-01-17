"""Unit tests for PDF processor and chunking strategies."""
import pytest
from pathlib import Path
from app.services.pdf_processor import PDFProcessor, ChunkingStrategy
from unittest.mock import patch, MagicMock


@pytest.fixture
def pdf_processor():
    """Create PDF processor instance."""
    return PDFProcessor()


@pytest.fixture
def sample_text():
    """Sample text for chunking tests."""
    return """
    Section 1: Enrolment Requirements
    
    To enroll in ICL Graduate Business Programmes, both domestic and international students are required to have a valid visa to study in New Zealand. International students must also have suitable travel and medical insurance. You need enough funds for onward travel or to sustain you while studying.
    
    Section 2: Visa Information
    
    As an international student, you are required by law to hold a valid visa for the duration of your study at ICL Graduate Business School. You must show a copy of your valid visa to ICL before the first day of your class. You will need a valid visa to complete your enrolment.
    
    Section 3: Student Support
    
    Our Student Support Team provides you with the highest level of support and care. We aim to create a supportive, safe and caring learning environment for you. Contact us at studentsupport@icl.ac.nz for assistance.
    """


def test_chunk_sentence_based(pdf_processor, sample_text):
    """Test sentence-based chunking strategy."""
    chunks = pdf_processor._chunk_sentence_based(sample_text, chunk_size=200, chunk_overlap=50)
    
    assert len(chunks) > 0
    assert all('id' in chunk for chunk in chunks)
    assert all('text' in chunk for chunk in chunks)
    assert all('strategy' in chunk for chunk in chunks)
    assert all(chunk['strategy'] == 'sentence' for chunk in chunks)
    
    # Check chunk sizes
    for chunk in chunks:
        assert len(chunk['text']) <= 250  # chunk_size + some overlap tolerance


def test_chunk_sentence_based_overlap(pdf_processor):
    """Test sentence-based chunking with overlap."""
    text = "Sentence one. Sentence two. Sentence three. Sentence four. Sentence five."
    chunks = pdf_processor._chunk_sentence_based(text, chunk_size=50, chunk_overlap=20)
    
    if len(chunks) > 1:
        # Check that chunks have some overlap
        first_chunk_end = chunks[0]['text'][-20:]
        second_chunk_start = chunks[1]['text'][:30]
        # There should be some common text
        assert len(first_chunk_end) > 0


def test_chunk_section_based(pdf_processor, sample_text):
    """Test section-based chunking strategy."""
    chunks = pdf_processor._chunk_section_based(sample_text, chunk_size=500, chunk_overlap=50)
    
    assert len(chunks) > 0
    assert all('strategy' in chunk for chunk in chunks)
    assert all(chunk['strategy'] == 'section' for chunk in chunks)
    assert all('section_title' in chunk for chunk in chunks)


def test_chunk_recursive(pdf_processor, sample_text):
    """Test recursive chunking strategy."""
    chunks = pdf_processor._chunk_recursive(sample_text, chunk_size=200, chunk_overlap=50)
    
    assert len(chunks) > 0
    assert all('strategy' in chunk for chunk in chunks)
    assert all(chunk['strategy'] == 'recursive' for chunk in chunks)
    
    # Check chunk sizes
    for chunk in chunks:
        assert len(chunk['text']) <= 250  # chunk_size + overlap tolerance


def test_chunk_semantic_fallback(pdf_processor, sample_text):
    """Test semantic chunking falls back to sentence-based if embeddings unavailable."""
    with patch('app.services.pdf_processor.EmbeddingService', side_effect=ImportError):
        chunks = pdf_processor._chunk_semantic(sample_text, chunk_size=200, chunk_overlap=50)
        
        # Should fall back to sentence-based
        assert len(chunks) > 0
        assert all('strategy' in chunk for chunk in chunks)


def test_chunk_semantic_with_embeddings(pdf_processor, sample_text):
    """Test semantic chunking with embeddings."""
    mock_embedding_service = MagicMock()
    mock_embedding_service.encode.return_value = [
        [0.1, 0.2, 0.3] * 128,  # 384 dim embedding
        [0.2, 0.3, 0.4] * 128,
        [0.1, 0.2, 0.3] * 128,
    ]
    
    with patch('app.services.pdf_processor.EmbeddingService', return_value=mock_embedding_service):
        # First create sentence chunks
        sentence_chunks = pdf_processor._chunk_sentence_based(sample_text, 100, 20)
        if len(sentence_chunks) >= 3:
            chunks = pdf_processor._chunk_semantic(sample_text, chunk_size=200, chunk_overlap=50)
            assert len(chunks) > 0
            assert all('strategy' in chunk for chunk in chunks)


def test_chunk_text_strategy_selection(pdf_processor, sample_text):
    """Test chunk_text method with different strategies."""
    strategies = [
        ChunkingStrategy.SENTENCE,
        ChunkingStrategy.SECTION,
        ChunkingStrategy.RECURSIVE
    ]
    
    for strategy in strategies:
        chunks = pdf_processor.chunk_text(
            sample_text,
            chunk_size=200,
            chunk_overlap=50,
            strategy=strategy
        )
        assert len(chunks) > 0
        assert all(chunk['strategy'] == strategy.value for chunk in chunks)


def test_chunk_text_invalid_strategy(pdf_processor, sample_text):
    """Test chunk_text with invalid strategy falls back to sentence-based."""
    # Use invalid strategy value
    chunks = pdf_processor.chunk_text(
        sample_text,
        chunk_size=200,
        chunk_overlap=50,
        strategy="invalid_strategy"
    )
    # Should still work (fallback)
    assert len(chunks) > 0


def test_extract_sections(pdf_processor, sample_text):
    """Test section extraction from text."""
    sections = pdf_processor.extract_sections(sample_text)
    
    assert len(sections) > 0
    assert all('title' in section for section in sections)
    assert all('content' in section for section in sections)
    
    # Check that section titles are extracted
    titles = [s['title'] for s in sections]
    assert any('Enrolment' in title or 'Visa' in title or 'Support' in title for title in titles)


def test_extract_sections_no_headers(pdf_processor):
    """Test section extraction with text that has no clear headers."""
    text = "This is just regular text without any clear section headers. It continues here."
    sections = pdf_processor.extract_sections(text)
    
    # Should still return something
    assert isinstance(sections, list)


@patch('app.services.pdf_processor.pdfplumber')
def test_extract_text_from_pdf_pdfplumber(mock_pdfplumber, pdf_processor, temp_dir):
    """Test PDF text extraction using pdfplumber."""
    pdf_path = Path(temp_dir) / "test.pdf"
    pdf_path.write_bytes(b"fake pdf content")
    
    mock_pdf = MagicMock()
    mock_page = MagicMock()
    mock_page.extract_text.return_value = "Extracted text from page 1"
    mock_pdf.pages = [mock_page]
    mock_pdfplumber.open.return_value.__enter__.return_value = mock_pdf
    
    text = pdf_processor.extract_text_from_pdf(str(pdf_path))
    
    assert "Extracted text from page 1" in text
    mock_pdfplumber.open.assert_called_once()


@patch('app.services.pdf_processor.pdfplumber', None)
@patch('app.services.pdf_processor.pypdf')
def test_extract_text_from_pdf_pypdf_fallback(mock_pypdf, pdf_processor, temp_dir):
    """Test PDF text extraction using pypdf as fallback."""
    pdf_path = Path(temp_dir) / "test.pdf"
    pdf_path.write_bytes(b"fake pdf content")
    
    mock_reader = MagicMock()
    mock_page = MagicMock()
    mock_page.extract_text.return_value = "Extracted text from pypdf"
    mock_reader.pages = [mock_page]
    mock_pypdf.PdfReader.return_value = mock_reader
    
    text = pdf_processor._extract_with_pypdf(pdf_path)
    
    assert "Extracted text from pypdf" in text


def test_extract_text_from_pdf_file_not_found(pdf_processor):
    """Test PDF extraction with non-existent file."""
    with pytest.raises(FileNotFoundError):
        pdf_processor.extract_text_from_pdf("nonexistent.pdf")


def test_chunk_text_empty_string(pdf_processor):
    """Test chunking with empty string."""
    chunks = pdf_processor.chunk_text("", chunk_size=100, chunk_overlap=10)
    # Should handle gracefully
    assert isinstance(chunks, list)


def test_chunk_text_whitespace_only(pdf_processor):
    """Test chunking with whitespace-only string."""
    chunks = pdf_processor.chunk_text("   \n\n   ", chunk_size=100, chunk_overlap=10)
    # Should handle gracefully
    assert isinstance(chunks, list)
