import logging
from typing import List, Dict, Any, Set, Tuple
from dataclasses import dataclass

from vector_store import chroma_service
from database import db
from services import LLMService
from models import Citation

logger = logging.getLogger(__name__)

@dataclass
class HybridSearchResult:
    """Result from hybrid search combining documents and graph context"""
    document_id: str
    title: str
    content: str
    metadata: Dict[str, Any]
    similarity: float
    graph_context: List[Dict[str, Any]]
    related_entities: List[str]

class HybridSearchService:
    def __init__(self):
        self.llm_service = LLMService()
    
    def expand_query_with_graph(self, query: str) -> Tuple[str, List[str]]:
        """Use Neo4j to find related entities and expand the query"""
        try:
            # Extract potential entity names from query (simple approach)
            query_lower = query.lower()
            entities = []
            
            # Search for mentioned companies, people, or topics in the query
            with db.driver.session() as session:
                # Look for companies mentioned in query
                company_result = session.run("""
                    MATCH (c:Company)
                    WHERE toLower(c.name) CONTAINS $query_part
                    RETURN c.name as name, c.industry as industry
                    LIMIT 5
                """, query_part=query_lower)
                
                for record in company_result:
                    entities.append({
                        "name": record["name"],
                        "type": "Company",
                        "industry": record["industry"]
                    })
                
                # Look for topics mentioned in query
                topic_result = session.run("""
                    MATCH (t:Topic)
                    WHERE toLower(t.name) CONTAINS $query_part
                    RETURN t.name as name, t.description as description
                    LIMIT 3
                """, query_part=query_lower)
                
                for record in topic_result:
                    entities.append({
                        "name": record["name"],
                        "type": "Topic",
                        "description": record["description"]
                    })
            
            # Find related entities
            related_entities = []
            for entity in entities:
                related = self._find_related_entities(entity["name"], entity["type"])
                related_entities.extend(related)
            
            # Expand query with related terms
            expanded_query = query
            if related_entities:
                related_terms = " ".join(related_entities)
                expanded_query = f"{query} {related_terms}"
            
            logger.info(f"Expanded query from '{query}' to include: {related_entities}")
            return expanded_query, related_entities
            
        except Exception as e:
            logger.error(f"Failed to expand query with graph: {e}")
            return query, []
    
    def _find_related_entities(self, entity_name: str, entity_type: str) -> List[str]:
        """Find entities related to the given entity"""
        related = []
        
        try:
            with db.driver.session() as session:
                if entity_type == "Company":
                    # Find related companies, people, and topics
                    result = session.run("""
                        MATCH (c:Company {name: $name})
                        OPTIONAL MATCH (c)-[r]-(related)
                        WHERE labels(related) IN [['Company'], ['Person'], ['Topic'], ['Document']]
                        RETURN DISTINCT 
                            CASE 
                                WHEN related.name IS NOT NULL THEN related.name
                                WHEN related.title IS NOT NULL THEN related.title
                                ELSE ''
                            END as related_name,
                            labels(related) as labels,
                            type(r) as relationship
                        LIMIT 10
                    """, name=entity_name)
                    
                    for record in result:
                        if record["related_name"]:
                            related.append(record["related_name"])
                
                elif entity_type == "Topic":
                    # Find companies and documents related to this topic
                    result = session.run("""
                        MATCH (t:Topic {name: $name})
                        OPTIONAL MATCH (t)-[r]-(related)
                        WHERE labels(related) IN [['Company'], ['Document']]
                        RETURN DISTINCT 
                            CASE 
                                WHEN related.name IS NOT NULL THEN related.name
                                WHEN related.title IS NOT NULL THEN related.title
                                ELSE ''
                            END as related_name
                        LIMIT 8
                    """, name=entity_name)
                    
                    for record in result:
                        if record["related_name"]:
                            related.append(record["related_name"])
            
            return related[:5]  # Limit to avoid too much expansion
            
        except Exception as e:
            logger.error(f"Failed to find related entities for {entity_name}: {e}")
            return []
    
    def get_graph_context_for_entities(self, entities: List[str]) -> List[Dict[str, Any]]:
        """Get graph context for the mentioned entities"""
        context = []
        
        try:
            with db.driver.session() as session:
                for entity in entities:
                    # Find the entity and its immediate connections
                    result = session.run("""
                        MATCH (n)
                        WHERE n.name = $entity OR n.title = $entity
                        OPTIONAL MATCH (n)-[r]-(connected)
                        RETURN n, collect({
                            related: connected,
                            relationship: type(r),
                            labels: labels(connected)
                        }) as connections
                        LIMIT 1
                    """, entity=entity)
                    
                    for record in result:
                        node = dict(record["n"])
                        connections = record["connections"]
                        
                        context.append({
                            "entity": entity,
                            "node_data": node,
                            "connections": connections[:5]  # Limit connections
                        })
            
            return context
            
        except Exception as e:
            logger.error(f"Failed to get graph context: {e}")
            return []
    
    def hybrid_search(self, 
                     query: str, 
                     max_results: int = 10,
                     document_filters: Dict = None) -> List[HybridSearchResult]:
        """Perform hybrid search combining ChromaDB documents and Neo4j graph context"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Step 1: Expand query using Neo4j graph relationships
                expanded_query, related_entities = self.expand_query_with_graph(query)
                
                # Step 2: Search documents in ChromaDB
                doc_results = chroma_service.search_documents(
                    query=expanded_query,
                    n_results=max_results,
                    where=document_filters
                )
                
                # Step 3: Get graph context for related entities
                graph_context = self.get_graph_context_for_entities(related_entities)
                
                # Step 4: Combine results
                hybrid_results = []
                for doc in doc_results:
                    # Get additional graph context specific to this document
                    doc_entities = self._extract_entities_from_document(doc['metadata'])
                    doc_graph_context = self.get_graph_context_for_entities(doc_entities)
                    
                    # Combine general and document-specific context
                    combined_context = graph_context + doc_graph_context
                    
                    hybrid_result = HybridSearchResult(
                        document_id=doc['id'],
                        title=doc['metadata'].get('title', 'Untitled'),
                        content=doc['content'],
                        metadata=doc['metadata'],
                        similarity=doc['similarity'] or 0.0,
                        graph_context=combined_context,
                        related_entities=related_entities + doc_entities
                    )
                    
                    hybrid_results.append(hybrid_result)
                
                logger.info(f"Hybrid search returned {len(hybrid_results)} results")
                return hybrid_results
                
            except Exception as e:
                logger.warning(f"Hybrid search attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    logger.error(f"Hybrid search failed after {max_retries} attempts: {e}")
                    raise
                import time
                time.sleep(0.5)  # Brief delay before retry
    
    def _extract_entities_from_document(self, metadata: Dict[str, Any]) -> List[str]:
        """Extract entity names from document metadata"""
        entities = []
        
        # Extract from common metadata fields (now strings with commas)
        if 'companies' in metadata and metadata['companies']:
            if isinstance(metadata['companies'], str):
                entities.extend([c.strip() for c in metadata['companies'].split(',')])
            else:
                entities.extend(metadata['companies'])
        
        if 'topics' in metadata and metadata['topics']:
            if isinstance(metadata['topics'], str):
                entities.extend([t.strip() for t in metadata['topics'].split(',')])
            else:
                entities.extend(metadata['topics'])
        
        if 'people' in metadata and metadata['people']:
            if isinstance(metadata['people'], str):
                entities.extend([p.strip() for p in metadata['people'].split(',')])
            else:
                entities.extend(metadata['people'])
        
        if 'authors' in metadata and metadata['authors']:
            if isinstance(metadata['authors'], str):
                entities.extend([a.strip() for a in metadata['authors'].split(',')])
            else:
                entities.extend(metadata['authors'])
        
        return list(set(entities))  # Remove duplicates
    
    def generate_hybrid_answer(self, 
                              query: str, 
                              hybrid_results: List[HybridSearchResult]) -> Dict[str, Any]:
        """Generate answer using both document content and graph context"""
        try:
            if not hybrid_results:
                return {
                    "query": query,
                    "answer": "No relevant documents found.",
                    "documents": [],
                    "graph_entities": [],
                    "citations": []
                }
            
            # Build comprehensive context
            context_text = f"User Query: {query}\n\n"
            
            # Add document context
            context_text += "RELEVANT DOCUMENTS:\n"
            for i, result in enumerate(hybrid_results[:5], 1):
                context_text += f"\n{i}. {result.title}\n"
                context_text += f"Content: {result.content[:1000]}...\n"
                if result.metadata.get('type'):
                    context_text += f"Type: {result.metadata['type']}\n"
                if result.metadata.get('date'):
                    context_text += f"Date: {result.metadata['date']}\n"
                if result.metadata.get('source'):
                    context_text += f"Source: {result.metadata['source']}\n"
            
            # Add graph context
            if any(result.graph_context for result in hybrid_results):
                context_text += "\nRELATED KNOWLEDGE GRAPH ENTITIES:\n"
                seen_entities = set()
                for result in hybrid_results:
                    for ctx in result.graph_context:
                        entity_name = ctx.get('entity', '')
                        if entity_name and entity_name not in seen_entities:
                            context_text += f"- {entity_name}: {ctx.get('node_data', {})}\n"
                            seen_entities.add(entity_name)
            
            # Generate answer
            answer = self.llm_service.generate_answer(query, context_text)
            
            # Extract citations
            citations = self._extract_citations_from_results(hybrid_results)
            
            return {
                "query": query,
                "answer": answer,
                "documents": [
                    {
                        "id": r.document_id,
                        "title": r.title,
                        "similarity": r.similarity,
                        "metadata": r.metadata
                    } for r in hybrid_results
                ],
                "graph_entities": list(set(
                    entity for result in hybrid_results 
                    for entity in result.related_entities
                )),
                "citations": citations
            }
            
        except Exception as e:
            logger.error(f"Failed to generate hybrid answer: {e}")
            raise
    
    def _extract_citations_from_results(self, results: List[HybridSearchResult]) -> List[Dict[str, Any]]:
        """Extract citations from hybrid search results"""
        citations = []
        seen_sources = set()
        
        for result in results:
            metadata = result.metadata
            source_key = result.title
            
            if source_key not in seen_sources:
                citation = {
                    "source": source_key,
                    "title": result.title,
                    "authors": metadata.get("authors"),
                    "year": metadata.get("year"),
                    "venue": metadata.get("venue") or metadata.get("source"),
                    "doi": metadata.get("doi"),
                    "type": metadata.get("type", "document")
                }
                citations.append(citation)
                seen_sources.add(source_key)
        
        return citations

# Global instance
hybrid_search_service = HybridSearchService()