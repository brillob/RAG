"""Local embeddings service using sentence-transformers."""
import logging
from typing import List
import numpy as np

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Local embedding service using sentence-transformers."""
    
    def __init__(self, model_name: Optional[str] = None):
        """
        Initialize embedding service.
        
        Args:
            model_name: Name of the sentence-transformers model (defaults to config)
                Options:
                - "all-MiniLM-L6-v2" (fast, English, 384 dims)
                - "paraphrase-multilingual-MiniLM-L12-v2" (multilingual, 384 dims)
                - "all-mpnet-base-v2" (better quality, English, 768 dims)
        """
        from app.config import settings
        
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise ImportError(
                "sentence-transformers not installed. "
                "Install with: pip install sentence-transformers"
            )
        
        if model_name is None:
            model_name = settings.embedding_model
        self.model_name = model_name
        logger.info(f"Loading embedding model: {model_name}...")
        
        try:
            self.model = SentenceTransformer(model_name)
            logger.info(f"✓ Loaded embedding model: {model_name}")
        except Exception as e:
            logger.error(f"Error loading embedding model: {e}")
            raise
    
    def encode(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """
        Generate embeddings for texts.
        
        Args:
            texts: List of text strings
            batch_size: Batch size for processing
            
        Returns:
            Numpy array of embeddings
        """
        if not texts:
            return np.array([])
        
        try:
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                show_progress_bar=len(texts) > 10,
                convert_to_numpy=True
            )
            logger.debug(f"Generated embeddings for {len(texts)} texts")
            return embeddings
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise
    
    def encode_query(self, query: str) -> np.ndarray:
        """
        Generate embedding for a single query.
        
        Args:
            query: Query text
            
        Returns:
            Embedding vector
        """
        return self.encode([query])[0]
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings."""
        # Test with a single word
        test_embedding = self.encode(["test"])
        return test_embedding.shape[1]
