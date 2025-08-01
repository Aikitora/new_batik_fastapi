#!/bin/bash

echo "🎨 Starting Batik Classification API..."

# Check if model file exists
if [ ! -f "final_tuned_genetic_algorithm_model.keras" ]; then
    echo "❌ Error: Model file 'final_tuned_genetic_algorithm_model.keras' not found!"
    echo "Please ensure the model file is in the current directory."
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed!"
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ Error: pip3 is not installed!"
    exit 1
fi

echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

echo "🚀 Starting FastAPI server..."
echo "📍 API will be available at: http://localhost:8000"
echo "📚 API Documentation: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the API
python3 main.py 