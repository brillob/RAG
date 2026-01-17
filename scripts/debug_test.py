#!/usr/bin/env python3
"""Quick debugging script to test RAG system components."""
import sys
import asyncio
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Enable debug logging and set timeout
os.environ["LOG_LEVEL"] = "DEBUG"
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Debug timeout setting
DEBUG_TIMEOUT = 120  # 2 minutes for debug mode

logger = logging.getLogger(__name__)


def test_config():
    """Test configuration loading."""
    print("\n" + "=" * 60)
    print("Testing Configuration")
    print("=" * 60)
    try:
        from app.config import settings
        
        print(f"✓ Mode: {settings.mode}")
        print(f"✓ Log Level: {settings.log_level}")
        print(f"✓ LLM Provider: {settings.local_llm_provider}")
        print(f"✓ LLM Model: {settings.local_llm_model}")
        print(f"✓ Vector DB Path: {settings.vector_db_path}")
        print(f"✓ Chunking Strategy: {settings.chunking_strategy}")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_vector_store():
    """Test vector store."""
    print("\n" + "=" * 60)
    print("Testing Vector Store")
    print("=" * 60)
    try:
        from app.services.vector_store import VectorStore
        
        vs = VectorStore()
        count = vs.count()
        print(f"✓ Vector store initialized")
        print(f"✓ Documents in store: {count}")
        
        if count == 0:
            print("⚠ Warning: Vector store is empty!")
            print("  Run: python scripts/process_handbook.py")
            return False
        
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_embeddings():
    """Test embedding service."""
    print("\n" + "=" * 60)
    print("Testing Embeddings")
    print("=" * 60)
    try:
        from app.services.embeddings import EmbeddingService
        
        emb = EmbeddingService()
        test_text = "What are the enrolment requirements?"
        embedding = emb.generate_embedding(test_text)
        
        print(f"✓ Embedding service initialized")
        print(f"✓ Model: {emb.model_name}")
        print(f"✓ Embedding shape: {embedding.shape}")
        print(f"✓ Sample values: {embedding[:5]}")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_local_llm():
    """Test local LLM service."""
    print("\n" + "=" * 60)
    print("Testing Local LLM")
    print("=" * 60)
    try:
        from app.services.local_llm import LocalLLMService
        from app.config import settings
        
        llm = LocalLLMService(
            provider=settings.local_llm_provider,
            model_name=settings.local_llm_model,
            base_url=settings.local_llm_base_url,
            use_gpu=settings.local_llm_use_gpu
        )
        
        print(f"✓ LLM service initialized")
        print(f"✓ Provider: {llm.provider}")
        print(f"✓ Model: {llm.model_name}")
        
        # Health check
        health = await llm.health_check()
        print(f"✓ Health check: {health}")
        
        if health.get("status") != "healthy":
            print("⚠ Warning: LLM service may not be ready")
            return False
        
        # Test generation
        print("\nTesting generation...")
        response = await llm.generate_response(
            prompt="Hello, how are you?",
            max_tokens=50,
            temperature=0.3
        )
        print(f"✓ Generated response: {response[:100]}...")
        
        await llm.close()
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_rag_service():
    """Test RAG service."""
    print("\n" + "=" * 60)
    print("Testing RAG Service")
    print("=" * 60)
    try:
        from app.services.rag_service import RAGService
        
        rag = RAGService()
        print(f"✓ RAG service initialized")
        print(f"✓ Mode: {'local' if rag.is_local else 'azure'}")
        
        # Test query
        print("\nTesting query processing...")
        result = await rag.process_query(
            query="What are the enrolment requirements?",
            language="en",
            student_id="debug_test"
        )
        
        print(f"✓ Query processed")
        print(f"✓ Response: {result.get('response', '')[:200]}...")
        print(f"✓ Language: {result.get('language')}")
        print(f"✓ Confidence: {result.get('confidence')}")
        print(f"✓ Sources: {len(result.get('sources', []))}")
        
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all debug tests."""
    print("\n" + "=" * 60)
    print("RAG System Debug Test")
    print("=" * 60)
    print()
    
    results = []
    
    # Test configuration
    results.append(("Configuration", test_config()))
    
    # Test vector store
    results.append(("Vector Store", test_vector_store()))
    
    # Test embeddings
    results.append(("Embeddings", test_embeddings()))
    
    # Test local LLM
    results.append(("Local LLM", await test_local_llm()))
    
    # Test RAG service
    results.append(("RAG Service", await test_rag_service()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {name}")
    
    all_passed = all(result[1] for result in results)
    if all_passed:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed. Check errors above.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
