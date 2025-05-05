from fastapi import APIRouter, Body
from fastapi.responses import JSONResponse
from services.translate_service import translate_to_hebrew

router = APIRouter()

@router.post("/")
async def translate(sentence: str = Body(..., embed=True)):
    try:
        hebrew = translate_to_hebrew(sentence)
        return JSONResponse({"translation": hebrew})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)