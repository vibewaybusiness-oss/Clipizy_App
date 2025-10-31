#!/usr/bin/env python3
"""
clipizy FastAPI Main Application - Sophisticated Router Architecture
Uses middleware-based authentication and security with organized router management
"""

import asyncio
import os
import traceback
from contextlib import asynccontextmanager

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
from typing import Dict, Any
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from api.config.settings import settings

# Import middleware
from api.middleware.sanitizer_middleware import SanitizerMiddleware, SanitizationConfig, SanitizationLevel
from api.middleware.error_middleware import setup_error_handlers
from api.middleware.rate_limiting_middleware import RateLimitingMiddleware, RateLimitConfig
from api.middleware.security_headers_middleware import SecurityHeadersMiddleware, SecurityHeadersConfig
from api.middleware.monitoring_middleware import MonitoringMiddleware, MonitoringConfig
from api.middleware.auth_middleware import AuthMiddleware, AuthMiddlewareConfig
from api.middleware.localhost_logging_middleware import LocalhostLoggingMiddleware

# Import router architecture
from api.routers import (
    # Architecture and registry
    get_router_registry,
    register_router,
    register_all_routers_with_app,
    validate_router_registry,
    get_router_registry_summary,
    # Router instances
    auth_router,
    project_router,
    credits_router,
    payment_router,
    
    prompt_router,
    prompts_router,
    export_router,
    particle_router,
    visualizer_router,
    stats_router,
    social_media_router,
    automation_router,
    backend_storage_router,
)

# Import additional routers
from api.routers.ai.llm_router import router as llm_router
from api.routers.ai.runpod_router import router as runpod_router
from api.routers.chatbot.chatbot_router import router as chatbot_router
from api.routers.ai.producer_ai import router as producer_ai_router
from api.routers.admin.stripe_admin_router import router as stripe_admin_router
from api.routers.admin.credits_admin import router as credits_admin_router
from api.routers.admin.database_router import router as database_admin_router
from api.routers.admin.database_data_router import router as database_data_router
from api.routers.workflows import router as workflows_router
from api.routers.health_router import router as health_router
from api.routes.producer import router as producer_router
from api.routes.producer_music_clip import router as producer_music_clip_router

# Import services for initialization
# from api.services.sanitization import SanitizerConfig as MediaSanitizerConfig  # Module not found


class LargeBodyMiddleware(BaseHTTPMiddleware):
    """Middleware to handle large request bodies"""

    def __init__(self, app, max_body_size: int = 100 * 1024 * 1024):  # 100MB default
        super().__init__(app)
        self.max_body_size = max_body_size

    async def dispatch(self, request: Request, call_next):
        # Check content length if available
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.max_body_size:
            return JSONResponse(status_code=413, content={"error": "Payload Too Large", "max_size": self.max_body_size})

        # Read the body to prevent uvicorn's default 1MB limit
        try:
            body = await request.body()
            if len(body) > self.max_body_size:
                return JSONResponse(
                    status_code=413, content={"error": "Payload Too Large", "max_size": self.max_body_size}
                )
            # Store the body for later use
            request._body = body
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={"error": "Internal server error", "detail": str(e)})

        response = await call_next(request)
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    print("🚀 Starting clipizy API with sophisticated architecture...")

    # Initialize database tables
    try:
        from api.services.database import create_tables
        create_tables()
        print("✅ Database tables created/verified")
    except Exception as e:
        print(f"⚠️ Database table creation failed: {e}")

    # Queue manager removed

    # Validate router architecture
    try:
        issues = validate_router_registry()
        if issues:
            print(f"⚠️ Router validation issues found: {issues}")
        else:
            print("✅ Router architecture validation passed")
    except Exception as e:
        print(f"⚠️ Router validation failed: {e}")

    yield

    # Shutdown
    print("🛑 Shutting down clipizy API...")
    
    # Queue manager removed


