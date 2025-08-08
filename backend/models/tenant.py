from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from core.database import Base


class Tenant(Base):
    """Tenant model for multi-tenant architecture."""
    
    __tablename__ = "tenants"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    org_name = Column(String(255), nullable=False)
    domain = Column(String(255), unique=True, index=True)
    plan = Column(String(50), default="trial")  # trial, basic, pro, enterprise
    status = Column(String(20), default="active")  # active, suspended, deleted
    settings = Column(JSON, default=dict)
    
    # Billing
    stripe_customer_id = Column(String(255), unique=True, index=True)
    billing_email = Column(String(255))
    
    # Trial limits
    trial_start_date = Column(DateTime, default=datetime.utcnow)
    trial_end_date = Column(DateTime)
    trial_queries_used = Column(Integer, default=0)
    trial_queries_limit = Column(Integer, default=100)
    trial_upload_mb_used = Column(Integer, default=0)
    trial_upload_mb_limit = Column(Integer, default=10)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    users = relationship("User", back_populates="tenant", cascade="all, delete-orphan")
    agent_instances = relationship("AgentInstance", back_populates="tenant", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="tenant", cascade="all, delete-orphan")
    interactions = relationship("Interaction", back_populates="tenant", cascade="all, delete-orphan")
    billing_records = relationship("BillingRecord", back_populates="tenant", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="tenant", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Tenant(id={self.id}, org_name='{self.org_name}', plan='{self.plan}')>"
    
    @property
    def is_trial_active(self) -> bool:
        """Check if trial is still active."""
        if self.plan != "trial":
            return False
        
        now = datetime.utcnow()
        if self.trial_end_date and now > self.trial_end_date:
            return False
            
        if self.trial_queries_used >= self.trial_queries_limit:
            return False
            
        if self.trial_upload_mb_used >= self.trial_upload_mb_limit:
            return False
            
        return True
    
    @property
    def qdrant_collection_name(self) -> str:
        """Get the Qdrant collection name for this tenant."""
        return f"tenant_{self.id}"
