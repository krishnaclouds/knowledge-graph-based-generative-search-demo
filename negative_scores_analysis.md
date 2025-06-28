# Analysis: Negative Relevance Scores for "AI Investment Strategy" Searches

## Executive Summary

The negative relevance scores for "AI Investment strategy" search strings are **normal and expected behavior** in the current implementation. This is not a bug but rather the mathematical result of cosine similarity calculations when query and document embeddings are semantically dissimilar.

## Root Cause Analysis

### 1. Mathematical Foundation

**Cosine Similarity Range**: -1 to +1
- **+1**: Vectors point in exactly the same direction (perfect similarity)
- **0**: Vectors are perpendicular (no similarity)
- **-1**: Vectors point in opposite directions (perfect dissimilarity)

**Current Implementation**:
```python
# In services.py (line 152)
similarities = cosine_similarity(query_embedding, embeddings)[0]

# In vector_store.py (line 102) 
'similarity': 1 - results['distances'][0][i] if results['distances'] else None
```

### 2. Where Negative Scores Occur

#### Neo4j Knowledge Graph Search (`services.py`)
- **Direct cosine similarity calculation** between query and node embeddings
- **Filtering**: Only results with `similarity > 0.1` are returned (line 158)
- **Issue**: Many legitimate results with negative similarities are filtered out

#### ChromaDB Document Search (`vector_store.py`)
- **Distance-to-similarity conversion**: `similarity = 1 - distance`
- When cosine similarity < 0, distance > 1, resulting in negative converted similarity
- **No similarity threshold filtering** applied in ChromaDB search

### 3. Current Data and Configuration

**Similarity Threshold**: 0.1 (set in `config.py` line 23)
**Embedding Model**: `all-MiniLM-L6-v2` (general-purpose model)

**Sample Data Analysis**:
- **Neo4j**: Contains companies, people, documents, topics (tech, AI, etc.)
- **ChromaDB**: Contains investment strategy documents from major tech companies
- **Content variety**: Mix of technical AI content and business investment content

## Impact Analysis

### Query: "AI Investment strategy"

**Expected Similarity Distribution**:
- **High positive** (0.3-0.8): Investment strategy documents, AI company information
- **Low positive** (0.0-0.3): Tangentially related tech content
- **Negative** (-0.5-0.0): Unrelated content (cooking recipes, sports, etc.)

**Current Filtering Effect**:
- **Neo4j Search**: Filters out ALL negative scores and most low-positive scores (threshold 0.1)
- **ChromaDB Search**: Returns negative scores but they appear as "negative relevance"
- **Result**: Limited search results, especially for diverse query terms

## Technical Evidence

### Cosine Similarity Behavior (from investigation)
```
Random 384-dimensional vectors:
- Similarity range: -0.1725 to 0.1657
- Mean similarity: 0.0003
- Negative similarities: 484/1000 (48.4%)
```

### Distance Conversion Examples
```
Distance 0.0 -> Similarity 1.0   (perfect match)
Distance 0.5 -> Similarity 0.5   (good match)  
Distance 1.0 -> Similarity 0.0   (no similarity)
Distance 1.5 -> Similarity -0.5  (dissimilar)
Distance 2.0 -> Similarity -1.0  (opposite)
```

## Recommendations

### 1. Immediate Fix: Adjust Similarity Threshold

**Change in `config.py`**:
```python
# Current
similarity_threshold: float = Field(default=0.1, env="SIMILARITY_THRESHOLD")

# Recommended
similarity_threshold: float = Field(default=0.0, env="SIMILARITY_THRESHOLD")
# Or even: default=-0.1 for more inclusive results
```

**Benefits**: 
- More search results returned
- Maintains relative ranking
- Simple implementation

### 2. Score Normalization (Recommended)

**Implementation in `services.py`**:
```python
def normalize_similarities(similarities):
    """Normalize similarities to [0, 1] range"""
    min_sim = similarities.min()
    max_sim = similarities.max()
    if max_sim > min_sim:
        return (similarities - min_sim) / (max_sim - min_sim)
    return similarities

# Apply after cosine similarity calculation
similarities = cosine_similarity(query_embedding, embeddings)[0]
similarities = normalize_similarities(similarities)
```

### 3. Enhanced Scoring Strategy

**Hybrid approach**:
```python
def enhanced_similarity_score(cosine_sim, query, document_text):
    """Enhanced scoring combining cosine similarity with other factors"""
    base_score = cosine_sim
    
    # Apply sigmoid to compress range to (0, 1)
    sigmoid_score = 1 / (1 + np.exp(-base_score * 5))
    
    # Optional: Add keyword boost
    keyword_boost = calculate_keyword_overlap(query, document_text)
    
    return sigmoid_score + (keyword_boost * 0.1)
```

### 4. Domain-Specific Embedding Model

**Alternative models for investment/finance domain**:
- `sentence-transformers/all-mpnet-base-v2` (better general performance)
- `ProsusAI/finbert` (finance-specific)
- `msmarco-distilbert-base-v4` (passage retrieval optimized)

### 5. Query Expansion

**Improve search recall**:
```python
def expand_investment_query(query):
    """Expand investment-related queries with synonyms"""
    expansions = {
        "investment": ["funding", "capital", "financing", "venture"],
        "strategy": ["plan", "approach", "roadmap", "framework"],
        "AI": ["artificial intelligence", "machine learning", "ML"]
    }
    # Implementation to expand query terms
```

## Implementation Priority

### Phase 1: Quick Fix (High Priority)
1. **Lower similarity threshold** to 0.0 or -0.1
2. **Test with "AI Investment strategy"** queries
3. **Monitor result quality** and user feedback

### Phase 2: Enhanced Scoring (Medium Priority)  
1. **Implement score normalization** 
2. **Add sigmoid transformation** for positive-only scores
3. **A/B test** against current implementation

### Phase 3: Advanced Improvements (Low Priority)
1. **Evaluate domain-specific embedding models**
2. **Implement query expansion**
3. **Add learning-based relevance feedback**

## Validation Tests

### Test Queries
```python
test_queries = [
    "AI Investment strategy",
    "artificial intelligence investment",  
    "technology investment strategy",
    "machine learning funding",
    "venture capital AI companies"
]
```

### Expected Improvements
- **Increased recall**: More relevant results returned
- **Maintained precision**: Top results still highly relevant  
- **Better user experience**: No more "no results found" for valid queries

## Conclusion

Negative relevance scores are a **mathematical feature, not a bug**. The current filtering is too restrictive for the investment domain where content diversity creates natural semantic distance. 

**Recommended immediate action**: Lower the similarity threshold to 0.0 to include more results while maintaining relevance ranking.

**Long-term recommendation**: Implement score normalization and consider domain-specific embedding models for better investment query handling.