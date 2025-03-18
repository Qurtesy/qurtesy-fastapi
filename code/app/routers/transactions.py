from fastapi import APIRouter

router = APIRouter()


@router.get("/transactions/", tags=["transactions"])
async def read_transactions():
    return [
        {"name": "Transactions"},
        {"name": "Cash"},
        {"name": "Card"}
    ]


@router.get("/transactions/{id}", tags=["transactions"])
async def read_transaction():
    return {"name": "Transactions"}


@router.post("/transactions/", tags=["transactions"])
async def create_transaction(name: str):
    return {"name": name}