"""Quick test to verify the RAG system is working with the loaded data."""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.services.vector_store import VectorStore
from app.services.rag_service import RAGService
import asyncio

def test_vector_store():
    """Test that vector store has data."""
    print("=" * 60)
    print("Testing Vector Store")
    print("=" * 60)
    try:
        vs = VectorStore()
        count = vs.count()
        print(f"✓ Vector store has {count} documents")
        if count > 0:
            print("✓ Data is loaded and ready!")
            return True
        else:
            print("✗ Vector store is empty!")
            print("  Run: python scripts/process_handbook.py")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

async def test_rag_query():
    """Test a simple RAG query."""
    print("\n" + "=" * 60)
    print("Testing RAG Query")
    print("=" * 60)
    try:
        rag_service = RAGService()
        print("✓ RAG Service initialized")
        
        query = "What are the enrolment requirements?"
        print(f"\nQuery: {query}")
        print("Processing...")
        
        result = await rag_service.process_query(
            query=query,
            language="en",
            student_id="test_student"
        )
        
        print("\n✓ Query processed successfully!")
        print("\nResponse:")
        print("-" * 60)
        print(result.get("response", "No response"))
        print("-" * 60)
        print(f"\nLanguage: {result.get('language', 'unknown')}")
        print(f"Confidence: {result.get('confidence', 0):.2f}")
        print(f"Sources: {len(result.get('sources', []))} document(s)")
        
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("RAG System Quick Test")
    print("=" * 60)
    print()
    
    # Test vector store
    if not test_vector_store():
        print("\n❌ Vector store test failed. Please process the handbook first.")
        sys.exit(1)
    
    # Test RAG query
    print("\nTesting RAG query (this may take a moment to load the model)...")
    success = asyncio.run(test_rag_query())
    
    if success:
        print("\n" + "=" * 60)
        print("✅ All tests passed! Your RAG system is working!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Start the server: python -m app.main")
        print("2. Open Swagger UI: http://localhost:8000/docs")
        print("3. Test queries in the browser!")
    else:
        print("\n❌ RAG query test failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()
