from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship
from datetime import datetime

from core.database import Base


class AgentType(Base):
    """Agent type definition (HR, Sales, Legal, etc.)."""
    
    __tablename__ = "agent_types"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    display_name = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(100))  # hr, sales, legal, marketing, etc.
    
    # Configuration
    config_template = Column(JSON, nullable=False)  # LangGraph configuration
    default_model = Column(String(100), default="gemini-pro")
    default_temperature = Column(Float, default=0.7)
    
    # Pricing
    trial_enabled = Column(Boolean, default=True)
    base_price_monthly = Column(Float, default=99.0)
    price_per_query = Column(Float, default=0.1)
    
    # Features
    supports_file_upload = Column(Boolean, default=True)
    supports_integrations = Column(Boolean, default=True)
    max_context_length = Column(Integer, default=16000)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    instances = relationship("AgentInstance", back_populates="agent_type", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<AgentType(id={self.id}, name='{self.name}', category='{self.category}')>"


class AgentInstance(Base):
    """Tenant-specific agent instance."""
    
    __tablename__ = "agent_instances"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    
    # Relationships
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    agent_type_id = Column(Integer, ForeignKey("agent_types.id"), nullable=False)
    
    # Configuration
    config = Column(JSON, nullable=False)  # Instance-specific configuration
    model = Column(String(100))
    temperature = Column(Float)
    system_prompt = Column(Text)
    
    # Resources
    status = Column(String(20), default="provisioning")  # provisioning, active, suspended, deleted
    resource_quota = Column(JSON, default=dict)  # CPU, memory, storage limits
    
    # Usage tracking
    queries_count = Column(Integer, default=0)
    tokens_used = Column(Integer, default=0)
    last_used = Column(DateTime)
    
    # Timestamps
    provisioned_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="agent_instances")
    agent_type = relationship("AgentType", back_populates="instances")
    interactions = relationship("Interaction", back_populates="agent_instance", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<AgentInstance(id={self.id}, name='{self.name}', status='{self.status}')>"
    
    @property
    def qdrant_collection_name(self) -> str:
        """Get the Qdrant collection name for this agent instance."""
        return f"tenant_{self.tenant_id}_agent_{self.id}"
