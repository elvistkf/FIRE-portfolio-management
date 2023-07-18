import pytest
import pandas as pd
import portfolio.portfolio as p

def test_portfolio_without_shares():
    with pytest.raises(ValueError, match="Expected column \"shares\" in the provided DataFrame."):
        df = pd.DataFrame(data = [0, 1, 2])
        portfolio = p.Portfolio(details=df)

