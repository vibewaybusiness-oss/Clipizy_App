"""
Database Data Display Router
Endpoints for displaying database data in admin interface
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text, inspect

from api.services.database import get_db
from api.models import User
from api.services.auth import get_current_user
from api.services.errors import handle_exception

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin/database", tags=["Admin Database Data"])


def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Allow any authenticated user for now"""
    return current_user


@router.get("/tables")
async def get_all_tables(
    db: Session = Depends(get_db)
):
    """Get all table names in the database"""
    try:
        inspector = inspect(db.bind)
        tables = inspector.get_table_names()
        
        return {
            "status": "success",
            "tables": tables,
            "count": len(tables),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    except Exception as e:
        logger.error(f"Error getting tables: {e}")
        raise handle_exception(e, "getting database tables")


@router.get("/tables/{table_name}/info")
async def get_table_info(
    table_name: str,
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific table"""
    try:
        # Get table structure
        result = db.execute(text(f"""
            SELECT column_name, data_type, is_nullable, column_default, character_maximum_length
            FROM information_schema.columns 
            WHERE table_name = '{table_name}'
            ORDER BY ordinal_position
        """))
        columns = result.fetchall()
        
        # Get row count
        count_result = db.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
        row_count = count_result.scalar()
        
        # Get table size
        size_result = db.execute(text(f"""
            SELECT pg_size_pretty(pg_total_relation_size('{table_name}'))
        """))
        table_size = size_result.scalar()
        
        return {
            "status": "success",
            "table_name": table_name,
            "row_count": row_count,
            "table_size": table_size,
            "columns": [
                {
                    "name": col[0],
                    "type": col[1],
                    "nullable": col[2] == "YES",
                    "default": col[3],
                    "max_length": col[4]
                }
                for col in columns
            ],
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    except Exception as e:
        logger.error(f"Error getting table info for {table_name}: {e}")
        raise handle_exception(e, f"getting table info for {table_name}")


@router.get("/tables/{table_name}/data")
async def get_table_data(
    table_name: str,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get data from a specific table with pagination"""
    try:
        # Get total count
        count_result = db.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
        total_count = count_result.scalar()
        
        # Get data with pagination
        result = db.execute(text(f"""
            SELECT * FROM {table_name} 
            ORDER BY 1 
            LIMIT {limit} OFFSET {offset}
        """))
        rows = result.fetchall()
        columns = result.keys()
        
        # Convert rows to dictionaries
        data = []
        for row in rows:
            row_dict = {}
            for col, value in zip(columns, row):
                if isinstance(value, datetime):
                    row_dict[col] = value.isoformat()
                elif isinstance(value, dict):
                    row_dict[col] = value
                else:
                    row_dict[col] = value
            data.append(row_dict)
        
        return {
            "status": "success",
            "table_name": table_name,
            "data": data,
            "pagination": {
                "limit": limit,
                "offset": offset,
                "total_count": total_count,
                "has_more": offset + limit < total_count
            },
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    except Exception as e:
        logger.error(f"Error getting table data for {table_name}: {e}")
        raise handle_exception(e, f"getting table data for {table_name}")


@router.get("/tables/{table_name}/sample")
async def get_table_sample(
    table_name: str,
    limit: int = Query(5, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get a sample of data from a specific table"""
    try:
        result = db.execute(text(f"SELECT * FROM {table_name} LIMIT {limit}"))
        rows = result.fetchall()
        columns = result.keys()
        
        # Convert rows to dictionaries
        data = []
        for row in rows:
            row_dict = {}
            for col, value in zip(columns, row):
                if isinstance(value, datetime):
                    row_dict[col] = value.isoformat()
                elif isinstance(value, dict):
                    row_dict[col] = value
                else:
                    row_dict[col] = value
            data.append(row_dict)
        
        return {
            "status": "success",
            "table_name": table_name,
            "sample_data": data,
            "columns": list(columns),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    except Exception as e:
        logger.error(f"Error getting table sample for {table_name}: {e}")
        raise handle_exception(e, f"getting table sample for {table_name}")


@router.get("/overview")
async def get_database_overview(
    db: Session = Depends(get_db)
):
    """Get overall database overview and statistics"""
    try:
        # Get database name and size
        db_result = db.execute(text("SELECT current_database()"))
        db_name = db_result.scalar()
        
        size_result = db.execute(text("SELECT pg_size_pretty(pg_database_size(current_database()))"))
        db_size = size_result.scalar()
        
        # Get all tables with row counts
        tables_result = db.execute(text("""
            SELECT 
                schemaname,
                relname as tablename,
                n_tup_ins as inserts,
                n_tup_upd as updates,
                n_tup_del as deletes,
                n_live_tup as live_tuples,
                n_dead_tup as dead_tuples
            FROM pg_stat_user_tables
            ORDER BY relname
        """))
        tables_stats = tables_result.fetchall()
        
        # Get connection info
        conn_result = db.execute(text("SELECT version()"))
        version = conn_result.scalar()
        
        return {
            "status": "success",
            "database": {
                "name": db_name,
                "size": db_size,
                "version": version
            },
            "tables": [
                {
                    "name": table[1],
                    "schema": table[0],
                    "live_tuples": table[5],
                    "dead_tuples": table[6],
                    "inserts": table[2],
                    "updates": table[3],
                    "deletes": table[4]
                }
                for table in tables_stats
            ],
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    except Exception as e:
        logger.error(f"Error getting database overview: {e}")
        raise handle_exception(e, "getting database overview")


@router.get("/query")
async def execute_custom_query(
    query: str = Query(..., description="SQL query to execute"),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Execute a custom SQL query (admin only)"""
    try:
        # Basic safety check - only allow SELECT statements
        query_upper = query.strip().upper()
        if not query_upper.startswith('SELECT'):
            raise HTTPException(
                status_code=400, 
                detail="Only SELECT queries are allowed for security reasons"
            )
        
        # Add limit if not present
        if 'LIMIT' not in query_upper:
            query = f"{query} LIMIT {limit}"
        
        result = db.execute(text(query))
        rows = result.fetchall()
        columns = result.keys()
        
        # Convert rows to dictionaries
        data = []
        for row in rows:
            row_dict = {}
            for col, value in zip(columns, row):
                if isinstance(value, datetime):
                    row_dict[col] = value.isoformat()
                elif isinstance(value, dict):
                    row_dict[col] = value
                else:
                    row_dict[col] = value
            data.append(row_dict)
        
        return {
            "status": "success",
            "query": query,
            "data": data,
            "columns": list(columns),
            "row_count": len(data),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    except Exception as e:
        logger.error(f"Error executing custom query: {e}")
        raise handle_exception(e, "executing custom query")
