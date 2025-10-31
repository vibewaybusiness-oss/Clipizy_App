"""
UNIFIED SERVICES MODULE
Consolidated service management with all utilities, base classes, and patterns
"""

# CORE IMPORTS
import asyncio
import logging
import os
import sys
import traceback
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Type, Union
from uuid import UUID
from contextlib import asynccontextmanager

from fastapi import HTTPException, UploadFile
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

# UNIFIED DI SYSTEM
from .di import (
    BaseService, ServiceConfig, ServiceMetrics, ServiceFactory,
    get_container, get_service_factory, service_method, retry_on_failure,
    service_context, inject_service, require_service,
    register_singleton, register_transient, register_scoped, get_service
)

# ERROR HANDLING
from api.services.errors import ResourceErrors, ServiceErrors, ValidationErrors
from api.config.logging import get_service_logger

# STORAGE
from api.config.settings import settings

# SERVICE IMPORTS
from .auth import auth_service
from .business import PRICES, credits_service, stripe_service
# from .functionalities import ProjectService, StatsService  # Module not found
from .storage import backend_storage_service

# GLOBAL SERVICE REGISTRY
service_registry = get_container()
service_factory = get_service_factory()
service_manager = get_container()
service_container = get_container()
service_health_monitor = get_container()


# UNIFIED LOGGING SYSTEM
class ServiceLogger:
    """Unified service logger with structured logging"""
    
    def __init__(self, service_name: str, log_level: str = "INFO"):
        self.service_name = service_name
        self.logger = get_service_logger()
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        self._formatter = logging.Formatter(
            f'%(asctime)s - {service_name} - %(levelname)s - %(message)s'
        )
        
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(self._formatter)
            self.logger.addHandler(handler)
    
    def _log_with_context(
        self,
        level: str,
        message: str,
        operation: Optional[str] = None,
        user_id: Optional[str] = None,
        request_id: Optional[str] = None,
        additional_data: Optional[Dict[str, Any]] = None,
        exc_info: bool = False
    ):
        log_data = {
            "service": self.service_name,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if operation:
            log_data["operation"] = operation
        if user_id:
            log_data["user_id"] = user_id
        if request_id:
            log_data["request_id"] = request_id
        if additional_data:
            log_data["data"] = additional_data
        
        formatted_message = f"{message}"
        if operation:
            formatted_message = f"[{operation}] {formatted_message}"
        if user_id:
            formatted_message = f"[User:{user_id}] {formatted_message}"
        if request_id:
            formatted_message = f"[Req:{request_id}] {formatted_message}"
        if additional_data:
            formatted_message = f"{formatted_message} | Data: {additional_data}"
        
        log_method = getattr(self.logger, level.lower())
        log_method(formatted_message, exc_info=exc_info)
    
    def info(self, message: str, operation: Optional[str] = None, user_id: Optional[str] = None, request_id: Optional[str] = None, additional_data: Optional[Dict[str, Any]] = None):
        self._log_with_context("INFO", message, operation, user_id, request_id, additional_data)
    
    def debug(self, message: str, operation: Optional[str] = None, user_id: Optional[str] = None, request_id: Optional[str] = None, additional_data: Optional[Dict[str, Any]] = None):
        self._log_with_context("DEBUG", message, operation, user_id, request_id, additional_data)
    
    def warning(self, message: str, operation: Optional[str] = None, user_id: Optional[str] = None, request_id: Optional[str] = None, additional_data: Optional[Dict[str, Any]] = None):
        self._log_with_context("WARNING", message, operation, user_id, request_id, additional_data)
    
    def error(self, message: str, operation: Optional[str] = None, user_id: Optional[str] = None, request_id: Optional[str] = None, additional_data: Optional[Dict[str, Any]] = None, exc_info: bool = True):
        self._log_with_context("ERROR", message, operation, user_id, request_id, additional_data, exc_info)
    
    def critical(self, message: str, operation: Optional[str] = None, user_id: Optional[str] = None, request_id: Optional[str] = None, additional_data: Optional[Dict[str, Any]] = None, exc_info: bool = True):
        self._log_with_context("CRITICAL", message, operation, user_id, request_id, additional_data, exc_info)


# UNIFIED ERROR HANDLING
class ErrorContext:
    """Context for error handling with additional information"""
    
    def __init__(
        self,
        operation: str,
        service: str,
        user_id: Optional[str] = None,
        request_id: Optional[str] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ):
        self.operation = operation
        self.service = service
        self.user_id = user_id
        self.request_id = request_id
        self.additional_data = additional_data or {}
        self.timestamp = datetime.utcnow()


class CentralizedErrorHandler:
    """Centralized error handling for all services"""
    
    def __init__(self):
        self.error_handlers: Dict[Type[Exception], callable] = {
            ValidationErrors: self._handle_validation_error,
            ResourceErrors: self._handle_resource_error,
            ServiceErrors: self._handle_service_error,
            SQLAlchemyError: self._handle_database_error,
            HTTPException: self._handle_http_error,
            ValueError: self._handle_value_error,
            TypeError: self._handle_type_error,
            KeyError: self._handle_key_error,
            AttributeError: self._handle_attribute_error,
            PermissionError: self._handle_permission_error,
            FileNotFoundError: self._handle_file_not_found_error,
            ConnectionError: self._handle_connection_error,
            TimeoutError: self._handle_timeout_error,
        }
        
        self.error_metrics: Dict[str, int] = {}
        self.error_history: List[Dict[str, Any]] = []
    
    def handle_error(
        self,
        error: Exception,
        context: ErrorContext,
        reraise: bool = True
    ) -> Optional[Dict[str, Any]]:
        self._log_error(error, context)
        self._record_error_metrics(error, context)
        
        error_type = type(error)
        handler = self._get_error_handler(error_type)
        error_response = handler(error, context)
        
        self._store_error_history(error, context, error_response)
        
        if reraise:
            raise error
        
        return error_response
    
    def _get_error_handler(self, error_type: Type[Exception]) -> callable:
        if error_type in self.error_handlers:
            return self.error_handlers[error_type]
        
        for handler_type, handler in self.error_handlers.items():
            if issubclass(error_type, handler_type):
                return handler
        
        return self._handle_generic_error
    
    def _handle_validation_error(self, error: ValidationErrors, context: ErrorContext) -> Dict[str, Any]:
        return {
            "error_type": "validation_error",
            "error_code": "VALIDATION_FAILED",
            "message": str(error),
            "details": getattr(error, 'details', {}),
            "field": getattr(error, 'field', None),
            "status_code": 400
        }
    
    def _handle_resource_error(self, error: ResourceErrors, context: ErrorContext) -> Dict[str, Any]:
        return {
            "error_type": "resource_error",
            "error_code": "RESOURCE_NOT_FOUND",
            "message": str(error),
            "resource_type": getattr(error, 'resource_type', None),
            "resource_id": getattr(error, 'resource_id', None),
            "status_code": 404
        }
    
    def _handle_service_error(self, error: ServiceErrors, context: ErrorContext) -> Dict[str, Any]:
        return {
            "error_type": "service_error",
            "error_code": "SERVICE_ERROR",
            "message": str(error),
            "service": context.service,
            "operation": context.operation,
            "status_code": 500
        }
    
    def _handle_database_error(self, error: SQLAlchemyError, context: ErrorContext) -> Dict[str, Any]:
        return {
            "error_type": "database_error",
            "error_code": "DATABASE_ERROR",
            "message": "Database operation failed",
            "service": context.service,
            "operation": context.operation,
            "status_code": 500
        }
    
    def _handle_http_error(self, error: HTTPException, context: ErrorContext) -> Dict[str, Any]:
        return {
            "error_type": "http_error",
            "error_code": "HTTP_ERROR",
            "message": error.detail,
            "status_code": error.status_code
        }
    
    def _handle_value_error(self, error: ValueError, context: ErrorContext) -> Dict[str, Any]:
        return {
            "error_type": "value_error",
            "error_code": "INVALID_VALUE",
            "message": str(error),
            "service": context.service,
            "operation": context.operation,
            "status_code": 400
        }
    
    def _handle_type_error(self, error: TypeError, context: ErrorContext) -> Dict[str, Any]:
        return {
            "error_type": "type_error",
            "error_code": "INVALID_TYPE",
            "message": str(error),
            "service": context.service,
            "operation": context.operation,
            "status_code": 400
        }
    
    def _handle_key_error(self, error: KeyError, context: ErrorContext) -> Dict[str, Any]:
        return {
            "error_type": "key_error",
            "error_code": "MISSING_KEY",
            "message": f"Missing key: {str(error)}",
            "service": context.service,
            "operation": context.operation,
            "status_code": 400
        }
    
    def _handle_attribute_error(self, error: AttributeError, context: ErrorContext) -> Dict[str, Any]:
        return {
            "error_type": "attribute_error",
            "error_code": "MISSING_ATTRIBUTE",
            "message": str(error),
            "service": context.service,
            "operation": context.operation,
            "status_code": 500
        }
    
    def _handle_permission_error(self, error: PermissionError, context: ErrorContext) -> Dict[str, Any]:
        return {
            "error_type": "permission_error",
            "error_code": "PERMISSION_DENIED",
            "message": str(error),
            "service": context.service,
            "operation": context.operation,
            "status_code": 403
        }
    
    def _handle_file_not_found_error(self, error: FileNotFoundError, context: ErrorContext) -> Dict[str, Any]:
        return {
            "error_type": "file_not_found_error",
            "error_code": "FILE_NOT_FOUND",
            "message": str(error),
            "service": context.service,
            "operation": context.operation,
            "status_code": 404
        }
    
    def _handle_connection_error(self, error: ConnectionError, context: ErrorContext) -> Dict[str, Any]:
        return {
            "error_type": "connection_error",
            "error_code": "CONNECTION_FAILED",
            "message": str(error),
            "service": context.service,
            "operation": context.operation,
            "status_code": 503
        }
    
    def _handle_timeout_error(self, error: TimeoutError, context: ErrorContext) -> Dict[str, Any]:
        return {
            "error_type": "timeout_error",
            "error_code": "OPERATION_TIMEOUT",
            "message": str(error),
            "service": context.service,
            "operation": context.operation,
            "status_code": 408
        }
    
    def _handle_generic_error(self, error: Exception, context: ErrorContext) -> Dict[str, Any]:
        return {
            "error_type": "generic_error",
            "error_code": "UNKNOWN_ERROR",
            "message": str(error),
            "service": context.service,
            "operation": context.operation,
            "status_code": 500
        }
    
    def _log_error(self, error: Exception, context: ErrorContext):
        log_data = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "service": context.service,
            "operation": context.operation,
            "user_id": context.user_id,
            "request_id": context.request_id,
            "timestamp": context.timestamp.isoformat(),
            "additional_data": context.additional_data
        }
        
        if isinstance(error, (ValidationErrors, ResourceErrors)):
            logging.warning(f"Service error: {log_data}")
        elif isinstance(error, ServiceErrors):
            logging.error(f"Service error: {log_data}")
        else:
            logging.error(f"Unexpected error: {log_data}", exc_info=True)
    
    def _record_error_metrics(self, error: Exception, context: ErrorContext):
        error_key = f"{context.service}.{context.operation}.{type(error).__name__}"
        self.error_metrics[error_key] = self.error_metrics.get(error_key, 0) + 1
    
    def _store_error_history(self, error: Exception, context: ErrorContext, error_response: Dict[str, Any]):
        error_record = {
            "timestamp": context.timestamp.isoformat(),
            "service": context.service,
            "operation": context.operation,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "error_response": error_response,
            "user_id": context.user_id,
            "request_id": context.request_id,
            "additional_data": context.additional_data
        }
        
        self.error_history.append(error_record)
        
        if len(self.error_history) > 1000:
            self.error_history = self.error_history[-1000:]


