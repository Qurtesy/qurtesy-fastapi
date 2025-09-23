import spacy
import re
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from spacy.lang.en.examples import sentences

router = APIRouter()

nlp = spacy.load("en_core_web_trf")

def parse_transaction(text: str):
    print(sentences[0])
    doc = nlp(text)
    print(doc.ents)

    # Extract amount
    amount_match = re.search(r"\d+(?:\.\d{1,2})?", text)
    amount = float(amount_match.group()) if amount_match else None

    # Intent classification (basic rule-based)
    lower_text = text.lower()
    if "spent" in lower_text or "bought" in lower_text:
        tx_type = "Expense"
    elif "sent" in lower_text or "transfer" in lower_text:
        tx_type = "Transfer"
    elif "gave" in lower_text or "lend" in lower_text:
        tx_type = "Lend"
    else:
        tx_type = "Other"

    # Extract entities
    entities = [{"text": ent.text, "label": ent.label_} for ent in doc.ents]

    return {
        "transaction_type": tx_type,
        "amount": amount,
        "entities": entities
    }


class TransactionRequest(BaseModel):
    text: str

@router.post("/parse")
async def create_split_transaction(request: TransactionRequest):
    try:
        result = parse_transaction(request.text)
        return {
            "input": request.text,
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse transaction: {str(e)}")
