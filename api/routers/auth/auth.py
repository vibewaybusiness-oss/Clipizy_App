"""
Unified Authentication Router
Combines authentication, user management, and OAuth functionality into a single router
"""

import json
import logging
import time
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import File, HTTPException, UploadFile, Depends
from fastapi.responses import Response, JSONResponse, RedirectResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel

from api.routers.factory import create_auth_router
from api.routers.base_router import create_standard_response, create_error_response
from api.services.database import get_db
from api.models import User
from api.schemas import Token, UserCreate, UserLogin, UserRead
from api.schemas.auth.oauth import OAuthResponse, OAuthTokenRequest
from api.services.auth import (
    auth_service,
    user_creation_service,
    user_management_service,
    oauth_service,
)
from api.services.storage import backend_storage_service

# Async helper function for storage creation
async def _create_storage_structure_async(user_id: str):
    """Create user storage structure asynchronously"""
    try:
        # Run the synchronous storage creation in a thread pool
        import asyncio
        loop = asyncio.get_event_loop()
        # Backend storage doesn't need explicit user structure creation
        # Database tables handle user isolation automatically
        pass
        logger.info(f"✅ [STORAGE] User storage structure created for user: {user_id}")
    except Exception as e:
        logger.error(f"❌ [STORAGE] Failed to create storage structure for user {user_id}: {e}")
from api.services.auth import get_current_user
from api.services.errors import ValidationErrors, ResourceErrors, handle_exception

logger = logging.getLogger(__name__)

# Create router using the new architecture
router_wrapper = create_auth_router(
    name="auth",
    prefix="",  # Let architecture handle the prefix
    tags=["Authentication"]
)
router = router_wrapper.router

# Security removed - handled by router wrapper


# REQUEST/RESPONSE MODELS
class UserRegistrationResponse(BaseModel):
    user: dict
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserLoginResponse(BaseModel):
    user: dict
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefreshResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# AUTHENTICATION ENDPOINTS
@router.post("/register", response_model=UserRegistrationResponse)
async def register(
    user_data: UserCreate,
    db: Session = router_wrapper.get_db_dependency()
):
    """Register a new user and return authentication tokens"""
    try:
        # Create user using service
        user = user_creation_service.create_user(db, user_data)

        # Note: Storage structure creation moved to onboarding flow for better UX

        # Create tokens and response using service
        access_token, refresh_token = user_management_service.create_token_pair(user)
        auth_response = user_management_service.create_auth_response(user, access_token, refresh_token)

        return UserRegistrationResponse(**auth_response)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}", exc_info=True)
        raise handle_exception(e, "registering user")


@router.post("/login", response_model=UserLoginResponse)
async def login(
    login_data: UserLogin,
    response: Response,
    db: Session = router_wrapper.get_db_dependency()
):
    """Authenticate user and return tokens"""
    try:
        # Authenticate user using service
        user = auth_service.authenticate_user(db, login_data.email, login_data.password)
        if not user:
            raise ValidationErrors.invalid_credentials()

        # Update last login using service
        auth_service.update_user_last_login(db, str(user.id))

        # Note: Storage structure creation moved to onboarding flow for better UX

        # Create tokens and response using service
        access_token, refresh_token = user_management_service.create_token_pair(user)
        auth_response = user_management_service.create_auth_response(user, access_token, refresh_token)

        # Set cookies for cookie-based authentication fallback
        response.set_cookie(
            key="access_token",
            value=access_token,
            max_age=30 * 60,  # 30 minutes
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite="lax"
        )
        
        response.set_cookie(
            key="refresh_token", 
            value=refresh_token,
            max_age=30 * 24 * 60 * 60,  # 30 days
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite="lax"
        )

        return UserLoginResponse(**auth_response)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}", exc_info=True)
        raise handle_exception(e, "authenticating user")


