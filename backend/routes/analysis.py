from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import JSONResponse
from services.wav2vec_service import convert_audio_file
import os
import json
import requests

router = APIRouter()


@router.post("/")
async def analyze_audio(
    sentence: str = Form(...),
    sentenceIPA: str = Form(...),
    audio: UploadFile = File(...),
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

        # Analyze pronunciation with LLM via LLMTeacher microservice
        try:
            response = requests.post(
                "http://llmteacher:5000/analyze-pronunciation",
                json={"alignment_results": wav2vec_result},
                timeout=30
            )
            response.raise_for_status()
            llm_feedback = response.json()
        except Exception as e:
            print("Error communicating with LLMTeacher:", e)
            llm_feedback = {"error": "Failed to get feedback from LLMTeacher."}

        # Return a success response
        return JSONResponse(
            llm_feedback,
            status_code=200,
        )
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
