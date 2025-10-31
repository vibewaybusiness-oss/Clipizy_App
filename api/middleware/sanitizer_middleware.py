#!/usr/bin/env python3
"""
SANITIZER MIDDLEWARE
FastAPI middleware for automatic input sanitization
Self-contained with all sanitization logic defined directly
"""
import html
import json
import logging
import re
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from .utils import BaseMiddleware, MiddlewareConfig, get_user_identifier

logger = logging.getLogger(__name__)


class SanitizationLevel(Enum):
    """Sanitization strictness levels"""
    STRICT = "strict"
    MODERATE = "moderate"
    PERMISSIVE = "permissive"


@dataclass
class SanitizationConfig:
    """Configuration for sanitization behavior"""
    max_length: int = 10000
    strip_whitespace: bool = True
    normalize_unicode: bool = True
    remove_control_chars: bool = True
    level: SanitizationLevel = SanitizationLevel.MODERATE
    allow_html: bool = False
    allow_scripts: bool = False
    allow_sql_keywords: bool = False
    allowed_tags: List[str] = None
    allowed_attributes: List[str] = None
    allowed_extensions: List[str] = None
    allowed_content_types: List[str] = None
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    custom_patterns: List[str] = None
    
    def __post_init__(self):
        if self.allowed_tags is None:
            self.allowed_tags = []
        if self.allowed_attributes is None:
            self.allowed_attributes = []
        if self.allowed_extensions is None:
            self.allowed_extensions = [".jpg", ".jpeg", ".png", ".gif", ".pdf", ".txt", ".mp3", ".wav", ".mp4", ".avi"]
        if self.allowed_content_types is None:
            self.allowed_content_types = [
                "image/jpeg", "image/png", "image/gif", "application/pdf",
                "text/plain", "audio/mpeg", "audio/wav", "video/mp4", "video/avi"
            ]
        if self.custom_patterns is None:
            self.custom_patterns = []


