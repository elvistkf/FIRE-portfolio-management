from typing import Optional
from datetime import datetime
from pydantic import condecimal
from sqlmodel import Field, SQLModel

class Transaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    date: datetime = Field(nullable=False)
    account: int = Field(default=None, nullable=False)
    ticker: str = Field(max_length=10, nullable=False)
    price: condecimal(max_digits=10, decimal_places=3) = Field(nullable=False)
    quantity: condecimal(max_digits=10, decimal_places=3) = Field(nullable=False)

class Account(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100, nullable=False)
    description: str = Field(max_length=200)