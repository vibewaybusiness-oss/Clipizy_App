# Services System

The services system provides a unified, dependency-injected architecture for all business logic, with comprehensive service management, error handling, and utility functions.

## Overview

This module contains all business logic services organized in a unified system with dependency injection, service lifecycle management, and comprehensive utilities. It provides a clean separation between business logic and data access.

## Architecture

```
api/services/
├── __init__.py              # Service exports and unified system
├── README.md               # This file
├── services.py             # Unified services and utilities
├── ai/                     # AI and ML services
├── auth/                   # Authentication services
├── business/               # Business logic services
├── cache/                  # Caching services
├── create/                 # Content creation services
├── database/               # Database services
├── errors/                 # Error handling services
├── utils/                  # Utility services
└── admin/                  # Administrative services
```

## Core Components

### 1. Unified Services (`services.py`)

The central unified services system that provides:

**Core DI System:**
- `BaseService`: Base class for all services
- `ServiceConfig`: Service configuration
- `ServiceMetrics`: Service performance metrics
- `ServiceFactory`: Service creation factory
- `ServiceLogger`: Unified logging for services

**Service Management:**
- `service_registry`: Global service registry
- `service_factory`: Global service factory
- `service_manager`: Service lifecycle management
- `service_container`: Service container
- `service_health_monitor`: Health monitoring

**Service Decorators:**
- `@service_method`: Mark service methods
- `@retry_on_failure`: Retry failed operations
- `@service_context`: Service context management
- `@inject_service`: Dependency injection
- `@require_service`: Service requirement validation

**Base Service Classes:**
- `DatabaseService`: Database operations
- `ExternalService`: External API calls
- `AsyncService`: Async operations
- `CommonServiceBase`: Common service functionality

**Mixins:**
- `ServiceInitializationMixin`: Service initialization
- `DatabaseOperationMixin`: Database operations
- `ValidationMixin`: Input validation
- `FileOperationMixin`: File operations
- `AsyncOperationMixin`: Async operations
- `ConfigurationMixin`: Configuration access
- `MetricsMixin`: Performance metrics

**Utility Functions:**
- `generate_unique_id()`: Generate unique identifiers
- `format_timestamp()`: Format timestamps
- `calculate_duration()`: Calculate durations
- `safe_get_dict_value()`: Safe dictionary access
- `merge_dicts()`: Merge dictionaries
- `chunk_list()`: Chunk lists
- `validate_required_fields()`: Validate required fields
- `sanitize_filename()`: Sanitize filenames

### 2. AI Services (`ai/`)

Artificial intelligence and machine learning services:

**ProducerAI Services:**
- `ProducerMusicClipService`: Music clip generation
- `ProducerIntegration`: ProducerAI integration
- `ProducerSessionManager`: Session management
- `ProducerAIOptimizer`: Performance optimization

**LLM Services:**
- `LLMService`: LLM AI integration (qwen-omni)
- `LLMChatService`: Chat functionality
- `LLMImageService`: Image generation

**Job Services:**
- `JobService`: Background job management
- `JobProcessor`: Job processing
- `JobScheduler`: Job scheduling

### 3. Authentication Services (`auth/`)

User authentication and authorization:

**Core Services:**
- `auth_service`: Main authentication service
- `UserService`: User management
- `TokenService`: JWT token management
- `OAuthService`: OAuth integration
- `SocialAccountService`: Social media accounts

### 4. Business Services (`business/`)

Core business logic:

**Payment Services:**
- `stripe_service`: Stripe payment processing
- `credits_service`: Credits management
- `PaymentService`: Payment operations
- `SubscriptionService`: Subscription management

**Project Services:**
- `ProjectService`: Project management
- `ProjectCollaborationService`: Collaboration features
- `ProjectSharingService`: Project sharing

### 5. Database Services (`database/`)

Database operations and optimization:

**Core Services:**
- `ConnectionManager`: Database connections
- `QueryOptimizer`: Query optimization
- `IndexingStrategy`: Index management
- `OptimizationService`: Database optimization

### 6. Cache Services (`cache/`)

Caching and performance optimization:

**Core Services:**
- `RedisCache`: Redis caching
- `CacheIntegration`: Cache integration
- `CacheService`: Cache management

### 7. Error Handling (`errors/`)

Comprehensive error handling:

**Core Services:**
- `CentralizedErrorHandler`: Global error handling
- `ErrorContext`: Error context management
- `ErrorHandlingContext`: Error handling context

## Usage Examples

### Basic Service Usage

```python
from api.services import BaseService, ServiceConfig, get_service

# Create a service
class MyService(BaseService):
    def __init__(self):
        config = ServiceConfig(name="my_service")
        super().__init__(config)
    
    async def _service_health_check(self):
        return {"status": "healthy"}

# Register service
from api.services import register_singleton
register_singleton(MyService, name="my_service")

# Use service
my_service = get_service(MyService)
result = await my_service.some_method()
```

