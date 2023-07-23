from typing import Any, Type, List
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

    Examples:
        >>> idx1 = pd.Index([1, 2, 3, 4, 5])
        >>> idx2 = pd.Index([5, 4, 3, 2, 1])
        >>> is_matching_index(idx1, idx2)
        True

        >>> idx3 = pd.Index(['apple', 'banana', 'orange'])
        >>> idx4 = pd.Index(['banana', 'orange', 'apple'])
        >>> is_matching_index(idx3, idx4, strict=True)
        False
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

    Examples:
        >>> matrix1 = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
        >>> is_psd(matrix1)
        True

        >>> matrix3 = np.array([[1, 2, 3], [4, 5, 6]])
        >>> is_psd(matrix3)
        False
    """
    if not isinstance(X, pd.DataFrame) and not isinstance(X, np.ndarray):
        raise TypeError(
            f"Expected input matrix X to be DataFrame or ndarray, instead found {type(X)}."
        )

    if isinstance(X, pd.DataFrame):
        X = X.to_numpy()

    if X.shape[0] != X.shape[1]:  # X must be a squared matrix to be PSD
        return False
    if not np.all(X - X.T == 0):  # X must be symmetric
        return False

    try:
        # regularize the input matrix to make it PD if it is PSD
        X_reg = X + np.eye(X.shape[0]) * 1e-10
        # apply the Cholesky decomposition to the regularized matrix, which fails if it is not PD
        _ = np.linalg.cholesky(X_reg)
    except np.linalg.LinAlgError:
        return False

    return True


def normalize(s: pd.Series | np.ndarray) -> pd.Series:
    """Normalize the a non-negative (element-wise) array/Series to sum up to 1

    Args:
        s (pd.Series | np.ndarray): Input array/Series

    Returns:
        pd.Series: Normalized array/Series

    Examples:
        >>> arr = np.array([10, 20, 30, 40])
        >>> normalize(arr)
        array([0.1, 0.2, 0.3, 0.4])

        >>> series = pd.Series([0.5, 0.5, 0.5])
        >>> normalize(series)
        0    0.333333
        1    0.333333
        2    0.333333
        dtype: float64
    """
    if not (isinstance(s, pd.Series) or isinstance(s, np.ndarray)):
        raise TypeError(
            f"Expected s to be a Series or ndarray, instead found {type(s)}"
        )
    if np.any(s < 0):
        raise ValueError(
            "Expected s to be non-negative array/Series."
        )
    return s / s.sum()


def is_iterable_of_type(var: Any, itype: Type, dtype: Type) -> bool:
    """Check if a variable is an iterable of a specific type.

    This function verifies whether the input variable is an iterable (e.g., list, tuple, etc.)
    and if all its elements are of a specific data type.

    Args:
        var (Any): Variable to be checked.
        itype (Type): The expected iterable type (e.g., list, tuple, etc.).
        dtype (Type): The expected data type of elements inside the iterable.

    Returns:
        bool: True if the variable is an iterable of the specified type and all its elements are of the specified data type. False otherwise.

    Examples:
        >>> list1 = [1, 2, 3, 4]
        >>> is_iterable_of_type(list1, list, int)
        True

        >>> tuple1 = ("apple", "banana", "orange")
        >>> is_iterable_of_type(tuple1, tuple, str)
        True

        >>> list2 = [1, 2, 3, "four"]
        >>> is_iterable_of_type(list3, list, int)
        False
    """
    return isinstance(var, itype) and np.all([isinstance(item, dtype) for item in var])


def is_list_of_type(var: Any, dtype: Type) -> bool:
    return is_iterable_of_type(var, list, dtype)


def is_tuple_of_type(var: Any, dtype: Type) -> bool:
    return is_iterable_of_type(var, tuple, dtype)


def is_close(
    d1: pd.DataFrame | pd.Series | np.ndarray | List[float] | List[int] | float | int,
    d2: pd.DataFrame | pd.Series | np.ndarray | List[float] | List[int] | float | int,
    threshold: float = 1e-5
) -> bool:
    if isinstance(d1, pd.DataFrame) \
        and isinstance(d2, pd.DataFrame) or isinstance(d1, pd.Series) \
            and isinstance(d2, pd.Series):
        
        d1 = d1.sort_index()
        d2 = d2.sort_index()
        return np.all((np.abs(d1 - d2) <= threshold) | (pd.isna(d1) & pd.isna(d2)))
    elif (is_list_of_type(d1, float) or is_list_of_type(d1, int)) and (is_list_of_type(d2, float) or is_list_of_type(d2, int)):
        d1 = np.array(d1)
        d2 = np.array(d2)
        return np.all(np.abs(d1 - d2) <= threshold)
    return np.all(np.abs(d1 - d2) <= threshold)
