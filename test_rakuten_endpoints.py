#!/usr/bin/env python3
"""
Test script to discover the correct Rakuten API endpoint
"""

import requests
import os
import sys
from pathlib import Path

# Add src to path
current_dir = Path(__file__).parent
src_path = current_dir / "src"
sys.path.insert(0, str(src_path))

def test_rakuten_endpoints():
    """Test different Rakuten API endpoints to find the correct one"""
    
    try:
        from src.lineage_lens.utils.config import settings
        base_url = settings.anthropic_base_url
        api_key = settings.anthropic_api_key
    except:
        base_url = os.getenv('ANTHROPIC_BASE_URL')
        api_key = os.getenv('ANTHROPIC_API_KEY')
    
    if not base_url or not api_key:
        print("❌ Missing base URL or API key")
        return
        
    print(f"🔍 Testing Rakuten API endpoints at: {base_url}")
    print(f"🔑 API Key: {api_key[:20]}..." if len(api_key) > 20 else f"🔑 API Key: {api_key}")
    print()
    
    # Test different endpoint combinations
    endpoints_to_test = [
        "",  # Base URL only
        "/",
        "/v1",
        "/v1/",
        "/v1/messages",
        "/v1/chat/completions", 
        "/messages",
        "/chat/completions",
        "/anthropic/v1/messages",
        "/anthropic/messages",
        "/claude/v1/messages",
        "/claude/messages",
        "/api/v1/messages",
        "/api/messages"
    ]
    
    auth_methods = [
        {"x-api-key": api_key},
        {"Authorization": f"Bearer {api_key}"},
        {"Authorization": f"Api-Key {api_key}"}
    ]
    
    # Simple test payload
    test_payload = {
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 10,
        "messages": [{"role": "user", "content": "Hi"}]
    }
    
    working_endpoints = []
    
    print("🧪 Testing endpoints...")
    for endpoint_path in endpoints_to_test:
        full_url = f"{base_url.rstrip('/')}{endpoint_path}"
        
        for i, auth_headers in enumerate(auth_methods):
            auth_name = list(auth_headers.keys())[0]
            headers = {**auth_headers, "Content-Type": "application/json"}
            
            try:
                response = requests.post(
                    full_url,
                    headers=headers,
                    json=test_payload,
                    timeout=10
                )
                
                status_emoji = "✅" if response.status_code == 200 else "⚠️" if response.status_code in [400, 401, 403] else "❌"
                print(f"{status_emoji} {full_url} [{auth_name}] → {response.status_code}")
                
                if response.status_code == 200:
                    working_endpoints.append((full_url, auth_name))
                elif response.status_code in [400, 401, 403]:
                    # These might be authentication/parameter issues, not endpoint issues
                    print(f"   💡 Endpoint exists but auth/params may need adjustment")
                    
            except requests.exceptions.RequestException as e:
                print(f"❌ {full_url} [{auth_name}] → Connection Error: {str(e)[:50]}...")
    
    print(f"\n📊 Results:")
    if working_endpoints:
        print("✅ Working endpoints found:")
        for url, auth in working_endpoints:
            print(f"   {url} with {auth}")
    else:
        print("❌ No working endpoints found")
        print("\n💡 Try these manual tests:")
        print(f"   curl -X GET {base_url}")
        print(f"   curl -X GET {base_url}/v1")
        print(f"   curl -H 'x-api-key: {api_key}' {base_url}/v1/messages")

if __name__ == "__main__":
    test_rakuten_endpoints()
