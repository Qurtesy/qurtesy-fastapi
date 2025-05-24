from fastapi import APIRouter

router = APIRouter()


@router.get("/config/category")
async def config_category():
    return None
