"""
ProducerAI Music Clip API Routes
"""

import logging
import time
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from api.services.ai.producer.producer_music_clip_service import producer_music_clip_service
from api.services.auth import get_current_user_simple

logger = logging.getLogger(__name__)


class GenerateMusicRequest(BaseModel):
    prompt: str
    title: Optional[str] = None
    is_instrumental: bool = False
    lyrics: Optional[str] = None
    project_id: Optional[str] = None


router = APIRouter(prefix="/api/ai/producer/music-clip", tags=["producer-music-clip"])


@router.post("/generate")
async def generate_music_for_clip(request: GenerateMusicRequest, current_user: dict = Depends(get_current_user_simple)):
    """
    Generate music for music clip workflow using ProducerAI

    Args:
        prompt: Music generation prompt
        title: Optional title for the song
        is_instrumental: Whether to generate instrumental music
        lyrics: Optional lyrics for the song
        project_id: Project ID for organizing files

    Returns:
        Generation result with S3 URLs
    """
    try:
        logger.info(
            f"ProducerAI music clip generation request from user {current_user.get('email', 'unknown')}: {request.prompt}"
        )

        result = await producer_music_clip_service.generate_music_for_clip(
            prompt=request.prompt,
            title=request.title,
            is_instrumental=request.is_instrumental,
            lyrics=request.lyrics,
            project_id=request.project_id,
            user_id=current_user.get("user_id") or current_user.get("sub"),
        )

        if result["success"]:
            logger.info(f"ProducerAI music clip generation successful: {result.get('generation_id')}")

            # Clean up local files after successful S3 upload
            if result.get("generation_id"):
                await producer_music_clip_service.cleanup_local_files(result["generation_id"])

            return result
        else:
            logger.error(f"ProducerAI music clip generation failed: {result.get('error')}")
            raise HTTPException(status_code=500, detail=result.get("error", "Generation failed"))

    except Exception as e:
        logger.error(f"ProducerAI music clip generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_music_clip_status(current_user: dict = Depends(get_current_user_simple)):
    """
    Get the current status of the ProducerAI session manager

    Returns:
        Session status including tab information and queue status
    """
    try:
        status = await producer_music_clip_service.get_session_status()
        return {"success": True, "status": status, "timestamp": time.time()}
    except Exception as e:
        logger.error(f"Failed to get music clip status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/session-status")
async def get_session_status(current_user: dict = Depends(get_current_user_simple)):
    """
    Get ProducerAI music clip service status

    Returns:
        Service status information
    """
    try:
        status = await producer_music_clip_service.get_session_status()
        return {"success": True, "status": status, "timestamp": time.time()}
    except Exception as e:
        logger.error(f"Failed to get session status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/request-status/{request_id}")
async def get_request_status(request_id: str, current_user: dict = Depends(get_current_user_simple)):
    """
    Get the status of a specific music generation request

    Args:
        request_id: The request ID to check

    Returns:
        Request status information
    """
    try:
        result = await producer_music_clip_service.get_request_status(request_id)
        return result
    except Exception as e:
        logger.error(f"Failed to get request status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/test-status")
async def test_status():
    """
    Test endpoint to check session manager status without authentication
    """
    try:
        status = await producer_music_clip_service.get_session_status()
        return {"success": True, "status": status, "timestamp": time.time()}
    except Exception as e:
        logger.error(f"Failed to get test status: {e}")
        return {"success": False, "error": str(e), "timestamp": time.time()}


@router.post("/test-generate")
async def test_generate(request: GenerateMusicRequest):
    """
    Test endpoint to test music generation without authentication
    """
    try:
        logger.info(f"Test music generation request: {request.prompt}")

        result = await producer_music_clip_service.generate_music_for_clip(
            prompt=request.prompt,
            title=request.title,
            is_instrumental=request.is_instrumental,
            lyrics=request.lyrics,
            project_id=request.project_id,
            user_id="test-user",
        )

        return result

    except Exception as e:
        logger.error(f"Test music generation error: {e}")
        return {"success": False, "error": str(e), "timestamp": time.time()}


@router.get("/simple-test")
async def simple_test():
    """
    Simple test endpoint to check if the route is working
    """
    return {"success": True, "message": "Simple test endpoint working", "timestamp": time.time()}


@router.post("/direct-test")
async def direct_test(request: GenerateMusicRequest):
    """
    Direct test endpoint that bypasses the service completely
    """
    try:
        logger.info(f"Direct test request: {request.prompt}")

        # Return a simple response without using any services
        return {
            "success": True,
            "generation_id": f"direct_{int(time.time())}",
            "title": request.title,
            "prompt": request.prompt,
            "method": "direct_test",
            "timestamp": time.time(),
            "message": "Direct test completed successfully",
        }

    except Exception as e:
        logger.error(f"Direct test error: {e}")
        return {"success": False, "error": str(e), "timestamp": time.time()}


@router.post("/raw-test")
async def raw_test():
    """
    Raw test endpoint that doesn't use any models or services
    """
    try:
        logger.info("Raw test request received")

        # Return a simple response immediately
        return {"success": True, "message": "Raw test completed successfully", "timestamp": time.time()}

    except Exception as e:
        logger.error(f"Raw test error: {e}")
        return {"success": False, "error": str(e), "timestamp": time.time()}


@router.post("/minimal-test")
async def minimal_test():
    """
    Minimal test endpoint with no logic
    """
    return {"success": True, "message": "Minimal test", "timestamp": time.time()}


@router.get("/browser-test")
async def browser_test():
    """
    Test browser automation by navigating to Google
    """
    try:
        from api.services.ai.producer_session_manager import session_manager

        logger.info("🌐 Testing browser automation...")

        # Check if session manager is initialized
        if not session_manager.is_authenticated:
            logger.info("🔄 Session manager not initialized, initializing...")
            await session_manager.initialize()

        # Get the first available window
        if not session_manager.windows:
            logger.error("❌ No windows available")
            return {"success": False, "error": "No browser windows available", "timestamp": time.time()}

        # Get the first window
        window_id = list(session_manager.windows.keys())[0]
        window_info = session_manager.windows[window_id]
        page = window_info.page

        # Navigate to Google
        logger.info(f"🌐 Navigating to Google using window {window_id}...")
        await page.goto("https://www.google.com", timeout=30000)
        await page.wait_for_load_state("domcontentloaded", timeout=30000)

        # Check if we can find the search box
        try:
            search_box = await page.wait_for_selector('input[name="q"]', timeout=10000)
            if search_box:
                logger.info("✅ Found Google search box - browser automation working!")
                return {
                    "success": True,
                    "message": "Browser automation working - found Google search box",
                    "window_id": window_id,
                    "current_url": page.url,
                    "timestamp": time.time(),
                }
        except:
            pass

        # If we can't find the search box, at least we navigated to Google
        logger.info("✅ Successfully navigated to Google")
        return {
            "success": True,
            "message": "Browser automation working - navigated to Google",
            "window_id": window_id,
            "current_url": page.url,
            "timestamp": time.time(),
        }

    except Exception as e:
        logger.error(f"❌ Browser test failed: {e}")
        return {"success": False, "error": str(e), "timestamp": time.time()}


@router.get("/producer-test")
async def producer_test():
    """
    Test ProducerAI navigation specifically
    """
    try:
        from api.services.ai.producer_session_manager import session_manager

        logger.info("🎵 Testing ProducerAI navigation...")

        # Check if session manager is initialized
        if not session_manager.is_authenticated:
            logger.info("🔄 Session manager not initialized, initializing...")
            await session_manager.initialize()

        # Get the first available window
        if not session_manager.windows:
            logger.error("❌ No windows available")
            return {"success": False, "error": "No browser windows available", "timestamp": time.time()}

        # Get the first window
        window_id = list(session_manager.windows.keys())[0]
        window_info = session_manager.windows[window_id]
        page = window_info.page

        # Navigate to ProducerAI create page
        logger.info(f"🎵 Navigating to ProducerAI create page using window {window_id}...")
        await page.goto("https://www.producer.ai/create", timeout=30000)
        await page.wait_for_load_state("domcontentloaded", timeout=30000)
        await asyncio.sleep(3)  # Wait for page to load

        # Check current URL
        current_url = page.url
        logger.info(f"🔍 Current URL: {current_url}")

        # Look for the prompt textarea
        try:
            prompt_textarea = await page.wait_for_selector('textarea[placeholder*="Ask Producer"]', timeout=10000)
            if prompt_textarea:
                is_visible = await prompt_textarea.is_visible()
                is_enabled = await prompt_textarea.is_enabled()
                placeholder = await prompt_textarea.evaluate("el => el.placeholder || ''")

                logger.info(
                    f"✅ Found ProducerAI prompt textarea: visible={is_visible}, enabled={is_enabled}, placeholder='{placeholder}'"
                )

                return {
                    "success": True,
                    "message": "ProducerAI navigation working - found prompt textarea",
                    "window_id": window_id,
                    "current_url": current_url,
                    "textarea_found": True,
                    "textarea_visible": is_visible,
                    "textarea_enabled": is_enabled,
                    "placeholder": placeholder,
                    "timestamp": time.time(),
                }
        except Exception as e:
            logger.warning(f"⚠️ Could not find prompt textarea: {e}")

        # If we can't find the textarea, check what elements are available
        try:
            all_textareas = await page.query_selector_all("textarea")
            all_inputs = await page.query_selector_all("input")

            textarea_info = []
            for i, textarea in enumerate(all_textareas):
                try:
                    placeholder = await textarea.evaluate("el => el.placeholder || ''")
                    visible = await textarea.is_visible()
                    enabled = await textarea.is_enabled()
                    textarea_info.append(
                        {"index": i, "placeholder": placeholder, "visible": visible, "enabled": enabled}
                    )
                except:
                    pass

            return {
                "success": False,
                "message": "ProducerAI navigation working but prompt textarea not found",
                "window_id": window_id,
                "current_url": current_url,
                "textarea_count": len(all_textareas),
                "input_count": len(all_inputs),
                "textarea_info": textarea_info,
                "timestamp": time.time(),
            }

        except Exception as e:
            logger.error(f"❌ Error checking elements: {e}")
            return {
                "success": False,
                "error": f"Error checking elements: {str(e)}",
                "window_id": window_id,
                "current_url": current_url,
                "timestamp": time.time(),
            }

    except Exception as e:
        logger.error(f"❌ ProducerAI test failed: {e}")
        return {"success": False, "error": str(e), "timestamp": time.time()}
