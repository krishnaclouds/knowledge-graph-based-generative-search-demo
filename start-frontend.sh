#!/bin/bash

# Knowledge Graph RAG Demo - Frontend Startup Script

echo "🎨 Starting Knowledge Graph RAG Frontend..."

# Check if we're in the right directory
if [ ! -f "frontend/package.json" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Change to frontend directory
cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing npm dependencies..."
    npm install
fi

# Start the development server
echo "🌐 Starting Vite development server..."
echo "🔗 Frontend will be available at http://localhost:5173"
echo "🔄 Hot reload enabled for development"
echo ""
echo "Press Ctrl+C to stop the server"
npm run dev