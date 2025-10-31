# Cache Service

This directory contains the Redis-based caching service implementation for the Clipizy backend, providing high-performance caching capabilities to reduce database load and improve response times.

## Purpose

The cache service provides a comprehensive caching layer that:
- Reduces database load by caching frequently accessed data
- Improves API response times through intelligent caching
- Provides distributed caching capabilities with Redis
- Supports various caching patterns and strategies
- Includes cache warming and invalidation utilities

## Files Overview

### Core Cache Service
- **`redis_cache.py`** - High-performance Redis caching service
  - **Connection Pooling** - Efficient Redis connection management
  - **Error Handling** - Robust error handling and reconnection logic
  - **Serialization** - JSON-based data serialization with compression support
  - **Statistics** - Comprehensive cache hit/miss statistics and monitoring
  - **Distributed Locks** - Redis-based distributed locking mechanism

### Cache Integration
- **`cache_integration.py`** - Integration layer for existing services
  - **Service Mixins** - Database, API, session, and file caching mixins
  - **Decorators** - Easy-to-use caching decorators for functions
  - **Cache Warming** - Utilities for preloading frequently accessed data
  - **Pattern Invalidation** - Smart cache invalidation strategies

## Cache Service Features

### Redis Cache Service
The Redis cache service provides comprehensive caching capabilities:

#### Core Functionality
- **High Performance** - Connection pooling and async operations
- **Automatic Reconnection** - Health checks and automatic reconnection
- **Data Serialization** - JSON serialization with compression support
- **TTL Management** - Configurable time-to-live for cache entries
- **Statistics Tracking** - Hit/miss rates and performance metrics

#### Configuration Options
```python
from api.services.cache.redis_cache import CacheConfig, RedisCacheService

# Configure Redis connection
config = CacheConfig(
    host="localhost",
    port=6379,
    db=0,
    password=None,
    max_connections=20,
    default_ttl=300,
    key_prefix="clipizy:",
    enable_compression=True
)

# Initialize cache service
cache_service = RedisCacheService(config)
await cache_service.connect()
```

#### Basic Operations
```python
# Set value with TTL
await cache_service.set("user:123", user_data, ttl=3600)

# Get value
user_data = await cache_service.get("user:123")

# Delete value
await cache_service.delete("user:123")

# Check if key exists
exists = await cache_service.exists("user:123")

# Set expiration
await cache_service.expire("user:123", 1800)

# Get TTL
ttl = await cache_service.ttl("user:123")
```

#### Batch Operations
```python
# Get multiple values
values = await cache_service.mget(["user:1", "user:2", "user:3"])

# Set multiple values
mapping = {
    "user:1": user1_data,
    "user:2": user2_data,
    "user:3": user3_data
}
await cache_service.mset(mapping, ttl=3600)
```

#### Pattern Operations
```python
# Clear keys matching pattern
deleted_count = await cache_service.clear_pattern("user:*")

# Use distributed locks
async with cache_service.lock("critical_section", timeout=10):
    # Critical section code
    pass
```

## Cache Integration Features

### Service Mixins
The cache integration provides mixins for different service types:

#### Database Cache Mixin
```python
from api.services.cache.cache_integration import DatabaseCacheMixin

class UserService(DatabaseCacheMixin):
    async def get_user(self, user_id: str):
        return await self.cached_query(
            f"user:{user_id}",
            lambda: self.db.get_user(user_id),
            ttl=3600
        )
    
    async def update_user(self, user_id: str, data: dict):
        result = await self.db.update_user(user_id, data)
        await self.invalidate_query_cache("users")
        return result
```

#### API Cache Mixin
```python
from api.services.cache.cache_integration import APICacheMixin

class ExternalAPIService(APICacheMixin):
    async def get_weather_data(self, city: str):
        return await self.cached_api_call(
            f"weather:{city}",
            lambda: self.fetch_weather(city),
            ttl=1800
        )
```

#### Session Cache Mixin
```python
from api.services.cache.cache_integration import SessionCacheMixin

class AuthService(SessionCacheMixin):
    async def create_session(self, user_id: str, session_data: dict):
        await self.cache_user_session(user_id, session_data, ttl=3600)
    
    async def get_session(self, user_id: str):
        return await self.get_user_session(user_id)
    
    async def logout(self, user_id: str):
        await self.invalidate_user_session(user_id)
```

### Caching Decorators
Easy-to-use decorators for function caching:

#### Basic Caching
```python
from api.services.cache.cache_integration import cached

@cached(ttl=300, key_prefix="user:")
async def get_user_profile(user_id: str):
    # Expensive database operation
    return await database.get_user(user_id)
```

#### Cache Invalidation
```python
from api.services.cache.cache_integration import cache_invalidate_pattern

@cache_invalidate_pattern("user:*")
async def update_user(user_id: str, data: dict):
    # Update user and invalidate related cache
    return await database.update_user(user_id, data)
```

### Cache Warming
Preload frequently accessed data:

```python
from api.services.cache.cache_integration import get_cache_warmer

async def warm_cache():
    cache_warmer = await get_cache_warmer()
    
    # Warm user data for active users
    active_users = await get_active_users()
    await cache_warmer.warm_user_data(active_users)
    
    # Warm system configuration
    await cache_warmer.warm_system_data()
    
    # Warm popular content
    await cache_warmer.warm_frequently_accessed_data()
```

