"""
Simple test script for the Finance Research Agent.
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Add the src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agents.finance import FinanceResearchAgent

def main():
    """Test the finance research agent."""
    # Load environment variables
    load_dotenv()
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    print("Initializing Finance Research Agent...")
    
    # Initialize the agent
    agent = FinanceResearchAgent()
    
    print("Agent initialized successfully!")
    
    # Print available tools
    print("\nAvailable tools:")
    for tool in agent.get_available_tools():
        print(f"- {tool['name']}: {tool['description']}")
    
    print("\nTest complete!")

if __name__ == "__main__":
    main()
