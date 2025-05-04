from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import JSONResponse
from services.wav2vec_service import convert_audio_file
from services.LLMFeedback import analyze_pronunciation_with_llm
import os
import json

router = APIRouter()

@router.post("/")
async def analyze_audio(
    sentence: str = Form(...),
    sentenceIPA: str = Form(...),
    audio: UploadFile = File(...)
):
    try:
        # Save input audio and transcript files
        audio_path = f"temp_{audio.filename}"
        with open(audio_path, "wb") as f:
            f.write(await audio.read())
    

        wav2vec_result = await convert_audio_file(audio_path, sentenceIPA, sentence)        

        wav2vec_output_path = os.path.join("services", "wav2vec_transcription.json")
        with open(wav2vec_output_path, "w") as f:
            json.dump(wav2vec_result, f, indent=4)
            
        print("Wav2Vec Transcription Results:", wav2vec_result)

        




        # Analyze pronunciation with LLM
        llm_feedback = analyze_pronunciation_with_llm(wav2vec_result)
        print("LLM Analysis Results:", llm_feedback)

        # Return a success response
        return JSONResponse(
            llm_feedback,
            status_code=200,
        )
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})