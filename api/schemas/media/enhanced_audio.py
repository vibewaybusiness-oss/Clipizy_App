"""
Enhanced Audio Schemas
Improved audio file schemas with better validation and metadata
"""

from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID

from pydantic import Field, validator

from api.schemas.base import (
    BaseSchema, TimestampMixin, IDMixin, UserMixin, ProjectMixin, 
    FileMixin, MetadataMixin, StatusMixin, VersionMixin,
    AudioFormatField, DurationField, FileSizeField, FilenameField,
    CommonFields, ValidationUtils
)


class AudioBase(BaseSchema):
    """Base audio schema with common fields"""
    prompt: Optional[str] = Field(None, max_length=1000, description="AI generation prompt")
    audio_type: str = Field("other", description="Type of audio (voiceover, sfx, stem, other)")
    description: Optional[str] = Field(None, max_length=500, description="Audio description")
    
    @validator('audio_type')
    def validate_audio_type(cls, v):
        valid_types = ['voiceover', 'sfx', 'stem', 'other']
        if v not in valid_types:
            raise ValueError(f"Invalid audio type. Must be one of: {', '.join(valid_types)}")
        return v


class AudioCreate(AudioBase):
    """Schema for creating new audio files"""
    filename: FilenameField = CommonFields.FILENAME
    content_type: Optional[str] = Field(None, description="MIME content type")
    
    @validator('content_type')
    def validate_content_type(cls, v):
        if v and not v.startswith('audio/'):
            raise ValueError("Content type must be an audio format")
        return v


class AudioUpdate(BaseSchema):
    """Schema for updating audio files"""
    prompt: Optional[str] = Field(None, max_length=1000, description="AI generation prompt")
    audio_type: Optional[str] = Field(None, description="Type of audio")
    description: Optional[str] = Field(None, max_length=500, description="Audio description")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    
    @validator('audio_type')
    def validate_audio_type(cls, v):
        if v is not None:
            valid_types = ['voiceover', 'sfx', 'stem', 'other']
            if v not in valid_types:
                raise ValueError(f"Invalid audio type. Must be one of: {', '.join(valid_types)}")
        return v


class AudioMetadata(BaseSchema):
    """Audio-specific metadata"""
    duration: Optional[DurationField] = Field(None, description="Duration in seconds")
    format: Optional[AudioFormatField] = Field(None, description="Audio format")
    sample_rate: Optional[int] = Field(None, ge=8000, le=192000, description="Sample rate in Hz")
    channels: Optional[int] = Field(None, ge=1, le=8, description="Number of channels")
    bitrate: Optional[int] = Field(None, ge=32, le=320, description="Bitrate in kbps")
    size_mb: Optional[float] = Field(None, ge=0, description="File size in megabytes")
    
    @validator('sample_rate')
    def validate_sample_rate(cls, v):
        if v is not None:
            common_rates = [8000, 11025, 16000, 22050, 32000, 44100, 48000, 88200, 96000, 176400, 192000]
            if v not in common_rates:
                # Allow custom rates but warn
                pass
        return v
    
    @validator('channels')
    def validate_channels(cls, v):
        if v is not None:
            valid_channels = [1, 2, 4, 6, 8]  # mono, stereo, quad, 5.1, 7.1
            if v not in valid_channels:
                raise ValueError("Invalid number of channels")
        return v


class AudioRead(AudioBase, IDMixin, UserMixin, ProjectMixin, FileMixin, MetadataMixin, StatusMixin, TimestampMixin):
    """Schema for reading audio files with full metadata"""
    filename: FilenameField = CommonFields.FILENAME
    file_path: str = CommonFields.FILE_PATH
    size_bytes: Optional[FileSizeField] = Field(None, description="File size in bytes")
    content_type: Optional[str] = Field(None, description="MIME content type")
    
    # Audio-specific metadata
    duration: Optional[DurationField] = Field(None, description="Duration in seconds")
    format: Optional[AudioFormatField] = Field(None, description="Audio format")
    sample_rate: Optional[int] = Field(None, ge=8000, le=192000, description="Sample rate in Hz")
    channels: Optional[int] = Field(None, ge=1, le=8, description="Number of channels")
    bitrate: Optional[int] = Field(None, ge=32, le=320, description="Bitrate in kbps")
    size_mb: Optional[float] = Field(None, ge=0, description="File size in megabytes")
    
    # Processing status
    processing_status: str = Field("completed", description="Processing status")
    analysis_completed: bool = Field(False, description="Whether audio analysis is completed")
    
    # AI generation fields
    ai_generated: bool = Field(False, description="Whether audio was AI generated")
    generation_model: Optional[str] = Field(None, description="AI model used for generation")
    generation_parameters: Optional[Dict[str, Any]] = Field(None, description="Generation parameters")
    
    @validator('processing_status')
    def validate_processing_status(cls, v):
        valid_statuses = ['pending', 'processing', 'completed', 'failed', 'cancelled']
        if v not in valid_statuses:
            raise ValueError(f"Invalid processing status. Must be one of: {', '.join(valid_statuses)}")
        return v


