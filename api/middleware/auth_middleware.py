#!/usr/bin/env python3
"""
AUTHENTICATION MIDDLEWARE
FastAPI middleware for automatic authentication and user context
"""
from typing import Optional, Dict, Any
from dataclasses import dataclass

from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from api.services.auth import auth_service
from api.services.database import get_db
from api.models import User
from api.config.logging import MiddlewareLogger, get_middleware_logger
from .utils import BaseMiddleware, MiddlewareConfig, get_user_identifier, get_client_ip

# Use centralized logging
logger = get_middleware_logger("auth_middleware")

security = HTTPBearer()


@dataclass
class AuthMiddlewareConfig(MiddlewareConfig):
    """Configuration for authentication middleware"""
    
    # Paths that don't require authentication
    public_paths: list[str] = None
    
    # Paths that require admin access
    admin_paths: list[str] = None
    
    # Enable user context injection
    inject_user_context: bool = True
    
    # Enable request logging
    log_auth_attempts: bool = True
    
    def __post_init__(self):
        super().__post_init__()
        if self.public_paths is None:
            self.public_paths = [
                "/health",
                "/docs", 
                "/openapi.json",
                "/redoc",
                "/metrics",
                "/api/auth/login",
                "/api/auth/register",
                "/api/auth/oauth",
                "/api/auth/refresh",
                "/api/auth/verify-email",
                "/api/auth/reset-password",
                "/api/auth/forgot-password",
                "/api/analysis/analyze/comprehensive"  # Temporary: allow analysis without auth for testing
            ]
        
        if self.admin_paths is None:
            self.admin_paths = [
                "/api/admin/",
                "/api/system/"
            ]


