from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.database import get_db
from api.deps import get_current_user, get_current_tenant
from models.user import User
from models.tenant import Tenant

router = APIRouter()


@router.get("/me")
async def get_current_tenant_info(
    current_tenant: Tenant = Depends(get_current_tenant),
    current_user: User = Depends(get_current_user)
):
    """Get current tenant information."""
    return {
        "id": current_tenant.id,
        "uuid": current_tenant.uuid,
        "org_name": current_tenant.org_name,
        "domain": current_tenant.domain,
        "plan": current_tenant.plan,
        "status": current_tenant.status,
        "trial_active": current_tenant.is_trial_active,
        "trial_queries_used": current_tenant.trial_queries_used,
        "trial_queries_limit": current_tenant.trial_queries_limit,
        "trial_upload_mb_used": current_tenant.trial_upload_mb_used,
        "trial_upload_mb_limit": current_tenant.trial_upload_mb_limit,
        "created_at": current_tenant.created_at,
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "full_name": current_user.full_name,
            "role": current_user.role
        }
    }


@router.get("/usage")
async def get_usage_stats(
    current_tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db)
):
    """Get tenant usage statistics."""
    # TODO: Implement comprehensive usage stats
    # This would query interactions, documents, billing records etc.
    
    return {
        "current_period": {
            "queries_used": current_tenant.trial_queries_used,
            "queries_limit": current_tenant.trial_queries_limit,
            "storage_mb_used": current_tenant.trial_upload_mb_used,
            "storage_mb_limit": current_tenant.trial_upload_mb_limit
        },
        "total": {
            "agents_created": 0,  # TODO: Count from DB
            "documents_uploaded": 0,  # TODO: Count from DB
            "total_queries": 0  # TODO: Count from DB
        }
    }
