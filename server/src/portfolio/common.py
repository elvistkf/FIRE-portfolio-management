import numpy as np
import pandas as pd

def is_matching_index(idx1: pd.Index, idx2: pd.Index, strict: bool = False) -> bool:
    """Check if the provided indices match each other.

    Args:
        idx1 (pd.Index): Index 1
        idx2 (pd.Index): Index 2
        strict (bool, optional): Whether or not the indices must be in the same order. Defaults to False.

    Returns:
        bool: Whether or not the provided indices match each other.
    """
    if idx1.shape[0] != idx2.shape[0]:
        return False
    if strict:
        return np.all(idx1 == idx2)
    else:
        return np.all(idx1.sort_values() == idx2.sort_values())

def is_psd(X: pd.DataFrame | np.ndarray) -> bool:
    """Check if the provided matrix is positive semi-definite (PSD).

    Args:
        X (pd.DataFrame | np.ndarray): Matrix to be checked for positive semi-definiteness

    Returns:
        bool: Whether the provided matrix is PSD or not.
    """
    if not isinstance(X, pd.DataFrame) and not isinstance(X, np.ndarray):
        raise TypeError(f"Expected input matrix X to be DataFrame or ndarray, instead found {type(X)}.")
    
    if isinstance(X, pd.DataFrame):
        X = X.to_numpy()

    if X.shape[0] != X.shape[1]:        # X must be a squared matrix to be PSD
        return False
    if not np.all(X - X.T == 0):        # X must be symmetric
        return False
    
    try:
        X_reg = X + np.eye(X.shape[0]) * 1e-14  # regularize the input matrix to make it PD if it is PSD
        _ = np.linalg.cholesky(X_reg)           # apply the Cholesky decomposition to the regularized matrix, which fails if it is not PD
    except np.linalg.LinAlgError:
        return False

    return True