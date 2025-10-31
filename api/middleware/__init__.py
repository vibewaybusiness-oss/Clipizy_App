"""
Middleware System
Comprehensive request processing, authentication, security, and monitoring
"""

from .auth_middleware import (
    AuthMiddleware,
    AuthMiddlewareConfig,
    get_user_from_request,
    get_user_id_from_request,
    is_admin_from_request
)

from .monitoring_middleware import (
    MonitoringMiddleware,
    MonitoringConfig
)

from .rate_limiting_middleware import (
    RateLimitingMiddleware,
    RateLimitConfig
)

from .sanitizer_middleware import (
    SanitizerMiddleware,
    SanitizationConfig
)

from .security_headers_middleware import (
    SecurityHeadersMiddleware,
    SecurityHeadersConfig
)

from .error_middleware import (
    GlobalErrorHandler
)

from .utils import (
    BaseMiddleware,
    MiddlewareConfig,
    MiddlewareMetrics,
    get_user_identifier,
    get_client_ip
)

__all__ = [
    # Authentication middleware
    "AuthMiddleware",
    "AuthMiddlewareConfig",
    "get_user_from_request",
    "get_user_id_from_request",
    "is_admin_from_request",
    
    # Monitoring middleware
    "MonitoringMiddleware",
    "MonitoringConfig",
    
    # Rate limiting middleware
    "RateLimitingMiddleware",
    "RateLimitConfig",
    
    # Sanitizer middleware
    "SanitizerMiddleware",
    "SanitizationConfig",
    
    # Security headers middleware
    "SecurityHeadersMiddleware",
    "SecurityHeadersConfig",
    
    # Error middleware
    "GlobalErrorHandler",
    
    # Utilities
    "BaseMiddleware",
    "MiddlewareConfig",
    "MiddlewareMetrics",
    "get_user_identifier",
    "get_client_ip"
]
