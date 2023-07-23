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
    period: str = "1d"
) -> pd.DataFrame:
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
        return yf.download(tickers=tickers, start=start, end=end, period=period).Close
