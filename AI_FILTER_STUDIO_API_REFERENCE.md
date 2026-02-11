# 🔌 AI FILTER STUDIO - API REFERENCE

## 📡 COMPLETE API DOCUMENTATION

### BASE URL
```
http://localhost:8000/api/ai-filter-studio
```

---

## 🔵 REST ENDPOINTS

### 1. CREATE SESSION
**Endpoint**: `POST /session/create`

**Description**: Create new filter processing session

**Request**:
```json
{
  "user_id": "user123"
}
```

**Response** (200 OK):
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "user123",
  "created_at": "2024-01-15T10:30:00Z"
}
```

**cURL**:
```bash
curl -X POST http://localhost:8000/api/ai-filter-studio/session/create \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user123"}'
```

---

### 2. PROCESS FRAME
**Endpoint**: `POST /frame/process`

**Description**: Process single video frame with filters

**Request**:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "frame_base64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
  "active_filters": ["beauty", "background"],
  "beauty_config": {
    "smoothing_strength": 0.5,
    "brightness_adjustment": 0.1,
    "contrast_adjustment": 0,
    "saturation_boost": 0.2,
    "eye_enlargement": 0.1,
    "eye_brightness": 0.3,
    "lips_tint": "#FF6B9D",
    "lips_intensity": 0.5
  },
  "background_config": {
    "filter_type": "blur",
    "blur_strength": 25,
    "replacement_color": "#FFFFFF",
    "opacity": 1.0
  }
}
```

**Response** (200 OK):
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "frame_base64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJ...",
  "detected_faces": 1,
  "processing_time_ms": 45.23,
  "applied_filters": ["beauty", "background"],
  "ai_suggestions": [
    "Increase eye brightness for more definition",
    "Consider higher saturation for better skin tone"
  ]
}
```

**Error** (400 Bad Request):
```json
{
  "detail": "Invalid frame_base64: Unable to decode frame"
}
```

**cURL**:
```bash
curl -X POST http://localhost:8000/api/ai-filter-studio/frame/process \
  -H "Content-Type: application/json" \
  -d @request.json
```

---

### 3. AI ENHANCE FRAME
**Endpoint**: `POST /ai/enhance`

**Description**: Apply AI-powered enhancements to frame

**Request**:
```json
{
  "filter_type": "beauty",
  "image_base64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJ...",
  "prompt": "Make the face more radiant",
  "model": "groq_llama",
  "config": {
    "smoothing_strength": 0.7,
    "eye_brightness": 0.5,
    "saturation_boost": 0.3
  }
}
```

**Response** (200 OK):
```json
{
  "frame_base64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJ...",
  "ai_suggestions": [
    "Apply additional eye brightening",
    "Increase lip tint for more definition",
    "Consider contrast boost for better skin definition"
  ],
  "applied_filters": ["beauty"],
  "model_used": "groq_llama"
}
```

---

### 4. GET AVAILABLE FILTERS
**Endpoint**: `GET /filters/available`

**Description**: List all available filter types with descriptions

**Response** (200 OK):
```json
{
  "filters": [
    {
      "name": "Beauty",
      "type": "beauty",
      "description": "Skin smoothing, brightening, eye and lip enhancement",
      "configurable": true
    },
    {
      "name": "Background Blur",
      "type": "background",
      "description": "Professional background blur effect",
      "configurable": true
    },
    {
      "name": "Cartoon",
      "type": "cartoon",
      "description": "Transform to cartoon style",
      "configurable": false
    },
    {
      "name": "Vintage",
      "type": "vintage",
      "description": "Classic vintage film effect",
      "configurable": false
    },
    {
      "name": "Artistic",
      "type": "artistic",
      "description": "Artistic stylization effect",
      "configurable": false
    }
  ]
}
```

**cURL**:
```bash
curl http://localhost:8000/api/ai-filter-studio/filters/available
```

---

### 5. GENERATE SUGGESTIONS
**Endpoint**: `POST /suggestions/generate`

**Description**: Generate AI-powered filter suggestions

**Request**:
```json
{
  "frame_base64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJ...",
  "filter_type": "beauty"
}
```

**Response** (200 OK):
```json
{
  "filter_type": "beauty",
  "suggestions": [
    "Increase eye brightness for more definition",
    "Apply saturation boost for vibrant skin tone",
    "Consider eye enlargement for dramatic effect",
    "Use lips tint for more defined look"
  ]
}
```

**cURL**:
```bash
curl -X POST http://localhost:8000/api/ai-filter-studio/suggestions/generate \
  -H "Content-Type: application/json" \
  -d '{
    "frame_base64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJ...",
    "filter_type": "beauty"
  }'
