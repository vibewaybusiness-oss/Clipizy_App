#!/usr/bin/env python3
"""
Simple script to check user credits and load credits
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy.orm import Session
from api.db import get_db
from api.models import User

def check_user_credits():
    """Check user credits in database"""
    try:
        db = next(get_db())
        
        # Get all users
        all_users = db.query(User).all()
        
        print(f"Total users in database: {len(all_users)}")
        
        # Count users by credit status
        users_with_credits = db.query(User).filter(User.credits_balance > 0).count()
        users_without_credits = db.query(User).filter(User.credits_balance == 0).count()
        users_with_earned = db.query(User).filter(User.total_credits_earned > 0).count()
        users_without_earned = db.query(User).filter(User.total_credits_earned == 0).count()
        
        print(f"Users with credits balance > 0: {users_with_credits}")
        print(f"Users with credits balance = 0: {users_without_credits}")
        print(f"Users with total_credits_earned > 0: {users_with_earned}")
        print(f"Users with total_credits_earned = 0: {users_without_earned}")
        
        # Show details for all users
        print("\nAll users credit details:")
        for i, user in enumerate(all_users):
            print(f"  {i+1}. {user.email} - Balance: {user.credits_balance}, Earned: {user.total_credits_earned}, Spent: {user.total_credits_spent}")
        
        return True
        
    except Exception as e:
        print(f"Error checking credits: {str(e)}")
        return False

def load_credits_to_user(email: str, credits: int):
    """Load credits to a specific user account"""
    try:
        db = next(get_db())
        
        # Find user by email
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            print(f"User with email '{email}' not found")
            return False
        
        # Update credits
        old_balance = user.credits_balance
        user.credits_balance += credits
        user.total_credits_earned += credits
        
        # Commit changes
        db.commit()
        
        print(f"Successfully loaded {credits} credits to {email}")
        print(f"Previous balance: {old_balance}")
        print(f"New balance: {user.credits_balance}")
        print(f"Total earned: {user.total_credits_earned}")
        
        return True
        
    except Exception as e:
        print(f"Error loading credits: {str(e)}")
        db.rollback()
        return False

def load_credits_to_all_users(credits: int):
    """Load credits to all users in the database"""
    try:
        db = next(get_db())
        
        # Get all users
        all_users = db.query(User).all()
        
        if not all_users:
            print("No users found in database")
            return False
        
        updated_count = 0
        for user in all_users:
            user.credits_balance += credits
            user.total_credits_earned += credits
            updated_count += 1
        
        # Commit changes
        db.commit()
        
        print(f"Successfully loaded {credits} credits to {updated_count} users")
        
        return True
        
    except Exception as e:
        print(f"Error loading credits to all users: {str(e)}")
        db.rollback()
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Check user credits and load credits")
    parser.add_argument("--check", action="store_true", help="Check user credits")
    parser.add_argument("--load", type=int, help="Load credits to all users")
    parser.add_argument("--load-user", type=str, help="Email of user to load credits to")
    parser.add_argument("--credits", type=int, help="Number of credits to load")
    
    args = parser.parse_args()
    
    if args.check:
        check_user_credits()
    elif args.load is not None:
        load_credits_to_all_users(args.load)
    elif args.load_user and args.credits is not None:
        load_credits_to_user(args.load_user, args.credits)
    else:
        # Default behavior - just check credits
        check_user_credits()
