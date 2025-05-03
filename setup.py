from setuptools import setup, find_packages

setup(
    name="ai-agents",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "aiohappyeyeballs>=2.6.1",
        "aiohttp>=3.11.18",
        "langchain>=0.3.25",
        "langchain-community>=0.3.9",
        "langchain-core>=0.3.58",
        "langchain-openai>=0.2.11",
        "langgraph>=0.2.56",
        "openai>=1.77.0",
        "pandas>=2.2.3",
        "matplotlib>=3.10.1",
        "python-dotenv>=1.1.0",
        "tavily-python>=0.5.0",
        "tiktoken>=0.9.0",
        "pydantic>=2.11.4",
    ],
    author="Dipesh Bhardwaj",
    description="A collection of intelligent AI agents for various practical applications",
    keywords="ai, agents, research, finance",
    python_requires=">=3.8",
)
