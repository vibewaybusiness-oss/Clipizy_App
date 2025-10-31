#!/usr/bin/env python3
"""
Quick Database View Script
Simple script to quickly view database data without interactive prompts
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def get_database_connection():
    """Get database connection"""
    database_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/clipizy")
    
    try:
        engine = create_engine(database_url)
        Session = sessionmaker(bind=engine)
        return engine, Session()
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        sys.exit(1)

def quick_view_table(session, table_name, limit=10):
    """Quick view of table data"""
    try:
        result = session.execute(text(f"SELECT * FROM {table_name} LIMIT {limit}"))
        rows = result.fetchall()
        columns = result.keys()
        
        print(f"\n📊 {table_name.upper()} (showing {len(rows)} rows)")
        print("-" * 60)
        
        if not rows:
            print("  (empty table)")
            return
        
        # Display as simple table
        for i, row in enumerate(rows, 1):
            print(f"\nRow {i}:")
            for col, value in zip(columns, row):
                if isinstance(value, datetime):
                    value = value.strftime("%Y-%m-%d %H:%M")
                elif isinstance(value, dict):
                    value = json.dumps(value, indent=2)[:50] + "..."
                elif value is None:
                    value = "NULL"
                else:
                    value = str(value)[:50]
                
                print(f"  {col}: {value}")
        
    except Exception as e:
        print(f"❌ Error reading {table_name}: {e}")

def main():
    """Quick database view"""
    print("🔍 Quick Database View")
    
    engine, session = get_database_connection()
    
    try:
        # Get all tables
        result = session.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """))
        tables = [row[0] for row in result.fetchall()]
        
        print(f"📋 Found {len(tables)} tables: {', '.join(tables)}")
        
        # Show each table
        for table in tables:
            quick_view_table(session, table)
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    main()
