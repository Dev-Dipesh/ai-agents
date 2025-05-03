"""
Tests for the planning engine.
"""

import unittest
from src.core.planning import DefaultPlanningEngine

class TestDefaultPlanningEngine(unittest.TestCase):
    """Test cases for the default planning engine."""
    
    def setUp(self):
        """Set up the test environment."""
        self.planning_engine = DefaultPlanningEngine()
    
    def test_create_plan(self):
        """Test creating a basic plan."""
        query = "What are the investment prospects for renewable energy?"
        plan = self.planning_engine.create_plan(query)
        
        # Check plan structure
        self.assertIsInstance(plan, dict)
        self.assertEqual(plan["query"], query)
        self.assertIn("steps", plan)
        self.assertIsInstance(plan["steps"], list)
        self.assertGreater(len(plan["steps"]), 0)
        
        # Check step structure
        first_step = plan["steps"][0]
        self.assertIn("id", first_step)
        self.assertIn("name", first_step)
        self.assertIn("description", first_step)
    
    def test_research_depth(self):
        """Test that different research depths create different plans."""
        query = "Analyze Tesla stock"
        
        # Create plans with different depths
        light_plan = self.planning_engine.create_plan(query, research_depth="light")
        standard_plan = self.planning_engine.create_plan(query, research_depth="standard")
        deep_plan = self.planning_engine.create_plan(query, research_depth="deep")
        expert_plan = self.planning_engine.create_plan(query, research_depth="expert")
        
        # Check that depths are set correctly
        self.assertEqual(light_plan["depth"], "light")
        self.assertEqual(standard_plan["depth"], "standard")
        self.assertEqual(deep_plan["depth"], "deep")
        self.assertEqual(expert_plan["depth"], "expert")
        
        # Check that deeper research has more steps
        self.assertLessEqual(len(light_plan["steps"]), len(standard_plan["steps"]))
        self.assertLessEqual(len(standard_plan["steps"]), len(deep_plan["steps"]))
        self.assertLessEqual(len(deep_plan["steps"]), len(expert_plan["steps"]))
    
    def test_validate_plan(self):
        """Test plan validation."""
        # Create a valid plan
        query = "What are the investment prospects for tech stocks?"
        plan = self.planning_engine.create_plan(query)
        
        # Valid plan should pass validation
        is_valid, error = self.planning_engine.validate_plan(plan)
        self.assertTrue(is_valid)
        self.assertIsNone(error)
        
        # Test invalid plan (no steps)
        invalid_plan = {
            "query": query,
            "steps": []
        }
        is_valid, error = self.planning_engine.validate_plan(invalid_plan)
        self.assertFalse(is_valid)
        self.assertIsNotNone(error)
        
        # Test invalid plan (no query)
        invalid_plan = {
            "steps": plan["steps"]
        }
        is_valid, error = self.planning_engine.validate_plan(invalid_plan)
        self.assertFalse(is_valid)
    
    def test_adjust_plan_depth(self):
        """Test adjusting the depth of an existing plan."""
        query = "Analyze Amazon stock"
        original_plan = self.planning_engine.create_plan(query, research_depth="standard")
        
        # Adjust to light depth
        light_plan = self.planning_engine.adjust_plan_depth(original_plan, "light")
        self.assertEqual(light_plan["depth"], "light")
        self.assertLessEqual(len(light_plan["steps"]), len(original_plan["steps"]))
        
        # Adjust to expert depth
        expert_plan = self.planning_engine.adjust_plan_depth(original_plan, "expert")
        self.assertEqual(expert_plan["depth"], "expert")
        self.assertGreaterEqual(len(expert_plan["steps"]), len(original_plan["steps"]))
        
        # Test with invalid depth
        with self.assertRaises(ValueError):
            self.planning_engine.adjust_plan_depth(original_plan, "invalid_depth")
    
    def test_serialize_and_deserialize(self):
        """Test serializing and deserializing a plan."""
        query = "What are the top performing ETFs this year?"
        original_plan = self.planning_engine.create_plan(query)
        
        # Serialize
        serialized = self.planning_engine.serialize_plan(original_plan)
        self.assertIsNotNone(serialized)
        
        # Deserialize
        deserialized = self.planning_engine.deserialize_plan(serialized)
        self.assertEqual(deserialized["query"], original_plan["query"])
        self.assertEqual(len(deserialized["steps"]), len(original_plan["steps"]))
        self.assertEqual(deserialized["depth"], original_plan["depth"])


if __name__ == "__main__":
    unittest.main()
