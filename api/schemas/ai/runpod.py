# runpod.py
# RunPod schemas for API requests and responses
# ----------------------------------------------------------

from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar, Union

from pydantic import BaseModel, Field

T = TypeVar("T")

# ============================================================================
# BASE SCHEMAS
# ============================================================================


class RunPodApiResponse(BaseModel, Generic[T]):
    """Generic API response wrapper for RunPod"""

    success: bool
    data: Optional[T] = None
    error: Optional[str] = None


# ============================================================================
# USER SCHEMAS
# ============================================================================


class RunPodUser(BaseModel):
    """RunPod user information"""

    id: str
    email: str
    min_balance: float


# ============================================================================
# POD SCHEMAS
# ============================================================================


class RunPodPod(BaseModel):
    """RunPod pod information"""

    id: str
    name: Optional[str] = None
    image_name: Optional[str] = Field(alias="imageName", default=None)
    uptime_seconds: int = Field(alias="uptimeSeconds", default=0)
    cost_per_hr: float = Field(alias="costPerHr", default=0.0)
    created_at: Optional[str] = Field(alias="createdAt", default=None)
    status: Optional[str] = None
    desired_status: Optional[str] = Field(alias="desiredStatus", default=None)
    ip: Optional[str] = None
    public_ip: Optional[str] = Field(alias="publicIp", default=None)
    machine_id: Optional[str] = Field(alias="machineId", default=None)
    gpu_count: Optional[int] = Field(alias="gpuCount", default=None)
    memory_in_gb: Optional[float] = Field(alias="memoryInGb", default=None)
    vcpu_count: Optional[int] = Field(alias="vcpuCount", default=None)
    last_started_at: Optional[str] = Field(alias="lastStartedAt", default=None)
    port_mappings: Optional[Dict[str, int]] = Field(alias="portMappings", default=None)
    ports: Optional[List[str]] = Field(default=None)
    network_volume_id: Optional[str] = Field(alias="networkVolumeId", default=None)
    volume_in_gb: Optional[int] = Field(alias="volumeInGb", default=None)
    volume_mount_path: Optional[str] = Field(alias="volumeMountPath", default=None)


class RestPodConfig(BaseModel):
    """Configuration for creating a new pod"""

    gpu_type_ids: Optional[List[str]] = Field(alias="gpuTypeIds", default=None)
    image_name: Optional[str] = Field(alias="imageName", default=None)
    name: str
    env: Optional[Dict[str, str]] = None
    container_disk_in_gb: int = Field(alias="containerDiskInGb")
    volume_in_gb: Optional[int] = Field(alias="volumeInGb", default=None)
    volume_mount_path: Optional[str] = Field(alias="volumeMountPath", default=None)
    network_volume_id: Optional[str] = Field(alias="networkVolumeId", default=None)
    gpu_count: Optional[int] = Field(alias="gpuCount", default=1)
    min_memory_in_gb: Optional[int] = Field(alias="minMemoryInGb", default=None)
    country_code: Optional[str] = Field(alias="countryCode", default=None)
    support_public_ip: Optional[bool] = Field(alias="supportPublicIp", default=True)
    min_vcpu_count: Optional[int] = Field(alias="minVcpuCount", default=None)
    ports: Optional[List[str]] = None
    template_id: Optional[str] = Field(alias="templateId", default=None)
    # Additional fields from old working approach
    cloud_type: Optional[str] = Field(alias="cloudType", default="SECURE")
    compute_type: Optional[str] = Field(alias="computeType", default="GPU")
    vcpu_count: Optional[int] = Field(alias="vcpuCount", default=4)
    data_center_priority: Optional[str] = Field(alias="dataCenterPriority", default="availability")
    gpu_type_priority: Optional[str] = Field(alias="gpuTypePriority", default="availability")
    cpu_flavor_priority: Optional[str] = Field(alias="cpuFlavorPriority", default="availability")
    min_ram_per_gpu: Optional[int] = Field(alias="minRAMPerGPU", default=8)
    min_vcpu_per_gpu: Optional[int] = Field(alias="minVCPUPerGPU", default=2)
    interruptible: Optional[bool] = Field(default=False)
    locked: Optional[bool] = Field(default=False)
    global_networking: Optional[bool] = Field(alias="globalNetworking", default=True)

    class Config:
        populate_by_name = True


