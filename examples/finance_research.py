"""
Example script demonstrating the Finance Research Agent.
"""

import os
import sys
import time
import logging
from dotenv import load_dotenv

# Add the src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agents.finance import FinanceResearchAgent
from src.core.utils import get_llm_config_interactive
from src.core.logging_config import setup_logging

def main():
    """Run the finance research agent example."""
    # Load environment variables
    load_dotenv()
    
    # Set up logging
    debug_mode = os.environ.get('DEBUG', 'false').lower() == 'true'
    log_level = 'DEBUG' if debug_mode else 'INFO'
    log_to_console = os.environ.get('LOG_TO_CONSOLE', 'true').lower() == 'true'
    log_to_file = os.environ.get('LOG_TO_FILE', 'false').lower() == 'true'
    
    logger = setup_logging(
        level=log_level,
        log_to_console=log_to_console,
        log_to_file=log_to_file,
        log_dir=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs'),
        log_file=f"finance_agent_{time.strftime('%Y%m%d_%H%M%S')}.log"
    )
    
    # Check for required API keys
    if not os.environ.get("OPENAI_API_KEY"):
        logger.error("OPENAI_API_KEY environment variable is required.")
        print("Error: OPENAI_API_KEY environment variable is required.")
        print("Please set it in the .env file or as an environment variable.")
        return
    
    if not os.environ.get("TAVILY_API_KEY"):
        logger.warning("TAVILY_API_KEY environment variable is recommended for web search.")
        print("Warning: TAVILY_API_KEY environment variable is recommended for web search.")
        print("Limited functionality without it.")
    
    # Enable debug mode if needed
    debug_mode = os.environ.get('DEBUG', 'false').lower() == 'true'
    
    print("Initializing Finance Research Agent...")
    
    # Get LLM configuration interactively
    llm_config = get_llm_config_interactive()
    
    # Initialize agent with LLM configuration
    agent_config = {
        "llm": llm_config,
        "debug": debug_mode
    }
    
    # Initialize agent
    agent = FinanceResearchAgent(agent_config)
    
    # Log available tools
    logger.info(f"Available tools: {[tool['name'] for tool in agent.get_available_tools()]}")
    
    # Example queries
    example_queries = [
        "What are the investment prospects for renewable energy stocks in 2025?",
        "Should I invest in artificial intelligence companies right now?",
        "Analyze the financial performance of Apple over the last 3 years.",
        "What are the risks of investing in emerging markets?",
        "Compare Tesla and Ford as investment opportunities."
    ]
    
    # Print example queries
    print("\nExample queries:")
    for i, query in enumerate(example_queries, 1):
        print(f"{i}. {query}")
    
    while True:
        # Get user input
        print("\nEnter the number of an example query, or type your own query (or 'q' to quit):")
        user_input = input("> ")
        
        if user_input.lower() == 'q':
            print("\nThank you for using the Finance Research Agent!")
            break
        
        # Debug mode toggle
        if user_input.lower() == 'debug':
            debug_mode = not debug_mode
            print(f"Debug mode {'enabled' if debug_mode else 'disabled'}")
            continue
        
        # Process user input
        try:
            query_idx = int(user_input) - 1
            if 0 <= query_idx < len(example_queries):
                query = example_queries[query_idx]
            else:
                print("Invalid number. Please enter a number between 1 and", len(example_queries))
                continue
        except ValueError:
            # User entered their own query
            query = user_input
        
        # Select research depth
        print("\nSelect research depth:")
        print("1. Light (quick overview)")
        print("2. Standard (balanced depth)")
        print("3. Deep (comprehensive analysis)")
        print("4. Expert (in-depth research)")
        
        depth_input = input("> ")
        
        research_depth_map = {
            "1": "light",
            "2": "standard",
            "3": "deep",
            "4": "expert"
        }
        
        research_depth = research_depth_map.get(depth_input, "standard")
        
        # Run the agent
        print(f"\nAnalyzing: {query}")
        print(f"Research depth: {research_depth}")
        print("This may take a few minutes depending on the complexity of the query...\n")
        
        start_time = time.time()
        
        try:
            # Add analysis date to context
            context = {
                "analysis_date": time.strftime("%Y-%m-%d"),
                "debug_mode": debug_mode,
                "research_depth": research_depth
            }
            
            # Run the analysis
            try:
                response = agent.analyze_investment(
                    query=query,
                    research_depth=research_depth,
                    context=context,
                    evaluate=True
                )
                
                # Print the results
                print("\n" + "="*80)
                print("\nRESULTS:\n")
                
                # Handle both string and dict responses (for compatibility)
                if isinstance(response, str):
                    print(response)
                    response_text = response
                else:
                    print(response.get("response_text", "No response generated"))
                    response_text = response.get("response_text", "")
                
                print("\n" + "="*80)
                
                # Print evaluation if available
                if isinstance(response, dict) and "evaluation" in response:
                    print("\nEVALUATION:\n")
                    scores = response["evaluation"]["scores"]
                    
                    for metric, score in scores.items():
                        print(f"{metric}: {score:.2f}")
                    
                    print("\nFeedback:")
                    print(response["evaluation"]["feedback"])
                elif "EVALUATION:" in response_text:
                    # Extract evaluation from text response
                    eval_section = response_text.split("EVALUATION:")[1]
                    if "FEEDBACK:" in eval_section.upper():
                        eval_section = eval_section.split("FEEDBACK:")[0]
                    print("\nEVALUATION:")
                    print(eval_section.strip())
            except Exception as e:
                logger.error(f"Error in analysis: {str(e)}", exc_info=True)
                print(f"Error performing analysis: {str(e)}")
            
            execution_time = time.time() - start_time
            print(f"\nAnalysis completed in {execution_time:.2f} seconds")
            
            # Log completion
            logger.info(f"Analysis of '{query}' completed in {execution_time:.2f} seconds")
            
        except Exception as e:
            logger.error(f"Error running analysis: {e}", exc_info=True)
            print(f"Error running analysis: {e}")
            print("Check the log file for more details.")
    
    print("\nThank you for using the Finance Research Agent!")

if __name__ == "__main__":
    main()