# UNIFIED MIXINS
class ServiceInitializationMixin:
    """Mixin for common service initialization patterns"""
    
    def __init__(self, service_name: str, db: Optional[Session] = None, **kwargs):
        self.service_name = service_name
        self.db = db
        self.logger = ServiceLogger(service_name)
        self.logger.info(f"{service_name} initialized")
        
        self._initialized = True
        self._start_time = datetime.utcnow()
        
        if hasattr(self, '_custom_init'):
            self._custom_init(**kwargs)
    
    def _custom_init(self, **kwargs):
        pass


class DatabaseOperationMixin:
    """Mixin for common database operations"""
    
    def _safe_db_operation(self, operation_name: str, operation_func, *args, **kwargs):
        try:
            self.logger.debug(f"Executing {operation_name}")
            result = operation_func(*args, **kwargs)
            self.logger.debug(f"{operation_name} completed successfully")
            return result
        except Exception as e:
            self.logger.error(f"{operation_name} failed: {str(e)}")
            if hasattr(self, 'db') and self.db:
                self.db.rollback()
            raise ServiceErrors.operation_failed(f"{operation_name} failed: {str(e)}")
    
    def _safe_db_commit(self, operation_name: str = "database commit"):
        try:
            self.db.commit()
            self.logger.debug(f"{operation_name} successful")
        except Exception as e:
            self.logger.error(f"{operation_name} failed: {str(e)}")
            self.db.rollback()
            raise ServiceErrors.operation_failed(f"{operation_name} failed: {str(e)}")
    
    def _safe_db_rollback(self, operation_name: str = "database rollback"):
        try:
            self.db.rollback()
            self.logger.debug(f"{operation_name} successful")
        except Exception as e:
            self.logger.error(f"{operation_name} failed: {str(e)}")
            raise ServiceErrors.operation_failed(f"{operation_name} failed: {str(e)}")