```

---

### 6. OPTIMIZE PARAMETERS
**Endpoint**: `POST /parameters/optimize`

**Description**: Use AI to optimize filter parameters based on feedback

**Request**:
```json
{
  "current_config": {
    "smoothing_strength": 0.3,
    "brightness_adjustment": 0,
    "eye_brightness": 0.1
  },
  "user_feedback": "Make the face look more radiant and brighter"
}
```

**Response** (200 OK):
```json
{
  "optimized_config": {
    "smoothing_strength": 0.6,
    "brightness_adjustment": 0.2,
    "eye_brightness": 0.4,
    "saturation_boost": 0.3
  },
  "feedback_applied": "Make the face look more radiant and brighter"
}
```

---

### 7. HEALTH CHECK
**Endpoint**: `GET /health`

**Description**: Check service health status

**Response** (200 OK):
```json
{
  "status": "healthy",
  "service": "ai_filter_studio",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**cURL**:
```bash
curl http://localhost:8000/api/ai-filter-studio/health
```

---

## 🟣 WEBSOCKET ENDPOINT

### REAL-TIME STREAMING
**URL**: `ws://localhost:8000/ws/stream/{session_id}`

**Description**: Bidirectional real-time frame streaming

#### MESSAGE TYPES

##### Send: FRAME
```json
{
  "type": "frame",
  "frame_base64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJ...",
  "request_id": "1705316400000"
}
```

##### Receive: FRAME (Response)
```json
{
  "type": "frame",
  "request_id": "1705316400000",
  "frame_base64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJ...",
  "detected_faces": 1,
  "processing_time_ms": 42.15,
  "applied_filters": ["beauty"],
  "metrics": {
    "fps": 28.5,
    "avg_processing_ms": 35.2,
    "total_frames": 850,
    "uptime_seconds": 30.0
  },
  "ai_suggestions": [
    "Increase saturation for more vibrant look"
  ]
}
```

##### Send: CONFIG (Beauty)
```json
{
  "type": "config",
  "beauty_config": {
    "smoothing_strength": 0.6,
    "brightness_adjustment": 0.2,
    "contrast_adjustment": 0.1,
    "saturation_boost": 0.3,
    "eye_enlargement": 0.15,
    "eye_brightness": 0.4,
    "lips_tint": "#FF6B9D",
    "lips_intensity": 0.6
  }
}
```

##### Send: CONFIG (Background)
```json
{
  "type": "config",
  "background_config": {
    "filter_type": "blur",
    "blur_strength": 30,
    "replacement_color": "#FFFFFF",
    "opacity": 1.0
  }
}
```

##### Send: UPDATE FILTERS
```json
{
  "type": "filters",
  "filters": ["beauty", "background", "cartoon"]
}
```

##### Send: RECORD
```json
{
  "type": "record",
  "enabled": true
}
```

##### Send: PING
```json
{
  "type": "ping"
}
```

##### Receive: PONG
```json
{
  "type": "pong",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

##### Receive: METRICS
```json
{
  "type": "metrics",
  "data": {
    "active_sessions": 3,
    "sessions": {
      "550e8400-e29b-41d4-a716-446655440000": {
        "fps": 28.5,
        "avg_processing_ms": 35.2,
        "total_frames": 850,
        "uptime_seconds": 30.0
      }
    }
  }
}
```

##### Receive: ERROR
```json
{
  "type": "error",
  "error": "Invalid frame_base64",
  "request_id": "1705316400000"
}
```

#### WebSocket JavaScript Example
```javascript
// Connect
const ws = new WebSocket('ws://localhost:8000/ws/stream/550e8400-e29b-41d4-a716-446655440000');

// Handle connection
ws.onopen = () => {
  console.log('Connected');
};

// Send frame
ws.send(JSON.stringify({
  type: 'frame',
  frame_base64: 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJ...',
  request_id: Date.now().toString()
}));

// Receive response
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(`Processed in ${data.processing_time_ms}ms`);
  console.log(`Faces detected: ${data.detected_faces}`);
};

// Handle disconnection
ws.onclose = () => {
  console.log('Disconnected');
};

// Handle errors
ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};
```

---

## 🔐 AUTHENTICATION

### Bearer Token
All REST endpoints support optional Bearer token:

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/ai-filter-studio/health
```

### WebSocket Auth
Include token in URL or headers:

```javascript
const token = localStorage.getItem('token');
const ws = new WebSocket(`ws://localhost:8000/ws/stream/session123?token=${token}`);
```

---

## ⚠️ ERROR CODES

| Code | Meaning | Example |
|------|---------|---------|
| 200 | Success | Frame processed |
| 400 | Bad Request | Invalid base64 |
| 401 | Unauthorized | Missing token |
| 422 | Validation Error | Invalid config |
| 500 | Server Error | Processing failed |
| 503 | Service Unavailable | Overloaded |

---

## 📊 RATE LIMITS

```
REST Endpoints: 100 requests/minute per user
WebSocket: 30 frames/second per session
Session Limit: 10 concurrent per user
```

---

## 🧪 TESTING WITH POSTMAN

1. **Import Collection**
   - File → Import → Select `ai-filter-studio.postman_collection.json`

2. **Set Variables**
   - base_url = `http://localhost:8000`
   - session_id = `550e8400-e29b-41d4-a716-446655440000`

3. **Run Requests**
   - Create Session
   - Process Frame
   - Get Filters
   - Generate Suggestions

---

## 📈 PERFORMANCE BENCHMARKS

| Endpoint | Avg Time | P99 | Throughput |
|----------|----------|-----|-----------|
| session/create | 10ms | 50ms | 1000/s |
| frame/process | 45ms | 150ms | 20/s |
| filters/available | 2ms | 10ms | 5000/s |
| suggestions/generate | 500ms | 2000ms | 2/s |
| WebSocket frame | 35ms | 100ms | 30/s |

---

## 💡 BEST PRACTICES

1. **Reuse Sessions**
   - Create once, use for multiple frames
   - Don't create new session per frame

2. **Optimize Frame Size**
   - 1280x720: Best quality/speed balance
   - 640x480: Better for low-bandwidth
   - <512x512: Not recommended

3. **Batch Suggestions**
   - Request every 30-60 frames
   - Not on every frame

4. **Handle WebSocket Timeouts**
   - Implement 30-second heartbeat
   - Reconnect on disconnect
   - Use exponential backoff

5. **Error Handling**
   - Always catch WebSocket errors
   - Implement retry logic
   - Log failed requests

---

**Last Updated**: 2024
**Version**: 1.0.0
**Status**: Production Ready ✅
