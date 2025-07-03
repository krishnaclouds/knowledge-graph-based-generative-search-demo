#!/usr/bin/env python3
"""
Quick Knowledge Graph Enhancement Script
Processes a sample of documents to significantly improve the knowledge graph
"""

import logging
import json
from typing import List, Dict
from enhanced_entity_extractor import EnhancedEntityExtractor
from vector_store import chroma_service
from database import db
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def enhance_knowledge_graph_sample(sample_size: int = 50) -> Dict:
    """Enhance knowledge graph with a sample of documents"""
    
    logger.info(f"🧠 Enhancing knowledge graph with {sample_size} document sample...")
    
    # Get current stats
    with db.driver.session() as session:
        current_nodes = session.run("MATCH (n) RETURN count(n) as count").single()['count']
        current_rels = session.run("MATCH ()-[r]->() RETURN count(r) as count").single()['count']
    
    logger.info(f"📊 Current graph: {current_nodes} nodes, {current_rels} relationships")
    
    # Get sample documents from ChromaDB
    collection = chroma_service.collection
    results = collection.get(
        limit=sample_size,
        include=['metadatas', 'documents']
    )
    
    # Convert to document format
    documents = []
    for i, (doc_content, metadata) in enumerate(zip(results['documents'], results['metadatas'])):
        documents.append({
            'id': f"sample_{i}",
            'title': metadata.get('title', f'Document {i}'),
            'content': doc_content,
            'source': metadata.get('source', 'unknown'),
            'metadata': metadata
        })
    
    logger.info(f"📄 Retrieved {len(documents)} documents from ChromaDB")
    
    # Process with enhanced extractor
    extractor = EnhancedEntityExtractor()
    extraction_result = extractor.process_document_batch(documents)
    
    # Add to Neo4j
    if extraction_result['entities']:
        neo4j_result = extractor.add_entities_to_neo4j(extraction_result)
        
        # Get new stats
        with db.driver.session() as session:
            new_nodes = session.run("MATCH (n) RETURN count(n) as count").single()['count']
            new_rels = session.run("MATCH ()-[r]->() RETURN count(r) as count").single()['count']
        
        logger.info(f"📈 Enhanced graph: {new_nodes} nodes (+{new_nodes-current_nodes}), {new_rels} relationships (+{new_rels-current_rels})")
        
        return {
            'success': True,
            'documents_processed': len(documents),
            'entities_extracted': extraction_result['stats']['entities_found'],
            'relationships_extracted': extraction_result['stats']['relationships_found'],
            'nodes_before': current_nodes,
            'nodes_after': new_nodes,
            'nodes_added': new_nodes - current_nodes,
            'relationships_before': current_rels,
            'relationships_after': new_rels,
            'relationships_added': new_rels - current_rels,
            'message': f"Enhanced knowledge graph with {extraction_result['stats']['entities_found']} entities and {extraction_result['stats']['relationships_found']} relationships"
        }
    else:
        return {
            'success': False,
            'message': "No entities extracted from documents"
        }

def show_graph_sample():
    """Show a sample of the enhanced knowledge graph"""
    
    logger.info("📋 Showing knowledge graph sample...")
    
    with db.driver.session() as session:
        # Show node counts by type
        logger.info("=== Node Counts by Type ===")
        result = session.run("MATCH (n) RETURN labels(n) as labels, count(n) as count ORDER BY count DESC")
        for record in result:
            labels = record['labels']
            count = record['count']
            logger.info(f"{labels}: {count}")
        
        # Show relationship counts
        logger.info("\n=== Relationship Counts ===")
        result = session.run("MATCH ()-[r]->() RETURN type(r) as rel_type, count(r) as count ORDER BY count DESC")
        for record in result:
            rel_type = record['rel_type']
            count = record['count']
            logger.info(f"{rel_type}: {count}")
        
        # Show some example entities
        logger.info("\n=== Sample Entities ===")
        result = session.run("MATCH (n) WHERE n.source = 'llm_extracted' RETURN n.name as name, labels(n) as labels LIMIT 10")
        for record in result:
            name = record['name']
            labels = record['labels']
            logger.info(f"{labels}: {name}")

if __name__ == "__main__":
    print("🚀 Quick Knowledge Graph Enhancement")
    print("===================================")
    
    # Enhance with sample
    result = enhance_knowledge_graph_sample(sample_size=30)
    
    if result['success']:
        print("✅ Enhancement completed successfully!")
        print(f"📊 Processed {result['documents_processed']} documents")
        print(f"🔍 Found {result['entities_extracted']} entities")
        print(f"↔️ Found {result['relationships_extracted']} relationships")
        print(f"📈 Added {result['nodes_added']} nodes and {result['relationships_added']} relationships")
        
        # Show sample
        show_graph_sample()
        
    else:
        print(f"❌ Enhancement failed: {result['message']}")