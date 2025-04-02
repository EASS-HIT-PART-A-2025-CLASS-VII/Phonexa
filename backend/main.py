from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allow requests from the frontend
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Endpoint to handle audio and sentence analysis
@app.post("/analysis")
async def analyze_audio(
    sentence: str = Form(...),
    audio: UploadFile = File(...)
):
    try:
        # Save the uploaded audio file temporarily
        audio_path = f"temp_{audio.filename}"
        with open(audio_path, "wb") as f:
            f.write(await audio.read())

        # Placeholder for analysis logic (to be implemented later)
        # For now, return a mock response
        score = 85  # Mock score
        feedback = "Work on Clarity"  # Mock feedback

        # Clean up the temporary file
        os.remove(audio_path)

        # Return the analysis result
        return JSONResponse(
            content={
                "score": score,
                "feedback": feedback
            },
            status_code=200
        )
    except Exception as e:
        return JSONResponse(
            content={"error": str(e)},
            status_code=500
        )