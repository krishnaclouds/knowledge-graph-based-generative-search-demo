"""
GraphRAG Service

This module implements true GraphRAG by leveraging knowledge graph relationships
to enhance document retrieval and answer generation. It uses graph traversal
to find related entities and expands the context beyond simple vector similarity.
"""

import logging
from typing import List, Dict, Any, Set, Tuple
from dataclasses import dataclass
import numpy as np

from vector_store import chroma_service
from database import db
from core_services import llm_service, embedding_service
from models import Citation
from utils import serialize_for_json

logger = logging.getLogger(__name__)

@dataclass
class GraphRAGResult:
    """Result from GraphRAG search combining graph traversal and document retrieval"""
    query: str
    graph_entities: List[Dict[str, Any]]
    related_documents: List[Dict[str, Any]]
    knowledge_paths: List[Dict[str, Any]]
    answer: str
    citations: List[Dict[str, Any]]
    reasoning_trace: List[str]

class GraphRAGService:
    """Enhanced RAG service that uses knowledge graph structure for context expansion"""
    
    def __init__(self):
        self.llm_service = llm_service
        self.embedding_service = embedding_service
        
    def graphrag_search(self, 
                       query: str, 
                       max_results: int = 10,
                       graph_depth: int = 2) -> GraphRAGResult:
        """
        Perform GraphRAG search by:
        1. Finding relevant entities in the knowledge graph
        2. Expanding context through graph traversal
        3. Retrieving documents connected to these entities
        4. Generating answer with enriched context
        """
        reasoning_trace = ["🔍 Starting GraphRAG search"]
        
        try:
            # Step 1: Identify relevant entities from query
            reasoning_trace.append("📊 Step 1: Identifying relevant entities from query")
            relevant_entities = self._find_query_entities(query)
            reasoning_trace.append(f"   Found {len(relevant_entities)} direct entities: {[e['name'] for e in relevant_entities[:3]]}")
            
            # Step 2: Expand context through graph traversal
            reasoning_trace.append("🕸️ Step 2: Expanding context through graph relationships")
            expanded_entities = self._expand_entities_via_graph(relevant_entities, depth=graph_depth)
            reasoning_trace.append(f"   Expanded to {len(expanded_entities)} entities via {graph_depth}-hop traversal")
            
            # Step 3: Find knowledge paths between entities
            reasoning_trace.append("🔗 Step 3: Finding knowledge paths between entities")
            knowledge_paths = self._find_knowledge_paths(expanded_entities)
            reasoning_trace.append(f"   Discovered {len(knowledge_paths)} relationship paths")
            
            # Step 4: Retrieve documents connected to expanded entities
            reasoning_trace.append("📄 Step 4: Retrieving documents connected to entities")
            connected_documents = self._find_entity_documents(expanded_entities, max_results)
            reasoning_trace.append(f"   Retrieved {len(connected_documents)} entity-connected documents")
            
            # Step 5: Enhance with vector similarity search on documents
            reasoning_trace.append("🔍 Step 5: Enhancing with semantic document search")
            vector_documents = self._semantic_document_search(query, max_results//2)
            reasoning_trace.append(f"   Added {len(vector_documents)} semantically similar documents")
            
            # Step 6: Combine and deduplicate documents
            all_documents = self._merge_document_sources(connected_documents, vector_documents)
            reasoning_trace.append(f"   Final document set: {len(all_documents)} unique documents")
            
            # Step 7: Build enriched context with graph relationships
            reasoning_trace.append("🧠 Step 7: Building enriched context with graph relationships")
            enriched_context = self._build_graphrag_context(
                query, expanded_entities, knowledge_paths, all_documents
            )
            
            # Step 8: Generate answer with GraphRAG context
            reasoning_trace.append("🤖 Step 8: Generating answer with GraphRAG context")
            answer = self._generate_graphrag_answer(query, enriched_context)
            
            # Step 9: Extract citations
            citations = self._extract_graphrag_citations(all_documents, expanded_entities)
            reasoning_trace.append(f"✅ GraphRAG search completed with {len(citations)} citations")
            
            return GraphRAGResult(
                query=query,
                graph_entities=serialize_for_json(expanded_entities),
                related_documents=serialize_for_json(all_documents),
                knowledge_paths=serialize_for_json(knowledge_paths),
                answer=answer,
                citations=serialize_for_json(citations),
                reasoning_trace=reasoning_trace
            )
            
        except Exception as e:
            error_msg = f"GraphRAG search failed: {e}"
            logger.error(error_msg)
            reasoning_trace.append(f"❌ Error: {error_msg}")
            
            return GraphRAGResult(
                query=query,
                graph_entities=[],
                related_documents=[],
                knowledge_paths=[],
                answer=f"GraphRAG search encountered an error: {str(e)}",
                citations=[],
                reasoning_trace=reasoning_trace
            )
    
    def _find_query_entities(self, query: str) -> List[Dict[str, Any]]:
        """Find entities in the knowledge graph that are relevant to the query"""
        entities = []
        query_lower = query.lower()
        
        try:
            with db.driver.session() as session:
                # Search for entities by name/title containing query terms
                result = session.run("""
                    MATCH (n)
                    WHERE 
                        tolower(coalesce(n.name, '')) CONTAINS $query_term OR
                        tolower(coalesce(n.title, '')) CONTAINS $query_term OR
                        tolower(coalesce(n.description, '')) CONTAINS $query_term OR
                        any(keyword IN $query_words WHERE 
                            tolower(coalesce(n.name, '')) CONTAINS keyword OR
                            tolower(coalesce(n.title, '')) CONTAINS keyword
                        )
                    RETURN n, labels(n) as labels, id(n) as node_id
                    LIMIT 20
                """, query_term=query_lower, query_words=query_lower.split())
                
                for record in result:
                    node = dict(record["n"])
                    node["labels"] = record["labels"]
                    node["node_id"] = record["node_id"]
                    entities.append(node)
                
                # Also search for entities based on semantic similarity if we have embeddings
                if not entities:
                    # Fallback: get some entities for semantic matching
                    result = session.run("""
                        MATCH (n)
                        WHERE n.name IS NOT NULL OR n.title IS NOT NULL
                        RETURN n, labels(n) as labels, id(n) as node_id
                        LIMIT 50
                    """)
                    
                    potential_entities = []
                    for record in result:
                        node = dict(record["n"])
                        node["labels"] = record["labels"]
                        node["node_id"] = record["node_id"]
                        potential_entities.append(node)
                    
                    # Use embedding similarity to find relevant entities
                    entities = self._semantic_entity_matching(query, potential_entities)
            
            return entities[:10]  # Limit to top 10 relevant entities
            
        except Exception as e:
            logger.error(f"Error finding query entities: {e}")
            return []
    
    def _semantic_entity_matching(self, query: str, entities: List[Dict]) -> List[Dict]:
        """Use semantic similarity to match query with entities"""
        try:
            if not entities:
                return []
            
            # Create text representations of entities
            entity_texts = []
            for entity in entities:
                text = ""
                if entity.get("name"):
                    text += f"Name: {entity['name']} "
                if entity.get("title"):
                    text += f"Title: {entity['title']} "
                if entity.get("description"):
                    text += f"Description: {entity['description'][:200]} "
                if entity.get("industry"):
                    text += f"Industry: {entity['industry']} "
                entity_texts.append(text.strip())
            
            # Get embeddings
            query_embedding = self.embedding_service.encode([query])
            entity_embeddings = self.embedding_service.encode(entity_texts)
            
            # Calculate similarities
            from sklearn.metrics.pairwise import cosine_similarity
            similarities = cosine_similarity(query_embedding, entity_embeddings)[0]
            
            # Sort by similarity and return top matches
            entity_scores = list(zip(entities, similarities))
            entity_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Return entities with similarity > threshold
            relevant_entities = [entity for entity, score in entity_scores if score > 0.3]
            return relevant_entities[:10]
            
        except Exception as e:
            logger.error(f"Error in semantic entity matching: {e}")
            return entities[:5]  # Fallback to first 5 entities
    
    def _expand_entities_via_graph(self, seed_entities: List[Dict], depth: int = 2) -> List[Dict]:
        """Expand entity set by traversing graph relationships"""
        expanded_entities = {entity["node_id"]: entity for entity in seed_entities}
        current_level = [entity["node_id"] for entity in seed_entities]
        
        try:
            with db.driver.session() as session:
                for level in range(depth):
                    if not current_level:
                        break
                    
                    # Find entities connected to current level
                    result = session.run("""
                        MATCH (n)-[r]-(connected)
                        WHERE id(n) IN $node_ids
                        RETURN connected, labels(connected) as labels, id(connected) as node_id,
                               type(r) as relationship_type, n.name as source_name
                        LIMIT 100
                    """, node_ids=current_level)
                    
                    next_level = []
                    for record in result:
                        connected_id = record["node_id"]
                        if connected_id not in expanded_entities:
                            connected_node = dict(record["connected"])
                            connected_node["labels"] = record["labels"]
                            connected_node["node_id"] = connected_id
                            connected_node["graph_distance"] = level + 1
                            connected_node["source_relationship"] = record["relationship_type"]
                            connected_node["source_entity"] = record["source_name"]
                            
                            expanded_entities[connected_id] = connected_node
                            next_level.append(connected_id)
                    
                    current_level = next_level
            
            return list(expanded_entities.values())
            
        except Exception as e:
            logger.error(f"Error expanding entities via graph: {e}")
            return seed_entities
    
    def _find_knowledge_paths(self, entities: List[Dict]) -> List[Dict]:
        """Find interesting paths between entities in the knowledge graph"""
        paths = []
        
        try:
            entity_ids = [e["node_id"] for e in entities]
            
            with db.driver.session() as session:
                # Find 2-hop paths between entities
                result = session.run("""
                    MATCH path = (a)-[r1]-(intermediate)-[r2]-(b)
                    WHERE id(a) IN $entity_ids AND id(b) IN $entity_ids 
                    AND id(a) < id(b)
                    RETURN 
                        a.name as start_name, 
                        b.name as end_name,
                        intermediate.name as intermediate_name,
                        type(r1) as rel1_type,
                        type(r2) as rel2_type,
                        length(path) as path_length
                    LIMIT 20
                """, entity_ids=entity_ids)
                
                for record in result:
                    path = {
                        "start": record["start_name"],
                        "end": record["end_name"],
                        "intermediate": record["intermediate_name"],
                        "relationships": [record["rel1_type"], record["rel2_type"]],
                        "length": record["path_length"],
                        "path_description": f"{record['start_name']} → {record['rel1_type']} → {record['intermediate_name']} → {record['rel2_type']} → {record['end_name']}"
                    }
                    paths.append(path)
            
            return paths
            
        except Exception as e:
            logger.error(f"Error finding knowledge paths: {e}")
            return []
    
    def _find_entity_documents(self, entities: List[Dict], max_docs: int) -> List[Dict]:
        """Find documents connected to the expanded entities"""
        try:
            # Get entity names for document search
            entity_names = []
            for entity in entities:
                if entity.get("name"):
                    entity_names.append(entity["name"])
                if entity.get("title"):
                    entity_names.append(entity["title"])
            
            if not entity_names:
                return []
            
            # Search documents that mention these entities
            # Create a natural language query from entity names
            entity_query = " ".join(entity_names[:10])  # Join with spaces, not OR
            
            documents = chroma_service.search_documents(
                query=entity_query,
                n_results=max_docs
            )
            
            # Add entity connection information
            for doc in documents:
                doc["connected_entities"] = []
                content = doc.get("content", "").lower()
                for entity in entities:
                    entity_name = (entity.get("name") or entity.get("title", "")).lower()
                    if entity_name and entity_name in content:
                        doc["connected_entities"].append({
                            "name": entity.get("name") or entity.get("title"),
                            "type": entity.get("labels", ["Unknown"])[0],
                            "distance": entity.get("graph_distance", 0)
                        })
            
            return documents
            
        except Exception as e:
            logger.error(f"Error finding entity documents: {e}")
            return []
    
    def _semantic_document_search(self, query: str, max_docs: int) -> List[Dict]:
        """Perform semantic search on documents"""
        try:
            return chroma_service.search_documents(
                query=query,
                n_results=max_docs
            )
        except Exception as e:
            logger.error(f"Error in semantic document search: {e}")
            return []
    
    def _merge_document_sources(self, graph_docs: List[Dict], vector_docs: List[Dict]) -> List[Dict]:
        """Merge documents from graph and vector search, removing duplicates"""
        seen_ids = set()
        merged_docs = []
        
        # Add graph-connected documents first (higher priority)
        for doc in graph_docs:
            doc_id = doc.get("id")
            if doc_id not in seen_ids:
                doc["source_type"] = "graph_connected"
                merged_docs.append(doc)
                seen_ids.add(doc_id)
        
        # Add vector-similar documents
        for doc in vector_docs:
            doc_id = doc.get("id")
            if doc_id not in seen_ids:
                doc["source_type"] = "vector_similar"
                doc["connected_entities"] = []  # Initialize empty
                merged_docs.append(doc)
                seen_ids.add(doc_id)
        
        return merged_docs
    
    def _build_graphrag_context(self, 
                               query: str, 
                               entities: List[Dict], 
                               paths: List[Dict], 
                               documents: List[Dict]) -> str:
        """Build enriched context using graph structure and documents"""
        
        context_parts = [
            f"USER QUERY: {query}",
            "",
            "=== GRAPHRAG ENHANCED CONTEXT ===",
            ""
        ]
        
        # Add knowledge graph entities with relationships
        if entities:
            context_parts.append("KNOWLEDGE GRAPH ENTITIES:")
            for i, entity in enumerate(entities[:15], 1):
                entity_info = f"{i}. {entity.get('name') or entity.get('title', 'Unknown')}"
                if entity.get("labels"):
                    entity_info += f" ({', '.join(entity['labels'])})"
                if entity.get("graph_distance", 0) > 0:
                    entity_info += f" [Distance: {entity['graph_distance']}]"
                if entity.get("source_relationship"):
                    entity_info += f" [Via: {entity['source_relationship']}]"
                
                context_parts.append(entity_info)
                
                if entity.get("description"):
                    context_parts.append(f"   Description: {entity['description'][:200]}")
                if entity.get("industry"):
                    context_parts.append(f"   Industry: {entity['industry']}")
                    
            context_parts.append("")
        
        # Add knowledge paths showing relationships
        if paths:
            context_parts.append("KNOWLEDGE RELATIONSHIPS:")
            for i, path in enumerate(paths[:10], 1):
                context_parts.append(f"{i}. {path['path_description']}")
            context_parts.append("")
        
        # Add documents with entity connections
        if documents:
            context_parts.append("RELEVANT DOCUMENTS:")
            for i, doc in enumerate(documents[:8], 1):
                doc_info = f"{i}. {doc.get('metadata', {}).get('title', f'Document {i}')}"
                if doc.get("source_type"):
                    doc_info += f" [{doc['source_type'].replace('_', ' ').title()}]"
                
                context_parts.append(doc_info)
                
                # Add connected entities
                if doc.get("connected_entities"):
                    entity_names = [e["name"] for e in doc["connected_entities"][:3]]
                    context_parts.append(f"   Connected Entities: {', '.join(entity_names)}")
                
                # Add document content
                content = doc.get("content", "")[:800]
                context_parts.append(f"   Content: {content}...")
                context_parts.append("")
        
        return "\n".join(context_parts)
    
    def _generate_graphrag_answer(self, query: str, context: str) -> str:
        """Generate answer using GraphRAG-enhanced context"""
        
        system_prompt = """You are a GraphRAG assistant that provides comprehensive answers using both document content and knowledge graph relationships.

Your approach:
- Process information from documents and knowledge graph structure
- Synthesize content using entity relationships and document semantics  
- Provide thorough analysis leveraging both structured and unstructured data
- Focus on multi-source information integration and relationship context

Guidelines for GraphRAG responses:
1. MULTI-SOURCE SYNTHESIS: Combine and analyze information from documents and graph relationships
2. RELATIONSHIP-ENHANCED ANALYSIS: Use entity connections to provide enriched context and insights
3. PATTERN IDENTIFICATION: Identify connections and patterns across different information sources
4. COMPREHENSIVE INTEGRATION: Synthesize information using both semantic similarity and graph structure
5. COMPLETE COVERAGE: Provide thorough answers leveraging all available information types
6. CLEAR SOURCE ATTRIBUTION: Reference documents, entities, and relationships in your reasoning

Your goal is to provide the most comprehensive and accurate answer possible using the combined document and graph information."""

        try:
            response = self.llm_service.client.messages.create(
                model=self.llm_service.settings.anthropic_model,
                max_tokens=self.llm_service.settings.max_tokens,
                temperature=self.llm_service.settings.temperature,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": f"Query: {query}\n\nGraphRAG Context:\n{context}\n\nProvide a comprehensive answer leveraging both the document content and knowledge graph relationships:"
                    }
                ]
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Error generating GraphRAG answer: {e}")
            return f"Error generating GraphRAG answer: {str(e)}"
    
    def _extract_graphrag_citations(self, documents: List[Dict], entities: List[Dict]) -> List[Dict]:
        """Extract citations from both documents and knowledge graph entities"""
        citations = []
        seen_sources = set()
        
        # Citations from documents
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
                    "venue": metadata.get("venue"),
                    "doi": metadata.get("doi"),
                    "source_type": doc.get("source_type", "unknown"),
                    "connected_entities": len(doc.get("connected_entities", []))
                }
                citations.append(citation)
                seen_sources.add(title)
        
        # Citations from knowledge graph entities (for attribution)
        for entity in entities[:5]:  # Limit to top 5 entities
            name = entity.get("name") or entity.get("title")
            if name and name not in seen_sources:
                citation = {
                    "source": name,
                    "title": name,
                    "type": "knowledge_graph_entity",
                    "entity_type": entity.get("labels", ["Unknown"])[0] if entity.get("labels") else "Unknown",
                    "graph_distance": entity.get("graph_distance", 0),
                    "source_relationship": entity.get("source_relationship")
                }
                citations.append(citation)
                seen_sources.add(name)
        
        return citations

# Global instance
graphrag_service = GraphRAGService()