from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship
from datetime import datetime

from core.database import Base


class Interaction(Base):
    """User interaction with an agent."""
    
    __tablename__ = "interactions"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Content
    prompt = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    
    # Model information
    model = Column(String(100), nullable=False)
    temperature = Column(Float)
    tokens_input = Column(Integer)
    tokens_output = Column(Integer)
    tokens_total = Column(Integer)
    
    # Performance metrics
    response_time_ms = Column(Integer)
    retrieval_time_ms = Column(Integer)
    llm_time_ms = Column(Integer)
    
    # Context used
    context_chunks = Column(JSON, default=list)  # List of chunk IDs used
    top_k = Column(Integer)
    rerank_score = Column(Float)
    
    # Status
    status = Column(String(20), default="completed")  # completed, failed, timeout
    error_message = Column(Text)
    
    # Relationships
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    agent_instance_id = Column(Integer, ForeignKey("agent_instances.id"), nullable=False)
    
    # Timestamps
    timestamp = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="interactions")
    user = relationship("User", back_populates="interactions")
    agent_instance = relationship("AgentInstance", back_populates="interactions")
    feedback = relationship("Feedback", back_populates="interaction", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Interaction(id={self.id}, user_id={self.user_id}, status='{self.status}')>"


class Feedback(Base):
    """User feedback on agent responses."""
    
    __tablename__ = "feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Feedback content
    rating = Column(Integer, nullable=False)  # 1-5 scale
    feedback_type = Column(String(20), default="rating")  # rating, edit, report
    edit_text = Column(Text)  # User's corrected response
    comment = Column(Text)
    
    # Classification
    category = Column(String(50))  # accuracy, relevance, tone, etc.
    tags = Column(JSON, default=list)
    
    # Relationships
    interaction_id = Column(Integer, ForeignKey("interactions.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    interaction = relationship("Interaction", back_populates="feedback")
    user = relationship("User", back_populates="feedback")
    
    def __repr__(self):
        return f"<Feedback(id={self.id}, interaction_id={self.interaction_id}, rating={self.rating})>"