class ValidationMixin:
    """Mixin for common validation patterns"""
    
    def _validate_uuid(self, value: str, field_name: str = "id") -> str:
        try:
            UUID(value)
            return value
        except ValueError:
            raise ValidationErrors.invalid_input(field_name, value, "valid UUID format")
    
    def _validate_required(self, value: Any, field_name: str):
        if value is None or (isinstance(value, str) and not value.strip()):
            raise ValidationErrors.missing_field(field_name)
        return value
    
    def _validate_positive_number(self, value: Union[int, float], field_name: str) -> Union[int, float]:
        if value <= 0:
            raise ValidationErrors.invalid_input(field_name, value, "positive number")
        return value
    
    def _validate_string_length(self, value: str, field_name: str, min_length: int = 1, max_length: int = 255) -> str:
        if not isinstance(value, str):
            raise ValidationErrors.invalid_input(field_name, value, "string")
        
        if len(value) < min_length:
            raise ValidationErrors.invalid_input(field_name, value, f"minimum {min_length} characters")
        
        if len(value) > max_length:
            raise ValidationErrors.invalid_input(field_name, value, f"maximum {max_length} characters")
        
        return value.strip()
    
    def _validate_email(self, email: str) -> str:
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValidationErrors.invalid_input("email", email, "valid email format")
        return email.lower().strip()


