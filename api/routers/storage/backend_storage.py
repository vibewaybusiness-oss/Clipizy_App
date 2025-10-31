"""
Backend-Only Storage Router
Uses PostgreSQL for all project data and S3 only for file storage
No JSON files or localStorage dependencies
"""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status, Request, Depends
from sqlalchemy.orm import Session

from api.services.storage.backend_storage import backend_storage_service
from api.services.database import get_db
from api.services.auth.auth import get_current_user
from api.routers.factory import create_media_router
from api.routers.base_router import create_standard_response
from api.models import User, Project, ProjectStatus
from api.services.errors import handle_exception
from api.middleware.auth_middleware import get_user_from_request
from api.config.logging import get_router_logger

logger = get_router_logger("backend-storage")

# Create router using sophisticated architecture
router_wrapper = create_media_router("storage", "/api/storage", ["Backend Storage"])  # Use correct prefix
router = router_wrapper.router

# Supported project types
SUPPORTED_PROJECT_TYPES = ['music-clip', 'video-edit', 'audio-edit', 'image-edit', 'custom']


# ============================================================================
# PROJECT DATA MANAGEMENT ENDPOINTS (PostgreSQL-based)
# ============================================================================

@router.post("/projects/{project_id}/data")
async def save_project_data(
    project_id: str,
    request: Request,
    data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Save project data to PostgreSQL database"""
    try:
        project_type = data.get('projectType', 'music-clip')
        
        if project_type not in SUPPORTED_PROJECT_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid project type. Supported types: {SUPPORTED_PROJECT_TYPES}"
            )
        
        result = await backend_storage_service.save_project_data(
            db=db,
            user_id=str(current_user.id),
            project_id=project_id,
            project_type=project_type,
            data=data
        )
        
        logger.info(f"Project data saved to PostgreSQL: {project_id}")
        
        return create_standard_response(
            data={"message": result, "project_id": project_id},
            message="Project data saved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to save project data: {e}")
        return handle_exception(e, "Failed to save project data")


@router.get("/projects/{project_id}/data")
async def load_project_data(
    project_id: str,
    request: Request,
    project_type: str = "music-clip",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Load project data from PostgreSQL database"""
    try:
        if project_type not in SUPPORTED_PROJECT_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid project type. Supported types: {SUPPORTED_PROJECT_TYPES}"
            )
        
        data = await backend_storage_service.load_project_data(
            db=db,
            user_id=str(current_user.id),
            project_id=project_id,
            project_type=project_type
        )
        
        logger.info(f"Project data loaded from PostgreSQL: {project_id}")
        
        return create_standard_response(
            data=data,
            message="Project data loaded successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to load project data: {e}")
        return handle_exception(e, "Failed to load project data")


@router.post("/projects/{project_id}/update-data")
async def update_project_data(
    project_id: str,
    request: Request,
    data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update project data in PostgreSQL database"""
    try:
        project_type = data.get('projectType', 'music-clip')
        
        if project_type not in SUPPORTED_PROJECT_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid project type. Supported types: {SUPPORTED_PROJECT_TYPES}"
            )
        
        await backend_storage_service.save_project_data(
            db=db,
            user_id=str(current_user.id),
            project_id=project_id,
            project_type=project_type,
            data=data
        )
        
        logger.info(f"Project data updated in PostgreSQL: {project_id}")
        
        return create_standard_response(
            data={"project_id": project_id},
            message="Project data updated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update project data: {e}")
        return handle_exception(e, "Failed to update project data")


@router.delete("/projects/{project_id}/data")
async def delete_project_data(
    project_id: str,
    request: Request,
    project_type: str = "music-clip",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete project data from PostgreSQL database"""
    try:
        if project_type not in SUPPORTED_PROJECT_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid project type. Supported types: {SUPPORTED_PROJECT_TYPES}"
            )
        
        result = await backend_storage_service.delete_project_data(
            db=db,
            user_id=str(current_user.id),
            project_id=project_id,
            project_type=project_type
        )
        
        logger.info(f"Project data deleted from PostgreSQL: {project_id}")
        
        return create_standard_response(
            data={"message": result, "project_id": project_id},
            message="Project data deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete project data: {e}")
        return handle_exception(e, "Failed to delete project data")


