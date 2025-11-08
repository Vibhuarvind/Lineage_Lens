#!/bin/bash

# Lineage Lens - Startup Script
echo "🚀 Starting Lineage Lens..."

# Check if we're in the right directory
if [ ! -f "streamlit_app.py" ]; then
    echo "❌ Error: streamlit_app.py not found!"
    echo "Please run this script from the code directory"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ] && [ ! -d ".venv" ]; then
    echo "⚠️ No virtual environment found. Creating one..."
    python3 -m venv venv
    source venv/bin/activate
    echo "📦 Installing requirements..."
    pip install -r requirements.txt
else
    # Activate existing virtual environment
    if [ -d "venv" ]; then
        source venv/bin/activate
    else
        source .venv/bin/activate
    fi
    echo "✅ Virtual environment activated"
fi

# Check if sample data exists
if [ ! -f "data/sample_lineage.sql" ]; then
    echo "📁 Sample data not found, but that's okay - you can upload your own SQL files!"
fi

echo ""
echo "🔍 Lineage Lens - Intelligent Data Lineage Analysis Platform"
echo "============================================================"
echo ""
echo "🌐 The app will open in your browser at: http://localhost:8501"
echo ""
echo "📋 Quick Start:"
echo "1. 🔑 Enter your API key in the sidebar (or set ANTHROPIC_API_KEY env var)"
echo "2. 📁 Upload your SQL files using the file uploader"
echo "3. 🔍 Click 'Analyze Lineage' to extract dependencies"
echo "4. 📊 View the interactive visualization"
echo "5. 💬 Ask questions about your data flow"
echo ""
echo "🎨 Visualization Options:"
echo "- Simple & Reliable (SVG): Fast, works offline, perfect for demos"
echo "- Professional (Cytoscape.js): Interactive, enterprise-grade"
echo "- Classic (Plotly): Traditional network graph"
echo ""
echo "🛑 Press Ctrl+C to stop the application"
echo ""

# Start Streamlit
streamlit run streamlit_app.py --server.port 8501 --server.address localhost