"""
Base Schema Classes and Validation Utilities
Provides common patterns and validation for all schemas
"""

import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, Field, validator, root_validator
from pydantic.types import EmailStr, HttpUrl


class BaseSchema(BaseModel):
    """Base schema with common configuration"""
    
    class Config:
        from_attributes = True
        validate_assignment = True
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }


class TimestampMixin(BaseModel):
    """Mixin for schemas that include timestamps"""
    created_at: datetime
    updated_at: Optional[datetime] = None


class IDMixin(BaseModel):
    """Mixin for schemas that include an ID"""
    id: UUID


class UserMixin(BaseModel):
    """Mixin for schemas that include user information"""
    user_id: UUID


class ProjectMixin(BaseModel):
    """Mixin for schemas that include project information"""
    project_id: UUID


class FileMixin(BaseModel):
    """Mixin for schemas that include file information"""
    file_path: str
    filename: Optional[str] = None
    size_bytes: Optional[int] = None
    content_type: Optional[str] = None


class MetadataMixin(BaseModel):
    """Mixin for schemas that include metadata"""
    metadata: Optional[Dict[str, Any]] = None


class StatusMixin(BaseModel):
    """Mixin for schemas that include status"""
    status: str = "active"


class VersionMixin(BaseModel):
    """Mixin for schemas that include versioning"""
    version: int = 1


# Standard Response Schemas
class StandardResponse(BaseSchema):
    """Standard API response schema"""
    success: bool = True
    message: str
    data: Optional[Any] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class PaginatedResponse(BaseSchema):
    """Paginated response schema"""
    items: List[Any]
    total: int
    page: int = 1
    per_page: int = 20
    pages: int
    has_next: bool
    has_prev: bool


class ErrorResponse(BaseSchema):
    """Error response schema"""
    success: bool = False
    error: str
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Validation Utilities
class ValidationUtils:
    """Utility class for common validation patterns"""
    
    @staticmethod
    def validate_filename(value: str) -> str:
        """Validate filename format"""
        if not value:
            raise ValueError("Filename cannot be empty")
        
        # Remove or replace invalid characters
        invalid_chars = r'[<>:"/\\|?*]'
        cleaned = re.sub(invalid_chars, '_', value)
        
        if len(cleaned) > 255:
            raise ValueError("Filename too long (max 255 characters)")
        
        return cleaned
    
    @staticmethod
    def validate_file_size(value: int) -> int:
        """Validate file size"""
        if value < 0:
            raise ValueError("File size cannot be negative")
        
        # 100MB limit
        max_size = 100 * 1024 * 1024
        if value > max_size:
            raise ValueError(f"File size too large (max {max_size // (1024*1024)}MB)")
        
        return value
    
    @staticmethod
    def validate_duration(value: float) -> float:
        """Validate duration in seconds"""
        if value < 0:
            raise ValueError("Duration cannot be negative")
        
        # 10 hours limit
        max_duration = 10 * 3600
        if value > max_duration:
            raise ValueError("Duration too long (max 10 hours)")
        
        return value
    
    @staticmethod
    def validate_resolution(value: str) -> str:
        """Validate video resolution format"""
        if not value:
            return value
        
        # Common resolution patterns
        valid_patterns = [
            r'^\d+x\d+$',  # 1920x1080
            r'^\d+p$',     # 1080p
            r'^\d+k$',     # 4k
            r'^HD$',       # HD
            r'^SD$'        # SD
        ]
        
        for pattern in valid_patterns:
            if re.match(pattern, value, re.IGNORECASE):
                return value
        
        raise ValueError("Invalid resolution format")
    
    @staticmethod
    def validate_audio_format(value: str) -> str:
        """Validate audio format"""
        if not value:
            return value
        
        valid_formats = ['mp3', 'wav', 'flac', 'aac', 'ogg', 'm4a']
        if value.lower() not in valid_formats:
            raise ValueError(f"Invalid audio format. Supported: {', '.join(valid_formats)}")
        
        return value.lower()
    
    @staticmethod
    def validate_video_format(value: str) -> str:
        """Validate video format"""
        if not value:
            return value
        
        valid_formats = ['mp4', 'avi', 'mov', 'mkv', 'webm', 'flv']
        if value.lower() not in valid_formats:
            raise ValueError(f"Invalid video format. Supported: {', '.join(valid_formats)}")
        
        return value.lower()
    
    @staticmethod
    def validate_image_format(value: str) -> str:
        """Validate image format"""
        if not value:
            return value
        
        valid_formats = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg']
        if value.lower() not in valid_formats:
            raise ValueError(f"Invalid image format. Supported: {', '.join(valid_formats)}")
        
        return value.lower()
    
    @staticmethod
    def validate_genre(value: str) -> str:
        """Validate music genre"""
        if not value:
            return value
        
        # Common music genres
        valid_genres = [
            'pop', 'rock', 'hip-hop', 'rap', 'country', 'jazz', 'blues',
            'classical', 'electronic', 'dance', 'reggae', 'folk', 'r&b',
            'soul', 'funk', 'disco', 'punk', 'metal', 'alternative',
            'indie', 'ambient', 'lounge', 'chill', 'instrumental'
        ]
        
        if value.lower() not in valid_genres:
            # Allow custom genres but warn
            return value.lower()
        
        return value.lower()
    
    @staticmethod
    def validate_vibe(value: str) -> str:
        """Validate music vibe/mood"""
        if not value:
            return value
        
        valid_vibes = [
            'happy', 'sad', 'energetic', 'calm', 'romantic', 'mysterious',
            'dramatic', 'uplifting', 'melancholic', 'aggressive', 'peaceful',
            'nostalgic', 'futuristic', 'vintage', 'modern', 'dark', 'bright'
        ]
        
        if value.lower() not in valid_vibes:
            return value.lower()  # Allow custom vibes
        
        return value.lower()


