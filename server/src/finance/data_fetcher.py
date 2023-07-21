from typing import Tuple, List, Callable
from datetime import datetime
import numpy as np
import pandas as pd
import yfinance as yf
import functools
import threading
import time


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

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if np.all([isinstance(arg, list) for arg in args]):
                key = (tuple(*args), frozenset(kwargs.items()))
            else:
                key = (args, frozenset(kwargs.items()))
            # Check if the result is already cached
            with lock:
                if key in cache:
                    result, timestamp = cache[key]
                    current_time = time.time()
                    # Check if the cached result has expired
                    if current_time - timestamp <= expiration_seconds:
                        return result
                    else:
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


@data_cache(maxsize=100, expiration_seconds=10)
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
    if not (isinstance(tickers, str) or
            (isinstance(tickers, list) or isinstance(tickers, tuple)) and np.all([isinstance(ticker, str) for ticker in tickers])):
        raise TypeError(f"Expected tickers to be List[str], Tuple[str] or str, instead found {type(tickers)}.")
    else:
        return yf.download(tickers=tickers, start=start, period="1d").Close
