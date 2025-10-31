"""
Router Architecture Configuration
Defines consistent router organization and prefixing strategy
"""

from enum import Enum
from typing import Dict, List, Optional
from dataclasses import dataclass


class RouterCategory(Enum):
    """Router categories for organization"""
    AUTH = "auth"
    BUSINESS = "business"
    MEDIA = "media"
    AI = "ai"
    ADMIN = "admin"
    ANALYTICS = "analytics"
    CONTENT = "content"
    SOCIAL = "social"
    SYSTEM = "system"


class RouterPriority(Enum):
    """Router priority for registration order"""
    HIGH = 1      # Core business logic
    MEDIUM = 2    # Feature-specific
    LOW = 3       # Utility/admin
    SYSTEM = 4    # System/health


@dataclass
class RouterConfig:
    """Configuration for router registration"""
    
    # Router identification
    name: str
    category: RouterCategory
    priority: RouterPriority
    
    # URL configuration
    prefix: str
    tags: List[str]
    
    # Dependencies
    dependencies: Optional[List[str]] = None
    
    # Middleware
    middleware: Optional[List[str]] = None
    
    # Security
    requires_auth: bool = True
    requires_admin: bool = False
    
    # Documentation
    description: Optional[str] = None
    version: str = "1.0.0"


class RouterArchitecture:
    """Manages router architecture and organization"""
    
    def __init__(self):
        self.routers: Dict[str, RouterConfig] = {}
        self._initialize_router_configs()
    
    def _initialize_router_configs(self):
        """Initialize all router configurations"""
        
        # AUTHENTICATION ROUTERS
        self.routers["auth"] = RouterConfig(
            name="auth",
            category=RouterCategory.AUTH,
            priority=RouterPriority.HIGH,
            prefix="/api/auth",
            tags=["Authentication"],
            requires_auth=False,
            description="User authentication and authorization",
        )
        
        self.routers["user_management"] = RouterConfig(
            name="user_management",
            category=RouterCategory.AUTH,
            priority=RouterPriority.HIGH,
            prefix="/api/users",
            tags=["User Management"],
            description="User profile and account management",
        )
        
        # BUSINESS ROUTERS
        self.routers["projects"] = RouterConfig(
            name="projects",
            category=RouterCategory.BUSINESS,
            priority=RouterPriority.HIGH,
            prefix="/api/projects",
            tags=["Projects"],
            description="Project management and operations",
        )
        
        self.routers["credits"] = RouterConfig(
            name="credits",
            category=RouterCategory.BUSINESS,
            priority=RouterPriority.HIGH,
            prefix="/api/credits",
            tags=["Credits"],
            description="Credit system and balance management",
        )
        
        self.routers["payments"] = RouterConfig(
            name="payments",
            category=RouterCategory.BUSINESS,
            priority=RouterPriority.HIGH,
            prefix="/api/payments",
            tags=["Payments"],
            description="Payment processing and transactions",
        )
        
        self.routers["mailing"] = RouterConfig(
            name="mailing",
            category=RouterCategory.BUSINESS,
            priority=RouterPriority.MEDIUM,
            prefix="/api/mailing",
            tags=["Mailing"],
            description="Email subscription and mailing services",
        )
        
        # MEDIA ROUTERS
        self.routers["tracks"] = RouterConfig(
            name="tracks",
            category=RouterCategory.MEDIA,
            priority=RouterPriority.HIGH,
            prefix="/api/tracks",
            tags=["Tracks"],
            description="Audio track management",
        )
        
        self.routers["music_clip"] = RouterConfig(
            name="music_clip",
            category=RouterCategory.MEDIA,
            priority=RouterPriority.HIGH,
            prefix="/api/music-clip",
            tags=["Music Clip"],
            description="Music clip project management",
        )
        
        self.routers["music_analysis"] = RouterConfig(
            name="music_analysis",
            category=RouterCategory.MEDIA,
            priority=RouterPriority.MEDIUM,
            prefix="/api/music-analysis",
            tags=["Music Analysis"],
            description="Music analysis and processing",
        )
        
        self.routers["exports"] = RouterConfig(
            name="exports",
            category=RouterCategory.MEDIA,
            priority=RouterPriority.MEDIUM,
            prefix="/api/exports",
            tags=["Exports"],
            description="Media export and download",
        )
        
        # AI ROUTERS
        self.routers["jobs"] = RouterConfig(
            name="jobs",
            category=RouterCategory.AI,
            priority=RouterPriority.HIGH,
            prefix="/api/jobs",
            tags=["Jobs"],
            description="AI job management and monitoring",
        )
        
        self.routers["suno"] = RouterConfig(
            name="suno",
            category=RouterCategory.AI,
            priority=RouterPriority.MEDIUM,
            prefix="/api/ai/suno",
            tags=["Suno AI"],
            description="Suno AI music generation",
        )
        
        self.routers["llm"] = RouterConfig(
            name="llm",
            category=RouterCategory.AI,
            priority=RouterPriority.MEDIUM,
            prefix="/api/ai/llm",
            tags=["LLM AI"],
            description="LLM AI prompt generation (qwen-omni)",
        )
        
        self.routers["comfyui"] = RouterConfig(
            name="comfyui",
            category=RouterCategory.AI,
            priority=RouterPriority.MEDIUM,
            prefix="/api/ai/comfyui",
            tags=["ComfyUI"],
            description="ComfyUI workflow management",
        )
        
        self.routers["runpod"] = RouterConfig(
            name="runpod",
            category=RouterCategory.AI,
            priority=RouterPriority.MEDIUM,
            prefix="/api/ai/runpod",
            tags=["RunPod"],
            description="RunPod infrastructure management",
        )
        
        self.routers["producer_ai"] = RouterConfig(
            name="producer_ai",
            category=RouterCategory.AI,
            priority=RouterPriority.MEDIUM,
            prefix="/api/ai/producer",
            tags=["Producer AI"],
            description="Producer AI integration",
        )
        
        self.routers["prompts"] = RouterConfig(
            name="prompts",
            category=RouterCategory.AI,
            priority=RouterPriority.LOW,
            prefix="/api/ai/prompts",
            tags=["Prompts"],
            description="AI prompt management",
        )
        
        # CONTENT ROUTERS
        self.routers["visualizers"] = RouterConfig(
            name="visualizers",
            category=RouterCategory.CONTENT,
            priority=RouterPriority.MEDIUM,
            prefix="/api/visualizers",
            tags=["Visualizers"],
            description="Visual content generation",
        )
        
        self.routers["particles"] = RouterConfig(
            name="particles",
            category=RouterCategory.CONTENT,
            priority=RouterPriority.MEDIUM,
            prefix="/api/particles",
            tags=["Particles"],
            description="Particle system management",
        )
        
        # SOCIAL ROUTERS
        self.routers["social_media"] = RouterConfig(
            name="social_media",
            category=RouterCategory.SOCIAL,
            priority=RouterPriority.MEDIUM,
            prefix="/api/social-media",
            tags=["Social Media"],
            description="Social media integration",
        )
        
        self.routers["automation"] = RouterConfig(
            name="automation",
            category=RouterCategory.SOCIAL,
            priority=RouterPriority.MEDIUM,
            prefix="/api/automation",
            tags=["Automation"],
            description="Social media automation",
        )
        
        # ADMIN ROUTERS
        self.routers["admin_credits"] = RouterConfig(
            name="admin_credits",
            category=RouterCategory.ADMIN,
            priority=RouterPriority.LOW,
            prefix="/api/admin/credits",
            tags=["Admin - Credits"],
            requires_admin=True,
            description="Admin credit management",
        )
        
        self.routers["admin_stripe"] = RouterConfig(
            name="admin_stripe",
            category=RouterCategory.ADMIN,
            priority=RouterPriority.LOW,
            prefix="/api/admin/stripe",
            tags=["Admin - Stripe"],
            requires_admin=True,
            description="Admin Stripe management",
        )
        
        self.routers["admin_database"] = RouterConfig(
            name="admin_database",
            category=RouterCategory.ADMIN,
            priority=RouterPriority.LOW,
            prefix="/api/admin/database",
            tags=["Admin - Database"],
            requires_admin=True,
            description="Admin database management",
        )
        
        # ANALYTICS ROUTERS
        self.routers["stats"] = RouterConfig(
            name="stats",
            category=RouterCategory.ANALYTICS,
            priority=RouterPriority.MEDIUM,
            prefix="/api/analytics/stats",
            tags=["Analytics"],
            description="Application statistics and metrics",
        )
        
        self.routers["analysis"] = RouterConfig(
            name="analysis",
            category=RouterCategory.ANALYTICS,
            priority=RouterPriority.MEDIUM,
            prefix="/api/analytics/analysis",
            tags=["Analysis"],
            description="Data analysis and insights",
        )
        
        # STORAGE ROUTERS
        self.routers["storage"] = RouterConfig(
            name="storage",
            category=RouterCategory.SYSTEM,
            priority=RouterPriority.HIGH,
            prefix="/api/storage",
            tags=["Storage"],
            description="File storage and project management",
        )
        
        # SYSTEM ROUTERS
        self.routers["video_generation"] = RouterConfig(
            name="video_generation",
            category=RouterCategory.SYSTEM,
            priority=RouterPriority.SYSTEM,
            prefix="/api/system/video-generation",
            tags=["System - Video Generation"],
            description="System video generation workflows",
        )
        
        # ADDITIONAL SYSTEM ROUTERS
        self.routers["create_analysis"] = RouterConfig(
            name="create_analysis",
            category=RouterCategory.SYSTEM,
            priority=RouterPriority.MEDIUM,
            prefix="/api/music-analysis",
            tags=["Analysis Creation"],
            description="Analysis creation workflows",
        )
        
        self.routers["producer"] = RouterConfig(
            name="producer",
            category=RouterCategory.AI,
            priority=RouterPriority.MEDIUM,
            prefix="/api/ai/producer/core",
            tags=["Producer"],
            description="Producer AI workflows",
        )
        
        self.routers["producer_music_clip"] = RouterConfig(
            name="producer_music_clip",
            category=RouterCategory.AI,
            priority=RouterPriority.MEDIUM,
            prefix="/api/ai/producer/music-clip",
            tags=["Producer Music Clip"],
            description="Producer AI music clip workflows",
        )
        
        self.routers["workflows"] = RouterConfig(
            name="workflows",
            category=RouterCategory.SYSTEM,
            priority=RouterPriority.HIGH,
            requires_auth=True,
            prefix="/api/workflows",
            tags=["Workflows"],
            description="Workflow management and execution",
        )
        
        # job_events router removed - using event-driven approach instead
    
    def get_router_config(self, name: str) -> Optional[RouterConfig]:
        """Get router configuration by name"""
        return self.routers.get(name)
    
    def get_routers_by_category(self, category: RouterCategory) -> List[RouterConfig]:
        """Get all routers in a category"""
        return [config for config in self.routers.values() if config.category == category]
    
    def get_routers_by_priority(self, priority: RouterPriority) -> List[RouterConfig]:
        """Get all routers with a specific priority"""
        return [config for config in self.routers.values() if config.priority == priority]
    
    def get_router_registration_order(self) -> List[RouterConfig]:
        """Get routers in registration order (by priority)"""
        return sorted(self.routers.values(), key=lambda x: x.priority.value)
    
    def get_public_routers(self) -> List[RouterConfig]:
        """Get routers that don't require authentication"""
        return [config for config in self.routers.values() if not config.requires_auth]
    
    def get_admin_routers(self) -> List[RouterConfig]:
        """Get routers that require admin access"""
        return [config for config in self.routers.values() if config.requires_admin]
    
    def validate_router_config(self, config: RouterConfig) -> List[str]:
        """Validate router configuration and return any issues"""
        issues = []
        
        # Check prefix format
        if not config.prefix.startswith("/api"):
            issues.append(f"Router '{config.name}' prefix should start with '/api'")
        
        # Check for duplicate prefixes
        duplicate_prefixes = [name for name, cfg in self.routers.items() 
                            if cfg.prefix == config.prefix and name != config.name]
        if duplicate_prefixes:
            issues.append(f"Router '{config.name}' has duplicate prefix with: {duplicate_prefixes}")
        
        # Check tags
        if not config.tags:
            issues.append(f"Router '{config.name}' should have at least one tag")
        
        return issues
    
    def get_router_summary(self) -> Dict[str, any]:
        """Get summary of router architecture"""
        return {
            "total_routers": len(self.routers),
            "categories": {
                category.value: len(self.get_routers_by_category(category))
                for category in RouterCategory
            },
            "priorities": {
                priority.name: len(self.get_routers_by_priority(priority))
                for priority in RouterPriority
            },
            "public_routers": len(self.get_public_routers()),
            "admin_routers": len(self.get_admin_routers()),
            "routers": {
                name: {
                    "category": config.category.value,
                    "priority": config.priority.name,
                    "prefix": config.prefix,
                    "tags": config.tags,
                    "requires_auth": config.requires_auth,
                    "requires_admin": config.requires_admin,
                }
                for name, config in self.routers.items()
            }
        }


# Global router architecture instance
router_architecture = RouterArchitecture()


def get_router_architecture() -> RouterArchitecture:
    """Get the global router architecture instance"""
    return router_architecture


def get_router_config(name: str) -> Optional[RouterConfig]:
    """Get router configuration by name"""
    return router_architecture.get_router_config(name)


def get_router_registration_order() -> List[RouterConfig]:
    """Get routers in registration order"""
    return router_architecture.get_router_registration_order()


def validate_all_routers() -> Dict[str, List[str]]:
    """Validate all router configurations"""
    issues = {}
    for name, config in router_architecture.routers.items():
        router_issues = router_architecture.validate_router_config(config)
        if router_issues:
            issues[name] = router_issues
    return issues
