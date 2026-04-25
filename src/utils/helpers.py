"""
Utility helper functions for the test framework.
"""
import time
from datetime import datetime
from typing import Optional


def format_duration(seconds: float) -> str:
    """
    Format duration in human-readable format.

    Examples:
        0.5 -> "0.5s"
        65 -> "1m 5s"
        3661 -> "1h 1m 1s"
    """
    if seconds < 60:
        return f"{seconds:.3f}s"
    elif seconds < 3600:
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins}m {secs}s"
    else:
        hours = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours}h {mins}m {secs}s"


def get_timestamp(format_str: str = None) -> str:
    """
    Get current timestamp in specified format.

    Args:
        format_str: strftime format string.
                    Defaults to '%Y%m%d_%H%M%S'

    Returns:
        Formatted timestamp string
    """
    if format_str is None:
        format_str = '%Y%m%d_%H%M%S'
    return datetime.now().strftime(format_str)


def get_iso_timestamp() -> str:
    """Get current time in ISO format."""
    return datetime.now().isoformat()


def retry_decorator(max_attempts: int = 3, delay: float = 1.0):
    """
    Decorator for retrying a function on failure.

    Args:
        max_attempts: Maximum number of retry attempts
        delay: Delay between retries in seconds

    Usage:
        @retry_decorator(max_attempts=3, delay=0.5)
        def flaky_operation():
            ...
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        time.sleep(delay)
            raise last_exception
        return wrapper
    return decorator


def truncate_string(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate string to max_length, adding suffix if truncated."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def safe_get(dictionary: dict, *keys, default=None):
    """
    Safely get nested dictionary value.

    Usage:
        safe_get(data, 'level1', 'level2', 'key', default='N/A')
    """
    value = dictionary
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return default
    return value
