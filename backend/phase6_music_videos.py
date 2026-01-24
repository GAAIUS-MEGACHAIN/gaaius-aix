"""
Phase 6: Music Videos Integration
Music video profiles, length enforcement, and copyright protection.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel
from datetime import datetime
import logging
import hashlib

logger = logging.getLogger(__name__)


class MusicVideo(BaseModel):
    """Music video model"""
    video_id: str
    track_id: str  # Associated track
    title: str
    artist: str
    creator_id: str
    video_url: str
    thumbnail_url: str
    duration_seconds: int
    uploaded_at: datetime
    view_count: int = 0
    like_count: int = 0
    is_copyrighted: bool = False
    copyright_claim_id: Optional[str] = None


class MusicVideoProfile:
    """Creator's music video profile"""
    
    def __init__(self, creator_id: str):
        self.creator_id = creator_id
        self.music_videos: List[str] = []  # video_ids
        self.created_at = datetime.utcnow()
        self.video_count = 0
        self.total_views = 0
        self.total_likes = 0
    
    def to_dict(self) -> Dict:
        return {
            "creator_id": self.creator_id,
            "video_count": self.video_count,
            "total_views": self.total_views,
            "total_likes": self.total_likes,
            "music_videos": self.music_videos,
            "created_at": self.created_at.isoformat()
        }


class MusicVideoManager:
    """Music video management"""
    
    def __init__(self):
        self.videos: Dict[str, MusicVideo] = {}
        self.profiles: Dict[str, MusicVideoProfile] = {}
        self.MAX_VIDEO_DURATION = 600  # 10 minutes
    
    async def upload_music_video(
        self,
        track_id: str,
        title: str,
        artist: str,
        creator_id: str,
        video_url: str,
        thumbnail_url: str,
        duration_seconds: int
    ) -> MusicVideo:
        """Upload music video (only for original music, max 10 min)"""
        
        # Enforce 10-minute limit
        if duration_seconds > self.MAX_VIDEO_DURATION:
            raise ValueError(
                f"Music video exceeds 10-minute limit: {duration_seconds}s > {self.MAX_VIDEO_DURATION}s"
            )
        
        video_id = hashlib.sha256(
            f"{track_id}{creator_id}{datetime.utcnow().isoformat()}".encode()
        ).hexdigest()[:16]
        
        music_video = MusicVideo(
            video_id=video_id,
            track_id=track_id,
            title=title,
            artist=artist,
            creator_id=creator_id,
            video_url=video_url,
            thumbnail_url=thumbnail_url,
            duration_seconds=duration_seconds,
            uploaded_at=datetime.utcnow()
        )
        
        self.videos[video_id] = music_video
        
        # Add to creator's profile
        if creator_id not in self.profiles:
            self.profiles[creator_id] = MusicVideoProfile(creator_id)
        
        profile = self.profiles[creator_id]
        profile.music_videos.append(video_id)
        profile.video_count += 1
        
        logger.info(f"Uploaded music video: {title} by {artist} ({duration_seconds}s)")
        return music_video
    
    async def get_music_video(self, video_id: str) -> Optional[MusicVideo]:
        """Get music video details"""
        return self.videos.get(video_id)
    
    async def get_creator_music_videos(self, creator_id: str) -> List[MusicVideo]:
        """Get all music videos for a creator"""
        if creator_id not in self.profiles:
            return []
        
        profile = self.profiles[creator_id]
        videos = []
        for video_id in profile.music_videos:
            if video_id in self.videos:
                videos.append(self.videos[video_id])
        
        return sorted(videos, key=lambda v: v.uploaded_at, reverse=True)
    
    async def get_creator_profile(self, creator_id: str) -> Optional[Dict]:
        """Get creator's music video profile"""
        if creator_id not in self.profiles:
            return None
        
        profile = self.profiles[creator_id]
        return profile.to_dict()
    
    async def increment_view_count(self, video_id: str) -> Dict:
        """Increment view count"""
        if video_id not in self.videos:
            raise ValueError(f"Video not found: {video_id}")
        
        video = self.videos[video_id]
        video.view_count += 1
        
        # Update profile stats
        creator_id = video.creator_id
        if creator_id in self.profiles:
            self.profiles[creator_id].total_views += 1
        
        return {"video_id": video_id, "view_count": video.view_count}
    
    async def like_music_video(self, video_id: str) -> Dict:
        """Like music video"""
        if video_id not in self.videos:
            raise ValueError(f"Video not found: {video_id}")
        
        video = self.videos[video_id]
        video.like_count += 1
        
        # Update profile stats
        creator_id = video.creator_id
        if creator_id in self.profiles:
            self.profiles[creator_id].total_likes += 1
        
        return {"video_id": video_id, "like_count": video.like_count}
    
    async def mark_as_copyrighted(
        self,
        video_id: str,
        copyright_claim_id: str
    ) -> Dict:
        """Mark video as copyrighted (from copyright detection)"""
        if video_id not in self.videos:
            raise ValueError(f"Video not found: {video_id}")
        
        video = self.videos[video_id]
        video.is_copyrighted = True
        video.copyright_claim_id = copyright_claim_id
        
        logger.warning(f"Marked video as copyrighted: {video_id} (claim: {copyright_claim_id})")
        
        return {
            "video_id": video_id,
            "is_copyrighted": True,
            "copyright_claim_id": copyright_claim_id
        }
    
    async def get_non_copyrighted_videos(self, creator_id: str) -> List[MusicVideo]:
        """Get creator's non-copyrighted music videos"""
        all_videos = await self.get_creator_music_videos(creator_id)
        return [v for v in all_videos if not v.is_copyrighted]


