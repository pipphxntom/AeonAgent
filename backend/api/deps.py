from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import JWTError, jwt
from typing import Optional

from core.database import get_db
from core.config import settings
from models.user import User
from models.tenant import Tenant
from services.supabase_auth import supabase_auth

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get current authenticated user using Supabase."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Verify token with Supabase
        supabase_user = await supabase_auth.verify_token(credentials.credentials)
        
        if not supabase_user:
            raise credentials_exception
        
        email = supabase_user.get("email")
        if not email:
            raise credentials_exception
            
    except Exception as e:
        raise credentials_exception
    
    # Get user from our database
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    
    # Auto-create user if doesn't exist (first-time Supabase users)
    if user is None:
        # Create tenant first (for new organizations)
        from models.tenant import Tenant
        tenant = Tenant(
            org_name=email.split("@")[1],  # Use domain as org name initially
            domain=email.split("@")[1],
            plan="trial"
        )
        db.add(tenant)
        await db.flush()
        
        # Create user
        user = User(
            email=email,
            full_name=supabase_user.get("user_metadata", {}).get("full_name", ""),
            tenant_id=tenant.id,
            role="admin",  # First user is admin
            is_verified=supabase_user.get("email_confirmed", False),
            auth_provider="supabase",
            auth_provider_id=supabase_user["id"]
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user"
        )
    
    return user


async def get_current_tenant(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Tenant:
    """Get current user's tenant."""
    result = await db.execute(select(Tenant).where(Tenant.id == current_user.tenant_id))
    tenant = result.scalar_one_or_none()
    
    if tenant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    if tenant.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant account is not active"
        )
    
    return tenant


def require_permission(permission: str):
    """Dependency to require specific permission."""
    def permission_dependency(current_user: User = Depends(get_current_user)):
        if not current_user.has_permission(permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission}' required"
            )
        return current_user
    return permission_dependency


def require_admin():
    """Dependency to require admin role."""
    return require_permission("admin")


def require_trial_quota(current_tenant: Tenant = Depends(get_current_tenant)):
    """Check if tenant has trial quota remaining."""
    if current_tenant.plan == "trial" and not current_tenant.is_trial_active:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Trial quota exceeded. Please upgrade your plan."
        )
    return current_tenant
