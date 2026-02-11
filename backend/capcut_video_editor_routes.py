"""
CapCut Video Editor API Routes
Endpoints for video editing operations
"""

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, BackgroundTasks, Query
from fastapi.responses import FileResponse
from typing import Optional, List
import os
import uuid
from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorDatabase

# Import the video editor service
from .capcut_video_editor_service import (
    VideoEditorService, VideoProject, VideoClip, Segment, Subtitle,
    AudioTrack, TextElement, StickersElement,
    EffectType, TransitionType, FilterType, AspectRatio, ResolutionType,
    FFmpegService, S3VideoService
)

# Import JWT auth
from .authentication_service import get_current_user, verify_token

# Create router
router = APIRouter(prefix="/api/v1/video-editor", tags=["video-editor"])

# ==================== DEPENDENCY INJECTION ====================

async def get_video_service(db: AsyncIOMotorDatabase = Depends(lambda: None)) -> VideoEditorService:
    """Get video editor service instance"""
    # This would be injected from main server
    from ..server import db as database
    return VideoEditorService(database)

# ==================== PROJECT ENDPOINTS ====================

@router.post("/projects", response_model=VideoProject)
async def create_project(
    project_data: dict,
    current_user: dict = Depends(get_current_user),
    service: VideoEditorService = Depends(get_video_service)
):
    """Create new video editing project"""
    try:
        project = await service.create_project(
            user_id=current_user['user_id'],
            title=project_data.get('title', 'Untitled Project'),
            description=project_data.get('description'),
            aspect_ratio=AspectRatio(project_data.get('aspect_ratio', '9:16'))
        )
        return project
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Project creation failed: {str(e)}")

@router.get("/projects/{project_id}", response_model=VideoProject)
async def get_project(
    project_id: str,
    current_user: dict = Depends(get_current_user),
    service: VideoEditorService = Depends(get_video_service)
):
    """Get project details"""
    project = await service.get_project(project_id, current_user['user_id'])
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.get("/projects", response_model=List[VideoProject])
async def list_projects(
    skip: int = Query(0),
    limit: int = Query(20),
    current_user: dict = Depends(get_current_user),
    service: VideoEditorService = Depends(get_video_service)
):
    """List user's projects"""
    projects, total = await service.list_projects(current_user['user_id'], skip, limit)
    return projects

@router.put("/projects/{project_id}", response_model=VideoProject)
async def update_project(
    project_id: str,
    updates: dict,
    current_user: dict = Depends(get_current_user),
    service: VideoEditorService = Depends(get_video_service)
):
    """Update project"""
    project = await service.update_project(project_id, current_user['user_id'], updates)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.delete("/projects/{project_id}")
async def delete_project(
    project_id: str,
    current_user: dict = Depends(get_current_user),
    service: VideoEditorService = Depends(get_video_service)
):
    """Delete project"""
    success = await service.delete_project(project_id, current_user['user_id'])
    if not success:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"message": "Project deleted successfully"}

# ==================== VIDEO CLIP ENDPOINTS ====================

@router.post("/projects/{project_id}/clips", response_model=VideoClip)
async def add_clip(
    project_id: str,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    service: VideoEditorService = Depends(get_video_service)
):
    """Add video clip to project"""
    try:
        clip = await service.add_video_clip(
            project_id=project_id,
            user_id=current_user['user_id'],
            file=file.file,
            filename=file.filename or f"clip_{uuid.uuid4().hex[:8]}.mp4"
        )
        if not clip:
            raise HTTPException(status_code=400, detail="Failed to add clip")
        return clip
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Clip upload failed: {str(e)}")

@router.delete("/projects/{project_id}/clips/{clip_id}")
async def remove_clip(
    project_id: str,
    clip_id: str,
    current_user: dict = Depends(get_current_user),
    service: VideoEditorService = Depends(get_video_service)
):
    """Remove clip from project"""
    success = await service.remove_video_clip(project_id, clip_id, current_user['user_id'])
    if not success:
        raise HTTPException(status_code=404, detail="Clip not found")
    return {"message": "Clip removed successfully"}

# ==================== SEGMENT/TIMELINE ENDPOINTS ====================

