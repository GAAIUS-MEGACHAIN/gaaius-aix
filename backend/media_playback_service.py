"""
Media Playback Tracking and Persistence Service
Tracks media playback history and saves viewer progress
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from motor.motor_asyncio import AsyncMotorDatabase
from bson import ObjectId

# Models
class PlaybackTrackingRequest(BaseModel):
    mediaId: str
    type: str  # 'video', 'music', 'livestream', 'movie', 'podcast', 'event', 'course', 'chat'
    timestamp: datetime

class PlaybackProgressRequest(BaseModel):
    mediaId: str
    currentTime: float
    duration: float
    type: str

class PlaybackProgressResponse(BaseModel):
    success: bool
    message: str
    progress: Optional[dict] = None

class PlaybackHistoryResponse(BaseModel):
    mediaId: str
    type: str
    title: str
    lastWatched: datetime
    currentTime: float
    duration: float
    progress: float  # percentage

# Router
router = APIRouter(prefix="/api/media", tags=["media-playback"])

async def get_db() -> AsyncMotorDatabase:
    """Get database connection"""
    from motor.motor_asyncio import AsyncMotorClient
    client = AsyncMotorClient(process.env.get("MONGODB_URL", "mongodb://localhost:27017"))
    return client.gaaius

@router.post("/track-playback")
async def track_playback_start(
    request: PlaybackTrackingRequest,
    db: AsyncMotorDatabase = Depends(get_db)
):
    """
    Track when user starts playing media
    Used for analytics and recommendations
    """
    try:
        collection = db.playback_history
        
        # Create playback history entry
        playback_entry = {
            "mediaId": request.mediaId,
            "type": request.type,
            "startTime": datetime.now(),
            "lastUpdated": datetime.now(),
            "currentTime": 0,
            "duration": 0,
            "status": "playing",
        }
        
        # Insert or update
        result = await collection.update_one(
            {
                "mediaId": request.mediaId,
                "userId": request.user_id  # From auth token
            },
            {
                "$set": playback_entry
            },
            upsert=True
        )
        
        return {
            "success": True,
            "message": "Playback tracking started",
            "entryId": str(result.upserted_id) if result.upserted_id else "updated"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to track playback: {str(e)}"
        )

@router.post("/save-progress")
async def save_playback_progress(
    request: PlaybackProgressRequest,
    db: AsyncMotorDatabase = Depends(get_db)
):
    """
    Save user's playback progress
    Called periodically while media is playing
    """
    try:
        collection = db.playback_progress
        
        # Calculate progress percentage
        progress = (request.currentTime / request.duration * 100) if request.duration > 0 else 0
        
        # Save progress
        result = await collection.update_one(
            {
                "mediaId": request.mediaId,
                "userId": request.user_id  # From auth token
            },
            {
                "$set": {
                    "currentTime": request.currentTime,
                    "duration": request.duration,
                    "progress": progress,
                    "type": request.type,
                    "lastUpdated": datetime.now(),
                    "completed": progress >= 90,  # Mark as completed if >90% watched
                }
            },
            upsert=True
        )
        
        return PlaybackProgressResponse(
            success=True,
            message="Progress saved successfully",
            progress={
                "currentTime": request.currentTime,
                "duration": request.duration,
                "progress": progress,
                "completed": progress >= 90
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save progress: {str(e)}"
        )

@router.get("/playback-history")
async def get_playback_history(
    skip: int = 0,
    limit: int = 20,
    db: AsyncMotorDatabase = Depends(get_db)
):
    """
    Get user's playback history
    """
    try:
        collection = db.playback_history
        
        # Fetch user's history
        history = await collection.find(
            {"userId": request.user_id}  # From auth token
        ).sort("lastUpdated", -1).skip(skip).limit(limit).to_list(limit)
        
        return {
            "success": True,
            "count": len(history),
            "history": [
                PlaybackHistoryResponse(
                    mediaId=item.get("mediaId"),
                    type=item.get("type"),
                    title=item.get("title", "Unknown"),
                    lastWatched=item.get("lastUpdated"),
                    currentTime=item.get("currentTime", 0),
                    duration=item.get("duration", 0),
                    progress=item.get("progress", 0),
                ).dict() for item in history
            ]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch history: {str(e)}"
        )

@router.get("/resume/{media_id}")
async def get_resume_point(
    media_id: str,
    db: AsyncMotorDatabase = Depends(get_db)
):
    """
    Get resume point for a specific media
    Returns saved progress to resume playback
    """
    try:
        collection = db.playback_progress
        
        # Find saved progress
        progress = await collection.find_one({
            "mediaId": media_id,
            "userId": request.user_id  # From auth token
        })
        
        if not progress:
            return {
                "success": False,
                "message": "No saved progress found",
                "canResume": False
            }
        
        # Only offer resume if less than 90% watched and not too old (< 30 days)
        current_time = datetime.now()
        days_since = (current_time - progress.get("lastUpdated", current_time)).days
        
        can_resume = (
            progress.get("progress", 0) < 90 and 
            days_since < 30
        )
        
        return {
            "success": True,
            "canResume": can_resume,
            "resumePoint": {
                "currentTime": progress.get("currentTime", 0),
                "duration": progress.get("duration", 0),
                "progress": progress.get("progress", 0),
                "lastWatched": progress.get("lastUpdated"),
            } if can_resume else None
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch resume point: {str(e)}"
        )

@router.delete("/clear-history/{media_id}")
async def clear_playback_history(
    media_id: str,
    db: AsyncMotorDatabase = Depends(get_db)
):
    """
    Clear playback history for a specific media
    """
    try:
        collection = db.playback_progress
        
        result = await collection.delete_one({
            "mediaId": media_id,
            "userId": request.user_id  # From auth token
        })
        
        return {
            "success": True,
            "message": f"Deleted {result.deleted_count} history record(s)"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear history: {str(e)}"
        )

@router.get("/watch-stats")
async def get_watch_stats(
    db: AsyncMotorDatabase = Depends(get_db)
):
    """
    Get user's watch statistics
    """
    try:
        collection = db.playback_history
        
        # Aggregate stats
        stats = await collection.aggregate([
            {
                "$match": {"userId": request.user_id}  # From auth token
            },
            {
                "$group": {
                    "_id": "$type",
                    "count": {"$sum": 1},
                    "totalWatchTime": {"$sum": "$currentTime"}
                }
            }
        ]).to_list(None)
        
        # Format response
        total_watch_time = sum(s.get("totalWatchTime", 0) for s in stats)
        
        return {
            "success": True,
            "totalWatchTime": total_watch_time,
            "totalItems": sum(s.get("count", 0) for s in stats),
            "byType": [
                {
                    "type": s.get("_id"),
                    "count": s.get("count"),
                    "totalTime": s.get("totalWatchTime")
                } for s in stats
            ]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get stats: {str(e)}"
        )
