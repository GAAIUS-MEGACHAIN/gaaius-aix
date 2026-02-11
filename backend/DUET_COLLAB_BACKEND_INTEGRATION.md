# Duet & Collab Backend Integration Guide

## Quick Start

The Duet & Collab backend consists of 4 main modules that need to be integrated into your FastAPI server:

1. **duet_collab_service.py** - Database operations and business logic
2. **duet_collab_routes.py** - REST API endpoints
3. **duet_collab_websocket.py** - Real-time collaboration via WebSocket
4. **duet_collab_video_processor.py** - Video processing and effects

---

## Integration Steps

### Step 1: Add Imports to server.py

```python
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

# Import Duet & Collab modules
from duet_collab_routes import router as duet_router
from duet_collab_websocket import handle_duet_websocket, duet_ws_manager

app = FastAPI()

# Add CORS middleware if not already present
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Duet & Collab routes
app.include_router(duet_router)
```

### Step 2: Add WebSocket Endpoint

```python
@app.websocket("/ws/duet/{session_id}/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: str,
    user_id: str
):
    """WebSocket endpoint for real-time collaboration"""
    await handle_duet_websocket(websocket, session_id, user_id)
```

### Step 3: Initialize Duet Service in app startup

```python
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    # Initialize database
    from motor.motor_asyncio import AsyncIOMotorClient
    
    client = AsyncIOMotorClient(os.getenv("MONGODB_URI"))
    db = client["gaaius_db"]
    
    # Initialize duet service indexes
    from duet_collab_service import DuetCollabService
    service = DuetCollabService(db)
    await service.init_indexes()
    
    # Store in app state for dependency injection
    app.state.db = db
    app.state.duet_service = service
```

### Step 4: Update Dependencies

Add to `requirements.txt`:
```
fastapi>=0.95.0
motor>=3.2.0
pymongo>=4.3.0
pydantic>=1.10.0
boto3>=1.26.0
ffmpeg-python>=0.2.1
python-multipart>=0.0.5
aiofiles>=23.1.0
websockets>=10.0
```

### Step 5: Environment Variables

Add to `.env`:
```
# MongoDB
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB=gaaius_db

# AWS S3
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_S3_BUCKET=gaaius-duet-videos
AWS_REGION=us-east-1

# Video Processing
FFMPEG_PATH=/usr/bin/ffmpeg
TEMP_DIR=/tmp/duet_processing

# API
API_HOST=0.0.0.0
API_PORT=8000
```

---

## Database Collections

The service automatically creates these MongoDB collections:

```python
- duet_sessions      # Main session documents
- duet_clips         # Video clips in sessions
- duet_collaborators # Collaborator records
- duet_comments      # Comments and replies
- duet_exports       # Export jobs
```

---

## API Endpoints Overview

### Sessions
```
POST   /api/duet/sessions              - Create new session
GET    /api/duet/sessions              - List user's sessions
GET    /api/duet/sessions/{id}         - Get session details
PUT    /api/duet/sessions/{id}/status  - Update status
DELETE /api/duet/sessions/{id}         - Delete session
```

### Clips
```
POST   /api/duet/clips                         - Upload clip
GET    /api/duet/clips/{id}                    - Get clip details
GET    /api/duet/sessions/{id}/clips           - List session clips
POST   /api/duet/clips/{id}/effects            - Apply effect
DELETE /api/duet/clips/{id}                    - Delete clip
```

### Collaborators
```
POST   /api/duet/sessions/{id}/collaborators              - Add collaborator
GET    /api/duet/sessions/{id}/collaborators              - List collaborators
PUT    /api/duet/sessions/{id}/collaborators/{uid}/status - Update status
DELETE /api/duet/sessions/{id}/collaborators/{uid}        - Remove collaborator
```

### Comments
```
POST   /api/duet/sessions/{id}/comments       - Add comment
GET    /api/duet/sessions/{id}/comments       - Get comments
DELETE /api/duet/comments/{id}                - Delete comment
```

### Export
```
POST   /api/duet/export        - Create export job
GET    /api/duet/export/{id}   - Get export status
```

### Engagement
```
POST   /api/duet/sessions/{id}/view      - Record view
POST   /api/duet/sessions/{id}/like      - Toggle like
PUT    /api/duet/sessions/{id}/viewers   - Update viewer count
```

### Discovery
```
GET    /api/duet/trending             - Get trending duets
GET    /api/duet/users/{id}/stats     - Get user statistics
```

---

## WebSocket Events

### Connection Flow
```
Client connects -> Server broadcasts COLLABORATOR_JOINED
Server sends presence snapshot
Client receives all current collaborators
```

### Message Types

**Collaborator Events:**
```json
{
  "type": "collaborator_joined",
  "user_id": "user_123",
  "timestamp": "2026-01-20T10:00:00Z"
}

{
  "type": "collaborator_status_changed",
  "user_id": "user_123",
  "status": "editing",
  "timestamp": "2026-01-20T10:00:00Z"
}
```

**Clip Events:**
```json
{
  "type": "clip_added",
  "clip": {
    "clip_id": "clip_123",
    "title": "Dancing",
    "duration": 15.5,
    "position": 0
  },
  "timestamp": "2026-01-20T10:00:00Z"
}

{
  "type": "effect_applied",
  "clip_id": "clip_123",
  "effect": {
    "effect_id": "eff_123",
    "effect_type": "blur",
    "intensity": 1.0
  },
  "timestamp": "2026-01-20T10:00:00Z"
}
```

