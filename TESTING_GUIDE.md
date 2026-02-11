# 🧪 GAAIUS AI - Testing & Troubleshooting Guide

## ✅ Quick Start Checklist

### Before You Start
- [ ] MongoDB is running (default: localhost:27017)
- [ ] Python 3.8+ installed
- [ ] Node.js 16+ installed
- [ ] All dependencies installed

### Starting the Backend
```powershell
# In PowerShell, from project root:
cd f:\gaaius-aiX\gaaius-ai
$env:GROQ_API_KEY = 'test-key'
$env:MONGO_URL = 'mongodb://127.0.0.1:27017'
$env:DB_NAME = 'gaaius'
python -m uvicorn backend.server:app --host 127.0.0.1 --port 8000 --reload
```

Expected output:
```
Uvicorn running on http://127.0.0.1:8000
Press CTRL+C to quit
```

### Starting the Frontend
```powershell
# In another PowerShell window:
cd f:\gaaius-aiX\gaaius-ai\frontend
npm start
```

Expected output:
```
Compiled successfully!
You can now view frontend in the browser.
Local: http://localhost:3000
```

---

## 🌐 Testing the Features

### 1. Image Resizer

**Test Route**: http://localhost:3000/image-resizer

**Manual API Test** (using curl or Postman):
```bash
curl -X POST http://localhost:8000/api/image/resize \
  -F "file=@path/to/image.jpg" \
  -F "width=800" \
  -F "height=600" \
  -F "format=jpeg"
```

**Expected Response**:
```json
{
  "id": "uuid-string",
  "url": "/api/static/images/resized_uuid.jpeg",
  "width": 800,
  "height": 600,
  "format": "jpeg",
  "timestamp": "2026-01-15T..."
}
```

**What to Verify**:
- [ ] Upload form appears
- [ ] Can select image file
- [ ] Preview shows image
- [ ] Can enter width/height
- [ ] Can lock aspect ratio
- [ ] Can select format
- [ ] Resize button works
- [ ] Download button appears after resize
- [ ] History shows previous resizes

---

### 2. Image Converter

**Test Route**: http://localhost:3000/image-converter

**Manual API Test**:
```bash
curl -X POST http://localhost:8000/api/image/convert \
  -F "file=@path/to/image.jpg" \
  -F "format=png" \
  -F "quality=90"
```

**Expected Response**:
```json
{
  "id": "uuid-string",
  "url": "/api/static/images/converted_uuid.png",
  "format": "png",
  "quality": 90,
  "timestamp": "2026-01-15T..."
}
```

**What to Verify**:
- [ ] Upload form appears
- [ ] Can select image file
- [ ] Preview shows image
- [ ] Can select format (7 formats available)
- [ ] Quality slider works (10-100%)
- [ ] Convert button works
- [ ] Download button appears after conversion
- [ ] Conversion history shows operations

---

### 3. VIDEOS

**Test Route**: http://localhost:3000/multitube

**Manual API Test**:
```bash
curl -X POST http://localhost:8000/api/videos/upload \
  -F "file=@path/to/video.mp4" \
  -F "title=My Video" \
  -F "description=Video description" \
  -F "tags=tag1,tag2,tag3"
```

**Get Videos**:
```bash
curl -X GET "http://localhost:8000/api/videos/videos?skip=0&limit=20&search="
```

**Expected Response (Upload)**:
```json
{
  "id": "uuid-string",
  "user_id": "user-uuid",
  "title": "My Video",
  "description": "Video description",
  "tags": ["tag1", "tag2", "tag3"],
  "url": "/api/static/videos/video_uuid.mp4",
  "views": 0,
  "likes": 0,
  "timestamp": "2026-01-15T..."
}
```

**What to Verify**:
- [ ] Upload form appears
- [ ] Can select video file
- [ ] Can enter title (required)
- [ ] Can enter description
- [ ] Can enter tags
- [ ] Progress bar shows upload progress
- [ ] Upload completes successfully
- [ ] Video appears in grid/list
- [ ] Can search by title
- [ ] Can filter by tags
- [ ] View counter works
- [ ] Grid/list view toggle works

---

### 4. Music Streaming

**Test Route**: http://localhost:3000/music

