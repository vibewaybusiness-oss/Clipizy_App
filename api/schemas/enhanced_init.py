"""
Enhanced Schema Imports
Updated schema imports with enhanced validation and metadata
"""

# Import base schemas and utilities
from .base import (
    BaseSchema, TimestampMixin, IDMixin, UserMixin, ProjectMixin, FileMixin,
    MetadataMixin, StatusMixin, VersionMixin, StandardResponse, PaginatedResponse,
    ErrorResponse, ValidationUtils, FileSizeField, DurationField, FilenameField,
    ResolutionField, AudioFormatField, VideoFormatField, ImageFormatField,
    GenreField, VibeField, CommonFields
)

# Import enhanced response schemas
from .responses import (
    SuccessResponse, ErrorResponse as EnhancedErrorResponse, ValidationErrorResponse,
    FileUploadResponse, FileDeleteResponse, BatchOperationResponse, ListResponse,
    SearchResponse, AnalysisResponse, GenerationResponse, ProcessingResponse,
    ExportResponse, HealthCheckResponse, MetricsResponse, WebhookResponse,
    NotificationResponse
)

# Import enhanced media schemas
from .media.enhanced_audio import (
    AudioBase, AudioCreate, AudioUpdate, AudioRead, AudioMetadata, AudioAnalysis,
    AudioUploadRequest, AudioUploadResponse, AudioListResponse, AudioSearchRequest
)

from .media.enhanced_track import (
    TrackBase, TrackCreate, TrackUpdate, TrackRead, TrackMetadata, TrackAnalysis,
    TrackUploadRequest, TrackUploadResponse, TrackListResponse, TrackSearchRequest,
    TrackGenerationRequest, TrackGenerationResponse
)

from .media.enhanced_video import (
    VideoBase, VideoCreate, VideoUpdate, VideoRead, VideoMetadata, VideoAnalysis,
    VideoUploadRequest, VideoUploadResponse, VideoListResponse, VideoSearchRequest,
    VideoGenerationRequest, VideoGenerationResponse, VideoProcessingRequest,
    VideoProcessingResponse
)

# Import enhanced business schemas
from .business.enhanced_project import (
    ProjectBase, ProjectCreate, ProjectUpdate, ProjectRead, ProjectMetadata,
    ProjectListResponse, ProjectSearchRequest, ProjectCreateRequest, ProjectCreateResponse,
    ProjectUpdateRequest, ProjectUpdateResponse, ProjectStats, ProjectTemplate,
    ProjectCollaboration
)

# Import existing schemas (to be gradually replaced)
from .ai import (
    BaseWorkflowInput, CloudType, ComfyUIConfig, ComfyUIHealthStatus, ComfyUIRequest,
    FluxImageInput, GpuType, InterpolationInput, MMAudioInput, NetworkVolume,
    NetworkVolumeCreate, PodHealthStatus, PodUpdateRequest, QueueStatus,
    QwenImageInput, RestPodConfig, RunPodApiResponse, RunPodPod, RunPodUser,
    ServiceHealthStatus, Template, TemplateCreate, UpscalingInput, VoicemakerInput,
    WanVideoInput, WorkflowConfig, WorkflowInput, WorkflowRequest, WorkflowResult,
    WorkflowType
)

from .analytics import StatsRead

from .auth import (
    OAuthResponse, OAuthTokenRequest, OAuthUserInfo, SocialAccountCreate,
    SocialAccountRead, Token, UserCreate, UserLogin, UserRead, UserUpdate
)

from .business import (
    CreditsBalance, CreditsPurchaseRequest, CreditsSpendRequest,
    CreditsTransactionCreate, CreditsTransactionRead, DefaultSettings,
    JobCreate, JobResponse, PaymentCreate, PaymentIntentCreate,
    PaymentIntentResponse, PaymentRead, PaymentWebhookData, UserSettingsResponse,
    UserSettingsUpdate
)

from .media import (
    AnalysisResponse as MediaAnalysisResponse, ExportCreate, ExportRead,
    ImageCreate, ImageRead
)

