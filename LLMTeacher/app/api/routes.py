from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.LLMFeedback import analyze_pronunciation_with_llm
from app.services.GenerateFirstSentence import generate_first_sentence
from app.services.GenerateAdvancedSentence import generate_advanced_sentence
from typing import List, Union


router = APIRouter()

class AlignmentResultsRequest(BaseModel):
    alignment_results: dict

class AdvancedSentenceRequest(BaseModel):
    previous_sentence: str
    feedback: object

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