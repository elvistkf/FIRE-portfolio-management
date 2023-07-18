import pytest
import pandas as pd
import portfolio.financial_models as models

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
            [0.2, 0.1, -0.1],
            [0.1, 0.3, -0.2],
            [-0.1, -0.2, 0.1]
        ],
        ["VFV", "QQC", "AC"],
        ["VFV", "QQC", "AC"]
    )


def test_expected_return(weights, er):
    assert models.expected_return(weights, er) == 0.125

def test_expected_return_with_different_index_order(weights, er):
    weights = weights.sort_index()
    assert models.expected_return(weights, er) == 0.125

