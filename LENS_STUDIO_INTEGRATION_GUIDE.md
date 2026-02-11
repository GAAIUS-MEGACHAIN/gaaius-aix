# 🎬 Lens Studio - Complete Integration Guide

## Quick Start (5 Minutes)

### Step 1: Update Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Step 2: Add Routes to FastAPI Server
In `backend/server.py`:

```python
# Add imports at top
from lens_studio_service import router as lens_studio_router
from lens_studio_db import initialize_database, seed_initial_filters

# In your startup event
@app.on_event("startup")
async def startup_event():
    # ... existing startup code ...
    
    # Initialize Lens Studio
    db = app.db  # Your MongoDB database instance
    await initialize_database(db)
    await seed_initial_filters(db)

# Register router
app.include_router(lens_studio_router)
```

### Step 3: Update Frontend Routes
In your main app file (e.g., `frontend/src/App.jsx`):

```jsx
import LensStudioEditor from './components/LensStudioEditor';

function App() {
  return (
    <Routes>
      {/* ... existing routes ... */}
      <Route path="/lens-studio" element={<LensStudioEditor userId={userId} />} />
    </Routes>
  );
}
```

### Step 4: Start Services
```bash
# Terminal 1: Backend
cd backend
python run_server.py

# Terminal 2: Frontend
cd frontend
npm start
```

### Step 5: Access Application
Open `http://localhost:3000/lens-studio` in your browser

---

## Detailed Integration

### Backend Integration

#### 1. Database Configuration

**MongoDB Setup** (in `server.py`):

```python
import motor.motor_asyncio
from lens_studio_db import initialize_database, seed_initial_filters

# Create MongoDB client
client = motor.motor_asyncio.AsyncIOMotorClient(
    os.getenv("MONGODB_URL", "mongodb://localhost:27017")
)
db = client.lens_studio_db

# Initialize in startup
@app.on_event("startup")
async def init_db():
    await initialize_database(db)
    await seed_initial_filters(db)
    app.db = db
```

#### 2. FastAPI Router Integration

**In `server.py` or `router.py`**:

```python
from fastapi import FastAPI
from lens_studio_service import router as lens_studio_router

app = FastAPI(title="Lens Studio API")

# Include Lens Studio routes
app.include_router(lens_studio_router)

# Now available:
# GET /api/lens-studio/filters/free
# POST /api/lens-studio/process-image
# WS /api/lens-studio/ws/live-filter/{user_id}
# POST /api/lens-studio/social/create-post-with-filter
```

#### 3. Dependency Injection Setup

**For database access in routes**:

```python
async def get_db() -> motor.motor_asyncio.AsyncIOMotorDatabase:
    return app.db

# Use in routes
@app.get("/api/lens-studio/filters")
async def list_filters(db: AsyncIOMotorDatabase = Depends(get_db)):
    # Access database
    filters = await db.filters.find().to_list(length=100)
    return {"filters": filters}
```

#### 4. WebSocket Configuration

**Ensure WebSocket support in CORS**:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Frontend Integration

#### 1. Component Import

```jsx
import LensStudioEditor from './components/LensStudioEditor';

// Use in routes
<Route path="/lens-studio" element={<LensStudioEditor userId={currentUser.id} />} />
```

#### 2. Styling with TailwindCSS

Component uses TailwindCSS classes. Ensure your `tailwind.config.js` includes:

```js
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

#### 3. WebSocket Configuration

Update your API base URL in `LensStudioEditor.jsx`:

```jsx
// Currently uses: window.location.host
// This works if backend and frontend on same host

// For different hosts:
const API_HOST = process.env.REACT_APP_API_HOST || window.location.host;
const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const ws = new WebSocket(`${protocol}//${API_HOST}/api/lens-studio/ws/live-filter/${userId}`);
```

#### 4. Environment Variables

Create `.env` in frontend root:

```
REACT_APP_API_HOST=localhost:8000
REACT_APP_API_BASE=/api
```

### Social Integration

#### Integrate with Existing Post System

In your post creation component:

```jsx
import LensStudioEditor from './components/LensStudioEditor';

function CreatePost() {
  const [useFilters, setUseFilters] = useState(false);
  
  return (
    <>
      <label>
        <input
          type="checkbox"
          checked={useFilters}
          onChange={(e) => setUseFilters(e.target.checked)}
        />
        Apply Lens Studio Filters
      </label>
      
      {useFilters && (
        <LensStudioEditor userId={currentUser.id} />
      )}
    </>
  );
}
```

#### Link Filtered Posts to User Feed

```python
# In your post model
class Post(BaseModel):
    post_id: str
    user_id: str
    image: bytes
    filters_applied: List[str]  # List of filter IDs
    caption: str
    created_at: datetime
    likes: int = 0
    
    # New fields for social integration
    visibility: str = "public"  # public, private, friends
    is_processed: bool = True  # Processed with filters
