from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import JSONResponse
from services.wav2vec_service import convert_audio_file
from services.LLMAnalysis import analyze_pronunciation_with_llm

router = APIRouter()

@router.post("/")
async def analyze_audio(
    sentence: str = Form(...),
    audio: UploadFile = File(...)
):
    try:
        # Step 1: Call the wav2vec service to get the phoneme transcription
        phoneme_result = await convert_audio_file(audio)
        phoneme_text = phoneme_result["phonemes"]

        # Step 2: Call the LLM analysis service
        llm_response = analyze_pronunciation_with_llm(sentence, phoneme_text)
        print("LLM Response:", llm_response)


        # Return the response from the LLM
        return llm_response
    except Exception as e:
        # Handle errors and return a JSON response with the error message
        return JSONResponse(status_code=500, content={"error": str(e)})