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
from hybrid_search import hybrid_search_service
from vector_store import chroma_service
from models import SearchQuery, HealthStatus, EvaluationRequest, EvaluationResponse
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
        logger.info(f"Knowledge graph search requested: '{search_query.query}' (max_results: {search_query.max_results})")
        
        result = search_service.search_and_answer(
            query=search_query.query,
            max_results=search_query.max_results
        )
        
        logger.info(f"Knowledge graph search completed. Found {len(result['results'])} results")
        return JSONResponse(result)
        
    except Exception as e:
        logger.error(f"Knowledge graph search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.post("/hybrid-search")
def hybrid_search(search_query: SearchQuery):
    """Hybrid search combining ChromaDB documents with Neo4j knowledge graph"""
    try:
        logger.info(f"Hybrid search requested: '{search_query.query}' (max_results: {search_query.max_results})")
        
        # Perform hybrid search
        hybrid_results = hybrid_search_service.hybrid_search(
            query=search_query.query,
            max_results=search_query.max_results
        )
        
        # Generate comprehensive answer
        result = hybrid_search_service.generate_hybrid_answer(
            query=search_query.query,
            hybrid_results=hybrid_results
        )
        
        logger.info(f"Hybrid search completed. Found {len(hybrid_results)} documents")
        return JSONResponse(result)
        
    except Exception as e:
        logger.error(f"Hybrid search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Hybrid search failed: {str(e)}")

@app.get("/documents/stats")
def get_document_stats():
    """Get statistics about the document collection"""
    try:
        stats = chroma_service.get_collection_stats()
        return JSONResponse(stats)
    except Exception as e:
        logger.error(f"Failed to get document stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

@app.post("/documents/search")
def search_documents_only(search_query: SearchQuery):
    """Search only the document collection (ChromaDB) with LLM-generated summary"""
    try:
        logger.info(f"Document search requested: '{search_query.query}'")
        
        # Get document search results
        results = chroma_service.search_documents(
            query=search_query.query,
            n_results=search_query.max_results
        )
        
        # Initialize default values
        answer = "No relevant documents found for this query."
        citations = []
        
        # Generate LLM-powered summary if documents found
        if results:
            try:
                # Create context from documents only (no knowledge graph)
                context_text = f"User Query: {search_query.query}\n\n"
                context_text += "RELEVANT DOCUMENTS:\n"
                
                for i, doc in enumerate(results[:5], 1):
                    # Extract metadata safely
                    title = doc.get('metadata', {}).get('title', f'Document {i}')
                    content = doc.get('content', '')[:1000]
                    authors = doc.get('metadata', {}).get('authors', 'Unknown')
                    year = doc.get('metadata', {}).get('year', 'Unknown')
                    
                    context_text += f"\n{i}. {title}\n"
                    context_text += f"Authors: {authors}\n"
                    context_text += f"Year: {year}\n"
                    context_text += f"Content: {content}...\n"
                
                logger.info(f"Generated context for LLM: {len(context_text)} characters")
                
                # Generate answer using LLM service
                from services import LLMService
                llm_service = LLMService()
                answer = llm_service.generate_answer(search_query.query, context_text)
                
                logger.info(f"LLM generated answer: {len(answer)} characters")
                
                # Create citations from document metadata
                citations = []
                for doc in results:
                    metadata = doc.get('metadata', {})
                    citation = {
                        "source": metadata.get('source', 'Unknown Source'),
                        "title": metadata.get('title', 'Untitled Document'),
                        "authors": metadata.get('authors', '').split(', ') if metadata.get('authors') else [],
                        "year": metadata.get('year'),
                        "venue": metadata.get('venue'),
                        "doi": metadata.get('doi')
                    }
                    citations.append(citation)
                
                logger.info(f"Created {len(citations)} citations")
                
            except Exception as llm_error:
                logger.error(f"LLM generation failed, using fallback: {llm_error}")
                answer = f"Based on {len(results)} documents found, but LLM summary generation failed. Raw document content available in results."
        
        return JSONResponse({
            "query": search_query.query,
            "answer": answer,
            "results": results,
            "citations": citations,
            "total_found": len(results)
        })
        
    except Exception as e:
        logger.error(f"Document search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Document search failed: {str(e)}")

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