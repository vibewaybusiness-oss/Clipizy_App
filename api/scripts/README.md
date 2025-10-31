# Scripts System

The scripts system provides utility scripts for database optimization, maintenance, and administrative tasks.

## Overview

This module contains standalone scripts that perform various administrative and maintenance tasks for the application. These scripts are designed to be run independently and provide essential functionality for database management and system optimization.

## Architecture

```
api/scripts/
├── __init__.py              # Script exports and utilities
├── README.md               # This file
└── optimize_database.py    # Database optimization script
```

## Core Components

### 1. Database Optimization Script (`optimize_database.py`)

Comprehensive database optimization and maintenance tool:

**Key Features:**
- Database performance analysis
- Index optimization
- Query performance tuning
- Connection pool optimization
- Database health checks
- Maintenance recommendations

**Optimization Areas:**
- **Index Analysis**: Analyze and optimize database indexes
- **Query Performance**: Identify and optimize slow queries
- **Connection Pooling**: Optimize connection pool settings
- **Table Maintenance**: Analyze table statistics and fragmentation
- **Storage Optimization**: Optimize database storage and compression

**Usage Example:**
```bash
# Run database optimization
python api/scripts/optimize_database.py

# Run with specific options
python api/scripts/optimize_database.py --analyze-indexes --optimize-queries

# Run in dry-run mode
python api/scripts/optimize_database.py --dry-run

# Run with custom configuration
python api/scripts/optimize_database.py --config custom_config.json
```

## Script Implementation Details

### Database Optimization Features

The optimization script provides comprehensive database analysis and optimization:

```python
from api.scripts.optimize_database import DatabaseOptimizer

# Initialize optimizer
optimizer = DatabaseOptimizer()

# Analyze database performance
analysis = optimizer.analyze_performance()
print(f"Database performance score: {analysis['score']}")

# Optimize indexes
index_optimization = optimizer.optimize_indexes()
print(f"Optimized {index_optimization['indexes_optimized']} indexes")

# Optimize queries
query_optimization = optimizer.optimize_queries()
print(f"Optimized {query_optimization['queries_optimized']} queries")

# Generate optimization report
report = optimizer.generate_report()
print(report)
```

### Performance Analysis

The script analyzes various database performance metrics:

```python
# Analyze connection pool performance
pool_analysis = optimizer.analyze_connection_pool()
print(f"Pool utilization: {pool_analysis['utilization']}%")
print(f"Average connection time: {pool_analysis['avg_connection_time']}ms")

# Analyze table performance
table_analysis = optimizer.analyze_tables()
for table in table_analysis['tables']:
    print(f"Table {table['name']}: {table['row_count']} rows, {table['size']}MB")

# Analyze query performance
query_analysis = optimizer.analyze_queries()
for query in query_analysis['slow_queries']:
    print(f"Slow query: {query['query']} - {query['execution_time']}ms")
```

### Index Optimization

The script provides intelligent index optimization:

```python
# Analyze index usage
index_analysis = optimizer.analyze_indexes()
for index in index_analysis['unused_indexes']:
    print(f"Unused index: {index['name']} on table {index['table']}")

# Suggest new indexes
suggestions = optimizer.suggest_indexes()
for suggestion in suggestions:
    print(f"Suggested index: {suggestion['index']} for query {suggestion['query']}")

# Create optimized indexes
optimization_result = optimizer.create_optimized_indexes()
print(f"Created {optimization_result['indexes_created']} new indexes")
```

## Configuration Integration

### Script Configuration

Scripts integrate with the configuration system:

```python
from api.config import get_config_value
from api.scripts.optimize_database import DatabaseOptimizer

# Get configuration values
db_url = get_config_value("database.url")
pool_size = get_config_value("database.pool_size", 10)
optimization_level = get_config_value("scripts.optimization_level", "standard")

# Initialize optimizer with configuration
optimizer = DatabaseOptimizer(
    database_url=db_url,
    pool_size=pool_size,
    optimization_level=optimization_level
)
```

### Environment-Specific Configuration

```python
# Development configuration
if environment == "development":
    optimizer = DatabaseOptimizer(
        optimization_level="basic",
        dry_run=True,
        verbose=True
    )

# Production configuration
elif environment == "production":
    optimizer = DatabaseOptimizer(
        optimization_level="aggressive",
        dry_run=False,
        backup_before_optimization=True
    )
```

## Error Handling and Logging

### Comprehensive Error Handling

```python
from api.scripts.optimize_database import DatabaseOptimizer
from api.config.logging import get_logger

logger = get_logger(__name__)

try:
    optimizer = DatabaseOptimizer()
    result = optimizer.optimize_database()
    logger.info(f"Database optimization completed: {result}")
except DatabaseConnectionError as e:
    logger.error(f"Database connection failed: {e}")
except OptimizationError as e:
    logger.error(f"Optimization failed: {e}")
except Exception as e:
    logger.error(f"Unexpected error: {e}")
```

### Detailed Logging

```python
# Enable detailed logging
optimizer = DatabaseOptimizer(verbose=True)

# Log optimization steps
optimizer.log_step("Starting database analysis")
analysis = optimizer.analyze_performance()
optimizer.log_step(f"Analysis completed: {analysis['score']} score")

optimizer.log_step("Starting index optimization")
index_result = optimizer.optimize_indexes()
optimizer.log_step(f"Index optimization completed: {index_result['indexes_optimized']} indexes")
```

