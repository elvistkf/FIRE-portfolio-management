import pandas as pd
import numpy as np
from sqlmodel import Session, select
from .utils import is_matching_index, normalize

from exceptions import MismatchedIndexException
from database import engine
from schema import Transaction


class Portfolio:
    def __init__(self, details: pd.DataFrame | pd.Series | None = None) -> None:
        """Initialize the Portfolio object with either transaction history or shares/weights distribution.

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
            pass
        elif details is None:
            self.transactions = self.retrieve_transactions().astype({"amount": "float64", "shares": "float64"})
        else:
            raise TypeError(f"Expected input details to be a DataFrame or a Series, instead found {type(details)}.")

    def get_holdings(self) -> pd.DataFrame:
        """Calculate and return the holdings summary of the portfolio

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
            return self.holdings

    def get_weights(self, account: int | None = None) -> pd.Series:
        """Calculate and return the weights of each ticker of the portfolio by account

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

    def retrieve_transactions(self) -> pd.DataFrame:
        """Retrieve transaction history from the database

        Returns:
            pd.DataFrame: Transaction history from the database in pandas DataFrame
        """
        with Session(engine) as session:
            statement = select(Transaction)
            results = session.exec(statement).all()
        return pd.DataFrame([t.dict() for t in results])
