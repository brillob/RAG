"""In-memory mock Azure Search service for local testing."""
from typing import List, Dict
import logging
import re

logger = logging.getLogger(__name__)


class MockSearchService:
    """Mock Azure Search service using in-memory data for local testing."""
    
    def __init__(self):
        """Initialize with sample knowledge base data."""
        # Sample knowledge base for testing
        self.knowledge_base = [
            {
                'id': 'doc1',
                'title': 'Admission Requirements',
                'content': 'To be admitted, students need a high school diploma or equivalent, minimum GPA of 2.5, and English proficiency test scores (IELTS 6.0 or TOEFL 70). Application deadline is March 1st for fall semester.',
                'source': 'admissions-handbook.pdf',
                'category': 'admissions'
            },
            {
                'id': 'doc2',
                'title': 'Tuition and Fees',
                'content': 'Annual tuition is $15,000 for undergraduate programs. Additional fees include registration ($500), technology ($300), and student services ($200). Financial aid and scholarships are available.',
                'source': 'tuition-guide.pdf',
                'category': 'financial'
            },
            {
                'id': 'doc3',
                'title': 'Course Registration',
                'content': 'Course registration opens two weeks before each semester. Students can register online through the student portal. Prerequisites must be completed before enrolling in advanced courses.',
                'source': 'registration-manual.pdf',
                'category': 'academics'
            },
            {
                'id': 'doc4',
                'title': 'Visa Information',
                'content': 'International students need an F-1 student visa. You must provide proof of acceptance, financial support documents, and complete the DS-160 form. Visa processing takes 2-4 weeks.',
                'source': 'visa-guide.pdf',
                'category': 'international'
            },
            {
                'id': 'doc5',
                'title': 'Housing Options',
                'content': 'On-campus housing is available with meal plans. Off-campus options include apartments near campus. Housing applications open in April for the fall semester. Priority is given to first-year students.',
                'source': 'housing-info.pdf',
                'category': 'housing'
            },
            {
                'id': 'doc6',
                'title': 'Academic Calendar',
                'content': 'Fall semester runs from September to December. Spring semester runs from January to April. Summer sessions are available in June and July. Registration deadlines are posted on the academic calendar.',
                'source': 'academic-calendar.pdf',
                'category': 'academics'
            }
        ]
        logger.info(f"Mock Search Service initialized with {len(self.knowledge_base)} documents")
    
    def search(
        self,
        query: str,
        language: str = "en",
        top: int = 5,
        min_score: float = 0.5
    ) -> List[Dict]:
        """
        Search the mock knowledge base.
        
        Args:
            query: Search query
            language: Language code (ignored in mock)
            top: Number of results to return
            min_score: Minimum relevance score threshold
            
        Returns:
            List of relevant documents
        """
        query_lower = query.lower()
        query_terms = set(re.findall(r'\b\w+\b', query_lower))
        
        results = []
        for doc in self.knowledge_base:
            # Simple keyword matching for mock
            content_lower = doc['content'].lower()
            title_lower = doc.get('title', '').lower()
            
            # Calculate simple relevance score
            content_matches = sum(1 for term in query_terms if term in content_lower)
            title_matches = sum(2 for term in query_terms if term in title_lower)  # Title matches weighted higher
            
            score = (content_matches + title_matches) / max(len(query_terms), 1)
            
            # Normalize score to 0-10 range
            normalized_score = min(score * 3, 10.0)
            
            if normalized_score >= min_score:
                results.append({
                    'content': doc['content'],
                    'title': doc.get('title', ''),
                    'source': doc.get('source', ''),
                    'score': normalized_score,
                    'metadata': {
                        'id': doc.get('id', ''),
                        'category': doc.get('category', '')
                    }
                })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        
        # Return top N results
        results = results[:top]
        
        logger.info(f"Mock search returned {len(results)} results for query: {query[:50]}")
        return results
    
    def add_document(self, document: Dict):
        """Add a document to the mock knowledge base (for testing)."""
        self.knowledge_base.append(document)
        logger.info(f"Added document to mock knowledge base: {document.get('title', 'Untitled')}")
    
    def clear(self):
        """Clear the mock knowledge base (for testing)."""
        self.knowledge_base.clear()
        logger.info("Mock knowledge base cleared")