def register_all_routers():
    """Register all routers with the registry"""
    registry = get_router_registry()
    
    # Register routers with their configurations (only those that are imported)
    registry.register_router("auth", auth_router)
    registry.register_router("projects", project_router)
    registry.register_router("credits", credits_router)
    registry.register_router("payments", payment_router)
    
    # suno router removed
    registry.register_router("llm", llm_router)
    registry.register_router("chatbot", chatbot_router)
    # include runpod router for pod signaling/health
    registry.register_router("runpod", runpod_router)
    # comfyui router remains removed
    registry.register_router("producer_ai", producer_ai_router)
    registry.register_router("prompts", prompts_router)
    registry.register_router("exports", export_router)
    registry.register_router("particles", particle_router)
    registry.register_router("visualizers", visualizer_router)
    registry.register_router("stats", stats_router)
    registry.register_router("social_media", social_media_router)
    registry.register_router("automation", automation_router)
    registry.register_router("storage", backend_storage_router)
    registry.register_router("admin_credits", credits_admin_router)
    registry.register_router("admin_stripe", stripe_admin_router)
    registry.register_router("admin_database", database_admin_router)
    registry.register_router("admin_database_data", database_data_router)
    registry.register_router("workflows", workflows_router)
    registry.register_router("producer", producer_router)
    registry.register_router("producer_music_clip", producer_music_clip_router)
    
    print("✅ All routers registered with registry")


def validate_router_architecture():
    """Validate router architecture and report issues"""
    try:
        issues = validate_router_registry()
        if issues:
            print("⚠️ Router architecture validation issues:")
            for router_name, router_issues in issues.items():
                print(f"  - {router_name}: {router_issues}")
        else:
            print("✅ Router architecture validation passed")
        
        # Print router summary
        summary = get_router_registry_summary()
        print(f"📊 Router Summary: {summary['total_registered']} routers registered")
        print(f"📊 Categories: {summary['categories']}")
        print(f"📊 Priorities: {summary['priorities']}")
        
        return issues
    except Exception as e:
        print(f"❌ Router validation failed: {e}")
        return {"validation_error": [str(e)]}


# Register all routers with the registry BEFORE app creation
try:
    register_all_routers()
    print("✅ All routers registered with sophisticated architecture")
except Exception as e:
    print(f"⚠️ Router registration failed: {e}")

