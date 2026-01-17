"""PDF processing utilities for extracting content from student handbook."""
import logging
import re
from typing import List, Dict, Optional
from pathlib import Path
from enum import Enum

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False
    try:
        import pypdf
        PYPDF_AVAILABLE = True
    except ImportError:
        PYPDF_AVAILABLE = False

logger = logging.getLogger(__name__)


class ChunkingStrategy(str, Enum):
    """Available chunking strategies."""
    SENTENCE = "sentence"  # Original sentence-based
    SEMANTIC = "semantic"  # Group by semantic similarity
    SECTION = "section"   # Chunk by document sections
    RECURSIVE = "recursive"  # Recursive character splitting


class PDFProcessor:
    """Process PDF documents and extract structured content."""
    
    def __init__(self):
        """Initialize PDF processor."""
        if not PDFPLUMBER_AVAILABLE and not PYPDF_AVAILABLE:
            logger.warning("No PDF library available. Install pdfplumber or pypdf.")
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text from PDF file.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted text content
        """
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        text_content = []
        
        if PDFPLUMBER_AVAILABLE:
            try:
                with pdfplumber.open(pdf_path) as pdf:
                    for page in pdf.pages:
                        text = page.extract_text()
                        if text:
                            text_content.append(text)
                logger.info(f"Extracted text from {len(text_content)} pages using pdfplumber")
            except Exception as e:
                logger.error(f"Error extracting text with pdfplumber: {e}")
                if PYPDF_AVAILABLE:
                    return self._extract_with_pypdf(pdf_path)
                raise
        elif PYPDF_AVAILABLE:
            return self._extract_with_pypdf(pdf_path)
        else:
            raise ImportError("No PDF library available. Install pdfplumber or pypdf.")
        
        return "\n\n".join(text_content)
    
    def _extract_with_pypdf(self, pdf_path: Path) -> str:
        """Extract text using pypdf as fallback."""
        import pypdf
        text_content = []
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = pypdf.PdfReader(file)
                for page in pdf_reader.pages:
                    text = page.extract_text()
                    if text:
                        text_content.append(text)
            logger.info(f"Extracted text from {len(text_content)} pages using pypdf")
        except Exception as e:
            logger.error(f"Error extracting text with pypdf: {e}")
            raise
        
        return "\n\n".join(text_content)
    
    def chunk_text(
        self,
        text: str,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        strategy: ChunkingStrategy = ChunkingStrategy.SENTENCE
    ) -> List[Dict[str, str]]:
        """
        Split text into chunks using the specified strategy.
        
        Args:
            text: Text to chunk
            chunk_size: Maximum characters per chunk
            chunk_overlap: Overlap between chunks
            strategy: Chunking strategy to use
            
        Returns:
            List of text chunks with metadata
        """
        if strategy == ChunkingStrategy.SENTENCE:
            return self._chunk_sentence_based(text, chunk_size, chunk_overlap)
        elif strategy == ChunkingStrategy.SEMANTIC:
            return self._chunk_semantic(text, chunk_size, chunk_overlap)
        elif strategy == ChunkingStrategy.SECTION:
            return self._chunk_section_based(text, chunk_size, chunk_overlap)
        elif strategy == ChunkingStrategy.RECURSIVE:
            return self._chunk_recursive(text, chunk_size, chunk_overlap)
        else:
            logger.warning(f"Unknown strategy {strategy}, using sentence-based")
            return self._chunk_sentence_based(text, chunk_size, chunk_overlap)
    
    def _chunk_sentence_based(
        self,
        text: str,
        chunk_size: int,
        chunk_overlap: int
    ) -> List[Dict[str, str]]:
        """Original sentence-based chunking strategy."""
        # Clean text
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Split into sentences first
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        chunks = []
        current_chunk = ""
        current_length = 0
        chunk_id = 0
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            sentence_length = len(sentence)
            
            # If adding this sentence would exceed chunk size, save current chunk
            if current_length + sentence_length > chunk_size and current_chunk:
                chunks.append({
                    'id': f"chunk_{chunk_id}",
                    'text': current_chunk.strip(),
                    'chunk_index': chunk_id,
                    'strategy': 'sentence'
                })
                chunk_id += 1
                
                # Start new chunk with overlap
                if chunk_overlap > 0 and len(current_chunk) > chunk_overlap:
                    overlap_text = current_chunk[-chunk_overlap:]
                    current_chunk = overlap_text + " " + sentence
                    current_length = len(current_chunk)
                else:
                    current_chunk = sentence
                    current_length = sentence_length
            else:
                # Add sentence to current chunk
                if current_chunk:
                    current_chunk += " " + sentence
                else:
                    current_chunk = sentence
                current_length = len(current_chunk)
        
        # Add final chunk
        if current_chunk.strip():
            chunks.append({
                'id': f"chunk_{chunk_id}",
                'text': current_chunk.strip(),
                'chunk_index': chunk_id,
                'strategy': 'sentence'
            })
        
        logger.info(f"Created {len(chunks)} text chunks using sentence-based strategy")
        return chunks
    
    def _chunk_section_based(
        self,
        text: str,
        chunk_size: int,
        chunk_overlap: int
    ) -> List[Dict[str, str]]:
        """Section-based chunking - chunks by document sections."""
        sections = self.extract_sections(text)
        chunks = []
        chunk_id = 0
        
        for section in sections:
            section_text = f"{section['title']}\n{section['content']}"
            
            # If section is small enough, use as single chunk
            if len(section_text) <= chunk_size:
                chunks.append({
                    'id': f"chunk_{chunk_id}",
                    'text': section_text.strip(),
                    'chunk_index': chunk_id,
                    'strategy': 'section',
                    'section_title': section['title']
                })
                chunk_id += 1
            else:
                # Split large sections using sentence-based within section
                section_chunks = self._chunk_sentence_based(
                    section_text,
                    chunk_size,
                    chunk_overlap
                )
                for sc in section_chunks:
                    sc['id'] = f"chunk_{chunk_id}"
                    sc['chunk_index'] = chunk_id
                    sc['strategy'] = 'section'
                    sc['section_title'] = section['title']
                    chunks.append(sc)
                    chunk_id += 1
        
        logger.info(f"Created {len(chunks)} text chunks using section-based strategy")
        return chunks
    
    def _chunk_recursive(
        self,
        text: str,
        chunk_size: int,
        chunk_overlap: int
    ) -> List[Dict[str, str]]:
        """Recursive character splitting - hierarchical splitting."""
        def recursive_split(text: str, max_size: int) -> List[str]:
            """Recursively split text by different separators."""
            if len(text) <= max_size:
                return [text]
            
            # Try different separators in order of preference
            separators = [
                '\n\n',  # Paragraphs
                '\n',    # Lines
                '. ',    # Sentences
                ' ',     # Words
                ''       # Characters (last resort)
            ]
            
            for sep in separators:
                if sep in text:
                    parts = text.split(sep)
                    if len(parts) > 1:
                        result = []
                        current_part = ""
                        
                        for part in parts:
                            if sep:
                                part_with_sep = part + sep
                            else:
                                part_with_sep = part
                            
                            if len(current_part) + len(part_with_sep) <= max_size:
                                current_part += part_with_sep
                            else:
                                if current_part:
                                    result.extend(recursive_split(current_part, max_size))
                                current_part = part_with_sep
                        
                        if current_part:
                            result.extend(recursive_split(current_part, max_size))
                        
                        return result
            
            # Fallback: split by character
            return [text[i:i+max_size] for i in range(0, len(text), max_size)]
        
        # Clean text
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Recursively split
        text_chunks = recursive_split(text, chunk_size)
        
        # Apply overlap
        chunks = []
        for i, chunk_text in enumerate(text_chunks):
            # Add overlap from previous chunk
            if i > 0 and chunk_overlap > 0:
                prev_chunk = chunks[-1]['text']
                if len(prev_chunk) > chunk_overlap:
                    overlap = prev_chunk[-chunk_overlap:]
                    chunk_text = overlap + " " + chunk_text
            
            chunks.append({
                'id': f"chunk_{i}",
                'text': chunk_text.strip(),
                'chunk_index': i,
                'strategy': 'recursive'
            })
        
        logger.info(f"Created {len(chunks)} text chunks using recursive strategy")
        return chunks
    
    def _chunk_semantic(
        self,
        text: str,
        chunk_size: int,
        chunk_overlap: int
    ) -> List[Dict[str, str]]:
        """
        Semantic chunking - groups text by semantic similarity.
        Note: Requires embeddings service, falls back to sentence-based if not available.
        """
        try:
            from app.services.embeddings import EmbeddingService
            embedding_service = EmbeddingService()
        except Exception as e:
            logger.warning(f"Semantic chunking requires embeddings service: {e}. Falling back to sentence-based.")
            return self._chunk_sentence_based(text, chunk_size, chunk_overlap)
        
        # First, create sentence-based chunks
        sentence_chunks = self._chunk_sentence_based(text, chunk_size, chunk_overlap)
        
        if len(sentence_chunks) <= 1:
            return sentence_chunks
        
        # Generate embeddings for all chunks
        chunk_texts = [chunk['text'] for chunk in sentence_chunks]
        embeddings = embedding_service.encode(chunk_texts)
        
        # Group similar chunks together
        # Simple approach: merge chunks with high similarity
        merged_chunks = []
        current_group = [sentence_chunks[0]]
        current_text = sentence_chunks[0]['text']
        
        similarity_threshold = 0.85  # Adjust based on needs
        
        for i in range(1, len(sentence_chunks)):
            # Calculate cosine similarity
            import numpy as np
            similarity = np.dot(embeddings[i-1], embeddings[i]) / (
                np.linalg.norm(embeddings[i-1]) * np.linalg.norm(embeddings[i])
            )
            
            # Check if we can merge (similarity high and within size limit)
            test_merge = current_text + " " + sentence_chunks[i]['text']
            
            if similarity > similarity_threshold and len(test_merge) <= chunk_size * 1.5:
                current_group.append(sentence_chunks[i])
                current_text = test_merge
            else:
                # Save current group
                merged_chunks.append({
                    'id': f"chunk_{len(merged_chunks)}",
                    'text': current_text.strip(),
                    'chunk_index': len(merged_chunks),
                    'strategy': 'semantic',
                    'merged_from': len(current_group)
                })
                # Start new group
                current_group = [sentence_chunks[i]]
                current_text = sentence_chunks[i]['text']
        
        # Add final group
        if current_text.strip():
            merged_chunks.append({
                'id': f"chunk_{len(merged_chunks)}",
                'text': current_text.strip(),
                'chunk_index': len(merged_chunks),
                'strategy': 'semantic',
                'merged_from': len(current_group)
            })
        
        logger.info(f"Created {len(merged_chunks)} text chunks using semantic strategy (from {len(sentence_chunks)} initial chunks)")
        return merged_chunks
    
    def extract_sections(self, text: str) -> List[Dict[str, str]]:
        """
        Extract sections from structured PDF text.
        
        Args:
            text: Full text content
            
        Returns:
            List of sections with titles and content
        """
        sections = []
        
        # Pattern to match section headers (usually in caps or bold)
        # Look for lines that are all caps, short, and followed by content
        lines = text.split('\n')
        current_section = None
        current_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if line looks like a section header
            # Headers are often short, may be in caps, or have specific patterns
            is_header = (
                len(line) < 100 and
                (line.isupper() or
                 line.startswith('#') or
                 re.match(r'^[A-Z][a-z]+(\s+[A-Z][a-z]+)*$', line))
            )
            
            if is_header and len(line) > 3:
                # Save previous section
                if current_section and current_content:
                    sections.append({
                        'title': current_section,
                        'content': '\n'.join(current_content).strip()
                    })
                
                # Start new section
                current_section = line
                current_content = []
            else:
                if current_section:
                    current_content.append(line)
                else:
                    # Content before first section
                    if current_content or line:
                        current_content.append(line)
        
        # Add final section
        if current_section and current_content:
            sections.append({
                'title': current_section,
                'content': '\n'.join(current_content).strip()
            })
        
        logger.info(f"Extracted {len(sections)} sections from document")
        return sections
