"""Script to process ICL Student Support Services Handbook PDF and populate vector database."""
import argparse
import logging
import sys
from pathlib import Path
import requests
from urllib.parse import urlparse

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.services.pdf_processor import PDFProcessor, ChunkingStrategy
from app.services.vector_store import VectorStore
from app.services.embeddings import EmbeddingService
from app.config import settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def download_pdf(url: str, output_path: str) -> Path:
    """
    Download PDF from URL.
    
    Args:
        url: URL to download from
        output_path: Path to save the PDF
        
    Returns:
        Path to downloaded file
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Downloading PDF from {url}...")
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            f.write(response.content)
        
        logger.info(f"✓ Downloaded PDF to {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"Error downloading PDF: {e}")
        raise


def process_handbook(
    pdf_path: str,
    reset_db: bool = False,
    chunk_size: int = 500,
    chunk_overlap: int = 50,
    strategy: str = None
):
    """
    Process the ICL Student Handbook PDF and populate vector database.
    
    Args:
        pdf_path: Path to PDF file
        reset_db: Whether to reset the database before processing
        chunk_size: Size of text chunks
        chunk_overlap: Overlap between chunks
    """
    pdf_path = Path(pdf_path)
    
    # Initialize services
    logger.info("Initializing services...")
    pdf_processor = PDFProcessor()
    vector_store = VectorStore()
    embedding_service = EmbeddingService()
    
    # Reset database if requested
    if reset_db:
        logger.info("Resetting vector database...")
        vector_store.reset()
    
    # Check if database already has content
    doc_count = vector_store.count()
    if doc_count > 0 and not reset_db:
        logger.info(f"Vector database already contains {doc_count} documents.")
        response = input("Do you want to reset and reprocess? (yes/no): ")
        if response.lower() in ['yes', 'y']:
            vector_store.reset()
        else:
            logger.info("Skipping processing. Using existing database.")
            return
    
    # Extract text from PDF
    logger.info(f"Extracting text from PDF: {pdf_path}")
    try:
        text = pdf_processor.extract_text_from_pdf(str(pdf_path))
        logger.info(f"✓ Extracted {len(text)} characters from PDF")
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {e}")
        sys.exit(1)
    
    # Determine chunking strategy
    if strategy is None:
        strategy = settings.chunking_strategy
    
    try:
        chunking_strategy = ChunkingStrategy(strategy.lower())
    except ValueError:
        logger.warning(f"Invalid strategy '{strategy}', using 'sentence'")
        chunking_strategy = ChunkingStrategy.SENTENCE
    
    # Chunk the text
    logger.info(f"Chunking text using {chunking_strategy.value} strategy...")
    chunks = pdf_processor.chunk_text(
        text,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        strategy=chunking_strategy
    )
    logger.info(f"✓ Created {len(chunks)} chunks using {chunking_strategy.value} strategy")
    
    # Generate embeddings and add to vector store
    logger.info("Generating embeddings and adding to vector database...")
    texts = [chunk['text'] for chunk in chunks]
    metadatas = [
        {
            'chunk_id': chunk['id'],
            'chunk_index': chunk['chunk_index'],
            'source': 'ICL Student Support Services Handbook',
            'title': f"Handbook Section {chunk['chunk_index']}"
        }
        for chunk in chunks
    ]
    ids = [chunk['id'] for chunk in chunks]
    
    try:
        # ChromaDB will generate embeddings automatically using its default embedding function
        # The embeddings are generated on-the-fly when documents are added
        vector_store.add_documents(
            texts=texts,
            metadatas=metadatas,
            ids=ids
        )
        logger.info(f"✓ Added {len(chunks)} documents to vector database")
    except Exception as e:
        logger.error(f"Error adding documents to vector database: {e}")
        sys.exit(1)
    
    # Verify
    final_count = vector_store.count()
    logger.info(f"✓ Vector database now contains {final_count} documents")
    logger.info("✓ Processing complete!")


def main():
    parser = argparse.ArgumentParser(
        description="Process ICL Student Support Services Handbook PDF"
    )
    parser.add_argument(
        "--pdf",
        type=str,
        help="Path to PDF file or URL to download from"
    )
    parser.add_argument(
        "--url",
        type=str,
        default="https://www.icl.ac.nz/wp-content/uploads/2022/02/Student-Support-Services-Handbook-Feb-2022.pdf",
        help="URL to download PDF from (default: ICL handbook URL)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="./data/icl_handbook.pdf",
        help="Output path for downloaded PDF (default: ./data/icl_handbook.pdf)"
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset vector database before processing"
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=500,
        help="Size of text chunks (default: 500)"
    )
    parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=50,
        help="Overlap between chunks (default: 50)"
    )
    parser.add_argument(
        "--strategy",
        type=str,
        choices=["sentence", "semantic", "section", "recursive"],
        default=None,
        help="Chunking strategy (default: from config or 'sentence')"
    )
    
    args = parser.parse_args()
    
    # Determine PDF path
    if args.pdf:
        pdf_path = args.pdf
    else:
        # Download from URL
        pdf_path = download_pdf(args.url, args.output)
    
    # Process the handbook
    process_handbook(
        pdf_path=str(pdf_path),
        reset_db=args.reset,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
        strategy=args.strategy
    )


if __name__ == "__main__":
    main()
