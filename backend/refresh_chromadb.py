#!/usr/bin/env python3
"""
Refresh ChromaDB with documents that align with Neo4j knowledge graph
This creates better synergy between document search and knowledge graph entities
"""
import logging
from dotenv import load_dotenv
load_dotenv()

from vector_store import chroma_service
from database import db

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def refresh_chromadb_with_aligned_documents():
    """
    Refresh ChromaDB with documents that align with Neo4j knowledge graph.
    Combines academic research papers with investment-related documents for comprehensive coverage.
    """
    
    aligned_documents = [
        # Academic Research Papers (matching Neo4j documents)
        {
            "title": "Attention Is All You Need",
            "content": """The dominant sequence transduction models are based on complex recurrent or convolutional neural networks that include an encoder and a decoder. The best performing models also connect the encoder and decoder through an attention mechanism. We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely.

Experiments on two machine translation tasks show these models to be superior in quality while being more parallelizable and requiring significantly less time to train. Our model achieves 28.4 BLEU on the WMT 2014 English-to-German translation task, improving over the existing best results, including ensembles, by over 2 BLEU.

The Transformer allows for significantly more parallelization and can reach a new state of the art in translation quality after being trained for as little as twelve hours on eight P100 GPUs. The Transformer follows this overall architecture using stacked self-attention and point-wise, fully connected layers for both the encoder and decoder.

Multi-Head Attention allows the model to jointly attend to information from different representation subspaces at different positions. This architecture has become fundamental to modern AI systems, powering breakthrough models like GPT, BERT, and many others used by companies like Google, OpenAI, and Microsoft.

Investment Impact: This research has driven billions in AI investments across tech companies, with Google alone investing $25B in 2025 for AI research building on Transformer architectures. The paper's impact on commercial AI development has been transformative.""",
            "metadata": {
                "type": "research_paper",
                "authors": "Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob Uszkoreit",
                "year": 2017,
                "venue": "Neural Information Processing Systems (NeurIPS)",
                "citations": 45000,
                "doi": "10.48550/arXiv.1706.03762",
                "companies": "Google, OpenAI, Microsoft",
                "topics": "artificial intelligence, machine learning, transformers, attention mechanisms",
                "source": "Google Research"
            }
        },
        {
            "title": "Language Models are Few-Shot Learners",
            "content": """Recent work has demonstrated substantial gains on many NLP tasks and benchmarks by pre-training on a large corpus of text followed by fine-tuning on a specific task. While typically task-agnostic in architecture, this method still requires task-specific fine-tuning datasets of thousands or tens of thousands of examples.

By contrast, humans can generally perform a new language task from only a few examples or from simple instructions – something which current NLP systems still largely struggle with. Here we show that scaling up language models greatly improves task-agnostic, few-shot performance, sometimes even reaching competitiveness with prior state-of-the-art fine-tuning approaches.

GPT-3 achieves strong performance on many NLP datasets, including translation, question-answering, and cloze tasks, as well as several tasks that require on-the-fly reasoning or domain adaptation, such as unscrambling words, using a novel word in a sentence, or performing 3-digit arithmetic.

We find that GPT-3's performance scales with model size across a wide range of tasks, and that models with tens of billions of parameters can match the performance of fine-tuned systems on some tasks. We also find that larger models exhibit an improved ability to learn from context (in-context learning).

Commercial Impact: GPT-3 and its successors have driven massive investment in AI companies. OpenAI received over $13B in funding from Microsoft, while competitors like Google and Meta have invested billions in competing language models. The few-shot learning capabilities demonstrated here have become central to modern AI investment strategies.""",
            "metadata": {
                "type": "research_paper",
                "authors": "Tom B. Brown, Benjamin Mann, Nick Ryder, Melanie Subbiah",
                "year": 2020,
                "venue": "Neural Information Processing Systems (NeurIPS)",
                "citations": 12000,
                "doi": "10.48550/arXiv.2005.14165",
                "companies": "OpenAI, Microsoft, Google, Meta",
                "topics": "artificial intelligence, machine learning, language models, few-shot learning",
                "source": "OpenAI"
            }
        },
        {
            "title": "Deep Learning",
            "content": """Deep learning is a form of machine learning that enables computers to learn from experience and understand the world in terms of a hierarchy of concepts. Because the computer gathers knowledge from experience, there is no need for a human computer operator to formally specify all the knowledge that the computer needs.

The hierarchy of concepts allows the computer to learn complicated concepts by building them out of simpler ones; a graph of these hierarchies would be many layers deep. This book introduces a broad range of topics in deep learning.

The Deep Learning textbook is a resource intended to help students and practitioners enter the field of machine learning in general and deep learning in particular. Deep learning is a form of machine learning that enables computers to learn from experience and understand the world in terms of a hierarchy of concepts.

This comprehensive textbook covers the mathematical and conceptual background, deep feedforward networks, regularization, optimization, convolutional networks, sequence modeling, practical methodology, and research perspectives. The techniques described have enabled breakthrough applications in computer vision, natural language processing, and speech recognition.

Investment Relevance: This foundational text has educated thousands of AI researchers and engineers now working at major tech companies. The deep learning techniques described here underpin the AI investments of companies like Google ($25B), Apple ($15B), and Meta ($18B) in 2025, making this knowledge directly applicable to understanding modern AI investment strategies.""",
            "metadata": {
                "type": "textbook",
                "authors": "Ian Goodfellow, Yoshua Bengio, Aaron Courville",
                "year": 2016,
                "venue": "MIT Press",
                "citations": 35000,
                "doi": "N/A",
                "companies": "Google, Apple, Meta, Microsoft, Tesla",
                "topics": "artificial intelligence, machine learning, deep learning, neural networks",
                "source": "MIT Press"
            }
        },
        {
            "title": "Tesla Autopilot: Full Self-Driving Capability Technical Report",
            "content": """This technical report describes Tesla's approach to autonomous driving, detailing the neural network architectures, training methodologies, and real-world deployment strategies used in Tesla Autopilot and Full Self-Driving (FSD) capability.

Tesla's Autopilot represents one of the most advanced driver assistance systems currently deployed at scale. The system leverages a suite of cameras, ultrasonic sensors, and radar to provide 360-degree visibility around the vehicle. The neural networks powering Autopilot are trained on millions of miles of real-world driving data collected from Tesla's fleet.

The architecture has evolved from modular, hand-engineered systems to increasingly end-to-end neural network approaches. Tesla's unique advantage lies in its ability to collect vast amounts of real-world driving data from its fleet of vehicles, enabling continuous improvement of the Autopilot system through over-the-air updates.

The report covers the evolution from rule-based systems to end-to-end neural networks, the use of large-scale real-world driving data, and the challenges of scaling autonomous driving technology. Key innovations include multi-camera video networks, temporal reasoning, and efficient inference on custom AI chips.

Investment Context: Tesla's $12B investment in energy storage and autonomous driving technology for 2025 builds directly on the Autopilot research described in this report. The company's approach to real-world AI deployment has influenced investment strategies across the automotive and AI industries, with competitors investing billions to match Tesla's capabilities.""",
            "metadata": {
                "type": "technical_report",
                "authors": "Tesla AI Team, Andrej Karpathy, Ashok Elluswamy",
                "year": 2022,
                "venue": "Tesla Technical Report",
                "citations": 150,
                "doi": "N/A",
                "companies": "Tesla, Google, Apple",
                "topics": "artificial intelligence, autonomous driving, computer vision, neural networks",
                "source": "Tesla Inc."
            }
        },
        
        # Investment-focused documents that complement the research papers
        {
            "title": "AI Investment Trends 2025: From Research to Commercial Applications",
            "content": """The artificial intelligence investment landscape in 2025 represents a maturation of technologies that began as academic research papers. Companies are now investing unprecedented amounts in AI capabilities, with total industry investment exceeding $100 billion globally.

Key Investment Areas:
1. Foundation Models: Companies like OpenAI, Google, and Microsoft are investing billions in large language models building on Transformer architectures introduced in "Attention Is All You Need"
2. Autonomous Systems: Tesla's $12B investment in self-driving technology represents practical application of deep learning research
3. AI Infrastructure: Google's $25B investment in AI research and quantum computing aims to maintain technological leadership
4. Healthcare AI: Apple's $8B healthcare technology investment leverages machine learning for medical applications

Research-to-Market Pipeline:
The path from academic research to commercial investment has accelerated dramatically. Breakthrough papers like GPT-3's few-shot learning capabilities have driven Microsoft's $13B investment in OpenAI within just three years of publication.

Investment Patterns:
- Large tech companies are acquiring AI research talent at unprecedented rates
- Venture capital funding for AI startups reached $75B in 2024
- Government investment in AI research has tripled since 2020
- Corporate R&D spending on AI exceeded $200B globally in 2024

Strategic Implications:
Companies that successfully bridge academic research and commercial applications are seeing the highest returns. Tesla's approach of deploying research-grade neural networks at scale has created a sustainable competitive advantage worth hundreds of billions in market value.

The integration of foundational AI research with practical investment strategies is creating entirely new market categories and reshaping traditional industries.""",
            "metadata": {
                "type": "investment_analysis",
                "date": "2025-01-30",
                "source": "AI Investment Research Institute",
                "companies": "OpenAI, Google, Microsoft, Tesla, Apple, Meta",
                "topics": "artificial intelligence, investment, technology trends, venture capital",
                "amount": "$100B+ industry investment",
                "year": 2025,
                "authors": "AI Investment Research Team"
            }
        },
        
        {
            "title": "The Economics of AI Research: How Academic Papers Drive Billion-Dollar Investments",
            "content": """The relationship between academic AI research and commercial investment has reached an unprecedented level of integration. Foundational papers are now directly influencing investment decisions worth tens of billions of dollars.

Case Study Analysis:

1. Transformer Architecture Impact:
The 2017 "Attention Is All You Need" paper has generated over $50B in related investments:
- Google's continued investment in Transformer-based models
- OpenAI's GPT series built on Transformer architecture
- Microsoft's $13B investment in OpenAI
- Meta's $5B annual investment in AI research
- Apple's $15B AI investment plan for 2025

2. Few-Shot Learning Commercial Applications:
GPT-3's demonstration of few-shot learning has revolutionized AI product development:
- Reduced training data requirements lowering development costs
- Enabled rapid deployment of AI applications across industries
- Created new market categories for AI-powered tools
- Influenced VC investment patterns toward foundation model companies

3. Deep Learning Infrastructure:
The mathematical foundations described in the "Deep Learning" textbook underpin:
- NVIDIA's $60B revenue from AI chips in 2024
- Cloud computing investments by AWS, Azure, and Google Cloud
- Edge AI development across consumer electronics
- Autonomous vehicle technology investments

4. Real-World AI Deployment:
Tesla's technical approach to Autopilot demonstrates how research translates to market value:
- $12B investment in autonomous driving technology
- $800B+ market capitalization driven partly by AI capabilities
- Influence on competitors' autonomous vehicle investments
- Creation of new market for AI-powered transportation

Investment Metrics:
- Time from research publication to commercial application: 2-5 years (down from 10-15 years)
- Average venture capital valuation premium for AI companies: 300%
- Corporate R&D allocation to AI: 15-25% of total R&D budgets
- Government AI research funding growth: 400% since 2020

The convergence of academic excellence and commercial viability has created a new paradigm where fundamental research directly drives investment strategy and market creation.""",
            "metadata": {
                "type": "economic_analysis",
                "date": "2025-02-20",
                "source": "Technology Economics Research Center",
                "companies": "Google, OpenAI, Microsoft, Tesla, Apple, Meta, NVIDIA",
                "topics": "artificial intelligence, research economics, investment strategy, technology transfer",
                "amount": "$50B+ research-driven investment",
                "year": 2025,
                "authors": "Economics of AI Research Team"
            }
        }
    ]
    
    # Clear existing documents
    logger.info("Clearing existing ChromaDB documents...")
    chroma_service.clear_collection()
    
    # Load aligned documents
    logger.info("Loading aligned documents into ChromaDB...")
    success_count = 0
    
    for doc in aligned_documents:
        try:
            doc_id = chroma_service.add_document(
                title=doc["title"],
                content=doc["content"],
                metadata=doc["metadata"]
            )
            logger.info(f"✅ Added document: {doc['title']}")
            success_count += 1
        except Exception as e:
            logger.error(f"❌ Failed to add document {doc['title']}: {e}")
    
    # Verify loading
    stats = chroma_service.get_collection_stats()
    logger.info(f"📊 Successfully loaded {stats['document_count']} documents")
    logger.info(f"✅ Refresh completed: {success_count}/{len(aligned_documents)} documents loaded")
    
    return success_count

