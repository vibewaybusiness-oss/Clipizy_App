"""
ProducerAI API Routes
"""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel

from api.services.ai.producer.legacy_compatibility import producer_service as producer_ai_service
from api.routers.factory import create_ai_router
from api.middleware.auth_middleware import get_user_from_request
from api.services.auth.auth import get_current_user

logger = logging.getLogger(__name__)

# Create router using sophisticated architecture
router_wrapper = create_ai_router("producer_ai", "", ["Producer AI"])  # Let architecture handle the prefix
router = router_wrapper.router


class MusicGenerationRequest(BaseModel):
    prompt: str
    title: Optional[str] = None
    email: Optional[str] = None  # Get from environment or user settings
    password: Optional[str] = None  # Get from environment or user settings


class MusicGenerationResponse(BaseModel):
    success: bool
    song_id: Optional[str] = None
    title: Optional[str] = None
    prompt: Optional[str] = None
    audio_url: Optional[str] = None
    method: str
    timestamp: Optional[float] = None
    generation_completed: Optional[bool] = None
    download_success: Optional[bool] = None
    downloaded_files: Optional[list] = None
    download_path: Optional[str] = None
    network_urls: Optional[list] = None
    error: Optional[str] = None


@router.post("/generate", response_model=MusicGenerationResponse)
async def generate_music(music_request: MusicGenerationRequest, request: Request):
    """
    Generate music using ProducerAI complete workflow
    """
    try:
        current_user = get_user_from_request(request)
        logger.info(f"🎵 ProducerAI generation request from user: {current_user.email if current_user else 'unknown'} (uid: {current_user.id if current_user else 'unknown'})")
        logger.info(f"Prompt: {music_request.prompt}")

        result = await producer_ai_service.generate_music(
            prompt=music_request.prompt, title=music_request.title, email=music_request.email, password=music_request.password
        )

        return MusicGenerationResponse(**result)

    except Exception as e:
        logger.error(f"❌ ProducerAI generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Music generation failed: {str(e)}")


@router.get("/files")
async def get_available_files(request: Request):
    """
    Get list of available downloaded music files
    """
    try:
        files = await producer_ai_service.get_available_files()
        return {"files": files}

    except Exception as e:
        logger.error(f"❌ Failed to get available files: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get files: {str(e)}")


@router.get("/test")
async def test_producer_ai(current_user: dict = Depends(get_current_user)):
    """
    Test ProducerAI integration
    """
    try:
        logger.info(f"🧪 Testing ProducerAI integration for user {current_user['id']}...")

        # Test with a simple prompt
        result = await producer_ai_service.generate_music(prompt="create a simple test song", title="Test Song")

        return {"success": True, "message": "ProducerAI integration test completed", "result": result}

    except Exception as e:
        logger.error(f"❌ ProducerAI test failed: {e}")
        raise HTTPException(status_code=500, detail=f"Test failed: {str(e)}")
