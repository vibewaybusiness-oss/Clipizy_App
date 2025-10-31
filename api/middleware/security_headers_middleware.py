#!/usr/bin/env python3
"""
SECURITY HEADERS MIDDLEWARE
FastAPI middleware for comprehensive security headers and protection
"""
import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from collections import defaultdict

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
class SecurityHeadersConfig:
    """Configuration for security headers"""
    enable_csp: bool = True
    enable_hsts: bool = True
    enable_xss_protection: bool = True
    enable_content_type_nosniff: bool = True
    enable_frame_options: bool = True
    enable_referrer_policy: bool = True
    enable_permissions_policy: bool = True
    skip_paths: List[str] = None
    skip_methods: List[str] = None
    custom_headers: Dict[str, str] = None
    
    def __post_init__(self):
        if self.skip_paths is None:
            self.skip_paths = ["/health", "/docs", "/openapi.json", "/redoc"]
        if self.skip_methods is None:
            self.skip_methods = ["GET", "HEAD", "OPTIONS"]
        if self.custom_headers is None:
            self.custom_headers = {}


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware for comprehensive security headers"""
    
    def __init__(
        self,
        app,
        config: Optional[SecurityHeadersConfig] = None,
    ):
        super().__init__(app)
        self.config = config or SecurityHeadersConfig()
        self.security_headers = self._build_security_headers()
        self.request_stats = {
            "total_requests": 0,
            "requests_by_user": defaultdict(int),
            "requests_by_endpoint": defaultdict(int),
        }
    
    async def dispatch(self, request: Request, call_next):
        """Process request through security headers middleware"""
        user_id = get_user_identifier(request)
        
        # Track request statistics
        self.request_stats["total_requests"] += 1
        self.request_stats["requests_by_user"][user_id] += 1
        self.request_stats["requests_by_endpoint"][request.url.path] += 1
        
        # Skip security headers for certain paths and methods
        if self._should_skip_request(request):
            response = await call_next(request)
            return response
        
        # Process request
        response = await call_next(request)
        
        # Add security headers to response
        self._add_security_headers(response)
        
        return response
    
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
    
    def _build_security_headers(self) -> Dict[str, str]:
        """Build security headers configuration"""
        headers = {}
        
        # Content Security Policy
        if self.config.enable_csp:
            headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://unpkg.com; "
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
                "font-src 'self' https://fonts.gstatic.com; "
                "img-src 'self' data: https: blob:; "
                "media-src 'self' data: https: blob:; "
                "connect-src 'self' https: wss:; "
                "frame-src 'self' https:; "
                "object-src 'none'; "
                "base-uri 'self'; "
                "form-action 'self'; "
                "frame-ancestors 'none'; "
                "upgrade-insecure-requests; "
                "block-all-mixed-content"
            )
        
        # HTTP Strict Transport Security
        if self.config.enable_hsts:
            headers["Strict-Transport-Security"] = (
                "max-age=31536000; "
                "includeSubDomains; "
                "preload"
            )
        
        # XSS Protection
        if self.config.enable_xss_protection:
            headers["X-XSS-Protection"] = "1; mode=block"
        
        # Content Type Options
        if self.config.enable_content_type_nosniff:
            headers["X-Content-Type-Options"] = "nosniff"
        
        # Frame Options
        if self.config.enable_frame_options:
            headers["X-Frame-Options"] = "DENY"
        
        # Referrer Policy
        if self.config.enable_referrer_policy:
            headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Permissions Policy
        if self.config.enable_permissions_policy:
            headers["Permissions-Policy"] = (
                "accelerometer=(), "
                "ambient-light-sensor=(), "
                "autoplay=(), "
                "battery=(), "
                "camera=(), "
                "cross-origin-isolated=(), "
                "display-capture=(), "
                "document-domain=(), "
                "encrypted-media=(), "
                "execution-while-not-rendered=(), "
                "execution-while-out-of-viewport=(), "
                "fullscreen=(self), "
                "geolocation=(), "
                "gyroscope=(), "
                "keyboard-map=(), "
                "magnetometer=(), "
                "microphone=(), "
                "midi=(), "
                "navigation-override=(), "
                "payment=(), "
                "picture-in-picture=(), "
                "publickey-credentials-get=(), "
                "screen-wake-lock=(), "
                "sync-xhr=(), "
                "usb=(), "
                "web-share=(), "
                "xr-spatial-tracking=()"
            )
        
        # Additional security headers
        headers.update({
            "X-DNS-Prefetch-Control": "off",
            "X-Download-Options": "noopen",
            "X-Permitted-Cross-Domain-Policies": "none",
            "Cross-Origin-Embedder-Policy": "require-corp",
            "Cross-Origin-Opener-Policy": "same-origin",
            "Cross-Origin-Resource-Policy": "same-origin",
            "Cache-Control": "no-store, no-cache, must-revalidate, proxy-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
        })
        
        # Add custom headers
        if self.config.custom_headers:
            headers.update(self.config.custom_headers)
        
        return headers
    
    def _add_security_headers(self, response: Response):
        """Add security headers to response"""
        for header_name, header_value in self.security_headers.items():
            # Don't override existing headers
            if header_name not in response.headers:
                response.headers[header_name] = header_value
    
    def get_security_headers(self) -> Dict[str, str]:
        """Get current security headers configuration"""
        return self.security_headers.copy()
    
    def update_security_headers(self, headers: Dict[str, str]):
        """Update security headers configuration"""
        self.security_headers.update(headers)
    
    def remove_security_header(self, header_name: str):
        """Remove a security header"""
        if header_name in self.security_headers:
            del self.security_headers[header_name]
    
    def get_request_stats(self) -> Dict[str, Any]:
        """Get request statistics"""
        stats = self.request_stats.copy()
        # Convert defaultdicts to regular dicts for JSON serialization
        stats["requests_by_user"] = dict(stats["requests_by_user"])
        stats["requests_by_endpoint"] = dict(stats["requests_by_endpoint"])
        return stats
    
    def reset_request_stats(self):
        """Reset request statistics"""
        self.request_stats = {
            "total_requests": 0,
            "requests_by_user": defaultdict(int),
            "requests_by_endpoint": defaultdict(int),
        }
