"""
Enhanced Track Schemas
Improved music track schemas with better validation and metadata
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID

from pydantic import Field, validator

from api.schemas.base import (
    BaseSchema, TimestampMixin, IDMixin, UserMixin, ProjectMixin, 
    FileMixin, MetadataMixin, StatusMixin, VersionMixin,
    AudioFormatField, DurationField, FileSizeField, FilenameField,
    GenreField, VibeField, CommonFields, ValidationUtils
)


class TrackBase(BaseSchema):
    """Base track schema with common fields"""
    title: Optional[str] = Field(None, max_length=255, description="Track title")
    prompt: Optional[str] = Field(None, max_length=1000, description="AI generation prompt")
    description: Optional[str] = Field(None, max_length=500, description="Track description")
    ai_generated: bool = Field(False, description="Whether track was AI generated")
    
    @validator('title')
    def validate_title(cls, v):
        if v is not None and len(v.strip()) == 0:
            raise ValueError("Title cannot be empty")
        return v.strip() if v else v


class TrackCreate(TrackBase):
    """Schema for creating new tracks"""
    filename: FilenameField = CommonFields.FILENAME
    content_type: Optional[str] = Field(None, description="MIME content type")
    
    @validator('content_type')
    def validate_content_type(cls, v):
        if v and not v.startswith('audio/'):
            raise ValueError("Content type must be an audio format")
        return v


class TrackUpdate(BaseSchema):
    """Schema for updating tracks"""
    title: Optional[str] = Field(None, max_length=255, description="Track title")
    prompt: Optional[str] = Field(None, max_length=1000, description="AI generation prompt")
    description: Optional[str] = Field(None, max_length=500, description="Track description")
    genre: Optional[GenreField] = Field(None, description="Music genre")
    vibe: Optional[VibeField] = Field(None, description="Music vibe/mood")
    lyrics: Optional[str] = Field(None, max_length=10000, description="Track lyrics")
    instrumental: Optional[bool] = Field(None, description="Whether track is instrumental")
    video_description: Optional[str] = Field(None, max_length=1000, description="Video description")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    
    @validator('title')
    def validate_title(cls, v):
        if v is not None and len(v.strip()) == 0:
            raise ValueError("Title cannot be empty")
        return v.strip() if v else v
    
    @validator('lyrics')
    def validate_lyrics(cls, v):
        if v is not None and len(v.strip()) == 0:
            return None  # Convert empty strings to None
        return v


class TrackMetadata(BaseSchema):
    """Track-specific metadata"""
    duration: Optional[DurationField] = Field(None, description="Duration in seconds")
    format: Optional[AudioFormatField] = Field(None, description="Audio format")
    sample_rate: Optional[int] = Field(None, ge=8000, le=192000, description="Sample rate in Hz")
    channels: Optional[int] = Field(None, ge=1, le=8, description="Number of channels")
    bitrate: Optional[int] = Field(None, ge=32, le=320, description="Bitrate in kbps")
    size_mb: Optional[float] = Field(None, ge=0, description="File size in megabytes")
    
    # Music-specific fields
    genre: Optional[GenreField] = Field(None, description="Music genre")
    vibe: Optional[VibeField] = Field(None, description="Music vibe/mood")
    tempo: Optional[int] = Field(None, ge=30, le=300, description="Tempo in BPM")
    key: Optional[str] = Field(None, description="Musical key")
    time_signature: Optional[str] = Field(None, description="Time signature (e.g., 4/4)")
    
    @validator('tempo')
    def validate_tempo(cls, v):
        if v is not None:
            # Common tempo ranges
            if v < 30 or v > 300:
                raise ValueError("Tempo must be between 30 and 300 BPM")
        return v
    
    @validator('key')
    def validate_key(cls, v):
        if v is not None:
            # Common musical keys
            valid_keys = [
                'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B',
                'Cm', 'C#m', 'Dm', 'D#m', 'Em', 'Fm', 'F#m', 'Gm', 'G#m', 'Am', 'A#m', 'Bm'
            ]
            if v not in valid_keys:
                # Allow custom keys but warn
                pass
        return v
    
    @validator('time_signature')
    def validate_time_signature(cls, v):
        if v is not None:
            # Common time signatures
            valid_signatures = ['4/4', '3/4', '2/4', '6/8', '12/8', '5/4', '7/8']
            if v not in valid_signatures:
                # Allow custom signatures but warn
                pass
        return v


class TrackRead(TrackBase, IDMixin, UserMixin, ProjectMixin, FileMixin, MetadataMixin, StatusMixin, VersionMixin, TimestampMixin):
    """Schema for reading tracks with full metadata"""
    filename: FilenameField = CommonFields.FILENAME
    file_path: str = CommonFields.FILE_PATH
    size_bytes: Optional[FileSizeField] = Field(None, description="File size in bytes")
    content_type: Optional[str] = Field(None, description="MIME content type")
    
    # Track-specific fields
    genre: Optional[GenreField] = Field(None, description="Music genre")
    vibe: Optional[VibeField] = Field(None, description="Music vibe/mood")
    lyrics: Optional[str] = Field(None, description="Track lyrics")
    instrumental: bool = Field(False, description="Whether track is instrumental")
    video_description: Optional[str] = Field(None, description="Video description")
    
    # Audio metadata
    duration: Optional[DurationField] = Field(None, description="Duration in seconds")
    format: Optional[AudioFormatField] = Field(None, description="Audio format")
    sample_rate: Optional[int] = Field(None, ge=8000, le=192000, description="Sample rate in Hz")
    channels: Optional[int] = Field(None, ge=1, le=8, description="Number of channels")
    bitrate: Optional[int] = Field(None, ge=32, le=320, description="Bitrate in kbps")
    size_mb: Optional[float] = Field(None, ge=0, description="File size in megabytes")
    
    # Music analysis fields
    tempo: Optional[int] = Field(None, ge=30, le=300, description="Tempo in BPM")
    key: Optional[str] = Field(None, description="Musical key")
    time_signature: Optional[str] = Field(None, description="Time signature")
    energy: Optional[float] = Field(None, ge=0, le=1, description="Energy level")
    valence: Optional[float] = Field(None, ge=0, le=1, description="Valence (positivity)")
    danceability: Optional[float] = Field(None, ge=0, le=1, description="Danceability")
    
    # Processing status
    processing_status: str = Field("completed", description="Processing status")
    analysis_completed: bool = Field(False, description="Whether music analysis is completed")
    
    # AI generation fields
    generation_model: Optional[str] = Field(None, description="AI model used for generation")
    generation_parameters: Optional[Dict[str, Any]] = Field(None, description="Generation parameters")
    generation_cost: Optional[float] = Field(None, ge=0, description="Generation cost in credits")
    
    # Version control
    parent_track_id: Optional[UUID] = Field(None, description="Parent track ID for versions")
    is_remix: bool = Field(False, description="Whether this is a remix")
    remix_of: Optional[UUID] = Field(None, description="Original track ID if this is a remix")
    
    @validator('processing_status')
    def validate_processing_status(cls, v):
        valid_statuses = ['pending', 'processing', 'completed', 'failed', 'cancelled']
        if v not in valid_statuses:
            raise ValueError(f"Invalid processing status. Must be one of: {', '.join(valid_statuses)}")
        return v
    
    @validator('energy', 'valence', 'danceability')
    def validate_audio_features(cls, v):
        if v is not None and (v < 0 or v > 1):
            raise ValueError("Audio features must be between 0 and 1")
        return v


class TrackAnalysis(BaseSchema):
    """Track analysis results"""
    track_id: UUID = Field(..., description="Track ID")
    analysis_type: str = Field(..., description="Type of analysis performed")
    results: Dict[str, Any] = Field(..., description="Analysis results")
    confidence: Optional[float] = Field(None, ge=0, le=1, description="Analysis confidence score")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Analysis timestamp")
    
    @validator('analysis_type')
    def validate_analysis_type(cls, v):
        valid_types = ['music_analysis', 'lyrics_analysis', 'genre_classification', 'mood_analysis', 'quality_analysis']
        if v not in valid_types:
            raise ValueError(f"Invalid analysis type. Must be one of: {', '.join(valid_types)}")
        return v


class TrackUploadRequest(BaseSchema):
    """Request schema for track upload"""
    title: Optional[str] = Field(None, max_length=255, description="Track title")
    prompt: Optional[str] = Field(None, max_length=1000, description="AI generation prompt")
    description: Optional[str] = Field(None, max_length=500, description="Track description")
    genre: Optional[GenreField] = Field(None, description="Music genre")
    vibe: Optional[VibeField] = Field(None, description="Music vibe/mood")
    lyrics: Optional[str] = Field(None, max_length=10000, description="Track lyrics")
    instrumental: bool = Field(False, description="Whether track is instrumental")
    video_description: Optional[str] = Field(None, max_length=1000, description="Video description")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    
    @validator('title')
    def validate_title(cls, v):
        if v is not None and len(v.strip()) == 0:
            raise ValueError("Title cannot be empty")
        return v.strip() if v else v


class TrackUploadResponse(BaseSchema):
    """Response schema for track upload"""
    success: bool = Field(True, description="Upload success status")
    track_id: UUID = Field(..., description="Created track ID")
    filename: str = Field(..., description="Uploaded filename")
    file_path: str = Field(..., description="File path in storage")
    s3_url: Optional[str] = Field(None, description="S3 URL for file access")
    duration: Optional[float] = Field(None, description="Track duration in seconds")
    size_mb: Optional[float] = Field(None, description="File size in megabytes")
    message: str = Field(..., description="Response message")


class TrackListResponse(BaseSchema):
    """Response schema for track list"""
    tracks: List[TrackRead] = Field(..., description="List of tracks")
    total: int = Field(..., description="Total number of tracks")
    page: int = Field(1, description="Current page number")
    per_page: int = Field(20, description="Items per page")
    has_next: bool = Field(False, description="Whether there are more pages")


class TrackSearchRequest(BaseSchema):
    """Request schema for track search"""
    query: Optional[str] = Field(None, max_length=255, description="Search query")
    genre: Optional[GenreField] = Field(None, description="Filter by genre")
    vibe: Optional[VibeField] = Field(None, description="Filter by vibe")
    instrumental: Optional[bool] = Field(None, description="Filter by instrumental status")
    ai_generated: Optional[bool] = Field(None, description="Filter by AI generation status")
    duration_min: Optional[float] = Field(None, ge=0, description="Minimum duration in seconds")
    duration_max: Optional[float] = Field(None, ge=0, description="Maximum duration in seconds")
    tempo_min: Optional[int] = Field(None, ge=30, description="Minimum tempo in BPM")
    tempo_max: Optional[int] = Field(None, le=300, description="Maximum tempo in BPM")
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
    
    @validator('tempo_max')
    def validate_tempo_range(cls, v, values):
        if v is not None and 'tempo_min' in values and values['tempo_min'] is not None:
            if v < values['tempo_min']:
                raise ValueError("tempo_max must be greater than tempo_min")
        return v
    
    @validator('created_before')
    def validate_date_range(cls, v, values):
        if v is not None and 'created_after' in values and values['created_after'] is not None:
            if v < values['created_after']:
                raise ValueError("created_before must be after created_after")
        return v


class TrackGenerationRequest(BaseSchema):
    """Request schema for AI track generation"""
    prompt: str = Field(..., min_length=1, max_length=1000, description="Generation prompt")
    title: Optional[str] = Field(None, max_length=255, description="Track title")
    genre: Optional[GenreField] = Field(None, description="Music genre")
    vibe: Optional[VibeField] = Field(None, description="Music vibe/mood")
    duration: Optional[DurationField] = Field(None, description="Desired duration in seconds")
    instrumental: bool = Field(False, description="Whether track should be instrumental")
    lyrics: Optional[str] = Field(None, max_length=10000, description="Track lyrics")
    tempo: Optional[int] = Field(None, ge=30, le=300, description="Desired tempo in BPM")
    key: Optional[str] = Field(None, description="Musical key")
    model: Optional[str] = Field(None, description="AI model to use")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Additional generation parameters")
    
    @validator('title')
    def validate_title(cls, v):
        if v is not None and len(v.strip()) == 0:
            raise ValueError("Title cannot be empty")
        return v.strip() if v else v


class TrackGenerationResponse(BaseSchema):
    """Response schema for AI track generation"""
    success: bool = Field(True, description="Generation success status")
    track_id: UUID = Field(..., description="Generated track ID")
    job_id: Optional[UUID] = Field(None, description="Generation job ID")
    estimated_duration: Optional[int] = Field(None, description="Estimated generation time in seconds")
    cost_credits: Optional[float] = Field(None, description="Cost in credits")
    message: str = Field(..., description="Response message")


# Export all schemas
__all__ = [
    "TrackBase",
    "TrackCreate",
    "TrackUpdate", 
    "TrackRead",
    "TrackMetadata",
    "TrackAnalysis",
    "TrackUploadRequest",
    "TrackUploadResponse",
    "TrackListResponse",
    "TrackSearchRequest",
    "TrackGenerationRequest",
    "TrackGenerationResponse"
]
