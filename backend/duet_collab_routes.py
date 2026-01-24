"""
Duet & Collab Video Editor Routes
FastAPI endpoints for collaborative video editing
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, UploadFile, File
from fastapi.responses import JSONResponse, StreamingResponse
import asyncio
from typing import List, Optional
from datetime import datetime
import logging
import os
import uuid

from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel

from duet_collab_service import (
    DuetCollabService,
    CreateSessionRequest,
    JoinSessionRequest,
    UploadClipRequest,
    ApplyEffectRequest,
    AddCommentRequest,
    ExportSessionRequest,
    EffectModel,
    ClipModel,
    CommentModel,
    CollaboratorRole,
    DuetSessionStatus,
    ClipStatus,
    SessionResponse,
    ClipResponse,
    CollaboratorResponse
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/duet", tags=["duet-collab"])


# ==================== DEPENDENCY INJECTION ====================

def get_duet_service(db: AsyncIOMotorDatabase = Depends()) -> DuetCollabService:
    """Get duet service instance"""
    return DuetCollabService(db)


async def get_current_user(token: str = None) -> dict:
    """Get current user from token"""
    # This will be integrated with your auth service
    if not token:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # Decode token and return user
    return {
        "user_id": "user_123",  # From token
        "username": "john_doe",
        "avatar_url": "https://avatar.url"
    }


# ==================== SESSION ENDPOINTS ====================

@router.post("/sessions", response_model=dict)
async def create_session(
    request: CreateSessionRequest,
    current_user: dict = Depends(get_current_user),
    service: DuetCollabService = Depends(get_duet_service)
):
    """Create new duet session"""
    try:
        session = await service.create_session(
            creator_id=current_user["user_id"],
            creator_name=current_user["username"],
            request=request
        )
        
        return {
            "status": "success",
            "session_id": session.session_id,
            "title": session.title,
            "creator_name": session.creator_name,
            "created_at": session.created_at
        }
    except Exception as e:
        logger.error(f"Error creating session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}", response_model=dict)
async def get_session(
    session_id: str,
    service: DuetCollabService = Depends(get_duet_service)
):
    """Get session details"""
    try:
        session = await service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {
            "session_id": session.get("session_id"),
            "title": session.get("title"),
            "description": session.get("description"),
            "creator_name": session.get("creator_name"),
            "status": session.get("status"),
            "clip_count": len(session.get("clips", [])),
            "collaborator_count": len(session.get("collaborators", [])),
            "comments_count": len(session.get("comments", [])),
            "live_viewers": session.get("live_viewers", 0),
            "view_count": session.get("view_count", 0),
            "like_count": session.get("like_count", 0),
            "duration": session.get("duration", 0),
            "thumbnail_url": session.get("thumbnail_url"),
            "is_public": session.get("is_public", False),
            "allow_comments": session.get("allow_comments", True),
            "created_at": session.get("created_at"),
            "updated_at": session.get("updated_at")
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions", response_model=dict)
async def list_user_sessions(
    limit: int = 20,
    current_user: dict = Depends(get_current_user),
    service: DuetCollabService = Depends(get_duet_service)
):
    """List user's duet sessions"""
    try:
        sessions = await service.list_user_sessions(current_user["user_id"], limit)
        
        return {
            "status": "success",
            "count": len(sessions),
            "sessions": sessions
        }
    except Exception as e:
        logger.error(f"Error listing sessions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/sessions/{session_id}/status", response_model=dict)
