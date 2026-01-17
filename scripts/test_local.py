"""Local testing script for the RAG API."""
import requests
import json
import sys
from typing import Dict, Optional


def test_query(
    base_url: str = "http://localhost:8000",
    query: str = "What are the admission requirements?",
    api_key: Optional[str] = None,
    language: Optional[str] = None
) -> Dict:
    """Test the query endpoint."""
    url = f"{base_url}/api/v1/query"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    if api_key:
        headers["X-API-Key"] = api_key
    
    payload = {
        "query": query,
        "language": language or "auto"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        return {}


def test_health(base_url: str = "http://localhost:8000") -> bool:
    """Test the health endpoint."""
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        response.raise_for_status()
        print(f"Health check: {response.json()}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Health check failed: {e}")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test the RAG API locally")
    parser.add_argument("--url", default="http://localhost:8000", help="API base URL")
    parser.add_argument("--query", default="What are the admission requirements?", help="Query to test")
    parser.add_argument("--api-key", help="API key for authentication")
    parser.add_argument("--language", help="Language code (or 'auto')")
    
    args = parser.parse_args()
    
    print("Testing RAG Student Support API...")
    print("-" * 50)
    
    # Test health
    print("\n1. Testing health endpoint...")
    if not test_health(args.url):
        print("Health check failed. Is the server running?")
        sys.exit(1)
    
    # Test query
    print(f"\n2. Testing query endpoint...")
    print(f"Query: {args.query}")
    result = test_query(
        base_url=args.url,
        query=args.query,
        api_key=args.api_key,
        language=args.language
    )
    
    if result:
        print("\nResponse:")
        print(json.dumps(result, indent=2))
    else:
        print("Query test failed.")
        sys.exit(1)
    
    print("\n" + "-" * 50)
    print("Tests completed!")
