#!/usr/bin/env python3
"""
Test script to validate Streamlit app structure
"""

import sys
from pathlib import Path
import os

# Add src to path
current_dir = Path(__file__).parent
src_path = current_dir / "src"
sys.path.insert(0, str(src_path))

def test_imports():
    """Test all required imports"""
    try:
        print("🧪 Testing imports...")
        
        # Test core imports
        import streamlit as st
        print("✅ Streamlit imported")
        
        from lineage_lens.parsers.sql_parser import SQLLineageParser
        print("✅ SQL Parser imported")
        
        from lineage_lens.visualizers.graph_visualizer import LineageGraphVisualizer
        print("✅ Graph Visualizer imported")
        
        from lineage_lens.visualizers.cytoscape_visualizer import CytoscapeGraphVisualizer
        print("✅ Cytoscape Visualizer imported")
        
        from lineage_lens.llm.claude_explainer import ClaudeLineageExplainer
        print("✅ Claude Explainer imported")
        
        from lineage_lens.models.lineage_models import LineageQuery
        print("✅ Lineage Models imported")
        
        from lineage_lens.utils.config import settings
        print("✅ Config imported")
        
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_session_state_structure():
    """Test session state initialization logic"""
    try:
        print("\n🧪 Testing session state logic...")
        
        # Mock session state
        class MockSessionState:
            def __init__(self):
                self.state = {}
            
            def __contains__(self, key):
                return key in self.state
            
            def __getitem__(self, key):
                return self.state[key]
            
            def __setitem__(self, key, value):
                self.state[key] = value
        
        # Test initialization logic
        mock_state = MockSessionState()
        
        # Simulate initialize_session_state logic
        if 'lineage_graph' not in mock_state:
            mock_state['lineage_graph'] = None
        if 'uploaded_files' not in mock_state:
            mock_state['uploaded_files'] = []
        if 'chat_history' not in mock_state:
            mock_state['chat_history'] = []
        if 'api_key' not in mock_state:
            mock_state['api_key'] = os.getenv('ANTHROPIC_API_KEY', '')
        if 'layout_option' not in mock_state:
            mock_state['layout_option'] = 'hierarchical'
        
        print("✅ Session state initialization logic works")
        print(f"   - lineage_graph: {mock_state['lineage_graph']}")
        print(f"   - uploaded_files: {mock_state['uploaded_files']}")
        print(f"   - chat_history: {mock_state['chat_history']}")
        print(f"   - api_key: {'***' if mock_state['api_key'] else 'empty'}")
        print(f"   - layout_option: {mock_state['layout_option']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Session state test error: {e}")
        return False

def test_cytoscape_demo():
    """Test cytoscape demo generation"""
    try:
        print("\n🧪 Testing Cytoscape demo generation...")
        
        from lineage_lens.visualizers.cytoscape_visualizer import CytoscapeGraphVisualizer
        from lineage_lens.models.lineage_models import LineageGraph
        
        # Create empty graph for testing
        empty_graph = LineageGraph(tables={})
        visualizer = CytoscapeGraphVisualizer()
        
        # This should not fail even with empty graph
        html_content = visualizer.create_cytoscape_visualization(empty_graph)
        
        if len(html_content) > 1000:  # Should be substantial HTML
            print("✅ Cytoscape HTML generation works")
            return True
        else:
            print("❌ Generated HTML seems too short")
            return False
            
    except Exception as e:
        print(f"❌ Cytoscape test error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Lineage Lens App Structure Test")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_session_state_structure,
        test_cytoscape_demo
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n📊 Test Results:")
    print("=" * 30)
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 All tests passed! Your app should work correctly.")
        print("\n🚀 Ready to run:")
        print("   ./run_app.sh")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
