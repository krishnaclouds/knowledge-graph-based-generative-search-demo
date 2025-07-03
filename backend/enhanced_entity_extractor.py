#!/usr/bin/env python3
"""
Enhanced Entity Extractor for Knowledge Graph
Uses Claude LLM to extract entities and relationships from documents
"""

import logging
import json
from typing import List, Dict, Set, Tuple
from anthropic import Anthropic
import os
from dotenv import load_dotenv
from database import db
from vector_store import chroma_service
import time

load_dotenv()

logger = logging.getLogger(__name__)

class EnhancedEntityExtractor:
    """LLM-powered entity extraction for knowledge graphs"""
    
    def __init__(self):
        self.anthropic = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        self.processed_docs = set()
        self.extraction_stats = {
            'documents_processed': 0,
            'entities_found': 0,
            'relationships_found': 0,
            'errors': []
        }
    
    def extract_entities_from_text(self, text: str, title: str = "", source: str = "") -> Dict:
        """Extract entities and relationships from text using Claude"""
        
        prompt = f"""
Extract entities and relationships from this document. Focus on:

ENTITIES to extract:
- People (researchers, CEOs, engineers, etc.)
- Organizations (companies, universities, research labs)
- Technologies (AI models, frameworks, algorithms, software)
- Concepts (research areas, methodologies, domains)
- Products (software, hardware, services)
- Publications (papers, books, reports)
- Events (conferences, releases, discoveries)

RELATIONSHIPS to extract:
- Person WORKS_AT Organization
- Person FOUNDED Organization  
- Person RESEARCHES Concept
- Organization DEVELOPS Technology
- Technology ENABLES Concept
- Publication DESCRIBES Technology
- Event FEATURES Technology
- Organization COLLABORATES_WITH Organization
- Technology BASED_ON Technology
- Concept RELATED_TO Concept

Document Title: {title}
Source: {source}

Document Text:
{text[:4000]}  # Limit to avoid token limits

Return a JSON object with this structure:
{{
  "entities": {{
    "people": [list of person names],
    "organizations": [list of organization names],
    "technologies": [list of technology names],
    "concepts": [list of concept names],
    "products": [list of product names],
    "publications": [list of publication titles],
    "events": [list of event names]
  }},
  "relationships": [
    {{"subject": "EntityName", "predicate": "RELATIONSHIP_TYPE", "object": "EntityName", "confidence": 0.8}}
  ]
}}

Focus on extracting the most important and clearly mentioned entities. Be conservative - only include entities you're confident about.
"""

        try:
            response = self.anthropic.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=2000,
                temperature=0.1,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Parse the JSON response
            result_text = response.content[0].text
            
            # Find JSON in the response
            if '{' in result_text:
                json_start = result_text.find('{')
                json_end = result_text.rfind('}') + 1
                json_str = result_text[json_start:json_end]
                
                try:
                    result = json.loads(json_str)
                    return result
                except json.JSONDecodeError:
                    logger.error(f"Failed to parse JSON from Claude response")
                    return {"entities": {}, "relationships": []}
            else:
                logger.error(f"No JSON found in Claude response")
                return {"entities": {}, "relationships": []}
                
        except Exception as e:
            logger.error(f"Error calling Claude API: {e}")
            return {"entities": {}, "relationships": []}
    
    def process_document_batch(self, documents: List[Dict], batch_size: int = 5) -> Dict:
        """Process a batch of documents for entity extraction"""
        
        logger.info(f"Processing {len(documents)} documents for entity extraction...")
        
        all_entities = {
            'people': set(),
            'organizations': set(), 
            'technologies': set(),
            'concepts': set(),
            'products': set(),
            'publications': set(),
            'events': set()
        }
        
        all_relationships = []
        
        for i, doc in enumerate(documents):
            try:
                # Skip if already processed
                doc_id = doc.get('id', f"doc_{i}")
                if doc_id in self.processed_docs:
                    continue
                
                logger.info(f"Processing document {i+1}/{len(documents)}: {doc.get('title', 'Untitled')[:50]}...")
                
                # Extract entities from this document
                result = self.extract_entities_from_text(
                    text=doc.get('content', ''),
                    title=doc.get('title', ''),
                    source=doc.get('source', '')
                )
                
                # Merge entities
                for entity_type, entities in result.get('entities', {}).items():
                    if entity_type in all_entities:
                        all_entities[entity_type].update(entities)
                
                # Add relationships
                relationships = result.get('relationships', [])
                for rel in relationships:
                    rel['source_document'] = doc.get('title', f"Document {i}")
                    all_relationships.append(rel)
                
                self.processed_docs.add(doc_id)
                self.extraction_stats['documents_processed'] += 1
                
                # Rate limiting - wait between API calls
                time.sleep(0.5)
                
                # Progress update
                if (i + 1) % 10 == 0:
                    logger.info(f"Processed {i+1} documents. Found {sum(len(entities) for entities in all_entities.values())} entities so far.")
                
            except Exception as e:
                error_msg = f"Error processing document {i}: {e}"
                logger.error(error_msg)
                self.extraction_stats['errors'].append(error_msg)
                continue
        
        # Convert sets to lists
        for entity_type in all_entities:
            all_entities[entity_type] = list(all_entities[entity_type])
        
        self.extraction_stats['entities_found'] = sum(len(entities) for entities in all_entities.values())
        self.extraction_stats['relationships_found'] = len(all_relationships)
        
        return {
            'entities': all_entities,
            'relationships': all_relationships,
            'stats': self.extraction_stats.copy()
        }
    
    def add_entities_to_neo4j(self, extraction_result: Dict) -> Dict:
        """Add extracted entities and relationships to Neo4j"""
        
        try:
            with db.driver.session() as session:
                entities = extraction_result['entities']
                relationships = extraction_result['relationships']
                
                added_counts = {}
                
                # Add people
                for person in entities.get('people', []):
                    session.run("""
                        MERGE (p:Person {name: $name})
                        ON CREATE SET p.source = 'llm_extracted', p.created_date = datetime()
                        ON MATCH SET p.updated_date = datetime()
                    """, name=person)
                added_counts['people'] = len(entities.get('people', []))
                
                # Add organizations  
                for org in entities.get('organizations', []):
                    session.run("""
                        MERGE (o:Organization {name: $name})
                        ON CREATE SET o.source = 'llm_extracted', o.created_date = datetime()
                        ON MATCH SET o.updated_date = datetime()
                    """, name=org)
                added_counts['organizations'] = len(entities.get('organizations', []))
                
                # Add technologies
                for tech in entities.get('technologies', []):
                    session.run("""
                        MERGE (t:Technology {name: $name})
                        ON CREATE SET t.source = 'llm_extracted', t.created_date = datetime()
                        ON MATCH SET t.updated_date = datetime()
                    """, name=tech)
                added_counts['technologies'] = len(entities.get('technologies', []))
                
                # Add concepts
                for concept in entities.get('concepts', []):
                    session.run("""
                        MERGE (c:Concept {name: $name})
                        ON CREATE SET c.source = 'llm_extracted', c.created_date = datetime()
                        ON MATCH SET c.updated_date = datetime()
                    """, name=concept)
                added_counts['concepts'] = len(entities.get('concepts', []))
                
                # Add products
                for product in entities.get('products', []):
                    session.run("""
                        MERGE (p:Product {name: $name})
                        ON CREATE SET p.source = 'llm_extracted', p.created_date = datetime()
                        ON MATCH SET p.updated_date = datetime()
                    """, name=product)
                added_counts['products'] = len(entities.get('products', []))
                
                # Add publications
                for pub in entities.get('publications', []):
                    session.run("""
                        MERGE (p:Publication {title: $title})
                        ON CREATE SET p.source = 'llm_extracted', p.created_date = datetime()
                        ON MATCH SET p.updated_date = datetime()
                    """, title=pub)
                added_counts['publications'] = len(entities.get('publications', []))
                
                # Add events
                for event in entities.get('events', []):
                    session.run("""
                        MERGE (e:Event {name: $name})
                        ON CREATE SET e.source = 'llm_extracted', e.created_date = datetime()
                        ON MATCH SET e.updated_date = datetime()
                    """, name=event)
                added_counts['events'] = len(entities.get('events', []))
                
                logger.info(f"Added entities to Neo4j: {added_counts}")
                
                # Add relationships
                relationship_count = 0
                for rel in relationships:
                    try:
                        # Create relationship based on predicate
                        rel_type = rel.get('predicate', 'RELATED_TO')
                        subject = rel.get('subject', '')
                        obj = rel.get('object', '')
                        confidence = rel.get('confidence', 0.5)
                        
                        if subject and obj:
                            session.run(f"""
                                MATCH (s), (o)
                                WHERE s.name = $subject OR s.title = $subject
                                AND (o.name = $object OR o.title = $object)
                                MERGE (s)-[r:{rel_type}]->(o)
                                ON CREATE SET r.confidence = $confidence, r.source = 'llm_extracted', r.created_date = datetime()
                                ON MATCH SET r.updated_date = datetime()
                            """, subject=subject, object=obj, confidence=confidence)
                            relationship_count += 1
                    except Exception as e:
                        logger.error(f"Error creating relationship {rel}: {e}")
                        continue
                
                logger.info(f"Added {relationship_count} relationships to Neo4j")
                
                return {
                    'success': True,
                    'entities_added': added_counts,
                    'relationships_added': relationship_count,
                    'message': f'Successfully enhanced knowledge graph with {sum(added_counts.values())} entities and {relationship_count} relationships'
                }
                
        except Exception as e:
            error_msg = f"Error adding entities to Neo4j: {e}"
            logger.error(error_msg)
            return {
                'success': False,
                'message': error_msg
            }
    
    def enhance_knowledge_graph_from_chromadb(self, max_documents: int = None) -> Dict:
        """Extract entities from all documents in ChromaDB and enhance the knowledge graph"""
        
        logger.info("Starting enhanced knowledge graph extraction from ChromaDB...")
        
        # Get all documents from ChromaDB
        collection = chroma_service.collection
        
        # Get document count
        if max_documents:
            limit = min(max_documents, 500)  # Reasonable limit for API calls
        else:
            limit = 500
        
        results = collection.get(
            limit=limit,
            include=['metadatas', 'documents']
        )
        
        # Convert to document format
        documents = []
        for i, (doc_content, metadata) in enumerate(zip(results['documents'], results['metadatas'])):
            documents.append({
                'id': f"chroma_{i}",
                'title': metadata.get('title', f'Document {i}'),
                'content': doc_content,
                'source': metadata.get('source', 'unknown'),
                'metadata': metadata
            })
        
        logger.info(f"Retrieved {len(documents)} documents from ChromaDB")
        
        # Process documents for entity extraction
        extraction_result = self.process_document_batch(documents)
        
        # Add to Neo4j
        if extraction_result['entities']:
            neo4j_result = self.add_entities_to_neo4j(extraction_result)
            
            return {
                'success': True,
                'extraction_stats': extraction_result['stats'],
                'neo4j_result': neo4j_result,
                'message': f"Enhanced knowledge graph with {extraction_result['stats']['entities_found']} entities and {extraction_result['stats']['relationships_found']} relationships"
            }
        else:
            return {
                'success': False,
                'message': "No entities extracted from documents"
            }

def run_enhanced_extraction(max_documents: int = None) -> Dict:
    """Run the enhanced entity extraction process"""
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    extractor = EnhancedEntityExtractor()
    result = extractor.enhance_knowledge_graph_from_chromadb(max_documents=max_documents)
    
    return result

if __name__ == "__main__":
    # Run extraction on all documents
    print("🧠 Starting Enhanced Knowledge Graph Extraction...")
    result = run_enhanced_extraction(max_documents=100)  # Start with 100 documents
    
    if result['success']:
        print("✅ Enhanced extraction completed successfully!")
        print(f"📊 Stats: {result['extraction_stats']}")
    else:
        print(f"❌ Enhanced extraction failed: {result['message']}")