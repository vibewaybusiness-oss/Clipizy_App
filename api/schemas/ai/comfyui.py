# comfyui.py
# ComfyUI schemas for API requests and responses
# ----------------------------------------------------------

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

# ============================================================================
# ENUMS
# ============================================================================


class WorkflowType(str, Enum):
    IMAGE_QWEN = "comfyui_image_qwen"
    IMAGE_QWEN_EDIT = "comfyui_image_qwen_edit"
    IMAGE_FLUX = "comfyui_image_flux"
    VIDEO_WAN = "comfyui_video_wan"
    AUDIO_MMAUDIO = "comfyui_audio_mmaudio"
    VOICE_VOICEMAKER = "comfyui_voice_voicemaker"
    UPSCALING = "comfyui_upscaling"
    INTERPOLATION = "comfyui_interpolation"
    LLM_LLM = "llm_llm"
    OLLAMA_LLM = "ollama"


# ============================================================================
# BASE SCHEMAS
# ============================================================================


class BaseWorkflowInput(BaseModel):
    """Base class for all workflow inputs"""

    seed: Optional[str] = None
    negative_prompt: Optional[str] = None


# ============================================================================
# IMAGE WORKFLOW SCHEMAS
# ============================================================================


class QwenImageInput(BaseWorkflowInput):
    """Input schema for Qwen image generation"""

    prompt: str = Field(..., description="Text prompt for image generation")
    reference_image_path: Optional[str] = Field(None, description="Path to reference image for editing")
    width: int = Field(1328, description="Image width")
    height: int = Field(1328, description="Image height")


class FluxImageInput(BaseWorkflowInput):
    """Input schema for Flux image generation"""

    prompt: str = Field(..., description="Text prompt for image generation")
    lora: Optional[str] = Field(None, description="LoRA model name")
    steps: int = Field(30, description="Number of generation steps")
    width: int = Field(1920, description="Image width")
    height: int = Field(1080, description="Image height")
    model: str = Field("flux1-schnell.safetensors", description="Model name")


# ============================================================================
# VIDEO WORKFLOW SCHEMAS
# ============================================================================


class WanVideoInput(BaseWorkflowInput):
    """Input schema for WAN video generation"""

    prompt: str = Field(..., description="Text prompt for video generation")
    input_image_path: Optional[str] = Field(None, description="Path to input image for image-to-video")
    width: int = Field(832, description="Video width")
    height: int = Field(480, description="Video height")
    num_frames: int = Field(121, description="Number of frames")
    frame_rate: int = Field(16, description="Frames per second")
    camera_motions: Optional[List[str]] = Field(None, description="List of camera motion types")
    speed: float = Field(0.2, description="Camera motion speed")


# ============================================================================
# AUDIO WORKFLOW SCHEMAS
# ============================================================================


class MMAudioInput(BaseWorkflowInput):
    """Input schema for MMAudio generation"""

    input_path: str = Field(..., description="Path to input video")
    prompt: str = Field(..., description="Audio generation prompt")
    steps: int = Field(25, description="Number of sampling steps")
    cfg: float = Field(4.5, description="CFG scale")
    mask_away_clip: bool = Field(False, description="Whether to mask away clip")
    force_offload: bool = Field(True, description="Force model offloading")
    loop_count: int = Field(0, description="Number of loops")
    crf: int = Field(19, description="Video compression quality")
    save_metadata: bool = Field(True, description="Save metadata")
    trim_to_audio: bool = Field(False, description="Trim video to audio length")


# ============================================================================
# VOICE WORKFLOW SCHEMAS
# ============================================================================


class VoicemakerInput(BaseWorkflowInput):
    """Input schema for Voicemaker text-to-speech"""

    text: str = Field(..., description="Text to convert to speech")
    audio_input: str = Field(..., description="Path to reference audio file for voice cloning")
    model: str = Field("VibeVoice-1.5B", description="VibeVoice model to use")
    diffusion_steps: int = Field(20, description="Number of diffusion steps")
    cfg_scale: float = Field(1.3, description="Classifier-free guidance scale")
    temperature: float = Field(0.95, description="Sampling temperature")
    top_p: float = Field(0.95, description="Top-p sampling parameter")
    use_sampling: bool = Field(False, description="Whether to use sampling")
    attention_type: str = Field("auto", description="Attention mechanism type")
    free_memory_after_generate: bool = Field(True, description="Whether to free memory after generation")


# ============================================================================
# PROCESSING WORKFLOW SCHEMAS
# ============================================================================


class UpscalingInput(BaseWorkflowInput):
    """Input schema for video upscaling"""

    input_path: str = Field(..., description="Path to input video")
    frame_rate: float = Field(25.0, description="Output frame rate")


class InterpolationInput(BaseWorkflowInput):
    """Input schema for video interpolation"""

    input_path: str = Field(..., description="Path to input video")
    multiplier: int = Field(4, description="Frame interpolation multiplier")
    target_fps: float = Field(24.0, description="Target frame rate")
    ckpt_name: str = Field("rife47.pth", description="RIFE checkpoint model name")
    fast_mode: bool = Field(True, description="Enable fast mode")
    ensemble: bool = Field(True, description="Enable ensemble mode")
    clear_cache_after_n_frames: int = Field(10, description="Clear cache after N frames")


