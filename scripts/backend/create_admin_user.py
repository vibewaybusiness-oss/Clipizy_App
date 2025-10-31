#!/usr/bin/env python3
"""
Script to create an admin user manually
"""
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.db import get_database_url
from api.models.user import User
from api.services.auth.auth_service import auth_service
from api.schemas.auth.user import UserCreate

def create_admin_user():
    """Create an admin user"""
    print("👤 Creating Admin User...")
    
    try:
        # Create database engine
        database_url = get_database_url()
        engine = create_engine(database_url, echo=False)
        
        # Create session
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        try:
            # Get admin details from user input
            print("\nEnter admin user details:")
            email = input("Email: ").strip()
            if not email:
                print("❌ Email is required")
                return False
                
            password = input("Password: ").strip()
            if not password:
                print("❌ Password is required")
                return False
                
            name = input("Name (optional): ").strip()
            if not name:
                name = email.split('@')[0]
            
            # Check if user already exists
            existing_user = db.query(User).filter(User.email == email).first()
            if existing_user:
                print(f"❌ User with email {email} already exists")
                return False
            
            # Create admin user
            admin_user_data = UserCreate(
                email=email,
                password=password,
                name=name
            )
            
            admin_user = auth_service.create_user(db, admin_user_data)
            
            # Set admin privileges
            admin_user.is_admin = True
            admin_user.is_verified = True
            db.commit()
            
            print(f"✅ Admin user created successfully!")
            print(f"   Email: {admin_user.email}")
            print(f"   Name: {admin_user.name}")
            print(f"   ID: {admin_user.id}")
            print(f"   Admin: {admin_user.is_admin}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating admin user: {str(e)}")
            db.rollback()
            return False
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔐 Clipizy Admin User Creator")
    print("=" * 40)
    
    success = create_admin_user()
    if success:
        print("\n🎉 Admin user created successfully!")
        print("You can now login with these credentials to access the admin panel.")
    else:
        print("\n💥 Failed to create admin user!")
        sys.exit(1)
