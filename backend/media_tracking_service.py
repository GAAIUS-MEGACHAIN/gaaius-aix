"""
Media Playback Tracking Service
Tracks user playback across different content types and pages
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# MODELS
# ============================================================================

class PlaybackTrackingRequest(BaseModel):
    """Track playback session"""
    media_id: str
    user_id: str
    current_time: float
    duration: float
    content_type: str  # MUSIC, VIDEO, LIVESTREAM, PODCAST, etc
    page_context: Optional[str] = None  # chat, discover, profile, etc
    
    class Config:
        json_schema_extra = {
            "example": {
                "media_id": "123",
                "user_id": "user456",
                "current_time": 45.5,
                "duration": 180.0,
                "content_type": "MUSIC",
                "page_context": "chat"
            }
        }

class PlaybackSession(BaseModel):
    """Playback session data"""
    media_id: str
    user_id: str
    content_type: str
    start_time: datetime
    last_position: float
    duration: float
    total_watch_time: float = 0
    page_contexts: List[str] = Field(default_factory=list)
    
    class Config:
        from_attributes = True

class PlaybackHistoryResponse(BaseModel):
    """User's playback history"""
    media_id: str
    title: str
    content_type: str
    last_played: datetime
    total_watch_time: float
    last_position: float
    duration: float
    
    class Config:
        from_attributes = True

# ============================================================================
# ROUTER
# ============================================================================

router = APIRouter(prefix="/api/media/tracking", tags=["Media Tracking"])

# Store playback sessions in memory (would use MongoDB in production)
playback_sessions = {}

# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post(
    "/update",
    summary="Update playback position",
    description="Track user playback across pages and services"
)
async def update_playback(request: PlaybackTrackingRequest):
    """
    Update playback tracking for a media item.
    This endpoint is called periodically while content is playing.
    """
    try:
        session_key = f"{request.user_id}:{request.media_id}"
        
        # Get or create session
        if session_key not in playback_sessions:
            playback_sessions[session_key] = {
                "media_id": request.media_id,
                "user_id": request.user_id,
                "content_type": request.content_type,
                "start_time": datetime.utcnow(),
                "last_position": request.current_time,
                "duration": request.duration,
                "total_watch_time": 0,
                "page_contexts": [],
                "last_updated": datetime.utcnow(),
            }
        
        session = playback_sessions[session_key]
        
        # Update position
        old_time = session.get("last_position", 0)
        session["last_position"] = request.current_time
        session["duration"] = request.duration
        session["last_updated"] = datetime.utcnow()
        
        # Calculate watch time (if time moved forward)
        if request.current_time > old_time:
            watch_time = request.current_time - old_time
            session["total_watch_time"] = session.get("total_watch_time", 0) + watch_time
        
        # Track page context
        if request.page_context and request.page_context not in session["page_contexts"]:
            session["page_contexts"].append(request.page_context)
        
        logger.info(
            f"Tracked playback: {request.media_id} "
            f"({request.current_time}/{request.duration}s) "
            f"at {request.page_context or 'unknown'}"
        )
        
        return {
            "success": True,
            "message": "Playback tracked successfully",
            "session_key": session_key,
            "watch_time": session["total_watch_time"],
        }
    except Exception as e:
        logger.error(f"Error tracking playback: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/session/{user_id}/{media_id}",
    response_model=PlaybackSession,
    summary="Get current playback session",
    description="Retrieve playback progress for resuming"
)
async def get_playback_session(user_id: str, media_id: str):
    """
    Get the current playback session for a user and media item.
    Used to resume playback when navigating back.
    """
    try:
        session_key = f"{user_id}:{media_id}"
        
        if session_key not in playback_sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return playback_sessions[session_key]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting playback session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/history/{user_id}",
    response_model=List[PlaybackHistoryResponse],
    summary="Get user playback history",
    description="Get all recently played media by user"
)
async def get_playback_history(
    user_id: str,
    limit: int = Query(10, ge=1, le=100),
    content_type: Optional[str] = None
):
    """
    Get the playback history for a user.
    Can filter by content type (MUSIC, VIDEO, LIVESTREAM, etc).
    """
    try:
        # Filter sessions by user_id
        user_sessions = [
            session for key, session in playback_sessions.items()
            if session["user_id"] == user_id
        ]
        
        # Filter by content type if specified
        if content_type:
            user_sessions = [
                s for s in user_sessions
                if s["content_type"] == content_type
            ]
        
        # Sort by last updated (most recent first)
        user_sessions.sort(
            key=lambda x: x.get("last_updated", datetime.min),
            reverse=True
        )
        
        # Limit results
        user_sessions = user_sessions[:limit]
        
        # Format response
        return [
            {
                "media_id": s["media_id"],
                "title": f"Media {s['media_id']}",  # Would get from DB
                "content_type": s["content_type"],
                "last_played": s.get("last_updated", datetime.utcnow()),
                "total_watch_time": s.get("total_watch_time", 0),
                "last_position": s.get("last_position", 0),
                "duration": s.get("duration", 0),
            }
            for s in user_sessions
        ]
    except Exception as e:
        logger.error(f"Error getting playback history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post(
    "/resume/{user_id}/{media_id}",
    summary="Resume playback",
    description="Resume playing a media item from last position"
)
async def resume_playback(user_id: str, media_id: str):
    """
    Get the last position for resuming playback of a media item.
    """
    try:
        session_key = f"{user_id}:{media_id}"
        
        if session_key not in playback_sessions:
            return {
                "success": False,
                "message": "No previous playback session found",
                "position": 0,
            }
        
        session = playback_sessions[session_key]
        return {
            "success": True,
            "message": "Playback session found",
            "position": session.get("last_position", 0),
            "duration": session.get("duration", 0),
            "total_watch_time": session.get("total_watch_time", 0),
        }
    except Exception as e:
        logger.error(f"Error resuming playback: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post(
    "/stats/{user_id}",
    summary="Get user media stats",
    description="Get statistics about user's media consumption"
)
async def get_user_media_stats(user_id: str):
    """
    Get statistics about a user's media consumption patterns.
    """
    try:
        # Filter sessions by user_id
        user_sessions = [
            session for key, session in playback_sessions.items()
            if session["user_id"] == user_id
        ]
        
        # Calculate stats
        total_watch_time = sum(s.get("total_watch_time", 0) for s in user_sessions)
        
        # Group by content type
        by_type = {}
        for session in user_sessions:
            content_type = session.get("content_type", "UNKNOWN")
            if content_type not in by_type:
                by_type[content_type] = {
                    "count": 0,
                    "total_watch_time": 0,
                }
            by_type[content_type]["count"] += 1
            by_type[content_type]["total_watch_time"] += session.get("total_watch_time", 0)
        
        # Group by page context
        by_context = {}
        for session in user_sessions:
            for context in session.get("page_contexts", []):
                if context not in by_context:
                    by_context[context] = 0
                by_context[context] += 1
        
        return {
            "user_id": user_id,
            "total_sessions": len(user_sessions),
            "total_watch_time": total_watch_time,
            "by_content_type": by_type,
            "by_page_context": by_context,
        }
    except Exception as e:
        logger.error(f"Error getting user stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete(
    "/session/{user_id}/{media_id}",
    summary="Clear playback session",
    description="Delete playback tracking for a media item"
)
async def delete_playback_session(user_id: str, media_id: str):
    """
    Delete a playback session (e.g., when user finishes watching).
    """
    try:
        session_key = f"{user_id}:{media_id}"
        
        if session_key in playback_sessions:
            del playback_sessions[session_key]
        
        return {
            "success": True,
            "message": "Playback session deleted",
        }
    except Exception as e:
        logger.error(f"Error deleting playback session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# HEALTH CHECK
# ============================================================================

@router.get(
    "/health",
    summary="Health check",
    description="Verify media tracking service is operational"
)
async def health_check():
    """Health check endpoint for media tracking service."""
    return {
        "status": "operational",
        "service": "media_tracking",
        "active_sessions": len(playback_sessions),
    }