**Comment Events:**
```json
{
  "type": "comment_added",
  "comment": {
    "comment_id": "cmt_123",
    "author_name": "John",
    "text": "Nice shot!",
    "timestamp": 5.0
  },
  "server_timestamp": "2026-01-20T10:00:00Z"
}
```

**Export Events:**
```json
{
  "type": "export_progress",
  "export_id": "exp_123",
  "progress": 45,
  "timestamp": "2026-01-20T10:00:00Z"
}

{
  "type": "export_completed",
  "export_id": "exp_123",
  "video_url": "s3://bucket/exports/session_123/video.mp4",
  "timestamp": "2026-01-20T10:00:00Z"
}
```

---

## Authentication Integration

The service uses token-based authentication. Update `get_current_user()` in `duet_collab_routes.py`:

```python
async def get_current_user(request: Request) -> dict:
    """Get current user from JWT token"""
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    try:
        scheme, token = auth_header.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid auth scheme")
        
        # Decode your JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Fetch user from database
        user = await db.users.find_one({"_id": user_id})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        return {
            "user_id": user["_id"],
            "username": user["username"],
            "avatar_url": user.get("avatar_url")
        }
    
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))
```

---

## Video Processing Setup

### FFmpeg Installation

**Ubuntu/Debian:**
```bash
sudo apt-get install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
```bash
choco install ffmpeg
```

### S3 Configuration

1. Create AWS bucket: `gaaius-duet-videos`
2. Set CORS policy:
```json
[
  {
    "AllowedHeaders": ["*"],
    "AllowedMethods": ["GET", "PUT", "POST"],
    "AllowedOrigins": ["*"],
    "ExposeHeaders": ["ETag"],
    "MaxAgeSeconds": 3000
  }
]
```

3. Create IAM user with permissions for S3 bucket

---

## Testing

### 1. Create Session
```bash
curl -X POST http://localhost:8000/api/duet/sessions \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Summer Vibes",
    "description": "Dancing in the sun",
    "max_collaborators": 5,
    "is_public": true
  }'
```

### 2. Upload Clip
```bash
curl -X POST "http://localhost:8000/api/duet/clips?session_id=SESSION_ID&title=Dance&duration=15.5" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@video.mp4"
```

### 3. WebSocket Connection
```javascript
const ws = new WebSocket(
  'ws://localhost:8000/ws/duet/SESSION_ID/USER_ID'
);

ws.onopen = () => {
  ws.send(JSON.stringify({
    type: 'ping'
  }));
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log('Message:', message);
};
```

---

## Performance Optimization

### Database Indexes
- `sessions_collection`: creator_id, status, created_at
- `clips_collection`: session_id, contributor_id, status
- `comments_collection`: session_id, author_id
- `collaborators_collection`: (session_id, user_id) compound

### Caching Strategy
```python
from redis import asyncio as aioredis

redis = await aioredis.create_redis_pool('redis://localhost')

# Cache trending duets (5 min TTL)
await redis.setex(
    f"trending:{limit}",
    300,
    json.dumps(trending_duets)
)

# Cache user stats (10 min TTL)
await redis.setex(
    f"user_stats:{user_id}",
    600,
    json.dumps(user_stats)
)
```

### Connection Pooling
```python
from motor.motor_asyncio import AsyncIOMotorClient

client = AsyncIOMotorClient(
    connection_uri,
    maxPoolSize=50,
    minPoolSize=10
)
```

---

## Monitoring & Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('duet_collab.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
```

---

## Error Handling

The service includes comprehensive error handling:

- **400 Bad Request** - Invalid parameters
- **401 Unauthorized** - Missing/invalid token
- **403 Forbidden** - Insufficient permissions
- **404 Not Found** - Resource not found
- **500 Server Error** - Processing errors

All errors return consistent format:
```json
{
  "detail": "Error message",
  "status_code": 400,
  "timestamp": "2026-01-20T10:00:00Z"
}
```

---

## Production Deployment

### Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN apt-get update && apt-get install -y ffmpeg
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Kubernetes
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: duet-collab-api
spec:
  containers:
  - name: api
    image: gaaius/duet-collab:latest
    ports:
    - containerPort: 8000
    env:
    - name: MONGODB_URI
      valueFrom:
        secretKeyRef:
          name: db-credentials
          key: uri
    - name: AWS_ACCESS_KEY_ID
      valueFrom:
        secretKeyRef:
          name: aws-credentials
          key: access_key
```

---

## Troubleshooting

### WebSocket Connection Issues
- Check firewall rules allow WebSocket (port 8000)
- Verify token is valid
- Check browser console for connection errors

### Video Processing Fails
- Verify FFmpeg is installed: `ffmpeg -version`
- Check S3 credentials and bucket permissions
- Review `/tmp/duet_processing` for temp files

### Database Issues
- Verify MongoDB connection string
- Check collections exist: `db.duet_sessions.find()`
- Review indexes: `db.duet_sessions.getIndexes()`

---

## Support & Documentation

- API Documentation: `/docs` (Swagger UI)
- OpenAPI Schema: `/openapi.json`
- Health Check: `/health`

