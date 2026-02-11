"""
PHASE 3: Advanced rate limiting for production
Protects endpoints from abuse and DoS attacks
"""

from fastapi import Request, HTTPException
from slowapi import Limiter, ASGIMiddleware
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from typing import Dict, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import time

# Configure rate limiter
limiter = Limiter(key_func=get_remote_address)


# Custom rate limit policies for different endpoint types
RATE_LIMITS = {
    # Auth endpoints - strict limits
    "auth_login": "5/minute",           # 5 attempts per minute
    "auth_register": "3/minute",        # 3 registrations per minute
    "auth_password_reset": "2/minute",  # 2 resets per minute
    
    # Video operations - moderate limits
    "video_upload": "10/hour",          # 10 uploads per hour
    "video_like": "100/minute",         # 100 likes per minute
    "video_comment": "30/minute",       # 30 comments per minute
    "video_share": "50/minute",         # 50 shares per minute
    
    # Search and list - higher limits
    "video_search": "60/minute",        # 60 searches per minute
    "video_list": "100/minute",         # 100 list requests per minute
    "channel_list": "60/minute",        # 60 channel requests per minute
    
    # API access - general limit
    "general": "1000/hour",             # 1000 requests per hour
}


class RateLimitMiddleware:
    """Custom rate limiting middleware with per-endpoint tracking"""
    
    def __init__(self):
        self.request_counts: Dict[str, list] = defaultdict(list)
        self.blocked_ips: Dict[str, datetime] = {}
    
    def is_ip_blocked(self, client_ip: str) -> bool:
        """Check if IP is temporarily blocked"""
        if client_ip in self.blocked_ips:
            if datetime.now() < self.blocked_ips[client_ip]:
                return True
            else:
                del self.blocked_ips[client_ip]
        return False
    
    def block_ip(self, client_ip: str, duration_minutes: int = 15):
        """Temporarily block an IP"""
        self.blocked_ips[client_ip] = datetime.now() + timedelta(minutes=duration_minutes)
    
    def get_request_count(self, client_ip: str, endpoint: str, 
                         window_seconds: int = 60) -> int:
        """Get request count within time window"""
        key = f"{client_ip}:{endpoint}"
        now = time.time()
        
        # Remove old requests outside window
        self.request_counts[key] = [
            req_time for req_time in self.request_counts[key]
            if now - req_time < window_seconds
        ]
        
        return len(self.request_counts[key])
    
    def track_request(self, client_ip: str, endpoint: str):
        """Track a request"""
        key = f"{client_ip}:{endpoint}"
        self.request_counts[key].append(time.time())
    
    def check_limit(self, client_ip: str, endpoint: str, 
                   limit: str) -> Tuple[bool, int]:
        """Check if request is within rate limit"""
        if self.is_ip_blocked(client_ip):
            return False, 0
        
        # Parse limit string (e.g., "100/minute" or "10/hour")
        parts = limit.split("/")
        if len(parts) != 2:
            return True, 0
        
        try:
            max_requests = int(parts[0])
            time_unit = parts[1].lower()
            
            # Convert to seconds
            window_seconds = {
                "second": 1,
                "minute": 60,
                "hour": 3600,
                "day": 86400
            }.get(time_unit, 60)
            
            count = self.get_request_count(client_ip, endpoint, window_seconds)
            
            if count >= max_requests:
                # Block after 3 limit violations in 5 minutes
                violation_key = f"{client_ip}:violations"
                if violation_key not in self.request_counts:
                    self.request_counts[violation_key] = []
                
                self.request_counts[violation_key].append(time.time())
                violations = len([
                    t for t in self.request_counts[violation_key]
                    if time.time() - t < 300  # 5 minute window
                ])
                
                if violations >= 3:
                    self.block_ip(client_ip, duration_minutes=15)
                
                return False, max_requests
            
            return True, max_requests
        
        except Exception as e:
            print(f"Rate limit check error: {e}")
            return True, 0


# Global rate limit middleware instance
rate_limit_middleware = RateLimitMiddleware()


async def check_rate_limit(request: Request, endpoint: str = None) -> bool:
    """Middleware to check rate limits"""
    
    client_ip = get_remote_address(request)
    endpoint = endpoint or request.url.path
    
    # Get limit for this endpoint
    limit = RATE_LIMITS.get(endpoint, RATE_LIMITS.get("general", "1000/hour"))
    
    # Check rate limit
    allowed, max_requests = rate_limit_middleware.check_limit(client_ip, endpoint, limit)
    
    if allowed:
        rate_limit_middleware.track_request(client_ip, endpoint)
        return True
    
    raise HTTPException(
        status_code=429,
        detail=f"Rate limit exceeded. Max {max_requests} requests allowed per {limit.split('/')[1]}"
    )


# Specific rate limit decorators for different endpoint types

def rate_limit_auth_login():
    """Rate limiter for login endpoint"""
    return limiter.limit(RATE_LIMITS["auth_login"])


def rate_limit_auth_register():
    """Rate limiter for registration endpoint"""
    return limiter.limit(RATE_LIMITS["auth_register"])


def rate_limit_video_upload():
    """Rate limiter for video upload endpoint"""
    return limiter.limit(RATE_LIMITS["video_upload"])


def rate_limit_video_search():
    """Rate limiter for video search endpoint"""
    return limiter.limit(RATE_LIMITS["video_search"])


def rate_limit_general():
    """General rate limiter"""
    return limiter.limit(RATE_LIMITS["general"])


# Export middleware for FastAPI
middleware = ASGIMiddleware(limiter)