### Service with Dependencies

```python
from api.services import BaseService, inject_service

class UserService(BaseService):
    def __init__(self):
        super().__init__(ServiceConfig(name="user_service"))
    
    @inject_service("database_service")
    async def get_user(self, user_id: str, database_service):
        return await database_service.get_user(user_id)

# Register with dependencies
register_singleton(UserService, name="user_service", dependencies=["database_service"])
```

### Service with Decorators

```python
from api.services import BaseService, service_method, retry_on_failure

class ExternalAPIService(BaseService):
    @service_method
    @retry_on_failure(max_retries=3, delay=1.0)
    async def call_external_api(self, endpoint: str):
        # External API call with retry logic
        response = await self.http_client.get(endpoint)
        return response.json()
```

### Service Health Monitoring

```python
from api.services import get_service, health_check_all_services

# Check individual service health
user_service = get_service("user_service")
health = await user_service.health_check()
print(f"User service health: {health}")

# Check all services
all_health = await health_check_all_services()
for service_name, health in all_health.items():
    print(f"{service_name}: {health['status']}")
```

### Service Statistics

```python
from api.services import get_service_summary

# Get service summary
summary = get_service_summary()
print(f"Total services: {summary['total_services']}")
print(f"Healthy services: {summary['healthy_services']}")
print(f"Service metrics: {summary['metrics']}")
```

## Service Lifecycle

### Service Initialization

```python
from api.services import startup_all_services, shutdown_all_services

# Startup all services
await startup_all_services()

# Shutdown all services
await shutdown_all_services()
```

### Service Configuration

```python
from api.services import ServiceConfig

# Service configuration
config = ServiceConfig(
    name="my_service",
    version="1.0.0",
    dependencies=["database_service", "cache_service"],
    health_check_interval=30,
    metrics_enabled=True
)
```

## Error Handling

### Centralized Error Handling

```python
from api.services import CentralizedErrorHandler, ErrorContext

# Global error handler
error_handler = CentralizedErrorHandler()

# Handle errors with context
async def service_method():
    try:
        # Service logic
        result = await some_operation()
        return result
    except Exception as e:
        # Log error with context
        await error_handler.handle_error(
            error=e,
            context=ErrorContext(
                service="my_service",
                method="service_method",
                user_id="123"
            )
        )
        raise
```

### Service Error Handling

```python
from api.services import BaseService, handle_errors

class MyService(BaseService):
    @handle_errors
    async def risky_operation(self):
        # Operation that might fail
        return await external_api_call()
```

## Performance Monitoring

### Service Metrics

```python
from api.services import MetricsMixin

class MetricsService(BaseService, MetricsMixin):
    def __init__(self):
        super().__init__(ServiceConfig(name="metrics_service"))
        self.metrics_enabled = True
    
    async def track_operation(self, operation_name: str):
        start_time = time.time()
        try:
            result = await self.perform_operation()
            self.record_metric(operation_name, "success", time.time() - start_time)
            return result
        except Exception as e:
            self.record_metric(operation_name, "error", time.time() - start_time)
            raise
```

### Service Performance

```python
from api.services import get_service_metrics

# Get service performance metrics
metrics = get_service_metrics("my_service")
print(f"Average response time: {metrics['avg_response_time']}ms")
print(f"Success rate: {metrics['success_rate']}%")
print(f"Error rate: {metrics['error_rate']}%")
```

## Configuration Integration

### Service Configuration

```python
from api.config import get_config_value
from api.services import BaseService

class ConfigurableService(BaseService):
    def __init__(self):
        super().__init__(ServiceConfig(name="configurable_service"))
        
        # Get configuration values
        self.api_key = get_config_value("external_services.api_key")
        self.timeout = get_config_value("external_services.timeout", 30)
        self.retry_attempts = get_config_value("external_services.retry_attempts", 3)
```

### Environment-Specific Configuration

```python
from api.config import get_config_manager

class EnvironmentAwareService(BaseService):
    def __init__(self):
        super().__init__(ServiceConfig(name="environment_aware_service"))
        
        config = get_config_manager()
        self.environment = config.environment.value
        
        if self.environment == "production":
            self.debug_mode = False
            self.log_level = "WARNING"
        else:
            self.debug_mode = True
            self.log_level = "DEBUG"
```

## Testing

### Service Testing

```python
from api.services import BaseService, ServiceConfig
import pytest

class TestService(BaseService):
    def __init__(self):
        super().__init__(ServiceConfig(name="test_service"))
    
    async def test_method(self):
        return "test_result"

@pytest.mark.asyncio
async def test_service():
    service = TestService()
    result = await service.test_method()
    assert result == "test_result"
```

### Service Integration Testing

