from schema import Transaction
from database import engine
from fastapi import APIRouter
from sqlmodel import Session, select, func
import sys
sys.path.insert(0, '..')

router = APIRouter(
    prefix="/portfolio",
    tags=["portfolio"]
)


@router.get("/")
async def get_porfolio():
    with Session(engine) as session:
        statement = select(
            Transaction.account,
            Transaction.ticker,
            func.sum(Transaction.shares).label("total_shares"),
            (func.sum(Transaction.price * Transaction.shares) /
                func.sum(Transaction.shares)).label("average_cost")
        ).group_by(Transaction.account, Transaction.ticker)
        results = session.exec(statement).all()
    return results
