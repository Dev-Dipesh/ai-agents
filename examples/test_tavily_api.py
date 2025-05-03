#!/usr/bin/env python
"""
Test script to examine Tavily API response format.
This helps debug the title extraction issue in our Finance Research Agent.
"""

import os
import json
import logging
from dotenv import load_dotenv
import sys

# Add the src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_tavily():
    """
    Set up the Tavily API client using both direct and LangChain methods.
    Returns both clients for comparison.
    """
    try:
        # Method 1: Direct Tavily API
        direct_client = None
        try:
            from tavily import TavilyClient
            tavily_api_key = os.environ.get("TAVILY_API_KEY")
            if tavily_api_key:
                direct_client = TavilyClient(api_key=tavily_api_key)
                logger.info("Successfully initialized direct Tavily client")
            else:
                logger.warning("TAVILY_API_KEY not found in environment variables")
        except ImportError:
            logger.warning("Tavily package not found. Try: pip install tavily-python")
        except Exception as e:
            logger.error(f"Error initializing direct Tavily client: {e}")
        
        # Method 2: LangChain Tavily
        langchain_client = None
        try:
            from langchain_community.utilities import TavilySearchResults
            tavily_api_key = os.environ.get("TAVILY_API_KEY")
            if tavily_api_key:
                langchain_client = TavilySearchResults(api_key=tavily_api_key, max_results=5)
                logger.info("Successfully initialized LangChain Tavily client")
            else:
                logger.warning("TAVILY_API_KEY not found in environment variables")
        except ImportError:
            logger.warning("LangChain or Tavily package not found. Try: pip install langchain-community tavily-python")
        except Exception as e:
            logger.error(f"Error initializing LangChain Tavily client: {e}")
        
        return direct_client, langchain_client
    
    except Exception as e:
        logger.error(f"Error setting up Tavily: {e}")
        return None, None

def test_direct_tavily(client, query="renewable energy stocks 2025"):
    """Test direct Tavily API and examine response format."""
    if not client:
        logger.error("Direct Tavily client not initialized")
        return None
    
    try:
        logger.info(f"Executing direct Tavily search with query: '{query}'")
        response = client.search(query=query, search_depth="basic", max_results=5)
        
        # Examine response format
        logger.info(f"Response keys: {list(response.keys())}")
        if "results" in response and len(response["results"]) > 0:
            sample_result = response["results"][0]
            logger.info(f"Sample result keys: {list(sample_result.keys())}")
            logger.info(f"Sample title: {sample_result.get('title')}")
            logger.info(f"Sample URL: {sample_result.get('url')}")
        
        # Pretty print full response
        logger.info("Full response structure:")
        print(json.dumps(response, indent=2))
        
        return response
    except Exception as e:
        logger.error(f"Error with direct Tavily search: {e}")
        return None

def test_langchain_tavily(client, query="renewable energy stocks 2025"):
    """Test LangChain Tavily integration and examine response format."""
    if not client:
        logger.error("LangChain Tavily client not initialized")
        return None
    
    try:
        logger.info(f"Executing LangChain Tavily search with query: '{query}'")
        results = client.invoke(query)
        
        # Examine response format
        if isinstance(results, list) and len(results) > 0:
            sample_result = results[0]
            logger.info(f"Sample result keys: {list(sample_result.keys())}")
            logger.info(f"Sample title: {sample_result.get('title')}")
            logger.info(f"Sample URL: {sample_result.get('url')}")
        
        # Pretty print full response
        logger.info("Full response structure:")
        print(json.dumps(results, indent=2))
        
        return results
    except Exception as e:
        logger.error(f"Error with LangChain Tavily search: {e}")
        return None

def main():
    """Main function to run the tests."""
    # Load environment variables
    load_dotenv()
    
    # Set up Tavily
    direct_client, langchain_client = setup_tavily()
    
    # Run tests
    print("\n=== TESTING DIRECT TAVILY API ===\n")
    if direct_client:
        direct_results = test_direct_tavily(direct_client)
    else:
        print("Skipping direct Tavily API test as client initialization failed")
    
    print("\n=== TESTING LANGCHAIN TAVILY API ===\n")
    if langchain_client:
        langchain_results = test_langchain_tavily(langchain_client)
    else:
        print("Skipping LangChain Tavily API test as client initialization failed")

if __name__ == "__main__":
    main()
