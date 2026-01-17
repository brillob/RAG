"""In-memory mock OpenAI service for local testing."""
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class MockOpenAIService:
    """Mock OpenAI service for local testing without API calls."""
    
    def __init__(self):
        """Initialize mock service."""
        logger.info("Mock OpenAI Service initialized")
    
    async def generate_response(
        self,
        prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.3
    ) -> str:
        """
        Generate a mock response based on the prompt.
        
        Args:
            prompt: The prompt to generate a response for
            max_tokens: Maximum tokens (ignored in mock)
            temperature: Temperature setting (ignored in mock)
            
        Returns:
            Mock response text
        """
        # Extract query from prompt
        query = self._extract_query_from_prompt(prompt)
        context = self._extract_context_from_prompt(prompt)
        
        # Simple rule-based response generation for testing
        if not context or len(context.strip()) < 50:
            return "I don't have enough information to answer that question. Please contact our support team for assistance."
        
        # Generate a simple response based on context
        response = f"Based on the information available: {query}\n\n"
        response += "Here's what I found in our knowledge base:\n\n"
        
        # Extract key information from context
        if "admission" in query.lower() or "requirements" in query.lower():
            response += "The admission requirements include a high school diploma or equivalent, minimum GPA, and English proficiency test scores. Please check the specific requirements for your program."
        elif "tuition" in query.lower() or "fee" in query.lower() or "cost" in query.lower():
            response += "Tuition and fees vary by program. Annual tuition for undergraduate programs is approximately $15,000. Additional fees apply. Financial aid options are available."
        elif "visa" in query.lower() or "international" in query.lower():
            response += "International students need an F-1 student visa. You'll need proof of acceptance, financial support documents, and must complete the DS-160 form. Processing typically takes 2-4 weeks."
        elif "housing" in query.lower() or "accommodation" in query.lower():
            response += "Both on-campus and off-campus housing options are available. On-campus housing includes meal plans. Applications open in April for the fall semester."
        elif "registration" in query.lower() or "course" in query.lower():
            response += "Course registration opens two weeks before each semester. You can register online through the student portal. Make sure prerequisites are completed."
        else:
            # Generic response based on context
            response += "I found relevant information in our knowledge base. " + context[:200] + "..."
        
        response += "\n\nIf you need more specific information, please contact our support team."
        
        # Limit response length
        if len(response) > max_tokens:
            response = response[:max_tokens] + "..."
        
        logger.info(f"Mock OpenAI generated response (length: {len(response)})")
        return response.strip()
    
    def _extract_query_from_prompt(self, prompt: str) -> str:
        """Extract the student's query from the prompt."""
        if "Student's question:" in prompt:
            parts = prompt.split("Student's question:")
            if len(parts) > 1:
                query_part = parts[1].split("\n")[0].strip()
                return query_part
        return "student question"
    
    def _extract_context_from_prompt(self, prompt: str) -> str:
        """Extract context from the prompt."""
        if "Context from knowledge base:" in prompt:
            parts = prompt.split("Context from knowledge base:")
            if len(parts) > 1:
                context_part = parts[1].split("Student's question:")[0].strip()
                return context_part
        return ""
