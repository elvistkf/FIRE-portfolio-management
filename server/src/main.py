from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import accounts, transactions, portfolio
import database as db

db.create_tables()
app = FastAPI()
app.include_router(accounts.router)
app.include_router(transactions.router)
app.include_router(portfolio.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Hello World!!!"}