# ============================================================================
# FILE MANAGEMENT ENDPOINTS (S3-based)
# ============================================================================

@router.post("/projects/{project_id}/files/upload")
async def upload_project_file(
    project_id: str,
    request: Request,
    file: UploadFile = File(...),
    project_type: str = Form("music-clip"),
    metadata: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload file to S3 and save metadata to PostgreSQL"""
    try:
        if project_type not in SUPPORTED_PROJECT_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid project type. Supported types: {SUPPORTED_PROJECT_TYPES}"
            )
        
        # Parse metadata if provided
        parsed_metadata = {}
        if metadata:
            try:
                import json
                parsed_metadata = json.loads(metadata)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid metadata JSON")
        
        file_info = await backend_storage_service.upload_project_file(
            db=db,
            user_id=str(current_user.id),
            project_id=project_id,
            project_type=project_type,
            file=file,
            metadata=parsed_metadata
        )
        
        logger.info(f"File uploaded successfully: {file_info['filename']}")
        
        return create_standard_response(
            data=file_info,
            message="File uploaded successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to upload file: {e}")
        return handle_exception(e, "File upload failed")


@router.delete("/projects/{project_id}/files/{file_id}")
async def delete_project_file(
    project_id: str,
    file_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete file from S3 and PostgreSQL"""
    try:
        result = await backend_storage_service.delete_project_file(
            db=db,
            user_id=str(current_user.id),
            project_id=project_id,
            file_id=file_id
        )
        
        logger.info(f"File deleted successfully: {file_id}")
        
        return create_standard_response(
            data={"message": result, "file_id": file_id},
            message="File deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete file: {e}")
        return handle_exception(e, "File deletion failed")


@router.get("/projects/{project_id}/files/{file_id}/url")
async def get_file_url(
    project_id: str,
    file_id: str,
    request: Request,
    expiration: int = 3600,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get presigned URL for file access"""
    try:
        # Get file record to get S3 key
        from api.models import Track, Image as ImageModel, Video, Audio
        
        file_record = None
        for model in [Track, ImageModel, Video, Audio]:
            file_record = db.query(model).filter(
                model.id == file_id,
                model.user_id == str(current_user.id),
                model.project_id == project_id
            ).first()
            if file_record:
                break
        
        if not file_record:
            raise HTTPException(status_code=404, detail="File not found")
        
        url = backend_storage_service.get_presigned_url(
            key=file_record.file_path,
            expiration=expiration
        )
        
        return create_standard_response(
            data={"url": url, "expiration": expiration},
            message="File URL generated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate file URL: {e}")
        return handle_exception(e, "Failed to generate file URL")


# ============================================================================
# PROJECT MANAGEMENT ENDPOINTS
# ============================================================================

@router.post("/projects")
async def create_project(
    request: Request,
    project_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new project of any supported type"""
    try:
        project_type = project_data.get('type')
        if not project_type or project_type not in SUPPORTED_PROJECT_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid project type. Supported types: {SUPPORTED_PROJECT_TYPES}"
            )
        
        # Create project in database
        project = Project(
            id=str(uuid.uuid4()),
            user_id=str(current_user.id),
            type=project_type,
            name=project_data.get('name', f'New {project_type} Project'),
            description=project_data.get('description', ''),
            status=ProjectStatus.DRAFT
        )
        
        db.add(project)
        db.commit()
        db.refresh(project)
        
        logger.info(f"Project created: {project.id}")
        
        return create_standard_response(
            data={
                "id": str(project.id),
                "name": project.name,
                "type": project.type,
                "description": project.description,
                "created_at": project.created_at.isoformat(),
                "status": project.status.value
            },
            message="Project created successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create project: {e}")
        return handle_exception(e, "Failed to create project")


@router.get("/projects")
async def list_projects(
    request: Request,
    project_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List user's projects, optionally filtered by type"""
    try:
        from api.models import Export, Track, Video, Image as ImageModel
        
        query = db.query(Project).filter(Project.user_id == str(current_user.id))
        
        if project_type:
            if project_type not in SUPPORTED_PROJECT_TYPES:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid project type. Supported types: {SUPPORTED_PROJECT_TYPES}"
                )
            query = query.filter(Project.type == project_type)
        
        projects = query.order_by(Project.updated_at.desc()).all()
        
        project_list = []
        for project in projects:
            project_dict = {
                "id": str(project.id),
                "name": project.name,
                "type": project.type,
                "description": project.description,
                "created_at": project.created_at.isoformat(),
                "updated_at": project.updated_at.isoformat(),
                "status": project.status.value,
                "user_id": str(project.user_id)
            }
            
            latest_export = db.query(Export).filter(
                Export.project_id == project.id
            ).order_by(Export.created_at.desc()).first()
            
            if latest_export and latest_export.file_path:
                try:
                    export_url = backend_storage_service.get_presigned_url(
                        latest_export.file_path, 
                        expiration=3600
                    )
                    project_dict["preview_url"] = export_url
                    project_dict["export_id"] = str(latest_export.id)
                except Exception as e:
                    logger.warning(f"Failed to generate export URL for project {project.id}: {e}")
            
            thumbnail = db.query(ImageModel).filter(
                ImageModel.project_id == project.id,
                ImageModel.type == "thumbnail"
            ).order_by(ImageModel.created_at.desc()).first()
            
            if thumbnail and thumbnail.file_path:
                try:
                    thumbnail_url = backend_storage_service.get_presigned_url(
                        thumbnail.file_path,
                        expiration=3600
                    )
                    project_dict["thumbnail_url"] = thumbnail_url
                except Exception as e:
                    logger.warning(f"Failed to generate thumbnail URL for project {project.id}: {e}")
            
            track_count = db.query(Track).filter(Track.project_id == project.id).count()
            video_count = db.query(Video).filter(Video.project_id == project.id).count()
            image_count = db.query(ImageModel).filter(ImageModel.project_id == project.id).count()
            
            project_dict["media_counts"] = {
                "tracks": track_count,
                "videos": video_count,
                "images": image_count
            }
            
            project_list.append(project_dict)
        
        return create_standard_response(
            data={"projects": project_list, "count": len(project_list)},
            message="Projects retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list projects: {e}")
        return handle_exception(e, "Failed to list projects")


@router.get("/projects/{project_id}")
async def get_project(
    project_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get project details"""
    try:
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.user_id == str(current_user.id)
        ).first()
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        return create_standard_response(
            data={
                "id": str(project.id),
                "name": project.name,
                "type": project.type,
                "description": project.description,
                "created_at": project.created_at.isoformat(),
                "updated_at": project.updated_at.isoformat(),
                "status": project.status.value,
                "settings": project.settings,
                "analysis": project.analysis
            },
            message="Project retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get project: {e}")
        return handle_exception(e, "Failed to get project")


@router.put("/projects/{project_id}")
async def update_project(
    project_id: str,
    request: Request,
    project_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update project"""
    try:
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.user_id == str(current_user.id)
        ).first()
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Update allowed fields
        if 'name' in project_data:
            project.name = project_data['name']
        if 'description' in project_data:
            project.description = project_data['description']
        
        project.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(project)
        
        logger.info(f"Project updated: {project_id}")
        
        return create_standard_response(
            data={
                "id": str(project.id),
                "name": project.name,
                "type": project.type,
                "description": project.description,
                "updated_at": project.updated_at.isoformat()
            },
            message="Project updated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to update project: {e}")
        return handle_exception(e, "Failed to update project")


@router.get("/projects/{project_id}/script")
async def get_project_script(
    project_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get project script data"""
    try:
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.user_id == str(current_user.id)
        ).first()
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Get script data from project data
        project_data = await backend_storage_service.load_project_data(
            db=db,
            user_id=str(current_user.id),
            project_id=project_id,
            project_type=project.type
        )
        
        script_data = project_data.get('script', {}) if project_data else {}
        
        logger.info(f"Project script retrieved: {project_id}")
        
        return create_standard_response(
            data=script_data,
            message="Project script retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get project script: {e}")
        return handle_exception(e, "Failed to get project script")


@router.get("/projects/{project_id}/analysis")
async def get_project_analysis(
    project_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get project analysis data"""
    try:
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.user_id == str(current_user.id)
        ).first()
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Get analysis data from project data
        project_data = await backend_storage_service.load_project_data(
            db=db,
            user_id=str(current_user.id),
            project_id=project_id,
            project_type=project.type
        )
        
        analysis_data = project_data.get('analysis', {}) if project_data else {}
        
        logger.info(f"Project analysis retrieved: {project_id}")
        
        return create_standard_response(
            data=analysis_data,
            message="Project analysis retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get project analysis: {e}")
        return handle_exception(e, "Failed to get project analysis")


@router.get("/projects/{project_id}/settings")
async def get_project_settings(
    project_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get project settings data"""
    try:
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.user_id == str(current_user.id)
        ).first()
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Get settings data from project data
        project_data = await backend_storage_service.load_project_data(
            db=db,
            user_id=str(current_user.id),
            project_id=project_id,
            project_type=project.type
        )
        
        settings_data = project_data.get('settings', {}) if project_data else {}
        
        if isinstance(settings_data, dict):
            logger.info(f"📤 Loading settings keys: {list(settings_data.keys())}")
            if 'tracks' in settings_data:
                tracks_data = settings_data['tracks']
                logger.info(f"🎵 Tracks found when loading! Count: {len(tracks_data) if isinstance(tracks_data, list) else 'not a list'}")
                if isinstance(tracks_data, list) and len(tracks_data) > 0:
                    logger.info(f"🎵 First track on load: {tracks_data[0]}")
            else:
                logger.warning("⚠️ No tracks in loaded settings")
        
        logger.info(f"Project settings retrieved: {project_id}")
        
        return create_standard_response(
            data=settings_data,
            message="Project settings retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get project settings: {e}")
        return handle_exception(e, "Failed to get project settings")


@router.put("/projects/{project_id}/settings")
async def update_project_settings(
    project_id: str,
    request: Request,
    settings_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update project settings data"""
    try:
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.user_id == str(current_user.id)
        ).first()
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Load existing project data
        existing_data = await backend_storage_service.load_project_data(
            db=db,
            user_id=str(current_user.id),
            project_id=project_id,
            project_type=project.type
        ) or {}
        
        # Update settings data
        existing_data['settings'] = settings_data
        
        # Save updated project data
        await backend_storage_service.save_project_data(
            db=db,
            user_id=str(current_user.id),
            project_id=project_id,
            project_type=project.type,
            data=existing_data
        )
        
        logger.info(f"Project settings updated: {project_id}")
        
        return create_standard_response(
            data={"project_id": project_id, "settings": settings_data},
            message="Project settings updated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update project settings: {e}")
        return handle_exception(e, "Failed to update project settings")


@router.put("/projects/{project_id}/analysis")
async def update_project_analysis(
    project_id: str,
    request: Request,
    analysis_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update project analysis data"""
    try:
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.user_id == str(current_user.id)
        ).first()
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Load existing project data
        existing_data = await backend_storage_service.load_project_data(
            db=db,
            user_id=str(current_user.id),
            project_id=project_id,
            project_type=project.type
        ) or {}
        
        # Update analysis data
        existing_data['analysis'] = analysis_data
        
        # Save updated project data
        await backend_storage_service.save_project_data(
            db=db,
            user_id=str(current_user.id),
            project_id=project_id,
            project_type=project.type,
            data=existing_data
        )
        
        logger.info(f"Project analysis updated: {project_id}")
        
        return create_standard_response(
            data={"project_id": project_id, "analysis": analysis_data},
            message="Project analysis updated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update project analysis: {e}")
        return handle_exception(e, "Failed to update project analysis")


@router.delete("/projects/{project_id}")
async def delete_project(
    project_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete project and all associated data"""
    try:
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.user_id == str(current_user.id)
        ).first()
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        project_type = project.type
        
        # Delete project data (this will also delete files from S3)
        await backend_storage_service.delete_project_data(
            db=db,
            user_id=str(current_user.id),
            project_id=project_id,
            project_type=project_type
        )
        
        logger.info(f"Project deleted: {project_id}")
        
        return create_standard_response(
            data={"project_id": project_id},
            message="Project deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to delete project: {e}")
        return handle_exception(e, "Failed to delete project")


# ============================================================================
# UTILITY ENDPOINTS
# ============================================================================

@router.get("/project-types")
async def get_supported_project_types(request: Request):
    """Get supported project types"""
    return create_standard_response(
        data={"project_types": SUPPORTED_PROJECT_TYPES},
        message="Supported project types retrieved"
    )


@router.get("/stats")
async def get_storage_stats(request: Request):
    """Get storage service statistics"""
    try:
        stats = backend_storage_service.get_storage_stats()
        return create_standard_response(
            data=stats,
            message="Storage statistics retrieved"
        )
    except Exception as e:
        logger.error(f"Failed to get storage stats: {e}")
        return handle_exception(e, "Failed to get storage statistics")


# ============================================================================
# AUTO-SAVE ENDPOINT
# ============================================================================

@router.post("/projects/{project_id}/auto-save")
async def auto_save_project_data(
    project_id: str,
    request: Request,
    data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Auto-save project data to PostgreSQL"""
    try:
        project_type = data.get('projectType', 'music-clip')
        
        if project_type not in SUPPORTED_PROJECT_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid project type. Supported types: {SUPPORTED_PROJECT_TYPES}"
            )
        
        # Extract project data from the request
        project_data = data.get('projectData', {})
        
        # Debug logging
        logger.info(f"Auto-save received data structure: {list(data.keys())}")
        logger.info(f"Project data extracted: {list(project_data.keys())}")
        logger.info(f"Settings present: {'settings' in project_data}")
        logger.info(f"Analysis present: {'analysis' in project_data}")
        
        if 'settings' in project_data and isinstance(project_data['settings'], dict):
            settings = project_data['settings']
            logger.info(f"📦 Settings keys: {list(settings.keys())}")
            if 'tracks' in settings:
                tracks_data = settings['tracks']
                if isinstance(tracks_data, list):
                    logger.info(f"🎵 Tracks found in auto-save! Count: {len(tracks_data)}")
                    if len(tracks_data) > 0:
                        logger.info(f"🎵 First track: {tracks_data[0]}")
                else:
                    logger.warning(f"⚠️ Tracks is not a list: {type(tracks_data)}")
            else:
                logger.warning("⚠️ No tracks key in settings")
        
        result = await backend_storage_service.save_project_data(
            db=db,
            user_id=str(current_user.id),
            project_id=project_id,
            project_type=project_type,
            data=project_data
        )
        
        logger.info(f"Project data auto-saved to PostgreSQL: {project_id}")
        
        return create_standard_response(
            data={"message": result, "project_id": project_id, "timestamp": datetime.utcnow().isoformat()},
            message="Project data auto-saved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to auto-save project data: {e}")
        return handle_exception(e, "Failed to auto-save project data")
