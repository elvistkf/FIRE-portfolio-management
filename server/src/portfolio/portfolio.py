from schema import Transaction
from database import engine
import pandas as pd
from sqlmodel import Session, select
from .common import is_matching_index

import sys
sys.path.insert(0, '..')


class Portfolio:
    def __init__(self, details: pd.DataFrame | pd.Series | None = None) -> None:
        """Initialize the Portfolio object with either transaction history or shares/weights distribution.

        Args:
            details (pd.DataFrame | pd.Series | None, optional): Transaction history or shares/weights distribution for the portfolio.
            If None is passed as the argument, the transaction history from the database will be automatically retrieved. Defaults to None.
        """

        if isinstance(details, pd.DataFrame):
            if not is_matching_index(details.columns, Transaction.get_fields()):
                raise AttributeError(
                    "Expected matching columns from transaction details with table schema."
                )
            self.transactions = details
        elif isinstance(details, pd.Series):
            self.distribution = details
        else:
            raise TypeError(
                f"Expected input details to be a DataFrame or a Series, instead found {type(details)}.")

    def get_weights(self) -> pd.Series:
        return 0

    def get_transactions(self) -> pd.DataFrame:
        """Retrieve transaction history from the database

        Returns:
            pd.DataFrame: Transaction history from the database in pandas DataFrame
        """
        with Session(engine) as session:
            statement = select(Transaction)
            results = session.exec(statement).all()
        return pd.DataFrame(results)