class PodRecruitmentConfig(BaseModel):
    """Configuration for recruiting a new pod"""

    workflow_name: str = Field(..., description="Name of the workflow")
    gpu_type_ids: List[str] = Field(..., description="GPU type IDs")
    image_name: str = Field(..., description="Docker image name")
    name: str = Field(..., description="Pod name")
    env: Optional[Dict[str, str]] = Field(None, description="Environment variables")
    container_disk_in_gb: int = Field(..., description="Container disk size in GB")
    volume_in_gb: Optional[int] = Field(None, description="Volume size in GB")
    volume_mount_path: Optional[str] = Field(None, description="Volume mount path")
    network_volume_id: Optional[str] = Field(None, description="Network volume ID")
    gpu_count: Optional[int] = Field(1, description="Number of GPUs")
    min_memory_in_gb: Optional[int] = Field(None, description="Minimum memory in GB")
    country_code: Optional[str] = Field(None, description="Country code")
    support_public_ip: Optional[bool] = Field(alias="supportPublicIp", default=None)
    min_vcpu_count: Optional[int] = Field(alias="minVcpuCount", default=None)
    ports: Optional[List[str]] = None
    docker_args: Optional[str] = Field(alias="dockerArgs", default=None)


class PodConnectionInfo(BaseModel):
    """Pod connection information"""

    pod_id: str = Field(..., description="Pod ID")
    ip: Optional[str] = Field(None, description="Pod IP address")
    port: Optional[int] = Field(None, description="Port number")
    status: str = Field(..., description="Pod status")
    ready: bool = Field(False, description="Whether pod is ready")


class AccountSummary(BaseModel):
    """Account summary information"""

    balance: Optional[float] = Field(None, description="Account balance")
    credits: Optional[float] = Field(None, description="Available credits")
    total_pods: Optional[int] = Field(None, description="Total number of pods")
    active_pods: Optional[int] = Field(None, description="Number of active pods")
    total_runtime: Optional[float] = Field(None, description="Total runtime in hours")


class PodUpdateRequest(BaseModel):
    """Request schema for updating a pod"""

    name: Optional[str] = None
    env: Optional[Dict[str, str]] = None
    docker_args: Optional[str] = Field(alias="dockerArgs", default=None)


# ============================================================================
# NETWORK VOLUME SCHEMAS
# ============================================================================


class NetworkVolume(BaseModel):
    """RunPod network volume information"""

    id: str
    name: str
    size: float
    data_center_id: str = Field(alias="dataCenterId")


class NetworkVolumeCreate(BaseModel):
    """Request schema for creating a network volume"""

    name: str
    size: float
    data_center_id: str = Field(alias="dataCenterId")


# ============================================================================
# GPU AND CLOUD SCHEMAS
# ============================================================================


class GpuType(BaseModel):
    """RunPod GPU type information"""

    id: str
    display_name: str = Field(alias="displayName")
    memory_in_gb: float = Field(alias="memoryInGb")
    secure_cloud: bool = Field(alias="secureCloud")
    community_cloud: bool = Field(alias="communityCloud")
    lowest_price: Optional[float] = Field(alias="lowestPrice", default=None)


class CloudType(BaseModel):
    """RunPod cloud type information"""

    id: str
    name: str


# ============================================================================
# WORKFLOW SCHEMAS
# ============================================================================


class WorkflowInput(BaseModel):
    """Input schema for workflow execution"""

    prompt: str
    negative_prompt: Optional[str] = Field(alias="negativePrompt", default="")
    width: int = 1328
    height: int = 1328
    seed: int = -1
    steps: int = 4
    cfg: Optional[float] = Field(default=1.0)
    sampler: Optional[str] = Field(default="euler")
    scheduler: Optional[str] = Field(default="simple")


