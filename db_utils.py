"""Database utilities for testing and maintenance"""
import logging
from sqlalchemy import text
from backend.database import SessionLocal, engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_db_stats():
    """Get database statistics"""
    db = SessionLocal()
    try:
        # Count items
        items_count = db.execute(text("SELECT COUNT(*) FROM lmrc.items")).scalar()
        embeddings_count = db.execute(text("SELECT COUNT(*) FROM lmrc.item_embeddings")).scalar()
        sessions_count = db.execute(text("SELECT COUNT(*) FROM lmrc.sessions")).scalar()
        events_count = db.execute(text("SELECT COUNT(*) FROM lmrc.events")).scalar()
        
        return {
            "items": items_count,
            "embeddings": embeddings_count,
            "sessions": sessions_count,
            "events": events_count,
        }
    finally:
        db.close()


def print_stats():
    """Print database statistics"""
    logger.info("=" * 50)
    logger.info("Database Statistics")
    logger.info("=" * 50)
    
    stats = get_db_stats()
    for key, value in stats.items():
        logger.info(f"{key:20s}: {value:10d}")


def check_missing_embeddings():
    """Check items without embeddings"""
    db = SessionLocal()
    try:
        count = db.execute(text("""
            SELECT COUNT(*) FROM lmrc.items
            WHERE asin NOT IN (SELECT asin FROM lmrc.item_embeddings)
        """)).scalar()
        
        return count
    finally:
        db.close()


def cleanup_sessions(days=30):
    """Clean up old sessions"""
    db = SessionLocal()
    try:
        result = db.execute(text(f"""
            DELETE FROM lmrc.sessions
            WHERE updated_at < NOW() - INTERVAL '{days} days'
        """))
        db.commit()
        return result.rowcount
    finally:
        db.close()


if __name__ == "__main__":
    print_stats()
    missing = check_missing_embeddings()
    logger.info(f"\nItems without embeddings: {missing}")
