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
from graphrag_service import graphrag_service
from traditional_rag_service import traditional_rag_service
from models import SearchQuery, HealthStatus, EvaluationRequest, EvaluationResponse
from utils import setup_logging, safe_json_serialize

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








@app.post("/compare-rag-modes")
def compare_rag_modes(search_query: SearchQuery):
    """Compare GraphRAG vs Traditional RAG side-by-side"""
    try:
        logger.info(f"RAG comparison requested: '{search_query.query}' (max_results: {search_query.max_results})")
        
        # Run both searches in parallel
        graphrag_result = graphrag_service.graphrag_search(
            query=search_query.query,
            max_results=search_query.max_results
        )
        
        traditional_result = traditional_rag_service.traditional_rag_search(
            query=search_query.query,
            max_results=search_query.max_results
        )
        
        # Format comparison response
        comparison_response = {
            "query": search_query.query,
            "search_mode": "comparison",
            "graphrag": {
                "answer": graphrag_result.answer,
                "documents": graphrag_result.related_documents,
                "graph_entities": graphrag_result.graph_entities,
                "knowledge_paths": graphrag_result.knowledge_paths,
                "citations": graphrag_result.citations,
                "reasoning_trace": graphrag_result.reasoning_trace,
                "total_sources": len(graphrag_result.related_documents) + len(graphrag_result.graph_entities)
            },
            "traditional_rag": {
                "answer": traditional_result.answer,
                "documents": traditional_result.documents,
                "citations": traditional_result.citations,
                "reasoning_trace": traditional_result.reasoning_trace,
                "similarity_scores": traditional_result.similarity_scores,
                "total_sources": len(traditional_result.documents)
            },
            "comparison_metrics": {
                "graphrag_entities": len(graphrag_result.graph_entities),
                "graphrag_documents": len(graphrag_result.related_documents),
                "graphrag_paths": len(graphrag_result.knowledge_paths),
                "traditional_documents": len(traditional_result.documents),
                "graphrag_answer_length": len(graphrag_result.answer),
                "traditional_answer_length": len(traditional_result.answer)
            }
        }
        
        logger.info(f"RAG comparison completed. GraphRAG: {len(graphrag_result.graph_entities)} entities, {len(graphrag_result.related_documents)} docs. Traditional: {len(traditional_result.documents)} docs")
        
        # Safely serialize the response to handle Neo4j DateTime objects
        safe_response = safe_json_serialize(comparison_response)
        return JSONResponse(safe_response)
        
    except Exception as e:
        logger.error(f"RAG comparison failed: {e}")
        raise HTTPException(status_code=500, detail=f"RAG comparison failed: {str(e)}")

@app.post("/evaluate-summaries", response_model=EvaluationResponse)
def evaluate_summaries(evaluation_request: EvaluationRequest):
    """Evaluate and compare summaries using LLM judge"""
    try:
        logger.info(f"LLM judge evaluation requested for query: '{evaluation_request.query}'")
        
        # Import here to avoid circular imports
        from llm_judge import LLMJudge
        
        # Create LLM judge instance and evaluate
        judge = LLMJudge()
        evaluation_result = judge.evaluate_summaries(evaluation_request)
        
        logger.info(f"LLM judge evaluation completed. Winner: {evaluation_result.winner}")
        return evaluation_result
        
    except Exception as e:
        logger.error(f"LLM judge evaluation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)