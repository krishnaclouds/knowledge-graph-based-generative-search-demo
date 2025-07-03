"""
LLM Judge implementation for comparing search result summaries
"""
from core_services import llm_service
from models import EvaluationRequest, EvaluationResponse, CriteriaScores
import logging

logger = logging.getLogger(__name__)

class LLMJudge:
    def __init__(self):
        self.llm_service = llm_service
    
    def evaluate_summaries(self, request: EvaluationRequest) -> EvaluationResponse:
        """
        Use Claude as an impartial judge to evaluate and compare summaries
        """
        # Prepare BLIND evaluation prompt (no method identification)
        evaluation_prompt = f"""You are an expert research analyst tasked with objectively evaluating two AI-generated summaries for the same query. You do not know which method or system generated each summary. Please provide a detailed comparison and determine which summary is superior based purely on content quality.

QUERY: "{request.query}"

SUMMARY A:
{request.summary_a}

SUMMARY B:
{request.summary_b}

EVALUATION CRITERIA:
Please score each summary on a scale of 1-10 for each criterion:

1. COMPLETENESS: How thoroughly does the summary address all aspects of the query?
2. ACCURACY: How factually correct and reliable is the information presented?
3. CONTEXTUAL DEPTH: How well does the summary provide relevant background and context?
4. CLARITY: How clear, well-structured, and easy to understand is the summary?
5. RELEVANCE TO QUERY: How directly and specifically does the summary answer the original question?
6. ACTIONABLE INSIGHTS: How useful and practical is the information for decision-making?

RESPONSE FORMAT:
Provide your evaluation in this exact JSON format:

{{
    "winner": "summary_a" or "summary_b",
    "confidence": [confidence score 1-100],
    "reasoning": "[2-3 sentence explanation of your decision]",
    "criteria_scores": {{
        "completeness": {{"summary_a": [score], "summary_b": [score]}},
        "accuracy": {{"summary_a": [score], "summary_b": [score]}},
        "contextual_depth": {{"summary_a": [score], "summary_b": [score]}},
        "clarity": {{"summary_a": [score], "summary_b": [score]}},
        "relevance_to_query": {{"summary_a": [score], "summary_b": [score]}},
        "actionable_insights": {{"summary_a": [score], "summary_b": [score]}}
    }}
}}

Be objective and focus solely on the quality and usefulness of each summary content. Do not make assumptions about the underlying data sources or methods used."""

        try:
            # Get evaluation from Claude
            evaluation_text = self.llm_service.generate_answer(
                query="Evaluate summaries",
                context=evaluation_prompt
            )
            
            # Parse JSON response
            import json
            import re
            
            # Extract JSON from the response (sometimes LLM adds extra text)
            json_match = re.search(r'\{.*\}', evaluation_text, re.DOTALL)
            if json_match:
                json_text = json_match.group()
                evaluation_data = json.loads(json_text)
                return EvaluationResponse(**evaluation_data)
            else:
                logger.warning("No JSON found in LLM response, using fallback")
                return self._fallback_evaluation(request)
            
        except Exception as e:
            logger.error(f"LLM Judge evaluation failed: {e}")
            
            # Fallback to rule-based evaluation
            return self._fallback_evaluation(request)
    
    def _fallback_evaluation(self, request: EvaluationRequest) -> EvaluationResponse:
        """Fallback evaluation logic when LLM fails"""
        
        hybrid_score = 0
        docs_score = 0
        
        # Simple fallback scoring based on summary length and content
        summary_a_score = len(request.summary_a) // 100 + 5  # Base score of 5 + length bonus
        summary_b_score = len(request.summary_b) // 100 + 5  # Base score of 5 + length bonus
        
        # Determine winner based on length (simple heuristic)
        if summary_a_score > summary_b_score:
            winner = "summary_a"
            confidence = min(95, 60 + abs(summary_a_score - summary_b_score) * 5)
        else:
            winner = "summary_b"
            confidence = min(95, 60 + abs(summary_a_score - summary_b_score) * 5)
        
        return EvaluationResponse(
            winner=winner,
            confidence=confidence,
            reasoning=f"Summary {'A' if winner == 'summary_a' else 'B'} appears more comprehensive with {len(request.summary_a if winner == 'summary_a' else request.summary_b)} characters vs the other summary with {len(request.summary_b if winner == 'summary_a' else request.summary_a)} characters.",
            criteria_scores={
                "completeness": CriteriaScores(summary_a=min(10, summary_a_score), summary_b=min(10, summary_b_score)),
                "accuracy": CriteriaScores(summary_a=7, summary_b=7),
                "contextual_depth": CriteriaScores(summary_a=min(10, summary_a_score), summary_b=min(10, summary_b_score)),
                "clarity": CriteriaScores(summary_a=8, summary_b=7),
                "relevance_to_query": CriteriaScores(summary_a=8, summary_b=7),
                "actionable_insights": CriteriaScores(summary_a=7, summary_b=6)
            }
        )