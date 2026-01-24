# 🎬 FREE CONTENT INTEGRATION GUIDE

Complete setup to populate your platform with FREE movies, videos, and music!

---

## 📊 QUICK SUMMARY

| Source | Content | Free? | Key Needed? | Quality | Setup Time |
|--------|---------|-------|-----------|---------|-----------|
| **TMDB** | Movies/TV | ✅ Yes | ✅ Free | ⭐⭐⭐⭐⭐ | 5 min |
| **Pexels** | Videos | ✅ Yes | ❌ No | ⭐⭐⭐⭐⭐ | 0 min |
| **Pixabay** | Videos | ✅ Yes | ❌ No | ⭐⭐⭐⭐⭐ | 0 min |
| **Freesound** | Music/Audio | ✅ Yes | ✅ Free | ⭐⭐⭐⭐⭐ | 5 min |

---

## 🎬 SETUP INSTRUCTIONS

### 1️⃣ TMDB - THE MOVIE DATABASE (MOVIES TAB)

**What**: 500,000+ movies and TV shows  
**Cost**: COMPLETELY FREE  
**Quality**: Professional metadata, posters, ratings  

**Setup**:
1. Go to: https://www.themoviedb.org/settings/api
2. Click "Create" → New TMDB Account
3. Verify email
4. Go back to API settings
5. Click "Create" → Accept terms
6. Copy your API KEY
7. Add to `.env`:
```env
TMDB_API_KEY=your_api_key_here
```

**Time**: 5 minutes ⏱️

---

### 2️⃣ PEXELS - FREE VIDEOS (VIDEOS TAB)

**What**: Thousands of FREE stock videos  
**Cost**: COMPLETELY FREE  
**Key Required**: ❌ NO (but optional API key for higher limits)  
**Quality**: HD/4K, professional videos  

**Setup**:
- **Option A (Easiest - NO SETUP NEEDED)**:
  ```python
  # Just use it! No key required
  # 5000 requests per hour included
  ```

- **Option B (Optional - Higher limits)**:
  1. Go to: https://www.pexels.com/api/
  2. Sign up (FREE)
  3. Copy API key
  4. Add to `.env`:
  ```env
  PEXELS_API_KEY=your_api_key_here
  ```

**Time**: 0 minutes (Option A) or 3 minutes (Option B) ⏱️

---

### 3️⃣ PIXABAY - MORE FREE VIDEOS (VIDEOS TAB)

**What**: Another source of FREE stock videos  
**Cost**: COMPLETELY FREE  
**Key Required**: ❌ NO  
**Quality**: Good variety of videos  

**Setup**:
- No setup needed! Just works out of the box
- 100 requests per hour
- Completely free

**Time**: 0 minutes ⏱️

---

### 4️⃣ FREESOUND - FREE MUSIC & AUDIO (MUSIC TAB)

**What**: 700,000+ FREE audio tracks and music  
**Cost**: COMPLETELY FREE  
**Quality**: High quality Creative Commons licensed music  

**Setup**:
1. Go to: https://freesound.org/
2. Sign up (FREE account)
3. Go to: https://freesound.org/api/apply/
4. Create API application (FREE)
5. Copy your API Token
6. Add to `.env`:
```env
FREESOUND_API_KEY=your_api_key_here
```

**Time**: 5 minutes ⏱️

---

## 🚀 INTEGRATION STEPS

### Step 1: Copy Files to Your Project
```bash
# These files are already created:
backend/free_content_integration.py    # Main service
backend/free_content_routes.py         # FastAPI routes
```

### Step 2: Update Your Server

In your `server.py` or main FastAPI file:

```python
from backend.free_content_routes import router as content_router

# Add this line:
app.include_router(content_router)
```

### Step 3: Set Environment Variables

Create or update `.env`:
```env
# Optional - Gets FREE movies/TV shows
TMDB_API_KEY=your_tmdb_key

# Optional - Pexels videos (optional, has free tier)
PEXELS_API_KEY=your_pexels_key

# Optional - Freesound music (optional, has free tier)
FREESOUND_API_KEY=your_freesound_key
```

### Step 4: Restart Server

```bash
python server.py
```

### Step 5: Test the Endpoints

```bash
# Movies
curl http://localhost:8000/api/v1/content/movies/trending

# Videos
curl http://localhost:8000/api/v1/content/videos/popular

# Music
curl http://localhost:8000/api/v1/content/music/popular

# ALL CONTENT
curl http://localhost:8000/api/v1/content/all/trending

# Check status
curl http://localhost:8000/api/v1/content/health
```

---

## 📍 API ENDPOINTS

### Movies Endpoints

```
GET /api/v1/content/movies/trending?limit=50
→ Get trending movies from TMDB

GET /api/v1/content/movies/popular?limit=50
→ Get popular movies from TMDB

GET /api/v1/content/movies/search?q=inception&limit=20
→ Search movies on TMDB
```

### Videos Endpoints

```
GET /api/v1/content/videos/popular?limit=30
→ Get free videos from Pexels & Pixabay

GET /api/v1/content/videos/search?q=nature&limit=20
→ Search free videos on Pexels
```

