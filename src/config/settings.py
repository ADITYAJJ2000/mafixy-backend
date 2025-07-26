import os
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost/mafixy"
    
    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Media Storage
    MEDIA_URL: str = "http://localhost:8000/media/"
    MEDIA_PATH: str = "./media/"
    
    # CORS
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:5000"]
    
    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = "your-email@gmail.com"
    SMTP_PASSWORD: str = "your-app-password"
    
    # Premium Features
    PREMIUM_TRIAL_DAYS: int = 7
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
