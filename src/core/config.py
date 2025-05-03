"""
Configuration manager for agent settings and operational parameters.
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from .base import BaseComponent

class BaseConfigurationManager(BaseComponent):
    """Interface for configuration management."""
    
    def get_config(self, key, default=None):
        """
        Get a configuration value by key.
        
        Parameters:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        raise NotImplementedError
    
    def set_config(self, key, value):
        """
        Set a configuration value.
        
        Parameters:
            key: Configuration key
            value: Configuration value
            
        Returns:
            Success boolean
        """
        raise NotImplementedError
    
    def load_config(self, config_file):
        """
        Load configuration from a file.
        
        Parameters:
            config_file: Path to configuration file
            
        Returns:
            Success boolean
        """
        raise NotImplementedError
    
    def save_config(self, config_file):
        """
        Save current configuration to a file.
        
        Parameters:
            config_file: Path to configuration file
            
        Returns:
            Success boolean
        """
        raise NotImplementedError
    
    def get_research_depth_config(self):
        """
        Get the current research depth configuration.
        
        Returns:
            Dict with depth settings for each domain
        """
        raise NotImplementedError
    
    def set_research_depth(self, depth, domain=None):
        """
        Set research depth globally or for a specific domain.
        
        Parameters:
            depth: Research depth level ("light", "standard", "deep", "expert")
            domain: Optional domain to apply to (None for global)
            
        Returns:
            Success boolean
        """
        raise NotImplementedError
    
    def get_depth_parameters(self, depth, domain=None):
        """
        Get parameters associated with a research depth level.
        
        Parameters:
            depth: Research depth level
            domain: Optional domain-specific parameters
            
        Returns:
            Dict of parameters (sources_count, search_depth, etc.)
        """
        raise NotImplementedError


class DefaultConfigurationManager(BaseConfigurationManager):
    """Default implementation of the configuration manager."""
    
    def __init__(self, config=None):
        """Initialize the configuration manager."""
        super().__init__(config)
        self.settings = {}
        
        # Load default configuration
        self._load_defaults()
        
        # Override with provided config
        if config:
            self.settings.update(config)
    
    def _load_defaults(self):
        """Load default configuration settings."""
        # Core settings
        self.settings["core"] = {
            "logging_level": "INFO",
            "max_execution_time": 300,  # 5 minutes
            "error_handling": "abort",  # "abort", "continue", "retry"
            "debug_mode": False
        }
        
        # Research depth settings
        self.settings["research_depth"] = {
            "default": "standard",
            "domains": {},
            "parameters": {
                "light": {
                    "sources_count": 3,
                    "search_depth": "basic",
                    "max_steps": 5
                },
                "standard": {
                    "sources_count": 7,
                    "search_depth": "basic",
                    "max_steps": 10
                },
                "deep": {
                    "sources_count": 15,
                    "search_depth": "advanced",
                    "max_steps": 20
                },
                "expert": {
                    "sources_count": 25,
                    "search_depth": "advanced",
                    "max_steps": 30
                }
            }
        }
        
        # LLM provider settings
        self.settings["llm"] = {
            "default_provider": "openai",
            "default_model": "gpt-4o",
            "max_retries": 3,
            "timeout": 60
        }
        
        # Tool settings
        self.settings["tools"] = {
            "register_defaults": True,
            "web_search": {
                "provider": "tavily",
                "max_results": 5
            }
        }
        
        # Domain-specific settings
        self.settings["domains"] = {
            "finance": {
                "research_depth": "deep",
                "evaluation_metrics": [
                    "relevance", 
                    "helpfulness", 
                    "correctness", 
                    "completeness",
                    "follows_instructions",
                    "reasoning_quality",
                    "investment_analysis",
                    "risk_assessment",
                    "market_awareness",
                    "financial_literacy"
                ]
            }
        }
    
    def get_config(self, key, default=None):
        """Get a configuration value by key."""
        # Split dotted path (e.g., "core.logging_level")
        parts = key.split(".")
        
        # Navigate through the settings
        current = self.settings
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return default
        
        return current
    
    def set_config(self, key, value):
        """Set a configuration value."""
        # Split dotted path (e.g., "core.logging_level")
        parts = key.split(".")
        
        if not parts:
            return False
        
        # Navigate to the correct location
        current = self.settings
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            elif not isinstance(current[part], dict):
                # Can't set a sub-key for a non-dict value
                return False
            
            current = current[part]
        
        # Set the value
        current[parts[-1]] = value
        return True
    
    def load_config(self, config_file):
        """Load configuration from a file."""
        if not os.path.exists(config_file):
            logging.error(f"Config file not found: {config_file}")
            return False
        
        try:
            with open(config_file, "r") as f:
                config = json.load(f)
            
            # Update settings with loaded config
            self._deep_update(self.settings, config)
            return True
        
        except Exception as e:
            logging.error(f"Error loading config file: {e}")
            return False
    
    def save_config(self, config_file):
        """Save current configuration to a file."""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(config_file), exist_ok=True)
            
            with open(config_file, "w") as f:
                json.dump(self.settings, f, indent=2)
            
            return True
        
        except Exception as e:
            logging.error(f"Error saving config file: {e}")
            return False
    
    def get_research_depth_config(self):
        """Get the current research depth configuration."""
        return {
            "default": self.settings["research_depth"]["default"],
            "domains": self.settings["research_depth"]["domains"].copy()
        }
    
    def set_research_depth(self, depth, domain=None):
        """Set research depth globally or for a specific domain."""
        if depth not in ["light", "standard", "deep", "expert"]:
            return False
        
        if domain:
            # Set domain-specific depth
            if "domains" not in self.settings["research_depth"]:
                self.settings["research_depth"]["domains"] = {}
            
            self.settings["research_depth"]["domains"][domain] = depth
        else:
            # Set global default
            self.settings["research_depth"]["default"] = depth
        
        return True
    
    def get_depth_parameters(self, depth, domain=None):
        """Get parameters associated with a research depth level."""
        # Get parameters for the depth
        params = self.settings["research_depth"]["parameters"].get(depth, {}).copy()
        
        # Check for domain-specific overrides
        if domain and domain in self.settings.get("domains", {}):
            domain_settings = self.settings["domains"][domain]
            
            # If domain has depth-specific parameters, update with those
            if "depth_parameters" in domain_settings and depth in domain_settings["depth_parameters"]:
                params.update(domain_settings["depth_parameters"][depth])
        
        return params
    
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
