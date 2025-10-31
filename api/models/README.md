# Database Models

The models package contains all SQLAlchemy database models that define the structure and relationships of the application's data.

## Overview

This module defines the database schema using SQLAlchemy ORM models. Each model represents a table in the database and includes relationships, constraints, and business logic.

## Architecture

```
api/models/
├── __init__.py              # Model exports and relationships
├── README.md               # This file
├── user.py                 # User and authentication models
├── project.py              # Project management models
├── music.py                # Music and track models
├── video.py                # Video file models
├── image.py                # Image file models
├── audio.py                # Audio file models
├── job.py                  # Background job models
├── export.py               # Export operation models
├── stats.py                # Statistics and analytics models
├── pricing.py              # Payment and credits models
├── user_settings.py        # User preferences and settings
├── social_account.py       # Social media account models
├── comfyui.py              # ComfyUI workflow models
├── runpod.py               # RunPod execution models
└── llm.py                  # LLM AI models (qwen-omni)
```

## Core Models

### 1. User Management (`user.py`)

**User Model:**
- User accounts and authentication
- Profile information
- Account status and permissions
- Timestamps and metadata

**Key Fields:**
- `id`: Primary key (UUID)
- `email`: User email (unique)
- `username`: Username (unique)
- `hashed_password`: Encrypted password
- `is_active`: Account status
- `is_admin`: Admin privileges
- `created_at`: Account creation time
- `updated_at`: Last update time

### 2. Project Management (`project.py`)

**Project Model:**
- User projects and workspaces
- Project metadata and settings
- Project status and lifecycle

**Key Fields:**
- `id`: Primary key (UUID)
- `user_id`: Owner user ID
- `name`: Project name
- `description`: Project description
- `status`: Project status
- `settings`: JSON project settings
- `created_at`: Project creation time

### 3. Media Models

**Track Model (`music.py`):**
- Music tracks and audio files
- Track metadata and properties
- Audio analysis results

**Video Model (`video.py`):**
- Video files and clips
- Video metadata and properties
- Video processing status

**Image Model (`image.py`):**
- Image files and graphics
- Image metadata and properties
- Image processing results

**Audio Model (`audio.py`):**
- Audio files and recordings
- Audio metadata and properties
- Audio analysis data

### 4. Job Management (`job.py`)

**Job Model:**
- Background job processing
- Job status and progress
- Job results and errors

**Key Fields:**
- `id`: Primary key (UUID)
- `user_id`: Job owner
- `job_type`: Type of job
- `status`: Job status
- `progress`: Job progress percentage
- `result`: Job result data
- `error`: Error information
- `created_at`: Job creation time
- `started_at`: Job start time
- `completed_at`: Job completion time

### 5. Export Operations (`export.py`)

**Export Model:**
- File export operations
- Export formats and settings
- Export status and results

### 6. Statistics (`stats.py`)

**Stats Model:**
- Application usage statistics
- User activity metrics
- Performance data

### 7. Payment System (`pricing.py`)

**Payment Models:**
- `Payment`: Payment transactions
- `CreditsTransaction`: Credits management
- `PaymentMethod`: Payment methods
- `PaymentStatus`: Payment statuses

**Key Enums:**
- `PaymentStatus`: PENDING, COMPLETED, FAILED, REFUNDED
- `CreditsTransactionType`: PURCHASE, SPEND, REFUND, BONUS

### 8. User Settings (`user_settings.py`)

**UserSettings Model:**
- User preferences and configuration
- Application settings
- Personalization data

### 9. Social Media (`social_account.py`)

**SocialAccount Model:**
- Connected social media accounts
- OAuth tokens and credentials
- Account metadata

### 10. AI/ML Models

**ComfyUI Models (`comfyui.py`):**
- `ComfyUIWorkflowExecution`: Workflow execution tracking
- `ComfyUIPod`: Pod management
- `ComfyUIWorkflowConfig`: Workflow configuration
- `ComfyUIExecutionLog`: Execution logging
- `ComfyUIResourceUsage`: Resource monitoring

**RunPod Models (`runpod.py`):**
- `RunPodPod`: Pod instances
- `RunPodExecution`: Execution tracking
- `RunPodTemplate`: Template management
- `RunPodUser`: User management
- `RunPodConfiguration`: Configuration settings

**LLM Models (`llm.py`):**
- AI model interactions
- Request/response tracking
- Model performance metrics

## Model Relationships

### User Relationships
```python
# User has many projects
user.projects  # List of Project objects

# User has many jobs
user.jobs  # List of Job objects

# User has many tracks
user.tracks  # List of Track objects

# User has many payments
user.payments  # List of Payment objects
```

