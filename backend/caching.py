"""
PHASE 3: Redis caching layer for performance optimization
Caches all expensive operations (DB queries, AI calls, etc)
"""

import redis
import json
from typing import Any, Optional, Callable
from functools import wraps
from datetime import datetime, timedelta
import os
import pickle


class CacheManager:
    """Manage Redis caching for all operations"""
    
    def __init__(self):
        self.redis_host = os.environ.get('REDIS_HOST', 'localhost')
        self.redis_port = int(os.environ.get('REDIS_PORT', 6379))
        self.redis_db = int(os.environ.get('REDIS_DB', 0))
        self.ttl = int(os.environ.get('CACHE_TTL', 3600))  # 1 hour default
        
        try:
            self.client = redis.Redis(
                host=self.redis_host,
                port=self.redis_port,
                db=self.redis_db,
                decode_responses=True,
                socket_connect_timeout=5
            )
            self.client.ping()
            self.available = True
        except Exception as e:
            print(f"Redis not available: {e}")
            self.available = False
            self.client = None
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.available:
            return None
        
        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"Cache get error: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        if not self.available:
            return False
        
        try:
            ttl = ttl or self.ttl
            self.client.setex(
                key,
                ttl,
                json.dumps(value, default=str)
            )
            return True
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self.available:
            return False
        
        try:
            self.client.delete(key)
            return True
        except Exception:
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern"""
        if not self.available:
            return 0
        
        try:
            keys = self.client.keys(pattern)
            if keys:
                return self.client.delete(*keys)
            return 0
        except Exception:
            return 0
    
    def exists(self, key: str) -> bool:
        """Check if key exists"""
        if not self.available:
            return False
        
        try:
            return self.client.exists(key) > 0
        except Exception:
            return False


def cache_route(ttl: int = 3600, key_prefix: str = ""):
    """Decorator to cache route responses"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache = CacheManager()
            
            # Build cache key
            cache_key = f"{key_prefix}:{func.__name__}:{str(args)}:{str(kwargs)}"
            cache_key = cache_key.replace(" ", "").replace("'", "")
            
            # Try to get from cache
            cached = cache.get(cache_key)
            if cached is not None:
                return cached
            
            # Call function
            result = await func(*args, **kwargs)
            
            # Cache result
            cache.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator


def cache_db_query(ttl: int = 3600, key_prefix: str = ""):
    """Decorator to cache database queries"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache = CacheManager()
            
            # Build cache key
            cache_key = f"db:{key_prefix}:{func.__name__}:{str(kwargs)}"
            cache_key = cache_key.replace(" ", "").replace("'", "")
            
            # Try to get from cache
            cached = cache.get(cache_key)
            if cached is not None:
                return cached
            
            # Call function
            result = await func(*args, **kwargs)
            
            # Cache result
            cache.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator


# Cache key patterns for different data types
CACHE_PATTERNS = {
    "videos": "cache:videos:*",
    "users": "cache:users:*",
    "comments": "cache:comments:*",
    "playlists": "cache:playlists:*",
    "channels": "cache:channels:*",
    "chat": "cache:chat:*",
    "ai_responses": "cache:ai:*",
}


class VideoCacheService:
    """Cache service for video operations"""
    
    def __init__(self):
        self.cache = CacheManager()
    
    async def get_video(self, video_id: str):
        """Get video from cache or DB"""
        key = f"cache:videos:get:{video_id}"
        cached = self.cache.get(key)
        
        if cached:
            return cached
        
        # TODO: Fetch from DB and cache
        return None
    
    async def get_video_list(self, page: int = 1, limit: int = 20):
        """Get video list from cache"""
        key = f"cache:videos:list:{page}:{limit}"
        cached = self.cache.get(key)
        
        if cached:
            return cached
        
        # TODO: Fetch from DB and cache
        return []
    
    def invalidate_video(self, video_id: str):
        """Invalidate video cache on update"""
        self.cache.delete(f"cache:videos:get:{video_id}")
        self.cache.clear_pattern("cache:videos:list:*")
    
    def invalidate_channel_videos(self, channel_id: str):
        """Invalidate all videos in a channel"""
        self.cache.clear_pattern(f"cache:videos:channel:{channel_id}:*")


class UserCacheService:
    """Cache service for user operations"""
    
    def __init__(self):
        self.cache = CacheManager()
    
    async def get_user(self, user_id: str):
        """Get user from cache"""
        key = f"cache:users:get:{user_id}"
        cached = self.cache.get(key)
        
        if cached:
            return cached
        
        # TODO: Fetch from DB and cache
        return None
    
    async def get_user_profile(self, username: str):
        """Get user profile from cache"""
        key = f"cache:users:profile:{username}"
        cached = self.cache.get(key)
        
        if cached:
            return cached
        
        # TODO: Fetch from DB and cache
        return None
    
    def invalidate_user(self, user_id: str):
        """Invalidate user cache on update"""
        self.cache.delete(f"cache:users:get:{user_id}")
        self.cache.clear_pattern("cache:users:profile:*")


class ChatCacheService:
    """Cache service for chat operations"""
    
    def __init__(self):
        self.cache = CacheManager()
    
    async def get_chat_history(self, session_id: str):
        """Get chat history from cache"""
        key = f"cache:chat:history:{session_id}"
        cached = self.cache.get(key)
        
        if cached:
            return cached
        
        # TODO: Fetch from DB and cache with shorter TTL
        return []
    
    async def get_ai_response(self, prompt_hash: str):
        """Get cached AI response (expensive operation)"""
        key = f"cache:ai:response:{prompt_hash}"
        cached = self.cache.get(key)
        
        if cached:
            return cached
        
        # TODO: Call AI API and cache for longer TTL (24 hours)
        return None
    
    def invalidate_chat_session(self, session_id: str):
        """Invalidate chat cache on new message"""
        self.cache.delete(f"cache:chat:history:{session_id}")


# Global cache manager instance
cache_manager = CacheManager()
video_cache = VideoCacheService()
user_cache = UserCacheService()
chat_cache = ChatCacheService()


# Cache statistics tracking
class CacheStats:
    """Track cache hit/miss statistics"""
    
    def __init__(self):
        self.hits = 0
        self.misses = 0
        self.sets = 0
    
    def hit(self):
        self.hits += 1
    
    def miss(self):
        self.misses += 1
    
    def set(self):
        self.sets += 1
    
    def get_stats(self):
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        
        return {
            "hits": self.hits,
            "misses": self.misses,
            "sets": self.sets,
            "total_requests": total,
            "hit_rate": round(hit_rate, 2)
        }


cache_stats = CacheStats()
