"""
Database module - compatibility layer for scripts
Provides the expected api.db interface with minimal dependencies
"""

import os
import sys
from pathlib import Path
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Get database URL from environment
def get_database_url():
    """Get database URL from environment variables"""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        # Default to PostgreSQL
        database_url = "postgresql://postgres:postgres@localhost:5432/clipizy"
    return database_url

# Create base class for models
Base = declarative_base()
metadata = MetaData()

# Create engine and session factory
database_url = get_database_url()
engine = create_engine(database_url, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Create all database tables"""
    try:
        # Import all models to ensure they're registered
        import api.models
        Base.metadata.create_all(bind=engine)
        return True
    except Exception as e:
        print(f"Error creating tables: {e}")
        return False

def drop_tables():
    """Drop all database tables"""
    try:
        Base.metadata.drop_all(bind=engine)
        return True
    except Exception as e:
        print(f"Error dropping tables: {e}")
        return False

def get_connection_pool_status():
    """Get connection pool status"""
    return {
        "pool_size": engine.pool.size(),
        "checked_in": engine.pool.checkedin(),
        "checked_out": engine.pool.checkedout(),
        "overflow": engine.pool.overflow(),
        "invalid": engine.pool.invalid()
    }

def test_database_connection():
    """Test database connection"""
    try:
        with engine.connect() as connection:
            connection.execute("SELECT 1")
        return True
    except Exception as e:
        print(f"Database connection test failed: {e}")
        return False

def close_database_connections():
    """Close all database connections"""
    try:
        engine.dispose()
        return True
    except Exception as e:
        print(f"Error closing database connections: {e}")
        return False

# Placeholder functions for compatibility
def get_optimized_db():
    """Get optimized database session (placeholder)"""
    return get_db()

def get_connection_manager():
    """Get connection manager (placeholder)"""
    return None

def initialize_connection_manager(database_url, environment="development"):
    """Initialize connection manager (placeholder)"""
    return None

def get_db_session():
    """Get database session (placeholder)"""
    return SessionLocal()

def get_pool_status():
    """Get pool status (placeholder)"""
    return get_connection_pool_status()

def close_all_connections():
    """Close all connections (placeholder)"""
    return close_database_connections()

__all__ = [
    "Base",
    "metadata", 
    "engine",
    "SessionLocal",
    "get_db",
    "get_optimized_db",
    "create_tables",
    "drop_tables",
    "get_database_url",
    "get_connection_pool_status",
    "test_database_connection",
    "close_database_connections",
    "get_connection_manager",
    "initialize_connection_manager",
    "get_db_session",
    "get_pool_status",
    "close_all_connections",
]