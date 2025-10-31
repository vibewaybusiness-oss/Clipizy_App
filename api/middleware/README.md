# Middleware System

The middleware system provides comprehensive request processing, authentication, security, and monitoring capabilities for the FastAPI application.

## Overview

This module contains all middleware components that process requests before they reach the API endpoints. Each middleware has a specific responsibility and integrates with the centralized logging and configuration systems.

## Architecture

```
api/middleware/
├── __init__.py                    # Middleware exports and utilities
├── README.md                     # This file
├── auth_middleware.py            # Authentication and authorization
├── monitoring_middleware.py      # Request monitoring and metrics
├── rate_limiting_middleware.py   # Rate limiting and throttling
├── sanitizer_middleware.py       # Input sanitization and validation
├── security_headers_middleware.py # Security headers and CORS
├── error_middleware.py           # Error handling and logging
└── utils.py                      # Common middleware utilities
```

## Core Components

### 1. Authentication Middleware (`auth_middleware.py`)

Handles user authentication and authorization:

**Features:**
- JWT token validation
- User context injection
- Admin access control
- Public path handling
- Authentication statistics

**Configuration:**
```python
@dataclass
class AuthMiddlewareConfig(MiddlewareConfig):
    public_paths: list[str] = ["/health", "/docs", "/api/auth/login"]
    admin_paths: list[str] = ["/api/admin/", "/api/system/"]
    inject_user_context: bool = True
    log_auth_attempts: bool = True
```

**Usage:**
```python
from api.middleware.auth_middleware import AuthMiddleware, AuthMiddlewareConfig

app.add_middleware(
    AuthMiddleware,
    config=AuthMiddlewareConfig(
        public_paths=["/health", "/docs"],
        admin_paths=["/api/admin/"]
    )
)
```

### 2. Monitoring Middleware (`monitoring_middleware.py`)

Tracks request metrics and performance:

**Features:**
- Request/response timing
- User activity tracking
- Performance metrics
- Endpoint usage statistics
- Error rate monitoring

**Metrics Tracked:**
- Request count and duration
- User activity by endpoint
- Error rates and types
- Performance bottlenecks
- Resource usage

### 3. Rate Limiting Middleware (`rate_limiting_middleware.py`)

Implements rate limiting and throttling:

**Features:**
- Per-user rate limiting
- Per-IP rate limiting
- Endpoint-specific limits
- Burst handling
- Rate limit headers

**Configuration:**
```python
@dataclass
class RateLimitingConfig(MiddlewareConfig):
    requests_per_minute: int = 60
    burst_limit: int = 10
    window_size: int = 60
    enable_per_user_limits: bool = True
    enable_per_ip_limits: bool = True
```

### 4. Sanitizer Middleware (`sanitizer_middleware.py`)

Sanitizes and validates input data:

**Features:**
- HTML sanitization
- XSS prevention
- SQL injection prevention
- File upload validation
- Input length limits

**Sanitization Types:**
- HTML content sanitization
- File name sanitization
- URL parameter sanitization
- JSON payload sanitization
- Form data sanitization

### 5. Security Headers Middleware (`security_headers_middleware.py`)

Adds security headers and handles CORS:

**Features:**
- Security headers (HSTS, CSP, etc.)
- CORS configuration
- Content type validation
- Request size limits
- Security policy enforcement

**Security Headers:**
- `Strict-Transport-Security`
- `Content-Security-Policy`
- `X-Frame-Options`
- `X-Content-Type-Options`
- `Referrer-Policy`

### 6. Error Middleware (`error_middleware.py`)

Handles errors and exceptions:

**Features:**
- Global error handling
- Error logging and tracking
- User-friendly error responses
- Error categorization
- Debug information handling

**Error Types:**
- Validation errors
- Authentication errors
- Authorization errors
- Internal server errors
- Custom business logic errors

### 7. Middleware Utilities (`utils.py`)

Common utilities and base classes:

**Base Classes:**
- `BaseMiddleware`: Base class for all middleware
- `MiddlewareConfig`: Configuration base class
- `MiddlewareStats`: Statistics tracking

**Utility Functions:**
- `get_user_identifier()`: Extract user identifier from request
- `get_client_ip()`: Get client IP address
- `is_public_path()`: Check if path is public
- `is_admin_path()`: Check if path requires admin access

## Usage Examples

### Basic Middleware Setup

