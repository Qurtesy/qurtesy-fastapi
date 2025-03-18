from typing import Union

from fastapi import FastAPI
from app.routers import accounts, categories, transactions
from app.internal import admin

app = FastAPI()


app.include_router(accounts.router)
app.include_router(categories.router)
app.include_router(transactions.router)

@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}
