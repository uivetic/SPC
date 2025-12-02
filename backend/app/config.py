"""Configuration settings for the application"""
import os
from typing import Optional, Union
from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Aplikacija za praćenje članstva"
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
    GOOGLE_SHEETS_SCOPES: list[str] = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/admin.directory.group.readonly"  # For Google Groups access
    ]
    
    # Google Groups - mailing list for view access
    GOOGLE_GROUP_EMAIL: str = os.getenv("GOOGLE_GROUP_EMAIL", "opsta@best.rs")
    
    # Admin email for domain-wide delegation (usually a super admin email)
    # This is required for Admin Directory API to work with domain-wide delegation
    GOOGLE_ADMIN_EMAIL: Optional[str] = os.getenv("GOOGLE_ADMIN_EMAIL", None)
    
    # Redis Settings (optional)
    REDIS_URL: Optional[str] = os.getenv("REDIS_URL", None)
    CACHE_TTL_SECONDS: int = 300  # 5 minutes
    
    # Frontend URL
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")
    
    # Access Control - Email lists
    ALLOWED_WRITE_EMAILS: list[str] = [
        "hr@best.rs",
        "vpp@best.rs",
        "secretary@best.rs",
        "fr@best.rs",
        "president@best.rs",
        "pr@best.rs",
        "treasurer@best.rs",
    ]
    
    # All users with @best.rs domain can view (or specific list if needed)
    ALLOWED_VIEW_EMAILS: list[str] = []  # Empty means all @best.rs emails can view
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

