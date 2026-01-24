# GAAIUS AI - Quick Fixes Implementation Guide

## 1. FIX SILENT ERROR HANDLER (CRITICAL)

**File**: `frontend/src/App.js:293`  
**Severity**: 🔴 CRITICAL - Breaks payment system silently

### Current Code:
```javascript
api.get("/payment/config").then(res => setPaypalClientId(res.data.paypal_client_id)).catch(() => {});
```

### Fixed Code:
```javascript
useEffect(() => {
  api.get("/payment/config")
    .then(res => {
      if (res.data?.paypal_client_id) {
        setPaypalClientId(res.data.paypal_client_id);
      } else {
        console.warn("PayPal client ID not found in config");
        toast.error("Payment system not configured");
      }
    })
    .catch(error => {
      console.error("Failed to load PayPal config:", error);
      toast.error("Payment system unavailable - please try again later");
    });
}, []);
```

---

## 2. ADD MIME TYPE VALIDATION (CRITICAL)

**File**: `backend/server.py` - All upload endpoints  
**Severity**: 🔴 CRITICAL - Security vulnerability

### Find and Replace:

**Location**: Image/Video/Audio upload endpoints

```python
# ADD AT TOP OF FILE:
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif", "image/bmp", "image/tiff"}
ALLOWED_VIDEO_TYPES = {"video/mp4", "video/mpeg", "video/quicktime", "video/webm"}
ALLOWED_AUDIO_TYPES = {"audio/mpeg", "audio/wav", "audio/ogg", "audio/aac", "audio/flac"}

# In each endpoint, ADD THIS VALIDATION:
@api_router.post("/image/resize")
async def resize_image(file: UploadFile = File(...)):
    # ✅ CRITICAL FIX: Add MIME type check
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid image format. Allowed: JPG, PNG, WebP, GIF, BMP, TIFF"
        )
    
    # ✅ CRITICAL FIX: Add file size check
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    
    MAX_IMAGE_SIZE = 50 * 1024 * 1024  # 50MB
    if file_size > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size: 50MB (You uploaded: {file_size / 1024 / 1024:.1f}MB)"
        )
    
    # REST OF CODE...
```

### Apply Same Pattern To:
- `POST /api/image/convert`
- `POST /api/videos/upload`
- `POST /api/music/upload`

---

## 3. FIX BARE EXCEPT CLAUSE (CRITICAL)

**File**: `backend/server.py:344`  
**Severity**: 🔴 CRITICAL - Hides errors

### Current Code:
```python
try:
    # code here
except:  # ❌ BARE EXCEPT
    pass
```

### Fixed Code:
```python
try:
    # code here
except Exception as e:
    logger.error(f"Database operation failed: {e}", exc_info=True)
    # Don't re-raise, just log - this maintains original behavior but with visibility
```

**Search for all bare `except:` statements**:
```bash
grep -n "except:" backend/server.py
```

Replace each one with proper exception handling.

---

## 4. ADD FILE SIZE VALIDATION (CRITICAL)

**File**: `backend/server.py` - Upload endpoints  
**Severity**: 🔴 CRITICAL - DoS vulnerability

### Create a Helper Function:

Add this to `backend/server.py`:

```python
async def validate_file(file: UploadFile, max_size_mb: int, allowed_types: set):
    """
    Validates uploaded file for type and size
    
    Args:
        file: Uploaded file
        max_size_mb: Maximum file size in MB
        allowed_types: Set of allowed MIME types
    
    Raises:
        HTTPException if validation fails
    """
    # Check MIME type
    if file.content_type not in allowed_types:
        allowed_str = ", ".join(sorted(allowed_types))
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type: {file.content_type}. Allowed types: {allowed_str}"
        )
    
    # Check file size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to start
    
    max_bytes = max_size_mb * 1024 * 1024
    if file_size > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File too large ({file_size / 1024 / 1024:.1f}MB). Maximum: {max_size_mb}MB"
        )
    
    return file_size

# Usage in endpoints:
@api_router.post("/image/resize")
async def resize_image(file: UploadFile = File(...)):
    await validate_file(file, max_size_mb=50, allowed_types=ALLOWED_IMAGE_TYPES)
    # Continue with processing...
```

---

## 5. FIX PAGINATION (HIGH PRIORITY)

**File**: `backend/server.py` - All list endpoints  
**Severity**: ⚠️ HIGH - Performance/DoS risk