```python
from fastapi import FastAPI
from api.middleware import (
    AuthMiddleware,
    MonitoringMiddleware,
    RateLimitingMiddleware,
    SanitizerMiddleware,
    SecurityHeadersMiddleware,
    ErrorMiddleware
)

app = FastAPI()

# Add middleware in order (last added = first executed)
app.add_middleware(ErrorMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(SanitizerMiddleware)
app.add_middleware(RateLimitingMiddleware)
app.add_middleware(MonitoringMiddleware)
app.add_middleware(AuthMiddleware)
```

### Custom Middleware Configuration

```python
from api.middleware.auth_middleware import AuthMiddlewareConfig
from api.middleware.rate_limiting_middleware import RateLimitingConfig

# Authentication middleware with custom config
auth_config = AuthMiddlewareConfig(
    public_paths=["/health", "/docs", "/api/public/"],
    admin_paths=["/api/admin/", "/api/system/"],
    inject_user_context=True,
    log_auth_attempts=True
)
app.add_middleware(AuthMiddleware, config=auth_config)

# Rate limiting with custom limits
rate_limit_config = RateLimitingConfig(
    requests_per_minute=100,
    burst_limit=20,
    enable_per_user_limits=True
)
app.add_middleware(RateLimitingMiddleware, config=rate_limit_config)
```

### Accessing User Context

```python
from fastapi import Request
from api.middleware.auth_middleware import get_user_from_request

@app.get("/protected")
def protected_endpoint(request: Request):
    user = get_user_from_request(request)
    if user:
        return {"message": f"Hello {user.email}"}
    return {"error": "Not authenticated"}
```

### Middleware Statistics

```python
from api.middleware.monitoring_middleware import get_middleware_stats

@app.get("/admin/stats")
def get_stats():
    stats = get_middleware_stats()
    return {
        "total_requests": stats["total_requests"],
        "average_response_time": stats["average_response_time"],
        "error_rate": stats["error_rate"],
        "top_endpoints": stats["top_endpoints"]
    }
```

## Centralized Logging Integration

All middleware uses the centralized logging system:

```python
from api.config.logging import MiddlewareLogger, get_middleware_logger

class CustomMiddleware(BaseMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.logger = MiddlewareLogger("custom_middleware")
    
    async def dispatch(self, request, call_next):
        self.logger.log_request(request, "Processing request")
        # ... middleware logic
        self.logger.log_request(request, "Request completed", level="debug")
```

## Configuration Integration

Middleware integrates with the configuration system:

```python
from api.config import get_config_value

class ConfigurableMiddleware(BaseMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.rate_limit = get_config_value("middleware.rate_limit", 60)
        self.enable_logging = get_config_value("middleware.enable_logging", True)
```

## Error Handling

Comprehensive error handling across all middleware:

```python
from api.middleware.error_middleware import ErrorMiddleware

# Global error handling
app.add_middleware(ErrorMiddleware)

# Custom error responses
@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=422,
        content={"error": "Validation failed", "details": exc.errors()}
    )
```

## Security Features

### Authentication & Authorization
- JWT token validation
- Role-based access control
- Admin privilege checking
- Session management

### Input Security
- XSS prevention
- SQL injection prevention
- File upload validation
- Input sanitization

### Network Security
- Rate limiting
- CORS configuration
- Security headers
- Request size limits

## Performance Monitoring

### Metrics Collection
- Request/response timing
- Error rates
- User activity
- Resource usage

### Health Checks
- Middleware health status
- Performance bottlenecks
- Error tracking
- Statistics reporting

## Best Practices

1. **Order Matters**: Add middleware in the correct order
2. **Use Centralized Logging**: Use the centralized logging system
3. **Configure Properly**: Use appropriate configuration for each environment
4. **Handle Errors**: Implement proper error handling
5. **Monitor Performance**: Track middleware performance
6. **Security First**: Implement security measures at the middleware level
7. **Test Thoroughly**: Test middleware in different scenarios
8. **Document Configuration**: Document middleware configuration options

## Integration with Services

Middleware integrates with:
- **Configuration System**: Uses centralized configuration
- **Logging System**: Uses centralized logging
- **Services Layer**: Accesses services for business logic
- **Data Layer**: Uses data layer for persistence
- **Authentication Service**: Integrates with auth service

## Environment-Specific Configuration

Different middleware configurations for different environments:

```python
# Development
if environment == "development":
    app.add_middleware(AuthMiddleware, config=AuthMiddlewareConfig(
        log_auth_attempts=True,
        public_paths=["/health", "/docs", "/debug/"]
    ))

# Production
elif environment == "production":
    app.add_middleware(AuthMiddleware, config=AuthMiddlewareConfig(
        log_auth_attempts=False,
        public_paths=["/health"]
    ))
```

This middleware system provides comprehensive request processing, security, and monitoring capabilities that scale with the application.
