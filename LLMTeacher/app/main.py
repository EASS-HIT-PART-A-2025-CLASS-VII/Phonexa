from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router as api_router
import sys
from app.tests.APIKeysTest import test_env_keys_exist


try:
    test_env_keys_exist()
    print("All required API keys are present.")
except AssertionError as e:
    print(f"Environment variable check failed: {e}")
    sys.exit(1)


app = FastAPI()

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, restrict to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)