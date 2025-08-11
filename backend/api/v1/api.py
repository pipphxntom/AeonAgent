from fastapi import APIRouter

from . import auth, tenants, agents, documents, interactions, billing, admin

api_router = APIRouter()

# Include all route modules
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(tenants.router, prefix="/tenants", tags=["Tenants"])
api_router.include_router(agents.router, prefix="/agents", tags=["Agents"])
api_router.include_router(documents.router, prefix="/documents", tags=["Documents"])
api_router.include_router(interactions.router, prefix="/interactions", tags=["Interactions"])
api_router.include_router(billing.router, prefix="/billing", tags=["Billing"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])
