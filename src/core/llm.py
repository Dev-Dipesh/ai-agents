"""
LLM provider interface for uniform access to different language models.
"""

import os
import logging
from typing import Dict, List, Any, Optional, Union
from .base import BaseComponent

class BaseLLMProviderInterface(BaseComponent):
    """Interface for LLM provider abstraction."""
    
    def get_available_models(self):
        """
        Get list of available models for the current providers.
        
        Returns:
            Dict mapping provider names to lists of available models
        """
        raise NotImplementedError
    
    def register_provider(self, provider_name, provider_config):
        """
        Register a new LLM provider.
        
        Parameters:
            provider_name: Name of the provider to register
            provider_config: Configuration for the provider
            
        Returns:
            Success boolean
        """
        raise NotImplementedError
    
    def remove_provider(self, provider_name):
        """
        Remove a registered LLM provider.
        
        Parameters:
            provider_name: Name of the provider to remove
            
        Returns:
            Success boolean
        """
        raise NotImplementedError
    
    def set_default_provider(self, provider_name, model_name=None):
        """
        Set the default provider and optionally model.
        
        Parameters:
            provider_name: Name of the provider to set as default
            model_name: Optional specific model to set as default
            
        Returns:
            Success boolean
        """
        raise NotImplementedError
        
    def get_completion(self, prompt, model=None, provider=None, parameters=None):
        """
        Get a completion from an LLM.
        
        Parameters:
            prompt: The prompt to send to the LLM
            model: Optional specific model to use
            provider: Optional specific provider to use
            parameters: Optional model-specific parameters
            
        Returns:
            Completion text and metadata
        """
        raise NotImplementedError
    
    def get_chat_completion(self, messages, model=None, provider=None, parameters=None):
        """
        Get a chat completion from an LLM.
        
        Parameters:
            messages: List of message objects
            model: Optional specific model to use
            provider: Optional specific provider to use
            parameters: Optional model-specific parameters
            
        Returns:
            Completion text and metadata
        """
        raise NotImplementedError
    
    def get_embeddings(self, texts, model=None, provider=None):
        """
        Get embeddings for a list of texts.
        
        Parameters:
            texts: List of texts to get embeddings for
            model: Optional specific model to use
            provider: Optional specific provider to use
            
        Returns:
            List of embeddings
        """
        raise NotImplementedError
        
    def estimate_tokens(self, text, model=None):
        """
        Estimate token count for a text with specific model.
        
        Parameters:
            text: Text to estimate tokens for
            model: Optional specific model to use
            
        Returns:
            Estimated token count
        """
        raise NotImplementedError
    
    def optimize_prompt(self, prompt, max_tokens, model=None):
        """
        Optimize a prompt to fit within token limits.
        
        Parameters:
            prompt: Prompt to optimize
            max_tokens: Maximum number of tokens
            model: Optional specific model to use
            
        Returns:
            Optimized prompt
        """
        raise NotImplementedError
    
    def get_token_usage_stats(self, timeframe=None):
        """
        Get token usage statistics for a timeframe.
        
        Parameters:
            timeframe: Optional timeframe specification
            
        Returns:
            Token usage statistics
        """
        raise NotImplementedError
    
    def handle_provider_error(self, error, provider_name, retry_count=0):
        """
        Handle provider-specific errors with potential fallbacks.
        
        Parameters:
            error: The error that occurred
            provider_name: Name of the provider that raised the error
            retry_count: Number of retries attempted so far
            
        Returns:
            Error handling result
        """
        raise NotImplementedError


class DummyLLMProvider:
    """Dummy LLM provider for testing and fallback."""
    
    def __init__(self, config=None):
        """Initialize the dummy provider."""
        self.default_provider = "dummy"
        self.default_model = "dummy-model"
    
    def get_available_models(self):
        """Get available models."""
        return {"dummy": ["dummy-model"]}
    
    def get_completion(self, prompt, model=None, parameters=None):
        """Get a completion (dummy implementation)."""
        return {
            "text": f"This is a dummy response to: {prompt[:50]}...",
            "model": model or self.default_model,
            "provider": self.default_provider,
            "usage": {
                "prompt_tokens": len(prompt.split()),
                "completion_tokens": 20,
                "total_tokens": len(prompt.split()) + 20
            }
        }
    
    def get_chat_completion(self, messages, model=None, parameters=None):
        """Get a chat completion (dummy implementation)."""
        last_message = messages[-1]["content"] if messages else ""
        return self.get_completion(last_message, model, parameters)


