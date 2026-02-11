"""
Artwork Generation API Routes
Provides endpoints for generating AI artwork for distributions
"""

import logging
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, List
from backend.artwork_generation_service import (
    get_artwork_manager,
    ArtworkPrompt,
    ArtworkType,
    AIModel,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/artwork", tags=["artwork"])


# Request/Response Models

class ArtworkPromptRequest(BaseModel):
    """Request to generate artwork"""
    text: str = Field(..., min_length=10, max_length=500)
    style: str = Field(default="professional", max_length=100)
    mood: str = Field(default="energetic", max_length=100)
    artist_reference: Optional[str] = Field(default=None, max_length=200)
    color_palette: Optional[str] = Field(default=None, max_length=200)
    negative_prompt: Optional[str] = Field(default=None, max_length=500)


class GenerateMusicCoverRequest(BaseModel):
    """Request to generate music cover art"""
    user_id: str = Field(..., min_length=1)
    song_title: str = Field(..., min_length=1, max_length=200)
    artist_name: str = Field(..., min_length=1, max_length=200)
    genre: str = Field(default="electronic", max_length=100)
    mood: str = Field(default="energetic", max_length=100)
    style: str = Field(default="professional", max_length=100)


class GenerateVideoThumbnailRequest(BaseModel):
    """Request to generate video thumbnail"""
    user_id: str = Field(..., min_length=1)
    video_title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=10, max_length=500)
    style: str = Field(default="cinematic", max_length=100)


class GenerateMoviePosterRequest(BaseModel):
    """Request to generate movie poster"""
    user_id: str = Field(..., min_length=1)
    movie_title: str = Field(..., min_length=1, max_length=200)
    genre: str = Field(..., min_length=1, max_length=100)
    mood: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=10, max_length=500)


class ArtworkResponse(BaseModel):
    """Generated artwork response"""
    id: str
    url: str
    prompt: str
    model: str
    artwork_type: str
    created_at: str
    width: int
    height: int
    seed: Optional[int] = None
    metadata: Optional[dict] = None


class ArtworkSelectionRequest(BaseModel):
    """Select artwork for an upload"""
    user_id: str = Field(..., min_length=1)
    upload_id: str = Field(..., min_length=1)
    artwork_id: str = Field(..., min_length=1)


# Endpoints

@router.post("/music-cover", response_model=List[ArtworkResponse])
async def generate_music_cover(request: GenerateMusicCoverRequest):
    """
    Generate music cover artwork
    
    Returns 3 different cover art options
    """
    try:
        manager = get_artwork_manager()
        
        artworks = await manager.generate_for_upload(
            user_id=request.user_id,
            upload_title=request.song_title,
            upload_type="music",
            description=f"{request.artist_name} - {request.song_title}",
            genre=request.genre,
            artist_name=request.artist_name,
        )
        
        return [
            ArtworkResponse(
                id=art.id,
                url=art.url,
                prompt=art.prompt,
                model=art.model,
                artwork_type=art.artwork_type,
                created_at=art.created_at,
                width=art.width,
                height=art.height,
                seed=art.seed,
                metadata=art.metadata,
            )
            for art in artworks
        ]
    
    except Exception as e:
        logger.error(f"Error generating music cover: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate artwork: {str(e)}")


@router.post("/video-thumbnail", response_model=List[ArtworkResponse])
async def generate_video_thumbnail(request: GenerateVideoThumbnailRequest):
    """
    Generate video thumbnail
    
    Returns 3 different thumbnail options
    """
    try:
        manager = get_artwork_manager()
        
        artworks = await manager.generate_for_upload(
            user_id=request.user_id,
            upload_title=request.video_title,
            upload_type="video",
            description=request.description,
        )
        
        return [
            ArtworkResponse(
                id=art.id,
                url=art.url,
                prompt=art.prompt,
                model=art.model,
                artwork_type=art.artwork_type,
                created_at=art.created_at,
                width=art.width,
                height=art.height,
                seed=art.seed,
                metadata=art.metadata,
            )
            for art in artworks
        ]
    
    except Exception as e:
        logger.error(f"Error generating video thumbnail: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate artwork: {str(e)}")


@router.post("/movie-poster", response_model=List[ArtworkResponse])
async def generate_movie_poster(request: GenerateMoviePosterRequest):
    """
    Generate movie poster
    
    Returns 3 different poster options
    """
    try:
        manager = get_artwork_manager()
        
        artworks = await manager.generate_for_upload(
            user_id=request.user_id,
            upload_title=request.movie_title,
            upload_type="movie",
            description=request.description,
            genre=request.genre,
        )
        
        return [
            ArtworkResponse(
                id=art.id,
                url=art.url,
                prompt=art.prompt,
                model=art.model,
                artwork_type=art.artwork_type,
                created_at=art.created_at,
                width=art.width,
                height=art.height,
                seed=art.seed,
                metadata=art.metadata,
            )
            for art in artworks
        ]
    
    except Exception as e:
        logger.error(f"Error generating movie poster: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate artwork: {str(e)}")


@router.get("/artwork/{artwork_id}", response_model=ArtworkResponse)
async def get_artwork(artwork_id: str):
    """
    Get artwork by ID
    """
    try:
        manager = get_artwork_manager()
        artwork = manager.get_artwork(artwork_id)
        
        if not artwork:
            raise HTTPException(status_code=404, detail="Artwork not found")
        
        return ArtworkResponse(
            id=artwork.id,
            url=artwork.url,
            prompt=artwork.prompt,
            model=artwork.model,
            artwork_type=artwork.artwork_type,
            created_at=artwork.created_at,
            width=artwork.width,
            height=artwork.height,
            seed=artwork.seed,
            metadata=artwork.metadata,
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving artwork: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve artwork")


@router.get("/history/{user_id}", response_model=List[ArtworkResponse])
async def get_user_artwork_history(user_id: str):
    """
    Get all artwork generated by a user
    """
    try:
        manager = get_artwork_manager()
        artworks = manager.get_user_artwork_history(user_id)
        
        return [
            ArtworkResponse(
                id=art.id,
                url=art.url,
                prompt=art.prompt,
                model=art.model,
                artwork_type=art.artwork_type,
                created_at=art.created_at,
                width=art.width,
                height=art.height,
                seed=art.seed,
                metadata=art.metadata,
            )
            for art in artworks
        ]
    
    except Exception as e:
        logger.error(f"Error retrieving user artwork history: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve history")


@router.post("/select")
async def select_artwork(request: ArtworkSelectionRequest):
    """
    Save user's artwork selection for an upload
    """
    try:
        manager = get_artwork_manager()
        
        success = manager.save_artwork_selection(
            user_id=request.user_id,
            upload_id=request.upload_id,
            artwork_id=request.artwork_id,
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Artwork not found")
        
        return {
            "status": "success",
            "message": "Artwork selected successfully",
            "user_id": request.user_id,
            "upload_id": request.upload_id,
            "artwork_id": request.artwork_id,
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error selecting artwork: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to select artwork")


@router.delete("/artwork/{artwork_id}")
async def delete_artwork(artwork_id: str):
    """
    Delete artwork
    """
    try:
        manager = get_artwork_manager()
        
        if not manager.delete_artwork(artwork_id):
            raise HTTPException(status_code=404, detail="Artwork not found")
        
        return {
            "status": "success",
            "message": "Artwork deleted successfully",
            "artwork_id": artwork_id,
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting artwork: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete artwork")


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "artwork-generation",
        "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
    }
