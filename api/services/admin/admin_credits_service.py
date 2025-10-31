"""
ADMIN CREDITS SERVICE
Business logic for admin credits management
"""

import logging
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from api.models import User
from api.models.pricing import CreditsTransactionType
from api.services.business.pricing_service import credits_service
from api.services.errors import ValidationErrors, ResourceErrors

logger = logging.getLogger(__name__)


class AdminCreditsService:
    @staticmethod
    def add_credits_to_user(
        db: Session,
        user_id: str,
        amount: int,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Add credits to a user (admin operation)
        
        Args:
            db: Database session
            user_id: Target user ID
            amount: Credits amount to add
            description: Optional description for the transaction
            
        Returns:
            Dict containing transaction details and new balance
        """
        if amount <= 0:
            raise ValidationErrors.invalid_amount("Credit amount must be positive")

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ResourceErrors.user_not_found(user_id)

        transaction = credits_service.add_credits(
            db=db,
            user_id=str(user.id),
            amount=amount,
            transaction_type=CreditsTransactionType.ADMIN_ADJUSTMENT,
            description=description or f"Admin credit addition: {amount} credits",
            reference_id=None,
            reference_type="admin_addition",
        )

        return {
            "message": f"Successfully added {amount} credits to {user.email}",
            "new_balance": user.credits_balance,
            "transaction_id": str(transaction.id),
            "user_email": user.email,
            "user_id": str(user.id)
        }

    @staticmethod
    def get_user_credits_info(db: Session, user_id: str) -> Dict[str, Any]:
        """
        Get detailed credits information for a user
        
        Args:
            db: Database session
            user_id: Target user ID
            
        Returns:
            Dict containing user credits information
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ResourceErrors.user_not_found(user_id)

        balance_info = credits_service.get_user_balance(db, str(user.id))

        return {
            "user_email": user.email,
            "user_id": str(user.id),
            "balance_info": balance_info
        }
