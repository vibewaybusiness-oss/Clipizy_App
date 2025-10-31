"""
Enhanced Response Schemas
Standardized response schemas for consistent API responses
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from pydantic import Field, validator

from api.schemas.base import BaseSchema, StandardResponse, PaginatedResponse, ErrorResponse


class SuccessResponse(BaseSchema):
    """Standard success response schema"""
    success: bool = Field(True, description="Success status")
    message: str = Field(..., description="Success message")
    data: Optional[Any] = Field(None, description="Response data")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")


class ErrorResponse(BaseSchema):
    """Standard error response schema"""
    success: bool = Field(False, description="Success status")
    error: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code")
    details: Optional[Dict[str, Any]] = Field(None, description="Error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")


class ValidationErrorResponse(BaseSchema):
    """Validation error response schema"""
    success: bool = Field(False, description="Success status")
    error: str = Field("Validation Error", description="Error message")
    error_code: str = Field("VALIDATION_ERROR", description="Error code")
    validation_errors: List[Dict[str, Any]] = Field(..., description="Validation error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")


class FileUploadResponse(BaseSchema):
    """Standard file upload response schema"""
    success: bool = Field(True, description="Upload success status")
    file_id: UUID = Field(..., description="Uploaded file ID")
    filename: str = Field(..., description="Original filename")
    file_path: str = Field(..., description="File path in storage")
    s3_url: Optional[str] = Field(None, description="S3 URL for file access")
    size_mb: Optional[float] = Field(None, description="File size in megabytes")
    content_type: Optional[str] = Field(None, description="File content type")
    message: str = Field(..., description="Response message")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")


class FileDeleteResponse(BaseSchema):
    """Standard file delete response schema"""
    success: bool = Field(True, description="Delete success status")
    file_id: UUID = Field(..., description="Deleted file ID")
    message: str = Field(..., description="Response message")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")


class BatchOperationResponse(BaseSchema):
    """Standard batch operation response schema"""
    success: bool = Field(True, description="Overall operation success status")
    total_items: int = Field(..., description="Total number of items processed")
    successful_items: int = Field(..., description="Number of successfully processed items")
    failed_items: int = Field(..., description="Number of failed items")
    results: List[Dict[str, Any]] = Field(..., description="Individual operation results")
    message: str = Field(..., description="Response message")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")


class ListResponse(BaseSchema):
    """Standard list response schema"""
    success: bool = Field(True, description="Success status")
    items: List[Any] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    page: int = Field(1, description="Current page number")
    per_page: int = Field(20, description="Items per page")
    pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(False, description="Whether there are more pages")
    has_prev: bool = Field(False, description="Whether there are previous pages")
    message: str = Field(..., description="Response message")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")


class SearchResponse(BaseSchema):
    """Standard search response schema"""
    success: bool = Field(True, description="Success status")
    query: Optional[str] = Field(None, description="Search query")
    results: List[Any] = Field(..., description="Search results")
    total: int = Field(..., description="Total number of results")
    page: int = Field(1, description="Current page number")
    per_page: int = Field(20, description="Results per page")
    pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(False, description="Whether there are more pages")
    has_prev: bool = Field(False, description="Whether there are previous pages")
    search_time_ms: Optional[float] = Field(None, description="Search execution time in milliseconds")
    message: str = Field(..., description="Response message")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")


class AnalysisResponse(BaseSchema):
    """Standard analysis response schema"""
    success: bool = Field(True, description="Analysis success status")
    analysis_id: UUID = Field(..., description="Analysis ID")
    target_id: UUID = Field(..., description="Target file/entity ID")
    analysis_type: str = Field(..., description="Type of analysis performed")
    results: Dict[str, Any] = Field(..., description="Analysis results")
    confidence: Optional[float] = Field(None, ge=0, le=1, description="Analysis confidence score")
    processing_time_ms: Optional[float] = Field(None, description="Processing time in milliseconds")
    message: str = Field(..., description="Response message")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")


class GenerationResponse(BaseSchema):
    """Standard AI generation response schema"""
    success: bool = Field(True, description="Generation success status")
    generation_id: UUID = Field(..., description="Generation ID")
    job_id: Optional[UUID] = Field(None, description="Generation job ID")
    target_id: Optional[UUID] = Field(None, description="Generated content ID")
    generation_type: str = Field(..., description="Type of generation performed")
    prompt: str = Field(..., description="Generation prompt used")
    model: Optional[str] = Field(None, description="AI model used")
    estimated_duration: Optional[int] = Field(None, description="Estimated generation time in seconds")
    cost_credits: Optional[float] = Field(None, description="Cost in credits")
    message: str = Field(..., description="Response message")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")


class ProcessingResponse(BaseSchema):
    """Standard processing response schema"""
    success: bool = Field(True, description="Processing success status")
    processing_id: UUID = Field(..., description="Processing ID")
    job_id: Optional[UUID] = Field(None, description="Processing job ID")
    target_id: UUID = Field(..., description="Target file/entity ID")
    processing_type: str = Field(..., description="Type of processing performed")
    status: str = Field(..., description="Processing status")
    estimated_duration: Optional[int] = Field(None, description="Estimated processing time in seconds")
    progress_percentage: Optional[float] = Field(None, ge=0, le=100, description="Processing progress percentage")
    message: str = Field(..., description="Response message")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    
    @validator('status')
    def validate_status(cls, v):
        valid_statuses = ['pending', 'processing', 'completed', 'failed', 'cancelled']
        if v not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
        return v


class ExportResponse(BaseSchema):
    """Standard export response schema"""
    success: bool = Field(True, description="Export success status")
    export_id: UUID = Field(..., description="Export ID")
    file_id: Optional[UUID] = Field(None, description="Exported file ID")
    export_type: str = Field(..., description="Type of export performed")
    format: str = Field(..., description="Export format")
    file_path: Optional[str] = Field(None, description="Exported file path")
    download_url: Optional[str] = Field(None, description="Download URL")
    size_mb: Optional[float] = Field(None, description="Exported file size in megabytes")
    duration: Optional[float] = Field(None, description="Export duration in seconds")
    credits_spent: Optional[float] = Field(None, description="Credits spent on export")
    message: str = Field(..., description="Response message")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")


class HealthCheckResponse(BaseSchema):
    """Standard health check response schema"""
    success: bool = Field(True, description="Health check success status")
    status: str = Field(..., description="Service status")
    service: str = Field(..., description="Service name")
    version: Optional[str] = Field(None, description="Service version")
    uptime_seconds: Optional[float] = Field(None, description="Service uptime in seconds")
    checks: Dict[str, Any] = Field(..., description="Health check results")
    message: str = Field(..., description="Response message")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    
    @validator('status')
    def validate_status(cls, v):
        valid_statuses = ['healthy', 'unhealthy', 'degraded', 'maintenance']
        if v not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
        return v


class MetricsResponse(BaseSchema):
    """Standard metrics response schema"""
    success: bool = Field(True, description="Success status")
    metrics: Dict[str, Any] = Field(..., description="Metrics data")
    period: Optional[str] = Field(None, description="Metrics time period")
    granularity: Optional[str] = Field(None, description="Metrics granularity")
    message: str = Field(..., description="Response message")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    
    @validator('period')
    def validate_period(cls, v):
        if v is not None:
            valid_periods = ['1h', '24h', '7d', '30d', '90d', '1y']
            if v not in valid_periods:
                raise ValueError(f"Invalid period. Must be one of: {', '.join(valid_periods)}")
        return v
    
    @validator('granularity')
    def validate_granularity(cls, v):
        if v is not None:
            valid_granularities = ['1m', '5m', '15m', '1h', '1d']
            if v not in valid_granularities:
                raise ValueError(f"Invalid granularity. Must be one of: {', '.join(valid_granularities)}")
        return v


class WebhookResponse(BaseSchema):
    """Standard webhook response schema"""
    success: bool = Field(True, description="Webhook success status")
    webhook_id: UUID = Field(..., description="Webhook ID")
    event_type: str = Field(..., description="Webhook event type")
    payload: Dict[str, Any] = Field(..., description="Webhook payload")
    delivery_attempt: int = Field(1, ge=1, description="Delivery attempt number")
    max_attempts: int = Field(3, ge=1, description="Maximum delivery attempts")
    next_retry_at: Optional[datetime] = Field(None, description="Next retry timestamp")
    message: str = Field(..., description="Response message")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")


class NotificationResponse(BaseSchema):
    """Standard notification response schema"""
    success: bool = Field(True, description="Notification success status")
    notification_id: UUID = Field(..., description="Notification ID")
    user_id: UUID = Field(..., description="Target user ID")
    notification_type: str = Field(..., description="Notification type")
    title: str = Field(..., description="Notification title")
    message: str = Field(..., description="Notification message")
    data: Optional[Dict[str, Any]] = Field(None, description="Notification data")
    read: bool = Field(False, description="Whether notification was read")
    message: str = Field(..., description="Response message")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")


# Export all response schemas
__all__ = [
    "SuccessResponse",
    "ErrorResponse", 
    "ValidationErrorResponse",
    "FileUploadResponse",
    "FileDeleteResponse",
    "BatchOperationResponse",
    "ListResponse",
    "SearchResponse",
    "AnalysisResponse",
    "GenerationResponse",
    "ProcessingResponse",
    "ExportResponse",
    "HealthCheckResponse",
    "MetricsResponse",
    "WebhookResponse",
    "NotificationResponse"
]
