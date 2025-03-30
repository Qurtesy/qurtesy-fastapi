import httpx  # Use async HTTP requests instead of requests
import asyncio
from datetime import date
from typing import Annotated
from fastapi import APIRouter, BackgroundTasks, Depends, File, UploadFile, Query, Body, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from database import get_db
from models import SectionEnum, CategoryGroup, Transaction
from utils.datetime import format_date
from _whisper.transcribe import transcribe_audio_blob

router = APIRouter()

TRANSCRIPTION_CATEGORY = 'Transcription'


async def log_transcribe(blob_data, filename: str):
    print("🔄 Job queued...", flush=True)

    transcript = transcribe_audio_blob(blob_data, filename)
    print(f"✅ Transcript: {transcript}", flush=True)

    url = 'https://qurtesy-finance-default-rtdb.asia-southeast1.firebasedatabase.app/transcribes.json'
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=transcript)
        print(f"✅ Firebase Response: {response.status_code}, {response.text}", flush=True)


@router.post("/transcribes/queue")
async def transcribe_queue(
    file: UploadFile,
    background_tasks: BackgroundTasks
):
    blob_data = await file.read()
    background_tasks.add_task(log_transcribe, blob_data, file.filename)  # ✅ Non-blocking
    return {"message": "✅ Log transcribe job queued!"}


@router.post("/transcribes/")
async def transcribe(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        # Read the blob data
        blob_data = await file.read()
        
        # Call transcribe function
        transcript = transcribe_audio_blob(blob_data, file.filename)

        category_group = (
            db.query(CategoryGroup)
            .filter(CategoryGroup.value == TRANSCRIPTION_CATEGORY)
            .first()
        )
        new_transaction = Transaction(
            date=date.today(),
            credit=False,
            amount=200,
            section=SectionEnum.EXPENSE,
            category_group=category_group.id,
            account_group=1,
            note=transcript
        ).create()
        db.add(new_transaction)
        db.commit()
        if transcript:
            return JSONResponse(content=transcript)
        else:
            return JSONResponse(content={"error": "Failed to transcribe"}, status_code=500)
    
    except Exception as e:
        print(str(e))
        return JSONResponse(content={"error": str(e)}, status_code=500)
    
