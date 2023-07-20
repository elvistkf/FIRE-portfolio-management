import pytest
import pandas as pd
import portfolio.portfolio as p
import portfolio.common as common
import schema


@pytest.fixture
def transactions():
    return [
        schema.Transaction(id=1, date="2023-01-01T00:00:00", account=1, ticker="QQQ", price=260, shares=10),
        schema.Transaction(id=2, date="2023-01-15T00:00:00", account=1, ticker="VOO", price=349.62, shares=20),
        schema.Transaction(id=3, date="2023-01-16T00:00:00", account=2, ticker="VOO", price=351.09, shares=52),
        schema.Transaction(id=4, date="2023-02-01T00:00:00", account=1, ticker="QQQ", price=299.12, shares=15),
        schema.Transaction(id=5, date="2023-03-01T00:00:00", account=1, ticker="QQQ", price=292.43, shares=10),
        schema.Transaction(id=6, date="2023-03-01T00:00:00", account=1, ticker="TSLA", price=204.08, shares=5),
        schema.Transaction(id=6, date="2023-03-12T00:00:00", account=2, ticker="VOO", price=360.08, shares=5),
    ]


@pytest.fixture
def transactions_df(transactions):
    return pd.DataFrame([t.dict() for t in transactions])


def test_portfolio_init(transactions_df):
    """Test Portfolio initialization with valid transaction DataFrame"""
    _ = p.Portfolio(transactions_df)
    assert True


def test_portfolio_init_with_invalid_details_type():
    """Test Portfolio initialization with invalid data type for the input details. This should raise a TypeError."""
    with pytest.raises(TypeError):
        _ = p.Portfolio(details=[[0.5, 0.2, 0.3]])


def test_portfolio_init_with_missing_columns():
    """Test Portfolio initialization with correct data type for details (DataFrame), but with missing columns. This should raise an AttributeError."""
    with pytest.raises(AttributeError, match="Expected matching columns from transaction details with table schema."):
        df = pd.DataFrame(data=[[0, 1, 2, 3]])
        _ = p.Portfolio(details=df)


def test_portfolio_init_with_mismatched_columns():
    """Test Portfolio initialization with correct data type for details (DataFrame), but with mismatched columns.
    This should raise an AttributedError."""
    with pytest.raises(AttributeError, match="Expected matching columns from transaction details with table schema."):
        df = pd.DataFrame(data=[[0, 1, 2, 3, 4, 5]], columns=["id", "Shares", "price", "datetime", "account_no", "stock"])
        _ = p.Portfolio(details=df)


def test_portfolio_get_summary(transactions_df):
    """Test Portfolio.get_summary with valid transaction DataFrame"""
    expected = pd.DataFrame(
        [
            {"account": 1, "ticker": "QQQ", "total_shares": 35, "total_cost": 10011.1},
            {"account": 1, "ticker": "VOO", "total_shares": 20, "total_cost": 6992.40},
            {"account": 1, "ticker": "TSLA", "total_shares": 5, "total_cost": 1020.40},
            {"account": 2, "ticker": "VOO", "total_shares": 57, "total_cost": 20057.08},
        ]
    ).set_index(["account", "ticker"])
    portfolio = p.Portfolio(details=transactions_df)
    print(expected)
    assert common.is_close(expected, portfolio.get_summary())
