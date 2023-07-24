from typing import Tuple, List
from datetime import datetime
import pandas as pd
import yfinance as yf

from .utils import is_list_of_type, is_tuple_of_type
from .decorators import data_cache


@data_cache(maxsize=512, expiration_seconds=7200)
def get_tickers(
    tickers: Tuple[str] | List[str] | str, 
    start: datetime | str = "2018-01-01", 
    end: datetime | str | None = None,
    period: str | None = None,
    interval: str = "1d"
) -> pd.DataFrame:
    """Retrieve the historical data of the provided tickers

    Args:
        tickers (Tuple[str] | List[str] | str): Ticker or tickers to retrieve
        start (datetime | str, optional): Start of data range (inclusive). Defaults to "2023-01-01".
        end (datetime | str | None, optional): End of data range (exclusive). Defaults to None.
        period (str | None, optional): Period of data range. Either use this or start and end. 
            If period is defined then start and end are ignored. Defaults to None.
            Valid periods: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max.
        interval (str, optional): Interval of data. 
            Intra-day data cannot extend past 60 days. Defaults to "1d".
            Valid intervals: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo. 
    
    Raises:
        TypeError: Raised when the provided tickers is not a List[str], Tuple[str] or str.
        ValueError: Raised when the provided period of interval is invalid.

    Returns:
        pd.DataFrame: A DataFrame representing tickers data for the requested data range and interval.

    Examples:
        >>> # Example 1: Retrieve historical data for a single ticker with default parameters
        >>> data_single_ticker = get_tickers("AAPL")
        >>> print(data_single_ticker.head())

        >>> # Example 2: Retrieve historical data for multiple tickers with a specific period
        >>> data_multiple_tickers = get_tickers(["AAPL", "GOOGL", "MSFT"], period="1mo")
        >>> print(data_multiple_tickers.head())

        >>> # Example 3: Retrieve intraday data for a single ticker within a specific date range
        >>> intraday_data = get_tickers("AAPL", start="2023-07-01", end="2023-07-15", interval="15m")
        >>> print(intraday_data.head())
    """
    if not (isinstance(tickers, str) or is_tuple_of_type(tickers, str) or is_list_of_type(tickers, str)):
        raise TypeError(f"Expected tickers to be List[str], Tuple[str] or str, instead found {type(tickers)}.")
    if period is not None and period not in ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]:
        raise ValueError(f"Expected period to be None or one of (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max), instead found {period}.")
    if interval not in ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"]:
        raise ValueError(f"Expected interval to be one of (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo), instead found {interval}.")
    
    if period is None:
        return yf.download(tickers=tickers, start=start, end=end, interval=interval).Close
    else:
        return yf.download(tickers=tickers, period=period, interval=interval).Close
