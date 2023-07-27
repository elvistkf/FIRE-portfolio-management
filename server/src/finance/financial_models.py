import pandas as pd
import numpy as np
from scipy.stats import norm
from .utils import is_psd, is_matching_index, is_close
from exceptions import MismatchedIndexException, MismatchedDimensionException


def validate_weights(w: pd.Series | np.ndarray) -> None:
    """
    Validate if the provided weights w is valid subject to practical constraints.
    If any of the constraints are violated, an exception is raised.

    Args:
        w (pd.Series | np.ndarray): Weights to be checked for validity.
    
    Raises:
        TypeError: If the input weights is not a Series.
        ValueError: If the sum of the weights is not equal to 1, or if any element in the weights is negative.
    """
    if not isinstance(w, pd.Series) and not isinstance(w, np.ndarray):
        raise TypeError(f"Expected weights w to be a Series or ndarray, instead found {type(w)}.")
    if not is_close(w.sum(), 1, threshold=0.001):  # the sum of the weights must equal to 1
        raise ValueError(f"Expected the sum of weights w to be 1, instead found {w.sum()}.")
    if np.any(w < 0):  # all elements in weights must be non-negative
        raise ValueError("Expected all elements in weights w to be non-negative.")


def expected_return(w: pd.Series | np.ndarray, er: pd.Series) -> float:
    """
    Calculate the overall expected return of a combination of assets.

    Args:
        w (pd.Series | np.ndarray): Weight distribution of the assets.
        er (pd.Series): Expected return of each asset.

    Returns:
        float: Expected return of the combined assets.

    Raises:
        TypeError: If either 'w' or 'er' is not a pandas Series.
        MismatchedIndexException: If the indices of 'w' and 'er' do not match.
        MismatchedDimensionException: If the dimensions of 'w' and 'er' do not match.

    """
    validate_weights(w)
    if not isinstance(er, pd.Series) and not isinstance(er, np.ndarray):
        raise TypeError(f"Expected expected return er to be a Series or ndarray, instead found {type(er)}.")
    if isinstance(w, pd.Series) and not is_matching_index(w.index, er.index):
        raise MismatchedIndexException("Expected matching index from weights w and expected return er.")
    if isinstance(w, np.ndarray) and w.shape[0] != er.shape[0]:
        raise MismatchedDimensionException("Expected matching dimensions from weights w and expected return er")

    return w.T @ er


def volatility(w: pd.Series | np.ndarray, cov: pd.DataFrame) -> float:
    """
    Calculate the overall volatility of a combination of assets.

    Args:
        w (pd.Series | np.ndarray): Weight distribution of the assets.
        cov (pd.DataFrame): Covariance matrix of the assets.

    Returns:
        float: Volatility of the combined assets

    Raises:
        TypeError: If either 'w' or 'cov' is not a Series or DataFrame.
        ValueError: If the covariance matrix `cov` is not positive semi-definite.
        MismatchedIndexException: If the indices of 'w' and 'cov' do not match, or if the covariance matrix has mismatched index and columns.

    """
    validate_weights(w)
    if not isinstance(cov, pd.DataFrame):
        raise TypeError(f"Expected covariance matrix cov to be a DataFrame, instead found {type(cov)}.")
    if not is_psd(cov):
        raise ValueError("Expected covariance matrix cov to be positive semi-definiteness.")
    if isinstance(w, pd.Series) and not is_matching_index(w.index, cov.index):
        raise MismatchedIndexException("Expected matching index from weights w and covariance matrix cov.")
    if isinstance(w, np.ndarray) and w.shape[0] != cov.shape[0]:
        raise MismatchedDimensionException("Expected matching dimensions from weights w and covariance matrix cov.")
    if not is_matching_index(cov.index, cov.columns, strict=True):
        raise MismatchedIndexException("Expected matching index and columns for the covariance matrix.")

    return np.sqrt(w.T @ cov @ w)


def sharpe_ratio(w: pd.Series | np.ndarray, er: pd.Series, cov: pd.DataFrame, rf: int | float = 0) -> float:
    """
    Calculate the Sharpe ratio of a combination of assets.

    Args:
        w (pd.Series | np.ndarray): Weight distribution of the assets.
        er (pd.Series): Expected return of each asset.
        cov (pd.DataFrame): Covariance matrix of the assets.
        rf (float): Risk-free return (by the same interval as the expected return).

    Returns:
        float: Sharpe ratio of the combined assets.

    Raises:
        TypeError: If the riskfree rate 'rf' is neither a float nor an int
    """
    if not isinstance(rf, float) and not isinstance(rf, int):
        raise TypeError(f"Expected risk-free rate rf to be int or float, instead found {type(rf)}.")

    adjusted_return = expected_return(w, er) - rf
    return adjusted_return / volatility(w, cov)


