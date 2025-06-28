#!/usr/bin/env python3
"""
Simple investigation of negative relevance scores without complex imports
"""
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def investigate_cosine_similarity():
    """Investigate how cosine similarity can produce negative values"""
    print("="*60)
    print("INVESTIGATING COSINE SIMILARITY AND NEGATIVE SCORES")
    print("="*60)
    
    # Create sample embeddings to demonstrate negative cosine similarity
    np.random.seed(42)
    
    # Example 1: Completely opposite vectors (should give -1)
    vec_a = np.array([1, 1, 1, 1]).reshape(1, -1)
    vec_b = np.array([-1, -1, -1, -1]).reshape(1, -1)
    sim = cosine_similarity(vec_a, vec_b)[0][0]
    print(f"Example 1 - Opposite vectors: {sim:.4f}")
    
    # Example 2: Perpendicular vectors (should give 0)
    vec_a = np.array([1, 0, 0, 0]).reshape(1, -1)
    vec_b = np.array([0, 1, 0, 0]).reshape(1, -1)
    sim = cosine_similarity(vec_a, vec_b)[0][0]
    print(f"Example 2 - Perpendicular vectors: {sim:.4f}")
    
    # Example 3: Similar vectors (should give positive value close to 1)
    vec_a = np.array([1, 1, 1, 1]).reshape(1, -1)
    vec_b = np.array([0.9, 0.8, 1.1, 0.7]).reshape(1, -1)
    sim = cosine_similarity(vec_a, vec_b)[0][0]
    print(f"Example 3 - Similar vectors: {sim:.4f}")
    
    # Example 4: Random high-dimensional vectors (common in embeddings)
    dim = 384  # Similar to sentence transformer dimensions
    vec_query = np.random.randn(1, dim)
    
    print(f"\nTesting with {dim}-dimensional random vectors:")
    similarities = []
    for i in range(1000):
        vec_doc = np.random.randn(1, dim)
        sim = cosine_similarity(vec_query, vec_doc)[0][0]
        similarities.append(sim)
    
    similarities = np.array(similarities)
    print(f"Random similarity range: {similarities.min():.4f} to {similarities.max():.4f}")
    print(f"Mean similarity: {similarities.mean():.4f}")
    print(f"Std similarity: {similarities.std():.4f}")
    
    negative_count = np.sum(similarities < 0)
    print(f"Negative similarities: {negative_count}/1000 ({negative_count/10:.1f}%)")
    
    return similarities

def investigate_distance_to_similarity_conversion():
    """Investigate how distances are converted to similarities in ChromaDB"""
    print("\n" + "="*60)
    print("INVESTIGATING DISTANCE TO SIMILARITY CONVERSION")
    print("="*60)
    
    # ChromaDB typically uses cosine distance
    # Cosine distance = 1 - cosine similarity
    # So cosine similarity = 1 - cosine distance
    
    print("ChromaDB distance conversion formulas:")
    print("- Cosine distance = 1 - cosine_similarity")
    print("- Cosine similarity = 1 - cosine_distance")
    print()
    
    # Test various distance values
    test_distances = [0.0, 0.5, 1.0, 1.5, 2.0]
    
    print("Distance -> Similarity conversion examples:")
    for dist in test_distances:
        similarity = 1 - dist
        print(f"Distance {dist:.1f} -> Similarity {similarity:.1f}")
    
    print("\nKey insight: Distances > 1.0 will result in negative similarities!")
    print("This happens when cosine similarity between vectors is negative.")
    
    # Demonstrate with actual vectors
    print("\nDemonstration with vectors:")
    vec_a = np.array([1, 1]).reshape(1, -1)
    vec_b = np.array([-1, -1]).reshape(1, -1)
    
    cos_sim = cosine_similarity(vec_a, vec_b)[0][0]
    cos_dist = 1 - cos_sim
    recovered_sim = 1 - cos_dist
    
    print(f"Vector A: {vec_a.flatten()}")
    print(f"Vector B: {vec_b.flatten()}")
    print(f"Cosine similarity: {cos_sim:.4f}")
    print(f"Cosine distance: {cos_dist:.4f}")
    print(f"Recovered similarity (1 - distance): {recovered_sim:.4f}")

