from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from _nlp.parser import parse
from _nlp.train import train

router = APIRouter()


class TransactionRequest(BaseModel):
    text: str

@router.post("/parse")
async def parse_transaction(request: TransactionRequest):
    try:
        result = parse(request.text)
        return {
            "input": request.text,
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse transaction: {str(e)}")


@router.get("/train")
async def train_parser():
    try:
        return train()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to train the parser: {str(e)}")