@router.post("/projects/{project_id}/segments", response_model=Segment)
async def create_segment(
    project_id: str,
    segment_data: dict,
    current_user: dict = Depends(get_current_user),
    service: VideoEditorService = Depends(get_video_service)
):
    """Create segment from clip"""
    try:
        segment = await service.create_segment(
            project_id=project_id,
            clip_id=segment_data.get('clip_id'),
            start_time_ms=segment_data.get('start_time_ms', 0),
            end_time_ms=segment_data.get('end_time_ms', 0),
            clip_index=segment_data.get('clip_index', 0)
        )
        if not segment:
            raise HTTPException(status_code=400, detail="Failed to create segment")
        return segment
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Segment creation failed: {str(e)}")

@router.put("/projects/{project_id}/segments/{segment_id}", response_model=Segment)
async def update_segment(
    project_id: str,
    segment_id: str,
    updates: dict,
    current_user: dict = Depends(get_current_user),
    service: VideoEditorService = Depends(get_video_service)
):
    """Update segment properties"""
    segment = await service.update_segment(project_id, segment_id, updates)
    if not segment:
        raise HTTPException(status_code=404, detail="Segment not found")
    return segment

@router.put("/projects/{project_id}/segments/{segment_id}/trim")
async def trim_segment(
    project_id: str,
    segment_id: str,
    trim_data: dict,
    current_user: dict = Depends(get_current_user),
    service: VideoEditorService = Depends(get_video_service)
):
    """Trim segment"""
    segment = await service.trim_segment(
        project_id=project_id,
        segment_id=segment_id,
        trim_start_ms=trim_data.get('trim_start_ms', 0),
        trim_end_ms=trim_data.get('trim_end_ms', 0)
    )
    if not segment:
        raise HTTPException(status_code=404, detail="Segment not found")
    return {"message": "Segment trimmed", "segment": segment}

@router.post("/projects/{project_id}/segments/{segment_id}/effects")
async def apply_effect(
    project_id: str,
    segment_id: str,
    effect_data: dict,
    current_user: dict = Depends(get_current_user),
    service: VideoEditorService = Depends(get_video_service)
):
    """Apply effect to segment"""
    try:
        segment = await service.apply_effect_to_segment(
            project_id=project_id,
            segment_id=segment_id,
            effect_type=EffectType(effect_data.get('effect_type', 'none')),
            intensity=effect_data.get('intensity', 0.5)
        )
        if not segment:
            raise HTTPException(status_code=404, detail="Segment not found")
        return {"message": "Effect applied", "segment": segment}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Effect application failed: {str(e)}")

@router.post("/projects/{project_id}/segments/{segment_id}/filters")
async def apply_filter(
    project_id: str,
    segment_id: str,
    filter_data: dict,
    current_user: dict = Depends(get_current_user),
    service: VideoEditorService = Depends(get_video_service)
):
    """Apply color filter to segment"""
    try:
        segment = await service.apply_filter_to_segment(
            project_id=project_id,
            segment_id=segment_id,
            filter_type=FilterType(filter_data.get('filter_type', 'none'))
        )
        if not segment:
            raise HTTPException(status_code=404, detail="Segment not found")
        return {"message": "Filter applied", "segment": segment}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Filter application failed: {str(e)}")

# ==================== SUBTITLE ENDPOINTS ====================

@router.post("/projects/{project_id}/subtitles", response_model=Subtitle)
async def add_subtitle(
    project_id: str,
    subtitle_data: dict,
    current_user: dict = Depends(get_current_user),
    service: VideoEditorService = Depends(get_video_service)
):
    """Add subtitle to project"""
    try:
        subtitle = await service.add_subtitle(
            project_id=project_id,
            text=subtitle_data.get('text'),
            start_time_ms=subtitle_data.get('start_time_ms'),
            end_time_ms=subtitle_data.get('end_time_ms'),
            style=subtitle_data.get('style')
        )
        if not subtitle:
            raise HTTPException(status_code=400, detail="Failed to add subtitle")
        return subtitle
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Subtitle addition failed: {str(e)}")