class DefaultLLMProviderInterface(BaseLLMProviderInterface):
    """Default implementation of the LLM provider interface."""
    
    def __init__(self, config=None):
        """Initialize the LLM provider interface."""
        super().__init__(config)
        self.providers = {}
        self.default_provider = None
        self.default_model = None
        self.token_usage = []
        
        # Load configuration
        self.default_provider = self.config.get("default_provider", "openai")
        self.default_model = self.config.get("default_model", "gpt-4o")
        
        # Try to initialize default providers
        self._initialize_default_providers()
    
    def _initialize_default_providers(self):
        """Initialize default providers based on available API keys."""
        # Try OpenAI
        openai_api_key = os.environ.get("OPENAI_API_KEY")
        if openai_api_key:
            try:
                self.register_provider("openai", {"api_key": openai_api_key})
                self.default_provider = "openai"
                self.default_model = "gpt-4o"
                logging.info("Initialized OpenAI provider")
            except Exception as e:
                logging.error(f"Failed to initialize OpenAI provider: {e}")
        
        # Try Anthropic
        anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY")
        if anthropic_api_key:
            try:
                self.register_provider("anthropic", {"api_key": anthropic_api_key})
                if not self.default_provider:
                    self.default_provider = "anthropic"
                    self.default_model = "claude-3-opus-20240229"
                logging.info("Initialized Anthropic provider")
            except Exception as e:
                logging.error(f"Failed to initialize Anthropic provider: {e}")
    
    def get_available_models(self):
        """Get list of available models for the current providers."""
        models = {}
        
        for provider_name, provider in self.providers.items():
            try:
                models[provider_name] = provider.get_available_models()
            except Exception as e:
                logging.error(f"Error getting models for {provider_name}: {e}")
                models[provider_name] = []
        
        return models
    
    def register_provider(self, provider_name, provider_config):
        """Register a new LLM provider."""
        if provider_name == "openai":
            try:
                self.providers[provider_name] = OpenAIProvider(
                    api_key=provider_config.get("api_key"),
                    organization=provider_config.get("organization")
                )
                return True
            except Exception as e:
                logging.error(f"Error registering OpenAI provider: {e}")
                return False
        
        elif provider_name == "anthropic":
            try:
                self.providers[provider_name] = AnthropicProvider(
                    api_key=provider_config.get("api_key")
                )
                return True
            except Exception as e:
                logging.error(f"Error registering Anthropic provider: {e}")
                return False
        
        else:
            logging.error(f"Unknown provider: {provider_name}")
            return False
    
    def remove_provider(self, provider_name):
        """Remove a registered LLM provider."""
        if provider_name in self.providers:
            del self.providers[provider_name]
            
            # If this was the default provider, reset default
            if self.default_provider == provider_name:
                self.default_provider = next(iter(self.providers)) if self.providers else None
                self.default_model = None
            
            return True
        
        return False
    
    def set_default_provider(self, provider_name, model_name=None):
        """Set the default provider and optionally model."""
        if provider_name not in self.providers:
            return False
        
        self.default_provider = provider_name
        self.default_model = model_name
        
        return True
    
    def get_completion(self, prompt, model=None, provider=None, parameters=None):
        """Get a completion from an LLM."""
        provider_name = provider or self.default_provider
        
        if not provider_name or provider_name not in self.providers:
            logging.warning(f"Provider not available: {provider_name}, using dummy provider")
            dummy_provider = DummyLLMProvider()
            return dummy_provider.get_completion(prompt, model, parameters)
        
        provider_instance = self.providers[provider_name]
        model = model or self.default_model
        
        try:
            result = provider_instance.get_completion(
                prompt=prompt,
                model=model,
                parameters=parameters
            )
            
            # Log token usage
            self._log_token_usage(
                provider_name=provider_name,
                model=result["model"],
                prompt_tokens=result["usage"]["prompt_tokens"],
                completion_tokens=result["usage"]["completion_tokens"],
                total_tokens=result["usage"]["total_tokens"]
            )
            
            return result
        except Exception as e:
            return self.handle_provider_error(e, provider_name)
    
    def get_chat_completion(self, messages, model=None, provider=None, parameters=None):
        """Get a chat completion from an LLM."""
        provider_name = provider or self.default_provider
        
        if not provider_name or provider_name not in self.providers:
            logging.warning(f"Provider not available: {provider_name}, using dummy provider")
            dummy_provider = DummyLLMProvider()
            return dummy_provider.get_chat_completion(messages, model, parameters)
        
        provider_instance = self.providers[provider_name]
        model = model or self.default_model
        
        try:
            result = provider_instance.get_chat_completion(
                messages=messages,
                model=model,
                parameters=parameters
            )
            
            # Log token usage
            self._log_token_usage(
                provider_name=provider_name,
                model=result["model"],
                prompt_tokens=result["usage"]["prompt_tokens"],
                completion_tokens=result["usage"]["completion_tokens"],
                total_tokens=result["usage"]["total_tokens"]
            )
            
            return result
        except Exception as e:
            return self.handle_provider_error(e, provider_name)
    
    def get_embeddings(self, texts, model=None, provider=None):
        """Get embeddings for a list of texts."""
        provider_name = provider or self.default_provider
        
        if not provider_name or provider_name not in self.providers:
            logging.warning(f"Provider not available for embeddings: {provider_name}")
            return None
        
        provider_instance = self.providers[provider_name]
        
        try:
            result = provider_instance.get_embeddings(
                texts=texts,
                model=model
            )
            
            # Log token usage
            self._log_token_usage(
                provider_name=provider_name,
                model=result["model"],
                prompt_tokens=result["usage"]["prompt_tokens"],
                completion_tokens=0,
                total_tokens=result["usage"]["total_tokens"]
            )
            
            return result
        except Exception as e:
            return self.handle_provider_error(e, provider_name)
    
    def estimate_tokens(self, text, model=None):
        """Estimate token count for a text with specific model."""
        # Use tiktoken for OpenAI models
        try:
            import tiktoken
            
            model = model or self.default_model
            
            if model.startswith("gpt-"):
                encoding = tiktoken.encoding_for_model(model)
            else:
                # Default to cl100k_base for non-OpenAI models
                encoding = tiktoken.get_encoding("cl100k_base")
            
            tokens = encoding.encode(text)
            return len(tokens)
        except Exception as e:
            logging.error(f"Error estimating tokens: {e}")
            # Fallback to crude approximation
            return len(text.split()) * 1.3
    
    def optimize_prompt(self, prompt, max_tokens, model=None):
        """Optimize a prompt to fit within token limits."""
        current_tokens = self.estimate_tokens(prompt, model)
        
        if current_tokens <= max_tokens:
            return prompt
        
        # Simple truncation strategy - could be much more sophisticated
        truncation_ratio = max_tokens / current_tokens
        words = prompt.split()
        truncated_word_count = int(len(words) * truncation_ratio)
        
        # Keep at least the first 70% of the prompt
        truncated_word_count = max(truncated_word_count, int(len(words) * 0.7))
        
        truncated_prompt = " ".join(words[:truncated_word_count])
        truncated_prompt += "... [Content truncated to fit token limits]"
        
        return truncated_prompt
    
    def get_token_usage_stats(self, timeframe=None):
        """Get token usage statistics for a timeframe."""
        import time
        
        now = time.time()
        
        if timeframe:
            # Filter by timeframe
            timeframe_seconds = {
                "hour": 60 * 60,
                "day": 24 * 60 * 60,
                "week": 7 * 24 * 60 * 60,
                "month": 30 * 24 * 60 * 60
            }.get(timeframe, 24 * 60 * 60)  # Default to a day
            
            filtered_usage = [
                usage for usage in self.token_usage
                if (now - usage["timestamp"]) <= timeframe_seconds
            ]
        else:
            filtered_usage = self.token_usage
        
        # Aggregate by provider and model
        stats = {}
        
        for usage in filtered_usage:
            provider = usage["provider"]
            model = usage["model"]
            
            if provider not in stats:
                stats[provider] = {}
            
            if model not in stats[provider]:
                stats[provider][model] = {
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0,
                    "request_count": 0
                }
            
            stats[provider][model]["prompt_tokens"] += usage["prompt_tokens"]
            stats[provider][model]["completion_tokens"] += usage["completion_tokens"]
            stats[provider][model]["total_tokens"] += usage["total_tokens"]
            stats[provider][model]["request_count"] += 1
        
        return stats
    
    def handle_provider_error(self, error, provider_name, retry_count=0):
        """Handle provider-specific errors with potential fallbacks."""
        logging.error(f"Error from {provider_name}: {error}")
        
        max_retries = self.config.get("max_retries", 3)
        
        if retry_count < max_retries:
            # Retry with exponential backoff
            import time
            time.sleep(2 ** retry_count)
            
            # If we have alternate providers, try those instead
            if provider_name == self.default_provider and len(self.providers) > 1:
                alternate_provider = next(
                    (p for p in self.providers if p != provider_name),
                    None
                )
                
                if alternate_provider:
                    logging.info(f"Falling back to alternate provider: {alternate_provider}")
                    # The calling method would need to re-attempt with the new provider
                    return {
                        "error": str(error),
                        "fallback_provider": alternate_provider,
                        "retry": True,
                        "retry_count": retry_count + 1
                    }
            
            # Otherwise just retry with the same provider
            return {
                "error": str(error),
                "retry": True,
                "retry_count": retry_count + 1
            }
        
        # Out of retries, return error
        return {
            "error": str(error),
            "retry": False
        }
    
    def _log_token_usage(self, provider_name, model, prompt_tokens, completion_tokens, total_tokens):
        """Log token usage for tracking and billing."""
        import time
        
        usage = {
            "timestamp": time.time(),
            "provider": provider_name,
            "model": model,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens
        }
        
        self.token_usage.append(usage)
        
        # Prune old entries if list gets too long
        max_entries = self.config.get("max_token_usage_entries", 1000)
        if len(self.token_usage) > max_entries:
            self.token_usage = self.token_usage[-max_entries:]


