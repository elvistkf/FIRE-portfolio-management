from fastapi import FastAPI
from sqlmodel import Session, select

from routers import accounts, transactions, portfolio
from schema import Transaction
import database as db

db.create_tables()
app = FastAPI()
app.include_router(accounts.router)
app.include_router(transactions.router)
app.include_router(portfolio.router)

@app.get("/")
async def root():
    return {"message": "Hello World!!!"}


