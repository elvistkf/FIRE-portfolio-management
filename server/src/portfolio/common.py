import numpy as np
import pandas as pd

def is_psd(X: pd.DataFrame | np.matrix | np.ndarray) -> bool:
    """Check if the provided matrix is positive semi-definite (PSD).

    Args:
        X (pd.DataFrame | np.matrix | np.ndarray): Matrix to be checked for positive semi-definiteness

    Returns:
        bool: Whether the provided matrix is PSD or not.
    """
    if isinstance(X, pd.DataFrame):
        X = X.to_numpy()
    
    if X.shape[0] != X.shape[1]:        # X must be a squared matrix to be PSD
        return False
    if not np.all(X - X.T == 0):        # X must be symmetric
        return False
    
    try:
        X_reg = X + np.eye(X.shape[0]) * 1e-14
        _ = np.linalg.cholesky(X_reg)
    except np.linalg.LinAlgError:
        return False
    
    return True