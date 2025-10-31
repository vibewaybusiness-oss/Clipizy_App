"""
Centralized Error Handling Utilities
Provides consistent error handling patterns across the application
"""

import logging
from typing import Any, Dict, List, Optional, Union
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class ErrorCodes:
    """Standard error codes for consistent error handling"""
    
    # Authentication & Authorization
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    INSUFFICIENT_PERMISSIONS = "INSUFFICIENT_PERMISSIONS"
    
    # Resource Management
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    RESOURCE_ALREADY_EXISTS = "RESOURCE_ALREADY_EXISTS"
    RESOURCE_CONFLICT = "RESOURCE_CONFLICT"
    RESOURCE_LIMIT_EXCEEDED = "RESOURCE_LIMIT_EXCEEDED"
    
    # Validation
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_INPUT = "INVALID_INPUT"
    MISSING_REQUIRED_FIELD = "MISSING_REQUIRED_FIELD"
    INVALID_FILE_TYPE = "INVALID_FILE_TYPE"
    FILE_TOO_LARGE = "FILE_TOO_LARGE"
    
    # Business Logic
    INSUFFICIENT_CREDITS = "INSUFFICIENT_CREDITS"
    OPERATION_NOT_ALLOWED = "OPERATION_NOT_ALLOWED"
    QUOTA_EXCEEDED = "QUOTA_EXCEEDED"
    FEATURE_NOT_AVAILABLE = "FEATURE_NOT_AVAILABLE"
    
    # External Services
    EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    TIMEOUT_ERROR = "TIMEOUT_ERROR"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    
    # System
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    DATABASE_ERROR = "DATABASE_ERROR"
    CONFIGURATION_ERROR = "CONFIGURATION_ERROR"
    MAINTENANCE_MODE = "MAINTENANCE_MODE"


class ErrorHandler:
    """Centralized error handling utilities"""
    
    @staticmethod
    def not_found(
        resource: str = "Resource",
        resource_id: Optional[str] = None,
        details: Optional[str] = None
    ) -> HTTPException:
        """
        Create a 404 Not Found error
        
        Args:
            resource: Type of resource (e.g., "Project", "User", "Track")
            resource_id: ID of the resource if available
            details: Additional details
            
        Returns:
            HTTPException with 404 status
        """
        message = f"{resource} not found"
        if resource_id:
            message += f" (ID: {resource_id})"
        if details:
            message += f": {details}"
            
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_code": ErrorCodes.RESOURCE_NOT_FOUND,
                "message": message,
                "resource": resource,
                "resource_id": resource_id
            }
        )
    
    @staticmethod
    def bad_request(
        message: str,
        error_code: str = ErrorCodes.VALIDATION_ERROR,
        details: Optional[Dict[str, Any]] = None
    ) -> HTTPException:
        """
        Create a 400 Bad Request error
        
        Args:
            message: Error message
            error_code: Error code
            details: Additional error details
            
        Returns:
            HTTPException with 400 status
        """
        error_detail = {
            "error_code": error_code,
            "message": message
        }
        if details:
            error_detail["details"] = details
            
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_detail
        )
    
    @staticmethod
    def unauthorized(
        message: str = "Authentication required",
        error_code: str = ErrorCodes.UNAUTHORIZED,
        details: Optional[Dict[str, Any]] = None
    ) -> HTTPException:
        """
        Create a 401 Unauthorized error
        
        Args:
            message: Error message
            error_code: Error code
            details: Additional error details
            
        Returns:
            HTTPException with 401 status
        """
        error_detail = {
            "error_code": error_code,
            "message": message
        }
        if details:
            error_detail["details"] = details
            
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_detail
        )
    
    @staticmethod
    def forbidden(
        message: str = "Access denied",
        error_code: str = ErrorCodes.FORBIDDEN,
        details: Optional[Dict[str, Any]] = None
    ) -> HTTPException:
        """
        Create a 403 Forbidden error
        
        Args:
            message: Error message
            error_code: Error code
            details: Additional error details
            
        Returns:
            HTTPException with 403 status
        """
        error_detail = {
            "error_code": error_code,
            "message": message
        }
        if details:
            error_detail["details"] = details
            
        return HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=error_detail
        )
    
    @staticmethod
    def internal_server_error(
        message: str = "Internal server error",
        error_code: str = ErrorCodes.INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None,
        log_error: bool = True
    ) -> HTTPException:
        """
        Create a 500 Internal Server Error
        
        Args:
            message: Error message
            error_code: Error code
            details: Additional error details
            log_error: Whether to log the error
            
        Returns:
            HTTPException with 500 status
        """
        if log_error:
            logger.error(f"Internal server error: {message}", extra={"details": details})
            
        error_detail = {
            "error_code": error_code,
            "message": message
        }
        if details:
            error_detail["details"] = details
            
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_detail
        )
    
    @staticmethod
    def service_unavailable(
        service_name: str,
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> HTTPException:
        """
        Create a 503 Service Unavailable error
        
        Args:
            service_name: Name of the unavailable service
            message: Custom error message
            details: Additional error details
            
        Returns:
            HTTPException with 503 status
        """
        error_message = message or f"{service_name} service is currently unavailable"
        
        error_detail = {
            "error_code": ErrorCodes.SERVICE_UNAVAILABLE,
            "message": error_message,
            "service": service_name
        }
        if details:
            error_detail["details"] = details
            
        return HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=error_detail
        )
    
    @staticmethod
    def conflict(
        message: str,
        error_code: str = ErrorCodes.RESOURCE_CONFLICT,
        details: Optional[Dict[str, Any]] = None
    ) -> HTTPException:
        """
        Create a 409 Conflict error
        
        Args:
            message: Error message
            error_code: Error code
            details: Additional error details
            
        Returns:
            HTTPException with 409 status
        """
        error_detail = {
            "error_code": error_code,
            "message": message
        }
        if details:
            error_detail["details"] = details
            
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=error_detail
        )
    
    @staticmethod
    def too_many_requests(
        message: str = "Too many requests",
        retry_after: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> HTTPException:
        """
        Create a 429 Too Many Requests error
        
        Args:
            message: Error message
            retry_after: Seconds to wait before retrying
            details: Additional error details
            
        Returns:
            HTTPException with 429 status
        """
        error_detail = {
            "error_code": ErrorCodes.RATE_LIMIT_EXCEEDED,
            "message": message
        }
        if details:
            error_detail["details"] = details
        if retry_after:
            error_detail["retry_after"] = retry_after
            
        return HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=error_detail
        )


