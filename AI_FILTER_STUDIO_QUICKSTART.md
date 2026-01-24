# 🚀 AI FILTER STUDIO - QUICK START GUIDE

## ⚡ 30-Second Setup

### Step 1: Get Groq API Key
```bash
# Visit: https://console.groq.com/
# Create account → Get API key
export GROQ_API_KEY="gsk_xxxxxxxxxxxx"
```

### Step 2: Backend
```bash
cd backend
python -m uvicorn server:app --reload --port 8000
```

### Step 3: Frontend
```bash
cd frontend
npm start
# Opens http://localhost:3000
```

### Step 4: Access AI Filter Studio
1. Open http://localhost:3000
2. Look for **"AI Filters"** button in the main menu (cyan icon with sparkles ✨)
3. Click it → Stream starts automatically
4. Select filters and adjust settings

---

## 🎬 USAGE EXAMPLE

```javascript
// JavaScript WebSocket Client Example

const sessionId = "your-session-id";
const ws = new WebSocket(`ws://localhost:8000/ws/stream/${sessionId}`);

// Send frame for processing
const sendFrame = async (videoElement) => {
  const canvas = document.createElement('canvas');
  canvas.width = videoElement.videoWidth;
  canvas.height = videoElement.videoHeight;
  
  const ctx = canvas.getContext('2d');
  ctx.drawImage(videoElement, 0, 0);
  
  canvas.toBlob((blob) => {
    const reader = new FileReader();
    reader.onload = () => {
      const frameBase64 = reader.result.split(',')[1];
      
      ws.send(JSON.stringify({
        type: 'frame',
        frame_base64: frameBase64,
        request_id: Date.now().toString()
      }));
    };
    reader.readAsDataURL(blob);
  }, 'image/jpeg', 0.9);
};

// Receive processed frame
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  if (data.type === 'frame') {
    const img = new Image();
    img.src = `data:image/jpeg;base64,${data.frame_base64}`;
    img.onload = () => {
      const canvas = document.getElementById('output');
      const ctx = canvas.getContext('2d');
      ctx.drawImage(img, 0, 0);
    };
    
    console.log(`FPS: ${data.metrics.fps}`);
    console.log(`Faces: ${data.detected_faces}`);
  }
};
```

---

## 🎨 FILTER TYPES

| Filter | Type | Description | Config |
|--------|------|-------------|--------|
| **Beauty** | beauty | Skin smoothing, eye/lip enhancement | Sliders |
| **Background** | background | Blur or color replacement | Dropdown |
| **Cartoon** | cartoon | Anime-style effect | Fixed |
| **Vintage** | vintage | Old film look | Fixed |
| **Artistic** | artistic | Oil painting style | Fixed |

---

## ⚙️ API QUICK REFERENCE

### Create Session
```bash
curl -X POST http://localhost:8000/api/ai-filter-studio/session/create \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user123"}'
```

**Response:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "user123",
  "created_at": "2024-01-01T12:00:00"
}
```

### Process Frame
```bash
curl -X POST http://localhost:8000/api/ai-filter-studio/frame/process \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "frame_base64": "iVBORw0KGgoAAAANSUhEUgAAAA...",
    "active_filters": ["beauty"],
    "beauty_config": {
      "smoothing_strength": 0.5,
      "brightness_adjustment": 0.1,
      "eye_brightness": 0.3
    }
  }'
```

**Response:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "frame_base64": "iVBORw0KGgoAAAANSUhEUgAAAA...",
  "detected_faces": 1,
  "processing_time_ms": 45.2,
  "applied_filters": ["beauty"],
  "ai_suggestions": [
    "Increase eye brightness for better definition",
    "Try saturation boost for more vibrant skin tone"
  ]
}
```

### Get Available Filters
```bash
curl http://localhost:8000/api/ai-filter-studio/filters/available
```

### Generate AI Suggestions
```bash
curl -X POST http://localhost:8000/api/ai-filter-studio/suggestions/generate \
  -H "Content-Type: application/json" \
  -d '{
    "frame_base64": "iVBORw0KGgoAAAANSUhEUgAAAA...",
    "filter_type": "beauty"
  }'
```

---

## 🔧 TROUBLESHOOTING

### Issue: WebSocket Connection Failed
```
Error: WebSocket connection to 'ws://localhost:8000/ws/stream/...' failed

Solution:
1. Check backend is running: curl http://localhost:8000/api/ai-filter-studio/health
2. Verify port 8000 is open
3. Check firewall settings
4. Try: export CORS_ORIGINS="http://localhost:3000"
```

### Issue: No Face Detected
```
Problem: detected_faces = 0

