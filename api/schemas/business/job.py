"""
Job schemas for API requests and responses
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from api.models.job import JobStatus, JobType

# ---------- REQUEST ----------


class JobCreate(BaseModel):
    project_id: UUID
    job_type: JobType
    step: Optional[str] = Field(None, description="Pipeline step: music, analysis, visuals, export")
    config: Optional[Dict[str, Any]] = None
    priority: int = Field(default=0, ge=0, le=10)
    depends_on: Optional[List[UUID]] = Field(None, description="IDs of jobs this job depends on")
    max_retries: int = Field(default=1, ge=0, le=5)


# ---------- RESPONSE ----------


class JobResponse(BaseModel):
    id: UUID
    project_id: UUID
    user_id: UUID
    job_type: JobType
    step: Optional[str]
    status: JobStatus

    # Config and execution
    config: Optional[Dict[str, Any]]
    priority: int
    retry_count: int
    max_retries: int

    # RunPod / GPU info
    runpod_pod_id: Optional[str]
    runpod_job_id: Optional[str]
    worker_node: Optional[str]

    # Outputs
    output_paths: Optional[Dict[str, str]] = None
    artifacts: Optional[Dict[str, Any]] = Field(
        None, description="Structured outputs: e.g. {track_id, video_id, image_id}"
    )

    # Logs and errors
    logs: Optional[str]
    error_message: Optional[str]

    # Progress
    progress_percentage: int
    current_step: Optional[str] = None
    estimated_completion: Optional[datetime] = None

    # Resource usage
    credits_spent: Optional[int] = None
    gpu_hours: Optional[float] = None

    # Timestamps
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


# ---------- LIGHTWEIGHT RESPONSES ----------


class JobStatusResponse(BaseModel):
    job_id: UUID
    status: JobStatus
    progress_percentage: int
    current_step: Optional[str] = None
    estimated_completion: Optional[datetime] = None
    error_message: Optional[str] = None


class JobListResponse(BaseModel):
    jobs: List[JobResponse]
    total: int
    page: int
    per_page: int
    has_next: bool
    has_prev: bool
