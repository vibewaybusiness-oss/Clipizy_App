"""
Enhanced Video Schemas
Improved video file schemas with better validation and metadata
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID

from pydantic import Field, validator

from api.schemas.base import (
    BaseSchema, TimestampMixin, IDMixin, UserMixin, ProjectMixin, 
    FileMixin, MetadataMixin, StatusMixin, VersionMixin,
    VideoFormatField, DurationField, FileSizeField, FilenameField,
    ResolutionField, CommonFields, ValidationUtils
)


class VideoBase(BaseSchema):
    """Base video schema with common fields"""
    prompt: Optional[str] = Field(None, max_length=1000, description="AI generation prompt")
    video_type: str = Field("draft", description="Type of video (draft, final, intro_animation, outro_animation)")
    description: Optional[str] = Field(None, max_length=500, description="Video description")
    
    @validator('video_type')
    def validate_video_type(cls, v):
        valid_types = ['draft', 'final', 'intro_animation', 'outro_animation', 'thumbnail', 'preview']
        if v not in valid_types:
            raise ValueError(f"Invalid video type. Must be one of: {', '.join(valid_types)}")
        return v


class VideoCreate(VideoBase):
    """Schema for creating new video files"""
    filename: FilenameField = CommonFields.FILENAME
    content_type: Optional[str] = Field(None, description="MIME content type")
    
    @validator('content_type')
    def validate_content_type(cls, v):
        if v and not v.startswith('video/'):
            raise ValueError("Content type must be a video format")
        return v


class VideoUpdate(BaseSchema):
    """Schema for updating video files"""
    prompt: Optional[str] = Field(None, max_length=1000, description="AI generation prompt")
    video_type: Optional[str] = Field(None, description="Type of video")
    description: Optional[str] = Field(None, max_length=500, description="Video description")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    
    @validator('video_type')
    def validate_video_type(cls, v):
        if v is not None:
            valid_types = ['draft', 'final', 'intro_animation', 'outro_animation', 'thumbnail', 'preview']
            if v not in valid_types:
                raise ValueError(f"Invalid video type. Must be one of: {', '.join(valid_types)}")
        return v


class VideoMetadata(BaseSchema):
    """Video-specific metadata"""
    duration: Optional[DurationField] = Field(None, description="Duration in seconds")
    format: Optional[VideoFormatField] = Field(None, description="Video format")
    resolution: Optional[ResolutionField] = Field(None, description="Video resolution")
    aspect_ratio: Optional[str] = Field(None, description="Aspect ratio (e.g., 16:9)")
    fps: Optional[int] = Field(None, ge=1, le=120, description="Frames per second")
    bitrate: Optional[int] = Field(None, ge=0, description="Video bitrate in kbps")
    size_mb: Optional[float] = Field(None, ge=0, description="File size in megabytes")
    
    # Animation-specific fields
    is_intro_animation: bool = Field(False, description="Whether this is an intro animation")
    is_outro_animation: bool = Field(False, description="Whether this is an outro animation")
    animation_duration: Optional[int] = Field(None, ge=0, description="Animation duration in seconds")
    animation_style: Optional[str] = Field(None, description="Animation style")
    
    @validator('aspect_ratio')
    def validate_aspect_ratio(cls, v):
        if v is not None:
            # Common aspect ratios
            valid_ratios = ['16:9', '9:16', '4:3', '3:4', '1:1', '21:9', '2:1']
            if v not in valid_ratios:
                # Allow custom ratios but warn
                pass
        return v
    
    @validator('animation_style')
    def validate_animation_style(cls, v):
        if v is not None:
            valid_styles = ['smooth', 'dynamic', 'static', 'bounce', 'fade', 'slide', 'zoom']
            if v not in valid_styles:
                # Allow custom styles but warn
                pass
        return v


class VideoRead(VideoBase, IDMixin, UserMixin, ProjectMixin, FileMixin, MetadataMixin, StatusMixin, TimestampMixin):
    """Schema for reading video files with full metadata"""
    filename: FilenameField = CommonFields.FILENAME
    file_path: str = CommonFields.FILE_PATH
    size_bytes: Optional[FileSizeField] = Field(None, description="File size in bytes")
    content_type: Optional[str] = Field(None, description="MIME content type")
    
    # Video-specific fields
    duration: Optional[DurationField] = Field(None, description="Duration in seconds")
    format: Optional[VideoFormatField] = Field(None, description="Video format")
    resolution: Optional[ResolutionField] = Field(None, description="Video resolution")
    aspect_ratio: Optional[str] = Field(None, description="Aspect ratio")
    fps: Optional[int] = Field(None, ge=1, le=120, description="Frames per second")
    bitrate: Optional[int] = Field(None, ge=0, description="Video bitrate in kbps")
    size_mb: Optional[float] = Field(None, ge=0, description="File size in megabytes")
    
    # Animation-specific fields
    is_intro_animation: bool = Field(False, description="Whether this is an intro animation")
    is_outro_animation: bool = Field(False, description="Whether this is an outro animation")
    animation_duration: Optional[int] = Field(None, ge=0, description="Animation duration in seconds")
    animation_style: Optional[str] = Field(None, description="Animation style")
    
    # Processing status
    processing_status: str = Field("completed", description="Processing status")
    analysis_completed: bool = Field(False, description="Whether video analysis is completed")
    
    # AI generation fields
    ai_generated: bool = Field(False, description="Whether video was AI generated")
    generation_model: Optional[str] = Field(None, description="AI model used for generation")
    generation_parameters: Optional[Dict[str, Any]] = Field(None, description="Generation parameters")
    generation_cost: Optional[float] = Field(None, ge=0, description="Generation cost in credits")
    
    # Video analysis fields
    has_audio: bool = Field(False, description="Whether video contains audio")
    audio_track_count: Optional[int] = Field(None, ge=0, description="Number of audio tracks")
    subtitle_track_count: Optional[int] = Field(None, ge=0, description="Number of subtitle tracks")
    
    # Quality metrics
    quality_score: Optional[float] = Field(None, ge=0, le=1, description="Video quality score")
    compression_ratio: Optional[float] = Field(None, ge=0, description="Compression ratio")
    
    @validator('processing_status')
    def validate_processing_status(cls, v):
        valid_statuses = ['pending', 'processing', 'completed', 'failed', 'cancelled']
        if v not in valid_statuses:
            raise ValueError(f"Invalid processing status. Must be one of: {', '.join(valid_statuses)}")
        return v
    
    @validator('quality_score')
    def validate_quality_score(cls, v):
        if v is not None and (v < 0 or v > 1):
            raise ValueError("Quality score must be between 0 and 1")
        return v


class VideoAnalysis(BaseSchema):
    """Video analysis results"""
    video_id: UUID = Field(..., description="Video file ID")
    analysis_type: str = Field(..., description="Type of analysis performed")
    results: Dict[str, Any] = Field(..., description="Analysis results")
    confidence: Optional[float] = Field(None, ge=0, le=1, description="Analysis confidence score")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Analysis timestamp")
    
    @validator('analysis_type')
    def validate_analysis_type(cls, v):
        valid_types = ['video_analysis', 'quality_analysis', 'content_analysis', 'motion_analysis', 'color_analysis']
        if v not in valid_types:
            raise ValueError(f"Invalid analysis type. Must be one of: {', '.join(valid_types)}")
        return v


class VideoUploadRequest(BaseSchema):
    """Request schema for video upload"""
    video_type: str = Field("draft", description="Type of video")
    prompt: Optional[str] = Field(None, max_length=1000, description="AI generation prompt")
    description: Optional[str] = Field(None, max_length=500, description="Video description")
    is_intro_animation: bool = Field(False, description="Whether this is an intro animation")
    is_outro_animation: bool = Field(False, description="Whether this is an outro animation")
    animation_duration: Optional[int] = Field(None, ge=0, description="Animation duration in seconds")
    animation_style: Optional[str] = Field(None, description="Animation style")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    
    @validator('video_type')
    def validate_video_type(cls, v):
        valid_types = ['draft', 'final', 'intro_animation', 'outro_animation', 'thumbnail', 'preview']
        if v not in valid_types:
            raise ValueError(f"Invalid video type. Must be one of: {', '.join(valid_types)}")
        return v


class VideoUploadResponse(BaseSchema):
    """Response schema for video upload"""
    success: bool = Field(True, description="Upload success status")
    video_id: UUID = Field(..., description="Created video ID")
    filename: str = Field(..., description="Uploaded filename")
    file_path: str = Field(..., description="File path in storage")
    s3_url: Optional[str] = Field(None, description="S3 URL for file access")
    duration: Optional[float] = Field(None, description="Video duration in seconds")
    size_mb: Optional[float] = Field(None, description="File size in megabytes")
    message: str = Field(..., description="Response message")


class VideoListResponse(BaseSchema):
    """Response schema for video list"""
    videos: List[VideoRead] = Field(..., description="List of video files")
    total: int = Field(..., description="Total number of video files")
    page: int = Field(1, description="Current page number")
    per_page: int = Field(20, description="Items per page")
    has_next: bool = Field(False, description="Whether there are more pages")


class VideoSearchRequest(BaseSchema):
    """Request schema for video search"""
    query: Optional[str] = Field(None, max_length=255, description="Search query")
    video_type: Optional[str] = Field(None, description="Filter by video type")
    duration_min: Optional[float] = Field(None, ge=0, description="Minimum duration in seconds")
    duration_max: Optional[float] = Field(None, ge=0, description="Maximum duration in seconds")
    resolution: Optional[ResolutionField] = Field(None, description="Filter by resolution")
    aspect_ratio: Optional[str] = Field(None, description="Filter by aspect ratio")
    fps_min: Optional[int] = Field(None, ge=1, description="Minimum FPS")
    fps_max: Optional[int] = Field(None, le=120, description="Maximum FPS")
    ai_generated: Optional[bool] = Field(None, description="Filter by AI generation status")
    has_audio: Optional[bool] = Field(None, description="Filter by audio presence")
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
    
    @validator('fps_max')
    def validate_fps_range(cls, v, values):
        if v is not None and 'fps_min' in values and values['fps_min'] is not None:
            if v < values['fps_min']:
                raise ValueError("fps_max must be greater than fps_min")
        return v
    
    @validator('created_before')
    def validate_date_range(cls, v, values):
        if v is not None and 'created_after' in values and values['created_after'] is not None:
            if v < values['created_after']:
                raise ValueError("created_before must be after created_after")
        return v


class VideoGenerationRequest(BaseSchema):
    """Request schema for AI video generation"""
    prompt: str = Field(..., min_length=1, max_length=1000, description="Generation prompt")
    video_type: str = Field("draft", description="Type of video to generate")
    duration: Optional[DurationField] = Field(None, description="Desired duration in seconds")
    resolution: Optional[ResolutionField] = Field(None, description="Desired resolution")
    aspect_ratio: Optional[str] = Field(None, description="Desired aspect ratio")
    fps: Optional[int] = Field(None, ge=1, le=120, description="Desired FPS")
    style: Optional[str] = Field(None, description="Video style")
    model: Optional[str] = Field(None, description="AI model to use")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Additional generation parameters")
    
    @validator('video_type')
    def validate_video_type(cls, v):
        valid_types = ['draft', 'final', 'intro_animation', 'outro_animation', 'thumbnail', 'preview']
        if v not in valid_types:
            raise ValueError(f"Invalid video type. Must be one of: {', '.join(valid_types)}")
        return v


class VideoGenerationResponse(BaseSchema):
    """Response schema for AI video generation"""
    success: bool = Field(True, description="Generation success status")
    video_id: UUID = Field(..., description="Generated video ID")
    job_id: Optional[UUID] = Field(None, description="Generation job ID")
    estimated_duration: Optional[int] = Field(None, description="Estimated generation time in seconds")
    cost_credits: Optional[float] = Field(None, description="Cost in credits")
    message: str = Field(..., description="Response message")


class VideoProcessingRequest(BaseSchema):
    """Request schema for video processing"""
    video_id: UUID = Field(..., description="Video ID to process")
    processing_type: str = Field(..., description="Type of processing to perform")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Processing parameters")
    
    @validator('processing_type')
    def validate_processing_type(cls, v):
        valid_types = ['resize', 'compress', 'convert', 'add_watermark', 'extract_audio', 'add_subtitles']
        if v not in valid_types:
            raise ValueError(f"Invalid processing type. Must be one of: {', '.join(valid_types)}")
        return v


class VideoProcessingResponse(BaseSchema):
    """Response schema for video processing"""
    success: bool = Field(True, description="Processing success status")
    job_id: UUID = Field(..., description="Processing job ID")
    estimated_duration: Optional[int] = Field(None, description="Estimated processing time in seconds")
    message: str = Field(..., description="Response message")


# Export all schemas
__all__ = [
    "VideoBase",
    "VideoCreate",
    "VideoUpdate",
    "VideoRead", 
    "VideoMetadata",
    "VideoAnalysis",
    "VideoUploadRequest",
    "VideoUploadResponse",
    "VideoListResponse",
    "VideoSearchRequest",
    "VideoGenerationRequest",
    "VideoGenerationResponse",
    "VideoProcessingRequest",
    "VideoProcessingResponse"
]
