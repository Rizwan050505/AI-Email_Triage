import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "AI Email Triage System"
    DATABASE_URL: str = "sqlite:///./backend/database/email_triage.db"
    MODEL_PATH: str = "backend/models/classifier.pkl"
    VECTORIZER_PATH: str = "backend/models/vectorizer.pkl"
    DATASET_PATH: str = "data/dataset.json"

    class Config:
        env_file = ".env"

settings = Settings()
