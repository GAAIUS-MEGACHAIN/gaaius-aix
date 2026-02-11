"""
AI TOOLS ANALYTICS ROUTES
================================================================================
Analytics endpoints for new AI tools:
- Image Resizer
- Image Converter
- Document Studio
- AI Builder
- Videos Platform (Multitube)
- Sound/Audio
================================================================================
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone, timedelta
from .comprehensive_analytics import (
    ComprehensiveAnalyticsEngine,
    FeatureType,
    ActivityType,
    ImageResizerAnalytics,
    ImageConverterAnalytics,
    DocumentStudioAnalytics,
    AIBuilderAnalytics,
    VideoPlatformAnalytics,
    SoundAnalytics,
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/analytics/ai-tools", tags=["AI Tools Analytics"])

# Inject analytics engine (would come from dependency)
analytics_engine: ComprehensiveAnalyticsEngine = None


# ============== IMAGE RESIZER ANALYTICS ==============

@router.post("/image-resizer/track")
async def track_image_resize(
    user_id: str,
    original_dimensions: str,
    output_dimensions: str,
    input_format: str,
    output_format: str,
    duration_seconds: float,
    success: bool = True,
    error_message: Optional[str] = None,
):
    """Track image resize operation"""
    try:
        await analytics_engine.track_activity(
            user_id=user_id,
            feature=FeatureType.IMAGE_RESIZER,
            activity=ActivityType.UPDATE,
            resource_name=f"resize_{original_dimensions}_to_{output_dimensions}",
            duration_seconds=duration_seconds,
            success=success,
            error_message=error_message,
            metadata={
                "dimensions": f"{original_dimensions} → {output_dimensions}",
                "input_format": input_format,
                "output_format": output_format,
                "operation": "resize",
            }
        )
        return {"status": "tracked", "message": "Image resize tracked successfully"}
    except Exception as e:
        logger.error(f"Error tracking image resize: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/image-resizer/analytics")
async def get_image_resizer_analytics(user_id: str):
    """Get image resizer usage analytics"""
    try:
        user_profile = analytics_engine.user_profiles.get(user_id)
        if not user_profile:
            return {"message": "No resizer activity found for this user"}
        
        user_events = analytics_engine.user_events.get(user_id, [])
        analytics = ImageResizerAnalytics.analyze_resizer(user_events)
        
        return {
            "user_id": user_id,
            "total_resizes": analytics.get('total_resizes', 0),
            "resizes_this_month": analytics.get('resizes_this_month', 0),
            "avg_resize_time": round(analytics.get('avg_resize_time', 0), 2),
            "success_rate": round(analytics.get('success_rate', 0), 2),
            "most_common_format": max(set(analytics.get('format_preferences', [])), default=None),
        }
    except Exception as e:
        logger.error(f"Error getting resizer analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/image-resizer/trending")
async def get_trending_resize_dimensions():
    """Get trending resize dimensions across all users"""
    try:
        all_events = []
        for events in analytics_engine.user_events.values():
            all_events.extend(events)
        
        resizer_events = [e for e in all_events if e.feature == FeatureType.IMAGE_RESIZER]
        dimensions = [e.metadata.get('dimensions', '') for e in resizer_events if 'dimensions' in e.metadata]
        
        # Count occurrences
        dimension_counts = {}
        for dim in dimensions:
            dimension_counts[dim] = dimension_counts.get(dim, 0) + 1
        
        # Sort by count
        trending = sorted(dimension_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "trending_dimensions": [{"dimensions": dim, "count": count} for dim, count in trending],
            "total_resizes": len(resizer_events),
        }
    except Exception as e:
        logger.error(f"Error getting trending dimensions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============== IMAGE CONVERTER ANALYTICS ==============

@router.post("/image-converter/track")
async def track_image_conversion(
    user_id: str,
    input_format: str,
    output_format: str,
    quality: int,
    duration_seconds: float,
    success: bool = True,
    error_message: Optional[str] = None,
):
    """Track image conversion operation"""
    try:
        await analytics_engine.track_activity(
            user_id=user_id,
            feature=FeatureType.IMAGE_CONVERTER,
            activity=ActivityType.UPDATE,
            resource_name=f"convert_{input_format}_to_{output_format}",
            duration_seconds=duration_seconds,
            success=success,
            error_message=error_message,
            metadata={
                "input_format": input_format,
                "output_format": output_format,
                "quality": quality,
                "operation": "convert",
            }
        )
        return {"status": "tracked", "message": "Image conversion tracked successfully"}
    except Exception as e:
        logger.error(f"Error tracking image conversion: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/image-converter/analytics")
async def get_image_converter_analytics(user_id: str):
    """Get image converter usage analytics"""
    try:
        user_profile = analytics_engine.user_profiles.get(user_id)
        if not user_profile:
            return {"message": "No converter activity found for this user"}
        
        user_events = analytics_engine.user_events.get(user_id, [])
        analytics = ImageConverterAnalytics.analyze_converter(user_events)
        
        return {
            "user_id": user_id,
            "total_conversions": analytics.get('total_conversions', 0),
            "conversions_this_month": analytics.get('conversions_this_month', 0),
            "avg_conversion_time": round(analytics.get('avg_conversion_time', 0), 2),
            "success_rate": round(analytics.get('conversion_success_rate', 0), 2),
            "most_used_quality": max(set(analytics.get('quality_settings_used', [])), default=None),
        }
    except Exception as e:
        logger.error(f"Error getting converter analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/image-converter/popular-conversions")
async def get_popular_conversions():
    """Get most popular format conversions"""
    try:
        all_events = []
        for events in analytics_engine.user_events.values():
            all_events.extend(events)
        
        converter_events = [e for e in all_events if e.feature == FeatureType.IMAGE_CONVERTER]
        
        conversions = {}
        for event in converter_events:
            input_fmt = event.metadata.get('input_format', '')
            output_fmt = event.metadata.get('output_format', '')
            if input_fmt and output_fmt:
                key = f"{input_fmt} → {output_fmt}"
                conversions[key] = conversions.get(key, 0) + 1
        
        popular = sorted(conversions.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "popular_conversions": [{"conversion": conv, "count": count} for conv, count in popular],
            "total_conversions": len(converter_events),
        }
    except Exception as e:
        logger.error(f"Error getting popular conversions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============== DOCUMENT STUDIO ANALYTICS ==============

@router.post("/document-studio/track")
async def track_document_generation(
    user_id: str,
    doc_type: str,
    export_format: str,
    duration_seconds: float,
    success: bool = True,
    error_message: Optional[str] = None,
):
    """Track document generation"""
    try:
        await analytics_engine.track_activity(
            user_id=user_id,
            feature=FeatureType.DOCUMENT_STUDIO,
            activity=ActivityType.CREATE,
            resource_name=f"document_{doc_type}",
            duration_seconds=duration_seconds,
            success=success,
            error_message=error_message,
            metadata={
                "doc_type": doc_type,
                "export_format": export_format,
                "operation": "generate",
            }
        )
        return {"status": "tracked", "message": "Document generation tracked successfully"}
    except Exception as e:
        logger.error(f"Error tracking document generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/document-studio/analytics")
async def get_document_studio_analytics(user_id: str):
    """Get document studio usage analytics"""
    try:
        user_profile = analytics_engine.user_profiles.get(user_id)
        if not user_profile:
            return {"message": "No document activity found for this user"}
        
        user_events = analytics_engine.user_events.get(user_id, [])
        analytics = DocumentStudioAnalytics.analyze_document_studio(user_events)
        
        return {
            "user_id": user_id,
            "total_documents_generated": analytics.get('total_documents_generated', 0),
            "documents_this_month": analytics.get('documents_this_month', 0),
            "avg_generation_time": round(analytics.get('avg_generation_time', 0), 2),
            "success_rate": round(analytics.get('generation_success_rate', 0), 2),
            "document_types_used": list(set(analytics.get('document_types', []))),
            "export_formats": list(set(analytics.get('export_formats', []))),
        }
    except Exception as e:
        logger.error(f"Error getting document studio analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/document-studio/popular-types")
async def get_popular_document_types():
    """Get most popular document types"""
    try:
        all_events = []
        for events in analytics_engine.user_events.values():
            all_events.extend(events)
        
        doc_events = [e for e in all_events if e.feature == FeatureType.DOCUMENT_STUDIO]
        
        doc_types = {}
        for event in doc_events:
            doc_type = event.metadata.get('doc_type', 'unknown')
            doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
        
        popular = sorted(doc_types.items(), key=lambda x: x[1], reverse=True)[:15]
        
        return {
            "popular_document_types": [{"type": dtype, "count": count} for dtype, count in popular],
            "total_documents": len(doc_events),
        }
    except Exception as e:
        logger.error(f"Error getting popular document types: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============== AI BUILDER ANALYTICS ==============

@router.post("/ai-builder/track")
async def track_ai_builder_project(
    user_id: str,
    project_type: str,
    tech_stack: str,
    duration_seconds: float,
    quality_score: float,
    success: bool = True,
    error_message: Optional[str] = None,
):
    """Track AI Builder project generation"""
    try:
        await analytics_engine.track_activity(
            user_id=user_id,
            feature=FeatureType.AI_BUILDER,
            activity=ActivityType.CREATE,
            resource_name=f"project_{project_type}",
            duration_seconds=duration_seconds,
            success=success,
            error_message=error_message,
            metadata={
                "project_type": project_type,
                "tech_stack": tech_stack,
                "quality_score": quality_score,
                "operation": "generate",
            }
        )
        return {"status": "tracked", "message": "Project generation tracked successfully"}
    except Exception as e:
        logger.error(f"Error tracking project generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ai-builder/track-export")
async def track_ai_builder_export(user_id: str, export_format: str):
    """Track AI Builder project export"""
    try:
        await analytics_engine.track_activity(
            user_id=user_id,
            feature=FeatureType.AI_BUILDER,
            activity=ActivityType.DOWNLOAD,
            resource_name=f"export_{export_format}",
            metadata={"export_format": export_format}
        )
        return {"status": "tracked", "message": "Export tracked successfully"}
    except Exception as e:
        logger.error(f"Error tracking export: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ai-builder/analytics")
async def get_ai_builder_analytics(user_id: str):
    """Get AI Builder usage analytics"""
    try:
        user_profile = analytics_engine.user_profiles.get(user_id)
        if not user_profile:
            return {"message": "No builder activity found for this user"}
        
        user_events = analytics_engine.user_events.get(user_id, [])
        analytics = AIBuilderAnalytics.analyze_ai_builder(user_events)
        
        quality_scores = analytics.get('project_quality_scores', [])
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        
        return {
            "user_id": user_id,
            "total_projects_generated": analytics.get('total_projects_generated', 0),
            "projects_this_month": analytics.get('projects_this_month', 0),
            "avg_generation_time": round(analytics.get('avg_generation_time', 0), 2),
            "exports_created": analytics.get('exports_created', 0),
            "avg_quality_score": round(avg_quality, 2),
            "tech_stacks_used": list(set(analytics.get('tech_stacks_used', []))),
        }
    except Exception as e:
        logger.error(f"Error getting builder analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ai-builder/popular-stacks")
async def get_popular_tech_stacks():
    """Get most popular tech stacks used"""
    try:
        all_events = []
        for events in analytics_engine.user_events.values():
            all_events.extend(events)
        
        builder_events = [e for e in all_events if e.feature == FeatureType.AI_BUILDER]
        
        stacks = {}
        for event in builder_events:
            stack = event.metadata.get('tech_stack', 'unknown')
            stacks[stack] = stacks.get(stack, 0) + 1
        
        popular = sorted(stacks.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "popular_stacks": [{"stack": stack, "count": count} for stack, count in popular],
            "total_projects": len(builder_events),
        }
    except Exception as e:
        logger.error(f"Error getting popular stacks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============== VIDEOS PLATFORM ANALYTICS ==============

@router.post("/videos-platform/track-upload")
async def track_video_upload(
    user_id: str,
    title: str,
    duration_seconds: float,
    tags: List[str] = None,
):
    """Track video upload"""
    try:
        await analytics_engine.track_activity(
            user_id=user_id,
            feature=FeatureType.VIDEOS_PLATFORM,
            activity=ActivityType.UPLOAD,
            resource_name=title,
            duration_seconds=duration_seconds,
            metadata={
                "title": title,
                "tags": tags or [],
                "operation": "upload",
            }
        )
        return {"status": "tracked", "message": "Video upload tracked successfully"}
    except Exception as e:
        logger.error(f"Error tracking video upload: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/videos-platform/track-view")
async def track_video_view(
    user_id: str,
    video_id: str,
    watch_duration: float,
    completion_rate: float,
):
    """Track video view"""
    try:
        await analytics_engine.track_activity(
            user_id=user_id,
            feature=FeatureType.VIDEOS_PLATFORM,
            activity=ActivityType.VIEW,
            resource_id=video_id,
            duration_seconds=watch_duration,
            metadata={"completion_rate": completion_rate}
        )
        return {"status": "tracked", "message": "Video view tracked successfully"}
    except Exception as e:
        logger.error(f"Error tracking video view: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/videos-platform/analytics")
async def get_videos_platform_analytics(user_id: str):
    """Get videos platform usage analytics"""
    try:
        user_profile = analytics_engine.user_profiles.get(user_id)
        if not user_profile:
            return {"message": "No video activity found for this user"}
        
        user_events = analytics_engine.user_events.get(user_id, [])
        analytics = VideoPlatformAnalytics.analyze_videos_platform(user_events)
        
        return {
            "user_id": user_id,
            "total_videos_uploaded": analytics.get('total_videos_uploaded', 0),
            "uploads_this_month": analytics.get('uploads_this_month', 0),
            "total_video_views": analytics.get('total_video_views', 0),
            "total_watch_time": round(analytics.get('total_watch_time', 0), 2),
            "avg_view_duration": round(analytics.get('avg_view_duration', 0), 2),
            "video_completion_rate": round(analytics.get('video_completion_rate', 0), 2),
            "likes": analytics.get('likes_received', 0),
            "comments": analytics.get('comments', 0),
            "shares": analytics.get('shares', 0),
        }
    except Exception as e:
        logger.error(f"Error getting videos platform analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/videos-platform/trending-videos")
async def get_trending_videos(limit: int = Query(10, le=100)):
    """Get trending videos across platform"""
    try:
        all_events = []
        for events in analytics_engine.user_events.values():
            all_events.extend(events)
        
        video_events = [e for e in all_events if e.feature == FeatureType.VIDEOS_PLATFORM]
        
        # Group by video and count views
        video_stats = {}
        for event in video_events:
            video_id = event.resource_id
            if not video_id:
                continue
            if video_id not in video_stats:
                video_stats[video_id] = {
                    "views": 0,
                    "watch_time": 0,
                    "title": event.resource_name,
                }
            if event.activity == ActivityType.VIEW:
                video_stats[video_id]["views"] += 1
                video_stats[video_id]["watch_time"] += event.duration_seconds or 0
        
        trending = sorted(video_stats.items(), key=lambda x: x[1]["views"], reverse=True)[:limit]
        
        return {
            "trending_videos": [
                {
                    "video_id": vid,
                    "title": stats["title"],
                    "views": stats["views"],
                    "total_watch_time": round(stats["watch_time"], 2),
                }
                for vid, stats in trending
            ]
        }
    except Exception as e:
        logger.error(f"Error getting trending videos: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============== SOUND/AUDIO ANALYTICS ==============

@router.post("/sound/track")
async def track_sound_generation(
    user_id: str,
    format: str,
    duration_seconds: float,
    language: Optional[str] = None,
    voice: Optional[str] = None,
    success: bool = True,
    error_message: Optional[str] = None,
):
    """Track sound/audio generation"""
    try:
        activity = ActivityType.CREATE
        resource_name = f"audio_{format}"
        if language:
            resource_name += f"_{language}"
        
        await analytics_engine.track_activity(
            user_id=user_id,
            feature=FeatureType.SOUND,
            activity=activity,
            resource_name=resource_name,
            duration_seconds=duration_seconds,
            success=success,
            error_message=error_message,
            metadata={
                "format": format,
                "language": language,
                "voice": voice,
                "operation": "generate",
            }
        )
        return {"status": "tracked", "message": "Sound generation tracked successfully"}
    except Exception as e:
        logger.error(f"Error tracking sound generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sound/analytics")
async def get_sound_analytics(user_id: str):
    """Get sound/audio usage analytics"""
    try:
        user_profile = analytics_engine.user_profiles.get(user_id)
        if not user_profile:
            return {"message": "No sound activity found for this user"}
        
        user_events = analytics_engine.user_events.get(user_id, [])
        analytics = SoundAnalytics.analyze_sound(user_events)
        
        return {
            "user_id": user_id,
            "total_audio_files": analytics.get('total_audio_files', 0),
            "audio_files_this_month": analytics.get('audio_files_this_month', 0),
            "total_audio_duration": round(analytics.get('total_audio_created', 0), 2),
            "avg_audio_duration": round(analytics.get('avg_audio_duration', 0), 2),
            "audio_formats": list(set(analytics.get('audio_formats', []))),
            "voices_used": list(set(analytics.get('voices_used', []))),
            "languages": list(set(analytics.get('languages_supported', []))),
        }
    except Exception as e:
        logger.error(f"Error getting sound analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sound/popular-voices")
async def get_popular_voices():
    """Get most popular voices used"""
    try:
        all_events = []
        for events in analytics_engine.user_events.values():
            all_events.extend(events)
        
        sound_events = [e for e in all_events if e.feature == FeatureType.SOUND]
        
        voices = {}
        for event in sound_events:
            voice = event.metadata.get('voice', 'default')
            voices[voice] = voices.get(voice, 0) + 1
        
        popular = sorted(voices.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "popular_voices": [{"voice": voice, "usage_count": count} for voice, count in popular],
            "total_audio_generations": len(sound_events),
        }
    except Exception as e:
        logger.error(f"Error getting popular voices: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============== UNIFIED AI TOOLS ANALYTICS ==============

@router.get("/all-tools/summary")
async def get_all_ai_tools_summary(user_id: Optional[str] = None):
    """Get summary analytics for all AI tools"""
    try:
        if user_id:
            user_events = analytics_engine.user_events.get(user_id, [])
        else:
            # Aggregate across all users
            user_events = []
            for events in analytics_engine.user_events.values():
                user_events.extend(events)
        
        # Count usage by tool
        tool_usage = {}
        for event in user_events:
            tool = event.feature.value
            tool_usage[tool] = tool_usage.get(tool, 0) + 1
        
        return {
            "user_id": user_id or "all_users",
            "tool_usage": {
                "image_resizer": tool_usage.get("image_resizer", 0),
                "image_converter": tool_usage.get("image_converter", 0),
                "document_studio": tool_usage.get("document_studio", 0),
                "ai_builder": tool_usage.get("ai_builder", 0),
                "videos_platform": tool_usage.get("videos_platform", 0),
                "sound": tool_usage.get("sound", 0),
                "audio": tool_usage.get("audio", 0),
            },
            "total_operations": len(user_events),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        logger.error(f"Error getting all tools summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/all-tools/health")
async def ai_tools_analytics_health():
    """Health check for AI tools analytics"""
    try:
        total_users = len(analytics_engine.user_profiles)
        total_events = sum(len(events) for events in analytics_engine.user_events.values())
        
        return {
            "status": "healthy",
            "total_tracked_users": total_users,
            "total_tracked_events": total_events,
            "analytics_engine": "operational",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        logger.error(f"Error checking health: {e}")
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
