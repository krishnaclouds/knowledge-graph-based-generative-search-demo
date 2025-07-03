#!/bin/bash
# Simple data loading script for GraphRAG vs Traditional RAG comparison

echo "🔄 Loading data for GraphRAG vs Traditional RAG comparison..."

# Check if we're in the right directory
if [ ! -f "backend/main.py" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Go to backend directory
cd backend

echo "📦 Installing/updating requirements..."
pip install -r requirements.txt

echo "🔍 Checking existing data..."

# Check if ChromaDB data already exists
if [ -d "chroma_db" ] && [ "$(ls -A chroma_db)" ]; then
    echo "✅ ChromaDB data found - using existing data"
    CHROMA_EXISTS=true
else
    echo "⚠️  No ChromaDB data found"
    CHROMA_EXISTS=false
fi

# Check if we need to load new data
if [ "$CHROMA_EXISTS" = false ]; then
    echo "📚 Loading sample documents..."
    echo "Choose data loading option:"
    echo "1) Quick load (10 documents) - fastest"
    echo "2) Standard load (100 documents) - recommended"
    echo "3) Large load (1000+ documents) - most comprehensive"
    
    read -p "Enter choice (1-3): " choice
    
    case $choice in
        1)
            echo "🚀 Running quick data collection..."
            python run_collection.py
            ;;
        2)
            echo "🚀 Running standard data collection..."
            python -c "
from data_orchestrator import run_data_collection_pipeline
result = run_data_collection_pipeline(target_documents=100)
print('✅ Collection complete!' if result['success'] else '❌ Collection failed')
"
            ;;
        3)
            echo "🚀 Running large data collection..."
            python collect_1k_documents.py
            ;;
        *)
            echo "❌ Invalid choice. Using quick load..."
            python run_collection.py
            ;;
    esac
else
    echo "📊 Using existing data - skipping collection"
fi

echo ""
echo "🎯 Data loading complete!"
echo ""
echo "🚀 Next steps:"
echo "1. Start the backend: cd backend && python main.py"
echo "2. Start the frontend: cd frontend && npm run dev"
echo "3. Open http://localhost:5173 for GraphRAG vs Traditional RAG comparison"
echo ""
echo "💡 The application will run comparison analysis between:"
echo "   - GraphRAG (Knowledge Graph + Documents)"
echo "   - Traditional RAG (Documents only)"