async def update_session_status(
    session_id: str,
    status: str,
    current_user: dict = Depends(get_current_user),
    service: DuetCollabService = Depends(get_duet_service)
):
    """Update session status"""
    try:
        session = await service.get_session(session_id)
        if not session or session["creator_id"] != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        try:
            session_status = DuetSessionStatus(status)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
        
        await service.update_session_status(session_id, session_status)
        
        return {
            "status": "success",
            "session_id": session_id,
            "new_status": status
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/sessions/{session_id}", response_model=dict)
async def delete_session(
    session_id: str,
    current_user: dict = Depends(get_current_user),
    service: DuetCollabService = Depends(get_duet_service)
):
    """Delete session (creator only)"""
    try:
        deleted = await service.delete_session(session_id, current_user["user_id"])
        
        if not deleted:
            raise HTTPException(status_code=403, detail="Not authorized to delete")
        
        return {
            "status": "success",
            "message": "Session deleted",
            "session_id": session_id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== CLIP ENDPOINTS ====================

@router.post("/clips", response_model=dict)
async def upload_clip(
    session_id: str,
    title: str,
    duration: float,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    service: DuetCollabService = Depends(get_duet_service)
):
    """Upload clip to session"""
    try:
        # Verify session exists
        session = await service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        clip_id = str(uuid.uuid4())
        position = len(session.get("clips", []))
        
        # Save file to S3
        file_key = f"duets/{session_id}/{clip_id}/{file.filename}"
        # TODO: Upload to S3
        clip_url = f"s3://{os.getenv('AWS_S3_BUCKET')}/{file_key}"
        
        # Create clip
        clip = ClipModel(
            session_id=session_id,
            contributor_id=current_user["user_id"],
            contributor_name=current_user["username"],
            url=clip_url,
            title=title,
            duration=duration,
            status=ClipStatus.PROCESSING,
            position=position
        )
        
        await service.add_clip(clip)
        
        return {
            "status": "success",
            "clip_id": clip.clip_id,
            "title": clip.title,
            "duration": clip.duration,
            "position": position,
            "message": "Clip uploaded and processing"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading clip: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/clips/{clip_id}", response_model=dict)
async def get_clip(
    clip_id: str,
    service: DuetCollabService = Depends(get_duet_service)
):
    """Get clip details"""
    try:
        clip = await service.get_clip(clip_id)
        if not clip:
            raise HTTPException(status_code=404, detail="Clip not found")
        
        return {
            "clip_id": clip.get("clip_id"),
            "title": clip.get("title"),
            "contributor_name": clip.get("contributor_name"),
            "duration": clip.get("duration"),
            "status": clip.get("status"),
            "effect_count": len(clip.get("effects", [])),
            "position": clip.get("position"),
            "created_at": clip.get("created_at")
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting clip: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}/clips", response_model=dict)
async def list_session_clips(
    session_id: str,
    service: DuetCollabService = Depends(get_duet_service)
):
    """List all clips in session"""
    try:
        clips = await service.list_session_clips(session_id)
        
        return {
            "status": "success",
            "session_id": session_id,
            "clip_count": len(clips),
            "clips": clips
        }
    except Exception as e:
        logger.error(f"Error listing clips: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/clips/{clip_id}/effects", response_model=dict)
async def apply_effect(
    clip_id: str,
    request: ApplyEffectRequest,
    current_user: dict = Depends(get_current_user),
    service: DuetCollabService = Depends(get_duet_service)
):
    """Apply effect to clip"""
    try:
        clip = await service.get_clip(clip_id)
        if not clip:
            raise HTTPException(status_code=404, detail="Clip not found")
        
        # Verify permission
        if clip["contributor_id"] != current_user["user_id"]:
            if not await service._is_editor(clip["session_id"], current_user["user_id"]):
                raise HTTPException(status_code=403, detail="Not authorized")
        
        effect = EffectModel(
            effect_type=request.effect_type,
            intensity=request.intensity,
            duration=request.duration
        )
        
        await service.apply_effect(clip_id, effect)
        
        return {
            "status": "success",
            "clip_id": clip_id,
            "effect_id": effect.effect_id,
            "effect_type": request.effect_type.value,
            "message": "Effect applied"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error applying effect: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/clips/{clip_id}", response_model=dict)
async def delete_clip(
    clip_id: str,
    current_user: dict = Depends(get_current_user),
    service: DuetCollabService = Depends(get_duet_service)
):
    """Delete clip"""
    try:
        deleted = await service.delete_clip(clip_id, current_user["user_id"])
        
        if not deleted:
            raise HTTPException(status_code=403, detail="Not authorized to delete")
        
        return {
            "status": "success",
            "message": "Clip deleted",
            "clip_id": clip_id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting clip: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== COLLABORATOR ENDPOINTS ====================

@router.post("/sessions/{session_id}/collaborators", response_model=dict)
async def add_collaborator(
    session_id: str,
    request: JoinSessionRequest,
    current_user: dict = Depends(get_current_user),
    service: DuetCollabService = Depends(get_duet_service)
):
    """Add collaborator to session"""
    try:
        session = await service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Check if not creator and session is private
        if session["creator_id"] != current_user["user_id"] and not session.get("is_public"):
            raise HTTPException(status_code=403, detail="Session is private")
        
        # Check max collaborators
        collab_count = len(session.get("collaborators", []))
        if collab_count >= session.get("max_collaborators", 5):
            raise HTTPException(status_code=400, detail="Session is full")
        
        await service.add_collaborator(
            session_id=session_id,
            user_id=current_user["user_id"],
            username=current_user["username"],
            role=request.role
        )
        
        return {
            "status": "success",
            "message": f"Added as {request.role.value}",
            "session_id": session_id,
            "user_id": current_user["user_id"]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding collaborator: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}/collaborators", response_model=dict)
async def get_session_collaborators(
    session_id: str,
    service: DuetCollabService = Depends(get_duet_service)
):
    """Get all collaborators in session"""
    try:
        collaborators = await service.get_session_collaborators(session_id)
        
        return {
            "status": "success",
            "session_id": session_id,
            "collaborator_count": len(collaborators),
            "collaborators": collaborators
        }
    except Exception as e:
        logger.error(f"Error getting collaborators: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/sessions/{session_id}/collaborators/{user_id}/status", response_model=dict)
async def update_collaborator_status(
    session_id: str,
    user_id: str,
    status: str,
    service: DuetCollabService = Depends(get_duet_service)
):
    """Update collaborator status (real-time)"""
    try:
        valid_statuses = ["idle", "recording", "editing", "viewing"]
        if status not in valid_statuses:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
        
        await service.update_collaborator_status(session_id, user_id, status)
        
        return {
            "status": "success",
            "session_id": session_id,
            "user_id": user_id,
            "new_status": status
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating collaborator status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/sessions/{session_id}/collaborators/{user_id}", response_model=dict)
async def remove_collaborator(
    session_id: str,
    user_id: str,
    current_user: dict = Depends(get_current_user),
    service: DuetCollabService = Depends(get_duet_service)
):
    """Remove collaborator from session"""
    try:
        session = await service.get_session(session_id)
        if not session or session["creator_id"] != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        removed = await service.remove_collaborator(session_id, user_id)
        
        if not removed:
            raise HTTPException(status_code=400, detail="Cannot remove creator")
        
        return {
            "status": "success",
            "message": "Collaborator removed",
            "session_id": session_id,
            "user_id": user_id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing collaborator: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== COMMENT ENDPOINTS ====================

@router.post("/sessions/{session_id}/comments", response_model=dict)
async def add_comment(
    session_id: str,
    request: AddCommentRequest,
    current_user: dict = Depends(get_current_user),
    service: DuetCollabService = Depends(get_duet_service)
):
    """Add comment to session"""
    try:
        session = await service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        if not session.get("allow_comments"):
            raise HTTPException(status_code=400, detail="Comments disabled")
        
        comment = CommentModel(
            session_id=session_id,
            author_id=current_user["user_id"],
            author_name=current_user["username"],
            author_avatar=current_user.get("avatar_url"),
            text=request.text,
            timestamp=request.timestamp
        )
        
        await service.add_comment(comment)
        
        return {
            "status": "success",
            "comment_id": comment.comment_id,
            "author_name": comment.author_name,
            "timestamp": comment.timestamp,
            "text": comment.text
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding comment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}/comments", response_model=dict)
async def get_session_comments(
    session_id: str,
    limit: int = 100,
    service: DuetCollabService = Depends(get_duet_service)
):
    """Get all comments for session"""
    try:
        comments = await service.get_session_comments(session_id, limit)
        
        return {
            "status": "success",
            "session_id": session_id,
            "comment_count": len(comments),
            "comments": comments
        }
    except Exception as e:
        logger.error(f"Error getting comments: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/comments/{comment_id}", response_model=dict)
async def delete_comment(
    comment_id: str,
    current_user: dict = Depends(get_current_user),
    service: DuetCollabService = Depends(get_duet_service)
):
    """Delete comment"""
    try:
        deleted = await service.delete_comment(comment_id, current_user["user_id"])
        
        if not deleted:
            raise HTTPException(status_code=403, detail="Not authorized to delete")
        
        return {
            "status": "success",
            "message": "Comment deleted",
            "comment_id": comment_id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting comment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== EXPORT ENDPOINTS ====================

@router.post("/export", response_model=dict)
async def export_session(
    request: ExportSessionRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    service: DuetCollabService = Depends(get_duet_service)
):
    """Create video export job"""
    try:
        session = await service.get_session(request.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Verify permission
        if session["creator_id"] != current_user["user_id"]:
            if not await service._is_editor(request.session_id, current_user["user_id"]):
                raise HTTPException(status_code=403, detail="Not authorized")
        
        export_job = await service.create_export_job(
            request.session_id,
            current_user["user_id"],
            request
        )
        
        # TODO: Add background task for actual video export
        # background_tasks.add_task(process_export, export_job["export_id"])
        
        return {
            "status": "success",
            "export_id": export_job["export_id"],
            "session_id": export_job["session_id"],
            "format": export_job["format"],
            "quality": export_job["quality"],
            "progress": 0,
            "message": "Export job created, processing will start shortly"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating export: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export/{export_id}", response_model=dict)
async def get_export_status(
    export_id: str,
    service: DuetCollabService = Depends(get_duet_service)
):
    """Get export job status"""
    try:
        export_job = await service.get_export_job(export_id)
        if not export_job:
            raise HTTPException(status_code=404, detail="Export job not found")
        
        return {
            "export_id": export_job.get("export_id"),
            "session_id": export_job.get("session_id"),
            "status": export_job.get("status"),
            "progress": export_job.get("progress"),
            "format": export_job.get("format"),
            "quality": export_job.get("quality"),
            "video_url": export_job.get("video_url"),
            "created_at": export_job.get("created_at"),
            "updated_at": export_job.get("updated_at")
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting export status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== ENGAGEMENT ENDPOINTS ====================

@router.post("/sessions/{session_id}/view", response_model=dict)
async def increment_view(
    session_id: str,
    service: DuetCollabService = Depends(get_duet_service)
):
    """Increment session view count"""
    try:
        await service.increment_view_count(session_id)
        
        return {
            "status": "success",
            "message": "View recorded"
        }
    except Exception as e:
        logger.error(f"Error recording view: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sessions/{session_id}/like", response_model=dict)
async def toggle_like(
    session_id: str,
    current_user: dict = Depends(get_current_user),
    service: DuetCollabService = Depends(get_duet_service)
):
    """Toggle like on session"""
    try:
        await service.toggle_like(session_id, current_user["user_id"])
        
        return {
            "status": "success",
            "message": "Like toggled"
        }
    except Exception as e:
        logger.error(f"Error toggling like: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/sessions/{session_id}/viewers", response_model=dict)
async def update_live_viewers(
    session_id: str,
    count: int,
    service: DuetCollabService = Depends(get_duet_service)
):
    """Update live viewer count"""
    try:
        await service.update_live_viewers(session_id, count)
        
        return {
            "status": "success",
            "session_id": session_id,
            "live_viewers": count
        }
    except Exception as e:
        logger.error(f"Error updating viewers: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== DISCOVERY ENDPOINTS ====================

@router.get("/trending", response_model=dict)
async def get_trending_duets(
    limit: int = 20,
    service: DuetCollabService = Depends(get_duet_service)
):
    """Get trending duets"""
    try:
        duets = await service.get_trending_duets(limit)
        
        return {
            "status": "success",
            "count": len(duets),
            "duets": duets
        }
    except Exception as e:
        logger.error(f"Error getting trending: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/{user_id}/stats", response_model=dict)
async def get_user_stats(
    user_id: str,
    service: DuetCollabService = Depends(get_duet_service)
):
    """Get user's duet statistics"""
    try:
        stats = await service.get_user_stats(user_id)
        
        return {
            "status": "success",
            "user_id": user_id,
            **stats
        }
    except Exception as e:
        logger.error(f"Error getting user stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
