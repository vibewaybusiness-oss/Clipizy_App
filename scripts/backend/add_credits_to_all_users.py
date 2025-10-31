#!/usr/bin/env python3
"""
Script to add 1000 credits to all users
"""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from sqlalchemy.orm import Session
from api.db import get_db, engine
from api.models import User
from api.models.pricing import CreditsTransactionType
from api.services.business.pricing_service import credits_service
from api.config.logging import get_project_logger

logger = get_project_logger()

def add_credits_to_all_users(credits_amount: int = 1000):
    """Add specified amount of credits to all users"""
    
    db = next(get_db())
    
    try:
        # Get all users
        users = db.query(User).all()
        total_users = len(users)
        
        if total_users == 0:
            print("No users found in the database.")
            return
        
        print(f"Found {total_users} users. Adding {credits_amount} credits to each...")
        
        success_count = 0
        error_count = 0
        
        for i, user in enumerate(users, 1):
            try:
                # Add credits to user
                transaction = credits_service.add_credits(
                    db=db,
                    user_id=str(user.id),
                    amount=credits_amount,
                    transaction_type=CreditsTransactionType.ADMIN_ADJUSTMENT,
                    description=f"Bulk credit addition: {credits_amount} credits added to all users",
                    reference_id=None,
                    reference_type="bulk_admin_addition",
                )
                
                success_count += 1
                print(f"[{i}/{total_users}] ✅ Added {credits_amount} credits to {user.email} (ID: {user.id})")
                
            except Exception as e:
                error_count += 1
                print(f"[{i}/{total_users}] ❌ Failed to add credits to {user.email} (ID: {user.id}): {str(e)}")
                logger.error(f"Error adding credits to user {user.id}: {str(e)}")
        
        print(f"\n📊 SUMMARY:")
        print(f"Total users processed: {total_users}")
        print(f"Successful additions: {success_count}")
        print(f"Failed additions: {error_count}")
        print(f"Credits added per user: {credits_amount}")
        print(f"Total credits distributed: {success_count * credits_amount}")
        
        if error_count > 0:
            print(f"\n⚠️  {error_count} users failed to receive credits. Check the logs for details.")
        else:
            print(f"\n🎉 Successfully added {credits_amount} credits to all {total_users} users!")
            
    except Exception as e:
        logger.error(f"Error in bulk credit addition: {str(e)}")
        print(f"❌ Script failed: {str(e)}")
        raise
    finally:
        db.close()

def main():
    """Main function"""
    print("🚀 Starting bulk credit addition script...")
    print("=" * 50)
    
    # Confirm before proceeding
    response = input("This will add 1000 credits to ALL users. Are you sure? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("❌ Operation cancelled.")
        return
    
    try:
        add_credits_to_all_users(1000)
    except Exception as e:
        print(f"❌ Script failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
