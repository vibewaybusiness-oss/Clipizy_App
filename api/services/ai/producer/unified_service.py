"""
Unified ProducerAI Service
Consolidates music generation functionality from multiple services
"""

import asyncio
import logging
import os
import time
from typing import Any, Dict, List, Optional

from .shared_config import config
from .shared_utils import (
    upload_to_s3, extract_file_metadata, find_recent_audio_files,
    create_success_response, create_error_response, safe_operation,
    generate_id, cleanup_local_file, wait_for_condition,
    ProducerAIError, S3UploadError, GenerationError
)
from .producer_session_manager import session_manager, MusicGenerationRequest, RequestStatus

logger = logging.getLogger(__name__)


class UnifiedProducerAIService:
    """Unified service for ProducerAI music generation with persistent sessions"""

    def __init__(self):
        self.download_path = config.download_path
        self._initialization_task = None
        
        logger.info(f"Unified ProducerAI service initialized with download path: {self.download_path}")

    async def _ensure_session_initialized(self):
        """Ensure the session manager is initialized"""
        logger.info("🔍 Checking session manager status...")
        
        if not session_manager.is_authenticated:
            logger.warning("Session manager not authenticated, attempting initialization...")
            try:
                if self._initialization_task is None:
                    self._initialization_task = asyncio.create_task(session_manager.initialize())

                await asyncio.wait_for(self._initialization_task, timeout=30.0)
                self._initialization_task = None
                logger.info("Session manager initialized successfully")
            except asyncio.TimeoutError:
                logger.error("Session manager initialization timed out")
                raise GenerationError("Session manager initialization timeout")
            except Exception as e:
                logger.error(f"Session manager initialization failed: {e}")
                raise GenerationError(f"Session manager initialization failed: {e}")
        else:
            logger.info("✅ Session manager already authenticated")

    async def generate_music(
        self,
        prompt: str,
        title: Optional[str] = None,
        is_instrumental: bool = False,
        lyrics: Optional[str] = None,
        project_id: Optional[str] = None,
        user_id: Optional[str] = None,
        use_queue: bool = True
    ) -> Dict[str, Any]:
        """
        Generate music using ProducerAI with optional queue system
        
        Args:
            prompt: Music generation prompt
            title: Optional title for the song
            is_instrumental: Whether to generate instrumental music
            lyrics: Optional lyrics for the song
            project_id: Project ID for organizing files
            user_id: User ID for organizing files
            use_queue: Whether to use queue system (default: True)
            
        Returns:
            Dict containing generation results with S3 URLs
        """
        generation_id = generate_id("clip")
        
        try:
            # Ensure session manager is properly initialized
            await self._ensure_session_initialized()

            # Prepare the prompt for ProducerAI
            full_prompt = prompt
            if lyrics and not is_instrumental:
                full_prompt = f"{prompt}\n\nLyrics:\n{lyrics}"

            logger.info(f"Starting ProducerAI music generation with prompt: {full_prompt}")

            if use_queue:
                return await self._generate_with_queue(
                    generation_id, full_prompt, title, is_instrumental, 
                    lyrics, project_id, user_id
                )
            else:
                return await self._generate_direct(
                    generation_id, full_prompt, title, is_instrumental,
                    lyrics, project_id, user_id
                )

        except Exception as e:
            logger.error(f"ProducerAI music generation failed: {e}")
            return create_error_response(
                str(e), 
                error_type="GenerationError",
                method="producer_ai_unified",
                prompt=prompt
            )

    async def _generate_with_queue(
        self,
        generation_id: str,
        prompt: str,
        title: Optional[str],
        is_instrumental: bool,
        lyrics: Optional[str],
        project_id: Optional[str],
        user_id: Optional[str]
    ) -> Dict[str, Any]:
        """Generate music using queue system"""
        try:
            # Create a music generation request for the queue
            request = MusicGenerationRequest(
                request_id=generation_id,
                prompt=prompt,
                title=title or f"Music Track {generation_id}",
                is_instrumental=is_instrumental,
                lyrics=lyrics,
                project_id=project_id,
                user_id=user_id,
                status=RequestStatus.PENDING,
            )

            # Add to queue and get immediate status
            queue_result = await session_manager.generate_music(request)
            
            if not queue_result.get("success"):
                return create_error_response(
                    queue_result.get("error", "Failed to queue generation request"),
                    error_type="QueueError",
                    method="producer_ai_queue"
                )

            # Wait for generation to complete
            result = await self._wait_for_queue_completion(generation_id)
            
            if not result.get("success"):
                return result

            # Process uploaded files
            uploaded_files = await self._process_generation_files(
                result, generation_id, project_id, user_id, prompt, title, is_instrumental, lyrics
            )

            return create_success_response(
                "Music generation completed successfully",
                song_id=result.get("song_id"),
                title=result.get("title"),
                prompt=prompt,
                method="producer_ai_queue",
                is_instrumental=is_instrumental,
                lyrics=lyrics,
                project_id=project_id,
                generation_id=generation_id,
                request_id=result.get("request_id", generation_id),
                uploaded_files=uploaded_files,
                generation_completed=result.get("generation_completed", False),
                download_success=result.get("download_success", False),
                tab_id=result.get("tab_id")
            )

        except Exception as e:
            logger.error(f"Queue-based generation failed: {e}")
            return create_error_response(
                str(e),
                error_type="QueueGenerationError",
                method="producer_ai_queue"
            )

    async def _generate_direct(
        self,
        generation_id: str,
        prompt: str,
        title: Optional[str],
        is_instrumental: bool,
        lyrics: Optional[str],
        project_id: Optional[str],
        user_id: Optional[str]
    ) -> Dict[str, Any]:
        """Generate music using direct session manager"""
        try:
            result = await session_manager.generate_music_direct(
                prompt=prompt,
                title=title or f"Track {generation_id}",
                is_instrumental=is_instrumental,
                lyrics=lyrics,
                project_id=project_id,
                user_id=user_id
            )

            if not result.get("success"):
                return create_error_response(
                    result.get("error", "Direct generation failed"),
                    error_type="DirectGenerationError",
                    method="producer_ai_direct"
                )

            # Process uploaded files
            uploaded_files = await self._process_generation_files(
                result, generation_id, project_id, user_id, prompt, title, is_instrumental, lyrics
            )

            return create_success_response(
                "Music generation completed successfully",
                song_id=result.get("song_id"),
                title=result.get("title"),
                prompt=prompt,
                method="producer_ai_direct",
                is_instrumental=is_instrumental,
                lyrics=lyrics,
                project_id=project_id,
                generation_id=generation_id,
                uploaded_files=uploaded_files,
                generation_completed=result.get("generation_completed", False),
                download_success=result.get("download_success", False)
            )

        except Exception as e:
            logger.error(f"Direct generation failed: {e}")
            return create_error_response(
                str(e),
                error_type="DirectGenerationError",
                method="producer_ai_direct"
            )

    async def _wait_for_queue_completion(self, generation_id: str, max_wait_time: int = 300) -> Dict[str, Any]:
        """Wait for queue-based generation to complete"""
        start_time = time.time()

        while time.time() - start_time < max_wait_time:
            status_result = await session_manager.queue_manager.get_request_status(generation_id)

            if not status_result:
                return create_error_response(
                    f"Request {generation_id} not found in queue",
                    error_type="QueueError"
                )

            current_status = status_result.get("status")

            if current_status == "completed":
                result = status_result.get("result")
                if result and result.get("success"):
                    return result
                else:
                    return create_error_response(
                        result.get("error", "Generation failed") if result else "Unknown error",
                        error_type="GenerationError"
                    )
            elif current_status == "failed":
                return create_error_response(
                    status_result.get("error", "Generation failed"),
                    error_type="GenerationError"
                )
            elif current_status == "cancelled":
                return create_error_response(
                    "Generation was cancelled",
                    error_type="CancellationError"
                )
            else:
                await asyncio.sleep(5)  # Check every 5 seconds

        return create_error_response(
            "Generation timeout",
            error_type="TimeoutError"
        )

    async def _process_generation_files(
        self,
        result: Dict[str, Any],
        generation_id: str,
        project_id: Optional[str],
        user_id: Optional[str],
        prompt: str,
        title: Optional[str],
        is_instrumental: bool,
        lyrics: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Process generated files and upload to S3"""
        uploaded_files = []

        # Check if session manager already uploaded files to S3
        if result.get("uploaded_files"):
            logger.info(f"Session manager already uploaded {len(result['uploaded_files'])} files to S3")
            
            for uploaded_file in result["uploaded_files"]:
                track_record = await self._create_track_record(
                    file_path=None,
                    s3_url=uploaded_file.get("s3_url"),
                    project_id=project_id,
                    prompt=prompt,
                    title=title,
                    is_instrumental=is_instrumental,
                    lyrics=lyrics,
                    user_id=user_id,
                    file_metadata=uploaded_file.get("file_metadata")
                )

                uploaded_files.append({
                    "local_path": None,
                    "s3_url": uploaded_file.get("s3_url"),
                    "filename": uploaded_file.get("filename"),
                    "size": uploaded_file.get("file_size", 0),
                    "track_record": track_record,
                })

        # Check for local files if session manager didn't upload them
        if not uploaded_files:
            uploaded_files = await self._process_local_files(
                generation_id, project_id, user_id, prompt, title, is_instrumental, lyrics
            )

        return uploaded_files

    async def _process_local_files(
        self,
        generation_id: str,
        project_id: Optional[str],
        user_id: Optional[str],
        prompt: str,
        title: Optional[str],
        is_instrumental: bool,
        lyrics: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Process local files and upload to S3"""
        uploaded_files = []

        # Check generation-specific directory
        generation_path = os.path.join(self.download_path, generation_id)
        if os.path.exists(generation_path):
            for filename in os.listdir(generation_path):
                if filename.lower().endswith((".wav", ".mp3", ".m4a", ".ogg", ".flac")):
                    file_path = os.path.join(generation_path, filename)
                    if os.path.exists(file_path):
                        upload_result = await self._upload_and_create_record(
                            file_path, project_id, generation_id, user_id,
                            prompt, title, is_instrumental, lyrics
                        )
                        if upload_result:
                            uploaded_files.append(upload_result)

        # Check for recent files in main directory
        if not uploaded_files:
            recent_files = find_recent_audio_files(self.download_path)
            for file_path in recent_files:
                if os.path.exists(file_path):
                    upload_result = await self._upload_and_create_record(
                        file_path, project_id, generation_id, user_id,
                        prompt, title, is_instrumental, lyrics
                    )
                    if upload_result:
                        uploaded_files.append(upload_result)

        return uploaded_files

    async def _upload_and_create_record(
        self,
        file_path: str,
        project_id: Optional[str],
        generation_id: str,
        user_id: Optional[str],
        prompt: str,
        title: Optional[str],
        is_instrumental: bool,
        lyrics: Optional[str]
    ) -> Optional[Dict[str, Any]]:
        """Upload file to S3 and create track record"""
        try:
            upload_result = await upload_to_s3(
                file_path, user_id, project_id, generation_id, "music_clip"
            )
            
            if upload_result.get("success"):
                track_record = await self._create_track_record(
                    file_path=file_path,
                    s3_url=upload_result.get("s3_url"),
                    project_id=project_id,
                    prompt=prompt,
                    title=title,
                    is_instrumental=is_instrumental,
                    lyrics=lyrics,
                    user_id=user_id,
                    file_metadata=upload_result.get("file_metadata")
                )

                # Clean up local file after successful upload
                cleanup_local_file(file_path)

                return {
                    "local_path": file_path,
                    "s3_url": upload_result.get("s3_url"),
                    "filename": upload_result.get("filename"),
                    "size": upload_result.get("file_size", 0),
                    "track_record": track_record,
                }
        except Exception as e:
            logger.error(f"Failed to upload and create record for {file_path}: {e}")
        
        return None

    async def _create_track_record(
        self,
        file_path: Optional[str],
        s3_url: str,
        project_id: str,
        prompt: str,
        title: str,
        is_instrumental: bool,
        lyrics: Optional[str],
        user_id: Optional[str] = None,
        file_metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """Create a track record in the database"""
        try:
            from api.services.database import get_db
            from api.services import project_service

            # Get database session
            db = next(get_db())

            # Use provided metadata or extract from file
            if not file_metadata and file_path and os.path.exists(file_path):
                file_metadata = await extract_file_metadata(file_path)

            # Get user_id from project if not provided
            if not user_id:
                from api.models import Project
                project = db.query(Project).filter(Project.id == project_id).first()
                if project:
                    user_id = str(project.user_id)
                else:
                    logger.error(f"Project {project_id} not found, cannot create track record")
                    return None

            # Create track record using project service
            track_record = project_service.add_music_track(
                db=db,
                project_id=project_id,
                user_id=user_id,
                file_path=s3_url,
                file_metadata=file_metadata or {"duration": 0, "format": "wav", "size_mb": 0},
                ai_generated=True,
                prompt=prompt,
                genre=None,
                instrumental=is_instrumental,
                video_description=lyrics,
            )

            logger.info(f"Created track record in database: {track_record.id}")
            return track_record

        except Exception as e:
            logger.error(f"Failed to create track record: {e}")
            return None

    async def get_available_files(self, download_path: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get list of available generated music files"""
        try:
            final_download_path = download_path or self.download_path

            if not os.path.exists(final_download_path):
                return []

            files = []
            for filename in os.listdir(final_download_path):
                if filename.lower().endswith((".wav", ".mp3", ".m4a", ".ogg", ".flac")):
                    file_path = os.path.join(final_download_path, filename)
                    file_stat = os.stat(file_path)

                    files.append({
                        "filename": filename,
                        "path": file_path,
                        "size": file_stat.st_size,
                        "created": file_stat.st_ctime,
                        "modified": file_stat.st_mtime,
                        "url": f"/api/ai/producer/files/{filename}",
                    })

            # Sort by creation time (newest first)
            files.sort(key=lambda x: x["created"], reverse=True)
            return files

        except Exception as e:
            logger.error(f"Failed to get available files: {e}")
            return []

    async def serve_file(self, filename: str, download_path: Optional[str] = None) -> Optional[str]:
        """Get file path for serving a generated music file"""
        try:
            final_download_path = download_path or self.download_path
            file_path = os.path.join(final_download_path, filename)

            if os.path.exists(file_path) and os.path.isfile(file_path):
                return file_path

            return None

        except Exception as e:
            logger.error(f"Failed to serve file {filename}: {e}")
            return None

    async def get_session_status(self) -> Dict[str, Any]:
        """Get the current status of the session manager"""
        try:
            await self._ensure_session_initialized()
            return await session_manager.get_status()
        except Exception as e:
            logger.error(f"Failed to get session status: {e}")
            return {"error": str(e), "is_authenticated": False}

    async def get_request_status(self, request_id: str) -> Dict[str, Any]:
        """Get the status of a specific music generation request"""
        try:
            await self._ensure_session_initialized()
            status = await session_manager.queue_manager.get_request_status(request_id)
            if status:
                return {"success": True, "status": status}
            else:
                return {"success": False, "error": "Request not found"}
        except Exception as e:
            logger.error(f"Failed to get request status: {e}")
            return {"success": False, "error": str(e)}


# Global service instance
unified_producer_service = UnifiedProducerAIService()
