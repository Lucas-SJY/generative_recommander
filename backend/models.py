"""SQLAlchemy ORM models"""
from sqlalchemy import Column, String, Text, Integer, Float, DateTime, JSON, ForeignKey, BigInteger, Index
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from datetime import datetime
from backend.database import Base
from backend.config import settings


class Item(Base):
    """Product item"""
    __tablename__ = "items"
    __table_args__ = {"schema": "lmrc"}
    
    asin = Column(String, primary_key=True)
    parent_asin = Column(String, nullable=True)
    title = Column(Text, nullable=False)
    category = Column(String, nullable=True)
    category_path = Column(Text, nullable=True)
    brand = Column(String, nullable=True)
    price = Column(Float, nullable=True)
    rating_avg = Column(Float, default=0)
    rating_count = Column(Integer, default=0)
    attributes = Column(JSON, default={})
    
    # Relationships
    embedding = relationship("ItemEmbedding", uselist=False, back_populates="item", cascade="all, delete-orphan")
    review_summary = relationship("ReviewSummary", uselist=False, back_populates="item", cascade="all, delete-orphan")


class ItemEmbedding(Base):
    """Item embedding vector"""
    __tablename__ = "item_embeddings"
    __table_args__ = (
        Index("idx_item_embeddings_hnsw", "embedding", postgresql_using="hnsw", postgresql_ops={"embedding": "vector_cosine_ops"}),
        {"schema": "lmrc"}
    )
    
    asin = Column(String, ForeignKey("lmrc.items.asin", ondelete="CASCADE"), primary_key=True)
    embedding = Column(Vector(settings.embed_dim), nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    item = relationship("Item", back_populates="embedding")


class ReviewSummary(Base):
    """Product review summary"""
    __tablename__ = "reviews_summary"
    __table_args__ = ({
        "schema": "lmrc"
    },)
    
    asin = Column(String, ForeignKey("lmrc.items.asin", ondelete="CASCADE"), primary_key=True)
    pros = Column(JSON, default={})
    cons = Column(JSON, default={})
    summary_text = Column(Text, nullable=True)
    embedding = Column(Vector(settings.embed_dim), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    item = relationship("Item", back_populates="review_summary")


class Session(Base):
    """User session for conversation history"""
    __tablename__ = "sessions"
    __table_args__ = {"schema": "lmrc"}
    
    session_id = Column(String, primary_key=True)
    user_id = Column(String, nullable=True)
    memory_json = Column(JSON, default={})
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Event(Base):
    """Event log for tracking interactions"""
    __tablename__ = "events"
    __table_args__ = (
        Index("idx_events_session", "session_id"),
        {"schema": "lmrc"}
    )
    
    event_id = Column(BigInteger, primary_key=True, autoincrement=True)
    session_id = Column(String, nullable=True)
    user_id = Column(String, nullable=True)
    asin = Column(String, nullable=True)
    event_type = Column(String, nullable=False)  # "query", "view", "click", etc.
    payload = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
