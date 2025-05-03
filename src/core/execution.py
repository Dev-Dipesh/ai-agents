"""
Execution engine for running plan steps using available tools.
"""

import time
import logging
from .base import BaseComponent

class BaseExecutionEngine(BaseComponent):
    """Interface for execution components."""
    
    def execute_plan(self, plan, context=None):
        """
        Execute the given plan.
        
        Parameters:
            plan: The research plan to execute
            context: Optional context information
            
        Returns:
            Execution results with all step outputs
        """
        raise NotImplementedError
    
    def execute_step(self, step, context=None):
        """
        Execute a single step of the plan.
        
        Parameters:
            step: The step to execute
            context: Optional context information
            
        Returns:
            Step execution result
        """
        raise NotImplementedError
    
    def select_tool(self, step, available_tools):
        """
        Select appropriate tool for the step.
        
        Parameters:
            step: The step to select a tool for
            available_tools: Dictionary of available tools
            
        Returns:
            Selected tool instance
        """
        raise NotImplementedError
    
    def process_result(self, step_result, context=None):
        """
        Process the result of a step execution.
        
        Parameters:
            step_result: The raw result from tool execution
            context: Optional context information
            
        Returns:
            Processed result
        """
        raise NotImplementedError
    
    def handle_execution_error(self, error, step, context=None):
        """
        Handle errors during execution.
        
        Parameters:
            error: The error that occurred
            step: The step that was being executed
            context: Optional context information
            
        Returns:
            Error handling result
        """
        raise NotImplementedError


