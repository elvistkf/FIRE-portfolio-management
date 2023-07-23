import pytest
import pandas as pd
import finance.portfolio as p
import finance.utils as utils
import schema

from exceptions import MismatchedIndexException


class TestPortfolio:

    @pytest.fixture
    def transactions_df(self):
        transactions = [
            schema.Transaction(id=1, date="2023-01-01T00:00:00", account=1, action="Deposit", amount=50000),
            schema.Transaction(id=2, date="2023-01-01T00:00:00", account=1, action="Buy", ticker="QQQ", amount=2600, shares=10),
            schema.Transaction(id=3, date="2023-01-15T00:00:00", account=1, action="Buy", ticker="VOO", amount=6992.4, shares=20),
            schema.Transaction(id=4, date="2023-01-16T00:00:00", account=2, action="Buy", ticker="VOO", amount=18256.68, shares=52),
            schema.Transaction(id=5, date="2023-02-01T00:00:00", account=1, action="Buy", ticker="QQQ", amount=4486.8, shares=15),
            schema.Transaction(id=6, date="2023-03-01T00:00:00", account=1, action="Buy", ticker="QQQ", amount=2924.3, shares=10),
            schema.Transaction(id=7, date="2023-03-01T00:00:00", account=1, action="Buy", ticker="TSLA", amount=1020.4, shares=5),
            schema.Transaction(id=8, date="2023-03-12T00:00:00", account=2, action="Buy", ticker="VOO", amount=1800.4, shares=5),
            schema.Transaction(id=9, date="2023-04-01T00:00:00", account=1, action="Sell", ticker="QQQ", amount=7478, shares=25),
            schema.Transaction(id=10, date="2023-06-01T00:00:00", account=3, action="Buy", ticker="MSFT", amount=3400, shares=10),
            schema.Transaction(id=11, date="2023-06-02T00:00:00", account=3, action="Sell", ticker="MSFT", amount=3450, shares=10)
        ]
        return pd.DataFrame([t.dict() for t in transactions])

    @pytest.fixture
    def portfolio(self, transactions_df):
        return p.Portfolio(details=transactions_df)

    def test_portfolio_init(self, transactions_df: pd.DataFrame):
        """Test Portfolio initialization with a valid DataFrame containing transaction details.

        Args:
            transactions_df (pd.DataFrame): A DataFrame representing transaction details.
        """
        _ = p.Portfolio(transactions_df)
        assert True

    def test_portfolio_init_with_invalid_details_type(self):
        """Test Portfolio initialization with invalid data type for the input details. This should raise a TypeError."""
        with pytest.raises(TypeError):
            _ = p.Portfolio(details=[[0.5, 0.2, 0.3]])

    def test_portfolio_init_with_missing_columns(self):
        """Test Portfolio initialization with correct data type for details (DataFrame), but with missing columns.
        This should raise an AttributeError."""
        with pytest.raises(MismatchedIndexException):
            df = pd.DataFrame(data=[[0, 1, 2, 3]])
            _ = p.Portfolio(details=df)

    def test_portfolio_init_with_mismatched_columns(self):
        """Test Portfolio initialization with correct data type for details (DataFrame), but with mismatched columns.
        This should raise an AttributedError."""
        with pytest.raises(MismatchedIndexException):
            df = pd.DataFrame(data=[[0, 1, 2, 3, 4, 5]], columns=["id", "Shares", "price", "datetime", "account_no", "stock"])
            _ = p.Portfolio(details=df)

    def test_portfolio_get_holdings(self, portfolio: p.Portfolio):
        """
        Test the `get_holdings` method of the Portfolio class with a valid transaction DataFrame.

        Args:
        portfolio (p.Portfolio): An instance of the Portfolio class containing valid transaction data.
        """
        expected = pd.DataFrame(
            [
                {"account": 1, "ticker": "QQQ", "total_shares": 10, "book_value": 2860.31, "avg_cost": 286.03, "realized_gain": 327.21},
                {"account": 1, "ticker": "VOO", "total_shares": 20, "book_value": 6992.40, "avg_cost": 349.62, "realized_gain": 0},
                {"account": 1, "ticker": "TSLA", "total_shares": 5, "book_value": 1020.40, "avg_cost": 204.08, "realized_gain": 0},
                {"account": 2, "ticker": "VOO", "total_shares": 57, "book_value": 20057.08, "avg_cost": 351.88, "realized_gain": 0}
            ]
        ).set_index(["account", "ticker"])
        holdings = portfolio.get_holdings()
        assert utils.is_close(holdings, expected)

    @pytest.mark.parametrize("account,expected", [
        (None, pd.Series([0.108695, 0.836957, 0.054348], index=["QQQ", "VOO", "TSLA"])),
        (1, pd.Series([0.285714, 0.142857, 0.571429], index=["QQQ", "TSLA", "VOO"])),
        (2, pd.Series([1], index=["VOO"]))
    ])
    def test_portfolio_get_weights(self, portfolio: p.Portfolio, account: int, expected: pd.DataFrame):
        """Test the `get_weights` method of the Portfolio class

        Args:
            portfolio (p.Portfolio): An instance of the Portfolio class to be tested.
            account (int): The account ID for which to retrieve the weights.
            expected (pd.DataFrame): The expected weights as a pandas DataFrame. 
        """

        weights = portfolio.get_weights(account)
        print(weights)
        assert utils.is_close(weights, expected)
