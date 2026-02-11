"""
AI Artwork Generation Service using Pollinations AI (100% FREE)
Generates professional artwork for music covers, video thumbnails, and movie posters
Powered by Pollinations.ai - No API key needed, completely free!
"""

import os
import logging
import asyncio
import json
from enum import Enum
from dataclasses import dataclass, asdict
from typing import Optional, Dict, List
from datetime import datetime
import aiohttp
import uuid

logger = logging.getLogger(__name__)

# Pollinations API endpoint (free, no auth required)
POLLINATIONS_API = "https://image.pollinations.ai/prompt/"


class ArtworkType(str, Enum):
    """Types of artwork that can be generated"""
    MUSIC_COVER = "music_cover"           # Album/single cover art (1024x1024)
    MUSIC_BANNER = "music_banner"         # Social media banner (1920x1080)
    VIDEO_THUMBNAIL = "video_thumbnail"   # YouTube thumbnail (1280x720)
    MOVIE_POSTER = "movie_poster"         # Movie poster (1456x2160)
    PROMOTIONAL = "promotional"            # General promo art (1920x1080)
    ARTIST_PORTRAIT = "artist_portrait"   # Artist profile image (1024x1024)
    PLAYLIST_COVER = "playlist_cover"     # Playlist artwork (1024x1024)


class AIModel(str, Enum):
    """Available AI models (all free on Pollinations!)"""
    TURBO = "turbo"              # Fastest generation
    STANDARD = "standard"        # Balanced quality/speed
    QUALITY = "quality"          # Best quality


@dataclass
class ArtworkPrompt:
    """Prompt configuration for artwork generation"""
    text: str                               # Main description
    style: str = "professional"             # Art style
    mood: str = "vibrant"                   # Mood/atmosphere
    artist_reference: Optional[str] = None  # Reference artists/styles
    color_palette: Optional[str] = None     # Color preferences
    negative_prompt: str = "low quality, blurry, distorted"  # What NOT to include


@dataclass
class GeneratedArtwork:
    """Generated artwork metadata"""
    id: str
    url: str                        # CDN URL to image
    prompt: str                     # Original prompt
    model: str                      # Model used
    artwork_type: str               # Type of artwork
    created_at: str                 # ISO timestamp
    seed: Optional[int] = None      # Reproducibility seed
    width: int = 1024
    height: int = 1024
    metadata: Optional[Dict] = None # Additional info


