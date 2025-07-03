import logging
import sys
from data_orchestrator import run_data_collection_pipeline

# Setup logging to console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)

print("🔄 Starting data collection...")
try:
    result = run_data_collection_pipeline(target_documents=10)
    
    if result['success']:
        print("")
        print("✅ Collection completed successfully!")
        
        # Show stats
        if 'collection' in result and 'stats' in result['collection']:
            stats = result['collection']['stats']
            print(f"📊 ArXiv papers: {stats.get('arxiv_papers', 0)}")
            print(f"📊 Semantic Scholar papers: {stats.get('semantic_scholar_papers', 0)}")
            print(f"📊 News articles: {stats.get('news_articles', 0)}")
            print(f"📊 GitHub repos: {stats.get('github_repos', 0)}")
            print(f"📊 Total collected: {stats.get('total_documents', 0)}")
        
        if 'vector_store' in result:
            vs = result['vector_store']
            print(f"💾 Ingested: {vs.get('ingested_count', 0)}")
            print(f"💾 Failed: {vs.get('failed_count', 0)}")
            print(f"💾 Total in DB: {vs.get('total_in_collection', 0)}")
        
        print("")
        print("🎉 Ready for GraphRAG vs RAG evaluation!")
        
    else:
        print("❌ Collection failed:", result.get('message', 'Unknown error'))
        sys.exit(1)
        
except KeyboardInterrupt:
    print("")
    print("⚠️ Collection interrupted by user")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
