"""Initialize the recommendation system"""
import logging
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_environment():
    """Check if all required components are available"""
    logger.info("Checking environment...")
    
    checks = {
        "PostgreSQL": check_postgres,
        "Ollama": check_ollama,
        "Python Packages": check_packages,
    }
    
    all_passed = True
    for name, check_func in checks.items():
        try:
            check_func()
            logger.info(f"✓ {name} - OK")
        except Exception as e:
            logger.error(f"✗ {name} - FAILED: {e}")
            all_passed = False
    
    return all_passed


def check_postgres():
    """Check PostgreSQL connection"""
    from backend.database import engine
    from sqlalchemy import text
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))


def check_ollama():
    """Check Ollama service"""
    from backend.ollama_client import ollama_client
    import requests
    
    response = requests.get(
        f"{ollama_client.base_url}/api/tags",
        timeout=5
    )
    response.raise_for_status()


def check_packages():
    """Check required Python packages"""
    required = [
        "sqlalchemy",
        "psycopg",
        "pgvector",
        "fastapi",
        "uvicorn",
        "pydantic",
    ]
    
    for package in required:
        __import__(package)


def main():
    """Run initialization checks"""
    logger.info("=" * 50)
    logger.info("Recommendation System - Health Check")
    logger.info("=" * 50)
    
    if check_environment():
        logger.info("\n✓ All checks passed! System is ready.")
        return 0
    else:
        logger.error("\n✗ Some checks failed. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
