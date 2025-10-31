#!/usr/bin/env python3
"""
Fix existing user profile files to include credits information
"""
import sys
import os
import json
from pathlib import Path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy.orm import Session
from api.db import get_db
from api.models import User

def fix_existing_profile_credits():
    """Update existing profile files to include credits information"""
    try:
        db = next(get_db())
        base_users_dir = Path("users")
        
        # Get all users from database
        all_users = db.query(User).all()
        
        print(f"Found {len(all_users)} users in database")
        
        for user in all_users:
            try:
                user_id = str(user.id)
                user_dir = base_users_dir / user_id
                
                if not user_dir.exists():
                    print(f"User directory not found for {user.email}, skipping...")
                    continue
                
                # Update profile.json
                profile_file = user_dir / "profile" / "profile.json"
                if profile_file.exists():
                    with open(profile_file, 'r') as f:
                        profile_data = json.load(f)
                    
                    # Add credits information if not present
                    if "credits" not in profile_data:
                        profile_data["credits"] = {
                            "balance": user.credits_balance,
                            "total_earned": user.total_credits_earned,
                            "total_spent": user.total_credits_spent,
                            "last_updated": None
                        }
                        
                        with open(profile_file, 'w') as f:
                            json.dump(profile_data, f, indent=2)
                        
                        print(f"Updated profile.json for {user.email} with credits info")
                
                # Update billing.json
                billing_file = user_dir / "profile" / "billing" / "billing.json"
                if billing_file.exists():
                    with open(billing_file, 'r') as f:
                        billing_data = json.load(f)
                    
                    # Add credits information if not present
                    if "credits" not in billing_data:
                        billing_data["credits"] = {
                            "balance": user.credits_balance,
                            "total_earned": user.total_credits_earned,
                            "total_spent": user.total_credits_spent
                        }
                        
                        with open(billing_file, 'w') as f:
                            json.dump(billing_data, f, indent=2)
                        
                        print(f"Updated billing.json for {user.email} with credits info")
                
            except Exception as e:
                print(f"Error updating profile files for {user.email}: {str(e)}")
                continue
        
        print("Profile files update completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error updating profile files: {str(e)}")
        return False

if __name__ == "__main__":
    fix_existing_profile_credits()
