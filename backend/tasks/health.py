"""Health / diagnostic tasks."""
from .app import celery_app

@celery_app.task(name="health.ping")
def ping() -> str:
    return "pong"
