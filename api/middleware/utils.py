#!/usr/bin/env python3
"""
MIDDLEWARE UTILITIES
Shared utilities and common functionality for all middleware components
"""

import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from collections import defaultdict

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


def get_user_identifier(request: Request) -> str:
    """
    Extract user identifier from request - centralized implementation
    
    Priority order:
    1. User ID from request state (set by auth middleware)
    2. User ID from JWT token (if implemented)
    3. Client IP address (fallback)
    
    Args:
        request: FastAPI request object
        
    Returns:
        str: User identifier in format "user:{user_id}" or "ip:{client_ip}"
    """
    # Try to get user ID from request state (set by auth middleware)
    if hasattr(request.state, 'user_id') and request.state.user_id:
        return f"user:{request.state.user_id}"
    
    # Try to get user ID from JWT token
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        try:
            # This would need to be implemented with your JWT service
            # token = auth_header.split(" ")[1]
            # user_id = decode_jwt_token(token).get("user_id")
            # if user_id:
            #     return f"user:{user_id}"
            pass
        except Exception:
            pass
    
    # Fallback to client IP
    client_ip = get_client_ip(request)
    return f"ip:{client_ip}"


def get_client_ip(request: Request) -> str:
    """
    Extract client IP address from request
    
    Args:
        request: FastAPI request object
        
    Returns:
        str: Client IP address
    """
    # Try to get real IP from headers (for reverse proxy setups)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    # Fallback to direct client IP
    return request.client.host if request.client else "unknown"


def get_client_identifier(request: Request) -> str:
    """
    Get unique client identifier combining IP and user agent
    
    Args:
        request: FastAPI request object
        
    Returns:
        str: Unique client identifier
    """
    client_ip = get_client_ip(request)
    user_agent = request.headers.get("User-Agent", "unknown")
    
    # Create composite key for more granular identification
    return f"{client_ip}:{hash(user_agent) % 10000}"


@dataclass
class MiddlewareConfig:
    """Base configuration for middleware components"""
    
    # Common skip configurations
    skip_paths: List[str] = None
    skip_methods: List[str] = None
    
    # Common logging configurations
    enable_logging: bool = True
    log_level: str = "INFO"
    
    def __post_init__(self):
        if self.skip_paths is None:
            self.skip_paths = [
                "/health",
                "/docs", 
                "/openapi.json",
                "/redoc",
                "/metrics"
            ]
        
        if self.skip_methods is None:
            self.skip_methods = ["HEAD", "OPTIONS"]


class BaseMiddleware(BaseHTTPMiddleware):
    """Base middleware class with common functionality"""
    
    def __init__(self, app, config: Optional[MiddlewareConfig] = None):
        super().__init__(app)
        self.config = config or MiddlewareConfig()
        self.stats = {
            "total_requests": 0,
            "skipped_requests": 0,
            "processed_requests": 0,
            "errors": 0,
        }
    
    def should_skip_request(self, request: Request) -> bool:
        """
        Check if request should be skipped based on path and method
        
        Args:
            request: FastAPI request object
            
        Returns:
            bool: True if request should be skipped
        """
        # Skip by method
        if request.method in self.config.skip_methods:
            return True
        
        # Skip by path
        for skip_path in self.config.skip_paths:
            if request.url.path.startswith(skip_path):
                return True
        
        return False
    
    def log_request(self, request: Request, message: str, level: str = "info", **extra_data):
        """
        Log request with consistent format
        
        Args:
            request: FastAPI request object
            message: Log message
            level: Log level (info, warning, error)
            **extra_data: Additional data to include in log
        """
        if not self.config.enable_logging:
            return
        
        log_data = {
            "method": request.method,
            "path": request.url.path,
            "client_ip": get_client_ip(request),
            "user_id": get_user_identifier(request),
            "user_agent": request.headers.get("User-Agent", "unknown"),
            **extra_data
        }
        
        log_func = getattr(logger, level.lower(), logger.info)
        log_func(message, extra=log_data)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get middleware statistics"""
        return self.stats.copy()
    
    def reset_stats(self):
        """Reset middleware statistics"""
        self.stats = {
            "total_requests": 0,
            "skipped_requests": 0,
            "processed_requests": 0,
            "errors": 0,
        }


class MiddlewareMetrics:
    """Centralized metrics collection for middleware"""
    
    def __init__(self):
        self.metrics = {
            "total_requests": 0,
            "requests_by_endpoint": defaultdict(int),
            "requests_by_method": defaultdict(int),
            "requests_by_user": defaultdict(int),
            "requests_by_client": defaultdict(int),
            "errors_by_type": defaultdict(int),
            "response_times": [],
        }
    
    def record_request(self, request: Request, response_time: float = 0, error: Optional[str] = None):
        """Record request metrics"""
        self.metrics["total_requests"] += 1
        self.metrics["requests_by_endpoint"][request.url.path] += 1
        self.metrics["requests_by_method"][request.method] += 1
        
        user_id = get_user_identifier(request)
        client_id = get_client_identifier(request)
        
        self.metrics["requests_by_user"][user_id] += 1
        self.metrics["requests_by_client"][client_id] += 1
        
        if response_time > 0:
            self.metrics["response_times"].append(response_time)
        
        if error:
            self.metrics["errors_by_type"][error] += 1
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get metrics summary"""
        response_times = self.metrics["response_times"]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        return {
            "total_requests": self.metrics["total_requests"],
            "requests_by_endpoint": dict(self.metrics["requests_by_endpoint"]),
            "requests_by_method": dict(self.metrics["requests_by_method"]),
            "requests_by_user": dict(self.metrics["requests_by_user"]),
            "requests_by_client": dict(self.metrics["requests_by_client"]),
            "errors_by_type": dict(self.metrics["errors_by_type"]),
            "average_response_time": avg_response_time,
            "unique_users": len(self.metrics["requests_by_user"]),
            "unique_clients": len(self.metrics["requests_by_client"]),
        }
    
    def reset_metrics(self):
        """Reset all metrics"""
        self.metrics = {
            "total_requests": 0,
            "requests_by_endpoint": defaultdict(int),
            "requests_by_method": defaultdict(int),
            "requests_by_user": defaultdict(int),
            "requests_by_client": defaultdict(int),
            "errors_by_type": defaultdict(int),
            "response_times": [],
        }


