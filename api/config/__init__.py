"""
Configuration Package
Centralized configuration management with service integration
"""

from .manager import (
    ConfigurationManager,
    get_config_manager,
    get_config_value,
    set_config_value,
    validate_configuration,
    get_configuration_summary,
    reload_configuration,
    Environment,
    LogLevel,
    DatabaseConfig,
    StorageConfig,
    SecurityConfig,
    APIConfig,
    LoggingConfig,
    ProducerAIConfig,
    FileProcessingConfig,
    PerformanceConfig,
    ExternalServicesConfig,
    BusinessConfig
)

from .decorators import (
    config_value,
    config_section,
    validate_config,
    config_dependent,
    environment_specific,
    config_cache,
    config_logger,
    config_metrics,
    ConfigProperty,
    ConfigSection,
    ConfigMixin,
    fastapi_config_dependency,
    fastapi_config_section_dependency,
    validate_database_config,
    validate_storage_config,
    validate_security_config,
    auto_reload_config,
    config_change_listener
)

from .logging import (
    setup_logger,
    get_logger,
    get_service_logger,
    get_middleware_logger,
    get_api_logger,
    get_router_logger,
    MiddlewareLogger,
    get_auth_logger,
    get_storage_logger,
    get_prompt_logger,
    get_job_logger,
    get_project_logger,
    get_track_logger,
    get_video_logger,
    get_image_logger,
    get_audio_logger,
    get_export_logger,
    get_stats_logger,
    get_pricing_logger,
    cleanup_old_logs,
    app_logger,
    # Global logger instances
    auth_middleware_logger,
    rate_limiting_logger,
    monitoring_logger,
    security_logger
)

# Global configuration manager instance
config_manager = get_config_manager()

# Backward compatibility
settings = config_manager

__all__ = [
    # Core configuration
    "ConfigurationManager",
    "get_config_manager", 
    "get_config_value",
    "set_config_value",
    "validate_configuration",
    "get_configuration_summary",
    "reload_configuration",
    "config_manager",
    "settings",  # Backward compatibility
    
    # Configuration classes
    "Environment",
    "LogLevel", 
    "DatabaseConfig",
    "StorageConfig",
    "SecurityConfig",
    "APIConfig",
    "LoggingConfig",
    "ProducerAIConfig",
    "FileProcessingConfig",
    "PerformanceConfig",
    "ExternalServicesConfig",
    "BusinessConfig",
    
    # Decorators
    "config_value",
    "config_section",
    "validate_config",
    "config_dependent",
    "environment_specific",
    "config_cache",
    "config_logger",
    "config_metrics",
    "ConfigProperty",
    "ConfigSection",
    "ConfigMixin",
    "fastapi_config_dependency",
    "fastapi_config_section_dependency",
    "validate_database_config",
    "validate_storage_config",
    "validate_security_config",
    "auto_reload_config",
    "config_change_listener",
    
    # Logging
    "setup_logger",
    "get_logger",
    "get_service_logger",
    "get_middleware_logger",
    "get_api_logger",
    "get_router_logger",
    "MiddlewareLogger",
    "get_auth_logger",
    "get_storage_logger",
    "get_prompt_logger",
    "get_job_logger",
    "get_project_logger",
    "get_track_logger",
    "get_video_logger",
    "get_image_logger",
    "get_audio_logger",
    "get_export_logger",
    "get_stats_logger",
    "get_pricing_logger",
    "cleanup_old_logs",
    "app_logger",
    # Global logger instances
    "auth_middleware_logger",
    "rate_limiting_logger",
    "monitoring_logger",
    "security_logger"
]