# Enhanced schema exports
__all__ = [
    # Base schemas and utilities
    "BaseSchema", "TimestampMixin", "IDMixin", "UserMixin", "ProjectMixin", "FileMixin",
    "MetadataMixin", "StatusMixin", "VersionMixin", "StandardResponse", "PaginatedResponse",
    "ErrorResponse", "ValidationUtils", "FileSizeField", "DurationField", "FilenameField",
    "ResolutionField", "AudioFormatField", "VideoFormatField", "ImageFormatField",
    "GenreField", "VibeField", "CommonFields",
    
    # Enhanced response schemas
    "SuccessResponse", "EnhancedErrorResponse", "ValidationErrorResponse",
    "FileUploadResponse", "FileDeleteResponse", "BatchOperationResponse", "ListResponse",
    "SearchResponse", "AnalysisResponse", "GenerationResponse", "ProcessingResponse",
    "ExportResponse", "HealthCheckResponse", "MetricsResponse", "WebhookResponse",
    "NotificationResponse",
    
    # Enhanced media schemas
    "AudioBase", "AudioCreate", "AudioUpdate", "AudioRead", "AudioMetadata", "AudioAnalysis",
    "AudioUploadRequest", "AudioUploadResponse", "AudioListResponse", "AudioSearchRequest",
    
    "TrackBase", "TrackCreate", "TrackUpdate", "TrackRead", "TrackMetadata", "TrackAnalysis",
    "TrackUploadRequest", "TrackUploadResponse", "TrackListResponse", "TrackSearchRequest",
    "TrackGenerationRequest", "TrackGenerationResponse",
    
    "VideoBase", "VideoCreate", "VideoUpdate", "VideoRead", "VideoMetadata", "VideoAnalysis",
    "VideoUploadRequest", "VideoUploadResponse", "VideoListResponse", "VideoSearchRequest",
    "VideoGenerationRequest", "VideoGenerationResponse", "VideoProcessingRequest",
    "VideoProcessingResponse",
    
    # Enhanced business schemas
    "ProjectBase", "ProjectCreate", "ProjectUpdate", "ProjectRead", "ProjectMetadata",
    "ProjectListResponse", "ProjectSearchRequest", "ProjectCreateRequest", "ProjectCreateResponse",
    "ProjectUpdateRequest", "ProjectUpdateResponse", "ProjectStats", "ProjectTemplate",
    "ProjectCollaboration",
    
    # Existing schemas (for backward compatibility)
    "BaseWorkflowInput", "CloudType", "ComfyUIConfig", "ComfyUIHealthStatus", "ComfyUIRequest",
    "FluxImageInput", "GpuType", "InterpolationInput", "MMAudioInput", "NetworkVolume",
    "NetworkVolumeCreate", "PodHealthStatus", "PodUpdateRequest", "QueueStatus",
    "QwenImageInput", "RestPodConfig", "RunPodApiResponse", "RunPodPod", "RunPodUser",
    "ServiceHealthStatus", "Template", "TemplateCreate", "UpscalingInput", "VoicemakerInput",
    "WanVideoInput", "WorkflowConfig", "WorkflowInput", "WorkflowRequest", "WorkflowResult",
    "WorkflowType",
    
    "StatsRead",
    
    "OAuthResponse", "OAuthTokenRequest", "OAuthUserInfo", "SocialAccountCreate",
    "SocialAccountRead", "Token", "UserCreate", "UserLogin", "UserRead", "UserUpdate",
    
    "CreditsBalance", "CreditsPurchaseRequest", "CreditsSpendRequest",
    "CreditsTransactionCreate", "CreditsTransactionRead", "DefaultSettings",
    "JobCreate", "JobResponse", "PaymentCreate", "PaymentIntentCreate",
    "PaymentIntentResponse", "PaymentRead", "PaymentWebhookData", "UserSettingsResponse",
    "UserSettingsUpdate",
    
    "MediaAnalysisResponse", "ExportCreate", "ExportRead", "ImageCreate", "ImageRead"
]
