"""Vector database service using ChromaDB for local storage."""
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class VectorStore:
    """ChromaDB-based vector store for local RAG."""
    
    def __init__(
        self,
        collection_name: str = "student_handbook",
        persist_directory: Optional[str] = None
    ):
        """
        Initialize vector store.
        
        Args:
            collection_name: Name of the ChromaDB collection
            persist_directory: Directory to persist the database (defaults to config)
        """
        from app.config import settings
        
        self.collection_name = collection_name
        if persist_directory is None:
            persist_directory = settings.vector_db_path
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Get or create collection
        try:
            self.collection = self.client.get_collection(name=collection_name)
            logger.info(f"Loaded existing collection '{collection_name}' with {self.collection.count()} documents")
        except Exception:
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={"description": "ICL Student Support Services Handbook"}
            )
            logger.info(f"Created new collection '{collection_name}'")
    
    def add_documents(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict]] = None,
        ids: Optional[List[str]] = None
    ):
        """
        Add documents to the vector store.
        
        Args:
            texts: List of text documents
            metadatas: Optional metadata for each document
            ids: Optional IDs for each document
        """
        if not texts:
            logger.warning("No texts provided to add")
            return
        
        # Generate IDs if not provided
        if ids is None:
            ids = [f"doc_{i}" for i in range(len(texts))]
        
        # Default metadata if not provided
        if metadatas is None:
            metadatas = [{}] * len(texts)
        
        try:
            self.collection.add(
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Added {len(texts)} documents to collection")
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            raise
    
    def search(
        self,
        query: str,
        n_results: int = 5,
        filter_metadata: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Search for similar documents.
        
        Args:
            query: Search query text
            n_results: Number of results to return
            filter_metadata: Optional metadata filters
            
        Returns:
            List of search results with text, metadata, and distance
        """
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=filter_metadata
            )
            
            # Format results
            formatted_results = []
            if results['documents'] and len(results['documents'][0]) > 0:
                for i, doc in enumerate(results['documents'][0]):
                    result = {
                        'content': doc,
                        'score': 1.0 - results['distances'][0][i] if 'distances' in results else 0.0,
                        'metadata': results['metadatas'][0][i] if results.get('metadatas') and results['metadatas'][0] else {},
                        'id': results['ids'][0][i] if results.get('ids') and results['ids'][0] else None
                    }
                    formatted_results.append(result)
            
            logger.info(f"Found {len(formatted_results)} results for query")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching vector store: {e}")
            return []
    
    def delete_collection(self):
        """Delete the collection."""
        try:
            self.client.delete_collection(name=self.collection_name)
            logger.info(f"Deleted collection '{self.collection_name}'")
        except Exception as e:
            logger.error(f"Error deleting collection: {e}")
    
    def reset(self):
        """Reset the collection (delete and recreate)."""
        try:
            self.delete_collection()
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "ICL Student Support Services Handbook"}
            )
            logger.info(f"Reset collection '{self.collection_name}'")
        except Exception as e:
            logger.error(f"Error resetting collection: {e}")
            raise
    
    def count(self) -> int:
        """Get the number of documents in the collection."""
        try:
            return self.collection.count()
        except Exception:
            return 0
