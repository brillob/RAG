#!/usr/bin/env python3
"""Debug script for RAG service - fixes Python path issues."""
import sys
from pathlib import Path

# Add project root to Python path BEFORE importing app modules
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Now we can import app modules
import logging
import asyncio
from app.config import settings
from app.services.rag_service import RAGService

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def debug_rag_service():
    """Debug the RAG service."""
    print("=" * 60)
    print("Debugging RAG Service")
    print("=" * 60)
    
    # Initialize RAG service
    print("\n1. Initializing RAG Service...")
    rag = RAGService()
    print(f"   ✓ Mode: {'local' if rag.is_local else 'azure'}")
    
    # Test query
    print("\n2. Testing query processing...")
    print("   Query: 'What are the enrolment requirements?'")
    
    # Add breakpoint here if needed
    # breakpoint()  # Uncomment to add breakpoint
    
    result = await rag.process_query(
        query="What are the enrolment requirements?",
        language="en",
        student_id="debug_test"
    )
    
    print("\n3. Results:")
    print(f"   Response: {result.get('response', '')[:200]}...")
    print(f"   Language: {result.get('language')}")
    print(f"   Confidence: {result.get('confidence')}")
    print(f"   Sources: {len(result.get('sources', []))}")
    
    print("\n" + "=" * 60)
    print("Debug complete!")
    print("=" * 60)
    
    return result


if __name__ == "__main__":
    # Run the debug function
    asyncio.run(debug_rag_service())
