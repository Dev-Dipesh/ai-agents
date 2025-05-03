# Galileo Implementation Guide

This guide provides comprehensive instructions for implementing Galileo evaluation and monitoring in your AI agent applications.

## Table of Contents

1. [Installation](#installation)
2. [Authentication](#authentication)
3. [Basic Usage](#basic-usage)
4. [Evaluation Methods](#evaluation-methods)
5. [Monitoring](#monitoring)
6. [Integration with LangChain](#integration-with-langchain)
7. [Custom Metrics](#custom-metrics)
8. [Best Practices](#best-practices)

## Installation

Install the required packages:

```bash
# Core packages
pip install promptquality

# Optional integrations
pip install langchain-community langchain_openai
```

Add these to your requirements.txt:

```
promptquality==0.69.1
```

## Authentication

There are multiple ways to authenticate with Galileo:

### Environment Variables (Recommended)

```python
import os

# Set environment variables
os.environ["GALILEO_CONSOLE_URL"] = "your_console_url"  # Optional, defaults to public console
os.environ["GALILEO_API_KEY"] = "your_api_key"
```

### Login Method

```python
import promptquality as pq

# Use explicit login (will use env vars if available)
pq.login(console_url="your_console_url")  # URL is optional
```

## Basic Usage

Basic pattern for evaluating LLM outputs:

```python
import promptquality as pq
from promptquality import EvaluateRun

# Set up project and metrics
PROJECT_NAME = "my-evaluation-project"
metrics = [
    pq.Scorers.context_adherence_luna, 
    pq.Scorers.completeness_luna, 
    pq.Scorers.correctness
]

# Create evaluation run
evaluate_run = EvaluateRun(
    run_name="my_model_evaluation", 
    project_name=PROJECT_NAME, 
    scorers=metrics
)

# Add a single evaluation
evaluate_run.add_single_step_workflow(
    prompt="Your prompt here",
    completion="LLM response here",
    reference="Optional reference answer", 
    metadata={"key": "value"}  # Optional
)

# Complete the evaluation
evaluate_run.finish()
```

## Evaluation Methods

### Single-Step Workflows

For simple prompt-completion evaluation:

```python
evaluate_run.add_single_step_workflow(
    prompt="What is machine learning?",
    completion="Machine learning is...",
    reference="Optional reference answer"
)
```

### Multi-Step Workflows

For complex chains or multi-turn conversations:

```python
evaluate_run.add_multi_step_workflow(
    prompts=["Initial question", "Follow-up question"],
    completions=["First answer", "Second answer"],
    reference="Optional reference answer"
)
```

### Batch Evaluation

For evaluating multiple examples at once:

```python
import pandas as pd

# Create dataset
data = pd.DataFrame({
    'prompt': ["Question 1", "Question 2"],
    'completion': ["Answer 1", "Answer 2"],
    'reference': ["Reference 1", "Reference 2"]
})

# Evaluate batch
evaluate_run.batch(
    data=data,
    prompt_column='prompt',
    completion_column='completion',
    reference_column='reference'
)
```

## Monitoring

For ongoing monitoring of production systems:

```python
from galileo_observe import GalileoObserveCallback

# Initialize callback
galileo_callback = GalileoObserveCallback(
    project_name='monitoring-project-name'
)

# Use with LangChain
result = chain.invoke(
    {"query": "User query"},
    config=dict(callbacks=[galileo_callback])
)
```

## Integration with LangChain

```python
from promptquality.integrations.langchain import GalileoPromptCallback

# Create callback with metrics
callback = GalileoPromptCallback(
    project_name=PROJECT_NAME,
    scorers=metrics
)

# Run experiment with callback
results = chain.batch(
    inputs=[{"question": q} for q in questions],
    config={"callbacks": [callback]}
)

# Finish and submit results
callback.finish()
```

## Custom Metrics

Create custom evaluation metrics:

```python
def my_custom_metric(prompt, completion, reference=None, **kwargs):
    # Implement your metric logic
    score = calculate_score(prompt, completion, reference)
    return {
        "score": score,
        "reasoning": "Explanation of the score"
    }

# Register custom metric
custom_metrics = [my_custom_metric]

# Use in evaluation
evaluate_run = EvaluateRun(
    run_name="custom_metrics_run", 
    project_name=PROJECT_NAME, 
    scorers=[*metrics, *custom_metrics]
)
```

## Best Practices

1. **Project Organization**:
   - Use consistent project names
   - Group related evaluations under the same project
   - Use descriptive run names

2. **Metadata**:
   - Include relevant metadata with each evaluation
   - Tag evaluations with model versions, parameters, etc.

3. **Reference Answers**:
   - Provide reference answers whenever possible
   - Use structured reference data for complex tasks

4. **Environment Variables**:
   - Store API keys in environment variables
   - Use a .env file for local development

5. **Error Handling**:
   - Implement try/except blocks around Galileo calls
   - Have fallbacks for evaluation failures

## Example Implementation

Complete example with error handling:

```python
import os
import promptquality as pq
from promptquality import EvaluateRun

# Configure environment
os.environ["GALILEO_API_KEY"] = "your_api_key"

try:
    # Login to Galileo
    pq.login()
    
    # Set up evaluation
    metrics = [
        pq.Scorers.context_adherence_luna, 
        pq.Scorers.completeness_luna
    ]
    
    evaluate_run = EvaluateRun(
        run_name="production_eval", 
        project_name="my-agent-evaluation", 
        scorers=metrics
    )
    
    # Add evaluation data
    evaluate_run.add_single_step_workflow(
        prompt="User query",
        completion="Agent response",
        metadata={"model": "gpt-4", "temperature": 0.7}
    )
    
    # Complete evaluation
    evaluate_run.finish()
    
    print("Evaluation completed successfully")
    
except Exception as e:
    print(f"Galileo evaluation failed: {str(e)}")
    # Continue with fallback behavior
```