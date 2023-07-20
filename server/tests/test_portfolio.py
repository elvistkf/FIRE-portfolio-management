import pytest
import pandas as pd
import numpy as np
import portfolio.portfolio as p
import schema


class TestPortfolio:
    @pytest.fixture
    def transactions_df(self):
        transactions = [
            schema.Transaction(id=1, date="2023-01-01T00:00:00", account=1, action="Deposit", amount=50000),
            schema.Transaction(id=2, date="2023-01-01T00:00:00", account=1, action="Buy", ticker="QQQ", amount=260, shares=10),
            schema.Transaction(id=3, date="2023-01-15T00:00:00", account=1, action="Buy", ticker="VOO", amount=349.62, shares=20),
            schema.Transaction(id=4, date="2023-01-16T00:00:00", account=2, action="Buy", ticker="VOO", amount=351.09, shares=52),
            schema.Transaction(id=5, date="2023-02-01T00:00:00", account=1, action="Buy", ticker="QQQ", amount=299.12, shares=15),
            schema.Transaction(id=6, date="2023-03-01T00:00:00", account=1, action="Buy", ticker="QQQ", amount=292.43, shares=10),
            schema.Transaction(id=7, date="2023-03-01T00:00:00", account=1, action="Buy", ticker="TSLA", amount=204.08, shares=5),
            schema.Transaction(id=8, date="2023-03-12T00:00:00", account=2, action="Buy", ticker="VOO", amount=360.08, shares=5),
            schema.Transaction(id=9, date="2023-02-01T00:00:00", account=1, action="Sell", ticker="QQQ", amount=299.12, shares=25)
        ]
        return pd.DataFrame([t.dict() for t in transactions])

    @pytest.fixture
    def portfolio(self, transactions_df):
        return p.Portfolio(details=transactions_df)

    def test_portfolio_init(self, transactions_df):
        """Test Portfolio initialization with valid transaction DataFrame"""
        _ = p.Portfolio(transactions_df)
        assert True

    def test_portfolio_init_with_invalid_details_type(self):
        """Test Portfolio initialization with invalid data type for the input details. This should raise a TypeError."""
        with pytest.raises(TypeError):
            _ = p.Portfolio(details=[[0.5, 0.2, 0.3]])

    def test_portfolio_init_with_missing_columns(self):
        """Test Portfolio initialization with correct data type for details (DataFrame), but with missing columns.
        This should raise an AttributeError."""
        with pytest.raises(AttributeError, match="Expected matching columns from transaction details with table schema."):
            df = pd.DataFrame(data=[[0, 1, 2, 3]])
            _ = p.Portfolio(details=df)

    def test_portfolio_init_with_mismatched_columns(self):
        """Test Portfolio initialization with correct data type for details (DataFrame), but with mismatched columns.
        This should raise an AttributedError."""
        with pytest.raises(AttributeError, match="Expected matching columns from transaction details with table schema."):
            df = pd.DataFrame(data=[[0, 1, 2, 3, 4, 5]], columns=["id", "Shares", "price", "datetime", "account_no", "stock"])
            _ = p.Portfolio(details=df)

    def test_portfolio_get_summary(self, portfolio):
        """Test Portfolio.get_summary with valid transaction DataFrame"""
        expected = pd.DataFrame(
            [
                {"account": 1, "ticker": "QQQ", "total_shares": 10, "book_value": 2860.31, "avg_cost": 286.03},
                {"account": 1, "ticker": "VOO", "total_shares": 20, "book_value": 6992.40, "avg_cost": 349.62},
                {"account": 1, "ticker": "TSLA", "total_shares": 5, "book_value": 1020.40, "avg_cost": 204.08},
                {"account": 2, "ticker": "VOO", "total_shares": 57, "book_value": 20057.08, "avg_cost": 351.88},
            ]
        ).set_index(["account", "ticker"])
        assert np.all(portfolio.get_holdings() - expected == 0)
