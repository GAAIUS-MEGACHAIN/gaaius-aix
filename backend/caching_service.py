"""
PHASE 9: Caching & Rate Limiting Service
Redis integration for high-performance caching
Rate limiting, throttling, and DDoS protection
"""

import os
import json
import hashlib
import time
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta, timezone
from functools import wraps
import logging

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

logger = logging.getLogger(__name__)


# ============================================================================
# REDIS CONFIGURATION
# ============================================================================

class CacheConfig:
    """Caching configuration"""
    REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.environ.get("REDIS_PORT", "6379"))
    REDIS_DB = int(os.environ.get("REDIS_DB", "0"))
    REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD")
    
    # Cache TTLs
    CACHE_TTL_SHORT = int(os.environ.get("CACHE_TTL_SHORT", "300"))  # 5 minutes
    CACHE_TTL_MEDIUM = int(os.environ.get("CACHE_TTL_MEDIUM", "3600"))  # 1 hour
    CACHE_TTL_LONG = int(os.environ.get("CACHE_TTL_LONG", "86400"))  # 24 hours
    
    # Rate limiting
    RATE_LIMIT_ENABLED = os.environ.get("RATE_LIMIT_ENABLED", "true").lower() == "true"
    RATE_LIMIT_REQUESTS_PER_MINUTE = int(os.environ.get("RATE_LIMIT_REQUESTS_PER_MINUTE", "60"))
    RATE_LIMIT_REQUESTS_PER_HOUR = int(os.environ.get("RATE_LIMIT_REQUESTS_PER_HOUR", "1000"))
    RATE_LIMIT_BURST_SIZE = int(os.environ.get("RATE_LIMIT_BURST_SIZE", "10"))


# ============================================================================
# REDIS CLIENT
# ============================================================================

class RedisClient:
    """Redis connection management"""
    
    def __init__(self):
        self.client = None
        self._connect()
    
    def _connect(self):
        """Connect to Redis"""
        if not REDIS_AVAILABLE:
            logger.warning("Redis client not available")
            return
        
        try:
            self.client = redis.Redis(
                host=CacheConfig.REDIS_HOST,
                port=CacheConfig.REDIS_PORT,
                db=CacheConfig.REDIS_DB,
                password=CacheConfig.REDIS_PASSWORD,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_keepalive=True,
                health_check_interval=30
            )
            
            # Test connection
            self.client.ping()
            logger.info(f"✅ Connected to Redis at {CacheConfig.REDIS_HOST}:{CacheConfig.REDIS_PORT}")
        except Exception as e:
            logger.warning(f"⚠️ Redis connection failed: {e}")
            self.client = None
    
    def is_connected(self) -> bool:
        """Check if connected to Redis"""
        if not self.client:
            return False
        
        try:
            self.client.ping()
            return True
        except:
            return False
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set cache value"""
        if not self.client:
            return False
        
        try:
            serialized = json.dumps(value) if isinstance(value, (dict, list)) else value
            self.client.setex(key, ttl, serialized)
            return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """Get cache value"""
        if not self.client:
            return None
        
        try:
            value = self.client.get(key)
            if value:
                try:
                    return json.loads(value)
                except:
                    return value
            return None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """Delete cache value"""
        if not self.client:
            return False
        
        try:
            self.client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists"""
        if not self.client:
            return False
        
        try:
            return self.client.exists(key) > 0
        except Exception as e:
            logger.error(f"Cache exists error: {e}")
            return False
    
    def increment(self, key: str, amount: int = 1) -> int:
        """Increment counter"""
        if not self.client:
            return 0
        
        try:
            return self.client.incrby(key, amount)
        except Exception as e:
            logger.error(f"Cache increment error: {e}")
            return 0
    
    def expire(self, key: str, ttl: int) -> bool:
        """Set expiration"""
        if not self.client:
            return False
        
        try:
            return self.client.expire(key, ttl)
        except Exception as e:
            logger.error(f"Cache expire error: {e}")
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """Clear keys by pattern"""
        if not self.client:
            return 0
        
        try:
            keys = self.client.keys(pattern)
            if keys:
                return self.client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache clear pattern error: {e}")
            return 0


# Global Redis client
redis_client = RedisClient()


# ============================================================================
# CACHE SERVICE
# ============================================================================