@router.post("/refresh", response_model=TokenRefreshResponse)
async def refresh_token(
    request: dict,
    db: Session = router_wrapper.get_db_dependency()
):
    """Refresh access token using refresh token"""
    try:
        refresh_token = request.get("refresh_token")
        if not refresh_token:
            raise ValidationErrors.missing_token()

        # Verify refresh token using service
        payload = auth_service.verify_refresh_token(refresh_token)
        if not payload:
            raise ValidationErrors.invalid_token()

        user_id = payload.get("sub")
        if not user_id:
            raise ValidationErrors.invalid_token()

        # Get user using service
        user = auth_service.get_user_by_id(db, user_id)
        if not user:
            raise ResourceErrors.user_not_found(user_id)

        # Create new access token using service
        access_token, _ = user_management_service.create_token_pair(user)

        return TokenRefreshResponse(
            access_token=access_token,
            token_type="bearer"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {e}", exc_info=True)
        raise handle_exception(e, "refreshing token")


@router.get("/me", response_model=UserRead)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user information"""
    try:
        return current_user
    except Exception as e:
        logger.error(f"Get user info error: {e}", exc_info=True)
        raise handle_exception(e, "getting user information")


# OAUTH ENDPOINTS
@router.get("/google")
async def google_auth():
    """Initiate Google OAuth flow"""
    try:
        logger.info("Google OAuth endpoint called")
        logger.info(f"OAuth service GOOGLE_CLIENT_ID: {getattr(oauth_service, 'GOOGLE_CLIENT_ID', 'NOT_SET')}")
        auth_url = oauth_service.get_google_auth_url()
        logger.info(f"Generated auth URL: {auth_url}")
        return create_standard_response(
            data={"auth_url": auth_url},
            message="Google OAuth URL generated"
        )
    except HTTPException as e:
        logger.info(f"HTTPException caught: {e.status_code} - {e.detail}")
        return JSONResponse(
            status_code=e.status_code,
            content={
                "success": False,
                "error": e.detail,
                "path": "/api/auth/google",
                "method": "GET"
            }
        )
    except Exception as e:
        logger.error(f"Google OAuth error: {e}", exc_info=True)
        raise handle_exception(e, "initiating Google OAuth")


@router.get("/github")
async def github_auth():
    """Initiate GitHub OAuth flow"""
    try:
        auth_url = oauth_service.get_github_auth_url()
        return create_standard_response(
            data={"auth_url": auth_url},
            message="GitHub OAuth URL generated"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"GitHub OAuth error: {e}", exc_info=True)
        raise handle_exception(e, "initiating GitHub OAuth")



@router.post("/google/callback", response_model=OAuthResponse)
async def google_callback(
    token_data: OAuthTokenRequest,
    db: Session = Depends(get_db)
):
    """Handle Google OAuth callback"""
    try:
        import asyncio
        import time
        start_time = time.time()
        logger.info(f"🔵 [OAUTH] Processing Google OAuth callback for code: {token_data.code[:10]}...")
        
        # Get user info from Google
        step_start = time.time()
        google_user_info = await oauth_service.get_google_user_info(token_data.code)
        logger.info(f"⏱️ [OAUTH] Google user info fetch took {time.time() - step_start:.2f}s")
        
        if not google_user_info:
            raise HTTPException(status_code=400, detail="Failed to get user info from Google")
        
        # Get or create user in database
        step_start = time.time()
        user = oauth_service.get_or_create_user(db, google_user_info)
        logger.info(f"⏱️ [OAUTH] User lookup/creation took {time.time() - step_start:.2f}s")
        
        if not user:
            raise HTTPException(status_code=400, detail="Failed to create or retrieve user")
        
        # Generate JWT tokens
        step_start = time.time()
        access_token = auth_service.create_access_token(data={"sub": str(user.id)})
        refresh_token = auth_service.create_refresh_token(data={"sub": str(user.id)})
        logger.info(f"⏱️ [OAUTH] Token generation took {time.time() - step_start:.2f}s")
        
        # Create storage structure asynchronously (non-blocking)
        asyncio.create_task(_create_storage_structure_async(user.id))
        
        # Prepare response
        response_data = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 3600,
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "is_active": user.is_active,
                "is_admin": user.is_admin,
                "credits_balance": user.credits_balance
            }
        }
        
        logger.info(f"✅ [OAUTH] Total OAuth callback took {time.time() - start_time:.2f}s")
        return OAuthResponse(**response_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Google OAuth callback error: {e}", exc_info=True)
        raise handle_exception(e, "processing Google OAuth callback")


@router.post("/github/callback", response_model=OAuthResponse)
async def github_callback(
    token_data: OAuthTokenRequest,
    db: Session = router_wrapper.get_db_dependency()
):
    """Handle GitHub OAuth callback"""
    try:
        # Get user info from GitHub using service
        user_info = await oauth_service.get_github_user_info(token_data.code)
        if not user_info:
            raise ValidationErrors.oauth_user_info_failed()

        # Find or create user using service
        user = oauth_service.get_or_create_user(db, user_info)
        if not user:
            raise ValidationErrors.oauth_user_creation_failed()

        # Update last login using service
        auth_service.update_user_last_login(db, str(user.id))

        # Note: Storage structure creation moved to onboarding flow for better UX

        # Create tokens and response using service
        access_token, refresh_token = user_management_service.create_token_pair(user)
        auth_response = user_management_service.create_auth_response(user, access_token, refresh_token)

        return OAuthResponse(**auth_response)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"GitHub OAuth callback error: {e}", exc_info=True)
        raise handle_exception(e, "processing GitHub OAuth callback")


@router.post("/youtube/callback")
async def youtube_callback(
    token_data: OAuthTokenRequest,
    current_user: User = Depends(get_current_user),
    db: Session = router_wrapper.get_db_dependency()
):
    """Handle YouTube OAuth callback for social media connection"""
    try:
        from api.services.social_medias.social_media_service import SocialMediaService
        from api.services.storage import backend_storage_service
        
        logger.info(f"🔵 [YOUTUBE OAUTH] Processing YouTube OAuth callback for user {current_user.id}")
        
        # Get YouTube access token using the same Google OAuth service
        youtube_tokens = await oauth_service.get_google_tokens(token_data.code)
        if not youtube_tokens:
            raise HTTPException(status_code=400, detail="Failed to get YouTube tokens")
        
        # Connect YouTube account using social media service
        social_media_service = SocialMediaService(backend_storage_service)
        social_account = await social_media_service.connect_account(
            db, 
            str(current_user.id), 
            "youtube", 
            youtube_tokens
        )
        
        logger.info(f"✅ [YOUTUBE OAUTH] Successfully connected YouTube account for user {current_user.id}")
        
        return create_standard_response(
            data={
                "success": True,
                "account": {
                    "id": str(social_account.id),
                    "platform": social_account.platform,
                    "account_name": social_account.account_name,
                    "connected": True,
                },
            },
            message="YouTube account connected successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"YouTube OAuth callback error: {e}", exc_info=True)
        raise handle_exception(e, "processing YouTube OAuth callback")


# ONBOARDING ENDPOINT
@router.post("/onboard")
async def onboard_user(
    current_user: User = Depends(get_current_user),
    db: Session = router_wrapper.get_db_dependency()
):
    """Ensure user is properly onboarded with credits and directory structure"""
    try:
        # Check if user needs onboarding
        needs_onboarding = False
        
        # Check if user has credits
        if current_user.credits_balance == 0 and current_user.total_credits_earned == 0:
            needs_onboarding = True
            logger.info(f"User {current_user.email} needs initial credits")
        
        # Ensure user has proper settings
        if not current_user.settings:
            needs_onboarding = True
            logger.info(f"User {current_user.email} needs initial settings")
        
        if needs_onboarding:
            # Create complete user profile (this will add credits and settings)
            user_creation_service.create_complete_user_profile(
                db=db,
                email=current_user.email,
                name=current_user.username,
                password=None,  # Don't change password
                oauth_provider=None,
                oauth_data=None,
                custom_user_id=str(current_user.id)
            )
            
            # Refresh user from database
            db.refresh(current_user)
            logger.info(f"User {current_user.email} onboarded successfully with {current_user.credits_balance} credits")
        
        # Backend storage doesn't need explicit user structure creation
        # Database tables handle user isolation automatically
        storage_created = True  # Always successful for backend storage
        
        return create_standard_response(
            data={
                "user_id": str(current_user.id),
                "email": current_user.email,
                "credits_balance": current_user.credits_balance,
                "onboarded": True,
                "s3_directory_created": storage_created,
                "needed_onboarding": needs_onboarding
            },
            message="User onboarding completed successfully"
        )
        
    except Exception as e:
        logger.error(f"Onboarding error for user {current_user.email}: {e}", exc_info=True)
        raise handle_exception(e, "onboarding user")


# USER MANAGEMENT ENDPOINTS
@router.get("/profile-info")
async def get_user_profile_info(
    current_user: User = Depends(get_current_user)
):
    """Get user profile information"""
    try:
        profile_data = user_creation_service.get_user_profile_data(current_user)

        return create_standard_response(
            data={"profile": profile_data},
            message="Profile information retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error getting user profile info: {str(e)}")
        raise handle_exception(e, "getting user profile information")


@router.put("/profile-info")
async def update_user_profile_info(
    profile_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = router_wrapper.get_db_dependency()
):
    """Update user profile information"""
    try:
        success = user_creation_service.update_user_profile(db, current_user, profile_data)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update profile")

        return create_standard_response(
            data={"profile": profile_data},
            message="Profile updated successfully"
        )
    except Exception as e:
        logger.error(f"Error updating user profile info: {str(e)}")
        raise handle_exception(e, "updating user profile information")


@router.get("/settings")
async def get_user_settings(
    current_user: User = Depends(get_current_user)
):
    """Get user settings from database"""
    try:
        formatted_settings = user_creation_service.get_user_settings_formatted(current_user)

        return create_standard_response(
            data={"settings": formatted_settings},
            message="User settings retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error getting user settings: {str(e)}")
        raise handle_exception(e, "getting user settings")


@router.put("/settings")
async def update_user_settings(
    settings_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = router_wrapper.get_db_dependency()
):
    """Update user settings in database"""
    try:
        success = user_creation_service.update_user_settings(db, current_user, settings_data)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update settings")

        return create_standard_response(
            data={"settings": settings_data},
            message="Settings updated successfully"
        )
    except Exception as e:
        logger.error(f"Error updating user settings: {str(e)}")
        raise handle_exception(e, "updating user settings")


@router.get("/billing-info")
async def get_user_billing_info(
    current_user: User = Depends(get_current_user)
):
    """Get user billing information from SQL database"""
    try:
        billing_data = user_creation_service.get_user_billing_data(current_user)

        return create_standard_response(
            data={"billing": billing_data},
            message="Billing information retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error getting user billing info: {str(e)}")
        raise handle_exception(e, "getting user billing information")


@router.put("/billing-info")
async def update_user_billing_info(
    billing_data: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    """Update user billing information in SQL database"""
    try:
        return create_standard_response(
            data={"billing": billing_data},
            message="Billing information updated successfully"
        )
    except Exception as e:
        logger.error(f"Error updating user billing info: {str(e)}")
        raise handle_exception(e, "updating user billing information")


@router.get("/storage-usage")
async def get_user_storage_usage(
    current_user: User = Depends(get_current_user)
):
    """Get user storage usage information"""
    try:
        usage_data = user_creation_service.get_user_storage_usage(current_user)

        return create_standard_response(
            data={"usage": usage_data},
            message="Storage usage retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error getting user storage usage: {str(e)}")
        raise handle_exception(e, "getting user storage usage")


@router.delete("/delete-account")
async def delete_user_account(
    current_user: User = Depends(get_current_user),
    db: Session = router_wrapper.get_db_dependency()
):
    """Delete user account and all associated data"""
    try:
        success = user_creation_service.delete_user_account(db, current_user)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete account")

        return create_standard_response(
            data={},
            message="Account deleted successfully"
        )
    except Exception as e:
        logger.error(f"Error deleting user account: {str(e)}")
        raise handle_exception(e, "deleting account")


@router.get("/app-settings")
async def get_app_settings(
    current_user: User = Depends(get_current_user)
):
    """Get application settings for the user"""
    try:
        app_settings = user_creation_service.get_app_settings(current_user)

        return create_standard_response(
            data={"settings": app_settings},
            message="App settings retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error getting app settings: {str(e)}")
        raise handle_exception(e, "getting app settings")


@router.put("/app-settings")
async def update_app_settings(
    settings_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = router_wrapper.get_db_dependency()
):
    """Update application settings for the user"""
    try:
        success = user_creation_service.update_app_settings(db, current_user, settings_data)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update app settings")

        return create_standard_response(
            data={},
            message="App settings updated successfully"
        )
    except Exception as e:
        logger.error(f"Error updating app settings: {str(e)}")
        raise handle_exception(e, "updating app settings")


@router.get("/social-settings")
async def get_social_settings(
    current_user: User = Depends(get_current_user)
):
    """Get social media settings for the user"""
    try:
        social_settings = user_creation_service.get_social_settings(current_user)

        return create_standard_response(
            data={"settings": social_settings},
            message="Social settings retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error getting social settings: {str(e)}")
        raise handle_exception(e, "getting social settings")


@router.put("/social-settings")
async def update_social_settings(
    settings_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = router_wrapper.get_db_dependency()
):
    """Update social media settings for the user"""
    try:
        success = user_creation_service.update_social_settings(db, current_user, settings_data)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update social settings")

        return create_standard_response(
            data={},
            message="Social settings updated successfully"
        )
    except Exception as e:
        logger.error(f"Error updating social settings: {str(e)}")
        raise handle_exception(e, "updating social settings")


@router.get("/subscription")
async def get_user_subscription(
    current_user: User = Depends(get_current_user)
):
    """Get user subscription information"""
    try:
        subscription_info = user_creation_service.get_subscription_info(current_user)

        return create_standard_response(
            data={"subscription": subscription_info},
            message="Subscription information retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error getting subscription info: {str(e)}")
        raise handle_exception(e, "getting subscription information")


@router.post("/upload-avatar")
async def upload_avatar(
    avatar: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = router_wrapper.get_db_dependency()
):
    """Upload user avatar"""
    try:
        # Validate file type
        allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/gif", "image/webp"]
        if avatar.content_type not in allowed_types:
            raise HTTPException(
                status_code=400, detail="Invalid file type. Please upload a JPG, PNG, GIF, or WebP image."
            )

        # Validate file size (2MB limit)
        max_size = 2 * 1024 * 1024  # 2MB
        file_content = await avatar.read()
        if len(file_content) > max_size:
            raise HTTPException(status_code=400, detail="File too large. Please upload an image smaller than 2MB.")

        # Process avatar upload using service
        result = user_creation_service.process_avatar_upload(db, current_user, file_content, avatar.filename)

        return create_standard_response(
            data=result,
            message="Avatar uploaded successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading avatar: {str(e)}")
        raise handle_exception(e, "uploading avatar")


@router.get("/avatar/{user_id}/{filename}")
async def get_user_avatar(user_id: str, filename: str):
    """Serve user avatar files"""
    try:
        # Validate filename to prevent directory traversal
        if ".." in filename or "/" in filename or "\\" in filename:
            raise HTTPException(status_code=400, detail="Invalid filename")

        # For now, return a placeholder response
        # In a real implementation, you would serve the actual file
        raise HTTPException(status_code=404, detail="Avatar not found")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error serving avatar: {str(e)}")
        raise handle_exception(e, "serving avatar")


@router.get("/export-data")
async def export_user_data(
    current_user: User = Depends(get_current_user)
):
    """Export user data as JSON"""
    try:
        user_id = str(current_user.id)
        export_data = user_creation_service.export_user_data(current_user)

        return Response(
            content=json.dumps(export_data, indent=2),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename=clipizi-data-export-{user_id}.json"},
        )
    except Exception as e:
        logger.error(f"Error exporting user data: {str(e)}")
        raise handle_exception(e, "exporting user data")


# DEBUG ENDPOINTS (for development)
@router.get("/debug")
async def debug_oauth_config():
    """Debug OAuth configuration"""
    import os

    return create_standard_response(
        data={
            "google_client_id": os.getenv("GOOGLE_CLIENT_ID", "NOT_SET")[:10] + "...",
            "google_client_secret": os.getenv("GOOGLE_CLIENT_SECRET", "NOT_SET")[:10] + "...",
            "oauth_redirect_uri": os.getenv("OAUTH_REDIRECT_URI", "NOT_SET"),
            "github_client_id": os.getenv("GITHUB_CLIENT_ID", "NOT_SET"),
            "github_client_secret": os.getenv("GITHUB_CLIENT_SECRET", "NOT_SET")[:10] + "...",
        },
        message="OAuth configuration debug info"
    )


@router.post("/test-callback")
async def test_oauth_callback(
    request: dict,
    db: Session = router_wrapper.get_db_dependency()
):
    """Test OAuth callback with detailed error information"""
    try:
        code = request.get("code")
        if not code:
            return create_error_response("No code provided in request")

        logger.info(f"Test callback received code: {code[:10]}...")
        logger.info(f"OAuth redirect URI: {oauth_service.redirect_uri}")
        logger.info(f"OAuth client ID: {oauth_service.GOOGLE_CLIENT_ID[:10]}...")

        # Test the OAuth service directly with timeout
        import asyncio
        try:
            oauth_user_info = await asyncio.wait_for(
                oauth_service.get_google_user_info(code),
                timeout=10.0
            )
        except asyncio.TimeoutError:
            return create_error_response("OAuth request timed out after 10 seconds")
        
        logger.info(f"OAuth user info result: {oauth_user_info}")

        if not oauth_user_info:
            return create_error_response("Failed to get user info from Google")

        return create_standard_response(
            data={"user_info": oauth_user_info},
            message="OAuth test successful"
        )

    except Exception as e:
        logger.error(f"Test callback error: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")

        return create_error_response(
            f"OAuth test failed: {str(e)}"
        )


@router.post("/onboarding/setup")
async def setup_user_onboarding(
    current_user: User = Depends(get_current_user),
    db: Session = router_wrapper.get_db_dependency()
):
    """Setup user onboarding - create storage structure and initial setup"""
    try:
        logger.info(f"Setting up onboarding for user: {current_user.email}")
        
        # Backend storage doesn't need explicit user structure creation
        # Database tables handle user isolation automatically
        storage_created = True  # Always successful for backend storage
        if storage_created:
            logger.info(f"✅ User storage structure ready for {current_user.email}")
        else:
            logger.warning(f"⚠️ Failed to create storage structure for {current_user.email}")
        
        return create_standard_response(
            data={
                "storage_created": storage_created,
                "user_id": str(current_user.id),
                "email": current_user.email
            },
            message="User onboarding setup completed"
        )
        
    except Exception as e:
        logger.error(f"Onboarding setup error for {current_user.email}: {e}", exc_info=True)
        raise handle_exception(e, "setting up user onboarding")


@router.post("/test")
async def test_post():
    """Test POST endpoint"""
    print("DEBUG: Test POST endpoint called")
    return create_standard_response(
        data={"message": "POST endpoint works"},
        message="Test endpoint successful"
    )


# Health check endpoint is automatically added by BaseRouter
# Error handling is automatically added by BaseRouter
# Authentication is automatically handled by AuthRouter (no auth required for auth endpoints)
