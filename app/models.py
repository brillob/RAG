"""Data models for API requests and responses."""
from pydantic import BaseModel, Field
from typing import Optional, List


class QueryRequest(BaseModel):
    """Request model for student inquiry."""
    query: str = Field(
        ...,
        description="The student's question",
        min_length=1,
        max_length=2000,
        example="What are the enrolment requirements?"
    )
    student_id: Optional[str] = Field(
        None,
        description="Optional student identifier for tracking",
        example="student123"
    )
    language: Optional[str] = Field(
        "auto",
        description="Language code (e.g., 'en', 'es', 'fr') or 'auto' for automatic detection",
        example="auto"
    )
    conversation_id: Optional[str] = Field(
        None,
        description="Conversation ID from previous response for follow-up questions. Leave empty for new conversations.",
        example="abc-123-def-456"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "What are the enrolment requirements?",
                "student_id": "student123",
                "language": "auto",
                "conversation_id": None
            }
        }


class QueryResponse(BaseModel):
    """Response model for student inquiry."""
    response: str = Field(
        ...,
        description="The AI-generated response based on the knowledge base",
        example="To enroll in ICL Graduate Business Programmes, both domestic and international students are required to have a valid visa, suitable travel/medical insurance, and enough funds for onward travel."
    )
    language: str = Field(
        ...,
        description="Detected or used language code (e.g., 'en', 'es', 'fr')",
        example="en"
    )
    confidence: float = Field(
        ...,
        description="Confidence score indicating how confident the system is in the response (0.0 to 1.0)",
        ge=0.0,
        le=1.0,
        example=0.95
    )
    sources: List[str] = Field(
        default_factory=list,
        description="List of source document/chunk IDs used to generate the response",
        example=["chunk_1", "chunk_2"]
    )
    query_id: Optional[str] = Field(
        None,
        description="Unique identifier for this query",
        example="550e8400-e29b-41d4-a716-446655440000"
    )
    conversation_id: Optional[str] = Field(
        None,
        description="Conversation ID for this session. Use this in follow-up questions to maintain context.",
        example="abc-123-def-456"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "response": "To enroll in ICL Graduate Business Programmes, both domestic and international students are required to have a valid visa, suitable travel/medical insurance, and enough funds for onward travel.",
                "language": "en",
                "confidence": 0.95,
                "sources": ["chunk_1", "chunk_2"],
                "query_id": "550e8400-e29b-41d4-a716-446655440000",
                "conversation_id": "abc-123-def-456"
            }
        }


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(
        default="healthy",
        description="Service health status",
        example="healthy"
    )
    version: str = Field(
        default="1.0.0",
        description="API version",
        example="1.0.0"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "1.0.0"
            }
        }
