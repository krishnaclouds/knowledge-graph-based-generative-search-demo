import logging
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
import uuid
import os

from config import get_settings

logger = logging.getLogger(__name__)

class ChromaDBService:
    def __init__(self):
        self.settings = get_settings()
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path="./chroma_db",
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer(self.settings.embedding_model_name)
        
        # Create or get collection
        self.collection = self.client.get_or_create_collection(
            name="documents",
            embedding_function=self._get_embedding_function()
        )
        
        logger.info("ChromaDB service initialized")
    
    def _get_embedding_function(self):
        """Create embedding function for ChromaDB"""
        class SentenceTransformerEmbeddings:
            def __init__(self, model):
                self.model = model
            
            def __call__(self, input: List[str]) -> List[List[float]]:
                embeddings = self.model.encode(input)
                return embeddings.tolist()
            
            def name(self) -> str:
                return "sentence-transformers"
        
        return SentenceTransformerEmbeddings(self.embedding_model)
    
    def add_document(self, 
                    title: str,
                    content: str,
                    metadata: Dict[str, Any],
                    doc_id: Optional[str] = None) -> str:
        """Add a document to ChromaDB"""
        try:
            if doc_id is None:
                doc_id = str(uuid.uuid4())
            
            # Prepare metadata
            doc_metadata = {
                "title": title,
                "type": metadata.get("type", "document"),
                "source": metadata.get("source", "unknown"),
                **metadata
            }
            
            # Add to collection
            self.collection.add(
                documents=[content],
                metadatas=[doc_metadata],
                ids=[doc_id]
            )
            
            logger.info(f"Added document: {title}")
            return doc_id
            
        except Exception as e:
            logger.error(f"Failed to add document {title}: {e}")
            raise
    
    def search_documents(self, 
                        query: str, 
                        n_results: int = 10,
                        where: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Search documents in ChromaDB"""
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where
            )
            
            # Format results
            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for i in range(len(results['documents'][0])):
                    formatted_results.append({
                        'id': results['ids'][0][i],
                        'content': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i],
                        'distance': results['distances'][0][i] if results['distances'] else None,
                        'similarity': 1 - results['distances'][0][i] if results['distances'] else None
                    })
            
            logger.info(f"Found {len(formatted_results)} documents for query: {query}")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Failed to search documents: {e}")
            raise
    
    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific document by ID"""
        try:
            results = self.collection.get(ids=[doc_id])
            
            if results['documents']:
                return {
                    'id': results['ids'][0],
                    'content': results['documents'][0],
                    'metadata': results['metadatas'][0]
                }
            return None
            
        except Exception as e:
            logger.error(f"Failed to get document {doc_id}: {e}")
            return None
    
    def delete_document(self, doc_id: str) -> bool:
        """Delete a document from ChromaDB"""
        try:
            self.collection.delete(ids=[doc_id])
            logger.info(f"Deleted document: {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete document {doc_id}: {e}")
            return False
    
    def clear_collection(self) -> bool:
        """Clear all documents from the collection"""
        try:
            self.client.delete_collection("documents")
            self.collection = self.client.get_or_create_collection(
                name="documents",
                embedding_function=self._get_embedding_function()
            )
            logger.info("Cleared ChromaDB collection")
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear collection: {e}")
            return False
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection"""
        try:
            count = self.collection.count()
            return {
                "document_count": count,
                "collection_name": "documents"
            }
            
        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            return {"document_count": 0, "collection_name": "documents"}

# Global instance
chroma_service = ChromaDBService()