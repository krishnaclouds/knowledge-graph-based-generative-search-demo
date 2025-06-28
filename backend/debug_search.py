#!/usr/bin/env python3
"""
Debug script to investigate negative relevance scores for "AI Investment strategy" searches
"""
import logging
import numpy as np
from dotenv import load_dotenv
load_dotenv()

from services import search_service
from vector_store import chroma_service
from hybrid_search import hybrid_search_service
from config import get_settings

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_search_query(query: str):
    """Test a search query and examine the scoring details"""
    print(f"\n{'='*60}")
    print(f"TESTING QUERY: '{query}'")
    print(f"{'='*60}")
    
    settings = get_settings()
    print(f"Similarity threshold: {settings.similarity_threshold}")
    print(f"Embedding model: {settings.embedding_model_name}")
    
    try:
        # Test document search in ChromaDB
        print("\n--- ChromaDB Document Search ---")
        doc_results = chroma_service.search_documents(query=query, n_results=10)
        print(f"Found {len(doc_results)} documents")
        
        for i, doc in enumerate(doc_results[:5]):
            distance = doc.get('distance', 'N/A')
            similarity = doc.get('similarity', 'N/A')
            print(f"{i+1}. Title: {doc['metadata'].get('title', 'Untitled')}")
            print(f"   Distance: {distance}")
            print(f"   Similarity: {similarity}")
            print(f"   Content preview: {doc['content'][:100]}...")
            print()
        
        # Test Neo4j knowledge graph search
        print("\n--- Neo4j Knowledge Graph Search ---")
        kg_results = search_service.semantic_search(query=query, max_results=10)
        print(f"Found {len(kg_results)} knowledge graph results")
        
        for i, result in enumerate(kg_results[:5]):
            print(f"{i+1}. Node: {result.node.name or result.node.title or 'Unnamed'}")
            print(f"   Labels: {result.node.labels}")
            print(f"   Similarity: {result.similarity}")
            print(f"   Text preview: {result.node.text[:100]}...")
            print()
        
        # Test hybrid search
        print("\n--- Hybrid Search ---")
        hybrid_results = hybrid_search_service.hybrid_search(query=query, max_results=10)
        print(f"Found {len(hybrid_results)} hybrid results")
        
        for i, result in enumerate(hybrid_results[:5]):
            print(f"{i+1}. Title: {result.title}")
            print(f"   Similarity: {result.similarity}")
            print(f"   Related entities: {result.related_entities}")
            print(f"   Content preview: {result.content[:100]}...")
            print()
            
    except Exception as e:
        logger.error(f"Error during search testing: {e}", exc_info=True)

def debug_embedding_similarity():
    """Debug the embedding similarity calculation process"""
    print(f"\n{'='*60}")
    print("DEBUGGING EMBEDDING SIMILARITY CALCULATION")
    print(f"{'='*60}")
    
    query = "AI Investment strategy"
    
    try:
        # Get embeddings directly
        embedding_service = search_service.embedding_service
        
        # Test query embedding
        query_embedding = embedding_service.encode([query])
        print(f"Query embedding shape: {query_embedding.shape}")
        print(f"Query embedding sample values: {query_embedding[0][:10]}")
        
        # Get some sample documents and their embeddings
        node_data, embeddings = search_service.get_node_data_with_embeddings()
        if embeddings.size > 0:
            print(f"Node embeddings shape: {embeddings.shape}")
            print(f"Number of nodes: {len(node_data)}")
            
            # Calculate similarities manually
            from sklearn.metrics.pairwise import cosine_similarity
            similarities = cosine_similarity(query_embedding, embeddings)[0]
            
            print(f"Similarity scores range: {similarities.min():.4f} to {similarities.max():.4f}")
            print(f"Similarity scores mean: {similarities.mean():.4f}")
            print(f"Similarity scores std: {similarities.std():.4f}")
            
            # Show top 10 similarities
            top_indices = np.argsort(similarities)[::-1][:10]
            print("\nTop 10 similarity scores:")
            for i, idx in enumerate(top_indices):
                node = node_data[idx]
                print(f"{i+1}. Score: {similarities[idx]:.4f} - {node.name or node.title or 'Unnamed'}")
                
            # Show bottom 10 similarities 
            bottom_indices = np.argsort(similarities)[:10]
            print("\nBottom 10 similarity scores (potential negatives):")
            for i, idx in enumerate(bottom_indices):
                node = node_data[idx]
                print(f"{i+1}. Score: {similarities[idx]:.4f} - {node.name or node.title or 'Unnamed'}")
                
            # Check for negative scores
            negative_scores = similarities[similarities < 0]
            if len(negative_scores) > 0:
                print(f"\nFound {len(negative_scores)} negative similarity scores!")
                print(f"Most negative: {negative_scores.min():.4f}")
                print(f"Negative scores: {negative_scores[:10]}")
                
                # Show nodes with negative scores
                negative_indices = np.where(similarities < 0)[0]
                print("\nNodes with negative scores:")
                for i, idx in enumerate(negative_indices[:5]):
                    node = node_data[idx]
                    print(f"{i+1}. Score: {similarities[idx]:.4f}")
                    print(f"   Node: {node.name or node.title or 'Unnamed'}")
                    print(f"   Labels: {node.labels}")
                    print(f"   Text: {node.text[:200]}...")
                    print()
            else:
                print("\nNo negative similarity scores found.")
                
    except Exception as e:
        logger.error(f"Error during embedding debugging: {e}", exc_info=True)

