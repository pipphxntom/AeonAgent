from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from core.database import Base


class User(Base):
    """User model."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255))
    
    # Authentication
    auth_provider = Column(String(50), default="auth0")  # auth0, supabase, local
    auth_provider_id = Column(String(255), unique=True, index=True)
    is_verified = Column(Boolean, default=False)
    
    # Role and permissions
    role = Column(String(50), default="user")  # admin, user, viewer
    permissions = Column(JSON, default=list)
    
    # Status
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime)
    
    # Tenant relationship
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="users")
    interactions = relationship("Interaction", back_populates="user", cascade="all, delete-orphan")
    feedback = relationship("Feedback", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has a specific permission."""
        if self.role == "admin":
            return True
        return permission in (self.permissions or [])
