"""
INTEGRATION EXAMPLE - Add this to your server.py
"""

# ============================================================================
# OPTION 1: MINIMAL INTEGRATION (Recommended)
# ============================================================================

# At the top of your server.py file:

from fastapi import FastAPI
from backend.free_content_routes import router as content_router

app = FastAPI()

# Add the free content routes:
app.include_router(content_router)

# That's it! You're done!
# Your endpoints are now available:
# - /api/v1/content/movies/trending
# - /api/v1/content/videos/popular
# - /api/v1/content/music/popular
# - /api/v1/content/all/trending
# - etc.


# ============================================================================
# OPTION 2: FULL INTEGRATION WITH YOUR EXISTING ROUTES
# ============================================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.free_content_routes import router as content_router

app = FastAPI(
    title="Netflix Clone with Free Content",
    description="Integrated with 1.3M+ free movies, videos, and music"
)

# Add CORS (if needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add your existing routes
# app.include_router(existing_routes)

# Add free content routes
app.include_router(content_router)

# Health check
@app.get("/health")
async def health():
    return {"status": "healthy"}


# ============================================================================
# OPTION 3: ADVANCED - WITH CACHING
# ============================================================================

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from backend.free_content_routes import router as content_router
from backend.free_content_integration import FreeContentLoader
import asyncio
from datetime import datetime, timedelta

app = FastAPI()

# Initialize loader
content_loader = FreeContentLoader()
cached_content = None
cache_timestamp = None
CACHE_DURATION = 3600  # 1 hour

async def get_cached_content():
    """Get cached content or refresh if expired"""
    global cached_content, cache_timestamp
    
    now = datetime.utcnow()
    if cached_content is None or cache_timestamp is None or \
       (now - cache_timestamp).seconds > CACHE_DURATION:
        # Refresh cache
        cached_content = await content_loader.load_all_content()
        cache_timestamp = now
    
    return cached_content

# Add a super-fast endpoint that serves cached content
@app.get("/api/v1/content/cached")
async def get_cached_all_content():
    """
    Super fast endpoint - returns cached content (refreshed every hour)
    Perfect for homepage/feed
    """
    content = await get_cached_content()
    return {
        "status": "success",
        "data": content,
        "note": "Content cached for 1 hour"
    }

# Add the routes
app.include_router(content_router)

# Background task to pre-warm cache on startup
@app.on_event("startup")
async def startup_event():
    """Pre-warm cache on startup"""
    print("🔄 Pre-warming content cache...")
    await get_cached_content()
    print("✅ Cache ready!")


# ============================================================================
# OPTION 4: WITH YOUR EXISTING PHASE 9 CODE
# ============================================================================

from fastapi import FastAPI
from backend.free_content_routes import router as content_router
from backend.authentication_service import AuthenticationService
from backend.payment_service import StripePaymentProcessor
from backend.search_service import SearchService

app = FastAPI()

# Your existing services
auth_service = AuthenticationService()
payment_service = StripePaymentProcessor()
search_service = SearchService()

# Add free content routes
app.include_router(content_router)

# Your existing routes would go here...
# app.include_router(auth_routes)
# app.include_router(payment_routes)
# etc.


# ============================================================================
# ENVIRONMENT VARIABLES (.env file)
# ============================================================================

# Make sure your .env file has:
# TMDB_API_KEY=your_key_from_https://www.themoviedb.org/settings/api
# FREESOUND_API_KEY=your_key_from_https://freesound.org/

# Optional:
# PEXELS_API_KEY=optional


# ============================================================================
# TESTING - Quick test all endpoints
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    # Run with: python server.py
    # Then test with:
    # curl http://localhost:8000/api/v1/content/videos/popular
    # curl http://localhost:8000/api/v1/content/all/trending
    
    uvicorn.run(app, host="0.0.0.0", port=8000)


# ============================================================================
# USAGE IN YOUR FRONTEND
# ============================================================================

"""
JavaScript/React Example:

// Get trending movies
const movies = await fetch(
  '/api/v1/content/movies/trending?limit=20'
).then(r => r.json());

// Get free videos
const videos = await fetch(
  '/api/v1/content/videos/popular?limit=20'
).then(r => r.json());

// Get free music
const music = await fetch(
  '/api/v1/content/music/popular?limit=20'
).then(r => r.json());

// Get all at once
const allContent = await fetch(
  '/api/v1/content/all/trending'
).then(r => r.json());

// Search
const results = await fetch(
  '/api/v1/content/movies/search?q=inception&limit=10'
).then(r => r.json());
"""


# ============================================================================
# API RESPONSE EXAMPLES
# ============================================================================

"""
GET /api/v1/content/movies/trending
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
    }
  ]
}

GET /api/v1/content/videos/popular
{
  "status": "success",
  "sources": ["Pexels", "Pixabay"],
  "count": 30,
  "data": [
    {
      "id": "pexels_123456",
      "title": "Nature - Beautiful Forest",
      "url": "https://videos.pexels.com/...",
      "thumbnail": "https://images.pexels.com/...",
      "duration": 45,
      "source": "Pexels",
      "license": "Free"
    }
  ]
}

GET /api/v1/content/music/popular
{
  "status": "success",
  "source": "Freesound",
  "count": 50,
  "data": [
    {
      "id": "freesound_654321",
      "title": "Ambient Meditation Music",
      "url": "https://cdn.freesound.org/previews/...",
      "duration": 180,
      "source": "Freesound",
      "artist": "username123",
      "license": "Creative Commons",
      "tags": ["ambient", "meditation"]
    }
  ]
}
"""
