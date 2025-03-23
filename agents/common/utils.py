"""
Common utilities for agent functionality.

This module provides shared functions and utilities used by multiple agents,
focusing on setup, configuration, and error handling.
"""

import os
import json
import logging
from typing import Any, Dict, Optional

def setup_logging(log_level: str = "INFO") -> None:
    """
    Configure logging for the application.
    
    Args:
        log_level: The desired logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Map string log level to logging constants
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO, 
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }
    
    # Get numeric log level (default to INFO)
    numeric_level = level_map.get(log_level.upper(), logging.INFO)
    
    # Configure logging
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Set third-party loggers to a higher level to reduce noise
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    
    # Get the root logger
    logger = logging.getLogger()
    logger.setLevel(numeric_level)
    
    # Check if we're in a Lambda environment and configure accordingly
    if os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
        # In Lambda, remove existing handlers and let Lambda's handler work
        for handler in logger.handlers:
            logger.removeHandler(handler)


def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """
    Safely parse a JSON string, returning a default value on failure.
    
    Args:
        json_str: The JSON string to parse
        default: Value to return if parsing fails
        
    Returns:
        Parsed JSON object or the default value on failure
    """
    if not json_str:
        return default
        
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        return default


def get_env_var(name: str, default: Optional[str] = None, required: bool = False) -> Optional[str]:
    """
    Get an environment variable with validation.
    
    Args:
        name: Name of the environment variable
        default: Default value if not found
        required: Whether the variable is required
        
    Returns:
        Value of the environment variable or default
        
    Raises:
        ValueError: If the variable is required but not found
    """
    value = os.environ.get(name, default)
    
    if required and not value:
        raise ValueError(f"Required environment variable {name} is not set")
        
    return value


def format_lambda_response(status_code: int = 200, body: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Format a standardized API Gateway Lambda response.
    
    Args:
        status_code: HTTP status code
        body: Response body data
        
    Returns:
        Formatted response dictionary
    """
    if body is None:
        body = {}
        
    response = {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',  # CORS support
            'Access-Control-Allow-Headers': 'Content-Type,Authorization',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        'body': json.dumps(body)
    }
    
    return response