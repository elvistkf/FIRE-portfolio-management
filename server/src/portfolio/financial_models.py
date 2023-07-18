import pandas as pd
import numpy as np
from scipy.stats import norm

def expected_return(w: pd.Series, er: pd.Series) -> float:
    """Calculate the overall expected return of a combination of assets.

    Args:
        w (pd.Series): Weight distribution of the assets.
        er (pd.Series): Expected return of each asset.

    Returns:
        float: Expected return of the combined assets.
    """
    if not all(w.index.sort_values() == er.index.sort_values()):
        raise ValueError("Expected matching index from weights w and expected return er.")
    
    return w.T @ er

def volatility(w: pd.Series, cov: pd.DataFrame) -> float:
    """Calculate the overall volatility of a combination of assets.

    Args:
        w (pd.Series): Weight distribution of the assets.
        cov (pd.DataFrame): Covariance matrix of the assets.

    Returns:
        float: Volatility of the combined assets
    """
    if not all(w.index.sort_values() == cov.index.sort_values()):
        raise ValueError("Expected matching index from weights w and covariance matrix cov.")
    if not all(cov.index == cov.columns):
        raise ValueError("Expected matching index and columns for the covariance matrix.")
    
    return np.sqrt(w.T @ cov @ w)

def sharpe_ratio(w: pd.Series, er: pd.Series, cov: pd.DataFrame, rf: float) -> float:
    """Calculate the Sharpe ratio of a combination of assets.

    Args:
        w (pd.Series): Weight distribution of the assets.
        er (pd.Series): Expected return of each asset.
        cov (pd.DataFrame): Covariance matrix of the assets.
        rf (float): Risk-free return.

    Returns:
        float: Sharpe ratio of the combined assets.
    """
    adjusted_return = expected_return(w, er) - rf
    return adjusted_return / volatility(w, cov)

def information_ratio(w: pd.Series, er: pd.Series, cov: pd.DataFrame) -> float:
    """Calculate the information ratio of a combination of assets.

    Args:
        w (pd.Series): Weight distribution of the assets.
        er (pd.Series): Expected return of each asset.
        cov (pd.DataFrame): Covariance matrix of the assets.

    Returns:
        float: Information ratio of the combined assets
    """
    return sharpe_ratio(w, er, cov, 0)

def value_at_risk(w: pd.Series, er: pd.Series, cov: pd.DataFrame, alpha: float = 0.95) -> float:
    """Calculate the Value-at-Risk (VaR) of a combination of assets by Variance-Covariance method.

    The VaR is defined as the maximum potential loss expected, under normal market condition, with a certain confidence level.
    A VaR of 100 with confidence level of 99% means that the maximum potential loss will not exceed 100 with probability of 99%.

    Args:
        w (pd.Series): Weight distribution of the assets.
        er (pd.Series): Expected return of each asset.
        cov (pd.DataFrame): Covariance matrix of the assets.
        alpha (float): Confidence level in range [0, 1]. For example, a confidence level of 95% is represented by 0.95. Defaults to 0.95.

    Returns:
        float: Value-at-Risk (VaR) of the combined assets
    """
    mean = expected_return(w, er)
    vol = volatility(w, cov)
    return -norm.ppf(1-alpha, mean, vol)

def historic_value_at_risk(r: pd.Series | pd.DataFrame, alpha: float = 0.95, w: pd.Series = None) -> float | pd.Series:
    """Calculate the Value-at-Risk (VaR) of a single asset of a combination of assets by historical method.

    Args:
        r (pd.DataFrame | pd.Series): Historical return of the asset(s).
        alpha (float, optional): Confidence level in range [0, 1]. Defaults to 0.95.
        w (pd.Series, optional): Weight distribution of the assets. Defaults to None.

    Returns:
        float | pd.Series: The historical VaR for the asset(s). 
        If only one asset's data is provided, or if weights are provided, the returned value is a float representing the overall historical VaR.
        If multiple assets are provided but not weights, then a Series is provided with the VaR for each asset.
    """
    if isinstance(r, pd.Series):
        return -np.percentile(r.dropna(), q=int((1-alpha) * 100), axis=0)
    elif isinstance(r, pd.DataFrame):
        var = r.aggregate(historic_value_at_risk, alpha = alpha)
        if w is None:
            return var
        else:
            return w.T @ var
    else:
        raise TypeError("Expected r to be a Series or DataFrame.")
        