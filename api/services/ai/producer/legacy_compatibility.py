"""
Legacy Compatibility Layer
Maintains backward compatibility with existing code while using the unified service
"""

import logging
from typing import Any, Dict, List, Optional

from .unified_service import unified_producer_service

logger = logging.getLogger(__name__)


class ProducerAIService:
    """Legacy compatibility wrapper for ProducerAIService"""
    
    def __init__(self):
        self.service = unified_producer_service
        logger.info("ProducerAIService initialized with unified backend")

    async def generate_music(
        self, prompt: str, title: Optional[str] = None, download_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Legacy generate_music method"""
        result = await self.service.generate_music(
            prompt=prompt,
            title=title,
            use_queue=False  # Use direct generation for legacy compatibility
        )
        
        # Transform result to match legacy format
        if result.get("success"):
            return {
                "success": True,
                "song_id": result.get("song_id"),
                "title": result.get("title"),
                "prompt": prompt,
                "method": "producer_ai_automation",
                "timestamp": result.get("timestamp"),
                "download_path": result.get("uploaded_files", [{}])[0].get("s3_url") if result.get("uploaded_files") else None,
                "downloaded_files": [f.get("filename") for f in result.get("uploaded_files", [])],
                "generation_completed": result.get("generation_completed", False),
                "download_success": result.get("download_success", False),
                "network_urls": [f.get("s3_url") for f in result.get("uploaded_files", [])],
            }
        else:
            return {
                "success": False,
                "error": result.get("error"),
                "method": "producer_ai_automation",
                "timestamp": result.get("timestamp"),
                "prompt": prompt,
            }

    async def get_available_files(self, download_path: Optional[str] = None) -> List[Dict[str, Any]]:
        """Legacy get_available_files method"""
        return await self.service.get_available_files(download_path)

    async def serve_file(self, filename: str, download_path: Optional[str] = None) -> Optional[str]:
        """Legacy serve_file method"""
        return await self.service.serve_file(filename, download_path)


class ProducerAIMusicClipService:
    """Legacy compatibility wrapper for ProducerAIMusicClipService"""
    
    def __init__(self):
        self.service = unified_producer_service
        logger.info("ProducerAIMusicClipService initialized with unified backend")

    async def generate_music_for_clip(
        self,
        prompt: str,
        title: Optional[str] = None,
        is_instrumental: bool = False,
        lyrics: Optional[str] = None,
        project_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Legacy generate_music_for_clip method"""
        return await self.service.generate_music(
            prompt=prompt,
            title=title,
            is_instrumental=is_instrumental,
            lyrics=lyrics,
            project_id=project_id,
            user_id=user_id,
            use_queue=True  # Use queue system for music clip workflow
        )

    async def get_session_status(self) -> Dict[str, Any]:
        """Legacy get_session_status method"""
        return await self.service.get_session_status()

    async def get_request_status(self, request_id: str) -> Dict[str, Any]:
        """Legacy get_request_status method"""
        return await self.service.get_request_status(request_id)

    async def cleanup_local_files(self, generation_id: str) -> bool:
        """Legacy cleanup_local_files method - now handled automatically"""
        logger.info(f"Cleanup requested for {generation_id} - handled automatically by unified service")
        return True


# Global service instances for backward compatibility
producer_service = ProducerAIService()
producer_music_clip_service = ProducerAIMusicClipService()
