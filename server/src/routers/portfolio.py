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

    ticker_metrics = portfolio.get_tickers_metrics().reset_index()
    ticker_metrics = ticker_metrics[["index", "volatility", "expected_returns"]]
    ticker_metrics.columns = ["ticker", "x", "y"]

    results = {
        "tickers": json.loads(ticker_metrics.to_json(orient="records")),
        "curve": json.loads(efficient_frontier.to_json(orient="records")),
    }
    return results


@router.get("/overall_metrics")
async def get_overall_metrics():
    portfolio = p.Portfolio()
    overall_metrics = portfolio.get_overall_metrics()
    return json.loads(overall_metrics.to_json(orient="index"))


@router.get("/tickers_metrics")
async def get_tickers_metrics():
    portfolio = p.Portfolio()
    tickers_metrics = portfolio.get_tickers_metrics()
    return json.loads(tickers_metrics.reset_index().to_json(orient="records"))