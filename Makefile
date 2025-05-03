.PHONY: setup install test lint format clean docs

# Default target
all: install test lint

# Setup development environment
setup:
	python3 -m venv venv
	@echo "Virtual environment created. Activate with 'source venv/bin/activate'"

# Install the package in development mode
install:
	pip install -e .
	pip install -r requirements-dev.txt

# Run tests
test:
	pytest -xvs tests/

# Run tests with coverage
coverage:
	pytest --cov=src tests/ --cov-report=html
	@echo "Coverage report generated in htmlcov/"

# Run linting
lint:
	flake8 src/ tests/
	black --check src/ tests/
	isort --check-only src/ tests/

# Format code
format:
	black src/ tests/
	isort src/ tests/

# Clean up generated files
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	find . -type d -name "__pycache__" -exec rm -rf {} +

# Generate documentation
docs:
	cd docs && sphinx-build -b html . _build/html
	@echo "Documentation built in docs/_build/html/"

# Run the finance research example
finance-example:
	python examples/finance_research.py
