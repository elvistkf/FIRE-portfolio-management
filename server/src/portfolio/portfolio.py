import sys
import pandas as pd
import numpy as np
from sqlmodel import Session, select
from .utils import is_matching_index

sys.path.insert(0, "..")
from schema import Transaction
from database import engine


class Portfolio:
    def __init__(self, details: pd.DataFrame | pd.Series | None = None) -> None:
        """Initialize the Portfolio object with either transaction history or shares/weights distribution.

        Args:
            details (pd.DataFrame | pd.Series | None, optional): Transaction history or shares/weights distribution for the portfolio.
            If None is passed as the argument, the transaction history from the database will be automatically retrieved. Defaults to None.
        """

        if isinstance(details, pd.DataFrame):
            if not is_matching_index(details.columns, Transaction.get_fields()):
                print(details)
                print(details.columns, Transaction.get_fields())
                raise AttributeError("Expected matching columns from transaction details with table schema.")

            # Cast the decimal columns to float64
            self.transactions = details.astype({"amount": "float64", "shares": "float64"})
        elif isinstance(details, pd.Series):
            pass
        elif details is None:
            self.transactions = self.retrieve_transactions()
        else:
            raise TypeError(f"Expected input details to be a DataFrame or a Series, instead found {type(details)}.")

    def get_holdings(self) -> pd.DataFrame:
        try:
            return self.holdings
        except AttributeError:
            df = self.transactions[["account", "action", "ticker", "amount", "shares"]].copy()
            df["buy"] = df["action"].map({"Buy": 1, "Sell": 0}) * df["shares"]
            df["sell"] = df["action"].map({"Buy": 0, "Sell": 1}) * df["shares"]
            df["net"] = df["buy"] - df["sell"]
            df["total_cost"] = df["buy"] * df["amount"]


            holdings = df.groupby(["account", "ticker"]).agg(
                total_buy=pd.NamedAgg(column="buy", aggfunc=np.sum),
                total_cost=pd.NamedAgg(column="total_cost", aggfunc=np.sum),
                total_shares=pd.NamedAgg(column="net", aggfunc=np.sum)
            )
            holdings["book_value"] = (holdings["total_cost"] * holdings["total_shares"] / holdings["total_buy"]).apply(lambda x: round(x, 2))
            holdings["avg_cost"] = (holdings["book_value"] / holdings["total_shares"]).apply(lambda x: round(x, 2))
            self.holdings = holdings[["total_shares", "book_value", "avg_cost"]]
            return self.holdings

    def get_weights(self) -> pd.Series:
        return 0

    def retrieve_transactions(self) -> pd.DataFrame:
        """Retrieve transaction history from the database

        Returns:
            pd.DataFrame: Transaction history from the database in pandas DataFrame
        """
        with Session(engine) as session:
            statement = select(Transaction)
            results = session.exec(statement).all()
        return pd.DataFrame(results)