```python
from api.services import register_singleton, get_service, startup_all_services

@pytest.mark.asyncio
async def test_service_integration():
    # Register test services
    register_singleton(TestService, name="test_service")
    
    # Startup services
    await startup_all_services()
    
    # Test service integration
    service = get_service("test_service")
    result = await service.test_method()
    assert result == "test_result"
```

## Best Practices

1. **Use Base Classes**: Inherit from appropriate base service classes
2. **Implement Health Checks**: Add health checks for all services
3. **Use Dependency Injection**: Leverage the DI system
4. **Handle Errors**: Implement comprehensive error handling
5. **Monitor Performance**: Track service performance metrics
6. **Use Configuration**: Integrate with configuration system
7. **Test Thoroughly**: Write comprehensive tests
8. **Document Services**: Document service purpose and usage

## Integration with Other Systems

Services integrate with:
- **Configuration System**: Uses centralized configuration
- **Data Layer**: Accesses data through models
- **Logging System**: Uses centralized logging
- **Middleware**: Provides business logic for middleware
- **API Layer**: Powers API endpoints with business logic

## Service Discovery and Registration

### Automatic Service Discovery

```python
from api.services import discover_services, register_discovered_services

# Discover services automatically
discovered_services = discover_services()
print(f"Discovered {len(discovered_services)} services")

# Register discovered services
register_discovered_services(discovered_services)
```

### Service Groups

```python
from api.services import register_service_group

# Register service group
register_service_group("ai_services", [
    "producer_service",
    "llm_service",
    "job_service"
])

# Get services by group
ai_services = get_services_by_group("ai_services")
```

## Unified Storage System

### Overview

The services system includes a unified storage system that supports multiple project types with a single, consistent implementation.

### Storage Service (`storage/storage.py`)
- **Multi-project type support**: music-clip, video-edit, audio-edit, image-edit, custom
- **Type-specific validation**: File type and size limits per project type
- **Unified API**: Consistent interface across all project types
- **Configurable storage paths**: Project-type specific S3 organization
- **Single implementation**: No legacy code, unified architecture

### Supported Project Types

```python
PROJECT_CONFIGS = {
    'music-clip': {
        'storage_prefix': 'music-clip',
        'allowed_file_types': ['audio/mpeg', 'audio/wav', 'audio/mp3', 'audio/ogg'],
        'max_file_size': 50 * 1024 * 1024,  # 50MB
        'supported_operations': ['upload', 'generate', 'analyze', 'export']
    },
    'video-edit': {
        'storage_prefix': 'video-edit',
        'allowed_file_types': ['video/mp4', 'video/avi', 'video/mov', 'video/webm'],
        'max_file_size': 500 * 1024 * 1024,  # 500MB
        'supported_operations': ['upload', 'edit', 'render', 'export']
    },
    'audio-edit': {
        'storage_prefix': 'audio-edit',
        'allowed_file_types': ['audio/mpeg', 'audio/wav', 'audio/mp3', 'audio/ogg', 'audio/flac'],
        'max_file_size': 100 * 1024 * 1024,  # 100MB
        'supported_operations': ['upload', 'edit', 'mix', 'export']
    },
    'image-edit': {
        'storage_prefix': 'image-edit',
        'allowed_file_types': ['image/jpeg', 'image/png', 'image/gif', 'image/webp'],
        'max_file_size': 20 * 1024 * 1024,  # 20MB
        'supported_operations': ['upload', 'edit', 'filter', 'export']
    },
    'custom': {
        'storage_prefix': 'custom',
        'allowed_file_types': ['*/*'],
        'max_file_size': 100 * 1024 * 1024,  # 100MB
        'supported_operations': ['upload', 'process', 'export']
    }
}
```

### Usage Examples

#### Unified Storage Service

```python
from api.services.storage import storage_service

# Upload file for any project type
file_info = await storage_service.upload_project_file(
    user_id=user_id,
    project_id=project_id,
    project_type='video-edit',
    file=uploaded_file,
    metadata={'resolution': '1080p'}
)

# Save project data
await storage_service.save_project_data(
    user_id=user_id,
    project_id=project_id,
    project_type='video-edit',
    data=project_data
)

# Load project data
data = await storage_service.load_project_data(
    user_id=user_id,
    project_id=project_id,
    project_type='video-edit'
)
```

#### File Validation

```python
# Validate file for specific project type
storage_service.validate_file_for_project_type(file, 'video-edit')

# Get project type configuration
config = storage_service.get_project_config('video-edit')
print(f"Max file size: {config['max_file_size']}")
print(f"Allowed types: {config['allowed_file_types']}")
```

### Benefits

1. **Type Safety**: Full support for different project types with validation
2. **Consistency**: Unified API across all project types
3. **Extensibility**: Easy to add new project types
4. **Performance**: Optimized storage paths per project type
5. **Maintainability**: Single implementation, centralized configuration
6. **Simplicity**: No legacy code, clean architecture

This services system provides a robust, scalable, and maintainable architecture for all business logic that integrates seamlessly with the rest of the application.
