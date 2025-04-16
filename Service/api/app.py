# app.py
from fastapi import FastAPI, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from model.speech_model import SpeechRecognitionModel
from model.rag_insurance_model import InsuranceModel
from api.schemas import TranscriptionRequest, TranscriptionResponse
from typing import Optional
import io
from fastapi import APIRouter,Depends

router = APIRouter(
    prefix="/insurance",
    tags=["insurance"],
)


# Initialize model
model = SpeechRecognitionModel()
insurance_model = InsuranceModel()


@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(
    file: UploadFile,
    classification: str = Form("general")  # Make sure to use Form()
):
    try:
        content = await file.read()
        print("Received Classification",classification)
        
        # Check content type to determine if it's text or audio
        if file.content_type.startswith('text/'):
            question = content.decode('utf-8')
            print(f"Received text input: {question}")
        else:
            # Assume it's audio
            question = model.transcribe(content)
            print(f"Received audio input, transcribed to: {question}")
        
        answer = insurance_model.transcribe(question)
        
        return TranscriptionResponse(
            question=question,
            answer=answer,
            success=True
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error processing input: {str(e)}"
        )

@router.get("/health")
async def health_check():
    return {"status": "healthy"}