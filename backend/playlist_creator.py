"""
Playlist Creator - Curate & Share Playlists
Advanced playlist creation, management, curation, and sharing system
Integrated with music, movies, videos, and social features
"""

from typing import Dict, List, Optional, Set, Any
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
import logging
import hashlib
import uuid
from enum import Enum
import json

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS & MODELS
# ============================================================================

class ContentType(str, Enum):
    """Types of content in playlist"""
    MUSIC = "music"
    MOVIE = "movie"
    VIDEO = "video"
    PODCAST = "podcast"
    AUDIOBOOK = "audiobook"
    MUSIC_VIDEO = "music_video"


class PlaylistVisibility(str, Enum):
    """Playlist visibility settings"""
    PRIVATE = "private"
    PUBLIC = "public"
    FRIENDS_ONLY = "friends_only"
    LINK_ONLY = "link_only"


class CurationStrategy(str, Enum):
    """Playlist curation strategies"""
    MANUAL = "manual"  # User manually adds items
    AI_GENERATED = "ai_generated"  # AI creates based on preferences
    MOOD_BASED = "mood_based"  # Based on mood/vibe
    TIME_BASED = "time_based"  # Based on time of day
    GENRE_BASED = "genre_based"  # By music genre
    THEME_BASED = "theme_based"  # By theme/topic
    TRENDING = "trending"  # Trending items
    ALGORITHM = "algorithm"  # Smart algorithm


class PlaylistItem(BaseModel):
    """Item in a playlist"""
    item_id: str
    content_type: ContentType
    title: str
    description: Optional[str] = None
    creator: str
    duration_seconds: Optional[int] = None
    thumbnail_url: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    added_at: datetime = Field(default_factory=datetime.utcnow)
    order_index: int = 0


class PlaylistStats(BaseModel):
    """Playlist statistics"""
    total_items: int = 0
    total_duration_seconds: int = 0
    followers: int = 0
    plays: int = 0
    likes: int = 0
    shares: int = 0
    saves: int = 0


class PlaylistThumbnail(BaseModel):
    """Playlist cover thumbnail"""
    url: str
    auto_generated: bool = False
    custom_style: Optional[str] = None


class Playlist(BaseModel):
    """Curated playlist model"""
    playlist_id: str
    name: str
    description: str
    creator_id: str
    creator_name: str
    created_at: datetime
    updated_at: datetime
    items: List[PlaylistItem] = Field(default_factory=list)
    visibility: PlaylistVisibility = PlaylistVisibility.PRIVATE
    curation_strategy: CurationStrategy = CurationStrategy.MANUAL
    content_types: Set[ContentType] = Field(default_factory=set)
    tags: List[str] = Field(default_factory=list)
    mood: Optional[str] = None
    theme: Optional[str] = None
    language: str = "en"
    explicit_content: bool = False
    stats: PlaylistStats = Field(default_factory=PlaylistStats)
    thumbnail: Optional[PlaylistThumbnail] = None
    share_token: Optional[str] = None
    collaborative: bool = False
    collaborators: List[str] = Field(default_factory=list)
    liked_by: Set[str] = Field(default_factory=set)
    saved_by: Set[str] = Field(default_factory=set)
    followers: Set[str] = Field(default_factory=set)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class PlaylistTemplate(BaseModel):
    """Playlist template for quick creation"""
    template_id: str
    name: str
    description: str
    category: str
    icon: str
    default_content_type: ContentType
    suggested_items: int = 20
    mood: Optional[str] = None
    theme: Optional[str] = None


class PlaylistShare(BaseModel):
    """Playlist sharing record"""
    share_id: str
    playlist_id: str
    shared_by: str
    shared_with: str
    shared_at: datetime
    share_type: str = "link"  # link, direct, social
    platform: Optional[str] = None


class PlaylistCollaboration(BaseModel):
    """Playlist collaboration record"""
    collaboration_id: str
    playlist_id: str
    collaborator_id: str
    role: str = "editor"  # editor, contributor, viewer
    joined_at: datetime
    permissions: List[str] = Field(default_factory=list)