**Manual API Test (Upload)**:
```bash
curl -X POST http://localhost:8000/api/music/upload \
  -F "file=@path/to/song.mp3" \
  -F "title=Song Title" \
  -F "artist=Artist Name" \
  -F "album=Album Name"
```

**Get Tracks**:
```bash
curl -X GET "http://localhost:8000/api/music/tracks?skip=0&limit=50&search="
```

**Get Playlists**:
```bash
curl -X GET "http://localhost:8000/api/music/playlists"
```

**Create Playlist**:
```bash
curl -X POST http://localhost:8000/api/music/playlists \
  -d "name=My Playlist&description=My favorite songs"
```

**Add Track to Playlist**:
```bash
curl -X POST http://localhost:8000/api/music/playlists/{playlist_id}/tracks \
  -d "track_id={track_id}"
```

**Expected Response (Upload)**:
```json
{
  "id": "uuid-string",
  "user_id": "user-uuid",
  "title": "Song Title",
  "artist": "Artist Name",
  "album": "Album Name",
  "url": "/api/static/audio/track_uuid.mp3",
  "duration": 0,
  "plays": 0,
  "likes": 0,
  "timestamp": "2026-01-15T..."
}
```

**What to Verify**:
- [ ] Upload form appears
- [ ] Can select audio file
- [ ] Can enter title (required)
- [ ] Can enter artist (required)
- [ ] Can enter album
- [ ] Upload completes
- [ ] Track appears in list
- [ ] Can search by title/artist
- [ ] Playlist creation works
- [ ] Can add tracks to playlist
- [ ] Music player controls work
- [ ] Play/pause button works
- [ ] Skip buttons work
- [ ] Volume control works
- [ ] Recently played shows tracks
- [ ] Sidebar shows playlists

---

## 🔧 Troubleshooting

### Backend Won't Start

**Error**: `ModuleNotFoundError: No module named 'PIL'`
```bash
pip install Pillow
```

**Error**: `Connection refused` (MongoDB)
```bash
# Make sure MongoDB is running:
# Windows: mongod.exe from installation folder
# Or use MongoDB Atlas (cloud version)
```

**Error**: `Port 8000 already in use`
```bash
# Change port in command:
python -m uvicorn backend.server:app --host 127.0.0.1 --port 8001
```

### Frontend Won't Start

**Error**: `npm ERR!`
```bash
cd frontend
rm -r node_modules
npm cache clean --force
npm install --legacy-peer-deps
npm start
```

**Error**: `Port 3000 already in use`
```bash
# Kill process on port 3000:
# Windows: netstat -ano | findstr :3000
# Then: taskkill /PID <PID> /F
```

### API Calls Not Working

**Error**: `CORS error`
```
# Backend needs CORS enabled
# Already enabled in server.py, check:
# app.add_middleware(CORSMiddleware, ...)
```

**Error**: `401 Unauthorized`
```
# You need to be logged in
# Frontend should have auth token
# Check browser localStorage
```

**Error**: `413 Payload Too Large`
```
# Increase upload limits in main.py
# Or reduce file size
```

### File Upload Not Working

