"""
Credits Management Service
Handles user credits balance, transactions, spending, and pricing calculations
"""

import math
import uuid
import json
import os
from typing import Dict, List, Optional

from fastapi import HTTPException
from sqlalchemy import desc
from sqlalchemy.orm import Session

from api.config.logging import get_project_logger
from api.models import CreditsTransaction, User
from api.models.pricing import CreditsTransactionType
from api.services.database import QueryOptimizer
from api.services.errors import ResourceErrors, handle_exception
from api.schemas import (
    CreditsBalance,
    PaymentIntentCreate,
    CreditsSpendRequest,
    CreditsTransactionCreate,
    CreditsTransactionRead,
)

logger = get_project_logger()

def load_pricing_config() -> Dict:
    """Load pricing configuration from external JSON file"""
    try:
        config_path = os.path.join(os.path.dirname(__file__), 'pricing_config.json')
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning("Pricing config file not found, using default pricing")
        return get_default_pricing()
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in pricing config: {e}")
        return get_default_pricing()
    except Exception as e:
        logger.error(f"Error loading pricing config: {e}")
        return get_default_pricing()

def get_default_pricing() -> Dict:
    """Fallback default pricing configuration"""
    return {
        "credits_rate": 20,
        "pricing": {
            "music_generator": {
                "stable-audio": {"price": 0.5, "description": "Generate a music track based on the description."},
                "clipizy-model": {"price": 1.0, "description": "Generate a music track based on the description."},
            },
            "image_generator": {
                "clipizy-model": {
                    "minute_rate": 0.10,
                    "unit_rate": 0.50,
                    "min": 3,
                    "max": None,
                    "description": "Generate an image based on the description.",
                }
            },
            "looped_animation_generator": {
                "clipizy-model": {
                    "minute_rate": 0.11,
                    "unit_rate": 1,
                    "min": 3,
                    "max": None,
                    "description": "Generate a looping animation based on the description.",
                }
            },
            "recurring_scenes_generator": {
                "clipizy-model": {
                    "minute_rate": 0.15,
                    "unit_rate": 1.5,
                    "min": 5,
                    "max": None,
                    "description": "Generate recurring scenes that repeat throughout the video.",
                }
            },
            "video_generator": {
                "clipizy-model": {
                    "minute_rate": 0.15,
                    "min": 5,
                    "max": None,
                    "description": "Generate a video based on the description.",
                }
            },
            "scenes_generator": {
                "clipizy-model": {
                    "cost_per_scene": 0.40,
                    "duration_rate": 0.15,
                    "duration_rate_with_visualizer": 0.30,
                    "description": "Generate scenes based on number of scenes and duration."
                }
            },
            "visualizer": {
                "duration_rate_additional": 0.30,
                "description": "Additional cost per minute when visualizer is enabled."
            }
        },
        "subscription_plans": {
            "basic": {
                "name": "Basic Plan",
                "price": 9.99,
                "credits_per_month": 1000,
                "stripe_price_id": "price_basic_plan"
            },
            "pro": {
                "name": "Pro Plan", 
                "price": 19.99,
                "credits_per_month": 2500,
                "stripe_price_id": "price_pro_plan"
            },
            "enterprise": {
                "name": "Enterprise Plan",
                "price": 49.99,
                "credits_per_month": 7500,
                "stripe_price_id": "price_enterprise_plan"
            }
        },
        "credits_packages": {
            "small": {
                "name": "Small Package",
                "price": 4.99,
                "credits": 500,
                "stripe_price_id": "price_small_package"
            },
            "medium": {
                "name": "Medium Package",
                "price": 9.99,
                "credits": 1200,
                "stripe_price_id": "price_medium_package"
            },
            "large": {
                "name": "Large Package",
                "price": 19.99,
                "credits": 2800,
                "stripe_price_id": "price_large_package"
            },
            "xlarge": {
                "name": "Extra Large Package",
                "price": 39.99,
                "credits": 6000,
                "stripe_price_id": "price_xlarge_package"
            }
        }
    }

# Load pricing configuration
PRICING_CONFIG = load_pricing_config()
PRICES = PRICING_CONFIG["pricing"]
CREDITS_RATE = PRICING_CONFIG["credits_rate"]


