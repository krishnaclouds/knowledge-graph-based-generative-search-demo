"""
Dataset Quality Validator

This module validates the quality and interconnectedness of the collected dataset
to ensure it's suitable for GraphRAG vs simple RAG evaluation.
"""

import logging
from typing import Dict, List, Tuple, Optional
from collections import defaultdict, Counter
import json
from datetime import datetime

from database import db
from vector_store import chroma_service

logger = logging.getLogger(__name__)

class DatasetValidator:
    """Validates dataset quality for GraphRAG vs RAG evaluation"""
    
    def __init__(self):
        self.validation_results = {}
        
    def validate_complete_dataset(self) -> Dict:
        """Run complete dataset validation"""
        logger.info("Starting comprehensive dataset validation...")
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'vector_store_validation': self.validate_vector_store(),
            'knowledge_graph_validation': self.validate_knowledge_graph(),
            'content_quality_validation': self.validate_content_quality(),
            'interconnectedness_validation': self.validate_interconnectedness(),
            'coverage_validation': self.validate_domain_coverage(),
            'graphrag_readiness': {},
            'recommendations': []
        }
        
        # Calculate overall GraphRAG readiness
        results['graphrag_readiness'] = self._calculate_graphrag_readiness(results)
        
        # Generate recommendations
        results['recommendations'] = self._generate_recommendations(results)
        
        # Save validation report
        self._save_validation_report(results)
        
        return results
    
    def validate_vector_store(self) -> Dict:
        """Validate ChromaDB vector store"""
        logger.info("Validating vector store...")
        
        try:
            stats = chroma_service.get_collection_stats()
            
            # Test embedding functionality
            test_query = "machine learning artificial intelligence"
            search_results = chroma_service.search_documents(test_query, max_results=5)
            
            # Analyze document types
            all_docs = chroma_service.get_all_documents()
            doc_types = Counter()
            sources = Counter()
            
            for doc in all_docs:
                metadata = doc.get('metadata', {})
                doc_types[metadata.get('document_type', 'unknown')] += 1
                sources[metadata.get('source', 'unknown')] += 1
            
            validation = {
                'status': 'passed',
                'document_count': stats.get('document_count', 0),
                'embedding_test': {
                    'query': test_query,
                    'results_count': len(search_results),
                    'avg_similarity': sum(r.get('similarity', 0) for r in search_results) / len(search_results) if search_results else 0
                },
                'document_distribution': {
                    'by_type': dict(doc_types),
                    'by_source': dict(sources)
                },
                'issues': []
            }
            
            # Check for issues
            if stats.get('document_count', 0) < 100:
                validation['issues'].append("Low document count (< 100)")
                validation['status'] = 'warning'
            
            if not search_results:
                validation['issues'].append("Search functionality not working")
                validation['status'] = 'failed'
            
            if len(doc_types) < 3:
                validation['issues'].append("Limited document type diversity")
                validation['status'] = 'warning'
            
            logger.info(f"Vector store validation: {validation['status']}")
            return validation
            
        except Exception as e:
            logger.error(f"Vector store validation failed: {e}")
            return {
                'status': 'failed',
                'error': str(e),
                'issues': ['Vector store validation failed']
            }
    
    def validate_knowledge_graph(self) -> Dict:
        """Validate Neo4j knowledge graph"""
        logger.info("Validating knowledge graph...")
        
        try:
            with db.driver.session() as session:
                # Count nodes by type
                node_counts = {}
                node_types = ['Company', 'Person', 'Topic', 'Document', 'Technology', 'Venue', 'Researcher']
                
                for node_type in node_types:
                    result = session.run(f"MATCH (n:{node_type}) RETURN count(n) as count")
                    count = result.single()['count'] if result.single() else 0
                    node_counts[node_type.lower()] = count
                
                # Count relationships by type
                rel_result = session.run("MATCH ()-[r]->() RETURN type(r) as rel_type, count(r) as count")
                relationship_counts = {record['rel_type']: record['count'] for record in rel_result}
                
                # Test graph connectivity
                connectivity_result = session.run("""
                    MATCH (n)
                    WHERE size((n)--()) > 0
                    RETURN count(n) as connected_nodes
                """)
                connected_nodes = connectivity_result.single()['connected_nodes']
                
                total_nodes = sum(node_counts.values())
                connectivity_ratio = connected_nodes / total_nodes if total_nodes > 0 else 0
                
                # Test multi-hop queries
                multi_hop_result = session.run("""
                    MATCH path = (c:Company)-[*2..3]-(t:Topic)
                    RETURN count(path) as multi_hop_paths
                    LIMIT 100
                """)
                multi_hop_paths = multi_hop_result.single()['multi_hop_paths']
                
                validation = {
                    'status': 'passed',
                    'node_counts': node_counts,
                    'relationship_counts': relationship_counts,
                    'total_nodes': total_nodes,
                    'total_relationships': sum(relationship_counts.values()),
                    'connectivity_ratio': connectivity_ratio,
                    'multi_hop_paths': multi_hop_paths,
                    'issues': []
                }
                
                # Check for issues
                if total_nodes < 50:
                    validation['issues'].append("Low node count (< 50)")
                    validation['status'] = 'warning'
                
                if connectivity_ratio < 0.3:
                    validation['issues'].append(f"Low connectivity ratio: {connectivity_ratio:.2f}")
                    validation['status'] = 'warning'
                
                if multi_hop_paths < 10:
                    validation['issues'].append("Limited multi-hop connectivity")
                    validation['status'] = 'warning'
                
                if len(relationship_counts) < 3:
                    validation['issues'].append("Limited relationship type diversity")
                    validation['status'] = 'warning'
                
                logger.info(f"Knowledge graph validation: {validation['status']}")
                return validation
                
        except Exception as e:
            logger.error(f"Knowledge graph validation failed: {e}")
            return {
                'status': 'failed',
                'error': str(e),
                'issues': ['Knowledge graph validation failed']
            }
    
    def validate_content_quality(self) -> Dict:
        """Validate content quality metrics"""
        logger.info("Validating content quality...")
        
        try:
            # Get sample of documents
            all_docs = chroma_service.get_all_documents()
            sample_size = min(100, len(all_docs))
            sample_docs = all_docs[:sample_size]
            
            # Analyze content metrics
            word_counts = []
            char_counts = []
            has_abstracts = 0
            has_metadata = 0
            
            for doc in sample_docs:
                content = doc.get('content', '')
                metadata = doc.get('metadata', {})
                
                if content:
                    word_count = len(content.split())
                    char_count = len(content)
                    word_counts.append(word_count)
                    char_counts.append(char_count)
                
                if 'abstract' in content.lower() or metadata.get('abstract'):
                    has_abstracts += 1
                
                if metadata:
                    has_metadata += 1
            
            avg_word_count = sum(word_counts) / len(word_counts) if word_counts else 0
            avg_char_count = sum(char_counts) / len(char_counts) if char_counts else 0
            
            validation = {
                'status': 'passed',
                'sample_size': sample_size,
                'avg_word_count': avg_word_count,
                'avg_char_count': avg_char_count,
                'min_word_count': min(word_counts) if word_counts else 0,
                'max_word_count': max(word_counts) if word_counts else 0,
                'abstracts_ratio': has_abstracts / sample_size if sample_size > 0 else 0,
                'metadata_ratio': has_metadata / sample_size if sample_size > 0 else 0,
                'issues': []
            }
            
            # Check for issues
            if avg_word_count < 100:
                validation['issues'].append(f"Low average word count: {avg_word_count:.1f}")
                validation['status'] = 'warning'
            
            if validation['abstracts_ratio'] < 0.3:
                validation['issues'].append(f"Low abstracts ratio: {validation['abstracts_ratio']:.2f}")
                validation['status'] = 'warning'
            
            if validation['metadata_ratio'] < 0.8:
                validation['issues'].append(f"Low metadata ratio: {validation['metadata_ratio']:.2f}")
                validation['status'] = 'warning'
            
            logger.info(f"Content quality validation: {validation['status']}")
            return validation
            
        except Exception as e:
            logger.error(f"Content quality validation failed: {e}")
            return {
                'status': 'failed',
                'error': str(e),
                'issues': ['Content quality validation failed']
            }
    
    def validate_interconnectedness(self) -> Dict:
        """Validate interconnectedness for GraphRAG effectiveness"""
        logger.info("Validating dataset interconnectedness...")
        
        try:
            with db.driver.session() as session:
                # Test entity co-occurrence in documents
                entity_cooccurrence = session.run("""
                    MATCH (e1)-[]-(d:Document)-[]-(e2)
                    WHERE id(e1) < id(e2)
                    RETURN count(*) as cooccurrence_count
                """)
                cooccurrence_count = entity_cooccurrence.single()['cooccurrence_count']
                
                # Test cross-domain connections
                cross_domain = session.run("""
                    MATCH (c:Company)-[]-(t:Topic)-[]-(p:Person)
                    RETURN count(*) as cross_domain_paths
                """)
                cross_domain_paths = cross_domain.single()['cross_domain_paths']
                
                # Test temporal connections (if available)
                temporal_connections = session.run("""
                    MATCH (n)-[r]-(m)
                    WHERE exists(n.year) AND exists(m.year)
                    RETURN count(r) as temporal_connections
                """)
                temporal_count = temporal_connections.single()['temporal_connections']
                
                # Test topic clustering
                topic_clusters = session.run("""
                    MATCH (t:Topic)
                    OPTIONAL MATCH (t)-[]-(related)
                    RETURN t.name as topic, count(related) as connections
                    ORDER BY connections DESC
                    LIMIT 10
                """)
                
                top_topics = [(record['topic'], record['connections']) for record in topic_clusters]
                
                validation = {
                    'status': 'passed',
                    'entity_cooccurrence': cooccurrence_count,
                    'cross_domain_paths': cross_domain_paths,
                    'temporal_connections': temporal_count,
                    'top_connected_topics': top_topics,
                    'issues': []
                }
                
                # Check for issues
                if cooccurrence_count < 50:
                    validation['issues'].append("Low entity co-occurrence")
                    validation['status'] = 'warning'
                
                if cross_domain_paths < 20:
                    validation['issues'].append("Limited cross-domain connections")
                    validation['status'] = 'warning'
                
                if not top_topics or top_topics[0][1] < 5:
                    validation['issues'].append("Weak topic clustering")
                    validation['status'] = 'warning'
                
                logger.info(f"Interconnectedness validation: {validation['status']}")
                return validation
                
        except Exception as e:
            logger.error(f"Interconnectedness validation failed: {e}")
            return {
                'status': 'failed',
                'error': str(e),
                'issues': ['Interconnectedness validation failed']
            }
    
    def validate_domain_coverage(self) -> Dict:
        """Validate coverage of AI/tech domains"""
        logger.info("Validating domain coverage...")
        
        try:
            with db.driver.session() as session:
                # Check for key AI/tech topics
                key_topics = [
                    'artificial intelligence', 'machine learning', 'deep learning',
                    'natural language processing', 'computer vision', 'robotics',
                    'quantum computing', 'blockchain', 'cloud computing'
                ]
                
                covered_topics = []
                for topic in key_topics:
                    result = session.run("""
                        MATCH (t:Topic)
                        WHERE toLower(t.name) CONTAINS $topic
                        RETURN count(t) as count
                    """, topic=topic)
                    
                    if result.single()['count'] > 0:
                        covered_topics.append(topic)
                
                # Check for major tech companies
                major_companies = [
                    'Google', 'Apple', 'Microsoft', 'Amazon', 'Meta',
                    'Tesla', 'OpenAI', 'NVIDIA'
                ]
                
                covered_companies = []
                for company in major_companies:
                    result = session.run("""
                        MATCH (c:Company)
                        WHERE c.name CONTAINS $company
                        RETURN count(c) as count
                    """, company=company)
                    
                    if result.single()['count'] > 0:
                        covered_companies.append(company)
                
                # Check for research venues
                research_venues = session.run("""
                    MATCH (v:Venue)
                    RETURN count(v) as venue_count
                """)
                venue_count = research_venues.single()['venue_count']
                
                validation = {
                    'status': 'passed',
                    'topic_coverage': {
                        'covered': covered_topics,
                        'total_checked': len(key_topics),
                        'coverage_ratio': len(covered_topics) / len(key_topics)
                    },
                    'company_coverage': {
                        'covered': covered_companies,
                        'total_checked': len(major_companies),
                        'coverage_ratio': len(covered_companies) / len(major_companies)
                    },
                    'research_venues': venue_count,
                    'issues': []
                }
                
                # Check for issues
                if validation['topic_coverage']['coverage_ratio'] < 0.6:
                    validation['issues'].append("Insufficient AI/tech topic coverage")
                    validation['status'] = 'warning'
                
                if validation['company_coverage']['coverage_ratio'] < 0.5:
                    validation['issues'].append("Insufficient major tech company coverage")
                    validation['status'] = 'warning'
                
                if venue_count < 10:
                    validation['issues'].append("Limited research venue diversity")
                    validation['status'] = 'warning'
                
                logger.info(f"Domain coverage validation: {validation['status']}")
                return validation
                
        except Exception as e:
            logger.error(f"Domain coverage validation failed: {e}")
            return {
                'status': 'failed',
                'error': str(e),
                'issues': ['Domain coverage validation failed']
            }
    
    def _calculate_graphrag_readiness(self, results: Dict) -> Dict:
        """Calculate overall GraphRAG readiness score"""
        components = [
            'vector_store_validation',
            'knowledge_graph_validation', 
            'content_quality_validation',
            'interconnectedness_validation',
            'coverage_validation'
        ]
        
        scores = {}
        for component in components:
            validation = results.get(component, {})
            status = validation.get('status', 'failed')
            
            if status == 'passed':
                scores[component] = 1.0
            elif status == 'warning':
                scores[component] = 0.7
            else:
                scores[component] = 0.0
        
        overall_score = sum(scores.values()) / len(scores)
        
        if overall_score >= 0.8:
            readiness_level = 'excellent'
        elif overall_score >= 0.6:
            readiness_level = 'good'
        elif overall_score >= 0.4:
            readiness_level = 'fair'
        else:
            readiness_level = 'poor'
        
        return {
            'overall_score': overall_score,
            'readiness_level': readiness_level,
            'component_scores': scores,
            'suitable_for_graphrag': overall_score >= 0.6
        }
    
    def _generate_recommendations(self, results: Dict) -> List[str]:
        """Generate recommendations based on validation results"""
        recommendations = []
        
        # Vector store recommendations
        vs_validation = results.get('vector_store_validation', {})
        if vs_validation.get('status') != 'passed':
            if vs_validation.get('document_count', 0) < 1000:
                recommendations.append("Increase document count to at least 1000 for better evaluation")
        
        # Knowledge graph recommendations
        kg_validation = results.get('knowledge_graph_validation', {})
        if kg_validation.get('connectivity_ratio', 0) < 0.5:
            recommendations.append("Improve knowledge graph connectivity by adding more entity relationships")
        
        if kg_validation.get('multi_hop_paths', 0) < 50:
            recommendations.append("Enhance multi-hop connectivity for better GraphRAG performance")
        
        # Content quality recommendations
        cq_validation = results.get('content_quality_validation', {})
        if cq_validation.get('avg_word_count', 0) < 200:
            recommendations.append("Include more detailed documents with richer content")
        
        # Interconnectedness recommendations
        ic_validation = results.get('interconnectedness_validation', {})
        if ic_validation.get('cross_domain_paths', 0) < 100:
            recommendations.append("Add more cross-domain connections between companies, topics, and research")
        
        # Coverage recommendations
        cv_validation = results.get('coverage_validation', {})
        if cv_validation.get('topic_coverage', {}).get('coverage_ratio', 0) < 0.8:
            recommendations.append("Expand coverage of key AI/tech topics")
        
        # GraphRAG-specific recommendations
        graphrag_readiness = results.get('graphrag_readiness', {})
        if not graphrag_readiness.get('suitable_for_graphrag', False):
            recommendations.append("Dataset needs improvement before GraphRAG vs RAG evaluation")
            recommendations.append("Focus on improving knowledge graph connectivity and content quality")
        
        if not recommendations:
            recommendations.append("Dataset is well-prepared for GraphRAG vs RAG evaluation!")
        
        return recommendations
    
    def _save_validation_report(self, results: Dict):
        """Save validation report to file"""
        try:
            import os
            
            report_dir = os.path.join(os.path.dirname(__file__), 'reports')
            os.makedirs(report_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            report_file = os.path.join(report_dir, f'dataset_validation_{timestamp}.json')
            
            with open(report_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            
            logger.info(f"Validation report saved to: {report_file}")
            
        except Exception as e:
            logger.error(f"Failed to save validation report: {e}")
    
    def generate_test_queries(self) -> List[Dict]:
        """Generate test queries for GraphRAG vs RAG evaluation"""
        logger.info("Generating test queries for evaluation...")
        
        queries = [
            {
                'query': 'What are the connections between Google and OpenAI in AI research?',
                'type': 'multi_entity_relationship',
                'expected_graphrag_advantage': 'high',
                'reasoning': 'Requires finding relationships across multiple entities and domains'
            },
            {
                'query': 'Which companies are working on transformer neural networks and who are the key researchers?',
                'type': 'cross_domain_lookup',
                'expected_graphrag_advantage': 'high',
                'reasoning': 'Needs to connect technology, companies, and people nodes'
            },
            {
                'query': 'What is the evolution of machine learning research from 2020 to 2024?',
                'type': 'temporal_analysis',
                'expected_graphrag_advantage': 'medium',
                'reasoning': 'Temporal connections and trend analysis benefit from graph structure'
            },
            {
                'query': 'How do Tesla and Apple approach autonomous driving differently?',
                'type': 'comparative_analysis',
                'expected_graphrag_advantage': 'medium',
                'reasoning': 'Comparing company strategies requires understanding relationships'
            },
            {
                'query': 'What are the latest developments in computer vision?',
                'type': 'simple_topic_query',
                'expected_graphrag_advantage': 'low',
                'reasoning': 'Simple topic search may work equally well with both approaches'
            },
            {
                'query': 'Who are the co-authors of Attention Is All You Need paper?',
                'type': 'factual_lookup',
                'expected_graphrag_advantage': 'low',
                'reasoning': 'Direct factual query doesn\'t require complex reasoning'
            },
            {
                'query': 'What technologies and research areas connect Meta, NVIDIA, and Stanford University?',
                'type': 'multi_hop_connection',
                'expected_graphrag_advantage': 'high',
                'reasoning': 'Requires multi-hop traversal to find connecting technologies and research'
            },
            {
                'query': 'Which startups have been acquired by big tech companies for AI capabilities?',
                'type': 'acquisition_network',
                'expected_graphrag_advantage': 'high',
                'reasoning': 'Understanding acquisition relationships and AI focus areas'
            }
        ]
        
        return queries

def validate_dataset_for_graphrag_evaluation() -> Dict:
    """Main function to validate dataset for GraphRAG vs RAG evaluation"""
    validator = DatasetValidator()
    
    # Run complete validation
    results = validator.validate_complete_dataset()
    
    # Generate test queries
    test_queries = validator.generate_test_queries()
    results['test_queries'] = test_queries
    
    return results

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("🔍 Validating dataset for GraphRAG vs RAG evaluation...")
    results = validate_dataset_for_graphrag_evaluation()
    
    # Print summary
    print("\n" + "="*50)
    print("DATASET VALIDATION SUMMARY")
    print("="*50)
    
    graphrag_readiness = results.get('graphrag_readiness', {})
    print(f"📊 Overall Score: {graphrag_readiness.get('overall_score', 0):.2f}")
    print(f"🎯 Readiness Level: {graphrag_readiness.get('readiness_level', 'unknown').upper()}")
    print(f"✅ Suitable for GraphRAG: {graphrag_readiness.get('suitable_for_graphrag', False)}")
    
    print(f"\n📝 Recommendations:")
    for rec in results.get('recommendations', []):
        print(f"  • {rec}")
    
    print(f"\n🧪 Generated {len(results.get('test_queries', []))} test queries for evaluation")
    
    if graphrag_readiness.get('suitable_for_graphrag', False):
        print("\n🎉 Dataset is ready for GraphRAG vs RAG evaluation!")
    else:
        print("\n⚠️  Dataset needs improvement before evaluation.")
    
    print(f"\n📋 Detailed report saved to reports/ directory")