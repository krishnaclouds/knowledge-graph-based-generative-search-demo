#!/bin/bash

# Knowledge Graph RAG Demo - Complete Startup Script

echo "🎯 Knowledge Graph RAG Demo - Complete Setup"
echo "============================================="

# Check if we're in the right directory
if [ ! -f "README.md" ] || [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "🔍 Checking prerequisites..."

if ! command_exists python3; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

if ! command_exists node; then
    echo "❌ Node.js is required but not installed"
    exit 1
fi

if ! command_exists npm; then
    echo "❌ npm is required but not installed"
    exit 1
fi

echo "✅ Prerequisites check passed"

# Make scripts executable
chmod +x start-backend.sh
chmod +x start-frontend.sh

# Setup backend
echo ""
echo "🔧 Setting up backend..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Check environment configuration
if [ ! -f ".env" ]; then
    echo "⚠️  Creating .env file from template..."
    cp .env.example .env
    echo ""
    echo "📝 IMPORTANT: Please edit backend/.env with your configuration:"
    echo "   - NEO4J_PASSWORD: Your Neo4j database password"
    echo "   - ANTHROPIC_API_KEY: Your Anthropic API key"
    echo ""
    echo "⏸️  Setup paused. Please configure your .env file and run this script again."
    exit 1
fi

# Test database connection
echo "🔗 Testing database connection..."
python -c "
from database import db
try:
    health = db.health_check()
    if health['status'] == 'ok':
        print('✅ Database connection successful')
    else:
        print('❌ Database connection failed:', health.get('detail', 'Unknown error'))
        exit(1)
except Exception as e:
    print('❌ Database connection failed:', str(e))
    exit(1)
finally:
    db.close()
"

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Database connection failed. Please check:"
    echo "   - Neo4j is running"
    echo "   - Connection details in .env are correct"
    exit 1
fi

# Load sample data
echo "📊 Loading sample data..."
python sample_data.py

cd ..

# Setup frontend
echo ""
echo "🎨 Setting up frontend..."
cd frontend

# Install npm dependencies
if [ ! -d "node_modules" ]; then
    echo "📦 Installing npm dependencies..."
    npm install
fi

cd ..

echo ""
echo "🎉 Setup complete! You can now start the application:"
echo ""
echo "Option 1 - Start both services manually:"
echo "  Terminal 1: ./start-backend.sh"
echo "  Terminal 2: ./start-frontend.sh"
echo ""
echo "Option 2 - Start services automatically (requires tmux):"
if command_exists tmux; then
    echo "  ./start-demo.sh auto"
else
    echo "  Install tmux first: brew install tmux (macOS) or apt install tmux (Ubuntu)"
fi
echo ""
echo "🔗 URLs:"
echo "  Frontend: http://localhost:5173"
echo "  Backend API: http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo ""

# Auto-start option
if [ "$1" = "auto" ]; then
    if command_exists tmux; then
        echo "🚀 Starting both services automatically..."
        tmux new-session -d -s kg-demo -x 120 -y 40
        tmux send-keys -t kg-demo './start-backend.sh' Enter
        tmux split-window -t kg-demo -h
        tmux send-keys -t kg-demo './start-frontend.sh' Enter
        tmux select-pane -t kg-demo -L
        echo "✅ Services started in tmux session 'kg-demo'"
        echo "📺 Attach to session: tmux attach -t kg-demo"
        echo "🛑 Stop services: tmux kill-session -t kg-demo"
    else
        echo "❌ tmux not available for auto-start"
    fi
fi