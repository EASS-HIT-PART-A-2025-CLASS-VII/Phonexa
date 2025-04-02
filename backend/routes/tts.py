from fastapi import APIRouter, Form
from fastapi.responses import FileResponse, JSONResponse
from services.tts_service import generate_tts_audio
from pydantic import BaseModel
router = APIRouter()


class SentenceRequest(BaseModel):
    sentence: str

@router.post("/")
async def tts(request: SentenceRequest):
    try:
        audio_path = await generate_tts_audio(request.sentence)
        return FileResponse(audio_path, media_type="audio/wav", filename="output.wav")
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)