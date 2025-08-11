from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, Callable

from core.database import get_db
from models.user import User
from models.tenant import Tenant
from services.supabase_auth import supabase_auth

security = HTTPBearer()

# Reusable exceptions
credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)
inactive_user_exception = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Inactive user",
)
missing_tenant_exception = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Tenant not found",
)
inactive_tenant_exception = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Tenant is not active",
)
trial_quota_exceeded_exception = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Trial quota exceeded",
)
permission_denied_exception = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Permission denied",
)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get current authenticated user using Supabase JWT token."""
    token = credentials.credentials if credentials else None
    if not token:
        raise credentials_exception

    try:
        supabase_user = await supabase_auth.verify_token(token)
    except Exception:
        raise credentials_exception

    if not supabase_user:
        raise credentials_exception

    email: Optional[str] = supabase_user.get("email") if isinstance(supabase_user, dict) else None
    if not email or "@" not in email:
        raise credentials_exception

    # Fetch user
    result = await db.execute(select(User).where(User.email == email))
    user: Optional[User] = result.scalar_one_or_none()

    # Auto-provision user & tenant on first login
    if user is None:
        domain = email.split("@")[1]
        tenant = Tenant(
            org_name=domain.split(".")[0],
            domain=domain,
            plan="trial"
        )
        db.add(tenant)
        await db.flush()  # assign tenant.id

        user = User(
            email=email,
            full_name=supabase_user.get("user_metadata", {}).get("full_name", "") if isinstance(supabase_user, dict) else "",
            tenant_id=tenant.id,
            role="admin",
            is_verified=supabase_user.get("email_confirmed", False) if isinstance(supabase_user, dict) else False,
            auth_provider="supabase",
            auth_provider_id=supabase_user.get("id") if isinstance(supabase_user, dict) else None,
            permissions=[]
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    if not user.is_active:
        raise inactive_user_exception

    return user


async def get_current_tenant(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Tenant:
    """Resolve tenant for current user."""
    result = await db.execute(select(Tenant).where(Tenant.id == current_user.tenant_id))
    tenant: Optional[Tenant] = result.scalar_one_or_none()

    if tenant is None:
        raise missing_tenant_exception

    if tenant.status != "active":
        raise inactive_tenant_exception

    return tenant


def require_permission(permission: str) -> Callable:
    """Factory that returns dependency enforcing a permission (admin bypass)."""
    async def permission_dependency(current_user: User = Depends(get_current_user)):
        if not current_user.has_permission(permission):
            raise permission_denied_exception
        return current_user
    return permission_dependency


def require_admin() -> Callable:
    return require_permission("admin")


async def require_trial_quota(current_tenant: Tenant = Depends(get_current_tenant)) -> Tenant:
    """Enforce active trial quota for trial tenants."""
    if current_tenant.plan == "trial" and not current_tenant.is_trial_active:
        raise trial_quota_exceeded_exception
    return current_tenant