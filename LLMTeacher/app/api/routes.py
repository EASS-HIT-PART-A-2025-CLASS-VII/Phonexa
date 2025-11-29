from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
import traceback
from app.services.LLMFeedback import analyze_pronunciation_with_llm
from app.services.GenerateFirstSentence import generate_first_sentence
from app.services.GenerateAdvancedSentence import generate_advanced_sentence
from app.services.PhonemeTTS import generate_phoneme_audio_bytes


router = APIRouter()

class AlignmentResultsRequest(BaseModel):
    alignment_results: dict

class AdvancedSentenceRequest(BaseModel):
    previous_sentence: str
    feedback: object

class PhonemeTTSRequest(BaseModel):
    phonetic_word: str

@router.get("/")
async def read_root():
    return {"message": "Welcome to the LLMTeacher API"}

@router.get("/health")
async def health_check():
    return {"status": "healthy"}

@router.post("/analyze-pronunciation")
async def analyze_pronunciation(request: AlignmentResultsRequest):
    try:
        print(f"\n{'='*50}")
        print(f"[ANALYZE-PRONUNCIATION] Received request")
        print(f"[ANALYZE-PRONUNCIATION] Alignment results: {request.alignment_results}")
        print(f"{'='*50}\n")
        
        result = analyze_pronunciation_with_llm(request.alignment_results)
        
        print(f"\n{'='*50}")
        print(f"[ANALYZE-PRONUNCIATION] LLM Result: {result}")
        print(f"{'='*50}\n")
        
        return result
    except Exception as e:
        print(f"\n[ANALYZE-PRONUNCIATION] ERROR: {str(e)}")
        print(f"[ANALYZE-PRONUNCIATION] TRACEBACK: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/generate-first-sentence")
async def generate_first_sentence_route():
    try:
        result = generate_first_sentence()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/generate-advanced-sentence")
async def generate_advanced_sentence_route(request: AdvancedSentenceRequest):
    try:
        print(f"Received request: {request}")  # Debug line
        
        # Convert feedback to string if it's a list
        feedback = request.feedback
        if isinstance(feedback, list):
            feedback = "; ".join([str(item) for item in feedback])
            
        result = generate_advanced_sentence(
            request.previous_sentence,
            feedback
        )
        return result
    except Exception as e:
        print(f"Error processing request: {e}")  # Debug line
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-phoneme-audio")
async def generate_phoneme_audio_route(request: PhonemeTTSRequest):
    try:
        # Log the incoming request
        print(f"Processing phoneme request for: {request.phonetic_word}")
        
        # Generate the phoneme audio bytes
        audio_data = await generate_phoneme_audio_bytes(request.phonetic_word)
        
        # Log success
        print(f"Successfully generated audio data: {len(audio_data)} bytes")
        
        # Return the audio data as a streamable response
        return Response(
            content=audio_data,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": f"attachment; filename=phoneme.mp3"
            }
        )
        
    except Exception as e:
        # Print the full stack trace for debugging
        print(f"PHONEME TTS ERROR: {str(e)}")
        print(f"FULL TRACEBACK: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to generate phoneme audio: {str(e)}")