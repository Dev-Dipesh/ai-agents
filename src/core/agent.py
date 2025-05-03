"""
Base agent class for research agents.
"""

import time
import uuid
import logging
from typing import Dict, List, Any, Optional

from .base import BaseComponent
from .planning import BasePlanningEngine, DefaultPlanningEngine
from .execution import BaseExecutionEngine, DefaultExecutionEngine
from .evaluation import BaseEvaluationSystem, DefaultEvaluationSystem
from .tools import BaseToolRegistry, DefaultToolRegistry
from .llm import BaseLLMProviderInterface, DefaultLLMProviderInterface, DummyLLMProvider 
from .config import BaseConfigurationManager, DefaultConfigurationManager
from .citation import BaseCitationTracker, DefaultCitationTracker

class BaseAgent(BaseComponent):
    """Base class for all research agents."""
    
    def __init__(self, config=None):
        """
        Initialize the agent with configuration.
        
        Parameters:
            config: Optional configuration dictionary
        """
        super().__init__(config)
        
        # State tracking
        self.current_run_id = None
        self.current_state = {}
        self.runs_history = {}
        
        # Create placeholders for core components
        self.config_manager = None
        self.planning_engine = None
        self.tool_registry = None
        self.execution_engine = None
        self.evaluation_system = None
        self.llm_provider = None
        self.citation_tracker = None
        
        # Additional initialization - this will set up all components
        self.initialize()
    
    def _init_config_manager(self):
        """Initialize the configuration manager."""
        config_class = self.config.get("config_manager_class", DefaultConfigurationManager)
        return config_class(self.config.get("config_manager_config"))
    
    def _init_planning_engine(self):
        """Initialize the planning engine."""
        planning_class = self.config.get("planning_engine_class", DefaultPlanningEngine)
        return planning_class(self.config.get("planning_engine_config"))
    
    def _init_tool_registry(self):
        """Initialize the tool registry."""
        registry_class = self.config.get("tool_registry_class", DefaultToolRegistry)
        return registry_class(self.config.get("tool_registry_config"))
    
    def _init_execution_engine(self):
        """Initialize the execution engine."""
        execution_class = self.config.get("execution_engine_class", DefaultExecutionEngine)
        
        # Pass tool registry to execution engine
        execution_config = self.config.get("execution_engine_config", {})
        
        # Make sure we have a tool registry
        if hasattr(self, 'tool_registry') and self.tool_registry:
            execution_config["tool_registry"] = self.tool_registry
            logging.info("Passed tool registry to execution engine")
        else:
            logging.warning("No tool registry available for execution engine")
        
        return execution_class(execution_config)
    
    def _init_evaluation_system(self):
        """Initialize the evaluation system."""
        evaluation_class = self.config.get("evaluation_system_class", DefaultEvaluationSystem)
        return evaluation_class(self.config.get("evaluation_system_config"))
    
    def _init_llm_provider(self):
        """Initialize the LLM provider interface."""
        provider_class = self.config.get("llm_provider_class", DefaultLLMProviderInterface)
        provider_config = self.config.get("llm_provider_config", {})
        
        # Check for provider and model in config
        if "llm" in self.config:
            if "default_provider" in self.config["llm"]:
                provider_config["default_provider"] = self.config["llm"]["default_provider"]
            if "default_model" in self.config["llm"]:
                provider_config["default_model"] = self.config["llm"]["default_model"]
        
        try:
            return provider_class(provider_config)
        except Exception as e:
            logging.error(f"Error initializing LLM provider: {e}")
            # Return a dummy provider for testing
            return DummyLLMProvider()
    
    def _init_citation_tracker(self):
        """Initialize the citation tracker."""
        citation_class = self.config.get("citation_tracker_class", DefaultCitationTracker)
        return citation_class(self.config.get("citation_tracker_config"))
    
    def initialize(self):
        """Perform additional initialization."""
        # Initialize components in the correct order
        self.config_manager = self._init_config_manager()
        self.tool_registry = self._init_tool_registry()
        self.execution_engine = self._init_execution_engine()
        self.planning_engine = self._init_planning_engine()
        self.evaluation_system = self._init_evaluation_system()
        self.llm_provider = self._init_llm_provider()
        self.citation_tracker = self._init_citation_tracker()
        
        # Log available tools
        if hasattr(self.tool_registry, 'tools'):
            tool_names = list(self.tool_registry.tools.keys())
        elif isinstance(self.tool_registry, dict):
            tool_names = list(self.tool_registry.keys())
        else:
            tool_names = []
            
        logging.info(f"Available tools: {tool_names}")
    
    def run(self, query, context=None, research_depth=None):
        """
        Run the agent on a query.
        
        Parameters:
            query: User query to research
            context: Optional context information
            research_depth: Optional research depth override
            
        Returns:
            Agent response with results
        """
        try:
            # Generate a run ID
            self.current_run_id = str(uuid.uuid4())
            
            # Initialize run state
            self.current_state = {
                "run_id": self.current_run_id,
                "query": query,
                "context": context or {},
                "start_time": time.time(),
                "end_time": None,
                "status": "running",
                "research_depth": research_depth,
                "steps_completed": 0,
                "error": None
            }
            
            # Add to history
            self.runs_history[self.current_run_id] = self.current_state
            
            # Get research depth from context, parameter, or config
            if research_depth is None:
                if context and "research_depth" in context:
                    research_depth = context["research_depth"]
                else:
                    research_depth = self.config_manager.get_config(
                        "research_depth.default", "standard")
            
            # Validate research depth
            if research_depth not in ["light", "standard", "deep", "expert"]:
                research_depth = "standard"
                logging.warning(f"Invalid research depth provided, using 'standard' instead")
            
            # Update state with final research depth
            self.current_state["research_depth"] = research_depth
            
            # Create a research plan
            plan = self.planning_engine.create_plan(
                query, context=context, research_depth=research_depth)
            
            # Validate the plan
            is_valid, error = self.planning_engine.validate_plan(plan)
            if not is_valid:
                raise ValueError(f"Invalid research plan: {error}")
            
            # Execute the plan
            execution_results = self.execution_engine.execute_plan(plan, context=context)
            
            # Process results and generate response
            response = self._process_results(query, execution_results, context)
            
            # Evaluate response if evaluation is enabled
            if self.config.get("evaluate_responses", False):
                evaluation = self.evaluation_system.evaluate_response(
                    query, response["response_text"])
                response["evaluation"] = evaluation
            
            # Update state
            self.current_state["status"] = "completed"
            self.current_state["end_time"] = time.time()
            self.current_state["execution_time"] = self.current_state["end_time"] - self.current_state["start_time"]
            
            return response
            
        except Exception as e:
            # Log error
            logging.error(f"Error executing agent: {e}")
            
            # Update state
            if self.current_state:
                self.current_state["status"] = "error"
                self.current_state["end_time"] = time.time()
                self.current_state["execution_time"] = self.current_state["end_time"] - self.current_state["start_time"]
                self.current_state["error"] = str(e)
            
            # Re-raise
            raise
    
    def _process_results(self, query, execution_results, context=None):
        """
        Process execution results and generate a response.
        
        Parameters:
            query: Original query
            execution_results: Results from execution engine
            context: Optional context information
            
        Returns:
            Processed response
        """
        # This is a placeholder implementation
        # Domain-specific agents should override this
        
        response_text = f"Research results for query: {query}\n\n"
        
        # Add status
        if execution_results.get("success", False):
            response_text += "Research completed successfully.\n\n"
        else:
            response_text += f"Research encountered errors: {execution_results.get('error', 'Unknown error')}\n\n"
        
        # Add steps summary
        steps = execution_results.get("steps", [])
        response_text += f"Completed {len(steps)} research steps:\n"
        
        for step in steps:
            step_name = step.get("step_name", "Unknown step")
            status = "✓" if step.get("success", False) else "✗"
            response_text += f"- {status} {step_name}\n"
        
        response_text += "\n"
        
        # Add a simple summary
        response_text += "Summary of findings:\n"
        
        for step in steps:
            if step.get("success", False):
                result = step.get("result", {}).get("data")
                if result:
                    response_text += f"- {result[:100]}...\n"
        
        # Create the response object
        response = {
            "run_id": self.current_run_id,
            "query": query,
            "response_text": response_text,
            "execution_results": execution_results,
            "sources": []  # Would be populated with sources in a real implementation
        }
        
        return response
    
    def get_run_state(self, run_id=None):
        """
        Get the state of a specific run or the current run.
        
        Parameters:
            run_id: Optional run ID (uses current run if not provided)
            
        Returns:
            Run state
        """
        if run_id is None:
            run_id = self.current_run_id
        
        if run_id in self.runs_history:
            return self.runs_history[run_id]
        
        return None
    
    def get_runs_history(self, limit=None):
        """
        Get execution history.
        
        Parameters:
            limit: Optional limit on number of runs to return
            
        Returns:
            List of run states
        """
        history = list(self.runs_history.values())
        
        # Sort by start time (newest first)
        history.sort(key=lambda x: x.get("start_time", 0), reverse=True)
        
        if limit:
            history = history[:limit]
        
        return history
    
    def get_available_tools(self):
        """
        Get list of available tools.
        
        Returns:
            List of tool metadata
        """
        return self.tool_registry.list_tools()
    
    def register_tool(self, tool):
        """
        Register a new tool.
        
        Parameters:
            tool: Tool instance to register
            
        Returns:
            Success boolean
        """
        return self.tool_registry.register_tool(tool)


