"""
Comprehensive evaluation queries for GraphRAG vs Traditional RAG comparison
"""

# Categories of evaluation queries based on available data
EVALUATION_QUERIES = {
    "ai_ml_research": [
        "What are the latest developments in transformer neural networks?",
        "How do large language models handle multimodal inputs?",
        "What are the current challenges in neural machine translation?",
        "How has attention mechanism evolved in deep learning?",
        "What are the key innovations in BERT and its variants?",
        "How do graph neural networks differ from traditional neural networks?",
        "What are the recent advances in computer vision for autonomous vehicles?",
        "How is reinforcement learning being applied to robotics?",
        "What are the latest techniques in natural language processing?",
        "How do generative adversarial networks work in practice?",
        "What are the current limitations of deep learning models?",
        "How is federated learning changing machine learning deployment?",
        "What are the key principles behind retrieval augmented generation?",
        "How do knowledge graphs enhance information retrieval?",
        "What are the latest developments in quantum machine learning?",
        "How is AI being used for drug discovery and healthcare?",
        "What are the current approaches to AI safety and alignment?",
        "How do neural networks process sequential data?",
        "What are the key challenges in scaling deep learning models?",
        "How is artificial intelligence being applied to climate change?",
    ],
    
    "company_technology": [
        "How is Google advancing artificial intelligence research?",
        "What AI technologies is Microsoft developing?",
        "How does Apple integrate machine learning into its products?",
        "What are Amazon's key contributions to cloud computing?",
        "How is Meta approaching virtual and augmented reality?",
        "What role does NVIDIA play in AI hardware acceleration?",
        "How is Tesla advancing autonomous driving technology?",
        "What are IBM's key innovations in quantum computing?",
        "How is OpenAI contributing to large language model research?",
        "What technologies is Salesforce developing for business automation?",
        "How does Oracle's cloud infrastructure support AI workloads?",
        "What are Intel's contributions to AI chip development?",
        "How is LinkedIn using AI for professional networking?",
        "What are Twitter's approaches to content moderation using AI?",
        "How does Uber use machine learning for ride optimization?",
        "What are the key partnerships between tech companies in AI?",
        "How do tech companies approach AI ethics and responsibility?",
        "What are the competitive advantages of different AI platforms?",
        "How do companies balance innovation with privacy in AI?",
        "What are the emerging trends in enterprise AI adoption?",
    ],
    
    "cross_domain_connections": [
        "How is machine learning being applied in healthcare diagnostics?",
        "What role does AI play in financial fraud detection?",
        "How are autonomous vehicles using computer vision?",
        "What are the applications of NLP in customer service?",
        "How is blockchain technology being integrated with AI?",
        "What are the connections between quantum computing and machine learning?",
        "How does IoT benefit from artificial intelligence?",
        "What are the applications of AI in cybersecurity?",
        "How is machine learning transforming software engineering?",
        "What role does AI play in renewable energy optimization?",
        "How are robotics and AI converging in manufacturing?",
        "What are the applications of AI in education technology?",
        "How is computer vision being used in agriculture?",
        "What are the connections between AI and biotechnology?",
        "How does AI enhance cloud computing services?",
        "What are the applications of machine learning in gaming?",
        "How is AI being used for environmental monitoring?",
        "What role does machine learning play in supply chain optimization?",
        "How are AI and 5G technologies complementing each other?",
        "What are the applications of AI in content creation?",
    ],
    
    "research_trends": [
        "What are the emerging trends in neural architecture search?",
        "How is explainable AI developing as a research field?",
        "What are the latest developments in few-shot learning?",
        "How is transfer learning evolving in deep learning?",
        "What are the current trends in multimodal AI research?",
        "How is continual learning being addressed in machine learning?",
        "What are the latest approaches to adversarial robustness?",
        "How is meta-learning changing machine learning paradigms?",
        "What are the current trends in automated machine learning?",
        "How is differential privacy being integrated into ML systems?",
        "What are the latest developments in neural-symbolic integration?",
        "How is causal inference being applied in machine learning?",
        "What are the emerging trends in self-supervised learning?",
        "How is human-AI collaboration being researched?",
        "What are the latest developments in graph machine learning?",
        "How is uncertainty quantification being addressed in deep learning?",
        "What are the current trends in AI for scientific discovery?",
        "How is online learning evolving in machine learning?",
        "What are the latest approaches to model compression?",
        "How is edge AI being researched and developed?",
    ],
    
    "technical_deep_dive": [
        "How do transformer architectures handle long sequence dependencies?",
        "What are the mathematical foundations of backpropagation?",
        "How do convolutional neural networks process image data?",
        "What are the key components of a recommendation system?",
        "How do recurrent neural networks maintain temporal dependencies?",
        "What are the optimization techniques used in deep learning?",
        "How do attention mechanisms work in neural networks?",
        "What are the key differences between supervised and unsupervised learning?",
        "How do ensemble methods improve machine learning performance?",
        "What are the principles behind dimensionality reduction techniques?",
        "How do regularization techniques prevent overfitting?",
        "What are the key concepts in information theory for ML?",
        "How do probabilistic graphical models represent uncertainty?",
        "What are the foundations of reinforcement learning algorithms?",
        "How do kernel methods work in machine learning?",
        "What are the key principles of feature engineering?",
        "How do batch normalization techniques improve training?",
        "What are the mathematical foundations of neural networks?",
        "How do gradient descent variants optimize neural networks?",
        "What are the key concepts in representation learning?",
    ],
    
    "industry_applications": [
        "How is AI transforming the healthcare industry?",
        "What are the applications of machine learning in finance?",
        "How is computer vision being used in retail?",
        "What role does AI play in manufacturing automation?",
        "How is natural language processing changing customer service?",
        "What are the applications of AI in transportation?",
        "How is machine learning being used in energy management?",
        "What role does AI play in agricultural optimization?",
        "How is computer vision transforming security systems?",
        "What are the applications of AI in media and entertainment?",
        "How is machine learning being used in telecommunications?",
        "What role does AI play in real estate technology?",
        "How is natural language processing being used in legal tech?",
        "What are the applications of AI in sports analytics?",
        "How is computer vision being used in quality control?",
        "What role does AI play in environmental monitoring?",
        "How is machine learning transforming logistics?",
        "What are the applications of AI in personalization?",
        "How is computer vision being used in autonomous systems?",
        "What role does AI play in predictive maintenance?",
    ],
    
    "comparative_analysis": [
        "What are the advantages of GraphRAG over traditional RAG?",
        "How do different neural network architectures compare?",
        "What are the trade-offs between accuracy and interpretability?",
        "How do supervised and unsupervised learning methods compare?",
        "What are the differences between batch and online learning?",
        "How do different optimization algorithms compare in practice?",
        "What are the trade-offs between model complexity and performance?",
        "How do different regularization techniques compare?",
        "What are the advantages of distributed vs centralized learning?",
        "How do different evaluation metrics compare for ML models?",
        "What are the trade-offs between privacy and utility in ML?",
        "How do different data augmentation techniques compare?",
        "What are the advantages of ensemble vs single models?",
        "How do different feature selection methods compare?",
        "What are the trade-offs between speed and accuracy in inference?",
        "How do different clustering algorithms compare?",
        "What are the advantages of deep vs shallow learning?",
        "How do different dimensionality reduction techniques compare?",
        "What are the trade-offs between local vs global explanations?",
        "How do different cross-validation strategies compare?",
    ],
    
    "future_directions": [
        "What are the future directions in artificial general intelligence?",
        "How might quantum computing change machine learning?",
        "What are the potential impacts of neuromorphic computing on AI?",
        "How might brain-computer interfaces integrate with AI?",
        "What are the future applications of AI in space exploration?",
        "How might AI evolve to better understand human emotions?",
        "What are the potential developments in AI-powered creativity?",
        "How might AI contribute to solving global challenges?",
        "What are the future directions in human-AI collaboration?",
        "How might AI systems become more energy efficient?",
        "What are the potential developments in AI safety research?",
        "How might AI contribute to scientific breakthroughs?",
        "What are the future applications of AI in education?",
        "How might AI systems become more transparent and explainable?",
        "What are the potential developments in AI governance?",
        "How might AI contribute to sustainable development?",
        "What are the future directions in AI for mental health?",
        "How might AI systems become more robust and reliable?",
        "What are the potential applications of AI in democracy?",
        "How might AI contribute to reducing inequality?",
    ]
}