# Custom Field Types
class FileSizeField(int):
    """Custom field type for file sizes"""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        return ValidationUtils.validate_file_size(v)


class DurationField(float):
    """Custom field type for durations"""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        return ValidationUtils.validate_duration(v)


class FilenameField(str):
    """Custom field type for filenames"""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        return ValidationUtils.validate_filename(v)


class ResolutionField(str):
    """Custom field type for video resolutions"""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        return ValidationUtils.validate_resolution(v)


class AudioFormatField(str):
    """Custom field type for audio formats"""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        return ValidationUtils.validate_audio_format(v)


class VideoFormatField(str):
    """Custom field type for video formats"""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        return ValidationUtils.validate_video_format(v)


class ImageFormatField(str):
    """Custom field type for image formats"""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        return ValidationUtils.validate_image_format(v)


class GenreField(str):
    """Custom field type for music genres"""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        return ValidationUtils.validate_genre(v)


class VibeField(str):
    """Custom field type for music vibes"""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        return ValidationUtils.validate_vibe(v)


# Common Field Definitions
class CommonFields:
    """Common field definitions for reuse across schemas"""
    
    # Basic fields
    ID = Field(..., description="Unique identifier")
    NAME = Field(..., min_length=1, max_length=255, description="Name")
    DESCRIPTION = Field(None, max_length=1000, description="Description")
    TITLE = Field(None, max_length=255, description="Title")
    
    # File fields
    FILENAME = Field(..., description="Original filename")
    FILE_PATH = Field(..., description="File path in storage")
    FILE_SIZE = Field(None, ge=0, description="File size in bytes")
    CONTENT_TYPE = Field(None, description="MIME content type")
    
    # Media fields
    DURATION = Field(None, ge=0, le=36000, description="Duration in seconds")
    RESOLUTION = Field(None, description="Video resolution (e.g., 1920x1080)")
    FORMAT = Field(None, description="File format")
    SIZE_MB = Field(None, ge=0, description="File size in megabytes")
    
    # Audio fields
    SAMPLE_RATE = Field(None, ge=0, description="Audio sample rate in Hz")
    CHANNELS = Field(None, ge=1, le=8, description="Number of audio channels")
    BITRATE = Field(None, ge=0, description="Audio bitrate in kbps")
    
    # Video fields
    ASPECT_RATIO = Field(None, description="Video aspect ratio (e.g., 16:9)")
    FPS = Field(None, ge=1, le=120, description="Frames per second")
    
    # Image fields
    WIDTH = Field(None, ge=1, description="Image width in pixels")
    HEIGHT = Field(None, ge=1, description="Image height in pixels")
    
    # Music fields
    GENRE = Field(None, description="Music genre")
    VIBE = Field(None, description="Music vibe/mood")
    LYRICS = Field(None, description="Song lyrics")
    INSTRUMENTAL = Field(False, description="Whether track is instrumental")
    
    # Status fields
    STATUS = Field("active", description="Current status")
    VERSION = Field(1, ge=1, description="Version number")
    
    # Timestamp fields
    CREATED_AT = Field(..., description="Creation timestamp")
    UPDATED_AT = Field(None, description="Last update timestamp")
    
    # User/Project fields
    USER_ID = Field(..., description="User identifier")
    PROJECT_ID = Field(..., description="Project identifier")
    
    # Metadata fields
    METADATA = Field(None, description="Additional metadata")
    CUSTOM_DATA = Field(None, description="Custom data fields")


# Export all base classes and utilities
__all__ = [
    # Base classes
    "BaseSchema",
    "TimestampMixin",
    "IDMixin", 
    "UserMixin",
    "ProjectMixin",
    "FileMixin",
    "MetadataMixin",
    "StatusMixin",
    "VersionMixin",
    
    # Response schemas
    "StandardResponse",
    "PaginatedResponse", 
    "ErrorResponse",
    
    # Validation utilities
    "ValidationUtils",
    
    # Custom field types
    "FileSizeField",
    "DurationField",
    "FilenameField",
    "ResolutionField",
    "AudioFormatField",
    "VideoFormatField",
    "ImageFormatField",
    "GenreField",
    "VibeField",
    
    # Common fields
    "CommonFields"
]