# Create FastAPI app with sophisticated configuration
app = FastAPI(
    title="Clipizy API - Sophisticated Architecture",
    description="Advanced music and video generation platform with sophisticated router architecture",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Middleware configuration - CORS + Auth for proper authentication
print("✅ Using CORS + Auth middleware for proper authentication")

# CORS middleware - required for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins if hasattr(settings, 'cors_origins') else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Auth middleware - required for protected endpoints
auth_config = AuthMiddlewareConfig(
    public_paths=[
        "/health", 
        "/docs", 
        "/openapi.json", 
        "/redoc", 
        "/metrics",
        "/api/auth/google",  # OAuth initiation
        "/api/auth/google/callback",  # OAuth callback
        "/api/auth/github",  # GitHub OAuth initiation
        "/api/auth/github/callback",  # GitHub OAuth callback
        "/api/auth/youtube/callback",  # YouTube OAuth callback
        "/api/auth/register",  # User registration
        "/api/auth/login",  # User login
        "/api/auth/refresh",  # Token refresh
        "/api/analysis/analyze/comprehensive",  # Temporary: allow analysis without auth for testing
        "/api/ai/prompts/random",  # Temporary: allow prompts without auth for testing
        "/api/credits/pricing/calculate-budget",  # Allow pricing calculation without auth
        "/api/workflows/ws/"  # WebSocket endpoints for workflow updates
    ],
    skip_methods=["GET", "HEAD", "OPTIONS"],
    log_auth_attempts=True
)
app.add_middleware(AuthMiddleware, config=auth_config)

# Localhost logging middleware - replaces 127.0.0.1 with localhost in all logs
app.add_middleware(LocalhostLoggingMiddleware)

# DISABLED: Sanitizer middleware - causing body parsing issues with OAuth
# sanitizer_config = SanitizationConfig(
#     level=SanitizationLevel.MODERATE,
#     allow_html=False,
#     allow_scripts=False,
#     custom_patterns=[]
# )
# app.add_middleware(
#     SanitizerMiddleware,
#     config=sanitizer_config,
#     skip_paths=["/health", "/docs", "/openapi.json", "/redoc", "/metrics"],
#     skip_methods=["GET", "HEAD", "OPTIONS"],
#     log_violations=True
# )

# Setup error handlers
setup_error_handlers(app)

# Register all routers with the app using sophisticated architecture
register_all_routers_with_app(app)

# ADDITIONAL ROUTES FOR WORKFLOW COMPATIBILITY
# Direct route for /api/ai/generate-music (frontend workflow expects this path)
from api.services.chatbot.llm_requests.llm_requests import get_llm_request_handler
from api.services.storage.backend_storage import backend_storage_service
from api.models import Image as ImageModel

@app.post("/api/ai/generate-music")
async def generate_music_endpoint(music_request: Dict[str, Any], request: Request):
    """
    GENERATE MUSIC USING WORKFLOW-BASED LLM REQUESTS
    Direct endpoint matching frontend workflow expectations: /api/ai/generate-music
    """
    try:
        from api.middleware.auth_middleware import get_user_from_request
        from api.config.logging import get_prompt_logger
        logger = get_prompt_logger()
        
        current_user = get_user_from_request(request)
        logger.info(f"Music generation request from user: {current_user.email if current_user else 'unknown'}")
        
        workflow = music_request.get("workflow", "music-clip")
        prompt_name = music_request.get("prompt", "generate-music")
        description = music_request.get("description", "")
        lyrics = music_request.get("lyrics", "")
        is_instrumental = music_request.get("isInstrumental", False) or music_request.get("is_instrumental", False)
        genre = music_request.get("genre", "")
        
        if not description:
            raise HTTPException(status_code=400, detail="Description is required")
        
        handler = get_llm_request_handler()
        
        arguments = {
            "description": description,
            "genre": genre if genre else "music",
            "is_instrumental": "instrumental" if is_instrumental else "with vocals",
            "lyrics": lyrics if lyrics else "None provided"
        }
        
        optional_arguments = {}
        if lyrics:
            optional_arguments["optional_instructions"] = f"Additional context: The user has provided lyrics that should be considered: {lyrics}"
        else:
            optional_arguments["optional_instructions"] = ""
        
        response_text = await handler.process_request(
            workflow=workflow,
            prompt=prompt_name,
            arguments=arguments,
            optional_arguments=optional_arguments
        )
        
        return {
            "success": True,
            "workflow": workflow,
            "prompt": prompt_name,
            "generated_prompt": response_text.strip(),
            "description": description,
            "genre": genre,
            "is_instrumental": is_instrumental,
            "lyrics": lyrics
        }
        
    except HTTPException:
        raise
    except FileNotFoundError as e:
        logger.error(f"Workflow configuration not found: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        logger.error(f"Invalid request parameters: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to generate music: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate music: {str(e)}")

@app.post("/api/ai/generate-image-description")
async def generate_image_description_endpoint(request_data: Dict[str, Any], request: Request):
    """
    GENERATE IMAGE DESCRIPTION FROM REFERENCE IMAGES
    Uses uploaded reference images to generate descriptive text via vision LLM
    """
    try:
        from api.middleware.auth_middleware import get_user_from_request
        from api.services.database import get_db
        from api.config.logging import get_prompt_logger
        import traceback
        logger = get_prompt_logger()
        
        current_user = get_user_from_request(request)
        logger.info(f"Image description generation request from user: {current_user.email if current_user else 'unknown'}")
        
        project_id = request_data.get("project_id")
        if not project_id:
            raise HTTPException(status_code=400, detail="project_id is required")
        
        logger.info(f"Looking for reference images for project_id: {project_id}")
        
        db = next(get_db())
        
        try:
            reference_images = db.query(ImageModel).filter(
                ImageModel.project_id == project_id,
                ImageModel.type == 'reference'
            ).all()
        except Exception as db_error:
            logger.error(f"Database query error: {str(db_error)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"Database query failed: {str(db_error)}")
        
        logger.info(f"Found {len(reference_images)} reference images for project {project_id}")
        
        if not reference_images:
            raise HTTPException(status_code=404, detail=f"No reference images found for project {project_id}. Please upload an image first.")
        
        first_image = reference_images[0]
        if not first_image.file_path:
            raise HTTPException(status_code=400, detail="Reference image has no file path")
        
        image_s3_key = first_image.file_path
        logger.info(f"Using image with S3 key: {image_s3_key}")
        
        handler = get_llm_request_handler()
        
        try:
            from api.services.ai.runpod.queues_service import compute_pod_signal
            
            logger.info("Signaling for LLM pod availability...")
            await compute_pod_signal("llm-qwen3-vl")
            await compute_pod_signal("llm-mistral")
            
            response_text = await handler.process_request(
                workflow="music-clip",
                prompt="generate-image-description",
                arguments={},
                optional_arguments={},
                image_s3_key=image_s3_key,
                use_queue=True
            )
        except Exception as llm_error:
            error_msg = str(llm_error)
            logger.error(f"LLM request failed: {error_msg}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            # Return proper JSON error response
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": {
                        "error_code": "LLM_PROCESSING_ERROR",
                        "message": f"LLM processing failed: {error_msg}"
                    }
                }
            )
        
        logger.info(f"Generated image description for project {project_id}: {response_text[:100]}...")
        
        return {
            "success": True,
            "description": response_text.strip(),
            "image_count": len(reference_images),
            "image_id": str(first_image.id)
        }
        
    except HTTPException as http_exc:
        # Convert HTTPException to JSONResponse to ensure JSON format
        return JSONResponse(
            status_code=http_exc.status_code,
            content={
                "success": False,
                "error": {
                    "error_code": "HTTP_ERROR",
                    "message": str(http_exc.detail)
                }
            }
        )
    except Exception as e:
        error_trace = traceback.format_exc()
        logger.error(f"Failed to generate image description: {str(e)}")
        logger.error(f"Full traceback: {error_trace}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": {
                    "error_code": "INTERNAL_SERVER_ERROR",
                    "message": f"Failed to generate image description: {str(e)}"
                }
            }
        )


