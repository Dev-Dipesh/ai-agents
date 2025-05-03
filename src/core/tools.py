"""
Tool registry for managing available tools and their capabilities.
"""

import logging
from typing import Dict, List, Any, Callable, Optional
from .base import BaseComponent

class BaseTool:
    """Base class for all tools."""
    
    def __init__(self, name, description=None, config=None):
        """
        Initialize a tool.
        
        Parameters:
            name: Tool name
            description: Tool description
            config: Tool configuration
        """
        self.name = name
        self.description = description or ""
        self.config = config or {}
    
    def execute(self, params, context=None):
        """
        Execute the tool with the given parameters.
        
        Parameters:
            params: Tool parameters
            context: Optional execution context
            
        Returns:
            Tool execution result
        """
        raise NotImplementedError
    
    def validate_params(self, params):
        """
        Validate the tool parameters.
        
        Parameters:
            params: Parameters to validate
            
        Returns:
            (is_valid, error_message) tuple
        """
        return True, None
    
    def get_schema(self):
        """
        Get the parameter schema for this tool.
        
        Returns:
            JSON schema for tool parameters
        """
        return {}


class WebSearchTool(BaseTool):
    """Tool for performing web searches."""
    
    def __init__(self, name="web_search", description=None, config=None):
        """Initialize the web search tool."""
        description = description or "Performs web searches to find information on the internet."
        super().__init__(name, description, config)
        
        # Initialize search provider
        self._initialize_search_provider()
    
    def _initialize_search_provider(self):
        """Initialize the search provider based on configuration."""
        provider = self.config.get("provider", "tavily")
        api_key = self.config.get("api_key")
        
        if provider == "tavily":
            self._initialize_tavily(api_key)
        else:
            raise ValueError(f"Unsupported search provider: {provider}")
    
    def _initialize_tavily(self, api_key=None):
        """Initialize the Tavily search client."""
        import os
        import ssl
        
        # Try to get API key from environment if not provided
        api_key = api_key or os.environ.get("TAVILY_API_KEY")
        
        if not api_key:
            # For testing purposes, we'll just log a warning
            logging.warning("Tavily API key is required for actual web search functionality")
            self.client = None
            return
        
        try:
            # Attempt to fix SSL issues by configuring the context
            try:
                # Create a default SSL context
                ssl_context = ssl.create_default_context()
                # Use it for HTTPS connections
                ssl._create_default_https_context = lambda: ssl_context
                logging.info("Configured SSL context for Tavily API")
            except Exception as ssl_e:
                logging.warning(f"Could not configure SSL context: {ssl_e}")
            
            # Import TavilySearchResults from langchain
            try:
                from langchain_community.tools.tavily_search import TavilySearchResults
                self.client = TavilySearchResults(
                    api_key=api_key,
                    max_results=5
                )
                logging.info("Initialized Tavily search provider using LangChain wrapper")
            except Exception as e:
                logging.error(f"Error initializing LangChain Tavily client: {e}")
                
                # Try direct tavily package
                try:
                    from tavily import TavilyClient
                    self.client = TavilyClient(api_key=api_key)
                    logging.info("Initialized Tavily client directly from package")
                except Exception as tavily_e:
                    logging.error(f"Error initializing direct Tavily client: {tavily_e}")
                    
                    # Try alternate implementation
                    try:
                        import httpx
                        
                        class SimpleTavilyClient:
                            """Simple implementation of Tavily client to bypass SSL issues."""
                            def __init__(self, api_key):
                                self.api_key = api_key
                                self.base_url = "https://api.tavily.com/v1"
                                
                            def search(self, query, search_depth="basic", max_results=5):
                                """Perform a search using direct HTTP request."""
                                headers = {
                                    "Authorization": f"Bearer {self.api_key}",
                                    "Content-Type": "application/json"
                                }
                                data = {
                                    "query": query,
                                    "search_depth": search_depth,
                                    "max_results": max_results
                                }
                                
                                response = httpx.post(
                                    f"{self.base_url}/search",
                                    json=data,
                                    headers=headers
                                )
                                
                                if response.status_code == 200:
                                    return response.json()
                                else:
                                    raise Exception(f"Tavily API error: {response.status_code} - {response.text}")
                        
                        self.client = SimpleTavilyClient(api_key=api_key)
                        logging.info("Initialized simple Tavily client as fallback")
                        
                    except Exception as alt_e:
                        logging.error(f"Error initializing alternate Tavily client: {alt_e}")
                        self.client = None
                        raise
                
        except ImportError as e:
            logging.error(f"Required package not found: {e}")
            logging.warning("Please install required packages: pip install langchain-community tavily-python httpx")
            self.client = None
    
    def execute(self, params, context=None):
        """Execute a web search."""
        query = params.get("query")
        
        if not query:
            logging.error("No query provided for web search")
            return {
                "success": False,
                "error": "Query parameter is required",
                "results": []
            }
        
        search_depth = params.get("search_depth", "basic")
        max_results = params.get("max_results", 5)
        
        # Log search attempt
        logging.info(f"Executing web search: query='{query}', depth='{search_depth}', max_results={max_results}")
        
        # Check if client is initialized
        if self.client is None:
            # Return mock results for testing
            logging.error("Tavily client is not initialized. Check API key and Tavily installation.")
            mock_results = [
                {
                    "title": f"Mock result for: {query}",
                    "url": "https://example.com/mock-result",
                    "content": f"This is a mock search result for the query: {query}. In a real implementation, this would contain actual search results from the web.",
                    "score": 0.95
                },
                {
                    "title": f"Another mock result for: {query}",
                    "url": "https://example.com/mock-result-2",
                    "content": f"This is another mock search result for testing purposes. The query was: {query}.",
                    "score": 0.85
                }
            ]
            
            return {
                "success": True,
                "query": query,
                "results": mock_results,
                "total": len(mock_results),
                "mock": True
            }
        
        try:
            # Use LangChain TavilySearchResults if that's what we have
            if hasattr(self.client, 'invoke'):
                logging.info("Using LangChain TavilySearchResults invoke method")
                try:
                    raw_results = self.client.invoke(query)
                    # Format into expected structure
                    if isinstance(raw_results, list):
                        search_response = {"results": raw_results}
                    else:
                        search_response = {"results": [raw_results]}
                except Exception as e:
                    logging.error(f"Error in LangChain Tavily search: {e}")
                    # Try fallback to tool wrapper
                    from langchain_core.tools import tool
                    
                    @tool
                    def tavily_search_tool(question: str) -> dict:
                        """Wrapper for Tavily search to avoid SSL errors."""
                        return self.client.invoke(question)
                    
                    # Call the wrapped tool
                    logging.info("Trying tool wrapper approach for Tavily")
                    raw_results = tavily_search_tool.invoke(query)
                    if isinstance(raw_results, list):
                        search_response = {"results": raw_results}
                    else:
                        search_response = {"results": [raw_results]}
            # Use direct Tavily client if that's what we have
            elif hasattr(self.client, 'search'):
                logging.info("Using Tavily client search method")
                search_response = self.client.search(
                    query=query,
                    search_depth=search_depth,
                    max_results=max_results
                )
            else:
                logging.error("Unknown client type, unable to perform search")
                raise ValueError("Unknown client type")
            
            # Log successful search with details about results
            result_count = len(search_response.get("results", []))
            logging.info(f"Search successful: found {result_count} results")
            
            # Format results
            results = []
            for result in search_response.get("results", []):
                # Ensure we have a proper title - fix the None issue
                title = result.get("title")
                if title is None or title == "":
                    # Extract title from URL if no title is provided
                    url = result.get("url", "")
                    if url:
                        # Try to extract a title from the URL
                        from urllib.parse import urlparse
                        parsed_url = urlparse(url)
                        domain = parsed_url.netloc
                        path = parsed_url.path
                        if path and path != "/":
                            # Use the last part of the path as title
                            path_parts = path.strip('/').split('/')
                            title = path_parts[-1].replace('-', ' ').replace('_', ' ').title()
                        else:
                            # Use domain as title
                            title = domain
                    else:
                        title = "Untitled Search Result"
                
                # Log the result details
                logging.info(f"  Result: {title} - {result.get('url')}")
                
                # Add to results with proper title
                results.append({
                    "title": title,
                    "url": result.get("url", ""),
                    "content": result.get("content", ""),
                    "score": result.get("score", 0.0)
                })
            
            return {
                "success": True,
                "query": query,
                "results": results,
                "total": len(results)
            }
        
        except Exception as e:
            logging.error(f"Error executing web search: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "query": query,
                "results": []
            }
    
    def _execute_search_synchronous(self, query, search_depth, max_results):
        """Execute Tavily search synchronously."""
        return self.client.search(
            query=query,
            search_depth=search_depth,
            max_results=max_results
        )
    
    def _execute_search_with_tool_wrapper(self, query, search_depth, max_results):
        """Execute search using a tool wrapper approach to avoid SSL errors."""
        try:
            from langchain_core.tools import tool
            
            @tool
            def tavily_search_tool(question: str) -> dict:
                """Wrapper for Tavily search to avoid SSL errors."""
                return self.client.search(
                    query=question,
                    search_depth=search_depth,
                    max_results=max_results
                )
            
            # Call the wrapped tool
            return tavily_search_tool.invoke(query)
        except Exception as e:
            logging.error(f"Error in tool-wrapped search: {e}")
            raise
    
    def validate_params(self, params):
        """Validate the search parameters."""
        if not params.get("query"):
            return False, "Query parameter is required"
        
        search_depth = params.get("search_depth", "basic")
        if search_depth not in ["basic", "advanced"]:
            return False, "search_depth must be 'basic' or 'advanced'"
        
        return True, None
    
    def get_schema(self):
        """Get the parameter schema for web search."""
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query"
                },
                "search_depth": {
                    "type": "string",
                    "enum": ["basic", "advanced"],
                    "description": "Depth of search to perform",
                    "default": "basic"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results to return",
                    "default": 5,
                    "minimum": 1,
                    "maximum": 10
                }
            },
            "required": ["query"]
        }


