"""Database connection and session management"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
from backend.config import settings
import logging

logger = logging.getLogger(__name__)

# Use NullPool to avoid connection pooling issues
engine = create_engine(
    settings.database_url,
    poolclass=NullPool,
    echo=False
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database - ensure extensions"""
    with engine.connect() as conn:
        # Ensure schema exists before creating tables or extensions that depend on it
        try:
            conn.execute(text("CREATE SCHEMA IF NOT EXISTS lmrc"))
            conn.commit()
            logger.info("lmrc schema ensured")
        except Exception as e:
            logger.warning(f"Could not ensure lmrc schema: {e}")
            conn.rollback()
        
        # Enable pgvector extension
        try:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            conn.commit()
            logger.info("pgvector extension enabled")
        except Exception as e:
            logger.warning(f"pgvector extension may already exist: {e}")
        
        # Enable pg_trgm for text search
        try:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))
            conn.commit()
            logger.info("pg_trgm extension enabled")
        except Exception as e:
            logger.warning(f"pg_trgm extension may already exist: {e}")
