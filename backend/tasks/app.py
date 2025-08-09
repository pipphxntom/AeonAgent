"""Celery application initialization.

Run a worker with:
    celery -A tasks.app.celery_app worker -l info
"""
from celery import Celery
import os

# Basic configuration from environment (already present in settings / .env)
BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", BROKER_URL)

celery_app = Celery(
    "aeonagent",
    broker=BROKER_URL,
    backend=RESULT_BACKEND,
    include=["tasks.health"],
)

# Minimal config; can be extended later
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)
