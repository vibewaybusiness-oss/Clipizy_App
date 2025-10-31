"""
Database Connection Manager
Provides optimized connection pooling and database management for production
"""

import logging
import os
from contextlib import asynccontextmanager
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional, Union

from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool, StaticPool, NullPool
from sqlalchemy.exc import DisconnectionError, OperationalError

logger = logging.getLogger(__name__)


class DatabaseType(Enum):
    """Database type enumeration"""
    POSTGRESQL = "postgresql"


class PoolType(Enum):
    """Connection pool type enumeration"""
    QUEUE = "queue"
    STATIC = "static"
    NULL = "null"


@dataclass
class ConnectionPoolConfig:
    """Configuration for database connection pooling"""
    
    # Pool size settings
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    pool_recycle: int = 3600  # 1 hour
    pool_pre_ping: bool = True
    
    # Connection settings
    connect_args: Dict[str, Any] = None
    echo: bool = False
    
    # Pool type
    pool_type: PoolType = PoolType.QUEUE
    
    # Performance settings
    pool_reset_on_return: str = "commit"  # commit, rollback, none
    pool_validate: bool = True
    
    # Timeout settings
    connect_timeout: int = 10
    socket_timeout: int = 30
    
    def __post_init__(self):
        if self.connect_args is None:
            self.connect_args = {}


@dataclass
class DatabaseConfig:
    """Database configuration"""
    
    # Database connection
    database_url: str
    database_type: DatabaseType
    
    # Pool configuration
    pool_config: ConnectionPoolConfig
    
    # Environment settings
    is_production: bool = False
    is_testing: bool = False
    
    # Monitoring settings
    enable_monitoring: bool = True
    log_queries: bool = False


class DatabaseConnectionManager:
    """Manages database connections with optimized pooling"""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.engine: Optional[Engine] = None
        self.session_factory: Optional[sessionmaker] = None
        self._connection_count = 0
        self._active_connections = 0
        
        # Initialize connection pool
        self._create_engine()
        self._setup_monitoring()
    
    def _create_engine(self):
        """Create database engine with optimized pooling"""
        try:
            # Get pool class based on database type and pool type
            pool_class = self._get_pool_class()
            
            # Create engine arguments
            engine_args = {
                "echo": self.config.pool_config.echo,
                "pool_pre_ping": self.config.pool_config.pool_pre_ping,
                "pool_recycle": self.config.pool_config.pool_recycle,
                "pool_reset_on_return": self.config.pool_config.pool_reset_on_return,
                "connect_args": self.config.pool_config.connect_args,
            }
            
            # Add pool-specific arguments
            if pool_class == QueuePool:
                engine_args.update({
                    "pool_size": self.config.pool_config.pool_size,
                    "max_overflow": self.config.pool_config.max_overflow,
                    "pool_timeout": self.config.pool_config.pool_timeout,
                })
            elif pool_class == StaticPool:
                # StaticPool configuration
                pass
            
            # Create engine
            self.engine = create_engine(
                self.config.database_url,
                poolclass=pool_class,
                **engine_args
            )
            
            # Create session factory
            self.session_factory = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            logger.info(f"Database engine created with {pool_class.__name__} pool")
            logger.info(f"Pool configuration: {self._get_pool_info()}")
            
        except Exception as e:
            logger.error(f"Failed to create database engine: {e}")
            raise
    
    def _get_pool_class(self):
        """Get appropriate pool class based on configuration"""
        if self.config.is_testing:
            return StaticPool
        
        # PostgreSQL uses QueuePool for optimal performance
        
        return QueuePool
    
    def _get_pool_info(self) -> Dict[str, Any]:
        """Get current pool information"""
        if not self.engine:
            return {}
        
        pool = self.engine.pool
        return {
            "pool_class": pool.__class__.__name__,
            "size": getattr(pool, 'size', lambda: None)(),
            "checked_in": getattr(pool, 'checkedin', lambda: None)(),
            "checked_out": getattr(pool, 'checkedout', lambda: None)(),
            "overflow": getattr(pool, 'overflow', lambda: None)(),
            "invalid": getattr(pool, 'invalid', lambda: None)(),
        }
    
    def _setup_monitoring(self):
        """Setup database connection monitoring"""
        if not self.config.enable_monitoring:
            return
        
        # Monitor connection events
        @event.listens_for(self.engine, "connect")
        def receive_connect(dbapi_connection, connection_record):
            self._connection_count += 1
            self._active_connections += 1
            logger.debug(f"Database connection established. Total: {self._connection_count}, Active: {self._active_connections}")
        
        @event.listens_for(self.engine, "checkout")
        def receive_checkout(dbapi_connection, connection_record, connection_proxy):
            self._active_connections += 1
            logger.debug(f"Connection checked out. Active: {self._active_connections}")
        
        @event.listens_for(self.engine, "checkin")
        def receive_checkin(dbapi_connection, connection_record):
            self._active_connections -= 1
            logger.debug(f"Connection checked in. Active: {self._active_connections}")
        
        @event.listens_for(self.engine, "close")
        def receive_close(dbapi_connection, connection_record):
            self._active_connections -= 1
            logger.debug(f"Database connection closed. Active: {self._active_connections}")
        
        # Monitor pool events
        @event.listens_for(self.engine, "invalidate")
        def receive_invalidate(dbapi_connection, connection_record, exception):
            logger.warning(f"Database connection invalidated: {exception}")
    
    def get_session(self) -> Session:
        """Get a database session"""
        if not self.session_factory:
            raise RuntimeError("Database engine not initialized")
        
        return self.session_factory()
    
    @asynccontextmanager
    async def get_session_context(self):
        """Get a database session with automatic cleanup"""
        session = self.get_session()
        try:
            yield session
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()
    
    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Database connection test successful")
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False
    
    def get_pool_status(self) -> Dict[str, Any]:
        """Get current pool status"""
        pool_info = self._get_pool_info()
        return {
            "pool_info": pool_info,
            "connection_count": self._connection_count,
            "active_connections": self._active_connections,
            "database_type": self.config.database_type.value,
            "is_production": self.config.is_production,
        }
    
    def close_all_connections(self):
        """Close all database connections"""
        if self.engine:
            self.engine.dispose()
            logger.info("All database connections closed")
    
    def dispose(self):
        """Dispose of the database engine"""
        self.close_all_connections()
        self.engine = None
        self.session_factory = None


