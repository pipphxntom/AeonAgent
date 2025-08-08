# AeonAgent - AI Agent SaaS Platform

AeonAgent is a comprehensive SaaS platform where customers can preview, trial, buy/rent, and integrate pre-built agent applications (HR agent, Sales Ops agent, Legal agent, etc.). Each agent is an orchestrated pipeline of LLMs, retrievers, tools, and connectors built with LangGraph, AutoGen, MCP, and LlamaIndex.

## 🚀 Features

### Core Platform
- **Agent Catalog & Marketplace** - Browse, preview, and trial AI agents
- **Multi-Tenant Architecture** - Secure tenant isolation and data privacy
- **Trial Management** - Time and query-limited trials with conversion tracking
- **Subscription Billing** - Flexible pricing with Stripe integration
- **Enterprise Auth** - OAuth, SAML, and SSO support

### Agent Capabilities
- **LangGraph Orchestration** - Complex agent workflows and pipelines
- **Vector Search** - Qdrant-powered document retrieval and semantic search
- **File Processing** - Intelligent document parsing and chunking
- **Tool Integration** - Connectors for Slack, HRIS, Google Workspace, APIs
- **Feedback Loop** - Continuous learning from user interactions

### Developer Experience
- **FastAPI Backend** - High-performance async Python API
- **Next.js Frontend** - Modern React dashboard and marketplace
- **Docker Compose** - Full local development environment
- **Comprehensive Monitoring** - Prometheus, Grafana, and OpenTelemetry
- **CI/CD Ready** - GitHub Actions workflows and deployment configs

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Next.js       │    │   FastAPI       │    │   PostgreSQL    │
│   Frontend      │◄──►│   Backend       │◄──►│   Database      │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │                          │
                              ▼                          ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Qdrant        │    │   Redis         │    │   Celery        │
│   Vector DB     │    │   Cache/Queue   │    │   Workers       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │   LangGraph     │
                    │   Agents        │
                    └─────────────────┘
```

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - ORM with async support
- **Alembic** - Database migrations
- **PostgreSQL** - Primary database
- **Redis** - Caching and job queue
- **Celery** - Background task processing

### AI & ML
- **LangGraph** - Agent orchestration
- **LlamaIndex** - Document indexing and retrieval
- **Qdrant** - Vector database
- **OpenAI/Gemini** - LLM providers
- **Hugging Face** - Open-source models

### Frontend
- **Next.js 14** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Zustand** - State management
- **React Query** - API state management

### Infrastructure
- **Docker** - Containerization
- **Prometheus** - Metrics collection
- **Grafana** - Monitoring dashboards
- **OpenTelemetry** - Distributed tracing
- **Stripe** - Payment processing

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for frontend development)
- Python 3.11+ (for backend development)

### 1. Clone and Setup
```bash
git clone <repository-url>
cd AeonAgent
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local
```

### 2. Start Services
```bash
# Start all services
docker-compose up -d

# Or start individual services for development
docker-compose up postgres redis qdrant  # Infrastructure only
```

### 3. Backend Development
```bash
cd backend
pip install -r requirements.txt
alembic upgrade head  # Run migrations
uvicorn main:app --reload  # Start dev server
```

### 4. Frontend Development
```bash
cd frontend
npm install
npm run dev  # Start dev server
```

### 5. Access Applications
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Grafana**: http://localhost:3001 (admin/admin)
- **Prometheus**: http://localhost:9090

## 📊 API Endpoints

### Authentication
- `POST /api/v1/auth/signup` - Create account
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh token

### Agents
- `GET /api/v1/agents/catalog` - Browse agent types
- `POST /api/v1/agents/trial` - Start agent trial
- `GET /api/v1/agents/instances` - List tenant agents
- `POST /api/v1/agents/instances/{id}/query` - Query agent

### Tenants
- `GET /api/v1/tenants/me` - Get tenant info
- `GET /api/v1/tenants/usage` - Usage statistics

## 🏢 Business Model

### Trial Strategy
- 14-day free trial
- 100 queries per trial
- 10MB document upload limit
- No credit card required

### Pricing Tiers
- **Basic**: $99/month - Single agent, 1000 queries
- **Pro**: $299/month - 3 agents, 5000 queries, integrations
- **Enterprise**: Custom pricing - Unlimited agents, SSO, on-premise

### Revenue Streams
- SaaS subscriptions
- Usage-based billing
- Marketplace revenue share
- Enterprise services

## 🔒 Security & Compliance

### Data Protection
- Tenant isolation at database level
- Encryption at rest and in transit
- PII detection and redaction
- GDPR compliance features

### Access Control
- Role-based permissions (RBAC)
- API key management
- OAuth/SAML integration
- Audit logging

### Infrastructure Security
- Container security scanning
- Secrets management
- Network isolation
- Regular security updates

## 📈 Monitoring & Analytics

### Metrics Tracked
- API response times and errors
- Agent query performance
- Trial conversion rates
- Resource utilization
- User engagement patterns

### Dashboards Available
- Platform health and performance
- Business metrics and KPIs
- Tenant usage analytics
- Financial reporting

## 🚀 Deployment

### Development
```bash
docker-compose up
```

### Staging/Production
- Kubernetes manifests in `/k8s`
- Terraform infrastructure in `/infrastructure`
- GitHub Actions CI/CD in `/.github/workflows`
- Environment-specific configs

### Scaling Considerations
- Horizontal pod autoscaling
- Database read replicas
- CDN for static assets
- Multi-region deployment

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### Development Guidelines
- Follow PEP 8 for Python code
- Use TypeScript strict mode
- Write comprehensive tests
- Document API changes
- Update migration scripts

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [docs.aeonagent.com](https://docs.aeonagent.com)
- **Support Email**: support@aeonagent.com
- **Community**: [Discord](https://discord.gg/aeonagent)
- **Issues**: [GitHub Issues](https://github.com/your-org/aeonagent/issues)

---

Built with ❤️ by the AeonAgent team