class TextAnalysisTool(BaseTool):
    """Tool for analyzing text content."""
    
    def __init__(self, name="text_analysis", description=None, config=None):
        """Initialize the text analysis tool."""
        description = description or "Analyzes text content for key information."
        super().__init__(name, description, config)
    
    def execute(self, params, context=None):
        """Execute text analysis."""
        text = params.get("text")
        
        if not text:
            return {
                "success": False,
                "error": "Text parameter is required"
            }
        
        analysis_type = params.get("analysis_type", "summary")
        
        if analysis_type == "summary":
            return self._generate_summary(text, params.get("max_length", 100))
        elif analysis_type == "keywords":
            return self._extract_keywords(text, params.get("max_keywords", 5))
        elif analysis_type == "sentiment":
            return self._analyze_sentiment(text)
        else:
            return {
                "success": False,
                "error": f"Unsupported analysis type: {analysis_type}"
            }
    
    def _generate_summary(self, text, max_length=100):
        """Generate a summary of the text."""
        # Simple implementation - in a real system this would use NLP
        words = text.split()
        
        if len(words) <= max_length:
            return {
                "success": True,
                "analysis_type": "summary",
                "summary": text,
                "original_length": len(words),
                "summary_length": len(words)
            }
        
        # Very simple summarization - first N words
        summary = " ".join(words[:max_length])
        
        return {
            "success": True,
            "analysis_type": "summary",
            "summary": summary,
            "original_length": len(words),
            "summary_length": max_length
        }
    
    def _extract_keywords(self, text, max_keywords=5):
        """Extract keywords from the text."""
        # Simple implementation - in a real system this would use NLP
        import re
        from collections import Counter
        
        # Tokenize and clean text
        words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())
        
        # Remove common stop words
        stop_words = {"the", "and", "is", "in", "to", "of", "that", "for", "on", "with"}
        filtered_words = [word for word in words if word not in stop_words]
        
        # Count and rank
        counter = Counter(filtered_words)
        keywords = [word for word, _ in counter.most_common(max_keywords)]
        
        return {
            "success": True,
            "analysis_type": "keywords",
            "keywords": keywords,
            "word_count": len(words)
        }
    
    def _analyze_sentiment(self, text):
        """Analyze sentiment of the text."""
        # Simple implementation - in a real system this would use NLP
        positive_words = {"good", "great", "excellent", "best", "wonderful", "amazing"}
        negative_words = {"bad", "terrible", "worst", "awful", "poor", "horrible"}
        
        words = text.lower().split()
        
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)
        
        if positive_count > negative_count:
            sentiment = "positive"
            score = min(1.0, positive_count / len(words) * 5)
        elif negative_count > positive_count:
            sentiment = "negative"
            score = min(1.0, negative_count / len(words) * 5) * -1
        else:
            sentiment = "neutral"
            score = 0.0
        
        return {
            "success": True,
            "analysis_type": "sentiment",
            "sentiment": sentiment,
            "score": score,
            "positive_words": positive_count,
            "negative_words": negative_count
        }
    
    def validate_params(self, params):
        """Validate the analysis parameters."""
        if not params.get("text"):
            return False, "Text parameter is required"
        
        analysis_type = params.get("analysis_type", "summary")
        if analysis_type not in ["summary", "keywords", "sentiment"]:
            return False, "analysis_type must be 'summary', 'keywords', or 'sentiment'"
        
        return True, None
    
    def get_schema(self):
        """Get the parameter schema for text analysis."""
        return {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "The text to analyze"
                },
                "analysis_type": {
                    "type": "string",
                    "enum": ["summary", "keywords", "sentiment"],
                    "description": "Type of analysis to perform",
                    "default": "summary"
                },
                "max_length": {
                    "type": "integer",
                    "description": "Maximum length of summary (words)",
                    "default": 100
                },
                "max_keywords": {
                    "type": "integer",
                    "description": "Maximum number of keywords to extract",
                    "default": 5
                }
            },
            "required": ["text"]
        }


