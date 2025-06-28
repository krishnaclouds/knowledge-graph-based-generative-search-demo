import logging
import numpy as np
from typing import List, Dict, Any
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from anthropic import Anthropic

from config import get_settings
from database import db
from models import NodeData, SearchResult

logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(self):
        self.settings = get_settings()
        try:
            self.model = SentenceTransformer(self.settings.embedding_model_name)
            logger.info(f"Loaded embedding model: {self.settings.embedding_model_name}")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise
    
    def encode(self, texts: List[str]) -> np.ndarray:
        """Encode texts to embeddings"""
        try:
            return self.model.encode(texts)
        except Exception as e:
            logger.error(f"Failed to encode texts: {e}")
            raise

class LLMService:
    def __init__(self):
        self.settings = get_settings()
        try:
            self.client = Anthropic(api_key=self.settings.anthropic_api_key)
            logger.info("Initialized Anthropic client")
        except Exception as e:
            logger.error(f"Failed to initialize Anthropic client: {e}")
            raise
    
    def generate_answer(self, query: str, context_text: str) -> str:
        """Generate answer using LLM"""
        try:
            response = self.client.messages.create(
                model=self.settings.anthropic_model,
                max_tokens=self.settings.max_tokens,
                temperature=self.settings.temperature,
                system="You are a helpful assistant that answers questions based on the provided knowledge graph information. Use only the information provided and be concise and accurate.",
                messages=[
                    {
                        "role": "user",
                        "content": f"Based on the following knowledge graph information, please answer this question: {query}\\n\\n{context_text}"
                    }
                ]
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Failed to generate answer: {e}")
            return f"Error generating answer: {str(e)}"

class SearchService:
    def __init__(self):
        self.settings = get_settings()
        self.embedding_service = EmbeddingService()
        self.llm_service = LLMService()
    
    def get_node_data_with_embeddings(self) -> tuple[List[NodeData], np.ndarray]:
        """Get all node data and their embeddings"""
        try:
            nodes = db.get_all_nodes()
            
            if not nodes:
                return [], np.array([])
            
            node_data = []
            texts = []
            
            for node in nodes:
                # Build text content for embedding
                text_content = ""
                if node["name"]:
                    text_content += f"Name: {node['name']} "
                if node["title"]:
                    text_content += f"Title: {node['title']} "
                if node["industry"]:
                    text_content += f"Industry: {node['industry']} "
                if node["topic"]:
                    text_content += f"Topic: {node['topic']} "
                
                label = node["labels"][0] if node["labels"] else "Node"
                text_content += f"Type: {label}"
                
                node_obj = NodeData(
                    id=node["id"],
                    text=text_content.strip(),
                    labels=node["labels"],
                    name=node["name"],
                    title=node["title"],
                    industry=node["industry"],
                    topic=node["topic"]
                )
                
                node_data.append(node_obj)
                texts.append(text_content.strip())
            
            embeddings = self.embedding_service.encode(texts)
            return node_data, embeddings
            
        except Exception as e:
            logger.error(f"Failed to get node data with embeddings: {e}")
            raise
    
    def semantic_search(self, query: str, max_results: int = 5) -> List[SearchResult]:
        """Perform semantic search on the knowledge graph"""
        try:
            node_data, embeddings = self.get_node_data_with_embeddings()
            
            if not node_data:
                return []
            
            query_embedding = self.embedding_service.encode([query])
            similarities = cosine_similarity(query_embedding, embeddings)[0]
            
            top_indices = np.argsort(similarities)[::-1][:max_results]
            
            results = []
            for idx in top_indices:
                if similarities[idx] > self.settings.similarity_threshold:
                    results.append(SearchResult(
                        node=node_data[idx],
                        similarity=float(similarities[idx])
                    ))
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to perform semantic search: {e}")
            raise
    
    def build_context_text(self, search_results: List[SearchResult]) -> str:
        """Build context text from search results"""
        if not search_results:
            return ""
        
        context_text = "Knowledge Graph Information:\\n\\n"
        
        for i, result in enumerate(search_results, 1):
            node = result.node
            similarity = result.similarity
            
            context_text += f"{i}. {node.text} (Relevance: {similarity:.2f})\\n"
            
            try:
                node_context = db.get_node_context(node.id)
                if node_context["relationships"]:
                    context_text += "   Relationships:\\n"
                    for rel in node_context["relationships"]:
                        rel_text = f"   - {rel['type']}: "
                        connected = rel["connected_node"]
                        if 'name' in connected:
                            rel_text += connected['name']
                        elif 'title' in connected:
                            rel_text += connected['title']
                        context_text += rel_text + "\\n"
                context_text += "\\n"
            except Exception as e:
                logger.warning(f"Failed to get context for node {node.id}: {e}")
                context_text += "\\n"
        
        return context_text
    
    def search_and_answer(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """Perform search and generate answer"""
        try:
            search_results = self.semantic_search(query, max_results)
            
            if not search_results:
                return {
                    "query": query,
                    "results": [],
                    "answer": "No relevant information found in the knowledge graph."
                }
            
            context_text = self.build_context_text(search_results)
            answer = self.llm_service.generate_answer(query, context_text)
            
            return {
                "query": query,
                "results": [result.dict() for result in search_results],
                "answer": answer
            }
            
        except Exception as e:
            logger.error(f"Failed to search and answer: {e}")
            raise

# Global service instances
search_service = SearchService()