class MusicVideoContentValidator:
    """Validate music video content before upload"""
    
    def __init__(self, copyright_detector):
        self.copyright_detector = copyright_detector
    
    async def validate_upload(
        self,
        title: str,
        creator_id: str,
        duration_seconds: int,
        audio_data: Optional[bytes] = None,
        video_data: Optional[bytes] = None
    ) -> Dict:
        """Validate music video before upload"""
        
        errors = []
        warnings = []
        
        # Check duration
        if duration_seconds > 600:
            errors.append(f"Duration exceeds 10-minute limit: {duration_seconds}s")
        
        if duration_seconds < 10:
            warnings.append("Music video is very short")
        
        # Check title
        if not title or len(title) < 3:
            errors.append("Title must be at least 3 characters")
        
        # Check for copyright via audio fingerprint
        if audio_data and self.copyright_detector:
            copyright_match = await self.copyright_detector.detect_copyright_violation(
                audio_data,
                content_type="music_video",
                title=title,
                creator_id=creator_id
            )
            
            if copyright_match:
                errors.append(
                    f"Copyright violation detected: {copyright_match.reason} "
                    f"(claimed by {copyright_match.claimed_by})"
                )
        
        # Check for copyright via video metadata
        if video_data and self.copyright_detector:
            copyright_match = await self.copyright_detector.detect_copyright_violation(
                video_data,
                content_type="music_video",
                title=title,
                creator_id=creator_id
            )
            
            if copyright_match:
                errors.append(
                    f"Copyright violation detected in video: {copyright_match.reason}"
                )
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }


class MusicVideoIntegration:
    """Music video system integration"""
    
    def __init__(self, copyright_detector=None):
        self.manager = MusicVideoManager()
        self.validator = MusicVideoContentValidator(copyright_detector)
        self.copyright_detector = copyright_detector
    
    async def upload_music_video(
        self,
        track_id: str,
        title: str,
        artist: str,
        creator_id: str,
        video_url: str,
        thumbnail_url: str,
        duration_seconds: int,
        audio_data: Optional[bytes] = None,
        video_data: Optional[bytes] = None
    ) -> Dict:
        """Upload music video with validation"""
        
        # Validate first
        validation = await self.validator.validate_upload(
            title,
            creator_id,
            duration_seconds,
            audio_data,
            video_data
        )
        
        if not validation["is_valid"]:
            return {
                "status": "rejected",
                "errors": validation["errors"],
                "warnings": validation["warnings"]
            }
        
        try:
            video = await self.manager.upload_music_video(
                track_id,
                title,
                artist,
                creator_id,
                video_url,
                thumbnail_url,
                duration_seconds
            )
            
            return {
                "status": "uploaded",
                "video_id": video.video_id,
                "warnings": validation["warnings"]
            }
        except Exception as e:
            logger.error(f"Music video upload error: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def get_creator_profile(self, creator_id: str) -> Dict:
        """Get creator's music video profile"""
        profile = await self.manager.get_creator_profile(creator_id)
        if not profile:
            return {
                "creator_id": creator_id,
                "video_count": 0,
                "total_views": 0,
                "total_likes": 0,
                "music_videos": []
            }
        return profile
    
    async def get_music_video(self, video_id: str) -> Optional[Dict]:
        """Get music video"""
        video = await self.manager.get_music_video(video_id)
        if video:
            return video.dict()
        return None
    
    async def view_music_video(self, video_id: str) -> Dict:
        """Record music video view"""
        return await self.manager.increment_view_count(video_id)
    
    async def like_music_video(self, video_id: str) -> Dict:
        """Like music video"""
        return await self.manager.like_music_video(video_id)
    
    async def _on_shutdown(self) -> None:
        """Graceful shutdown"""
        logger.info("Music Videos system shutdown")
