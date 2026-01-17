#!/usr/bin/env python3
"""Debug script for API testing with extended timeouts."""
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import requests
from app.config import settings

# Set debug timeout
DEBUG_TIMEOUT = 120  # 2 minutes for debug mode

def test_health(base_url: str = "http://localhost:8000"):
    """Test health endpoint."""
    print(f"Testing health endpoint at {base_url}/health...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        response.raise_for_status()
        print(f"✓ Health check passed: {response.json()}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"✗ Health check failed: {e}")
        return False

def test_query(
    base_url: str = "http://localhost:8000",
    query: str = "What are the enrolment requirements?",
    api_key: str = None
):
    """Test query endpoint with debug timeout."""
    url = f"{base_url}/api/v1/query"
    
    payload = {
        "query": query
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    if api_key:
        headers["X-API-Key"] = api_key
    
    print(f"\nTesting query endpoint...")
    print(f"URL: {url}")
    print(f"Query: {query}")
    print(f"Timeout: {DEBUG_TIMEOUT} seconds (debug mode)")
    
    try:
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=DEBUG_TIMEOUT  # 120 seconds for debug
        )
        response.raise_for_status()
        
        result = response.json()
        print(f"\n✓ Query successful!")
        print(f"Response: {result.get('response', '')[:200]}...")
        print(f"Language: {result.get('language')}")
        print(f"Confidence: {result.get('confidence')}")
        print(f"Sources: {len(result.get('sources', []))}")
        
        return result
    except requests.exceptions.Timeout:
        print(f"\n✗ Request timed out after {DEBUG_TIMEOUT} seconds")
        print("   The LLM might be taking too long. Check:")
        print("   1. Is Ollama running? (ollama list)")
        print("   2. Is the model loaded? (first request can be slow)")
        print("   3. Check server logs for errors")
        return None
    except requests.exceptions.RequestException as e:
        print(f"\n✗ Request failed: {e}")
        return None

def main():
    """Run debug API tests."""
    print("=" * 60)
    print("API Debug Test (120 second timeout)")
    print("=" * 60)
    
    base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
    api_key = os.getenv("API_KEY")
    
    # Test health
    if not test_health(base_url):
        print("\n⚠ Server might not be running. Start it with:")
        print("   python -m app.main")
        return
    
    # Test query
    result = test_query(
        base_url=base_url,
        query="What are the enrolment requirements?",
        api_key=api_key
    )
    
    if result:
        print("\n" + "=" * 60)
        print("✅ Debug test completed successfully!")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ Debug test failed. Check errors above.")
        print("=" * 60)

if __name__ == "__main__":
    main()