**Check**:
1. Is backend running? (http://localhost:8000/health)
2. Is MongoDB running? (check logs)
3. Is file size under limit?
   - Images: 50MB
   - Videos: 500MB
   - Audio: 50MB
4. Is file format correct?
   - Images: jpg, png, gif, etc.
   - Videos: mp4, mov, avi, etc.
   - Audio: mp3, wav, m4a, etc.

---

## 📊 API Testing Tools

### Postman (Recommended)
1. Download: https://www.postman.com/downloads/
2. Create new request: `POST http://localhost:8000/api/image/resize`
3. Go to "Body" tab → Select "form-data"
4. Add form fields as shown above
5. Click "Send"

### cURL (Command Line)
```bash
# Already shown in examples above
# Use with files from your system
```

### Thunder Client (VS Code Extension)
1. Install extension
2. Create new request
3. Fill in details
4. Send request
5. See response

### API Documentation
Visit: http://localhost:8000/docs
- Interactive API docs
- Try requests directly
- See response schemas

---

## 📝 Database Verification

### Check if MongoDB is Running
```bash
# Windows - check if service is running
Get-Service -Name MongoDB

# Or test connection:
python -c "from pymongo import MongoClient; client = MongoClient('mongodb://localhost:27017'); print(client.server_info())"
```

### View Collections
```bash
# Using MongoDB Compass (GUI):
# 1. Download from: https://www.mongodb.com/try/download/compass
# 2. Connect to: mongodb://localhost:27017
# 3. Browse databases and collections

# Or using command line:
mongosh
use gaaius
db.resizes.find()
db.conversions.find()
db.videos.find()
db.tracks.find()
db.playlists.find()
```

---

## 🎯 Feature-by-Feature Testing

### Image Resizer Full Test
```
1. Navigate to http://localhost:3000/image-resizer
2. Click "Choose File" and select an image
3. Image preview should show
4. Enter width: 800, height: 600
5. Check "Lock Aspect Ratio"
6. Select format: "PNG"
7. Click "Resize Image"
8. Wait for processing
9. "Download" button should appear
10. Click download and verify file
11. Check "History" section shows operation
```

### Image Converter Full Test
```
1. Navigate to http://localhost:3000/image-converter
2. Click "Choose File" and select an image
3. Image preview should show
4. Click "PNG" format button
5. Adjust quality slider to 85
6. Click "Convert Image"
7. Wait for processing
8. "Download" button should appear
9. Click download and verify file
10. Check "History" section shows operation
```

### VIDEOS Full Test
```
1. Navigate to http://localhost:3000/multitube
2. Click "Upload Video"
3. Select a video file
4. Enter title: "My Test Video"
5. Enter description: "Test description"
6. Enter tags: "test,video,upload"
7. Click "Upload"
8. See progress bar
9. Wait for completion
10. Video should appear in grid
11. Click on video to view details
12. Test search bar with keywords
13. Test grid/list view toggle
14. Verify view counter
15. Check date display
```

### Music Full Test
```
1. Navigate to http://localhost:3000/music
2. Click "Upload Music"
3. Select an audio file
4. Enter title: "Test Song"
5. Enter artist: "Test Artist"
6. Enter album: "Test Album"
7. Click "Upload"
8. Wait for completion
9. Track should appear in list
10. Click play button on track
11. Music should play (or show in queue)
12. Test skip controls
13. Test volume control
14. Create new playlist: "Test Playlist"
15. Add song to playlist
16. View playlist and verify it contains song
17. Test search by title/artist
18. Check "Recently Played" section
```

---

## 🚨 Common Issues & Fixes

| Issue | Cause | Fix |
|-------|-------|-----|
| Can't upload files | Backend not running | Start backend: `python -m uvicorn backend.server:app --host 127.0.0.1 --port 8000` |
| Files not saving | MongoDB not running | Start MongoDB service or use Atlas |
| "CORS error" | Backend CORS not enabled | Check server.py has CORSMiddleware |
| "405 Method Not Allowed" | Wrong HTTP method | Verify POST/GET in request |
| "413 Payload Too Large" | File too big | Check file size limits |
| "404 Not Found" | Wrong endpoint path | Verify URL: /api/image/resize |
| "500 Internal Error" | Backend exception | Check backend logs for error |
| Files show 404 | Files not in static folder | Check directory permissions |
| Search not working | Database empty | Upload files first |
| Player controls broken | Audio file format issue | Try different audio format |

---

## 📈 Performance Testing

### Load Testing
```bash
# Using Apache Bench (ab):
ab -n 100 -c 10 http://localhost:8000/api/videos/videos

# Results show:
# - Requests per second
# - Time per request
# - Connection times
```

### Memory Usage
```bash
# Monitor backend:
tasklist | findstr python

# Monitor frontend:
tasklist | findstr node
```

---

## 🎓 Learning Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **React Docs**: https://react.dev/
- **MongoDB Docs**: https://docs.mongodb.com/
- **Tailwind CSS**: https://tailwindcss.com/

---

## ✅ Final Verification

Before considering complete, verify:

- [ ] All 4 features accessible from main menu
- [ ] Each feature has dedicated page
- [ ] Upload functionality works
- [ ] Search functionality works
- [ ] Data persists in database
- [ ] No console errors
- [ ] No network errors
- [ ] Responsive on mobile
- [ ] All buttons functional
- [ ] Download works
- [ ] Delete works (if implemented)
- [ ] Player controls work (music)
- [ ] Playlists work (music)

---

**Happy Testing! 🎉**
