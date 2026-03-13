import os
from typing import Optional
from supabase import create_client, Client
from functools import lru_cache

class Config:
    """Application configuration."""
    
    # Database
    SUPABASE_URL = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
    
    # JWT
    JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRATION_HOURS = 24
    
    # Storage
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./data/uploads")
    MAX_FILE_SIZE_MB = 100
    ALLOWED_EXTENSIONS = {"csv", "xlsx", "xls"}
    
    # S3 Configuration (for production)
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET", "")
    AWS_S3_REGION = os.getenv("AWS_S3_REGION", "us-east-1")
    
    # Environment
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    USE_S3 = ENVIRONMENT == "production" and bool(AWS_S3_BUCKET)
    
    # CORS
    CORS_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ]
    
    # API
    API_PREFIX = "/api"
    API_V1_PREFIX = "/api/v1"

@lru_cache()
def get_config():
    """Get configuration singleton."""
    return Config()

@lru_cache()
def get_supabase_client() -> Client:
    """Get Supabase client singleton."""
    config = get_config()
    if not config.SUPABASE_URL or not config.SUPABASE_KEY:
        raise ValueError("Supabase credentials not configured")
    return create_client(config.SUPABASE_URL, config.SUPABASE_KEY)

def get_db():
    """Dependency for FastAPI to get database client."""
    return get_supabase_client()