class DatabaseConfigFactory:
    """Factory for creating database configurations"""
    
    @staticmethod
    def create_production_config(database_url: str) -> DatabaseConfig:
        """Create production-optimized database configuration"""
        database_type = DatabaseConfigFactory._detect_database_type(database_url)
        
        pool_config = ConnectionPoolConfig(
            pool_size=20,  # Larger pool for production
            max_overflow=30,  # More overflow connections
            pool_timeout=30,
            pool_recycle=3600,  # 1 hour
            pool_pre_ping=True,
            pool_reset_on_return="commit",
            pool_validate=True,
            connect_timeout=10,
            socket_timeout=30,
            connect_args=DatabaseConfigFactory._get_production_connect_args(database_type),
        )
        
        return DatabaseConfig(
            database_url=database_url,
            database_type=database_type,
            pool_config=pool_config,
            is_production=True,
            enable_monitoring=True,
            log_queries=False,  # Disable in production for performance
        )
    
    @staticmethod
    def create_development_config(database_url: str) -> DatabaseConfig:
        """Create development database configuration"""
        database_type = DatabaseConfigFactory._detect_database_type(database_url)
        
        pool_config = ConnectionPoolConfig(
            pool_size=5,  # Smaller pool for development
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=3600,
            pool_pre_ping=True,
            pool_reset_on_return="commit",
            pool_validate=True,
            connect_timeout=10,
            socket_timeout=30,
            connect_args=DatabaseConfigFactory._get_development_connect_args(database_type),
        )
        
        return DatabaseConfig(
            database_url=database_url,
            database_type=database_type,
            pool_config=pool_config,
            is_production=False,
            enable_monitoring=True,
            log_queries=True,  # Enable in development for debugging
        )
    
    @staticmethod
    def create_testing_config(database_url: str) -> DatabaseConfig:
        """Create testing database configuration"""
        database_type = DatabaseConfigFactory._detect_database_type(database_url)
        
        pool_config = ConnectionPoolConfig(
            pool_size=1,  # Minimal pool for testing
            max_overflow=0,
            pool_timeout=30,
            pool_recycle=3600,
            pool_pre_ping=True,
            pool_reset_on_return="rollback",
            pool_validate=True,
            connect_timeout=5,
            socket_timeout=10,
            connect_args=DatabaseConfigFactory._get_testing_connect_args(database_type),
        )
        
        return DatabaseConfig(
            database_url=database_url,
            database_type=database_type,
            pool_config=pool_config,
            is_production=False,
            is_testing=True,
            enable_monitoring=False,
            log_queries=False,
        )
    
    @staticmethod
    def _detect_database_type(database_url: str) -> DatabaseType:
        """Database type is always PostgreSQL"""
        return DatabaseType.POSTGRESQL
    
    @staticmethod
    def _get_production_connect_args(database_type: DatabaseType) -> Dict[str, Any]:
        """Get production connection arguments"""
        return {
            "connect_timeout": 10,
            "application_name": "clipizy_production",
            "options": "-c default_transaction_isolation=read committed",
        }
    
    @staticmethod
    def _get_development_connect_args(database_type: DatabaseType) -> Dict[str, Any]:
        """Get development connection arguments"""
        return {
            "connect_timeout": 10,
            "application_name": "clipizy_development",
        }
    
    @staticmethod
    def _get_testing_connect_args(database_type: DatabaseType) -> Dict[str, Any]:
        """Get testing connection arguments"""
        return {
            "connect_timeout": 5,
            "application_name": "clipizy_testing",
        }


# Global connection manager instance
_connection_manager: Optional[DatabaseConnectionManager] = None


def get_connection_manager() -> DatabaseConnectionManager:
    """Get the global database connection manager"""
    global _connection_manager
    if _connection_manager is None:
        raise RuntimeError("Database connection manager not initialized")
    return _connection_manager


def initialize_connection_manager(database_url: str, environment: str = "development") -> DatabaseConnectionManager:
    """Initialize the global database connection manager"""
    global _connection_manager
    
    if environment == "production":
        config = DatabaseConfigFactory.create_production_config(database_url)
    elif environment == "testing":
        config = DatabaseConfigFactory.create_testing_config(database_url)
    else:
        config = DatabaseConfigFactory.create_development_config(database_url)
    
    _connection_manager = DatabaseConnectionManager(config)
    
    # Test connection
    if not _connection_manager.test_connection():
        raise RuntimeError("Failed to establish database connection")
    
    logger.info(f"Database connection manager initialized for {environment} environment")
    return _connection_manager


def get_db_session() -> Session:
    """Get a database session from the global connection manager"""
    return get_connection_manager().get_session()


def get_pool_status() -> Dict[str, Any]:
    """Get current pool status"""
    return get_connection_manager().get_pool_status()


def close_all_connections():
    """Close all database connections"""
    global _connection_manager
    if _connection_manager:
        _connection_manager.close_all_connections()
        _connection_manager = None