class LoggingMixin:
    """Mixin for common logging patterns"""
    
    def _log_operation_start(self, operation_name: str, **kwargs):
        self.logger.info(f"Starting {operation_name}" + (f" with {kwargs}" if kwargs else ""))
    
    def _log_operation_success(self, operation_name: str, result: Any = None):
        if result:
            self.logger.info(f"{operation_name} completed successfully: {result}")
        else:
            self.logger.info(f"{operation_name} completed successfully")
    
    def _log_operation_error(self, operation_name: str, error: Exception):
        self.logger.error(f"{operation_name} failed: {str(error)}", exc_info=True)
    
    def _log_operation_warning(self, operation_name: str, message: str):
        self.logger.warning(f"{operation_name}: {message}")


class FileOperationMixin:
    """Mixin for common file operations"""
    
    def _generate_file_id(self) -> str:
        return str(uuid.uuid4())
    
    def _generate_file_path(self, project_id: str, file_type: str, filename: str, user_id: Optional[str] = None, project_type: str = "music-clip") -> str:
        if user_id:
            return f"users/{user_id}/projects/{project_type}/{project_id}/{file_type}/{filename}"
        return f"projects/{project_type}/{project_id}/{file_type}/{filename}"
    
    def _validate_file_upload(self, file: UploadFile, max_size_mb: int = 100, allowed_types: List[str] = None) -> UploadFile:
        if not file:
            raise ValidationErrors.missing_field("file")
        
        if not file.filename:
            raise ValidationErrors.invalid_input("filename", "empty", "valid filename")
        
        if hasattr(file, 'size') and file.size:
            size_mb = file.size / (1024 * 1024)
            if size_mb > max_size_mb:
                raise ValidationErrors.invalid_input("file_size", f"{size_mb:.2f}MB", f"maximum {max_size_mb}MB")
        
        if allowed_types:
            file_extension = file.filename.split('.')[-1].lower() if '.' in file.filename else ''
            if file_extension not in allowed_types:
                raise ValidationErrors.invalid_input("file_type", file_extension, f"one of {allowed_types}")
        
        return file
    
    def _extract_file_metadata(self, file: UploadFile) -> Dict[str, Any]:
        return {
            "filename": file.filename,
            "content_type": file.content_type,
            "size": getattr(file, 'size', None),
            "uploaded_at": datetime.utcnow().isoformat()
        }