## Integration with FastAPI

### Service Integration
```python
from api.services.cache.redis_cache import get_cache_service
from api.services.cache.cache_integration import get_cache_integration

# In your service
class UserService:
    async def get_user(self, user_id: str):
        cache_integration = await get_cache_integration()
        
        return await cache_integration.get_or_set(
            f"user:{user_id}",
            lambda: self._fetch_user_from_db(user_id),
            ttl=3600
        )
```

### Health Check Integration
```python
from api.services.cache.redis_cache import get_cache_service

async def check_cache_health():
    cache_service = await get_cache_service()
    is_healthy = await cache_service.health_check()
    stats = await cache_service.get_stats()
    
    return {
        "healthy": is_healthy,
        "stats": stats
    }
```

## Configuration

### Environment Variables
```bash
# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=your_password
REDIS_MAX_CONNECTIONS=20

# Cache Configuration
CACHE_DEFAULT_TTL=300
CACHE_KEY_PREFIX=clipizy:
CACHE_ENABLE_COMPRESSION=true
```

### Settings Integration
```python
# In your settings file
class Settings:
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    redis_max_connections: int = 20
    cache_default_ttl: int = 300
    cache_key_prefix: str = "clipizy:"
```

## Performance Considerations

### Optimization Features
- **Connection Pooling** - Efficient Redis connection management
- **Async Operations** - Non-blocking cache operations
- **Batch Operations** - Multiple operations in single Redis calls
- **Compression** - Optional data compression for large values
- **TTL Management** - Automatic expiration handling

### Monitoring
- **Hit/Miss Rates** - Cache effectiveness metrics
- **Response Times** - Cache operation performance
- **Error Rates** - Cache operation reliability
- **Connection Health** - Redis connection status

### Best Practices
1. **Appropriate TTL** - Set TTL based on data freshness requirements
2. **Key Naming** - Use consistent, hierarchical key naming
3. **Pattern Invalidation** - Use pattern-based cache invalidation
4. **Error Handling** - Gracefully handle cache failures
5. **Monitoring** - Monitor cache performance and hit rates
6. **Warming** - Preload frequently accessed data
7. **Compression** - Use compression for large values
8. **Connection Limits** - Configure appropriate connection pool size

## Dependencies

### Core Dependencies
- `redis` - Redis Python client with async support
- `json` - JSON serialization
- `asyncio` - Async operations
- `logging` - Logging framework

### Optional Dependencies
- `lz4` - Fast compression (if compression enabled)
- `zlib` - Standard compression library

## Error Handling

### Connection Errors
- Automatic reconnection on connection loss
- Graceful degradation when Redis unavailable
- Health check monitoring

### Serialization Errors
- Robust JSON serialization with error handling
- Fallback mechanisms for serialization failures
- Logging of serialization issues

### Performance Errors
- Timeout handling for slow operations
- Circuit breaker pattern for failing operations
- Performance monitoring and alerting

## Security Considerations

### Data Protection
- No sensitive data in cache keys
- Secure Redis connection configuration
- TTL-based automatic data expiration

### Access Control
- Redis authentication and authorization
- Network-level security for Redis access
- Cache key validation and sanitization

## Testing

### Unit Tests
```python
import pytest
from api.services.cache.redis_cache import RedisCacheService, CacheConfig

@pytest.mark.asyncio
async def test_cache_operations():
    config = CacheConfig(host="localhost", port=6379, db=15)  # Test DB
    cache = RedisCacheService(config)
    await cache.connect()
    
    # Test set/get
    await cache.set("test_key", {"data": "value"}, ttl=60)
    result = await cache.get("test_key")
    assert result == {"data": "value"}
    
    # Test delete
    await cache.delete("test_key")
    result = await cache.get("test_key")
    assert result is None
    
    await cache.disconnect()
```

### Integration Tests
```python
@pytest.mark.asyncio
async def test_cache_integration():
    from api.services.cache.cache_integration import get_cache_integration
    
    cache_integration = await get_cache_integration()
    
    # Test get_or_set
    result = await cache_integration.get_or_set(
        "test_key",
        lambda: {"cached": "data"},
        ttl=60
    )
    assert result == {"cached": "data"}
```

## Troubleshooting

### Common Issues
1. **Connection Failures** - Check Redis server status and network connectivity
2. **Serialization Errors** - Ensure data is JSON serializable
3. **Memory Issues** - Monitor Redis memory usage and set appropriate limits
4. **Performance Issues** - Check connection pool size and Redis performance

### Debugging
- Enable debug logging for cache operations
- Monitor Redis server logs
- Use Redis CLI for manual cache inspection
- Check cache statistics and hit rates

## Future Enhancements

### Planned Features
- **Cache Clustering** - Redis cluster support
- **Advanced Compression** - Multiple compression algorithms
- **Cache Analytics** - Detailed performance analytics
- **Auto-scaling** - Dynamic cache scaling based on load
- **Multi-tier Caching** - L1/L2 cache architecture
