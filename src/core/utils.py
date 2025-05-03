"""
Utility functions for the agent framework.
"""

import logging
import os

def get_llm_config_interactive():
    """
    Interactive selection of LLM provider and model.
    
    Returns:
        Dictionary with provider and model configuration
    """
    # Provider selection
    print("\nSelect LLM provider:")
    print("1. OpenAI (default)")
    print("2. Anthropic (not fully implemented)")
    print("3. MistralAI (not fully implemented)")
    
    provider_input = input("> ")
    
    provider_map = {
        "1": "openai",
        "2": "anthropic",
        "3": "mistral"
    }
    
    provider = provider_map.get(provider_input, "openai")
    
    # Model selection based on provider
    model = None
    
    if provider == "openai":
        print("\nSelect OpenAI model:")
        print("1. gpt-4o (recommended)")
        print("2. gpt-4o-mini (faster)")
        print("3. gpt-4-turbo")
        print("4. gpt-3.5-turbo")
        
        model_input = input("> ")
        
        model_map = {
            "1": "gpt-4o",
            "2": "gpt-4o-mini",
            "3": "gpt-4-turbo",
            "4": "gpt-3.5-turbo"
        }
        
        model = model_map.get(model_input, "gpt-4o")
    
    elif provider == "anthropic":
        print("\nSelect Anthropic model:")
        print("1. claude-3-opus (recommended)")
        print("2. claude-3-sonnet")
        print("3. claude-3-haiku")
        
        model_input = input("> ")
        
        model_map = {
            "1": "claude-3-opus-20240229",
            "2": "claude-3-sonnet-20240229",
            "3": "claude-3-haiku-20240307"
        }
        
        model = model_map.get(model_input, "claude-3-opus-20240229")
    
    elif provider == "mistral":
        print("\nSelect MistralAI model:")
        print("1. mistral-large (recommended)")
        print("2. mistral-medium")
        print("3. mistral-small")
        
        model_input = input("> ")
        
        model_map = {
            "1": "mistral-large-latest",
            "2": "mistral-medium-latest",
            "3": "mistral-small-latest"
        }
        
        model = model_map.get(model_input, "mistral-large-latest")
    
    # Check for API key
    api_key_var = f"{provider.upper()}_API_KEY"
    api_key = os.environ.get(api_key_var)
    
    if not api_key:
        print(f"\nWarning: {api_key_var} not found in environment.")
        print(f"Provider '{provider}' might not work without valid API key.")
    
    # Return configuration
    return {
        "default_provider": provider,
        "default_model": model
    }
