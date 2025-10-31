"""
Backend-Only Storage Service
Uses PostgreSQL for all project data and S3 only for file storage
No JSON files or localStorage dependencies
"""

import asyncio
import os
import tempfile
import uuid
from datetime import datetime
from io import BytesIO
from typing import Any, Dict, List, Optional, Union

import boto3
from botocore.client import Config
from fastapi import HTTPException, UploadFile
from PIL import Image
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

try:
    import mutagen
    MUTAGEN_AVAILABLE = True
except ImportError:
    MUTAGEN_AVAILABLE = False

from api.config.logging import get_storage_logger
from api.config.settings import settings
from api.models import Project, Track, Image as ImageModel, Video, Audio, User

logger = get_storage_logger()

# File type to subfolder mapping with automatic metadata extraction
FILE_TYPE_MAPPING = {
    'image': {
        'subfolder': 'images',
        'allowed_types': ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/bmp', 'image/tiff'],
        'max_size': 20 * 1024 * 1024,  # 20MB
        'metadata_extractor': 'extract_image_metadata'
    },
    'video': {
        'subfolder': 'videos',
        'allowed_types': ['video/mp4', 'video/avi', 'video/mov', 'video/webm', 'video/mkv', 'video/flv'],
        'max_size': 500 * 1024 * 1024,  # 500MB
        'metadata_extractor': 'extract_video_metadata'
    },
    'track': {
        'subfolder': 'tracks',
        'allowed_types': ['audio/mpeg', 'audio/wav', 'audio/mp3', 'audio/ogg', 'audio/flac', 'audio/aac'],
        'max_size': 50 * 1024 * 1024,  # 50MB
        'metadata_extractor': 'extract_audio_metadata'
    },
    'voiceover': {
        'subfolder': 'voiceovers',
        'allowed_types': ['audio/mpeg', 'audio/wav', 'audio/mp3', 'audio/ogg', 'audio/flac', 'audio/aac'],
        'max_size': 50 * 1024 * 1024,  # 50MB
        'metadata_extractor': 'extract_audio_metadata'
    }
}

# Project type configurations
PROJECT_CONFIGS = {
    'music-clip': {
        'storage_prefix': 'music-clip',
        'allowed_file_types': ['audio/mpeg', 'audio/wav', 'audio/mp3', 'audio/ogg', 'audio/flac', 'audio/aac', 'image/jpeg', 'image/png', 'image/gif', 'image/webp', 'video/mp4', 'video/avi', 'video/mov', 'video/webm'],
        'max_file_size': 50 * 1024 * 1024,  # 50MB
        'supported_operations': ['upload', 'generate', 'analyze', 'export']
    },
    'video-edit': {
        'storage_prefix': 'video-edit',
        'allowed_file_types': ['video/mp4', 'video/avi', 'video/mov', 'video/webm', 'video/mkv', 'video/flv', 'audio/mpeg', 'audio/wav', 'audio/mp3', 'audio/ogg', 'image/jpeg', 'image/png', 'image/gif', 'image/webp'],
        'max_file_size': 500 * 1024 * 1024,  # 500MB
        'supported_operations': ['upload', 'edit', 'render', 'export']
    },
    'audio-edit': {
        'storage_prefix': 'audio-edit',
        'allowed_file_types': ['audio/mpeg', 'audio/wav', 'audio/mp3', 'audio/ogg', 'audio/flac', 'audio/aac'],
        'max_file_size': 100 * 1024 * 1024,  # 100MB
        'supported_operations': ['upload', 'edit', 'mix', 'export']
    },
    'image-edit': {
        'storage_prefix': 'image-edit',
        'allowed_file_types': ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/bmp', 'image/tiff'],
        'max_file_size': 20 * 1024 * 1024,  # 20MB
        'supported_operations': ['upload', 'edit', 'filter', 'export']
    },
    'custom': {
        'storage_prefix': 'custom',
        'allowed_file_types': ['*/*'],  # Allow all types
        'max_file_size': 100 * 1024 * 1024,  # 100MB
        'supported_operations': ['upload', 'process', 'export']
    }
}


