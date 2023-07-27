import pytest
import pandas as pd
import numpy as np
import finance.financial_models as models
import finance.utils as utils
from exceptions import MismatchedIndexException


@pytest.mark.parametrize("w", [
        pd.Series([0.5, 0.5], index=["T1", "T2"]),
        pd.Series([0.25, 0.25, 0.1, 0.4], index=["T1", "T2", "T3", "T4"]),
        np.array([0.1, 0.9]),
        np.array([0.8, 0.05, 0.05, 0.1]),
        np.array([1])
    ])
class TestValidateWeights:
    def test_validate_weights_with_valid_weights(self, w: pd.Series | np.ndarray):
        """Test the `validate_weights` function with valid weight vector. This should return True."""
        models.validate_weights(w)
        assert True

    def test_validate_weights_with_invalid_sum(self, w):
        """Test the `validate_weights` function with invalid weight vector. This should raise a ValueError."""
        _w = w.copy()
        _w[0] = _w[0] + 1.0
        with pytest.raises(ValueError):
            models.validate_weights(_w)

    def test_valid_weights_with_negative_elements(self, w):
        """Test the `validate_weights` function with negative weights. This should raise a ValueError."""
        _w = w.copy()
        _w[0] = -_w[0]
        with pytest.raises(ValueError):
            models.validate_weights(_w)


@pytest.mark.parametrize("w, er, expected", [
    (
        pd.Series([0.4, 0.5, 0.1], index=["VFV", "QQC", "AC"]),
        pd.Series([0.1, 0.2, -0.15], index=["VFV", "QQC", "AC"]),
        0.125
    ),
    (
        pd.Series([0.25, 0.25, 0.1, 0.4], index=["T1", "T2", "T3", "T4"]),
        pd.Series([0, 1, 2, 3], index=["T1", "T2", "T3", "T4"]),
        1.65
    )
])
class TestExpectedReturn:
    def test_expected_return(self, w: pd.Series, er: pd.Series, expected: float):
        """Test the `expected_return` function with valid inputs.

        Args:
            w (pd.Series): A Series representing the weight vector for the assets.
            er (pd.Series): A Series representing the expected returns of the assets.
            expected (float): The expected value of the portfolio's expected return.
        """
        assert utils.is_close(models.expected_return(w=w, er=er), expected)

    def test_expected_return_with_different_index_order(self, w: pd.Series, er: pd.Series, expected: float):
        """Test the `expected_return` function with valid weight (w) and expected return (er) inputs,
        but with different index order.

        Args:
            w (pd.Series): A Series representing the weight vector for the assets.
            er (pd.Series): A Series representing the expected returns of the assets.
            expected (float): The expected value of the portfolio's expected return.
        """
        w = w.sort_index(ascending=False)
        er = er.sort_index(ascending=True)
        assert utils.is_close(models.expected_return(w=w, er=er), expected)

    def test_expected_return_with_invalid_weights_type(self, w: pd.Series, er: pd.Series, expected: float):
        """Test the `expected_return` function with invalid data type for weight (w). This should raise a TypeError.

        Args:
            w (pd.Series): A Series representing the weight vector for the assets.
            er (pd.Series): A Series representing the expected returns of the assets.
            expected (float): Unused parameters from pytest parametrization
        """
        with pytest.raises(TypeError):
            w = list(w)
            _ = models.expected_return(w , er)

    def test_expected_return_with_invalid_returns_type(self, w: pd.Series, er: pd.Series, expected: float):
        """Test `expected_return` with invalid data type for er. This should raise a TypeError.

        Args:
            w (pd.Series): A Series representing the weight vector for the assets.
            er (pd.Series): A Series representing the expected returns of the assets.
            expected (float): Unused parameters from pytest parametrization
        """
        with pytest.raises(TypeError):
            er = list(er)
            _ = models.expected_return(w=w, er=er)

    def test_expected_return_with_mismatching_index(self, w: pd.Series, er: pd.Series, expected: float):
        """Test `expected_return` with data types for w and er, but with mismatching index. This should raise an AttributeError.

        Args:
            w (pd.Series): A Series representing the weight vector for the assets.
            er (pd.Series): A Series representing the expected returns of the assets.
            expected (float): Unused parameters from pytest parametrization
        """
        weights = w.set_axis(["A"] * w.shape[0])
        er = er.set_axis(["1"] * er.shape[0])
        with pytest.raises(MismatchedIndexException):
            _ = models.expected_return(w=weights, er=er)


@pytest.mark.parametrize("w, cov, expected", [
    (
        pd.Series([0.5, 0.5], index=["T1", "T2"]),
        pd.DataFrame([[0.04, 0.03], [0.03, 0.09]], index=["T1", "T2"], columns=["T1", "T2"]),
        0.217945
    ),
    (
        pd.Series([0.7, 0.3], index=["T1", "T2"]),
        pd.DataFrame([[0.04, -0.03], [-0.03, 0.09]], index=["T1", "T2"], columns=["T1", "T2"]),
        0.122882
    )
])
class TestVolatility:
    def test_volatility(self, w: pd.Series, cov: pd.Series, expected: float):
        """Test the `volatility` function with valid input.

        Args:
            w (pd.Series): A Series representing the weight vector for the assets.
            cov (pd.Series): A Series representing the covariance matrix of asset returns.
            expected (float): The expected volatility value calculated by the 'volatility' function.
        """
        assert utils.is_close(models.volatility(w=w, cov=cov), expected)


@pytest.mark.parametrize("w, er, cov, alpha, expected", [
    (
        pd.Series([1.0, 0.0], index=["T1", "T2"]),
        pd.Series([-0.1, 0.2], index=["T1", "T2"]),
        pd.DataFrame([[0.04, 0.03], [0.03, 0.09]], index=["T1", "T2"], columns=["T1", "T2"]),   
        0.5,
        0.1
    )
])
class TestVaRGaussian:
    def test_var_gaussian(self, w: pd.Series, er: pd.Series, cov: pd.Series, alpha: float, expected: float):
        assert models.var_gaussian(w, er, cov, alpha) == expected


class TestVaRHistoric:
    pass


class TestCVaRHistoric:
    pass