class AuthMiddleware(BaseMiddleware):
    """Middleware for automatic authentication and user context injection"""
    
    def __init__(
        self,
        app,
        config: Optional[AuthMiddlewareConfig] = None
    ):
        super().__init__(app, config or AuthMiddlewareConfig())
        self.auth_stats = {
            "authenticated_requests": 0,
            "public_requests": 0,
            "admin_requests": 0,
            "failed_auth_attempts": 0,
            "users_by_endpoint": {},
        }
        # Use structured logging
        self.middleware_logger = MiddlewareLogger("auth_middleware")
    
    async def dispatch(self, request: Request, call_next):
        """Process request through authentication middleware"""
        self.stats["total_requests"] += 1
        
        # Skip authentication for certain methods and paths
        if self.should_skip_request(request):
            self.stats["skipped_requests"] += 1
            return await call_next(request)
        
        # Check if path is public
        if self._is_public_path(request.url.path):
            self.auth_stats["public_requests"] += 1
            self.stats["processed_requests"] += 1
            return await call_next(request)
        
        # Extract and validate authentication
        try:
            user = await self._authenticate_request(request)
            
            if user:
                # Inject user context into request state
                if self.config.inject_user_context:
                    request.state.user = user
                    request.state.user_id = str(user.id)
                    request.state.is_admin = user.is_admin
                
                # Check admin access for admin paths
                if self._is_admin_path(request.url.path):
                    if not user.is_admin:
                        return JSONResponse(
                            status_code=status.HTTP_403_FORBIDDEN,
                            content={
                                "error": "Admin access required",
                                "detail": "This endpoint requires administrator privileges"
                            }
                        )
                    self.auth_stats["admin_requests"] += 1
                
                self.auth_stats["authenticated_requests"] += 1
                self.stats["processed_requests"] += 1
                
                # Track user activity
                endpoint = f"{request.method} {request.url.path}"
                if endpoint not in self.auth_stats["users_by_endpoint"]:
                    self.auth_stats["users_by_endpoint"][endpoint] = set()
                self.auth_stats["users_by_endpoint"][endpoint].add(str(user.id))
                
                if self.config.log_auth_attempts:
                    self.middleware_logger.log_request(
                        request, 
                        f"Authenticated user {user.email} accessing {endpoint}", 
                        level="debug",
                        user_id=str(user.id),
                        user_email=user.email,
                        endpoint=endpoint
                    )
                
            else:
                # No valid authentication found
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={
                        "error": "Authentication required",
                        "detail": "Valid authentication token required for this endpoint"
                    },
                    headers={"WWW-Authenticate": "Bearer"}
                )
        
        except HTTPException as e:
            self.auth_stats["failed_auth_attempts"] += 1
            self.stats["errors"] += 1
            if self.config.log_auth_attempts:
                self.middleware_logger.log_request(
                    request, 
                    f"Authentication failed: {e.detail}", 
                    level="warning",
                    error_detail=e.detail,
                    status_code=e.status_code
                )
            return JSONResponse(
                status_code=e.status_code,
                content={"error": "Authentication failed", "detail": e.detail},
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        except Exception as e:
            self.auth_stats["failed_auth_attempts"] += 1
            self.stats["errors"] += 1
            self.middleware_logger.log_error(request, e, error_context="authentication_middleware")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"error": "Authentication service error", "detail": "Internal authentication error"}
            )
        
        # Continue with authenticated request
        response = await call_next(request)
        return response
    
    def _is_public_path(self, path: str) -> bool:
        """Check if path is public (doesn't require authentication)"""
        for public_path in self.config.public_paths:
            if path.startswith(public_path):
                return True
        return False
    
    def _is_admin_path(self, path: str) -> bool:
        """Check if path requires admin access"""
        for admin_path in self.config.admin_paths:
            if path.startswith(admin_path):
                return True
        return False
    
    async def _authenticate_request(self, request: Request) -> Optional[User]:
        """Authenticate the request and return user if valid"""
        # Try Bearer token first
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            try:
                # Extract token
                token = auth_header.split(" ")[1]
                
                # Verify token
                payload = auth_service.verify_token(token)
                if payload:
                    user_id = payload.get("sub")
                    if user_id:
                        # Get database session
                        db = next(get_db())
                        try:
                            # Get user from database
                            user = auth_service.get_user_by_id(db, user_id)
                            if user and user.is_active:
                                return user
                        finally:
                            db.close()
            except Exception as e:
                logger.error(f"Bearer token verification error: {str(e)}")
        
        # Fallback: Try cookie-based authentication
        try:
            # Check for access_token cookie
            access_token = request.cookies.get("access_token")
            if access_token:
                payload = auth_service.verify_token(access_token)
                if payload:
                    user_id = payload.get("sub")
                    if user_id:
                        # Get database session
                        db = next(get_db())
                        try:
                            # Get user from database
                            user = auth_service.get_user_by_id(db, user_id)
                            if user and user.is_active:
                                logger.debug(f"User authenticated via cookie: {user.email}")
                                return user
                        finally:
                            db.close()
        except Exception as e:
            logger.error(f"Cookie authentication error: {str(e)}")
        
        return None
    
    def get_auth_stats(self) -> Dict[str, Any]:
        """Get authentication statistics"""
        # Convert sets to counts for JSON serialization
        users_by_endpoint = {
            endpoint: len(users) 
            for endpoint, users in self.auth_stats["users_by_endpoint"].items()
        }
        
        return {
            **self.stats,
            **self.auth_stats,
            "users_by_endpoint": users_by_endpoint,
            "auth_success_rate": (
                self.auth_stats["authenticated_requests"] / 
                max(self.stats["total_requests"], 1) * 100
            )
        }


def get_user_from_request(request: Request) -> Optional[User]:
    """Get user from request state (set by auth middleware)"""
    return getattr(request.state, 'user', None)


def get_user_id_from_request(request: Request) -> Optional[str]:
    """Get user ID from request state (set by auth middleware)"""
    return getattr(request.state, 'user_id', None)


def is_admin_from_request(request: Request) -> bool:
    """Check if user is admin from request state (set by auth middleware)"""
    return getattr(request.state, 'is_admin', False)
