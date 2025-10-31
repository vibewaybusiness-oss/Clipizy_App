from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class VideoGenerationRequest(BaseModel):
    project_id: str = Field(..., description="ID of the project to generate video for")
    video_type: str = Field(..., description="Type of video (looped-static, looped-animated, recurring-scenes, scenes)")
    video_style: Optional[str] = Field(None, description="Visual style of the video")
    audio_visualizer: Optional[Dict[str, Any]] = Field(None, description="Audio visualizer configuration")
    transitions: Optional[Dict[str, Any]] = Field(None, description="Transition settings")
    budget: Optional[int] = Field(None, description="Budget in credits")
    track_ids: List[str] = Field(default_factory=list, description="IDs of tracks to include")
    settings: Optional[Dict[str, Any]] = Field(None, description="Additional generation settings")
    estimated_credits: Optional[int] = Field(None, description="Estimated credit cost")
    estimated_completion_time: Optional[datetime] = Field(None, description="Estimated completion time")
    priority: Optional[int] = Field(0, description="Job priority (higher = more priority)")
    auto: Optional[bool] = Field(
        False, description="Whether the generation should run fully automated without manual validation"
    )


class VideoGenerationResponse(BaseModel):
    job_id: str = Field(..., description="ID of the generation job")
    project_id: str = Field(..., description="ID of the project")
    status: str = Field(..., description="Current status of the generation")
    estimated_completion_time: Optional[datetime] = Field(None, description="Estimated completion time")
    message: str = Field(..., description="Response message")
    credits_info: Optional[Dict[str, Any]] = Field(None, description="Credit information including cost and balance")


class GenerationStatusResponse(BaseModel):
    job_id: str = Field(..., description="ID of the generation job")
    status: str = Field(..., description="Current status")
    progress_percentage: Optional[int] = Field(None, description="Progress percentage (0-100)")
    current_step: Optional[str] = Field(None, description="Current processing step")
    estimated_completion: Optional[datetime] = Field(None, description="Estimated completion time")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    output_paths: Optional[List[str]] = Field(None, description="Paths to generated videos")
    created_at: datetime = Field(..., description="Job creation time")
    started_at: Optional[datetime] = Field(None, description="Job start time")
    completed_at: Optional[datetime] = Field(None, description="Job completion time")


class ManualPromptUpdateRequest(BaseModel):
    prompt: str = Field(..., description="Prompt text to store for manual validation")
    approve: bool = Field(True, description="Whether the prompt is approved")
    scene_prompts: Optional[List[str]] = Field(None, description="Optional per scene prompts")


class ManualSceneGenerationRequest(BaseModel):
    scene_index: int = Field(..., description="Scene index to target")
    prompt: str = Field(..., description="Prompt for generation")
    video_style: Optional[str] = Field("modern", description="Video style for generation")


class ManualVideoGenerationRequest(BaseModel):
    scene_index: int = Field(..., description="Scene index to target")
    prompt: str = Field(..., description="Prompt for generation")
    video_style: Optional[str] = Field("modern", description="Video style for generation")


class ManualFinalizeRequest(BaseModel):
    approve: bool = Field(True, description="Whether to approve the final output")


class ManualStateResponse(BaseModel):
    stage: str
    prompt: Dict[str, Any]
    scenes: List[Dict[str, Any]]
    totals: Dict[str, Any]
    updated_at: datetime


# NEW SCHEMAS FOR STEP-BY-STEP WORKFLOW
class StepValidationRequest(BaseModel):
    job_id: str = Field(..., description="ID of the generation job")
    step: str = Field(..., description="Step to validate (prompts, images, videos)")
    item_id: Optional[str] = Field(None, description="Specific item ID to validate (optional)")
    validate_all: bool = Field(False, description="Whether to validate all items in the step")


class StepValidationResponse(BaseModel):
    success: bool = Field(..., description="Whether validation was successful")
    message: str = Field(..., description="Response message")
    next_step: Optional[str] = Field(None, description="Next step to process")
    items_validated: int = Field(0, description="Number of items validated")


class RegenerateRequest(BaseModel):
    job_id: str = Field(..., description="ID of the generation job")
    step: str = Field(..., description="Step to regenerate (images, videos)")
    item_id: str = Field(..., description="Specific item ID to regenerate")
    prompt: Optional[str] = Field(None, description="Custom prompt for regeneration")


class RegenerateResponse(BaseModel):
    success: bool = Field(..., description="Whether regeneration was successful")
    message: str = Field(..., description="Response message")
    new_item_id: str = Field(..., description="ID of the newly generated item")


class GenerationProgressResponse(BaseModel):
    job_id: str = Field(..., description="ID of the generation job")
    current_step: str = Field(..., description="Current step (prompts, images, videos)")
    status: str = Field(..., description="Overall status")
    progress: Dict[str, Any] = Field(..., description="Progress details for each step")
    items: List[Dict[str, Any]] = Field(..., description="Generated items for current step")
    can_proceed: bool = Field(False, description="Whether user can proceed to next step")