"""OpenAPI tags configuration for Swagger UI."""
from typing import List
from fastapi.openapi.utils import get_openapi

# Define tags metadata for better Swagger UI organization
tags_metadata = [
    {
        "name": "Student Queries",
        "description": """
        Endpoints for processing student inquiries.
        
        These endpoints handle:
        - Student questions and queries
        - Multilingual support
        - Conversation management
        - RAG-based responses
        """,
        "externalDocs": {
            "description": "API Documentation",
            "url": "https://icl.ac.nz/",
        },
    },
    {
        "name": "Monitoring",
        "description": "Health check and monitoring endpoints for system status.",
    },
    {
        "name": "Information",
        "description": "General API information and documentation endpoints.",
    },
]
