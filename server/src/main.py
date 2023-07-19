from fastapi import FastAPI

from routers import accounts, transactions, portfolio
import database as db

db.create_tables()
app = FastAPI()
app.include_router(accounts.router)
app.include_router(transactions.router)
app.include_router(portfolio.router)


@app.get("/")
async def root():
    return {"message": "Hello World!!!"}
