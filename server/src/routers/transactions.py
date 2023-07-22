from schema import Transaction
from database import engine
from fastapi import APIRouter
from sqlmodel import Session, select


router = APIRouter(
    prefix="/transactions",
    tags=["transactions"]
)


@router.get("/")
async def get_transactions():
    with Session(engine) as session:
        results = session.exec(
            select(Transaction)
        ).all()
    return results


@router.get("/ticker/{ticker}")
async def get_transactions_by_ticker(ticker: str):
    with Session(engine) as session:
        results = session.exec(
            select(Transaction).where(Transaction.ticker == ticker)
        ).all()
    return results
