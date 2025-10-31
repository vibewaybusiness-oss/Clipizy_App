# Import router architecture and registry
from .architecture import (
    RouterConfig,
    RouterCategory,
    RouterPriority,
    get_router_architecture,
    validate_all_routers,
)
from .registry import (
    RouterRegistry,
    get_router_registry,
    register_router,
    get_router,
    register_all_routers_with_app,
    validate_router_registry,
    get_router_registry_summary,
)
from .factory import (
    RouterFactory,
    get_router_factory,
    create_router,
    create_auth_router,
    create_business_router,
    create_media_router,
    create_ai_router,
    create_admin_router,
    create_analytics_router,
    create_content_router,
    create_social_router,
    create_system_router,
)
from .base_router import (
    BaseRouter,
    AuthRouter,
    AdminRouter,
    BusinessRouter,
    MediaRouter,
    AIRouter,
    create_standard_response,
    create_error_response,
    validate_user_access,
)

# Import from organized subdirectories
from .ai import prompt_router, prompts_router
from .ai.runpod_router import router as runpod_router
from .analytics import stats_router
from .auth import auth_router
from .business import credits_router, payment_router, project_router, mailing_router
from .content import export_router, particle_router, visualizer_router
# from .media import (
#     music_clip_router removed - functionality moved to storage router
# )
from .social import automation_router, social_media_router
from .storage import backend_storage_router

# Alias for backward compatibility - credits_router already imported above

all_routers = [
    auth_router,
    project_router,
    export_router,
    stats_router,
    prompt_router,
    prompts_router,
    runpod_router,
    # music_clip_router removed - functionality moved to storage router
    visualizer_router,
    particle_router,
    credits_router,
    payment_router,
    mailing_router,
    social_media_router,
    automation_router,
    backend_storage_router,
]
