"""
Duet & Collab Video Editor Service
Advanced multi-user collaborative video editing with real-time synchronization
"""

import os
import uuid
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from enum import Enum
import asyncio
from dataclasses import dataclass, asdict

import boto3
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
from pydantic import BaseModel, Field, validator
import jwt


# ==================== ENUMS ====================

class DuetSessionStatus(str, Enum):
    DRAFT = "draft"
    RECORDING = "recording"
    EDITING = "editing"
    PROCESSING = "processing"
    READY = "ready"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class CollaboratorRole(str, Enum):
    CREATOR = "creator"
    EDITOR = "editor"
    VIEWER = "viewer"
    COMMENTER = "commenter"


class ClipStatus(str, Enum):
    PENDING = "pending"
    UPLOADING = "uploading"
    PROCESSING = "processing"
    READY = "ready"
    ERROR = "error"


class EffectType(str, Enum):
    BLUR = "blur"
    BRIGHTNESS = "brightness"
    CONTRAST = "contrast"
    SATURATE = "saturate"
    GRAYSCALE = "grayscale"
    SEPIA = "sepia"
    GLOW = "glow"
    GLITCH = "glitch"
    VIGNETTE = "vignette"
    SHAKE = "shake"
    ZOOM = "zoom"
    PARTICLES = "particles"


# ==================== MODELS ====================

class EffectModel(BaseModel):
    effect_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    effect_type: EffectType
    intensity: float = Field(default=1.0, ge=0.0, le=2.0)
    duration: float = Field(default=1.0, ge=0.0)
    applied_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        use_enum_values = True


class ClipModel(BaseModel):
    clip_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    contributor_id: str
    contributor_name: str
    url: str
    title: str
    duration: float  # in seconds
    status: ClipStatus = ClipStatus.PENDING
    effects: List[EffectModel] = []
    position: int  # Timeline position
    thumbnail_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        use_enum_values = True


class CollaboratorModel(BaseModel):
    user_id: str
    username: str
    avatar_url: Optional[str] = None
    role: CollaboratorRole = CollaboratorRole.EDITOR
    status: str = "idle"  # idle, recording, editing, viewing
    joined_at: datetime = Field(default_factory=datetime.utcnow)
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    is_online: bool = True

    class Config:
        use_enum_values = True


class CommentModel(BaseModel):
    comment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    author_id: str
    author_name: str
    author_avatar: Optional[str] = None
    text: str
    timestamp: float = 0.0  # Video timestamp
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_pinned: bool = False
    replies: List['CommentModel'] = []

    class Config:
        use_enum_values = True


CommentModel.update_forward_refs()


class DuetSessionModel(BaseModel):
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: Optional[str] = None
    creator_id: str
    creator_name: str
    status: DuetSessionStatus = DuetSessionStatus.DRAFT
    clips: List[ClipModel] = []
    collaborators: List[CollaboratorModel] = []
    comments: List[CommentModel] = []
    thumbnail_url: Optional[str] = None
    video_url: Optional[str] = None
    duration: float = 0.0
    view_count: int = 0
    like_count: int = 0
    share_count: int = 0
    live_viewers: int = 0
    max_collaborators: int = 5
    is_public: bool = False
    allow_comments: bool = True
    allow_duets: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    published_at: Optional[datetime] = None

    class Config:
        use_enum_values = True


# ==================== REQUEST/RESPONSE MODELS ====================

class CreateSessionRequest(BaseModel):
    title: str
    description: Optional[str] = None
    max_collaborators: int = 5
    is_public: bool = False


class JoinSessionRequest(BaseModel):
    session_id: str
    role: CollaboratorRole = CollaboratorRole.EDITOR


class UploadClipRequest(BaseModel):
    session_id: str
    title: str
    duration: float
    position: int = 0


class ApplyEffectRequest(BaseModel):
    clip_id: str
    effect_type: EffectType
    intensity: float = 1.0
    duration: float = 1.0


class AddCommentRequest(BaseModel):
    session_id: str
    text: str
    timestamp: float = 0.0
    reply_to: Optional[str] = None


class ExportSessionRequest(BaseModel):
    session_id: str
    format: str = "mp4"  # mp4, webm, mov
    quality: str = "high"  # low, medium, high, ultra
    include_intro: bool = False
    include_credits: bool = True


class SessionResponse(BaseModel):
    session_id: str
    title: str
    creator_name: str
    status: str
    clip_count: int
    collaborator_count: int
    live_viewers: int
    view_count: int
    like_count: int
    thumbnail_url: Optional[str]
    is_public: bool
    created_at: datetime

    class Config:
        use_enum_values = True


class ClipResponse(BaseModel):
    clip_id: str
    title: str
    contributor_name: str
    duration: float
    status: str
    position: int
    effect_count: int
    thumbnail_url: Optional[str]
    created_at: datetime

    class Config:
        use_enum_values = True


