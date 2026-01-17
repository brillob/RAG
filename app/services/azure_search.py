"""Azure AI Search integration for document retrieval."""
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.models import QueryType, QueryLanguage
from typing import List, Dict, Optional
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class AzureSearchService:
    """Service for querying Azure AI Search."""
    
    def __init__(self):
        """Initialize Azure Search client."""
        self.client = SearchClient(
            endpoint=settings.azure_search_endpoint,
            index_name=settings.azure_search_index_name,
            credential=AzureKeyCredential(settings.azure_search_key)
        )
        logger.info("Azure Search client initialized")
    
    def search(
        self,
        query: str,
        language: str = "en",
        top: int = 5,
        min_score: float = 0.5
    ) -> List[Dict]:
        """
        Search the knowledge base for relevant documents.
        
        Args:
            query: Search query
            language: Language code for query understanding
            top: Number of results to return
            min_score: Minimum relevance score threshold
            
        Returns:
            List of relevant documents with metadata
        """
        try:
            # Map language code to QueryLanguage enum
            query_language = self._map_language_to_query_language(language)
            
            results = self.client.search(
                search_text=query,
                query_type=QueryType.SEMANTIC,
                query_language=query_language,
                semantic_configuration_name="default",  # Configure in Azure portal
                top=top,
                include_total_count=True
            )
            
            documents = []
            for result in results:
                score = result.get('@search.score', 0.0)
                if score >= min_score:
                    doc = {
                        'content': result.get('content', ''),
                        'title': result.get('title', ''),
                        'source': result.get('source', ''),
                        'score': score,
                        'metadata': {k: v for k, v in result.items() 
                                   if not k.startswith('@')}
                    }
                    documents.append(doc)
            
            logger.info(f"Retrieved {len(documents)} relevant documents for query")
            return documents
            
        except Exception as e:
            logger.error(f"Azure Search error: {e}")
            return []
    
    def _map_language_to_query_language(self, language_code: str) -> QueryLanguage:
        """Map language code to Azure QueryLanguage enum."""
        mapping = {
            'en': QueryLanguage.EN_US,
            'es': QueryLanguage.ES_ES,
            'fr': QueryLanguage.FR_FR,
            'de': QueryLanguage.DE_DE,
            'it': QueryLanguage.IT_IT,
            'pt': QueryLanguage.PT_BR,
            'zh': QueryLanguage.ZH_CN,
            'ja': QueryLanguage.JA_JP,
            'ko': QueryLanguage.KO_KR,
        }
        return mapping.get(language_code, QueryLanguage.EN_US)