Solution:
1. Ensure adequate lighting (natural light preferred)
2. Position face 30-60cm from camera
3. Check webcam permission granted
4. Verify MediaPipe model loaded: Check server logs
5. Try: Zoom in camera on face
```

### Issue: High Latency (>150ms)
```
Solution:
1. Reduce frame quality: IMWRITE_JPEG_QUALITY=70 (default: 90)
2. Disable heavy filters (cartoon, artistic)
3. Reduce frame resolution: 640x480 instead of 1280x720
4. Check CPU usage: htop or Task Manager
5. Consider GPU acceleration: CUDA support available
```

### Issue: Out of Memory
```
Solution:
1. Reduce frame buffer: frame_buffer.maxlen = 100 (default: 300)
2. Stop all sessions and restart
3. Increase system RAM or use cloud instance
4. Monitor: ps aux | grep python
```

---

## 📊 PERFORMANCE TUNING

### For Optimal Performance

```python
# In ai_filter_studio.py - Adjust these values:

# 1. JPEG Quality (60-95)
cv2.imencode('.jpg', result_frame, [cv2.IMWRITE_JPEG_QUALITY, 80])

# 2. Face Detection Confidence
mp_face_detection.FaceDetection(
    model_selection=1,  # 0=short-range, 1=full-range
    min_detection_confidence=0.7  # 0.5-0.9
)

# 3. WebSocket Message Size
# Smaller = faster, Lower quality
# Larger = slower, Higher quality

# 4. Processing Threads
asyncio.create_task(...)  # Increase for more concurrency
```

---

## 🌐 ENVIRONMENT VARIABLES

```bash
# Required
GROQ_API_KEY=gsk_xxxxxxxxxxxx

# Optional
GOOGLE_API_KEY=AIzaXxxxxxxxxxx
MONGODB_URL=mongodb://localhost:27017
CORS_ORIGINS=http://localhost:3000
MAX_FRAME_SIZE=5242880  # 5MB in bytes
SESSION_TIMEOUT=1800    # 30 minutes in seconds
JPEG_QUALITY=90         # 60-95
```

---

## 📱 FRONTEND COMPONENT PROPS

```javascript
// AIFilterStudio.jsx doesn't require any props
// Usage:
<AIFilterStudio />

// All state managed internally
// WebSocket connection automatic
// Session creation automatic
```

---

## 🔌 BACKEND ROUTES INTEGRATION

Routes automatically registered in `server.py`:

```python
# These are added automatically:
/api/ai-filter-studio/*          # REST endpoints
/ws/stream/{session_id}          # WebSocket endpoint
```

---

## 💡 PRO TIPS

1. **Increase Eye Brightness First**
   - Makes face look more awake
   - Works well with beauty filter
   - Start at 0.2-0.3

2. **Use Saturation Boost Sparingly**
   - More than 0.5 looks unnatural
   - Combine with skin smoothing
   - Good for makeup effects

3. **Background Blur Over Color**
   - More professional appearance
   - Blur strength 15-30 recommended
   - Works with any lighting

4. **Record Before Download**
   - Click "● Record" to enable recording
   - Captures all frames for export
   - Up to 10 seconds (300 frames @ 30fps)

5. **AI Suggestions Every 30 Frames**
   - Appear in purple panel on right
   - Based on actual face analysis
   - Powered by Groq LLaMA

---

## 📞 SUPPORT COMMANDS

```bash
# Check server health
curl http://localhost:8000/api/ai-filter-studio/health

# View logs
tail -f logs/app.log

# Check WebSocket connections
curl http://localhost:8000/api/ai-filter-studio/filters/available

# Monitor performance
watch -n 1 'ps aux | grep python'
```

---

## ✅ VERIFICATION CHECKLIST

- [ ] `GROQ_API_KEY` set
- [ ] Backend running on port 8000
- [ ] Frontend running on port 3000
- [ ] Camera/webcam working
- [ ] "AI Filters" button visible
- [ ] Can start stream
- [ ] Filters apply in real-time
- [ ] FPS shows 25+ frames/second
- [ ] Face detection working
- [ ] WebSocket connection active

---

## 🎉 YOU'RE READY!

Everything is production-grade and ready to use.
Have fun with real-time AR filters! 🚀

---

**For detailed API documentation**, see: `AI_FILTER_STUDIO_COMPLETE.md`
