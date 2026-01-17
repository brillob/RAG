"""Main FastAPI application for the RAG student support system."""
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import uvicorn
from typing import Optional

from app.config import settings
from app.models import QueryRequest, QueryResponse, HealthResponse
from app.services.rag_service import RAGService
from app.openapi_tags import tags_metadata

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app with enhanced Swagger documentation
app = FastAPI(
    title="Multilingual RAG Student Support API",
    description="""
    ## ICL Student Support RAG System API
    
    A production-ready Retrieval-Augmented Generation (RAG) system for handling 
    high-volume student inquiries via WhatsApp, integrated with n8n workflow automation.
    
    ### Features
    
    * **Multilingual Support**: Automatically detects and responds in the student's native language
    * **Conversation Memory**: Handles follow-up questions with conversation context
    * **Vector Search**: Semantic search using ChromaDB (local) or Azure AI Search (production)
    * **Guardrails**: Built-in protection against hallucination
    * **Real-time Processing**: Fast response generation
    
    ### Knowledge Base
    
    Uses the **ICL Student Support Services Handbook** (February 2022) as the knowledge base.
    
    ### Authentication
    
    API key authentication is optional. Set `API_KEY` in environment variables to enable.
    Send API key in header: `X-API-Key: your-api-key`
    
    ### Getting Started
    
    1. Process the handbook: `python scripts/process_handbook.py`
    2. Start the server: `python -m app.main`
    3. Access Swagger UI: http://localhost:8000/docs
    4. Test the API using the interactive interface below
    
    ### API Documentation
    
    - **Swagger UI**: http://localhost:8000/docs (interactive testing)
    - **ReDoc**: http://localhost:8000/redoc (alternative documentation)
    - **OpenAPI JSON**: http://localhost:8000/openapi.json
    """,
    version="1.0.0",
    terms_of_service="https://icl.ac.nz/",
    contact={
        "name": "ICL Student Support",
        "email": "studentsupport@icl.ac.nz",
        "url": "https://icl.ac.nz"
    },
    license_info={
        "name": "Proprietary",
    },
    servers=[
        {
            "url": "http://localhost:8000",
            "description": "Local development server"
        },
        {
            "url": "https://api.example.com",
            "description": "Production server (example)"
        }
    ],
    openapi_tags=tags_metadata,
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware for n8n integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG service
rag_service = RAGService()


def verify_api_key(x_api_key: Optional[str] = Header(None)) -> bool:
    """Verify API key for authentication."""
    if not settings.api_key:
        # If no API key configured, allow all requests (development mode)
        return True
    
    if not x_api_key or x_api_key != settings.api_key:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key"
        )
    return True


@app.get(
    "/health",
    tags=["Monitoring"],
    summary="Health Check",
    description="Check if the API service is running and healthy.",
    response_description="Service health status"
)
async def health_check():
    """
    Health check endpoint for monitoring.
    
    Returns the current health status of the API service.
    Useful for:
    - Load balancer health checks
    - Monitoring systems
    - Container orchestration (Kubernetes liveness/readiness probes)
    """
    health_data = {
        "status": "healthy",
        "version": "1.0.0"
    }
    
    # Add LLM health status if in local mode
    if settings.is_local_mode() and hasattr(rag_service, 'local_llm'):
        try:
            if hasattr(rag_service.local_llm, 'health_check'):
                llm_health = await rag_service.local_llm.health_check()
                health_data["llm"] = llm_health
            else:
                health_data["llm"] = {"status": "mock", "provider": "mock_openai"}
        except Exception as e:
            health_data["llm"] = {"status": "error", "error": str(e)}
    
    return health_data


@app.post(
    "/api/v1/query",
    response_model=QueryResponse,
    tags=["Student Queries"],
    summary="Process Student Query",
    description="""
    Process a student inquiry and return a multilingual response using RAG.
    
    ### How it works:
    
    1. **Language Detection**: Automatically detects query language (if not specified)
    2. **Conversation Context**: Retrieves previous conversation history (if conversation_id provided)
    3. **Vector Search**: Searches the ICL Student Handbook for relevant information
    4. **Response Generation**: Generates answer using AI with guardrails
    5. **Memory Storage**: Stores Q&A in conversation memory for follow-ups
    
    ### Follow-up Questions:
    
    To ask follow-up questions, include the `conversation_id` from the previous response.
    The system will use conversation history to understand context.
    
    ### Example Flow:
    
    1. First question: `{"query": "What are the enrolment requirements?"}`
    2. Response includes: `"conversation_id": "abc-123-def-456"`
    3. Follow-up: `{"query": "Do I need insurance?", "conversation_id": "abc-123-def-456"}`
    """,
    response_description="AI-generated response with metadata",
    responses={
        200: {
            "description": "Successful response",
            "content": {
                "application/json": {
                    "example": {
                        "response": "To enroll in ICL Graduate Business Programmes, both domestic and international students are required to have a valid visa, suitable travel/medical insurance, and enough funds for onward travel.",
                        "language": "en",
                        "confidence": 0.95,
                        "sources": ["chunk_1", "chunk_2"],
                        "query_id": "550e8400-e29b-41d4-a716-446655440000",
                        "conversation_id": "abc-123-def-456"
                    }
                }
            }
        },
        401: {
            "description": "Unauthorized - Invalid or missing API key",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Invalid or missing API key"
                    }
                }
            }
        },
        422: {
            "description": "Validation error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["body", "query"],
                                "msg": "field required",
                                "type": "value_error.missing"
                            }
                        ]
                    }
                }
            }
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Internal server error: Error message"
                    }
                }
            }
        }
    }
)
async def process_query(
    request: QueryRequest,
    _: bool = Depends(verify_api_key)
):
    """
    Process a student inquiry and return a multilingual response.
    
    This endpoint:
    - Detects the language of the query (if not specified)
    - Searches the knowledge base using vector search (local) or Azure AI Search (production)
    - Generates a response using AI with guardrails
    - Returns the response in the student's language
    - Manages conversation memory for follow-up questions
    """
    try:
        logger.info(f"Processing query: {request.query[:100]}...")
        
        result = await rag_service.process_query(
            query=request.query,
            language=request.language,
            student_id=request.student_id,
            conversation_id=request.conversation_id
        )
        
        # Validate confidence score
        if result["confidence"] < settings.min_confidence_score:
            logger.warning(
                f"Low confidence response: {result['confidence']} "
                f"(threshold: {settings.min_confidence_score})"
            )
        
        return QueryResponse(**result)
        
    except Exception as e:
        logger.error(f"Error processing query: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.get(
    "/",
    tags=["Information"],
    summary="API Information",
    description="Get basic information about the API service and available endpoints."
)
async def root():
    """
    Root endpoint with API information.
    
    Returns service name, version, status, and available endpoints.
    """
    return {
        "service": "Multilingual RAG Student Support API",
        "version": "1.0.0",
        "status": "operational",
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc",
            "openapi_json": "/openapi.json"
        },
        "endpoints": {
            "health": "/health",
            "query": "/api/v1/query"
        },
        "knowledge_base": "ICL Student Support Services Handbook (February 2022)",
        "features": [
            "Multilingual support (12+ languages)",
            "Conversation memory for follow-ups",
            "Vector-based semantic search",
            "Hallucination prevention guardrails"
        ]
    }


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.lower()
    )