class ResourceErrors:
    """Specific error handlers for common resources"""
    
    @staticmethod
    def project_not_found(project_id: Optional[str] = None) -> HTTPException:
        """Project not found error"""
        return ErrorHandler.not_found("Project", project_id)
    
    @staticmethod
    def user_not_found(user_id: Optional[str] = None) -> HTTPException:
        """User not found error"""
        return ErrorHandler.not_found("User", user_id)
    
    @staticmethod
    def track_not_found(track_id: Optional[str] = None) -> HTTPException:
        """Track not found error"""
        return ErrorHandler.not_found("Track", track_id)
    
    @staticmethod
    def job_not_found(job_id: Optional[str] = None) -> HTTPException:
        """Job not found error"""
        return ErrorHandler.not_found("Job", job_id)
    
    @staticmethod
    def file_not_found(file_path: Optional[str] = None) -> HTTPException:
        """File not found error"""
        return ErrorHandler.not_found("File", file_path)
    
    @staticmethod
    def invalid_file_type(allowed_types: List[str]) -> HTTPException:
        """Invalid file type error"""
        return ErrorHandler.bad_request(
            f"Invalid file type. Allowed types: {', '.join(allowed_types)}",
            ErrorCodes.INVALID_FILE_TYPE,
            {"allowed_types": allowed_types}
        )
    
    @staticmethod
    def file_too_large(max_size: str) -> HTTPException:
        """File too large error"""
        return ErrorHandler.bad_request(
            f"File too large. Maximum size: {max_size}",
            ErrorCodes.FILE_TOO_LARGE,
            {"max_size": max_size}
        )
    
    @staticmethod
    def insufficient_credits(required: int, available: int) -> HTTPException:
        """Insufficient credits error"""
        return ErrorHandler.bad_request(
            f"Insufficient credits. Required: {required}, Available: {available}",
            ErrorCodes.INSUFFICIENT_CREDITS,
            {"required": required, "available": available}
        )