def analyze_potential_causes():
    """Analyze potential causes of negative relevance scores"""
    print("\n" + "="*60)
    print("ANALYZING POTENTIAL CAUSES OF NEGATIVE SCORES")
    print("="*60)
    
    causes = [
        {
            "cause": "Semantic Mismatch",
            "description": "Query and document embeddings point in completely different directions",
            "example": "Query: 'AI Investment' vs Document: 'Cooking recipes'",
            "likelihood": "High - very common with diverse content"
        },
        {
            "cause": "Embedding Model Limitations", 
            "description": "all-MiniLM-L6-v2 may not capture investment domain well",
            "example": "Technical AI terms vs business investment terms",
            "likelihood": "Medium - model may lack domain-specific training"
        },
        {
            "cause": "Text Preprocessing Issues",
            "description": "Poor text quality or preprocessing artifacts",
            "example": "Malformed text, special characters, encoding issues",
            "likelihood": "Low - but possible"
        },
        {
            "cause": "Normal Cosine Similarity Behavior",
            "description": "Negative cosine similarity is mathematically normal",
            "example": "Vectors in opposite directions naturally give negative scores",
            "likelihood": "High - this is expected behavior"
        }
    ]
    
    for i, cause in enumerate(causes, 1):
        print(f"{i}. {cause['cause']}")
        print(f"   Description: {cause['description']}")
        print(f"   Example: {cause['example']}")
        print(f"   Likelihood: {cause['likelihood']}")
        print()

def recommend_solutions():
    """Recommend solutions for handling negative relevance scores"""
    print("="*60)
    print("RECOMMENDED SOLUTIONS")
    print("="*60)
    
    solutions = [
        {
            "solution": "Adjust Similarity Threshold",
            "description": "Lower the similarity_threshold from 0.1 to 0.0 or even negative",
            "implementation": "Change SIMILARITY_THRESHOLD in config from 0.1 to 0.0",
            "pros": "Simple fix, allows some negative scores through",
            "cons": "May include irrelevant results"
        },
        {
            "solution": "Score Normalization", 
            "description": "Transform scores to positive range using min-max scaling",
            "implementation": "Apply (score - min_score) / (max_score - min_score)",
            "pros": "All scores become positive, maintains relative ranking", 
            "cons": "Loses absolute meaning of similarity"
        },
        {
            "solution": "Alternative Similarity Metrics",
            "description": "Use dot product or euclidean distance instead of cosine",
            "implementation": "Modify similarity calculation in services.py",
            "pros": "Different mathematical properties",
            "cons": "May not align with embedding model training"
        },
        {
            "solution": "Domain-Specific Embedding Model",
            "description": "Use a model trained on financial/investment data",
            "implementation": "Change EMBEDDING_MODEL_NAME to finance-specific model",
            "pros": "Better semantic understanding of investment terms",
            "cons": "May require model research and testing"
        },
        {
            "solution": "Score Post-Processing",
            "description": "Apply sigmoid/softmax to compress scores to [0,1] range",
            "implementation": "Add score transformation in search functions",
            "pros": "Smooth positive-only scores",
            "cons": "Changes score interpretation"
        }
    ]
    
    for i, sol in enumerate(solutions, 1):
        print(f"{i}. {sol['solution']}")
        print(f"   Description: {sol['description']}")
        print(f"   Implementation: {sol['implementation']}")
        print(f"   Pros: {sol['pros']}")
        print(f"   Cons: {sol['cons']}")
        print()

def main():
    """Main investigation function"""
    print("INVESTIGATING NEGATIVE RELEVANCE SCORES IN AI INVESTMENT STRATEGY SEARCHES")
    print("="*80)
    
    # Run investigations
    similarities = investigate_cosine_similarity()
    investigate_distance_to_similarity_conversion()
    analyze_potential_causes()
    recommend_solutions()
    
    print("\n" + "="*80)
    print("CONCLUSION")
    print("="*80)
    print("""
Negative relevance scores are NORMAL and EXPECTED behavior in cosine similarity:

1. Cosine similarity ranges from -1 to +1
2. Negative values indicate semantic opposition/dissimilarity  
3. ChromaDB converts: similarity = 1 - distance
4. When cosine similarity < 0, distance > 1, resulting in negative converted similarity

For "AI Investment strategy" searches:
- Documents about unrelated topics (cooking, sports, etc.) will have negative scores
- This indicates the search is working correctly by identifying irrelevant content
- The similarity_threshold of 0.1 filters out most negative scores

RECOMMENDED ACTION:
- Lower similarity_threshold to 0.0 or -0.1 to include some negatively-scored results
- This will provide more search results while maintaining relevance ranking
""")

if __name__ == "__main__":
    main()