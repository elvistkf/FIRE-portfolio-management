import numpy as np
import pandas as pd
from sqlmodel import Session, select, func
from .common import *

import sys
sys.path.insert(0, '..')
from database import engine
from schema import Transaction


class Portfolio:
    def __init__(self, details: pd.DataFrame | pd.Series | None = None) -> None:
        """Initialize the Portfolio object with either transaction history or shares/weights distribution.

        Args:
            details (pd.DataFrame | pd.Series | None, optional): Provided details for the portfolio, could be transaction history or shares/weights distribution. If None is passed as the argument, the transaction history from the database will be automatically retrieved. Defaults to None.
        """

        if isinstance(details, pd.DataFrame):
            if not is_matching_index(details.columns, Transaction.get_fields()):
                raise AttributeError("Expected matching columns from transaction details with table schema.")
        elif isinstance(details, pd.Series):
            pass
        else:
            raise TypeError(f"Expected input details to be a DataFrame or a Series, instead found {type(details)}.")
        
    
    def get_transactions(self) -> pd.DataFrame:
        """Retrieve transaction history from the database

        Returns:
            pd.DataFrame: Transaction history from the database in pandas DataFrame
        """
        with Session(engine) as session:
            statement = select(Transaction)
            results = session.exec(statement).all()
        return pd.DataFrame(results)