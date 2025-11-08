#!/usr/bin/env python3
"""
Test Rakuten API connectivity and permissions
Run this to diagnose 403 Forbidden errors
"""

import os
import sys
import requests
from pathlib import Path

# Add src to path
current_dir = Path(__file__).parent
src_path = current_dir / "src"
sys.path.insert(0, str(src_path))

def test_rakuten_api():
    """Test Rakuten API with various configurations"""
    
    print("🔍 Testing Rakuten API Connectivity...")
    print("=" * 50)
    
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("⚠️  python-dotenv not installed, using system environment")
    
    # Get configuration
    api_key = os.getenv('ANTHROPIC_API_KEY')
    base_url = os.getenv('ANTHROPIC_BASE_URL', 'https://api.ai.public.rakuten-it.com/anthropic/')
    model = os.getenv('CLAUDE_MODEL', 'claude-sonnet-4-20250514')
    
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not found in environment")
        print("💡 Create a .env file with your Rakuten API key")
        return False
    
    print(f"🔑 API Key: {api_key[:10]}...{api_key[-4:] if len(api_key) > 14 else api_key}")
    print(f"🌐 Base URL: {base_url}")
    print(f"🤖 Model: {model}")
    print()
    
    # Test different endpoints and auth methods
    endpoints = [
        f"{base_url.rstrip('/')}/v1/chat/completions",
        f"{base_url.rstrip('/')}/chat/completions",
        f"{base_url.rstrip('/')}/completions"
    ]
    
    auth_methods = [
        ("Bearer", {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}),
        ("x-api-key", {"x-api-key": api_key, "Content-Type": "application/json"})
    ]
    
    test_payload = {
        "model": model,
        "max_tokens": 50,
        "temperature": 0.1,
        "messages": [
            {"role": "user", "content": "Hello, can you respond with just 'API working'?"}
        ]
    }
    
    success_found = False
    
    for endpoint in endpoints:
        for auth_name, headers in auth_methods:
            print(f"🧪 Testing: {endpoint}")
            print(f"🔐 Auth: {auth_name}")
            
            try:
                response = requests.post(
                    endpoint,
                    headers=headers,
                    json=test_payload,
                    timeout=10
                )
                
                print(f"📊 Status: {response.status_code}")
                
                if response.status_code == 200:
                    print("✅ SUCCESS! API working correctly")
                    try:
                        result = response.json()
                        if "choices" in result:
                            print(f"💬 Response: {result['choices'][0]['message']['content']}")
                        print(f"📋 Full response: {result}")
                        success_found = True
                        break
                    except Exception as e:
                        print(f"⚠️  JSON parse error: {e}")
                        print(f"📋 Raw response: {response.text}")
                
                elif response.status_code == 401:
                    print("❌ 401 Unauthorized - API key invalid")
                    
                elif response.status_code == 403:
                    print("❌ 403 Forbidden - API key valid but lacks permissions")
                    print(f"📋 Response: {response.text}")
                    try:
                        error_data = response.json()
                        print(f"📋 Error details: {error_data}")
                    except:
                        pass
                        
                elif response.status_code == 404:
                    print("❌ 404 Not Found - Endpoint doesn't exist")
                    
                elif response.status_code == 429:
                    print("❌ 429 Rate Limited - Too many requests")
                    
                else:
                    print(f"❌ Error {response.status_code}: {response.text}")
                    
            except requests.exceptions.Timeout:
                print("⏰ Timeout - API took too long to respond")
            except requests.exceptions.ConnectionError:
                print("🔌 Connection Error - Cannot reach API")
            except Exception as e:
                print(f"💥 Exception: {e}")
            
            print("-" * 30)
        
        if success_found:
            break
    
    if not success_found:
        print("\n🚨 No working configuration found!")
        print("\n🔧 Troubleshooting steps:")
        print("1. Verify your Rakuten API key is correct")
        print("2. Check if your account has Claude model access")
        print("3. Ensure the model name 'claude-sonnet-4-20250514' exists")
        print("4. Check if you have sufficient credits/quota")
        print("5. Contact Rakuten support for API access issues")
        print("\n💡 Try different model names:")
        print("- claude-3-sonnet-20240229")
        print("- claude-3-haiku-20240307")
        print("- claude-2.1")
    
    return success_found

if __name__ == "__main__":
    test_rakuten_api()