class CacheService:
    """High-level caching service"""
    
    @staticmethod
    def get_cache_key(*args) -> str:
        """Generate cache key from arguments"""
        key_str = ":".join(str(arg) for arg in args)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    @staticmethod
    def cache_content(content_id: str, content_data: Dict, ttl: int = CacheConfig.CACHE_TTL_LONG) -> bool:
        """Cache content data"""
        key = f"content:{content_id}"
        return redis_client.set(key, content_data, ttl)
    
    @staticmethod
    def get_cached_content(content_id: str) -> Optional[Dict]:
        """Get cached content"""
        key = f"content:{content_id}"
        return redis_client.get(key)
    
    @staticmethod
    def cache_user_preferences(user_id: str, preferences: Dict, ttl: int = CacheConfig.CACHE_TTL_MEDIUM) -> bool:
        """Cache user preferences"""
        key = f"user_prefs:{user_id}"
        return redis_client.set(key, preferences, ttl)
    
    @staticmethod
    def get_user_preferences(user_id: str) -> Optional[Dict]:
        """Get cached user preferences"""
        key = f"user_prefs:{user_id}"
        return redis_client.get(key)
    
    @staticmethod
    def cache_search_results(query: str, filters: Dict, results: List, ttl: int = CacheConfig.CACHE_TTL_MEDIUM) -> bool:
        """Cache search results"""
        key = f"search:{hashlib.md5(f'{query}:{json.dumps(filters)}'.encode()).hexdigest()}"
        return redis_client.set(key, results, ttl)
    
    @staticmethod
    def get_cached_search_results(query: str, filters: Dict) -> Optional[List]:
        """Get cached search results"""
        key = f"search:{hashlib.md5(f'{query}:{json.dumps(filters)}'.encode()).hexdigest()}"
        return redis_client.get(key)
    
    @staticmethod
    def cache_recommendations(user_id: str, recommendations: List, ttl: int = CacheConfig.CACHE_TTL_MEDIUM) -> bool:
        """Cache recommendations"""
        key = f"recommendations:{user_id}"
        return redis_client.set(key, recommendations, ttl)
    
    @staticmethod
    def get_cached_recommendations(user_id: str) -> Optional[List]:
        """Get cached recommendations"""
        key = f"recommendations:{user_id}"
        return redis_client.get(key)
    
    @staticmethod
    def cache_session(session_id: str, session_data: Dict, ttl: int = CacheConfig.CACHE_TTL_MEDIUM) -> bool:
        """Cache session"""
        key = f"session:{session_id}"
        return redis_client.set(key, session_data, ttl)
    
    @staticmethod
    def get_session(session_id: str) -> Optional[Dict]:
        """Get cached session"""
        key = f"session:{session_id}"
        return redis_client.get(key)
    
    @staticmethod
    def invalidate_user_cache(user_id: str) -> int:
        """Invalidate all user cache"""
        return redis_client.clear_pattern(f"user_prefs:{user_id}*")
    
    @staticmethod
    def invalidate_content_cache(content_id: str) -> int:
        """Invalidate content cache"""
        return redis_client.delete(f"content:{content_id}")


# ============================================================================
# RATE LIMITER
# ============================================================================

class RateLimiter:
    """Token bucket rate limiting"""
    
    @staticmethod
    def get_limit_key(identifier: str, limit_type: str = "minute") -> str:
        """Get rate limit key"""
        return f"ratelimit:{identifier}:{limit_type}"
    
    @staticmethod
    def check_rate_limit(
        identifier: str,
        limit: int,
        window_seconds: int
    ) -> tuple[bool, Dict]:
        """Check if request is within rate limit"""
        if not CacheConfig.RATE_LIMIT_ENABLED:
            return True, {"remaining": limit, "reset_at": None}
        
        key = RateLimiter.get_limit_key(identifier)
        
        try:
            current = redis_client.increment(key, 1)
            
            if current == 1:
                redis_client.expire(key, window_seconds)
            
            remaining = max(0, limit - current)
            reset_at = redis_client.client.ttl(key) if redis_client.client else window_seconds
            
            is_allowed = current <= limit
            
            return is_allowed, {
                "current": current,
                "limit": limit,
                "remaining": remaining,
                "reset_at": reset_at,
                "reset_in_seconds": reset_at if reset_at > 0 else 0
            }
        except Exception as e:
            logger.error(f"Rate limit check error: {e}")
            # Allow if Redis is down
            return True, {"remaining": limit}
    
    @staticmethod
    def check_per_minute(identifier: str) -> tuple[bool, Dict]:
        """Check per-minute rate limit"""
        return RateLimiter.check_rate_limit(
            identifier,
            CacheConfig.RATE_LIMIT_REQUESTS_PER_MINUTE,
            60
        )
    
    @staticmethod
    def check_per_hour(identifier: str) -> tuple[bool, Dict]:
        """Check per-hour rate limit"""
        return RateLimiter.check_rate_limit(
            identifier,
            CacheConfig.RATE_LIMIT_REQUESTS_PER_HOUR,
            3600
        )
    
    @staticmethod
    def reset_limit(identifier: str) -> bool:
        """Reset rate limit"""
        key = RateLimiter.get_limit_key(identifier)
        return redis_client.delete(key)


