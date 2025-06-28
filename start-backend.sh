#!/bin/bash

# Knowledge Graph RAG Demo - Backend Startup Script

echo "🚀 Starting Knowledge Graph RAG Backend..."

# Check if we're in the right directory
if [ ! -f "backend/main.py" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Change to backend directory
cd backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo "📝 Please edit backend/.env with your configuration before continuing."
    echo "   Required: NEO4J_PASSWORD and ANTHROPIC_API_KEY"
    read -p "Press Enter when you've configured your .env file..."
fi

# Check if sample data should be loaded
echo "📊 Do you want to load sample data? (y/N)"
read -r load_data
if [[ $load_data =~ ^[Yy]$ ]]; then
    echo "📊 Loading sample data..."
    python sample_data.py
fi

# Start the backend server
echo "🌐 Starting FastAPI server on http://localhost:8000"
echo "📚 API Documentation available at http://localhost:8000/docs"
echo "❤️  Health check: http://localhost:8000/health"
echo ""
echo "Press Ctrl+C to stop the server"
python main.py