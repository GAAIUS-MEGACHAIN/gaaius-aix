# ⚡ QUICK FIXES GUIDE - Copy/Paste Solutions

**Goal:** Make GAAIUS AI production-safe in ~6 hours  
**Method:** Apply fixes one by one, test each one

---

## FIX #1: Bare Except Clause (15 min) - CRITICAL

### Step 1: Locate the Code
**File:** `backend/server.py` around line 340-345

### Step 2: Current Code
```python
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        decoded = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=['HS256'])
        return decoded
    except:
        raise HTTPException(status_code=401)
```

### Step 3: Replace With
```python
import logging
logger = logging.getLogger(__name__)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        decoded = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=['HS256'])
        return decoded
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.ExpiredSignatureError:
        logger.warning("Token expired")
        raise HTTPException(status_code=401, detail="Token expired")
    except Exception as e:
        logger.error(f"Unexpected auth error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
```

### Step 4: Test
```bash
# Test with invalid token
curl -H "Authorization: Bearer invalid" http://localhost:8000/api/profile
# Should return 401 with proper error message
```

---

## FIX #2: File Type Validation (30 min) - CRITICAL

### Add at Top of `backend/server.py` (after imports)
```python
# File upload security constants
ALLOWED_IMAGE_TYPES = {'image/jpeg', 'image/png', 'image/webp', 'image/gif', 'image/bmp', 'image/tiff'}
ALLOWED_AUDIO_TYPES = {'audio/mpeg', 'audio/wav', 'audio/ogg', 'audio/mp4', 'audio/aac'}
ALLOWED_VIDEO_TYPES = {'video/mp4', 'video/webm', 'video/mpeg', 'video/quicktime'}

MAX_IMAGE_SIZE = 50 * 1024 * 1024  # 50MB
MAX_AUDIO_SIZE = 100 * 1024 * 1024  # 100MB
MAX_VIDEO_SIZE = 500 * 1024 * 1024  # 500MB

def validate_file(file: UploadFile, allowed_types: set, max_size: int) -> bool:
    """Validate file type and size"""
    if file.content_type not in allowed_types:
        raise HTTPException(400, f"Invalid file type. Allowed: {', '.join(allowed_types)}")
    
    # Size validation
    if hasattr(file, 'size') and file.size > max_size:
        raise HTTPException(413, f"File too large. Max size: {max_size / (1024*1024):.0f}MB")
    
    return True
```

### Update Image Resize Endpoint
```python
@app.post("/api/image/resize")
async def resize_image(file: UploadFile = File(...)):
    # Add validation
    validate_file(file, ALLOWED_IMAGE_TYPES, MAX_IMAGE_SIZE)
    
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        # ... rest of code
    except Exception as e:
        logger.error(f"Image resize failed: {e}", exc_info=True)
        raise HTTPException(500, "Image processing failed")
```

### Update Image Convert Endpoint
```python
@app.post("/api/image/convert")
async def convert_image(file: UploadFile = File(...)):
    # Add validation
    validate_file(file, ALLOWED_IMAGE_TYPES, MAX_IMAGE_SIZE)
    
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        # ... rest of code
    except Exception as e:
        logger.error(f"Image convert failed: {e}", exc_info=True)
        raise HTTPException(500, "Image conversion failed")
```

### Update Music Upload
```python
@app.post("/api/music/upload")
async def upload_track(file: UploadFile = File(...), ...):
    # Add validation
    validate_file(file, ALLOWED_AUDIO_TYPES, MAX_AUDIO_SIZE)
    
    try:
        contents = await file.read()
        # ... rest of code
    except Exception as e:
        logger.error(f"Music upload failed: {e}", exc_info=True)
        raise HTTPException(500, "Upload failed")
```

### Update Video Upload
```python
@app.post("/api/videos/upload")
async def upload_video(file: UploadFile = File(...), ...):
    # Add validation
    validate_file(file, ALLOWED_VIDEO_TYPES, MAX_VIDEO_SIZE)
    
    try:
        contents = await file.read()
        # ... rest of code
    except Exception as e:
        logger.error(f"Video upload failed: {e}", exc_info=True)
        raise HTTPException(500, "Upload failed")
```

---

## FIX #3: CORS Security (15 min) - HIGH

### Find This in `backend/server.py`
```python
# Around line 280
CORSMiddleware(
    app,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Replace With
```python
# Security: Only allow specific origins
ALLOWED_ORIGINS = [
    "https://yourdomain.com",
    "https://www.yourdomain.com",
    "https://app.yourdomain.com",
]

# Allow localhost for development
if os.environ.get("ENV", "production") == "development":
    ALLOWED_ORIGINS.extend([
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
    ])

