# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Environment & Setup
- Create/activate virtual environment: `source venv/bin/activate`
- Install dependencies: `pip install -r requirements.txt`
- Setup environment from scratch: `./setup_env.sh`

## Development Commands
- Run notebook: `jupyter notebook notebooks/finance_research_agent.ipynb`
- Run specific tests: `python -m unittest test_file.py::TestClass::test_method`
- Lint Python code: `flake8 .`
- Type checking: `mypy .`

## Code Style Guidelines
- Follow PEP 8 for Python code style
- Use type hints for function parameters and return types
- Import order: standard library, third-party packages, local modules
- Prefer descriptive variable names over abbreviations
- Use snake_case for variables and functions
- Use docstrings for functions and classes
- Handle exceptions explicitly with appropriate error messages
- Keep functions focused on a single responsibility

## Project Structure
- Store notebooks in the `notebooks/` directory
- Store data files in the `data/` directory
- Keep the repository organized according to the structure in README.md