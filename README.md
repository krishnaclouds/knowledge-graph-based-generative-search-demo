# GraphRAG vs Traditional RAG Comparison Demo

A focused comparison application that demonstrates the differences between GraphRAG (Graph-enhanced Retrieval-Augmented Generation) and Traditional RAG approaches using knowledge graphs, vector databases, and Large Language Models.

## 🌟 Features

- **Side-by-Side Comparison**: Direct comparison of GraphRAG vs Traditional RAG results
- **LLM Judge Evaluation**: Automated evaluation using Claude as an impartial judge
- **Knowledge Graph Visualization**: Interactive graph visualization using vis-network
- **Comprehensive Metrics**: Detailed scoring on completeness, accuracy, contextual depth, and more
- **Real-time Analysis**: Live connection status and error handling
- **Clean Architecture**: Streamlined codebase focused on comparison functionality

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │    Neo4j        │
│   (React +      │◄──►│   (FastAPI +    │◄──►│   Database      │
│   Vite)         │    │   Python)       │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Anthropic     │
                       │   Claude API    │
                       └─────────────────┘
```

### Backend Components

- **`main.py`**: FastAPI application with global error handling
- **`models.py`**: Pydantic data models for API validation
- **`config.py`**: Environment configuration management
- **`database.py`**: Neo4j database operations
- **`core_services.py`**: Business logic for search and embeddings
- **`graphrag_service.py`**: GraphRAG implementation using knowledge graphs
- **`traditional_rag_service.py`**: Traditional RAG implementation
- **`llm_judge.py`**: LLM-based evaluation and comparison logic
- **`data_orchestrator.py`**: Data collection pipeline orchestration
- **`data_collectors/`**: Specialized data collectors (ArXiv, GitHub, news, etc.)
- **`vector_store.py`**: ChromaDB vector store operations
- **`utils.py`**: Utility functions for logging and data formatting

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- Neo4j Database (local or cloud)
- Anthropic API Key

### 1. Clone and Setup

```bash
git clone <repository-url>
cd knowledgeGraphDemo
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env
# Edit .env with your configuration
```

### 3. Environment Configuration

Create a `.env` file in the backend directory:

```env
# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password

# Anthropic API
ANTHROPIC_API_KEY=your_anthropic_api_key

# Optional: Advanced Configuration
EMBEDDING_MODEL_NAME=all-MiniLM-L6-v2
ANTHROPIC_MODEL=claude-3-haiku-20240307
SIMILARITY_THRESHOLD=0.1
MAX_TOKENS=300
TEMPERATURE=0.3
CORS_ORIGINS=["*"]
```

### 4. Data Loading

The application includes ChromaDB data and supports loading additional documents:

```bash
# Simple data loading (recommended)
./load-data.sh
```

This script will:
- Check for existing data
- Offer loading options (quick/standard/large)
- Set up both ChromaDB and knowledge graph data

**Manual data loading options:**
```bash
cd backend

# Quick load (10 documents)
python run_collection.py

# Standard load (100 documents) 
python -c "from data_orchestrator import run_data_collection_pipeline; run_data_collection_pipeline(target_documents=100)"

# Large load (1000+ documents)
python collect_1k_documents.py
```

### 5. Neo4j Setup

#### Option A: Neo4j Desktop
1. Download and install Neo4j Desktop
2. Create a new database
3. Start the database
4. Note the connection details (bolt://localhost:7687 by default)

#### Option B: Neo4j AuraDB (Cloud)
1. Sign up at [neo4j.com/aura](https://neo4j.com/aura)
2. Create a free database
3. Download the connection file or note the connection details

### 5. Load Data

#### Option A: Quick Start with Sample Data
```bash
./start-backend.sh
# Choose 'y' when prompted to load sample data
```

#### Option B: Load 1000+ Documents for GraphRAG Evaluation
```bash
./load-data.sh
```
This will collect 1000+ documents from multiple sources:
- ArXiv research papers (~300)
- Semantic Scholar academic papers (~250) 
- Tech news and company blogs (~250)
- GitHub repositories (~200)

### 6. Start Backend

```bash
./start-backend.sh
```

The API will be available at `http://localhost:8000`

### 7. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:5173`

## 📊 Data Options

### Sample Data (Quick Start)
The application includes basic sample data with:
- **Companies**: Technology companies with industry information
- **People**: Employees with roles and company affiliations  
- **Topics**: Discussion topics with participant relationships

