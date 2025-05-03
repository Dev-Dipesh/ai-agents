"""
Finance research agent implementation.
"""

import time
import logging
from typing import Dict, List, Any, Optional

from src.core.agent import BaseAgent
from src.core.planning import DefaultPlanningEngine
from src.core.evaluation import DefaultEvaluationSystem

# Import the proper evaluation system
try:
    from .evaluation import FinanceEvaluationSystem
except ImportError:
    # If not available, use the default one
    FinanceEvaluationSystem = DefaultEvaluationSystem
    logging.warning("Could not import FinanceEvaluationSystem, using default")

# If can't import, use the default
try:
    from .planning import FinanceResearchPlanningEngine
except ImportError:
    # If not available, use the default one
    FinanceResearchPlanningEngine = DefaultPlanningEngine
    logging.warning("Could not import FinanceResearchPlanningEngine, using default")

class FinanceResearchAgent(BaseAgent):
    """
    Finance research agent for investment analysis and financial research.
    
    Features:
    - Breaks down complex investment questions into detailed research plans
    - Dynamically adjusts research based on gathered information
    - Provides formatted, visual output suitable for client presentations
    - Includes comprehensive evaluation of financial analysis quality
    """
    
    def __init__(self, config=None):
        """Initialize the finance research agent."""
        # Set default finance-specific configuration
        finance_config = {
            "planning_engine_class": FinanceResearchPlanningEngine,
            "evaluation_system_class": FinanceEvaluationSystem,
            "evaluate_responses": True,
            "finance_config": {
                "analysis_focus": "comprehensive",  # "comprehensive", "risk-focused", "growth-focused"
                "include_market_context": True,
                "include_competitor_analysis": True,
                "visual_outputs": True
            }
        }
        
        # Merge with provided config
        if config:
            self._deep_update(finance_config, config)
        
        # Initialize the base agent with the finance config
        super().__init__(finance_config)
    
    def initialize(self):
        """Perform finance-specific initialization."""
        # Base class initialization must happen first
        super().initialize()
        
        # Register finance-specific evaluation metrics
        self._register_finance_metrics()
        
        # Load any finance-specific tools
        self._register_finance_tools()
        
    def run(self, query, context=None, research_depth=None):
        """
        Run the finance research agent on a query.
        
        Parameters:
            query: The query to research
            context: Optional context information
            research_depth: Optional research depth override
            
        Returns:
            Finance research results
        """
        # Set up finance-specific context
        finance_context = context or {}
        finance_context["domain"] = "finance"
        finance_context["analysis_type"] = "investment"
        finance_context["original_query"] = query
        
        # Add current date/time context if not provided
        if "analysis_date" not in finance_context:
            finance_context["analysis_date"] = time.strftime("%Y-%m-%d")
        
        if "current_year" not in finance_context:
            finance_context["current_year"] = time.strftime("%Y")
            
        if "current_quarter" not in finance_context:
            current_month = int(time.strftime("%m"))
            finance_context["current_quarter"] = f"Q{((current_month-1)//3)+1}"
        
        # Set research depth if provided
        if research_depth:
            finance_context["research_depth"] = research_depth
            
        # Debug mode
        debug_mode = finance_context.get("debug_mode", False) or self.config.get("debug_mode", False)
        finance_context["debug_mode"] = debug_mode
        
        if debug_mode:
            logging.info(f"Finance agent: Processing query: {query}")
            logging.info(f"Context: {finance_context}")
        
        # Create a research plan
        plan = self._create_finance_research_plan(query, finance_context)
        
        # Execute the plan
        execution_results = self.execution_engine.execute_plan(plan, finance_context)
        
        # Process results
        response = self._process_results(query, execution_results, finance_context)
        
        # Add finance-specific post-processing
        if isinstance(response, dict):
            self._enhance_finance_response(response)
            return response["response_text"]
        else:
            # If it's a string, just return it
            return response
    
    def _register_finance_metrics(self):
        """Register finance-specific evaluation metrics."""
        # These would be implemented in the FinanceEvaluationSystem
        # but we're ensuring they're properly initialized
        metrics = [
            "investment_analysis",
            "risk_assessment",
            "market_awareness",
            "financial_literacy"
        ]
        
        for metric in metrics:
            if metric not in self.evaluation_system.get_metrics():
                logging.warning(f"Finance metric {metric} not properly registered")
    
    def _register_finance_tools(self):
        """Register finance-specific tools."""
        # This would register any finance-specific tools with the tool registry
        
        # Check if tool registry is available
        if not hasattr(self, 'tool_registry') or not self.tool_registry:
            logging.warning("Tool registry not available for registering finance tools")
            return
            
        # Log available tools before registration
        tools = self.get_available_tools()
        tool_names = [tool['name'] for tool in tools] if tools else []
        logging.info(f"Available tools: {tool_names}")
        
        # Here you would add any finance-specific tools
        # For example:
        # from src.core.tools import WebSearchTool
        # self.tool_registry.register_tool(WebSearchTool(name="finance_search"))
        
        # For now, just log a message
        logging.info("Finance-specific tools would be registered here")
    
    def analyze_investment(self, query, context=None, research_depth=None, evaluate=True):
        """
        Analyze an investment query.
        
        Parameters:
            query: Investment query to research
            context: Optional context information
            research_depth: Optional research depth override
            evaluate: Whether to evaluate the response
            
        Returns:
            Investment analysis with results
        """
        # Set evaluation flag based on parameter
        old_evaluate = self.config.get("evaluate_responses", False)
        self.config["evaluate_responses"] = evaluate
        
        # Check for debug mode in context
        debug_mode = False
        if context and context.get("debug_mode", False):
            debug_mode = True
            logging.info(f"Debug mode enabled for query: {query}")
        
        try:
            # Add finance-specific context
            finance_context = {
                "domain": "finance",
                "analysis_type": "investment",
                "current_year": time.strftime("%Y"),
                "current_quarter": f"Q{((int(time.strftime('%m'))-1)//3)+1}",
                "debug_mode": debug_mode,
                "original_query": query
            }
            
            # Set research depth
            if research_depth:
                finance_context["research_depth"] = research_depth
            
            # Merge with provided context
            if context:
                finance_context.update(context)
            
            if debug_mode:
                logging.info(f"Starting investment analysis with depth: {finance_context.get('research_depth', 'standard')}")
                logging.info(f"Query: {query}")
                logging.info(f"Context: {finance_context}")
            
            # Create research plan
            plan = self._create_finance_research_plan(query, finance_context)
            
            # Execute the plan
            execution_results = self.execution_engine.execute_plan(plan, finance_context)
            
            # Process results
            response = self._process_results(query, execution_results, finance_context)
            
            # Evaluate if requested
            if evaluate and self.evaluation_system:
                try:
                    evaluation_result = self.evaluation_system.evaluate(
                        query, 
                        response.get("response_text", ""), 
                        finance_context
                    )
                    response["evaluation"] = evaluation_result
                except Exception as e:
                    logging.error(f"Error during evaluation: {str(e)}")
            
            # Add finance-specific enhancements
            self._enhance_finance_response(response)
            
            if debug_mode:
                logging.info("Analysis completed successfully")
                
                # Log sources in debug mode
                if "sources" in response:
                    source_count = len(response["sources"])
                    logging.info(f"Used {source_count} sources in this analysis")
                    if source_count > 0:
                        for i, source in enumerate(response["sources"][:3], 1):
                            logging.info(f"  Source {i}: {source.get('title')} - {source.get('url')}")
                else:
                    logging.info("No sources were used in this analysis")
            
            return response
            
        finally:
            # Restore original evaluation setting
            self.config["evaluate_responses"] = old_evaluate
    
    def _enhance_finance_response(self, response):
        """
        Enhance the response with finance-specific information.
        
        Parameters:
            response: Response to enhance
            
        Returns:
            Enhanced response
        """
        # Add market disclaimer
        disclaimer = (
            "\n\nDISCLAIMER: This investment analysis is for informational purposes only "
            "and should not be considered financial advice. Always consult with a qualified "
            "financial advisor before making investment decisions. Market conditions can "
            "change rapidly, and past performance is not indicative of future results."
        )
        
        response["response_text"] += disclaimer
        
        # Add finance-specific metadata
        finance_metadata = {
            "analysis_focus": self.config.get("finance_config", {}).get("analysis_focus", "comprehensive"),
            "market_context_included": self.config.get("finance_config", {}).get("include_market_context", True),
            "competitor_analysis_included": self.config.get("finance_config", {}).get("include_competitor_analysis", True),
            "analysis_date": time.strftime("%Y-%m-%d"),
            "analysis_time": time.strftime("%H:%M:%S")
        }
        
        response["finance_metadata"] = finance_metadata
        
        return response
    
    def _process_results(self, query, execution_results, context=None):
        """
        Process execution results into a finance-specific response.
        
        Parameters:
            query: Original query
            execution_results: Results from execution engine
            context: Optional context information
            
        Returns:
            Processed response
        """
        # Extract and categorize financial information
        financial_insights = self._extract_financial_insights(execution_results)
        
        # Create a more structured finance response
        response_text = f"# Investment Analysis: {query}\n\n"
        
        # Add executive summary
        response_text += "## Executive Summary\n\n"
        response_text += f"Research results for query: {query}\n\n"
        
        # Add key findings
        response_text += "## Key Findings\n\n"
        
        for category, insights in financial_insights.items():
            if insights:
                response_text += f"### {category}\n\n"
                for insight in insights:
                    response_text += f"- {insight}\n"
                response_text += "\n"
        
        # Add market context if enabled
        if self.config.get("finance_config", {}).get("include_market_context", True):
            response_text += "## Market Context\n\n"
            response_text += "Current market conditions affecting this investment:\n\n"
            
            # Extract market information from execution results
            market_info = self._extract_market_context(execution_results)
            
            for point in market_info:
                response_text += f"- {point}\n"
            
            response_text += "\n"
        
        # Add risk assessment
        response_text += "## Risk Assessment\n\n"
        
        # Extract risks from execution results
        risks = self._extract_risk_factors(execution_results)
        
        for risk in risks:
            response_text += f"- **{risk['name']}**: {risk['description']}\n"
        
        response_text += "\n"
        
        # Add conclusion
        response_text += "## Conclusion\n\n"
        response_text += "Based on the available information, this investment opportunity "
        
        # Simple sentiment analysis for conclusion
        if len(risks) > 3:
            response_text += "carries significant risks that should be carefully considered. "
            response_text += "Further research and consultation with a financial advisor is recommended."
        else:
            response_text += "appears to have potential in line with typical market expectations. "
            response_text += "As with any investment, careful consideration of your financial goals and risk tolerance is advised."
        
        # Add analysis information (provider, model, date)
        provider = "Unknown"
        model = "Unknown"
        
        if self.llm_provider:
            provider = self.llm_provider.provider if hasattr(self.llm_provider, 'provider') else "Unknown"
            model = self.llm_provider.model if hasattr(self.llm_provider, 'model') else "Unknown"
        
        response_text += "\n\n## Analysis Information\n\n"
        response_text += f"- **Analysis Date**: {context.get('analysis_date', 'Unknown')}\n"
        response_text += f"- **LLM Provider**: {provider}\n"
        response_text += f"- **Model**: {model}\n"
        
        # Add citations
        response_text += "\n## Sources\n\n"
        
        # Extract sources from execution results
        sources = []
        if isinstance(execution_results, dict) and "sources" in execution_results:
            sources = execution_results["sources"]
        
        if sources:
            for i, source in enumerate(sources, 1):
                response_text += f"{i}. {source.get('title', 'Unknown')} - {source.get('url', '')}\n"
        else:
            response_text += "No external sources were used in this analysis.\n"
        
        # Create the response object
        response = {
            "response_text": response_text,
            "sources": sources,
            "execution_results": execution_results
        }
        
        return response
        
    def _create_finance_research_plan(self, query, context=None):
        """
        Create a finance-specific research plan.
        
        Parameters:
            query: User query to research
            context: Optional context information
            
        Returns:
            Research plan with steps
        """
        context = context or {}
        research_depth = context.get("research_depth", "standard")
        
        # Basic plan template
        plan = {
            "id": f"finance_{time.strftime('%Y%m%d%H%M%S')}",
            "query": query,
            "research_depth": research_depth,
            "steps": []
        }
        
        # Query analysis to determine relevant research steps
        query_lower = query.lower()
        
        # Default steps for every finance query
        default_steps = [
            {
                "id": 1,
                "name": "Market Overview",
                "description": "Get an overview of the current market conditions",
                "search_query": f"current market conditions for {query} finance investment {time.strftime('%Y')} {time.strftime('%B')}",
                "tool": "web_search"
            },
            {
                "id": 2,
                "name": "Investment Opportunities",
                "description": "Identify potential investment opportunities related to the query",
                "search_query": f"investment opportunities {query} {time.strftime('%Y')} analysis",
                "tool": "web_search"
            },
            {
                "id": 3,
                "name": "Risk Factors",
                "description": "Identify potential risks and challenges",
                "search_query": f"investment risks challenges {query} {time.strftime('%Y')}",
                "tool": "web_search"
            }
        ]
        
        # Add default steps
        plan["steps"].extend(default_steps)
        
        # Add company-specific steps if query mentions a company
        companies = self._extract_companies(query)
        for i, company in enumerate(companies, 4):
            plan["steps"].append({
                "id": i,
                "name": f"{company} Analysis",
                "description": f"Analyze {company}'s financial performance and outlook",
                "search_query": f"{company} financial performance stock analysis {time.strftime('%Y')}",
                "tool": "web_search"
            })
        
        # Add sector-specific steps if query mentions a sector
        sectors = self._extract_sectors(query)
        start_id = len(plan["steps"]) + 1
        for i, sector in enumerate(sectors, start_id):
            plan["steps"].append({
                "id": i,
                "name": f"{sector} Sector Analysis",
                "description": f"Analyze the {sector} sector trends and performance",
                "search_query": f"{sector} sector investment analysis trends {time.strftime('%Y')}",
                "tool": "web_search"
            })
        
        # Add research-depth specific steps
        if research_depth in ["deep", "expert"]:
            start_id = len(plan["steps"]) + 1
            plan["steps"].extend([
                {
                    "id": start_id,
                    "name": "Expert Opinions",
                    "description": "Gather expert opinions and analyst recommendations",
                    "search_query": f"expert analyst opinions {query} investment {time.strftime('%Y')}",
                    "tool": "web_search"
                },
                {
                    "id": start_id + 1,
                    "name": "Competitor Analysis",
                    "description": "Analyze competitive landscape and market positioning",
                    "search_query": f"competitive landscape market positioning {query} {time.strftime('%Y')}",
                    "tool": "web_search"
                }
            ])
        
        # Log the plan
        logging.info(f"Created finance research plan with {len(plan['steps'])} steps")
        
        return plan
    
    def _extract_companies(self, query):
        """Extract company names from query."""
        # Simple implementation - look for common company names
        companies = []
        
        # Common tech companies
        tech_companies = ["Apple", "Microsoft", "Google", "Amazon", "Facebook", "Meta", 
                          "Netflix", "Tesla", "Nvidia", "AMD", "Intel"]
        
        # Check for company names in query
        for company in tech_companies:
            if company.lower() in query.lower():
                companies.append(company)
        
        # Match patterns like "Company X" or "X Corp"
        import re
        company_patterns = [
            r'([A-Z][a-z]+ (?:Inc|Corp|Corporation|Company|Technologies|Labs))',
            r'([A-Z][a-z]+ [A-Z][a-z]+ (?:Inc|Corp|Corporation|Company|Technologies|Labs))'
        ]
        
        for pattern in company_patterns:
            matches = re.findall(pattern, query)
            companies.extend(matches)
        
        # Limit to 3 companies
        return companies[:3]
    
    def _extract_sectors(self, query):
        """Extract sector names from query."""
        # Common sectors to check for
        sectors = []
        common_sectors = {
            "tech": "Technology",
            "technology": "Technology",
            "healthcare": "Healthcare",
            "health": "Healthcare",
            "finance": "Financial",
            "financial": "Financial",
            "energy": "Energy",
            "renewable": "Renewable Energy",
            "green": "Green Energy",
            "consumer": "Consumer Goods",
            "retail": "Retail",
            "manufacturing": "Manufacturing",
            "telecom": "Telecommunications",
            "real estate": "Real Estate",
            "crypto": "Cryptocurrency",
            "blockchain": "Blockchain"
        }
        
        # Check for sector keywords
        query_lower = query.lower()
        for keyword, sector in common_sectors.items():
            if keyword in query_lower and sector not in sectors:
                sectors.append(sector)
        
        # Limit to 3 sectors
        return sectors[:3]
    
    def _extract_sources(self, execution_results):
        """
        Extract sources from execution results.
        
        Parameters:
            execution_results: Results from execution engine
            
        Returns:
            List of sources
        """
        sources = []
        seen_urls = set()
        
        # Extract sources from steps
        for step in execution_results.get("steps", []):
            if not step.get("success", False):
                continue
                
            result = step.get("result", {})
            
            # Check for search results
            if "results" in result and isinstance(result["results"], list):
                for item in result["results"]:
                    if "url" in item and "title" in item:
                        url = item.get("url")
                        if url and url not in seen_urls:
                            seen_urls.add(url)
                            sources.append({
                                "title": item.get("title", "Unknown"),
                                "url": url
                            })
            # Check for data array if using the updated structure
            elif "data" in result and isinstance(result["data"], list):
                for item in result["data"]:
                    if "url" in item and "title" in item:
                        url = item.get("url")
                        if url and url not in seen_urls:
                            seen_urls.add(url)
                            sources.append({
                                "title": item.get("title", "Unknown"),
                                "url": url
                            })
        
        return sources
    
    def _extract_financial_insights(self, execution_results):
        """
        Extract financial insights from execution results.
        
        Parameters:
            execution_results: Results from execution engine
            
        Returns:
            Categorized financial insights
        """
        # Extract actual insights from search results
        insights = {
            "Financial Performance": [],
            "Industry Position": [],
            "Growth Prospects": []
        }
        
        # Process all step results
        for step in execution_results.get("steps", []):
            if not step.get("success", False):
                continue
                
            result = step.get("result", {})
            
            # Check for search results
            if "results" in result and isinstance(result["results"], list):
                for item in result["results"]:
                    content = item.get("content", "")
                    
                    # Analyze content for financial insights
                    if content:
                        # Look for financial performance information
                        if any(term in content.lower() for term in ["revenue", "profit", "earnings", "financial performance", "balance sheet", "income", "cash flow"]):
                            # Extract relevant sentence
                            sentences = content.split(". ")
                            for sentence in sentences:
                                if any(term in sentence.lower() for term in ["revenue", "profit", "earnings", "financial"]):
                                    if sentence not in insights["Financial Performance"] and len(sentence) > 20:
                                        insights["Financial Performance"].append(sentence)
                        
                        # Look for industry position information
                        if any(term in content.lower() for term in ["market share", "competitor", "industry position", "rank", "standing", "leadership"]):
                            # Extract relevant sentence
                            sentences = content.split(". ")
                            for sentence in sentences:
                                if any(term in sentence.lower() for term in ["market", "competitor", "industry", "position"]):
                                    if sentence not in insights["Industry Position"] and len(sentence) > 20:
                                        insights["Industry Position"].append(sentence)
                        
                        # Look for growth prospects information
                        if any(term in content.lower() for term in ["growth", "forecast", "outlook", "future", "expansion", "opportunity"]):
                            # Extract relevant sentence
                            sentences = content.split(". ")
                            for sentence in sentences:
                                if any(term in sentence.lower() for term in ["growth", "forecast", "outlook", "future"]):
                                    if sentence not in insights["Growth Prospects"] and len(sentence) > 20:
                                        insights["Growth Prospects"].append(sentence)
        
        # If no insights found, use placeholders but mark them clearly
        for category, items in insights.items():
            if not items:
                if category == "Financial Performance":
                    insights[category] = [
                        "No specific financial performance data found in search results",
                        "Consider researching quarterly or annual reports for detailed financial metrics"
                    ]
                elif category == "Industry Position":
                    insights[category] = [
                        "No specific industry position information found in search results",
                        "Consider researching market share data and competitive landscape reports"
                    ]
                elif category == "Growth Prospects":
                    insights[category] = [
                        "No specific growth prospect information found in search results",
                        "Consider researching analyst forecasts and future outlook statements"
                    ]
            
            # Limit to 3 insights per category
            insights[category] = insights[category][:3]
        
        return insights
    
    def _extract_market_context(self, execution_results):
        """
        Extract market context from execution results.
        
        Parameters:
            execution_results: Results from execution engine
            
        Returns:
            List of market context points
        """
        # Extract actual market context from search results
        market_points = []
        
        # Process all step results
        for step in execution_results.get("steps", []):
            if not step.get("success", False):
                continue
                
            result = step.get("result", {})
            
            # Check for search results
            if "results" in result and isinstance(result["results"], list):
                for item in result["results"]:
                    content = item.get("content", "")
                    
                    # Analyze content for market context
                    if content:
                        # Look for market information
                        if any(term in content.lower() for term in ["market condition", "industry trend", "economic", "sector", "outlook"]):
                            # Extract relevant sentences
                            sentences = content.split(". ")
                            for sentence in sentences:
                                if any(term in sentence.lower() for term in ["market", "industry", "economic", "sector"]):
                                    # Clean up sentence
                                    clean_sentence = sentence.strip()
                                    if clean_sentence.endswith('.'):
                                        clean_sentence = clean_sentence[:-1]
                                        
                                    # Check if it's substantial and not redundant
                                    if clean_sentence not in market_points and len(clean_sentence) > 20:
                                        market_points.append(clean_sentence)
        
        # If no market points found, use generic points but mark them clearly
        if not market_points:
            market_points = [
                "No specific market context found in search results - further research recommended",
                f"Current year is {time.strftime('%Y')} - consider checking recent market reports",
                "Consider examining latest economic indicators for additional context",
                "Industry-specific analyst reports may provide more detailed market insights",
                "Broader economic conditions can impact investment performance"
            ]
        
        # Limit to 5 points
        return market_points[:5]
    
    def _extract_risk_factors(self, execution_results):
        """
        Extract risk factors from execution results.
        
        Parameters:
            execution_results: Results from execution engine
            
        Returns:
            List of risk factors
        """
        # Extract actual risks from search results
        risks = []
        
        # Process all step results
        for step in execution_results.get("steps", []):
            if not step.get("success", False):
                continue
                
            result = step.get("result", {})
            
            # Check for search results
            if "results" in result and isinstance(result["results"], list):
                for item in result["results"]:
                    content = item.get("content", "")
                    
                    # Analyze content for risks
                    if content:
                        # Look for risk-related information
                        if any(term in content.lower() for term in ["risk", "challenge", "threat", "uncertainty", "concern", "downside"]):
                            # Extract relevant sentences
                            sentences = content.split(". ")
                            for sentence in sentences:
                                if any(term in sentence.lower() for term in ["risk", "challenge", "threat", "concern"]):
                                    # Try to determine the risk type
                                    risk_type = "General Risk"
                                    
                                    if any(term in sentence.lower() for term in ["market", "economic", "economy", "recession"]):
                                        risk_type = "Market Risk"
                                    elif any(term in sentence.lower() for term in ["competition", "competitor", "market share"]):
                                        risk_type = "Competitive Risk"
                                    elif any(term in sentence.lower() for term in ["regulation", "regulatory", "compliance", "legal"]):
                                        risk_type = "Regulatory Risk"
                                    elif any(term in sentence.lower() for term in ["technology", "innovation", "disruption"]):
                                        risk_type = "Technology Risk"
                                    elif any(term in sentence.lower() for term in ["operation", "supply chain", "production"]):
                                        risk_type = "Operational Risk"
                                    
                                    # Add as risk factor
                                    risk = {
                                        "name": risk_type,
                                        "description": sentence.strip()
                                    }
                                    
                                    # Check if not redundant
                                    if risk not in risks:
                                        risks.append(risk)
        
        # If no risks found, use generic risks but mark them clearly
        if not risks:
            risks = [
                {
                    "name": "Market Volatility",
                    "description": "Investment may be subject to market volatility; specific risks not found in search results"
                },
                {
                    "name": "Information Gap",
                    "description": "Limited risk information found; further detailed risk analysis recommended"
                },
                {
                    "name": "General Investment Risk",
                    "description": "All investments carry inherent risks including potential loss of capital"
                }
            ]
        
        # Limit to 5 risk factors
        return risks[:5]
    
    def _deep_update(self, original, update):
        """
        Recursively update a nested dictionary.
        
        Parameters:
            original: Original dictionary to update
            update: Dictionary with updates
        """
        for key, value in update.items():
            if key in original and isinstance(original[key], dict) and isinstance(value, dict):
                self._deep_update(original[key], value)
            else:
                original[key] = value
