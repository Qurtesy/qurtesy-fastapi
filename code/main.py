from fastapi import FastAPI
from code.routers import accounts, categories, transactions
from code.internal import admin

app = FastAPI()


app.include_router(accounts.router)
app.include_router(categories.router)
app.include_router(transactions.router)

@app.get("/")
async def root():
    return {"message": "Hello, welcome to finance by Qurtesy!"}
