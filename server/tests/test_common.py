import pytest
import pandas as pd
import numpy as np

import portfolio.common as common


@pytest.fixture
def X_ndarray():
    A = np.random.rand(10, 10)
    X = A @ A.T
    return X


@pytest.fixture
def X_df(X_ndarray):
    return pd.DataFrame(X_ndarray)

@pytest.fixture
def s_ndarray():
    return np.array([1, 1, 2, 2, 4])

@pytest.fixture
def s_series(s_ndarray):
    return pd.Series(s_ndarray)

def test_is_psd_ndarray(X_ndarray):
    assert common.is_psd(X_ndarray)


def test_is_psd_dataframe(X_df):
    assert common.is_psd(X_df)


def test_is_psd_negative(X_ndarray):
    X = X_ndarray + np.random.rand(10, 10) * 0.01 - np.eye(10)
    assert not common.is_psd(X)


def test_is_psd_invalid_type():
    with pytest.raises(TypeError):
        _ = common.is_psd([[1, 2, 3], [2, 1, 3], [3, 2, 1]])

def test_normalize_ndarray(s_ndarray):
    assert np.all(common.normalize(s_ndarray) == np.array([0.1, 0.1, 0.2, 0.2, 0.4]))

def test_normalize_series(s_series):
    assert np.all(common.normalize(s_series) ==  np.array([0.1, 0.1, 0.2, 0.2, 0.4]))