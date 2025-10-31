#!/usr/bin/env python3
"""
RATE LIMITING MIDDLEWARE
FastAPI middleware for API rate limiting and abuse prevention
"""
import time
import logging
from typing import Dict, List, Optional, Tuple
from collections import defaultdict, deque
from dataclasses import dataclass

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


def get_user_identifier(request: Request) -> str:
    """Extract user identifier from request"""
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
    client_ip = request.client.host if request.client else "unknown"
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        client_ip = forwarded_for.split(",")[0].strip()
    
    return f"ip:{client_ip}"


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting"""
    default_limits: List[str] = None
    per_endpoint_limits: Dict[str, List[str]] = None
    skip_paths: List[str] = None
    skip_methods: List[str] = None
    enable_logging: bool = True
    enable_metrics: bool = True
    storage_backend: str = "memory"  # memory, redis
    redis_url: Optional[str] = None
    
    def __post_init__(self):
        if self.default_limits is None:
            self.default_limits = ["1000/hour", "100/minute", "10/second"]
        if self.per_endpoint_limits is None:
            self.per_endpoint_limits = {
                "/api/auth/login": ["5/minute", "20/hour"],
                "/api/auth/register": ["3/minute", "10/hour"],
                "/api/auth/forgot-password": ["2/minute", "5/hour"],
                "/api/music-clip/upload": ["10/minute", "50/hour"],
                "/api/analysis": ["20/minute", "100/hour"],
            }
        if self.skip_paths is None:
            self.skip_paths = ["/health", "/docs", "/openapi.json", "/redoc"]
        if self.skip_methods is None:
            self.skip_methods = ["GET", "HEAD", "OPTIONS"]


class RateLimitStorage:
    """In-memory storage for rate limiting"""
    
    def __init__(self):
        self.requests: Dict[str, deque] = defaultdict(deque)
        self.cleanup_interval = 300  # 5 minutes
        self.last_cleanup = time.time()
    
    def _cleanup_old_requests(self):
        """Remove old request records"""
        current_time = time.time()
        if current_time - self.last_cleanup < self.cleanup_interval:
            return
        
        cutoff_time = current_time - 3600  # Remove requests older than 1 hour
        for key in list(self.requests.keys()):
            requests = self.requests[key]
            while requests and requests[0] < cutoff_time:
                requests.popleft()
            
            if not requests:
                del self.requests[key]
        
        self.last_cleanup = current_time
    
    def add_request(self, key: str, timestamp: float):
        """Add a request timestamp"""
        self._cleanup_old_requests()
        self.requests[key].append(timestamp)
    
    def get_request_count(self, key: str, window_seconds: int) -> int:
        """Get request count within time window"""
        self._cleanup_old_requests()
        current_time = time.time()
        cutoff_time = current_time - window_seconds
        
        requests = self.requests[key]
        count = 0
        for timestamp in reversed(requests):
            if timestamp >= cutoff_time:
                count += 1
            else:
                break
        
        return count
    
    def is_allowed(self, key: str, limit: str) -> Tuple[bool, Dict]:
        """Check if request is allowed based on limit"""
        limit_parts = limit.split("/")
        if len(limit_parts) != 2:
            return True, {}
        
        try:
            max_requests = int(limit_parts[0])
            time_unit = limit_parts[1]
            
            # Convert time unit to seconds
            time_multipliers = {
                "second": 1,
                "minute": 60,
                "hour": 3600,
                "day": 86400
            }
            
            if time_unit not in time_multipliers:
                return True, {}
            
            window_seconds = time_multipliers[time_unit]
            current_count = self.get_request_count(key, window_seconds)
            
            is_allowed = current_count < max_requests
            
            return is_allowed, {
                "limit": limit,
                "current": current_count,
                "max": max_requests,
                "window": time_unit,
                "reset_time": time.time() + window_seconds
            }
            
        except (ValueError, IndexError):
            return True, {}


class RateLimitingMiddleware(BaseHTTPMiddleware):
    """Middleware for API rate limiting and abuse prevention"""
    
    def __init__(
        self,
        app,
        config: Optional[RateLimitConfig] = None,
        storage: Optional[RateLimitStorage] = None,
    ):
        super().__init__(app)
        self.config = config or RateLimitConfig()
        self.storage = storage or RateLimitStorage()
        self.metrics = {
            "total_requests": 0,
            "rate_limited_requests": 0,
            "endpoint_limits": defaultdict(int),
            "client_limits": defaultdict(int),
            "user_limits": defaultdict(int),
        }
    
    async def dispatch(self, request: Request, call_next):
        """Process request through rate limiting middleware"""
        self.metrics["total_requests"] += 1
        
        # Skip rate limiting for certain paths and methods
        if self._should_skip_request(request):
            return await call_next(request)
        
        try:
            # Get client and user identifiers
            client_id = self._get_client_identifier(request)
            user_id = get_user_identifier(request)
            
            # Check rate limits
            is_allowed, limit_info = await self._check_rate_limits(request, client_id, user_id)
            
            if not is_allowed:
                self.metrics["rate_limited_requests"] += 1
                self.metrics["endpoint_limits"][request.url.path] += 1
                self.metrics["client_limits"][client_id] += 1
                if user_id.startswith("user:"):
                    self.metrics["user_limits"][user_id] += 1
                
                if self.config.enable_logging:
                    logger.warning(
                        f"Rate limit exceeded for {client_id} (user: {user_id}) on {request.method} {request.url.path}",
                        extra={
                            "client_id": client_id,
                            "user_id": user_id,
                            "method": request.method,
                            "path": request.url.path,
                            "limit_info": limit_info
                        }
                    )
                
                return JSONResponse(
                    status_code=429,
                    content={
                        "success": False,
                        "error": {
                            "code": "RATE_LIMIT_EXCEEDED",
                            "message": "Rate limit exceeded. Please try again later.",
                            "details": limit_info
                        },
                        "path": request.url.path,
                        "method": request.method,
                        "user_id": user_id,
                        "client_id": client_id
                    },
                    headers={
                        "X-RateLimit-Limit": str(limit_info.get("max", 0)),
                        "X-RateLimit-Remaining": str(max(0, limit_info.get("max", 0) - limit_info.get("current", 0))),
                        "X-RateLimit-Reset": str(int(limit_info.get("reset_time", 0))),
                        "Retry-After": str(int(limit_info.get("reset_time", 0) - time.time()))
                    }
                )
            
            # Add request to storage (both client and user if available)
            self.storage.add_request(client_id, time.time())
            if user_id.startswith("user:"):
                self.storage.add_request(user_id, time.time())
            
            # Continue with request
            response = await call_next(request)
            
            # Add rate limit headers to response
            if limit_info:
                response.headers["X-RateLimit-Limit"] = str(limit_info.get("max", 0))
                response.headers["X-RateLimit-Remaining"] = str(max(0, limit_info.get("max", 0) - limit_info.get("current", 0) - 1))
                response.headers["X-RateLimit-Reset"] = str(int(limit_info.get("reset_time", 0)))
            
            return response
            
        except Exception as e:
            logger.error(f"Rate limiting middleware error: {str(e)}")
            # Don't block requests on middleware errors
            return await call_next(request)
    
    def _should_skip_request(self, request: Request) -> bool:
        """Check if request should be skipped"""
        # Skip by method
        if request.method in self.config.skip_methods:
            return True
        
        # Skip by path
        for skip_path in self.config.skip_paths:
            if request.url.path.startswith(skip_path):
                return True
        
        return False
    
    def _get_client_identifier(self, request: Request) -> str:
        """Get unique client identifier"""
        # Try to get real IP from headers (for reverse proxy setups)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "unknown"
        
        # Add user agent for more granular identification
        user_agent = request.headers.get("User-Agent", "unknown")
        
        # Create composite key
        return f"{client_ip}:{hash(user_agent) % 10000}"
    
    async def _check_rate_limits(self, request: Request, client_id: str, user_id: str) -> Tuple[bool, Dict]:
        """Check all applicable rate limits"""
        path = request.url.path
        
        # Get limits for this endpoint
        endpoint_limits = self.config.per_endpoint_limits.get(path, [])
        all_limits = self.config.default_limits + endpoint_limits
        
        # Check client-based limits
        for limit in all_limits:
            is_allowed, limit_info = self.storage.is_allowed(client_id, limit)
            if not is_allowed:
                return False, limit_info
        
        # Check user-based limits if user is authenticated
        if user_id.startswith("user:"):
            for limit in all_limits:
                is_allowed, limit_info = self.storage.is_allowed(user_id, limit)
                if not is_allowed:
                    return False, limit_info
        
        # If all limits pass, return the most restrictive limit info
        if all_limits:
            # Get the most restrictive limit (lowest max requests)
            most_restrictive = None
            min_max = float('inf')
            
            for limit in all_limits:
                is_allowed, limit_info = self.storage.is_allowed(client_id, limit)
                if limit_info.get("max", float('inf')) < min_max:
                    min_max = limit_info.get("max", float('inf'))
                    most_restrictive = limit_info
            
            return True, most_restrictive or {}
        
        return True, {}
    
    def get_metrics(self) -> Dict:
        """Get rate limiting metrics"""
        return {
            "total_requests": self.metrics["total_requests"],
            "rate_limited_requests": self.metrics["rate_limited_requests"],
            "rate_limit_percentage": (
                self.metrics["rate_limited_requests"] / max(1, self.metrics["total_requests"]) * 100
            ),
            "endpoint_limits": dict(self.metrics["endpoint_limits"]),
            "client_limits": dict(self.metrics["client_limits"]),
            "user_limits": dict(self.metrics["user_limits"]),
            "active_clients": len(self.storage.requests),
        }
    
    def reset_metrics(self):
        """Reset rate limiting metrics"""
        self.metrics = {
            "total_requests": 0,
            "rate_limited_requests": 0,
            "endpoint_limits": defaultdict(int),
            "client_limits": defaultdict(int),
            "user_limits": defaultdict(int),
        }
