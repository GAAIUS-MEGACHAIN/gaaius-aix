"""
Phase 6: Music Platform Core (Spotify Clone)
Music streaming, playlists, library management, and music recommendations.
"""

import asyncio
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
import logging
import hashlib

logger = logging.getLogger(__name__)


class Track(BaseModel):
    """Music track model"""
    track_id: str
    title: str
    artist: str
    album: str
    duration_seconds: int
    genre: str
    file_url: str
    uploaded_by: str  # creator_id
    uploaded_at: datetime
    play_count: int = 0
    like_count: int = 0
    is_original: bool = True


class Playlist(BaseModel):
    """Playlist model"""
    playlist_id: str
    name: str
    created_by: str  # user_id
    description: str = ""
    tracks: List[str] = []  # track_ids
    is_public: bool = True
    created_at: datetime
    updated_at: datetime
    cover_url: Optional[str] = None


class MusicLibrary(BaseModel):
    """User music library"""
    library_id: str
    user_id: str
    liked_tracks: List[str] = []  # track_ids
    playlists: List[str] = []  # playlist_ids
    recent_plays: List[str] = []  # track_ids (ordered)
    saved_artists: List[str] = []  # artist_ids
    updated_at: datetime


class MusicRecommendation(BaseModel):
    """Music recommendation"""
    track_id: str
    reason: str
    score: float  # 0-1 confidence


class MusicStreamer:
    """Music streaming and playback management"""
    
    def __init__(self):
        self.tracks: Dict[str, Track] = {}
        self.active_streams: Dict[str, Dict] = {}  # user_id -> stream info
        self.playback_queue: Dict[str, List[str]] = {}  # user_id -> queue
    
    async def upload_track(
        self,
        title: str,
        artist: str,
        album: str,
        duration_seconds: int,
        genre: str,
        creator_id: str,
        file_url: str
    ) -> Track:
        """Upload new music track"""
        if duration_seconds > 600:  # 10 minute limit
            raise ValueError(f"Track duration exceeds 10 minute limit: {duration_seconds}s")
        
        track_id = hashlib.sha256(
            f"{title}{artist}{creator_id}{datetime.utcnow().isoformat()}".encode()
        ).hexdigest()[:16]
        
        track = Track(
            track_id=track_id,
            title=title,
            artist=artist,
            album=album,
            duration_seconds=duration_seconds,
            genre=genre,
            file_url=file_url,
            uploaded_by=creator_id,
            uploaded_at=datetime.utcnow(),
            is_original=True
        )
        
        self.tracks[track_id] = track
        logger.info(f"Uploaded track: {title} by {artist} ({duration_seconds}s)")
        return track
    
    async def start_playback(
        self,
        user_id: str,
        track_id: str
    ) -> Dict:
        """Start playing a track"""
        if track_id not in self.tracks:
            raise ValueError(f"Track not found: {track_id}")
        
        track = self.tracks[track_id]
        
        self.active_streams[user_id] = {
            "track_id": track_id,
            "start_time": datetime.utcnow(),
            "pause_time": None,
            "elapsed_seconds": 0
        }
        
        logger.info(f"Started playback: {track.title} for user {user_id}")
        return {
            "status": "playing",
            "track_id": track_id,
            "duration_seconds": track.duration_seconds
        }
    
    async def pause_playback(self, user_id: str) -> Dict:
        """Pause playback"""
        if user_id not in self.active_streams:
            raise ValueError(f"No active stream for user: {user_id}")
        
        stream = self.active_streams[user_id]
        stream["pause_time"] = datetime.utcnow()
        stream["elapsed_seconds"] = (
            stream["pause_time"] - stream["start_time"]
        ).total_seconds() + stream.get("elapsed_seconds", 0)
        
        return {"status": "paused", "elapsed": stream["elapsed_seconds"]}
    
    async def resume_playback(self, user_id: str) -> Dict:
        """Resume playback"""
        if user_id not in self.active_streams:
            raise ValueError(f"No stream to resume for user: {user_id}")
        
        stream = self.active_streams[user_id]
        stream["start_time"] = datetime.utcnow()
        stream["pause_time"] = None
        
        return {"status": "resumed", "track_id": stream["track_id"]}
    
    async def stop_playback(self, user_id: str) -> Dict:
        """Stop playback and record listen"""
        if user_id not in self.active_streams:
            return {"status": "not_playing"}
        
        stream = self.active_streams[user_id]
        track_id = stream["track_id"]
        
        # Update play count
        if track_id in self.tracks:
            self.tracks[track_id].play_count += 1
        
        del self.active_streams[user_id]
        logger.info(f"Stopped playback for user {user_id}")
        
        return {"status": "stopped", "track_id": track_id}
    
    async def get_track(self, track_id: str) -> Optional[Track]:
        """Get track details"""
        return self.tracks.get(track_id)
    
    async def search_tracks(
        self,
        query: str,
        limit: int = 20,
        offset: int = 0
    ) -> List[Track]:
        """Search for tracks by title, artist, or album"""
        query_lower = query.lower()
        results = []
        
        for track in self.tracks.values():
            if (query_lower in track.title.lower() or
                query_lower in track.artist.lower() or
                query_lower in track.album.lower()):
                results.append(track)
        
        # Sort by relevance and popularity
        results.sort(key=lambda t: (
            t.title.lower().startswith(query_lower),
            t.play_count
        ), reverse=True)
        
        return results[offset:offset + limit]
    
    async def get_trending_tracks(self, limit: int = 50) -> List[Track]:
        """Get trending music tracks"""
        tracks_sorted = sorted(
            self.tracks.values(),
            key=lambda t: t.play_count,
            reverse=True
        )
        return tracks_sorted[:limit]


