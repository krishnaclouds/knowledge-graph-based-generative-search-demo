#!/usr/bin/env python3
"""
Final analysis script for comprehensive evaluation results
"""

import json
import glob
from pathlib import Path
from evaluation_metrics import EvaluationAnalyzer
from datetime import datetime

def find_latest_results():
    """Find the most recent evaluation results"""
    results_dir = Path("evaluation_results")
    if not results_dir.exists():
        return None
    
    # Look for comprehensive evaluation reports
    report_files = list(results_dir.glob("comprehensive_evaluation_report_*.json"))
    if not report_files:
        return None
    
    # Get the most recent one
    latest_report = max(report_files, key=lambda x: x.stat().st_mtime)
    return latest_report

def analyze_final_results():
    """Analyze and summarize final evaluation results"""
    
    # Find latest results
    latest_report = find_latest_results()
    if not latest_report:
        print("No evaluation results found yet. Check evaluation_results/ directory.")
        return
    
    print(f"Analyzing results from: {latest_report}")
    
    # Load the report
    with open(latest_report, 'r') as f:
        report = json.load(f)
    
    # Print comprehensive analysis
    print("="*100)
    print("COMPREHENSIVE GRAPHRAG vs TRADITIONAL RAG EVALUATION - FINAL RESULTS")
    print("="*100)
    
    # Overall performance
    summary = report['evaluation_summary']
    print(f"\n📊 OVERALL PERFORMANCE:")
    print(f"Total Queries Evaluated: {summary['total_queries']}")
    print(f"GraphRAG Wins: {summary['graphrag_wins']} ({summary['graphrag_win_rate']}%)")
    print(f"Traditional RAG Wins: {summary['traditional_rag_wins']} ({summary['traditional_rag_win_rate']}%)")
    print(f"Ties: {summary['ties']} ({summary['tie_rate']}%)")
    
    # Confidence analysis
    confidence = report['confidence_analysis']
    print(f"\n🎯 CONFIDENCE ANALYSIS:")
    print(f"Average Confidence: {confidence['average_confidence']}/100")
    print(f"High Confidence Decisions (>80): {confidence['high_confidence_decisions']} ({confidence['high_confidence_percentage']}%)")
    print(f"Low Confidence Decisions (<50): {confidence['low_confidence_decisions']}")
    
    # Criteria performance
    if 'criteria_performance' in report and report['criteria_performance']:
        print(f"\n📋 CRITERIA PERFORMANCE (GraphRAG vs Traditional RAG):")
        criteria_perf = report['criteria_performance']
        
        criteria_names = {
            'completeness': 'Completeness',
            'accuracy': 'Accuracy', 
            'contextual_depth': 'Contextual Depth',
            'clarity': 'Clarity',
            'relevance_to_query': 'Relevance to Query',
            'actionable_insights': 'Actionable Insights'
        }
        
        for criterion, performance in criteria_perf.items():
            name = criteria_names.get(criterion, criterion.replace('_', ' ').title())
            graphrag_avg = performance.get('graphrag_avg', 0)
            traditional_avg = performance.get('traditional_rag_avg', 0)
            advantage = performance.get('graphrag_advantage', 0)
            
            print(f"{name}: GraphRAG {graphrag_avg:.2f} vs Traditional {traditional_avg:.2f} ({advantage:+.2f})")
    
    # Category performance
    if 'category_performance' in report and report['category_performance']:
        print(f"\n🏷️ CATEGORY PERFORMANCE:")
        category_perf = report['category_performance']
        
        category_names = {
            'ai_ml_research': 'AI/ML Research',
            'company_technology': 'Company Technology',
            'cross_domain_connections': 'Cross-domain Connections',
            'research_trends': 'Research Trends',
            'technical_deep_dive': 'Technical Deep Dive',
            'industry_applications': 'Industry Applications',
            'comparative_analysis': 'Comparative Analysis',
            'future_directions': 'Future Directions'
        }
        
        for category, performance in category_perf.items():
            name = category_names.get(category, category.replace('_', ' ').title())
            total = sum(performance.values())
            if total > 0:
                graphrag_rate = performance.get('graphrag', 0) / total
                traditional_rate = performance.get('traditional_rag', 0) / total
                tie_rate = performance.get('ties', 0) / total
                
                print(f"{name}: GraphRAG {graphrag_rate:.1%} | Traditional {traditional_rate:.1%} | Ties {tie_rate:.1%}")
    
    # Complexity performance
    if 'complexity_performance' in report and report['complexity_performance']:
        print(f"\n🧠 COMPLEXITY PERFORMANCE:")
        complexity_perf = report['complexity_performance']
        
        for complexity, performance in complexity_perf.items():
            total = sum(performance.values())
            if total > 0:
                graphrag_rate = performance.get('graphrag', 0) / total
                traditional_rate = performance.get('traditional_rag', 0) / total
                tie_rate = performance.get('ties', 0) / total
                
                print(f"{complexity.title()} Complexity: GraphRAG {graphrag_rate:.1%} | Traditional {traditional_rate:.1%} | Ties {tie_rate:.1%}")
    
    # Prediction accuracy
    pred_accuracy = report.get('prediction_accuracy', 0)
    print(f"\n🔮 PREDICTION ACCURACY: {pred_accuracy}%")
    
    # Statistical significance
    if 'statistical_significance' in report and report['statistical_significance']:
        print(f"\n📈 STATISTICAL SIGNIFICANCE:")
        sig = report['statistical_significance']
        
        if sig.get('p_value') is not None:
            print(f"P-value: {sig['p_value']:.4f}")
            print(f"Significant at α=0.05: {sig['significant_at_05']}")
            print(f"Significant at α=0.01: {sig['significant_at_01']}")
        
        print(f"Effect Size: {sig['effect_size']:.3f}")
        
        if 'note' in sig:
            print(f"Note: {sig['note']}")
    
    # Key insights
    print(f"\n💡 KEY INSIGHTS:")
    
    # Determine winner
    if summary['graphrag_win_rate'] > summary['traditional_rag_win_rate']:
        winner = "GraphRAG"
        margin = summary['graphrag_win_rate'] - summary['traditional_rag_win_rate']
    elif summary['traditional_rag_win_rate'] > summary['graphrag_win_rate']:
        winner = "Traditional RAG"
        margin = summary['traditional_rag_win_rate'] - summary['graphrag_win_rate']
    else:
        winner = "Tie"
        margin = 0
    
    print(f"• Overall Winner: {winner}" + (f" (by {margin:.1f}%)" if margin > 0 else ""))
    print(f"• Judge Confidence: {'High' if confidence['average_confidence'] > 75 else 'Medium' if confidence['average_confidence'] > 50 else 'Low'}")
    
    # Identify GraphRAG strengths
    if 'criteria_performance' in report and report['criteria_performance']:
        strongest_criteria = []
        weakest_criteria = []
        
        for criterion, performance in report['criteria_performance'].items():
            advantage = performance.get('graphrag_advantage', 0)
            if advantage > 0.5:
                strongest_criteria.append(criterion.replace('_', ' ').title())
            elif advantage < -0.5:
                weakest_criteria.append(criterion.replace('_', ' ').title())
        
        if strongest_criteria:
            print(f"• GraphRAG Strengths: {', '.join(strongest_criteria)}")
        if weakest_criteria:
            print(f"• GraphRAG Weaknesses: {', '.join(weakest_criteria)}")
    
    # Category insights
    if 'category_performance' in report and report['category_performance']:
        best_categories = []
        worst_categories = []
        
        for category, performance in report['category_performance'].items():
            total = sum(performance.values())
            if total > 0:
                graphrag_rate = performance.get('graphrag', 0) / total
                if graphrag_rate > 0.6:
                    best_categories.append(category_names.get(category, category))
                elif graphrag_rate < 0.4:
                    worst_categories.append(category_names.get(category, category))
        
        if best_categories:
            print(f"• GraphRAG Best Categories: {', '.join(best_categories)}")
        if worst_categories:
            print(f"• GraphRAG Challenging Categories: {', '.join(worst_categories)}")
    
    print(f"\n📁 FULL RESULTS:")
    print(f"Report: {latest_report}")
    
    # Look for detailed results and CSV
    detailed_files = list(latest_report.parent.glob("detailed_evaluation_results_*.json"))
    csv_files = list(latest_report.parent.glob("evaluation_results_*.csv"))
    
    if detailed_files:
        print(f"Detailed Results: {max(detailed_files, key=lambda x: x.stat().st_mtime)}")
    if csv_files:
        print(f"CSV Export: {max(csv_files, key=lambda x: x.stat().st_mtime)}")
    
    print("="*100)

if __name__ == "__main__":
    analyze_final_results()