class ValidationErrors:
    """Validation-specific error handlers"""
    
    @staticmethod
    def missing_required_field(field_name: str) -> HTTPException:
        """Missing required field error"""
        return ErrorHandler.bad_request(
            f"Missing required field: {field_name}",
            ErrorCodes.MISSING_REQUIRED_FIELD,
            {"field": field_name}
        )
    
    @staticmethod
    def invalid_input(field_name: str, value: Any = None, reason: str = "invalid value") -> HTTPException:
        """Invalid input error"""
        message = f"Invalid input for {field_name}: {reason}"
        details = {"field": field_name, "reason": reason}
        if value is not None:
            details["value"] = str(value)
        return ErrorHandler.bad_request(
            message,
            ErrorCodes.INVALID_INPUT,
            details
        )
    
    @staticmethod
    def validation_failed(errors: List[Dict[str, Any]]) -> HTTPException:
        """Validation failed error"""
        return ErrorHandler.bad_request(
            "Validation failed",
            ErrorCodes.VALIDATION_ERROR,
            {"validation_errors": errors}
        )
    
    @staticmethod
    def invalid_credentials() -> HTTPException:
        """Invalid credentials error"""
        return ErrorHandler.unauthorized(
            "Invalid email or password",
            ErrorCodes.INVALID_CREDENTIALS,
            {"field": "credentials"}
        )
    
    @staticmethod
    def invalid_token() -> HTTPException:
        """Invalid token error"""
        return ErrorHandler.unauthorized(
            "Invalid or expired token",
            ErrorCodes.TOKEN_EXPIRED,
            {"field": "token"}
        )
    
    @staticmethod
    def invalid_amount(message: str = "Invalid amount") -> HTTPException:
        """Invalid amount error"""
        return ErrorHandler.bad_request(
            message,
            ErrorCodes.INVALID_INPUT,
            {"field": "amount"}
        )
    
    @staticmethod
    def missing_token() -> HTTPException:
        """Missing token error"""
        return ErrorHandler.unauthorized(
            "Authentication token is required",
            ErrorCodes.UNAUTHORIZED,
            {"field": "token"}
        )
    
    @staticmethod
    def oauth_user_info_failed() -> HTTPException:
        """OAuth user info retrieval failed"""
        return ErrorHandler.bad_request(
            "Failed to retrieve user information from OAuth provider",
            ErrorCodes.EXTERNAL_SERVICE_ERROR,
            {"provider": "oauth"}
        )
    
    @staticmethod
    def oauth_user_creation_failed() -> HTTPException:
        """OAuth user creation failed"""
        return ErrorHandler.internal_server_error(
            "Failed to create user from OAuth data",
            ErrorCodes.INTERNAL_SERVER_ERROR,
            {"provider": "oauth"}
        )
    
    @staticmethod
    def missing_field(field_name: str) -> HTTPException:
        """Missing field error (alias for missing_required_field)"""
        return ValidationErrors.missing_required_field(field_name)
    
    @staticmethod
    def missing_fields(field_names: List[str]) -> HTTPException:
        """Multiple missing fields error"""
        return ErrorHandler.bad_request(
            f"Missing required fields: {', '.join(field_names)}",
            ErrorCodes.MISSING_REQUIRED_FIELD,
            {"fields": field_names}
        )
    
    @staticmethod
    def missing_required_fields(field_names: List[str]) -> HTTPException:
        """Missing required fields error (alias for missing_fields)"""
        return ValidationErrors.missing_fields(field_names)
    
    @staticmethod
    def insufficient_credits() -> HTTPException:
        """Insufficient credits error"""
        return ErrorHandler.bad_request(
            "Insufficient credits for this operation",
            ErrorCodes.INSUFFICIENT_CREDITS,
            {"field": "credits"}
        )


class ServiceErrors:
    """Service-specific error handlers"""
    
    @staticmethod
    def database_error(operation: str, details: Optional[str] = None) -> HTTPException:
        """Database operation error"""
        message = f"Database error during {operation}"
        if details:
            message += f": {details}"
        return ErrorHandler.internal_server_error(
            message,
            ErrorCodes.DATABASE_ERROR,
            {"operation": operation, "details": details}
        )
    
    @staticmethod
    def storage_error(operation: str, details: Optional[str] = None) -> HTTPException:
        """Storage operation error"""
        message = f"Storage error during {operation}"
        if details:
            message += f": {details}"
        return ErrorHandler.internal_server_error(
            message,
            ErrorCodes.EXTERNAL_SERVICE_ERROR,
            {"operation": operation, "details": details}
        )
    
    @staticmethod
    def ai_service_error(service_name: str, details: Optional[str] = None) -> HTTPException:
        """AI service error"""
        message = f"{service_name} service error"
        if details:
            message += f": {details}"
        return ErrorHandler.service_unavailable(
            service_name,
            message,
            {"details": details}
        )


def handle_exception(
    exception: Exception,
    context: str = "Unknown operation",
    log_error: bool = True
) -> HTTPException:
    """
    Handle generic exceptions and convert to appropriate HTTPException
    
    Args:
        exception: The exception to handle
        context: Context where the exception occurred
        log_error: Whether to log the error
        
    Returns:
        Appropriate HTTPException
    """
    if log_error:
        logger.error(f"Exception in {context}: {str(exception)}", exc_info=True)
    
    # Handle specific exception types
    if isinstance(exception, HTTPException):
        return exception
    
    # Handle common exception patterns
    error_message = str(exception)
    
    if "not found" in error_message.lower():
        return ErrorHandler.not_found(details=error_message)
    elif "permission" in error_message.lower() or "access" in error_message.lower():
        return ErrorHandler.forbidden(error_message)
    elif "validation" in error_message.lower() or "invalid" in error_message.lower():
        return ErrorHandler.bad_request(error_message)
    else:
        return ErrorHandler.internal_server_error(
            f"Error in {context}: {error_message}",
            log_error=False  # Already logged above
        )


# Convenience functions for common error patterns
def not_found(resource: str, resource_id: Optional[str] = None) -> HTTPException:
    """Convenience function for not found errors"""
    return ErrorHandler.not_found(resource, resource_id)

def bad_request(message: str, error_code: str = ErrorCodes.VALIDATION_ERROR) -> HTTPException:
    """Convenience function for bad request errors"""
    return ErrorHandler.bad_request(message, error_code)

def internal_error(message: str, details: Optional[Dict[str, Any]] = None) -> HTTPException:
    """Convenience function for internal server errors"""
    return ErrorHandler.internal_server_error(message, details=details)

def unauthorized(message: str = "Authentication required") -> HTTPException:
    """Convenience function for unauthorized errors"""
    return ErrorHandler.unauthorized(message)

def forbidden(message: str = "Access denied") -> HTTPException:
    """Convenience function for forbidden errors"""
    return ErrorHandler.forbidden(message)
