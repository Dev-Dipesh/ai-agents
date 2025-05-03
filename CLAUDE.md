# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
This project implements a finance research agent that uses AI to conduct multi-step investment analysis. The agent breaks down complex finance questions, researches key aspects, and synthesizes findings into investment recommendations.

## Environment & Setup
- Create/activate virtual environment: `source venv/bin/activate` or `source pyenv/bin/activate`
- Install dependencies: `pip install -r requirements.txt`
- Setup environment from scratch: `./setup_env.sh`
- Required API keys:
  - OpenAI API key: Set as `OPENAI_API_KEY` in `.env`
  - Tavily API key: Set as `TAVILY_API_KEY` in `.env`

## Development Commands
- Run notebook: `jupyter notebook notebooks/finance_research_agent.ipynb`
- Run specific tests: `python -m unittest test_file.py::TestClass::test_method`
- Lint Python code: `flake8 .`
- Type checking: `mypy .`
- Demo the finance agent: Run the notebook and execute `analyze_investment("your question", evaluate=True)`

## Finance Agent Architecture
The agent uses a multi-component architecture:
1. **Planning Component**: Creates structured research plans with 3-5 steps
2. **Execution Engine**: Implements steps using web search (Tavily API)
3. **Replanning Component**: Evaluates progress and determines next actions
4. **Evaluation System**: Assesses response quality using finance-specific metrics
5. **Visualization Tools**: Displays performance metrics and evaluation results

## Local Evaluation System
The project implements a local evaluation system that:
- Tracks agent runs with unique identifiers
- Stores evaluations in-memory during the session
- Uses GPT-4o to evaluate responses against finance-specific criteria
- Visualizes performance with score breakdowns
- Supports batch evaluation for systematic testing

## Code Style Guidelines
- Follow PEP 8 for Python code style
- Use type hints for function parameters and return types
- Import order: standard library, third-party packages, local modules
- Prefer descriptive variable names over abbreviations
- Use snake_case for variables and functions
- Use docstrings for functions and classes
- Handle exceptions explicitly with appropriate error messages
- Keep functions focused on a single responsibility
- Implement comprehensive error handling and timeouts

## Project Structure
- Store notebooks in the `notebooks/` directory
- Store data files in the `data/` directory
- Main notebook: `notebooks/finance_research_agent.ipynb`
- Structure notebooks with markdown cells explaining each section

## Notebook Organization
The finance research agent notebook follows this structure:
1. Introduction and overview
2. Environment setup and API integration
3. Local evaluation system setup
4. Custom tools and agent configuration
5. Data structures for state management
6. Planning and execution components
7. Core execution functions
8. Workflow graph construction
9. User interface and execution functions
10. Example usage and testing
11. Evaluation dashboards and visualization
12. Batch evaluation system

## Working with the Finance Agent
- Use `analyze_investment("question", evaluate=True)` as the main entry point
- The agent typically takes 2-3 minutes to complete an analysis
- The `evaluate` parameter triggers automatic evaluation of responses
- Use `view_evaluation_history()` to see past evaluations
- Use `analyze_evaluation_metrics()` to visualize performance

## Troubleshooting
- If Tavily search fails, verify your API key in `.env`
- For SSL certificate errors, check the custom Tavily search tool implementation
- If evaluation fails, ensure OpenAI API key is valid
- For timeout errors, consider increasing the `max_time` parameter
- Check interpreter warnings for potential issues with async execution