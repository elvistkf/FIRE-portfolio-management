import pytest
import pandas as pd
import numpy as np
import finance.utils as utils


@pytest.mark.parametrize("X", [
    np.array([[0.3, 0.15, -0.06]]).T @ np.array([[0.3, 0.15, -0.06]]),
    np.array([[0.6, 0, -2, 1, -0.3, 0.5]]).T @ np.array([[0.6, 0, -2, 1, -0.3, 0.5]])
])
class TestIsPSD:
    def test_ndarray(self, X: np.ndarray) -> None:
        """
        Test if the `is_psd` function correctly identifies a positive semi-definite (PSD) matrix.

        Args:
            X (np.ndarray): An input 2D NumPy array representing the matrix to be tested.
        """
        assert utils.is_psd(X)

    def test_is_psd_dataframe(self, X: np.ndarray) -> None:
        """
        Test if the `is_psd` function correctly identifies a positive semi-definite (PSD) DataFrame.

        Args:
            X (np.ndarray): An input 2D NumPy array representing the data to construct the DataFrame.
        """
        X_df = pd.DataFrame(X)
        assert utils.is_psd(X_df)

    def test_is_psd_negative(self, X: np.ndarray) -> None:
        """
        Test if the `is_psd` function correctly identifies a non-positive semi-definite matrix.

        Args:
            X (np.ndarray): An input 2D NumPy array representing the matrix used to construct the non-PSD matrix.
        """
        n = X.shape[0]
        X_neg = X + np.random.rand(n, n) * 0.01 - np.eye(n)
        assert not utils.is_psd(X_neg)

    def test_is_psd_invalid_type(self, X: np.ndarray) -> None:
        """
        Test if the `is_psd` function raises a TypeError for an invalid input type.

        Args:
            X (np.ndarray):  Unused parameter from pytest parametrization.
        """
        with pytest.raises(TypeError):
            _ = utils.is_psd([[1, 2, 3], [2, 1, 3], [3, 2, 1]])


@pytest.mark.parametrize("arr, expected", [
    (np.array([1, 1, 2, 2, 4]), np.array([0.1, 0.1, 0.2, 0.2, 0.4])),
    (np.array([0.6, 0.3, 0.2, 0.9, 2]), np.array([0.15, 0.075, 0.05, 0.225, 0.5]))
])
class TestNormalize:
    def test_normalize_ndarray(self, arr, expected):
        assert np.all(utils.normalize(arr) == expected)

    def test_normalize_series(self, arr, expected):
        _s = pd.Series(arr)
        assert np.all(utils.normalize(_s) == expected)

    def test_normalize_list(self, arr, expected):
        _l = list(arr)
        with pytest.raises(TypeError):
            _ = utils.normalize(_l)

    def test_normalize_negative_ndarray(self, arr, expected):
        with pytest.raises(ValueError):
            _ = utils.normalize(-arr)


@pytest.mark.parametrize(
    "var, dtype, expected_result",
    [
        ([1, 2, 3], int, True),                 # All elements are integers
        (["apple", "banana"], str, True),       # All elements are strings
        ([1, 2, "hello"], int, False),          # Not all elements are integers
        (["apple", "banana"], int, False),      # Not all elements are integers
        ([], int, True),                        # Empty list should return True
        ([1.5, 2.7, 3.0], float, True),         # All elements are floats
        ([1, 2, 3], float, False),              # Not all elements are floats
        (["apple", "banana"], float, False),    # Not all elements are floats
        ("not_a_list", int, False),             # Not a list, should return False
    ],
)
class TestIsListOfType:
    def test_is_list_of_type(self, var, dtype, expected_result):
        assert utils.is_list_of_type(var=var, dtype=dtype) == expected_result


class TestIsTupleOfType:
    pass


class TestIsClose:
    pass