### Project Relationships
```python
# Project belongs to user
project.user  # User object

# Project has many tracks
project.tracks  # List of Track objects

# Project has many videos
project.videos  # List of Video objects
```

### Media Relationships
```python
# Track belongs to project and user
track.project  # Project object
track.user  # User object

# Video belongs to project and user
video.project  # Project object
video.user  # User object
```

## Usage Examples

### Creating Models

```python
from api.models import User, Project, Track
from api.data import get_db

# Create a new user
db = next(get_db())
user = User(
    email="user@example.com",
    username="johndoe",
    hashed_password="hashed_password_here"
)
db.add(user)
db.commit()

# Create a project
project = Project(
    user_id=user.id,
    name="My Music Project",
    description="A collection of my music"
)
db.add(project)
db.commit()

# Create a track
track = Track(
    user_id=user.id,
    project_id=project.id,
    name="My Song",
    file_path="/path/to/song.mp3"
)
db.add(track)
db.commit()
```

### Querying Models

```python
from api.models import User, Project, Track
from api.data import get_db

db = next(get_db())

# Get user by email
user = db.query(User).filter(User.email == "user@example.com").first()

# Get user's projects
projects = db.query(Project).filter(Project.user_id == user.id).all()

# Get project's tracks
tracks = db.query(Track).filter(Track.project_id == project.id).all()

# Get user with relationships
user_with_projects = db.query(User).options(
    joinedload(User.projects),
    joinedload(User.tracks)
).filter(User.id == user_id).first()
```

### Model Validation

```python
from api.models import User
from sqlalchemy.exc import IntegrityError

try:
    user = User(
        email="invalid-email",  # This will fail validation
        username="test"
    )
    db.add(user)
    db.commit()
except IntegrityError as e:
    print(f"Validation failed: {e}")
    db.rollback()
```

## Database Migrations

Models are managed through Alembic migrations:

```bash
# Create a new migration
alembic revision --autogenerate -m "Add new model"

# Apply migrations
alembic upgrade head

# Rollback migrations
alembic downgrade -1
```

## Model Validation

### Built-in Validation
- **Email Format**: Email fields are validated for proper format
- **Unique Constraints**: Unique fields prevent duplicates
- **Required Fields**: Non-nullable fields are enforced
- **Foreign Keys**: Referential integrity is maintained

### Custom Validation
```python
from sqlalchemy import Column, String, validate
from api.models import Base

class CustomModel(Base):
    __tablename__ = "custom_model"
    
    email = Column(
        String(255),
        validate=validate.Email(),
        nullable=False
    )
    
    username = Column(
        String(50),
        validate=validate.Length(min=3, max=50),
        nullable=False
    )
```

## Indexing Strategy

Models include strategic indexes for performance:

```python
from sqlalchemy import Index

# User model indexes
Index('ix_user_email', User.email, unique=True)
Index('ix_user_username', User.username, unique=True)
Index('ix_user_created_at', User.created_at)

# Project model indexes
Index('ix_project_user_id', Project.user_id)
Index('ix_project_status', Project.status)
Index('ix_project_created_at', Project.created_at)

# Track model indexes
Index('ix_track_user_id', Track.user_id)
Index('ix_track_project_id', Track.project_id)
Index('ix_track_status', Track.status)
```

## Model Serialization

Models can be serialized to dictionaries:

```python
from api.models import User

user = db.query(User).first()

# Convert to dictionary
user_dict = {
    "id": str(user.id),
    "email": user.email,
    "username": user.username,
    "is_active": user.is_active,
    "created_at": user.created_at.isoformat()
}
```

## Best Practices

1. **Use UUIDs**: Use UUID primary keys for better security
2. **Add Timestamps**: Include created_at and updated_at fields
3. **Validate Input**: Use SQLAlchemy validators
4. **Index Strategically**: Add indexes for frequently queried fields
5. **Handle Relationships**: Use proper foreign key relationships
6. **Use Transactions**: Wrap operations in transactions
7. **Handle Errors**: Implement proper error handling
8. **Document Models**: Document model purpose and relationships

## Integration with Services

Models integrate with:
- **Data Layer**: Used by database operations
- **Services Layer**: Business logic operates on models
- **API Layer**: Models are serialized for API responses
- **Configuration**: Model settings from configuration

## Security Considerations

### Data Protection
- **Password Hashing**: Passwords are hashed using secure algorithms
- **Input Validation**: All input is validated before storage
- **Access Control**: Models respect user ownership
- **Audit Logging**: Model changes are logged

### Privacy
- **Data Minimization**: Only necessary data is stored
- **User Consent**: User data handling follows consent rules
- **Data Retention**: Automatic cleanup of old data
- **Encryption**: Sensitive data is encrypted at rest

This model system provides a robust, secure, and scalable foundation for the application's data layer.