#!/usr/bin/env python3
"""
REDIS CACHE SERVICE
High-performance Redis caching service with connection pooling and error handling
"""
import json
import logging
import time
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from contextlib import asynccontextmanager
import asyncio

try:
    import redis.asyncio as redis
    from redis.asyncio import ConnectionPool, Redis
except ImportError:
    redis = None
    ConnectionPool = None
    Redis = None

logger = logging.getLogger(__name__)


@dataclass
class CacheConfig:
    """Configuration for Redis cache"""
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    max_connections: int = 20
    retry_on_timeout: bool = True
    socket_connect_timeout: int = 5
    socket_timeout: int = 5
    health_check_interval: int = 30
    default_ttl: int = 300  # 5 minutes
    key_prefix: str = "clipizy:"
    enable_compression: bool = False
    compression_threshold: int = 1024  # bytes


class RedisCacheService:
    """High-performance Redis caching service"""
    
    def __init__(self, config: Optional[CacheConfig] = None):
        self.config = config or CacheConfig()
        self.pool: Optional[ConnectionPool] = None
        self.client: Optional[Redis] = None
        self._connected = False
        self._last_health_check = 0
        self._stats = {
            "hits": 0,
            "misses": 0,
            "errors": 0,
            "sets": 0,
            "deletes": 0,
            "total_requests": 0
        }
    
    async def connect(self) -> bool:
        """Connect to Redis server"""
        if not redis:
            logger.error("Redis library not available. Install with: pip install redis")
            return False
        
        try:
            # Create connection pool
            self.pool = ConnectionPool(
                host=self.config.host,
                port=self.config.port,
                db=self.config.db,
                password=self.config.password,
                max_connections=self.config.max_connections,
                retry_on_timeout=self.config.retry_on_timeout,
                socket_connect_timeout=self.config.socket_connect_timeout,
                socket_timeout=self.config.socket_timeout,
                health_check_interval=self.config.health_check_interval
            )
            
            # Create Redis client
            self.client = Redis(connection_pool=self.pool)
            
            # Test connection
            await self.client.ping()
            self._connected = True
            
            logger.info(f"Connected to Redis at {self.config.host}:{self.config.port}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {str(e)}")
            self._connected = False
            return False
    
    async def disconnect(self):
        """Disconnect from Redis server"""
        if self.client:
            await self.client.close()
        if self.pool:
            await self.pool.disconnect()
        self._connected = False
        logger.info("Disconnected from Redis")
    
    async def health_check(self) -> bool:
        """Check Redis connection health"""
        if not self._connected or not self.client:
            return False
        
        try:
            current_time = time.time()
            # Only check every 30 seconds to avoid overhead
            if current_time - self._last_health_check < self.config.health_check_interval:
                return True
            
            await self.client.ping()
            self._last_health_check = current_time
            return True
            
        except Exception as e:
            logger.warning(f"Redis health check failed: {str(e)}")
            self._connected = False
            return False
    
    def _make_key(self, key: str) -> str:
        """Create full cache key with prefix"""
        return f"{self.config.key_prefix}{key}"
    
    def _serialize(self, value: Any) -> bytes:
        """Serialize value for storage"""
        if self.config.enable_compression and len(str(value)) > self.config.compression_threshold:
            # TODO: Implement compression if needed
            pass
        
        return json.dumps(value, default=str).encode('utf-8')
    
    def _deserialize(self, data: bytes) -> Any:
        """Deserialize value from storage"""
        if not data:
            return None
        
        try:
            return json.loads(data.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            logger.error(f"Failed to deserialize cache data: {str(e)}")
            return None
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not await self.health_check():
            return None
        
        try:
            self._stats["total_requests"] += 1
            full_key = self._make_key(key)
            
            data = await self.client.get(full_key)
            if data is not None:
                self._stats["hits"] += 1
                return self._deserialize(data)
            else:
                self._stats["misses"] += 1
                return None
                
        except Exception as e:
            logger.error(f"Cache get error for key '{key}': {str(e)}")
            self._stats["errors"] += 1
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with TTL"""
        if not await self.health_check():
            return False
        
        try:
            self._stats["total_requests"] += 1
            full_key = self._make_key(key)
            serialized_value = self._serialize(value)
            ttl = ttl or self.config.default_ttl
            
            await self.client.setex(full_key, ttl, serialized_value)
            self._stats["sets"] += 1
            return True
            
        except Exception as e:
            logger.error(f"Cache set error for key '{key}': {str(e)}")
            self._stats["errors"] += 1
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        if not await self.health_check():
            return False
        
        try:
            self._stats["total_requests"] += 1
            full_key = self._make_key(key)
            
            result = await self.client.delete(full_key)
            self._stats["deletes"] += 1
            return bool(result)
            
        except Exception as e:
            logger.error(f"Cache delete error for key '{key}': {str(e)}")
            self._stats["errors"] += 1
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        if not await self.health_check():
            return False
        
        try:
            full_key = self._make_key(key)
            return bool(await self.client.exists(full_key))
            
        except Exception as e:
            logger.error(f"Cache exists error for key '{key}': {str(e)}")
            return False
    
    async def expire(self, key: str, ttl: int) -> bool:
        """Set expiration time for key"""
        if not await self.health_check():
            return False
        
        try:
            full_key = self._make_key(key)
            return bool(await self.client.expire(full_key, ttl))
            
        except Exception as e:
            logger.error(f"Cache expire error for key '{key}': {str(e)}")
            return False
    
    async def ttl(self, key: str) -> int:
        """Get TTL for key"""
        if not await self.health_check():
            return -1
        
        try:
            full_key = self._make_key(key)
            return await self.client.ttl(full_key)
            
        except Exception as e:
            logger.error(f"Cache TTL error for key '{key}': {str(e)}")
            return -1
    
    async def mget(self, keys: List[str]) -> Dict[str, Any]:
        """Get multiple values from cache"""
        if not await self.health_check():
            return {}
        
        try:
            self._stats["total_requests"] += 1
            full_keys = [self._make_key(key) for key in keys]
            
            values = await self.client.mget(full_keys)
            result = {}
            
            for i, value in enumerate(values):
                if value is not None:
                    result[keys[i]] = self._deserialize(value)
                    self._stats["hits"] += 1
                else:
                    self._stats["misses"] += 1
            
            return result
            
        except Exception as e:
            logger.error(f"Cache mget error for keys {keys}: {str(e)}")
            self._stats["errors"] += 1
            return {}
    
    async def mset(self, mapping: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """Set multiple values in cache"""
        if not await self.health_check():
            return False
        
        try:
            self._stats["total_requests"] += 1
            ttl = ttl or self.config.default_ttl
            
            # Serialize all values
            serialized_mapping = {}
            for key, value in mapping.items():
                full_key = self._make_key(key)
                serialized_mapping[full_key] = self._serialize(value)
            
            # Set all values
            await self.client.mset(serialized_mapping)
            
            # Set TTL for all keys
            if ttl > 0:
                for key in mapping.keys():
                    await self.expire(key, ttl)
            
            self._stats["sets"] += len(mapping)
            return True
            
        except Exception as e:
            logger.error(f"Cache mset error for mapping {list(mapping.keys())}: {str(e)}")
            self._stats["errors"] += 1
            return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern"""
        if not await self.health_check():
            return 0
        
        try:
            full_pattern = self._make_key(pattern)
            keys = await self.client.keys(full_pattern)
            
            if keys:
                deleted = await self.client.delete(*keys)
                self._stats["deletes"] += deleted
                return deleted
            
            return 0
            
        except Exception as e:
            logger.error(f"Cache clear pattern error for pattern '{pattern}': {str(e)}")
            self._stats["errors"] += 1
            return 0
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        hit_rate = 0
        if self._stats["total_requests"] > 0:
            hit_rate = (self._stats["hits"] / self._stats["total_requests"]) * 100
        
        return {
            "connected": self._connected,
            "hit_rate_percent": round(hit_rate, 2),
            "total_requests": self._stats["total_requests"],
            "hits": self._stats["hits"],
            "misses": self._stats["misses"],
            "errors": self._stats["errors"],
            "sets": self._stats["sets"],
            "deletes": self._stats["deletes"],
            "config": {
                "host": self.config.host,
                "port": self.config.port,
                "db": self.config.db,
                "max_connections": self.config.max_connections,
                "default_ttl": self.config.default_ttl,
                "key_prefix": self.config.key_prefix
            }
        }
    
    async def reset_stats(self):
        """Reset cache statistics"""
        self._stats = {
            "hits": 0,
            "misses": 0,
            "errors": 0,
            "sets": 0,
            "deletes": 0,
            "total_requests": 0
        }
    
    @asynccontextmanager
    async def lock(self, key: str, timeout: int = 10):
        """Acquire distributed lock"""
        if not await self.health_check():
            raise Exception("Redis not connected")
        
        lock_key = self._make_key(f"lock:{key}")
        lock_value = str(time.time())
        
        try:
            # Try to acquire lock
            acquired = await self.client.set(lock_key, lock_value, nx=True, ex=timeout)
            if not acquired:
                raise Exception(f"Could not acquire lock for key '{key}'")
            
            yield
            
        finally:
            # Release lock
            try:
                # Use Lua script to ensure we only delete our own lock
                lua_script = """
                if redis.call("get", KEYS[1]) == ARGV[1] then
                    return redis.call("del", KEYS[1])
                else
                    return 0
                end
                """
                await self.client.eval(lua_script, 1, lock_key, lock_value)
            except Exception as e:
                logger.error(f"Failed to release lock for key '{key}': {str(e)}")


# Global cache service instance
_cache_service: Optional[RedisCacheService] = None


async def get_cache_service() -> RedisCacheService:
    """Get global cache service instance"""
    global _cache_service
    
    if _cache_service is None:
        # Create cache service from environment or default config
        config = CacheConfig(
            host=getattr(settings, 'redis_host', 'localhost'),
            port=getattr(settings, 'redis_port', 6379),
            db=getattr(settings, 'redis_db', 0),
            password=getattr(settings, 'redis_password', None),
            max_connections=getattr(settings, 'redis_max_connections', 20),
            default_ttl=getattr(settings, 'cache_default_ttl', 300),
            key_prefix=getattr(settings, 'cache_key_prefix', 'clipizy:')
        )
        
        _cache_service = RedisCacheService(config)
        await _cache_service.connect()
    
    return _cache_service


def cache_result(ttl: int = 300, key_prefix: str = ""):
    """Decorator to cache function results"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            cache_service = await get_cache_service()
            
            # Generate cache key
            cache_key = f"{key_prefix}{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            cached_result = await cache_service.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            await cache_service.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator


def cache_invalidate(pattern: str = ""):
    """Decorator to invalidate cache entries"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            
            # Invalidate cache entries matching pattern
            cache_service = await get_cache_service()
            if pattern:
                await cache_service.clear_pattern(pattern)
            
            return result
        
        return wrapper
    return decorator