# Global metrics instance
middleware_metrics = MiddlewareMetrics()


def get_middleware_metrics() -> MiddlewareMetrics:
    """Get the global middleware metrics instance"""
    return middleware_metrics


# Common response helpers
def create_error_response(
    error_code: str,
    message: str,
    status_code: int = 400,
    details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create standardized error response
    
    Args:
        error_code: Error code identifier
        message: Error message
        status_code: HTTP status code
        details: Additional error details
        
    Returns:
        Dict: Standardized error response
    """
    response = {
        "success": False,
        "error": {
            "code": error_code,
            "message": message
        }
    }
    
    if details:
        response["error"]["details"] = details
    
    return response


def create_success_response(
    data: Any = None,
    message: str = "Success"
) -> Dict[str, Any]:
    """
    Create standardized success response
    
    Args:
        data: Response data
        message: Success message
        
    Returns:
        Dict: Standardized success response
    """
    response = {
        "success": True,
        "message": message
    }
    
    if data is not None:
        response["data"] = data
    
    return response


# Common validation helpers
def validate_request_size(request: Request, max_size: int) -> bool:
    """
    Validate request size
    
    Args:
        request: FastAPI request object
        max_size: Maximum allowed size in bytes
        
    Returns:
        bool: True if request size is valid
    """
    content_length = request.headers.get("content-length")
    if content_length:
        return int(content_length) <= max_size
    return True


def validate_content_type(request: Request, allowed_types: List[str]) -> bool:
    """
    Validate request content type
    
    Args:
        request: FastAPI request object
        allowed_types: List of allowed content types
        
    Returns:
        bool: True if content type is allowed
    """
    content_type = request.headers.get("content-type", "")
    return any(allowed_type in content_type for allowed_type in allowed_types)


# Common header helpers
def add_security_headers(response, headers: Dict[str, str]):
    """
    Add security headers to response
    
    Args:
        response: FastAPI response object
        headers: Dictionary of headers to add
    """
    for header_name, header_value in headers.items():
        if header_name not in response.headers:
            response.headers[header_name] = header_value


def add_rate_limit_headers(response, limit_info: Dict[str, Any]):
    """
    Add rate limit headers to response
    
    Args:
        response: FastAPI response object
        limit_info: Rate limit information
    """
    if limit_info:
        response.headers["X-RateLimit-Limit"] = str(limit_info.get("max", 0))
        response.headers["X-RateLimit-Remaining"] = str(
            max(0, limit_info.get("max", 0) - limit_info.get("current", 0) - 1)
        )
        response.headers["X-RateLimit-Reset"] = str(int(limit_info.get("reset_time", 0)))
