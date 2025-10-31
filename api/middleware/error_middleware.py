"""
Global Error Handling Middleware
Provides centralized error handling for all API endpoints
"""

import logging
import traceback
from typing import Union
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from api.services.errors import ErrorHandler, ErrorCodes

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


class GlobalErrorHandler:
    """Global error handling middleware"""
    
    @staticmethod
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        """
        Handle HTTP exceptions with consistent error format
        
        Args:
            request: FastAPI request object
            exc: HTTPException instance
            
        Returns:
            JSONResponse with error details
        """
        # Get user identifier
        user_id = get_user_identifier(request)
        
        # Log the error
        logger.warning(
            f"HTTP {exc.status_code} error on {request.method} {request.url.path}: {exc.detail}",
            extra={
                "status_code": exc.status_code,
                "method": request.method,
                "path": request.url.path,
                "detail": exc.detail,
                "user_id": user_id,
                "request_id": getattr(request.state, 'request_id', None)
            }
        )
        
        # Ensure error detail is in the correct format
        if isinstance(exc.detail, dict):
            error_detail = exc.detail
        else:
            error_detail = {
                "error_code": ErrorCodes.INTERNAL_SERVER_ERROR,
                "message": str(exc.detail)
            }
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": error_detail,
                "path": request.url.path,
                "method": request.method,
                "user_id": user_id,
                "request_id": getattr(request.state, 'request_id', None)
            }
        )
    
    @staticmethod
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        """
        Handle validation errors with detailed field information
        
        Args:
            request: FastAPI request object
            exc: RequestValidationError instance
            
        Returns:
            JSONResponse with validation error details
        """
        # Get user identifier
        user_id = get_user_identifier(request)
        
        # Log the validation error
        logger.warning(
            f"Validation error on {request.method} {request.url.path}: {exc.errors()}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "errors": exc.errors(),
                "user_id": user_id,
                "request_id": getattr(request.state, 'request_id', None)
            }
        )
        
        # Format validation errors
        formatted_errors = []
        for error in exc.errors():
            formatted_errors.append({
                "field": ".".join(str(loc) for loc in error["loc"]),
                "message": error["msg"],
                "type": error["type"],
                "input": error.get("input")
            })
        
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "error": {
                    "error_code": ErrorCodes.VALIDATION_ERROR,
                    "message": "Validation failed",
                    "validation_errors": formatted_errors
                },
                "path": request.url.path,
                "method": request.method,
                "user_id": user_id,
                "request_id": getattr(request.state, 'request_id', None)
            }
        )
    
    @staticmethod
    async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """
        Handle general exceptions with proper logging and error format
        
        Args:
            request: FastAPI request object
            exc: Exception instance
            
        Returns:
            JSONResponse with error details
        """
        # Get user identifier
        user_id = get_user_identifier(request)
        
        # Log the full exception with traceback
        logger.error(
            f"Unhandled exception on {request.method} {request.url.path}: {str(exc)}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "exception_type": type(exc).__name__,
                "traceback": traceback.format_exc(),
                "user_id": user_id,
                "request_id": getattr(request.state, 'request_id', None)
            },
            exc_info=True
        )
        
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": {
                    "error_code": ErrorCodes.INTERNAL_SERVER_ERROR,
                    "message": "An unexpected error occurred",
                    "details": "Please try again later or contact support if the problem persists"
                },
                "path": request.url.path,
                "method": request.method,
                "user_id": user_id,
                "request_id": getattr(request.state, 'request_id', None)
            }
        )
    
    @staticmethod
    async def starlette_http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        """
        Handle Starlette HTTP exceptions
        
        Args:
            request: FastAPI request object
            exc: StarletteHTTPException instance
            
        Returns:
            JSONResponse with error details
        """
        # Get user identifier
        user_id = get_user_identifier(request)
        
        # Log the error
        logger.warning(
            f"Starlette HTTP {exc.status_code} error on {request.method} {request.url.path}: {exc.detail}",
            extra={
                "status_code": exc.status_code,
                "method": request.method,
                "path": request.url.path,
                "detail": exc.detail,
                "user_id": user_id,
                "request_id": getattr(request.state, 'request_id', None)
            }
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "error_code": ErrorCodes.INTERNAL_SERVER_ERROR,
                    "message": str(exc.detail)
                },
                "path": request.url.path,
                "method": request.method,
                "user_id": user_id,
                "request_id": getattr(request.state, 'request_id', None)
            }
        )


def setup_error_handlers(app):
    """
    Setup global error handlers for the FastAPI application
    
    Args:
        app: FastAPI application instance
    """
    # Add exception handlers in order of specificity (most specific first)
    app.add_exception_handler(RequestValidationError, GlobalErrorHandler.validation_exception_handler)
    app.add_exception_handler(HTTPException, GlobalErrorHandler.http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, GlobalErrorHandler.starlette_http_exception_handler)
    # Add general Exception handler as fallback to ensure all errors return JSON
    app.add_exception_handler(Exception, GlobalErrorHandler.general_exception_handler)
    
    logger.info("Global error handlers configured successfully")
