"""
Logging configuration for the AI Agents Framework.
Centralizes logging setup and provides various logging options.
"""

import os
import sys
import logging
import logging.handlers
from datetime import datetime

# Default log directory
DEFAULT_LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')

def setup_logging(
    level=None, 
    log_to_console=True, 
    log_to_file=True, 
    log_dir=None, 
    log_file=None,
    log_format=None
):
    """
    Set up logging configuration with multiple handlers.
    
    Parameters:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_console: Whether to log to console
        log_to_file: Whether to log to file
        log_dir: Directory for log files
        log_file: Specific log file name
        log_format: Custom log format string
        
    Returns:
        Logger instance
    """
    # Determine the log level
    if level is None:
        level = os.environ.get('LOG_LEVEL', 'INFO').upper()
    
    if isinstance(level, str):
        numeric_level = getattr(logging, level.upper(), logging.INFO)
    else:
        numeric_level = level
    
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(numeric_level)
    
    # Clear existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Define log format
    if log_format is None:
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    formatter = logging.Formatter(log_format)
    
    # Console handler
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(numeric_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # File handler
    if log_to_file:
        # Create log directory if it doesn't exist
        if log_dir is None:
            log_dir = DEFAULT_LOG_DIR
        
        os.makedirs(log_dir, exist_ok=True)
        
        # Generate log file name if not provided
        if log_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = f"agent_{timestamp}.log"
        
        log_path = os.path.join(log_dir, log_file)
        
        # Create rotating file handler
        file_handler = logging.handlers.RotatingFileHandler(
            log_path, 
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5
        )
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # Log initial message
    logger.info(f"Logging configured at level {level}")
    
    return logger

def get_agent_logger(agent_name, **kwargs):
    """
    Get a logger for a specific agent with appropriate configuration.
    
    Parameters:
        agent_name: Name of the agent for the logger
        **kwargs: Additional configuration options
        
    Returns:
        Logger instance for the agent
    """
    # Generate log file name for this agent
    log_file = f"{agent_name.lower().replace(' ', '_')}.log"
    
    # Setup logging with agent-specific configuration
    setup_logging(log_file=log_file, **kwargs)
    
    # Return named logger
    return logging.getLogger(agent_name)

def disable_console_logging():
    """Disable console logging while keeping file logging active."""
    logger = logging.getLogger()
    
    for handler in logger.handlers[:]:
        if isinstance(handler, logging.StreamHandler) and handler.stream == sys.stdout:
            logger.removeHandler(handler)
            break
    
    return logger

def enable_debug_logging():
    """Enable debug level logging."""
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    
    for handler in logger.handlers:
        handler.setLevel(logging.DEBUG)
    
    
    return logger

def enable_quiet_mode():
    """Enable quiet mode - log only warnings and errors."""
    logger = logging.getLogger()
    
    for handler in logger.handlers:
        if isinstance(handler, logging.StreamHandler) and handler.stream == sys.stdout:
            handler.setLevel(logging.WARNING)
    
    return logger
