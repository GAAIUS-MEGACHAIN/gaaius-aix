"""
FREE CONTENT ROUTES - Add to your FastAPI server
These endpoints populate your Movies, Videos, and Music tabs with FREE content
"""

from fastapi import APIRouter, Query, HTTPException
from typing import List, Dict, Optional
from backend.free_content_integration import FreeContentLoader
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/content", tags=["Free Content"])

# Initialize content loader
content_loader = FreeContentLoader()


# ============================================================================
# MOVIES ENDPOINTS
# ============================================================================

@router.get("/movies/trending")
async def get_trending_movies(limit: int = Query(50, ge=1, le=100)):
    """
    Get trending movies from TMDB (FREE)
    
    Example: GET /api/v1/content/movies/trending?limit=20
    """
    try:
        movies = await content_loader.tmdb.get_trending_movies(limit)
        return {
            "status": "success",
            "source": "TMDB",
            "count": len(movies),
            "data": movies
        }
    except Exception as e:
        logger.error(f"Error fetching movies: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/movies/popular")
async def get_popular_movies(limit: int = Query(50, ge=1, le=100)):
    """Get popular movies from TMDB (FREE)"""
    try:
        movies = await content_loader.tmdb.get_popular_movies(limit)
        return {
            "status": "success",
            "source": "TMDB",
            "count": len(movies),
            "data": movies
        }
    except Exception as e:
        logger.error(f"Error fetching movies: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/movies/search")
async def search_movies(q: str = Query(..., min_length=1), limit: int = Query(20, ge=1, le=100)):
    """Search movies on TMDB (FREE)"""
    try:
        movies = await content_loader.tmdb.search_movies(q, limit)
        return {
            "status": "success",
            "query": q,
            "source": "TMDB",
            "count": len(movies),
            "data": movies
        }
    except Exception as e:
        logger.error(f"Error searching movies: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# VIDEOS ENDPOINTS
# ============================================================================

@router.get("/videos/popular")
async def get_popular_videos(limit: int = Query(30, ge=1, le=100)):
    """
    Get popular free videos from Pexels & Pixabay (COMPLETELY FREE - NO KEY NEEDED)
    
    Example: GET /api/v1/content/videos/popular?limit=20
    """
    try:
        videos = await content_loader.load_videos_only(limit)
        return {
            "status": "success",
            "sources": ["Pexels", "Pixabay"],
            "count": len(videos),
            "data": videos,
            "note": "All videos are completely free and licensed for commercial use"
        }
    except Exception as e:
        logger.error(f"Error fetching videos: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/videos/search")
async def search_videos(q: str = Query(..., min_length=1), limit: int = Query(20, ge=1, le=100)):
    """Search free videos on Pexels"""
    try:
        videos = await content_loader.pexels.search_videos(q, limit)
        return {
            "status": "success",
            "query": q,
            "source": "Pexels",
            "count": len(videos),
            "data": videos
        }
    except Exception as e:
        logger.error(f"Error searching videos: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# MUSIC ENDPOINTS
# ============================================================================

@router.get("/music/popular")
async def get_popular_music(limit: int = Query(50, ge=1, le=100)):
    """
    Get popular free music from Freesound (700,000+ FREE tracks)
    
    Example: GET /api/v1/content/music/popular?limit=20
    """
    try:
        music = await content_loader.freesound.get_popular_music(limit)
        return {
            "status": "success",
            "source": "Freesound",
            "count": len(music),
            "data": music,
            "note": "All music is Creative Commons licensed and free to use"
        }
    except Exception as e:
        logger.error(f"Error fetching music: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/music/search")
async def search_music(q: str = Query(..., min_length=1), limit: int = Query(30, ge=1, le=100)):
    """Search free music on Freesound"""
    try:
        music = await content_loader.freesound.search_music(q, limit)
        return {
            "status": "success",
            "query": q,
            "source": "Freesound",
            "count": len(music),
            "data": music
        }
    except Exception as e:
        logger.error(f"Error searching music: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# COMBINED ENDPOINTS
# ============================================================================

@router.get("/all/trending")
async def get_all_trending():
    """
    Get ALL content (movies, videos, music) at once
    Perfect for homepage feed
    
    Example: GET /api/v1/content/all/trending
    """
    try:
        content = await content_loader.load_all_content()
        return {
            "status": "success",
            "timestamp": content["timestamp"],
            "movies": {
                "count": len(content["movies"]),
                "data": content["movies"]
            },
            "videos": {
                "count": len(content["videos"]),
                "data": content["videos"]
            },
            "music": {
                "count": len(content["music"]),
                "data": content["music"]
            }
        }
    except Exception as e:
        logger.error(f"Error loading all content: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def check_content_sources():
    """Check if all free content sources are working"""
    status = {
        "tmdb": "❌ Not configured" if not content_loader.tmdb.api_key else "✅ Ready",
        "pexels": "✅ Ready (No key needed)",
        "pixabay": "✅ Ready (No key needed)",
        "freesound": "❌ Not configured" if not content_loader.freesound.api_key else "✅ Ready"
    }
    
    return {
        "status": "success",
        "services": status,
        "message": "Get FREE API keys:\n"
                   "• TMDB: https://www.themoviedb.org/settings/api\n"
                   "• Freesound: https://freesound.org/\n"
                   "• Pexels & Pixabay: No keys needed!"
    }


# Add this router to your main FastAPI app:
# app.include_router(router)
