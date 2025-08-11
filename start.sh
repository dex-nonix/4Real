#!/bin/bash

# 4Real Music Application Startup Script
# This script starts the nonix_mini_artist application

echo "🎵 Starting 4Real Music Application..."
echo "======================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed or not in PATH"
    echo "Please install Python 3 and try again"
    exit 1
fi

# Check if virtual environment exists
if [ -d "venv" ] || [ -d ".venv" ]; then
    echo "🔧 Activating virtual environment..."
    if [ -d "venv" ]; then
        source venv/bin/activate
    else
        source .venv/bin/activate
    fi
    echo "✅ Virtual environment activated"
else
    echo "⚠️  No virtual environment found. Using system Python..."
fi

# Check if requirements are installed
echo "📦 Checking dependencies..."
if ! python3 -c "import tkinter" 2>/dev/null; then
    echo "❌ Error: Required dependencies not found"
    echo "Please install requirements: pip install -r requirements.txt"
    exit 1
fi

# Start the application
echo "🚀 Launching application..."
echo ""

# Try to start from main.py first, then from the src directory
if [ -f "main.py" ]; then
    echo "Starting from main.py..."
    python3 main.py
elif [ -f "src/nonix_mini_artist/ui/app.py" ]; then
    echo "Starting from UI app..."
    cd src/nonix_mini_artist/ui
    python3 app.py
    cd ../../..
else
    echo "❌ Error: Could not find main entry point"
    echo "Available files:"
    ls -la *.py 2>/dev/null || echo "No Python files in root"
    ls -la src/nonix_mini_artist/ui/*.py 2>/dev/null || echo "No UI files found"
    exit 1
fi

echo ""
echo "👋 Application closed"
