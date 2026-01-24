# 🔐 PHASE 3.1: SECURITY HARDENING IMPLEMENTATION

## Overview
This guide covers critical security improvements needed before production deployment.

---

## 1. Security Assessment

### Current State
✅ JWT authentication implemented
✅ Rate limiting with slowapi
⚠️ Input validation needs review
⚠️ Error messages may leak information
⚠️ No CORS configuration visible
⚠️ No HTTPS enforcement

### Target State
✅ OWASP Top 10 compliance
✅ Zero critical vulnerabilities
✅ Encrypted sensitive data
✅ Secure error handling
✅ CORS properly configured

---

## 2. Critical Security Updates

### A. Input Validation Hardening

**File:** `backend/server.py`

**Changes Needed:**
1. Add stricter Pydantic models with validators
2. Implement request size limits
3. Add file upload validation
4. Sanitize all string inputs

```python
from pydantic import BaseModel, validator, Field
import bleach

class VideoUploadRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., max_length=5000)
    tags: list = Field(default=[], max_items=50)
    
    @validator('title', 'description')
    def sanitize_text(cls, v):
        # Remove potentially harmful HTML
        return bleach.clean(v, tags=[], strip=True)
    
    @validator('tags')
    def validate_tags(cls, v):
        return [bleach.clean(tag, tags=[], strip=True) for tag in v]
```

### B. Error Handling Security

**Current Risk:** Error messages may expose internal details

**Solution:**
```python
# Instead of:
return {"error": str(exception)}

# Use:
return {
    "error": "Internal server error",
    "error_code": "ERR_001"
}

# Log detailed error server-side only
logger.error(f"Detailed error: {str(exception)}")
```

### C. CORS Configuration

Add to `backend/server.py`:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Specific domain, not "*"
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
    max_age=3600,  # Cache preflight requests
)
```

### D. Rate Limiting Enhancement

Ensure all 204 endpoints have rate limiting:
```python
# Verify each endpoint has:
@api_router.get("/endpoint")
@limiter.limit("100/minute")  # Per endpoint configuration
async def endpoint():
    pass
```

### E. HTTPS Enforcement

Add middleware to enforce HTTPS:
```python
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

app.add_middleware(HTTPSRedirectMiddleware)
```

---

## 3. Database Security

### A. Connection Encryption

Update MongoDB connection string:
```python
MONGODB_URL = "mongodb+srv://user:password@cluster.mongodb.net/database?retryWrites=true&w=majority&tls=true"
```

### B. Query Injection Prevention

All queries should use parameterized queries (Motor does this by default):
```python
# Good - parameterized
result = await db.videos.find_one({"_id": ObjectId(video_id)})

# Bad - string concatenation (never do this)
result = await db.videos.find_one({"_id": ObjectId(video_id + "extra")})
```

### C. Sensitive Data Protection

Ensure sensitive fields are not exposed in API responses:
```python
class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    # NEVER include password_hash, api_keys, etc.
```

---

## 4. API Key Management

### A. Implement Secure API Key Storage

```python
import hashlib
from datetime import datetime, timedelta

async def create_api_key(user_id: str):
    """Create and hash API key"""
    import secrets
    api_key = secrets.token_urlsafe(32)
    api_key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    
    await db.api_keys.insert_one({
        "user_id": user_id,
        "key_hash": api_key_hash,
        "created_at": datetime.utcnow(),
        "expires_at": datetime.utcnow() + timedelta(days=365),
        "last_used": None
    })
    
    return api_key  # Return only once to user

async def validate_api_key(api_key: str):
    """Validate API key against hash"""
    api_key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    return await db.api_keys.find_one({"key_hash": api_key_hash})
```

---

## 5. Audit Logging

### A. Log Sensitive Operations

```python
async def log_audit(action: str, user_id: str, resource: str, details: dict):
    """Log all sensitive operations"""
    await db.audit_logs.insert_one({
        "timestamp": datetime.utcnow(),
        "action": action,
        "user_id": user_id,
        "resource": resource,
        "details": details,
        "ip_address": request.client.host  # Capture IP for security
    })

# Usage:
@api_router.delete("/videos/{video_id}")
async def delete_video(video_id: str, user = Depends(get_current_user)):
    # ... deletion logic ...
    await log_audit("DELETE_VIDEO", user.id, video_id, {"status": "success"})
```

---

## 6. Dependency Vulnerability Check

### Before Deployment

```bash
# Check Python dependencies for vulnerabilities
pip install safety
safety check

# Or use Snyk
snyk test
```

---

## 7. Secret Management

### A. Environment Variables

Never commit secrets to code:
```bash
# .env (NOT committed to git)
DATABASE_URL=mongodb+srv://...
JWT_SECRET=your-secret-key-here
API_KEY=...
```

### B. Secret Rotation

Implement periodic secret rotation:
- JWT secret rotation every 90 days
- API key expiration (365 days default)
- Database password rotation (every 90 days)

---

## 8. Security Headers

Add security headers to all responses:
```python
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response
```

---

## 9. Rate Limiting - Per User

Current implementation is per-endpoint. Enhance with per-user tracking:
```python
@limiter.limit("1000/day")  # Per user per day
async def endpoint(user = Depends(get_current_user)):
    pass
```

---

## 10. Implementation Checklist

- [ ] Run code security scan (Snyk)
- [ ] Add input validation to all 204 endpoints
- [ ] Implement CORS security policy
- [ ] Add error handling without leaking details
- [ ] Encrypt database connections
- [ ] Implement API key hashing
- [ ] Add audit logging
- [ ] Add security headers
- [ ] Implement secret rotation
- [ ] Dependency vulnerability scan
- [ ] Load testing for rate limiting
- [ ] Penetration testing (optional but recommended)

---

## Files to Update

1. `backend/server.py` - Main API file (add validators, headers, CORS)
2. `backend/requirements.txt` - Add security libraries
3. `.env.example` - Document environment variables
4. New: `backend/security.py` - Security utilities
5. New: `backend/audit_logger.py` - Audit logging

---

## Testing Security

### SQL/NoSQL Injection Testing
```python
# Test with malicious input
test_id = "'; DROP TABLE users; --"
result = await db.videos.find_one({"_id": ObjectId(test_id)})
# Should handle gracefully with ObjectId conversion
```

### XSS Prevention Testing
```python
# Test with script tags
malicious_title = "<script>alert('XSS')</script>"
# Should be sanitized
clean_title = validator.sanitize(malicious_title)
# Result: sanitized and safe
```

---

**Next Phase:** Implement these security updates before production deployment.

