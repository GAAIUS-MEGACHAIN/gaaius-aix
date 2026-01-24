# Audio Converter - Complete Integration Guide

**Status**: ✅ **READY TO USE**  
**Tech Stack**: FastAPI (Backend) + React + Material-UI (Frontend)  
**Dependencies**: FFmpeg (system level)  
**Setup Time**: 5 minutes  

---

## What This Does

Professional audio format converter that supports:

✅ **8 Audio Formats**:
- MP3 (lossy, 64-320 kbps)
- WAV (lossless)
- FLAC (lossless, compressed)
- OGG Vorbis (lossy, 64-256 kbps)
- M4A/AAC (lossy, 64-320 kbps)
- AAC (lossy, 64-320 kbps)
- Opus (modern, 64-256 kbps)
- WMA (lossy, 64-320 kbps)

✅ **Quality Settings**: 6 bitrate options (64 kbps → Lossless)

✅ **Features**:
- Drag-and-drop upload
- Batch conversion support (future)
- Audio file analysis (duration, bitrate, sample rate, channels)
- Conversion history
- Download converted files
- Delete files

---

## Quick Setup (5 minutes)

### Step 1: Install FFmpeg

**Windows (PowerShell)**:
```powershell
# Using Chocolatey
choco install ffmpeg

# Or download from https://ffmpeg.org/download.html
```

**Mac**:
```bash
brew install ffmpeg
```

**Linux**:
```bash
sudo apt-get install ffmpeg  # Debian/Ubuntu
sudo yum install ffmpeg      # CentOS/RHEL
```

### Step 2: Integrate Backend

In `server.py`:

```python
from backend.audio_converter_service import init_audio_converter_service
from backend.audio_converter_routes import router as audio_router

# On startup:
@app.on_event("startup")
async def startup():
    await init_audio_converter_service()
    logger.info("Audio converter service started")

# Add router:
app.include_router(audio_router, prefix="/api/v1")
```

### Step 3: Add React Component to Menu

Choose ONE of the 10 menu options (or use all!):

**Option 1: Navbar Button (Recommended)**
```jsx
import AudioConverterMenuOptions from './components/menu/AudioConverterMenu';

// In your Navbar component:
<AudioConverterMenuOptions.Option1NavbarButton />
```

**Option 3: Floating Button (Best for mobile)**
```jsx
<AudioConverterMenuOptions.Option3FloatingButton />
```

**Option 6: Dashboard Card**
```jsx
<AudioConverterMenuOptions.Option6CardGrid />
```

### Step 4: Test It!

```bash
# Start backend
python server.py

# Start frontend
npm start

# Click the "Audio Converter" button and upload an MP3
```

---

## 10 Menu Integration Options

### 1️⃣ Navbar Button (Top Header)
```jsx
<AudioConverterMenuOptions.Option1NavbarButton />
```
- Visible in app header
- Professional appearance
- Always accessible

### 2️⃣ Sidebar Menu Item
```jsx
<AudioConverterMenuOptions.Option2SidebarMenu />
```
- Integrated in left sidebar
- With description text
- Icon + label

### 3️⃣ Floating Action Button (FAB)
```jsx
<AudioConverterMenuOptions.Option3FloatingButton />
```
- Bottom-right corner
- Always floating
- Mobile-friendly

### 4️⃣ Dropdown Menu
```jsx
<AudioConverterMenuOptions.Option4DropdownMenu />
```
- In "Tools" or similar menu
- Clean, space-saving
- Grouped with other tools

### 5️⃣ Tabbed Interface
```jsx
<AudioConverterMenuOptions.Option5TabbedInterface />
```
- Tab in main navigation
- Content area below tabs
- Dashboard-style

### 6️⃣ Dashboard Card Grid
```jsx
<AudioConverterMenuOptions.Option6CardGrid />
```
- Card in feature grid
- Icon + description
- Clickable card

