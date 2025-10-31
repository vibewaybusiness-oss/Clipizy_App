"""
Base Router Class
Provides common functionality and eliminates code duplication across all routers
"""

import logging
from typing import List, Optional, Dict, Any, Callable, TypeVar, Generic
from datetime import datetime
from functools import wraps

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel

from api.services.database import get_db
from api.services.errors import handle_exception
from api.services.cache.cache_integration import cache_result
from api.middleware.auth_middleware import get_user_from_request, get_user_id_from_request, is_admin_from_request

logger = logging.getLogger(__name__)

T = TypeVar('T')


class BaseRouter:
    """
    Base router class that provides common functionality for all routers.
    Eliminates code duplication and provides consistent patterns.
    """
    
    def __init__(
        self,
        prefix: str,
        tags: List[str],
        requires_auth: bool = True,
        requires_admin: bool = False,
        enable_caching: bool = False,
        cache_expiration: int = 300
    ):
        self.prefix = prefix
        self.tags = tags
        self.requires_auth = requires_auth
        self.requires_admin = requires_admin
        self.enable_caching = enable_caching
        self.cache_expiration = cache_expiration
        
        # Create router with common configuration
        self.router = APIRouter(
            prefix=prefix,
            tags=tags,
            responses={
                400: {"description": "Bad Request"},
                401: {"description": "Unauthorized"},
                403: {"description": "Forbidden"},
                404: {"description": "Not Found"},
                500: {"description": "Internal Server Error"},
            }
        )
        
        # Add common error handlers
        self._add_common_error_handlers()
        
        # Add health check endpoint
        self._add_health_check()
    
    def _add_common_error_handlers(self):
        """Add common error handlers to router"""
        # Note: Exception handlers are added to the main FastAPI app, not individual routers
        # This method is kept for compatibility but doesn't add handlers to the router
        pass
    
    def _add_health_check(self):
        """Add health check endpoint to router"""
        
        @self.router.get("/health")
        async def health_check():
            """Health check endpoint for router"""
            return {
                "status": "healthy",
                "router": self.prefix,
                "service": "clipizy API",
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
    
    def get_auth_dependency(self):
        """Get appropriate authentication dependency - now handled by middleware"""
        # Authentication is now handled by AuthMiddleware
        # This method is kept for backward compatibility but returns None
        return None
    
    def get_db_dependency(self):
        """Get database session dependency"""
        return Depends(get_db)
    
    def endpoint(
        self,
        path: str,
        methods: List[str] = ["GET"],
        response_model: Optional[type] = None,
        cache: bool = False,
        cache_expiration: Optional[int] = None
    ):
        """
        Decorator for creating endpoints with common dependencies and patterns
        """
        def decorator(func: Callable) -> Callable:
            # Add caching if enabled
            if cache or (self.enable_caching and cache):
                expiration = cache_expiration or self.cache_expiration
                func = cache_result(expiration=expiration)(func)
            
            # Add common dependencies
            auth_dep = self.get_auth_dependency()
            db_dep = self.get_db_dependency()
            
            # Create wrapper with error handling
            @wraps(func)
            async def wrapper(*args, **kwargs):
                try:
                    return await func(*args, **kwargs)
                except HTTPException:
                    raise
                except Exception as e:
                    logger.error(f"Error in {self.prefix}{path}: {e}", exc_info=True)
                    raise handle_exception(e, f"processing {path}")
            
            # Register endpoint with router
            for method in methods:
                endpoint_func = self.router.add_api_route(
                    path=path,
                    endpoint=wrapper,
                    methods=method,
                    response_model=response_model
                )
            
            return wrapper
        return decorator
    
    def create_crud_endpoints(
        self,
        model_name: str,
        create_schema: type,
        read_schema: type,
        update_schema: type,
        service_class: type
    ):
        """
        Create standard CRUD endpoints for a model
        """
        service = service_class()
        
        @self.router.post("/", response_model=read_schema)
        async def create_item(
            item_data: create_schema,
            request: Request,
            db: Session = self.get_db_dependency()
        ):
            """Create a new item"""
            current_user = get_user_from_request(request)
            return await service.create(db, item_data, current_user)
        
        @self.router.get("/", response_model=List[read_schema])
        async def list_items(
            request: Request,
            db: Session = self.get_db_dependency()
        ):
            """List all items for current user"""
            current_user = get_user_from_request(request)
            return await service.list_by_user(db, current_user)
        
        @self.router.get("/{item_id}", response_model=read_schema)
        async def get_item(
            item_id: str,
            request: Request,
            db: Session = self.get_db_dependency()
        ):
            """Get item by ID"""
            current_user = get_user_from_request(request)
            return await service.get_by_id(db, item_id, current_user)
        
        @self.router.put("/{item_id}", response_model=read_schema)
        async def update_item(
            item_id: str,
            item_data: update_schema,
            request: Request,
            db: Session = self.get_db_dependency()
        ):
            """Update item by ID"""
            current_user = get_user_from_request(request)
            return await service.update(db, item_id, item_data, current_user)
        
        @self.router.delete("/{item_id}")
        async def delete_item(
            item_id: str,
            request: Request,
            db: Session = self.get_db_dependency()
        ):
            """Delete item by ID"""
            current_user = get_user_from_request(request)
            await service.delete(db, item_id, current_user)
            return {"message": f"{model_name} deleted successfully"}


class AuthRouter(BaseRouter):
    """Specialized router for authentication endpoints"""
    
    def __init__(self, prefix: str, tags: List[str]):
        super().__init__(
            prefix=prefix,
            tags=tags,
            requires_auth=False,  # Auth endpoints don't require auth
            enable_caching=False
        )


class AdminRouter(BaseRouter):
    """Specialized router for admin endpoints"""
    
    def __init__(self, prefix: str, tags: List[str]):
        super().__init__(
            prefix=prefix,
            tags=tags,
            requires_auth=True,
            requires_admin=True,
            enable_caching=False  # Admin endpoints typically shouldn't be cached
        )


class BusinessRouter(BaseRouter):
    """Specialized router for business logic endpoints"""
    
    def __init__(self, prefix: str, tags: List[str]):
        super().__init__(
            prefix=prefix,
            tags=tags,
            requires_auth=True,
            requires_admin=False,
            enable_caching=True,
            cache_expiration=300
        )


class MediaRouter(BaseRouter):
    """Specialized router for media processing endpoints"""
    
    def __init__(self, prefix: str, tags: List[str]):
        super().__init__(
            prefix=prefix,
            tags=tags,
            requires_auth=True,
            requires_admin=False,
            enable_caching=True,
            cache_expiration=600  # Media endpoints can be cached longer
        )


class AIRouter(BaseRouter):
    """Specialized router for AI service endpoints"""
    
    def __init__(self, prefix: str, tags: List[str]):
        super().__init__(
            prefix=prefix,
            tags=tags,
            requires_auth=True,
            requires_admin=False,
            enable_caching=False  # AI endpoints shouldn't be cached
        )


# Utility functions for common patterns
def create_standard_response(data: Any, message: str = "Success") -> Dict[str, Any]:
    """Create a standard response format"""
    return {
        "status": "success",
        "message": message,
        "data": data,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


def create_error_response(error: str, status_code: int = 400) -> Dict[str, Any]:
    """Create a standard error response format"""
    return {
        "status": "error",
        "error": error,
        "status_code": status_code,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


def validate_user_access(current_user, resource_user_id: str) -> bool:
    """Validate that current user has access to resource"""
    if not current_user:
        return False
    
    # Admin users have access to everything
    if hasattr(current_user, 'is_admin') and current_user.is_admin:
        return True
    
    # Check if user owns the resource
    return str(current_user.id) == resource_user_id
