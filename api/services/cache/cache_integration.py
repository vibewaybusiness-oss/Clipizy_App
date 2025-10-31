#!/usr/bin/env python3
"""
CACHE INTEGRATION SERVICE
Integration layer for caching with existing services
"""
import logging
from typing import Any, Dict, List, Optional, Callable, TypeVar, Union
from functools import wraps
import asyncio
import time

from api.services.cache.redis_cache import get_cache_service, cache_result, cache_invalidate

logger = logging.getLogger(__name__)

T = TypeVar('T')


class CacheIntegration:
    """Cache integration service for existing services"""
    
    def __init__(self):
        self.cache_service = None
        self._initialized = False
    
    async def initialize(self):
        """Initialize cache service"""
        if not self._initialized:
            self.cache_service = await get_cache_service()
            self._initialized = True
    
    async def get_or_set(
        self, 
        key: str, 
        fetch_func: Callable[[], Any], 
        ttl: int = 300,
        key_prefix: str = ""
    ) -> Any:
        """Get value from cache or fetch and cache it"""
        await self.initialize()
        
        full_key = f"{key_prefix}{key}"
        
        # Try to get from cache
        cached_value = await self.cache_service.get(full_key)
        if cached_value is not None:
            return cached_value
        
        # Fetch from source
        try:
            if asyncio.iscoroutinefunction(fetch_func):
                value = await fetch_func()
            else:
                value = fetch_func()
            
            # Cache the result
            await self.cache_service.set(full_key, value, ttl)
            return value
            
        except Exception as e:
            logger.error(f"Error fetching value for key '{key}': {str(e)}")
            raise
    
    async def invalidate_pattern(self, pattern: str):
        """Invalidate cache entries matching pattern"""
        await self.initialize()
        await self.cache_service.clear_pattern(pattern)
    
    async def invalidate_key(self, key: str, key_prefix: str = ""):
        """Invalidate specific cache key"""
        await self.initialize()
        full_key = f"{key_prefix}{key}"
        await self.cache_service.delete(full_key)
    
    async def warm_cache(self, keys_and_fetchers: Dict[str, Callable[[], Any]], ttl: int = 300):
        """Warm cache with multiple keys"""
        await self.initialize()
        
        tasks = []
        for key, fetch_func in keys_and_fetchers.items():
            task = self.get_or_set(key, fetch_func, ttl)
            tasks.append(task)
        
        await asyncio.gather(*tasks, return_exceptions=True)


# Global cache integration instance
_cache_integration = CacheIntegration()


async def get_cache_integration() -> CacheIntegration:
    """Get global cache integration instance"""
    return _cache_integration


def cached(ttl: int = 300, key_prefix: str = "", invalidate_on: Optional[List[str]] = None):
    """Decorator for caching function results"""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> T:
            cache_integration = await get_cache_integration()
            
            # Generate cache key
            cache_key = f"{key_prefix}{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            async def fetch_value():
                return await func(*args, **kwargs)
            
            return await cache_integration.get_or_set(cache_key, fetch_value, ttl)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> T:
            cache_integration = asyncio.create_task(get_cache_integration())
            
            # Generate cache key
            cache_key = f"{key_prefix}{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            def fetch_value():
                return func(*args, **kwargs)
            
            # Run in event loop
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(
                cache_integration.get_or_set(cache_key, fetch_value, ttl)
            )
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def cache_invalidate_pattern(pattern: str):
    """Decorator to invalidate cache patterns after function execution"""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> T:
            result = await func(*args, **kwargs)
            
            cache_integration = await get_cache_integration()
            await cache_integration.invalidate_pattern(pattern)
            
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> T:
            result = func(*args, **kwargs)
            
            # Run invalidation in event loop
            loop = asyncio.get_event_loop()
            cache_integration = asyncio.create_task(get_cache_integration())
            loop.run_until_complete(
                cache_integration.invalidate_pattern(pattern)
            )
            
            return result
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


class CacheableService:
    """Base class for services that support caching"""
    
    def __init__(self):
        self.cache_integration = None
        self._cache_initialized = False
    
    async def _init_cache(self):
        """Initialize cache integration"""
        if not self._cache_initialized:
            self.cache_integration = await get_cache_integration()
            self._cache_initialized = True
    
    async def cache_get(self, key: str, key_prefix: str = "") -> Optional[Any]:
        """Get value from cache"""
        await self._init_cache()
        full_key = f"{key_prefix}{key}"
        return await self.cache_integration.cache_service.get(full_key)
    
    async def cache_set(self, key: str, value: Any, ttl: int = 300, key_prefix: str = ""):
        """Set value in cache"""
        await self._init_cache()
        full_key = f"{key_prefix}{key}"
        await self.cache_integration.cache_service.set(full_key, value, ttl)
    
    async def cache_delete(self, key: str, key_prefix: str = ""):
        """Delete value from cache"""
        await self._init_cache()
        full_key = f"{key_prefix}{key}"
        await self.cache_integration.cache_service.delete(full_key)
    
    async def cache_invalidate_pattern(self, pattern: str):
        """Invalidate cache pattern"""
        await self._init_cache()
        await self.cache_integration.invalidate_pattern(pattern)


