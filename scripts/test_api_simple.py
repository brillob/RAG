"""Simple script to test the RAG API - run this in a separate terminal while server is running."""
import requests
import json
import sys

def test_health():
    """Test the health endpoint."""
    print("=" * 60)
    print("Testing Health Endpoint")
    print("=" * 60)
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        response.raise_for_status()
        data = response.json()
        print(f"✓ Health check passed!")
        print(f"  Status: {data.get('status', 'unknown')}")
        print(f"  Version: {data.get('version', 'unknown')}")
        return True
    except requests.exceptions.ConnectionError:
        print("✗ ERROR: Cannot connect to server!")
        print("  Make sure the server is running on http://localhost:8000")
        print("  Start it with: python -m app.main")
        return False
    except Exception as e:
        print(f"✗ ERROR: {e}")
        return False

def test_query(query: str = "What are the enrolment requirements?", api_key: str = None):
    """Test a query to the RAG API."""
    print("\n" + "=" * 60)
    print("Testing Query Endpoint")
    print("=" * 60)
    print(f"Query: {query}")
    print()
    
    url = "http://localhost:8000/api/v1/query"
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["X-API-Key"] = api_key
    
    payload = {
        "query": query,
        "language": "auto",
        "student_id": "test_student_001"
    }
    
    try:
        print("Sending request...")
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        print("✓ Query successful!")
        print()
        print("Response:")
        print("-" * 60)
        print(data.get("response", "No response"))
        print("-" * 60)
        print()
        print(f"Language: {data.get('language', 'unknown')}")
        print(f"Confidence: {data.get('confidence', 0):.2f}")
        print(f"Sources: {len(data.get('sources', []))} document(s)")
        if data.get('conversation_id'):
            print(f"Conversation ID: {data.get('conversation_id')}")
        return True
    except requests.exceptions.ConnectionError:
        print("✗ ERROR: Cannot connect to server!")
        print("  Make sure the server is running on http://localhost:8000")
        return False
    except requests.exceptions.HTTPError as e:
        print(f"✗ HTTP Error: {e}")
        if response.status_code == 401:
            print("  Authentication required. Check your API key.")
        try:
            error_data = response.json()
            print(f"  Details: {error_data}")
        except:
            print(f"  Response: {response.text}")
        return False
    except Exception as e:
        print(f"✗ ERROR: {e}")
        return False

def main():
    """Main test function."""
    print("\n" + "=" * 60)
    print("RAG API Test Script")
    print("=" * 60)
    print("\nMake sure the server is running in another terminal!")
    print("Start it with: python -m app.main")
    print()
    
    # Test health
    if not test_health():
        print("\n❌ Health check failed. Please start the server first.")
        sys.exit(1)
    
    # Test query
    query = sys.argv[1] if len(sys.argv) > 1 else "What are the enrolment requirements?"
    test_query(query)
    
    print("\n" + "=" * 60)
    print("Test Complete!")
    print("=" * 60)
    print("\n💡 Tip: Open http://localhost:8000/docs in your browser")
    print("   for an interactive Swagger UI to test the API.")
    print()

if __name__ == "__main__":
    main()