class DefaultExecutionEngine(BaseExecutionEngine):
    """Default implementation of the execution engine."""
    
    def __init__(self, config=None):
        """
        Initialize with optional tool registry.
        
        Parameters:
            config: Engine configuration
        """
        super().__init__(config or {})
        
        # Handle tool registry from config
        if isinstance(config, dict) and "tool_registry" in config:
            self.tool_registry = config["tool_registry"]
            logging.info(f"Tool registry set from config")
        else:
            self.tool_registry = {}
            logging.warning("No tool registry provided, using empty registry")
        
        self.results = {}
    
    def execute_plan(self, plan, context=None):
        """Execute the given plan."""
        context = context or {}
        start_time = time.time()
        
        # Initialize results
        results = {
            "plan_id": plan.get("id", "unknown"),
            "query": plan.get("query", ""),
            "steps": [],
            "sources": [],
            "success": True,
            "error": None,
            "execution_time": 0
        }
        
        logging.info(f"Executing plan with {len(plan.get('steps', []))} steps")
        
        # Ensure we have a tool registry
        if not self.tool_registry:
            logging.error("No tool registry available for execution")
            results["success"] = False
            results["error"] = "No tool registry available"
            return results
            
        # Extract the tools from the registry
        if hasattr(self.tool_registry, 'tools') and isinstance(self.tool_registry.tools, dict):
            logging.info(f"Tool registry has {len(self.tool_registry.tools)} tools")
            available_tools = self.tool_registry.tools
        else:
            logging.info(f"Using tool_registry directly with {len(self.tool_registry) if hasattr(self.tool_registry, '__len__') else 'unknown'} tools")
            available_tools = self.tool_registry
        
        # Log available tools
        if isinstance(available_tools, dict):
            logging.info(f"Available tools: {list(available_tools.keys())}")
        else:
            logging.warning(f"Available tools is not a dictionary: {type(available_tools)}")
        
        # Store query in context for tools to use
        if "query" in plan:
            context["original_query"] = plan["query"]
        
        # Convert list-based steps to dict if needed
        steps = plan.get("steps", [])
        for i, step in enumerate(steps):
            # Ensure step has an id
            if "id" not in step:
                step["id"] = i
                
            # Ensure step has a name
            if "name" not in step:
                step["name"] = f"Step {i}"
                
            # Ensure step has a search query if it's not specified
            if "search_query" not in step and "description" in step:
                step["search_query"] = step["description"]
        
        # Execute each step
        for step in steps:
            try:
                logging.info(f"Executing step: {step.get('name', 'Unknown step')}")
                
                # Add any search query override
                if "search_query" in step:
                    context["search_query"] = step["search_query"]
                    logging.info(f"Using search query: {step['search_query']}")
                
                # Execute the step
                step_result = self.execute_step(step, context)
                results["steps"].append(step_result)
                
                # Check for any sources in the result and add to overall sources
                if step_result.get("success", False) and "result" in step_result:
                    result_data = step_result["result"]
                    if "data" in result_data and isinstance(result_data["data"], list):
                        # For search results
                        for item in result_data["data"]:
                            if "url" in item and "title" in item:
                                # Add to sources if not already present
                                source = {
                                    "title": item.get("title", "Unknown"),
                                    "url": item.get("url", ""),
                                    "content": item.get("content", "")
                                }
                                if source not in results["sources"]:
                                    results["sources"].append(source)
                                    logging.info(f"Added source: {source['title']}")
                
                # Update context with step result for subsequent steps
                context[f"step_{step['id']}_result"] = step_result
                
                # Break execution if step indicates to stop
                if step_result.get("stop_execution", False):
                    logging.info("Stopping execution as requested by step")
                    break
                    
            except Exception as e:
                logging.error(f"Error executing step {step.get('name', 'Unknown')}: {str(e)}", exc_info=True)
                error_result = self.handle_execution_error(e, step, context)
                results["steps"].append(error_result)
                results["success"] = False
                results["error"] = str(e)
                
                # Break execution on error unless configured to continue
                if not self.config.get("continue_on_error", False):
                    logging.info("Stopping execution due to error")
                    break
        
        # Calculate execution time
        end_time = time.time()
        results["execution_time"] = end_time - start_time
        logging.info(f"Plan execution completed in {results['execution_time']:.2f} seconds")
        
        return results
    
    def execute_step(self, step, context=None):
        """Execute a single step of the plan."""
        context = context or {}
        step_id = step.get("id", 0)
        step_name = step.get("name", "Unknown")
        
        logging.info(f"Executing step {step_id}: {step_name}")
        
        # Determine what query to use first, before selecting a tool
        search_query = ""
        
        if "search_query" in step:
            search_query = step["search_query"]
            logging.info(f"Using search_query from step: {search_query}")
        elif "search_query" in context:
            search_query = context["search_query"]
            logging.info(f"Using search_query from context: {search_query}")
        elif "description" in step:
            search_query = step["description"]
            logging.info(f"Using description as search_query: {search_query}")
        else:
            # Fall back to original query with step name
            original_query = context.get("original_query", "")
            search_query = f"{step_name} {original_query}"
            logging.info(f"Using fallback search_query: {search_query}")
        
        # Store search query in context for subsequent steps
        context["current_search_query"] = search_query
        
        # Get the appropriate tools
        if hasattr(self.tool_registry, 'tools') and isinstance(self.tool_registry.tools, dict):
            available_tools = self.tool_registry.tools
        else:
            available_tools = self.tool_registry
            
        # Select appropriate tool
        tool = self.select_tool(step, available_tools)
        
        # Execute the tool
        if tool:
            logging.info(f"Using tool: {tool.name}")
            
            # Prepare parameters for the tool
            params = {
                "query": search_query
            }
            
            # Add search depth if available in context
            if "research_depth" in context:
                depth = context["research_depth"]
                if depth in ["deep", "expert"]:
                    params["search_depth"] = "advanced"
                else:
                    params["search_depth"] = "basic"
            
            # Set max results
            params["max_results"] = 5
            
            # Execute the tool with parameters
            try:
                logging.info(f"Executing tool {tool.name} with params: {params}")
                raw_result = tool.execute(params, context)
                
                # Check for success
                if raw_result.get("success", False):
                    logging.info(f"Tool execution successful")
                else:
                    error_msg = raw_result.get("error", "Unknown error")
                    logging.error(f"Tool execution failed: {error_msg}")
                
                processed_result = self.process_result(raw_result, context)
                
                # Log results summary
                if "results" in raw_result:
                    results = raw_result["results"]
                    result_count = len(results) if isinstance(results, list) else 1
                    logging.info(f"Tool returned {result_count} results")
                elif "data" in raw_result:
                    data = raw_result["data"]
                    data_count = len(data) if isinstance(data, list) else 1
                    logging.info(f"Tool returned {data_count} data items")
                else:
                    logging.info(f"Tool returned result with keys: {raw_result.keys()}")
            except Exception as e:
                logging.error(f"Error executing tool {tool.name}: {str(e)}", exc_info=True)
                processed_result = {"success": False, "error": str(e), "data": []}
        else:
            # No tool available, return empty result
            logging.warning(f"No suitable tool found for step: {step_name}")
            processed_result = {"success": False, "error": "No suitable tool found", "data": []}
        
        # Combine into result
        result = {
            "step_id": step_id,
            "step_name": step_name,
            "search_query": search_query,
            "success": processed_result.get("success", False),
            "result": processed_result
        }
        
        # Store in results
        self.results[step_id] = result
        
        logging.info(f"Step {step_id} completed with success: {result['success']}")
        
        return result
    
    def select_tool(self, step, available_tools):
        """Select appropriate tool for the step."""
        # Handle the case where available_tools is a DefaultToolRegistry object
        if hasattr(available_tools, 'tools') and isinstance(available_tools.tools, dict):
            available_tools = available_tools.tools
            logging.info(f"Using tools from DefaultToolRegistry, available tools: {list(available_tools.keys())}")
        
        # Validate available_tools is a dictionary
        if not isinstance(available_tools, dict):
            logging.error(f"available_tools is not a dictionary: {type(available_tools)}")
            # Try to convert it to a dictionary if possible
            try:
                if hasattr(available_tools, '__dict__'):
                    available_tools = available_tools.__dict__
                    logging.info(f"Converted available_tools to dictionary, keys: {list(available_tools.keys())}")
            except Exception as e:
                logging.error(f"Could not convert available_tools to dictionary: {e}")
                return None
        
        # Log available tools for debugging
        logging.info(f"Available tools: {list(available_tools.keys())}")
        
        # Simple implementation - look for tool specified in step
        tool_name = step.get("tool")
        if tool_name and tool_name in available_tools:
            logging.info(f"Found specified tool: {tool_name}")
            return available_tools[tool_name]
        
        # If no specific tool, try to infer from step type/name
        step_type = step.get("type", "").lower()
        step_name = step.get("name", "").lower()
        
        # Search-related steps - highest priority for finance research
        if any(term in step_name for term in ["search", "find", "lookup", "research", "market", "overview", "analysis"]):
            if "web_search" in available_tools:
                logging.info(f"Selected web_search tool for step: {step_name}")
                return available_tools["web_search"]
        
        # Analysis steps
        if any(term in step_name for term in ["analyze", "analysis", "evaluate"]):
            if "text_analysis" in available_tools:
                logging.info(f"Selected text_analysis tool for step: {step_name}")
                return available_tools["text_analysis"]
        
        # Try any available tool as fallback
        if "web_search" in available_tools:
            logging.info(f"Falling back to web_search tool for step: {step_name}")
            return available_tools["web_search"]
        elif len(available_tools) > 0:
            first_tool_name = next(iter(available_tools.keys()))
            logging.info(f"Falling back to first available tool: {first_tool_name}")
            return available_tools[first_tool_name]
            
        # No suitable tool found
        logging.warning(f"No suitable tool found for step: {step_name}")
        return None
    
    def process_result(self, step_result, context=None):
        """Process the result of a step execution."""
        # Deep copy to avoid modifying the original
        processed = dict(step_result)
        
        # Normalize results format to ensure we have a data field
        if "data" not in processed and "results" in processed:
            processed["data"] = processed["results"]
            
        # Ensure we have a success field
        if "success" not in processed:
            processed["success"] = "error" not in processed
            
        # Handle cases where the tool returns a nested structure
        if "result" in processed and isinstance(processed["result"], dict):
            if "data" not in processed and "data" in processed["result"]:
                processed["data"] = processed["result"]["data"]
                
        # If there's still no data field, ensure it exists
        if "data" not in processed:
            processed["data"] = []
            
        return processed
    
    def handle_execution_error(self, error, step, context=None):
        """Handle errors during execution."""
        return {
            "step_id": step.get("id", 0),
            "step_name": step.get("name", ""),
            "success": False,
            "error": str(error),
            "result": {"data": None, "error": str(error)}
        }
