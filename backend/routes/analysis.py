import asyncio
from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import JSONResponse
from services.gentle_service import align_audio_with_gentle
from services.wav2vec_service import convert_audio_file
from services.LLMFeedback import analyze_pronunciation_with_llm
from services.LLMAlignment import process_phonemes
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
        transcript_path = f"temp_{os.path.splitext(audio.filename)[0]}.txt"
        with open(audio_path, "wb") as f:
            f.write(await audio.read())
        with open(transcript_path, "w") as f:
            f.write(sentence)

        # Run Gentle and Wav2Vec concurrently
        gentle_future = asyncio.to_thread(align_audio_with_gentle, audio_path, transcript_path)
        wav2vec_future = convert_audio_file(audio_path)
        gentle_alignment, wav2vec_result = await asyncio.gather(gentle_future, wav2vec_future)

        # Save Gentle and Wav2Vec results
        gentle_output_path = os.path.join("services", "gentle_alignment.json")
        with open(gentle_output_path, "w") as f:
            json.dump(gentle_alignment, f, indent=4)
        print("Gentle Alignment Results:", gentle_alignment)

        wav2vec_output_path = os.path.join("services", "wav2vec_transcription.json")
        with open(wav2vec_output_path, "w") as f:
            json.dump(wav2vec_result, f, indent=4)
        print("Wav2Vec Transcription Results:", wav2vec_result)

        # Extract phoneme array from Wav2Vec result
        phoneme_array = wav2vec_result.get("phonemes", [])

        # Align phoneme array to original sentence
        alignment_results = process_phonemes(sentence, sentenceIPA, phoneme_array, gentle_alignment)
        print("Alignment Results:", alignment_results)





        # Analyze pronunciation with LLM
        llm_feedback = analyze_pronunciation_with_llm(alignment_results)
        print("LLM Analysis Results:", llm_feedback)

        # Return a success response
        return JSONResponse(
            llm_feedback,
            status_code=200,
        )
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})