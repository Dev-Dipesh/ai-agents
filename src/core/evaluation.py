"""
Evaluation system for assessing response quality.
"""

import time
import uuid
from typing import Dict, List, Any, Optional, Callable
from .base import BaseComponent

class BaseEvaluationSystem(BaseComponent):
    """Interface for evaluation components."""
    
    def evaluate_response(self, query, response, criteria=None):
        """
        Evaluate response quality.
        
        Parameters:
            query: The original query
            response: The agent's response
            criteria: Optional evaluation criteria
            
        Returns:
            Evaluation results
        """
        raise NotImplementedError
    
    def register_metric(self, name, metric_function):
        """
        Register a new evaluation metric.
        
        Parameters:
            name: Metric name
            metric_function: Function that calculates the metric
            
        Returns:
            Success boolean
        """
        raise NotImplementedError
    
    def get_metrics(self):
        """
        Get all available metrics.
        
        Returns:
            Dictionary of metric names and functions
        """
        raise NotImplementedError
    
    def log_evaluation(self, evaluation_result):
        """
        Log evaluation result to history.
        
        Parameters:
            evaluation_result: The evaluation to log
            
        Returns:
            Success boolean
        """
        raise NotImplementedError
    
    def get_evaluation_history(self, filters=None):
        """
        Get evaluation history with optional filtering.
        
        Parameters:
            filters: Optional filters to apply
            
        Returns:
            List of filtered evaluation results
        """
        raise NotImplementedError


class DefaultEvaluationSystem(BaseEvaluationSystem):
    """Default implementation of the evaluation system."""
    
    def __init__(self, config=None):
        """Initialize the evaluation system."""
        super().__init__(config)
        self.metrics = {}
        self.evaluation_history = []
        
        # Register default metrics
        self.register_default_metrics()
    
    def register_default_metrics(self):
        """Register the default evaluation metrics."""
        self.register_metric("relevance", self._metric_relevance)
        self.register_metric("helpfulness", self._metric_helpfulness)
        self.register_metric("correctness", self._metric_correctness)
        self.register_metric("completeness", self._metric_completeness)
    
    def evaluate_response(self, query, response, criteria=None):
        """Evaluate response quality."""
        criteria = criteria or list(self.metrics.keys())
        
        evaluation = {
            "id": str(uuid.uuid4()),
            "timestamp": time.time(),
            "query": query,
            "response_summary": response[:200] + "..." if len(response) > 200 else response,
            "scores": {},
            "overall_score": 0.0,
            "feedback": ""
        }
        
        # Calculate scores for each metric
        valid_metrics = 0
        total_score = 0.0
        
        for metric_name in criteria:
            if metric_name in self.metrics:
                score = self.metrics[metric_name](query, response)
                evaluation["scores"][metric_name] = score
                total_score += score
                valid_metrics += 1
        
        # Calculate overall score
        if valid_metrics > 0:
            evaluation["overall_score"] = total_score / valid_metrics
        
        # Generate feedback based on scores
        evaluation["feedback"] = self._generate_feedback(evaluation["scores"])
        
        # Log the evaluation
        self.log_evaluation(evaluation)
        
        return evaluation
    
    def register_metric(self, name, metric_function):
        """Register a new evaluation metric."""
        if not callable(metric_function):
            return False
        
        self.metrics[name] = metric_function
        return True
    
    def get_metrics(self):
        """Get all available metrics."""
        return {name: func.__doc__ for name, func in self.metrics.items()}
    
    def log_evaluation(self, evaluation_result):
        """Log evaluation result to history."""
        self.evaluation_history.append(evaluation_result)
        return True
    
    def get_evaluation_history(self, filters=None):
        """Get evaluation history with optional filtering."""
        if not filters:
            return self.evaluation_history
        
        filtered_history = self.evaluation_history
        
        # Apply filters
        if "min_score" in filters:
            filtered_history = [
                eval for eval in filtered_history 
                if eval["overall_score"] >= filters["min_score"]
            ]
        
        if "max_results" in filters and isinstance(filters["max_results"], int):
            filtered_history = filtered_history[:filters["max_results"]]
        
        return filtered_history
    
    # Default metric implementations
    def _metric_relevance(self, query, response):
        """
        Evaluates how relevant the response is to the query.
        
        This is a placeholder implementation. In a real system, this would use
        more sophisticated NLP techniques or LLM evaluation.
        """
        # Placeholder - returns random score between 0.7 and 1.0
        import random
        return random.uniform(0.7, 1.0)
    
    def _metric_helpfulness(self, query, response):
        """
        Evaluates how helpful the response is.
        
        This is a placeholder implementation.
        """
        import random
        return random.uniform(0.7, 1.0)
    
    def _metric_correctness(self, query, response):
        """
        Evaluates the factual correctness of the response.
        
        This is a placeholder implementation.
        """
        import random
        return random.uniform(0.7, 1.0)
    
    def _metric_completeness(self, query, response):
        """
        Evaluates whether the response fully addresses the query.
        
        This is a placeholder implementation.
        """
        import random
        return random.uniform(0.7, 1.0)
    
    def _generate_feedback(self, scores):
        """Generate feedback based on evaluation scores."""
        feedback = "Response evaluation: "
        
        # Determine areas of strength
        strengths = [metric for metric, score in scores.items() if score >= 0.8]
        if strengths:
            feedback += f"Strong in {', '.join(strengths)}. "
        
        # Determine areas for improvement
        improvements = [metric for metric, score in scores.items() if score < 0.7]
        if improvements:
            feedback += f"Could improve in {', '.join(improvements)}. "
        
        # Overall assessment
        avg_score = sum(scores.values()) / len(scores) if scores else 0
        if avg_score >= 0.9:
            feedback += "Excellent overall response."
        elif avg_score >= 0.7:
            feedback += "Good response with minor improvement opportunities."
        else:
            feedback += "Response needs significant improvement."
        
        return feedback