class BackendStorageService:
    """
    Backend-only storage service using PostgreSQL for data and S3 for files
    No JSON files or localStorage dependencies
    """
    
    def __init__(self):
        self.s3_client = None
        self.bucket_name = settings.s3_bucket
        self._initialize_s3()
        logger.info("BackendStorageService initialized with PostgreSQL + S3 architecture")
    
    def _initialize_s3(self):
        """Initialize S3 client with proper configuration"""
        try:
            config = Config(
                region_name=settings.s3_region,
                signature_version='s3v4',
                retries={'max_attempts': 3, 'mode': 'adaptive'},
                read_timeout=300,  # 5 minutes
                connect_timeout=60  # 1 minute
            )
            
            # Fix endpoint URL - let boto3 handle AWS endpoints automatically
            endpoint_url = settings.s3_endpoint_url
            if endpoint_url in ["https://s3.amazonaws.com", "http://s3.amazonaws.com"]:
                endpoint_url = None  # Let boto3 use region-specific endpoint
            
            self.s3_client = boto3.client(
                's3',
                endpoint_url=endpoint_url,
                aws_access_key_id=settings.s3_access_key,
                aws_secret_access_key=settings.s3_secret_key,
                config=config
            )
            
            # Test connection
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            logger.info(f"S3 client initialized successfully with bucket: {self.bucket_name}")
            
        except Exception as e:
            logger.warning(f"S3 client initialization failed: {e}")
            logger.warning("Continuing without S3 - file operations will be limited")
            self.s3_client = None
    
    # ============================================================================
    # PROJECT DATA MANAGEMENT (PostgreSQL-based)
    # ============================================================================
    
    async def save_project_data(self, db: Session, user_id: str, project_id: str, project_type: str, data: Dict[str, Any]) -> str:
        """Save project data to PostgreSQL database"""
        try:
            logger.info(f"Saving project data to PostgreSQL for project {project_id}")
            
            # Get or create project
            project = db.query(Project).filter(
                and_(
                    Project.id == project_id,
                    Project.user_id == user_id,
                    Project.type == project_type
                )
            ).first()
            
            if not project:
                raise HTTPException(status_code=404, detail="Project not found")
            
            # Update project data fields (only fields that exist in Project model)
            logger.info(f"Data keys received: {list(data.keys())}")
            logger.info(f"Settings in data: {'settings' in data}")
            logger.info(f"Analysis in data: {'analysis' in data}")
            
            if 'settings' in data:
                logger.info(f"Updating settings: {type(data['settings'])}")
                settings_data = data['settings']
                if isinstance(settings_data, dict):
                    logger.info(f"Settings keys: {list(settings_data.keys())}")
                    if 'tracks' in settings_data:
                        logger.info(f"✅ Tracks found in settings! Count: {len(settings_data['tracks']) if isinstance(settings_data['tracks'], list) else 'not a list'}")
                        if isinstance(settings_data['tracks'], list) and len(settings_data['tracks']) > 0:
                            logger.info(f"First track data: {settings_data['tracks'][0]}")
                    else:
                        logger.warning("⚠️ No tracks field in settings data")
                project.settings = data['settings']
                logger.info("Settings updated successfully")
            if 'analysis' in data:
                logger.info(f"Updating analysis: {type(data['analysis'])}")
                project.analysis = data['analysis']
                logger.info("Analysis updated successfully")
            if 'name' in data:
                project.name = data['name']
            if 'description' in data:
                project.description = data['description']
            
            # Update timestamp
            project.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(project)
            
            logger.info(f"Project data saved to PostgreSQL successfully: {project_id}")
            return f"Project data saved to PostgreSQL for project {project_id}"
            
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to save project data to PostgreSQL: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to save project data: {str(e)}")
    
    async def load_project_data(self, db: Session, user_id: str, project_id: str, project_type: str) -> Dict[str, Any]:
        """Load project data from PostgreSQL database including tracks"""
        try:
            logger.info(f"Loading project data from PostgreSQL for project {project_id}")
            
            # Get project from database with tracks
            project = db.query(Project).filter(
                and_(
                    Project.id == project_id,
                    Project.user_id == user_id,
                    Project.type == project_type
                )
            ).first()
            
            if not project:
                logger.info(f"No project found in PostgreSQL: {project_id}")
                return {}
            
            # Load tracks for this project from Track table (for legacy/generated tracks)
            tracks = db.query(Track).filter(Track.project_id == project_id).all()
            logger.info(f"Found {len(tracks)} Track records (legacy) for project {project_id}")
            
            # Convert tracks to dictionary format
            tracks_data = []
            for track in tracks:
                # Generate presigned URL for the track
                track_url = None
                if track.file_path:
                    try:
                        track_url = self.get_presigned_url(track.file_path, expiration=3600)
                    except Exception as e:
                        logger.warning(f"Failed to generate URL for track {track.id}: {e}")
                        track_url = None
                
                track_data = {
                    'id': str(track.id),
                    'project_id': str(track.project_id),
                    'title': track.title,
                    'file_path': track.file_path,
                    'url': track_url,  # Include the presigned URL
                    'ai_generated': track.ai_generated,
                    'prompt': track.prompt,
                    'genre': track.genre,
                    'instrumental': track.instrumental,
                    'video_description': track.video_description,
                    'description': track.description,
                    'vibe': track.vibe,
                    'lyrics': track.lyrics,
                    'version': track.version,
                    'status': track.status,
                    'track_metadata': track.track_metadata,
                    'analysis': track.analysis,
                    'created_at': track.created_at.isoformat() if track.created_at else None
                }
                tracks_data.append(track_data)
            
            # Build data dictionary from project fields including tracks
            data = {
                'id': str(project.id),
                'name': project.name,
                'description': project.description,
                'type': project.type,
                'status': project.status.value,
                'settings': project.settings,
                'analysis': project.analysis,
                'tracks': tracks_data,  # Include tracks in project data (legacy Track records)
                'created_at': project.created_at.isoformat() if project.created_at else None,
                'updated_at': project.updated_at.isoformat() if project.updated_at else None
            }
            
            # Log what we're returning
            if isinstance(project.settings, dict):
                logger.info(f"📦 Settings being returned: {list(project.settings.keys())}")
                if 'tracks' in project.settings:
                    workflow_tracks = project.settings['tracks']
                    logger.info(f"🎵 Workflow tracks in settings: {len(workflow_tracks) if isinstance(workflow_tracks, list) else 'not a list'}")
                else:
                    logger.warning("⚠️ No 'tracks' field in project.settings when loading")
            
            logger.info(f"Project data loaded from PostgreSQL successfully: {project_id} with {len(tracks_data)} Track records")
            return data
            
        except Exception as e:
            logger.error(f"Failed to load project data from PostgreSQL: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to load project data: {str(e)}")
    
    async def delete_project_data(self, db: Session, user_id: str, project_id: str, project_type: str) -> str:
        """Delete project data from PostgreSQL database"""
        try:
            logger.info(f"Deleting project data from PostgreSQL for project {project_id}")
            
            # Get project
            project = db.query(Project).filter(
                and_(
                    Project.id == project_id,
                    Project.user_id == user_id,
                    Project.type == project_type
                )
            ).first()
            
            if not project:
                raise HTTPException(status_code=404, detail="Project not found")
            
            # Delete associated files from S3 first
            await self._delete_project_files_from_s3(user_id, project_id, project_type)
            
            # Delete project from database
            db.delete(project)
            db.commit()
            
            logger.info(f"Project data deleted from PostgreSQL successfully: {project_id}")
            return f"Project data deleted from PostgreSQL for project {project_id}"
            
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to delete project data from PostgreSQL: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to delete project data: {str(e)}")
    
    # ============================================================================
    # FILE MANAGEMENT (S3-based)
    # ============================================================================
    
    async def upload_project_file(
        self, 
        db: Session,
        user_id: str, 
        project_id: str, 
        project_type: str, 
        file: UploadFile, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Upload file to S3 and save metadata to PostgreSQL"""
        try:
            logger.info(f"Starting file upload: user_id={user_id}, project_id={project_id}, project_type={project_type}")
            
            # Validate filename
            if not file.filename:
                raise HTTPException(status_code=400, detail="Filename is required")
            
            # Sanitize filename
            sanitized_filename = self._sanitize_filename(file.filename)
            if not sanitized_filename:
                sanitized_filename = f"file_{uuid.uuid4().hex[:8]}"
            
            # Validate project type
            if project_type not in PROJECT_CONFIGS:
                raise HTTPException(status_code=400, detail=f"Unsupported project type: {project_type}")
            
            config = PROJECT_CONFIGS[project_type]
            
            # Validate file type and size
            if file.content_type not in config['allowed_file_types'] and '*' not in config['allowed_file_types']:
                raise HTTPException(
                    status_code=400, 
                    detail=f"File type {file.content_type} not allowed for project type {project_type}"
                )
            
            if file.size and file.size > config['max_file_size']:
                raise HTTPException(
                    status_code=400, 
                    detail=f"File size {file.size} exceeds maximum {config['max_file_size']} for project type {project_type}"
                )
            
            # Determine file type and subfolder
            file_type = self._determine_file_type(file.content_type)
            subfolder = FILE_TYPE_MAPPING.get(file_type, {}).get('subfolder', 'files')
            
            # Generate S3 key
            file_extension = os.path.splitext(sanitized_filename)[1] if sanitized_filename else ''
            if not file_extension:
                # Try to determine extension from content type
                content_type_to_ext = {
                    'image/jpeg': '.jpg',
                    'image/png': '.png',
                    'image/gif': '.gif',
                    'image/webp': '.webp',
                    'image/bmp': '.bmp',
                    'image/tiff': '.tiff',
                    'audio/mpeg': '.mp3',
                    'audio/wav': '.wav',
                    'audio/ogg': '.ogg',
                    'audio/flac': '.flac',
                    'audio/aac': '.aac',
                    'video/mp4': '.mp4',
                    'video/avi': '.avi',
                    'video/mov': '.mov',
                    'video/webm': '.webm'
                }
                file_extension = content_type_to_ext.get(file.content_type, '')
            
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            key = f"users/{user_id}/projects/{project_type}/{project_id}/{subfolder}/{unique_filename}"
            
            # Read file content once for both metadata extraction and S3 upload
            logger.info(f"Reading file content: filename={sanitized_filename}, content_type={file.content_type}")
            await file.seek(0)
            file_content = await file.read()
            file_size = len(file_content) if file_content else (file.size or 0)
            logger.info(f"File content read: size={file_size} bytes")
            
            # Extract metadata from file content
            logger.info("Extracting file metadata...")
            content_type = file.content_type or "application/octet-stream"
            extracted_metadata = self._extract_file_metadata_from_bytes(
                file_content, file_type, sanitized_filename, content_type, file_size
            )
            logger.info(f"Metadata extracted: {list(extracted_metadata.keys())}")
            
            # Upload to S3 (if available)
            if self.s3_client:
                logger.info(f"Uploading to S3: key={key}")
                file_stream = BytesIO(file_content)
                await self._upload_to_s3_from_bytes(file_stream, key, content_type)
                logger.info("S3 upload completed")
            else:
                logger.warning("S3 not available - file upload skipped")
            
            # Save file metadata to PostgreSQL
            logger.info("Creating file record in database...")
            file_record = self._create_file_record(
                db=db,
                user_id=user_id,
                project_id=project_id,
                file_type=file_type,
                filename=sanitized_filename,
                s3_key=key,
                content_type=content_type,
                file_size=file_size,
                extracted_metadata=extracted_metadata,
                custom_metadata=metadata
            )
            
            db.commit()
            db.refresh(file_record)
            
            logger.info(f"File uploaded successfully: {key}")
            
            # Generate presigned URL only if S3 is available
            presigned_url = None
            if self.s3_client:
                try:
                    presigned_url = self.get_presigned_url(key)
                except Exception as e:
                    logger.warning(f"Failed to generate presigned URL: {e}")
                    presigned_url = None
            
            return {
                'id': str(file_record.id),
                'filename': sanitized_filename,
                'key': key,
                'file_type': file_type,
                'file_type_directory': subfolder,
                'content_type': content_type,
                'file_size': file_size,
                'metadata': extracted_metadata,
                'uploaded_at': file_record.created_at.isoformat(),
                'presigned_url': presigned_url
            }
            
        except HTTPException:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            import traceback
            error_trace = traceback.format_exc()
            logger.error(f"Failed to upload file: {str(e)}")
            logger.error(f"Error traceback: {error_trace}")
            raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")
    
    async def delete_project_file(self, db: Session, user_id: str, project_id: str, file_id: str) -> str:
        """Delete file from S3 and PostgreSQL"""
        try:
            # Get file record
            file_record = db.query(Track).filter(
                and_(
                    Track.id == file_id,
                    Track.project_id == project_id
                )
            ).first()
            
            if not file_record:
                raise HTTPException(status_code=404, detail="File not found")
            
            # Delete from S3 (if available)
            if self.s3_client:
                self.s3_client.delete_object(Bucket=self.bucket_name, Key=file_record.file_path)
            
            # Delete from database
            db.delete(file_record)
            db.commit()
            
            logger.info(f"File deleted successfully: {file_record.file_path}")
            return f"File {file_id} deleted successfully"
            
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to delete file: {e}")
            raise HTTPException(status_code=500, detail=f"File deletion failed: {str(e)}")
    
    def get_file_content(self, key: str) -> bytes:
        """Download file content from S3"""
        if not self.s3_client:
            raise HTTPException(status_code=503, detail="S3 storage not available")
        
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
            return response['Body'].read()
        except Exception as e:
            logger.error(f"Failed to download file content: {e}")
            raise HTTPException(status_code=500, detail="Failed to download file content")
    
    def get_presigned_url(self, key: str, expiration: int = 3600) -> str:
        """Generate presigned URL for file access"""
        if not self.s3_client:
            raise HTTPException(status_code=503, detail="S3 storage not available")
        
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': key},
                ExpiresIn=expiration
            )
            return url
        except Exception as e:
            logger.error(f"Failed to generate presigned URL: {e}")
            raise HTTPException(status_code=500, detail="Failed to generate file access URL")
    
    def get_short_lived_image_url(self, s3_key: str, expiration_seconds: int = 300) -> str:
        """
        GENERATE SHORT-LIVED PRESIGNED URL FOR IMAGE ACCESS
        Default expiration: 5 minutes (300 seconds)
        Used for passing images to external services like LLM APIs
        """
        if not self.s3_client:
            raise HTTPException(status_code=503, detail="S3 storage not available")
        
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': s3_key},
                ExpiresIn=expiration_seconds
            )
            logger.debug(f"Generated short-lived image URL (expires in {expiration_seconds}s): {s3_key}")
            return url
        except Exception as e:
            logger.error(f"Failed to generate short-lived image URL for {s3_key}: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to generate image access URL: {str(e)}")
    
    def file_exists(self, key: str) -> bool:
        """Check if file exists in S3"""
        if not self.s3_client:
            return False
        
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=key)
            return True
        except:
            return False
    
    # ============================================================================
    # PRIVATE HELPER METHODS
    # ============================================================================
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename by removing invalid characters"""
        import re
        if not filename:
            return ""
        sanitized = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', filename)
        sanitized = sanitized.strip(' .')
        if len(sanitized) > 255:
            sanitized = sanitized[:255]
        return sanitized
    
    def _determine_file_type(self, content_type: str) -> str:
        """Determine file type from content type"""
        if content_type.startswith('audio/'):
            return 'track'
        elif content_type.startswith('video/'):
            return 'video'
        elif content_type.startswith('image/'):
            return 'image'
        else:
            return 'file'
    
    async def _upload_to_s3(self, file: UploadFile, key: str):
        """Upload file to S3 with streaming"""
        try:
            # Reset file pointer
            await file.seek(0)
            
            # Use streaming upload for better memory efficiency
            self.s3_client.upload_fileobj(
                file.file,
                self.bucket_name,
                key,
                ExtraArgs={
                    'ContentType': file.content_type,
                    'Metadata': {
                        'original-filename': file.filename or 'unknown',
                        'upload-timestamp': datetime.utcnow().isoformat()
                    }
                }
            )
            
        except Exception as e:
            logger.error(f"S3 upload failed: {e}")
            raise
    
    async def _upload_to_s3_from_bytes(self, file_stream: BytesIO, key: str, content_type: str):
        """Upload file to S3 from bytes stream"""
        try:
            file_stream.seek(0)
            
            # Run blocking S3 operation in executor to avoid blocking event loop
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self.s3_client.upload_fileobj(
                    file_stream,
                    self.bucket_name,
                    key,
                    ExtraArgs={
                        'ContentType': content_type,
                        'Metadata': {
                            'upload-timestamp': datetime.utcnow().isoformat()
                        }
                    }
                )
            )
            
        except Exception as e:
            logger.error(f"S3 upload failed: {e}")
            raise
    
    async def _extract_file_metadata(self, file: UploadFile, file_type: str) -> Dict[str, Any]:
        """Extract metadata from uploaded file (legacy method for compatibility)"""
        await file.seek(0)
        file_content = await file.read()
        await file.seek(0)
        file_size = len(file_content) if file_content else (file.size or 0)
        return self._extract_file_metadata_from_bytes(
            file_content, file_type, file.filename or "unknown", file.content_type or "application/octet-stream", file_size
        )
    
    def _extract_file_metadata_from_bytes(
        self, file_content: bytes, file_type: str, filename: str, content_type: str, file_size: int
    ) -> Dict[str, Any]:
        """Extract metadata from file bytes"""
        metadata = {
            'filename': filename,
            'content_type': content_type,
            'file_size': file_size,
            'upload_timestamp': datetime.utcnow().isoformat()
        }
        
        try:
            if file_type == 'track' and MUTAGEN_AVAILABLE:
                try:
                    temp_file = BytesIO(file_content)
                    audio_file = mutagen.File(temp_file)
                    
                    if audio_file:
                        metadata.update({
                            'duration': getattr(audio_file.info, 'length', 0),
                            'bitrate': getattr(audio_file.info, 'bitrate', 0),
                            'sample_rate': getattr(audio_file.info, 'sample_rate', 0),
                            'channels': getattr(audio_file.info, 'channels', 0)
                        })
                        
                        # Extract tags
                        if hasattr(audio_file, 'tags') and audio_file.tags:
                            for key, value in audio_file.tags.items():
                                if isinstance(value, list) and value:
                                    metadata[f'tag_{key.lower()}'] = value[0]
                except Exception as audio_error:
                    logger.warning(f"Failed to extract audio metadata: {audio_error}")
            
            elif file_type == 'image':
                try:
                    temp_file = BytesIO(file_content)
                    with Image.open(temp_file) as img:
                        metadata.update({
                            'width': img.width,
                            'height': img.height,
                            'format': img.format,
                            'mode': img.mode
                        })
                except Exception as img_error:
                    logger.warning(f"Failed to extract image metadata: {img_error}")
        
        except Exception as e:
            logger.warning(f"Failed to extract metadata: {e}")
        
        return metadata
    
    def _create_file_record(
        self, 
        db: Session, 
        user_id: str, 
        project_id: str, 
        file_type: str, 
        filename: str, 
        s3_key: str, 
        content_type: str, 
        file_size: int, 
        extracted_metadata: Dict[str, Any], 
        custom_metadata: Optional[Dict[str, Any]] = None
    ):
        """Create file record in PostgreSQL"""
        if file_type == 'track':
            # Combine extracted metadata with custom metadata
            combined_metadata = {
                **(extracted_metadata or {}),
                **(custom_metadata or {}),
                'file_size': file_size,
                'content_type': content_type
            }
            
            file_record = Track(
                id=str(uuid.uuid4()),
                project_id=project_id,
                title=filename,
                file_path=s3_key,
                ai_generated=custom_metadata.get('ai_generated', False) if custom_metadata else False,
                instrumental=custom_metadata.get('instrumental', False) if custom_metadata else False,
                track_metadata=combined_metadata
            )
            db.add(file_record)
            return file_record
        elif file_type == 'image':
            # Extract image metadata for Image model
            image_format = extracted_metadata.get('format', '').lower() if extracted_metadata.get('format') else None
            width = extracted_metadata.get('width')
            height = extracted_metadata.get('height')
            resolution = f"{width}x{height}" if width and height else None
            size_mb = int(file_size / (1024 * 1024)) if file_size else None
            
            # Combine all metadata
            image_metadata = {
                **(extracted_metadata or {}),
                **(custom_metadata or {}),
                'filename': filename,
                'content_type': content_type,
                'file_size': file_size
            }
            
            file_record = ImageModel(
                id=str(uuid.uuid4()),
                project_id=project_id,
                file_path=s3_key,
                type='reference',  # Required field - using 'reference' for uploaded reference images
                format=image_format,
                resolution=resolution,
                size_mb=size_mb,
                image_metadata=image_metadata
            )
            db.add(file_record)
            return file_record
        elif file_type == 'video':
            # Extract video metadata for Video model
            width = extracted_metadata.get('width')
            height = extracted_metadata.get('height')
            resolution = f"{width}x{height}" if width and height else None
            duration = extracted_metadata.get('duration')
            video_format = extracted_metadata.get('format', '').lower() if extracted_metadata.get('format') else None
            size_mb = int(file_size / (1024 * 1024)) if file_size else None
            
            # Combine all metadata
            video_metadata = {
                **(extracted_metadata or {}),
                **(custom_metadata or {}),
                'filename': filename,
                'content_type': content_type,
                'file_size': file_size
            }
            
            file_record = Video(
                id=str(uuid.uuid4()),
                project_id=project_id,
                file_path=s3_key,
                type='draft',
                duration=int(duration) if duration else None,
                format=video_format,
                resolution=resolution,
                size_mb=size_mb,
                video_metadata=video_metadata
            )
            db.add(file_record)
            return file_record
        else:
            # Extract audio metadata for Audio model
            duration = extracted_metadata.get('duration')
            audio_format = extracted_metadata.get('format', '').lower() if extracted_metadata.get('format') else None
            sample_rate = extracted_metadata.get('sample_rate')
            channels = extracted_metadata.get('channels')
            bitrate = extracted_metadata.get('bitrate')
            size_mb = int(file_size / (1024 * 1024)) if file_size else None
            
            file_record = Audio(
                id=str(uuid.uuid4()),
                project_id=project_id,
                file_path=s3_key,
                type='other',
                duration=int(duration) if duration else None,
                format=audio_format,
                sample_rate=sample_rate,
                channels=channels,
                bitrate=bitrate,
                size_mb=size_mb
            )
            db.add(file_record)
            return file_record
    
    async def _delete_project_files_from_s3(self, user_id: str, project_id: str, project_type: str):
        """Delete all project files from S3"""
        try:
            prefix = f"users/{user_id}/projects/{project_type}/{project_id}/"
            
            # List all objects with the prefix (if S3 available)
            if self.s3_client:
                paginator = self.s3_client.get_paginator('list_objects_v2')
                pages = paginator.paginate(Bucket=self.bucket_name, Prefix=prefix)
                
                # Delete all objects
                for page in pages:
                    if 'Contents' in page:
                        objects = [{'Key': obj['Key']} for obj in page['Contents']]
                        if objects:
                            self.s3_client.delete_objects(
                                Bucket=self.bucket_name,
                                Delete={'Objects': objects}
                            )
            
            logger.info(f"Deleted all files from S3 for project {project_id}")
            
        except Exception as e:
            logger.error(f"Failed to delete project files from S3: {e}")
            # Don't raise exception here as we still want to delete the project from database
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage service statistics"""
        try:
            # Get bucket info (if S3 available)
            if not self.s3_client:
                return {
                    'bucket': self.bucket_name,
                    'status': 'unavailable',
                    'message': 'S3 storage not available'
                }
            
            bucket_info = self.s3_client.head_bucket(Bucket=self.bucket_name)
            
            return {
                'bucket': self.bucket_name,
                'status': 'active',
                'timestamp': datetime.utcnow().isoformat(),
                'architecture': 'PostgreSQL + S3',
                'legacy_code_removed': True
            }
        except Exception as e:
            logger.error(f"Failed to get storage stats: {e}")
            return {
                'bucket': self.bucket_name,
                'status': 'error',
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(e)
            }


# Create singleton instance
backend_storage_service = BackendStorageService()
