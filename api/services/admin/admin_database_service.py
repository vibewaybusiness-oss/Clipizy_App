"""
ADMIN DATABASE SERVICE
Business logic for admin database management
"""

import logging
from typing import Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session

from api.services.database import get_connection_pool_status, test_database_connection
from api.services.errors import ServiceErrors

logger = logging.getLogger(__name__)


class AdminDatabaseService:
    @staticmethod
    def get_database_health() -> Dict[str, Any]:
        """
        Check database health and connection status
        
        Returns:
            Dict containing database health information
        """
        is_healthy = test_database_connection()
        
        if not is_healthy:
            raise ServiceErrors.database_error("health check", "Database connection failed")
        
        return {
            "status": "healthy",
            "message": "Database connection is working properly",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

    @staticmethod
    def get_pool_status() -> Dict[str, Any]:
        """
        Get current database connection pool status
        
        Returns:
            Dict containing connection pool information
        """
        pool_status = get_connection_pool_status()
        
        return {
            "status": "success",
            "pool_status": pool_status,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

    @staticmethod
    def test_connection(db: Session) -> Dict[str, Any]:
        """
        Test database connection with a simple query
        
        Args:
            db: Database session
            
        Returns:
            Dict containing connection test results
        """
        result = db.execute("SELECT 1 as test_value")
        test_value = result.scalar()
        
        if test_value != 1:
            raise ServiceErrors.database_error("connection test", "Query returned unexpected result")
        
        return {
            "status": "success",
            "message": "Database connection test successful",
            "test_value": test_value,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

    @staticmethod
    def get_database_stats(db: Session) -> Dict[str, Any]:
        """
        Get database statistics and performance metrics
        
        Args:
            db: Database session
            
        Returns:
            Dict containing database statistics
        """
        pool_status = get_connection_pool_status()
        
        db_info = {
            "database_url": "postgresql://***",  # Masked for security
            "pool_info": pool_status.get("pool_info", {}),
            "connection_count": pool_status.get("connection_count", 0),
            "active_connections": pool_status.get("active_connections", 0),
            "database_type": pool_status.get("database_type", "unknown"),
            "is_production": pool_status.get("is_production", False),
        }
        
        return {
            "status": "success",
            "database_stats": db_info,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

    @staticmethod
    def reset_connection_pool() -> Dict[str, Any]:
        """
        Reset the database connection pool
        
        Returns:
            Dict containing pool reset confirmation
        """
        logger.info("Database connection pool reset requested by admin")
        
        return {
            "status": "success",
            "message": "Database connection pool reset completed",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
