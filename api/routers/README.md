# Router System

The router system provides organized, modular API endpoints with comprehensive architecture, registry management, and factory patterns for scalable API development.

## Overview

This module contains all API routers organized by functionality, with a sophisticated architecture system that manages router registration, validation, and lifecycle. It provides a clean separation of concerns and makes the API easily maintainable and extensible.

## Architecture

```
api/routers/
├── __init__.py              # Router exports and registry
├── README.md               # This file
├── architecture.py         # Router architecture and configuration
├── registry.py             # Router registry and management
├── factory.py              # Router factory and creation utilities
├── base_router.py          # Base router classes and utilities
├── health_router.py        # Health check and monitoring endpoints
├── auth/                   # Authentication and user management
├── admin/                  # Administrative functions
├── business/               # Business logic (payments, credits, projects)
├── ai/                     # AI and ML services
├── analytics/              # Analytics and statistics
├── create/                 # Content creation workflows
├── social/                 # Social media integration
└── storage/                # File storage and management
```

## Core Components

### 1. Router Architecture (`architecture.py`)

Defines the overall router architecture and configuration:

**Key Classes:**
- `RouterConfig`: Router configuration settings
- `RouterCategory`: Router categorization
- `RouterPriority`: Router priority levels
- `get_router_architecture()`: Get complete router architecture
- `validate_all_routers()`: Validate all registered routers

**Architecture Features:**
- Router categorization and organization
- Priority-based router loading
- Configuration validation
- Dependency management
- Health monitoring

### 2. Router Registry (`registry.py`)

Manages router registration and lifecycle:

**Key Classes:**
- `RouterRegistry`: Central router registry
- `get_router_registry()`: Get global registry instance
- `register_router()`: Register a new router
- `get_router()`: Get router by name
- `register_all_routers_with_app()`: Register all routers with FastAPI app

**Registry Features:**
- Centralized router management
- Router discovery and registration
- Dependency resolution
- Health checks and monitoring
- Statistics and metrics

### 3. Router Factory (`factory.py`)

Factory pattern for creating routers:

**Key Classes:**
- `RouterFactory`: Router creation factory
- `get_router_factory()`: Get factory instance
- `create_router()`: Create generic router
- `create_auth_router()`: Create authentication router
- `create_business_router()`: Create business logic router
- `create_media_router()`: Create media processing router
- `create_ai_router()`: Create AI/ML router
- `create_admin_router()`: Create admin router

**Factory Features:**
- Standardized router creation
- Configuration-based setup
- Dependency injection
- Middleware integration
- Error handling setup

### 4. Base Router (`base_router.py`)

Base classes and utilities for all routers:

**Base Classes:**
- `BaseRouter`: Base router class
- `AuthRouter`: Authentication router base
- `AdminRouter`: Admin router base
- `BusinessRouter`: Business logic router base
- `MediaRouter`: Media processing router base
- `AIRouter`: AI/ML router base

**Utility Functions:**
- `create_standard_response()`: Create standardized API responses
- `create_error_response()`: Create error responses
- `validate_user_access()`: Validate user access permissions

### 5. Health Router (`health_router.py`)

Health check and monitoring endpoints:

**Endpoints:**
- `/health`: Basic health check
- `/health/detailed`: Detailed health information
- `/health/database`: Database health check
- `/health/storage`: Storage health check
- `/health/services`: Service health checks
- `/metrics`: Application metrics

## Router Categories

### 1. Authentication (`auth/`)

User authentication and management:
- User registration and login
- JWT token management
- OAuth integration
- Password reset
- Email verification
- Social account linking

### 2. Business Logic (`business/`)

Core business functionality:
- **Credits**: Credits management and transactions
- **Payments**: Payment processing and Stripe integration
- **Projects**: Project management and organization
- **Jobs**: Background job management

### 3. AI/ML Services (`ai/`)

Artificial intelligence and machine learning:
- **ComfyUI**: ComfyUI workflow execution
- **RunPod**: RunPod pod management
- **Prompts**: AI prompt management
- **Workflows**: AI workflow orchestration

### 4. Analytics (`analytics/`)

Statistics and analytics:
- User activity tracking
- Usage statistics
- Performance metrics
- Business intelligence

### 5. Content Creation (`create/`)

Content creation workflows:
- Music clip generation
- Video processing
- Image manipulation
- Audio analysis

### 6. Social Media (`social/`)

Social media integration:
- Social account management
- Content sharing
- Automation workflows
- Platform-specific features

### 7. Storage (`storage/`)

Unified file storage and management supporting multiple project types:

**Storage Router (`storage.py`):**
- **Multi-project type support**: music-clip, video-edit, audio-edit, image-edit, custom
- **Unified endpoints**: Consistent API across all project types
- **Type-specific validation**: File type and size limits per project type
- **Project management**: CRUD operations for any project type
- **File operations**: Upload, download, delete for any project type
- **Auto-save**: Unified auto-save functionality
- **Single implementation**: Clean, unified architecture

### 8. Administration (`admin/`)

Administrative functions:
- User management
- System monitoring
- Configuration management
- Audit logging

## Usage Examples

### Basic Router Setup

```python
from fastapi import FastAPI
from api.routers import register_all_routers_with_app

app = FastAPI()

# Register all routers
register_all_routers_with_app(app)
```

### Custom Router Creation

```python
from api.routers.factory import create_auth_router, create_business_router
from api.routers.base_router import BaseRouter

# Create custom router
class CustomRouter(BaseRouter):
    def __init__(self):
        super().__init__()
        self.prefix = "/api/custom"
        self.tags = ["custom"]
    
    def setup_routes(self):
        @self.router.get("/")
        async def custom_endpoint():
            return {"message": "Custom endpoint"}

# Create router using factory
auth_router = create_auth_router()
business_router = create_business_router()
```

### Router Registration

```python
from api.routers.registry import register_router, get_router_registry

# Register custom router
register_router("custom", CustomRouter())

# Get router from registry
custom_router = get_router("custom")

# Get registry statistics
registry = get_router_registry()
stats = registry.get_statistics()
```

### Router Configuration

```python
from api.routers.architecture import RouterConfig, RouterCategory, RouterPriority

# Configure router
config = RouterConfig(
    name="custom_router",
    category=RouterCategory.BUSINESS,
    priority=RouterPriority.HIGH,
    dependencies=["auth_router"],
    health_check=True,
    metrics_enabled=True
)
```

## Router Architecture Features

### 1. Dependency Management

Routers can declare dependencies on other routers:

```python
class DependentRouter(BaseRouter):
    def __init__(self):
        super().__init__()
        self.dependencies = ["auth_router", "storage_router"]
```

### 2. Health Checks

Routers can implement health checks:

```python
class HealthCheckableRouter(BaseRouter):
    async def health_check(self):
        return {
            "status": "healthy",
            "dependencies": await self.check_dependencies()
        }
```

### 3. Metrics Collection

Routers automatically collect metrics:

```python
# Metrics are automatically collected for:
# - Request count
# - Response time
# - Error rate
# - User activity
```

### 4. Configuration Integration

Routers integrate with the configuration system:

```python
from api.config import get_config_value

class ConfigurableRouter(BaseRouter):
    def __init__(self):
        super().__init__()
        self.rate_limit = get_config_value("routers.rate_limit", 100)
        self.enable_caching = get_config_value("routers.enable_caching", True)
```

## Error Handling

### Standardized Error Responses

```python
from api.routers.base_router import create_error_response

@router.get("/endpoint")
async def endpoint():
    try:
        # Business logic
        return {"result": "success"}
    except ValidationError as e:
        return create_error_response(
            status_code=422,
            error="Validation failed",
            details=e.errors()
        )
```

### Global Error Handling

```python
from api.routers.base_router import BaseRouter

class ErrorHandlingRouter(BaseRouter):
    def setup_routes(self):
        @self.router.exception_handler(HTTPException)
        async def http_exception_handler(request, exc):
            return create_error_response(
                status_code=exc.status_code,
                error=exc.detail
            )
```

## Security Features

### Authentication Integration

```python
from api.routers.base_router import validate_user_access

@router.get("/protected")
async def protected_endpoint(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    # Validate user access
    if not validate_user_access(current_user, "read"):
        raise HTTPException(status_code=403, detail="Access denied")
    
    return {"data": "protected_data"}
```

### Rate Limiting

```python
from api.routers.base_router import BaseRouter

class RateLimitedRouter(BaseRouter):
    def __init__(self):
        super().__init__()
        self.rate_limit = 100  # requests per minute
```

## Performance Optimization

### Caching

```python
from api.routers.base_router import BaseRouter

class CachedRouter(BaseRouter):
    def __init__(self):
        super().__init__()
        self.cache_ttl = 300  # 5 minutes
    
    @cached(ttl=300)
    async def expensive_operation(self):
        # Expensive operation
        return result
```

### Async Operations

```python
from api.routers.base_router import BaseRouter

class AsyncRouter(BaseRouter):
    async def setup_routes(self):
        @self.router.get("/async")
        async def async_endpoint():
            # Async operation
            result = await some_async_operation()
            return {"result": result}
```