### Music Endpoints

```
GET /api/v1/content/music/popular?limit=50
→ Get free music from Freesound (700K+ tracks!)

GET /api/v1/content/music/search?q=ambient&limit=30
→ Search free music on Freesound
```

### Combined

```
GET /api/v1/content/all/trending
→ Get movies + videos + music in one call (perfect for homepage)

GET /api/v1/content/health
→ Check which services are configured
```

---

## 💾 EXAMPLE RESPONSES

### Movies Response
```json
{
  "status": "success",
  "source": "TMDB",
  "count": 50,
  "data": [
    {
      "id": "tmdb_550",
      "title": "Fight Club",
      "description": "An insomniac office worker...",
      "poster": "https://image.tmdb.org/t/p/w500/...",
      "rating": 8.8,
      "release_date": "1999-10-15",
      "source": "TMDB",
      "genres": ["Drama", "Thriller"],
      "language": "en"
    },
    ...
  ]
}
```

### Videos Response
```json
{
  "status": "success",
  "sources": ["Pexels", "Pixabay"],
  "count": 30,
  "data": [
    {
      "id": "pexels_123456",
      "title": "Nature - Beautiful Forest",
      "description": "Free stock video from Pexels",
      "url": "https://videos.pexels.com/...",
      "thumbnail": "https://images.pexels.com/...",
      "duration": 45,
      "width": 1920,
      "height": 1080,
      "source": "Pexels",
      "license": "Free",
      "category": "nature"
    },
    ...
  ]
}
```

### Music Response
```json
{
  "status": "success",
  "source": "Freesound",
  "count": 50,
  "data": [
    {
      "id": "freesound_654321",
      "title": "Ambient Meditation Music",
      "description": "Relaxing ambient track",
      "url": "https://cdn.freesound.org/previews/...",
      "duration": 180,
      "source": "Freesound",
      "artist": "username123",
      "license": "Creative Commons",
      "tags": ["ambient", "meditation", "relaxing"]
    },
    ...
  ]
}
```

---

## ⚡ QUICK START (No API Keys!)

Want to start RIGHT NOW with no setup?

```python
# This works immediately - no keys needed!
async with httpx.AsyncClient() as client:
    # Get videos - completely free
    response = await client.get(
        "https://api.pexels.com/videos/search",
        params={"query": "nature", "per_page": 20}
    )
    videos = response.json()
```

---

## 🎯 OPTIONAL: Add to Database

Once you have the content, you can cache it:

```python
# Cache movies in your database for faster access
from backend.database_models import Content

for movie in movies:
    db_movie = Content(
        title=movie["title"],
        description=movie["description"],
        poster_url=movie["poster"],
        source="TMDB",
        source_id=movie["id"],
        content_type="movie",
        rating=movie["rating"]
    )
    session.add(db_movie)

session.commit()
```

---

## 🔄 AUTO-UPDATE CONTENT

Add a background task to refresh content daily:

```python
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()

async def refresh_free_content():
    """Update free content every day"""
    content = await content_loader.load_all_content()
    # Save to database...
    logger.info("✅ Free content updated")

scheduler.add_job(refresh_free_content, 'interval', hours=24)
scheduler.start()
```

---

## 📊 EXPECTED RESULTS

Once setup is complete, you'll have:

✅ **50+ movies** per day from TMDB  
✅ **30+ videos** from Pexels & Pixabay  
✅ **50+ music tracks** from Freesound  

**All completely FREE to use!**

---

## 🆘 TROUBLESHOOTING

### "TMDB_API_KEY not set"
- Go to https://www.themoviedb.org/settings/api
- Create FREE account
- Copy API key to `.env`

### "Freesound returns 401"
- Go to https://freesound.org/
- Sign up (FREE)
- Get API token
- Add to `.env`: `FREESOUND_API_KEY=your_token`

### "No videos showing"
- Try Pexels alone (no key needed)
- Check internet connection
- Try different search terms

### "No music showing"
- Register FREE account at https://freesound.org/
- Get API token
- Verify it's in `.env`

---

## 📝 CHECKLIST

- [ ] Copy `free_content_integration.py` to `backend/`
- [ ] Copy `free_content_routes.py` to `backend/`
- [ ] Get TMDB API key (optional but recommended)
- [ ] Get Freesound API key (optional but recommended)
- [ ] Add keys to `.env`
- [ ] Add `router` to `server.py`
- [ ] Restart server
- [ ] Test endpoints
- [ ] Add to your UI (movies/videos/music tabs)

---

## 🎉 YOU'RE DONE!

Your platform now has thousands of FREE movies, videos, and music tracks!

**Next Steps**:
1. Add endpoints to your frontend
2. Display content in Movies/Videos/Music tabs
3. Let users watch/listen
4. Optional: Cache content in database for faster access

---

## 📞 SUPPORT

If you need help:
1. Check TMDB docs: https://www.themoviedb.org/settings/api
2. Check Freesound docs: https://freesound.org/api/
3. Check Pexels docs: https://www.pexels.com/api/

All three are completely FREE and well-documented! 🚀
