#!/usr/bin/env python3
"""
Fix User Initial Credits Script
Adds 60 initial credits to users who don't have them
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy.orm import Session
from api.db import get_db
from api.models import User
from api.services.business.pricing_service import credits_service
from api.models.pricing import CreditsTransactionType
from api.config.logging import get_project_logger

logger = get_project_logger()

def fix_user_initial_credits():
    """Add 60 initial credits to users who don't have them"""
    try:
        db = next(get_db())
        
        # Find users with 0 credits balance and 0 total earned
        users_without_credits = db.query(User).filter(
            User.credits_balance == 0,
            User.total_credits_earned == 0
        ).all()
        
        logger.info(f"Found {len(users_without_credits)} users without initial credits")
        
        for user in users_without_credits:
            try:
                # Add 60 initial credits
                credits_service.add_credits(
                    db=db,
                    user_id=str(user.id),
                    amount=60,
                    transaction_type=CreditsTransactionType.EARNED,
                    description="Welcome bonus - Initial credits for new users",
                    reference_id=None,
                    reference_type="welcome_bonus"
                )
                
                logger.info(f"Added 60 initial credits to user {user.email} (ID: {user.id})")
                
            except Exception as e:
                logger.error(f"Failed to add credits to user {user.email}: {str(e)}")
                continue
        
        # Also check users who might have some credits but no total_earned (inconsistent state)
        users_inconsistent = db.query(User).filter(
            User.credits_balance > 0,
            User.total_credits_earned == 0
        ).all()
        
        logger.info(f"Found {len(users_inconsistent)} users with inconsistent credit state")
        
        for user in users_inconsistent:
            try:
                # Update total_credits_earned to match current balance
                user.total_credits_earned = user.credits_balance
                db.commit()
                
                logger.info(f"Fixed inconsistent credit state for user {user.email} (ID: {user.id})")
                
            except Exception as e:
                logger.error(f"Failed to fix inconsistent state for user {user.email}: {str(e)}")
                db.rollback()
                continue
        
        logger.info("✅ Initial credits fix completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to fix initial credits: {str(e)}")
        return False

def check_user_credits_status():
    """Check the current status of user credits"""
    try:
        db = next(get_db())
        
        # Get all users
        all_users = db.query(User).all()
        
        logger.info(f"Total users in database: {len(all_users)}")
        
        # Count users by credit status
        users_with_credits = db.query(User).filter(User.credits_balance > 0).count()
        users_without_credits = db.query(User).filter(User.credits_balance == 0).count()
        users_with_earned = db.query(User).filter(User.total_credits_earned > 0).count()
        users_without_earned = db.query(User).filter(User.total_credits_earned == 0).count()
        
        logger.info(f"Users with credits balance > 0: {users_with_credits}")
        logger.info(f"Users with credits balance = 0: {users_without_credits}")
        logger.info(f"Users with total_credits_earned > 0: {users_with_earned}")
        logger.info(f"Users with total_credits_earned = 0: {users_without_earned}")
        
        # Show details for first few users
        logger.info("\nFirst 5 users credit details:")
        for i, user in enumerate(all_users[:5]):
            logger.info(f"  {i+1}. {user.email} - Balance: {user.credits_balance}, Earned: {user.total_credits_earned}, Spent: {user.total_credits_spent}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to check credits status: {str(e)}")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Fix user initial credits")
    parser.add_argument("--check", action="store_true", help="Check current credits status")
    parser.add_argument("--fix", action="store_true", help="Fix users without initial credits")
    
    args = parser.parse_args()
    
    if args.check:
        logger.info("🔍 Checking user credits status...")
        check_user_credits_status()
    elif args.fix:
        logger.info("🔧 Fixing user initial credits...")
        fix_user_initial_credits()
    else:
        logger.info("Usage: python fix_user_initial_credits.py --check or --fix")
        logger.info("  --check: Check current credits status")
        logger.info("  --fix: Fix users without initial credits")
