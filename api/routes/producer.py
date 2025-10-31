"""
ProducerAI API Routes
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse

from api.services.ai.producer.unified_service import unified_producer_service as producer_service
from api.services.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ai/producer", tags=["producer"])


@router.post("/generate")
async def generate_music(
    prompt: str,
    title: Optional[str] = None,
    download_path: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
):
    """
    Generate music using ProducerAI web automation

    Args:
        prompt: Music generation prompt
        title: Optional title for the song
        download_path: Optional custom download path

    Returns:
        Generation result with file information
    """
    try:
        logger.info(f"ProducerAI generation request from user {current_user.get('email', 'unknown')}: {prompt}")

        result = await producer_service.generate_music(prompt=prompt, title=title, download_path=download_path)

        if result["success"]:
            logger.info(f"ProducerAI generation successful: {result.get('song_id')}")
            return result
        else:
            logger.error(f"ProducerAI generation failed: {result.get('error')}")
            raise HTTPException(status_code=500, detail=result.get("error", "Generation failed"))

    except Exception as e:
        logger.error(f"ProducerAI generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/files")
async def list_files(download_path: Optional[str] = None, current_user: dict = Depends(get_current_user)):
    """
    List available generated music files

    Args:
        download_path: Optional custom download path

    Returns:
        List of available files
    """
    try:
        files = await producer_service.get_available_files(download_path=download_path)
        return {"success": True, "files": files, "count": len(files)}

    except Exception as e:
        logger.error(f"Failed to list files: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/files/{filename}")
async def download_file(
    filename: str, download_path: Optional[str] = None, current_user: dict = Depends(get_current_user)
):
    """
    Download a generated music file

    Args:
        filename: Name of the file to download
        download_path: Optional custom download path

    Returns:
        File response
    """
    try:
        file_path = await producer_service.serve_file(filename, download_path=download_path)

        if not file_path:
            raise HTTPException(status_code=404, detail="File not found")

        return FileResponse(path=file_path, filename=filename, media_type="audio/mpeg")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to serve file {filename}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_status(current_user: dict = Depends(get_current_user)):
    """
    Get ProducerAI service status

    Returns:
        Service status information
    """
    try:
        files = await producer_service.get_available_files()

        return {
            "success": True,
            "service": "ProducerAI",
            "method": "web_automation",
            "email": producer_service.email,
            "download_path": producer_service.download_path,
            "available_files": len(files),
            "status": "operational",
        }

    except Exception as e:
        logger.error(f"Failed to get status: {e}")
        return {"success": False, "service": "ProducerAI", "status": "error", "error": str(e)}
