# Routes System

The routes system provides legacy route definitions and specific endpoint implementations that complement the main router system.

## Overview

This module contains specific route implementations and legacy route definitions that provide additional functionality beyond the main router system. It serves as a bridge between legacy code and the new router architecture.

## Architecture

```
api/routes/
├── __init__.py              # Route exports and utilities
├── README.md               # This file
├── producer.py             # ProducerAI integration routes
├── producer_music_clip.py  # Music clip generation routes
└── __pycache__/           # Python cache files
```

## Core Components

### 1. Producer Routes (`producer.py`)

ProducerAI integration and workflow management:

**Key Features:**
- ProducerAI session management
- Workflow execution
- Content generation
- Status monitoring

**Endpoints:**
- `POST /producer/session`: Create new ProducerAI session
- `GET /producer/session/{session_id}`: Get session status
- `POST /producer/generate`: Generate content
- `DELETE /producer/session/{session_id}`: End session

**Usage Example:**
```python
from api.routes.producer import producer_router

# Register with FastAPI app
app.include_router(producer_router, prefix="/api/producer")
```

### 2. Producer Music Clip Routes (`producer_music_clip.py`)

Music clip generation and processing:

**Key Features:**
- Music clip generation
- Audio processing
- Video creation
- Export management

**Endpoints:**
- `POST /producer/music-clip`: Create music clip
- `GET /producer/music-clip/{clip_id}`: Get clip status
- `POST /producer/music-clip/{clip_id}/process`: Process clip
- `GET /producer/music-clip/{clip_id}/download`: Download clip

**Usage Example:**
```python
from api.routes.producer_music_clip import music_clip_router

# Register with FastAPI app
app.include_router(music_clip_router, prefix="/api/producer/music-clip")
```

## Route Implementation Details

### ProducerAI Integration

The producer routes handle integration with ProducerAI for content generation:

```python
from api.routes.producer import create_producer_session

# Create a new ProducerAI session
session = await create_producer_session(
    user_id=user.id,
    session_config={
        "max_windows": 5,
        "timeout": 120000
    }
)

# Generate content
result = await generate_content(
    session_id=session.id,
    prompt="Create a music video",
    settings={
        "style": "modern",
        "duration": 30
    }
)
```

### Music Clip Generation

The music clip routes handle the complete music clip generation workflow:

```python
from api.routes.producer_music_clip import create_music_clip

# Create a new music clip
clip = await create_music_clip(
    user_id=user.id,
    project_id=project.id,
    audio_file="path/to/audio.mp3",
    settings={
        "style": "energetic",
        "duration": 30,
        "resolution": "1080p"
    }
)

# Process the clip
await process_music_clip(clip.id)

# Download the result
download_url = await get_clip_download_url(clip.id)
```

## Integration with Router System

### Router Registration

Routes can be registered with the main router system:

```python
from api.routes import producer_router, music_clip_router
from api.routers.registry import register_router

# Register routes as routers
register_router("producer", producer_router)
register_router("music_clip", music_clip_router)
```

### Service Integration

Routes integrate with the services layer:

```python
from api.services import ProjectService, MediaService
from api.routes.producer_music_clip import create_music_clip

# Routes use services for business logic
async def create_music_clip_endpoint(request: MusicClipRequest):
    # Use services for business logic
    project_service = ProjectService()
    media_service = MediaService()
    
    # Create clip using services
    clip = await media_service.create_music_clip(
        project_id=request.project_id,
        audio_file=request.audio_file,
        settings=request.settings
    )
    
    return {"clip_id": clip.id, "status": "created"}
```

## Error Handling

### Route-Specific Error Handling

```python
from api.routes.producer import producer_router
from fastapi import HTTPException

@producer_router.exception_handler(ProducerAIError)
async def producer_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error": "ProducerAI error",
            "detail": str(exc),
            "session_id": getattr(exc, 'session_id', None)
        }
    )
```

### Validation Error Handling

```python
from api.routes.producer_music_clip import music_clip_router
from pydantic import ValidationError

@music_clip_router.exception_handler(ValidationError)
async def validation_error_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation failed",
            "details": exc.errors()
        }
    )
```

## Authentication and Authorization

### User Authentication

```python
from api.routes.producer import producer_router
from api.middleware.auth_middleware import get_user_from_request

@producer_router.post("/session")
async def create_session(
    request: Request,
    session_config: SessionConfig
):
    user = get_user_from_request(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Create session for authenticated user
    session = await create_producer_session(user.id, session_config)
    return {"session_id": session.id}
```

### Admin Authorization

```python
from api.routes.producer_music_clip import music_clip_router
from api.middleware.auth_middleware import is_admin_from_request

@music_clip_router.get("/admin/stats")
async def get_admin_stats(request: Request):
    if not is_admin_from_request(request):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Return admin statistics
    return await get_music_clip_stats()
```

## Configuration Integration

### Environment-Specific Configuration

