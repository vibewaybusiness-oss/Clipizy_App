"""
UNIFIED SERVICES PACKAGE
Consolidated service management with all utilities, base classes, and patterns
"""

# Import unified services module
from .services import *

# Import additional services not yet unified
from .auth import auth_service
from .business import PRICES, credits_service, stripe_service
# from .functionalities import ProjectService, StatsService  # Module not found
# from .media import MediaService  # Available from storage
from .storage import (
    backend_storage_service
)
from .database import (
    get_db, get_optimized_db, create_tables, drop_tables,
    get_database_url, get_connection_pool_status, test_database_connection,
    close_database_connections, Base, metadata, GUID, engine, SessionLocal
)
# from .sanitization import InputSanitizer, SanitizerConfig, SanitizerResult, sanitize_input  # Module not found
# Legacy storage service removed - use centralized services instead

# Initialize services using unified system
# project_service initialization removed - ProjectService not available

# Export all services and utilities
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
    "backend_storage_service",
    "auth_service",
    "credits_service", "stripe_service", "PRICES",
    # Database utilities
    "get_db", "get_optimized_db", "create_tables", "drop_tables",
    "get_database_url", "get_connection_pool_status", "test_database_connection",
    "close_database_connections", "Base", "metadata", "GUID", "engine", "SessionLocal",
    # Sanitization services (module not found)
    # "InputSanitizer", "SanitizerConfig", "SanitizerResult", "sanitize_input"
]