class PlaylistManager:
    """Playlist management"""
    
    def __init__(self):
        self.playlists: Dict[str, Playlist] = {}
    
    async def create_playlist(
        self,
        user_id: str,
        name: str,
        description: str = "",
        is_public: bool = True
    ) -> Playlist:
        """Create new playlist"""
        playlist_id = hashlib.sha256(
            f"{user_id}{name}{datetime.utcnow().isoformat()}".encode()
        ).hexdigest()[:16]
        
        playlist = Playlist(
            playlist_id=playlist_id,
            name=name,
            created_by=user_id,
            description=description,
            is_public=is_public,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        self.playlists[playlist_id] = playlist
        logger.info(f"Created playlist: {name} by user {user_id}")
        return playlist
    
    async def add_track_to_playlist(
        self,
        playlist_id: str,
        track_id: str,
        user_id: str
    ) -> Dict:
        """Add track to playlist"""
        if playlist_id not in self.playlists:
            raise ValueError(f"Playlist not found: {playlist_id}")
        
        playlist = self.playlists[playlist_id]
        
        if playlist.created_by != user_id:
            raise ValueError("Only playlist creator can add tracks")
        
        if track_id not in playlist.tracks:
            playlist.tracks.append(track_id)
            playlist.updated_at = datetime.utcnow()
            logger.info(f"Added track {track_id} to playlist {playlist_id}")
        
        return {"status": "added", "playlist_id": playlist_id, "track_count": len(playlist.tracks)}
    
    async def remove_track_from_playlist(
        self,
        playlist_id: str,
        track_id: str,
        user_id: str
    ) -> Dict:
        """Remove track from playlist"""
        if playlist_id not in self.playlists:
            raise ValueError(f"Playlist not found: {playlist_id}")
        
        playlist = self.playlists[playlist_id]
        
        if playlist.created_by != user_id:
            raise ValueError("Only playlist creator can remove tracks")
        
        if track_id in playlist.tracks:
            playlist.tracks.remove(track_id)
            playlist.updated_at = datetime.utcnow()
        
        return {"status": "removed", "playlist_id": playlist_id, "track_count": len(playlist.tracks)}
    
    async def get_playlist(self, playlist_id: str) -> Optional[Playlist]:
        """Get playlist details"""
        return self.playlists.get(playlist_id)
    
    async def get_user_playlists(self, user_id: str) -> List[Playlist]:
        """Get all playlists created by user"""
        return [p for p in self.playlists.values() if p.created_by == user_id]


class MusicLibraryManager:
    """User music library management"""
    
    def __init__(self):
        self.libraries: Dict[str, MusicLibrary] = {}
    
    async def get_or_create_library(self, user_id: str) -> MusicLibrary:
        """Get or create user's music library"""
        if user_id not in self.libraries:
            library = MusicLibrary(
                library_id=hashlib.sha256(user_id.encode()).hexdigest()[:16],
                user_id=user_id,
                updated_at=datetime.utcnow()
            )
            self.libraries[user_id] = library
        
        return self.libraries[user_id]
    
    async def like_track(self, user_id: str, track_id: str) -> Dict:
        """Like a track"""
        library = await self.get_or_create_library(user_id)
        
        if track_id not in library.liked_tracks:
            library.liked_tracks.append(track_id)
            library.updated_at = datetime.utcnow()
        
        return {"status": "liked", "liked_count": len(library.liked_tracks)}
    
    async def unlike_track(self, user_id: str, track_id: str) -> Dict:
        """Unlike a track"""
        library = await self.get_or_create_library(user_id)
        
        if track_id in library.liked_tracks:
            library.liked_tracks.remove(track_id)
            library.updated_at = datetime.utcnow()
        
        return {"status": "unliked", "liked_count": len(library.liked_tracks)}
    
    async def add_to_recent_plays(self, user_id: str, track_id: str) -> None:
        """Add track to recent plays"""
        library = await self.get_or_create_library(user_id)
        
        # Remove if already in list, then add to front
        if track_id in library.recent_plays:
            library.recent_plays.remove(track_id)
        
        library.recent_plays.insert(0, track_id)
        
        # Keep only last 100 plays
        library.recent_plays = library.recent_plays[:100]
        library.updated_at = datetime.utcnow()
    
    async def get_recent_plays(self, user_id: str, limit: int = 50) -> List[str]:
        """Get user's recent plays"""
        library = await self.get_or_create_library(user_id)
        return library.recent_plays[:limit]
    
    async def get_liked_tracks(self, user_id: str) -> List[str]:
        """Get user's liked tracks"""
        library = await self.get_or_create_library(user_id)
        return library.liked_tracks


class MusicRecommendationEngine:
    """Music recommendation engine"""
    
    def __init__(self, music_streamer: MusicStreamer, library_manager: MusicLibraryManager):
        self.streamer = music_streamer
        self.library_manager = library_manager
    
    async def get_recommendations_for_user(
        self,
        user_id: str,
        limit: int = 20
    ) -> List[MusicRecommendation]:
        """Get personalized music recommendations"""
        library = await self.library_manager.get_or_create_library(user_id)
        recommendations = []
        
        # Strategy 1: Recommend based on liked tracks
        for track_id in library.liked_tracks[-10:]:  # Last 10 liked
            if track_id in self.streamer.tracks:
                track = self.streamer.tracks[track_id]
                similar = await self._find_similar_tracks(track)
                for similar_track, score in similar[:3]:
                    if similar_track.track_id not in library.liked_tracks:
                        recommendations.append(MusicRecommendation(
                            track_id=similar_track.track_id,
                            reason=f"Similar to {track.title}",
                            score=score
                        ))
        
        # Strategy 2: Recommend trending tracks
        trending = await self.streamer.get_trending_tracks(50)
        for track in trending[:5]:
            if track.track_id not in library.liked_tracks:
                recommendations.append(MusicRecommendation(
                    track_id=track.track_id,
                    reason="Trending now",
                    score=0.85
                ))
        
        # Deduplicate and sort by score
        seen = set()
        unique_recs = []
        for rec in sorted(recommendations, key=lambda r: r.score, reverse=True):
            if rec.track_id not in seen:
                unique_recs.append(rec)
                seen.add(rec.track_id)
        
        return unique_recs[:limit]
    
    async def _find_similar_tracks(
        self,
        track: Track,
        limit: int = 5
    ) -> List[tuple]:
        """Find similar tracks (by genre, artist)"""
        similar = []
        
        for other_track in self.streamer.tracks.values():
            if other_track.track_id == track.track_id:
                continue
            
            similarity = 0.0
            
            # Same genre = +0.5
            if other_track.genre == track.genre:
                similarity += 0.5
            
            # Same artist = +0.3
            if other_track.artist == track.artist:
                similarity += 0.3
            
            # Same album = +0.2
            if other_track.album == track.album:
                similarity += 0.2
            
            if similarity > 0:
                similar.append((other_track, similarity))
        
        return sorted(similar, key=lambda x: x[1], reverse=True)[:limit]


class Phase6MusicIntegration:
    """Master orchestrator for Phase 6 music system"""
    
    def __init__(self):
        self.streamer = MusicStreamer()
        self.playlist_manager = PlaylistManager()
        self.library_manager = MusicLibraryManager()
        self.recommendation_engine = MusicRecommendationEngine(
            self.streamer,
            self.library_manager
        )
    
    async def setup_music(self, app, db) -> None:
        """Initialize music system"""
        logger.info("Music Platform initialized")
    
    async def upload_music(
        self,
        title: str,
        artist: str,
        album: str,
        duration_seconds: int,
        genre: str,
        creator_id: str,
        file_url: str
    ) -> Track:
        """Upload music track"""
        return await self.streamer.upload_track(
            title, artist, album, duration_seconds, genre, creator_id, file_url
        )
    
    async def play_track(self, user_id: str, track_id: str) -> Dict:
        """Start playing track"""
        result = await self.streamer.start_playback(user_id, track_id)
        if track_id in self.streamer.tracks:
            await self.library_manager.add_to_recent_plays(user_id, track_id)
        return result
    
    async def search_music(self, query: str, limit: int = 20) -> List[Track]:
        """Search music"""
        return await self.streamer.search_tracks(query, limit)
    
    async def get_trending_music(self, limit: int = 50) -> List[Track]:
        """Get trending music"""
        return await self.streamer.get_trending_tracks(limit)
    
    async def get_recommendations(self, user_id: str, limit: int = 20) -> List[MusicRecommendation]:
        """Get music recommendations"""
        return await self.recommendation_engine.get_recommendations_for_user(user_id, limit)
    
    async def like_track(self, user_id: str, track_id: str) -> Dict:
        """Like track"""
        return await self.library_manager.like_track(user_id, track_id)
    
    async def create_playlist(self, user_id: str, name: str, description: str = "") -> Playlist:
        """Create playlist"""
        return await self.playlist_manager.create_playlist(user_id, name, description)
    
    async def add_to_playlist(self, playlist_id: str, track_id: str, user_id: str) -> Dict:
        """Add track to playlist"""
        return await self.playlist_manager.add_track_to_playlist(playlist_id, track_id, user_id)
    
    async def _on_shutdown(self) -> None:
        """Graceful shutdown"""
        logger.info("Music Platform shutdown")
