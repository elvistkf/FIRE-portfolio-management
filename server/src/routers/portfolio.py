from fastapi import APIRouter
import json
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
