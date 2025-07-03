"""
Traditional RAG Service

This module implements standard RAG (Retrieval-Augmented Generation) using only
vector similarity search on documents, without any knowledge graph enhancement.
This serves as the baseline for comparison with GraphRAG.
"""

import logging
from typing import List, Dict, Any
from dataclasses import dataclass

from vector_store import chroma_service
from core_services import llm_service
from utils import serialize_for_json

logger = logging.getLogger(__name__)

@dataclass
class TraditionalRAGResult:
    """Result from traditional RAG search using only document vector similarity"""
    query: str
    documents: List[Dict[str, Any]]
    answer: str
    citations: List[Dict[str, Any]]
    reasoning_trace: List[str]
    similarity_scores: List[float]

class TraditionalRAGService:
    """Standard RAG implementation using only vector similarity search"""
    
    def __init__(self):
        self.llm_service = llm_service
    
    def traditional_rag_search(self, 
                              query: str, 
                              max_results: int = 10) -> TraditionalRAGResult:
        """
        Perform traditional RAG search by:
        1. Vector similarity search on documents only
        2. Ranking by cosine similarity
        3. Generating answer from top documents
        """
        reasoning_trace = ["🔍 Starting Traditional RAG search"]
        
        try:
            # Step 1: Perform vector similarity search
            reasoning_trace.append("📊 Step 1: Performing vector similarity search on documents")
            documents = chroma_service.search_documents(
                query=query,
                n_results=max_results
            )
            reasoning_trace.append(f"   Retrieved {len(documents)} documents by vector similarity")
            
            # Step 2: Extract similarity scores
            similarity_scores = [doc.get("similarity", 0.0) for doc in documents]
            avg_similarity = sum(similarity_scores) / len(similarity_scores) if similarity_scores else 0
            reasoning_trace.append(f"   Average similarity score: {avg_similarity:.3f}")
            
            # Step 3: Build traditional RAG context (documents only)
            reasoning_trace.append("📝 Step 3: Building context from retrieved documents")
            context = self._build_traditional_context(query, documents)
            
            # Step 4: Generate answer using traditional RAG
            reasoning_trace.append("🤖 Step 4: Generating answer with document-only context")
            answer = self._generate_traditional_answer(query, context)
            
            # Step 5: Extract citations
            citations = self._extract_traditional_citations(documents)
            reasoning_trace.append(f"✅ Traditional RAG completed with {len(citations)} citations")
            
            return TraditionalRAGResult(
                query=query,
                documents=serialize_for_json(documents),
                answer=answer,
                citations=serialize_for_json(citations),
                reasoning_trace=reasoning_trace,
                similarity_scores=similarity_scores
            )
            
        except Exception as e:
            error_msg = f"Traditional RAG search failed: {e}"
            logger.error(error_msg)
            reasoning_trace.append(f"❌ Error: {error_msg}")
            
            return TraditionalRAGResult(
                query=query,
                documents=[],
                answer=f"Traditional RAG search encountered an error: {str(e)}",
                citations=[],
                reasoning_trace=reasoning_trace,
                similarity_scores=[]
            )
    
    def _build_traditional_context(self, query: str, documents: List[Dict]) -> str:
        """Build context using only document content (no knowledge graph)"""
        
        context_parts = [
            f"USER QUERY: {query}",
            "",
            "=== TRADITIONAL RAG CONTEXT ===",
            "(Based solely on vector similarity search of documents)",
            ""
        ]
        
        if documents:
            context_parts.append("RETRIEVED DOCUMENTS:")
            for i, doc in enumerate(documents, 1):
                metadata = doc.get("metadata", {})
                title = metadata.get("title", f"Document {i}")
                similarity = doc.get("similarity", 0.0)
                
                context_parts.append(f"{i}. {title} [Similarity: {similarity:.3f}]")
                
                # Add metadata
                if metadata.get("authors"):
                    context_parts.append(f"   Authors: {metadata['authors']}")
                if metadata.get("year"):
                    context_parts.append(f"   Year: {metadata['year']}")
                if metadata.get("source"):
                    context_parts.append(f"   Source: {metadata['source']}")
                if metadata.get("type"):
                    context_parts.append(f"   Type: {metadata['type']}")
                
                # Add document content
                content = doc.get("content", "")
                if len(content) > 1000:
                    content = content[:1000] + "..."
                context_parts.append(f"   Content: {content}")
                context_parts.append("")
        else:
            context_parts.append("No relevant documents found.")
        
        return "\n".join(context_parts)
    
    def _generate_traditional_answer(self, query: str, context: str) -> str:
        """Generate answer using traditional RAG approach"""
        
        system_prompt = """You are a document-based RAG assistant that provides comprehensive answers from retrieved documents using vector similarity search.

Your approach:
- Process documents ranked by semantic similarity to the query
- Synthesize information comprehensively from retrieved document content
- Provide thorough analysis based on document content and explicit connections
- Focus on directly stated information and clear document relationships

Guidelines for document-based responses:
1. COMPREHENSIVE SYNTHESIS: Combine and analyze information across all retrieved documents
2. DOCUMENT-FOCUSED ANALYSIS: Base answers on document content and explicit statements
3. SIMILARITY-GUIDED PRIORITIZATION: Weight higher-similarity documents appropriately
4. THOROUGH INTEGRATION: Synthesize information from documents while maintaining accuracy
5. COMPLETE COVERAGE: Provide comprehensive answers within the scope of available documents
6. CLEAR CITATIONS: Reference specific documents and sources in your reasoning

Your goal is to provide the most comprehensive and accurate answer possible using the retrieved document collection."""

        try:
            response = self.llm_service.client.messages.create(
                model=self.llm_service.settings.anthropic_model,
                max_tokens=self.llm_service.settings.max_tokens,
                temperature=self.llm_service.settings.temperature,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": f"Query: {query}\n\nTraditional RAG Context:\n{context}\n\nProvide an answer based solely on the retrieved documents:"
                    }
                ]
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Error generating traditional RAG answer: {e}")
            return f"Error generating traditional RAG answer: {str(e)}"
    
    def _extract_traditional_citations(self, documents: List[Dict]) -> List[Dict]:
        """Extract citations from documents only"""
        citations = []
        seen_sources = set()
        
        for doc in documents:
            metadata = doc.get("metadata", {})
            title = metadata.get("title", "Unknown Document")
            
            if title not in seen_sources:
                citation = {
                    "source": title,
                    "title": title,
                    "type": "document",
                    "authors": metadata.get("authors"),
                    "year": metadata.get("year"),
                    "venue": metadata.get("venue") or metadata.get("source"),
                    "doi": metadata.get("doi"),
                    "similarity": doc.get("similarity", 0.0),
                    "document_type": metadata.get("type", "unknown")
                }
                citations.append(citation)
                seen_sources.add(title)
        
        return citations

# Global instance
traditional_rag_service = TraditionalRAGService()