```

---

## API Usage Examples

### Frontend JavaScript

#### Fetch Available Filters
```javascript
async function getFreeFilters() {
  const response = await fetch('/api/lens-studio/filters/free');
  const data = await response.json();
  console.log(data.filters); // Array of 12 filters
}
```

#### Send Frame via WebSocket
```javascript
const ws = new WebSocket('ws://localhost:8000/api/lens-studio/ws/live-filter/user123');

// When camera frame captured
canvas.toBlob((blob) => {
  const reader = new FileReader();
  reader.onload = (event) => {
    const frameData = event.target.result.split(',')[1]; // base64
    ws.send(JSON.stringify({
      type: 'frame',
      frame: frameData,
      filters: ['skin_smoothing', 'big_eyes']
    }));
  };
  reader.readAsDataURL(blob);
});

// Receive processed frame
ws.onmessage = (event) => {
  const { frame, metadata } = JSON.parse(event.data);
  // Render frame to canvas
  renderProcessedFrame(frame);
};
```

#### Create Post with Filters
```javascript
async function createFilteredPost(imageBlob, selectedFilters, caption) {
  const formData = new FormData();
  formData.append('image_data', imageBlob);
  formData.append('filters', selectedFilters.join(','));
  formData.append('caption', caption);
  formData.append('user_id', userId);
  
  const response = await fetch('/api/lens-studio/social/create-post-with-filter', {
    method: 'POST',
    body: formData
  });
  
  const data = await response.json();
  return data.post_id;
}
```

### Backend Python

#### Get Filter Metadata
```python
async def get_filter_info(db, filter_id):
    filter_doc = await db.filters.find_one({"filter_id": filter_id})
    return FilterMetadata(
        filter_id=filter_doc["filter_id"],
        name=filter_doc["name"],
        filter_type=FilterType(filter_doc["type"]),
        intensity=filter_doc.get("intensity", 0.7),
        parameters=filter_doc.get("parameters", {})
    )
```

#### Process Image
```python
from lens_studio_core import FilterProcessor
import cv2

processor = FilterProcessor()

# Read image
frame = cv2.imread("photo.jpg")

# Get filters
filters = [DEFAULT_FILTERS["skin_smoothing"], DEFAULT_FILTERS["big_eyes"]]

# Process
result, metadata = processor.process_frame(frame, filters)

# Save result
cv2.imwrite("filtered_photo.jpg", result)
```

#### Track Analytics
```python
async def log_filter_usage(db, filter_id, user_id):
    await db.filter_analytics.insert_one({
        "filter_id": filter_id,
        "user_id": user_id,
        "timestamp": datetime.utcnow(),
        "session_id": str(uuid.uuid4())
    })
    
    # Update usage count
    await db.filters.update_one(
        {"filter_id": filter_id},
        {"$inc": {"usage_count": 1}}
    )
```

---

## Configuration Options

### Backend Configuration (`.env`)

```bash
# MongoDB
MONGODB_URL=mongodb://localhost:27017
DB_NAME=lens_studio

# Server
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000
DEBUG=False

# Lens Studio
FILTER_MAX_RESOLUTION=1280x720
FILTER_JPEG_QUALITY=90
FILTER_PROCESSING_TIMEOUT=5000
MAX_WEBSOCKET_CONNECTIONS=1000

# Storage
STORAGE_TYPE=local  # or s3
STORAGE_PATH=./uploads/filters
S3_BUCKET=lens-studio-filters
S3_REGION=us-east-1

# Analytics
ANALYTICS_BATCH_SIZE=100
ANALYTICS_RETENTION_DAYS=90

# Performance
PROCESS_POOL_SIZE=4
FRAME_BUFFER_SIZE=30
```

### Frontend Configuration (`.env`)

```bash
# API
REACT_APP_API_HOST=localhost:8000
REACT_APP_API_PROTOCOL=http
REACT_APP_WS_PROTOCOL=ws

# UI
REACT_APP_MAX_CAMERA_RESOLUTION=1280x720
REACT_APP_TARGET_FPS=30
REACT_APP_JPEG_QUALITY=90

