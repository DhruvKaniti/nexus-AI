import httpx
import json

try:
    with httpx.Client(timeout=30.0) as client:
        # Try different GDELT API endpoints
        endpoints = [
            ("https://api.gdeltproject.org/api/v2/doc/query", {"query": "sort:Date desc", "mode": "artlist", "maxrecords": "5", "format": "json", "trans": "googtrans"}),
            ("https://api.gdeltproject.org/api/v2/events/query", {"query": "sort:Date desc", "mode": "artlist", "maxrecords": "5", "format": "json", "trans": "googtrans"}),
            ("https://api.gdeltproject.org/api/v2/doc/doc", {"query": "sort:Date desc", "mode": "artlist", "maxrecords": "5", "format": "json"}),
        ]
        
        print("Testing GDELT API endpoints...")
        for url, params in endpoints:
            print(f"\n{'='*60}")
            print(f"Testing: {url}")
            print(f"{'='*60}")
            response = client.get(url, params=params)
            print(f"Status Code: {response.status_code}")
            print(f"Response Body (first 500 chars):")
            print(response.text[:500])
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"\n\nParsed JSON structure:")
                print(f"Keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                if isinstance(data, dict) and "articles" in data:
                    print(f"Number of articles: {len(data['articles'])}")
                    if data['articles']:
                        print(f"\nFirst article keys: {list(data['articles'][0].keys())}")
                        print(f"\nFirst article sample:")
                        print(json.dumps(data['articles'][0], indent=2)[:1000])
            except Exception as e:
                print(f"\nFailed to parse JSON: {e}")
                
except Exception as e:
    print(f"Request failed: {e}")