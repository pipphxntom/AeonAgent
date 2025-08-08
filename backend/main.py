from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer
from contextlib import asynccontextmanager
import uvicorn
import logging
from prometheus_client import start_http_server

from core.config import settings
from core.database import init_db
from core.logging import setup_logging
from core.monitoring import setup_monitoring
from api.v1.api import api_router
from api.deps import get_current_user


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    setup_logging()
    setup_monitoring()
    await init_db()
    
    # Start Prometheus metrics server
    if settings.ENVIRONMENT != "test":
        start_http_server(settings.PROMETHEUS_PORT)
    
    logging.info("AeonAgent backend started successfully")
    yield
    
    # Shutdown
    logging.info("AeonAgent backend shutting down")


# Create FastAPI application
app = FastAPI(
    title="AeonAgent API",
    description="SaaS platform for pre-built AI agent applications",
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
    lifespan=lifespan
)

# Security
security = HTTPBearer()

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)

# Routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "AeonAgent API",
        "version": "1.0.0",
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/protected")
async def protected_route(current_user=Depends(get_current_user)):
    """Example protected route."""
    return {"message": f"Hello {current_user.email}"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True if settings.ENVIRONMENT == "development" else False,
        log_level=settings.LOG_LEVEL.lower()
    )
