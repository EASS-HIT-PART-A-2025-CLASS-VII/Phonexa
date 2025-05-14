from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.LLMFeedback import analyze_pronunciation_with_llm
from app.services.GenerateFirstSentence import generate_first_sentence
from app.services.GenerateAdvancedSentence import generate_advanced_sentence


router = APIRouter()

class AlignmentResultsRequest(BaseModel):
    alignment_results: dict

class AdvancedSentenceRequest(BaseModel):
    previous_sentence: str
    feedback: str

@router.get("/")
async def read_root():
    return {"message": "Welcome to the LLMTeacher API"}

@router.get("/health")
async def health_check():
    return {"status": "healthy"}

@router.post("/analyze-pronunciation")
async def analyze_pronunciation(request: AlignmentResultsRequest):
    try:
        result = analyze_pronunciation_with_llm(request.alignment_results)
        return result
    except Exception as e:
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
        result = generate_advanced_sentence(
            request.previous_sentence,
            request.feedback
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))