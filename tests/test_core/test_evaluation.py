"""
Tests for the evaluation system.
"""

import unittest
from src.core.evaluation import DefaultEvaluationSystem

class TestDefaultEvaluationSystem(unittest.TestCase):
    """Test cases for the default evaluation system."""
    
    def setUp(self):
        """Set up the test environment."""
        self.evaluation_system = DefaultEvaluationSystem()
    
    def test_evaluate_response(self):
        """Test evaluating a response."""
        query = "What are the prospects for AI stocks in 2025?"
        response = """
        AI stocks show strong growth potential in 2025 due to increasing enterprise adoption 
        and expanding use cases. Companies with established AI infrastructure and clear 
        monetization strategies are particularly well-positioned. However, investors should 
        be aware of regulatory risks and potential market saturation in certain segments.
        Overall, a selective approach focusing on companies with sustainable competitive 
        advantages is recommended.
        """
        
        # Evaluate the response
        evaluation = self.evaluation_system.evaluate_response(query, response)
        
        # Check evaluation structure
        self.assertIsInstance(evaluation, dict)
        self.assertIn("id", evaluation)
        self.assertIn("timestamp", evaluation)
        self.assertIn("query", evaluation)
        self.assertIn("scores", evaluation)
        self.assertIn("overall_score", evaluation)
        self.assertIn("feedback", evaluation)
        
        # Check scores
        self.assertGreater(len(evaluation["scores"]), 0)
        for metric, score in evaluation["scores"].items():
            self.assertIsInstance(score, float)
            self.assertGreaterEqual(score, 0.0)
            self.assertLessEqual(score, 1.0)
        
        # Check overall score
        self.assertGreaterEqual(evaluation["overall_score"], 0.0)
        self.assertLessEqual(evaluation["overall_score"], 1.0)
    
    def test_register_metric(self):
        """Test registering a custom metric."""
        # Define a custom metric
        def custom_metric(query, response):
            """Custom evaluation metric."""
            return 0.85  # Arbitrary score
        
        # Register the metric
        result = self.evaluation_system.register_metric("custom_test_metric", custom_metric)
        self.assertTrue(result)
        
        # Get available metrics
        metrics = self.evaluation_system.get_metrics()
        self.assertIn("custom_test_metric", metrics)
        
        # Test evaluation with the custom metric
        query = "Test query"
        response = "Test response"
        evaluation = self.evaluation_system.evaluate_response(
            query, response, criteria=["custom_test_metric"])
        
        # Check that the custom metric was used
        self.assertIn("custom_test_metric", evaluation["scores"])
        self.assertEqual(evaluation["scores"]["custom_test_metric"], 0.85)
    
    def test_evaluation_history(self):
        """Test logging and retrieving evaluation history."""
        # Clear any existing history
        self.evaluation_system.evaluation_history = []
        
        # Create test evaluations
        query1 = "Query 1"
        response1 = "Response 1"
        evaluation1 = self.evaluation_system.evaluate_response(query1, response1)
        
        query2 = "Query 2"
        response2 = "Response 2"
        evaluation2 = self.evaluation_system.evaluate_response(query2, response2)
        
        # Get evaluation history
        history = self.evaluation_system.get_evaluation_history()
        
        # Check history
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["query"], query1)
        self.assertEqual(history[1]["query"], query2)
        
        # Test filtering
        filtered_history = self.evaluation_system.get_evaluation_history(
            filters={"max_results": 1})
        self.assertEqual(len(filtered_history), 1)
        
        # Test filtering by score
        high_score = max(evaluation1["overall_score"], evaluation2["overall_score"])
        threshold = high_score - 0.1  # Set threshold just below highest score
        
        filtered_history = self.evaluation_system.get_evaluation_history(
            filters={"min_score": threshold})
        
        # At least one evaluation should meet the threshold
        self.assertGreaterEqual(len(filtered_history), 1)
    
    def test_default_metrics(self):
        """Test that default metrics are registered and working."""
        metrics = self.evaluation_system.get_metrics()
        
        # Check for default metrics
        default_metrics = ["relevance", "helpfulness", "correctness", "completeness"]
        for metric in default_metrics:
            self.assertIn(metric, metrics)
        
        # Test that each metric can be used
        query = "Test query"
        response = "Test response"
        
        for metric in default_metrics:
            evaluation = self.evaluation_system.evaluate_response(
                query, response, criteria=[metric])
            self.assertIn(metric, evaluation["scores"])
            
            # Score should be a float between 0 and 1
            score = evaluation["scores"][metric]
            self.assertIsInstance(score, float)
            self.assertGreaterEqual(score, 0.0)
            self.assertLessEqual(score, 1.0)


if __name__ == "__main__":
    unittest.main()
