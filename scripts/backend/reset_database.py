#!/usr/bin/env python3
"""
Database reset script for Clipizy
Drops all tables and enums, then recreates them
"""
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text
from api.db import get_database_url

def reset_database():
    """Reset the database by dropping all tables and enums"""
    print("🔄 Resetting Clipizy database...")
    
    try:
        # Create database engine
        database_url = get_database_url()
        engine = create_engine(database_url, echo=False)
        
        with engine.connect() as connection:
            # Start transaction
            trans = connection.begin()
            
            try:
                print("🗑️  Dropping existing tables...")
                
                # Drop all tables first
                connection.execute(text("DROP SCHEMA public CASCADE"))
                connection.execute(text("CREATE SCHEMA public"))
                connection.execute(text("GRANT ALL ON SCHEMA public TO postgres"))
                connection.execute(text("GRANT ALL ON SCHEMA public TO public"))
                
                print("✅ Database reset successfully")
                
                # Commit the transaction
                trans.commit()
                
                return True
                
            except Exception as e:
                print(f"❌ Error during database reset: {str(e)}")
                trans.rollback()
                return False
                
    except Exception as e:
        print(f"❌ Database reset failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = reset_database()
    if success:
        print("✅ Database reset completed successfully")
        print("ℹ️  Run init_database.py to recreate tables")
    else:
        print("❌ Database reset failed")
        sys.exit(1)