### 7️⃣ Speed Dial (Floating Menu)
```jsx
<AudioConverterMenuOptions.Option7SpeedDial />
```
- Multi-action floating menu
- Expandable
- Multiple related tools

### 8️⃣ Badge Notification
```jsx
<AudioConverterMenuOptions.Option8BadgeNotification />
```
- Button with notification badge
- Show conversion count
- Alert status

### 9️⃣ Chip Group
```jsx
<AudioConverterMenuOptions.Option9ChipGroup />
```
- Horizontal chip layout
- Multiple tools in row
- Compact design

### 🔟 Modal Launcher
```jsx
<AudioConverterMenuOptions.Option10ModalLauncher />
```
- Info dialog before converter
- Explanation of features
- "Learn more" pattern

---

## API Endpoints (7 Total)

### 1. Upload Audio File
```
POST /api/v1/audio/upload
Content-Type: multipart/form-data

Parameters:
- file: Binary audio file
- user_id: User identifier

Response:
{
  "id": "audio_abc123",
  "filename": "song.mp3",
  "format": "mp3",
  "file_size": 5242880,
  "duration": 180.5,
  "bitrate": "128",
  "sample_rate": 44100,
  "channels": 2,
  "uploaded_at": "2024-01-17T10:30:00Z"
}
```

### 2. Convert Audio
```
POST /api/v1/audio/convert

Body:
{
  "user_id": "user123",
  "audio_file_id": "audio_abc123",
  "target_format": "flac",
  "target_bitrate": "lossless"
}

Response:
{
  "id": "conv_xyz789",
  "original_file_id": "audio_abc123",
  "filename": "song.flac",
  "format": "flac",
  "bitrate": "lossless",
  "file_size": 52428800,
  "duration": 180.5,
  "converted_at": "2024-01-17T10:35:00Z"
}
```

### 3. Get Audio File Info
```
GET /api/v1/audio/file/{file_id}

Response: AudioFileResponse (same as upload response)
```

### 4. Get Converted File Info
```
GET /api/v1/audio/converted/{file_id}

Response: ConvertedFileResponse (same as convert response)
```

### 5. Get User Conversion History
```
GET /api/v1/audio/history/{user_id}

Response: List[ConvertedFileResponse]
```

### 6. Delete Converted File
```
DELETE /api/v1/audio/delete/{file_id}

Response:
{
  "status": "success",
  "message": "File deleted"
}
```

### 7. Get Supported Formats & Bitrates
```
GET /api/v1/audio/formats

Response:
{
  "formats": [
    {"name": "MP3", "value": "mp3", "lossless": false},
    {"name": "WAV", "value": "wav", "lossless": true},
    ...
  ],
  "bitrates": [
    {"label": "Phone (64 kbps)", "value": "64", "quality": "low"},
    ...
  ]
}
```

---

## Format Comparison

| Format | Quality | File Size | Use Case |
|--------|---------|-----------|----------|
| **MP3** | Lossy | Small | Streaming, sharing |
| **FLAC** | Lossless | Large | Archival, audiophiles |
| **WAV** | Lossless | Large | Professional, editing |
| **OGG** | Lossy | Small | Open source (Opus/Vorbis) |
| **M4A** | Lossy | Small | Apple devices |
| **AAC** | Lossy | Small | Modern standard |
| **Opus** | Lossy | Very Small | Streaming, voice |
| **WMA** | Lossy | Small | Windows legacy |

---

## Bitrate Recommendations

| Bitrate | Quality | Use Case | File Size |
|---------|---------|----------|-----------|
| **64 kbps** | Phone quality | Voice, audiobooks | Very small |
| **128 kbps** | Good quality | Mobile, web | Small |
| **192 kbps** | Very good | Standard streaming | Medium |
| **256 kbps** | Excellent | High-quality streaming | Medium |
| **320 kbps** | Highest | Best quality MP3 | Larger |
| **Lossless** | Perfect | Archival, editing | Large |

---

## Code Examples

