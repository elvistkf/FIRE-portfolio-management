import pytest
import pandas as pd
import finance.financial_models as models
from exceptions import MismatchedIndexException


@pytest.fixture
def weights():
    return pd.Series(
        [0.4, 0.5, 0.1],
        ["VFV", "QQC", "AC"]
    )


@pytest.fixture
def er():
    return pd.Series(
        [0.1, 0.2, -0.15],
        ["VFV", "QQC", "AC"]
    )


@pytest.fixture
def cov():
    return pd.DataFrame(
        [
            [1, 0.1, -0.1],
            [0.1, 2, -0.2],
            [-0.1, -0.2, 0.5]
        ],
        ["VFV", "QQC", "AC"],
        ["VFV", "QQC", "AC"]
    )


class TestExpectedReturn:
    def test_expected_return(self, weights, er):
        """Test expected_return with valid w and er.
        """
        assert models.expected_return(w=weights, er=er) == 0.125

    def test_expected_return_with_different_index_order(self, weights, er):
        """Test expected_return with valid w and er but with different index order.
        """
        weights = weights.sort_index()
        assert models.expected_return(w=weights, er=er) == 0.125

    def test_expected_return_with_invalid_weights_type(self, er):
        """Test expected_return with invalid data type for w. This should raise a TypeError.
        """
        with pytest.raises(TypeError):
            _ = models.expected_return([0.2, 0.3, 0.5], er)

    def test_expected_return_with_invalid_returns_type(self, weights):
        """Test expected_return with invalid data type for er. This should raise a TypeError.
        """
        with pytest.raises(TypeError):
            _ = models.expected_return(w=weights, er=[0.5, 0.2, -0.3])

    def test_expected_return_with_mismatching_index(self, weights, er):
        """Test expected_return with data types for w and er, but with mismatching index. This should raise an AttributeError.
        """
        weights.index = ["A", "B", "C"]
        er.index = ["1", "2", "3"]
        with pytest.raises(MismatchedIndexException):
            _ = models.expected_return(w=weights, er=er)