def verify_neo4j_chromadb_alignment():
    """Verify that ChromaDB documents align with Neo4j knowledge graph entities"""
    logger.info("🔍 Verifying Neo4j-ChromaDB alignment...")
    
    try:
        # Get Neo4j document titles
        with db.driver.session() as session:
            result = session.run("MATCH (d:Document) RETURN d.title as title")
            neo4j_documents = [record["title"] for record in result]
        
        # Get ChromaDB document titles
        chromadb_docs = chroma_service.search_documents("", n_results=100)
        chromadb_titles = [doc["metadata"].get("title", "Untitled") for doc in chromadb_docs]
        
        logger.info(f"📚 Neo4j documents: {neo4j_documents}")
        logger.info(f"📄 ChromaDB documents: {chromadb_titles}")
        
        # Find overlapping documents
        overlap = set(neo4j_documents) & set(chromadb_titles)
        logger.info(f"🔗 Document overlap: {len(overlap)}/{len(neo4j_documents)} documents aligned")
        
        for title in overlap:
            logger.info(f"  ✅ Aligned: {title}")
        
        # Find missing documents
        missing_in_chromadb = set(neo4j_documents) - set(chromadb_titles)
        if missing_in_chromadb:
            logger.warning(f"⚠️  Missing in ChromaDB: {missing_in_chromadb}")
        
        return len(overlap) == len(neo4j_documents)
        
    except Exception as e:
        logger.error(f"❌ Alignment verification failed: {e}")
        return False

if __name__ == "__main__":
    logger.info("🚀 Starting ChromaDB refresh with aligned documents...")
    
    # Refresh ChromaDB
    loaded_count = refresh_chromadb_with_aligned_documents()
    
    # Verify alignment
    is_aligned = verify_neo4j_chromadb_alignment()
    
    if is_aligned:
        logger.info("✅ ChromaDB refresh completed successfully with full Neo4j alignment!")
    else:
        logger.warning("⚠️  ChromaDB refresh completed but alignment may need improvement")
    
    logger.info(f"📈 Final status: {loaded_count} documents loaded, alignment: {'✅' if is_aligned else '⚠️'}")