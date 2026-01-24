"""
Phase 7: Advanced Music Platform Features
Artist profiles, offline support, queue management, radio stations
Production-grade implementations
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
import hashlib
import random

# Configure logging
logger = logging.getLogger(__name__)


class RadioGenre(str, Enum):
    """Radio station genres"""
    POP = "pop"
    HIP_HOP = "hip_hop"
    ROCK = "rock"
    EDM = "edm"
    JAZZ = "jazz"
    CLASSICAL = "classical"
    R_AND_B = "r_and_b"
    COUNTRY = "country"
    INDIE = "indie"
    METAL = "metal"


@dataclass
class ArtistProfile:
    """Artist profile information"""
    artist_id: str
    name: str
    bio: str = ""
    profile_image: str = ""
    monthly_listeners: int = 0
    total_streams: int = 0
    follower_count: int = 0
    verified: bool = False
    genres: List[str] = field(default_factory=list)
    top_tracks: List[str] = field(default_factory=list)
    related_artists: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PlaybackQueue:
    """Music playback queue"""
    queue_id: str
    user_id: str
    tracks: List[str] = field(default_factory=list)  # track IDs
    current_index: int = 0
    shuffle: bool = False
    repeat_mode: str = "off"  # off, one, all
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class OfflineTrack:
    """Offline downloaded track"""
    track_id: str
    user_id: str
    audio_data: bytes = b""
    metadata: Dict = field(default_factory=dict)
    downloaded_at: datetime = field(default_factory=datetime.utcnow)
    storage_size: int = 0
    expiry_date: Optional[datetime] = None  # DRM expiry (license-based)


@dataclass
class RadioStation:
    """Dynamic radio station"""
    station_id: str
    name: str
    genre: RadioGenre
    seed_tracks: List[str] = field(default_factory=list)
    seed_artists: List[str] = field(default_factory=list)
    current_playlist: List[str] = field(default_factory=list)
    listeners: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Lyrics:
    """Song lyrics with timestamps"""
    track_id: str
    content: str
    synced_lyrics: List[Dict] = field(default_factory=list)  # [{time: ms, lyric: "..."}]
    language: str = "en"
    provider: str = "genius"
    explicit: bool = False
    fetched_at: datetime = field(default_factory=datetime.utcnow)


class ArtistManager:
    """Manage artist profiles and relationships"""

    def __init__(self):
        self.artists: Dict[str, ArtistProfile] = {}
        self.user_follows: Dict[str, Set[str]] = {}  # user_id -> artist_ids
        self.artist_followers: Dict[str, Set[str]] = {}  # artist_id -> user_ids

    async def create_artist_profile(
        self,
        artist_id: str,
        name: str,
        bio: str = "",
        genres: List[str] = None
    ) -> ArtistProfile:
        """Create artist profile"""
        artist = ArtistProfile(
            artist_id=artist_id,
            name=name,
            bio=bio,
            genres=genres or []
        )
        self.artists[artist_id] = artist
        self.artist_followers[artist_id] = set()
        logger.info(f"Artist profile created: {name}")
        return artist

    async def get_artist_profile(self, artist_id: str) -> Optional[ArtistProfile]:
        """Get artist profile"""
        return self.artists.get(artist_id)

    async def update_artist_stats(
        self,
        artist_id: str,
        monthly_listeners: int = None,
        total_streams: int = None
    ) -> Optional[ArtistProfile]:
        """Update artist statistics"""
        if artist_id not in self.artists:
            return None
        
        artist = self.artists[artist_id]
        if monthly_listeners is not None:
            artist.monthly_listeners = monthly_listeners
        if total_streams is not None:
            artist.total_streams = total_streams
        
        return artist

    async def follow_artist(self, user_id: str, artist_id: str) -> bool:
        """User follows artist"""
        if artist_id not in self.artists:
            return False
        
        if user_id not in self.user_follows:
            self.user_follows[user_id] = set()
        
        self.user_follows[user_id].add(artist_id)
        self.artist_followers[artist_id].add(user_id)
        self.artists[artist_id].follower_count += 1
        
        logger.info(f"User {user_id} followed artist {artist_id}")
        return True

    async def unfollow_artist(self, user_id: str, artist_id: str) -> bool:
        """User unfollows artist"""
        if user_id not in self.user_follows or artist_id not in self.user_follows[user_id]:
            return False
        
        self.user_follows[user_id].discard(artist_id)
        self.artist_followers[artist_id].discard(user_id)
        self.artists[artist_id].follower_count = max(0, self.artists[artist_id].follower_count - 1)
        
        logger.info(f"User {user_id} unfollowed artist {artist_id}")
        return True

    async def get_followed_artists(self, user_id: str) -> List[ArtistProfile]:
        """Get all followed artists"""
        if user_id not in self.user_follows:
            return []
        
        artist_ids = self.user_follows[user_id]
        return [self.artists[aid] for aid in artist_ids if aid in self.artists]

    async def get_related_artists(self, artist_id: str, limit: int = 10) -> List[ArtistProfile]:
        """Get related artists by genre"""
        if artist_id not in self.artists:
            return []
        
        source_artist = self.artists[artist_id]
        related = []
        
        for aid, artist in self.artists.items():
            if aid == artist_id:
                continue
            
            # Genre overlap
            genre_overlap = len(set(source_artist.genres) & set(artist.genres))
            if genre_overlap > 0:
                related.append((artist, genre_overlap))
        
        # Sort by genre overlap, then by followers
        related.sort(key=lambda x: (x[1], x[0].follower_count), reverse=True)
        return [artist for artist, _ in related[:limit]]


class QueueManager:
    """Manage playback queues with shuffle and repeat"""

    def __init__(self):
        self.queues: Dict[str, PlaybackQueue] = {}
        self.shuffle_history: Dict[str, List[int]] = {}  # queue_id -> indices

    async def create_queue(self, user_id: str, tracks: List[str]) -> PlaybackQueue:
        """Create new playback queue"""
        queue_id = hashlib.md5(
            f"{user_id}{datetime.utcnow().isoformat()}".encode()
        ).hexdigest()
        
        queue = PlaybackQueue(
            queue_id=queue_id,
            user_id=user_id,
            tracks=tracks
        )
        self.queues[queue_id] = queue
        self.shuffle_history[queue_id] = list(range(len(tracks)))
        
        logger.info(f"Queue created: {queue_id} with {len(tracks)} tracks")
        return queue

    async def get_queue(self, queue_id: str) -> Optional[PlaybackQueue]:
        """Get queue"""
        return self.queues.get(queue_id)

    async def toggle_shuffle(self, queue_id: str) -> Optional[PlaybackQueue]:
        """Toggle shuffle mode"""
        if queue_id not in self.queues:
            return None
        
        queue = self.queues[queue_id]
        queue.shuffle = not queue.shuffle
        
        if queue.shuffle:
            # Create shuffled order
            indices = list(range(len(queue.tracks)))
            random.shuffle(indices)
            self.shuffle_history[queue_id] = indices
        else:
            # Return to original order
            self.shuffle_history[queue_id] = list(range(len(queue.tracks)))
        
        logger.info(f"Shuffle {'enabled' if queue.shuffle else 'disabled'} for queue {queue_id}")
        return queue

    async def set_repeat_mode(self, queue_id: str, mode: str) -> Optional[PlaybackQueue]:
        """Set repeat mode: off, one, all"""
        if queue_id not in self.queues:
            return None
        
        if mode not in ["off", "one", "all"]:
            return None
        
        queue = self.queues[queue_id]
        queue.repeat_mode = mode
        
        logger.info(f"Repeat mode set to '{mode}' for queue {queue_id}")
        return queue

    async def next_track(self, queue_id: str) -> Optional[str]:
        """Get next track in queue"""
        if queue_id not in self.queues:
            return None
        
        queue = self.queues[queue_id]
        
        if not queue.tracks:
            return None
        
        if queue.repeat_mode == "one":
            return queue.tracks[queue.current_index]
        
        # Calculate next index
        if queue.shuffle:
            indices = self.shuffle_history[queue_id]
            current_pos = indices.index(queue.current_index)
            next_pos = (current_pos + 1) % len(indices)
            queue.current_index = indices[next_pos]
        else:
            queue.current_index = (queue.current_index + 1) % len(queue.tracks)
        
        # Handle end of queue
        if queue.current_index == 0 and queue.repeat_mode == "off":
            return None
        
        return queue.tracks[queue.current_index]

    async def previous_track(self, queue_id: str) -> Optional[str]:
        """Get previous track in queue"""
        if queue_id not in self.queues:
            return None
        
        queue = self.queues[queue_id]
        
        if not queue.tracks:
            return None
        
        # Calculate previous index
        if queue.shuffle:
            indices = self.shuffle_history[queue_id]
            current_pos = indices.index(queue.current_index)
            prev_pos = (current_pos - 1) % len(indices)
            queue.current_index = indices[prev_pos]
        else:
            queue.current_index = (queue.current_index - 1) % len(queue.tracks)
        
        return queue.tracks[queue.current_index]

    async def add_to_queue(self, queue_id: str, track_id: str) -> Optional[PlaybackQueue]:
        """Add track to end of queue"""
        if queue_id not in self.queues:
            return None
        
        queue = self.queues[queue_id]
        queue.tracks.append(track_id)
        
        # Update shuffle history
        self.shuffle_history[queue_id].append(len(queue.tracks) - 1)
        
        logger.info(f"Track {track_id} added to queue {queue_id}")
        return queue

    async def remove_from_queue(self, queue_id: str, index: int) -> Optional[PlaybackQueue]:
        """Remove track at index from queue"""
        if queue_id not in self.queues or index >= len(self.queues[queue_id].tracks):
            return None
        
        queue = self.queues[queue_id]
        queue.tracks.pop(index)
        
        # Update shuffle history
        self.shuffle_history[queue_id] = list(range(len(queue.tracks)))
        
        logger.info(f"Track at index {index} removed from queue {queue_id}")
        return queue


class OfflineDownloadManager:
    """Manage offline downloads with storage limits"""

    def __init__(self, max_storage_gb: int = 5):
        self.offline_tracks: Dict[str, OfflineTrack] = {}
        self.user_downloads: Dict[str, Set[str]] = {}  # user_id -> track_ids
        self.storage_usage: Dict[str, int] = {}  # user_id -> bytes used
        self.max_storage = max_storage_gb * 1024 * 1024 * 1024

    async def download_track(
        self,
        user_id: str,
        track_id: str,
        audio_data: bytes,
        metadata: Dict,
        license_hours: int = 30 * 24  # 30 days
    ) -> Dict:
        """Download track for offline playback"""
        storage_needed = len(audio_data)
        current_usage = self.storage_usage.get(user_id, 0)
        
        # Check storage limit
        if current_usage + storage_needed > self.max_storage:
            return {
                "success": False,
                "error": "Storage limit exceeded",
                "available": self.max_storage - current_usage,
                "needed": storage_needed
            }
        
        download_id = f"{user_id}_{track_id}_{datetime.utcnow().timestamp()}"
        
        offline_track = OfflineTrack(
            track_id=track_id,
            user_id=user_id,
            audio_data=audio_data,
            metadata=metadata,
            storage_size=storage_needed,
            expiry_date=datetime.utcnow() + timedelta(hours=license_hours)
        )
        
        self.offline_tracks[download_id] = offline_track
        
        if user_id not in self.user_downloads:
            self.user_downloads[user_id] = set()
        
        self.user_downloads[user_id].add(track_id)
        self.storage_usage[user_id] = current_usage + storage_needed
        
        logger.info(f"Track {track_id} downloaded for offline use by {user_id}")
        
        return {
            "success": True,
            "download_id": download_id,
            "storage_used": storage_needed,
            "total_usage": self.storage_usage[user_id],
            "expiry_date": offline_track.expiry_date.isoformat()
        }

    async def get_offline_tracks(self, user_id: str) -> List[Dict]:
        """Get all offline downloads for user"""
        if user_id not in self.user_downloads:
            return []
        
        tracks = []
        for download_id, offline_track in self.offline_tracks.items():
            if offline_track.user_id == user_id:
                # Check if expired
                if offline_track.expiry_date and datetime.utcnow() > offline_track.expiry_date:
                    # Clean up expired
                    del self.offline_tracks[download_id]
                    self.user_downloads[user_id].discard(offline_track.track_id)
                    continue
                
                tracks.append({
                    "track_id": offline_track.track_id,
                    "metadata": offline_track.metadata,
                    "downloaded_at": offline_track.downloaded_at.isoformat(),
                    "expiry_date": offline_track.expiry_date.isoformat() if offline_track.expiry_date else None,
                    "storage_size": offline_track.storage_size
                })
        
        return tracks

    async def delete_offline_track(self, user_id: str, track_id: str) -> bool:
        """Delete offline download"""
        # Find and remove
        found_download_id = None
        for download_id, offline_track in self.offline_tracks.items():
            if offline_track.user_id == user_id and offline_track.track_id == track_id:
                found_download_id = download_id
                break
        
        if not found_download_id:
            return False
        
        offline_track = self.offline_tracks.pop(found_download_id)
        self.storage_usage[user_id] -= offline_track.storage_size
        self.user_downloads[user_id].discard(track_id)
        
        logger.info(f"Offline track {track_id} deleted for user {user_id}")
        return True

    async def get_storage_info(self, user_id: str) -> Dict:
        """Get storage usage info"""
        used = self.storage_usage.get(user_id, 0)
        return {
            "used_bytes": used,
            "used_gb": used / (1024 ** 3),
            "max_bytes": self.max_storage,
            "max_gb": self.max_storage / (1024 ** 3),
            "available_bytes": self.max_storage - used,
            "available_gb": (self.max_storage - used) / (1024 ** 3),
            "track_count": len(self.user_downloads.get(user_id, set()))
        }


class RadioStationManager:
    """Manage dynamic radio stations"""

    def __init__(self):
        self.stations: Dict[str, RadioStation] = {}
        self.user_stations: Dict[str, Set[str]] = {}  # user_id -> station_ids

    async def create_station(
        self,
        name: str,
        genre: RadioGenre,
        seed_tracks: List[str] = None,
        seed_artists: List[str] = None
    ) -> RadioStation:
        """Create radio station"""
        station_id = hashlib.md5(
            f"{name}{genre}{datetime.utcnow().isoformat()}".encode()
        ).hexdigest()
        
        station = RadioStation(
            station_id=station_id,
            name=name,
            genre=genre,
            seed_tracks=seed_tracks or [],
            seed_artists=seed_artists or []
        )
        
        self.stations[station_id] = station
        logger.info(f"Radio station created: {name} ({genre.value})")
        
        return station

    async def generate_station_playlist(
        self,
        station_id: str,
        available_tracks: Dict[str, Dict],
        limit: int = 50
    ) -> Optional[RadioStation]:
        """Generate playlist for radio station"""
        if station_id not in self.stations:
            return None
        
        station = self.stations[station_id]
        
        # Filter tracks by genre
        genre_tracks = [
            track_id for track_id, track_data in available_tracks.items()
            if track_data.get("genre") == station.genre.value
        ]
        
        # Add seed tracks first
        playlist = station.seed_tracks[:limit]
        
        # Fill rest from genre
        remaining = limit - len(playlist)
        playlist.extend(random.sample(genre_tracks, min(remaining, len(genre_tracks))))
        
        station.current_playlist = playlist
        
        logger.info(f"Playlist generated for station {station_id}: {len(playlist)} tracks")
        return station

    async def follow_station(self, user_id: str, station_id: str) -> bool:
        """User follows radio station"""
        if station_id not in self.stations:
            return False
        
        if user_id not in self.user_stations:
            self.user_stations[user_id] = set()
        
        self.user_stations[user_id].add(station_id)
        self.stations[station_id].listeners += 1
        
        logger.info(f"User {user_id} followed station {station_id}")
        return True

    async def get_user_stations(self, user_id: str) -> List[RadioStation]:
        """Get user's followed stations"""
        if user_id not in self.user_stations:
            return []
        
        return [self.stations[sid] for sid in self.user_stations[user_id] if sid in self.stations]


