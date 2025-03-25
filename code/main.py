from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from code.routers import accounts, categories, transactions, transfers
from code.internal import admin

app = FastAPI()

origins = [
    "http://localhost:5173",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(accounts.router)
app.include_router(categories.router)
app.include_router(transactions.router)
app.include_router(transfers.router)

@app.get("/")
async def root():
    return {"message": "Hello, welcome to finance by Qurtesy!"}
