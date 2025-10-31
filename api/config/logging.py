"""
Centralized logging configuration for clipizy Backend
Single source of truth for all logging across the application
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

# Import configuration manager for dynamic logging settings
try:
    from .manager import get_config_manager
    _config_manager = get_config_manager()
except ImportError:
    _config_manager = None

# Create logs directory
LOGS_DIR = Path(__file__).parent.parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Log file paths
INFO_LOG = LOGS_DIR / "info.log"
ERROR_LOG = LOGS_DIR / "error.log"
DEBUG_LOG = LOGS_DIR / "debug.log"
SERVICE_LOG = LOGS_DIR / "services.log"
MIDDLEWARE_LOG = LOGS_DIR / "middleware.log"
API_LOG = LOGS_DIR / "api.log"


def get_logging_config() -> Dict[str, Any]:
    """Get logging configuration from config manager"""
    if _config_manager:
        return {
            "level": _config_manager.logging.level.value,
            "file_max_size": _config_manager.logging.file_max_size,
            "file_backup_count": _config_manager.logging.file_backup_count,
            "enable_console": _config_manager.logging.enable_console_logging,
            "enable_file": _config_manager.logging.enable_file_logging,
            "log_format": _config_manager.logging.log_format
        }
    else:
        # Default configuration
        return {
            "level": "INFO",
            "file_max_size": 10 * 1024 * 1024,  # 10MB
            "file_backup_count": 5,
            "enable_console": True,
            "enable_file": True,
            "log_format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }


def setup_logger(name: str, level: Optional[str] = None, log_file: Optional[Path] = None) -> logging.Logger:
    """
    Set up a logger with file and console handlers using centralized configuration

    Args:
        name: Logger name (usually __name__)
        level: Logging level (default: from config)
        log_file: Specific log file (default: based on logger type)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Get configuration
    config = get_logging_config()
    log_level = getattr(logging, (level or config["level"]).upper())
    logger.setLevel(log_level)

    # Prevent duplicate handlers
    if logger.handlers:
        return logger

    # Create formatters
    detailed_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s", 
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    simple_formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s", 
        datefmt="%H:%M:%S"
    )

    # Console handler
    if config["enable_console"]:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)
        logger.addHandler(console_handler)

    # File handlers
    if config["enable_file"]:
        # Determine log file based on logger name or provided file
        if log_file:
            target_log = log_file
        elif "middleware" in name.lower():
            target_log = MIDDLEWARE_LOG
        elif "api" in name.lower() or "router" in name.lower():
            target_log = API_LOG
        elif "service" in name.lower():
            target_log = SERVICE_LOG
        else:
            target_log = INFO_LOG

        # File handler (rotating)
        file_handler = logging.handlers.RotatingFileHandler(
            target_log, 
            maxBytes=config["file_max_size"], 
            backupCount=config["file_backup_count"], 
            encoding="utf-8"
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)

        # Error file handler for all loggers
        if target_log != ERROR_LOG:
            error_handler = logging.handlers.RotatingFileHandler(
                ERROR_LOG, 
                maxBytes=config["file_max_size"], 
                backupCount=config["file_backup_count"], 
                encoding="utf-8"
            )
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(detailed_formatter)
            logger.addHandler(error_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance - this is the main function to use throughout the app
    Replaces all instances of logging.getLogger(__name__)
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Configured logger instance
    """
    return setup_logger(name)


def get_service_logger(service_name: str) -> logging.Logger:
    """
    Get a specialized logger for services with additional service-specific file handler

    Args:
        service_name: Name of the service (e.g., 'auth_service', 'storage_service')

    Returns:
        Configured service logger
    """
    logger = setup_logger(f"services.{service_name}")

    # Add service-specific file handler if it doesn't exist
    service_handler_exists = any(
        isinstance(handler, logging.handlers.RotatingFileHandler) and handler.baseFilename == str(SERVICE_LOG)
        for handler in logger.handlers
    )

    if not service_handler_exists:
        service_handler = logging.handlers.RotatingFileHandler(
            SERVICE_LOG, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"
        )
        service_handler.setLevel(logging.INFO)
        service_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
        logger.addHandler(service_handler)

    return logger


# Pre-configured loggers for common use cases
def get_auth_logger():
    return get_service_logger("auth_service")


def get_middleware_logger(middleware_name: str) -> logging.Logger:
    """
    Get a specialized logger for middleware components
    
    Args:
        middleware_name: Name of the middleware (e.g., 'auth_middleware', 'rate_limiting')
        
    Returns:
        Configured middleware logger
    """
    return setup_logger(f"middleware.{middleware_name}", log_file=MIDDLEWARE_LOG)


def get_api_logger(component_name: str) -> logging.Logger:
    """
    Get a specialized logger for API components (routers, endpoints)
    
    Args:
        component_name: Name of the API component
        
    Returns:
        Configured API logger
    """
    return setup_logger(f"api.{component_name}", log_file=API_LOG)


def get_router_logger(router_name: str) -> logging.Logger:
    """
    Get a specialized logger for routers
    
    Args:
        router_name: Name of the router
        
    Returns:
        Configured router logger
    """
    return get_api_logger(f"router.{router_name}")


# Structured logging for middleware
class MiddlewareLogger:
    """Structured logger for middleware components"""
    
    def __init__(self, middleware_name: str):
        self.logger = get_middleware_logger(middleware_name)
        self.middleware_name = middleware_name
    
    def log_request(self, request, message: str, level: str = "info", **kwargs):
        """Log request with structured data"""
        log_data = {
            "middleware": self.middleware_name,
            "method": request.method,
            "path": request.url.path,
            "client_ip": request.client.host if request.client else "unknown",
            "user_agent": request.headers.get("user-agent", "unknown"),
            "timestamp": datetime.utcnow().isoformat(),
            **kwargs
        }
        
        log_message = f"[{self.middleware_name}] {message}"
        if kwargs:
            log_message += f" | Data: {log_data}"
        
        log_method = getattr(self.logger, level.lower())
        log_method(log_message)
    
    def log_error(self, request, error: Exception, **kwargs):
        """Log error with structured data"""
        self.log_request(
            request, 
            f"Error: {str(error)}", 
            level="error", 
            error_type=type(error).__name__,
            **kwargs
        )
    
    def log_stats(self, stats: Dict[str, Any]):
        """Log middleware statistics"""
        self.logger.info(f"[{self.middleware_name}] Stats: {stats}")


# Global logger instances for common use cases
auth_middleware_logger = get_middleware_logger("auth_middleware")
rate_limiting_logger = get_middleware_logger("rate_limiting")
monitoring_logger = get_middleware_logger("monitoring")
security_logger = get_middleware_logger("security")


def get_storage_logger():
    return get_service_logger("storage_service")


def get_prompt_logger():
    return get_service_logger("prompt_service")


def get_job_logger():
    return get_service_logger("job_service")


def get_project_logger():
    return get_service_logger("project_service")


def get_track_logger():
    return get_service_logger("track_service")


def get_video_logger():
    return get_service_logger("video_service")


def get_image_logger():
    return get_service_logger("image_service")


def get_audio_logger():
    return get_service_logger("audio_service")


def get_export_logger():
    return get_service_logger("export_service")


def get_stats_logger():
    return get_service_logger("stats_service")


def get_pricing_logger():
    return get_service_logger("pricing_service")


# Log cleanup function
def cleanup_old_logs(days_to_keep: int = 30):
    """
    Clean up log files older than specified days

    Args:
        days_to_keep: Number of days to keep log files
    """
    import time

    current_time = time.time()
    cutoff_time = current_time - (days_to_keep * 24 * 60 * 60)

    for log_file in LOGS_DIR.glob("*.log*"):
        if log_file.stat().st_mtime < cutoff_time:
            log_file.unlink()
            print(f"Deleted old log file: {log_file}")


# Initialize main application logger
app_logger = setup_logger("clipizy_app")
