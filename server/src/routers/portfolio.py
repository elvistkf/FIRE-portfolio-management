# from database import engine
from fastapi import APIRouter
# from sqlmodel import Session, select
# from schema import Account
import json
# import pandas as pd
import finance.portfolio as p


router = APIRouter(
    prefix="/portfolio",
    tags=["portfolio"]
)


@router.get("/")
async def get_holdings():
    portfolio = p.Portfolio()
    holdings = portfolio.get_holdings().reset_index().to_json(orient="records")
    return json.loads(holdings)


@router.get("/summary")
async def get_account_summary():
    portfolio = p.Portfolio()
    summary = portfolio.get_account_summary()
    accounts = portfolio.get_accounts().set_index("id")
    accounts.index.name = "account"
    results = accounts.join(summary)
    return json.loads(results.reset_index().to_json(orient="records"))

@router.get("/efficient_frontier")
async def get_efficient_frontier():
    portfolio = p.Portfolio()
    efficient_frontier = portfolio.get_efficient_frontier()[["risk", "return"]]
    efficient_frontier.columns = ["x", "y"]
    return json.loads(efficient_frontier.to_json(orient="records"))