"""
Enhanced Project Schemas
Improved project management schemas with better validation and metadata
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID

from pydantic import Field, validator

from api.schemas.base import (
    BaseSchema, TimestampMixin, IDMixin, UserMixin, MetadataMixin, StatusMixin,
    CommonFields, ValidationUtils
)
from api.models.project import ProjectStatus


class ProjectBase(BaseSchema):
    """Base project schema with common fields"""
    type: str = Field(..., description="Project type (music-clip, video-clip, short-clip)")
    name: Optional[str] = Field(None, max_length=255, description="Project name")
    description: Optional[str] = Field(None, max_length=1000, description="Project description")
    
    @validator('type')
    def validate_project_type(cls, v):
        valid_types = ['music-clip', 'video-clip', 'short-clip', 'audio-project', 'video-project']
        if v not in valid_types:
            raise ValueError(f"Invalid project type. Must be one of: {', '.join(valid_types)}")
        return v
    
    @validator('name')
    def validate_name(cls, v):
        if v is not None and len(v.strip()) == 0:
            raise ValueError("Project name cannot be empty")
        return v.strip() if v else v


class ProjectCreate(ProjectBase):
    """Schema for creating new projects"""
    pass


class ProjectUpdate(BaseSchema):
    """Schema for updating projects"""
    name: Optional[str] = Field(None, max_length=255, description="Project name")
    description: Optional[str] = Field(None, max_length=1000, description="Project description")
    status: Optional[ProjectStatus] = Field(None, description="Project status")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    
    @validator('name')
    def validate_name(cls, v):
        if v is not None and len(v.strip()) == 0:
            raise ValueError("Project name cannot be empty")
        return v.strip() if v else v


class ProjectMetadata(BaseSchema):
    """Project-specific metadata"""
    # Project settings
    auto_save: bool = Field(True, description="Whether to auto-save changes")
    public: bool = Field(False, description="Whether project is public")
    collaborative: bool = Field(False, description="Whether project allows collaboration")
    
    # Content settings
    target_duration: Optional[float] = Field(None, ge=0, description="Target duration in seconds")
    target_resolution: Optional[str] = Field(None, description="Target resolution")
    target_format: Optional[str] = Field(None, description="Target format")
    
    # Workflow settings
    workflow_stage: Optional[str] = Field(None, description="Current workflow stage")
    completion_percentage: Optional[float] = Field(None, ge=0, le=100, description="Completion percentage")
    
    # Collaboration settings
    collaborators: Optional[List[UUID]] = Field(None, description="List of collaborator user IDs")
    permissions: Optional[Dict[str, List[str]]] = Field(None, description="User permissions")
    
    @validator('workflow_stage')
    def validate_workflow_stage(cls, v):
        if v is not None:
            valid_stages = ['planning', 'creation', 'editing', 'review', 'finalization', 'published']
            if v not in valid_stages:
                raise ValueError(f"Invalid workflow stage. Must be one of: {', '.join(valid_stages)}")
        return v
    
    @validator('completion_percentage')
    def validate_completion_percentage(cls, v):
        if v is not None and (v < 0 or v > 100):
            raise ValueError("Completion percentage must be between 0 and 100")
        return v


class ProjectRead(ProjectBase, IDMixin, UserMixin, StatusMixin, TimestampMixin, MetadataMixin):
    """Schema for reading projects with full metadata"""
    name: Optional[str] = Field(None, description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    
    # Project statistics
    tracks_count: int = Field(0, ge=0, description="Number of tracks")
    audios_count: int = Field(0, ge=0, description="Number of audio files")
    videos_count: int = Field(0, ge=0, description="Number of video files")
    images_count: int = Field(0, ge=0, description="Number of images")
    exports_count: int = Field(0, ge=0, description="Number of exports")
    
    # Project metrics
    total_duration: Optional[float] = Field(None, ge=0, description="Total duration in seconds")
    total_size_mb: Optional[float] = Field(None, ge=0, description="Total size in megabytes")
    credits_spent: Optional[float] = Field(None, ge=0, description="Credits spent on project")
    
    # Workflow information
    workflow_stage: Optional[str] = Field(None, description="Current workflow stage")
    completion_percentage: Optional[float] = Field(None, ge=0, le=100, description="Completion percentage")
    last_activity: Optional[datetime] = Field(None, description="Last activity timestamp")
    
    # Collaboration information
    collaborators_count: int = Field(0, ge=0, description="Number of collaborators")
    is_public: bool = Field(False, description="Whether project is public")
    is_collaborative: bool = Field(False, description="Whether project allows collaboration")
    
    # AI generation information
    ai_generated_content: bool = Field(False, description="Whether project contains AI-generated content")
    ai_models_used: Optional[List[str]] = Field(None, description="AI models used in project")
    
    @validator('workflow_stage')
    def validate_workflow_stage(cls, v):
        if v is not None:
            valid_stages = ['planning', 'creation', 'editing', 'review', 'finalization', 'published']
            if v not in valid_stages:
                raise ValueError(f"Invalid workflow stage. Must be one of: {', '.join(valid_stages)}")
        return v


class ProjectListResponse(BaseSchema):
    """Response schema for project list"""
    projects: List[ProjectRead] = Field(..., description="List of projects")
    total: int = Field(..., description="Total number of projects")
    page: int = Field(1, description="Current page number")
    per_page: int = Field(20, description="Items per page")
    has_next: bool = Field(False, description="Whether there are more pages")


class ProjectSearchRequest(BaseSchema):
    """Request schema for project search"""
    query: Optional[str] = Field(None, max_length=255, description="Search query")
    project_type: Optional[str] = Field(None, description="Filter by project type")
    status: Optional[ProjectStatus] = Field(None, description="Filter by status")
    workflow_stage: Optional[str] = Field(None, description="Filter by workflow stage")
    is_public: Optional[bool] = Field(None, description="Filter by public status")
    has_ai_content: Optional[bool] = Field(None, description="Filter by AI-generated content")
    created_after: Optional[datetime] = Field(None, description="Filter by creation date")
    created_before: Optional[datetime] = Field(None, description="Filter by creation date")
    page: int = Field(1, ge=1, description="Page number")
    per_page: int = Field(20, ge=1, le=100, description="Items per page")
    
    @validator('project_type')
    def validate_project_type(cls, v):
        if v is not None:
            valid_types = ['music-clip', 'video-clip', 'short-clip', 'audio-project', 'video-project']
            if v not in valid_types:
                raise ValueError(f"Invalid project type. Must be one of: {', '.join(valid_types)}")
        return v
    
    @validator('workflow_stage')
    def validate_workflow_stage(cls, v):
        if v is not None:
            valid_stages = ['planning', 'creation', 'editing', 'review', 'finalization', 'published']
            if v not in valid_stages:
                raise ValueError(f"Invalid workflow stage. Must be one of: {', '.join(valid_stages)}")
        return v
    
    @validator('created_before')
    def validate_date_range(cls, v, values):
        if v is not None and 'created_after' in values and values['created_after'] is not None:
            if v < values['created_after']:
                raise ValueError("created_before must be after created_after")
        return v


class ProjectCreateRequest(BaseSchema):
    """Request schema for project creation"""
    type: str = Field(..., description="Project type")
    name: Optional[str] = Field(None, max_length=255, description="Project name")
    description: Optional[str] = Field(None, max_length=1000, description="Project description")
    template_id: Optional[UUID] = Field(None, description="Template ID to use")
    settings: Optional[Dict[str, Any]] = Field(None, description="Project settings")
    
    @validator('type')
    def validate_project_type(cls, v):
        valid_types = ['music-clip', 'video-clip', 'short-clip', 'audio-project', 'video-project']
        if v not in valid_types:
            raise ValueError(f"Invalid project type. Must be one of: {', '.join(valid_types)}")
        return v


class ProjectCreateResponse(BaseSchema):
    """Response schema for project creation"""
    success: bool = Field(True, description="Creation success status")
    project_id: UUID = Field(..., description="Created project ID")
    project: ProjectRead = Field(..., description="Created project data")
    message: str = Field(..., description="Response message")


class ProjectUpdateRequest(BaseSchema):
    """Request schema for project update"""
    name: Optional[str] = Field(None, max_length=255, description="Project name")
    description: Optional[str] = Field(None, max_length=1000, description="Project description")
    status: Optional[ProjectStatus] = Field(None, description="Project status")
    workflow_stage: Optional[str] = Field(None, description="Workflow stage")
    settings: Optional[Dict[str, Any]] = Field(None, description="Project settings")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    
    @validator('workflow_stage')
    def validate_workflow_stage(cls, v):
        if v is not None:
            valid_stages = ['planning', 'creation', 'editing', 'review', 'finalization', 'published']
            if v not in valid_stages:
                raise ValueError(f"Invalid workflow stage. Must be one of: {', '.join(valid_stages)}")
        return v


class ProjectUpdateResponse(BaseSchema):
    """Response schema for project update"""
    success: bool = Field(True, description="Update success status")
    project: ProjectRead = Field(..., description="Updated project data")
    message: str = Field(..., description="Response message")


class ProjectStats(BaseSchema):
    """Project statistics schema"""
    project_id: UUID = Field(..., description="Project ID")
    
    # File counts
    tracks_count: int = Field(0, ge=0, description="Number of tracks")
    audios_count: int = Field(0, ge=0, description="Number of audio files")
    videos_count: int = Field(0, ge=0, description="Number of video files")
    images_count: int = Field(0, ge=0, description="Number of images")
    exports_count: int = Field(0, ge=0, description="Number of exports")
    
    # Size metrics
    total_size_mb: float = Field(0, ge=0, description="Total size in megabytes")
    total_duration: Optional[float] = Field(None, ge=0, description="Total duration in seconds")
    
    # Usage metrics
    credits_spent: float = Field(0, ge=0, description="Credits spent")
    processing_time_minutes: float = Field(0, ge=0, description="Total processing time in minutes")
    
    # Activity metrics
    last_activity: Optional[datetime] = Field(None, description="Last activity timestamp")
    creation_date: datetime = Field(..., description="Project creation date")
    days_active: int = Field(0, ge=0, description="Number of days since creation")


class ProjectTemplate(BaseSchema):
    """Project template schema"""
    id: UUID = Field(..., description="Template ID")
    name: str = Field(..., max_length=255, description="Template name")
    description: Optional[str] = Field(None, max_length=1000, description="Template description")
    project_type: str = Field(..., description="Project type")
    template_data: Dict[str, Any] = Field(..., description="Template configuration")
    is_public: bool = Field(False, description="Whether template is public")
    created_by: UUID = Field(..., description="Template creator ID")
    created_at: datetime = Field(..., description="Template creation date")
    usage_count: int = Field(0, ge=0, description="Number of times template was used")


class ProjectCollaboration(BaseSchema):
    """Project collaboration schema"""
    project_id: UUID = Field(..., description="Project ID")
    user_id: UUID = Field(..., description="User ID")
    role: str = Field(..., description="User role in project")
    permissions: List[str] = Field(..., description="User permissions")
    joined_at: datetime = Field(..., description="When user joined project")
    last_activity: Optional[datetime] = Field(None, description="Last activity timestamp")
    
    @validator('role')
    def validate_role(cls, v):
        valid_roles = ['owner', 'editor', 'viewer', 'collaborator']
        if v not in valid_roles:
            raise ValueError(f"Invalid role. Must be one of: {', '.join(valid_roles)}")
        return v
    
    @validator('permissions')
    def validate_permissions(cls, v):
        valid_permissions = ['read', 'write', 'delete', 'share', 'export', 'admin']
        for permission in v:
            if permission not in valid_permissions:
                raise ValueError(f"Invalid permission: {permission}")
        return v


# Export all schemas
__all__ = [
    "ProjectBase",
    "ProjectCreate",
    "ProjectUpdate",
    "ProjectRead",
    "ProjectMetadata",
    "ProjectListResponse",
    "ProjectSearchRequest",
    "ProjectCreateRequest",
    "ProjectCreateResponse",
    "ProjectUpdateRequest",
    "ProjectUpdateResponse",
    "ProjectStats",
    "ProjectTemplate",
    "ProjectCollaboration"
]