class LyricsManager:
    """Manage song lyrics with sync support"""

    def __init__(self):
        self.lyrics_cache: Dict[str, Lyrics] = {}

    async def add_lyrics(
        self,
        track_id: str,
        content: str,
        synced_lyrics: List[Dict] = None,
        language: str = "en"
    ) -> Lyrics:
        """Add lyrics for track"""
        lyrics = Lyrics(
            track_id=track_id,
            content=content,
            synced_lyrics=synced_lyrics or [],
            language=language
        )
        
        self.lyrics_cache[track_id] = lyrics
        logger.info(f"Lyrics added for track {track_id}")
        
        return lyrics

    async def get_lyrics(self, track_id: str) -> Optional[Lyrics]:
        """Get lyrics for track"""
        return self.lyrics_cache.get(track_id)

    async def search_lyrics(self, query: str) -> List[Lyrics]:
        """Search lyrics by content"""
        results = []
        query_lower = query.lower()
        
        for lyrics in self.lyrics_cache.values():
            if query_lower in lyrics.content.lower():
                results.append(lyrics)
        
        return results[:20]  # Limit results


class Phase7Integration:
    """Master orchestrator for Phase 7 features"""

    def __init__(self, max_offline_storage_gb: int = 5):
        self.artist_manager = ArtistManager()
        self.queue_manager = QueueManager()
        self.offline_manager = OfflineDownloadManager(max_offline_storage_gb)
        self.radio_manager = RadioStationManager()
        self.lyrics_manager = LyricsManager()

    async def health_check(self) -> Dict:
        """System health check"""
        return {
            "status": "healthy",
            "artists": len(self.artist_manager.artists),
            "queues": len(self.queue_manager.queues),
            "radio_stations": len(self.radio_manager.stations),
            "cached_lyrics": len(self.lyrics_manager.lyrics_cache),
            "phase": 7
        }
