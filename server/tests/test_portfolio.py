import pytest
import pandas as pd
import portfolio.portfolio as p
import schema

@pytest.fixture
def transaction():
    return pd.DataFrame(
        [
            schema.Transaction(id=1, date="2023-01-01", account=1, ticker="QQQ", price=260.0, shares=10),
            schema.Transaction(id=2, date="2023-01-15", account=1, ticker="VOO", price=349.62, shares=20),
            schema.Transaction(id=3, date="2023-02-01", account=1, ticker="QQQ", price=299.12, shares=15),
            schema.Transaction(id=4, date="2023-03-01", account=1, ticker="QQQ", price=292.43, shares=10),
            schema.Transaction(id=5, date="2023-03-01", account=1, ticker="TSLA", price=204.08, shares=5)
        ]
    )

def test_portfolio_init_with_invalid_details_type():
    """Test Portfolio with invalid data type for the input details. This should raise a TypeError.
    """
    with pytest.raises(TypeError):
        _ = p.Portfolio(details=[[0.5, 0.2, 0.3]])


def test_portfolio_init_with_missing_columns():
    """Test Portfolio with correct data type for details (DataFrame), but with missing columns. This should raise an AttributeError.
    """
    with pytest.raises(AttributeError, match="Expected matching columns from transaction details with table schema."):
        df = pd.DataFrame(data=[[0, 1, 2, 3]])
        _ = p.Portfolio(details=df)


def test_portfolio_with_mismatched_columns():
    """Test Portfolio with correct data type for details (DataFrame), but with mismatched columns. This should raise an AttributedError.
    """
    with pytest.raises(AttributeError, match="Expected matching columns from transaction details with table schema."):
        df = pd.DataFrame(data=[[0, 1, 2, 3, 4, 5]],
                          columns=["id", "Shares", "price",
                                   "datetime", "account_no", "stock"])
        _ = p.Portfolio(details=df)

