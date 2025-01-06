"""Utility functions for handling browser requests."""
from typing import Dict, Tuple, Set
from src.constants import DOMAINS_OF_INTEREST, IGNORED_ERRORS

def is_domain_of_interest(url: str) -> Tuple[bool, bool]:
    """
    Check if URL belongs to a domain we care about.
    
    Args:
        url: The URL to check
        
    Returns:
        Tuple[bool, bool]: (is_interesting, is_critical)
    """
    url_lower = url.lower()
    for domain, info in DOMAINS_OF_INTEREST.items():
        if domain in url_lower:
            return True, info['critical']
    return False, False

def should_ignore_error(error_text: str) -> bool:
    """
    Check if an error should be ignored based on predefined patterns.
    
    Args:
        error_text: The error message to check
        
    Returns:
        bool: True if the error should be ignored
    """
    return any(err in error_text for err in IGNORED_ERRORS)

def create_request_info(request) -> Dict:
    """
    Create a standardized request info dictionary.
    
    Args:
        request: The request object from Playwright
        
    Returns:
        Dict: Standardized request information
    """
    return {
        'url': str(request.url),
        'method': request.method,
        'type': request.resource_type
    }

def create_failed_request_info(request, error_text: str) -> Dict:
    """
    Create a standardized failed request info dictionary.
    
    Args:
        request: The request object from Playwright
        error_text: The error message
        
    Returns:
        Dict: Standardized failed request information
    """
    return {
        'url': str(request.url),
        'method': request.method,
        'resource_type': request.resource_type,
        'error': error_text,
        'headers': dict(request.headers) if request.headers else {}
    } 