import sys
import pandas as pd
from sqlmodel import Session, select
from .common import is_matching_index

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

            # Cast the decimal columns to int64 and float64
            self.transactions = details.astype({"price": "float64", "shares": "int64"})
        elif isinstance(details, pd.Series):
            pass
        elif details is None:
            self.transactions = self.retrieve_transactions()
        else:
            raise TypeError(f"Expected input details to be a DataFrame or a Series, instead found {type(details)}.")

    def get_summary(self) -> pd.DataFrame:
        try:
            return self.summary
        except AttributeError:
            _tmp_df = self.transactions.copy()
            _tmp_df["total_cost"] = _tmp_df["price"] * _tmp_df["shares"]
            _tmp_df["total_shares"] = _tmp_df["shares"]
            self.summary = _tmp_df.groupby(["account", "ticker"]).agg({"total_shares": sum, "total_cost": sum}).sort_index()
            return self.summary

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