class AsyncOperationMixin:
    """Mixin for common async operations"""
    
    async def _execute_with_timeout(self, operation_name: str, coro, timeout: int = 30):
        try:
            self.logger.debug(f"Executing {operation_name} with {timeout}s timeout")
            result = await asyncio.wait_for(coro, timeout=timeout)
            self.logger.debug(f"{operation_name} completed within timeout")
            return result
        except asyncio.TimeoutError:
            self.logger.error(f"{operation_name} timed out after {timeout}s")
            raise ServiceErrors.operation_failed(f"{operation_name} timed out")
        except Exception as e:
            self.logger.error(f"{operation_name} failed: {str(e)}")
            raise ServiceErrors.operation_failed(f"{operation_name} failed: {str(e)}")
    
    async def _retry_operation(self, operation_name: str, coro, max_retries: int = 3, delay: float = 1.0):
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                self.logger.debug(f"Executing {operation_name} (attempt {attempt + 1}/{max_retries})")
                result = await coro()
                self.logger.debug(f"{operation_name} succeeded on attempt {attempt + 1}")
                return result
            except Exception as e:
                last_exception = e
                if attempt < max_retries - 1:
                    wait_time = delay * (2 ** attempt)
                    self.logger.warning(f"{operation_name} failed on attempt {attempt + 1}, retrying in {wait_time}s: {str(e)}")
                    await asyncio.sleep(wait_time)
                else:
                    self.logger.error(f"{operation_name} failed after {max_retries} attempts: {str(e)}")
        
        raise last_exception


class ConfigurationMixin:
    """Mixin for common configuration patterns"""
    
    def _get_config_value(self, key: str, default: Any = None, required: bool = False) -> Any:
        value = os.getenv(key, default)
        
        if required and value is None:
            raise ServiceErrors.configuration_error(f"Required configuration '{key}' not found")
        
        return value
    
    def _get_int_config(self, key: str, default: int = None, required: bool = False) -> int:
        value = self._get_config_value(key, default, required)
        
        if value is not None:
            try:
                return int(value)
            except ValueError:
                raise ServiceErrors.configuration_error(f"Configuration '{key}' must be an integer")
        
        return value
    
    def _get_bool_config(self, key: str, default: bool = None, required: bool = False) -> bool:
        value = self._get_config_value(key, default, required)
        
        if value is not None:
            if isinstance(value, bool):
                return value
            if isinstance(value, str):
                return value.lower() in ('true', '1', 'yes', 'on')
            return bool(value)
        
        return value