# Database query caching
class DatabaseCacheMixin:
    """Mixin for database services to add caching capabilities"""
    
    async def cached_query(
        self, 
        query_key: str, 
        query_func: Callable[[], Any], 
        ttl: int = 300
    ) -> Any:
        """Execute cached database query"""
        cache_integration = await get_cache_integration()
        return await cache_integration.get_or_set(
            f"db_query:{query_key}", 
            query_func, 
            ttl
        )
    
    async def invalidate_query_cache(self, table_name: str):
        """Invalidate all cached queries for a table"""
        cache_integration = await get_cache_integration()
        await cache_integration.invalidate_pattern(f"db_query:*{table_name}*")


# API response caching
class APICacheMixin:
    """Mixin for API services to add response caching"""
    
    async def cached_api_call(
        self, 
        endpoint_key: str, 
        api_func: Callable[[], Any], 
        ttl: int = 300
    ) -> Any:
        """Execute cached API call"""
        cache_integration = await get_cache_integration()
        return await cache_integration.get_or_set(
            f"api_call:{endpoint_key}", 
            api_func, 
            ttl
        )
    
    async def invalidate_api_cache(self, service_name: str):
        """Invalidate all cached API calls for a service"""
        cache_integration = await get_cache_integration()
        await cache_integration.invalidate_pattern(f"api_call:*{service_name}*")


# User session caching
class SessionCacheMixin:
    """Mixin for user session caching"""
    
    async def cache_user_session(self, user_id: str, session_data: Dict[str, Any], ttl: int = 3600):
        """Cache user session data"""
        cache_integration = await get_cache_integration()
        await cache_integration.cache_service.set(
            f"user_session:{user_id}", 
            session_data, 
            ttl
        )
    
    async def get_user_session(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get cached user session data"""
        cache_integration = await get_cache_integration()
        return await cache_integration.cache_service.get(f"user_session:{user_id}")
    
    async def invalidate_user_session(self, user_id: str):
        """Invalidate user session cache"""
        cache_integration = await get_cache_integration()
        await cache_integration.cache_service.delete(f"user_session:{user_id}")
    
    async def invalidate_all_user_sessions(self):
        """Invalidate all user session caches"""
        cache_integration = await get_cache_integration()
        await cache_integration.invalidate_pattern("user_session:*")


# File processing caching
class FileCacheMixin:
    """Mixin for file processing caching"""
    
    async def cache_file_metadata(self, file_hash: str, metadata: Dict[str, Any], ttl: int = 86400):
        """Cache file metadata"""
        cache_integration = await get_cache_integration()
        await cache_integration.cache_service.set(
            f"file_metadata:{file_hash}", 
            metadata, 
            ttl
        )
    
    async def get_file_metadata(self, file_hash: str) -> Optional[Dict[str, Any]]:
        """Get cached file metadata"""
        cache_integration = await get_cache_integration()
        return await cache_integration.cache_service.get(f"file_metadata:{file_hash}")
    
    async def invalidate_file_cache(self, file_hash: str):
        """Invalidate file cache"""
        cache_integration = await get_cache_integration()
        await cache_integration.cache_service.delete(f"file_metadata:{file_hash}")


# Cache warming utilities
class CacheWarmer:
    """Utility for warming cache with frequently accessed data"""
    
    def __init__(self):
        self.cache_integration = None
    
    async def initialize(self):
        """Initialize cache integration"""
        self.cache_integration = await get_cache_integration()
    
    async def warm_user_data(self, user_ids: List[str]):
        """Warm cache with user data"""
        await self.initialize()
        
        # This would integrate with your user service
        # Example implementation
        for user_id in user_ids:
            try:
                # Fetch user data and cache it
                # user_data = await user_service.get_user(user_id)
                # await self.cache_integration.cache_service.set(f"user:{user_id}", user_data, 3600)
                pass
            except Exception as e:
                logger.error(f"Failed to warm cache for user {user_id}: {str(e)}")
    
    async def warm_system_data(self):
        """Warm cache with system-wide data"""
        await self.initialize()
        
        # Cache system configuration, settings, etc.
        try:
            # system_config = await config_service.get_system_config()
            # await self.cache_integration.cache_service.set("system_config", system_config, 1800)
            pass
        except Exception as e:
            logger.error(f"Failed to warm system data cache: {str(e)}")
    
    async def warm_frequently_accessed_data(self):
        """Warm cache with frequently accessed data"""
        await self.initialize()
        
        # Cache popular content, trending items, etc.
        try:
            # popular_content = await content_service.get_popular_content()
            # await self.cache_integration.cache_service.set("popular_content", popular_content, 600)
            pass
        except Exception as e:
            logger.error(f"Failed to warm frequently accessed data cache: {str(e)}")


# Global cache warmer instance
_cache_warmer = CacheWarmer()


async def get_cache_warmer() -> CacheWarmer:
    """Get global cache warmer instance"""
    return _cache_warmer
