from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from pathlib import Path
from urllib.parse import quote_plus


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
    SUPABASE_DB_PASSWORD: Optional[str] = None
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
    GOOGLE_API_KEY: Optional[str] = None  # Fallback to GEMINI_API_KEY
    
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
        """Return an async SQLAlchemy database URL or raise with setup instructions.

        Resolution order:
        1. Construct from Supabase (SUPABASE_URL + SUPABASE_DB_PASSWORD) using asyncpg
        2. Use provided DATABASE_URL (upgrade to asyncpg driver if plain postgresql://)
        3. Raise RuntimeError with guidance
        """
        # Preferred: derive from Supabase settings
        if self.SUPABASE_URL and self.SUPABASE_DB_PASSWORD:
            host = self.SUPABASE_URL.replace("https://", "").rstrip("/")
            if not host.endswith(".supabase.co"):
                host = f"{host}.supabase.co"
            password = quote_plus(self.SUPABASE_DB_PASSWORD)
            return f"postgresql+asyncpg://postgres:{password}@{host}:5432/postgres"

        # Fallback: explicit DATABASE_URL
        if self.DATABASE_URL:
            url = self.DATABASE_URL
            if url.startswith("postgresql://") and "+asyncpg" not in url:
                url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
            return url

        # Nothing configured -> raise with instructions
        raise RuntimeError(
            "Database configuration missing. Set either (1) SUPABASE_URL and SUPABASE_DB_PASSWORD or (2) DATABASE_URL in backend/.env. "
            "Example Supabase vars: SUPABASE_URL=https://YOUR_REF.supabase.co SUPABASE_DB_PASSWORD=your_db_pass. "
            "Example direct URL: DATABASE_URL=postgresql://user:pass@host:5432/dbname"
        )

    def model_post_init(self, __context):  # pydantic v2 hook
        # Fallback: reuse GEMINI key for Google if GOOGLE_API_KEY unset
        if not self.GOOGLE_API_KEY and self.GEMINI_API_KEY:
            object.__setattr__(self, "GOOGLE_API_KEY", self.GEMINI_API_KEY)

# Create global settings instance
settings = Settings()

# Ensure upload directory exists
upload_path = Path(settings.UPLOAD_DIR)
upload_path.mkdir(exist_ok=True)
