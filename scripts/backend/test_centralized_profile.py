#!/usr/bin/env python3
"""
Test script for the centralized profile service
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy.orm import Session
from api.db import get_db
from api.services.auth.centralized_profile_service import centralized_profile_service

def test_centralized_profile_creation():
    """Test the centralized profile creation service"""
    try:
        db = next(get_db())
        
        # Test email user creation
        test_email = "test@example.com"
        test_name = "Test User"
        test_password = "testpassword123"
        
        print(f"Testing centralized profile creation for: {test_email}")
        
        # Create user
        user = centralized_profile_service.create_complete_user_profile(
            db=db,
            email=test_email,
            name=test_name,
            password=test_password,
            oauth_provider=None
        )
        
        print(f"✅ User created successfully:")
        print(f"   - ID: {user.id}")
        print(f"   - Email: {user.email}")
        print(f"   - Username: {user.username}")
        print(f"   - Credits Balance: {user.credits_balance}")
        print(f"   - Total Credits Earned: {user.total_credits_earned}")
        print(f"   - Total Credits Spent: {user.total_credits_spent}")
        
        # Check if profile files were created
        from pathlib import Path
        user_dir = Path("users") / str(user.id)
        profile_file = user_dir / "profile" / "profile.json"
        billing_file = user_dir / "profile" / "billing" / "billing.json"
        
        if profile_file.exists():
            print(f"✅ Profile file created: {profile_file}")
            with open(profile_file, 'r') as f:
                profile_data = json.load(f)
                if "credits" in profile_data:
                    print(f"   - Profile credits: {profile_data['credits']}")
                else:
                    print("   - ❌ Credits not found in profile file")
        else:
            print(f"❌ Profile file not created: {profile_file}")
        
        if billing_file.exists():
            print(f"✅ Billing file created: {billing_file}")
            with open(billing_file, 'r') as f:
                billing_data = json.load(f)
                if "credits" in billing_data:
                    print(f"   - Billing credits: {billing_data['credits']}")
                else:
                    print("   - ❌ Credits not found in billing file")
        else:
            print(f"❌ Billing file not created: {billing_file}")
        
        # Clean up test user
        db.delete(user)
        db.commit()
        print("✅ Test user cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    import json
    test_centralized_profile_creation()
