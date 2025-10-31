"""
Mailing Router
Handles email subscription and mailing list management
"""

import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from api.services.database import get_db
from api.services.auth.auth import get_current_user
from api.routers.factory import create_business_router
from api.routers.base_router import create_standard_response
from api.models import User
from api.services.errors import handle_exception

logger = logging.getLogger(__name__)

# Create router using sophisticated architecture
router_wrapper = create_business_router("mailing", "", ["Mailing"])  # Let architecture handle the prefix
router = router_wrapper.router


class SubscribeRequest(BaseModel):
    email: EmailStr
    source: str = "website"


class UnsubscribeRequest(BaseModel):
    email: EmailStr


@router.post("/subscribe")
async def subscribe_to_mailing_list(
    request: SubscribeRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """Subscribe email to mailing list"""
    try:
        # Import mailing service
        from api.services.business.mailing_service import mailing_service
        
        # Subscribe the email
        result = await mailing_service.subscribe_email(
            email=request.email,
            source=request.source,
            user_id=current_user.id if current_user else None
        )
        
        return create_standard_response(
            data={
                "email": request.email,
                "source": request.source,
                "subscribed_at": result.get("subscribed_at"),
                "subscriber_id": result.get("subscriber_id")
            },
            message="Successfully subscribed to mailing list"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error subscribing to mailing list: {str(e)}")
        raise handle_exception(e, "subscribing to mailing list")


@router.post("/unsubscribe")
async def unsubscribe_from_mailing_list(
    request: UnsubscribeRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """Unsubscribe email from mailing list"""
    try:
        # Import mailing service
        from api.services.business.mailing_service import mailing_service
        
        # Unsubscribe the email
        result = await mailing_service.unsubscribe_email(
            email=request.email,
            user_id=current_user.id if current_user else None
        )
        
        return create_standard_response(
            data={
                "email": request.email,
                "unsubscribed_at": result.get("unsubscribed_at")
            },
            message="Successfully unsubscribed from mailing list"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error unsubscribing from mailing list: {str(e)}")
        raise handle_exception(e, "unsubscribing from mailing list")


@router.get("/status/{email}")
async def get_subscription_status(
    email: EmailStr,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """Get subscription status for an email"""
    try:
        # Import mailing service
        from api.services.business.mailing_service import mailing_service
        
        # Get subscription status
        status = await mailing_service.get_subscription_status(email)
        
        return create_standard_response(
            data={
                "email": email,
                "is_subscribed": status.get("is_subscribed", False),
                "subscribed_at": status.get("subscribed_at"),
                "source": status.get("source")
            },
            message="Subscription status retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting subscription status: {str(e)}")
        raise handle_exception(e, "getting subscription status")


@router.get("/health")
async def health_check():
    """Health check endpoint for mailing router"""
    return create_standard_response(
        data={
            "status": "healthy",
            "service": "mailing"
        },
        message="Mailing service is healthy"
    )
