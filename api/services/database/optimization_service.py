#!/usr/bin/env python3
"""
DATABASE OPTIMIZATION SERVICE
Comprehensive database optimization and maintenance service
"""
import logging
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import json

from sqlalchemy import text, func
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from api.services.database.indexing_strategy import DatabaseIndexingStrategy, IndexDefinition, IndexType

logger = logging.getLogger(__name__)


@dataclass
class QueryPerformanceMetrics:
    """Query performance metrics"""
    query_id: str
    query_text: str
    execution_time_ms: float
    rows_returned: int
    rows_examined: int
    index_used: Optional[str]
    table_name: str
    timestamp: datetime


@dataclass
class DatabaseHealthMetrics:
    """Database health metrics"""
    total_size_bytes: int
    active_connections: int
    max_connections: int
    cache_hit_ratio: float
    index_usage_ratio: float
    slow_query_count: int
    dead_tuples_ratio: float
    last_vacuum: Optional[datetime]
    last_analyze: Optional[datetime]


class DatabaseOptimizationService:
    """Comprehensive database optimization service"""
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.indexing_strategy = DatabaseIndexingStrategy(db_session)
        self.performance_metrics: List[QueryPerformanceMetrics] = []
        self.health_metrics: Optional[DatabaseHealthMetrics] = None
    
    async def get_database_health(self) -> DatabaseHealthMetrics:
        """Get comprehensive database health metrics"""
        try:
            # Get database size
            size_result = await self.db_session.execute(text("""
                SELECT pg_database_size(current_database()) as size_bytes
            """))
            size_row = size_result.fetchone()
            total_size = size_row.size_bytes if size_row else 0
            
            # Get connection stats
            conn_result = await self.db_session.execute(text("""
                SELECT 
                    (SELECT count(*) FROM pg_stat_activity WHERE state = 'active') as active_connections,
                    (SELECT setting::int FROM pg_settings WHERE name = 'max_connections') as max_connections
            """))
            conn_row = conn_result.fetchone()
            active_connections = conn_row.active_connections if conn_row else 0
            max_connections = conn_row.max_connections if conn_row else 0
            
            # Get cache hit ratio
            cache_result = await self.db_session.execute(text("""
                SELECT 
                    round(100.0 * sum(blks_hit) / (sum(blks_hit) + sum(blks_read)), 2) as cache_hit_ratio
                FROM pg_stat_database 
                WHERE datname = current_database()
            """))
            cache_row = cache_result.fetchone()
            cache_hit_ratio = cache_row.cache_hit_ratio if cache_row else 0.0
            
            # Get index usage ratio
            index_result = await self.db_session.execute(text("""
                SELECT 
                    round(100.0 * sum(idx_scan) / (sum(idx_scan) + sum(seq_scan)), 2) as index_usage_ratio
                FROM pg_stat_user_tables
            """))
            index_row = index_result.fetchone()
            index_usage_ratio = index_row.index_usage_ratio if index_row else 0.0
            
            # Get slow query count (queries taking > 1 second)
            slow_query_result = await self.db_session.execute(text("""
                SELECT count(*) as slow_query_count
                FROM pg_stat_statements 
                WHERE mean_exec_time > 1000
            """))
            slow_query_row = slow_query_result.fetchone()
            slow_query_count = slow_query_row.slow_query_count if slow_query_row else 0
            
            # Get dead tuples ratio
            dead_tuples_result = await self.db_session.execute(text("""
                SELECT 
                    round(100.0 * sum(n_dead_tup) / sum(n_live_tup), 2) as dead_tuples_ratio
                FROM pg_stat_user_tables
                WHERE n_live_tup > 0
            """))
            dead_tuples_row = dead_tuples_result.fetchone()
            dead_tuples_ratio = dead_tuples_row.dead_tuples_ratio if dead_tuples_row else 0.0
            
            # Get last vacuum and analyze times
            maintenance_result = await self.db_session.execute(text("""
                SELECT 
                    max(last_vacuum) as last_vacuum,
                    max(last_analyze) as last_analyze
                FROM pg_stat_user_tables
            """))
            maintenance_row = maintenance_result.fetchone()
            last_vacuum = maintenance_row.last_vacuum if maintenance_row else None
            last_analyze = maintenance_row.last_analyze if maintenance_row else None
            
            self.health_metrics = DatabaseHealthMetrics(
                total_size_bytes=total_size,
                active_connections=active_connections,
                max_connections=max_connections,
                cache_hit_ratio=cache_hit_ratio,
                index_usage_ratio=index_usage_ratio,
                slow_query_count=slow_query_count,
                dead_tuples_ratio=dead_tuples_ratio,
                last_vacuum=last_vacuum,
                last_analyze=last_analyze
            )
            
            return self.health_metrics
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to get database health metrics: {str(e)}")
            return DatabaseHealthMetrics(
                total_size_bytes=0,
                active_connections=0,
                max_connections=0,
                cache_hit_ratio=0.0,
                index_usage_ratio=0.0,
                slow_query_count=0,
                dead_tuples_ratio=0.0,
                last_vacuum=None,
                last_analyze=None
            )
    
    async def get_slow_queries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get slowest queries from pg_stat_statements"""
        try:
            sql = """
            SELECT 
                query,
                calls,
                total_exec_time,
                mean_exec_time,
                stddev_exec_time,
                rows,
                100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent
            FROM pg_stat_statements 
            WHERE mean_exec_time > 100
            ORDER BY mean_exec_time DESC
            LIMIT :limit
            """
            
            result = await self.db_session.execute(text(sql), {"limit": limit})
            rows = result.fetchall()
            
            slow_queries = []
            for row in rows:
                slow_queries.append({
                    "query": row.query[:200] + "..." if len(row.query) > 200 else row.query,
                    "calls": row.calls,
                    "total_exec_time": row.total_exec_time,
                    "mean_exec_time": row.mean_exec_time,
                    "stddev_exec_time": row.stddev_exec_time,
                    "rows": row.rows,
                    "hit_percent": row.hit_percent
                })
            
            return slow_queries
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to get slow queries: {str(e)}")
            return []
    
    async def get_table_bloat_analysis(self) -> List[Dict[str, Any]]:
        """Analyze table bloat and recommend maintenance"""
        try:
            sql = """
            SELECT 
                schemaname,
                tablename,
                n_live_tup as live_tuples,
                n_dead_tup as dead_tuples,
                round(100.0 * n_dead_tup / nullif(n_live_tup, 0), 2) as dead_tuple_percent,
                last_vacuum,
                last_autovacuum,
                last_analyze,
                last_autoanalyze,
                pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as table_size
            FROM pg_stat_user_tables
            WHERE n_live_tup > 0
            ORDER BY dead_tuple_percent DESC
            """
            
            result = await self.db_session.execute(text(sql))
            rows = result.fetchall()
            
            bloat_analysis = []
            for row in rows:
                bloat_analysis.append({
                    "table": row.tablename,
                    "live_tuples": row.live_tuples,
                    "dead_tuples": row.dead_tuples,
                    "dead_tuple_percent": row.dead_tuple_percent,
                    "last_vacuum": row.last_vacuum,
                    "last_autovacuum": row.last_autovacuum,
                    "last_analyze": row.last_analyze,
                    "last_autoanalyze": row.last_autoanalyze,
                    "table_size": row.table_size,
                    "needs_vacuum": row.dead_tuple_percent > 10.0,
                    "needs_analyze": row.last_analyze is None or 
                                   (datetime.now() - row.last_analyze).days > 7
                })
            
            return bloat_analysis
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to get table bloat analysis: {str(e)}")
            return []
    
    async def get_index_effectiveness(self) -> List[Dict[str, Any]]:
        """Analyze index effectiveness and usage"""
        try:
            sql = """
            SELECT 
                schemaname,
                tablename,
                indexname,
                idx_scan as index_scans,
                idx_tup_read as tuples_read,
                idx_tup_fetch as tuples_fetched,
                pg_size_pretty(pg_relation_size(indexrelid)) as index_size,
                pg_relation_size(indexrelid) as index_size_bytes
            FROM pg_stat_user_indexes
            WHERE schemaname = 'public'
            ORDER BY idx_scan DESC
            """
            
            result = await self.db_session.execute(text(sql))
            rows = result.fetchall()
            
            index_effectiveness = []
            for row in rows:
                effectiveness = "high" if row.index_scans > 1000 else "medium" if row.index_scans > 100 else "low"
                index_effectiveness.append({
                    "table": row.tablename,
                    "index": row.indexname,
                    "scans": row.index_scans,
                    "tuples_read": row.tuples_read,
                    "tuples_fetched": row.tuples_fetched,
                    "size": row.index_size,
                    "size_bytes": row.index_size_bytes,
                    "effectiveness": effectiveness,
                    "unused": row.index_scans == 0
                })
            
            return index_effectiveness
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to get index effectiveness: {str(e)}")
            return []
    
    async def vacuum_table(self, table_name: str, full: bool = False) -> bool:
        """Run VACUUM on a table"""
        try:
            vacuum_type = "VACUUM FULL" if full else "VACUUM"
            sql = f"{vacuum_type} ANALYZE \"{table_name}\""
            
            await self.db_session.execute(text(sql))
            await self.db_session.commit()
            
            logger.info(f"Vacuumed table: {table_name}")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to vacuum table {table_name}: {str(e)}")
            await self.db_session.rollback()
            return False
    
    async def reindex_table(self, table_name: str) -> bool:
        """Reindex a table"""
        try:
            sql = f'REINDEX TABLE CONCURRENTLY "{table_name}"'
            
            await self.db_session.execute(text(sql))
            await self.db_session.commit()
            
            logger.info(f"Reindexed table: {table_name}")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to reindex table {table_name}: {str(e)}")
            await self.db_session.rollback()
            return False
    
    async def update_table_statistics(self, table_name: str) -> bool:
        """Update table statistics"""
        try:
            sql = f'ANALYZE "{table_name}"'
            
            await self.db_session.execute(text(sql))
            await self.db_session.commit()
            
            logger.info(f"Updated statistics for table: {table_name}")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to update statistics for table {table_name}: {str(e)}")
            await self.db_session.rollback()
            return False
    
    async def optimize_database_performance(self) -> Dict[str, Any]:
        """Run comprehensive database performance optimization"""
        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "health_metrics": None,
            "index_optimization": {},
            "maintenance_tasks": {
                "vacuumed_tables": [],
                "reindexed_tables": [],
                "analyzed_tables": [],
                "failed_operations": []
            },
            "recommendations": []
        }
        
        try:
            # Get current health metrics
            health_metrics = await self.get_database_health()
            results["health_metrics"] = {
                "total_size_gb": round(health_metrics.total_size_bytes / (1024**3), 2),
                "active_connections": health_metrics.active_connections,
                "max_connections": health_metrics.max_connections,
                "cache_hit_ratio": health_metrics.cache_hit_ratio,
                "index_usage_ratio": health_metrics.index_usage_ratio,
                "slow_query_count": health_metrics.slow_query_count,
                "dead_tuples_ratio": health_metrics.dead_tuples_ratio
            }
            
            # Run index optimization
            index_results = await self.indexing_strategy.optimize_database()
            results["index_optimization"] = index_results
            
            # Get table bloat analysis
            bloat_analysis = await self.get_table_bloat_analysis()
            
            # Perform maintenance on tables that need it
            for table_info in bloat_analysis:
                table_name = table_info["table"]
                
                # Vacuum tables with high dead tuple ratio
                if table_info["needs_vacuum"]:
                    success = await self.vacuum_table(table_name)
                    if success:
                        results["maintenance_tasks"]["vacuumed_tables"].append(table_name)
                    else:
                        results["maintenance_tasks"]["failed_operations"].append(f"vacuum_{table_name}")
                
                # Analyze tables that need statistics update
                if table_info["needs_analyze"]:
                    success = await self.update_table_statistics(table_name)
                    if success:
                        results["maintenance_tasks"]["analyzed_tables"].append(table_name)
                    else:
                        results["maintenance_tasks"]["failed_operations"].append(f"analyze_{table_name}")
            
            # Get index effectiveness and reindex if needed
            index_effectiveness = await self.get_index_effectiveness()
            for index_info in index_effectiveness:
                if index_info["unused"] and index_info["size_bytes"] > 1024 * 1024:  # > 1MB
                    results["recommendations"].append({
                        "type": "unused_index",
                        "table": index_info["table"],
                        "index": index_info["index"],
                        "size": index_info["size"],
                        "action": "Consider dropping unused index"
                    })
            
            # Generate performance recommendations
            if health_metrics.cache_hit_ratio < 95:
                results["recommendations"].append({
                    "type": "cache_performance",
                    "issue": "Low cache hit ratio",
                    "current_ratio": health_metrics.cache_hit_ratio,
                    "action": "Consider increasing shared_buffers"
                })
            
            if health_metrics.index_usage_ratio < 80:
                results["recommendations"].append({
                    "type": "index_usage",
                    "issue": "Low index usage ratio",
                    "current_ratio": health_metrics.index_usage_ratio,
                    "action": "Review query patterns and add missing indexes"
                })
            
            if health_metrics.dead_tuples_ratio > 10:
                results["recommendations"].append({
                    "type": "dead_tuples",
                    "issue": "High dead tuple ratio",
                    "current_ratio": health_metrics.dead_tuples_ratio,
                    "action": "Run VACUUM more frequently or tune autovacuum"
                })
            
            if health_metrics.slow_query_count > 10:
                results["recommendations"].append({
                    "type": "slow_queries",
                    "issue": "High number of slow queries",
                    "count": health_metrics.slow_query_count,
                    "action": "Review and optimize slow queries"
                })
            
            logger.info("Database performance optimization completed")
            
        except Exception as e:
            logger.error(f"Database optimization failed: {str(e)}")
            results["error"] = str(e)
        
        return results
    
    async def get_optimization_report(self) -> Dict[str, Any]:
        """Generate comprehensive optimization report"""
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "health_metrics": await self.get_database_health(),
            "slow_queries": await self.get_slow_queries(20),
            "table_bloat": await self.get_table_bloat_analysis(),
            "index_effectiveness": await self.get_index_effectiveness(),
            "index_usage_stats": await self.indexing_strategy.get_index_usage_stats(),
            "recommendations": []
        }
        
        # Generate recommendations based on analysis
        recommendations = []
        
        # Check cache hit ratio
        if report["health_metrics"].cache_hit_ratio < 95:
            recommendations.append({
                "type": "performance",
                "priority": "high",
                "issue": "Low cache hit ratio",
                "current_value": f"{report['health_metrics'].cache_hit_ratio}%",
                "target_value": ">95%",
                "action": "Increase shared_buffers or check for memory pressure"
            })
        
        # Check index usage
        if report["health_metrics"].index_usage_ratio < 80:
            recommendations.append({
                "type": "performance",
                "priority": "medium",
                "issue": "Low index usage ratio",
                "current_value": f"{report['health_metrics'].index_usage_ratio}%",
                "target_value": ">80%",
                "action": "Review query patterns and add missing indexes"
            })
        
        # Check for tables needing vacuum
        for table in report["table_bloat"]:
            if table["needs_vacuum"]:
                recommendations.append({
                    "type": "maintenance",
                    "priority": "medium",
                    "issue": f"Table {table['table']} needs vacuum",
                    "current_value": f"{table['dead_tuple_percent']}% dead tuples",
                    "target_value": "<10%",
                    "action": f"Run VACUUM on {table['table']}"
                })
        
        # Check for unused indexes
        for index in report["index_effectiveness"]:
            if index["unused"] and index["size_bytes"] > 1024 * 1024:
                recommendations.append({
                    "type": "maintenance",
                    "priority": "low",
                    "issue": f"Unused index {index['index']}",
                    "current_value": f"{index['size']} unused",
                    "target_value": "Remove unused indexes",
                    "action": f"Consider dropping index {index['index']} on {index['table']}"
                })
        
        # Check for slow queries
        if report["health_metrics"].slow_query_count > 10:
            recommendations.append({
                "type": "performance",
                "priority": "high",
                "issue": "High number of slow queries",
                "current_value": f"{report['health_metrics'].slow_query_count} slow queries",
                "target_value": "<10",
                "action": "Review and optimize slow queries"
            })
        
        report["recommendations"] = recommendations
        
        return report
    
    async def schedule_maintenance(self) -> Dict[str, Any]:
        """Schedule regular database maintenance tasks"""
        maintenance_results = {
            "timestamp": datetime.utcnow().isoformat(),
            "tasks_completed": [],
            "tasks_failed": [],
            "next_scheduled": (datetime.utcnow() + timedelta(days=1)).isoformat()
        }
        
        # Daily maintenance tasks
        daily_tasks = [
            ("update_statistics", self._update_all_table_statistics),
            ("vacuum_analysis", self._vacuum_analyze_tables),
            ("index_health_check", self._check_index_health)
        ]
        
        for task_name, task_func in daily_tasks:
            try:
                result = await task_func()
                maintenance_results["tasks_completed"].append({
                    "task": task_name,
                    "result": result
                })
            except Exception as e:
                maintenance_results["tasks_failed"].append({
                    "task": task_name,
                    "error": str(e)
                })
                logger.error(f"Maintenance task {task_name} failed: {str(e)}")
        
        return maintenance_results
    
    async def _update_all_table_statistics(self) -> Dict[str, Any]:
        """Update statistics for all tables"""
        tables = [
            "users", "projects", "jobs", "audio", "video", "track",
            "payments", "credits_transactions", "runpod_pods", "runpod_executions",
            "comfyui_workflow_executions", "social_accounts", "exports", "stats"
        ]
        
        updated_tables = []
        failed_tables = []
        
        for table in tables:
            try:
                success = await self.update_table_statistics(table)
                if success:
                    updated_tables.append(table)
                else:
                    failed_tables.append(table)
            except Exception as e:
                failed_tables.append(table)
                logger.error(f"Failed to update statistics for {table}: {str(e)}")
        
        return {
            "updated_tables": updated_tables,
            "failed_tables": failed_tables,
            "total_tables": len(tables)
        }
    
    async def _vacuum_analyze_tables(self) -> Dict[str, Any]:
        """Run VACUUM ANALYZE on tables that need it"""
        bloat_analysis = await self.get_table_bloat_analysis()
        
        vacuumed_tables = []
        failed_tables = []
        
        for table_info in bloat_analysis:
            if table_info["needs_vacuum"]:
                try:
                    success = await self.vacuum_table(table_info["table"])
                    if success:
                        vacuumed_tables.append(table_info["table"])
                    else:
                        failed_tables.append(table_info["table"])
                except Exception as e:
                    failed_tables.append(table_info["table"])
                    logger.error(f"Failed to vacuum {table_info['table']}: {str(e)}")
        
        return {
            "vacuumed_tables": vacuumed_tables,
            "failed_tables": failed_tables,
            "tables_checked": len(bloat_analysis)
        }
    
    async def _check_index_health(self) -> Dict[str, Any]:
        """Check index health and usage"""
        index_effectiveness = await self.get_index_effectiveness()
        
        unused_indexes = []
        low_usage_indexes = []
        
        for index_info in index_effectiveness:
            if index_info["unused"]:
                unused_indexes.append({
                    "table": index_info["table"],
                    "index": index_info["index"],
                    "size": index_info["size"]
                })
            elif index_info["scans"] < 10:
                low_usage_indexes.append({
                    "table": index_info["table"],
                    "index": index_info["index"],
                    "scans": index_info["scans"],
                    "size": index_info["size"]
                })
        
        return {
            "unused_indexes": unused_indexes,
            "low_usage_indexes": low_usage_indexes,
            "total_indexes": len(index_effectiveness)
        }
