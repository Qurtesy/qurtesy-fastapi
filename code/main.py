from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import (
    accounts,
    categories,
    transactions,
    transfers,
    # transcribes
    budgets,
    recurring_transactions,
    splits,
    profiles,
    # transcribes
)
from internal import admin
from database import init_db

app = FastAPI(
    title="Qurtesy Finance API",
    description="Enhanced Finance Tracking API with Budget Management and Analytics",
    version="2.0.0"
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()

origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(accounts.router, prefix="/api", tags=["accounts"])
app.include_router(categories.router, prefix="/api", tags=["categories"])
app.include_router(transactions.router, prefix="/api", tags=["transactions"])
app.include_router(transfers.router, prefix="/api", tags=["transfers"])
app.include_router(budgets.router, prefix="/api", tags=["budgets"])
app.include_router(recurring_transactions.router, prefix="/api", tags=["recurring-transactions"])
app.include_router(splits.router, prefix="/api", tags=["splits"])
app.include_router(profiles.router, prefix="/api", tags=["profiles"])
# app.include_router(transcribes.router, prefix="/api", tags=["transcribes"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to Qurtesy Finance API v2.0!",
        "features": [
            "Enhanced Transaction Management",
            "Budget Tracking",
            "Recurring Transactions",
            "Analytics & Reporting",
            "Advanced Search & Filtering",
            "Bulk Operations"
        ],
        "documentation": "/docs"
    }

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "2.0.0",
        "timestamp": "2025-05-24T00:00:00Z"
    }