# ============================================================================
# LLM WORKFLOW SCHEMAS
# ============================================================================


class LLMInput(BaseWorkflowInput):
    """Input schema for LLM generation (qwen-omni)"""

    prompt: str = Field(..., description="Text prompt for LLM generation")
    model: str = Field("qwen-omni", description="LLM model to use")
    stream: bool = Field(False, description="Whether to stream the response")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens to generate")
    temperature: Optional[float] = Field(None, description="Sampling temperature")
    top_p: Optional[float] = Field(None, description="Top-p sampling parameter")
    context: Optional[List[int]] = Field(None, description="Context tokens for conversation")


# ============================================================================
# RESULT SCHEMAS
# ============================================================================


class WorkflowResult(BaseModel):
    """Result schema for workflow execution"""

    success: bool
    request_id: str
    prompt_id: Optional[str] = None
    pod_id: Optional[str] = None
    pod_ip: Optional[str] = None
    files: List[str] = Field(default_factory=list)
    images: List[Dict[str, Any]] = Field(default_factory=list)
    error: Optional[str] = None
    status: str = "pending"
    response_text: Optional[str] = Field(None, description="LLM response text (for LLM workflows)")
    model: Optional[str] = Field(None, description="Model used for generation")
    total_duration: Optional[int] = Field(None, description="Total generation duration in nanoseconds")
    eval_count: Optional[int] = Field(None, description="Number of tokens evaluated")


class WorkflowRequest(BaseModel):
    """Request schema for workflow execution"""

    id: Optional[str] = Field(None, description="Unique request identifier")
    workflow_type: WorkflowType = Field(..., description="Type of workflow to execute")
    inputs: Dict[str, Any] = Field(..., description="Workflow-specific inputs")
    output_path: Optional[str] = Field(None, description="Output path for generated files")
    status: str = Field("pending", description="Request status")
    pod_id: Optional[str] = Field(None, description="Pod ID assigned to this request")
    pod_ip: Optional[str] = Field(None, description="Pod IP address")
    prompt_id: Optional[str] = Field(None, description="ComfyUI prompt ID")
    response_text: Optional[str] = Field(None, description="LLM response text (for LLM workflows)")
    error: Optional[str] = Field(None, description="Error message if failed")
    result: Optional[WorkflowResult] = Field(None, description="Workflow result")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")


# ============================================================================
# HEALTH CHECK SCHEMAS
# ============================================================================


class ComfyUIHealthStatus(BaseModel):
    """Health status for ComfyUI instance"""

    is_running: bool
    endcredits_accessible: List[str] = Field(default_factory=list)
    error: Optional[str] = None
    base_url: str
    comfyui_version: Optional[str] = None
    system_info: Optional[Dict[str, Any]] = None


class PodHealthStatus(BaseModel):
    """Health status for a specific pod"""

    pod_id: str
    is_ready: bool
    status: str
    ip: Optional[str] = None
    error: Optional[str] = None
    comfyui_health: Optional[ComfyUIHealthStatus] = None


# ============================================================================
# CONFIGURATION SCHEMAS
# ============================================================================


class WorkflowConfig(BaseModel):
    """Configuration for a specific workflow"""

    maxQueueSize: int = Field(3, description="Maximum queue size for this workflow")
    network_volume: Optional[str] = Field(None, description="Network volume ID")
    template: Optional[str] = Field(None, description="Template ID")
    description: Optional[str] = Field(None, description="Workflow description")


class ActivePod(BaseModel):
    """Active pod information"""

    id: str = Field(..., description="Pod ID")
    workflow_name: str = Field(..., description="Workflow name")
    created_at: int = Field(..., description="Creation timestamp")
    last_used_at: int = Field(..., description="Last used timestamp")
    pause_timeout_at: int = Field(..., description="Pause timeout timestamp")
    terminate_timeout_at: int = Field(..., description="Terminate timeout timestamp")
    status: str = Field(..., description="Pod status")
    request_queue: List[WorkflowRequest] = Field(default_factory=list, description="Request queue")
    paused_at: Optional[int] = Field(None, description="Pause timestamp")
    pod_ip: Optional[str] = Field(None, description="Pod IP address")
    comfyui_port: Optional[int] = Field(None, description="ComfyUI port")

    # Legacy field names for backward compatibility
    @property
    def workflowName(self) -> str:
        return self.workflow_name

    @property
    def requestQueue(self) -> List[WorkflowRequest]:
        return self.request_queue


class ComfyUIConfig(BaseModel):
    """ComfyUI configuration schema"""

    workflows: Dict[str, WorkflowConfig] = Field(default_factory=dict)
    defaults: WorkflowConfig = Field(default_factory=WorkflowConfig)


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "WorkflowType",
    "BaseWorkflowInput",
    "QwenImageInput",
    "FluxImageInput",
    "WanVideoInput",
    "MMAudioInput",
    "VoicemakerInput",
    "UpscalingInput",
    "InterpolationInput",
    "LLMInput",
    "WorkflowResult",
    "WorkflowRequest",
    "ComfyUIHealthStatus",
    "PodHealthStatus",
    "WorkflowConfig",
    "ComfyUIConfig",
    "ActivePod",
]