def test_chroma_search_directly():
    """Test ChromaDB search directly to see raw scores"""
    print(f"\n{'='*60}")
    print("TESTING CHROMADB SEARCH DIRECTLY")  
    print(f"{'='*60}")
    
    query = "AI Investment strategy"
    
    try:
        # Get collection stats
        stats = chroma_service.get_collection_stats()
        print(f"Collection stats: {stats}")
        
        # Query the collection directly with more details
        collection = chroma_service.collection
        results = collection.query(
            query_texts=[query],
            n_results=10,
            include=["metadatas", "documents", "distances"]
        )
        
        print(f"Raw ChromaDB results structure:")
        print(f"- IDs: {len(results.get('ids', [[]]))}") 
        print(f"- Documents: {len(results.get('documents', [[]]))}") 
        print(f"- Distances: {len(results.get('distances', [[]]))}") 
        print(f"- Metadatas: {len(results.get('metadatas', [[]]))}") 
        
        if results.get('distances') and results['distances'][0]:
            distances = results['distances'][0]
            print(f"\nDistance scores: {distances}")
            print(f"Distance range: {min(distances):.4f} to {max(distances):.4f}")
            
            # Convert distances to similarities (ChromaDB typically uses cosine distance)
            similarities = [1 - d for d in distances]
            print(f"Converted similarities: {similarities}")
            print(f"Similarity range: {min(similarities):.4f} to {max(similarities):.4f}")
            
            # Check for negative similarities
            negative_sims = [s for s in similarities if s < 0]
            if negative_sims:
                print(f"Found {len(negative_sims)} negative similarities: {negative_sims}")
            
        # Show document details
        if results.get('documents') and results['documents'][0]:
            print(f"\nDocument results:")
            for i, (doc, meta, dist) in enumerate(zip(
                results['documents'][0][:5], 
                results['metadatas'][0][:5], 
                results['distances'][0][:5]
            )):
                sim = 1 - dist
                print(f"{i+1}. Distance: {dist:.4f}, Similarity: {sim:.4f}")
                print(f"   Title: {meta.get('title', 'Untitled')}")
                print(f"   Content: {doc[:100]}...")
                print()
                
    except Exception as e:
        logger.error(f"Error during ChromaDB direct testing: {e}", exc_info=True)

def main():
    """Main debugging function"""
    print("Starting search debugging for negative relevance scores...")
    
    # Test queries
    test_queries = [
        "AI Investment strategy",
        "artificial intelligence investment",
        "technology investment strategy", 
        "investment in AI companies",
        "machine learning investment"
    ]
    
    for query in test_queries:
        test_search_query(query)
    
    # Debug embedding similarity calculation
    debug_embedding_similarity()
    
    # Test ChromaDB directly
    test_chroma_search_directly()
    
    print("\nDebugging complete!")

if __name__ == "__main__":
    main()