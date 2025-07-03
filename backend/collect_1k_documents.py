#!/usr/bin/env python3
"""
Script to collect 1000+ documents for GraphRAG vs RAG evaluation
"""

import logging
import sys
import os
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_orchestrator import run_data_collection_pipeline

def main():
    """Main function to collect 1000+ documents"""
    
    # Setup logging
    log_filename = f"data_collection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger(__name__)
    
    print("🚀 Starting Enhanced Dataset Collection for GraphRAG vs RAG Evaluation")
    print("=" * 70)
    print()
    
    # Check environment variables
    required_vars = ['NEO4J_URI', 'NEO4J_USER', 'NEO4J_PASSWORD', 'ANTHROPIC_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("⚠️  Warning: Missing environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("   Some data sources may not work without API keys.")
        print()
    
    # Optional API keys for better collection
    optional_vars = ['GITHUB_TOKEN', 'SEMANTIC_SCHOLAR_API_KEY']
    for var in optional_vars:
        if os.getenv(var):
            print(f"✓ {var} configured - enhanced collection available")
        else:
            print(f"○ {var} not set - using public tier")
    
    print()
    print("📊 Collection Plan:")
    print("   - ArXiv Papers: ~300 (30%)")
    print("   - Semantic Scholar Papers: ~250 (25%)")
    print("   - News Articles & Company Blogs: ~250 (25%)")
    print("   - GitHub Repositories: ~200 (20%)")
    print("   - Target Total: 1000+ documents")
    print()
    
    # Get user confirmation
    try:
        response = input("Continue with data collection? (y/N): ").strip().lower()
        if response not in ['y', 'yes']:
            print("❌ Collection cancelled by user")
            return
    except KeyboardInterrupt:
        print("\n❌ Collection cancelled")
        return
    
    print("\n🔄 Starting data collection pipeline...")
    print("This may take 15-30 minutes depending on network speed and API limits.")
    print()
    
    try:
        # Run the collection pipeline
        result = run_data_collection_pipeline(target_documents=1000)
        
        print("\n" + "=" * 70)
        
        if result['success']:
            print("✅ Data collection completed successfully!")
            print()
            print("📈 Collection Summary:")
            
            if 'collection' in result and result['collection'].get('stats'):
                stats = result['collection']['stats']
                print(f"   📄 ArXiv papers: {stats.get('arxiv_papers', 0)}")
                print(f"   📄 Semantic Scholar papers: {stats.get('semantic_scholar_papers', 0)}")
                print(f"   📰 News articles: {stats.get('news_articles', 0)}")
                print(f"   📁 GitHub repositories: {stats.get('github_repos', 0)}")
                print(f"   📚 Total documents: {stats.get('total_documents', 0)}")
                
                if stats.get('errors'):
                    print(f"   ⚠️  Errors encountered: {len(stats['errors'])}")
            
            print()
            
            if 'vector_store' in result:
                vs_result = result['vector_store']
                if vs_result.get('success'):
                    print(f"✅ Vector store: {vs_result.get('ingested_count', 0)} documents ingested")
                else:
                    print(f"❌ Vector store ingestion failed: {vs_result.get('message', 'Unknown error')}")
            
            if 'knowledge_graph' in result:
                kg_result = result['knowledge_graph']
                if kg_result.get('success'):
                    print("✅ Knowledge graph enhanced with extracted entities")
                    if 'added_counts' in kg_result:
                        counts = kg_result['added_counts']
                        print(f"   - Companies: {counts.get('companies', 0)}")
                        print(f"   - Technologies: {counts.get('technologies', 0)}")
                        print(f"   - Research areas: {counts.get('research_areas', 0)}")
                        print(f"   - People: {counts.get('people', 0)}")
                        print(f"   - Venues: {counts.get('venues', 0)}")
                else:
                    print(f"❌ Knowledge graph enhancement failed: {kg_result.get('message', 'Unknown error')}")
            
            print()
            print("🎯 Your dataset is now ready for GraphRAG vs RAG evaluation!")
            print("   The enhanced dataset provides rich interconnected content to evaluate")
            print("   whether GraphRAG performs better than simple RAG on complex queries.")
            
        else:
            print("❌ Data collection failed!")
            print(f"   Error: {result.get('message', 'Unknown error')}")
            
        print(f"\n📋 Detailed logs saved to: {log_filename}")
        
    except KeyboardInterrupt:
        print("\n⏹️  Collection interrupted by user")
        logger.info("Collection interrupted by user")
        
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        logger.error(f"Unexpected error in main: {e}", exc_info=True)

if __name__ == "__main__":
    main()