@app.post("/api/ai/test-image-s3-url")
async def test_image_s3_url_endpoint(request: Request):
    """
    TEST STEP 1: GENERATE PRESIGNED S3 URL FOR IMAGE
    Tests the S3 URL generation step only
    """
    try:
        import json
        from api.middleware.auth_middleware import get_user_from_request
        from api.services.database import get_db
        from api.config.logging import get_prompt_logger
        from api.services.storage.backend_storage import backend_storage_service
        import traceback
        logger = get_prompt_logger()
        
        # Safely parse request body
        try:
            body = await request.body()
            request_data = json.loads(body) if body else {}
        except Exception:
            request_data = {}
        
        current_user = get_user_from_request(request)
        project_id = request_data.get("project_id") if isinstance(request_data, dict) else None
        
        if not project_id:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": {"message": "project_id is required"}}
            )
        
        db = next(get_db())
        reference_images = db.query(ImageModel).filter(
            ImageModel.project_id == project_id,
            ImageModel.type == 'reference'
        ).all()
        
        if not reference_images:
            return JSONResponse(
                status_code=404,
                content={"success": False, "error": {"message": "No reference images found"}}
            )
        
        image_s3_key = reference_images[0].file_path
        presigned_url = backend_storage_service.get_short_lived_image_url(image_s3_key)
        
        return {
            "success": True,
            "step": "s3_url_generation",
            "image_s3_key": image_s3_key,
            "presigned_url": presigned_url,
            "url_length": len(presigned_url),
            "expires_in_seconds": 300
        }
    except Exception as e:
        logger.error(f"Test S3 URL generation failed: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": {"message": f"S3 URL generation failed: {str(e)}"}
            }
        )


@app.post("/api/ai/test-base64-conversion")
async def test_base64_conversion_endpoint(request: Request):
    """
    TEST STEP 2: CONVERT IMAGE URL TO BASE64
    Tests the base64 conversion step only
    """
    try:
        import json
        from api.services.ai.llm_service import debug_image_to_base64
        from api.config.logging import get_prompt_logger
        import traceback
        logger = get_prompt_logger()
        
        # Safely parse request body
        try:
            body = await request.body()
            request_data = json.loads(body) if body else {}
        except Exception:
            request_data = {}
        
        image_url = request_data.get("image_url") if isinstance(request_data, dict) else None
        if not image_url:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": {"message": "image_url is required"}}
            )
        
        debug_result = await debug_image_to_base64(image_url)
        
        return {
            "success": True,
            "step": "base64_conversion",
            "result": debug_result
        }
    except Exception as e:
        logger.error(f"Test base64 conversion failed: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": {"message": f"Base64 conversion failed: {str(e)}"}
            }
        )