# Create a flattened list of all queries with metadata
def get_all_queries():
    """Get all queries with their categories"""
    all_queries = []
    for category, queries in EVALUATION_QUERIES.items():
        for query in queries:
            all_queries.append({
                "query": query,
                "category": category,
                "complexity": _assess_complexity(query),
                "expected_advantage": _predict_graphrag_advantage(query, category)
            })
    return all_queries

def _assess_complexity(query):
    """Assess query complexity based on keywords and structure"""
    complex_keywords = ["how", "why", "compare", "difference", "relationship", "connection", "impact", "evolution", "future", "challenges"]
    simple_keywords = ["what", "who", "when", "where", "list", "define"]
    
    query_lower = query.lower()
    
    if any(keyword in query_lower for keyword in complex_keywords):
        return "high"
    elif any(keyword in query_lower for keyword in simple_keywords):
        return "low"
    else:
        return "medium"

def _predict_graphrag_advantage(query, category):
    """Predict whether GraphRAG should have an advantage for this query"""
    # GraphRAG should excel at:
    # 1. Relationship-based queries
    # 2. Multi-entity queries
    # 3. Cross-domain connections
    # 4. Company-technology relationships
    
    relationship_keywords = ["relationship", "connection", "how", "between", "interact", "collaborate", "partnership", "compare", "difference"]
    multi_entity_keywords = ["companies", "technologies", "researchers", "applications", "industries"]
    
    query_lower = query.lower()
    
    # High advantage for cross-domain and company-technology queries
    if category in ["cross_domain_connections", "company_technology", "comparative_analysis"]:
        return "high"
    
    # High advantage for relationship-based queries
    if any(keyword in query_lower for keyword in relationship_keywords):
        return "high"
    
    # Medium advantage for multi-entity queries
    if any(keyword in query_lower for keyword in multi_entity_keywords):
        return "medium"
    
    # Technical deep dives might favor traditional RAG
    if category == "technical_deep_dive":
        return "low"
    
    return "medium"

# Get total count
def get_query_count():
    """Get total number of evaluation queries"""
    return sum(len(queries) for queries in EVALUATION_QUERIES.values())

if __name__ == "__main__":
    queries = get_all_queries()
    print(f"Total evaluation queries: {len(queries)}")
    
    # Print category breakdown
    for category, queries_list in EVALUATION_QUERIES.items():
        print(f"{category}: {len(queries_list)} queries")