# ============================================================================
# CACHING DECORATOR
# ============================================================================

def cache_result(ttl: int = CacheConfig.CACHE_TTL_MEDIUM):
    """Decorator to cache function results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{func.__module__}:{func.__name__}:{str(args)}:{str(kwargs)}"
            cache_key = hashlib.md5(cache_key.encode()).hexdigest()
            
            # Try to get from cache
            cached = redis_client.get(cache_key)
            if cached is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached
            
            # Call function
            result = func(*args, **kwargs)
            
            # Cache result
            redis_client.set(cache_key, result, ttl)
            logger.debug(f"Cached result for {func.__name__}")
            
            return result
        
        return wrapper
    return decorator


# ============================================================================
# CIRCUIT BREAKER
# ============================================================================

class CircuitBreaker:
    """Circuit breaker for external service calls"""
    
    def __init__(self, name: str, failure_threshold: int = 5, timeout_seconds: int = 60):
        self.name = name
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
    
    def is_open(self) -> bool:
        """Check if circuit is open"""
        key = f"circuit_breaker:{self.name}:state"
        state = redis_client.get(key)
        return state == "open"
    
    def open(self) -> None:
        """Open circuit"""
        key = f"circuit_breaker:{self.name}:state"
        redis_client.set(key, "open", self.timeout_seconds)
        logger.warning(f"Circuit breaker {self.name} opened")
    
    def close(self) -> None:
        """Close circuit"""
        key = f"circuit_breaker:{self.name}:state"
        redis_client.delete(key)
        logger.info(f"Circuit breaker {self.name} closed")
    
    def record_failure(self) -> None:
        """Record failure"""
        key = f"circuit_breaker:{self.name}:failures"
        failures = redis_client.increment(key, 1)
        redis_client.expire(key, 60)
        
        if failures >= self.failure_threshold:
            self.open()
    
    def record_success(self) -> None:
        """Record success"""
        key = f"circuit_breaker:{self.name}:failures"
        redis_client.delete(key)


if __name__ == "__main__":
    print("🧪 Testing Caching & Rate Limiting\n")
    
    # Test Redis connection
    print(f"Redis connected: {redis_client.is_connected()}\n")
    
    # Test caching
    print("📦 Testing Cache Service:")
    test_data = {"id": "123", "title": "Test Content", "rating": 8.5}
    CacheService.cache_content("test_id", test_data)
    cached = CacheService.get_cached_content("test_id")
    print(f"  Cached: {cached}")
    
    # Test rate limiting
    print("\n⏱️ Testing Rate Limiting:")
    for i in range(5):
        allowed, info = RateLimiter.check_per_minute("user:123")
        print(f"  Request {i+1}: {'✅ Allowed' if allowed else '❌ Denied'} - Remaining: {info.get('remaining')}")
    
    # Test circuit breaker
    print("\n🔌 Testing Circuit Breaker:")
    cb = CircuitBreaker("external_api")
    for i in range(6):
        if cb.is_open():
            print(f"  {i+1}. Circuit is OPEN ❌")
        else:
            cb.record_failure()
            print(f"  {i+1}. Recorded failure - Is open now: {cb.is_open()}")
    
    print("\n✅ Caching & Rate Limiting configured successfully")
