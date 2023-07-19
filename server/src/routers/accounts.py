from schema import Account
from database import engine
from fastapi import APIRouter
from sqlmodel import Session, select

import sys
sys.path.insert(0, '..')

router = APIRouter(
    prefix="/accounts",
    tags=["accounts"]
)


@router.get("/")
async def get_accounts():
    with Session(engine) as session:
        results = session.exec(
            select(Account)
        ).all()
    return results
