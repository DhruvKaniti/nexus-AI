"""Test script for global scan endpoint"""
import httpx
import json
import os

BASE_URL = "http://localhost:8000"

def test_global_scan():
    print("Testing Global Scan Endpoint")
    print("=" * 60)
    
    # Test without NEWSAPI_KEY (should fail gracefully)
    print("\n1. Testing without NEWSAPI_KEY (should return error):")
    print("-" * 60)
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.get(f"{BASE_URL}/api/global-scan?limit=3")
            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Request failed: {e}")
    
    # Test with NEWSAPI_KEY if available
    newsapi_key = os.getenv('NEWSAPI_KEY')
    if newsapi_key:
        print("\n2. Testing with NEWSAPI_KEY (should return live events):")
        print("-" * 60)
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.get(f"{BASE_URL}/api/global-scan?limit=3")
                print(f"Status Code: {response.status_code}")
                data = response.json()
                print(f"Source: {data.get('source')}")
                print(f"Event Count: {data.get('count')}")
                print(f"Timestamp: {data.get('timestamp')}")
                
                if data.get('events'):
                    print(f"\nFirst Event:")
                    print(json.dumps(data['events'][0], indent=2))
        except Exception as e:
            print(f"Request failed: {e}")
    else:
        print("\n2. Skipping NEWSAPI test (NEWSAPI_KEY not set)")
        print("   To test with live news, set NEWSAPI_KEY environment variable")

if __name__ == "__main__":
    test_global_scan()