class CreditsService:
    def __init__(self):
        logger.info("CreditsService initialized")

    def get_user_balance(self, db: Session, user_id: str) -> CreditsBalance:
        """Get user's current credits balance and recent transactions using optimized queries"""
        try:
            # Use optimized query to get user and recent transactions
            user, recent_transactions = QueryOptimizer.get_user_credits_with_transactions(db, user_id, limit=10)
            if not user:
                logger.warning(f"User {user_id} not found")
                raise ResourceErrors.user_not_found(user_id)

            # Convert ORM objects to Pydantic models
            converted_transactions = [
                CreditsTransactionRead.model_validate(
                    {
                        "id": str(transaction.id),
                        "user_id": str(transaction.user_id),
                        "transaction_type": transaction.transaction_type,
                        "amount": transaction.amount,
                        "balance_after": transaction.balance_after,
                        "description": transaction.description,
                        "reference_id": transaction.reference_id,
                        "reference_type": transaction.reference_type,
                        "created_at": transaction.created_at,
                    }
                )
                for transaction in recent_transactions
            ]

            return CreditsBalance(
                current_balance=user.credits_balance,
                total_earned=user.total_credits_earned,
                total_spent=user.total_credits_spent,
                recent_transactions=converted_transactions,
            )

        except Exception as e:
            logger.error(f"Error getting user balance for {user_id}: {str(e)}")
            raise

    def add_credits(
        self,
        db: Session,
        user_id: str,
        amount: int,
        transaction_type: CreditsTransactionType,
        description: str = None,
        reference_id: str = None,
        reference_type: str = None,
    ) -> CreditsTransaction:
        """Add credits to user's account"""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ValueError(f"User {user_id} not found")

            if amount <= 0:
                raise ValueError("Amount must be positive")

            # Update user's balance
            new_balance = user.credits_balance + amount
            user.credits_balance = new_balance
            user.total_credits_earned += amount

            # Create transaction record
            transaction = CreditsTransaction(
                id=str(uuid.uuid4()),
                user_id=user_id,
                transaction_type=transaction_type,
                amount=amount,
                balance_after=new_balance,
                description=description,
                reference_id=reference_id,
                reference_type=reference_type,
            )

            db.add(transaction)
            db.commit()
            db.refresh(transaction)

            logger.info(f"Added {amount} credits to user {user_id}. New balance: {new_balance}")
            return transaction

        except Exception as e:
            logger.error(f"Error adding credits for user {user_id}: {str(e)}")
            db.rollback()
            raise

    def spend_credits(self, db: Session, user_id: str, spend_request: CreditsSpendRequest) -> CreditsTransaction:
        """Spend credits from user's account"""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ValueError(f"User {user_id} not found")

            if spend_request.amount <= 0:
                raise ValueError("Amount must be positive")

            if user.credits_balance < spend_request.amount:
                raise ValueError(
                    f"Insufficient credits. Current balance: {user.credits_balance}, Required: {spend_request.amount}"
                )

            # Update user's balance
            new_balance = user.credits_balance - spend_request.amount
            user.credits_balance = new_balance
            user.total_credits_spent += spend_request.amount

            # Create transaction record
            transaction = CreditsTransaction(
                id=str(uuid.uuid4()),
                user_id=user_id,
                transaction_type=CreditsTransactionType.SPENT,
                amount=-spend_request.amount,  # Negative for spending
                balance_after=new_balance,
                description=spend_request.description,
                reference_id=spend_request.reference_id,
                reference_type=spend_request.reference_type,
            )

            db.add(transaction)
            db.commit()
            db.refresh(transaction)

            logger.info(f"Spent {spend_request.amount} credits from user {user_id}. New balance: {new_balance}")
            return transaction

        except Exception as e:
            logger.error(f"Error spending credits for user {user_id}: {str(e)}")
            db.rollback()
            raise

    def get_transaction_history(self, db: Session, user_id: str, limit: int = 50) -> List[CreditsTransactionRead]:
        """Get user's transaction history"""
        try:
            transactions = (
                db.query(CreditsTransaction)
                .filter(CreditsTransaction.user_id == user_id)
                .order_by(desc(CreditsTransaction.created_at))
                .limit(limit)
                .all()
            )

            # Convert ORM objects to Pydantic models
            return [
                CreditsTransactionRead.model_validate(
                    {
                        "id": str(transaction.id),
                        "user_id": str(transaction.user_id),
                        "transaction_type": transaction.transaction_type,
                        "amount": transaction.amount,
                        "balance_after": transaction.balance_after,
                        "description": transaction.description,
                        "reference_id": transaction.reference_id,
                        "reference_type": transaction.reference_type,
                        "created_at": transaction.created_at,
                    }
                )
                for transaction in transactions
            ]

        except Exception as e:
            logger.error(f"Error getting transaction history for user {user_id}: {str(e)}")
            raise

    def can_afford(self, db: Session, user_id: str, amount: int) -> bool:
        """Check if user can afford to spend the specified amount of credits"""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return False
            return user.credits_balance >= amount

        except Exception as e:
            logger.error(f"Error checking affordability for user {user_id}: {str(e)}")
            return False

    async def check_user_credits(self, user_id: str, amount: int) -> bool:
        """Async wrapper for can_afford method"""
        from api.services.database import get_db

        db = next(get_db())
        return self.can_afford(db, user_id, amount)

    def refund_credits(
        self, db: Session, user_id: str, amount: int, description: str = None, reference_id: str = None
    ) -> CreditsTransaction:
        """Refund credits to user's account"""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ValueError(f"User {user_id} not found")

            if amount <= 0:
                raise ValueError("Amount must be positive")

            # Update user's balance
            new_balance = user.credits_balance + amount
            user.credits_balance = new_balance
            user.total_credits_earned += amount  # Refunds count as earned

            # Create transaction record
            transaction = CreditsTransaction(
                user_id=user_id,
                transaction_type=CreditsTransactionType.REFUNDED,
                amount=amount,
                balance_after=new_balance,
                description=description or "Credits refund",
                reference_id=reference_id,
                reference_type="refund",
            )

            db.add(transaction)
            db.commit()
            db.refresh(transaction)

            logger.info(f"Refunded {amount} credits to user {user_id}. New balance: {new_balance}")
            return transaction

        except Exception as e:
            logger.error(f"Error refunding credits for user {user_id}: {str(e)}")
            db.rollback()
            raise

    # PRICING METHODS
    def to_credits(self, dollars: float) -> int:
        """Convert $ to credits using global rate."""
        return math.ceil(dollars * CREDITS_RATE)

    def calculate_music_price(self, num_tracks: int, model: str = "clipizy-model") -> Dict:
        """Calculate price for music generation"""
        price = num_tracks * PRICES["music_generator"][model]["price"]
        return {"usd": round(price, 2), "credits": self.to_credits(price)}

    def calculate_image_price(self, num_units: int, total_minutes: float, has_visualizer: bool = False) -> Dict:
        """Calculate price for image generation"""
        base = (num_units * PRICES["image_generator"]["clipizy-model"]["unit_rate"]) + (
            total_minutes * PRICES["image_generator"]["clipizy-model"]["minute_rate"]
        )
        # Add visualizer duration rate if enabled
        if has_visualizer:
            base += total_minutes * PRICES["visualizer"]["duration_rate_additional"]
        
        price = max(base, PRICES["image_generator"]["clipizy-model"]["min"])
        return {"usd": round(price, 2), "credits": self.to_credits(price)}

    def calculate_looped_animation_price(self, num_units: int, total_minutes: float, has_visualizer: bool = False) -> Dict:
        """Calculate price for looped animation generation"""
        base = (num_units * PRICES["looped_animation_generator"]["clipizy-model"]["unit_rate"]) + (
            total_minutes * PRICES["looped_animation_generator"]["clipizy-model"]["minute_rate"]
        )
        # Add visualizer duration rate if enabled
        if has_visualizer:
            base += total_minutes * PRICES["visualizer"]["duration_rate_additional"]
        
        price = max(base, PRICES["looped_animation_generator"]["clipizy-model"]["min"])
        if PRICES["looped_animation_generator"]["clipizy-model"]["max"]:
            price = min(price, PRICES["looped_animation_generator"]["clipizy-model"]["max"])
        return {"usd": round(price, 2), "credits": self.to_credits(price)}

    def calculate_recurring_scenes_price(self, number_of_scenes: int, duration_minutes: float, has_visualizer: bool = False) -> Dict:
        """Calculate price for recurring scenes generation based on number of scenes and duration"""
        # Use the same calculation as scenes: scenes * cost + duration * rate
        return self.calculate_scenes_price(number_of_scenes, duration_minutes, has_visualizer)

    def calculate_video_price(self, duration_minutes: float) -> Dict:
        """Calculate price for video generation"""
        base = duration_minutes * PRICES["video_generator"]["clipizy-model"]["minute_rate"]
        price = max(base, PRICES["video_generator"]["clipizy-model"]["min"])
        return {"usd": round(price, 2), "credits": self.to_credits(price)}

    def calculate_scenes_price(self, number_of_scenes: int, duration_minutes: float = 0, has_visualizer: bool = False) -> Dict:
        """Calculate price for scenes generation based on number of scenes and duration"""
        # Get pricing from config
        scenes_config = PRICES["scenes_generator"]["clipizy-model"]
        cost_per_scene = scenes_config["cost_per_scene"]
        
        # Duration rate: use visualizer rate if enabled, otherwise standard rate
        duration_rate = scenes_config["duration_rate_with_visualizer"] if has_visualizer else scenes_config["duration_rate"]
        
        # Calculate: number_of_scenes * cost_per_scene + duration_minutes * duration_rate
        price_usd = (number_of_scenes * cost_per_scene) + (duration_minutes * duration_rate)
        
        return {"usd": round(price_usd, 2), "credits": self.to_credits(price_usd)}

    def get_pricing_info(self) -> Dict:
        """Get current pricing configuration"""
        return PRICING_CONFIG.copy()

    def get_subscription_plans(self) -> Dict:
        """Get subscription plans with Stripe price IDs"""
        return PRICING_CONFIG["subscription_plans"].copy()

    def get_credits_packages(self) -> Dict:
        """Get credits packages with Stripe price IDs"""
        return PRICING_CONFIG["credits_packages"].copy()

    def get_stripe_price_id(self, plan_type: str, plan_id: str) -> str:
        """Get Stripe price ID for a specific plan"""
        if plan_type == "subscription":
            return PRICING_CONFIG["subscription_plans"].get(plan_id, {}).get("stripe_price_id")
        elif plan_type == "credits":
            return PRICING_CONFIG["credits_packages"].get(plan_id, {}).get("stripe_price_id")
        return None

    def validate_spend_request(self, amount: int) -> None:
        """Validate spend request"""
        if amount <= 0:
            raise ValidationErrors.invalid_amount("Credit spend amount must be positive")

    def validate_affordability_request(self, amount: int) -> None:
        """Validate affordability check request"""
        if amount <= 0:
            raise ValidationErrors.invalid_amount("Amount must be positive")

    def validate_purchase_request(self, amount_dollars: float) -> None:
        """Validate purchase request"""
        if amount_dollars <= 0:
            raise ValidationErrors.invalid_amount("Purchase amount must be positive")

    def validate_checkout_request(self, plan_id: str, plan_type: str) -> None:
        """Validate checkout request"""
        if not plan_id or not plan_type:
            raise ValidationErrors.missing_required_fields(["plan_id", "plan_type"])

    def check_affordability_with_balance(self, db: Session, user_id: str, amount: int) -> dict:
        """Check affordability and return detailed response"""
        self.validate_affordability_request(amount)
        
        can_afford = self.can_afford(db, user_id, amount)
        current_balance = self.get_user_balance(db, user_id).current_balance
        
        return {
            "can_afford": can_afford,
            "amount_requested": amount,
            "current_balance": current_balance,
        }

    def spend_credits_with_validation(self, db: Session, user_id: str, spend_request: CreditsSpendRequest) -> dict:
        """Spend credits with full validation and response formatting"""
        self.validate_spend_request(spend_request.amount)
        
        if not self.can_afford(db, user_id, spend_request.amount):
            raise ValidationErrors.insufficient_credits()

        transaction = self.spend_credits(db, user_id, spend_request)
        
        return {
            "message": f"Successfully spent {spend_request.amount} credits",
            "transaction_id": str(transaction.id),
            "new_balance": transaction.balance_after,
        }

    def create_payment_intent_data(self, purchase_request) -> PaymentIntentCreate:
        """Create payment intent data with proper validation"""
        self.validate_purchase_request(purchase_request.amount_dollars)
        
        return PaymentIntentCreate(
            amount_dollars=purchase_request.amount_dollars,
            credits_per_dollar=PRICES["credits_rate"],
            payment_method_id=purchase_request.payment_method_id,
            description=f"Purchase of {int(purchase_request.amount_dollars * PRICES['credits_rate'])} credits",
        )

    def create_checkout_request(self, plan_id: str, plan_type: str):
        """Create checkout request with validation"""
        self.validate_checkout_request(plan_id, plan_type)
        
        # Return a simple dict for now since CheckoutSessionRequest is not available
        return {
            "plan_id": plan_id,
            "plan_type": plan_type
        }


# Create a default instance
credits_service = CreditsService()
