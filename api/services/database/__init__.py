"""
Database service utilities
"""

from .query_optimizer import QueryOptimizer, OptimizedQueries
from .connection_manager import (
    DatabaseConnectionManager,
    DatabaseConfig,
    ConnectionPoolConfig,
    DatabaseConfigFactory,
    get_connection_manager,
    initialize_connection_manager,
    get_db_session,
    get_pool_status,
    close_all_connections,
    DatabaseType,
    PoolType,
)
from .db_utils import (
    get_db,
    get_optimized_db,
    create_tables,
    drop_tables,
    get_database_url,
    get_connection_pool_status,
    test_database_connection,
    close_database_connections,
    engine,
    SessionLocal,
)
from .base_utils import Base, metadata, GUID

__all__ = [
    "QueryOptimizer",
    "OptimizedQueries",
    "DatabaseConnectionManager",
    "DatabaseConfig",
    "ConnectionPoolConfig",
    "DatabaseConfigFactory",
    "get_connection_manager",
    "initialize_connection_manager",
    "get_db_session",
    "get_db",
    "get_optimized_db",
    "create_tables",
    "drop_tables",
    "get_database_url",
    "get_connection_pool_status",
    "test_database_connection",
    "close_database_connections",
    "get_pool_status",
    "close_all_connections",
    "DatabaseType",
    "PoolType",
    "Base",
    "metadata",
    "GUID",
    "engine",
    "SessionLocal",
]