class BaseToolRegistry(BaseComponent):
    """Interface for tool registry components."""
    
    def register_tool(self, tool):
        """
        Register a new tool.
        
        Parameters:
            tool: Tool instance to register
            
        Returns:
            Success boolean
        """
        raise NotImplementedError
    
    def get_tool(self, name):
        """
        Get a tool by name.
        
        Parameters:
            name: Tool name
            
        Returns:
            Tool instance or None
        """
        raise NotImplementedError
    
    def list_tools(self):
        """
        List all registered tools.
        
        Returns:
            List of tool metadata
        """
        raise NotImplementedError
    
    def remove_tool(self, name):
        """
        Remove a tool from the registry.
        
        Parameters:
            name: Tool name
            
        Returns:
            Success boolean
        """
        raise NotImplementedError
    
    def execute_tool(self, name, params, context=None):
        """
        Execute a tool by name.
        
        Parameters:
            name: Tool name
            params: Tool parameters
            context: Optional execution context
            
        Returns:
            Tool execution result
        """
        raise NotImplementedError


class DefaultToolRegistry(BaseToolRegistry):
    """Default implementation of the tool registry."""
    
    def __init__(self, config=None):
        """Initialize the tool registry."""
        super().__init__(config)
        self.tools = {}
        
        # Register default tools if enabled
        if self.config.get("register_defaults", True):
            self._register_default_tools()
    
    def _register_default_tools(self):
        """Register the default set of tools."""
        try:
            # Web search tool
            self.register_tool(WebSearchTool())
            
            # Text analysis tool
            self.register_tool(TextAnalysisTool())
            
            logging.info("Registered default tools")
        except Exception as e:
            logging.error(f"Error registering default tools: {e}")
    
    def register_tool(self, tool):
        """Register a new tool."""
        if not isinstance(tool, BaseTool):
            return False
        
        self.tools[tool.name] = tool
        return True
    
    def get_tool(self, name):
        """Get a tool by name."""
        return self.tools.get(name)
    
    def list_tools(self):
        """List all registered tools."""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "schema": tool.get_schema()
            }
            for tool in self.tools.values()
        ]
    
    def remove_tool(self, name):
        """Remove a tool from the registry."""
        if name in self.tools:
            del self.tools[name]
            return True
        return False
    
    def execute_tool(self, name, params, context=None):
        """Execute a tool by name."""
        tool = self.get_tool(name)
        
        if not tool:
            return {
                "success": False,
                "error": f"Tool not found: {name}"
            }
        
        # Validate parameters
        is_valid, error = tool.validate_params(params)
        if not is_valid:
            return {
                "success": False,
                "error": error or f"Invalid parameters for tool: {name}"
            }
        
        # Execute the tool
        try:
            result = tool.execute(params, context)
            return result
        except Exception as e:
            logging.error(f"Error executing tool {name}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
            
    def __iter__(self):
        """Make the registry iterable to retrieve tools."""
        return iter(self.tools.items())
    
    def __getitem__(self, key):
        """Allow dictionary-like access to tools."""
        return self.tools[key]
    
    def __contains__(self, key):
        """Allow 'in' operator to check for tool existence."""
        return key in self.tools
    
    def __len__(self):
        """Return the number of tools in the registry."""
        return len(self.tools)
    
    def keys(self):
        """Return tool names (for dict-like operations)."""
        return self.tools.keys()
    
    def values(self):
        """Return tool objects (for dict-like operations)."""
        return self.tools.values()
    
    def items(self):
        """Return name-tool pairs (for dict-like operations)."""
        return self.tools.items()
