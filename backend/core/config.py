from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from pathlib import Path


class Settings(BaseSettings):
    """Application settings."""
    
    # Basic settings
    APP_NAME: str = "AeonAgent"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Supabase Database
    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str
    SUPABASE_SERVICE_KEY: str
    DATABASE_URL: Optional[str] = None  # Keep for backward compatibility
    DATABASE_TEST_URL: Optional[str] = None
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Qdrant Vector Database
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: Optional[str] = None
    
    # AI Models
    OPENAI_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    
    # Supabase Authentication
    SUPABASE_JWT_SECRET: str
    
    # Auth0 (Alternative - kept for reference)
    AUTH0_DOMAIN: Optional[str] = None
    AUTH0_CLIENT_ID: Optional[str] = None
    AUTH0_CLIENT_SECRET: Optional[str] = None
    
    # Stripe
    STRIPE_PUBLISHABLE_KEY: Optional[str] = None
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    
    # Monitoring
    SENTRY_DSN: Optional[str] = None
    PROMETHEUS_PORT: int = 8001
    
    # CORS
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # File Upload
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: str = "50MB"
    
    # Agent Configuration
    DEFAULT_AGENT_TIMEOUT: int = 300  # 5 minutes
    MAX_CONCURRENT_AGENTS: int = 10
    
    # Trial Limits
    DEFAULT_TRIAL_DAYS: int = 14
    DEFAULT_TRIAL_QUERIES: int = 100
    DEFAULT_TRIAL_UPLOAD_MB: int = 10
    
    class Config:
        env_file = ".env"
        case_sensitive = True


    @property
    def database_url(self) -> str:
        """Get database URL - prioritize Supabase URL if available."""
        if self.SUPABASE_URL:
            # Convert Supabase URL to PostgreSQL connection string
            return self.SUPABASE_URL.replace('https://', 'postgresql://postgres:[YOUR-PASSWORD]@').replace('.supabase.co', '.supabase.co:5432') + '/postgres'
        return self.DATABASE_URL

# Create global settings instance
settings = Settings()

# Ensure upload directory exists
upload_path = Path(settings.UPLOAD_DIR)
upload_path.mkdir(exist_ok=True)
