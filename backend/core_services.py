"""
Core services for the GraphRAG vs Traditional RAG comparison system.
Contains essential LLM and embedding services.
"""

import logging
import os
from typing import List, Optional
from sentence_transformers import SentenceTransformer
import anthropic
from config import get_settings

logger = logging.getLogger(__name__)

class EmbeddingService:
    """Service for converting text to embeddings using SentenceTransformers"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._model = None
        logger.info(f"Initialized EmbeddingService with model: {model_name}")
    
    @property
    def model(self):
        """Lazy load the embedding model"""
        if self._model is None:
            logger.info(f"Loading embedding model: {self.model_name}")
            self._model = SentenceTransformer(self.model_name)
        return self._model
    
    def encode(self, texts: List[str]) -> List[List[float]]:
        """Convert texts to embeddings"""
        try:
            embeddings = self.model.encode(texts, convert_to_tensor=False)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Failed to encode texts: {e}")
            raise

class LLMService:
    """Service for interacting with Anthropic's Claude LLM"""
    
    def __init__(self):
        self.settings = get_settings()
        self.api_key = self.settings.anthropic_api_key
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")
        
        self.client = anthropic.Anthropic(api_key=self.api_key)
        logger.info("Initialized LLMService with Anthropic Claude")
    
    def generate_answer(self, query: str, context: str, max_tokens: Optional[int] = None) -> str:
        """Generate an answer using Claude based on query and context"""
        try:
            # Use settings defaults if not provided
            if max_tokens is None:
                max_tokens = self.settings.max_tokens
            
            prompt = f"""Based on the following context, please provide a comprehensive answer to the user's question.

Context:
{context}

Question: {query}

Please provide a well-structured, informative answer based on the context provided. If the context doesn't contain enough information to fully answer the question, acknowledge this limitation."""

            response = self.client.messages.create(
                model=self.settings.anthropic_model,
                max_tokens=max_tokens,
                temperature=self.settings.temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return response.content[0].text if response.content else "No response generated"
            
        except Exception as e:
            logger.error(f"Failed to generate answer: {e}")
            return f"Error generating answer: {str(e)}"

# Global instances for easy import
embedding_service = EmbeddingService()
llm_service = LLMService()