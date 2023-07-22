import pytest
import pandas as pd
import numpy as np
import finance.utils as utils


@pytest.fixture
def s_ndarray():
    return np.array([1, 1, 2, 2, 4])


@pytest.fixture
def s_series(s_ndarray):
    return pd.Series(s_ndarray)


class TestIsPSD:
    @pytest.fixture
    def X_ndarray(self):
        A = np.random.rand(10, 1)
        X = A @ A.T
        return X

    @pytest.fixture
    def X_df(self, X_ndarray):
        return pd.DataFrame(X_ndarray)

    def test_ndarray(self, X_ndarray):
        assert utils.is_psd(X_ndarray)

    def test_is_psd_dataframe(self, X_df):
        assert utils.is_psd(X_df)

    def test_is_psd_negative(self, X_ndarray):
        X = X_ndarray + np.random.rand(10, 10) * 0.01 - np.eye(10)
        assert not utils.is_psd(X)

    def test_is_psd_invalid_type(self):
        with pytest.raises(TypeError):
            _ = utils.is_psd([[1, 2, 3], [2, 1, 3], [3, 2, 1]])


@pytest.mark.parametrize("arr,expected", [
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


class TestIsListOfType:
    pass


class TestIsTupleOfType:
    pass