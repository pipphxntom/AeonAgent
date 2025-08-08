from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
from pydantic import BaseModel, EmailStr
from typing import Optional

from core.database import get_db
from core.config import settings
from models.user import User
from models.tenant import Tenant
from services.supabase_auth import supabase_auth

router = APIRouter()


class SignUpRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    org_name: str


class SignInRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


@router.post("/signup")
async def signup(
    request: SignUpRequest,
    db: AsyncSession = Depends(get_db)
):
    """Create new account using Supabase authentication."""
    try:
        # Check if user already exists in our database
        result = await db.execute(select(User).where(User.email == request.email))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create user in Supabase
        supabase_result = await supabase_auth.sign_up(
            email=request.email,
            password=request.password,
            metadata={
                "full_name": request.full_name,
                "org_name": request.org_name
            }
        )
        
        if not supabase_result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=supabase_result["error"]
            )
        
        # Create tenant in our database
        tenant = Tenant(
            org_name=request.org_name,
            domain=request.email.split("@")[1],
            plan="trial",
            trial_end_date=datetime.utcnow() + timedelta(days=settings.DEFAULT_TRIAL_DAYS)
        )
        db.add(tenant)
        await db.flush()
        
        # Create user in our database
        user = User(
            email=request.email,
            full_name=request.full_name,
            tenant_id=tenant.id,
            role="admin",
            is_verified=False,  # Will be verified via email
            auth_provider="supabase",
            auth_provider_id=supabase_result["user"]["id"]
        )
        db.add(user)
        
        await db.commit()
        await db.refresh(tenant)
        await db.refresh(user)
        
        return {
            "message": "Account created successfully. Please check your email for verification.",
            "tenant_id": tenant.id,
            "user_id": user.id,
            "email_confirmed": supabase_result["user"]["email_confirmed"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create account: {str(e)}"
        )


@router.post("/login")
async def login(
    request: SignInRequest,
    db: AsyncSession = Depends(get_db)
):
    """Login user using Supabase authentication."""
    try:
        # Authenticate with Supabase
        supabase_result = await supabase_auth.sign_in(
            email=request.email,
            password=request.password
        )
        
        if not supabase_result["success"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=supabase_result["error"],
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Update last login in our database
        result = await db.execute(select(User).where(User.email == request.email))
        user = result.scalar_one_or_none()
        
        if user:
            user.last_login = datetime.utcnow()
            await db.commit()
        
        return {
            "access_token": supabase_result["access_token"],
            "refresh_token": supabase_result["refresh_token"],
            "token_type": "bearer",
            "expires_at": supabase_result["expires_at"],
            "user": supabase_result["user"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )


@router.post("/refresh")
async def refresh_token(request: RefreshRequest):
    """Refresh access token using Supabase."""
    try:
        supabase_result = await supabase_auth.refresh_session(request.refresh_token)
        
        if not supabase_result["success"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=supabase_result["error"]
            )
        
        return {
            "access_token": supabase_result["access_token"],
            "refresh_token": supabase_result["refresh_token"],
            "token_type": "bearer",
            "expires_at": supabase_result["expires_at"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Token refresh failed: {str(e)}"
        )


@router.post("/logout")
async def logout(
    access_token: str
):
    """Logout user."""
    try:
        success = await supabase_auth.sign_out(access_token)
        
        if success:
            return {"message": "Logged out successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Logout failed"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Logout failed: {str(e)}"
        )
