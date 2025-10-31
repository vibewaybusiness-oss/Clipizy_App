# Schema System

The schema system provides Pydantic models for request/response validation, data serialization, and API documentation generation.

## Overview

This module contains all Pydantic schemas that define the structure of API requests and responses. These schemas ensure data validation, type safety, and automatic API documentation generation.

## Architecture

```
api/schemas/
├── __init__.py              # Schema exports and utilities
├── README.md               # This file
├── base.py                 # Base schema classes and utilities
├── responses.py            # Standard response schemas
├── enhanced_init.py        # Enhanced schema initialization
├── auth/                   # Authentication schemas
├── ai/                     # AI/ML service schemas
├── analytics/              # Analytics and statistics schemas
├── business/               # Business logic schemas
├── content/                # Content creation schemas
└── media/                  # Media file schemas
```

## Core Components

### 1. Base Schemas (`base.py`)

Foundation classes and utilities for all schemas:

**Base Classes:**
- `BaseSchema`: Base class for all schemas
- `BaseRequest`: Base class for request schemas
- `BaseResponse`: Base class for response schemas
- `BaseModel`: Base class for data models

**Utility Classes:**
- `PaginatedResponse`: Pagination wrapper
- `ErrorResponse`: Error response structure
- `SuccessResponse`: Success response structure
- `ValidationError`: Validation error details

**Common Fields:**
- `id`: UUID primary key
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp
- `user_id`: User identifier
- `status`: Status field

### 2. Response Schemas (`responses.py`)

Standardized response structures:

**Response Types:**
- `StandardResponse`: Standard API response
- `ErrorResponse`: Error response format
- `SuccessResponse`: Success response format
- `PaginatedResponse`: Paginated data response
- `HealthResponse`: Health check response

**Usage Example:**
```python
from api.schemas.responses import StandardResponse, ErrorResponse

# Success response
return StandardResponse(
    data={"user_id": "123", "email": "user@example.com"},
    message="User created successfully"
)

# Error response
return ErrorResponse(
    error="Validation failed",
    details=["Email is required", "Password too short"]
)
```

### 3. Enhanced Initialization (`enhanced_init.py`)

Enhanced schema initialization and utilities:

**Features:**
- Schema validation utilities
- Data transformation helpers
- Schema merging capabilities
- Validation error handling

## Schema Categories

### 1. Authentication (`auth/`)

User authentication and management schemas:

**Request Schemas:**
- `UserCreate`: User registration
- `UserLogin`: User login
- `UserUpdate`: User profile update
- `OAuthTokenRequest`: OAuth token request
- `SocialAccountCreate`: Social account linking

**Response Schemas:**
- `UserRead`: User profile data
- `Token`: JWT token response
- `OAuthResponse`: OAuth authentication response
- `OAuthUserInfo`: OAuth user information
- `SocialAccountRead`: Social account data

**Usage Example:**
```python
from api.schemas.auth import UserCreate, UserRead, Token

# User registration
user_data = UserCreate(
    email="user@example.com",
    username="johndoe",
    password="secure_password"
)

# User response
user_response = UserRead(
    id="123",
    email="user@example.com",
    username="johndoe",
    is_active=True,
    created_at="2024-01-01T00:00:00Z"
)

# Token response
token_response = Token(
    access_token="jwt_token_here",
    token_type="bearer",
    expires_in=3600
)
```

### 2. AI/ML Services (`ai/`)

Artificial intelligence and machine learning schemas:

**Workflow Schemas:**
- `WorkflowRequest`: Workflow execution request
- `WorkflowResult`: Workflow execution result
- `WorkflowConfig`: Workflow configuration
- `BaseWorkflowInput`: Base workflow input

**AI Service Schemas:**
- `ComfyUIRequest`: ComfyUI workflow request
- `ComfyUIHealthStatus`: ComfyUI service health
- `RunPodPod`: RunPod pod configuration
- `RunPodExecution`: RunPod execution details

**Input Schemas:**
- `QwenImageInput`: Qwen image generation input
- `FluxImageInput`: Flux image generation input
- `WanVideoInput`: Wan video generation input
- `MMAudioInput`: Multi-modal audio input

**Usage Example:**
```python
from api.schemas.ai import WorkflowRequest, WorkflowResult, ComfyUIRequest

# Workflow request
workflow_request = WorkflowRequest(
    workflow_type="image_generation",
    input_data={
        "prompt": "A beautiful landscape",
        "style": "photorealistic",
        "resolution": "1024x1024"
    },
    user_id="123"
)

# ComfyUI request
comfyui_request = ComfyUIRequest(
    workflow_id="workflow_123",
    input_images=["base64_image_data"],
    parameters={"seed": 42, "steps": 20}
)
```

### 3. Business Logic (`business/`)

Core business functionality schemas:

**Payment Schemas:**
- `PaymentCreate`: Payment creation
- `PaymentRead`: Payment information
- `PaymentIntentCreate`: Payment intent creation
- `PaymentWebhookData`: Webhook data

**Credits Schemas:**
- `CreditsTransactionCreate`: Credits transaction
- `CreditsTransactionRead`: Credits transaction data
- `CreditsBalance`: User credits balance
- `CreditsPurchaseRequest`: Credits purchase

**Project Schemas:**
- `ProjectCreate`: Project creation
- `ProjectRead`: Project information
- `ProjectUpdate`: Project updates
- `JobCreate`: Job creation
- `JobResponse`: Job status