class MetricsMixin:
    """Mixin for common metrics patterns"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._operation_count = 0
        self._operation_times = []
        self._error_count = 0
    
    def _record_operation(self, operation_name: str, duration: float, success: bool = True):
        self._operation_count += 1
        self._operation_times.append(duration)
        
        if not success:
            self._error_count += 1
        
        if len(self._operation_times) > 1000:
            self._operation_times = self._operation_times[-1000:]
    
    def _get_metrics(self) -> Dict[str, Any]:
        if not self._operation_times:
            return {
                "total_operations": 0,
                "error_count": 0,
                "error_rate": 0.0,
                "average_duration": 0.0
            }
        
        return {
            "total_operations": self._operation_count,
            "error_count": self._error_count,
            "error_rate": self._error_count / self._operation_count if self._operation_count > 0 else 0.0,
            "average_duration": sum(self._operation_times) / len(self._operation_times),
            "min_duration": min(self._operation_times),
            "max_duration": max(self._operation_times)
        }


# UNIFIED BASE SERVICE CLASSES
class DatabaseService(BaseService):
    """Base service for database operations"""
    
    def __init__(self, config: ServiceConfig, db: Session):
        super().__init__(config, db)
        self.db = db
    
    async def _service_health_check(self) -> Dict[str, Any]:
        try:
            self.db.execute("SELECT 1")
            return {
                "database_connected": True,
                "database_status": "healthy"
            }
        except Exception as e:
            return {
                "database_connected": False,
                "database_status": "unhealthy",
                "database_error": str(e)
            }
    
    async def _service_cleanup(self):
        try:
            if self.db:
                self.db.close()
        except Exception as e:
            self.logger.error(f"Error closing database connection: {e}")


class ExternalService(BaseService):
    """Base service for external API integrations"""
    
    def __init__(self, config: ServiceConfig, base_url: str, api_key: Optional[str] = None):
        super().__init__(config)
        self.base_url = base_url
        self.api_key = api_key
        self._session = None
    
    async def _service_health_check(self) -> Dict[str, Any]:
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/health", timeout=5.0)
                return {
                    "external_service_connected": response.status_code == 200,
                    "external_service_status": "healthy" if response.status_code == 200 else "unhealthy",
                    "response_time_ms": response.elapsed.total_seconds() * 1000
                }
        except Exception as e:
            return {
                "external_service_connected": False,
                "external_service_status": "unhealthy",
                "external_service_error": str(e)
            }
    
    async def _service_cleanup(self):
        if self._session:
            await self._session.aclose()


class AsyncService(BaseService):
    """Base service for async operations"""
    
    def __init__(self, config: ServiceConfig):
        super().__init__(config)
        self._background_tasks: List[asyncio.Task] = []
    
    async def _service_health_check(self) -> Dict[str, Any]:
        return {
            "background_tasks": len(self._background_tasks),
            "active_tasks": len([task for task in self._background_tasks if not task.done()]),
            "async_status": "healthy"
        }
    
    async def _service_cleanup(self):
        for task in self._background_tasks:
            if not task.done():
                task.cancel()
        
        if self._background_tasks:
            await asyncio.gather(*self._background_tasks, return_exceptions=True)
    
    def add_background_task(self, coro):
        task = asyncio.create_task(coro)
        self._background_tasks.append(task)
        return task


class CommonServiceBase(
    ServiceInitializationMixin,
    DatabaseOperationMixin,
    ValidationMixin,
    LoggingMixin,
    FileOperationMixin,
    AsyncOperationMixin,
    ConfigurationMixin,
    MetricsMixin
):
    """Base class combining all common service utilities"""
    
    def __init__(self, service_name: str, db: Optional[Session] = None, **kwargs):
        ServiceInitializationMixin.__init__(self, service_name, db, **kwargs)
        DatabaseOperationMixin.__init__(self)
        ValidationMixin.__init__(self)
        LoggingMixin.__init__(self)
        FileOperationMixin.__init__(self)
        AsyncOperationMixin.__init__(self)
        ConfigurationMixin.__init__(self)
        MetricsMixin.__init__(self)
    
    async def health_check(self) -> Dict[str, Any]:
        return {
            "service": self.service_name,
            "status": "healthy",
            "uptime_seconds": (datetime.utcnow() - self._start_time).total_seconds(),
            "metrics": self._get_metrics(),
            "timestamp": datetime.utcnow().isoformat()
        }


# UTILITY FUNCTIONS
def create_service_logger(service_name: str) -> ServiceLogger:
    return ServiceLogger(service_name)


def generate_unique_id() -> str:
    return str(uuid.uuid4())


def format_timestamp(dt: Optional[datetime] = None) -> str:
    if dt is None:
        dt = datetime.utcnow()
    return dt.isoformat() + "Z"


def calculate_duration(start_time: datetime, end_time: Optional[datetime] = None) -> float:
    if end_time is None:
        end_time = datetime.utcnow()
    return (end_time - start_time).total_seconds()


def safe_get_dict_value(data: Dict[str, Any], key: str, default: Any = None) -> Any:
    return data.get(key, default)


def merge_dicts(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    result = {}
    for d in dicts:
        if d:
            result.update(d)
    return result


def chunk_list(items: List[Any], chunk_size: int) -> List[List[Any]]:
    return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]


def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> Dict[str, Any]:
    missing_fields = [field for field in required_fields if field not in data or data[field] is None]
    if missing_fields:
        raise ValidationErrors.missing_fields(missing_fields)
    return data


def sanitize_filename(filename: str) -> str:
    import re
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    sanitized = sanitized.strip(' .')
    if not sanitized:
        sanitized = f"file_{uuid.uuid4().hex[:8]}"
    return sanitized


# ERROR HANDLING DECORATORS
def handle_errors(service_name: str, operation_name: str, reraise: bool = True):
    """Decorator for automatic error handling"""
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            context = ErrorContext(
                operation=operation_name,
                service=service_name,
                user_id=kwargs.get('user_id'),
                request_id=kwargs.get('request_id'),
                additional_data=kwargs.get('additional_data')
            )
            
            try:
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    return func(*args, **kwargs)
            except Exception as e:
                error_handler.handle_error(e, context, reraise=reraise)
        
        def sync_wrapper(*args, **kwargs):
            context = ErrorContext(
                operation=operation_name,
                service=service_name,
                user_id=kwargs.get('user_id'),
                request_id=kwargs.get('request_id'),
                additional_data=kwargs.get('additional_data')
            )
            
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_handler.handle_error(e, context, reraise=reraise)
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


class ErrorHandlingContext:
    """Context manager for error handling"""
    
    def __init__(self, service_name: str, operation_name: str, **context_data):
        self.service_name = service_name
        self.operation_name = operation_name
        self.context_data = context_data
        self.context = None
    
    def __enter__(self):
        self.context = ErrorContext(
            operation=self.operation_name,
            service=self.service_name,
            **self.context_data
        )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            error_handler.handle_error(exc_val, self.context, reraise=False)
            return True


# GLOBAL INSTANCES
error_handler = CentralizedErrorHandler()

# SERVICE INITIALIZATION
storage_service = backend_storage_service
# project_service = ProjectService(storage_service)  # ProjectService not available
media_service = backend_storage_service


# EXPORT ALL UNIFIED COMPONENTS
__all__ = [
    # Core DI System
    "BaseService", "ServiceConfig", "ServiceMetrics", "ServiceFactory",
    "service_registry", "service_factory", "service_method", "retry_on_failure",
    "service_context", "inject_service", "require_service",
    "register_singleton", "register_transient", "register_scoped", "get_service",
    
    # Service Management
    "service_manager", "service_container", "service_health_monitor",
    
    # Logging System
    "ServiceLogger", "LoggingMixin", "create_service_logger",
    
    # Error Handling
    "ErrorContext", "CentralizedErrorHandler", "error_handler", "handle_errors",
    "ErrorHandlingContext",
    
    # Base Service Classes
    "DatabaseService", "ExternalService", "AsyncService", "CommonServiceBase",
    
    # Mixins
    "ServiceInitializationMixin", "DatabaseOperationMixin", "ValidationMixin",
    "FileOperationMixin", "AsyncOperationMixin", "ConfigurationMixin", "MetricsMixin",
    
    # Utility Functions
    "generate_unique_id", "format_timestamp", "calculate_duration",
    "safe_get_dict_value", "merge_dicts", "chunk_list", "validate_required_fields",
    "sanitize_filename",
    
    # Services
    "auth_service",
    "backend_storage_service", "credits_service", "stripe_service", "PRICES"
]