CORSMiddleware(
    app,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
    max_age=3600,
)
```

---

## FIX #4: Rate Limiting (45 min) - HIGH

### Step 1: Install Package
```bash
pip install slowapi
```

### Step 2: Add to `backend/server.py` (after imports)
```python
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
```

### Step 3: Add Exception Handler
```python
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request, exc):
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests. Please try again later."}
    )
```

### Step 4: Add Rate Limits to Key Endpoints
```python
# Authentication endpoints - strict limits
@app.post("/api/auth/register")
@limiter.limit("5/hour")
async def register(data: UserRegister):
    # ... code

@app.post("/api/auth/login")
@limiter.limit("10/hour")
async def login(data: UserLogin):
    # ... code

# Upload endpoints - moderate limits
@app.post("/api/image/resize")
@limiter.limit("20/hour")
async def resize_image(file: UploadFile = File(...)):
    # ... code

@app.post("/api/image/convert")
@limiter.limit("20/hour")
async def convert_image(file: UploadFile = File(...)):
    # ... code

@app.post("/api/music/upload")
@limiter.limit("10/hour")
async def upload_track(...):
    # ... code

@app.post("/api/videos/upload")
@limiter.limit("5/hour")
async def upload_video(...):
    # ... code

# Read endpoints - generous limits
@app.get("/api/posts")
@limiter.limit("100/minute")
async def get_posts(...):
    # ... code

@app.get("/api/music/tracks")
@limiter.limit("100/minute")
async def get_tracks(...):
    # ... code
```

---

## FIX #5: Input Validation with Pydantic (90 min) - HIGH

### Add Models to `backend/server.py`
```python
from pydantic import BaseModel, Field, validator
from typing import List, Optional

# Marketplace Listing Model
class ListingCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., max_length=5000)
    price_usd: float = Field(..., gt=0, le=999999)
    category: str = Field(..., min_length=1, max_length=100)
    
    @validator('title', 'category')
    def no_html_tags(cls, v):
        if '<' in v or '>' in v:
            raise ValueError('HTML tags not allowed')
        return v.strip()

# Post Model
class PostCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    content: str = Field(..., min_length=1, max_length=10000)
    tags: Optional[List[str]] = []
    
    @validator('tags')
    def validate_tags(cls, v):
        if len(v) > 10:
            raise ValueError('Maximum 10 tags allowed')
        for tag in v:
            if len(tag) > 50:
                raise ValueError('Tag too long')
        return v

# Music Track Model
class TrackCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    artist: str = Field(..., min_length=1, max_length=200)
    album: str = Field(..., min_length=1, max_length=200)
    duration: int = Field(..., gt=0, le=86400)  # max 24 hours

# Video Model
class VideoCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    description: str = Field(..., max_length=10000)
    tags: Optional[List[str]] = []
    thumbnail_url: Optional[str] = None

# Comment Model
class CommentCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000)
    post_id: str
```

### Update Endpoints to Use Models
```python
@app.post("/api/marketplace/listings")
@limiter.limit("20/hour")
async def create_listing(data: ListingCreate, user = Depends(get_current_user)):
    if not user:
        raise HTTPException(401, "Not authenticated")
    
    try:
        listing = {
            **data.dict(),
            "user_id": user["id"],
            "created_at": datetime.utcnow()
        }
        result = await db.listings.insert_one(listing)
        return {"_id": str(result.inserted_id), **listing}
    except Exception as e:
        logger.error(f"Create listing failed: {e}", exc_info=True)
        raise HTTPException(500, "Failed to create listing")

@app.post("/api/posts")
@limiter.limit("30/hour")
async def create_post(data: PostCreate, user = Depends(get_current_user)):
    if not user:
        raise HTTPException(401, "Not authenticated")
    
    try:
        post = {
            **data.dict(),
            "user_id": user["id"],
            "created_at": datetime.utcnow(),
            "likes": 0,
            "comments": 0
        }
        result = await db.posts.insert_one(post)
        return {"_id": str(result.inserted_id), **post}
    except Exception as e:
        logger.error(f"Create post failed: {e}", exc_info=True)
        raise HTTPException(500, "Failed to create post")
