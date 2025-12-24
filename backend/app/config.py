import os
from typing import Optional, Union
from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Aplikacija za praćenje članstva"
    VERSION: str = "1.0.0"
    
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
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v
    
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URI: Optional[str] = None
    
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
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
        "https://www.googleapis.com/auth/admin.directory.group.readonly"
    ]
    
    GOOGLE_GROUP_EMAIL: str = os.getenv("GOOGLE_GROUP_EMAIL", "opsta@best.rs")
    GOOGLE_ADMIN_EMAIL: Optional[str] = os.getenv("GOOGLE_ADMIN_EMAIL", None)
    
    REDIS_URL: Optional[str] = os.getenv("REDIS_URL", None)
    CACHE_TTL_SECONDS: int = 300
    
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")
    
    ALLOWED_WRITE_EMAILS: list[str] = [
        "hr@best.rs",
        "vpp@best.rs",
        "secretary@best.rs",
        "fr@best.rs",
        "president@best.rs",
        "pr@best.rs",
        "treasurer@best.rs",
    ]
    
    ALLOWED_VIEW_EMAILS: list[str] = []
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

