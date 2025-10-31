#!/usr/bin/env python3
"""
HEALTH CHECK ROUTER
Comprehensive health check endpoints for monitoring and observability
"""
import time
import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse

from api.config.settings import settings
from api.services.database import get_connection_manager, get_pool_status
# ComfyUI and RunPod queue manager removed

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/health", tags=["health"])


class HealthChecker:
    """Comprehensive health checking service"""
    
    def __init__(self):
        self.start_time = time.time()
        self.version = "1.0.0"
    
    async def check_database_health(self) -> Dict[str, Any]:
        """Check database connectivity and performance"""
        try:
            start_time = time.time()
            connection_manager = get_connection_manager()
            
            # Test basic connectivity
            connection_manager.test_connection()
            
            # Test connection pool
            pool_status = get_pool_status()
            
            response_time = (time.time() - start_time) * 1000
            
            return {
                "status": "healthy",
                "response_time_ms": round(response_time, 2),
                "connection_pool": pool_status,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def check_services_health(self) -> Dict[str, Any]:
        """Check external services health"""
        return {}
    
    async def check_system_health(self) -> Dict[str, Any]:
        """Check system resources and performance"""
        import psutil
        import os
        
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            
            # Disk usage
            disk = psutil.disk_usage('/')
            
            # Process info
            process = psutil.Process(os.getpid())
            process_memory = process.memory_info()
            
            return {
                "cpu_percent": cpu_percent,
                "memory": {
                    "total_gb": round(memory.total / (1024**3), 2),
                    "available_gb": round(memory.available / (1024**3), 2),
                    "used_percent": memory.percent
                },
                "disk": {
                    "total_gb": round(disk.total / (1024**3), 2),
                    "free_gb": round(disk.free / (1024**3), 2),
                    "used_percent": round((disk.used / disk.total) * 100, 2)
                },
                "process": {
                    "memory_mb": round(process_memory.rss / (1024**2), 2),
                    "cpu_percent": process.cpu_percent()
                },
                "uptime_seconds": time.time() - self.start_time
            }
            
        except Exception as e:
            logger.error(f"System health check failed: {str(e)}")
            return {
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def check_dependencies_health(self) -> Dict[str, Any]:
        """Check critical dependencies"""
        dependencies = {}
        
        # Check Redis (if configured)
        try:
            import redis
            if hasattr(settings, 'redis_url') and settings.redis_url:
                redis_client = redis.from_url(settings.redis_url)
                redis_client.ping()
                dependencies["redis"] = {"status": "healthy"}
            else:
                dependencies["redis"] = {"status": "not_configured"}
        except Exception as e:
            dependencies["redis"] = {"status": "unhealthy", "error": str(e)}
        
        # Check external APIs
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                # Test a simple external service
                response = await client.get("https://httpbin.org/status/200", timeout=5.0)
                dependencies["external_apis"] = {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "response_time_ms": response.elapsed.total_seconds() * 1000
                }
        except Exception as e:
            dependencies["external_apis"] = {"status": "unhealthy", "error": str(e)}
        
        return dependencies


# Global health checker instance
health_checker = HealthChecker()


@router.get("/")
async def basic_health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": health_checker.version,
        "uptime_seconds": time.time() - health_checker.start_time
    }


@router.get("/detailed")
async def detailed_health_check():
    """Detailed health check with all components"""
    start_time = time.time()
    
    # Run all health checks concurrently
    database_task = asyncio.create_task(health_checker.check_database_health())
    services_task = asyncio.create_task(health_checker.check_services_health())
    system_task = asyncio.create_task(health_checker.check_system_health())
    dependencies_task = asyncio.create_task(health_checker.check_dependencies_health())
    
    # Wait for all checks to complete
    database_health, services_health, system_health, dependencies_health = await asyncio.gather(
        database_task, services_task, system_task, dependencies_task,
        return_exceptions=True
    )
    
    # Handle exceptions
    if isinstance(database_health, Exception):
        database_health = {"status": "error", "error": str(database_health)}
    if isinstance(services_health, Exception):
        services_health = {"status": "error", "error": str(services_health)}
    if isinstance(system_health, Exception):
        system_health = {"status": "error", "error": str(system_health)}
    if isinstance(dependencies_health, Exception):
        dependencies_health = {"status": "error", "error": str(dependencies_health)}
    
    # Determine overall health status
    overall_status = "healthy"
    if (database_health.get("status") == "unhealthy" or 
        any(service.get("status") == "unhealthy" for service in services_health.values())):
        overall_status = "unhealthy"
    elif (database_health.get("status") == "error" or 
          any(service.get("status") == "error" for service in services_health.values())):
        overall_status = "degraded"
    
    total_check_time = (time.time() - start_time) * 1000
    
    return {
        "status": overall_status,
        "timestamp": datetime.utcnow().isoformat(),
        "version": health_checker.version,
        "uptime_seconds": time.time() - health_checker.start_time,
        "check_duration_ms": round(total_check_time, 2),
        "components": {
            "database": database_health,
            "services": services_health,
            "system": system_health,
            "dependencies": dependencies_health
        }
    }


@router.get("/database")
async def database_health_check():
    """Database-specific health check"""
    return await health_checker.check_database_health()


@router.get("/services")
async def services_health_check():
    """Services-specific health check"""
    return await health_checker.check_services_health()


@router.get("/system")
async def system_health_check():
    """System resources health check"""
    return await health_checker.check_system_health()


@router.get("/dependencies")
async def dependencies_health_check():
    """Dependencies health check"""
    return await health_checker.check_dependencies_health()


@router.get("/metrics")
async def health_metrics(request: Request):
    """Health metrics endpoint for monitoring systems"""
    try:
        # Get monitoring middleware metrics if available
        monitoring_middleware = getattr(request.app.state, 'monitoring_middleware', None)
        if monitoring_middleware:
            metrics = monitoring_middleware.get_metrics()
            health_status = monitoring_middleware.get_health_status()
        else:
            metrics = {}
            health_status = {"status": "unknown"}
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "health_status": health_status,
            "application_metrics": metrics,
            "system_info": {
                "version": health_checker.version,
                "uptime_seconds": time.time() - health_checker.start_time,
                "environment": settings.environment if hasattr(settings, 'environment') else "unknown"
            }
        }
        
    except Exception as e:
        logger.error(f"Health metrics error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get health metrics: {str(e)}")


@router.get("/readiness")
async def readiness_check():
    """Kubernetes readiness probe endpoint"""
    try:
        # Check critical dependencies
        database_health = await health_checker.check_database_health()
        
        if database_health.get("status") != "healthy":
            return JSONResponse(
                status_code=503,
                content={
                    "status": "not_ready",
                    "reason": "database_unavailable",
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        
        return {
            "status": "ready",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "not_ready",
                "reason": "check_failed",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )


@router.get("/liveness")
async def liveness_check():
    """Kubernetes liveness probe endpoint"""
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime_seconds": time.time() - health_checker.start_time
    }
