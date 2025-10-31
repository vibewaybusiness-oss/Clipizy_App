"""
Configuration Decorators
Provides decorators for easy configuration access and validation
"""

import functools
import logging
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, Union

from .manager import get_config_manager, get_config_value, set_config_value

logger = logging.getLogger(__name__)

T = TypeVar('T')


def config_value(config_path: str, default: Any = None):
    """
    Decorator to inject configuration value into function parameter
    
    Args:
        config_path: Configuration path using dot notation (e.g., 'database.url')
        default: Default value if configuration is not found
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get configuration value
            value = get_config_value(config_path, default)
            
            # Add to kwargs
            kwargs[f'config_{config_path.replace(".", "_")}'] = value
            
            return func(*args, **kwargs)
        
        return wrapper
    
    return decorator


def config_section(config_type: str):
    """
    Decorator to inject entire configuration section into function parameter
    
    Args:
        config_type: Configuration section type (e.g., 'database', 'storage')
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get configuration section
            config_section = get_config_manager().get_config(config_type)
            
            # Add to kwargs
            kwargs[f'config_{config_type}'] = config_section
            
            return func(*args, **kwargs)
        
        return wrapper
    
    return decorator


def validate_config(func: Callable) -> Callable:
    """Decorator to validate configuration before function execution"""
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Validate configuration
        issues = get_config_manager().validate_configuration()
        
        if issues:
            logger.warning(f"Configuration validation issues: {issues}")
            # You can choose to raise an exception or continue with warnings
            # raise ValueError(f"Configuration validation failed: {issues}")
        
        return func(*args, **kwargs)
    
    return wrapper


def config_dependent(config_paths: List[str], required: bool = True):
    """
    Decorator to ensure configuration dependencies are available
    
    Args:
        config_paths: List of configuration paths that must be available
        required: Whether to raise exception if config is missing
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Check configuration dependencies
            missing_configs = []
            
            for config_path in config_paths:
                value = get_config_value(config_path)
                if value is None:
                    missing_configs.append(config_path)
            
            if missing_configs:
                error_msg = f"Missing required configuration: {missing_configs}"
                if required:
                    raise ValueError(error_msg)
                else:
                    logger.warning(error_msg)
            
            return func(*args, **kwargs)
        
        return wrapper
    
    return decorator


def environment_specific(environments: List[str]):
    """
    Decorator to restrict function execution to specific environments
    
    Args:
        environments: List of allowed environments
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            current_env = get_config_manager().environment.value
            
            if current_env not in environments:
                raise RuntimeError(f"Function {func.__name__} is not allowed in environment: {current_env}")
            
            return func(*args, **kwargs)
        
        return wrapper
    
    return decorator


def config_cache(cache_key: str, ttl: int = 300):
    """
    Decorator to cache configuration-dependent function results
    
    Args:
        cache_key: Cache key for the result
        ttl: Time to live in seconds
    """
    def decorator(func: Callable) -> Callable:
        cache = {}
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            import time
            
            # Check cache
            if cache_key in cache:
                cached_result, timestamp = cache[cache_key]
                if time.time() - timestamp < ttl:
                    return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache[cache_key] = (result, time.time())
            
            return result
        
        return wrapper
    
    return decorator


def config_logger(logger_name: Optional[str] = None):
    """Decorator to inject configuration-aware logger"""
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get logger
            if logger_name:
                logger_instance = logging.getLogger(logger_name)
            else:
                logger_instance = logging.getLogger(func.__module__)
            
            # Add logger to kwargs
            kwargs['logger'] = logger_instance
            
            return func(*args, **kwargs)
        
        return wrapper
    
    return decorator


def config_metrics(metric_name: str):
    """Decorator to add configuration-aware metrics"""
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            import time
            
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                
                # Log success metric
                duration = time.time() - start_time
                logger.info(f"Metric {metric_name}: success, duration={duration:.3f}s")
                
                return result
                
            except Exception as e:
                # Log error metric
                duration = time.time() - start_time
                logger.error(f"Metric {metric_name}: error, duration={duration:.3f}s, error={str(e)}")
                raise
        
        return wrapper
    
    return decorator


class ConfigProperty:
    """Property-like access to configuration values"""
    
    def __init__(self, config_path: str, default: Any = None):
        self.config_path = config_path
        self.default = default
    
    def __get__(self, instance, owner):
        return get_config_value(self.config_path, self.default)
    
    def __set__(self, instance, value):
        set_config_value(self.config_path, value)


class ConfigSection:
    """Section-like access to configuration"""
    
    def __init__(self, config_type: str):
        self.config_type = config_type
    
    def __get__(self, instance, owner):
        return get_config_manager().get_config(self.config_type)


# Configuration mixin for classes
class ConfigMixin:
    """Mixin class to provide configuration access to classes"""
    
    @property
    def config(self):
        """Get configuration manager"""
        return get_config_manager()
    
    def get_config_value(self, config_path: str, default: Any = None) -> Any:
        """Get configuration value"""
        return get_config_value(config_path, default)
    
    def set_config_value(self, config_path: str, value: Any):
        """Set configuration value"""
        set_config_value(config_path, value)
    
    def get_config_section(self, config_type: str) -> Any:
        """Get configuration section"""
        return get_config_manager().get_config(config_type)


# FastAPI integration decorators
def fastapi_config_dependency(config_path: str, default: Any = None):
    """Create FastAPI dependency for configuration value"""
    
    def dependency():
        return get_config_value(config_path, default)
    
    # Add metadata for FastAPI
    dependency._config_path = config_path
    dependency._default_value = default
    dependency._is_config_dependency = True
    
    return dependency


def fastapi_config_section_dependency(config_type: str):
    """Create FastAPI dependency for configuration section"""
    
    def dependency():
        return get_config_manager().get_config(config_type)
    
    # Add metadata for FastAPI
    dependency._config_type = config_type
    dependency._is_config_dependency = True
    
    return dependency


# Configuration validation decorators
def validate_database_config(func: Callable) -> Callable:
    """Validate database configuration before function execution"""
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        db_config = get_config_manager().get_config("database")
        
        if not db_config.url:
            raise ValueError("Database URL is required")
        
        if db_config.pool_size <= 0:
            raise ValueError("Database pool size must be positive")
        
        return func(*args, **kwargs)
    
    return wrapper


def validate_storage_config(func: Callable) -> Callable:
    """Validate storage configuration before function execution"""
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        storage_config = get_config_manager().get_config("storage")
        
        if not storage_config.s3_bucket:
            raise ValueError("S3 bucket is required")
        
        if not storage_config.s3_access_key:
            raise ValueError("S3 access key is required")
        
        return func(*args, **kwargs)
    
    return wrapper


def validate_security_config(func: Callable) -> Callable:
    """Validate security configuration before function execution"""
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        security_config = get_config_manager().get_config("security")
        
        if not security_config.secret_key:
            raise ValueError("Secret key is required")
        
        if security_config.secret_key == "your-secret-key-here-change-in-production":
            raise ValueError("Default secret key detected - change in production")
        
        return func(*args, **kwargs)
    
    return wrapper


# Configuration reload decorators
def auto_reload_config(func: Callable) -> Callable:
    """Automatically reload configuration before function execution"""
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        get_config_manager().reload_configuration()
        return func(*args, **kwargs)
    
    return wrapper


def config_change_listener(config_paths: List[str]):
    """Decorator to listen for configuration changes"""
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # This would implement configuration change detection
            # For now, just execute the function
            return func(*args, **kwargs)
        
        return wrapper
    
    return decorator
