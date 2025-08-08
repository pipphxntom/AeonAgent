<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# AeonAgent Development Instructions

## Project Overview
AeonAgent is a SaaS platform for pre-built AI agent applications with the following architecture:
- FastAPI backend with PostgreSQL and Redis
- Next.js frontend with Tailwind CSS
- Qdrant vector database for embeddings
- LangGraph for agent orchestration
- Multi-tenant architecture with secure isolation
- Stripe integration for billing
- Auth0/Supabase for authentication

## Code Style Guidelines
- Use async/await patterns for all database and external API calls
- Implement proper error handling with custom exception classes
- Follow RESTful API design principles
- Use Pydantic models for request/response validation
- Implement proper logging and monitoring
- Use dependency injection for database sessions and external services
- Follow the repository pattern for data access
- Implement proper tenant isolation in all database queries

## Key Components
- **Backend**: FastAPI with SQLAlchemy ORM, Alembic migrations
- **Frontend**: Next.js with TypeScript, Tailwind CSS, and Zustand for state management
- **Agent Orchestration**: LangGraph with custom agent definitions
- **Vector DB**: Qdrant for embeddings and retrieval
- **Queue**: Celery with Redis for background tasks
- **Monitoring**: OpenTelemetry, Prometheus metrics
- **Security**: JWT tokens, RBAC, tenant isolation

## Development Practices
- Use type hints throughout Python code
- Implement comprehensive unit and integration tests
- Use environment variables for configuration
- Follow the principle of least privilege for security
- Implement proper audit logging for all tenant operations
- Use database migrations for schema changes
- Implement proper rate limiting and usage tracking