class ArtworkGenerator:
    """
    Generates AI artwork using Pollinations API (completely FREE!)
    No API key needed - just send a prompt and get an image!
    """
    
    def __init__(self):
        """Initialize artwork generator (no API token needed!)"""
        self.api_base = POLLINATIONS_API
        self.model = AIModel.QUALITY
        
        # Artwork type templates/configurations
        self.templates = {
            ArtworkType.MUSIC_COVER: {
                "width": 1024,
                "height": 1024,
                "style_prompt": "album cover art, professional music artwork, high quality",
            },
            ArtworkType.MUSIC_BANNER: {
                "width": 1920,
                "height": 1080,
                "style_prompt": "music banner, social media header, professional, vibrant",
            },
            ArtworkType.VIDEO_THUMBNAIL: {
                "width": 1280,
                "height": 720,
                "style_prompt": "video thumbnail, eye-catching, high contrast, engaging",
            },
            ArtworkType.MOVIE_POSTER: {
                "width": 1456,
                "height": 2160,
                "style_prompt": "movie poster, cinematic, dramatic lighting, professional",
            },
            ArtworkType.PROMOTIONAL: {
                "width": 1920,
                "height": 1080,
                "style_prompt": "promotional art, professional, eye-catching, high quality",
            },
            ArtworkType.ARTIST_PORTRAIT: {
                "width": 1024,
                "height": 1024,
                "style_prompt": "professional portrait, studio lighting, high quality",
            },
            ArtworkType.PLAYLIST_COVER: {
                "width": 1024,
                "height": 1024,
                "style_prompt": "playlist cover art, cohesive design, professional",
            },
        }
    
    async def generate_artwork(
        self,
        prompt: ArtworkPrompt,
        artwork_type: ArtworkType = ArtworkType.MUSIC_COVER,
        num_outputs: int = 1,
        seed: Optional[int] = None,
    ) -> List[GeneratedArtwork]:
        """
        Generate artwork using Pollinations AI
        
        Args:
            prompt: Artwork prompt with description
            artwork_type: Type of artwork
            num_outputs: Number of images to generate (1-4)
            seed: Random seed for reproducibility
        
        Returns:
            List of generated artwork metadata
        """
        num_outputs = max(1, min(4, num_outputs))
        
        try:
            template = self.templates.get(artwork_type, self.templates[ArtworkType.MUSIC_COVER])
            
            # Build complete prompt
            complete_prompt = self._build_prompt(prompt, template)
            
            logger.info(f"Generating {num_outputs} artwork(s) of type {artwork_type.value}")
            logger.debug(f"Prompt: {complete_prompt[:100]}...")
            
            results = []
            
            async with aiohttp.ClientSession() as session:
                for i in range(num_outputs):
                    artwork = await self._generate_single_image(
                        session,
                        complete_prompt,
                        artwork_type,
                        template,
                        seed + i if seed else None,
                    )
                    
                    if artwork:
                        results.append(artwork)
                    
                    # Small delay between requests
                    if i < num_outputs - 1:
                        await asyncio.sleep(0.5)
            
            logger.info(f"Successfully generated {len(results)} artwork(s)")
            return results
        
        except Exception as e:
            logger.error(f"Error generating artwork: {str(e)}")
            raise
    
    async def _generate_single_image(
        self,
        session: aiohttp.ClientSession,
        prompt: str,
        artwork_type: ArtworkType,
        config: Dict,
        seed: Optional[int] = None,
    ) -> Optional[GeneratedArtwork]:
        """Generate single image from Pollinations"""
        try:
            # Build Pollinations URL with prompt
            # Format: https://image.pollinations.ai/prompt/{prompt}
            url = f"{self.api_base}{prompt.replace(' ', '%20')}"
            
            # Add parameters
            params = {
                "width": config["width"],
                "height": config["height"],
                "nologo": "true",  # Remove watermark
            }
            
            if seed:
                params["seed"] = str(seed)
            
            # Generate with timeout
            async with session.get(
                url,
                params=params,
                timeout=aiohttp.ClientTimeout(total=60),
                allow_redirects=True,
            ) as resp:
                if resp.status == 200:
                    # Pollinations returns image directly
                    image_url = str(resp.url)
                    
                    artwork = GeneratedArtwork(
                        id=f"{artwork_type.value}-{int(datetime.utcnow().timestamp())}-{uuid.uuid4().hex[:8]}",
                        url=image_url,
                        prompt=prompt,
                        model=self.model.value,
                        artwork_type=artwork_type.value,
                        created_at=datetime.utcnow().isoformat() + "Z",
                        seed=seed,
                        width=config["width"],
                        height=config["height"],
                        metadata={
                            "style": config["style_prompt"],
                            "model": self.model.value,
                        }
                    )
                    
                    logger.info(f"Generated artwork: {artwork.id}")
                    return artwork
                else:
                    logger.warning(f"Failed to generate image: {resp.status}")
                    return None
        
        except Exception as e:
            logger.error(f"Error in _generate_single_image: {e}")
            return None
    
    def _build_prompt(self, prompt: ArtworkPrompt, template: Dict) -> str:
        """Build complete prompt from components"""
        parts = [
            template["style_prompt"],
            prompt.text,
            f"style: {prompt.style}",
            f"mood: {prompt.mood}",
        ]
        
        if prompt.artist_reference:
            parts.append(f"inspired by {prompt.artist_reference}")
        
        if prompt.color_palette:
            parts.append(f"color palette: {prompt.color_palette}")
        
        # Add negative prompt
        parts.append(f"avoid: {prompt.negative_prompt}")
        
        complete_prompt = ", ".join(parts)
        
        # Truncate to reasonable length for URL
        return complete_prompt[:1000]
    
    async def generate_music_cover(
        self,
        song_title: str,
        artist_name: str,
        genre: str,
        mood: str = "vibrant",
        style: str = "professional",
    ) -> List[GeneratedArtwork]:
        """Generate album/single cover art"""
        prompt = ArtworkPrompt(
            text=f"Album cover for '{song_title}' by {artist_name}, {genre} music",
            style=style,
            mood=mood,
            color_palette=f"colors that match {genre} vibe",
        )
        return await self.generate_artwork(
            prompt,
            artwork_type=ArtworkType.MUSIC_COVER,
            num_outputs=3,
        )
    
    async def generate_video_thumbnail(
        self,
        video_title: str,
        description: str,
        style: str = "cinematic",
    ) -> List[GeneratedArtwork]:
        """Generate eye-catching video thumbnail"""
        prompt = ArtworkPrompt(
            text=f"Thumbnail for video: '{video_title}'. {description}",
            style=style,
            mood="engaging",
        )
        return await self.generate_artwork(
            prompt,
            artwork_type=ArtworkType.VIDEO_THUMBNAIL,
            num_outputs=3,
        )
    
    async def generate_movie_poster(
        self,
        movie_title: str,
        genre: str,
        mood: str,
        description: str,
    ) -> List[GeneratedArtwork]:
        """Generate movie poster"""
        prompt = ArtworkPrompt(
            text=f"Movie poster for '{movie_title}' ({genre}). {description}",
            style="cinematic",
            mood=mood,
        )
        return await self.generate_artwork(
            prompt,
            artwork_type=ArtworkType.MOVIE_POSTER,
            num_outputs=3,
        )
    
    async def generate_artist_portrait(
        self,
        artist_name: str,
        genre: str,
        style: str = "professional",
    ) -> List[GeneratedArtwork]:
        """Generate artist profile image"""
        prompt = ArtworkPrompt(
            text=f"Professional portrait of artist: {artist_name}, {genre} genre",
            style=style,
            mood="professional",
        )
        return await self.generate_artwork(
            prompt,
            artwork_type=ArtworkType.ARTIST_PORTRAIT,
            num_outputs=2,
        )



