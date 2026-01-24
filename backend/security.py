"""
PHASE 3: Security hardening module
Real security implementations: input validation, error handling, rate limiting
"""

from pydantic import BaseModel, validator, Field
from typing import Optional, List, Any
import re
import html
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# ============== INPUT SANITIZATION ==============

def sanitize_string(value: str, max_length: int = 5000) -> str:
    """Sanitize user input: remove HTML, limit length, trim whitespace"""
    if not isinstance(value, str):
        return ""
    
    # Remove NULL bytes
    value = value.replace('\x00', '')
    
    # Remove HTML tags
    value = re.sub(r'<[^>]+>', '', value)
    
    # Decode HTML entities
    value = html.unescape(value)
    
    # Trim whitespace
    value = value.strip()
    
    # Enforce max length
    if len(value) > max_length:
        value = value[:max_length]
    
    return value


def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_username(username: str) -> bool:
    """Validate username: alphanumeric, 3-32 chars, no special chars"""
    pattern = r'^[a-zA-Z0-9_-]{3,32}$'
    return bool(re.match(pattern, username))


def validate_video_id(video_id: str) -> bool:
    """Validate MongoDB ObjectId format"""
    return bool(re.match(r'^[a-f0-9]{24}$', video_id))


# ============== SECURITY MODELS ==============

class VideoUploadRequest(BaseModel):
    """Validated video upload request"""
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(default="", max_length=5000)
    tags: List[str] = Field(default=[], max_items=50)
    is_private: bool = Field(default=False)
    
    @validator('title')
    def sanitize_title(cls, v):
        return sanitize_string(v, max_length=200)
    
    @validator('description')
    def sanitize_description(cls, v):
        return sanitize_string(v, max_length=5000)
    
    @validator('tags')
    def validate_tags(cls, v):
        return [sanitize_string(tag, max_length=50) for tag in v]


class CommentRequest(BaseModel):
    """Validated comment request"""
    text: str = Field(..., min_length=1, max_length=1000)
    
    @validator('text')
    def sanitize_text(cls, v):
        return sanitize_string(v, max_length=1000)


class PlaylistRequest(BaseModel):
    """Validated playlist request"""
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(default="", max_length=1000)
    is_public: bool = Field(default=True)
    
    @validator('name')
    def sanitize_name(cls, v):
        return sanitize_string(v, max_length=100)
    
    @validator('description')
    def sanitize_description(cls, v):
        return sanitize_string(v, max_length=1000)


class SearchRequest(BaseModel):
    """Validated search request"""
    query: str = Field(..., min_length=1, max_length=100)
    limit: int = Field(default=20, ge=1, le=100)
    skip: int = Field(default=0, ge=0)
    
    @validator('query')
    def sanitize_query(cls, v):
        return sanitize_string(v, max_length=100)


# ============== ERROR HANDLING ==============

class SecurityError(Exception):
    """Custom security error"""
    def __init__(self, message: str, error_code: str = "ERR_SECURITY"):
        self.message = message
        self.error_code = error_code
        logger.warning(f"{error_code}: {message}")


class ValidationError(SecurityError):
    """Input validation error"""
    def __init__(self, message: str):
        super().__init__(message, "ERR_VALIDATION")


class AuthenticationError(SecurityError):
    """Authentication error"""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, "ERR_AUTH")


class AuthorizationError(SecurityError):
    """Authorization error"""
    def __init__(self, message: str = "Not authorized"):
        super().__init__(message, "ERR_AUTHZ")


def create_error_response(error_code: str, message: str = None) -> dict:
    """Create safe error response (doesn't leak internal details)"""
    error_messages = {
        "ERR_VALIDATION": "Invalid input provided",
        "ERR_AUTH": "Authentication failed",
        "ERR_AUTHZ": "Not authorized to access this resource",
        "ERR_NOT_FOUND": "Resource not found",
        "ERR_CONFLICT": "Resource already exists",
        "ERR_RATE_LIMIT": "Too many requests",
        "ERR_SERVER": "Internal server error",
    }
    
    return {
        "error": error_messages.get(error_code, "Unknown error"),
        "error_code": error_code,
        "timestamp": datetime.utcnow().isoformat()
    }


# ============== AUDIT LOGGING ==============

async def log_audit(
    action: str,
    user_id: Optional[str],
    resource_type: str,
    resource_id: str,
    status: str,
    details: Optional[dict] = None,
    ip_address: Optional[str] = None
):
    """
    Log sensitive operations for audit trail
    This should be called for: login, password change, deletion, admin actions
    """
    audit_entry = {
        "timestamp": datetime.utcnow(),
        "action": action,  # LOGIN, DELETE_VIDEO, CHANGE_PASSWORD, etc.
        "user_id": user_id,
        "resource_type": resource_type,  # VIDEO, USER, PAYMENT, etc.
        "resource_id": resource_id,
        "status": status,  # SUCCESS, FAILED, DENIED
        "details": details or {},
        "ip_address": ip_address
    }
    
    logger.info(f"AUDIT: {action} on {resource_type} {resource_id} by {user_id} - {status}")
    
    # TODO: Store in database for audit trail
    # if db and db.audit_logs:
    #     await db.audit_logs.insert_one(audit_entry)


# ============== RATE LIMITING HELPERS ==============

class RateLimitTracker:
    """Simple in-memory rate limit tracker"""
    def __init__(self):
        self.requests = {}
    
    def is_allowed(self, user_id: str, limit: int, window_seconds: int = 60) -> bool:
        """Check if user is within rate limit"""
        now = datetime.utcnow().timestamp()
        
        if user_id not in self.requests:
            self.requests[user_id] = []
        
        # Remove old requests outside window
        self.requests[user_id] = [
            ts for ts in self.requests[user_id]
            if now - ts < window_seconds
        ]
        
        # Check limit
        if len(self.requests[user_id]) >= limit:
            return False
        
        # Add current request
        self.requests[user_id].append(now)
        return True


# ============== SECURITY HEADERS ==============

def get_security_headers() -> dict:
    """Return security headers for all responses"""
    return {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Content-Security-Policy": "default-src 'self'; script-src 'self'",
        "Referrer-Policy": "strict-origin-when-cross-origin",
    }