class SanitizerMiddleware(BaseMiddleware):
    """Middleware for automatic input sanitization with built-in sanitization logic"""

    # SECURITY PATTERNS
    SQL_INJECTION_PATTERNS = [
        r"(?i)(union|select|insert|update|delete|drop|create|alter|exec|execute)",
        r"(?i)(or|and)\s+\d+\s*=\s*\d+",
        r"(?i)(\'|\"|;|--|\/\*|\*\/)",
        r"(?i)(xp_|sp_|fn_)",
        r"(?i)(waitfor|delay|sleep)",
        r"(?i)(load_file|into\s+outfile|into\s+dumpfile)",
    ]
    
    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"vbscript:",
        r"on\w+\s*=",
        r"<iframe[^>]*>",
        r"<object[^>]*>",
        r"<embed[^>]*>",
        r"<link[^>]*>",
        r"<meta[^>]*>",
        r"<style[^>]*>",
        r"expression\s*\(",
        r"url\s*\(",
    ]
    
    PATH_TRAVERSAL_PATTERNS = [
        r"\.\./",
        r"\.\.\\",
        r"%2e%2e%2f",
        r"%2e%2e%5c",
        r"\.\.%2f",
        r"\.\.%5c",
        r"%252e%252e%252f",
        r"%252e%252e%255c",
    ]
    
    COMMAND_INJECTION_PATTERNS = [
        r"[;&|`$]",
        r"(?i)(cmd|command|exec|system|shell)",
        r"(?i)(powershell|bash|sh|cmd)",
        r"`[^`]*`",
        r"\$\([^)]*\)",
        r"<[^>]*>",
    ]
    
    LDAP_INJECTION_PATTERNS = [
        r"[()=*!&|]",
        r"(?i)(objectclass|cn|sn|givenname|mail)",
        r"(?i)(admin|administrator|root)",
    ]
    
    NOSQL_INJECTION_PATTERNS = [
        r"(?i)(\$where|\$ne|\$gt|\$lt|\$regex|\$exists)",
        r"(?i)(true|false|null)",
        r"(?i)(and|or|not)",
    ]
    
    CONTROL_CHARS_PATTERNS = [
        r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]",
    ]
    
    UNICODE_ABUSE_PATTERNS = [
        r"[\u200B-\u200D\uFEFF]",
        r"[\u2028\u2029]",
        r"[\u2060-\u2064]",
    ]

    def __init__(
        self,
        app,
        config: Optional[SanitizationConfig] = None,
        skip_paths: Optional[List[str]] = None,
        skip_methods: Optional[List[str]] = None,
        log_violations: bool = True,
    ):
        # Create middleware config with custom skip paths/methods
        middleware_config = MiddlewareConfig()
        if skip_paths:
            middleware_config.skip_paths.extend(skip_paths)
        if skip_methods:
            middleware_config.skip_methods.extend(skip_methods)
        
        super().__init__(app, middleware_config)
        # Keep BaseMiddleware config intact; store sanitization settings separately
        self.sanitization_config = config or SanitizationConfig()
        self.log_violations = log_violations
        self.violation_stats = {
            "sanitized_requests": 0,
            "violations_detected": 0,
            "patterns_triggered": {},
            "violations_by_user": defaultdict(int),
            "violations_by_endpoint": defaultdict(int),
        }
        self._setup_compiled_patterns()

    def _setup_compiled_patterns(self):
        """Setup compiled regex patterns based on sanitization level"""
        self.compiled_patterns = {}
        
        # Always include control characters and unicode abuse
        self.compiled_patterns["control_chars"] = [
            re.compile(pattern, re.IGNORECASE | re.MULTILINE) 
            for pattern in self.CONTROL_CHARS_PATTERNS
        ]
        self.compiled_patterns["unicode_abuse"] = [
            re.compile(pattern, re.IGNORECASE | re.MULTILINE) 
            for pattern in self.UNICODE_ABUSE_PATTERNS
        ]
        
        # Add patterns based on sanitization level
        if self.sanitization_config.level in [SanitizationLevel.STRICT, SanitizationLevel.MODERATE]:
            self.compiled_patterns["sql_injection"] = [
                re.compile(pattern, re.IGNORECASE | re.MULTILINE) 
                for pattern in self.SQL_INJECTION_PATTERNS
            ]
            self.compiled_patterns["xss"] = [
                re.compile(pattern, re.IGNORECASE | re.MULTILINE) 
                for pattern in self.XSS_PATTERNS
            ]
            self.compiled_patterns["path_traversal"] = [
                re.compile(pattern, re.IGNORECASE | re.MULTILINE) 
                for pattern in self.PATH_TRAVERSAL_PATTERNS
            ]
            self.compiled_patterns["command_injection"] = [
                re.compile(pattern, re.IGNORECASE | re.MULTILINE) 
                for pattern in self.COMMAND_INJECTION_PATTERNS
            ]
        
        if self.sanitization_config.level == SanitizationLevel.STRICT:
            self.compiled_patterns["ldap_injection"] = [
                re.compile(pattern, re.IGNORECASE | re.MULTILINE) 
                for pattern in self.LDAP_INJECTION_PATTERNS
            ]
            self.compiled_patterns["nosql_injection"] = [
                re.compile(pattern, re.IGNORECASE | re.MULTILINE) 
                for pattern in self.NOSQL_INJECTION_PATTERNS
            ]
        
        # Add custom patterns
        if self.sanitization_config.custom_patterns:
            self.compiled_patterns["custom"] = [
                re.compile(pattern, re.IGNORECASE | re.MULTILINE) 
                for pattern in self.sanitization_config.custom_patterns
            ]

    def sanitize_string(self, value: str, input_type: str = "text") -> Dict[str, Any]:
        """Sanitize string input with built-in logic"""
        if not isinstance(value, str):
            return {
                "original": value,
                "sanitized": str(value),
                "is_valid": False,
                "warnings": [],
                "errors": ["Input must be a string"]
            }
        
        original = value
        warnings = []
        errors = []
        
        # Length validation
        if len(value) > self.sanitization_config.max_length:
            value = value[:self.sanitization_config.max_length]
            warnings.append(f"Input truncated to {self.sanitization_config.max_length} characters")
        
        # Strip whitespace if configured
        if self.sanitization_config.strip_whitespace:
            value = value.strip()
        
        # Remove control characters
        if self.sanitization_config.remove_control_chars:
            for pattern in self.compiled_patterns.get("control_chars", []):
                value = pattern.sub("", value)
        
        # Normalize unicode
        if self.sanitization_config.normalize_unicode:
            for pattern in self.compiled_patterns.get("unicode_abuse", []):
                value = pattern.sub("", value)
        
        # Check for malicious patterns
        for category, patterns in self.compiled_patterns.items():
            if category in ["control_chars", "unicode_abuse"]:
                continue
            
            for pattern in patterns:
                if pattern.search(value):
                    if category == "sql_injection" and not self.sanitization_config.allow_sql_keywords:
                        errors.append(f"Potential {category} detected")
                    else:
                        warnings.append(f"Potential {category} pattern detected")
        
        # HTML encoding if not allowed
        if not self.sanitization_config.allow_html:
            value = html.escape(value, quote=True)
        
        return {
            "original": original,
            "sanitized": value,
            "is_valid": len(errors) == 0,
            "warnings": warnings,
            "errors": errors
        }

    def sanitize_number(self, value: Union[int, float, str], input_type: str = "number") -> Dict[str, Any]:
        """Sanitize numeric input with built-in logic"""
        original = value
        warnings = []
        errors = []
        
        try:
            if isinstance(value, str):
                # Remove any non-numeric characters except decimal point and minus
                cleaned = re.sub(r"[^\d.-]", "", value)
                if "." in cleaned:
                    sanitized = float(cleaned)
                else:
                    sanitized = int(cleaned)
            else:
                sanitized = value
            
            # Validate range for common numeric types
            if input_type == "integer":
                if not isinstance(sanitized, int):
                    sanitized = int(sanitized)
            elif input_type == "float":
                if not isinstance(sanitized, float):
                    sanitized = float(sanitized)
            
            # Check for reasonable bounds
            if abs(sanitized) > 1e15:
                warnings.append("Number exceeds reasonable bounds")
        
        except (ValueError, TypeError) as e:
            errors.append(f"Invalid number format: {str(e)}")
            sanitized = 0
        
        return {
            "original": original,
            "sanitized": sanitized,
            "is_valid": len(errors) == 0,
            "warnings": warnings,
            "errors": errors
        }

    def sanitize_boolean(self, value: Any) -> Dict[str, Any]:
        """Sanitize boolean input with built-in logic"""
        original = value
        warnings = []
        errors = []
        
        if isinstance(value, bool):
            sanitized = value
        elif isinstance(value, str):
            sanitized = value.lower() in ("true", "1", "yes", "on", "enabled")
        elif isinstance(value, (int, float)):
            sanitized = bool(value)
        else:
            sanitized = bool(value)
            warnings.append("Non-boolean value converted to boolean")
        
        return {
            "original": original,
            "sanitized": sanitized,
            "is_valid": True,
            "warnings": warnings,
            "errors": errors
        }

    def sanitize_file_upload(self, filename: str, content_type: str, size: int) -> Dict[str, Any]:
        """Sanitize file upload metadata with built-in logic"""
        original = {"filename": filename, "content_type": content_type, "size": size}
        warnings = []
        errors = []
        
        # Sanitize filename
        filename_result = self.sanitize_string(filename, "filename")
        if not filename_result["is_valid"]:
            errors.extend([f"Filename: {e}" for e in filename_result["errors"]])
        
        # Validate file extension
        file_ext = filename.lower().split(".")[-1] if "." in filename else ""
        if f".{file_ext}" not in self.sanitization_config.allowed_extensions:
            errors.append(f"File extension '.{file_ext}' not allowed")
        
        # Validate content type
        if content_type not in self.sanitization_config.allowed_content_types:
            errors.append(f"Content type '{content_type}' not allowed")
        
        # Validate file size
        if size > self.sanitization_config.max_file_size:
            errors.append(f"File size {size} exceeds maximum {self.sanitization_config.max_file_size} bytes")
        
        sanitized = {
            "filename": filename_result["sanitized"],
            "content_type": content_type,
            "size": size
        }
        
        return {
            "original": original,
            "sanitized": sanitized,
            "is_valid": len(errors) == 0,
            "warnings": warnings,
            "errors": errors
        }

    async def dispatch(self, request: Request, call_next):
        """Process request through sanitization middleware"""
        self.stats["total_requests"] += 1
        user_id = get_user_identifier(request)

        # Skip sanitization for certain paths and methods
        if self.should_skip_request(request):
            self.stats["skipped_requests"] += 1
            return await call_next(request)

        try:
            # Sanitize request data
            sanitized_data = await self._sanitize_request(request)

            if sanitized_data:
                self.violation_stats["sanitized_requests"] += 1
                self.stats["processed_requests"] += 1

                # Log violations if enabled
                if self.log_violations and self._has_violations(sanitized_data):
                    await self._log_violations(request, sanitized_data, user_id)

            # Continue with sanitized request
            response = await call_next(request)
            return response

        except Exception as e:
            self.stats["errors"] += 1
            self.log_request(request, f"Sanitizer middleware error: {str(e)}", "error")
            return JSONResponse(status_code=500, content={"error": "Sanitization failed", "detail": str(e)})


    async def _sanitize_request(self, request: Request) -> Optional[Dict[str, Any]]:
        """Sanitize request data"""
        sanitized_data = {}
        has_violations = False

        # Sanitize query parameters
        if request.query_params:
            query_result = self._sanitize_query_params(request.query_params)
            if query_result:
                sanitized_data["query"] = query_result
                if self._has_violations_in_result(query_result):
                    has_violations = True

        # Sanitize path parameters
        if request.path_params:
            path_result = self._sanitize_path_params(request.path_params)
            if path_result:
                sanitized_data["path"] = path_result
                if self._has_violations_in_result(path_result):
                    has_violations = True

        # Sanitize request body
        if request.method in ["POST", "PUT", "PATCH"]:
            body_result = await self._sanitize_request_body(request)
            if body_result:
                sanitized_data["body"] = body_result
                if self._has_violations_in_result(body_result):
                    has_violations = True

        # Sanitize headers
        header_result = self._sanitize_headers(request.headers)
        if header_result:
            sanitized_data["headers"] = header_result
            if self._has_violations_in_result(header_result):
                has_violations = True

        if has_violations:
            self.violation_stats["violations_detected"] += 1
            # Track violations by user and endpoint
            user_id = get_user_identifier(request)
            self.violation_stats["violations_by_user"][user_id] += 1
            self.violation_stats["violations_by_endpoint"][request.url.path] += 1

        return sanitized_data if sanitized_data else None

    def _sanitize_query_params(self, query_params) -> Optional[Dict[str, Any]]:
        """Sanitize query parameters"""
        sanitized = {}
        has_violations = False

        for key, value in query_params.items():
            result = self.sanitize_string(value, "string")
            sanitized[key] = result["sanitized"]

            if not result["is_valid"] or result["warnings"]:
                has_violations = True
                self._update_pattern_stats(result)

        return sanitized if has_violations else None

    def _sanitize_path_params(self, path_params: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Sanitize path parameters"""
        sanitized = {}
        has_violations = False

        for key, value in path_params.items():
            result = self.sanitize_string(value, "string")
            sanitized[key] = result["sanitized"]

            if not result["is_valid"] or result["warnings"]:
                has_violations = True
                self._update_pattern_stats(result)

        return sanitized if has_violations else None

    async def _sanitize_request_body(self, request: Request) -> Optional[Dict[str, Any]]:
        """Sanitize request body"""
        try:
            # Read body
            body = await request.body()
            if not body:
                return None

            # Parse JSON
            try:
                data = json.loads(body.decode("utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError):
                # If not JSON or not valid UTF-8 (binary data), skip sanitization
                # This is likely a file upload or binary data
                return None

            # Sanitize JSON data
            result = self.sanitize_string(str(data), "json")

            if not result["is_valid"] or result["warnings"]:
                self._update_pattern_stats(result)
                return {"json": result["sanitized"]}

            return None

        except Exception as e:
            logger.error(f"Error sanitizing request body: {str(e)}")
            return None

    def _sanitize_headers(self, headers) -> Optional[Dict[str, Any]]:
        """Sanitize request headers"""
        sanitized = {}
        has_violations = False

        # Only sanitize certain headers that might contain user input
        sensitive_headers = {
            "user-agent",
            "referer",
            "origin",
            "x-forwarded-for",
            "x-real-ip",
            "x-forwarded-proto",
            "x-forwarded-host",
        }

        for key, value in headers.items():
            if key.lower() in sensitive_headers:
                result = self.sanitize_string(value, "string")
                sanitized[key] = result["sanitized"]

                if not result["is_valid"] or result["warnings"]:
                    has_violations = True
                    self._update_pattern_stats(result)

        return sanitized if has_violations else None

    def _has_violations(self, sanitized_data: Dict[str, Any]) -> bool:
        """Check if sanitized data contains violations"""
        for section_data in sanitized_data.values():
            if self._has_violations_in_result(section_data):
                return True
        return False

    def _has_violations_in_result(self, result: Any) -> bool:
        """Check if a sanitization result contains violations"""
        if isinstance(result, dict):
            return any(self._has_violations_in_result(v) for v in result.values())
        elif isinstance(result, list):
            return any(self._has_violations_in_result(item) for item in result)
        else:
            return False

    def _update_pattern_stats(self, result: Dict[str, Any]):
        """Update violation pattern statistics"""
        for warning in result.get("warnings", []):
            pattern = warning.split(" ")[1] if " " in warning else "unknown"
            self.violation_stats["patterns_triggered"][pattern] = (
                self.violation_stats["patterns_triggered"].get(pattern, 0) + 1
            )

        for error in result.get("errors", []):
            pattern = error.split(" ")[1] if " " in error else "unknown"
            self.violation_stats["patterns_triggered"][pattern] = (
                self.violation_stats["patterns_triggered"].get(pattern, 0) + 1
            )

    async def _log_violations(self, request: Request, sanitized_data: Dict[str, Any], user_id: str):
        """Log security violations"""
        violation_info = {
            "method": request.method,
            "path": request.url.path,
            "client_ip": request.client.host if request.client else "unknown",
            "user_id": user_id,
            "user_agent": request.headers.get("user-agent", "unknown"),
            "violations": sanitized_data,
            "timestamp": str(request.state.get("timestamp", "")),
        }

        logger.warning(f"Security violation detected: {json.dumps(violation_info)}")

    def get_stats(self) -> Dict[str, Any]:
        """Get sanitization statistics"""
        stats = {
            **self.stats,
            **self.violation_stats
        }
        # Convert defaultdicts to regular dicts for JSON serialization
        stats["violations_by_user"] = dict(self.violation_stats["violations_by_user"])
        stats["violations_by_endpoint"] = dict(self.violation_stats["violations_by_endpoint"])
        return stats


def create_sanitizer_middleware(
    config: Optional[SanitizationConfig] = None,
    skip_paths: Optional[List[str]] = None,
    skip_methods: Optional[List[str]] = None,
    log_violations: bool = True,
) -> SanitizerMiddleware:
    """Create sanitizer middleware with configuration"""
    return SanitizerMiddleware(
        app=None,  # Will be set by FastAPI
        config=config,
        skip_paths=skip_paths,
        skip_methods=skip_methods,
        log_violations=log_violations,
    )


# Predefined configurations for common use cases
STRICT_CONFIG = SanitizationConfig(
    level=SanitizationLevel.STRICT,
    allow_html=False,
    allow_scripts=False,
    allow_sql_keywords=False
)

MODERATE_CONFIG = SanitizationConfig(
    level=SanitizationLevel.MODERATE,
    allow_html=False,
    allow_scripts=False,
    allow_sql_keywords=False
)

PERMISSIVE_CONFIG = SanitizationConfig(
    level=SanitizationLevel.PERMISSIVE,
    allow_html=True,
    allow_scripts=False,
    allow_sql_keywords=True
)