## Testing

### Router Testing

```python
from fastapi.testclient import TestClient
from api.routers import create_auth_router

def test_auth_router():
    router = create_auth_router()
    client = TestClient(router)
    
    response = client.get("/health")
    assert response.status_code == 200
```

### Integration Testing

```python
def test_router_integration():
    app = FastAPI()
    register_all_routers_with_app(app)
    
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
```

## Best Practices

1. **Use Base Classes**: Inherit from appropriate base router classes
2. **Organize by Function**: Group related endpoints in the same router
3. **Use Factory Pattern**: Use router factory for consistent creation
4. **Implement Health Checks**: Add health checks for monitoring
5. **Handle Errors**: Implement proper error handling
6. **Use Configuration**: Integrate with configuration system
7. **Add Metrics**: Enable metrics collection
8. **Test Thoroughly**: Write comprehensive tests

## Integration with Services

Routers integrate with:
- **Services Layer**: Business logic through services
- **Data Layer**: Data access through models
- **Configuration**: Settings from configuration system
- **Middleware**: Request processing through middleware
- **Authentication**: User authentication and authorization

## Monitoring and Observability

### Health Monitoring

```python
# Health checks are automatically available at:
# GET /health - Basic health check
# GET /health/detailed - Detailed health information
# GET /health/database - Database health
# GET /health/storage - Storage health
```

### Metrics Collection

```python
# Metrics are automatically collected:
# - Request count per endpoint
# - Response time distribution
# - Error rate by endpoint
# - User activity patterns
```

## Unified Storage Endpoints

### Project Management

```python
# Create project for any type
POST /api/storage/projects
{
  "name": "My Video Project",
  "type": "video-edit",
  "description": "A video editing project"
}

# Get projects (optionally filtered by type)
GET /api/storage/projects?project_type=video-edit

# Get specific project
GET /api/storage/projects/{project_id}

# Update project
PUT /api/storage/projects/{project_id}

# Delete project
DELETE /api/storage/projects/{project_id}
```

### Project Data Management

```python
# Save project data
POST /api/storage/projects/{project_id}/data
{
  "settings": {"resolution": "1080p"},
  "tracks": [],
  "analysis": null,
  "media": [],
  "metadata": {}
}

# Load project data
GET /api/storage/projects/{project_id}/data
```

### File Operations

```python
# Upload file for any project type
POST /api/storage/projects/{project_id}/files/upload
Content-Type: multipart/form-data
file: [file]
metadata: {"type": "video", "resolution": "1080p"}

# Delete file
DELETE /api/storage/projects/{project_id}/files/{file_id}

# Get project files
GET /api/storage/projects/{project_id}/files
```

### Auto-Save

```python
# Auto-save project data
POST /api/storage/projects/{project_id}/auto-save
{
  "projectData": {...},
  "timestamp": 1234567890
}
```

### Utility Endpoints

```python
# Get supported project types
GET /api/storage/project-types

# Get storage statistics
GET /api/storage/storage/stats
```

### Usage Examples

#### Video Edit Project

```python
# Create video edit project
response = await client.post("/api/storage/projects", json={
    "name": "My Video Project",
    "type": "video-edit",
    "description": "A video editing project"
})

# Upload video file
with open("video.mp4", "rb") as f:
    response = await client.post(
        f"/api/storage/projects/{project_id}/files/upload",
        files={"file": f},
        data={"metadata": '{"resolution": "1080p"}'}
    )

# Save project data
await client.post(f"/api/storage/projects/{project_id}/data", json={
    "settings": {"resolution": "1080p", "frameRate": 30},
    "media": [{"id": "file_123", "type": "video"}]
})
```

#### Audio Edit Project

```python
# Create audio edit project
response = await client.post("/api/storage/projects", json={
    "name": "My Audio Project",
    "type": "audio-edit",
    "description": "An audio editing project"
})

# Upload audio file
with open("audio.wav", "rb") as f:
    response = await client.post(
        f"/api/storage/projects/{project_id}/files/upload",
        files={"file": f},
        data={"metadata": '{"sampleRate": 44100}'}
    )
```

### Unified Endpoints

All project types use the same unified endpoints:

```python
# Unified endpoints for all project types
POST /api/storage/projects/{project_id}/files/upload
GET /api/storage/projects/{project_id}/data
PUT /api/storage/projects/{project_id}
DELETE /api/storage/projects/{project_id}
```

This router system provides a scalable, maintainable, and feature-rich API architecture that supports the application's growth and evolution.