class OpenAIProvider:
    """OpenAI-specific provider implementation."""
    
    def __init__(self, api_key=None, organization=None):
        """
        Initialize the OpenAI provider.
        
        Parameters:
            api_key: OpenAI API key
            organization: Optional OpenAI organization ID
        """
        import openai
        
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.organization = organization or os.environ.get("OPENAI_ORGANIZATION")
        
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        self.client = openai.OpenAI(
            api_key=self.api_key,
            organization=self.organization
        )
        
        # Default models
        self.default_model = "gpt-4o"
        self.default_embedding_model = "text-embedding-3-large"
    
    def get_available_models(self):
        """Get available OpenAI models."""
        try:
            models = self.client.models.list()
            return [model.id for model in models.data]
        except Exception as e:
            logging.error(f"Error getting OpenAI models: {e}")
            return []
    
    def get_completion(self, prompt, model=None, parameters=None):
        """Get a completion from OpenAI."""
        model = model or self.default_model
        parameters = parameters or {}
        
        # Set default parameters if not provided
        if "temperature" not in parameters:
            parameters["temperature"] = 0.7
        if "max_tokens" not in parameters:
            parameters["max_tokens"] = 1000
        
        try:
            response = self.client.completions.create(
                model=model,
                prompt=prompt,
                **parameters
            )
            
            return {
                "text": response.choices[0].text,
                "finish_reason": response.choices[0].finish_reason,
                "model": model,
                "provider": "openai",
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
        except Exception as e:
            logging.error(f"Error getting OpenAI completion: {e}")
            raise
    
    def get_chat_completion(self, messages, model=None, parameters=None):
        """Get a chat completion from OpenAI."""
        model = model or self.default_model
        parameters = parameters or {}
        
        # Set default parameters if not provided
        if "temperature" not in parameters:
            parameters["temperature"] = 0.7
        if "max_tokens" not in parameters:
            parameters["max_tokens"] = 1000
        
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                **parameters
            )
            
            return {
                "text": response.choices[0].message.content,
                "finish_reason": response.choices[0].finish_reason,
                "model": model,
                "provider": "openai",
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
        except Exception as e:
            logging.error(f"Error getting OpenAI chat completion: {e}")
            raise
    
    def get_embeddings(self, texts, model=None):
        """Get embeddings from OpenAI."""
        model = model or self.default_embedding_model
        
        try:
            response = self.client.embeddings.create(
                model=model,
                input=texts
            )
            
            embeddings = [data.embedding for data in response.data]
            
            return {
                "embeddings": embeddings,
                "model": model,
                "provider": "openai",
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
        except Exception as e:
            logging.error(f"Error getting OpenAI embeddings: {e}")
            raise


class AnthropicProvider:
    """Anthropic-specific provider implementation."""
    
    def __init__(self, api_key=None):
        """
        Initialize the Anthropic provider.
        
        Parameters:
            api_key: Anthropic API key
        """
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        
        if not self.api_key:
            raise ValueError("Anthropic API key is required")
        
        try:
            # Initialize Anthropic client
            from anthropic import Anthropic
            self.client = Anthropic(api_key=self.api_key)
            
            # Default model
            self.default_model = "claude-3-opus-20240229"
        except ImportError:
            logging.error("Anthropic Python library not installed. Please install with 'pip install anthropic'")
            raise
    
    def get_available_models(self):
        """Get available Anthropic models."""
        # Anthropic doesn't have a models.list() equivalent, so we hardcode the known models
        return [
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
            "claude-instant-1.2"
        ]
    
    def get_completion(self, prompt, model=None, parameters=None):
        """Get a completion from Anthropic."""
        # Claude doesn't have a direct equivalent to OpenAI's completions
        # So we use messages with just a user message
        return self.get_chat_completion(
            messages=[{"role": "user", "content": prompt}],
            model=model,
            parameters=parameters
        )
    
    def get_chat_completion(self, messages, model=None, parameters=None):
        """Get a chat completion from Anthropic."""
        model = model or self.default_model
        parameters = parameters or {}
        
        # Set default parameters if not provided
        if "temperature" not in parameters:
            parameters["temperature"] = 0.7
        if "max_tokens" not in parameters:
            parameters["max_tokens"] = 1000
        
        # Convert to Anthropic format if needed
        anthropic_messages = []
        for msg in messages:
            role = msg["role"]
            if role == "user":
                anthropic_role = "user"
            elif role == "assistant":
                anthropic_role = "assistant"
            elif role == "system":
                anthropic_role = "system"
            else:
                # Skip unknown roles
                continue
            
            anthropic_messages.append({
                "role": anthropic_role,
                "content": msg["content"]
            })
        
        try:
            response = self.client.messages.create(
                model=model,
                messages=anthropic_messages,
                max_tokens=parameters.get("max_tokens", 1000),
                temperature=parameters.get("temperature", 0.7)
            )
            
            # Anthropic doesn't provide token usage in the same way as OpenAI
            # We'd need to estimate this
            estimated_prompt_tokens = sum(len(msg["content"].split()) * 1.3 for msg in messages)
            estimated_completion_tokens = len(response.content[0].text.split()) * 1.3
            
            return {
                "text": response.content[0].text,
                "model": model,
                "provider": "anthropic",
                "usage": {
                    "prompt_tokens": int(estimated_prompt_tokens),
                    "completion_tokens": int(estimated_completion_tokens),
                    "total_tokens": int(estimated_prompt_tokens + estimated_completion_tokens)
                }
            }
        except Exception as e:
            logging.error(f"Error getting Anthropic chat completion: {e}")
            raise
