"""
Comprehensive metrics and evaluation framework for GraphRAG vs Traditional RAG comparison
"""

import json
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import statistics
from collections import Counter, defaultdict

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    from scipy import stats
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

@dataclass
class EvaluationMetrics:
    """Comprehensive metrics for evaluation results"""
    
    # Basic Performance Metrics
    total_queries: int = 0
    graphrag_wins: int = 0
    traditional_rag_wins: int = 0
    ties: int = 0
    
    # Win Rates
    graphrag_win_rate: float = 0.0
    traditional_rag_win_rate: float = 0.0
    tie_rate: float = 0.0
    
    # Confidence Metrics
    avg_confidence: float = 0.0
    high_confidence_decisions: int = 0  # confidence > 80
    low_confidence_decisions: int = 0   # confidence < 50
    
    # Criteria-based Performance
    criteria_performance: Dict[str, Dict[str, float]] = None
    
    # Category-based Performance
    category_performance: Dict[str, Dict[str, int]] = None
    
    # Complexity-based Performance
    complexity_performance: Dict[str, Dict[str, int]] = None
    
    # Expected vs Actual Performance
    prediction_accuracy: float = 0.0
    
    # Statistical Significance
    statistical_significance: Optional[Dict[str, float]] = None

class EvaluationAnalyzer:
    """Analyzer for comprehensive evaluation results"""
    
    def __init__(self):
        self.results = []
        self.metrics = EvaluationMetrics()
    
    def add_result(self, result: Dict):
        """Add a single evaluation result"""
        self.results.append(result)
    
    def add_results(self, results: List[Dict]):
        """Add multiple evaluation results"""
        self.results.extend(results)
    
    def analyze(self) -> EvaluationMetrics:
        """Perform comprehensive analysis of results"""
        if not self.results:
            return self.metrics
        
        # Basic performance metrics
        self._calculate_basic_metrics()
        
        # Confidence analysis
        self._analyze_confidence()
        
        # Criteria-based analysis
        self._analyze_criteria_performance()
        
        # Category-based analysis
        self._analyze_category_performance()
        
        # Complexity-based analysis
        self._analyze_complexity_performance()
        
        # Prediction accuracy
        self._calculate_prediction_accuracy()
        
        # Statistical significance
        self._calculate_statistical_significance()
        
        return self.metrics
    
    def _calculate_basic_metrics(self):
        """Calculate basic performance metrics"""
        self.metrics.total_queries = len(self.results)
        
        winners = [r.get('winner', 'tie') for r in self.results]
        winner_counts = Counter(winners)
        
        self.metrics.graphrag_wins = winner_counts.get('summary_a', 0)  # Assuming GraphRAG is summary_a
        self.metrics.traditional_rag_wins = winner_counts.get('summary_b', 0)
        self.metrics.ties = winner_counts.get('tie', 0)
        
        if self.metrics.total_queries > 0:
            self.metrics.graphrag_win_rate = self.metrics.graphrag_wins / self.metrics.total_queries
            self.metrics.traditional_rag_win_rate = self.metrics.traditional_rag_wins / self.metrics.total_queries
            self.metrics.tie_rate = self.metrics.ties / self.metrics.total_queries
    
    def _analyze_confidence(self):
        """Analyze confidence scores"""
        confidences = [r.get('confidence', 0) for r in self.results]
        
        if confidences:
            self.metrics.avg_confidence = statistics.mean(confidences)
            self.metrics.high_confidence_decisions = sum(1 for c in confidences if c > 80)
            self.metrics.low_confidence_decisions = sum(1 for c in confidences if c < 50)
    
    def _analyze_criteria_performance(self):
        """Analyze performance across different criteria"""
        criteria_scores = defaultdict(lambda: {'graphrag': [], 'traditional_rag': []})
        
        for result in self.results:
            criteria_data = result.get('criteria_scores', {})
            for criterion, scores in criteria_data.items():
                if isinstance(scores, dict):
                    criteria_scores[criterion]['graphrag'].append(scores.get('summary_a', 0))
                    criteria_scores[criterion]['traditional_rag'].append(scores.get('summary_b', 0))
        
        # Calculate average scores for each criterion
        self.metrics.criteria_performance = {}
        for criterion, scores in criteria_scores.items():
            self.metrics.criteria_performance[criterion] = {
                'graphrag_avg': statistics.mean(scores['graphrag']) if scores['graphrag'] else 0,
                'traditional_rag_avg': statistics.mean(scores['traditional_rag']) if scores['traditional_rag'] else 0,
                'graphrag_advantage': 0
            }
            
            # Calculate advantage
            if scores['graphrag'] and scores['traditional_rag']:
                graphrag_avg = statistics.mean(scores['graphrag'])
                traditional_avg = statistics.mean(scores['traditional_rag'])
                self.metrics.criteria_performance[criterion]['graphrag_advantage'] = graphrag_avg - traditional_avg
    
    def _analyze_category_performance(self):
        """Analyze performance by query category"""
        category_results = defaultdict(lambda: {'graphrag': 0, 'traditional_rag': 0, 'ties': 0})
        
        for result in self.results:
            category = result.get('category', 'unknown')
            winner = result.get('winner', 'tie')
            
            if winner == 'summary_a':  # GraphRAG
                category_results[category]['graphrag'] += 1
            elif winner == 'summary_b':  # Traditional RAG
                category_results[category]['traditional_rag'] += 1
            else:
                category_results[category]['ties'] += 1
        
        self.metrics.category_performance = dict(category_results)
    
    def _analyze_complexity_performance(self):
        """Analyze performance by query complexity"""
        complexity_results = defaultdict(lambda: {'graphrag': 0, 'traditional_rag': 0, 'ties': 0})
        
        for result in self.results:
            complexity = result.get('complexity', 'medium')
            winner = result.get('winner', 'tie')
            
            if winner == 'summary_a':  # GraphRAG
                complexity_results[complexity]['graphrag'] += 1
            elif winner == 'summary_b':  # Traditional RAG
                complexity_results[complexity]['traditional_rag'] += 1
            else:
                complexity_results[complexity]['ties'] += 1
        
        self.metrics.complexity_performance = dict(complexity_results)
    
    def _calculate_prediction_accuracy(self):
        """Calculate how well we predicted GraphRAG advantages"""
        correct_predictions = 0
        total_predictions = 0
        
        for result in self.results:
            expected_advantage = result.get('expected_advantage', 'medium')
            winner = result.get('winner', 'tie')
            
            if expected_advantage == 'high':
                # We predicted GraphRAG would win
                if winner == 'summary_a':
                    correct_predictions += 1
                total_predictions += 1
            elif expected_advantage == 'low':
                # We predicted Traditional RAG would win
                if winner == 'summary_b':
                    correct_predictions += 1
                total_predictions += 1
        
        if total_predictions > 0:
            self.metrics.prediction_accuracy = correct_predictions / total_predictions
    
    def _calculate_statistical_significance(self):
        """Calculate statistical significance of results"""
        if len(self.results) < 30:  # Not enough data for meaningful statistics
            return
        
        if not SCIPY_AVAILABLE:
            # Simple fallback significance test
            graphrag_wins = self.metrics.graphrag_wins
            total_queries = self.metrics.total_queries
            
            # Simple z-test approximation
            expected = total_queries * 0.5
            observed = graphrag_wins
            
            # Basic significance assessment
            difference = abs(observed - expected)
            significance_threshold = total_queries * 0.1  # 10% threshold
            
            self.metrics.statistical_significance = {
                'p_value': None,
                'significant_at_05': difference > significance_threshold,
                'significant_at_01': difference > significance_threshold * 1.5,
                'effect_size': abs(self.metrics.graphrag_win_rate - 0.5),
                'note': 'scipy not available, using simplified significance test'
            }
            return
        
        # Full significance test using binomial distribution
        graphrag_wins = self.metrics.graphrag_wins
        total_queries = self.metrics.total_queries
        
        # Two-tailed test
        p_value = 2 * min(
            stats.binom.cdf(graphrag_wins, total_queries, 0.5),
            1 - stats.binom.cdf(graphrag_wins, total_queries, 0.5)
        )
        
        self.metrics.statistical_significance = {
            'p_value': p_value,
            'significant_at_05': p_value < 0.05,
            'significant_at_01': p_value < 0.01,
            'effect_size': abs(self.metrics.graphrag_win_rate - 0.5)
        }
    
    def generate_report(self) -> Dict:
        """Generate comprehensive evaluation report"""
        report = {
            'evaluation_summary': {
                'timestamp': datetime.now().isoformat(),
                'total_queries': self.metrics.total_queries,
                'graphrag_wins': self.metrics.graphrag_wins,
                'traditional_rag_wins': self.metrics.traditional_rag_wins,
                'ties': self.metrics.ties,
                'graphrag_win_rate': round(self.metrics.graphrag_win_rate * 100, 2),
                'traditional_rag_win_rate': round(self.metrics.traditional_rag_win_rate * 100, 2),
                'tie_rate': round(self.metrics.tie_rate * 100, 2)
            },
            'confidence_analysis': {
                'average_confidence': round(self.metrics.avg_confidence, 2),
                'high_confidence_decisions': self.metrics.high_confidence_decisions,
                'low_confidence_decisions': self.metrics.low_confidence_decisions,
                'high_confidence_percentage': round(
                    (self.metrics.high_confidence_decisions / self.metrics.total_queries) * 100, 2
                ) if self.metrics.total_queries > 0 else 0
            },
            'criteria_performance': self.metrics.criteria_performance,
            'category_performance': self.metrics.category_performance,
            'complexity_performance': self.metrics.complexity_performance,
            'prediction_accuracy': round(self.metrics.prediction_accuracy * 100, 2),
            'statistical_significance': self.metrics.statistical_significance
        }
        
        return report
    
    def save_detailed_results(self, filename: str):
        """Save detailed results to JSON file"""
        detailed_results = {
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'total_queries': len(self.results),
                'evaluation_framework': 'GraphRAG vs Traditional RAG Comprehensive Evaluation'
            },
            'summary_metrics': self.generate_report(),
            'detailed_results': self.results
        }
        
        with open(filename, 'w') as f:
            json.dump(detailed_results, f, indent=2)
    
    def export_to_csv(self, filename: str):
        """Export results to CSV for further analysis"""
        if not PANDAS_AVAILABLE:
            # Fallback CSV export without pandas
            import csv
            if not self.results:
                return
            
            with open(filename, 'w', newline='') as csvfile:
                fieldnames = self.results[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for row in self.results:
                    # Flatten nested dictionaries for CSV export
                    flat_row = {}
                    for key, value in row.items():
                        if isinstance(value, dict):
                            flat_row[key] = str(value)
                        else:
                            flat_row[key] = value
                    writer.writerow(flat_row)
        else:
            df = pd.DataFrame(self.results)
            df.to_csv(filename, index=False)
    
    def print_summary(self):
        """Print a summary of the evaluation results"""
        print("=" * 80)
        print("GRAPHRAG vs TRADITIONAL RAG - COMPREHENSIVE EVALUATION RESULTS")
        print("=" * 80)
        
        print(f"\n📊 OVERALL PERFORMANCE:")
        print(f"Total Queries Evaluated: {self.metrics.total_queries}")
        print(f"GraphRAG Wins: {self.metrics.graphrag_wins} ({self.metrics.graphrag_win_rate:.1%})")
        print(f"Traditional RAG Wins: {self.metrics.traditional_rag_wins} ({self.metrics.traditional_rag_win_rate:.1%})")
        print(f"Ties: {self.metrics.ties} ({self.metrics.tie_rate:.1%})")
        
        print(f"\n🎯 CONFIDENCE ANALYSIS:")
        print(f"Average Confidence: {self.metrics.avg_confidence:.1f}/100")
        print(f"High Confidence Decisions (>80): {self.metrics.high_confidence_decisions}")
        print(f"Low Confidence Decisions (<50): {self.metrics.low_confidence_decisions}")
        
        if self.metrics.criteria_performance:
            print(f"\n📋 CRITERIA PERFORMANCE:")
            for criterion, performance in self.metrics.criteria_performance.items():
                advantage = performance['graphrag_advantage']
                print(f"{criterion.replace('_', ' ').title()}: GraphRAG {advantage:+.2f} points")
        
        if self.metrics.category_performance:
            print(f"\n🏷️ CATEGORY PERFORMANCE:")
            for category, performance in self.metrics.category_performance.items():
                total = sum(performance.values())
                graphrag_rate = performance['graphrag'] / total if total > 0 else 0
                print(f"{category.replace('_', ' ').title()}: GraphRAG {graphrag_rate:.1%} win rate")
        
        if self.metrics.statistical_significance:
            print(f"\n📈 STATISTICAL SIGNIFICANCE:")
            sig = self.metrics.statistical_significance
            print(f"P-value: {sig['p_value']:.4f}")
            print(f"Significant at α=0.05: {sig['significant_at_05']}")
            print(f"Effect Size: {sig['effect_size']:.3f}")
        
        print(f"\n🔮 PREDICTION ACCURACY: {self.metrics.prediction_accuracy:.1%}")
        print("=" * 80)

def create_evaluation_framework():
    """Create and return an evaluation framework instance"""
    return EvaluationAnalyzer()

if __name__ == "__main__":
    # Example usage
    analyzer = EvaluationAnalyzer()
    
    # Add sample results for testing
    sample_results = [
        {
            'query': 'Test query 1',
            'category': 'ai_ml_research',
            'complexity': 'high',
            'expected_advantage': 'high',
            'winner': 'summary_a',
            'confidence': 85,
            'criteria_scores': {
                'completeness': {'summary_a': 8, 'summary_b': 6},
                'accuracy': {'summary_a': 9, 'summary_b': 7}
            }
        },
        {
            'query': 'Test query 2',
            'category': 'technical_deep_dive',
            'complexity': 'medium',
            'expected_advantage': 'low',
            'winner': 'summary_b',
            'confidence': 75,
            'criteria_scores': {
                'completeness': {'summary_a': 7, 'summary_b': 8},
                'accuracy': {'summary_a': 8, 'summary_b': 9}
            }
        }
    ]
    
    analyzer.add_results(sample_results)
    metrics = analyzer.analyze()
    analyzer.print_summary()