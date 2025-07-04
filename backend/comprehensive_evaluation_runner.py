"""
Comprehensive Evaluation Runner for GraphRAG vs Traditional RAG comparison
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional
import requests
from pathlib import Path

from evaluation_queries import get_all_queries, get_query_count
from evaluation_metrics import EvaluationAnalyzer
from models import EvaluationRequest

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ComprehensiveEvaluationRunner:
    """Runner for comprehensive GraphRAG vs Traditional RAG evaluation"""
    
    def __init__(self, base_url: str = "http://localhost:8000", max_concurrent: int = 5):
        self.base_url = base_url
        self.max_concurrent = max_concurrent
        self.session = requests.Session()
        self.results = []
        self.failed_queries = []
        self.analyzer = EvaluationAnalyzer()
        
        # Rate limiting
        self.request_delay = 2  # seconds between requests
        self.last_request_time = 0
        
    async def run_comprehensive_evaluation(self, output_dir: str = "evaluation_results") -> Dict:
        """Run comprehensive evaluation with all queries"""
        logger.info("Starting comprehensive GraphRAG vs Traditional RAG evaluation")
        
        # Get all evaluation queries
        queries = get_all_queries()
        total_queries = len(queries)
        
        logger.info(f"Total queries to evaluate: {total_queries}")
        
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Run evaluations in batches to avoid overwhelming the API
        batch_size = 10
        completed = 0
        
        for i in range(0, total_queries, batch_size):
            batch = queries[i:i + batch_size]
            logger.info(f"Processing batch {i//batch_size + 1}/{(total_queries + batch_size - 1)//batch_size}")
            
            # Process batch
            batch_results = await self._process_batch(batch)
            self.results.extend(batch_results)
            
            completed += len(batch_results)
            logger.info(f"Completed {completed}/{total_queries} queries ({completed/total_queries:.1%})")
            
            # Save intermediate results
            self._save_intermediate_results(output_path, completed)
            
            # Small delay between batches
            await asyncio.sleep(1)
        
        # Analyze results
        logger.info("Analyzing evaluation results...")
        self.analyzer.add_results(self.results)
        metrics = self.analyzer.analyze()
        
        # Generate comprehensive report
        report = self.analyzer.generate_report()
        
        # Save final results
        self._save_final_results(output_path, report)
        
        # Print summary
        self.analyzer.print_summary()
        
        return {
            'total_queries': total_queries,
            'successful_evaluations': len(self.results),
            'failed_queries': len(self.failed_queries),
            'report': report,
            'output_directory': str(output_path)
        }
    
    async def _process_batch(self, batch: List[Dict]) -> List[Dict]:
        """Process a batch of queries"""
        results = []
        
        for query_data in batch:
            try:
                # Rate limiting
                current_time = time.time()
                if current_time - self.last_request_time < self.request_delay:
                    await asyncio.sleep(self.request_delay - (current_time - self.last_request_time))
                
                # Run single evaluation
                result = await self._evaluate_single_query(query_data)
                if result:
                    results.append(result)
                    self.last_request_time = time.time()
                
            except Exception as e:
                logger.error(f"Failed to evaluate query '{query_data['query']}': {e}")
                self.failed_queries.append({
                    'query': query_data['query'],
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
        
        return results
    
    async def _evaluate_single_query(self, query_data: Dict) -> Optional[Dict]:
        """Evaluate a single query using the comparison endpoint"""
        query = query_data['query']
        
        try:
            # Step 1: Get comparison results from the compare-rag-modes endpoint
            logger.info(f"Evaluating query: {query}")
            
            comparison_response = self._make_request(
                "POST",
                f"{self.base_url}/compare-rag-modes",
                json={"query": query, "max_results": 5}
            )
            
            if not comparison_response or 'graphrag' not in comparison_response:
                logger.error(f"No comparison results for query: {query}")
                return None
            
            graphrag_summary = comparison_response['graphrag']['answer']
            traditional_summary = comparison_response['traditional_rag']['answer']
            
            # Step 2: Use LLM judge to evaluate the summaries
            evaluation_request = {
                "query": query,
                "summary_a": graphrag_summary,  # GraphRAG
                "summary_b": traditional_summary  # Traditional RAG
            }
            
            evaluation_response = self._make_request(
                "POST",
                f"{self.base_url}/evaluate-summaries",
                json=evaluation_request
            )
            
            if not evaluation_response:
                logger.error(f"No evaluation results for query: {query}")
                return None
            
            # Combine results with query metadata
            result = {
                'query': query,
                'category': query_data['category'],
                'complexity': query_data['complexity'],
                'expected_advantage': query_data['expected_advantage'],
                'graphrag_summary': graphrag_summary,
                'traditional_rag_summary': traditional_summary,
                'winner': evaluation_response.get('winner'),
                'confidence': evaluation_response.get('confidence'),
                'reasoning': evaluation_response.get('reasoning'),
                'criteria_scores': evaluation_response.get('criteria_scores', {}),
                'timestamp': datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error evaluating query '{query}': {e}")
            return None
    
    def _make_request(self, method: str, url: str, **kwargs) -> Optional[Dict]:
        """Make HTTP request with error handling"""
        try:
            response = self.session.request(method, url, timeout=30, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return None
    
    def _save_intermediate_results(self, output_path: Path, completed: int):
        """Save intermediate results"""
        intermediate_file = output_path / f"intermediate_results_{completed}.json"
        
        with open(intermediate_file, 'w') as f:
            json.dump({
                'completed_queries': completed,
                'timestamp': datetime.now().isoformat(),
                'results': self.results[-10:] if len(self.results) > 10 else self.results  # Last 10 results
            }, f, indent=2)
    
    def _save_final_results(self, output_path: Path, report: Dict):
        """Save final results and analysis"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save comprehensive report
        report_file = output_path / f"comprehensive_evaluation_report_{timestamp}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Save detailed results
        detailed_file = output_path / f"detailed_evaluation_results_{timestamp}.json"
        self.analyzer.save_detailed_results(str(detailed_file))
        
        # Save CSV export
        csv_file = output_path / f"evaluation_results_{timestamp}.csv"
        self.analyzer.export_to_csv(str(csv_file))
        
        # Save failed queries
        if self.failed_queries:
            failed_file = output_path / f"failed_queries_{timestamp}.json"
            with open(failed_file, 'w') as f:
                json.dump(self.failed_queries, f, indent=2)
        
        logger.info(f"Results saved to {output_path}")
        logger.info(f"- Comprehensive report: {report_file}")
        logger.info(f"- Detailed results: {detailed_file}")
        logger.info(f"- CSV export: {csv_file}")
        
        if self.failed_queries:
            logger.info(f"- Failed queries: {failed_file}")
    
    def run_sample_evaluation(self, sample_size: int = 20) -> Dict:
        """Run evaluation on a sample of queries for testing"""
        logger.info(f"Running sample evaluation with {sample_size} queries")
        
        queries = get_all_queries()[:sample_size]
        
        # Run synchronous evaluation for sample
        results = []
        for query_data in queries:
            try:
                result = asyncio.run(self._evaluate_single_query(query_data))
                if result:
                    results.append(result)
                    logger.info(f"Completed: {query_data['query']}")
            except Exception as e:
                logger.error(f"Failed: {query_data['query']} - {e}")
        
        # Analyze sample results
        self.analyzer.add_results(results)
        metrics = self.analyzer.analyze()
        
        logger.info(f"Sample evaluation completed: {len(results)}/{sample_size} queries")
        self.analyzer.print_summary()
        
        return {
            'sample_size': sample_size,
            'successful_evaluations': len(results),
            'metrics': self.analyzer.generate_report()
        }

async def main():
    """Main function to run comprehensive evaluation"""
    runner = ComprehensiveEvaluationRunner()
    
    # Check if backend is running
    try:
        health_response = runner._make_request("GET", f"{runner.base_url}/health")
        if not health_response:
            logger.error("Backend is not running. Please start the backend first.")
            return
    except Exception as e:
        logger.error(f"Cannot connect to backend: {e}")
        return
    
    # Run comprehensive evaluation
    try:
        results = await runner.run_comprehensive_evaluation()
        logger.info("Comprehensive evaluation completed successfully!")
        logger.info(f"Results: {results}")
    except KeyboardInterrupt:
        logger.info("Evaluation interrupted by user")
    except Exception as e:
        logger.error(f"Evaluation failed: {e}")

if __name__ == "__main__":
    # For testing, run a sample evaluation
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "sample":
        # Run sample evaluation
        runner = ComprehensiveEvaluationRunner()
        sample_size = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        runner.run_sample_evaluation(sample_size)
    else:
        # Run full evaluation
        print(f"Total queries available: {get_query_count()}")
        print("Starting comprehensive evaluation...")
        asyncio.run(main())