### Current Code:
```python
@api_router.get("/api/music/tracks")
async def list_tracks(skip: int = 0, limit: int = 100):
    # ❌ No validation on limit
```

### Fixed Code:
```python
from pydantic import conint

@api_router.get("/api/music/tracks")
async def list_tracks(
    skip: conint(ge=0, le=100000) = 0,  # Max 100k skip
    limit: conint(ge=1, le=100) = 20,   # Default 20, max 100
):
    tracks = await db.tracks.find().skip(skip).limit(limit).to_list(None)
    total = await db.tracks.count_documents({})
    
    return {
        "data": tracks,
        "pagination": {
            "skip": skip,
            "limit": limit,
            "total": total,
            "has_more": (skip + limit) < total
        }
    }
```

### Apply To All Endpoints:
- `GET /api/music/tracks`
- `GET /api/music/playlists`
- `GET /api/videos/videos`
- `GET /marketplace/listings` (if exists)
- `GET /ads/campaigns` (if exists)

---

## 6. ADD DATABASE INDEXES (HIGH PRIORITY)

**File**: `backend/server.py` - Database initialization  
**Severity**: ⚠️ HIGH - Performance

### Add This Function:

```python
async def setup_database_indexes():
    """Initialize database indexes for optimal query performance"""
    
    try:
        # Image operations
        await db.resizes.create_index("user_id")
        await db.resizes.create_index("created_at", background=True)
        
        await db.conversions.create_index("user_id")
        await db.conversions.create_index("created_at", background=True)
        
        # Video operations
        await db.videos.create_index("user_id")
        await db.videos.create_index("title")
        await db.videos.create_index("tags")
        await db.videos.create_index("created_at")
        await db.videos.create_index([("title", "text"), ("description", "text")])  # Text index
        
        # Music operations
        await db.tracks.create_index("user_id")
        await db.tracks.create_index("title")
        await db.tracks.create_index("artist")
        await db.tracks.create_index([("title", "text"), ("artist", "text")])
        
        await db.playlists.create_index("user_id")
        await db.playlists.create_index("created_at")
        
        # Marketplace/Ads
        await db.marketplace_listings.create_index("user_id")
        await db.marketplace_listings.create_index("category")
        
        await db.ads_campaigns.create_index("user_id")
        await db.ads_campaigns.create_index("status")
        
        logger.info("Database indexes created successfully")
    except Exception as e:
        logger.error(f"Failed to create indexes: {e}")
        # Don't fail app startup if indexes fail

# Call this in startup event:
@app.on_event("startup")
async def startup_event():
    if db is not None:
        await setup_database_indexes()
```

---

## 7. ADD INPUT SANITIZATION (HIGH PRIORITY)

**File**: `frontend/src/App.js` - New feature components  
**Severity**: ⚠️ HIGH - XSS prevention

### Add Utility Function:

```javascript
// Add to top of App.js
const sanitizeInput = (input) => {
  if (typeof input !== 'string') return '';
  return input
    .replace(/[<>]/g, '')  // Remove angle brackets
    .trim()
    .substring(0, 500);    // Limit length
};

const validateImageDimensions = (width, height) => {
  const w = parseInt(width);
  const h = parseInt(height);
  
  if (isNaN(w) || isNaN(h)) return false;
  if (w < 1 || w > 10000) return false;
  if (h < 1 || h > 10000) return false;
  
  return { width: w, height: h };
};

// Usage in Image Resizer:
const handleResize = async () => {
  // Validate dimensions
  const dims = validateImageDimensions(resizeSettings.width, resizeSettings.height);
  if (!dims) {
    toast.error('Invalid dimensions. Width and height must be 1-10000 pixels');
    return;
  }
  
  // Sanitize format
  const validFormats = ['jpg', 'png', 'webp', 'gif'];
  const format = sanitizeInput(resizeSettings.format).toLowerCase();
  
  if (!validFormats.includes(format)) {
    toast.error('Invalid format. Use: ' + validFormats.join(', '));
    return;
  }
  
  // Rest of code...
};
```

---

## 8. ADD RATE LIMITING (HIGH PRIORITY)

**File**: `backend/server.py`  
**Severity**: ⚠️ HIGH - DoS protection

### Installation:
```bash
pip install slowapi
```

### Implementation:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_handler)