```

---

## FIX #6: Error Handling in Frontend (30 min) - MEDIUM

### Find All `.catch(() => {})` in `frontend/src/App.js`

Search for: `catch(() => {}`

Replace with: 
```javascript
.catch(error => {
    console.error("Error:", error);
    toast.error("An error occurred. Please try again.");
})
```

### Example Fixes

**Before:**
```javascript
api.get("/marketplace/listings")
    .then(response => setListings(response.data.listings || []))
    .catch(() => {})  // ❌ Silent error
```

**After:**
```javascript
api.get("/marketplace/listings")
    .then(response => setListings(response.data.listings || []))
    .catch(error => {
        console.error("Failed to load marketplace:", error);
        toast.error("Failed to load marketplace");
    })
```

---

## FIX #7: Database Indexes (20 min) - MEDIUM

### Add to `backend/server.py` initialization

```python
async def create_indexes():
    """Create database indexes for performance"""
    try:
        # Posts indexes
        await db.posts.create_index([("user_id", 1)])
        await db.posts.create_index([("created_at", -1)])
        await db.posts.create_index([("tags", 1)])
        
        # Comments indexes
        await db.comments.create_index([("post_id", 1)])
        await db.comments.create_index([("user_id", 1)])
        await db.comments.create_index([("created_at", -1)])
        
        # Tracks indexes
        await db.tracks.create_index([("user_id", 1)])
        await db.tracks.create_index([("created_at", -1)])
        await db.tracks.create_index([("artist", 1)])
        
        # Videos indexes
        await db.videos.create_index([("user_id", 1)])
        await db.videos.create_index([("created_at", -1)])
        await db.videos.create_index([("tags", 1)])
        
        # Listings indexes
        await db.listings.create_index([("user_id", 1)])
        await db.listings.create_index([("category", 1)])
        await db.listings.create_index([("created_at", -1)])
        
        logger.info("Database indexes created successfully")
    except Exception as e:
        logger.error(f"Failed to create indexes: {e}")

# Call during app startup
@app.on_event("startup")
async def startup():
    if db is not None:
        await create_indexes()
```

---

## FIX #8: JWT Secret Validation (10 min) - HIGH

### Replace This
```python
JWT_SECRET = os.environ.get('JWT_SECRET', 'default_secret')
```

### With This
```python
import secrets

JWT_SECRET = os.environ.get('JWT_SECRET')

if not JWT_SECRET:
    if os.environ.get("ENV") == "development":
        # Generate random secret for development
        JWT_SECRET = secrets.token_urlsafe(32)
        logger.warning("No JWT_SECRET provided. Generated random secret for development.")
    else:
        raise ValueError(
            "JWT_SECRET environment variable not set. "
            "Set a strong 32+ character secret before deploying."
        )

if len(JWT_SECRET) < 32:
    logger.error(f"JWT_SECRET too weak: {len(JWT_SECRET)} chars (min 32)")
    raise ValueError("JWT_SECRET must be at least 32 characters")

logger.info(f"JWT_SECRET loaded: {len(JWT_SECRET)} chars")
```

---

## FIX #9: Logging Configuration (30 min) - MEDIUM

### Add to `backend/server.py` (after imports)

```python
import logging
import logging.handlers
from pathlib import Path

# Create logs directory
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        # File handler
        logging.handlers.RotatingFileHandler(
            LOG_DIR / "app.log",
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=10,
        ),
        # Console handler
        logging.StreamHandler(),
    ]
)

logger = logging.getLogger(__name__)

# Log startup
logger.info("Starting GAAIUS AI Server")
logger.info(f"Environment: {os.environ.get('ENV', 'production')}")
logger.info(f"Database: {os.environ.get('DB_NAME')}")
```

---

## Testing Your Fixes

### Test Fix #1: Bare Except
```bash
# Should return proper error
curl -H "Authorization: Bearer invalid_token" http://localhost:8000/api/profile
```

### Test Fix #2: File Validation
```bash
# Create a test file with wrong MIME type
echo "dangerous" > test.exe

# Try to upload - should fail
curl -F "file=@test.exe" http://localhost:8000/api/image/resize
# Should get: Invalid file type
```

### Test Fix #3: Rate Limiting
```bash
# Make requests quickly - should get rate limited
for i in {1..30}; do curl http://localhost:8000/api/posts; done
# Should get 429 Too Many Requests
```

### Test Fix #4: CORS
```bash
# Test CORS headers from disallowed origin
curl -H "Origin: http://evil.com" http://localhost:8000/api/posts
# Should NOT have CORS headers
```

---

## Apply Fixes In Order

1. **Fix #1** (Bare Except) - 15 min ✅
2. **Fix #2** (File Validation) - 30 min ✅
3. **Fix #3** (CORS) - 15 min ✅
4. **Fix #4** (Rate Limiting) - 45 min ✅
5. **Fix #5** (Input Validation) - 90 min ✅
6. **Fix #6** (Frontend Errors) - 30 min ✅
7. **Fix #7** (DB Indexes) - 20 min ✅
8. **Fix #8** (JWT Secret) - 10 min ✅
9. **Fix #9** (Logging) - 30 min ✅

**Total: ~5.5 hours**

After applying all fixes, you can safely deploy to production! 🚀

