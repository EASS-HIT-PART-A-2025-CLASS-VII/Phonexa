from pydantic import BaseSettings

class Settings(BaseSettings):
    llm_api_key: str

    class Config:
        env_file = ".env"

settings = Settings()