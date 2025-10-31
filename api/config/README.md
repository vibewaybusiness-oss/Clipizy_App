# Configuration System

The configuration system provides centralized management of all application settings, logging, and environment-specific configurations.

## Overview

This module consolidates all configuration management into a single, unified system that integrates with the services and data layers. It replaces scattered configuration files and provides a clean, maintainable approach to application settings.

## Architecture

```
api/config/
├── __init__.py          # Main export point with all configuration APIs
├── manager.py           # Core configuration manager with service integration
├── decorators.py        # Configuration decorators for easy access
├── logging.py           # Centralized logging system
├── json/                # JSON configuration files
└── README.md           # This file
```

## Core Components

### 1. Configuration Manager (`manager.py`)

The central configuration manager that:
- Loads settings from environment variables and JSON files
- Integrates with the services and data layers
- Provides health checks and validation
- Supports hot reloading of configuration

**Key Classes:**
- `ConfigurationManager`: Main configuration manager extending `BaseService`
- `DatabaseConfig`: Database connection settings
- `StorageConfig`: S3 and local storage settings
- `SecurityConfig`: JWT and security settings
- `APIConfig`: API and CORS settings
- `LoggingConfig`: Logging configuration
- `ProducerAIConfig`: ProducerAI integration settings
- `FileProcessingConfig`: File upload and processing settings
- `PerformanceConfig`: Performance and optimization settings
- `ExternalServicesConfig`: Third-party service API keys
- `BusinessConfig`: Business logic settings

### 2. Configuration Decorators (`decorators.py`)

Decorators for easy configuration access and validation:

**Core Decorators:**
- `@config_value()`: Inject configuration values into functions
- `@config_section()`: Inject entire configuration sections
- `@validate_config()`: Validate configuration before execution
- `@environment_specific()`: Restrict functions to specific environments
- `@config_cache()`: Cache configuration-dependent results

**FastAPI Integration:**
- `@fastapi_config_dependency()`: Create FastAPI dependencies for config values
- `@fastapi_config_section_dependency()`: Create FastAPI dependencies for config sections

**Validation Decorators:**
- `@validate_database_config()`: Validate database configuration
- `@validate_storage_config()`: Validate storage configuration
- `@validate_security_config()`: Validate security configuration

### 3. Centralized Logging (`logging.py`)

Unified logging system that replaces scattered logger definitions:

**Core Functions:**
- `get_logger()`: Main function to get loggers (replaces `logging.getLogger`)
- `get_middleware_logger()`: Specialized loggers for middleware
- `get_api_logger()`: Specialized loggers for API components
- `get_service_logger()`: Specialized loggers for services

**Structured Logging:**
- `MiddlewareLogger`: Structured logging for middleware with request context
- Automatic log file routing based on component type
- Configuration-driven log levels and formats

## Usage Examples

### Basic Configuration Access

```python
from api.config import get_config_value, config_manager

# Direct access
db_url = get_config_value("database.url")
secret_key = get_config_value("security.secret_key")

# Using the manager
config = config_manager
print(f"Environment: {config.environment.value}")
print(f"Database URL: {config.database.url}")
```

### Using Decorators

```python
from api.config import config_value, validate_config

@config_value("database.url")
@validate_config
def connect_to_database(config_database_url):
    return f"Connecting to {config_database_url}"

@config_value("security.secret_key")
def create_jwt_token(config_security_secret_key, user_id):
    return jwt.encode({"user_id": user_id}, config_security_secret_key)
```

### FastAPI Integration

```python
from fastapi import Depends
from api.config import fastapi_config_dependency

@app.get("/health")
def health_check(
    db_url: str = Depends(fastapi_config_dependency("database.url")),
    environment: str = Depends(fastapi_config_dependency("environment"))
):
    return {"status": "healthy", "db_url": db_url, "env": environment}
```

### Centralized Logging

```python
from api.config import get_logger, get_middleware_logger, MiddlewareLogger

# In any component
logger = get_logger(__name__)
logger.info("Application started")

# In middleware
middleware_logger = MiddlewareLogger("auth_middleware")
middleware_logger.log_request(request, "User authenticated", user_id="123")
```

## Configuration Hierarchy

The configuration system follows this priority order:

1. **Environment Variables** (highest priority)
2. **JSON Configuration Files**
3. **Default Values** (lowest priority)

## Environment Variables

Key environment variables that can be set:

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/clipizy
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20

# Security
SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Storage
S3_BUCKET=clipizy
S3_ACCESS_KEY=your-access-key
S3_SECRET_KEY=your-secret-key

# Logging
LOG_LEVEL=INFO
ENABLE_CONSOLE_LOGGING=true
ENABLE_FILE_LOGGING=true

# Environment
ENVIRONMENT=development
```

## JSON Configuration Files

Configuration can be loaded from JSON files in the `json/` directory:

- `json/development.json`: Development-specific settings
- `json/production.json`: Production-specific settings
- `json/database.json`: Database configuration
- `json/storage.json`: Storage configuration
- `json/security.json`: Security configuration

## Health Checks

The configuration manager provides health checks:

```python
from api.config import config_manager

# Check configuration health
health = await config_manager.health_check()
print(health)
# {
#     "database_status": "connected",
#     "storage_status": "available",
#     "config_cache_size": 15,
#     "config_files_loaded": 3
# }
```

## Validation

Configuration validation ensures all required settings are present:

```python
from api.config import validate_configuration

issues = validate_configuration()
if issues:
    print(f"Configuration issues: {issues}")
```

## Migration from Legacy Systems

This configuration system replaces:
- Scattered `settings.py` files
- Hardcoded configuration values
- Multiple logging systems
- Environment-specific configuration files

## Best Practices

1. **Use the centralized system**: Always use `get_config_value()` instead of hardcoded values
2. **Use decorators**: Leverage configuration decorators for clean code
3. **Validate configuration**: Use validation decorators for critical functions
4. **Use structured logging**: Use the centralized logging system instead of `logging.getLogger`
5. **Environment-specific configs**: Use JSON files for environment-specific settings
6. **Health checks**: Implement health checks for configuration-dependent services

## Integration with Services

The configuration system integrates with:
- **Services Layer**: Configuration manager extends `BaseService`
- **Data Layer**: Uses database and storage services for configuration storage
- **Middleware**: Provides centralized logging for all middleware components
- **FastAPI**: Seamless integration with FastAPI dependency injection

This creates a unified, maintainable configuration system that scales with the application.