```python
from api.config import get_config_value
from api.routes.producer import producer_router

@producer_router.post("/session")
async def create_session(session_config: SessionConfig):
    # Get configuration values
    max_windows = get_config_value("producer_ai.max_windows", 5)
    timeout = get_config_value("producer_ai.generation_timeout", 120000)
    
    # Apply configuration
    session_config.max_windows = min(session_config.max_windows, max_windows)
    session_config.timeout = min(session_config.timeout, timeout)
    
    return await create_producer_session(session_config)
```

### Feature Flags

```python
from api.config import get_config_value
from api.routes.producer_music_clip import music_clip_router

@music_clip_router.post("/create")
async def create_music_clip(request: MusicClipRequest):
    # Check feature flags
    if not get_config_value("features.music_clip_generation", False):
        raise HTTPException(
            status_code=503, 
            detail="Music clip generation is currently disabled"
        )
    
    return await create_music_clip(request)
```

## Performance Optimization

### Caching

```python
from api.routes.producer import producer_router
from functools import lru_cache

@lru_cache(maxsize=100)
async def get_producer_session_status(session_id: str):
    # Cached session status lookup
    return await fetch_session_status(session_id)

@producer_router.get("/session/{session_id}")
async def get_session_status(session_id: str):
    status = await get_producer_session_status(session_id)
    return {"session_id": session_id, "status": status}
```

### Async Operations

```python
from api.routes.producer_music_clip import music_clip_router
import asyncio

@music_clip_router.post("/process")
async def process_music_clip(clip_id: str):
    # Start processing asynchronously
    task = asyncio.create_task(process_clip_async(clip_id))
    
    return {
        "clip_id": clip_id,
        "status": "processing",
        "task_id": task.get_name()
    }
```

## Monitoring and Logging

### Request Logging

```python
from api.config.logging import get_router_logger
from api.routes.producer import producer_router

logger = get_router_logger("producer")

@producer_router.post("/generate")
async def generate_content(request: GenerateRequest):
    logger.info(f"Content generation started for user {request.user_id}")
    
    try:
        result = await generate_content_async(request)
        logger.info(f"Content generation completed for user {request.user_id}")
        return result
    except Exception as e:
        logger.error(f"Content generation failed for user {request.user_id}: {e}")
        raise
```

### Performance Metrics

```python
from api.routes.producer_music_clip import music_clip_router
import time

@music_clip_router.post("/create")
async def create_music_clip(request: MusicClipRequest):
    start_time = time.time()
    
    try:
        result = await create_music_clip_async(request)
        
        # Log performance metrics
        duration = time.time() - start_time
        logger.info(f"Music clip creation completed in {duration:.2f}s")
        
        return result
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"Music clip creation failed after {duration:.2f}s: {e}")
        raise
```

## Testing

### Route Testing

```python
from fastapi.testclient import TestClient
from api.routes.producer import producer_router

def test_producer_session_creation():
    client = TestClient(producer_router)
    
    response = client.post("/session", json={
        "max_windows": 5,
        "timeout": 120000
    })
    
    assert response.status_code == 200
    assert "session_id" in response.json()
```

### Integration Testing

```python
def test_music_clip_workflow():
    client = TestClient(app)
    
    # Create music clip
    response = client.post("/api/producer/music-clip", json={
        "project_id": "test-project",
        "audio_file": "test-audio.mp3",
        "settings": {"duration": 30}
    })
    
    assert response.status_code == 200
    clip_id = response.json()["clip_id"]
    
    # Check status
    response = client.get(f"/api/producer/music-clip/{clip_id}")
    assert response.status_code == 200
    assert response.json()["status"] == "created"
```

## Best Practices

1. **Use Services**: Delegate business logic to services layer
2. **Handle Errors**: Implement comprehensive error handling
3. **Validate Input**: Use Pydantic models for validation
4. **Log Operations**: Log important operations and errors
5. **Use Configuration**: Integrate with configuration system
6. **Test Thoroughly**: Write comprehensive tests
7. **Monitor Performance**: Track performance metrics
8. **Secure Endpoints**: Implement proper authentication and authorization

## Migration to Router System

### Gradual Migration

Routes can be gradually migrated to the router system:

```python
# Legacy route
@producer_router.post("/legacy-endpoint")
async def legacy_endpoint():
    return {"message": "legacy"}

# New router implementation
class ProducerRouter(BaseRouter):
    def setup_routes(self):
        @self.router.post("/new-endpoint")
        async def new_endpoint():
            return {"message": "new"}
```

### Compatibility Layer

Routes provide compatibility with the router system:

```python
from api.routes import producer_router
from api.routers.registry import register_router

# Register legacy routes as routers
register_router("producer_legacy", producer_router)
```

## Integration with Services

Routes integrate with:
- **Services Layer**: Business logic through services
- **Data Layer**: Data access through models
- **Configuration**: Settings from configuration system
- **Middleware**: Request processing through middleware
- **Authentication**: User authentication and authorization

This routes system provides a bridge between legacy code and the new router architecture, ensuring smooth migration and continued functionality.