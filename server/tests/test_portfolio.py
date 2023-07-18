import pytest
import pandas as pd
import portfolio.portfolio as p

def test_portfolio_with_invalid_details_type():
    """Test Portfolio with invalid data type for the input details. This should raise a TypeError.
    """
    with pytest.raises(TypeError):
        _ = p.Portfolio(details = [[0.5, 0.2, 0.3]])

def test_portfolio_with_missing_columns():
    """Test Portfolio with correct data type for details (DataFrame), but with missing columns. This should raise an AttributeError.
    """
    with pytest.raises(AttributeError, match="Expected matching columns from transaction details with table schema."):
        df = pd.DataFrame(data = [[0, 1, 2, 3]])
        _ = p.Portfolio(details=df)

def test_portfolio_with_mismatched_columns():
    """Test Portfolio with correct data type for details (DataFrame), but with mismatched columns. This should raise an AttributedError.
    """
    with pytest.raises(AttributeError, match="Expected matching columns from transaction details with table schema."):
        df = pd.DataFrame(data = [[0, 1, 2, 3, 4, 5]], columns=["id", "Shares", "price", "datetime", "account_no", "stock"])
        _ = p.Portfolio(details=df)

