from typing import Tuple, List, Callable
from datetime import datetime
import numpy as np
import pandas as pd
import yfinance as yf
import functools
import threading
import time
import logging

if __name__ == "__main__":
    from utils import is_list_of_type, is_tuple_of_type
else:
    from .utils import is_list_of_type, is_tuple_of_type

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
    cache = {}
    lock = threading.Lock()

    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("CacheMetrics")

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            normalized_args = tuple(*args) if np.all([isinstance(arg, list) for arg in args]) else args
            normalized_kwargs = frozenset(kwargs.items())
            key = (normalized_args, normalized_kwargs)
            # Check if the result is already cached
            with lock:
                if key in cache:
                    result, timestamp = cache[key]
                    current_time = time.time()
                    # Check if the cached result has expired
                    if result is not None and current_time - timestamp <= expiration_seconds:
                        logger.info(f"Cache hit: {func.__name__}{normalized_args}, {kwargs}")
                        return result
                    else:
                        logger.info(f"Cache expired: {func.__name__}{normalized_args}, {kwargs}")
                        del cache[key]

            # If the result is not cached or has expired, call the function and cache the result
            result = func(*args, **kwargs)
            with lock:
                if len(cache) >= maxsize:
                    # Remove the least recently used entry when the cache is full
                    lru_key = min(cache, key=lambda k: cache[k][1])
                    del cache[lru_key]
                cache[key] = (result, time.time())

            return result

        return wrapper

    return decorator


@data_cache(maxsize=512, expiration_seconds=7200)
def get_tickers(tickers: Tuple[str] | List[str] | str, start: datetime | str = "2023-01-01", period: str = "1d") -> pd.DataFrame:
    """Retrieve the tickers data

    Args:
        tickers (Tuple[str] | List[str] | str): Ticker or tickers to retrieve
        start (datetime | str, optional): Start of data range. Defaults to "2023-01-01".
        period (str, optional): Period of data range. Defaults to "1d".

    Raises:
        TypeError: Raised when the provided tickers is not a List[str], Tuple[str] or str.

    Returns:
        _type_: Tickers data for the requested data range and period.
    """
    if not (isinstance(tickers, str) or is_tuple_of_type(tickers, str) or is_list_of_type(tickers, str)):
        raise TypeError(f"Expected tickers to be List[str], Tuple[str] or str, instead found {type(tickers)}.")
    else:
        return yf.download(tickers=tickers, start=start, period="1d").Close
