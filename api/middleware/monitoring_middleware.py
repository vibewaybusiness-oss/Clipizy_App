#!/usr/bin/env python3
"""
MONITORING MIDDLEWARE
FastAPI middleware for comprehensive monitoring, metrics, and observability
"""
import time
import logging
import json
from typing import Dict, Optional, Any
from dataclasses import dataclass
from collections import defaultdict, deque
import asyncio

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

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
class MonitoringConfig:
    """Configuration for monitoring middleware"""
    enable_metrics: bool = True
    enable_performance_tracking: bool = True
    enable_error_tracking: bool = True
    enable_request_logging: bool = True
    skip_paths: list = None
    skip_methods: list = None
    metrics_retention_hours: int = 24
    performance_threshold_ms: int = 1000
    log_slow_requests: bool = True
    log_request_body: bool = False
    log_response_body: bool = False
    
    def __post_init__(self):
        if self.skip_paths is None:
            self.skip_paths = ["/health", "/docs", "/openapi.json", "/redoc", "/metrics"]
        if self.skip_methods is None:
            self.skip_methods = ["HEAD", "OPTIONS"]


class MetricsCollector:
    """Collects and stores application metrics"""
    
    def __init__(self, retention_hours: int = 24):
        self.retention_hours = retention_hours
        self.retention_seconds = retention_hours * 3600
        
        # Request metrics
        self.request_count = 0
        self.request_count_by_endpoint = defaultdict(int)
        self.request_count_by_method = defaultdict(int)
        self.request_count_by_status = defaultdict(int)
        
        # Performance metrics
        self.response_times = deque(maxlen=10000)
        self.response_times_by_endpoint = defaultdict(lambda: deque(maxlen=1000))
        self.slow_requests = deque(maxlen=1000)
        
        # Error metrics
        self.error_count = 0
        self.error_count_by_endpoint = defaultdict(int)
        self.error_count_by_type = defaultdict(int)
        
        # System metrics
        self.active_requests = 0
        self.max_concurrent_requests = 0
        
        # Client metrics
        self.unique_clients = set()
        self.requests_by_client = defaultdict(int)
        
        # User metrics
        self.unique_users = set()
        self.requests_by_user = defaultdict(int)
        self.user_activity = defaultdict(lambda: deque(maxlen=1000))
        
        # Last cleanup time
        self.last_cleanup = time.time()
    
    def record_request(self, method: str, endpoint: str, status_code: int, 
                      response_time: float, client_ip: str, user_id: str = None, error: Optional[str] = None):
        """Record a request metric"""
        current_time = time.time()
        
        # Basic request metrics
        self.request_count += 1
        self.request_count_by_endpoint[endpoint] += 1
        self.request_count_by_method[method] += 1
        self.request_count_by_status[status_code] += 1
        
        # Performance metrics
        self.response_times.append(response_time)
        self.response_times_by_endpoint[endpoint].append(response_time)
        
        # Client metrics
        self.unique_clients.add(client_ip)
        self.requests_by_client[client_ip] += 1
        
        # User metrics
        if user_id and user_id.startswith("user:"):
            user_identifier = user_id
            self.unique_users.add(user_identifier)
            self.requests_by_user[user_identifier] += 1
            self.user_activity[user_identifier].append({
                "timestamp": current_time,
                "method": method,
                "endpoint": endpoint,
                "status_code": status_code,
                "response_time": response_time
            })
        
        # Error metrics
        if status_code >= 400 or error:
            self.error_count += 1
            self.error_count_by_endpoint[endpoint] += 1
            if error:
                self.error_count_by_type[error] += 1
        
        # Cleanup old data periodically
        if current_time - self.last_cleanup > 3600:  # Every hour
            self._cleanup_old_data()
            self.last_cleanup = current_time
    
    def record_slow_request(self, method: str, endpoint: str, response_time: float, 
                           client_ip: str, user_id: str = None, request_size: int = 0, response_size: int = 0):
        """Record a slow request"""
        self.slow_requests.append({
            "timestamp": time.time(),
            "method": method,
            "endpoint": endpoint,
            "response_time": response_time,
            "client_ip": client_ip,
            "user_id": user_id,
            "request_size": request_size,
            "response_size": response_size
        })
    
    def increment_active_requests(self):
        """Increment active request counter"""
        self.active_requests += 1
        self.max_concurrent_requests = max(self.max_concurrent_requests, self.active_requests)
    
    def decrement_active_requests(self):
        """Decrement active request counter"""
        self.active_requests = max(0, self.active_requests - 1)
    
    def _cleanup_old_data(self):
        """Clean up old data beyond retention period"""
        cutoff_time = time.time() - self.retention_seconds
        
        # Clean up slow requests
        while self.slow_requests and self.slow_requests[0]["timestamp"] < cutoff_time:
            self.slow_requests.popleft()
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get comprehensive metrics summary"""
        # Calculate average response times
        avg_response_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0
        
        # Calculate percentiles
        sorted_times = sorted(self.response_times)
        p50 = sorted_times[len(sorted_times) // 2] if sorted_times else 0
        p95 = sorted_times[int(len(sorted_times) * 0.95)] if sorted_times else 0
        p99 = sorted_times[int(len(sorted_times) * 0.99)] if sorted_times else 0
        
        return {
            "request_metrics": {
                "total_requests": self.request_count,
                "requests_per_endpoint": dict(self.request_count_by_endpoint),
                "requests_per_method": dict(self.request_count_by_method),
                "requests_per_status": dict(self.request_count_by_status),
                "unique_clients": len(self.unique_clients),
                "active_requests": self.active_requests,
                "max_concurrent_requests": self.max_concurrent_requests,
            },
            "performance_metrics": {
                "average_response_time_ms": round(avg_response_time * 1000, 2),
                "response_time_p50_ms": round(p50 * 1000, 2),
                "response_time_p95_ms": round(p95 * 1000, 2),
                "response_time_p99_ms": round(p99 * 1000, 2),
                "slow_requests_count": len(self.slow_requests),
            },
            "error_metrics": {
                "total_errors": self.error_count,
                "error_rate_percent": round((self.error_count / max(1, self.request_count)) * 100, 2),
                "errors_per_endpoint": dict(self.error_count_by_endpoint),
                "errors_per_type": dict(self.error_count_by_type),
            },
            "client_metrics": {
                "top_clients": dict(sorted(self.requests_by_client.items(), key=lambda x: x[1], reverse=True)[:10])
            },
            "user_metrics": {
                "unique_users": len(self.unique_users),
                "top_users": dict(sorted(self.requests_by_user.items(), key=lambda x: x[1], reverse=True)[:10]),
                "user_activity_summary": {
                    user_id: {
                        "total_requests": len(activity),
                        "last_activity": max([a["timestamp"] for a in activity]) if activity else 0,
                        "avg_response_time": sum([a["response_time"] for a in activity]) / len(activity) if activity else 0
                    }
                    for user_id, activity in self.user_activity.items()
                }
            }
        }


class MonitoringMiddleware(BaseHTTPMiddleware):
    """Middleware for comprehensive monitoring and observability"""
    
    def __init__(
        self,
        app,
        config: Optional[MonitoringConfig] = None,
        metrics_collector: Optional[MetricsCollector] = None,
    ):
        super().__init__(app)
        self.config = config or MonitoringConfig()
        self.metrics = metrics_collector or MetricsCollector(self.config.metrics_retention_hours)
    
    async def dispatch(self, request: Request, call_next):
        """Process request through monitoring middleware"""
        start_time = time.time()
        client_ip = self._get_client_ip(request)
        user_id = get_user_identifier(request)
        request_size = 0
        response_size = 0
        error = None
        response: Optional[Response] = None
        
        # Skip monitoring for certain paths and methods
        if self._should_skip_request(request):
            response = await call_next(request)
            return response
        
        # Track active requests
        if self.config.enable_metrics:
            self.metrics.increment_active_requests()
        
        try:
            # Log request if enabled
            if self.config.enable_request_logging:
                await self._log_request(request, client_ip)
            
            # Get request size
            if hasattr(request, '_body') and request._body:
                request_size = len(request._body)
            
            # Process request
            response = await call_next(request)
            
            # Get response size
            if hasattr(response, 'body') and response.body:
                response_size = len(response.body)
            
            return response
            
        except Exception as e:
            error = str(e)
            logger.error(f"Request processing error: {error}", exc_info=True)
            raise
            
        finally:
            # Calculate response time
            response_time = time.time() - start_time
            
            # Record metrics
            if self.config.enable_metrics:
                status_code = 500
                try:
                    status_code = response.status_code if response is not None else 500
                except Exception:
                    status_code = 500
                self.metrics.record_request(
                    method=request.method,
                    endpoint=request.url.path,
                    status_code=status_code,
                    response_time=response_time,
                    client_ip=client_ip,
                    user_id=user_id,
                    error=error
                )
                
                # Record slow requests
                if (self.config.enable_performance_tracking and 
                    response_time > (self.config.performance_threshold_ms / 1000)):
                    self.metrics.record_slow_request(
                        method=request.method,
                        endpoint=request.url.path,
                        response_time=response_time,
                        client_ip=client_ip,
                        user_id=user_id,
                        request_size=request_size,
                        response_size=response_size
                    )
                
                # Log slow requests
                if (self.config.log_slow_requests and 
                    response_time > (self.config.performance_threshold_ms / 1000)):
                    logger.warning(
                        f"Slow request detected: {request.method} {request.url.path} "
                        f"took {response_time:.3f}s (threshold: {self.config.performance_threshold_ms}ms)",
                        extra={
                            "method": request.method,
                            "path": request.url.path,
                            "response_time": response_time,
                            "client_ip": client_ip,
                            "user_id": user_id,
                            "request_size": request_size,
                            "response_size": response_size
                        }
                    )
                
                # Decrement active requests
                self.metrics.decrement_active_requests()
    
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
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        return request.client.host if request.client else "unknown"
    
    async def _log_request(self, request: Request, client_ip: str):
        """Log request details"""
        user_id = get_user_identifier(request)
        log_data = {
            "timestamp": time.time(),
            "method": request.method,
            "path": request.url.path,
            "query_params": str(request.query_params),
            "client_ip": client_ip,
            "user_id": user_id,
            "user_agent": request.headers.get("User-Agent", "unknown"),
            "content_type": request.headers.get("Content-Type", "unknown"),
            "content_length": request.headers.get("Content-Length", "0"),
        }
        
        # Add request body if enabled (be careful with sensitive data)
        if self.config.log_request_body and request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                if body and len(body) < 1000:  # Only log small bodies
                    log_data["request_body"] = body.decode("utf-8", errors="ignore")
            except Exception:
                pass  # Don't fail on body reading errors
        
        logger.info(f"Request: {request.method} {request.url.path}", extra=log_data)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        return self.metrics.get_metrics_summary()
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status based on metrics"""
        metrics = self.metrics.get_metrics_summary()
        
        # Calculate health indicators
        error_rate = metrics["error_metrics"]["error_rate_percent"]
        avg_response_time = metrics["performance_metrics"]["average_response_time_ms"]
        
        # Determine health status
        if error_rate > 10 or avg_response_time > 5000:
            status = "unhealthy"
        elif error_rate > 5 or avg_response_time > 2000:
            status = "degraded"
        else:
            status = "healthy"
        
        return {
            "status": status,
            "error_rate_percent": error_rate,
            "average_response_time_ms": avg_response_time,
            "active_requests": metrics["request_metrics"]["active_requests"],
            "total_requests": metrics["request_metrics"]["total_requests"],
            "timestamp": time.time()
        }
    
    def reset_metrics(self):
        """Reset all metrics"""
        self.metrics = MetricsCollector(self.config.metrics_retention_hours)