**Usage Example:**
```python
from api.schemas.business import (
    ProjectCreate, ProjectRead, CreditsTransactionCreate, PaymentCreate
)

# Project creation
project = ProjectCreate(
    name="My Music Project",
    description="A collection of my music",
    settings={"genre": "electronic", "bpm": 128}
)

# Credits transaction
credits_tx = CreditsTransactionCreate(
    user_id="123",
    amount=100,
    transaction_type="purchase",
    description="Credits purchase"
)

# Payment creation
payment = PaymentCreate(
    user_id="123",
    amount=9.99,
    currency="USD",
    payment_method="stripe"
)
```

### 4. Media Files (`media/`)

Media file and processing schemas:

**Media Schemas:**
- `TrackCreate`: Music track creation
- `TrackRead`: Music track data
- `VideoCreate`: Video file creation
- `VideoRead`: Video file data
- `ImageCreate`: Image file creation
- `ImageRead`: Image file data
- `AudioCreate`: Audio file creation
- `AudioRead`: Audio file data

**Analysis Schemas:**
- `AnalysisResponse`: File analysis results
- `ExportCreate`: Export operation creation
- `ExportRead`: Export operation data

**Usage Example:**
```python
from api.schemas.media import TrackCreate, TrackRead, AnalysisResponse

# Track creation
track = TrackCreate(
    name="My Song",
    file_path="/path/to/song.mp3",
    project_id="project_123",
    metadata={
        "duration": 180,
        "bpm": 128,
        "genre": "electronic"
    }
)

# Analysis response
analysis = AnalysisResponse(
    file_id="file_123",
    analysis_type="music",
    results={
        "bpm": 128,
        "key": "C major",
        "genre": "electronic",
        "mood": "energetic"
    },
    confidence=0.95
)
```

### 5. Analytics (`analytics/`)

Statistics and analytics schemas:

**Analytics Schemas:**
- `StatsRead`: Statistics data
- `UserActivity`: User activity tracking
- `PerformanceMetrics`: Performance metrics
- `UsageStatistics`: Usage statistics

**Usage Example:**
```python
from api.schemas.analytics import StatsRead, UserActivity

# Statistics data
stats = StatsRead(
    total_users=1000,
    active_users=750,
    total_projects=5000,
    total_tracks=15000,
    period="monthly"
)

# User activity
activity = UserActivity(
    user_id="123",
    action="create_project",
    timestamp="2024-01-01T00:00:00Z",
    metadata={"project_id": "project_123"}
)
```

## Schema Validation

### Built-in Validation

Schemas include comprehensive validation:

```python
from api.schemas.auth import UserCreate
from pydantic import ValidationError

try:
    user = UserCreate(
        email="invalid-email",  # This will fail validation
        username="",  # This will fail validation
        password="123"  # This will fail validation
    )
except ValidationError as e:
    print(f"Validation failed: {e.errors()}")
```

### Custom Validation

```python
from pydantic import BaseModel, validator
from api.schemas.base import BaseSchema

class CustomSchema(BaseSchema):
    email: str
    age: int
    
    @validator('email')
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('Invalid email format')
        return v
    
    @validator('age')
    def validate_age(cls, v):
        if v < 0 or v > 150:
            raise ValueError('Age must be between 0 and 150')
        return v
```

## Schema Serialization

### JSON Serialization

```python
from api.schemas.auth import UserCreate

# Create schema instance
user = UserCreate(
    email="user@example.com",
    username="johndoe",
    password="secure_password"
)

# Serialize to JSON
user_json = user.json()
print(user_json)

# Serialize to dictionary
user_dict = user.dict()
print(user_dict)
```

### API Response Serialization

```python
from api.schemas.responses import StandardResponse
from api.schemas.auth import UserRead

# Create response
user = UserRead(
    id="123",
    email="user@example.com",
    username="johndoe"
)

response = StandardResponse(
    data=user.dict(),
    message="User retrieved successfully"
)

# Serialize for API response
return response.dict()
```

## Schema Documentation

### Automatic API Documentation

Schemas automatically generate API documentation:

```python
from fastapi import FastAPI
from api.schemas.auth import UserCreate, UserRead

app = FastAPI()

@app.post("/users/", response_model=UserRead)
async def create_user(user: UserCreate):
    # FastAPI automatically generates documentation
    # based on the UserCreate and UserRead schemas
    return create_user_service(user)
```

### Schema Documentation

```python
from api.schemas.auth import UserCreate

# Schema documentation is automatically generated
print(UserCreate.__doc__)
print(UserCreate.schema())
print(UserCreate.schema_json())
```

## Best Practices

1. **Use Base Classes**: Inherit from appropriate base schema classes
2. **Validate Input**: Use Pydantic validators for data validation
3. **Document Schemas**: Add docstrings to schema classes
4. **Use Enums**: Use enums for fixed value sets
5. **Handle Optional Fields**: Use Optional for nullable fields
6. **Version Schemas**: Version schemas for API compatibility
7. **Test Schemas**: Write tests for schema validation
8. **Use Aliases**: Use field aliases for API compatibility

## Integration with Services

Schemas integrate with:
- **API Layer**: Request/response validation
- **Services Layer**: Data transformation
- **Data Layer**: Model serialization
- **Configuration**: Schema configuration
- **Documentation**: Automatic API documentation

## Performance Considerations

### Schema Caching

```python
from functools import lru_cache
from api.schemas.auth import UserCreate

@lru_cache(maxsize=100)
def validate_user_data(data: dict) -> UserCreate:
    return UserCreate(**data)
```

### Lazy Loading

```python
from typing import Optional
from api.schemas.base import BaseSchema

class LazySchema(BaseSchema):
    heavy_field: Optional[dict] = None
    
    def __init__(self, **data):
        super().__init__(**data)
        # Load heavy field only when needed
        if self.heavy_field is None:
            self.heavy_field = self._load_heavy_field()
```

This schema system provides comprehensive data validation, type safety, and automatic API documentation generation that scales with the application.
