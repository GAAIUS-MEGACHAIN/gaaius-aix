"""
Playlist Creator API Routes
RESTful API endpoints for playlist creation, management, and sharing
Integrated with music, movies, videos, and social platforms
"""

from fastapi import APIRouter, HTTPException, Query, Body, Depends
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import logging
from .playlist_creator import (
    PlaylistCreator, PlaylistIntegration, Playlist, PlaylistItem,
    ContentType, PlaylistVisibility, CurationStrategy
)

logger = logging.getLogger(__name__)

# Initialize services
playlist_service = PlaylistCreator()
playlist_integration = PlaylistIntegration(playlist_service)

# Create routers
router_playlist = APIRouter(prefix="/api/playlists", tags=["Playlists"])
router_create = APIRouter(prefix="/api/playlists/create", tags=["Playlist Creation"])
router_share = APIRouter(prefix="/api/playlists/share", tags=["Playlist Sharing"])


# ============================================================================
# BASIC PLAYLIST CRUD
# ============================================================================

@router_playlist.post("")
async def create_playlist(
    name: str = Query(...),
    user_id: str = Query(...),
    user_name: str = Query(...),
    description: str = Query(""),
    visibility: str = Query("private"),
    mood: Optional[str] = Query(None),
    tags: Optional[List[str]] = Query(None)
):
    """Create new playlist"""
    try:
        playlist = await playlist_service.create_playlist(
            name=name,
            creator_id=user_id,
            creator_name=user_name,
            description=description,
            visibility=PlaylistVisibility(visibility),
            mood=mood,
            tags=tags or []
        )
        
        return {
            "status": "created",
            "playlist_id": playlist.playlist_id,
            "name": playlist.name,
            "share_token": playlist.share_token,
            "created_at": playlist.created_at.isoformat()
        }
    except Exception as e:
        logger.error(f"Playlist creation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router_playlist.get("/{playlist_id}")
async def get_playlist(playlist_id: str):
    """Get playlist details"""
    try:
        playlist = await playlist_service.get_playlist(playlist_id)
        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist not found")
        
        return {
            "playlist_id": playlist.playlist_id,
            "name": playlist.name,
            "description": playlist.description,
            "creator_id": playlist.creator_id,
            "creator_name": playlist.creator_name,
            "created_at": playlist.created_at.isoformat(),
            "updated_at": playlist.updated_at.isoformat(),
            "item_count": len(playlist.items),
            "visibility": playlist.visibility.value,
            "mood": playlist.mood,
            "theme": playlist.theme,
            "tags": playlist.tags,
            "stats": {
                "plays": playlist.stats.plays,
                "likes": playlist.stats.likes,
                "shares": playlist.stats.shares,
                "saves": playlist.stats.saves,
                "followers": playlist.stats.followers,
                "total_items": playlist.stats.total_items,
                "total_duration_seconds": playlist.stats.total_duration_seconds
            }
        }
    except Exception as e:
        logger.error(f"Get playlist error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router_playlist.get("")
async def get_user_playlists(
    user_id: str = Query(...),
    skip: int = Query(0),
    limit: int = Query(20)
):
    """Get user's playlists"""
    try:
        playlists = await playlist_service.get_user_playlists(
            user_id=user_id,
            skip=skip,
            limit=limit
        )
        
        return {
            "playlists": [
                {
                    "playlist_id": p.playlist_id,
                    "name": p.name,
                    "description": p.description,
                    "item_count": len(p.items),
                    "created_at": p.created_at.isoformat(),
                    "updated_at": p.updated_at.isoformat(),
                    "followers": p.stats.followers,
                    "likes": p.stats.likes
                }
                for p in playlists
            ],
            "total": len(playlists)
        }
    except Exception as e:
        logger.error(f"Get user playlists error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router_playlist.patch("/{playlist_id}")
async def update_playlist(
    playlist_id: str,
    user_id: str = Query(...),
    updates: Dict[str, Any] = Body(...)
):
    """Update playlist metadata"""
    try:
        playlist = await playlist_service.update_playlist_metadata(
            playlist_id=playlist_id,
            updates=updates,
            user_id=user_id
        )
        
        return {
            "status": "updated",
            "playlist_id": playlist.playlist_id,
            "name": playlist.name,
            "updated_at": playlist.updated_at.isoformat()
        }
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Update playlist error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router_playlist.delete("/{playlist_id}")
async def delete_playlist(
    playlist_id: str,
    user_id: str = Query(...)
):
    """Delete playlist"""
    try:
        playlist = await playlist_service.get_playlist(playlist_id)
        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist not found")
        
        if playlist.creator_id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # Remove playlist
        del playlist_service.playlists[playlist_id]
        
        return {"status": "deleted", "playlist_id": playlist_id}
    except Exception as e:
        logger.error(f"Delete playlist error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# ITEM MANAGEMENT
# ============================================================================

@router_playlist.post("/{playlist_id}/items")
async def add_item_to_playlist(
    playlist_id: str,
    item_id: str = Query(...),
    content_type: str = Query(...),
    title: str = Query(...),
    creator: str = Query(...),
    description: Optional[str] = Query(None),
    duration_seconds: Optional[int] = Query(None),
    user_id: Optional[str] = Query(None)
):
    """Add item to playlist"""
    try:
        success = await playlist_service.add_item_to_playlist(
            playlist_id=playlist_id,
            item_id=item_id,
            content_type=ContentType(content_type),
            title=title,
            creator=creator,
            description=description,
            duration_seconds=duration_seconds,
            user_id=user_id
        )
        
        if success:
            playlist = await playlist_service.get_playlist(playlist_id)
            return {
                "status": "added",
                "playlist_id": playlist_id,
                "item_id": item_id,
                "item_count": len(playlist.items)
            }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Add item error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router_playlist.delete("/{playlist_id}/items/{item_id}")
async def remove_item_from_playlist(
    playlist_id: str,
    item_id: str,
    user_id: Optional[str] = Query(None)
):
    """Remove item from playlist"""
    try:
        success = await playlist_service.remove_item_from_playlist(
            playlist_id=playlist_id,
            item_id=item_id,
            user_id=user_id
        )
        
        if success:
            return {"status": "removed", "playlist_id": playlist_id, "item_id": item_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Remove item error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router_playlist.get("/{playlist_id}/items")
async def get_playlist_items(
    playlist_id: str,
    skip: int = Query(0),
    limit: int = Query(50)
):
    """Get playlist items"""
    try:
        playlist = await playlist_service.get_playlist(playlist_id)
        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist not found")
        
        items = playlist.items[skip:skip+limit]
        
        return {
            "playlist_id": playlist_id,
            "items": [
                {
                    "item_id": item.item_id,
                    "content_type": item.content_type.value,
                    "title": item.title,
                    "creator": item.creator,
                    "duration_seconds": item.duration_seconds,
                    "order_index": item.order_index,
                    "added_at": item.added_at.isoformat()
                }
                for item in items
            ],
            "total": len(playlist.items)
        }
    except Exception as e:
        logger.error(f"Get items error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router_playlist.post("/{playlist_id}/reorder")
async def reorder_playlist_items(
    playlist_id: str,
    user_id: str = Query(...),
    item_order: List[str] = Body(...)
):
    """Reorder playlist items"""
    try:
        success = await playlist_service.reorder_items(
            playlist_id=playlist_id,
            item_order=item_order,
            user_id=user_id
        )
        
        if success:
            return {"status": "reordered", "playlist_id": playlist_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Reorder error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# ENGAGEMENT
# ============================================================================

@router_playlist.post("/{playlist_id}/like")
async def like_playlist(
    playlist_id: str,
    user_id: str = Query(...)
):
    """Like a playlist"""
    try:
        success = await playlist_service.like_playlist(playlist_id, user_id)
        if success:
            return {"status": "liked", "playlist_id": playlist_id}
    except Exception as e:
        logger.error(f"Like error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router_playlist.post("/{playlist_id}/save")
async def save_playlist(
    playlist_id: str,
    user_id: str = Query(...)
):
    """Save playlist to library"""
    try:
        success = await playlist_service.save_playlist(playlist_id, user_id)
        if success:
            return {"status": "saved", "playlist_id": playlist_id}
    except Exception as e:
        logger.error(f"Save error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router_playlist.post("/{playlist_id}/follow")
async def follow_playlist(
    playlist_id: str,
    user_id: str = Query(...)
):
    """Follow a playlist"""
    try:
        success = await playlist_service.follow_playlist(playlist_id, user_id)
        if success:
            return {"status": "following", "playlist_id": playlist_id}
    except Exception as e:
        logger.error(f"Follow error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# SHARING & COLLABORATION
# ============================================================================

@router_share.post("/{playlist_id}")
async def share_playlist(
    playlist_id: str,
    shared_by: str = Query(...),
    shared_with: Optional[str] = Query(None),
    share_type: str = Query("link"),
    platform: Optional[str] = Query(None)
):
    """Share playlist"""
    try:
        share = await playlist_service.share_playlist(
            playlist_id=playlist_id,
            shared_by=shared_by,
            shared_with=shared_with,
            share_type=share_type,
            platform=platform
        )
        
        return {
            "status": "shared",
            "share_id": share.share_id,
            "share_token": await playlist_service.get_playlist(playlist_id).then(
                lambda p: p.share_token
            ) if await playlist_service.get_playlist(playlist_id) else None,
            "shared_at": share.shared_at.isoformat()
        }
    except Exception as e:
        logger.error(f"Share error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router_share.post("/{playlist_id}/duplicate")
async def duplicate_playlist(
    playlist_id: str,
    user_id: str = Query(...),
    user_name: str = Query(...),
    new_name: Optional[str] = Query(None)
):
    """Duplicate a playlist"""
    try:
        new_playlist = await playlist_service.duplicate_playlist(
            source_playlist_id=playlist_id,
            new_creator_id=user_id,
            new_creator_name=user_name,
            new_name=new_name
        )
        
        return {
            "status": "duplicated",
            "new_playlist_id": new_playlist.playlist_id,
            "name": new_playlist.name,
            "items": len(new_playlist.items)
        }
    except Exception as e:
        logger.error(f"Duplicate error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router_share.post("/{playlist_id}/collaborator")
async def add_collaborator(
    playlist_id: str,
    collaborator_id: str = Query(...),
    user_id: str = Query(...),
    role: str = Query("editor")
):
    """Add collaborator to playlist"""
    try:
        success = await playlist_service.add_collaborator(
            playlist_id=playlist_id,
            collaborator_id=collaborator_id,
            role=role,
            user_id=user_id
        )
        
        if success:
            return {"status": "collaborator_added", "playlist_id": playlist_id}
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Collaborator error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# DISCOVERY & RECOMMENDATIONS
# ============================================================================

@router_playlist.get("/search/find")
async def search_playlists(
    query: str = Query(...),
    content_type: Optional[str] = Query(None),
    mood: Optional[str] = Query(None),
    limit: int = Query(20)
):
    """Search for playlists"""
    try:
        content_type_enum = ContentType(content_type) if content_type else None
        
        results = await playlist_service.search_playlists(
            query=query,
            content_type=content_type_enum,
            mood=mood,
            limit=limit
        )
        
        return {
            "results": [
                {
                    "playlist_id": p.playlist_id,
                    "name": p.name,
                    "creator_name": p.creator_name,
                    "item_count": len(p.items),
                    "followers": p.stats.followers
                }
                for p in results
            ],
            "total": len(results)
        }
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router_playlist.get("/trending/all")
async def get_trending_playlists(
    limit: int = Query(20),
    content_type: Optional[str] = Query(None)
):
    """Get trending playlists"""
    try:
        content_type_enum = ContentType(content_type) if content_type else None
        
        trending = await playlist_service.get_trending_playlists(
            limit=limit,
            content_type=content_type_enum
        )
        
        return {
            "trending": [
                {
                    "playlist_id": p.playlist_id,
                    "name": p.name,
                    "creator_name": p.creator_name,
                    "item_count": len(p.items),
                    "followers": p.stats.followers,
                    "plays": p.stats.plays,
                    "likes": p.stats.likes
                }
                for p in trending
            ],
            "total": len(trending)
        }
    except Exception as e:
        logger.error(f"Trending error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router_playlist.get("/recommendations/for-user")
async def get_recommendations(
    user_id: str = Query(...),
    limit: int = Query(10)
):
    """Get personalized recommendations"""
    try:
        recommendations = await playlist_service.get_playlist_recommendations(
            user_id=user_id,
            limit=limit
        )
        
        return {
            "recommendations": [
                {
                    "playlist_id": p.playlist_id,
                    "name": p.name,
                    "creator_name": p.creator_name,
                    "item_count": len(p.items),
                    "followers": p.stats.followers
                }
                for p in recommendations
            ],
            "total": len(recommendations)
        }
    except Exception as e:
        logger.error(f"Recommendations error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# PLAYLIST CREATION HELPERS
# ============================================================================

@router_create.get("/templates")
async def get_templates():
    """Get playlist templates"""
    try:
        templates = playlist_service.get_templates()
        
        return {
            "templates": [
                {
                    "template_id": t.template_id,
                    "name": t.name,
                    "description": t.description,
                    "category": t.category,
                    "icon": t.icon,
                    "content_type": t.default_content_type.value,
                    "mood": t.mood
                }
                for t in templates.values()
            ]
        }
    except Exception as e:
        logger.error(f"Get templates error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router_create.post("/from-template")
async def create_from_template(
    template_id: str = Query(...),
    user_id: str = Query(...),
    user_name: str = Query(...),
    playlist_name: Optional[str] = Query(None)
):
    """Create playlist from template"""
    try:
        template = playlist_service.get_template(template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        name = playlist_name or template.name
        playlist = await playlist_service.create_playlist(
            name=name,
            creator_id=user_id,
            creator_name=user_name,
            description=template.description,
            mood=template.mood,
            curation_strategy=CurationStrategy.THEME_BASED
        )
        
        return {
            "status": "created",
            "playlist_id": playlist.playlist_id,
            "name": playlist.name,
            "template_used": template_id
        }
    except Exception as e:
        logger.error(f"Template creation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router_create.post("/name-suggestions")
async def get_name_suggestions(
    item_ids: List[str] = Body(...),
    mood: Optional[str] = Query(None),
    theme: Optional[str] = Query(None)
):
    """Get playlist name suggestions"""
    try:
        # Create mock items for suggestion generation
        items = [
            PlaylistItem(
                item_id=item_id,
                content_type=ContentType.MUSIC,
                title=f"Item {item_id}",
                creator="Unknown"
            )
            for item_id in item_ids
        ]
        
        suggestions = await playlist_service.generate_playlist_name_suggestions(
            items=items,
            mood=mood,
            theme=theme
        )
        
        return {"suggestions": suggestions}
    except Exception as e:
        logger.error(f"Suggestions error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# SPECIALIZED CREATION ENDPOINTS
# ============================================================================

@router_create.post("/music")
async def create_music_playlist(
    user_id: str = Query(...),
    user_name: str = Query(...),
    playlist_name: str = Query(...),
    track_ids: Optional[List[str]] = Body(None),
    mood: Optional[str] = Query(None),
    tags: Optional[List[str]] = Query(None)
):
    """Create music playlist"""
    try:
        playlist = await playlist_integration.create_music_playlist(
            user_id=user_id,
            user_name=user_name,
            playlist_name=playlist_name,
            track_ids=track_ids,
            mood=mood,
            tags=tags
        )
        
        return {
            "status": "created",
            "playlist_id": playlist.playlist_id,
            "name": playlist.name,
            "item_count": len(playlist.items)
        }
    except Exception as e:
        logger.error(f"Music playlist error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router_create.post("/movies")
async def create_movie_playlist(
    user_id: str = Query(...),
    user_name: str = Query(...),
    playlist_name: str = Query(...),
    movie_ids: Optional[List[str]] = Body(None),
    genre: Optional[str] = Query(None)
):
    """Create movie playlist"""
    try:
        playlist = await playlist_integration.create_movie_playlist(
            user_id=user_id,
            user_name=user_name,
            playlist_name=playlist_name,
            movie_ids=movie_ids,
            genre=genre
        )
        
        return {
            "status": "created",
            "playlist_id": playlist.playlist_id,
            "name": playlist.name,
            "item_count": len(playlist.items)
        }
    except Exception as e:
        logger.error(f"Movie playlist error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router_create.post("/videos")
async def create_video_playlist(
    user_id: str = Query(...),
    user_name: str = Query(...),
    playlist_name: str = Query(...),
    video_ids: Optional[List[str]] = Body(None)
):
    """Create video playlist"""
    try:
        playlist = await playlist_integration.create_video_playlist(
            user_id=user_id,
            user_name=user_name,
            playlist_name=playlist_name,
            video_ids=video_ids
        )
        
        return {
            "status": "created",
            "playlist_id": playlist.playlist_id,
            "name": playlist.name,
            "item_count": len(playlist.items)
        }
    except Exception as e:
        logger.error(f"Video playlist error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router_create.post("/music-videos")
async def create_music_video_playlist(
    user_id: str = Query(...),
    user_name: str = Query(...),
    playlist_name: str = Query(...),
    music_video_ids: Optional[List[str]] = Body(None),
    artist: Optional[str] = Query(None)
):
    """Create music video playlist"""
    try:
        playlist = await playlist_integration.create_music_video_playlist(
            user_id=user_id,
            user_name=user_name,
            playlist_name=playlist_name,
            music_video_ids=music_video_ids,
            artist=artist
        )
        
        return {
            "status": "created",
            "playlist_id": playlist.playlist_id,
            "name": playlist.name,
            "item_count": len(playlist.items)
        }
    except Exception as e:
        logger.error(f"Music video playlist error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router_create.post("/mixed-content")
async def create_mixed_playlist(
    user_id: str = Query(...),
    user_name: str = Query(...),
    playlist_name: str = Query(...),
    items: Dict[str, List[str]] = Body(...)
):
    """Create playlist with mixed content types"""
    try:
        # Convert content type strings to enums
        items_dict = {
            ContentType(k): v for k, v in items.items()
        }
        
        playlist = await playlist_integration.create_mixed_content_playlist(
            user_id=user_id,
            user_name=user_name,
            playlist_name=playlist_name,
            items=items_dict
        )
        
        return {
            "status": "created",
            "playlist_id": playlist.playlist_id,
            "name": playlist.name,
            "item_count": len(playlist.items),
            "content_types": [t.value for t in playlist.content_types]
        }
    except Exception as e:
        logger.error(f"Mixed playlist error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
