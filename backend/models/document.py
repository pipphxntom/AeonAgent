from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON, Float, LargeBinary
from sqlalchemy.orm import relationship
from datetime import datetime

from core.database import Base


class Document(Base):
    """Document uploaded by tenant."""
    
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    original_name = Column(String(255), nullable=False)
    content_type = Column(String(100))
    file_size = Column(Integer)  # Size in bytes
    
    # Source information
    source = Column(String(100), default="upload")  # upload, google_drive, sharepoint, etc.
    source_url = Column(String(500))
    source_metadata = Column(JSON, default=dict)
    
    # Processing status
    processing_status = Column(String(20), default="pending")  # pending, processing, completed, failed
    processing_error = Column(Text)
    
    # Content
    extracted_text = Column(Text)
    chunk_count = Column(Integer, default=0)
    
    # Tenant relationship
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    
    # Timestamps
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="documents")
    chunks = relationship("ClauseChunk", back_populates="document", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Document(id={self.id}, filename='{self.filename}', status='{self.processing_status}')>"


class ClauseChunk(Base):
    """Text chunk from a document with embeddings."""
    
    __tablename__ = "clause_chunks"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Content
    text = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False)  # Order within document
    
    # Embeddings
    embedding_id = Column(String(255), unique=True, index=True)  # Qdrant point ID
    embedding_model = Column(String(100), default="text-embedding-ada-002")
    
    # Metadata
    metadata = Column(JSON, default=dict)  # Page number, section, etc.
    
    # Relationships
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    document = relationship("Document", back_populates="chunks")
    
    def __repr__(self):
        return f"<ClauseChunk(id={self.id}, document_id={self.document_id}, chunk_index={self.chunk_index})>"
