#!/usr/bin/env python3
"""
Debug script to check configuration issues
"""

import os
import sys
from pathlib import Path

# Add src to path
current_dir = Path(__file__).parent
src_path = current_dir / "src"
sys.path.insert(0, str(src_path))

def check_environment():
    """Check environment variables"""
    print("🔍 Environment Variables:")
    print(f"ANTHROPIC_API_KEY: {'Set' if os.getenv('ANTHROPIC_API_KEY') else 'Not set'}")
    print(f"ANTHROPIC_BASE_URL: {os.getenv('ANTHROPIC_BASE_URL', 'Not set')}")
    print(f"CLAUDE_MODEL: {os.getenv('CLAUDE_MODEL', 'Not set')}")
    print(f"CLAUDE_TEMPERATURE: {os.getenv('CLAUDE_TEMPERATURE', 'Not set')}")
    print()

def test_claude_explainer():
    """Test ClaudeLineageExplainer initialization"""
    try:
        print("🧪 Testing ClaudeLineageExplainer...")
        from src.lineage_lens.llm.claude_explainer import ClaudeLineageExplainer
        
        explainer = ClaudeLineageExplainer()
        print(f"✅ ClaudeLineageExplainer initialized")
        print(f"   API Key: {'Set' if explainer.api_key else 'Not set'}")
        print(f"   Base URL: {explainer.base_url or 'Not set'}")
        print(f"   Model: {explainer.model_name}")
        print(f"   Temperature: {explainer.temperature}")
        print(f"   Is Rakuten API: {explainer.is_rakuten_api}")
        return True
    except Exception as e:
        print(f"❌ ClaudeLineageExplainer error: {e}")
        return False

def test_config():
    """Test config import"""
    try:
        print("🧪 Testing config import...")
        from src.lineage_lens.utils.config import settings
        print(f"✅ Config imported successfully")
        print(f"   API Key: {'Set' if settings.anthropic_api_key else 'Not set'}")
        print(f"   Base URL: {settings.anthropic_base_url or 'Not set'}")
        print(f"   Model: {settings.claude_model}")
        print(f"   Temperature: {settings.claude_temperature}")
        return True
    except Exception as e:
        print(f"❌ Config error: {e}")
        return False

def main():
    print("🚀 Configuration Debug Script")
    print("=" * 40)
    
    check_environment()
    
    config_ok = test_config()
    explainer_ok = test_claude_explainer()
    
    print("\n📊 Summary:")
    print(f"Config: {'✅' if config_ok else '❌'}")
    print(f"ClaudeExplainer: {'✅' if explainer_ok else '❌'}")
    
    if not config_ok or not explainer_ok:
        print("\n💡 Suggestions:")
        print("1. Check your .env file exists")
        print("2. Verify ANTHROPIC_API_KEY is set")
        print("3. Set ANTHROPIC_BASE_URL for Rakuten API")
        print("4. Check file paths and imports")

if __name__ == "__main__":
    main()
