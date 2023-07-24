import pandas as pd
import numpy as np
from datetime import datetime
from sqlmodel import Session, select
from .utils import is_matching_index, normalize, interval_to_periods_per_year
from .data_fetcher import get_tickers
from .financial_models import expected_return, volatility, sharpe_ratio, var_historic, cvar_historic, annualized_sharpe_ratio

from exceptions import MismatchedIndexException
from database import engine
from schema import Transaction


class Portfolio:
    def __init__(self, details: pd.DataFrame | pd.Series | None = None) -> None:
        """
        Initialize the Portfolio object with either transaction history or shares/weights distribution.

        Args:
            details (pd.DataFrame | pd.Series | None, optional): Transaction history or shares/weights distribution for the portfolio.
                If None is passed as the argument, the transaction history from the database will be automatically retrieved. Defaults to None.

        Raises:
            TypeError: Raised when the provided details is of invalid data types
            MismatchedIndexException: Raised when the details DataFrame does not have the appropriate columns
        """
        if isinstance(details, pd.DataFrame):
            if not is_matching_index(details.columns, Transaction.get_fields()):
                raise MismatchedIndexException("Expected matching columns from transaction details with table schema.")

            # Cast the decimal columns to float64
            self.transactions = details.astype({"amount": "float64", "shares": "float64"})

        elif isinstance(details, pd.Series):
            self.holdings = pd.DataFrame(details, index=details.index, columns=["total_shares"])
            self.holdings.index.name = "ticker"
        elif details is None:
            self.transactions = self.retrieve_transactions().astype({"amount": "float64", "shares": "float64"})
        else:
            raise TypeError(f"Expected input details to be a DataFrame or a Series, instead found {type(details)}.")

    def retrieve_transactions(self) -> pd.DataFrame:
        """
        Retrieve transaction history from the database

        Returns:
            pd.DataFrame: Transaction history from the database in pandas DataFrame
        """
        with Session(engine) as session:
            statement = select(Transaction)
            results = session.exec(statement).all()
        return pd.DataFrame([t.dict() for t in results])

    def get_holdings(self) -> pd.DataFrame:
        """
        Calculate and return the holdings summary of the portfolio

        Returns:
            pd.DataFrame: The holding summary with total shares, book values and average cost for each ticker per account
        """
        try:
            return self.holdings
        except AttributeError:
            df = self.transactions[["account", "action", "ticker", "amount", "shares"]].copy()
            df["buy"] = df["action"].map({"Buy": 1, "Sell": 0}) * df["shares"]
            df["sell"] = df["action"].map({"Buy": 0, "Sell": 1}) * df["shares"]
            df["net"] = df["buy"] - df["sell"]
            df["cost"] = df["action"].map({"Buy": 1, "Sell": 0}) * df["amount"]
            df["proceeds"] = df["action"].map({"Buy": 0, "Sell": 1}) * df["amount"]

            holdings = df.groupby(["account", "ticker"]).agg(
                total_buy=pd.NamedAgg(column="buy", aggfunc=np.sum),
                total_cost=pd.NamedAgg(column="cost", aggfunc=np.sum),
                total_shares=pd.NamedAgg(column="net", aggfunc=np.sum),
                total_shares_sold=pd.NamedAgg(column="sell", aggfunc=np.sum),
                total_proceeds=pd.NamedAgg(column="proceeds", aggfunc=np.sum)
            )
            holdings["avg_cost"] = (holdings["total_cost"] / holdings["total_buy"])
            holdings["book_value"] = (holdings["avg_cost"] * holdings["total_shares"])
            holdings["realized_gain"] = (holdings["total_proceeds"] - holdings["total_shares_sold"] * holdings["avg_cost"])

            rounding_columns = ["avg_cost", "book_value", "realized_gain"]
            holdings[rounding_columns] = holdings[rounding_columns].applymap(lambda x: round(x, 2))

            self.holdings = holdings[["total_shares", "book_value", "avg_cost", "realized_gain"]] \
                .loc[holdings["total_shares"] > 0] \
                .dropna()
        finally:
            return self.holdings

    def get_weights(self, account: int | None = None) -> pd.Series:
        """
        Calculate and return the weights of each ticker of the portfolio by account

        Args:
            account (int | None, optional): The targeted account number. 
            If None is passed as argument, holdings in all accounts will be aggregated in the calculation. Defaults to None.

        Raises:
            TypeError: Raised when the provided account number is not integer or None.

        Returns:
            pd.Series: The weights of each ticker by account.
        """

        holdings = self.get_holdings().copy()
        holdings = holdings.loc[holdings["total_shares"] > 0]
        if account is None:
            holdings = holdings.reset_index().groupby("ticker").sum()
            return normalize(holdings["total_shares"])
        elif isinstance(account, int):
            total_shares_by_account = holdings.reset_index().groupby("account").sum()
            return (holdings / total_shares_by_account)["total_shares"][account]
        else:
            raise TypeError(f"Expected account number to be an integer or None, instead found {type(account)}.")

    def get_tickers_metrics(
            self, 
            start: (datetime | str) = "2018-01-01",
            end: (datetime | str | None) = None,
            period: (str | None) = None,
            interval: str = "1d"
        ) -> pd.DataFrame:
        """
        Get metrics for each ticker held in the portfolio. Note that this is not the metrics for the overall portfolio.

        This method calculates various metrics for the tickers held in the portfolio, including expected returns, 
        volatility, Sharpe ratio, Value at Risk (VaR), and Conditional Value at Risk (CVaR).

        Args:
            start (datetime | str, optional): Start of data range (inclusive) used for metric calculation. 
                Defaults to "2023-01-01".
            end (datetime | str | None, optional): End of data range (exclusive) used for metric calculation.
                Passing None as argument means the end date is the most recent available date. Defaults to None.
            period (str | None, optional): Period of data range used for metric calculation.
                If period is defined then start and end are ignored. Defaults to None.
                Valid periods: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max.
            interval (str, optional): Interval of data used for metric calculation. Defaults to "1d".
                Valid intervals: 1d, 1wk, 1mo, 3mo. 

        Returns:
            pd.DataFrame: A DataFrame containing metrics for the tickers held in the portfolio.
        """
        ticker_list = self.get_holdings().reset_index()["ticker"].drop_duplicates().to_list()
        tickers = get_tickers(ticker_list, start=start, end=end, period=period, interval=interval)
        returns: pd.DataFrame = tickers.pct_change()
        
        metrics = pd.DataFrame()
        metrics["expected_returns"] = returns.mean()
        metrics["volatility"] = returns.std()
        metrics["sharpe_ratio"] = metrics["expected_returns"] / metrics["volatility"]
        metrics["value_at_risk"] = var_historic(returns)
        metrics["conditional_value_at_risk"] = cvar_historic(returns)
        metrics["annual_sharpe_ratio"] = annualized_sharpe_ratio(returns, rf=0, periods_per_year=interval_to_periods_per_year(interval))

        return metrics
    
    def get_overall_metrics(self, 
            start: (datetime | str) = "2018-01-01",
            end: (datetime | str | None) = None,
            period: (str | None) = None,
            interval: str = "1d"
        ) -> pd.Series:
        """
        Get overall metrics for the portfolio.

        This method calculates various metrics for the overall portfolio, including the portfolio's overall expected return, 
        volatility, Sharpe ratio, Value at Risk (VaR), and Conditional Value at Risk (CVaR).

        Args:
            start (datetime | str, optional): Start of data range (inclusive) used for metric calculation. 
                Defaults to "2018-01-01".
            end (datetime | str | None, optional): End of data range (exclusive) used for metric calculation.
                Passing None as the argument means the end date is the most recent available date. Defaults to None.
            period (str | None, optional): Period of data range used for metric calculation.
                If period is defined, then start and end are ignored. Defaults to None.
                Valid periods: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max.
            interval (str, optional): Interval of data used for metric calculation. Defaults to "1d".
                Valid intervals: 1d, 1wk, 1mo, 3mo. 

        Returns:
            pd.Series: A Series containing overall metrics for the portfolio.
        """
        ticker_list = self.get_holdings().reset_index()["ticker"].drop_duplicates().to_list()
        tickers = get_tickers(ticker_list, start=start, end=end, period=period, interval=interval)
        returns: pd.DataFrame = tickers.pct_change()

        w = self.get_weights()
        er = returns.mean()
        cov = returns.dropna().cov()
        metrics = pd.Series({
            "expected_return": expected_return(w=w, er=er),
            "volatility": volatility(w=w, cov=cov),
            "sharpe_ratio": sharpe_ratio(w=w, er=er, cov=cov, rf=0.0001),
            "value_at_risk": var_historic(r=returns, w=w),
            "conditional_value_at_risk": cvar_historic(r=returns, w=w),
            "annualized_sharpe_ratio": annualized_sharpe_ratio(returns, rf=0, periods_per_year=interval_to_periods_per_year(interval), w=w)
        })

        return metrics