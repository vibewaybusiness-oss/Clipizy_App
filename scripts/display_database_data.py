#!/usr/bin/env python3
"""
Database Data Display Script
Displays all data from PostgreSQL database tables
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

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

def get_table_names(engine):
    """Get all table names from database"""
    inspector = inspect(engine)
    return inspector.get_table_names()

def get_table_info(engine, table_name):
    """Get table structure information"""
    inspector = inspect(engine)
    columns = inspector.get_columns(table_name)
    return columns

def display_table_data(session, table_name, limit=100):
    """Display data from a specific table"""
    try:
        # Get table structure
        result = session.execute(text(f"SELECT * FROM {table_name} LIMIT {limit}"))
        rows = result.fetchall()
        
        if not rows:
            print(f"📋 Table '{table_name}' is empty")
            return
        
        # Get column names
        columns = result.keys()
        
        print(f"\n{'='*80}")
        print(f"📊 TABLE: {table_name.upper()}")
        print(f"{'='*80}")
        print(f"📈 Total rows displayed: {len(rows)}")
        print(f"📋 Columns: {', '.join(columns)}")
        print(f"{'='*80}")
        
        # Display data in a formatted way
        for i, row in enumerate(rows, 1):
            print(f"\n🔹 ROW {i}:")
            for col, value in zip(columns, row):
                # Format the value for better display
                if isinstance(value, datetime):
                    formatted_value = value.strftime("%Y-%m-%d %H:%M:%S")
                elif isinstance(value, dict):
                    formatted_value = json.dumps(value, indent=2)
                elif value is None:
                    formatted_value = "NULL"
                else:
                    formatted_value = str(value)
                
                # Truncate very long values
                if len(formatted_value) > 100:
                    formatted_value = formatted_value[:97] + "..."
                
                print(f"  {col}: {formatted_value}")
        
    except SQLAlchemyError as e:
        print(f"❌ Error reading table '{table_name}': {e}")

def display_table_summary(session, table_name):
    """Display summary information for a table"""
    try:
        # Get row count
        count_result = session.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
        row_count = count_result.scalar()
        
        # Get table structure
        result = session.execute(text(f"""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = '{table_name}'
            ORDER BY ordinal_position
        """))
        columns_info = result.fetchall()
        
        print(f"\n📋 TABLE SUMMARY: {table_name.upper()}")
        print(f"📊 Total rows: {row_count}")
        print(f"🏗️  Structure:")
        for col_info in columns_info:
            col_name, data_type, nullable, default = col_info
            nullable_str = "NULL" if nullable == "YES" else "NOT NULL"
            default_str = f" DEFAULT {default}" if default else ""
            print(f"  • {col_name}: {data_type} {nullable_str}{default_str}")
            
    except SQLAlchemyError as e:
        print(f"❌ Error getting summary for table '{table_name}': {e}")

def display_database_overview(session):
    """Display overall database information"""
    try:
        # Get database name
        db_result = session.execute(text("SELECT current_database()"))
        db_name = db_result.scalar()
        
        # Get database size
        size_result = session.execute(text("SELECT pg_size_pretty(pg_database_size(current_database()))"))
        db_size = size_result.scalar()
        
        # Get connection info
        conn_result = session.execute(text("SELECT version()"))
        version = conn_result.scalar()
        
        print(f"\n{'='*80}")
        print(f"🗄️  DATABASE OVERVIEW")
        print(f"{'='*80}")
        print(f"📊 Database: {db_name}")
        print(f"💾 Size: {db_size}")
        print(f"🔧 Version: {version}")
        print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except SQLAlchemyError as e:
        print(f"❌ Error getting database overview: {e}")

def main():
    """Main function to display database data"""
    print("🚀 Starting Database Data Display...")
    
    # Get database connection
    engine, session = get_database_connection()
    
    try:
        # Display database overview
        display_database_overview(session)
        
        # Get all table names
        table_names = get_table_names(engine)
        
        if not table_names:
            print("❌ No tables found in database")
            return
        
        print(f"\n📋 Found {len(table_names)} tables: {', '.join(table_names)}")
        
        # Display each table
        for table_name in table_names:
            # Show table summary first
            display_table_summary(session, table_name)
            
            # Ask user if they want to see the data
            response = input(f"\n❓ Do you want to see data from '{table_name}'? (y/n/s for summary only): ").lower().strip()
            
            if response == 'y':
                display_table_data(session, table_name)
            elif response == 's':
                continue  # Already showed summary
            elif response == 'n':
                continue
            else:
                print("Invalid response, skipping...")
        
        print(f"\n✅ Database data display completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    main()