# Add to endpoints:
@api_router.post("/image/resize")
@limiter.limit("10/minute")  # 10 per minute per IP
async def resize_image(request: Request, file: UploadFile = File(...)):
    # Implementation...

@api_router.post("/api/music/upload")
@limiter.limit("5/minute")  # Stricter for uploads
async def upload_music(request: Request, file: UploadFile = File(...)):
    # Implementation...

@api_router.get("/api/music/tracks")
@limiter.limit("60/minute")  # More generous for reads
async def list_tracks(request: Request, skip: int = 0, limit: int = 20):
    # Implementation...
```

---

## 9. IMPROVE ERROR MESSAGES (MEDIUM)

**File**: `frontend/src/App.js` - All new components  
**Severity**: 🟡 MEDIUM - UX improvement

### Current (Bad):
```javascript
catch (error) {
  toast.error('Failed to resize image: ' + error.message);
}
```

### Better:
```javascript
catch (error) {
  let userMessage = 'Operation failed';
  
  if (error.response?.status === 413) {
    userMessage = 'File is too large. Please use a smaller file.';
  } else if (error.response?.status === 400) {
    const detail = error.response.data?.detail;
    if (detail?.includes('format')) {
      userMessage = 'Invalid file format. Supported formats: JPG, PNG, WebP, GIF';
    } else if (detail?.includes('size')) {
      userMessage = 'File size exceeds maximum limit (50MB for images, 500MB for videos)';
    } else {
      userMessage = detail || 'Invalid input provided';
    }
  } else if (error.response?.status === 429) {
    userMessage = 'Too many requests. Please wait a moment and try again.';
  } else if (error.code === 'ECONNABORTED') {
    userMessage = 'Request timed out. Please try again.';
  }
  
  toast.error(userMessage);
  console.error('Detailed error:', error);
}
```

---

## 10. VERIFICATION CHECKLIST

After implementing fixes, verify:

```bash
# 1. Test MIME validation
curl -X POST http://localhost:8000/api/image/resize \
  -F "file=@malicious.exe"
# Should return 400 error

# 2. Test file size limit
# Create 100MB file and try to upload
# Should return 413 error

# 3. Test rate limiting
for i in {1..15}; do
  curl http://localhost:8000/api/image/resize
done
# Should get 429 error after 10 requests

# 4. Check database indexes
python3 << 'EOF'
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def check_indexes():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['gaaius_ai']
    
    for collection_name in ['tracks', 'videos', 'playlists']:
        indexes = await db[collection_name].list_indexes()
        print(f"\n{collection_name} indexes:")
        async for index in indexes:
            print(f"  - {index['name']}")

asyncio.run(check_indexes())
EOF

# 5. Test error handling
# Shut down MongoDB and make API call
# Should get proper error message, not 500
```

---

## ESTIMATED TIME TO IMPLEMENT

- **Fix 1-3** (Critical): 30 minutes
- **Fix 4-5** (File validation): 45 minutes
- **Fix 6-8** (Indexes, sanitization, rate limit): 1.5 hours
- **Fix 9-10** (Error messages, verification): 1 hour

**Total**: ~4 hours to production-ready security

---

## TESTING COMMANDS

```bash
# Test image resize with validation
curl -X POST http://localhost:8000/api/image/resize \
  -F "file=@test.jpg" \
  -F "width=800" \
  -F "height=600" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Test oversized file
curl -X POST http://localhost:8000/api/image/resize \
  -F "file=@huge_file.jpg" \
  -H "Authorization: Bearer YOUR_TOKEN"
# Should return 413

# Test invalid format
curl -X POST http://localhost:8000/api/image/resize \
  -F "file=@malicious.exe" \
  -H "Authorization: Bearer YOUR_TOKEN"
# Should return 400

# Monitor logs for errors
tail -f logs/application.log
```

---

## DEPLOYMENT STEPS

1. **Backup Database**: `mongodump --out ./backup`
2. **Test Locally**: Run all fixes in test environment
3. **Run Tests**: `pytest tests/ -v`
4. **Deploy**: Push to production branch
5. **Monitor**: Check error logs for 24 hours
6. **Verify**: Test all endpoints with production data

---

## NEXT STEPS

1. ✅ Implement critical fixes (1-5)
2. ✅ Deploy to staging
3. ✅ Run security scan (OWASP)
4. ✅ Performance test (k6)
5. ✅ Deploy to production
6. 🚀 Begin advanced features roadmap
