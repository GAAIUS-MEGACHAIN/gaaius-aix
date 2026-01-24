"""
Caching utility module for Podcast Platform.

Provides Redis-based caching for expensive operations with TTL support.
Falls back to in-memory caching if Redis is unavailable.
"""

import asyncio
import json
from typing import Any, Optional, Callable, Dict
from datetime import datetime, timedelta
import logging
from functools import wraps

logger = logging.getLogger(__name__)

# In-memory fallback cache
_memory_cache: Dict[str, tuple] = {}


class CacheManager:
    """Manager for caching operations with Redis fallback"""
    
    def __init__(self):
        """Initialize cache manager"""
        self.redis_available = False
        self.redis_client = None
        self._init_redis()
    
    def _init_redis(self):
        """Initialize Redis connection if available"""
        try:
            import redis.asyncio as redis_async
            # Try to connect to Redis
            # Note: Connection is lazy-loaded on first use
            self.redis_available = True
            logger.info("Redis caching enabled (connection will be lazy-loaded)")
        except ImportError:
            logger.info("Redis not available, using in-memory cache fallback")
    
    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        try:
            # Try Redis first
            if self.redis_available and self.redis_client:
                value = await self.redis_client.get(key)
                if value:
                    logger.debug(f"Cache HIT (Redis): {key}")
                    return json.loads(value)
            
            # Fall back to memory cache
            if key in _memory_cache:
                value, expiry = _memory_cache[key]
                if datetime.now() < expiry:
                    logger.debug(f"Cache HIT (Memory): {key}")
                    return value
                else:
                    del _memory_cache[key]  # Remove expired
            
            logger.debug(f"Cache MISS: {key}")
            return None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl_seconds: int = 3600):
        """
        Set value in cache with TTL
        
        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Time to live in seconds (default 1 hour)
        """
        try:
            # Try Redis first
            if self.redis_available and self.redis_client:
                await self.redis_client.setex(
                    key,
                    ttl_seconds,
                    json.dumps(value, default=str)
                )
                logger.debug(f"Cache SET (Redis): {key} ({ttl_seconds}s)")
                return
            
            # Fall back to memory cache
            expiry = datetime.now() + timedelta(seconds=ttl_seconds)
            _memory_cache[key] = (value, expiry)
            logger.debug(f"Cache SET (Memory): {key} ({ttl_seconds}s)")
        except Exception as e:
            logger.error(f"Cache set error: {e}")
    
    async def delete(self, key: str):
        """
        Delete value from cache
        
        Args:
            key: Cache key
        """
        try:
            if self.redis_available and self.redis_client:
                await self.redis_client.delete(key)
            
            if key in _memory_cache:
                del _memory_cache[key]
            
            logger.debug(f"Cache DELETE: {key}")
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
    
    async def clear_pattern(self, pattern: str):
        """
        Clear all keys matching pattern
        
        Args:
            pattern: Key pattern (e.g., "podcast:*")
        """
        try:
            if self.redis_available and self.redis_client:
                keys = await self.redis_client.keys(pattern)
                if keys:
                    await self.redis_client.delete(*keys)
                logger.debug(f"Cache CLEAR pattern (Redis): {pattern}")
            
            # Memory cache - simple prefix matching
            keys_to_delete = [k for k in _memory_cache.keys() if pattern.replace("*", "") in k]
            for k in keys_to_delete:
                del _memory_cache[k]
            
            if keys_to_delete:
                logger.debug(f"Cache CLEAR pattern (Memory): {pattern} ({len(keys_to_delete)} keys)")
        except Exception as e:
            logger.error(f"Cache clear pattern error: {e}")


# Global cache manager instance
cache_manager = CacheManager()


def cached(ttl: int = 3600, key_prefix: str = ""):
    """
    Decorator for caching async function results
    
    Args:
        ttl: Time to live in seconds
        key_prefix: Prefix for cache key
        
    Example:
        @cached(ttl=1800, key_prefix="podcasts")
        async def get_podcasts(limit: int):
            # Implementation
            pass
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Build cache key from function name and arguments
            cache_key = f"{key_prefix}:{func.__name__}"
            
            # Add arguments to cache key
            if args:
                cache_key += ":" + ":".join(str(a)[:10] for a in args)
            if kwargs:
                cache_key += ":" + ":".join(f"{k}={v}" for k, v in sorted(kwargs.items()))
            
            # Try to get from cache
            cached_value = await cache_manager.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Call function if not cached
            result = await func(*args, **kwargs)
            
            # Store in cache
            await cache_manager.set(cache_key, result, ttl)
            return result
        
        return wrapper
    return decorator


# Cache key constants
CACHE_KEYS = {
    "podcasts_list": "podcasts:list:{skip}:{limit}",
    "podcast_episodes": "podcast:{id}:episodes:{skip}:{limit}",
    "podcast_subscriptions": "podcast:subscriptions:{user_id}",
    "podcast_recommendations": "podcast:recommendations:{user_id}:{limit}",
    "trending_podcasts": "podcasts:trending:{limit}",
}
