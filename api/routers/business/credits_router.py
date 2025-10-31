"""
Unified Credits and Payments Router
Consolidates all credits and payment functionality into a single, simplified router
"""

import json
import logging
import math
from typing import List, Dict, Any, Optional

from fastapi import Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from api.routers.factory import create_business_router
from api.routers.base_router import create_standard_response
from api.services.database import get_db
from api.services.auth.auth import get_current_user
from api.models import User
from api.schemas import (
    CreditsBalance,
    CreditsPurchaseRequest,
    CreditsSpendRequest,
    CreditsTransactionRead,
    PaymentIntentCreate,
    PaymentIntentResponse,
    PaymentRead,
)
from api.services.business.pricing_service import PRICES, credits_service
from api.services.business.stripe_service import stripe_service, CheckoutSessionRequest
from api.services.errors import ValidationErrors, handle_exception

logger = logging.getLogger(__name__)

# Create router using the new architecture
router_wrapper = create_business_router(
    name="credits",
    prefix="",  # Let architecture handle the prefix
    tags=["Credits & Payments"]
)
router = router_wrapper.router


# REQUEST/RESPONSE MODELS
class CreditsSpendResponse(BaseModel):
    message: str
    transaction_id: str
    new_balance: int


class AffordabilityCheckResponse(BaseModel):
    can_afford: bool
    amount_requested: int
    current_balance: int


class WrappedAffordabilityCheckResponse(BaseModel):
    status: str
    message: str
    data: AffordabilityCheckResponse
    timestamp: str


class CheckoutRequest(BaseModel):
    plan_id: str
    plan_type: str


# CREDITS MANAGEMENT ENDPOINTS
@router.get("/balance", response_model=CreditsBalance)
async def get_credits_balance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's current credits balance and recent transactions"""
    try:
        balance = credits_service.get_user_balance(db, str(current_user.id))
        return balance
    except Exception as e:
        logger.error(f"Error retrieving credits balance: {e}", exc_info=True)
        raise handle_exception(e, "retrieving credits balance")