def information_ratio(w: pd.Series, er: pd.Series, cov: pd.DataFrame) -> float:
    """
    Calculate the information ratio of a combination of assets.

    Args:
        w (pd.Series): Weight distribution of the assets.
        er (pd.Series): Expected return of each asset.
        cov (pd.DataFrame): Covariance matrix of the assets.

    Returns:
        float: Information ratio of the combined assets
    """
    return sharpe_ratio(w, er, cov, 0)


def annualized_return(r: pd.Series | pd.DataFrame, periods_per_year: int) -> float:
    """
    Calculate the annualized return from historical returns.

    Args:
        r (pd.Series or pd.DataFrame): The historical returns of an asset or a portfolio. 
        periods_per_year (int): The number of periods that occur in a year.

    Returns:
        float: The annualized return of the input data.

    Raises:
        TypeError: If the input 'r' is neither a Series nor a DataFrame.

    Examples:
        >>> returns = pd.Series([0.05, 0.02, 0.03, -0.01, 0.04])
        >>> annualized_return(returns, periods_per_year=12)
        0.35740220595206784

        >>> portfolio_returns = pd.DataFrame({
        ...     'Asset1': [0.04, 0.02, 0.03, 0.01, 0.05],
        ...     'Asset2': [0.03, 0.01, 0.02, -0.01, 0.04]
        ... })
        >>> annualized_return(portfolio_returns, periods_per_year=12)
        Asset1    0.424149
        Asset2    0.236589
        dtype: float64
    """
    if isinstance(r, pd.Series):
        ar = (1+r).prod() ** (periods_per_year / r.shape[0]) - 1
        return ar
    elif isinstance(r, pd.DataFrame):
        return r.aggregate(annualized_return, periods_per_year=periods_per_year)
    else:
        raise TypeError(f"Expected r to be a Series or DataFrame, instead found {type(r)}.")


def annualized_volatility(r: pd.Series | pd.DataFrame, periods_per_year: int) -> float:
    """
    Calculate the annualized volatility from historical returns.

    Args:
        r (pd.Series or pd.DataFrame): The historical returns of an asset or a portfolio. 
        periods_per_year (int): The number of periods that occur in a year.

    Returns:
        float: The annualized volatility of the input data.

    Raises:
        TypeError: If the input 'r' is neither a Series nor a DataFrame.
    """
    if isinstance(r, pd.Series):
        av = r.std() * (periods_per_year ** 0.5)
        return av
    elif isinstance(r, pd.DataFrame):
        return r.aggregate(annualized_volatility, periods_per_year=periods_per_year)
    else:
        raise TypeError(f"Expected r to be a Series or DataFrame, instead found {type(r)}.")


def annualized_sharpe_ratio(r: pd.Series | pd.DataFrame, periods_per_year: int, rf: int | float, w: pd.Series | None = None) -> float:
    """
    Calculate the annualized Sharpe ratio from historical returns..

    The Sharpe ratio measures the risk-adjusted return of an investment or portfolio.
    A higher Sharpe ratio indicates better risk-adjusted performance.

    Args:
        r (pd.Series or pd.DataFrame): The historical returns of an asset or a portfolio. 
        periods_per_year (int): The number of periods that occur in a year.
        rf (int or float): The risk-free rate of return (annualized).
        w (pd.Series, optional): The weights of assets in the portfolio (applicable only if `r` is a DataFrame). 

    Returns:
        float: The annualized Sharpe ratio of the input data.

    Raises:
        TypeError: If the input 'r' is neither a Series nor a DataFrame.
    """
    if isinstance(r, pd.Series):
        r = r.dropna()
        annual_return = annualized_return(r, periods_per_year)
        annual_vol = annualized_volatility(r, periods_per_year)
        return (annual_return - rf) / annual_vol
    elif isinstance(r, pd.DataFrame):
        if w is None:
            return r.aggregate(annualized_sharpe_ratio, rf=rf, periods_per_year=periods_per_year)
        else:
            validate_weights(w)
            r_agg = (w * r).sum(axis=1)
            return annualized_sharpe_ratio(r_agg, periods_per_year=periods_per_year, rf=rf)
    else:
        raise TypeError(f"Expected r to be a Series or DataFrame, instead found {type(r)}.")


