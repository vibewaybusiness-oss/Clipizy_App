"""
Dependency Injection Module
Minimal implementation for service dependency injection
"""

import logging
from typing import Any, Dict, Optional, Type, TypeVar, Callable
from dataclasses import dataclass
from contextlib import contextmanager
import functools

T = TypeVar('T')

@dataclass
class ServiceConfig:
    """Service configuration"""
    name: str
    enabled: bool = True
    timeout: int = 30
    retry_count: int = 3
    dependencies: list = None

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []

@dataclass
class ServiceMetrics:
    """Service metrics"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time: float = 0.0
    last_request_time: Optional[str] = None

class BaseService:
    """Base service class"""
    
    def __init__(self, config: ServiceConfig, db=None):
        self.config = config
        self.db = db
        self.logger = logging.getLogger(f"service.{config.name}")
        self.metrics = ServiceMetrics()
        self._initialized = False
        self._start_time = None
    
    async def initialize(self):
        """Initialize the service"""
        if not self._initialized:
            self._start_time = self._get_current_time()
            await self._service_health_check()
            self._initialized = True
            self.logger.info(f"Service {self.config.name} initialized")
    
    async def _service_health_check(self) -> Dict[str, Any]:
        """Health check for the service"""
        return {
            "service": self.config.name,
            "status": "healthy",
            "initialized": self._initialized
        }
    
    async def _service_cleanup(self):
        """Cleanup service resources"""
        self.logger.info(f"Service {self.config.name} cleanup completed")
    
    def _get_current_time(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.utcnow().isoformat()

class ServiceFactory:
    """Service factory for creating service instances"""
    
    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._singletons: Dict[str, Any] = {}
        self._transients: Dict[str, Type] = {}
        self._scoped: Dict[str, Type] = {}
    
    def register_singleton(self, service_type: Type[T], instance: T = None):
        """Register a singleton service"""
        service_name = service_type.__name__
        if instance:
            self._singletons[service_name] = instance
        else:
            self._transients[service_name] = service_type
    
    def register_transient(self, service_type: Type[T], implementation: Type[T] = None):
        """Register a transient service"""
        service_name = service_type.__name__
        self._transients[service_name] = implementation or service_type
    
    def register_scoped(self, service_type: Type[T], implementation: Type[T] = None):
        """Register a scoped service"""
        service_name = service_type.__name__
        self._scoped[service_name] = implementation or service_type
    
    def get_service(self, service_type: Type[T]) -> T:
        """Get a service instance"""
        service_name = service_type.__name__
        
        # Check singletons first
        if service_name in self._singletons:
            return self._singletons[service_name]
        
        # Check transients
        if service_name in self._transients:
            implementation = self._transients[service_name]
            return implementation()
        
        # Check scoped
        if service_name in self._scoped:
            implementation = self._scoped[service_name]
            return implementation()
        
        raise ValueError(f"Service {service_name} not registered")

# Global service container
_container = ServiceFactory()

def get_container() -> ServiceFactory:
    """Get the global service container"""
    return _container

def get_service_factory() -> ServiceFactory:
    """Get the service factory"""
    return _container

def register_singleton(service_type: Type[T], instance: T = None):
    """Register a singleton service"""
    _container.register_singleton(service_type, instance)

def register_transient(service_type: Type[T], implementation: Type[T] = None):
    """Register a transient service"""
    _container.register_transient(service_type, implementation)

def register_scoped(service_type: Type[T], implementation: Type[T] = None):
    """Register a scoped service"""
    _container.register_scoped(service_type, implementation)

def get_service(service_type: Type[T]) -> T:
    """Get a service instance"""
    return _container.get_service(service_type)

def service_method(func):
    """Decorator for service methods"""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logging.error(f"Service method {func.__name__} failed: {e}")
            raise
    return wrapper

def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """Decorator for retrying failed operations"""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        import asyncio
                        await asyncio.sleep(delay * (2 ** attempt))
                    else:
                        raise last_exception
            return None
        return wrapper
    return decorator

@contextmanager
def service_context(service_name: str):
    """Context manager for service operations"""
    logger = logging.getLogger(f"service.{service_name}")
    logger.info(f"Starting service context: {service_name}")
    try:
        yield
    except Exception as e:
        logger.error(f"Service context error in {service_name}: {e}")
        raise
    finally:
        logger.info(f"Ending service context: {service_name}")

def inject_service(service_type: Type[T]):
    """Dependency injection decorator"""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            service = get_service(service_type)
            return await func(service, *args, **kwargs)
        return wrapper
    return decorator

def require_service(service_type: Type[T]):
    """Require a service dependency"""
    return get_service(service_type)

__all__ = [
    "BaseService",
    "ServiceConfig", 
    "ServiceMetrics",
    "ServiceFactory",
    "get_container",
    "get_service_factory",
    "service_method",
    "retry_on_failure",
    "service_context",
    "inject_service",
    "require_service",
    "register_singleton",
    "register_transient", 
    "register_scoped",
    "get_service"
]