class DefaultAgent(BaseAgent):
    """Default implementation of a research agent."""
    
    def __init__(self, config=None):
        """Initialize the default agent."""
        super().__init__(config)
    
    def _process_results(self, query, execution_results, context=None):
        """Process execution results into a coherent response."""
        # More sophisticated implementation than the base class
        
        steps = execution_results.get("steps", [])
        
        # Gather successful search results
        search_results = []
        for step in steps:
            if step.get("success", False) and step.get("step_name", "").lower().find("search") >= 0:
                result = step.get("result", {})
                if "data" in result and isinstance(result["data"], list):
                    search_results.extend(result["data"])
        
        # Gather analysis results
        analysis_results = []
        for step in steps:
            if step.get("success", False) and step.get("step_name", "").lower().find("analyz") >= 0:
                result = step.get("result", {})
                if "data" in result:
                    analysis_results.append(result["data"])
        
        # Use LLM to synthesize a response
        sources = []
        
        if search_results or analysis_results:
            # Format context for LLM
            llm_context = {
                "query": query,
                "search_results": search_results[:5],  # Limit to top 5
                "analysis_results": analysis_results
            }
            
            # Convert to string format
            prompt = f"""
            Please provide a comprehensive answer to the following query:
            
            QUERY: {query}
            
            Based on the following information:
            
            """
            
            if search_results:
                prompt += "SEARCH RESULTS:\n"
                for i, result in enumerate(search_results[:5]):
                    source_id = self.citation_tracker.register_source({
                        "type": "web",
                        "title": result.get("title", "Search Result"),
                        "url": result.get("url", ""),
                        "site_name": result.get("site_name", ""),
                        "year": time.strftime("%Y")
                    })
                    
                    sources.append({
                        "id": source_id,
                        "title": result.get("title", "Search Result"),
                        "url": result.get("url", "")
                    })
                    
                    content = result.get("content", "")
                    if content:
                        citation_id = self.citation_tracker.cite_source(source_id, content)
                        prompt += f"[{i+1}] {content}\n\n"
            
            if analysis_results:
                prompt += "ANALYSIS RESULTS:\n"
                for i, result in enumerate(analysis_results):
                    prompt += f"[{i+1}] {result}\n\n"
            
            prompt += """
            Provide a well-structured, informative response that directly answers the query.
            Include relevant information from the search results and analysis.
            Be objective and focus on facts from the provided information.
            Cite sources where appropriate using [1], [2], etc.
            """
            
            try:
                # Get response from LLM
                llm_response = self.llm_provider.get_completion(
                    prompt=prompt,
                    parameters={"temperature": 0.3, "max_tokens": 1000}
                )
                
                response_text = llm_response.get("text", "")
                
                # If no usable response, fall back to simple summary
                if not response_text:
                    response_text = f"Research results for query: {query}\n\n"
                    response_text += "No comprehensive response could be generated. Here are the key findings:\n\n"
                    
                    for i, result in enumerate(search_results[:3]):
                        response_text += f"[{i+1}] {result.get('title')}: {result.get('content')[:100]}...\n\n"
            
            except Exception as e:
                logging.error(f"Error generating response with LLM: {e}")
                response_text = f"Research results for query: {query}\n\n"
                response_text += f"Error generating comprehensive response. Raw search results:\n\n"
                
                for i, result in enumerate(search_results[:3]):
                    response_text += f"[{i+1}] {result.get('title')}: {result.get('content')[:100]}...\n\n"
        
        else:
            # No search or analysis results
            response_text = f"Research results for query: {query}\n\n"
            response_text += "No relevant information was found during research. Please try refining your query or adjusting the research parameters."
        
        # Create the response object
        response = {
            "run_id": self.current_run_id,
            "query": query,
            "response_text": response_text,
            "execution_results": execution_results,
            "sources": sources
        }
        
        return response
