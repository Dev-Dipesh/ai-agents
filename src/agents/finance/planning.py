"""
Finance-specific planning engine.
"""

import logging
from typing import Dict, List, Any, Optional

from src.core.planning import BasePlanningEngine, DefaultPlanningEngine

class FinanceResearchPlanningEngine(DefaultPlanningEngine):
    """
    Finance-specific planning engine that creates structured research plans
    tailored for investment analysis and financial research.
    """
    
    def __init__(self, config=None):
        """Initialize the finance planning engine."""
        super().__init__(config)
        
        # Finance-specific research templates
        self.finance_templates = {
            "company_analysis": self._company_analysis_template,
            "market_analysis": self._market_analysis_template,
            "investment_strategy": self._investment_strategy_template,
            "risk_assessment": self._risk_assessment_template,
            "financial_instrument": self._financial_instrument_template
        }
    
    def create_plan(self, query, context=None, research_depth="standard"):
        """
        Create a finance-specific research plan.
        
        Parameters:
            query: The research query to plan for
            context: Optional context information
            research_depth: Depth level ("light", "standard", "deep", "expert")
            
        Returns:
            A structured finance research plan
        """
        # Determine the plan type based on query analysis
        plan_type = self._analyze_query_type(query)
        
        # Get the appropriate template function
        template_func = self.finance_templates.get(
            plan_type, self._default_finance_template)
        
        # Create plan using the template
        plan = template_func(query, context, research_depth)
        
        # Add common finance research elements
        self._add_common_finance_elements(plan, research_depth)
        
        return plan
    
    def _analyze_query_type(self, query):
        """
        Analyze the query to determine the type of financial research needed.
        
        Parameters:
            query: The research query
            
        Returns:
            Type of financial research plan
        """
        # This would ideally use NLP/LLM to categorize the query
        # For now, use a simple keyword-based approach
        
        query_lower = query.lower()
        
        if any(term in query_lower for term in ["company", "stock", "shares", "equity"]):
            return "company_analysis"
        
        elif any(term in query_lower for term in ["market", "sector", "industry"]):
            return "market_analysis"
        
        elif any(term in query_lower for term in ["strategy", "portfolio", "allocation"]):
            return "investment_strategy"
        
        elif any(term in query_lower for term in ["risk", "volatility", "downside"]):
            return "risk_assessment"
        
        elif any(term in query_lower for term in ["bond", "option", "futures", "derivative"]):
            return "financial_instrument"
        
        else:
            return "default"
    
    def _company_analysis_template(self, query, context, research_depth):
        """Create a company analysis research plan."""
        steps = [
            {
                "id": 1,
                "name": "Company Overview",
                "description": "Research basic company information, business model, and history",
                "tool": "web_search"
            },
            {
                "id": 2,
                "name": "Financial Performance",
                "description": "Analyze revenue, earnings, margins, and growth trends",
                "tool": "web_search"
            },
            {
                "id": 3,
                "name": "Competitive Position",
                "description": "Evaluate market share, competitors, and competitive advantages",
                "tool": "web_search"
            }
        ]
        
        # Add depth-specific steps
        if research_depth in ["deep", "expert"]:
            steps.extend([
                {
                    "id": 4,
                    "name": "Management Analysis",
                    "description": "Evaluate leadership team, strategy, and execution",
                    "tool": "web_search"
                },
                {
                    "id": 5,
                    "name": "Financial Health",
                    "description": "Analyze balance sheet, cash flow, and debt levels",
                    "tool": "web_search"
                },
                {
                    "id": 6,
                    "name": "Valuation Analysis",
                    "description": "Calculate and compare valuation metrics",
                    "tool": "text_analysis"
                }
            ])
        
        if research_depth == "expert":
            steps.extend([
                {
                    "id": 7,
                    "name": "Risk Factor Analysis",
                    "description": "Identify company-specific and market risks",
                    "tool": "web_search"
                },
                {
                    "id": 8,
                    "name": "Future Outlook",
                    "description": "Analyze growth prospects, upcoming catalysts, and long-term trends",
                    "tool": "web_search"
                }
            ])
        
        return {
            "query": query,
            "plan_type": "company_analysis",
            "steps": steps,
            "depth": research_depth
        }
    
    def _market_analysis_template(self, query, context, research_depth):
        """Create a market analysis research plan."""
        steps = [
            {
                "id": 1,
                "name": "Market Overview",
                "description": "Research market size, growth rate, and overall trends",
                "tool": "web_search"
            },
            {
                "id": 2,
                "name": "Key Players",
                "description": "Identify major companies and market share distribution",
                "tool": "web_search"
            },
            {
                "id": 3,
                "name": "Market Dynamics",
                "description": "Analyze supply/demand factors and pricing trends",
                "tool": "web_search"
            }
        ]
        
        # Add depth-specific steps
        if research_depth in ["deep", "expert"]:
            steps.extend([
                {
                    "id": 4,
                    "name": "Regulatory Environment",
                    "description": "Evaluate current and upcoming regulations affecting the market",
                    "tool": "web_search"
                },
                {
                    "id": 5,
                    "name": "Technology Trends",
                    "description": "Research technological developments impacting the market",
                    "tool": "web_search"
                },
                {
                    "id": 6,
                    "name": "International Factors",
                    "description": "Analyze global influences and regional variations",
                    "tool": "web_search"
                }
            ])
        
        if research_depth == "expert":
            steps.extend([
                {
                    "id": 7,
                    "name": "Historical Performance",
                    "description": "Analyze market performance through different economic cycles",
                    "tool": "web_search"
                },
                {
                    "id": 8,
                    "name": "Future Projections",
                    "description": "Research analyst forecasts and long-term outlook",
                    "tool": "web_search"
                }
            ])
        
        return {
            "query": query,
            "plan_type": "market_analysis",
            "steps": steps,
            "depth": research_depth
        }
    
    def _investment_strategy_template(self, query, context, research_depth):
        """Create an investment strategy research plan."""
        steps = [
            {
                "id": 1,
                "name": "Strategy Overview",
                "description": "Research the fundamental principles of the strategy",
                "tool": "web_search"
            },
            {
                "id": 2,
                "name": "Historical Performance",
                "description": "Analyze how the strategy has performed over time",
                "tool": "web_search"
            },
            {
                "id": 3,
                "name": "Implementation Approaches",
                "description": "Research different ways to implement the strategy",
                "tool": "web_search"
            }
        ]
        
        # Add depth-specific steps
        if research_depth in ["deep", "expert"]:
            steps.extend([
                {
                    "id": 4,
                    "name": "Risk Analysis",
                    "description": "Evaluate risks associated with the strategy",
                    "tool": "web_search"
                },
                {
                    "id": 5,
                    "name": "Market Conditions",
                    "description": "Analyze how current market conditions may affect the strategy",
                    "tool": "web_search"
                },
                {
                    "id": 6,
                    "name": "Expert Opinions",
                    "description": "Research what financial experts say about the strategy",
                    "tool": "web_search"
                }
            ])
        
        if research_depth == "expert":
            steps.extend([
                {
                    "id": 7,
                    "name": "Tax Implications",
                    "description": "Research tax considerations for the strategy",
                    "tool": "web_search"
                },
                {
                    "id": 8,
                    "name": "Alternative Strategies",
                    "description": "Compare with alternative investment approaches",
                    "tool": "web_search"
                }
            ])
        
        return {
            "query": query,
            "plan_type": "investment_strategy",
            "steps": steps,
            "depth": research_depth
        }
    
    def _risk_assessment_template(self, query, context, research_depth):
        """Create a risk assessment research plan."""
        steps = [
            {
                "id": 1,
                "name": "Risk Identification",
                "description": "Identify main risk factors and categories",
                "tool": "web_search"
            },
            {
                "id": 2,
                "name": "Historical Volatility",
                "description": "Research historical price movements and volatility",
                "tool": "web_search"
            },
            {
                "id": 3,
                "name": "Risk Metrics",
                "description": "Analyze standard risk measurements and what they indicate",
                "tool": "web_search"
            }
        ]
        
        # Add depth-specific steps
        if research_depth in ["deep", "expert"]:
            steps.extend([
                {
                    "id": 4,
                    "name": "Systematic vs. Unsystematic Risk",
                    "description": "Differentiate between market-wide and specific risks",
                    "tool": "web_search"
                },
                {
                    "id": 5,
                    "name": "Risk Mitigation Strategies",
                    "description": "Research approaches to manage and reduce risks",
                    "tool": "web_search"
                },
                {
                    "id": 6,
                    "name": "Risk-Adjusted Returns",
                    "description": "Analyze performance in the context of risk taken",
                    "tool": "web_search"
                }
            ])
        
        if research_depth == "expert":
            steps.extend([
                {
                    "id": 7,
                    "name": "Stress Testing",
                    "description": "Research how investments might perform in extreme scenarios",
                    "tool": "web_search"
                },
                {
                    "id": 8,
                    "name": "Behavioral Aspects",
                    "description": "Analyze psychological factors affecting risk perception",
                    "tool": "web_search"
                }
            ])
        
        return {
            "query": query,
            "plan_type": "risk_assessment",
            "steps": steps,
            "depth": research_depth
        }
    
    def _financial_instrument_template(self, query, context, research_depth):
        """Create a financial instrument research plan."""
        steps = [
            {
                "id": 1,
                "name": "Instrument Overview",
                "description": "Research basic structure and characteristics",
                "tool": "web_search"
            },
            {
                "id": 2,
                "name": "Pricing Mechanics",
                "description": "Analyze how the instrument is priced and valued",
                "tool": "web_search"
            },
            {
                "id": 3,
                "name": "Market Conditions",
                "description": "Research current market conditions affecting the instrument",
                "tool": "web_search"
            }
        ]
        
        # Add depth-specific steps
        if research_depth in ["deep", "expert"]:
            steps.extend([
                {
                    "id": 4,
                    "name": "Historical Performance",
                    "description": "Analyze past performance patterns and returns",
                    "tool": "web_search"
                },
                {
                    "id": 5,
                    "name": "Risk Profile",
                    "description": "Evaluate specific risks associated with the instrument",
                    "tool": "web_search"
                },
                {
                    "id": 6,
                    "name": "Alternative Instruments",
                    "description": "Compare with similar financial instruments",
                    "tool": "web_search"
                }
            ])
        
        if research_depth == "expert":
            steps.extend([
                {
                    "id": 7,
                    "name": "Tax Treatment",
                    "description": "Research tax implications and considerations",
                    "tool": "web_search"
                },
                {
                    "id": 8,
                    "name": "Advanced Strategies",
                    "description": "Analyze sophisticated uses and strategies",
                    "tool": "web_search"
                }
            ])
        
        return {
            "query": query,
            "plan_type": "financial_instrument",
            "steps": steps,
            "depth": research_depth
        }
    
    def _default_finance_template(self, query, context, research_depth):
        """Create a default finance research plan."""
        steps = [
            {
                "id": 1,
                "name": "Background Research",
                "description": "Gather general information and context",
                "tool": "web_search"
            },
            {
                "id": 2,
                "name": "Financial Analysis",
                "description": "Research financial aspects and implications",
                "tool": "web_search"
            },
            {
                "id": 3,
                "name": "Market Context",
                "description": "Analyze relevant market conditions and trends",
                "tool": "web_search"
            }
        ]
        
        # Add depth-specific steps
        if research_depth in ["deep", "expert"]:
            steps.extend([
                {
                    "id": 4,
                    "name": "Risk Evaluation",
                    "description": "Identify and assess potential risks",
                    "tool": "web_search"
                },
                {
                    "id": 5,
                    "name": "Expert Perspectives",
                    "description": "Research what financial experts are saying",
                    "tool": "web_search"
                }
            ])
        
        if research_depth == "expert":
            steps.extend([
                {
                    "id": 6,
                    "name": "Long-term Outlook",
                    "description": "Analyze long-term prospects and implications",
                    "tool": "web_search"
                },
                {
                    "id": 7,
                    "name": "Alternative Viewpoints",
                    "description": "Research contrarian opinions and alternative analyses",
                    "tool": "web_search"
                }
            ])
        
        return {
            "query": query,
            "plan_type": "default_finance",
            "steps": steps,
            "depth": research_depth
        }
    
    def _add_common_finance_elements(self, plan, research_depth):
        """
        Add common finance research elements to the plan.
        
        Parameters:
            plan: The research plan to enhance
            research_depth: Research depth level
            
        Returns:
            Enhanced plan
        """
        # Add synthesis step to all plans
        plan["steps"].append({
            "id": len(plan["steps"]) + 1,
            "name": "Analysis Synthesis",
            "description": "Combine all research findings into a coherent analysis",
            "tool": "text_analysis"
        })
        
        # Add conclusion step to all plans
        plan["steps"].append({
            "id": len(plan["steps"]) + 1,
            "name": "Investment Conclusion",
            "description": "Draw conclusions and provide recommendation based on all findings",
            "tool": "text_analysis"
        })
        
        # Add additional finance metadata
        plan["finance_metadata"] = {
            "sectors": [],  # Would be populated based on query analysis
            "investment_type": "",  # Would be populated based on query analysis
            "time_horizon": "",  # Would be populated based on query analysis
            "risk_profile": ""  # Would be populated based on query analysis
        }
        
        return plan
