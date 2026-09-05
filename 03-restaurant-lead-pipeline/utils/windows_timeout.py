#!/usr/bin/env python3
"""
Windows-compatible timeout utility
Replaces Unix-specific timeout_decorator for Windows compatibility
"""

import threading
import time
import functools
from typing import Callable, Any

def timeout(seconds: int):
    """
    Windows-compatible timeout decorator
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            result = [None]
            exception = [None]
            
            def target():
                try:
                    result[0] = func(*args, **kwargs)
                except Exception as e:
                    exception[0] = e
            
            thread = threading.Thread(target=target)
            thread.daemon = True
            thread.start()
            thread.join(timeout=seconds)
            
            if thread.is_alive():
                # Thread is still running, timeout occurred
                raise TimeoutError(f"Function {func.__name__} timed out after {seconds} seconds")
            
            if exception[0]:
                raise exception[0]
            
            return result[0]
        
        return wrapper
    return decorator

def safe_timeout(seconds: int, default_return=None):
    """
    Safe timeout decorator that returns default value on timeout
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return timeout(seconds)(func)(*args, **kwargs)
            except TimeoutError:
                print(f"⚠️ Function {func.__name__} timed out after {seconds} seconds, returning default value")
                return default_return
            except Exception as e:
                print(f"❌ Error in {func.__name__}: {e}")
                return default_return
        
        return wrapper
    return decorator

# Create a mock timeout_decorator object for compatibility
class MockTimeoutDecorator:
    def timeout(self, seconds=None, **kwargs):
        if seconds is None:
            # Handle case where seconds is passed as keyword argument
            seconds = kwargs.get('seconds', 30)
        return timeout(seconds)

# Create the mock object
timeout_decorator = MockTimeoutDecorator() 