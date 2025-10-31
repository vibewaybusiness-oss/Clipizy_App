"""
Social Media Automation Router
REST API endpoints for social media account management and automated publishing
"""

import logging
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.services.database import get_db
from api.models import Export, User
from api.services.storage import backend_storage_service
from api.services.social_medias.social_media_service import SocialMediaService
from api.services.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(tags=["social-media"])

# Initialize services
social_media_service = SocialMediaService(backend_storage_service)


@router.get("/connect/{platform}")
async def initiate_oauth_flow(platform: str, current_user: User = Depends(get_current_user)):
    """Initiate OAuth flow for a social media platform"""
    try:
        if platform == "youtube":
            from api.services.auth.auth import oauth_service
            auth_url = oauth_service.get_youtube_auth_url()
            return {"success": True, "auth_url": auth_url}
        else:
            raise HTTPException(status_code=400, detail=f"Platform {platform} not supported for OAuth")
    except Exception as e:
        logger.error(f"Failed to initiate OAuth for {platform}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/connect/{platform}")
async def connect_account(
    platform: str,
    auth_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Connect a social media account via OAuth"""
    user_id = str(current_user.id)

    try:
        social_account = await social_media_service.connect_account(db, user_id, platform, auth_data)
        return {
            "success": True,
            "account": {
                "id": str(social_account.id),
                "platform": social_account.platform,
                "account_name": social_account.account_name,
                "connected": True,
            },
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to connect {platform} account: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/accounts")
async def get_connected_accounts(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all connected social media accounts for a user"""
    user_id = str(current_user.id)

    try:
        accounts = await social_media_service.get_connected_accounts(db, user_id)
        return {"accounts": accounts}
    except Exception as e:
        logger.error(f"Failed to get connected accounts: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/accounts/{account_id}")
async def disconnect_account(
    account_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Disconnect a social media account"""
    user_id = str(current_user.id)

    try:
        result = await social_media_service.disconnect_account(db, account_id, user_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to disconnect account: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/publish/{export_id}")
async def publish_video(
    export_id: str,
    platforms: List[str],
    publish_options: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Publish a video to one or more social media platforms"""
    user_id = str(current_user.id)

    # Get the export
    export = db.query(Export).filter(Export.id == export_id, Export.user_id == user_id).first()

    if not export:
        raise HTTPException(status_code=404, detail="Export not found")

    try:
        if len(platforms) == 1:
            result = await social_media_service.publish_video(db, export, platforms[0], user_id, publish_options)
        else:
            result = await social_media_service.batch_publish(db, export, platforms, user_id, publish_options)

        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to publish video: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/analytics/{stats_id}")
async def get_video_analytics(
    stats_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get current analytics for a published video"""
    try:
        analytics = await social_media_service.get_analytics(db, stats_id)
        return {"success": True, "analytics": analytics, "fetched_at": analytics.get("fetched_at")}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get analytics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/publish/batch")
async def batch_publish_multiple_exports(
    export_ids: List[str],
    platforms: List[str],
    publish_options: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Publish multiple videos to multiple platforms"""
    user_id = str(current_user.id)
    results = []

    for export_id in export_ids:
        export = db.query(Export).filter(Export.id == export_id, Export.user_id == user_id).first()

        if not export:
            results.append({"export_id": export_id, "success": False, "error": "Export not found"})
            continue

        try:
            result = await social_media_service.batch_publish(db, export, platforms, user_id, publish_options)
            result["export_id"] = export_id
            results.append(result)
        except Exception as e:
            results.append({"export_id": export_id, "success": False, "error": str(e)})

    return {"total_exports": len(export_ids), "results": results}


@router.get("/platforms")
async def get_supported_platforms():
    """Get list of supported social media platforms"""
    try:
        return await social_media_service.get_supported_platforms()
    except Exception as e:
        logger.error(f"Failed to get supported platforms: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/test-connection/{platform}")
async def test_platform_connection(platform: str, access_token: str, current_user: User = Depends(get_current_user)):
    """Test connection to a social media platform without saving"""
    try:
        result = await social_media_service.test_platform_connection(platform, access_token)
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to test {platform} connection: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
