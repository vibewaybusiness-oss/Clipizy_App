#!/usr/bin/env python3
"""
Database initialization script for Clipizy
Creates tables and default user
"""
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from api.db import Base, get_database_url
# Import all models to ensure they're registered with SQLAlchemy
from api.models import *

def init_database():
    """Initialize the database with tables"""
    print("🔄 Initializing Clipizy database...")
    
    try:
        # Create database engine
        database_url = get_database_url()
        engine = create_engine(database_url, echo=False)
        
        # Check if enums already exist and handle them
        with engine.connect() as connection:
            try:
                # Check if jobtype enum exists
                result = connection.execute(text("""
                    SELECT 1 FROM pg_type WHERE typname = 'jobtype' AND typnamespace = (
                        SELECT oid FROM pg_namespace WHERE nspname = 'public'
                    )
                """))
                
                if result.fetchone():
                    print("⚠️  jobtype enum already exists, dropping it...")
                    connection.execute(text("DROP TYPE IF EXISTS jobtype CASCADE"))
                
                # Check if jobstatus enum exists
                result = connection.execute(text("""
                    SELECT 1 FROM pg_type WHERE typname = 'jobstatus' AND typnamespace = (
                        SELECT oid FROM pg_namespace WHERE nspname = 'public'
                    )
                """))
                
                if result.fetchone():
                    print("⚠️  jobstatus enum already exists, dropping it...")
                    connection.execute(text("DROP TYPE IF EXISTS jobstatus CASCADE"))
                    
            except Exception as e:
                print(f"⚠️  Warning: Could not check/drop existing enums: {e}")
                # Continue anyway - the table creation might still work
        
        # Create all tables
        print("📋 Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Tables created successfully")
        
        print("📊 Database initialized successfully")
        print("ℹ️  No default users created - users must register through the application")
        
        return True
            
    except Exception as e:
        print(f"❌ Database initialization failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = init_database()
    if success:
        print("🎉 Database initialization completed successfully!")
        print("\n📝 Next steps:")
        print("1. Start the API server: python scripts/backend/start.py")
        print("2. Start the frontend: npm run dev")
        print("3. Register a new user at http://localhost:3000/auth/register")
        print("4. To create an admin user: python scripts/backend/create_admin_user.py")
    else:
        print("💥 Database initialization failed!")
        sys.exit(1)
