#!/usr/bin/env python3
"""
Database Optimization Script
Optimizes database connection pooling and performance settings
"""

import argparse
import logging
import os
import sys
from typing import Dict, Any

# Add the parent directory to the path so we can import from api
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.services.database import (
    DatabaseConfigFactory,
    DatabaseConnectionManager,
    get_connection_manager,
    get_pool_status,
)
from api.config.settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def optimize_for_production(database_url: str) -> Dict[str, Any]:
    """Optimize database configuration for production"""
    logger.info("Optimizing database configuration for production...")
    
    # Create production configuration
    config = DatabaseConfigFactory.create_production_config(database_url)
    
    # Create connection manager
    connection_manager = DatabaseConnectionManager(config)
    
    # Test connection
    if not connection_manager.test_connection():
        raise RuntimeError("Failed to establish database connection")
    
    # Get pool status
    pool_status = connection_manager.get_pool_status()
    
    logger.info("Production optimization completed successfully")
    logger.info(f"Pool configuration: {pool_status}")
    
    return pool_status


def optimize_for_development(database_url: str) -> Dict[str, Any]:
    """Optimize database configuration for development"""
    logger.info("Optimizing database configuration for development...")
    
    # Create development configuration
    config = DatabaseConfigFactory.create_development_config(database_url)
    
    # Create connection manager
    connection_manager = DatabaseConnectionManager(config)
    
    # Test connection
    if not connection_manager.test_connection():
        raise RuntimeError("Failed to establish database connection")
    
    # Get pool status
    pool_status = connection_manager.get_pool_status()
    
    logger.info("Development optimization completed successfully")
    logger.info(f"Pool configuration: {pool_status}")
    
    return pool_status


def optimize_for_testing(database_url: str) -> Dict[str, Any]:
    """Optimize database configuration for testing"""
    logger.info("Optimizing database configuration for testing...")
    
    # Create testing configuration
    config = DatabaseConfigFactory.create_testing_config(database_url)
    
    # Create connection manager
    connection_manager = DatabaseConnectionManager(config)
    
    # Test connection
    if not connection_manager.test_connection():
        raise RuntimeError("Failed to establish database connection")
    
    # Get pool status
    pool_status = connection_manager.get_pool_status()
    
    logger.info("Testing optimization completed successfully")
    logger.info(f"Pool configuration: {pool_status}")
    
    return pool_status


def show_current_status():
    """Show current database connection status"""
    try:
        connection_manager = get_connection_manager()
        pool_status = get_pool_status()
        
        logger.info("Current database connection status:")
        logger.info(f"Pool info: {pool_status.get('pool_info', {})}")
        logger.info(f"Connection count: {pool_status.get('connection_count', 0)}")
        logger.info(f"Active connections: {pool_status.get('active_connections', 0)}")
        logger.info(f"Database type: {pool_status.get('database_type', 'unknown')}")
        logger.info(f"Is production: {pool_status.get('is_production', False)}")
        
    except Exception as e:
        logger.error(f"Failed to get current status: {e}")


def benchmark_connections(database_url: str, num_connections: int = 10):
    """Benchmark database connections"""
    logger.info(f"Benchmarking {num_connections} database connections...")
    
    import time
    from concurrent.futures import ThreadPoolExecutor, as_completed
    
    def test_connection():
        """Test a single database connection"""
        start_time = time.time()
        try:
            config = DatabaseConfigFactory.create_production_config(database_url)
            connection_manager = DatabaseConnectionManager(config)
            
            if connection_manager.test_connection():
                end_time = time.time()
                return {
                    "success": True,
                    "duration": end_time - start_time,
                    "pool_status": connection_manager.get_pool_status()
                }
            else:
                return {"success": False, "error": "Connection test failed"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # Run concurrent connection tests
    start_time = time.time()
    results = []
    
    with ThreadPoolExecutor(max_workers=num_connections) as executor:
        futures = [executor.submit(test_connection) for _ in range(num_connections)]
        
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
    
    end_time = time.time()
    total_duration = end_time - start_time
    
    # Analyze results
    successful_connections = [r for r in results if r.get("success", False)]
    failed_connections = [r for r in results if not r.get("success", False)]
    
    if successful_connections:
        avg_duration = sum(r["duration"] for r in successful_connections) / len(successful_connections)
        min_duration = min(r["duration"] for r in successful_connections)
        max_duration = max(r["duration"] for r in successful_connections)
    else:
        avg_duration = min_duration = max_duration = 0
    
    logger.info("Benchmark Results:")
    logger.info(f"Total connections tested: {num_connections}")
    logger.info(f"Successful connections: {len(successful_connections)}")
    logger.info(f"Failed connections: {len(failed_connections)}")
    logger.info(f"Total duration: {total_duration:.3f}s")
    logger.info(f"Average connection time: {avg_duration:.3f}s")
    logger.info(f"Min connection time: {min_duration:.3f}s")
    logger.info(f"Max connection time: {max_duration:.3f}s")
    
    if failed_connections:
        logger.warning("Failed connections:")
        for i, result in enumerate(failed_connections):
            logger.warning(f"  Connection {i+1}: {result.get('error', 'Unknown error')}")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Database Optimization Script")
    parser.add_argument("--environment", choices=["production", "development", "testing"], 
                       default="development", help="Environment to optimize for")
    parser.add_argument("--database-url", help="Database URL (overrides settings)")
    parser.add_argument("--status", action="store_true", help="Show current database status")
    parser.add_argument("--benchmark", type=int, metavar="N", 
                       help="Benchmark N concurrent connections")
    
    args = parser.parse_args()
    
    # Get database URL
    database_url = args.database_url or settings.database_url
    
    if not database_url:
        logger.error("No database URL provided")
        sys.exit(1)
    
    try:
        if args.status:
            show_current_status()
        elif args.benchmark:
            benchmark_connections(database_url, args.benchmark)
        else:
            # Optimize for specified environment
            if args.environment == "production":
                optimize_for_production(database_url)
            elif args.environment == "development":
                optimize_for_development(database_url)
            elif args.environment == "testing":
                optimize_for_testing(database_url)
            
            logger.info(f"Database optimization completed for {args.environment} environment")
            
    except Exception as e:
        logger.error(f"Database optimization failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