def var_gaussian(w: pd.Series, er: pd.Series, cov: pd.DataFrame, alpha: float = 0.95) -> float:
    """
    Calculate the Value-at-Risk (VaR) of a combination of assets by Variance-Covariance method.

    The VaR is defined as the maximum potential loss expected, under normal market condition, with a certain confidence level.
    A VaR of 100 with confidence level of 99% means that the maximum loss will not exceed 100 with probability of 99%.

    Note that this function assumes normality of the underlying assets.
    If this assumption is not satisfied, the historical method must be used.
    See var_historic for calculating VaR with historical method.

    Args:
        w (pd.Series): Weight distribution of the assets.
        er (pd.Series): Expected return of each asset.
        cov (pd.DataFrame): Covariance matrix of the assets.
        alpha (float): Confidence level in range (0, 1). For example, a confidence level of 95% is represented by 0.95. Defaults to 0.95.

    Returns:
        float: Value-at-Risk (VaR) of the combined assets

    Raises:
        TypeError: If the input 'alpha' is not a float.
        ValueError: If the input 'alpha' is not in range (0, 1).
    """
    if not isinstance(alpha, float):
        raise TypeError(f"Expected confidence level alpha to be a float, instead found {type(alpha)}.")
    if alpha <= 0 or alpha >= 1:
        raise ValueError(f"Expected confidence level alpha to be in (0, 1), instead found {alpha}.")

    mean = expected_return(w, er)
    vol = volatility(w, cov)
    return -norm.ppf(1 - alpha, mean, vol)


def var_historic(r: pd.Series | pd.DataFrame, alpha: float = 0.95, w: pd.Series | None = None) -> float | pd.Series:
    """
    Calculate the Value-at-Risk (VaR) of a single asset of a combination of assets by historical method.

    The VaR is defined as the maximum potential loss expected, under normal market condition, with a certain confidence level.
    A VaR of 100 with confidence level of 99% means that the maximum potential loss will not exceed 100 with probability of 99%.

    Args:
        r (pd.DataFrame | pd.Series): Historical return of the asset(s).
        alpha (float, optional): Confidence level in range [0, 1]. Defaults to 0.95.
        w (pd.Series | None, optional): Weight distribution of the assets. Defaults to None.

    Returns:
        float | pd.Series: The historical VaR for the asset(s).
        If only one asset's data is provided, or if weights are provided, the returned value is a float representing the overall historical VaR.
        If multiple assets are provided but not weights, then a Series is provided with the VaR for each asset.

    Raises:
        TypeError: If the input 'r' is neither a Series nor a DataFrame.
    """
    if not isinstance(alpha, float):
        TypeError(f"Expected confidence level alpha to be a float, instead found {type(alpha)}.")
    if isinstance(r, pd.Series):
        return -np.percentile(r.dropna(), q=int((1 - alpha) * 100), axis=0)
    elif isinstance(r, pd.DataFrame):
        var = r.aggregate(var_historic, alpha=alpha)
        if w is None:
            return var
        else:
            validate_weights(w)
            return w.T @ var
    else:
        raise TypeError(f"Expected r to be a Series or DataFrame, instead found {type(r)}.")


def cvar_historic(r: pd.DataFrame | pd.Series, alpha: float = 0.95, w: pd.Series | None = None) -> float | pd.Series:
    """
    Calculate the Conditional Value-at-Risk (CVaR) of a single asset of a combination of assets by historical method.

    Args:
        r (pd.DataFrame | pd.Series): Historical return of the asset(s).
        alpha (float, optional): Confidence level in range [0, 1]. Defaults to 0.95.
        w (pd.Series | None, optional): Weight distribution of the assets. Defaults to None.

    Returns:
        float | pd.Series: The historical CVaR for the asset(s).
        If only one asset's data is provided, or if weights are provided, the returned value is a float representing the overall historical CVaR.
        If multiple assets are provided but not weights, a Series is provided with the CVaR for each asset.

    Raises:
        TypeError: If the input 'r' is neither a Series nor a DataFrame.
    """
    if isinstance(r, pd.Series):
        return -r[r <= -var_historic(r, alpha=alpha)].mean()
    elif isinstance(r, pd.DataFrame):
        cvar = r.aggregate(cvar_historic, alpha=alpha)
        if w is None:
            return cvar
        else:
            validate_weights(w)
            return w.T @ cvar
    else:
        raise TypeError(f"Expected r to be a Series or DataFrame, instead found {type(r)}.")


def risk_contribution(w: pd.Series | np.ndarray, cov: pd.DataFrame, relative: bool = True) -> pd.Series:
    """
    Calculate the risk contribution of each asset in a portfolio.

    Args:
        w (pd.Series | np.ndarray): Weight distribution of the assets.
        cov (pd.DataFrame): Covariance matrix of the assets.
        relative (bool, optional): Whether to return the relative risk contribution. Defaults to True.

    Raises:
        TypeError: If the input 'cov' is not a DataFrame.

    Returns:
        pd.Series: Risk contribution of each asset in the portfolio.
    """
    validate_weights(w)
    if not isinstance(cov, pd.DataFrame):
        raise TypeError(f"Expected covariance matrix cov to be a DataFrame, instead found {type(cov)}.")
    pwr = 1 if relative else 0.5
    Sw = cov @ w
    RRC = w * Sw / (np.power((w.T @ Sw), pwr))
    RRC = pd.Series(RRC, index=cov.index)
    return RRC