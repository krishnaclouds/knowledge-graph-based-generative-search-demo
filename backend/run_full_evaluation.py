#!/usr/bin/env python3
"""
Script to run the full comprehensive evaluation
"""

import asyncio
import logging
from comprehensive_evaluation_runner import ComprehensiveEvaluationRunner
from evaluation_queries import get_query_count

async def run_full_evaluation():
    """Run the full comprehensive evaluation"""
    print(f"Starting comprehensive evaluation with {get_query_count()} queries...")
    print("This will take approximately 15-20 minutes to complete.")
    
    runner = ComprehensiveEvaluationRunner(max_concurrent=3)
    
    # Check backend health
    health = runner._make_request("GET", f"{runner.base_url}/health")
    if not health:
        print("Error: Backend is not running. Please start the backend first.")
        return
    
    print("Backend is healthy. Starting evaluation...")
    
    try:
        results = await runner.run_comprehensive_evaluation()
        print("\n" + "="*80)
        print("COMPREHENSIVE EVALUATION COMPLETED!")
        print("="*80)
        print(f"Total queries: {results['total_queries']}")
        print(f"Successful evaluations: {results['successful_evaluations']}")
        print(f"Failed queries: {results['failed_queries']}")
        print(f"Results saved to: {results['output_directory']}")
        
        if results['successful_evaluations'] > 0:
            report = results['report']
            summary = report['evaluation_summary']
            print(f"\nQuick Results:")
            print(f"GraphRAG Win Rate: {summary['graphrag_win_rate']}%")
            print(f"Traditional RAG Win Rate: {summary['traditional_rag_win_rate']}%")
            print(f"Average Confidence: {report['confidence_analysis']['average_confidence']}")
        
    except Exception as e:
        print(f"Evaluation failed: {e}")
        logging.error(f"Full evaluation error: {e}", exc_info=True)

if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('comprehensive_evaluation.log'),
            logging.StreamHandler()
        ]
    )
    
    asyncio.run(run_full_evaluation())