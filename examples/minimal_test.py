"""
Minimal test script to initialize the Finance Research Agent.
"""

import os
import sys
import logging

# Add the src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Test importing and initializing the agent."""
    try:
        logger.info("Importing BaseAgent...")
        from src.core.agent import BaseAgent
        
        logger.info("Creating BaseAgent...")
        base_agent = BaseAgent()
        logger.info("BaseAgent created successfully!")
        
        logger.info("Importing FinanceResearchAgent...")
        from src.agents.finance import FinanceResearchAgent
        
        logger.info("Creating FinanceResearchAgent...")
        finance_agent = FinanceResearchAgent()
        logger.info("FinanceResearchAgent created successfully!")
        
        print("Test complete!")
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
