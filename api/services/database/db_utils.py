"""
Database utilities and session management
Moved from /api/data/database/ for complete data folder elimination
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Removed config import to avoid circular dependency
# Database URL will be obtained from environment variables directly
from .base_utils import Base, metadata
from .connection_manager import (
    initialize_connection_manager,
    get_connection_manager,
    get_db_session,
    get_pool_status,
    close_all_connections,
)


# Initialize connection manager based on environment
environment = os.getenv("ENVIRONMENT", "development")
database_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/clipizy")
connection_manager = initialize_connection_manager(database_url, environment)

# Get engine and session factory from connection manager
engine = connection_manager.engine
SessionLocal = connection_manager.session_factory


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_optimized_db():
    """Get optimized database session with connection pooling"""
    return get_db_session()


def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """Drop all database tables"""
    Base.metadata.drop_all(bind=engine)


def get_database_url():
    """Get database connection URL"""
    return os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/clipizy")


def get_connection_pool_status():
    """Get connection pool status"""
    return get_pool_status()


def test_database_connection():
    """Test database connection"""
    try:
        db = next(get_db())
        db.execute("SELECT 1")
        return True
    except Exception as e:
        print(f"Database connection test failed: {e}")
        return False


def close_database_connections():
    """Close all database connections"""
    close_all_connections()
