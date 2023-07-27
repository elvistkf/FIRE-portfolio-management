from scipy.optimize import minimize
from .financial_models import volatility, expected_return
from .utils import normalize
import pandas as pd
import numpy as np


def max_sharpe_ratio(er: pd.Series, cov: pd.DataFrame, rf: int | float = 0):
    """
    Calculate the weights of the portfolio that maximizes the sharpe ratio

    Args:
        er (pd.Series): Expected returns of the assets
        cov (pd.DataFrame): Covariance matrix of the assets
        rf (int | float, optional): Risk free rate. Defaults to 0.

    Returns:
        pd.Series: Weights of the optimized portfolio

    Examples:
        >>> er = pd.Series([0.1, 0.2, 0.2])
        >>> cov = pd.DataFrame([[0.1, 0.05, 0.03], [0.05, 0.12, 0.01], [0.03, 0.01, 0.1]])
        >>> rf = 0.05
        >>> max_sharpe_ratio(er, cov, rf)
        0    0.000000
        1    0.449511
        2    0.550489
        dtype: float64
    """
    def obj(w, er, cov, rf):
        return -(w @ er - rf) / np.sqrt(w.T @ cov @ w)
    n = er.shape[0]
    init_guess = np.repeat(1/n, n)
    bounds = ((0.0, 1.0),) * n
    constraint_sum = {
        'type': 'eq',
        'fun': lambda x: np.sum(x) - 1
    }

    results = minimize(obj, init_guess,
                       args=(er, cov, rf),
                       method="SLSQP",
                       constraints=(constraint_sum),
                       bounds=bounds)
    return pd.Series(normalize(results.x), index=cov.index)


def global_min_volatility(cov: pd.DataFrame) -> pd.Series:
    """Calculate the weights of the portfolio that minimizes the volatility

    Args:
        cov (pd.DataFrame): Covariance matrix of the assets

    Returns:
        pd.Series: Weights of the optimized portfolio
    """
    n = cov.shape[0]
    return max_sharpe_ratio(np.repeat(1, n), cov)


def risk_budget(cov: pd.DataFrame, b: pd.Series | np.ndarray) -> pd.Series:
    """
    Calculate the weights of the portfolio that minimizes the risk contribution

    Args:
        cov (pd.DataFrame): Covariance matrix of the assets
        b (pd.Series | np.ndarray): Risk budget of each asset

    Returns:
        pd.Series: Weights of the optimized portfolio
    """
    def obj(x): 
        return 0.5 * x.T @ cov @ x - b @ np.log(x)
    x0 = np.ones(b.shape)
    constraint = {
        'type': 'ineq',
        'fun': lambda x: x
    }
    x = minimize(obj, x0, constraints=constraint).x
    w = x / (x0 @ x)
    return pd.Series(w, index=cov.index)


def min_volatility(er: pd.Series, cov: pd.DataFrame, target_return: int | float):
    """
    Calculate the weights of the portfolio that minimizes the volatility given a target return

    Args:
        er (pd.Series): Expected returns of the assets
        cov (pd.DataFrame): Covariance matrix of the assets
        target_return (int | float): Target return of the portfolio

    Returns:
        pd.Series: Weights of the optimized portfolio
    """
    def obj(x): 
        return (x.T @ cov @ x) ** 0.5
    n = er.shape[0]
    initial_weights = np.repeat(1/n, n)
    bounds = ((0.0, 1.0),) * n
    constraint_sum = {
        'type': 'eq',
        'fun': lambda x: np.sum(x) - 1
    }
    constraint_return = {
        'type': 'eq',
        'fun': lambda x: x @ er - target_return
    }

    result = minimize(obj, initial_weights, constraints=[constraint_sum, constraint_return], bounds=bounds, method="SLSQP", tol=1e-10)

    return pd.Series(result.x, index=cov.index)


def efficient_frontier(er: pd.Series, cov: pd.DataFrame, n_points: int = 100):
    """
    Calculates the efficient frontier given expected returns and covariance matrix of assets.

    Parameters:
        er (pd.Series): Expected returns for each asset in the portfolio.
        cov (pd.DataFrame): Covariance matrix of asset returns.
        n_points (int, optional): Number of points on the efficient frontier curve. Default is 100.

    Returns:
        pd.DataFrame: DataFrame containing points on the efficient frontier curve.
    """
    target_returns = np.linspace(er.min(), er.max(), n_points)
    frontier_points = []
    for target_return in target_returns:
        optimized_weights = min_volatility(er, cov, target_return)

        portfolio_return = expected_return(optimized_weights, er)
        portfolio_risk = volatility(optimized_weights, cov)
        frontier_points.append([portfolio_return, portfolio_risk, optimized_weights])

    return pd.DataFrame(frontier_points, columns=['return', 'risk', 'weights'])
