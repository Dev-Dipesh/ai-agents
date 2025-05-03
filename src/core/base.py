"""
Base component interfaces for the agent framework.
"""

class BaseComponent:
    """Base interface for all agent components."""
    
    def __init__(self, config=None):
        """Initialize component with configuration."""
        self.config = config or {}
        self.initialize()
    
    def initialize(self):
        """Perform any initialization required."""
        pass
    
    def validate_config(self):
        """Validate component configuration."""
        pass
    
    def get_metadata(self):
        """Return component metadata."""
        return {
            "name": self.__class__.__name__,
            "description": self.__doc__,
            "version": getattr(self, "VERSION", "0.1.0"),
        }
