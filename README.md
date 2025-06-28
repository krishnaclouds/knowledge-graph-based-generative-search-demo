# Knowledge Graph RAG Search Demo

A full-stack application demonstrating Retrieval-Augmented Generation (RAG) search capabilities over a knowledge graph using Neo4j, embeddings, and Large Language Models.

## 🌟 Features

- **Knowledge Graph Visualization**: Interactive graph visualization using vis-network
- **Semantic Search**: Vector-based similarity search using sentence transformers
- **RAG-based Q&A**: Generate contextual answers using Anthropic's Claude API
- **Real-time Updates**: Live connection status and error handling
- **Modular Architecture**: Clean separation of concerns in backend
- **Comprehensive Error Handling**: User-friendly error messages and retry mechanisms

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
- **`services.py`**: Business logic for search and embeddings
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

### 4. Neo4j Setup

#### Option A: Neo4j Desktop
1. Download and install Neo4j Desktop
2. Create a new database
3. Start the database
4. Note the connection details (bolt://localhost:7687 by default)

#### Option B: Neo4j AuraDB (Cloud)
1. Sign up at [neo4j.com/aura](https://neo4j.com/aura)
2. Create a free database
3. Download the connection file or note the connection details

### 5. Load Sample Data

```bash
cd backend
python sample_data.py
```

### 6. Start Backend

```bash
cd backend
python main.py
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

## 📊 Sample Data

The application includes sample data with:

- **Companies**: Technology companies with industry information
- **People**: Employees with roles and company affiliations
- **Topics**: Discussion topics with participant relationships

Example queries to try:
- "What companies are in the technology industry?"
- "Who works at Google?"
- "What topics are being discussed?"
- "Tell me about artificial intelligence"

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
  cd backend && python sample_data.py
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

- [ ] Add user authentication and authorization
- [ ] Implement graph editing capabilities
- [ ] Add support for multiple knowledge graphs
- [ ] Integrate with other LLM providers
- [ ] Add graph analytics and insights
- [ ] Implement real-time collaborative features
- [ ] Add graph import/export functionality