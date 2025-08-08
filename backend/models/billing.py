from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON, Float, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

from core.database import Base


class Subscription(Base):
    """Tenant subscription information."""
    
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Stripe information
    stripe_subscription_id = Column(String(255), unique=True, index=True)
    stripe_price_id = Column(String(255))
    stripe_product_id = Column(String(255))
    
    # Subscription details
    plan_name = Column(String(100), nullable=False)  # basic, pro, enterprise
    status = Column(String(20), nullable=False)  # active, canceled, past_due, etc.
    
    # Billing
    amount = Column(Float, nullable=False)  # Amount in cents
    currency = Column(String(3), default="usd")
    interval = Column(String(20), default="month")  # month, year
    
    # Usage limits
    query_limit = Column(Integer)  # Queries per billing period
    user_limit = Column(Integer)   # Max users
    storage_limit_gb = Column(Integer)  # Storage limit in GB
    agent_limit = Column(Integer)  # Max agent instances
    
    # Dates
    current_period_start = Column(DateTime)
    current_period_end = Column(DateTime)
    trial_start = Column(DateTime)
    trial_end = Column(DateTime)
    canceled_at = Column(DateTime)
    ended_at = Column(DateTime)
    
    # Relationships
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="subscriptions")
    billing_records = relationship("BillingRecord", back_populates="subscription", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Subscription(id={self.id}, plan='{self.plan_name}', status='{self.status}')>"
    
    @property
    def is_active(self) -> bool:
        """Check if subscription is active."""
        return self.status in ["active", "trialing"]


class BillingRecord(Base):
    """Billing transaction record."""
    
    __tablename__ = "billing_records"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Stripe information
    stripe_invoice_id = Column(String(255), unique=True, index=True)
    stripe_charge_id = Column(String(255))
    stripe_payment_intent_id = Column(String(255))
    
    # Transaction details
    amount = Column(Float, nullable=False)  # Amount in cents
    currency = Column(String(3), default="usd")
    status = Column(String(20), nullable=False)  # paid, pending, failed, refunded
    description = Column(Text)
    
    # Usage details
    period_start = Column(DateTime)
    period_end = Column(DateTime)
    queries_billed = Column(Integer, default=0)
    overage_amount = Column(Float, default=0.0)
    
    # Relationships
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="billing_records")
    subscription = relationship("Subscription", back_populates="billing_records")
    
    def __repr__(self):
        return f"<BillingRecord(id={self.id}, amount={self.amount}, status='{self.status}')>"
