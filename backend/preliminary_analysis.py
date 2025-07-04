#!/usr/bin/env python3
"""
Preliminary analysis of the first 10 evaluation results
"""

import json
from evaluation_metrics import EvaluationAnalyzer

def analyze_preliminary_results():
    """Analyze the first 10 evaluation results"""
    
    # Load the intermediate results
    with open('evaluation_results/intermediate_results_10.json', 'r') as f:
        data = json.load(f)
    
    results = data['results']
    
    # Add them to the analyzer
    analyzer = EvaluationAnalyzer()
    
    # Convert format for analyzer
    formatted_results = []
    for result in results:
        formatted_result = {
            'query': result['query'],
            'category': result['category'],
            'complexity': result['complexity'],
            'expected_advantage': result['expected_advantage'],
            'winner': result['winner'],
            'confidence': result['confidence'],
            'criteria_scores': result['criteria_scores'],
            'reasoning': result['reasoning']
        }
        formatted_results.append(formatted_result)
    
    analyzer.add_results(formatted_results)
    metrics = analyzer.analyze()
    
    print("="*100)
    print("PRELIMINARY RESULTS - FIRST 10 QUERIES")
    print("="*100)
    
    analyzer.print_summary()
    
    # Additional detailed analysis
    print("\n🔍 DETAILED ANALYSIS OF FIRST 10 QUERIES:")
    
    # Query-by-query breakdown
    graphrag_wins = []
    traditional_wins = []
    
    for i, result in enumerate(results, 1):
        winner_text = "GraphRAG" if result['winner'] == 'summary_a' else "Traditional RAG"
        confidence = result['confidence']
        print(f"{i:2d}. {result['query'][:60]}...")
        print(f"    Winner: {winner_text} (Confidence: {confidence}%)")
        
        if result['winner'] == 'summary_a':
            graphrag_wins.append(result)
        else:
            traditional_wins.append(result)
    
    print(f"\n📊 WINNERS BREAKDOWN:")
    print(f"GraphRAG Wins: {len(graphrag_wins)}")
    for win in graphrag_wins:
        print(f"  • {win['query'][:50]}... (Confidence: {win['confidence']}%)")
    
    print(f"\nTraditional RAG Wins: {len(traditional_wins)}")
    for win in traditional_wins:
        print(f"  • {win['query'][:50]}... (Confidence: {win['confidence']}%)")
    
    # Confidence analysis
    confidences = [r['confidence'] for r in results]
    avg_confidence = sum(confidences) / len(confidences)
    high_conf = [c for c in confidences if c >= 80]
    med_conf = [c for c in confidences if 60 <= c < 80]
    low_conf = [c for c in confidences if c < 60]
    
    print(f"\n🎯 CONFIDENCE DISTRIBUTION:")
    print(f"Average Confidence: {avg_confidence:.1f}%")
    print(f"High Confidence (≥80%): {len(high_conf)} queries")
    print(f"Medium Confidence (60-79%): {len(med_conf)} queries") 
    print(f"Low Confidence (<60%): {len(low_conf)} queries")
    
    # Reasoning analysis
    print(f"\n💭 SAMPLE REASONING:")
    for result in results[:3]:
        winner_text = "GraphRAG" if result['winner'] == 'summary_a' else "Traditional RAG"
        print(f"\nQuery: {result['query']}")
        print(f"Winner: {winner_text}")
        print(f"Reasoning: {result['reasoning']}")
    
    print("\n" + "="*100)

if __name__ == "__main__":
    analyze_preliminary_results()