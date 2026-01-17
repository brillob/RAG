"""Utility functions."""
import logging
from typing import Optional


def setup_logging(level: str = "INFO") -> None:
    """Configure application logging."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
        ]
    )


def validate_query(query: str) -> tuple[bool, Optional[str]]:
    """
    Validate a query string.
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not query or not query.strip():
        return False, "Query cannot be empty"
    
    if len(query) > 2000:
        return False, "Query is too long (max 2000 characters)"
    
    return True, None
