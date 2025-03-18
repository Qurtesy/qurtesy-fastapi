from fastapi import APIRouter

router = APIRouter()


@router.get("/accounts/", tags=["accounts"])
async def read_accounts():
    return [
        {"name": "Accounts"},
        {"name": "Cash"},
        {"name": "Card"}
    ]


@router.get("/accounts/{id}", tags=["accounts"])
async def read_account():
    return {"name": "Accounts"}


@router.post("/accounts/", tags=["accounts"])
async def create_account(name: str):
    return {"name": name}