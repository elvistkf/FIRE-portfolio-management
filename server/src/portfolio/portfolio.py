import pandas as pd
from sqlmodel import Session, select, func

import sys
sys.path.insert(0, '..')
from database import engine
from schema import Transaction

class Portfolio:
    def __init__(self, details: pd.DataFrame = None) -> None:
        """Initialize the object with either transaction history or shares distribution.

        Args:
            details (pd.DataFrame, optional): Provided details for the portfolio, could be transaction history or shares distribution. If None is passed as the argument, the transaction history from the database will be automatically retrieved. Defaults to None.
        """
        if "shares" not in details.columns:
            raise ValueError("Expected column \"shares\" in the provided DataFrame.")        
        
    
    def get_transactions(self) -> pd.DataFrame:
        """Retrieve transaction history from the database

        Returns:
            pd.DataFrame: Transaction history from the database in pandas DataFrame
        """
        with Session(engine) as session:
            statement = select(Transaction)
            results = session.exec(statement).all()
        return pd.DataFrame(results)

df = pd.DataFrame()