class WorkflowResult(BaseModel):
    """Result schema for workflow execution"""

    success: bool
    files: Optional[List[str]] = None
    images: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None
    request_id: Optional[str] = Field(alias="requestId", default=None)
    pod_id: Optional[str] = Field(alias="podId", default=None)
    pod_ip: Optional[str] = Field(alias="podIp", default=None)
    prompt_id: Optional[str] = Field(alias="promptId", default=None)
    status: Optional[str] = None


# ============================================================================
# REQUEST AND QUEUE SCHEMAS
# ============================================================================


class ComfyUIRequest(BaseModel):
    """ComfyUI workflow request"""

    id: str
    workflow_name: str = Field(alias="workflowName")
    inputs: WorkflowInput
    status: str = "pending"  # pending, processing, completed, failed
    pod_id: Optional[str] = Field(alias="podId", default=None)
    pod_ip: Optional[str] = Field(alias="podIp", default=None)
    prompt_id: Optional[str] = Field(alias="promptId", default=None)
    created_at: datetime = Field(alias="createdAt", default_factory=datetime.now)
    updated_at: datetime = Field(alias="updatedAt", default_factory=datetime.now)
    completed_at: Optional[datetime] = Field(alias="completedAt", default=None)
    result: Optional[WorkflowResult] = None
    error: Optional[str] = None


class QueueStatus(BaseModel):
    """Queue status information"""

    active_pods: List[Dict[str, Any]] = Field(alias="activePods", default_factory=list)
    pending_requests: List[ComfyUIRequest] = Field(alias="pendingRequests", default_factory=list)
    completed_requests: List[ComfyUIRequest] = Field(alias="completedRequests", default_factory=list)
    failed_requests: List[ComfyUIRequest] = Field(alias="failedRequests", default_factory=list)


# ============================================================================
# TEMPLATE SCHEMAS
# ============================================================================


class Template(BaseModel):
    """RunPod template information"""

    id: str
    name: str
    description: Optional[str] = None
    image_name: str = Field(alias="imageName")
    gpu_type_ids: List[str] = Field(alias="gpuTypeIds")
    is_public: bool = Field(alias="isPublic", default=False)
    is_runpod: bool = Field(alias="isRunpod", default=False)
    is_endpoint_bound: bool = Field(alias="isEndpointBound", default=False)
    created_at: Optional[datetime] = Field(alias="createdAt", default=None)
    updated_at: Optional[datetime] = Field(alias="updatedAt", default=None)


class TemplateCreate(BaseModel):
    """Request schema for creating a template"""

    name: str
    description: Optional[str] = None
    image_name: str = Field(alias="imageName")
    gpu_type_ids: List[str] = Field(alias="gpuTypeIds")
    env: Optional[Dict[str, str]] = None
    docker_args: Optional[str] = Field(alias="dockerArgs", default=None)


# ============================================================================
# HEALTH CHECK SCHEMAS
# ============================================================================


class PodHealthStatus(BaseModel):
    """Pod health status"""

    pod_id: str
    is_healthy: bool
    status: str
    last_check: datetime = Field(alias="lastCheck", default_factory=datetime.now)
    error: Optional[str] = None
    response_time_ms: Optional[float] = Field(alias="responseTimeMs", default=None)


class ServiceHealthStatus(BaseModel):
    """Overall service health status"""

    is_healthy: bool
    total_pods: int = Field(alias="totalPods", default=0)
    active_pods: int = Field(alias="activePods", default=0)
    healthy_pods: int = Field(alias="healthyPods", default=0)
    last_check: datetime = Field(alias="lastCheck", default_factory=datetime.now)
    errors: List[str] = Field(default_factory=list)


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "RunPodApiResponse",
    "RunPodUser",
    "RunPodPod",
    "RestPodConfig",
    "PodRecruitmentConfig",
    "PodConnectionInfo",
    "AccountSummary",
    "PodUpdateRequest",
    "NetworkVolume",
    "NetworkVolumeCreate",
    "GpuType",
    "CloudType",
    "WorkflowInput",
    "WorkflowResult",
    "ComfyUIRequest",
    "QueueStatus",
    "Template",
    "TemplateCreate",
    "PodHealthStatus",
    "ServiceHealthStatus",
]
