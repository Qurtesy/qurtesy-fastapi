import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from routers import (
    front,
    transaction,
    transfers,
    # transcribes
    budgets,
    recurring_transactions,
    splits,
    lends,
    # transcribes
)
from database import init_db
from routers import account, category, profile

allowed_origin_urls = os.getenv("ALLOWED_ORIGIN_URLS")

app = FastAPI(
    title="Qurtesy Finance API",
    description="Enhanced Finance Tracking API with Budget Management and Analytics",
    version="2.0.0"
)

print("IS PROD: ", os.getenv("PROD"))
# Since Cloudflare handles SSL termination, this ensures
# any redirects use HTTPS
# app.add_middleware(HTTPSRedirectMiddleware)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()

origins = allowed_origin_urls.split(",") if allowed_origin_urls else []

print("ALLOWED_ORIGIN_URLS: ", origins)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(account.router, prefix="/api", tags=["accounts"])
app.include_router(category.router, prefix="/api", tags=["categories"])
app.include_router(transaction.router, prefix="/api", tags=["transactions"])
app.include_router(transfers.router, prefix="/api", tags=["transfers"])
app.include_router(budgets.router, prefix="/api", tags=["budgets"])
app.include_router(recurring_transactions.router, prefix="/api", tags=["recurring-transactions"])
app.include_router(splits.router, prefix="/api", tags=["splits"])
app.include_router(profile.router, prefix="/api", tags=["profiles"])
app.include_router(lends.router, prefix="/api", tags=["lends"])

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "2.0.0",
        "timestamp": "2025-05-24T00:00:00Z"
    }

@app.api_route("/api/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def api_not_found(request: Request, path: str):
    return {
        "message": "API endpoint not found",
        "path": f"/api/{path}",
        "method": request.method,
        "available_endpoints": [
            "/api/health",
            "/api/accounts/*",
            "/api/categories/*",
            "/api/transactions/*",
            "/api/transfers/*",
            "/api/budgets/*",
            "/api/recurring-transactions/*",
            "/api/splits/*",
            "/api/profiles/*",
            "/api/lends/*"
        ]
    }

# Include React frontend router LAST (catch-all)
app.include_router(front.router, tags=["frontend"])