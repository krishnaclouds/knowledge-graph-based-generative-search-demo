import logging
import time
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import json
import os

# Import collectors
from data_collectors.arxiv_collector import collect_arxiv_papers
from data_collectors.news_collector import collect_news_content
from data_collectors.github_collector import collect_github_data
from data_collectors.semantic_scholar_collector import collect_semantic_scholar_papers

# Import existing services
from vector_store import chroma_service
from database import db

logger = logging.getLogger(__name__)

class DataOrchestrator:
    """Orchestrates collection and ingestion of documents from multiple sources"""
    
    def __init__(self):
        self.collected_documents = []
        self.stats = {
            'arxiv_papers': 0,
            'semantic_scholar_papers': 0,
            'news_articles': 0,
            'github_repos': 0,
            'total_documents': 0,
            'start_time': None,
            'end_time': None,
            'errors': []
        }
    
    def collect_all_documents(self, 
                             target_count: int = 1000,
                             arxiv_ratio: float = 0.3,
                             semantic_scholar_ratio: float = 0.25,
                             news_ratio: float = 0.25,
                             github_ratio: float = 0.2) -> List[Dict]:
        """
        Collect documents from all sources to reach target count
        
        Args:
            target_count: Target number of documents to collect
            arxiv_ratio: Proportion of documents from ArXiv
            semantic_scholar_ratio: Proportion from Semantic Scholar
            news_ratio: Proportion from news sources
            github_ratio: Proportion from GitHub repositories
        """
        self.stats['start_time'] = datetime.now()
        logger.info(f"Starting document collection with target: {target_count} documents")
        
        # Calculate target counts for each source
        arxiv_target = int(target_count * arxiv_ratio)
        semantic_scholar_target = int(target_count * semantic_scholar_ratio)
        news_target = int(target_count * news_ratio)
        github_target = int(target_count * github_ratio)
        
        logger.info(f"Collection targets: ArXiv={arxiv_target}, SemanticScholar={semantic_scholar_target}, News={news_target}, GitHub={github_target}")
        
        all_documents = []
        
        # Collect from ArXiv
        try:
            logger.info("Collecting from ArXiv...")
            arxiv_docs = collect_arxiv_papers(max_papers=arxiv_target)
            all_documents.extend(arxiv_docs)
            self.stats['arxiv_papers'] = len(arxiv_docs)
            logger.info(f"✓ Collected {len(arxiv_docs)} ArXiv papers")
        except Exception as e:
            error_msg = f"Error collecting ArXiv papers: {e}"
            logger.error(error_msg)
            self.stats['errors'].append(error_msg)
        
        # Collect from Semantic Scholar
        try:
            logger.info("Collecting from Semantic Scholar...")
            scholar_docs = collect_semantic_scholar_papers(max_papers=semantic_scholar_target)
            all_documents.extend(scholar_docs)
            self.stats['semantic_scholar_papers'] = len(scholar_docs)
            logger.info(f"✓ Collected {len(scholar_docs)} Semantic Scholar papers")
        except Exception as e:
            error_msg = f"Error collecting Semantic Scholar papers: {e}"
            logger.error(error_msg)
            self.stats['errors'].append(error_msg)
        
        # Collect news articles and blog posts
        try:
            logger.info("Collecting news articles and blog posts...")
            news_docs = collect_news_content(max_articles=news_target)
            all_documents.extend(news_docs)
            self.stats['news_articles'] = len(news_docs)
            logger.info(f"✓ Collected {len(news_docs)} news articles and blog posts")
        except Exception as e:
            error_msg = f"Error collecting news content: {e}"
            logger.error(error_msg)
            self.stats['errors'].append(error_msg)
        
        # Collect GitHub repositories
        try:
            logger.info("Collecting GitHub repositories...")
            github_docs = collect_github_data(max_repos=github_target)
            all_documents.extend(github_docs)
            self.stats['github_repos'] = len(github_docs)
            logger.info(f"✓ Collected {len(github_docs)} GitHub repositories")
        except Exception as e:
            error_msg = f"Error collecting GitHub data: {e}"
            logger.error(error_msg)
            self.stats['errors'].append(error_msg)
        
        self.collected_documents = all_documents
        self.stats['total_documents'] = len(all_documents)
        self.stats['end_time'] = datetime.now()
        
        logger.info(f"Collection completed: {len(all_documents)} total documents")
        self._log_collection_stats()
        
        return all_documents
    
    def ingest_to_vector_store(self, documents: Optional[List[Dict]] = None) -> Dict:
        """Ingest documents into ChromaDB vector store"""
        if documents is None:
            documents = self.collected_documents
            
        if not documents:
            logger.warning("No documents to ingest")
            return {'success': False, 'message': 'No documents provided'}
        
        logger.info(f"Ingesting {len(documents)} documents to ChromaDB...")
        
        # Clear existing collection
        try:
            chroma_service.clear_collection()
            logger.info("Cleared existing ChromaDB collection")
        except Exception as e:
            logger.error(f"Error clearing ChromaDB: {e}")
        
        # Ingest documents
        ingested_count = 0
        failed_count = 0
        
        for i, doc in enumerate(documents):
            try:
                # Prepare metadata (convert lists to strings for ChromaDB compatibility)
                metadata = doc.get('metadata', {})
                
                # Convert any list values to comma-separated strings
                clean_metadata = {}
                for key, value in metadata.items():
                    if isinstance(value, list):
                        clean_metadata[key] = ', '.join(str(v) for v in value)
                    elif isinstance(value, (str, int, float, bool)) or value is None:
                        clean_metadata[key] = value
                    else:
                        clean_metadata[key] = str(value)
                
                clean_metadata.update({
                    'document_type': doc.get('document_type', 'unknown'),
                    'source': doc.get('source', 'unknown'),
                    'ingestion_date': datetime.now().isoformat(),
                    'document_index': i
                })
                
                # Add document to ChromaDB
                doc_id = chroma_service.add_document(
                    title=doc.get('title', f"Document {i}"),
                    content=doc.get('content', ''),
                    metadata=clean_metadata
                )
                
                ingested_count += 1
                
                if ingested_count % 50 == 0:
                    logger.info(f"Ingested {ingested_count}/{len(documents)} documents...")
                    
            except Exception as e:
                failed_count += 1
                logger.error(f"Failed to ingest document {i}: {e}")
        
        # Verify ingestion
        stats = chroma_service.get_collection_stats()
        
        result = {
            'success': True,
            'ingested_count': ingested_count,
            'failed_count': failed_count,
            'total_in_collection': stats.get('document_count', 0),
            'message': f"Successfully ingested {ingested_count} documents"
        }
        
        logger.info(f"Ingestion completed: {ingested_count} successful, {failed_count} failed")
        return result
    
    def enhance_knowledge_graph(self, documents: Optional[List[Dict]] = None) -> Dict:
        """Extract entities and relationships to enhance the knowledge graph"""
        if documents is None:
            documents = self.collected_documents
            
        if not documents:
            logger.warning("No documents to process for knowledge graph")
            return {'success': False, 'message': 'No documents provided'}
        
        logger.info(f"Enhancing knowledge graph with {len(documents)} documents...")
        
        # Extract entities and relationships
        extracted_entities = self._extract_entities_from_documents(documents)
        
        # Add to Neo4j
        kg_result = self._add_entities_to_neo4j(extracted_entities)
        
        return kg_result
    
    def full_pipeline(self, 
                     target_documents: int = 1000,
                     include_vector_store: bool = True,
                     include_knowledge_graph: bool = True) -> Dict:
        """Run the complete data collection and ingestion pipeline"""
        logger.info("Starting full data pipeline...")
        
        pipeline_result = {
            'collection': {},
            'vector_store': {},
            'knowledge_graph': {},
            'success': False,
            'total_documents': 0
        }
        
        try:
            # Step 1: Collect documents
            documents = self.collect_all_documents(target_count=target_documents)
            pipeline_result['collection'] = {
                'success': True,
                'document_count': len(documents),
                'stats': self.stats.copy()
            }
            pipeline_result['total_documents'] = len(documents)
            
            if not documents:
                pipeline_result['success'] = False
                pipeline_result['message'] = "No documents collected"
                return pipeline_result
            
            # Step 2: Ingest to vector store
            if include_vector_store:
                vector_result = self.ingest_to_vector_store(documents)
                pipeline_result['vector_store'] = vector_result
            
            # Step 3: Enhance knowledge graph
            if include_knowledge_graph:
                kg_result = self.enhance_knowledge_graph(documents)
                pipeline_result['knowledge_graph'] = kg_result
            
            pipeline_result['success'] = True
            pipeline_result['message'] = f"Pipeline completed successfully with {len(documents)} documents"
            
        except Exception as e:
            error_msg = f"Pipeline failed: {e}"
            logger.error(error_msg)
            pipeline_result['success'] = False
            pipeline_result['message'] = error_msg
        
        self._save_pipeline_report(pipeline_result)
        return pipeline_result
    
    def _extract_entities_from_documents(self, documents: List[Dict]) -> Dict:
        """Extract entities and relationships from collected documents"""
        entities = {
            'companies': set(),
            'people': set(),
            'technologies': set(),
            'research_areas': set(),
            'venues': set(),
            'relationships': []
        }
        
        # Common entity patterns
        company_keywords = [
            'Google', 'Apple', 'Microsoft', 'Amazon', 'Meta', 'Tesla', 'OpenAI',
            'NVIDIA', 'Intel', 'IBM', 'Oracle', 'Netflix', 'Uber', 'Airbnb',
            'Twitter', 'LinkedIn', 'Adobe', 'Salesforce', 'Zoom'
        ]
        
        tech_keywords = [
            'machine learning', 'deep learning', 'artificial intelligence',
            'neural networks', 'computer vision', 'natural language processing',
            'reinforcement learning', 'transformer', 'BERT', 'GPT',
            'blockchain', 'quantum computing', 'cloud computing', 'IoT'
        ]
        
        research_areas = [
            'computer science', 'artificial intelligence', 'machine learning',
            'data science', 'software engineering', 'cybersecurity',
            'human-computer interaction', 'robotics', 'bioinformatics'
        ]
        
        for doc in documents:
            content = f"{doc.get('title', '')} {doc.get('content', '')}".lower()
            
            # Extract companies
            for company in company_keywords:
                if company.lower() in content:
                    entities['companies'].add(company)
            
            # Extract technologies
            for tech in tech_keywords:
                if tech.lower() in content:
                    entities['technologies'].add(tech)
            
            # Extract research areas
            for area in research_areas:
                if area.lower() in content:
                    entities['research_areas'].add(area)
            
            # Extract people (from authors if available)
            if 'authors' in doc and doc['authors']:
                for author in doc['authors']:
                    if isinstance(author, str) and len(author.split()) >= 2:
                        entities['people'].add(author)
            
            # Extract venues
            if doc.get('venue'):
                entities['venues'].add(doc['venue'])
        
        # Convert sets to lists for JSON serialization
        for key in entities:
            if isinstance(entities[key], set):
                entities[key] = list(entities[key])
        
        logger.info(f"Extracted entities: {len(entities['companies'])} companies, "
                   f"{len(entities['people'])} people, {len(entities['technologies'])} technologies")
        
        return entities
    
    def _add_entities_to_neo4j(self, entities: Dict) -> Dict:
        """Add extracted entities to Neo4j knowledge graph"""
        try:
            with db.driver.session() as session:
                added_counts = {}
                
                # Add companies
                for company in entities['companies']:
                    session.run("""
                        MERGE (c:Company {name: $name})
                        ON CREATE SET c.source = 'extracted', c.created_date = datetime()
                    """, name=company)
                added_counts['companies'] = len(entities['companies'])
                
                # Add technologies
                for tech in entities['technologies']:
                    session.run("""
                        MERGE (t:Technology {name: $name})
                        ON CREATE SET t.source = 'extracted', t.created_date = datetime()
                    """, name=tech)
                added_counts['technologies'] = len(entities['technologies'])
                
                # Add research areas as topics
                for area in entities['research_areas']:
                    session.run("""
                        MERGE (r:Topic {name: $name})
                        ON CREATE SET r.description = $description, r.source = 'extracted', r.created_date = datetime()
                    """, name=area, description=f"Research area: {area}")
                added_counts['research_areas'] = len(entities['research_areas'])
                
                # Add people as researchers
                for person in entities['people'][:100]:  # Limit to avoid too many nodes
                    session.run("""
                        MERGE (p:Researcher {name: $name})
                        ON CREATE SET p.source = 'extracted', p.created_date = datetime()
                    """, name=person)
                added_counts['people'] = min(len(entities['people']), 100)
                
                # Add venues
                for venue in entities['venues']:
                    session.run("""
                        MERGE (v:Venue {name: $name})
                        ON CREATE SET v.source = 'extracted', v.created_date = datetime()
                    """, name=venue)
                added_counts['venues'] = len(entities['venues'])
            
            logger.info(f"Added entities to Neo4j: {added_counts}")
            
            return {
                'success': True,
                'added_counts': added_counts,
                'message': 'Successfully enhanced knowledge graph'
            }
            
        except Exception as e:
            error_msg = f"Error adding entities to Neo4j: {e}"
            logger.error(error_msg)
            return {
                'success': False,
                'message': error_msg
            }
    
    def _log_collection_stats(self):
        """Log detailed collection statistics"""
        if self.stats['start_time'] and self.stats['end_time']:
            duration = self.stats['end_time'] - self.stats['start_time']
            logger.info(f"Collection duration: {duration}")
        
        logger.info("Collection Statistics:")
        logger.info(f"  ArXiv papers: {self.stats['arxiv_papers']}")
        logger.info(f"  Semantic Scholar papers: {self.stats['semantic_scholar_papers']}")
        logger.info(f"  News articles: {self.stats['news_articles']}")
        logger.info(f"  GitHub repositories: {self.stats['github_repos']}")
        logger.info(f"  Total documents: {self.stats['total_documents']}")
        
        if self.stats['errors']:
            logger.warning(f"Errors encountered: {len(self.stats['errors'])}")
            for error in self.stats['errors']:
                logger.warning(f"  - {error}")
    
    def _save_pipeline_report(self, result: Dict):
        """Save pipeline execution report"""
        try:
            report_file = f"pipeline_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            report_path = os.path.join(os.path.dirname(__file__), 'reports', report_file)
            
            # Create reports directory if it doesn't exist
            os.makedirs(os.path.dirname(report_path), exist_ok=True)
            
            with open(report_path, 'w') as f:
                json.dump(result, f, indent=2, default=str)
            
            logger.info(f"Pipeline report saved to: {report_path}")
            
        except Exception as e:
            logger.error(f"Failed to save pipeline report: {e}")

def run_data_collection_pipeline(target_documents: int = 1000) -> Dict:
    """Main function to run the complete data collection pipeline"""
    orchestrator = DataOrchestrator()
    
    result = orchestrator.full_pipeline(
        target_documents=target_documents,
        include_vector_store=True,
        include_knowledge_graph=True
    )
    
    return result

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run with smaller number for testing
    result = run_data_collection_pipeline(target_documents=100)
    
    if result['success']:
        print(f"✓ Pipeline completed successfully!")
        print(f"Total documents collected: {result['total_documents']}")
    else:
        print(f"✗ Pipeline failed: {result.get('message', 'Unknown error')}")