class AudioAnalysis(BaseSchema):
    """Audio analysis results"""
    audio_id: UUID = Field(..., description="Audio file ID")
    analysis_type: str = Field(..., description="Type of analysis performed")
    results: Dict[str, Any] = Field(..., description="Analysis results")
    confidence: Optional[float] = Field(None, ge=0, le=1, description="Analysis confidence score")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Analysis timestamp")
    
    @validator('analysis_type')
    def validate_analysis_type(cls, v):
        valid_types = ['music_analysis', 'speech_analysis', 'noise_analysis', 'quality_analysis']
        if v not in valid_types:
            raise ValueError(f"Invalid analysis type. Must be one of: {', '.join(valid_types)}")
        return v


class AudioUploadRequest(BaseSchema):
    """Request schema for audio upload"""
    audio_type: str = Field("other", description="Type of audio")
    prompt: Optional[str] = Field(None, max_length=1000, description="AI generation prompt")
    description: Optional[str] = Field(None, max_length=500, description="Audio description")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    
    @validator('audio_type')
    def validate_audio_type(cls, v):
        valid_types = ['voiceover', 'sfx', 'stem', 'other']
        if v not in valid_types:
            raise ValueError(f"Invalid audio type. Must be one of: {', '.join(valid_types)}")
        return v


class AudioUploadResponse(BaseSchema):
    """Response schema for audio upload"""
    success: bool = Field(True, description="Upload success status")
    audio_id: UUID = Field(..., description="Created audio file ID")
    filename: str = Field(..., description="Uploaded filename")
    file_path: str = Field(..., description="File path in storage")
    s3_url: Optional[str] = Field(None, description="S3 URL for file access")
    duration: Optional[float] = Field(None, description="Audio duration in seconds")
    size_mb: Optional[float] = Field(None, description="File size in megabytes")
    message: str = Field(..., description="Response message")


class AudioListResponse(BaseSchema):
    """Response schema for audio list"""
    audios: list[AudioRead] = Field(..., description="List of audio files")
    total: int = Field(..., description="Total number of audio files")
    page: int = Field(1, description="Current page number")
    per_page: int = Field(20, description="Items per page")
    has_next: bool = Field(False, description="Whether there are more pages")


class AudioSearchRequest(BaseSchema):
    """Request schema for audio search"""
    query: Optional[str] = Field(None, max_length=255, description="Search query")
    audio_type: Optional[str] = Field(None, description="Filter by audio type")
    duration_min: Optional[float] = Field(None, ge=0, description="Minimum duration in seconds")
    duration_max: Optional[float] = Field(None, ge=0, description="Maximum duration in seconds")
    ai_generated: Optional[bool] = Field(None, description="Filter by AI generation status")
    created_after: Optional[datetime] = Field(None, description="Filter by creation date")
    created_before: Optional[datetime] = Field(None, description="Filter by creation date")
    page: int = Field(1, ge=1, description="Page number")
    per_page: int = Field(20, ge=1, le=100, description="Items per page")
    
    @validator('duration_max')
    def validate_duration_range(cls, v, values):
        if v is not None and 'duration_min' in values and values['duration_min'] is not None:
            if v < values['duration_min']:
                raise ValueError("duration_max must be greater than duration_min")
        return v
    
    @validator('created_before')
    def validate_date_range(cls, v, values):
        if v is not None and 'created_after' in values and values['created_after'] is not None:
            if v < values['created_after']:
                raise ValueError("created_before must be after created_after")
        return v


# Export all schemas
__all__ = [
    "AudioBase",
    "AudioCreate", 
    "AudioUpdate",
    "AudioRead",
    "AudioMetadata",
    "AudioAnalysis",
    "AudioUploadRequest",
    "AudioUploadResponse",
    "AudioListResponse",
    "AudioSearchRequest"
]
