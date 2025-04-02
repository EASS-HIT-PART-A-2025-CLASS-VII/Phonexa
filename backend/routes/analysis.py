from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import JSONResponse
from services.analysis_service import analyze_audio_file

router = APIRouter()

@router.post("/")
async def analyze_audio(
    sentence: str = Form(...),
    audio: UploadFile = File(...)
):
    try:
        result = await analyze_audio_file(sentence, audio)
        return JSONResponse(content=result, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)