### Enhanced Dataset (1000+ Documents)
For comprehensive GraphRAG vs RAG evaluation:
- **Research Papers**: ArXiv and Semantic Scholar papers on AI/ML
- **News Articles**: Tech news from TechCrunch, VentureBeat, Wired
- **Company Blogs**: Research posts from Google, Microsoft, OpenAI, Meta
- **GitHub Repositories**: AI/ML open source projects
- **Knowledge Graph**: 500+ entities with rich interconnections

### Search Modes Available

1. **GraphRAG**: Uses knowledge graph relationships + documents
2. **Traditional RAG**: Uses document vector similarity only
3. **Knowledge Graph Only**: Pure graph structure reasoning  
4. **Comparison Analysis**: Side-by-side GraphRAG vs Traditional RAG evaluation

### Example Queries to Try

**Sample Data Queries:**
- "What companies are in the technology industry?"
- "Who works at Google?"
- "What topics are being discussed?"

**Enhanced Dataset Queries:**
- "What are the latest advances in large language models?"
- "How does federated learning work with computer vision?"
- "What researchers are working on BERT and transformer models?"
- "Tell me about quantum computing developments"
- "What is the relationship between neural networks and reinforcement learning?"

## 🔧 API Endpoints

### Health Check
```http
GET /health
```

### Graph Data
```http
GET /graph
```

### Search
```http
POST /search
Content-Type: application/json

{
  "query": "your search query",
  "max_results": 5
}
```

## 🛠️ Development

### Backend Development

```bash
cd backend

# Install dev dependencies
pip install pytest black flake8

# Run tests
pytest

# Format code
black .

# Lint code
flake8
```

### Frontend Development

```bash
cd frontend

# Lint code
npm run lint

# Build for production
npm run build

# Preview production build
npm run preview
```

## 🐳 Docker Setup (Optional)

### Backend Docker

```bash
cd backend

# Build image
docker build -t kg-rag-backend .

# Run container
docker run -p 8000:8000 --env-file .env kg-rag-backend
```

### Docker Compose

```bash
# Run everything with Docker Compose
docker-compose up -d
```

## 🔍 Troubleshooting

### Common Issues

#### Backend won't start
- **Error**: "Failed to connect to Neo4j"
  - **Solution**: Ensure Neo4j is running and connection details are correct
  - Check NEO4J_URI, NEO4J_USER, and NEO4J_PASSWORD in .env

#### Search not working
- **Error**: "Error generating answer"
  - **Solution**: Verify ANTHROPIC_API_KEY is set correctly
  - Check API key has sufficient credits

#### Frontend shows "Backend Status: Disconnected"
- **Solution**: Ensure backend is running on port 8000
  ```bash
  cd backend && python main.py
  ```

#### No search results
- **Solution**: Load sample data or check if Neo4j has data
  ```bash
  cd backend && python run_collection.py
  ```

### Logs

Backend logs are written to console with timestamps. To increase verbosity:

```bash
export LOG_LEVEL=DEBUG
python main.py
```

### Performance Tips

1. **Neo4j Performance**:
   - Create indexes on frequently queried properties
   - Use database connection pooling for production

2. **Embedding Performance**:
   - Consider using GPU acceleration for sentence transformers
   - Cache embeddings for static data

3. **Frontend Performance**:
   - Enable graph virtualization for large datasets
   - Implement result pagination for large result sets

## 🏭 Production Deployment

### Backend Production

```bash
# Install production WSGI server
pip install gunicorn

# Run with gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Frontend Production

```bash
# Build for production
npm run build

# Serve static files with nginx or similar
```

### Environment Variables for Production

```env
# Restrict CORS for production
CORS_ORIGINS=["https://yourdomain.com"]

# Use production Neo4j instance
NEO4J_URI=neo4j+s://your-production-db.neo4j.io

# Configure logging
LOG_LEVEL=INFO
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Resources

- [Neo4j Documentation](https://neo4j.com/docs/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Anthropic Claude API](https://docs.anthropic.com/)
- [Sentence Transformers](https://www.sbert.net/)
- [React Documentation](https://react.dev/)

## 💡 Next Steps

Consider these enhancements:

- [ ] Implement graph editing capabilities
- [ ] Add support for multiple knowledge graphs
- [ ] Integrate with other LLM providers
- [ ] Add graph analytics and insights
- [ ] Implement real-time collaborative features
- [ ] Add graph import/export functionality