# ============================================================================
# PLAYLIST CREATOR SERVICE
# ============================================================================

class PlaylistCreator:
    """Core playlist creation and management service"""
    
    def __init__(self):
        self.playlists: Dict[str, Playlist] = {}
        self.templates: Dict[str, PlaylistTemplate] = self._init_templates()
        self.shares: Dict[str, PlaylistShare] = {}
        self.collaborations: Dict[str, PlaylistCollaboration] = {}
    
    def _init_templates(self) -> Dict[str, PlaylistTemplate]:
        """Initialize default playlist templates"""
        templates = {
            "workout": PlaylistTemplate(
                template_id="tpl-workout",
                name="Workout Mix",
                description="High-energy tracks for fitness",
                category="fitness",
                icon="💪",
                default_content_type=ContentType.MUSIC,
                mood="energetic"
            ),
            "chill": PlaylistTemplate(
                template_id="tpl-chill",
                name="Chill Vibes",
                description="Relaxing ambient and lo-fi",
                category="relaxation",
                icon="😎",
                default_content_type=ContentType.MUSIC,
                mood="relaxed"
            ),
            "study": PlaylistTemplate(
                template_id="tpl-study",
                name="Study Focus",
                description="Concentration-boosting music",
                category="productivity",
                icon="📚",
                default_content_type=ContentType.MUSIC,
                mood="focused"
            ),
            "party": PlaylistTemplate(
                template_id="tpl-party",
                name="Party Mode",
                description="Dance and celebration tracks",
                category="entertainment",
                icon="🎉",
                default_content_type=ContentType.MUSIC,
                mood="energetic"
            ),
            "movie_night": PlaylistTemplate(
                template_id="tpl-movie",
                name="Movie Night",
                description="Curated movies and trailers",
                category="entertainment",
                icon="🎬",
                default_content_type=ContentType.MOVIE
            ),
            "podcast_mix": PlaylistTemplate(
                template_id="tpl-podcast",
                name="Podcast Mix",
                description="Educational and entertaining podcasts",
                category="education",
                icon="🎙️",
                default_content_type=ContentType.PODCAST
            ),
            "road_trip": PlaylistTemplate(
                template_id="tpl-roadtrip",
                name="Road Trip",
                description="Long-drive soundtrack",
                category="travel",
                icon="🚗",
                default_content_type=ContentType.MUSIC,
                mood="adventurous"
            ),
            "sleep": PlaylistTemplate(
                template_id="tpl-sleep",
                name="Sleep Well",
                description="Calming music for better sleep",
                category="wellness",
                icon="😴",
                default_content_type=ContentType.MUSIC,
                mood="calm"
            ),
        }
        return templates
    
    async def create_playlist(
        self,
        name: str,
        creator_id: str,
        creator_name: str,
        description: str = "",
        visibility: PlaylistVisibility = PlaylistVisibility.PRIVATE,
        curation_strategy: CurationStrategy = CurationStrategy.MANUAL,
        mood: Optional[str] = None,
        theme: Optional[str] = None,
        tags: Optional[List[str]] = None,
        template_id: Optional[str] = None
    ) -> Playlist:
        """Create a new playlist"""
        playlist_id = str(uuid.uuid4())
        share_token = hashlib.sha256(
            f"{playlist_id}{creator_id}{datetime.utcnow().isoformat()}".encode()
        ).hexdigest()[:16]
        
        playlist = Playlist(
            playlist_id=playlist_id,
            name=name,
            description=description,
            creator_id=creator_id,
            creator_name=creator_name,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            visibility=visibility,
            curation_strategy=curation_strategy,
            mood=mood,
            theme=theme,
            tags=tags or [],
            share_token=share_token
        )
        
        self.playlists[playlist_id] = playlist
        logger.info(f"Created playlist '{name}' by {creator_name}")
        return playlist
    
    async def add_item_to_playlist(
        self,
        playlist_id: str,
        item_id: str,
        content_type: ContentType,
        title: str,
        creator: str,
        description: Optional[str] = None,
        duration_seconds: Optional[int] = None,
        thumbnail_url: Optional[str] = None,
        metadata: Optional[Dict] = None,
        user_id: Optional[str] = None
    ) -> bool:
        """Add item to playlist"""
        if playlist_id not in self.playlists:
            raise ValueError(f"Playlist {playlist_id} not found")
        
        playlist = self.playlists[playlist_id]
        
        # Check permissions
        if playlist.collaborative and user_id and user_id != playlist.creator_id:
            if user_id not in playlist.collaborators:
                raise PermissionError("Not authorized to add items")
        
        # Check max items (prevent bloated playlists)
        if len(playlist.items) >= 500:
            raise ValueError("Playlist full (max 500 items)")
        
        # Create item
        item = PlaylistItem(
            item_id=item_id,
            content_type=content_type,
            title=title,
            description=description,
            creator=creator,
            duration_seconds=duration_seconds,
            thumbnail_url=thumbnail_url,
            metadata=metadata or {},
            order_index=len(playlist.items)
        )
        
        playlist.items.append(item)
        playlist.content_types.add(content_type)
        
        # Update stats
        playlist.stats.total_items = len(playlist.items)
        if duration_seconds:
            playlist.stats.total_duration_seconds += duration_seconds
        
        playlist.updated_at = datetime.utcnow()
        logger.info(f"Added {title} to playlist {playlist_id}")
        return True
    
    async def remove_item_from_playlist(
        self,
        playlist_id: str,
        item_id: str,
        user_id: Optional[str] = None
    ) -> bool:
        """Remove item from playlist"""
        if playlist_id not in self.playlists:
            raise ValueError(f"Playlist {playlist_id} not found")
        
        playlist = self.playlists[playlist_id]
        
        # Check ownership
        if user_id and user_id != playlist.creator_id and user_id not in playlist.collaborators:
            raise PermissionError("Not authorized to remove items")
        
        # Find and remove item
        item_to_remove = next((item for item in playlist.items if item.item_id == item_id), None)
        if not item_to_remove:
            raise ValueError(f"Item {item_id} not in playlist")
        
        playlist.items.remove(item_to_remove)
        
        # Update stats
        playlist.stats.total_items = len(playlist.items)
        if item_to_remove.duration_seconds:
            playlist.stats.total_duration_seconds -= item_to_remove.duration_seconds
        
        # Re-order items
        for idx, item in enumerate(playlist.items):
            item.order_index = idx
        
        playlist.updated_at = datetime.utcnow()
        logger.info(f"Removed item {item_id} from playlist {playlist_id}")
        return True
    
    async def reorder_items(
        self,
        playlist_id: str,
        item_order: List[str],
        user_id: Optional[str] = None
    ) -> bool:
        """Reorder items in playlist"""
        if playlist_id not in self.playlists:
            raise ValueError(f"Playlist {playlist_id} not found")
        
        playlist = self.playlists[playlist_id]
        
        # Check ownership
        if user_id and user_id != playlist.creator_id:
            raise PermissionError("Only owner can reorder items")
        
        # Validate all items exist
        existing_ids = {item.item_id for item in playlist.items}
        if set(item_order) != existing_ids:
            raise ValueError("Invalid item order - missing or extra items")
        
        # Reorder
        item_map = {item.item_id: item for item in playlist.items}
        playlist.items = [item_map[item_id] for item_id in item_order]
        
        for idx, item in enumerate(playlist.items):
            item.order_index = idx
        
        playlist.updated_at = datetime.utcnow()
        logger.info(f"Reordered items in playlist {playlist_id}")
        return True
    
    async def update_playlist_metadata(
        self,
        playlist_id: str,
        updates: Dict[str, Any],
        user_id: Optional[str] = None
    ) -> Playlist:
        """Update playlist metadata"""
        if playlist_id not in self.playlists:
            raise ValueError(f"Playlist {playlist_id} not found")
        
        playlist = self.playlists[playlist_id]
        
        # Check ownership
        if user_id and user_id != playlist.creator_id:
            raise PermissionError("Not authorized to update playlist")
        
        # Update allowed fields
        allowed_fields = {'name', 'description', 'visibility', 'mood', 'theme', 'tags', 'explicit_content'}
        for key, value in updates.items():
            if key in allowed_fields:
                setattr(playlist, key, value)
        
        playlist.updated_at = datetime.utcnow()
        logger.info(f"Updated playlist {playlist_id}")
        return playlist
    
    async def duplicate_playlist(
        self,
        source_playlist_id: str,
        new_creator_id: str,
        new_creator_name: str,
        new_name: Optional[str] = None
    ) -> Playlist:
        """Duplicate an existing playlist"""
        if source_playlist_id not in self.playlists:
            raise ValueError(f"Playlist {source_playlist_id} not found")
        
        source = self.playlists[source_playlist_id]
        new_name = new_name or f"{source.name} (Copy)"
        
        # Create new playlist
        new_playlist = await self.create_playlist(
            name=new_name,
            creator_id=new_creator_id,
            creator_name=new_creator_name,
            description=source.description,
            visibility=source.visibility,
            curation_strategy=source.curation_strategy,
            mood=source.mood,
            theme=source.theme,
            tags=source.tags.copy()
        )
        
        # Copy items
        for item in source.items:
            await self.add_item_to_playlist(
                playlist_id=new_playlist.playlist_id,
                item_id=item.item_id,
                content_type=item.content_type,
                title=item.title,
                creator=item.creator,
                description=item.description,
                duration_seconds=item.duration_seconds,
                thumbnail_url=item.thumbnail_url,
                metadata=item.metadata.copy()
            )
        
        logger.info(f"Duplicated playlist from {source_playlist_id} to {new_playlist.playlist_id}")
        return new_playlist
    
    async def get_playlist(self, playlist_id: str) -> Optional[Playlist]:
        """Get playlist by ID"""
        return self.playlists.get(playlist_id)
    
    async def get_user_playlists(
        self,
        user_id: str,
        include_shared: bool = True,
        skip: int = 0,
        limit: int = 20
    ) -> List[Playlist]:
        """Get playlists owned by user"""
        user_playlists = [
            p for p in self.playlists.values()
            if p.creator_id == user_id
        ]
        
        if include_shared:
            # Add shared/collaborative playlists
            shared = [
                p for p in self.playlists.values()
                if user_id in p.collaborators or user_id in p.followers
            ]
            user_playlists.extend(shared)
        
        return user_playlists[skip:skip+limit]
    
    async def like_playlist(self, playlist_id: str, user_id: str) -> bool:
        """Like a playlist"""
        if playlist_id not in self.playlists:
            raise ValueError(f"Playlist {playlist_id} not found")
        
        playlist = self.playlists[playlist_id]
        if user_id not in playlist.liked_by:
            playlist.liked_by.add(user_id)
            playlist.stats.likes += 1
            logger.info(f"User {user_id} liked playlist {playlist_id}")
        
        return True
    
    async def save_playlist(self, playlist_id: str, user_id: str) -> bool:
        """Save playlist to user's library"""
        if playlist_id not in self.playlists:
            raise ValueError(f"Playlist {playlist_id} not found")
        
        playlist = self.playlists[playlist_id]
        if user_id not in playlist.saved_by:
            playlist.saved_by.add(user_id)
            playlist.stats.saves += 1
            logger.info(f"User {user_id} saved playlist {playlist_id}")
        
        return True
    
    async def follow_playlist(self, playlist_id: str, user_id: str) -> bool:
        """Follow a playlist"""
        if playlist_id not in self.playlists:
            raise ValueError(f"Playlist {playlist_id} not found")
        
        playlist = self.playlists[playlist_id]
        if user_id not in playlist.followers:
            playlist.followers.add(user_id)
            playlist.stats.followers += 1
            logger.info(f"User {user_id} followed playlist {playlist_id}")
        
        return True
    
    async def share_playlist(
        self,
        playlist_id: str,
        shared_by: str,
        shared_with: Optional[str] = None,
        share_type: str = "link",
        platform: Optional[str] = None
    ) -> PlaylistShare:
        """Share playlist"""
        if playlist_id not in self.playlists:
            raise ValueError(f"Playlist {playlist_id} not found")
        
        playlist = self.playlists[playlist_id]
        
        share_id = str(uuid.uuid4())
        share = PlaylistShare(
            share_id=share_id,
            playlist_id=playlist_id,
            shared_by=shared_by,
            shared_with=shared_with or "public",
            shared_at=datetime.utcnow(),
            share_type=share_type,
            platform=platform
        )
        
        self.shares[share_id] = share
        playlist.stats.shares += 1
        logger.info(f"Playlist {playlist_id} shared by {shared_by}")
        return share
    
    async def add_collaborator(
        self,
        playlist_id: str,
        collaborator_id: str,
        role: str = "editor",
        user_id: Optional[str] = None
    ) -> bool:
        """Add collaborator to playlist"""
        if playlist_id not in self.playlists:
            raise ValueError(f"Playlist {playlist_id} not found")
        
        playlist = self.playlists[playlist_id]
        
        # Check ownership
        if user_id and user_id != playlist.creator_id:
            raise PermissionError("Only owner can add collaborators")
        
        if collaborator_id not in playlist.collaborators:
            playlist.collaborators.append(collaborator_id)
            playlist.collaborative = True
            
            collab = PlaylistCollaboration(
                collaboration_id=str(uuid.uuid4()),
                playlist_id=playlist_id,
                collaborator_id=collaborator_id,
                role=role,
                joined_at=datetime.utcnow(),
                permissions=['view', 'add', 'remove', 'edit'] if role == 'editor' else ['view', 'add']
            )
            
            self.collaborations[collab.collaboration_id] = collab
            logger.info(f"Added collaborator {collaborator_id} to playlist {playlist_id}")
        
        return True
    
    def get_templates(self) -> Dict[str, PlaylistTemplate]:
        """Get all available templates"""
        return self.templates
    
    def get_template(self, template_id: str) -> Optional[PlaylistTemplate]:
        """Get specific template"""
        return self.templates.get(template_id)
    
    async def search_playlists(
        self,
        query: str,
        content_type: Optional[ContentType] = None,
        mood: Optional[str] = None,
        limit: int = 20
    ) -> List[Playlist]:
        """Search for playlists"""
        results = []
        
        for playlist in self.playlists.values():
            # Check visibility
            if playlist.visibility == PlaylistVisibility.PRIVATE:
                continue
            
            # Match query
            query_lower = query.lower()
            if query_lower not in playlist.name.lower() and query_lower not in playlist.description.lower():
                continue
            
            # Filter by content type
            if content_type and content_type not in playlist.content_types:
                continue
            
            # Filter by mood
            if mood and playlist.mood != mood:
                continue
            
            results.append(playlist)
        
        return results[:limit]
    
    async def get_trending_playlists(
        self,
        limit: int = 20,
        content_type: Optional[ContentType] = None
    ) -> List[Playlist]:
        """Get trending playlists by engagement"""
        playlists = list(self.playlists.values())
        
        # Filter by visibility
        playlists = [p for p in playlists if p.visibility != PlaylistVisibility.PRIVATE]
        
        # Filter by content type
        if content_type:
            playlists = [p for p in playlists if content_type in p.content_types]
        
        # Sort by engagement score
        def engagement_score(p):
            return (p.stats.plays * 0.3 + 
                    p.stats.likes * 0.25 + 
                    p.stats.followers * 0.25 + 
                    p.stats.shares * 0.2)
        
        playlists.sort(key=engagement_score, reverse=True)
        return playlists[:limit]
    
    async def get_playlist_recommendations(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[Playlist]:
        """Get personalized playlist recommendations"""
        user_playlists = await self.get_user_playlists(user_id, include_shared=False)
        
        if not user_playlists:
            # Recommend trending if no user playlists
            return await self.get_trending_playlists(limit)
        
        # Analyze user's content types and moods
        content_types = set()
        moods = set()
        
        for playlist in user_playlists:
            content_types.update(playlist.content_types)
            if playlist.mood:
                moods.add(playlist.mood)
        
        # Find similar playlists
        recommendations = []
        for playlist in self.playlists.values():
            if playlist.creator_id == user_id:
                continue
            if playlist.visibility == PlaylistVisibility.PRIVATE:
                continue
            
            # Score by similarity
            content_match = len(playlist.content_types & content_types) > 0
            mood_match = playlist.mood in moods if playlist.mood else False
            
            if content_match or mood_match:
                recommendations.append(playlist)
        
        # Sort by relevance
        recommendations.sort(key=lambda p: p.stats.followers, reverse=True)
        return recommendations[:limit]
    
    async def generate_playlist_name_suggestions(
        self,
        items: List[PlaylistItem],
        mood: Optional[str] = None,
        theme: Optional[str] = None
    ) -> List[str]:
        """Generate playlist name suggestions based on content"""
        suggestions = []
        
        # Get content info
        content_types = set(item.content_type for item in items)
        
        # Suggest based on mood
        if mood:
            mood_suggestions = {
                "energetic": ["Power Hour", "Pump It Up", "Go Time", "High Energy Mix"],
                "relaxed": ["Chill Zone", "Take It Easy", "Relaxation Station", "Calm Vibes"],
                "focused": ["Concentration Station", "Focus Mode", "Study Groove", "Workflow"],
                "adventurous": ["Adventure Awaits", "Explore", "Road Trip", "Journey"],
                "sad": ["Deep Feelings", "Emotional Depths", "Heart Songs", "Reflections"],
                "happy": ["Good Vibes", "Happiness Mix", "Smile Session", "Joy Ride"],
            }
            suggestions.extend(mood_suggestions.get(mood, []))
        
        # Suggest based on content type
        if ContentType.MUSIC in content_types:
            suggestions.extend(["My Mix", "Daily Beats", "Favorite Tracks"])
        if ContentType.MOVIE in content_types:
            suggestions.extend(["Movie Marathon", "Film Collection", "Cinema Night"])
        if ContentType.VIDEO in content_types:
            suggestions.extend(["Video Picks", "Watch Later", "Must-See Videos"])
        if ContentType.PODCAST in content_types:
            suggestions.extend(["Podcast Series", "Listen Up", "Audio Collection"])
        
        # Suggest based on first items
        if items:
            first_creator = items[0].creator
            suggestions.insert(0, f"{first_creator} Collection")
        
        # Add theme-based suggestions
        if theme:
            suggestions.insert(0, theme)
            suggestions.insert(1, f"{theme} Mix")
        
        return list(dict.fromkeys(suggestions))[:10]  # Remove duplicates, limit to 10


# ============================================================================
# INTEGRATION INTERFACES
# ============================================================================

class PlaylistIntegration:
    """Integration layer for playlist creation across all platforms"""
    
    def __init__(self, playlist_creator: PlaylistCreator):
        self.creator = playlist_creator
    
    # ---- MUSIC INTEGRATION ----
    
    async def create_music_playlist(
        self,
        user_id: str,
        user_name: str,
        playlist_name: str,
        description: str = "",
        track_ids: Optional[List[str]] = None,
        mood: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Playlist:
        """Create music playlist from track IDs"""
        playlist = await self.creator.create_playlist(
            name=playlist_name,
            creator_id=user_id,
            creator_name=user_name,
            description=description,
            mood=mood,
            tags=tags
        )
        
        if track_ids:
            for track_id in track_ids:
                # In production, fetch track metadata
                await self.creator.add_item_to_playlist(
                    playlist_id=playlist.playlist_id,
                    item_id=track_id,
                    content_type=ContentType.MUSIC,
                    title=f"Track {track_id}",  # Would fetch real title
                    creator="Unknown Artist"  # Would fetch real creator
                )
        
        return playlist
    
    # ---- MOVIE INTEGRATION ----
    
    async def create_movie_playlist(
        self,
        user_id: str,
        user_name: str,
        playlist_name: str,
        description: str = "",
        movie_ids: Optional[List[str]] = None,
        genre: Optional[str] = None
    ) -> Playlist:
        """Create movie playlist"""
        playlist = await self.creator.create_playlist(
            name=playlist_name,
            creator_id=user_id,
            creator_name=user_name,
            description=description,
            curation_strategy=CurationStrategy.THEME_BASED,
            theme=genre,
            visibility=PlaylistVisibility.PUBLIC
        )
        
        if movie_ids:
            for movie_id in movie_ids:
                await self.creator.add_item_to_playlist(
                    playlist_id=playlist.playlist_id,
                    item_id=movie_id,
                    content_type=ContentType.MOVIE,
                    title=f"Movie {movie_id}",
                    creator="Studio"
                )
        
        return playlist
    
    # ---- VIDEO INTEGRATION ----
    
    async def create_video_playlist(
        self,
        user_id: str,
        user_name: str,
        playlist_name: str,
        description: str = "",
        video_ids: Optional[List[str]] = None
    ) -> Playlist:
        """Create video playlist"""
        playlist = await self.creator.create_playlist(
            name=playlist_name,
            creator_id=user_id,
            creator_name=user_name,
            description=description,
            curation_strategy=CurationStrategy.MANUAL,
            visibility=PlaylistVisibility.PUBLIC
        )
        
        if video_ids:
            for video_id in video_ids:
                await self.creator.add_item_to_playlist(
                    playlist_id=playlist.playlist_id,
                    item_id=video_id,
                    content_type=ContentType.VIDEO,
                    title=f"Video {video_id}",
                    creator="Content Creator"
                )
        
        return playlist
    
    # ---- MUSIC VIDEO INTEGRATION ----
    
    async def create_music_video_playlist(
        self,
        user_id: str,
        user_name: str,
        playlist_name: str,
        description: str = "",
        music_video_ids: Optional[List[str]] = None,
        artist: Optional[str] = None
    ) -> Playlist:
        """Create music video playlist"""
        playlist = await self.creator.create_playlist(
            name=playlist_name,
            creator_id=user_id,
            creator_name=user_name,
            description=description,
            theme=artist or "Music Videos"
        )
        
        if music_video_ids:
            for video_id in music_video_ids:
                await self.creator.add_item_to_playlist(
                    playlist_id=playlist.playlist_id,
                    item_id=video_id,
                    content_type=ContentType.MUSIC_VIDEO,
                    title=f"Music Video {video_id}",
                    creator=artist or "Artist"
                )
        
        return playlist
    
    # ---- MIXED CONTENT PLAYLIST ----
    
    async def create_mixed_content_playlist(
        self,
        user_id: str,
        user_name: str,
        playlist_name: str,
        description: str = "",
        items: Optional[Dict[ContentType, List[str]]] = None
    ) -> Playlist:
        """Create playlist with mixed content types"""
        playlist = await self.creator.create_playlist(
            name=playlist_name,
            creator_id=user_id,
            creator_name=user_name,
            description=description,
            visibility=PlaylistVisibility.PUBLIC
        )
        
        if items:
            for content_type, content_ids in items.items():
                for content_id in content_ids:
                    await self.creator.add_item_to_playlist(
                        playlist_id=playlist.playlist_id,
                        item_id=content_id,
                        content_type=content_type,
                        title=f"{content_type.value} {content_id}",
                        creator="Creator"
                    )
        
        return playlist
