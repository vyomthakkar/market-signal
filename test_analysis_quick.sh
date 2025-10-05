#!/bin/bash
# Quick test script - activates venv and runs sample analysis

echo "🧪 Quick Analysis Test"
echo "====================="
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please create it first:"
    echo "  python3 -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install -r requirements.txt"
    exit 1
fi

# Activate venv
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
echo "🔍 Checking dependencies..."
python -c "import pandas, torch, transformers" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Dependencies not installed. Installing now..."
    pip install -q -r requirements.txt
fi

# Run test
echo ""
echo "🚀 Running sample analysis..."
echo ""
python test_analysis_sample.py

echo ""
echo "Done!"
