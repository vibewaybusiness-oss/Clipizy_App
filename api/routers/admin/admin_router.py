"""
UNIFIED ADMIN ROUTER
Consolidated admin endpoints with business logic moved to services
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from api.services.database import get_db
from api.models import User
from api.services.auth import get_current_user
from api.services.admin import AdminCreditsService, AdminDatabaseService, AdminStripeService
from api.services.errors import handle_exception

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin", tags=["Admin"])


# REQUEST/RESPONSE MODELS
class AddCreditsRequest(BaseModel):
    user_id: str
    amount: int
    description: Optional[str] = None


class AddCreditsResponse(BaseModel):
    message: str
    new_balance: int
    transaction_id: str
    user_email: str
    user_id: str


class UserCreditsResponse(BaseModel):
    user_email: str
    user_id: str
    balance_info: dict


# AUTHENTICATION DEPENDENCY
def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Ensure current user is admin"""
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return current_user


# CREDITS ENDPOINTS
@router.post("/credits/add", response_model=AddCreditsResponse)
async def add_credits_to_user(
    request: AddCreditsRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Add credits to a user (admin only)"""
    try:
        result = AdminCreditsService.add_credits_to_user(
            db=db,
            user_id=request.user_id,
            amount=request.amount,
            description=request.description
        )
        return AddCreditsResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding credits: {e}", exc_info=True)
        raise handle_exception(e, "adding credits")


@router.get("/credits/user/{user_id}", response_model=UserCreditsResponse)
async def get_user_credits(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Get user credits information (admin only)"""
    try:
        result = AdminCreditsService.get_user_credits_info(db=db, user_id=user_id)
        return UserCreditsResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user credits: {e}", exc_info=True)
        raise handle_exception(e, "getting user credits")


# DATABASE ENDPOINTS
@router.get("/database/health")
async def database_health_check(current_user: User = Depends(get_admin_user)):
    """Check database health and connection status"""
    try:
        return AdminDatabaseService.get_database_health()
    except HTTPException:
        raise
    except Exception as e:
        raise handle_exception(e, "checking database health")


@router.get("/database/pool-status")
async def get_pool_status(current_user: User = Depends(get_admin_user)):
    """Get current database connection pool status"""
    try:
        return AdminDatabaseService.get_pool_status()
    except Exception as e:
        raise handle_exception(e, "getting pool status")


@router.get("/database/connection-test")
async def test_connection(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Test database connection with a simple query"""
    try:
        return AdminDatabaseService.test_connection(db)
    except HTTPException:
        raise
    except Exception as e:
        raise handle_exception(e, "testing database connection")


@router.get("/database/stats")
async def get_database_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Get database statistics and performance metrics"""
    try:
        return AdminDatabaseService.get_database_stats(db)
    except Exception as e:
        raise handle_exception(e, "getting database statistics")


@router.post("/database/pool-reset")
async def reset_connection_pool(current_user: User = Depends(get_admin_user)):
    """Reset the database connection pool"""
    try:
        return AdminDatabaseService.reset_connection_pool()
    except Exception as e:
        raise handle_exception(e, "resetting connection pool")


# STRIPE ENDPOINTS
@router.get("/stripe/products")
async def get_stripe_products(current_user: User = Depends(get_admin_user)):
    """Get all Stripe products"""
    try:
        return AdminStripeService.get_products()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching products: {str(e)}"
        )


@router.get("/stripe/prices")
async def get_stripe_prices(current_user: User = Depends(get_admin_user)):
    """Get all Stripe prices"""
    try:
        return AdminStripeService.get_prices()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching prices: {str(e)}"
        )


@router.get("/stripe/payment-links")
async def get_stripe_payment_links(current_user: User = Depends(get_admin_user)):
    """Get all Stripe payment links"""
    try:
        return AdminStripeService.get_payment_links()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching payment links: {str(e)}"
        )


@router.get("/stripe/customers")
async def get_stripe_customers(current_user: User = Depends(get_admin_user)):
    """Get all Stripe customers"""
    try:
        return AdminStripeService.get_customers()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching customers: {str(e)}"
        )


@router.get("/stripe/subscriptions")
async def get_stripe_subscriptions(current_user: User = Depends(get_admin_user)):
    """Get all Stripe subscriptions"""
    try:
        return AdminStripeService.get_subscriptions()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching subscriptions: {str(e)}"
        )


@router.get("/stripe/payments")
async def get_stripe_payments(current_user: User = Depends(get_admin_user)):
    """Get recent Stripe payments"""
    try:
        return AdminStripeService.get_payments()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching payments: {str(e)}"
        )


@router.get("/stripe/balance")
async def get_stripe_balance(current_user: User = Depends(get_admin_user)):
    """Get Stripe account balance"""
    try:
        return AdminStripeService.get_balance()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching balance: {str(e)}"
        )


@router.get("/stripe/stats")
async def get_stripe_stats(current_user: User = Depends(get_admin_user)):
    """Get Stripe account statistics"""
    try:
        return AdminStripeService.get_stats()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching stats: {str(e)}"
        )
