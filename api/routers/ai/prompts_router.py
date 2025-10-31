"""
Prompts Router
Handles AI prompt generation and management
"""

import logging
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session

from api.services.database import get_db
from api.services.auth.auth import get_current_user
from api.routers.factory import create_ai_router
from api.routers.base_router import create_standard_response
from api.models import User
from api.services.errors import handle_exception

logger = logging.getLogger(__name__)

# Create router using sophisticated architecture
router_wrapper = create_ai_router("prompts", "", ["Prompts"])  # Let architecture handle the prefix
router = router_wrapper.router


@router.get("/random")
async def get_random_prompt(
    prompt_type: str = Query(..., description="Type of prompt to generate"),
    source: str = Query("json", description="Source for prompt generation"),
    categories: Optional[str] = Query(None, description="Comma-separated categories"),
    instrumental: Optional[bool] = Query(None, description="Whether the prompt is for instrumental music"),
    video_type: Optional[str] = Query(None, description="Type of video for video prompts"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate a random prompt based on type and parameters"""
    try:
        # Import the prompt service
        from api.services.ai.prompt_service import PromptService
        
        prompt_service = PromptService()
        
        # Parse categories if provided
        category_list = categories.split(',') if categories else []
        
        # Generate the prompt based on type
        if prompt_type == "music":
            prompt = prompt_service.get_random_prompt(
                prompt_type="music",
                categories=category_list,
                instrumental=instrumental
            )
        elif prompt_type in ["image_prompts", "video_prompts"]:
            prompt = prompt_service.get_random_prompt(
                prompt_type=prompt_type,
                categories=category_list,
                video_type=video_type
            )
        elif prompt_type in ["random_image", "random_video"]:
            prompt = prompt_service.get_random_prompt(
                prompt_type=prompt_type,
                categories=category_list,
                video_type=video_type
            )
        else:
            raise HTTPException(status_code=400, detail=f"Invalid prompt type: {prompt_type}")
        
        return create_standard_response(
            data={
                "prompt": prompt,
                "type": prompt_type,
                "source": source,
                "categories": category_list,
                "instrumental": instrumental,
                "video_type": video_type
            },
            message="Random prompt generated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating random prompt: {str(e)}")
        raise handle_exception(e, "generating random prompt")


@router.get("/categories")
async def get_prompt_categories(
    prompt_type: str = Query(..., description="Type of prompt"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get available categories for a prompt type"""
    try:
        from api.services.ai.prompt_service import PromptService
        
        prompt_service = PromptService()
        categories = prompt_service.get_categories(prompt_type)
        
        return create_standard_response(
            data={
                "categories": categories,
                "type": prompt_type
            },
            message="Categories retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting prompt categories: {str(e)}")
        raise handle_exception(e, "getting prompt categories")


@router.get("/health")
async def health_check():
    """Health check endpoint for prompts router"""
    return create_standard_response(
        data={
            "status": "healthy",
            "service": "prompts"
        },
        message="Prompts service is healthy"
    )