@router.get("/transactions", response_model=List[CreditsTransactionRead])
async def get_transaction_history(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's credits transaction history with pagination"""
    try:
        if limit > 100:
            limit = 100
        if limit < 1:
            limit = 10

        transactions = credits_service.get_transaction_history(db, str(current_user.id), limit)
        return transactions
    except Exception as e:
        logger.error(f"Error retrieving transaction history: {e}", exc_info=True)
        raise handle_exception(e, "retrieving transaction history")


@router.post("/spend", response_model=CreditsSpendResponse)
async def spend_credits(
    spend_request: CreditsSpendRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Spend credits from user's account with validation"""
    try:
        result = credits_service.spend_credits_with_validation(db, str(current_user.id), spend_request)
        return create_standard_response(
            data=CreditsSpendResponse(**result),
            message="Credits spent successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error spending credits: {e}", exc_info=True)
        raise handle_exception(e, "spending credits")


@router.get("/can-afford/{amount}", response_model=WrappedAffordabilityCheckResponse)
async def check_affordability(
    amount: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Check if user can afford to spend the specified amount of credits"""
    try:
        result = credits_service.check_affordability_with_balance(db, str(current_user.id), amount)
        return create_standard_response(
            data=AffordabilityCheckResponse(**result),
            message="Affordability check completed"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking affordability: {e}", exc_info=True)
        raise handle_exception(e, "checking affordability")


# PAYMENT ENDPOINTS
@router.post("/purchase", response_model=PaymentIntentResponse)
async def purchase_credits(
    purchase_request: CreditsPurchaseRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Purchase credits using Stripe with validation"""
    try:
        payment_data = credits_service.create_payment_intent_data(purchase_request)
        payment_intent = stripe_service.process_payment_intent_creation(db, current_user.id, payment_data)
        return create_standard_response(
            data=payment_intent,
            message="Payment intent created successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating payment intent: {e}", exc_info=True)
        raise handle_exception(e, "creating payment intent")


@router.post("/checkout")
async def create_checkout_session(
    request: CheckoutRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a checkout session for subscription or credits purchase"""
    try:
        checkout_request = credits_service.create_checkout_request(request.plan_id, request.plan_type)
        result = stripe_service.process_checkout_session_creation(db, str(current_user.id), checkout_request)
        return create_standard_response(
            data=result,
            message="Checkout session created successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating checkout session: {e}", exc_info=True)
        raise handle_exception(e, "creating checkout session")


@router.post("/confirm/{payment_intent_id}")
async def confirm_payment_intent(
    payment_intent_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Confirm a payment intent"""
    try:
        result = stripe_service.process_payment_confirmation(db, payment_intent_id)
        return create_standard_response(
            data=result,
            message="Payment confirmed successfully"
        )
    except Exception as e:
        logger.error(f"Error confirming payment: {e}", exc_info=True)
        raise handle_exception(e, "confirming payment")


class GenerationPaymentConfirmationRequest(BaseModel):
    generation_type: str
    project_id: str
    generation_data: Dict[str, Any]
    pricing: Optional[Dict[str, Any]] = None


@router.post("/confirm-generation")
async def confirm_generation_payment(
    request: GenerationPaymentConfirmationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Confirm payment for a generation (music, video, image, audio)"""
    try:
        from api.services.business.pricing_service import PricingService
        
        generation_type = request.generation_type
        project_id = request.project_id
        generation_data = request.generation_data
        
        pricing_service = PricingService()
        cost: int = 0
        
        if request.pricing and 'credits' in request.pricing:
            cost = int(request.pricing['credits'])
        else:
            if generation_type == 'music':
                num_tracks = generation_data.get('num_tracks', 1)
                price_data = pricing_service.calculate_music_price(num_tracks)
                cost = price_data.get('credits', 20)
            elif generation_type == 'video':
                num_units = generation_data.get('num_units', 1)
                total_minutes = generation_data.get('total_minutes', 1.0)
                has_visualizer = generation_data.get('has_visualizer', False)
                price_data = pricing_service.calculate_recurring_scenes_price(
                    num_units, total_minutes, has_visualizer
                )
                cost = price_data.get('credits', 20)
            elif generation_type == 'image':
                num_units = generation_data.get('num_units', 1)
                total_minutes = generation_data.get('total_minutes', 1.0)
                has_visualizer = generation_data.get('has_visualizer', False)
                price_data = pricing_service.calculate_image_price(
                    num_units, total_minutes, has_visualizer
                )
                cost = price_data.get('credits', 20)
            else:
                cost = 20
        
        logger.info(f"💰 Confirming generation payment: type={generation_type}, project={project_id}, cost={cost}")
        
        spend_request = CreditsSpendRequest(
            amount=cost,
            description=f"Generation: {generation_type}",
            metadata={
                "project_id": project_id,
                "generation_type": generation_type,
                "generation_data": generation_data
            }
        )
        
        result = credits_service.spend_credits_with_validation(db, str(current_user.id), spend_request)
        
        return create_standard_response(
            data={
                "confirmed": True,
                "transaction_id": result["transaction_id"],
                "credits_deducted": cost,
                "new_balance": result["new_balance"],
                "generation_type": generation_type,
                "project_id": project_id
            },
            message="Generation payment confirmed and credits deducted"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error confirming generation payment: {e}", exc_info=True)
        raise handle_exception(e, "confirming generation payment")


@router.get("/payments", response_model=List[PaymentRead])
async def get_payment_history(
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's payment history"""
    try:
        if limit > 100:
            limit = 100

        payments = stripe_service.get_payment_history(db, str(current_user.id), limit)
        return create_standard_response(
            data=payments,
            message=f"Payment history retrieved successfully (showing {len(payments)} payments)"
        )
    except Exception as e:
        logger.error(f"Error retrieving payment history: {e}", exc_info=True)
        raise handle_exception(e, "retrieving payment history")


@router.get("/payments/{payment_id}", response_model=PaymentRead)
async def get_payment(
    payment_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get details of a specific payment"""
    try:
        from api.models import Payment

        payment = db.query(Payment).filter(Payment.id == payment_id, Payment.user_id == current_user.id).first()

        if not payment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")

        return create_standard_response(
            data=payment,
            message="Payment details retrieved successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving payment: {e}", exc_info=True)
        raise handle_exception(e, "retrieving payment")


@router.post("/refund/{payment_id}")
async def refund_payment(
    payment_id: str,
    amount_cents: int = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Refund a payment (admin or user's own payments)"""
    try:
        from api.models import Payment

        payment = db.query(Payment).filter(Payment.id == payment_id, Payment.user_id == current_user.id).first()

        if not payment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")

        result = stripe_service.process_payment_refund(db, payment_id, amount_cents)
        return create_standard_response(
            data=result,
            message="Refund processed successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing refund: {e}", exc_info=True)
        raise handle_exception(e, "processing refund")


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle Stripe webhook events"""
    try:
        payload = await request.body()
        signature = request.headers.get("stripe-signature")

        if not signature:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing stripe-signature header")

        result = stripe_service.process_webhook(db, payload.decode(), signature)
        return create_standard_response(
            data=result,
            message="Webhook processed successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing webhook: {e}", exc_info=True)
        raise handle_exception(e, "processing webhook")


# PRICING ENDPOINTS
@router.get("/pricing/config")
async def get_pricing_config():
    """Get the complete pricing configuration"""
    return create_standard_response(
        data=PRICES,
        message="Pricing configuration retrieved successfully"
    )


@router.get("/pricing/subscription-plans")
async def get_subscription_plans():
    """Get available subscription plans"""
    try:
        plans = credits_service.get_subscription_plans()
        return create_standard_response(
            data=plans,
            message="Subscription plans retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error retrieving subscription plans: {e}", exc_info=True)
        raise handle_exception(e, "retrieving subscription plans")


@router.get("/pricing/credits-packages")
async def get_credits_packages():
    """Get available credits packages"""
    try:
        packages = credits_service.get_credits_packages()
        return create_standard_response(
            data=packages,
            message="Credits packages retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error retrieving credits packages: {e}", exc_info=True)
        raise handle_exception(e, "retrieving credits packages")


@router.get("/pricing/music")
async def price_music(num_tracks: int = 1):
    """Calculate price for music generation"""
    try:
        price = credits_service.calculate_music_price(num_tracks)
        return create_standard_response(
            data=price,
            message=f"Music pricing calculated for {num_tracks} tracks"
        )
    except Exception as e:
        logger.error(f"Error calculating music price: {e}", exc_info=True)
        raise handle_exception(e, "calculating music price")


@router.get("/pricing/image")
async def price_image(num_units: int, total_minutes: float):
    """Calculate price for image generation"""
    try:
        price = credits_service.calculate_image_price(num_units, total_minutes)
        return create_standard_response(
            data=price,
            message=f"Image pricing calculated for {num_units} units, {total_minutes} minutes"
        )
    except Exception as e:
        logger.error(f"Error calculating image price: {e}", exc_info=True)
        raise handle_exception(e, "calculating image price")


@router.get("/pricing/looped-animation")
async def price_looped(num_units: int, total_minutes: float):
    """Calculate price for looped animation generation"""
    try:
        price = credits_service.calculate_looped_animation_price(num_units, total_minutes)
        return create_standard_response(
            data=price,
            message=f"Looped animation pricing calculated for {num_units} units, {total_minutes} minutes"
        )
    except Exception as e:
        logger.error(f"Error calculating looped animation price: {e}", exc_info=True)
        raise handle_exception(e, "calculating looped animation price")


@router.get("/pricing/recurring-scenes")
async def price_recurring_scenes(num_units: int, total_minutes: float):
    """Calculate price for recurring scenes generation"""
    try:
        price = credits_service.calculate_recurring_scenes_price(num_units, total_minutes)
        return create_standard_response(
            data=price,
            message=f"Recurring scenes pricing calculated for {num_units} units, {total_minutes} minutes"
        )
    except Exception as e:
        logger.error(f"Error calculating recurring scenes price: {e}", exc_info=True)
        raise handle_exception(e, "calculating recurring scenes price")


@router.get("/pricing/video")
async def price_video(duration_minutes: float):
    """Calculate price for video generation"""
    try:
        price = credits_service.calculate_video_price(duration_minutes)
        return create_standard_response(
            data=price,
            message=f"Video pricing calculated for {duration_minutes} minutes"
        )
    except Exception as e:
        logger.error(f"Error calculating video price: {e}", exc_info=True)
        raise handle_exception(e, "calculating video price")


@router.post("/pricing/calculate-budget")
async def calculate_budget(request: dict):
    """Calculate comprehensive budget for video generation based on settings"""
    try:
        video_type = request.get("video_type")
        track_count = request.get("track_count", 1)
        total_duration = request.get("total_duration", 0)  # in seconds
        track_durations = request.get("track_durations", [])  # in seconds
        reuse_video = request.get("reuse_video", False)
        
        if not video_type:
            raise HTTPException(status_code=400, detail="video_type is required")
        
        total_minutes = total_duration / 60
        longest_track_minutes = max(track_durations) / 60 if track_durations else total_minutes
        
        # Initialize units variable
        units = None
        
        # Calculate units based on video type and reuse setting
        if video_type == "looped-static":
            units = 1 if reuse_video else track_count
            has_visualizer = request.get("has_visualizer", False)
            price = credits_service.calculate_image_price(units, total_minutes, has_visualizer)
        elif video_type == "looped-animated":
            units = 1 if reuse_video else track_count
            has_visualizer = request.get("has_visualizer", False)
            price = credits_service.calculate_looped_animation_price(units, total_minutes, has_visualizer)
        elif video_type == "recurring-scenes":
            # For recurring scenes: number_of_scenes * cost_per_scene + duration * rate
            # The number of scenes is determined by the user's budget choice
            # We'll calculate based on the maximum possible scenes for the given duration
            max_scenes = math.ceil(total_minutes * 60 / 5)  # Duration in seconds / 5 seconds per scene
            has_visualizer = request.get("has_visualizer", False)
            price = credits_service.calculate_recurring_scenes_price(max_scenes, total_minutes, has_visualizer)
            units = 1  # Recurring scenes create 1 video
        elif video_type == "scenes":
            # For dynamic scenes: number_of_scenes * cost_per_scene + duration * rate
            # Duration is in minutes, so convert to seconds and divide by 5
            scenes_count = math.ceil((total_minutes * 60) / 5)  # Duration in seconds / 5 seconds per scene
            has_visualizer = request.get("has_visualizer", False)
            price = credits_service.calculate_scenes_price(scenes_count, total_minutes, has_visualizer)
            units = None  # Dynamic scenes don't use units
        else:
            raise HTTPException(status_code=400, detail=f"Invalid video_type: {video_type}")
        
        # Calculate additional metrics for scenes
        scenes_info = None
        if video_type == "scenes":
            # For dynamic scenes: calculate based on duration / 5 seconds per scene
            total_scenes = math.ceil((total_minutes * 60) / 5)  # Duration in seconds / 5 seconds per scene
            videos_to_create = 1 if reuse_video else len(track_durations) if track_durations else 1
            max_scenes_per_video = math.ceil(total_scenes / videos_to_create) if videos_to_create > 0 else 1
            
            # Cost per scene: $0.40 * 20 (credits rate) = 8 credits per scene
            cost_per_scene = 0.40 * 20  # 8 credits per scene
            
            scenes_info = {
                "total_scenes": total_scenes,
                "videos_to_create": videos_to_create,
                "max_scenes_per_video": max_scenes_per_video,
                "min_scenes_per_video": 1,
                "cost_per_scene": cost_per_scene
            }
        elif video_type == "recurring-scenes":
            # For recurring scenes: calculate based on duration / 5 seconds per scene
            total_scenes = math.ceil((total_minutes * 60) / 5)  # Duration in seconds / 5 seconds per scene
            
            # Cost per scene: $0.40 * 20 (credits rate) = 8 credits per scene
            cost_per_scene = 0.40 * 20  # 8 credits per scene
            
            scenes_info = {
                "total_scenes": total_scenes,
                "videos_to_create": 1,  # Recurring scenes create 1 video
                "max_scenes_per_video": total_scenes,
                "min_scenes_per_video": 1,
                "cost_per_scene": cost_per_scene
            }
        
        return create_standard_response(
            data={
                "price": price,
                "video_type": video_type,
                "units": units if video_type != "scenes" else None,
                "scenes_info": scenes_info,
                "reuse_video": reuse_video,
                "total_minutes": total_minutes,
                "longest_track_minutes": longest_track_minutes
            },
            message=f"Budget calculated for {video_type} video generation"
        )
    except Exception as e:
        logger.error(f"Error calculating budget: {e}", exc_info=True)
        raise handle_exception(e, "calculating budget")


# TESTING ENDPOINTS
@router.post("/test-checkout")
async def test_checkout(
    request: CheckoutRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Test checkout endpoint for development"""
    return create_standard_response(
        data={
            "message": "Test checkout working",
            "plan_id": request.plan_id,
            "plan_type": request.plan_type,
            "user_id": str(current_user.id),
            "checkout_url": "https://checkout.stripe.com/test-session",
        },
        message="Test checkout endpoint working"
    )