class ArtworkManager:
    """
    Manages artwork generation and storage
    """
    
    def __init__(self, generator: Optional[ArtworkGenerator] = None):
        """Initialize artwork manager"""
        self.generator = generator or ArtworkGenerator()
        self.generated_artworks: Dict[str, GeneratedArtwork] = {}
        self.user_artwork_history: Dict[str, List[str]] = {}
        logger.info("ArtworkManager initialized with Pollinations AI")
    
    async def generate_for_upload(
        self,
        user_id: str,
        upload_title: str,
        upload_type: str,  # "music", "video", "movie"
        description: str,
        genre: Optional[str] = None,
        artist_name: Optional[str] = None,
    ) -> List[GeneratedArtwork]:
        """
        Generate artwork for a user's upload
        
        Args:
            user_id: User uploading content
            upload_title: Title of the content
            upload_type: Type of upload (music/video/movie)
            description: Description of content
            genre: Genre (for music/movies)
            artist_name: Artist name
        
        Returns:
            List of generated artwork options
        """
        try:
            artworks = []
            
            if upload_type.lower() == "music":
                artworks = await self.generator.generate_music_cover(
                    song_title=upload_title,
                    artist_name=artist_name or f"User {user_id}",
                    genre=genre or "electronic",
                    mood="vibrant",
                )
            elif upload_type.lower() == "video":
                artworks = await self.generator.generate_video_thumbnail(
                    video_title=upload_title,
                    description=description,
                )
            elif upload_type.lower() == "movie":
                artworks = await self.generator.generate_movie_poster(
                    movie_title=upload_title,
                    genre=genre or "drama",
                    mood="dramatic",
                    description=description,
                )
            else:
                raise ValueError(f"Unsupported upload type: {upload_type}")
            
            # Store artwork
            for artwork in artworks:
                self.generated_artworks[artwork.id] = artwork
            
            # Track user's artwork
            if user_id not in self.user_artwork_history:
                self.user_artwork_history[user_id] = []
            self.user_artwork_history[user_id].extend([art.id for art in artworks])
            
            logger.info(f"Generated {len(artworks)} artwork(s) for user {user_id}")
            return artworks
        
        except Exception as e:
            logger.error(f"Error generating artwork for upload: {str(e)}")
            raise
    
    def get_artwork(self, artwork_id: str) -> Optional[GeneratedArtwork]:
        """Retrieve artwork by ID"""
        return self.generated_artworks.get(artwork_id)
    
    def get_user_artwork_history(self, user_id: str) -> List[GeneratedArtwork]:
        """Get all artwork generated by a user"""
        artwork_ids = self.user_artwork_history.get(user_id, [])
        return [
            self.generated_artworks[aid]
            for aid in artwork_ids
            if aid in self.generated_artworks
        ]
    
    def save_artwork_selection(
        self,
        user_id: str,
        upload_id: str,
        artwork_id: str,
    ) -> bool:
        """Save user's artwork selection for an upload"""
        artwork = self.get_artwork(artwork_id)
        if not artwork:
            return False
        
        # Store association (ready for database integration)
        logger.info(f"User {user_id} selected artwork {artwork_id} for upload {upload_id}")
        return True
    
    def delete_artwork(self, artwork_id: str) -> bool:
        """Delete artwork"""
        if artwork_id in self.generated_artworks:
            del self.generated_artworks[artwork_id]
            logger.info(f"Deleted artwork: {artwork_id}")
            return True
        return False


# Singleton instance
_artwork_manager: Optional[ArtworkManager] = None


async def init_artwork_service() -> ArtworkManager:
    """Initialize artwork generation service"""
    global _artwork_manager
    _artwork_manager = ArtworkManager()
    logger.info("Artwork generation service initialized")
    return _artwork_manager


def get_artwork_manager() -> ArtworkManager:
    """Get artwork manager instance"""
    global _artwork_manager
    if _artwork_manager is None:
        _artwork_manager = ArtworkManager()
    return _artwork_manager