@app.post("/api/ai/test-llm-call")
async def test_llm_call_endpoint(request: Request):
    """
    TEST STEP 3: TEST LLM CALL WITH BASE64 IMAGE
    Tests the LLM call step only (bypasses queue, direct call)
    """
    # Initialize logger early - use standard logging as fallback
    import logging
    import traceback
    import json
    import sys
    
    logger = logging.getLogger(__name__)
    
    # Ultimate wrapper - catch ANY exception, even from imports or syntax errors
    try:
        # Wrap entire function to ensure JSON response on any error
        try:
            # Try to get better logger if available
            try:
                from api.config.logging import get_prompt_logger
                logger = get_prompt_logger()
            except:
                pass
            
            # Parse request body manually to avoid FastAPI auto-parsing issues
            request_data: Dict[str, Any] = {}
            try:
                body = await request.body()
                if body:
                    request_data = json.loads(body)
                else:
                    request_data = {}
            except json.JSONDecodeError as json_err:
                logger.warning(f"Failed to parse request body as JSON: {json_err}")
                return JSONResponse(
                    status_code=400,
                    content={"success": False, "error": {"message": "Invalid JSON in request body"}}
                )
            except Exception as body_err:
                logger.warning(f"Failed to read request body: {body_err}")
                request_data = {}
            
            if not isinstance(request_data, dict):
                request_data = {}
            
            from api.services.ai.llm_service import generate_prompt, check_runpod_pod_health
            
            image_url = request_data.get("image_url") if isinstance(request_data, dict) else None
            prompt = request_data.get("prompt", "Describe this image in detail.") if isinstance(request_data, dict) else "Describe this image in detail."
            model = request_data.get("model", "qwen3-vl") if isinstance(request_data, dict) else "qwen3-vl"
            use_queue = request_data.get("use_queue", False) if isinstance(request_data, dict) else False
            
            if not image_url:
                return JSONResponse(
                    status_code=400,
                    content={"success": False, "error": {"message": "image_url is required"}}
                )
            
            if use_queue:
                # Use queue system
                try:
                    from api.services.ai.runpod.queues_service import compute_pod_signal
                    from api.services.ai.llm_queue_service import get_llm_queue_client
                    
                    logger.info("Using queue system for LLM call")
                    logger.info("Signaling for LLM pod availability...")
                    await compute_pod_signal("llm-qwen3-vl")
                    
                    queue_client = get_llm_queue_client()
                    logger.info("Queue client obtained, executing LLM request through queue...")
                    
                    # Get active pod ID from queue system - NO FALLBACKS
                    from api.services.ai.runpod.queues_service import _get_active_pods_for_workflow
                    active_pods = await _get_active_pods_for_workflow("llm-qwen3-vl")
                    
                    if not active_pods:
                        raise Exception(
                            "No active pods found for workflow 'llm-qwen3-vl'. "
                            "The queue system must have an active pod to process requests. "
                            "Check RunPod console or wait for pod creation."
                        )
                    
                    # Get pod ID from first active pod
                    pod_id = active_pods[0].get("id")
                    if not pod_id:
                        raise Exception(
                            "Active pod found but pod ID is missing. "
                            "This should not happen - pod ID must be present in pod data."
                        )
                    
                    logger.info(f"Using pod ID from queue system: {pod_id}")
                    
                    # Note: Queue system requires a worker loop to process requests
                    # If requests timeout, the worker may not be running
                    response_text = await queue_client.execute(
                        prompt=prompt,
                        model=model,
                        image_url=image_url,
                        timeout_seconds=60  # Shorter timeout for testing
                    )
                    logger.info("Queue execution completed successfully")
                    
                    # Get pod health for response
                    health_info = await check_runpod_pod_health(pod_id=pod_id)
                except asyncio.TimeoutError as te:
                    raise Exception(
                        f"Queue request timed out. The queue system may not have a worker running to process LLM requests. "
                        f"Try using direct call (Step 3a) instead, or ensure the queue worker is running. "
                        f"Original error: {str(te)}"
                    )
                except Exception as queue_error:
                    raise Exception(
                        f"Queue system error: {str(queue_error)}. "
                        f"The queue may not be processing LLM requests. Try using direct call (Step 3a) instead."
                    )
            else:
                # Direct call - requires pod_id from queue system
                from api.services.ai.runpod.queues_service import _get_active_pods_for_workflow
                
                # Get pod ID from queue system - NO FALLBACKS
                active_pods = await _get_active_pods_for_workflow("llm-qwen3-vl")
                
                if not active_pods:
                    raise Exception(
                        "No active pods found for workflow 'llm-qwen3-vl'. "
                        "Cannot make direct call without a valid pod ID. "
                        "Use queue system (Step 3b) or ensure a pod is running."
                    )
                
                pod_id = active_pods[0].get("id")
                if not pod_id:
                    raise Exception(
                        "Active pod found but pod ID is missing. "
                        "This should not happen - pod ID must be present in pod data."
                    )
                
                logger.info(f"Using pod ID from queue system for direct call: {pod_id}")
                
                # Get pod health for response
                health_info = await check_runpod_pod_health(pod_id=pod_id)
                
                response_text = await generate_prompt(
                    prompt=prompt,
                    image_url=image_url,
                    model=model,
                    pod_id=pod_id,  # Pass pod_id - NO FALLBACKS
                    timeout_seconds=300
                )
            
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "step": "llm_call",
                    "method": "queue" if use_queue else "direct",
                    "prompt": prompt,
                    "model": model,
                    "response": response_text,
                    "response_length": len(response_text),
                    "pod_health": {
                        "accessible": health_info.get("accessible", False),
                        "available_endpoints": health_info.get("available_endpoints", [])
                    }
                }
            )
        except Exception as e:
            # Import logger if not already imported
            if logger is None:
                try:
                    from api.config.logging import get_prompt_logger
                    logger = get_prompt_logger()
                except:
                    import logging
                    logger = logging.getLogger(__name__)
            
            error_msg = str(e)
            error_trace = traceback.format_exc()
            logger.error(f"Test LLM call failed: {error_msg}")
            logger.error(f"Traceback: {error_trace}")
            
            # Include pod health info in error response (try to get from queue if available)
            pod_health = {}
            try:
                from api.services.ai.llm_service import check_runpod_pod_health
                from api.services.ai.runpod.queues_service import _get_active_pods_for_workflow
                
                # Try to get pod ID from queue system
                active_pods = await _get_active_pods_for_workflow("llm-qwen3-vl")
                if active_pods and active_pods[0].get("id"):
                    pod_id = active_pods[0].get("id")
                    pod_health = await check_runpod_pod_health(pod_id=pod_id)
                else:
                    pod_health = {"error": "No active pods found in queue system"}
            except Exception as health_error:
                logger.warning(f"Failed to get pod health: {health_error}")
                pod_health = {"error": f"Failed to check pod health: {str(health_error)}"}
            
            # Ensure we always return valid JSON
            use_queue_val = request_data.get("use_queue", False) if isinstance(request_data, dict) else False
            error_response = {
                "success": False,
                "error": {
                    "error_code": "LLM_CALL_ERROR",
                    "message": error_msg
                },
                "pod_health": pod_health,
                "method": "queue" if use_queue_val else "direct"
            }
            
            logger.info(f"Returning error response: {error_response}")
            return JSONResponse(
                status_code=500,
                content=error_response
            )
    except Exception as outer_error:
        # Ultimate fallback - ensure we ALWAYS return JSON
        import logging
        fallback_logger = logging.getLogger(__name__)
        fallback_logger.critical(f"Critical error in test-llm-call endpoint: {outer_error}")
        fallback_logger.critical(f"Traceback: {traceback.format_exc()}")
        
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": {
                    "error_code": "CRITICAL_ERROR",
                    "message": f"Endpoint error: {str(outer_error)}"
                }
            }
        )

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with sophisticated architecture information"""
    return {
        "message": "Clipizy API - Sophisticated Architecture",
        "version": "2.0.0",
        "architecture": "sophisticated",
        "features": [
            "Middleware-based authentication",
            "Automatic input sanitization",
            "Rate limiting and abuse protection",
            "Security headers",
            "Comprehensive monitoring",
            "Organized router architecture",
            "Priority-based registration",
            "Automatic error handling"
        ],
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "metrics": "/metrics"
        },
        "router_summary": get_router_registry_summary()
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint - Auto-reload test"""
    return {
        "status": "healthy",
        "architecture": "sophisticated",
        "version": "2.0.0",
        "timestamp": "2024-01-01T00:00:00Z",
        "auto_reload": "enabled"
    }


if __name__ == "__main__":
    uvicorn.run(
        "api.main:app",
        host="localhost",
        port=8000,
        reload=True,
        log_level="info"
    )