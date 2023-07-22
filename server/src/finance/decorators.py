from collections import OrderedDict
from io import StringIO
from typing import Callable, Any, Tuple
from .utils import is_tuple_of_type
import sys
import functools
import threading
import time


def capture_logs(func: Callable[..., Any]) -> Callable[..., Tuple[Any, str]]:
    def wrapper(*args: Any, **kwargs: Any) -> Tuple[Any, str]:
        captured_stdout = sys.stdout
        sys.stdout = captured_buffer = StringIO()
        try:
            result = func(*args, **kwargs)
        finally:
            sys.stdout = captured_stdout

        captured_logs = captured_buffer.getvalue()
        return result, captured_logs

    return wrapper


def data_cache(maxsize: int = 128, expiration_seconds: int | float = 3600) -> Callable:
    """A custom cache decorator that caches the results of function evaluations for a specified duration and with a maximum cache size.

    Args:
        maxsize (int, optional): The maximum number of entries the cache can hold.
            If the number of cached entries exceeds this value, the least recently used (LRU) entry will be evicted. Default is 128.
        expiration_seconds (int | float, optional): The duration in seconds for which the cached results should be considered valid. 
            After this duration has passed, the cached results will be re-evaluated on the next function call. 
            Default is 3600 seconds (1 hour).

    Returns:
        Callable: The cache decorator that can be applied to functions to cache their results.
    """
    cache = OrderedDict()
    lock = threading.Lock()

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            normalized_args = tuple(*args) if is_tuple_of_type(args, list) or is_tuple_of_type(args, tuple) else args
            normalized_kwargs = frozenset(kwargs.items())
            key = (normalized_args, normalized_kwargs)

            # Check if the result is already cached
            with lock:
                if key in cache:
                    result, timestamp = cache[key]
                    current_time = time.time()
                    # Check if the cached result has expired
                    if result is not None and current_time - timestamp <= expiration_seconds:
                        print(f"Cache hit: {func.__name__}{normalized_args}, {kwargs}")
                        return result
                    else:
                        print(f"Cache expired: {func.__name__}{normalized_args}, {kwargs}")
                        del cache[key]

            # If the result is not cached or has expired, call the function and cache the result
            result = func(*args, **kwargs)
            with lock:
                if len(cache) >= maxsize:
                    # Remove the least recently used entry when the cache is full
                    print("Cache full: removing the earliest item")
                    cache.popitem(last=False)
                cache[key] = (result, time.time())

            return result

        return wrapper

    return decorator