from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import analysis, tts, translate

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allow requests from the frontend
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Include routers
app.include_router(analysis.router, prefix="/analysis", tags=["Analysis"])
app.include_router(tts.router, prefix="/tts", tags=["Text-to-Speech"])
app.include_router(translate.router, prefix="/translate", tags=["Translate"])