# Features
REACT_APP_ENABLE_RECORDING=true
REACT_APP_ENABLE_SHARING=true
REACT_APP_ENABLE_ANALYTICS=true
```

---

## Troubleshooting

### Camera Not Working

**Issue**: "Could not access camera"

**Solutions**:
1. Check browser permissions (Settings > Privacy > Camera)
2. Ensure HTTPS (WSS requires HTTPS)
3. Verify camera not in use by another app
4. Test in different browser

```javascript
// Test camera access
try {
  const stream = await navigator.mediaDevices.getUserMedia({ video: true });
  stream.getTracks().forEach(t => t.stop());
  console.log('✅ Camera access granted');
} catch (e) {
  console.error('❌ Camera error:', e);
}
```

### WebSocket Connection Failed

**Issue**: "Connection refused"

**Solutions**:
1. Verify backend running on correct port
2. Check CORS configuration
3. Ensure WebSocket endpoint accessible
4. Review firewall/proxy settings

```bash
# Test WebSocket connectivity
curl -i -N -H "Connection: Upgrade" \
  -H "Upgrade: websocket" \
  http://localhost:8000/api/lens-studio/ws/live-filter/testuser
```

### Low FPS Performance

**Issue**: Filters slow, FPS < 20

**Solutions**:
1. Reduce filter count
2. Lower camera resolution
3. Disable less critical filters
4. Check system CPU usage
5. Increase `PROCESS_POOL_SIZE`

### Filter Not Detecting Face

**Issue**: "face_detected: false"

**Solutions**:
1. Improve lighting (front light)
2. Position face in center
3. Face should occupy 50%+ of frame
4. Check camera angle
5. Verify MediaPipe dependencies installed

```python
# Debug face detection
import cv2
from lens_studio_core import FaceDetector

detector = FaceDetector()
frame = cv2.imread("test.jpg")
face = detector.detect_face(frame)
if face:
    print(f"Face detected: {face.face_bbox}")
else:
    print("No face detected")
```

---

## Performance Tuning

### Optimize Filter Processing

```python
# Reduce complexity
processor = FilterProcessor()

# Enable frame caching
processor.frame_buffer = deque(maxlen=15)  # Reduce from 30

# Disable heavy filters
heavy_filters = ["oil_painting", "sketch"]
enabled_filters = [f for f in filters if f.filter_id not in heavy_filters]

# Process
result, _ = processor.process_frame(frame, enabled_filters)
```

### Optimize Network

```javascript
// Reduce JPEG quality for faster transmission
canvas.toDataURL('image/jpeg', 0.7)  // 70% quality

// Reduce frame resolution
canvas.width = 640;  // Instead of 1280
canvas.height = 480;  // Instead of 720

// Increase send interval
setTimeout(() => { /* send frame */ }, 100);  // 10 FPS instead of 30
```

### Optimize Database

```python
# Add indexes
await db.filters.create_index([("usage_count", -1)])
await db.filter_analytics.create_index([("user_id", 1)])

# Bulk inserts
await db.filter_analytics.insert_many(batch_events)  # Not one-by-one
```

---

## Production Deployment

### Docker Setup

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt

COPY backend/ .

ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
```

Run:
```bash
docker build -t lens-studio-backend .
docker run -e MONGODB_URL="mongodb://mongo:27017" -p 8000:8000 lens-studio-backend
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: lens-studio
spec:
  replicas: 3
  selector:
    matchLabels:
      app: lens-studio
  template:
    metadata:
      labels:
        app: lens-studio
    spec:
      containers:
      - name: lens-studio
        image: lens-studio-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: MONGODB_URL
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: mongodb-url
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
```

---

## Support & Debugging

### Enable Debug Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("lens_studio")
logger.debug("Filter processing started")
```

### Monitor Performance

```bash
# Check backend logs
docker logs <container_id>

# Monitor resource usage
docker stats <container_id>

# Test API endpoints
curl http://localhost:8000/api/lens-studio/filters/free
```

### Test Locally

```bash
# Run unit tests
cd backend
pytest tests/ -v

# Test WebSocket
python -m websockets ws://localhost:8000/api/lens-studio/ws/live-filter/testuser

# Benchmark filters
python benchmark_filters.py
```

---

## Next Steps

1. ✅ Install dependencies
2. ✅ Add routes to FastAPI server
3. ✅ Import frontend component
4. ✅ Configure MongoDB
5. ✅ Test camera functionality
6. ✅ Deploy to production

**Questions?** Check `/docs` endpoint for full API documentation!
