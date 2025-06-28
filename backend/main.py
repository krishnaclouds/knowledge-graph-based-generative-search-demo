import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from dotenv import load_dotenv

load_dotenv()

from config import get_settings
from database import db
from services import search_service
from models import SearchQuery, HealthStatus
from utils import setup_logging, format_graph_data

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Load settings
settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting Knowledge Graph RAG API")
    yield
    logger.info("Shutting down Knowledge Graph RAG API")
    db.close()

app = FastAPI(
    title="Knowledge Graph RAG API",
    description="A RAG-based search API for knowledge graphs using Neo4j, embeddings, and LLM",
    version="1.0.0",
    lifespan=lifespan
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError):
    logger.error(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={"error": "Validation error", "details": exc.errors()}
    )

@app.exception_handler(Exception)
async def general_exception_handler(_: Request, exc: Exception):
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": "An unexpected error occurred"}
    )

@app.get("/health", response_model=HealthStatus)
def health_check():
    """Health check endpoint"""
    try:
        logger.info("Health check requested")
        return db.health_check()
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@app.get("/graph")
def get_graph():
    """Get the complete knowledge graph"""
    try:
        logger.info("Graph data requested")
        nodes = db.get_all_nodes()
        edges = db.get_all_edges()
        
        graph_data = format_graph_data(nodes, edges)
        return JSONResponse(graph_data)
        
    except Exception as e:
        logger.error(f"Failed to get graph data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve graph data: {str(e)}")

@app.post("/search")
def search_knowledge_graph(search_query: SearchQuery):
    """Search the knowledge graph using semantic search and generate an answer"""
    try:
        logger.info(f"Search requested: '{search_query.query}' (max_results: {search_query.max_results})")
        
        result = search_service.search_and_answer(
            query=search_query.query,
            max_results=search_query.max_results
        )
        
        logger.info(f"Search completed. Found {len(result['results'])} results")
        return JSONResponse(result)
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)