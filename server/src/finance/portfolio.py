import pandas as pd
import numpy as np
from typing import List, Dict
from datetime import datetime
from sqlmodel import Session, select
from .utils import is_matching_index, normalize, interval_to_periods_per_year
from .data_fetcher import get_tickers
from .financial_models import expected_return, volatility, sharpe_ratio, var_historic, cvar_historic, annualized_sharpe_ratio
from .optimization import efficient_frontier

from exceptions import MismatchedIndexException
from database import engine
from schema import Transaction, Account


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
            self.retrieve_transactions()
        else:
            raise TypeError(f"Expected input details to be a DataFrame or a Series, instead found {type(details)}.")

    def retrieve_transactions(self):
        """
        Retrieve transaction history from the database

        Returns:
            pd.DataFrame: Transaction history from the database in pandas DataFrame
        """
        with Session(engine) as session:
            trans_statement = select(Transaction)
            trans_results = session.exec(trans_statement).all()
            acct_statement = select(Account)
            acct_results = session.exec(acct_statement).all()
        self.transactions = pd.DataFrame([t.dict() for t in trans_results]).astype({"amount": "float64", "shares": "float64"})
        self.accounts = pd.DataFrame([a.dict() for a in acct_results])

    def get_accounts(self) -> pd.DataFrame:
        """
        Retrieve the details of accounts for the portfolio

        Returns:
            pd.DataFrame: Details of accounts for the portfolio in DataFrame, including name, description and account id
        """
        return self.accounts

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
            holdings[rounding_columns] = holdings[rounding_columns].round(2)

            self.holdings = holdings[["total_shares", "book_value", "avg_cost", "realized_gain", "total_cost"]] \
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

    def get_ticker_list(self) -> List[str]:
        return self.get_holdings().reset_index()["ticker"].drop_duplicates().to_list()
    
    def get_basic_statistics(
            self, 
            start: (datetime | str) = "2018-01-01",
            end: (datetime | str | None) = None,
            period: (str | None) = None,
            interval: str = "1d"
        ) -> Dict[str, pd.Series | pd.DataFrame]:
        ticker_list = self.get_ticker_list()
        tickers: pd.DataFrame = get_tickers(ticker_list, start=start, end=end, period=period, interval=interval)
        returns = tickers.pct_change().dropna()

        er = returns.mean()
        cov = returns.cov()

        return {
            "returns": returns,
            "expected_return": er,
            "covariance": cov
        }


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
        ticker_list = self.get_ticker_list()
        tickers: pd.DataFrame = get_tickers(ticker_list, start=start, end=end, period=period, interval=interval)
        returns = tickers.pct_change().dropna()
        
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
        # ticker_list = self.get_ticker_list()
        # tickers: pd.DataFrame = get_tickers(ticker_list, start=start, end=end, period=period, interval=interval)
        # returns = tickers.pct_change().dropna()

        w = self.get_weights()
        stat = self.get_basic_statistics(start, end, period, interval)
        returns = stat["returns"]
        er = stat["expected_return"]
        cov = stat["covariance"]
        
        metrics = pd.Series({
            "expected_return": expected_return(w=w, er=er),
            "volatility": volatility(w=w, cov=cov),
            "sharpe_ratio": sharpe_ratio(w=w, er=er, cov=cov, rf=0.0001),
            "value_at_risk": var_historic(r=returns, w=w),
            "conditional_value_at_risk": cvar_historic(r=returns, w=w),
            "annualized_sharpe_ratio": annualized_sharpe_ratio(returns, rf=0, periods_per_year=interval_to_periods_per_year(interval), w=w)
        })

        return metrics
    
    def get_account_summary(self) -> pd.DataFrame:
        """
        Calculate and return a summary of account holdings and performance.

        This function retrieves account holdings and transactions data for the current instance,
        then computes various metrics related to the holdings' market values, gains, and cash flow.
        The resulting summary DataFrame includes the following columns:
        
        - 'account': The unique account identifier.
        - 'book_value': The book value of all stocks in the account.
        - 'stock_market_value': The total market value of all stocks in the account.
        - 'total_market_value': The sum of cash and stock market value, representing the overall account value.
        - 'unrealized_gain': The unrealized gain/loss (difference between market value and book value).
        - 'unrealized_gain_pct': The percentage of unrealized gain/loss relative to the book value.
        - 'cash': The remaining cash balance in the account.

        Returns:
            pd.DataFrame: A DataFrame containing the account summary with the mentioned columns.
        """
        holdings = self.get_holdings().copy()
        transactions = self.transactions.copy()[["account", "action", "amount"]]
        ticker_list = holdings.reset_index()["ticker"].drop_duplicates().to_list()
        tickers = get_tickers(ticker_list)
        prices = tickers.iloc[-1]
        prices.index.name = "ticker"
        holdings["stock_market_value"] = holdings["total_shares"] * prices
        holdings["unrealized_gain"] = holdings["stock_market_value"] - holdings["book_value"]
        
        holdings = holdings.reset_index().groupby("account").sum()
        holdings["unrealized_gain_pct"] = 100 * holdings["unrealized_gain"] / holdings["book_value"]
    
        transactions["cash_flow"] = transactions["action"].map({"Deposit": 1, "Sell": 1, "Buy": -1, "Withdrawl": -1}) * transactions["amount"]
        holdings["cash"] = transactions.groupby("account").sum()["cash_flow"]
        holdings["total_market_value"] = holdings["cash"] + holdings["stock_market_value"]

        # round the necessary columns after processing
        rounding_columns = ["unrealized_gain_pct", "stock_market_value", "total_market_value", "unrealized_gain", "book_value"]
        holdings[rounding_columns] = holdings[rounding_columns].round(2)

        holdings = holdings.drop(["ticker", "total_shares", "avg_cost"], axis=1)
        return holdings
    
    def get_efficient_frontier(self,
            start: (datetime | str) = "2018-01-01",
            end: (datetime | str | None) = None,
            period: (str | None) = None,
            interval: str = "1d"
        ) -> pd.DataFrame:
        """
        Calculate and return the Efficient Frontier based on the stocks in the current portfolio.

        The Efficient Frontier represents a set of optimal portfolios that offer the highest expected return
        for a given level of risk (standard deviation). This function calculates the Efficient Frontier using
        historical price data for the assets in the portfolio.

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
            pd.DataFrame: A DataFrame representing the Efficient Frontier. The DataFrame has two columns:
            'Returns': The expected returns for the portfolios on the Efficient Frontier.
            'Volatility': The corresponding standard deviation (volatility) for each portfolio.
        """

        stat = self.get_basic_statistics(start, end, period, interval)
        er = stat["expected_return"]
        cov = stat["covariance"]

        return efficient_frontier(er=er, cov=cov, n_points=100)