## Script Execution

### Command Line Interface

```bash
# Basic optimization
python api/scripts/optimize_database.py

# Advanced options
python api/scripts/optimize_database.py \
    --analyze-indexes \
    --optimize-queries \
    --analyze-connections \
    --generate-report \
    --output report.html

# Configuration file
python api/scripts/optimize_database.py --config optimization_config.json

# Dry run mode
python api/scripts/optimize_database.py --dry-run

# Verbose output
python api/scripts/optimize_database.py --verbose
```

### Programmatic Execution

```python
from api.scripts.optimize_database import DatabaseOptimizer

# Create optimizer instance
optimizer = DatabaseOptimizer(
    database_url="postgresql://user:pass@localhost:5432/clipizy",
    optimization_level="standard",
    dry_run=False
)

# Run optimization
result = optimizer.run_optimization()

# Check results
if result['success']:
    print(f"Optimization completed successfully")
    print(f"Performance improvement: {result['performance_improvement']}%")
    print(f"Indexes optimized: {result['indexes_optimized']}")
    print(f"Queries optimized: {result['queries_optimized']}")
else:
    print(f"Optimization failed: {result['error']}")
```

## Reporting and Analytics

### Optimization Reports

```python
# Generate HTML report
report = optimizer.generate_html_report()
with open("optimization_report.html", "w") as f:
    f.write(report)

# Generate JSON report
report = optimizer.generate_json_report()
with open("optimization_report.json", "w") as f:
    json.dump(report, f, indent=2)

# Generate summary report
summary = optimizer.generate_summary_report()
print(summary)
```

### Performance Metrics

```python
# Get performance metrics
metrics = optimizer.get_performance_metrics()
print(f"Database size: {metrics['database_size']}MB")
print(f"Table count: {metrics['table_count']}")
print(f"Index count: {metrics['index_count']}")
print(f"Query count: {metrics['query_count']}")
print(f"Average query time: {metrics['avg_query_time']}ms")
```

## Safety Features

### Backup and Recovery

```python
# Enable backup before optimization
optimizer = DatabaseOptimizer(backup_before_optimization=True)

# Create backup
backup_result = optimizer.create_backup()
print(f"Backup created: {backup_result['backup_path']}")

# Restore from backup if needed
if optimization_failed:
    restore_result = optimizer.restore_backup(backup_result['backup_path'])
    print(f"Database restored from backup")
```

### Dry Run Mode

```python
# Run in dry-run mode
optimizer = DatabaseOptimizer(dry_run=True)

# Analyze what would be optimized
analysis = optimizer.analyze_optimization_plan()
print(f"Would optimize {analysis['indexes_to_optimize']} indexes")
print(f"Would optimize {analysis['queries_to_optimize']} queries")
print(f"Estimated performance improvement: {analysis['estimated_improvement']}%")
```

## Integration with Services

### Service Integration

```python
from api.services.database.optimization_service import OptimizationService
from api.scripts.optimize_database import DatabaseOptimizer

# Use optimization service
optimization_service = OptimizationService()
optimizer = DatabaseOptimizer(service=optimization_service)

# Run optimization through service
result = optimization_service.run_optimization(optimizer)
```

### Configuration Integration

```python
from api.config import get_config_manager
from api.scripts.optimize_database import DatabaseOptimizer

# Get configuration
config = get_config_manager()
db_config = config.get_config("database")

# Initialize optimizer with configuration
optimizer = DatabaseOptimizer(
    database_url=db_config.url,
    pool_size=db_config.pool_size,
    max_overflow=db_config.max_overflow
)
```

## Best Practices

1. **Run Regularly**: Schedule optimization scripts to run regularly
2. **Monitor Performance**: Track performance improvements over time
3. **Use Dry Run**: Always test with dry-run mode first
4. **Create Backups**: Always backup before optimization
5. **Monitor Logs**: Check logs for optimization results
6. **Test Thoroughly**: Test optimization in development first
7. **Document Changes**: Document optimization changes
8. **Monitor Impact**: Monitor application performance after optimization

## Scheduling and Automation

### Cron Job Setup

```bash
# Add to crontab for daily optimization
0 2 * * * /path/to/python /path/to/api/scripts/optimize_database.py --config production_config.json

# Weekly comprehensive optimization
0 3 * * 0 /path/to/python /path/to/api/scripts/optimize_database.py --full-optimization
```

### Docker Integration

```dockerfile
# Add optimization script to Docker image
COPY api/scripts/ /app/scripts/

# Run optimization in container
RUN python /app/scripts/optimize_database.py --config /app/config/optimization.json
```

## Monitoring and Alerting

### Performance Monitoring

```python
# Monitor optimization results
optimization_result = optimizer.run_optimization()

# Send alerts if performance degrades
if optimization_result['performance_improvement'] < 0:
    send_alert(f"Database optimization resulted in performance degradation: {optimization_result['performance_improvement']}%")
```

### Health Checks

```python
# Check database health after optimization
health_check = optimizer.check_database_health()
if not health_check['healthy']:
    send_alert(f"Database health check failed: {health_check['issues']}")
```

This scripts system provides essential database maintenance and optimization capabilities that ensure the application's data layer remains performant and healthy.
