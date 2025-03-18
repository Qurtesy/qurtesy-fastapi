from fastapi import APIRouter

router = APIRouter()


@router.get("/categories/", tags=["categories"])
async def read_categories():
    return [
        {
            "name": "Payments",
            "emoji": 128184
        },
        {
            "name": "Food",
            "emoji": 127828
        },
        {
            "name": "Transport",
            "emoji": 128640
        }
    ]