@router.post("/projects/{project_id}/subtitles/auto-generate")
async def generate_auto_subtitles(
    project_id: str,
    language: str = Query("en"),
    current_user: dict = Depends(get_current_user),
    service: VideoEditorService = Depends(get_video_service)
):
    """Generate subtitles automatically from audio"""
    try:
        subtitles = await service.generate_auto_subtitles(project_id, language)
        return {
            "message": "Auto-subtitles generation started",
            "subtitles_count": len(subtitles),
            "language": language
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Auto-subtitle generation failed: {str(e)}")

@router.put("/projects/{project_id}/subtitles/{subtitle_id}", response_model=Subtitle)
async def update_subtitle(
    project_id: str,
    subtitle_id: str,
    updates: dict,
    current_user: dict = Depends(get_current_user),
    service: VideoEditorService = Depends(get_video_service)
):
    """Update subtitle"""
    subtitle = await service.update_subtitle(subtitle_id, updates)
    if not subtitle:
        raise HTTPException(status_code=404, detail="Subtitle not found")
    return subtitle

@router.delete("/projects/{project_id}/subtitles/{subtitle_id}")
async def delete_subtitle(
    project_id: str,
    subtitle_id: str,
    current_user: dict = Depends(get_current_user),
    service: VideoEditorService = Depends(get_video_service)
):
    """Delete subtitle"""
    success = await service.delete_subtitle(project_id, subtitle_id)
    if not success:
        raise HTTPException(status_code=404, detail="Subtitle not found")
    return {"message": "Subtitle deleted successfully"}

# ==================== AUDIO ENDPOINTS ====================

@router.post("/projects/{project_id}/audio", response_model=AudioTrack)
async def add_audio(
    project_id: str,
    file: UploadFile = File(...),
    audio_type: str = "music",
    current_user: dict = Depends(get_current_user),
    service: VideoEditorService = Depends(get_video_service)
):
    """Add audio track to project"""
    try:
        audio = await service.add_audio_track(
            project_id=project_id,
            file=file.file,
            filename=file.filename or f"audio_{uuid.uuid4().hex[:8]}.mp3",
            user_id=current_user['user_id'],
            audio_type=audio_type
        )
        if not audio:
            raise HTTPException(status_code=400, detail="Failed to add audio")
        return audio
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audio upload failed: {str(e)}")

@router.put("/projects/{project_id}/audio/{audio_id}/volume")
async def adjust_volume(
    project_id: str,
    audio_id: str,
    volume_data: dict,
    current_user: dict = Depends(get_current_user),
    service: VideoEditorService = Depends(get_video_service)
):
    """Adjust audio volume"""
    try:
        audio = await service.adjust_audio_volume(
            audio_id=audio_id,
            volume=volume_data.get('volume', 1.0)
        )
        if not audio:
            raise HTTPException(status_code=404, detail="Audio not found")
        return {"message": "Volume adjusted", "audio": audio}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Volume adjustment failed: {str(e)}")

@router.put("/projects/{project_id}/audio/{audio_id}/fade")
async def add_fade(
    project_id: str,
    audio_id: str,
    fade_data: dict,
    current_user: dict = Depends(get_current_user),
    service: VideoEditorService = Depends(get_video_service)
):
    """Add fade in/out to audio"""
    try:
        audio = await service.add_audio_fade(
            audio_id=audio_id,
            fade_in_ms=fade_data.get('fade_in_ms', 0),
            fade_out_ms=fade_data.get('fade_out_ms', 0)
        )
        if not audio:
            raise HTTPException(status_code=404, detail="Audio not found")
        return {"message": "Fade applied", "audio": audio}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fade application failed: {str(e)}")

@router.delete("/projects/{project_id}/audio/{audio_id}")
async def remove_audio(
    project_id: str,
    audio_id: str,
    current_user: dict = Depends(get_current_user),
    service: VideoEditorService = Depends(get_video_service)
):
    """Remove audio track"""
    success = await service.remove_audio_track(project_id, audio_id)
    if not success:
        raise HTTPException(status_code=404, detail="Audio not found")
    return {"message": "Audio removed successfully"}

# ==================== TEXT ELEMENT ENDPOINTS ====================

@router.post("/projects/{project_id}/text", response_model=TextElement)
async def add_text(
    project_id: str,
    text_data: dict,
    current_user: dict = Depends(get_current_user),
    service: VideoEditorService = Depends(get_video_service)
):
    """Add text overlay/title"""
    try:
        text = await service.add_text_element(
            project_id=project_id,
            content=text_data.get('content'),
            start_time_ms=text_data.get('start_time_ms'),
            end_time_ms=text_data.get('end_time_ms'),
            style=text_data.get('style')
        )
        if not text:
            raise HTTPException(status_code=400, detail="Failed to add text")
        return text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Text addition failed: {str(e)}")

@router.put("/projects/{project_id}/text/{text_id}", response_model=TextElement)
async def update_text(
    project_id: str,
    text_id: str,
    updates: dict,
    current_user: dict = Depends(get_current_user),
    service: VideoEditorService = Depends(get_video_service)
):
    """Update text element"""
    text = await service.update_text_element(text_id, updates)
    if not text:
        raise HTTPException(status_code=404, detail="Text not found")
    return text

@router.delete("/projects/{project_id}/text/{text_id}")
async def delete_text(
    project_id: str,
    text_id: str,
    current_user: dict = Depends(get_current_user),
    service: VideoEditorService = Depends(get_video_service)
):
    """Delete text element"""
    success = await service.delete_text_element(project_id, text_id)
    if not success:
        raise HTTPException(status_code=404, detail="Text not found")
    return {"message": "Text deleted successfully"}

# ==================== STICKER ENDPOINTS ====================

@router.post("/projects/{project_id}/stickers", response_model=StickersElement)
async def add_sticker(
    project_id: str,
    sticker_data: dict,
    current_user: dict = Depends(get_current_user),
    service: VideoEditorService = Depends(get_video_service)
):
    """Add sticker to video"""
    try:
        sticker = await service.add_sticker(
            project_id=project_id,
            sticker_url=sticker_data.get('sticker_url'),
            start_time_ms=sticker_data.get('start_time_ms'),
            end_time_ms=sticker_data.get('end_time_ms'),
            position_x=sticker_data.get('position_x', 0.5),
            position_y=sticker_data.get('position_y', 0.5),
            scale=sticker_data.get('scale', 1.0)
        )
        if not sticker:
            raise HTTPException(status_code=400, detail="Failed to add sticker")
        return sticker
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sticker addition failed: {str(e)}")

@router.delete("/projects/{project_id}/stickers/{sticker_id}")
async def remove_sticker(
    project_id: str,
    sticker_id: str,
    current_user: dict = Depends(get_current_user),
    service: VideoEditorService = Depends(get_video_service)
):
    """Remove sticker"""
    success = await service.delete_sticker(project_id, sticker_id)
    if not success:
        raise HTTPException(status_code=404, detail="Sticker not found")
    return {"message": "Sticker removed successfully"}

# ==================== EXPORT ENDPOINTS ====================

@router.post("/projects/{project_id}/export")
async def export_video(
    project_id: str,
    export_data: dict,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    service: VideoEditorService = Depends(get_video_service)
):
    """Start video export/rendering"""
    try:
        resolution = ResolutionType(export_data.get('resolution', '1080p'))
        
        result = await service.export_video(
            project_id=project_id,
            user_id=current_user['user_id'],
            resolution=resolution,
            include_watermark=export_data.get('include_watermark', False)
        )
        
        if not result:
            raise HTTPException(status_code=400, detail="Export failed")
        
        return {
            "message": "Video export started",
            "export_id": result['export_id'],
            "status": result['status'],
            "estimated_time": result['estimated_time_seconds']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

@router.get("/exports/{export_id}/progress")
async def get_export_progress(
    export_id: str,
    current_user: dict = Depends(get_current_user),
    service: VideoEditorService = Depends(get_video_service)
):
    """Get export progress"""
    progress = await service.get_export_progress(export_id)
    if not progress:
        raise HTTPException(status_code=404, detail="Export not found")
    return progress

# ==================== LIBRARY ENDPOINTS ====================

@router.get("/effects/presets")
async def get_effect_presets(
    current_user: dict = Depends(get_current_user),
    service: VideoEditorService = Depends(get_video_service)
):
    """Get available effect presets"""
    return await service.get_effect_presets()

@router.get("/transitions/templates")
async def get_transitions(
    current_user: dict = Depends(get_current_user),
    service: VideoEditorService = Depends(get_video_service)
):
    """Get available transitions"""
    return await service.get_transition_templates()

@router.get("/music/library")
async def get_music_library(
    skip: int = Query(0),
    limit: int = Query(20),
    current_user: dict = Depends(get_current_user),
    service: VideoEditorService = Depends(get_video_service)
):
    """Get royalty-free music library"""
    return await service.get_music_library(skip, limit)

# Export router
__all__ = ['router']
