"""Configuration settings for the application"""
import os
from typing import Optional, Union
from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "SPC Web App"
    VERSION: str = "1.0.0"
    
    # CORS Settings
    BACKEND_CORS_ORIGINS: Union[str, list[str]] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]
    
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Union[str, list[str]]) -> list[str]:
        if isinstance(v, str):
            # Parse comma-separated string
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v
    
    # Google OAuth Settings
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URI: Optional[str] = None
    
    # JWT Settings
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Google Sheets Settings
    GOOGLE_SHEETS_CREDENTIALS_PATH: str = os.getenv(
        "GOOGLE_SHEETS_CREDENTIALS_PATH", 
        "../credentials.json"
    )
    GOOGLE_SHEETS_ID: str = os.getenv(
        "GOOGLE_SHEETS_ID",
        "17yR3BJzslf4HLMGTDc0OvzRaY3t7VAZ1-CGx5GxQM_Q"
    )
    GOOGLE_SHEETS_SCOPES: list[str] = ["https://www.googleapis.com/auth/spreadsheets"]
    
    # Redis Settings (optional)
    REDIS_URL: Optional[str] = os.getenv("REDIS_URL", None)
    CACHE_TTL_SECONDS: int = 300  # 5 minutes
    
    # Frontend URL
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

