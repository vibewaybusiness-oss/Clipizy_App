#!/usr/bin/env python3
"""
DATABASE INDEXING STRATEGY
Comprehensive database indexing strategy for performance optimization
"""
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import asyncio

from sqlalchemy import text, Index, func
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)


class IndexType(Enum):
    """Types of database indexes"""
    PRIMARY = "primary"
    UNIQUE = "unique"
    B_TREE = "btree"
    HASH = "hash"
    GIN = "gin"
    GIST = "gist"
    BRIN = "brin"
    PARTIAL = "partial"
    COMPOSITE = "composite"


@dataclass
class IndexDefinition:
    """Definition of a database index"""
    name: str
    table: str
    columns: List[str]
    index_type: IndexType
    unique: bool = False
    partial_condition: Optional[str] = None
    include_columns: Optional[List[str]] = None
    fillfactor: Optional[int] = None
    concurrent: bool = True
    description: str = ""


@dataclass
class IndexPerformanceMetrics:
    """Performance metrics for database indexes"""
    index_name: str
    table_name: str
    index_size_bytes: int
    index_usage_count: int
    index_scan_count: int
    index_tup_read: int
    index_tup_fetch: int
    last_used: Optional[str] = None


class DatabaseIndexingStrategy:
    """Comprehensive database indexing strategy"""
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.index_definitions: List[IndexDefinition] = []
        self.performance_metrics: Dict[str, IndexPerformanceMetrics] = {}
    
    def define_core_indexes(self) -> List[IndexDefinition]:
        """Define core indexes for all tables"""
        indexes = []
        
        # User table indexes
        indexes.extend([
            IndexDefinition(
                name="idx_users_email",
                table="users",
                columns=["email"],
                index_type=IndexType.UNIQUE,
                unique=True,
                description="Unique index on user email for authentication"
            ),
            IndexDefinition(
                name="idx_users_created_at",
                table="users",
                columns=["created_at"],
                index_type=IndexType.B_TREE,
                description="Index on user creation date for analytics"
            ),
            IndexDefinition(
                name="idx_users_is_active",
                table="users",
                columns=["is_active"],
                index_type=IndexType.B_TREE,
                description="Index on active users for filtering"
            ),
            IndexDefinition(
                name="idx_users_plan",
                table="users",
                columns=["plan"],
                index_type=IndexType.B_TREE,
                description="Index on user plan for billing queries"
            ),
            IndexDefinition(
                name="idx_users_last_login",
                table="users",
                columns=["last_login"],
                index_type=IndexType.B_TREE,
                description="Index on last login for user activity tracking"
            ),
            IndexDefinition(
                name="idx_users_credits_balance",
                table="users",
                columns=["credits_balance"],
                index_type=IndexType.B_TREE,
                description="Index on credits balance for billing queries"
            )
        ])
        
        # Project table indexes
        indexes.extend([
            IndexDefinition(
                name="idx_projects_user_id",
                table="projects",
                columns=["user_id"],
                index_type=IndexType.B_TREE,
                description="Foreign key index for user projects"
            ),
            IndexDefinition(
                name="idx_projects_status",
                table="projects",
                columns=["status"],
                index_type=IndexType.B_TREE,
                description="Index on project status for filtering"
            ),
            IndexDefinition(
                name="idx_projects_type",
                table="projects",
                columns=["type"],
                index_type=IndexType.B_TREE,
                description="Index on project type for categorization"
            ),
            IndexDefinition(
                name="idx_projects_created_at",
                table="projects",
                columns=["created_at"],
                index_type=IndexType.B_TREE,
                description="Index on project creation date"
            ),
            IndexDefinition(
                name="idx_projects_user_status",
                table="projects",
                columns=["user_id", "status"],
                index_type=IndexType.COMPOSITE,
                description="Composite index for user projects by status"
            ),
            IndexDefinition(
                name="idx_projects_user_type",
                table="projects",
                columns=["user_id", "type"],
                index_type=IndexType.COMPOSITE,
                description="Composite index for user projects by type"
            ),
            IndexDefinition(
                name="idx_projects_updated_at",
                table="projects",
                columns=["updated_at"],
                index_type=IndexType.B_TREE,
                description="Index on project update date for recent activity"
            )
        ])
        
        # Job table indexes
        indexes.extend([
            IndexDefinition(
                name="idx_jobs_user_id",
                table="jobs",
                columns=["user_id"],
                index_type=IndexType.B_TREE,
                description="Foreign key index for user jobs"
            ),
            IndexDefinition(
                name="idx_jobs_project_id",
                table="jobs",
                columns=["project_id"],
                index_type=IndexType.B_TREE,
                description="Foreign key index for project jobs"
            ),
            IndexDefinition(
                name="idx_jobs_status",
                table="jobs",
                columns=["status"],
                index_type=IndexType.B_TREE,
                description="Index on job status for monitoring"
            ),
            IndexDefinition(
                name="idx_jobs_type",
                table="jobs",
                columns=["type"],
                index_type=IndexType.B_TREE,
                description="Index on job type for categorization"
            ),
            IndexDefinition(
                name="idx_jobs_created_at",
                table="jobs",
                columns=["created_at"],
                index_type=IndexType.B_TREE,
                description="Index on job creation date"
            ),
            IndexDefinition(
                name="idx_jobs_updated_at",
                table="jobs",
                columns=["updated_at"],
                index_type=IndexType.B_TREE,
                description="Index on job update date"
            ),
            IndexDefinition(
                name="idx_jobs_user_status",
                table="jobs",
                columns=["user_id", "status"],
                index_type=IndexType.COMPOSITE,
                description="Composite index for user jobs by status"
            ),
            IndexDefinition(
                name="idx_jobs_project_status",
                table="jobs",
                columns=["project_id", "status"],
                index_type=IndexType.COMPOSITE,
                description="Composite index for project jobs by status"
            ),
            IndexDefinition(
                name="idx_jobs_priority",
                table="jobs",
                columns=["priority"],
                index_type=IndexType.B_TREE,
                description="Index on job priority for scheduling"
            )
        ])
        
        # Audio table indexes
        indexes.extend([
            IndexDefinition(
                name="idx_audio_project_id",
                table="audio",
                columns=["project_id"],
                index_type=IndexType.B_TREE,
                description="Foreign key index for project audio files"
            ),
            IndexDefinition(
                name="idx_audio_type",
                table="audio",
                columns=["type"],
                index_type=IndexType.B_TREE,
                description="Index on audio type for filtering"
            ),
            IndexDefinition(
                name="idx_audio_created_at",
                table="audio",
                columns=["created_at"],
                index_type=IndexType.B_TREE,
                description="Index on audio creation date"
            ),
            IndexDefinition(
                name="idx_audio_duration",
                table="audio",
                columns=["duration"],
                index_type=IndexType.B_TREE,
                description="Index on audio duration for filtering"
            )
        ])
        
        # Video table indexes
        indexes.extend([
            IndexDefinition(
                name="idx_video_project_id",
                table="video",
                columns=["project_id"],
                index_type=IndexType.B_TREE,
                description="Foreign key index for project video files"
            ),
            IndexDefinition(
                name="idx_video_type",
                table="video",
                columns=["type"],
                index_type=IndexType.B_TREE,
                description="Index on video type for filtering"
            ),
            IndexDefinition(
                name="idx_video_created_at",
                table="video",
                columns=["created_at"],
                index_type=IndexType.B_TREE,
                description="Index on video creation date"
            ),
            IndexDefinition(
                name="idx_video_duration",
                table="video",
                columns=["duration"],
                index_type=IndexType.B_TREE,
                description="Index on video duration for filtering"
            ),
            IndexDefinition(
                name="idx_video_resolution",
                table="video",
                columns=["resolution"],
                index_type=IndexType.B_TREE,
                description="Index on video resolution for filtering"
            )
        ])
        
        # Track table indexes
        indexes.extend([
            IndexDefinition(
                name="idx_track_project_id",
                table="track",
                columns=["project_id"],
                index_type=IndexType.B_TREE,
                description="Foreign key index for project tracks"
            ),
            IndexDefinition(
                name="idx_track_created_at",
                table="track",
                columns=["created_at"],
                index_type=IndexType.B_TREE,
                description="Index on track creation date"
            ),
            IndexDefinition(
                name="idx_track_duration",
                table="track",
                columns=["duration"],
                index_type=IndexType.B_TREE,
                description="Index on track duration for filtering"
            ),
            IndexDefinition(
                name="idx_track_bpm",
                table="track",
                columns=["bpm"],
                index_type=IndexType.B_TREE,
                description="Index on track BPM for filtering"
            ),
            IndexDefinition(
                name="idx_track_genre",
                table="track",
                columns=["genre"],
                index_type=IndexType.B_TREE,
                description="Index on track genre for filtering"
            )
        ])
        
        # Payment and credits indexes
        indexes.extend([
            IndexDefinition(
                name="idx_payments_user_id",
                table="payments",
                columns=["user_id"],
                index_type=IndexType.B_TREE,
                description="Foreign key index for user payments"
            ),
            IndexDefinition(
                name="idx_payments_status",
                table="payments",
                columns=["status"],
                index_type=IndexType.B_TREE,
                description="Index on payment status"
            ),
            IndexDefinition(
                name="idx_payments_created_at",
                table="payments",
                columns=["created_at"],
                index_type=IndexType.B_TREE,
                description="Index on payment creation date"
            ),
            IndexDefinition(
                name="idx_credits_transactions_user_id",
                table="credits_transactions",
                columns=["user_id"],
                index_type=IndexType.B_TREE,
                description="Foreign key index for user credit transactions"
            ),
            IndexDefinition(
                name="idx_credits_transactions_type",
                table="credits_transactions",
                columns=["type"],
                index_type=IndexType.B_TREE,
                description="Index on credit transaction type"
            ),
            IndexDefinition(
                name="idx_credits_transactions_created_at",
                table="credits_transactions",
                columns=["created_at"],
                index_type=IndexType.B_TREE,
                description="Index on credit transaction date"
            )
        ])
        
        # RunPod indexes
        indexes.extend([
            IndexDefinition(
                name="idx_runpod_pods_user_id",
                table="runpod_pods",
                columns=["user_id"],
                index_type=IndexType.B_TREE,
                description="Foreign key index for user RunPod instances"
            ),
            IndexDefinition(
                name="idx_runpod_pods_status",
                table="runpod_pods",
                columns=["status"],
                index_type=IndexType.B_TREE,
                description="Index on RunPod status"
            ),
            IndexDefinition(
                name="idx_runpod_pods_gpu_type",
                table="runpod_pods",
                columns=["gpu_type"],
                index_type=IndexType.B_TREE,
                description="Index on RunPod GPU type"
            ),
            IndexDefinition(
                name="idx_runpod_executions_pod_id",
                table="runpod_executions",
                columns=["pod_id"],
                index_type=IndexType.B_TREE,
                description="Foreign key index for RunPod executions"
            ),
            IndexDefinition(
                name="idx_runpod_executions_status",
                table="runpod_executions",
                columns=["status"],
                index_type=IndexType.B_TREE,
                description="Index on RunPod execution status"
            )
        ])
        
        # ComfyUI indexes
        indexes.extend([
            IndexDefinition(
                name="idx_comfyui_executions_user_id",
                table="comfyui_workflow_executions",
                columns=["user_id"],
                index_type=IndexType.B_TREE,
                description="Foreign key index for user ComfyUI executions"
            ),
            IndexDefinition(
                name="idx_comfyui_executions_status",
                table="comfyui_workflow_executions",
                columns=["status"],
                index_type=IndexType.B_TREE,
                description="Index on ComfyUI execution status"
            ),
            IndexDefinition(
                name="idx_comfyui_executions_workflow_type",
                table="comfyui_workflow_executions",
                columns=["workflow_type"],
                index_type=IndexType.B_TREE,
                description="Index on ComfyUI workflow type"
            ),
            IndexDefinition(
                name="idx_comfyui_executions_created_at",
                table="comfyui_workflow_executions",
                columns=["created_at"],
                index_type=IndexType.B_TREE,
                description="Index on ComfyUI execution creation date"
            )
        ])
        
        # Social account indexes
        indexes.extend([
            IndexDefinition(
                name="idx_social_accounts_user_id",
                table="social_accounts",
                columns=["user_id"],
                index_type=IndexType.B_TREE,
                description="Foreign key index for user social accounts"
            ),
            IndexDefinition(
                name="idx_social_accounts_platform",
                table="social_accounts",
                columns=["platform"],
                index_type=IndexType.B_TREE,
                description="Index on social platform"
            ),
            IndexDefinition(
                name="idx_social_accounts_user_platform",
                table="social_accounts",
                columns=["user_id", "platform"],
                index_type=IndexType.COMPOSITE,
                unique=True,
                description="Unique composite index for user platform accounts"
            )
        ])
        
        # Export indexes
        indexes.extend([
            IndexDefinition(
                name="idx_exports_project_id",
                table="exports",
                columns=["project_id"],
                index_type=IndexType.B_TREE,
                description="Foreign key index for project exports"
            ),
            IndexDefinition(
                name="idx_exports_status",
                table="exports",
                columns=["status"],
                index_type=IndexType.B_TREE,
                description="Index on export status"
            ),
            IndexDefinition(
                name="idx_exports_created_at",
                table="exports",
                columns=["created_at"],
                index_type=IndexType.B_TREE,
                description="Index on export creation date"
            )
        ])
        
        # Stats indexes
        indexes.extend([
            IndexDefinition(
                name="idx_stats_date",
                table="stats",
                columns=["date"],
                index_type=IndexType.B_TREE,
                description="Index on stats date for time-series queries"
            ),
            IndexDefinition(
                name="idx_stats_metric_type",
                table="stats",
                columns=["metric_type"],
                index_type=IndexType.B_TREE,
                description="Index on stats metric type"
            ),
            IndexDefinition(
                name="idx_stats_date_metric",
                table="stats",
                columns=["date", "metric_type"],
                index_type=IndexType.COMPOSITE,
                description="Composite index for stats queries"
            )
        ])
        
        return indexes
    
    def define_performance_indexes(self) -> List[IndexDefinition]:
        """Define performance-optimized indexes"""
        indexes = []
        
        # Partial indexes for active records
        indexes.extend([
            IndexDefinition(
                name="idx_users_active_created",
                table="users",
                columns=["created_at"],
                index_type=IndexType.PARTIAL,
                partial_condition="is_active = true",
                description="Partial index on active users creation date"
            ),
            IndexDefinition(
                name="idx_projects_active_updated",
                table="projects",
                columns=["updated_at"],
                index_type=IndexType.PARTIAL,
                partial_condition="status != 'cancelled'",
                description="Partial index on active projects update date"
            ),
            IndexDefinition(
                name="idx_jobs_running_created",
                table="jobs",
                columns=["created_at"],
                index_type=IndexType.PARTIAL,
                partial_condition="status IN ('pending', 'running')",
                description="Partial index on running jobs creation date"
            )
        ])
        
        # BRIN indexes for large tables with time-series data
        indexes.extend([
            IndexDefinition(
                name="idx_jobs_created_at_brin",
                table="jobs",
                columns=["created_at"],
                index_type=IndexType.BRIN,
                description="BRIN index on jobs creation date for time-series queries"
            ),
            IndexDefinition(
                name="idx_payments_created_at_brin",
                table="payments",
                columns=["created_at"],
                index_type=IndexType.BRIN,
                description="BRIN index on payments creation date for time-series queries"
            ),
            IndexDefinition(
                name="idx_stats_date_brin",
                table="stats",
                columns=["date"],
                index_type=IndexType.BRIN,
                description="BRIN index on stats date for time-series queries"
            )
        ])
        
        # GIN indexes for JSON columns
        indexes.extend([
            IndexDefinition(
                name="idx_projects_analysis_gin",
                table="projects",
                columns=["analysis"],
                index_type=IndexType.GIN,
                description="GIN index on project analysis JSON for complex queries"
            ),
            IndexDefinition(
                name="idx_users_settings_gin",
                table="users",
                columns=["settings"],
                index_type=IndexType.GIN,
                description="GIN index on user settings JSON for complex queries"
            )
        ])
        
        return indexes
    
    def define_analytics_indexes(self) -> List[IndexDefinition]:
        """Define indexes for analytics and reporting"""
        indexes = []
        
        # Analytics composite indexes
        indexes.extend([
            IndexDefinition(
                name="idx_users_plan_created",
                table="users",
                columns=["plan", "created_at"],
                index_type=IndexType.COMPOSITE,
                description="Composite index for user plan analytics"
            ),
            IndexDefinition(
                name="idx_projects_type_status_created",
                table="projects",
                columns=["type", "status", "created_at"],
                index_type=IndexType.COMPOSITE,
                description="Composite index for project analytics"
            ),
            IndexDefinition(
                name="idx_jobs_type_status_created",
                table="jobs",
                columns=["type", "status", "created_at"],
                index_type=IndexType.COMPOSITE,
                description="Composite index for job analytics"
            ),
            IndexDefinition(
                name="idx_payments_status_created",
                table="payments",
                columns=["status", "created_at"],
                index_type=IndexType.COMPOSITE,
                description="Composite index for payment analytics"
            )
        ])
        
        return indexes
    
    async def create_index(self, index_def: IndexDefinition) -> bool:
        """Create a single index"""
        try:
            # Build index creation SQL
            sql_parts = [f"CREATE"]
            
            if index_def.unique:
                sql_parts.append("UNIQUE")
            
            sql_parts.append("INDEX")
            
            if index_def.concurrent:
                sql_parts.append("CONCURRENTLY")
            
            sql_parts.append(f'"{index_def.name}"')
            sql_parts.append(f'ON "{index_def.table}"')
            
            # Add columns
            columns_str = ", ".join([f'"{col}"' for col in index_def.columns])
            sql_parts.append(f"({columns_str})")
            
            # Add index type
            if index_def.index_type == IndexType.BRIN:
                sql_parts.append("USING brin")
            elif index_def.index_type == IndexType.GIN:
                sql_parts.append("USING gin")
            elif index_def.index_type == IndexType.GIST:
                sql_parts.append("USING gist")
            elif index_def.index_type == IndexType.HASH:
                sql_parts.append("USING hash")
            
            # Add partial condition
            if index_def.partial_condition:
                sql_parts.append(f"WHERE {index_def.partial_condition}")
            
            # Add include columns
            if index_def.include_columns:
                include_str = ", ".join([f'"{col}"' for col in index_def.include_columns])
                sql_parts.append(f"INCLUDE ({include_str})")
            
            # Add fillfactor
            if index_def.fillfactor:
                sql_parts.append(f"WITH (fillfactor = {index_def.fillfactor})")
            
            sql = " ".join(sql_parts)
            
            # Execute index creation
            await self.db_session.execute(text(sql))
            await self.db_session.commit()
            
            logger.info(f"Created index: {index_def.name} on {index_def.table}")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to create index {index_def.name}: {str(e)}")
            await self.db_session.rollback()
            return False
    
    async def drop_index(self, index_name: str, table_name: str) -> bool:
        """Drop an index"""
        try:
            sql = f'DROP INDEX CONCURRENTLY IF EXISTS "{index_name}"'
            await self.db_session.execute(text(sql))
            await self.db_session.commit()
            
            logger.info(f"Dropped index: {index_name}")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to drop index {index_name}: {str(e)}")
            await self.db_session.rollback()
            return False
    
    async def get_index_usage_stats(self) -> Dict[str, IndexPerformanceMetrics]:
        """Get index usage statistics"""
        try:
            sql = """
            SELECT 
                schemaname,
                tablename,
                indexname,
                idx_tup_read,
                idx_tup_fetch,
                idx_scan,
                pg_size_pretty(pg_relation_size(indexrelid)) as size
            FROM pg_stat_user_indexes 
            WHERE schemaname = 'public'
            ORDER BY idx_scan DESC
            """
            
            result = await self.db_session.execute(text(sql))
            rows = result.fetchall()
            
            metrics = {}
            for row in rows:
                metrics[row.indexname] = IndexPerformanceMetrics(
                    index_name=row.indexname,
                    table_name=row.tablename,
                    index_size_bytes=0,  # Would need additional query for exact size
                    index_usage_count=row.idx_scan,
                    index_scan_count=row.idx_scan,
                    index_tup_read=row.idx_tup_read,
                    index_tup_fetch=row.idx_tup_fetch
                )
            
            return metrics
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to get index usage stats: {str(e)}")
            return {}
    
    async def analyze_table(self, table_name: str) -> bool:
        """Run ANALYZE on a table to update statistics"""
        try:
            sql = f'ANALYZE "{table_name}"'
            await self.db_session.execute(text(sql))
            await self.db_session.commit()
            
            logger.info(f"Analyzed table: {table_name}")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to analyze table {table_name}: {str(e)}")
            await self.db_session.rollback()
            return False
    
    async def get_table_stats(self, table_name: str) -> Dict[str, Any]:
        """Get table statistics"""
        try:
            sql = """
            SELECT 
                schemaname,
                tablename,
                n_tup_ins as inserts,
                n_tup_upd as updates,
                n_tup_del as deletes,
                n_live_tup as live_tuples,
                n_dead_tup as dead_tuples,
                last_vacuum,
                last_autovacuum,
                last_analyze,
                last_autoanalyze
            FROM pg_stat_user_tables 
            WHERE tablename = :table_name
            """
            
            result = await self.db_session.execute(text(sql), {"table_name": table_name})
            row = result.fetchone()
            
            if row:
                return {
                    "table_name": row.tablename,
                    "inserts": row.inserts,
                    "updates": row.updates,
                    "deletes": row.deletes,
                    "live_tuples": row.live_tuples,
                    "dead_tuples": row.dead_tuples,
                    "last_vacuum": row.last_vacuum,
                    "last_autovacuum": row.last_autovacuum,
                    "last_analyze": row.last_analyze,
                    "last_autoanalyze": row.last_autoanalyze
                }
            
            return {}
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to get table stats for {table_name}: {str(e)}")
            return {}
    
    async def optimize_database(self) -> Dict[str, Any]:
        """Run comprehensive database optimization"""
        results = {
            "indexes_created": 0,
            "indexes_failed": 0,
            "tables_analyzed": 0,
            "tables_failed": 0,
            "errors": []
        }
        
        # Get all index definitions
        all_indexes = (
            self.define_core_indexes() +
            self.define_performance_indexes() +
            self.define_analytics_indexes()
        )
        
        # Create indexes
        for index_def in all_indexes:
            try:
                success = await self.create_index(index_def)
                if success:
                    results["indexes_created"] += 1
                else:
                    results["indexes_failed"] += 1
                    results["errors"].append(f"Failed to create index: {index_def.name}")
            except Exception as e:
                results["indexes_failed"] += 1
                results["errors"].append(f"Error creating index {index_def.name}: {str(e)}")
        
        # Analyze all tables
        tables = [
            "users", "projects", "jobs", "audio", "video", "track",
            "payments", "credits_transactions", "runpod_pods", "runpod_executions",
            "comfyui_workflow_executions", "social_accounts", "exports", "stats"
        ]
        
        for table in tables:
            try:
                success = await self.analyze_table(table)
                if success:
                    results["tables_analyzed"] += 1
                else:
                    results["tables_failed"] += 1
                    results["errors"].append(f"Failed to analyze table: {table}")
            except Exception as e:
                results["tables_failed"] += 1
                results["errors"].append(f"Error analyzing table {table}: {str(e)}")
        
        return results
    
    async def get_optimization_report(self) -> Dict[str, Any]:
        """Generate comprehensive optimization report"""
        report = {
            "timestamp": "2024-01-01T00:00:00Z",  # Would use actual timestamp
            "index_usage_stats": await self.get_index_usage_stats(),
            "table_stats": {},
            "recommendations": []
        }
        
        # Get table stats for all tables
        tables = [
            "users", "projects", "jobs", "audio", "video", "track",
            "payments", "credits_transactions", "runpod_pods", "runpod_executions",
            "comfyui_workflow_executions", "social_accounts", "exports", "stats"
        ]
        
        for table in tables:
            stats = await self.get_table_stats(table)
            if stats:
                report["table_stats"][table] = stats
        
        # Generate recommendations
        recommendations = []
        
        # Check for unused indexes
        for index_name, metrics in report["index_usage_stats"].items():
            if metrics.index_usage_count == 0:
                recommendations.append({
                    "type": "unused_index",
                    "index": index_name,
                    "table": metrics.table_name,
                    "action": "Consider dropping unused index"
                })
        
        # Check for tables that need vacuum
        for table_name, stats in report["table_stats"].items():
            if stats.get("dead_tuples", 0) > stats.get("live_tuples", 1) * 0.1:
                recommendations.append({
                    "type": "vacuum_needed",
                    "table": table_name,
                    "dead_tuples": stats["dead_tuples"],
                    "live_tuples": stats["live_tuples"],
                    "action": "Run VACUUM on table"
                })
        
        report["recommendations"] = recommendations
        
        return report
