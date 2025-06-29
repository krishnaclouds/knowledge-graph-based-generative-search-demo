#!/usr/bin/env python3
"""
Test script for documents search endpoint
"""
import requests
import json
import sys

def test_documents_endpoint():
    """Test the documents search endpoint"""
    
    url = "http://localhost:8000/documents/search"
    payload = {
        "query": "Apple AI investments 2025",
        "max_results": 3
    }
    
    print("🧪 Testing Documents Search Endpoint")
    print("=" * 50)
    print(f"📡 URL: {url}")
    print(f"📋 Payload: {payload}")
    print()
    
    try:
        print("🔄 Sending request...")
        response = requests.post(url, json=payload, timeout=30)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print("✅ Request successful!")
            print()
            print("📋 Response Structure:")
            print(f"  🔑 Keys: {list(data.keys())}")
            print()
            
            # Check specific fields
            fields_to_check = ['query', 'answer', 'results', 'citations', 'total_found']
            for field in fields_to_check:
                if field in data:
                    if field == 'answer':
                        if data[field]:
                            print(f"  ✅ {field}: Present ({len(data[field])} characters)")
                            print(f"      Preview: {data[field][:100]}...")
                        else:
                            print(f"  ❌ {field}: Empty/None")
                    elif field in ['results', 'citations']:
                        print(f"  📊 {field}: {len(data[field])} items")
                    else:
                        print(f"  📄 {field}: {data[field]}")
                else:
                    print(f"  ❌ {field}: Missing")
            
            # If no answer, check if results have content
            if not data.get('answer') and data.get('results'):
                print()
                print("🔍 Analyzing results for content:")
                for i, result in enumerate(data['results'][:2]):
                    print(f"  📄 Result {i+1}:")
                    print(f"      Content length: {len(result.get('content', ''))}")
                    print(f"      Metadata: {result.get('metadata', {}).get('title', 'No title')}")
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(f"📋 Response: {response.text}")
    
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - backend not running?")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_documents_endpoint()