class CollaboratorResponse(BaseModel):
    user_id: str
    username: str
    avatar_url: Optional[str]
    role: str
    status: str
    is_online: bool
    joined_at: datetime

    class Config:
        use_enum_values = True


# ==================== DATABASE SERVICE ====================

class DuetCollabService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.sessions_collection: AsyncIOMotorCollection = db["duet_sessions"]
        self.clips_collection: AsyncIOMotorCollection = db["duet_clips"]
        self.collaborators_collection: AsyncIOMotorCollection = db["duet_collaborators"]
        self.comments_collection: AsyncIOMotorCollection = db["duet_comments"]
        self.exports_collection: AsyncIOMotorCollection = db["duet_exports"]
        
        # S3 for video storage
        self.s3_client = boto3.client('s3')
        self.bucket_name = os.getenv('AWS_S3_BUCKET', 'gaaius-duet-videos')

    async def init_indexes(self):
        """Initialize database indexes for performance"""
        # Session indexes
        await self.sessions_collection.create_index("creator_id")
        await self.sessions_collection.create_index("status")
        await self.sessions_collection.create_index("created_at")
        
        # Clip indexes
        await self.clips_collection.create_index("session_id")
        await self.clips_collection.create_index("contributor_id")
        await self.clips_collection.create_index("status")
        
        # Comment indexes
        await self.comments_collection.create_index("session_id")
        await self.comments_collection.create_index("author_id")
        
        # Collaborator indexes
        await self.collaborators_collection.create_index([("session_id", 1), ("user_id", 1)])

    # ==================== SESSION OPERATIONS ====================

    async def create_session(self, creator_id: str, creator_name: str, 
                            request: CreateSessionRequest) -> DuetSessionModel:
        """Create new duet session"""
        session = DuetSessionModel(
            creator_id=creator_id,
            creator_name=creator_name,
            title=request.title,
            description=request.description,
            max_collaborators=request.max_collaborators,
            is_public=request.is_public
        )
        
        session_dict = {
            **asdict(session),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await self.sessions_collection.insert_one(session_dict)
        
        # Add creator as collaborator
        await self.add_collaborator(
            session.session_id,
            creator_id,
            creator_name,
            CollaboratorRole.CREATOR
        )
        
        return session

    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session details"""
        session = await self.sessions_collection.find_one({"session_id": session_id})
        return session

    async def list_user_sessions(self, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """List all sessions for a user (created or collaborating)"""
        pipeline = [
            {
                "$match": {
                    "$or": [
                        {"creator_id": user_id},
                        {"collaborators.user_id": user_id}
                    ]
                }
            },
            {"$sort": {"updated_at": -1}},
            {"$limit": limit},
            {
                "$project": {
                    "session_id": 1,
                    "title": 1,
                    "description": 1,
                    "creator_name": 1,
                    "status": 1,
                    "thumbnail_url": 1,
                    "clip_count": {"$size": "$clips"},
                    "collaborator_count": {"$size": "$collaborators"},
                    "view_count": 1,
                    "created_at": 1,
                    "updated_at": 1
                }
            }
        ]
        
        sessions = await self.sessions_collection.aggregate(pipeline).to_list(limit)
        return sessions

    async def update_session_status(self, session_id: str, status: DuetSessionStatus):
        """Update session status"""
        await self.sessions_collection.update_one(
            {"session_id": session_id},
            {
                "$set": {
                    "status": status.value,
                    "updated_at": datetime.utcnow()
                }
            }
        )

    async def delete_session(self, session_id: str, user_id: str):
        """Delete session (creator only)"""
        session = await self.get_session(session_id)
        if session and session["creator_id"] == user_id:
            await self.sessions_collection.delete_one({"session_id": session_id})
            # Clean up clips
            await self.clips_collection.delete_many({"session_id": session_id})
            # Clean up comments
            await self.comments_collection.delete_many({"session_id": session_id})
            return True
        return False

    # ==================== CLIP OPERATIONS ====================

    async def add_clip(self, clip_data: ClipModel) -> ClipModel:
        """Add clip to session timeline"""
        clip_dict = {
            **asdict(clip_data),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await self.clips_collection.insert_one(clip_dict)
        
        # Update session clip list and duration
        session = await self.get_session(clip_data.session_id)
        new_duration = sum([c.get("duration", 0) for c in session.get("clips", [])]) + clip_data.duration
        
        await self.sessions_collection.update_one(
            {"session_id": clip_data.session_id},
            {
                "$push": {"clips": clip_dict},
                "$set": {
                    "duration": new_duration,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return clip_data

    async def get_clip(self, clip_id: str) -> Optional[Dict[str, Any]]:
        """Get clip details"""
        return await self.clips_collection.find_one({"clip_id": clip_id})

    async def list_session_clips(self, session_id: str) -> List[Dict[str, Any]]:
        """List all clips in a session"""
        clips = await self.clips_collection.find(
            {"session_id": session_id}
        ).sort("position", 1).to_list(100)
        return clips

    async def apply_effect(self, clip_id: str, effect: EffectModel):
        """Apply effect to clip"""
        await self.clips_collection.update_one(
            {"clip_id": clip_id},
            {
                "$push": {"effects": asdict(effect)},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )

    async def remove_effect(self, clip_id: str, effect_id: str):
        """Remove effect from clip"""
        await self.clips_collection.update_one(
            {"clip_id": clip_id},
            {
                "$pull": {"effects": {"effect_id": effect_id}},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )

    async def update_clip_status(self, clip_id: str, status: ClipStatus):
        """Update clip processing status"""
        await self.clips_collection.update_one(
            {"clip_id": clip_id},
            {
                "$set": {
                    "status": status.value,
                    "updated_at": datetime.utcnow()
                }
            }
        )

    async def delete_clip(self, clip_id: str, user_id: str) -> bool:
        """Delete clip (contributor or editor only)"""
        clip = await self.get_clip(clip_id)
        if clip and (clip["contributor_id"] == user_id or 
                    await self._is_editor(clip["session_id"], user_id)):
            await self.clips_collection.delete_one({"clip_id": clip_id})
            return True
        return False

    # ==================== COLLABORATOR OPERATIONS ====================

    async def add_collaborator(self, session_id: str, user_id: str, 
                              username: str, role: CollaboratorRole):
        """Add collaborator to session"""
        collaborator = CollaboratorModel(
            user_id=user_id,
            username=username,
            role=role
        )
        
        collab_dict = asdict(collaborator)
        
        await self.sessions_collection.update_one(
            {"session_id": session_id},
            {
                "$push": {"collaborators": collab_dict},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        await self.collaborators_collection.insert_one({
            "session_id": session_id,
            **collab_dict
        })

    async def remove_collaborator(self, session_id: str, user_id: str) -> bool:
        """Remove collaborator from session"""
        session = await self.get_session(session_id)
        if session and session["creator_id"] != user_id:  # Can't remove creator
            await self.sessions_collection.update_one(
                {"session_id": session_id},
                {"$pull": {"collaborators": {"user_id": user_id}}}
            )
            await self.collaborators_collection.delete_one({
                "session_id": session_id,
                "user_id": user_id
            })
            return True
        return False

    async def update_collaborator_status(self, session_id: str, user_id: str, status: str):
        """Update collaborator status (idle, recording, editing, viewing)"""
        await self.sessions_collection.update_one(
            {"session_id": session_id, "collaborators.user_id": user_id},
            {
                "$set": {
                    "collaborators.$.status": status,
                    "collaborators.$.last_activity": datetime.utcnow()
                }
            }
        )

    async def get_session_collaborators(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all collaborators in session"""
        session = await self.get_session(session_id)
        return session.get("collaborators", []) if session else []

    async def set_collaborator_online(self, session_id: str, user_id: str, is_online: bool):
        """Set collaborator online/offline status"""
        await self.sessions_collection.update_one(
            {"session_id": session_id, "collaborators.user_id": user_id},
            {
                "$set": {
                    "collaborators.$.is_online": is_online,
                    "collaborators.$.last_activity": datetime.utcnow()
                }
            }
        )

    # ==================== COMMENT OPERATIONS ====================

    async def add_comment(self, comment: CommentModel):
        """Add comment to session"""
        comment_dict = asdict(comment)
        
        await self.comments_collection.insert_one(comment_dict)
        
        await self.sessions_collection.update_one(
            {"session_id": comment.session_id},
            {
                "$push": {"comments": comment_dict},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )

    async def get_session_comments(self, session_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all comments for session"""
        comments = await self.comments_collection.find(
            {"session_id": session_id}
        ).sort("created_at", -1).to_list(limit)
        return comments

    async def add_comment_reply(self, comment_id: str, reply: CommentModel):
        """Add reply to comment"""
        await self.comments_collection.update_one(
            {"comment_id": comment_id},
            {"$push": {"replies": asdict(reply)}}
        )

    async def pin_comment(self, comment_id: str):
        """Pin comment (creator only)"""
        await self.comments_collection.update_one(
            {"comment_id": comment_id},
            {"$set": {"is_pinned": True}}
        )

    async def delete_comment(self, comment_id: str, user_id: str) -> bool:
        """Delete comment (author only)"""
        comment = await self.comments_collection.find_one({"comment_id": comment_id})
        if comment and comment["author_id"] == user_id:
            await self.comments_collection.delete_one({"comment_id": comment_id})
            return True
        return False

    # ==================== EXPORT OPERATIONS ====================

    async def create_export_job(self, session_id: str, user_id: str, 
                               request: ExportSessionRequest) -> Dict[str, Any]:
        """Create video export job"""
        session = await self.get_session(session_id)
        if not session:
            raise ValueError("Session not found")
        
        export_job = {
            "export_id": str(uuid.uuid4()),
            "session_id": session_id,
            "user_id": user_id,
            "format": request.format,
            "quality": request.quality,
            "status": "pending",
            "progress": 0,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await self.exports_collection.insert_one(export_job)
        return export_job

    async def get_export_job(self, export_id: str) -> Optional[Dict[str, Any]]:
        """Get export job status"""
        return await self.exports_collection.find_one({"export_id": export_id})

    async def update_export_progress(self, export_id: str, progress: int):
        """Update export progress (0-100)"""
        await self.exports_collection.update_one(
            {"export_id": export_id},
            {
                "$set": {
                    "progress": progress,
                    "updated_at": datetime.utcnow()
                }
            }
        )

    async def mark_export_complete(self, export_id: str, video_url: str):
        """Mark export as complete"""
        await self.exports_collection.update_one(
            {"export_id": export_id},
            {
                "$set": {
                    "status": "completed",
                    "video_url": video_url,
                    "updated_at": datetime.utcnow()
                }
            }
        )

    # ==================== ENGAGEMENT OPERATIONS ====================

    async def increment_view_count(self, session_id: str):
        """Increment view count"""
        await self.sessions_collection.update_one(
            {"session_id": session_id},
            {"$inc": {"view_count": 1}}
        )

    async def toggle_like(self, session_id: str, user_id: str):
        """Toggle like on session"""
        session = await self.get_session(session_id)
        if session:
            likes = session.get("likes", [])
            if user_id in likes:
                await self.sessions_collection.update_one(
                    {"session_id": session_id},
                    {"$pull": {"likes": user_id}, "$inc": {"like_count": -1}}
                )
            else:
                await self.sessions_collection.update_one(
                    {"session_id": session_id},
                    {"$push": {"likes": user_id}, "$inc": {"like_count": 1}}
                )

    async def update_live_viewers(self, session_id: str, count: int):
        """Update live viewer count"""
        await self.sessions_collection.update_one(
            {"session_id": session_id},
            {"$set": {"live_viewers": count}}
        )

    # ==================== HELPER METHODS ====================

    async def _is_editor(self, session_id: str, user_id: str) -> bool:
        """Check if user is editor or creator"""
        session = await self.get_session(session_id)
        if not session:
            return False
        
        if session["creator_id"] == user_id:
            return True
        
        for collab in session.get("collaborators", []):
            if collab["user_id"] == user_id and collab["role"] in [CollaboratorRole.CREATOR.value, 
                                                                     CollaboratorRole.EDITOR.value]:
                return True
        
        return False

    async def get_trending_duets(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get trending duets"""
        pipeline = [
            {"$match": {"status": "published", "is_public": True}},
            {
                "$addFields": {
                    "score": {
                        "$add": [
                            {"$multiply": ["$view_count", 1]},
                            {"$multiply": ["$like_count", 10]},
                            {"$multiply": ["$share_count", 50]},
                            {"$multiply": ["$live_viewers", 5]}
                        ]
                    }
                }
            },
            {"$sort": {"score": -1}},
            {"$limit": limit},
            {
                "$project": {
                    "session_id": 1,
                    "title": 1,
                    "creator_name": 1,
                    "thumbnail_url": 1,
                    "view_count": 1,
                    "like_count": 1,
                    "clip_count": {"$size": "$clips"},
                    "collaborator_count": {"$size": "$collaborators"},
                    "created_at": 1,
                    "score": 1
                }
            }
        ]
        
        return await self.sessions_collection.aggregate(pipeline).to_list(limit)

    async def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Get user's duet statistics"""
        sessions = await self.sessions_collection.find(
            {"creator_id": user_id}
        ).to_list(None)
        
        clips = await self.clips_collection.find(
            {"contributor_id": user_id}
        ).to_list(None)
        
        total_views = sum(s.get("view_count", 0) for s in sessions)
        total_likes = sum(s.get("like_count", 0) for s in sessions)
        total_collaborations = len(set(c.get("contributor_id") for s in sessions 
                                      for c in s.get("clips", [])))
        
        return {
            "duet_sessions_created": len(sessions),
            "total_clips_uploaded": len(clips),
            "total_views": total_views,
            "total_likes": total_likes,
            "total_collaborations": total_collaborations,
            "avg_views_per_duet": total_views // len(sessions) if sessions else 0
        }
