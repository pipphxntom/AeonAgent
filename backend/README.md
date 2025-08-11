# AeonAgent Backend

FastAPI backend for the AeonAgent SaaS platform.

## Features
- Multi-tenant architecture with secure isolation
- AI agent orchestration with LangGraph
- Vector database integration with Qdrant
- Async task processing with Celery
- Authentication and authorization
- Billing integration with Stripe
- Comprehensive monitoring and logging

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Run database migrations:
```bash
alembic upgrade head
```

4. Start the development server:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing
```bash
pytest
```

## Architecture
- **main.py**: FastAPI application setup
- **api/**: API route handlers
- **core/**: Core configuration and utilities
- **models/**: SQLAlchemy database models
- **schemas/**: Pydantic request/response models
- **services/**: Business logic services
- **agents/**: Agent orchestration and management
- **tasks/**: Celery background tasks
- **migrations/**: Alembic database migrations