### JavaScript (React)
```javascript
import AudioConverter from './components/AudioConverter';

export default function App() {
  const [open, setOpen] = useState(false);

  return (
    <>
      <button onClick={() => setOpen(true)}>
        🎵 Convert Audio
      </button>
      <AudioConverter open={open} onClose={() => setOpen(false)} />
    </>
  );
}
```

### Python (FastAPI)
```python
from backend.audio_converter_service import get_conversion_manager, AudioFormat, AudioBitrate

manager = get_conversion_manager()

# Upload audio
audio_file = await manager.upload_audio(
    user_id="user123",
    file_path="song.mp3"
)

# Convert audio
converted_file, error = await manager.convert_audio(
    user_id="user123",
    audio_file_id=audio_file.id,
    target_format=AudioFormat.FLAC,
    target_bitrate=AudioBitrate.LOSSLESS
)

if not error:
    print(f"Converted: {converted_file.filename}")
```

---

## Customization

### Add New Format
1. Add to `AudioFormat` enum in `audio_converter_service.py`
2. Add codec mapping
3. Add to UI format list in `AudioConverter.jsx`

### Change Default Bitrate
In `AudioConverter.jsx`:
```javascript
const [selectedBitrate, setSelectedBitrate] = useState('192'); // Change from 256
```

### Customize UI
- Colors: Modify MUI theme
- Icons: Change from `@mui/icons-material`
- Layout: Modify Dialog structure

---

## Performance

**Conversion Times** (approximately):

| Format | Size | Time |
|--------|------|------|
| MP3 → FLAC (3 min song) | ~10 MB → ~30 MB | 15-30 seconds |
| MP3 → OGG (3 min song) | ~5 MB → ~3 MB | 10-20 seconds |
| WAV → MP3 (3 min song) | ~30 MB → ~5 MB | 10-20 seconds |
| Large file (1 hour) | Varies | 1-2 minutes |

**Factors**:
- Input file format
- Output format & bitrate
- Computer CPU speed
- Disk I/O speed

---

## Troubleshooting

### "FFmpeg not found"
```
→ Install FFmpeg: choco install ffmpeg (Windows)
→ Verify: ffmpeg -version
→ Add to PATH if needed
```

### "Conversion timeout"
```
→ FFmpeg is taking too long
→ Try with lower bitrate
→ Check disk space
→ File might be corrupted
```

### "Unsupported audio format"
```
→ FFmpeg can usually convert any format
→ Check if file is actually audio
→ Try with a different input file
```

### "Permission denied"
```
→ Check temp_audio and converted_audio folder permissions
→ mkdir -p temp_audio converted_audio
→ chmod 755 temp_audio converted_audio
```

### "Out of disk space"
```
→ Conversions need temp space
→ Clear converted_audio folder
→ Delete old conversions via API
```

---

## Database Integration (Future)

To persist conversions to database:

```python
# In audio_converter_service.py
async def save_conversion(self, db, user_id, converted_file):
    await db.execute(
        """INSERT INTO conversions 
        (id, user_id, original_format, target_format, bitrate, file_size)
        VALUES (?, ?, ?, ?, ?, ?)""",
        (
            converted_file.id,
            user_id,
            converted_file.original_file_id,
            converted_file.format,
            converted_file.bitrate,
            converted_file.file_size
        )
    )
```

---

## Security Considerations

✅ **Implemented**:
- File type validation
- FFmpeg safety (no shell injection)
- User isolation (user_id tracking)
- Temporary file cleanup

⏳ **To Add**:
- File size limits
- Rate limiting
- Virus scanning
- S3/cloud storage

---

## Next Steps

- ✅ Audio upload working
- ✅ Format conversion working
- ✅ 8 formats supported
- ✅ 6 quality settings
- ✅ UI component complete
- ✅ 10 menu options
- ⏳ Batch conversion
- ⏳ Database integration
- ⏳ Cloud storage
- ⏳ Progress bar

---

**Status**: 🎵 Ready to convert audio! Start using now! 🚀
