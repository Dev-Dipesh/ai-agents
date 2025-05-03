#!/bin/bash

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
elif [ -d "pyenv" ]; then
    echo "Activating virtual environment..."
    source pyenv/bin/activate
fi

# Check for required packages
echo "Checking required packages..."
PACKAGES_TO_INSTALL=()

# Check for openai
python3 -c "import openai" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "- OpenAI package not found, adding to install list"
    PACKAGES_TO_INSTALL+=("openai")
else
    echo "- OpenAI package found"
fi

# Check for python-dotenv
python3 -c "import dotenv" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "- Python-dotenv package not found, adding to install list"
    PACKAGES_TO_INSTALL+=("python-dotenv")
else
    echo "- Python-dotenv package found"
fi

# Check for tavily-python
python3 -c "import tavily" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "- Tavily package not found, adding to install list"
    PACKAGES_TO_INSTALL+=("tavily-python")
else
    echo "- Tavily package found"
fi

# Check for httpx (needed for Tavily fallback)
python3 -c "import httpx" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "- httpx package not found, adding to install list (required for Tavily fallback)"
    PACKAGES_TO_INSTALL+=("httpx")
else
    echo "- httpx package found"
fi

# Check for langchain_core
python3 -c "import langchain_core" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "- langchain_core package not found, adding to install list"
    PACKAGES_TO_INSTALL+=("langchain_core")
else
    echo "- langchain_core package found"
fi

# Check for langchain-community
python3 -c "import langchain_community" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "- langchain-community package not found, adding to install list"
    PACKAGES_TO_INSTALL+=("langchain-community")
else
    echo "- langchain-community package found"
fi

# Install missing packages if needed
if [ ${#PACKAGES_TO_INSTALL[@]} -gt 0 ]; then
    echo "Installing missing packages: ${PACKAGES_TO_INSTALL[*]}"
    pip3 install "${PACKAGES_TO_INSTALL[@]}"
else
    echo "All required packages are installed."
fi

# Check for API keys
if [ ! -f .env ]; then
    echo "Creating .env file for API keys..."
    if [ -f .env.example ]; then
        cp .env.example .env
    else
        echo "OPENAI_API_KEY=" > .env
        echo "TAVILY_API_KEY=" >> .env
    fi
    echo "Please edit .env file to add your API keys."
    exit 1
fi

# Check if API keys are set in .env
if ! grep -q "OPENAI_API_KEY=sk-" .env; then
    echo "⚠️ Warning: OPENAI_API_KEY appears to be missing or invalid in .env file."
    echo "The application requires a valid OpenAI API key to function correctly."
    echo "Please set your OpenAI API key in the .env file."
fi

if ! grep -q "TAVILY_API_KEY=" .env; then
    echo "⚠️ Warning: TAVILY_API_KEY is missing in .env file."
    echo "Web search functionality will not work without a Tavily API key."
    echo "You can get a free Tavily API key at https://tavily.com/"
    echo "Please set your Tavily API key in the .env file for web search functionality."
fi

# Set higher log level for more detailed output
export PYTHONUNBUFFERED=1
export LOG_LEVEL=INFO

# Use the new logging configuration
export LOG_TO_FILE=true
export LOG_TO_CONSOLE=false

# Create logs directory if it doesn't exist
mkdir -p logs

# Load environment variables from .env
if [ -f .env ]; then
    echo "Loading environment variables from .env..."
    export $(grep -v '^#' .env | xargs)
fi

# Run the finance agent
echo "Starting Finance Research Agent..."
# Run with debug flag enabled by default for better feedback
DEBUG=true python3 examples/finance_research.py

# Print path to log file
echo "Run completed. See logs/agent_*.log for detailed output."
