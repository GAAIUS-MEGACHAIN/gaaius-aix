"""
COMPREHENSIVE ANALYTICS API ROUTES
================================================================================
REST API endpoints for the advanced analytics dashboard
Integrates with Groq for AI-powered insights
================================================================================
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Body
from fastapi.responses import JSONResponse, StreamingResponse
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict, Any
import json
import asyncio
import logging

from comprehensive_analytics import (
    ComprehensiveAnalyticsEngine,
    UserActivityEvent,
    FeatureType,
    ActivityType,
    TimeGranularity,
    get_analytics_engine,
    ChatAnalytics,
    ProjectAnalytics,
    ImageAnalytics,
    DocumentAnalytics,
    MovieAnalytics,
    PodcastAnalytics,
    GroqInsightsGenerator,
)

logger = logging.getLogger(__name__)

# ============== ROUTER SETUP ==============

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

# Get analytics engine
def get_engine() -> ComprehensiveAnalyticsEngine:
    engine = get_analytics_engine()
    if not engine:
        raise HTTPException(status_code=500, detail="Analytics engine not initialized")
    return engine

# ============== DATA MODELS ==============

class ActivityEventRequest:
    """Request model for tracking activity"""
    feature: FeatureType
    activity: ActivityType
    resource_id: Optional[str] = None
    resource_name: Optional[str] = None
    duration_seconds: Optional[float] = None
    engagement_score: float = 0.0
    tags: List[str] = []
    metadata: Dict[str, Any] = {}


# ============== TRACKING ENDPOINTS ==============

@router.post("/track-activity")
async def track_activity(
    feature: str,
    activity: str,
    duration_seconds: Optional[float] = None,
    engagement_score: float = 0.0,
    resource_id: Optional[str] = None,
    tags: List[str] = [],
    metadata: Dict[str, Any] = {},
    engine: ComprehensiveAnalyticsEngine = Depends(get_engine),
):
    """Track a user activity"""
    try:
        # Get user ID from token (simplified - in production use proper auth)
        user_id = "user_123"  # Would come from JWT token
        
        # Create event
        event = UserActivityEvent(
            user_id=user_id,
            feature=FeatureType(feature),
            activity=ActivityType(activity),
            duration_seconds=duration_seconds,
            engagement_score=engagement_score,
            resource_id=resource_id,
            tags=tags,
            metadata=metadata,
        )
        
        # Track
        await engine.track_activity(event)
        
        return {
            "success": True,
            "event_id": event.event_id,
            "timestamp": event.timestamp.isoformat(),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid feature or activity: {str(e)}")
    except Exception as e:
        logger.error(f"Error tracking activity: {e}")
        raise HTTPException(status_code=500, detail="Failed to track activity")


@router.post("/batch-track")
async def batch_track(
    events: List[Dict[str, Any]] = Body(...),
    engine: ComprehensiveAnalyticsEngine = Depends(get_engine),
):
    """Track multiple activities in batch"""
    try:
        user_id = "user_123"  # From JWT token
        tracked_count = 0
        
        for event_data in events:
            try:
                event = UserActivityEvent(
                    user_id=user_id,
                    feature=FeatureType(event_data['feature']),
                    activity=ActivityType(event_data['activity']),
                    duration_seconds=event_data.get('duration_seconds'),
                    engagement_score=event_data.get('engagement_score', 0.0),
                    resource_id=event_data.get('resource_id'),
                    tags=event_data.get('tags', []),
                    metadata=event_data.get('metadata', {}),
                )
                await engine.track_activity(event)
                tracked_count += 1
            except Exception as e:
                logger.warning(f"Failed to track event: {e}")
        
        return {
            "success": True,
            "tracked_count": tracked_count,
            "total_count": len(events),
        }
    except Exception as e:
        logger.error(f"Error in batch tracking: {e}")
        raise HTTPException(status_code=500, detail="Batch tracking failed")


@router.post("/session/start")
async def start_session(
    feature: str,
    engine: ComprehensiveAnalyticsEngine = Depends(get_engine),
):
    """Start a tracking session"""
    try:
        import uuid
        user_id = "user_123"  # From JWT
        session_id = str(uuid.uuid4())
        
        engine.start_session(user_id, session_id, FeatureType(feature))
        
        return {
            "success": True,
            "session_id": session_id,
            "started_at": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to start session")


@router.post("/session/end/{session_id}")
async def end_session(
    session_id: str,
    engine: ComprehensiveAnalyticsEngine = Depends(get_engine),
):
    """End a tracking session"""
    try:
        session = engine.end_session(session_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {
            "success": True,
            "session": session,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to end session")


# ============== DASHBOARD ENDPOINTS ==============

@router.get("/user-profile")
async def get_user_profile(engine: ComprehensiveAnalyticsEngine = Depends(get_engine)):
    """Get user profile with all metrics"""
    try:
        user_id = "user_123"  # From JWT
        profile = engine.get_user_profile(user_id)
        
        if not profile:
            return {"error": "No profile found"}
        
        return {
            "success": True,
            "profile": profile.to_dict(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch user profile")


@router.get("/platform-dashboard")
async def get_platform_dashboard(
    time_range: str = Query("30d"),
    engine: ComprehensiveAnalyticsEngine = Depends(get_engine),
):
    """Get complete platform dashboard data"""
    try:
        user_id = "user_123"  # From JWT
        profile = engine.get_user_profile(user_id)
        
        if not profile:
            return {"error": "No profile found"}
        
        # Get all feature metrics
        feature_metrics = engine.get_feature_metrics(user_id)
        
        # Get time series data
        time_series = engine.get_time_series_data(user_id, days=30)
        
        # Get comparative analysis
        comparison = engine.get_comparative_analysis(user_id)
        
        # Calculate metrics
        total_activities = sum(m.get('total_activities', 0) for m in feature_metrics.values() if isinstance(m, dict))
        avg_engagement = profile.engagement_score
        
        # Feature distribution
        feature_distribution = [
            {
                'name': m.get('feature', 'unknown'),
                'value': m.get('total_activities', 0),
            }
            for m in feature_metrics.values() if isinstance(m, dict)
        ]
        
        return {
            "success": True,
            "profile": profile.to_dict(),
            "totalActivities": total_activities,
            "activeSessions": len(engine.active_sessions),
            "avgEngagement": avg_engagement,
            "featuresUsed": len(profile.features_used),
            "activityGrowth": comparison.get('growth_rate', 0),
            "sessionGrowth": 0,
            "engagementChange": 0,
            "featureAdoption": 0,
            "featureMetrics": feature_metrics,
            "featureDistribution": feature_distribution,
            "timeSeriesData": time_series,
            "trendData": time_series,
            "currentPeriodActivities": comparison.get('current_period', {}).get('activity_count', 0),
            "previousPeriodActivities": comparison.get('previous_period', {}).get('activity_count', 0),
            "growthRate": comparison.get('growth_rate', 0),
        }
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch dashboard")


@router.get("/feature/{feature_name}")
async def get_feature_analytics(
    feature_name: str,
    days: int = Query(30),
    engine: ComprehensiveAnalyticsEngine = Depends(get_engine),
):
    """Get detailed analytics for a specific feature"""
    try:
        user_id = "user_123"
        feature = FeatureType(feature_name)
        
        # Get metrics
        metrics = engine.get_feature_metrics(user_id, feature)
        
        # Get time series
        time_series = engine.get_time_series_data(user_id, feature, days=days)
        
        # Feature-specific analysis
        events = list(engine.user_events.get(user_id, []))
        events = [e for e in events if e.feature == feature]
        
        # Choose analyzer based on feature
        if feature == FeatureType.CHAT:
            analysis = ChatAnalytics.analyze_conversation(events)
        elif feature == FeatureType.PROJECTS:
            analysis = ProjectAnalytics.analyze_projects(events)
        elif feature == FeatureType.IMAGES:
            analysis = ImageAnalytics.analyze_images(events)
        elif feature == FeatureType.DOCUMENTS:
            analysis = DocumentAnalytics.analyze_documents(events)
        elif feature == FeatureType.MOVIES:
            analysis = MovieAnalytics.analyze_movies(events)
        elif feature == FeatureType.PODCASTS:
            analysis = PodcastAnalytics.analyze_podcasts(events)
        else:
            analysis = {}
        
        return {
            "success": True,
            "feature": feature_name,
            "metrics": metrics,
            "timeSeries": time_series,
            "analysis": analysis,
        }
    except Exception as e:
        logger.error(f"Feature analytics error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch feature analytics")


@router.get("/time-series")
async def get_time_series(
    feature: Optional[str] = None,
    granularity: str = Query("day"),
    days: int = Query(30),
    engine: ComprehensiveAnalyticsEngine = Depends(get_engine),
):
    """Get time-series analytics data"""
    try:
        user_id = "user_123"
        feature_obj = FeatureType(feature) if feature else None
        granularity_obj = TimeGranularity(granularity)
        
        data = engine.get_time_series_data(user_id, feature_obj, granularity_obj, days)
        
        return {
            "success": True,
            "data": data,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch time series")


@router.get("/insights")
async def get_insights(
    limit: int = Query(10),
    engine: ComprehensiveAnalyticsEngine = Depends(get_engine),
):
    """Get AI-powered insights"""
    try:
        user_id = "user_123"
        insights = engine.get_user_insights(user_id, limit)
        
        return {
            "success": True,
            "insights": insights,
            "count": len(insights),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch insights")


@router.post("/generate-insights")
async def generate_insights(
    engine: ComprehensiveAnalyticsEngine = Depends(get_engine),
):
    """Generate new AI insights using Groq"""
    try:
        user_id = "user_123"
        profile = engine.get_user_profile(user_id)
        
        if not profile:
            return {"error": "No profile found"}
        
        feature_metrics = engine.get_feature_metrics(user_id)
        existing_insights = engine.get_user_insights(user_id, limit=5)
        
        # Initialize Groq generator if API key available
        groq_key = "your_groq_api_key_here"  # Would come from env
        generator = GroqInsightsGenerator(groq_key)
        
        # Generate new insights
        new_insights = await generator.generate_insights(profile, feature_metrics, existing_insights)
        
        return {
            "success": True,
            "insights": new_insights,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        logger.error(f"Insight generation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate insights")


@router.get("/comparison")
async def get_comparison(
    days: int = Query(30),
    engine: ComprehensiveAnalyticsEngine = Depends(get_engine),
):
    """Get comparative analysis between periods"""
    try:
        user_id = "user_123"
        comparison = engine.get_comparative_analysis(user_id, days)
        
        return {
            "success": True,
            "comparison": comparison,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch comparison")


@router.get("/cohorts")
async def get_cohort_analysis(
    cohort_type: str = Query("signup_date"),
    engine: ComprehensiveAnalyticsEngine = Depends(get_engine),
):
    """Get cohort analysis"""
    try:
        cohorts = engine.get_cohort_analysis(cohort_type)
        
        return {
            "success": True,
            "cohorts": cohorts,
            "cohort_type": cohort_type,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch cohort analysis")


@router.get("/platform-metrics")
async def get_platform_metrics(
    engine: ComprehensiveAnalyticsEngine = Depends(get_engine),
):
    """Get platform-wide metrics"""
    try:
        metrics = engine.get_platform_analytics()
        
        return {
            "success": True,
            "metrics": metrics,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch platform metrics")


# ============== ADVANCED ANALYTICS ==============

@router.get("/anomalies")
async def detect_anomalies(
    days: int = Query(7),
    engine: ComprehensiveAnalyticsEngine = Depends(get_engine),
):
    """Detect anomalous activity patterns"""
    try:
        user_id = "user_123"
        events = list(engine.user_events.get(user_id, []))
        
        # Filter by days
        since = datetime.now(timezone.utc) - timedelta(days=days)
        events = [e for e in events if e.timestamp >= since]
        
        anomalies = []
        for event in events:
            if engine._detect_anomaly(event):
                anomalies.append({
                    "event_id": event.event_id,
                    "feature": event.feature.value,
                    "timestamp": event.timestamp.isoformat(),
                })
        
        return {
            "success": True,
            "anomalies": anomalies,
            "count": len(anomalies),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to detect anomalies")


@router.get("/churn-risk")
async def get_churn_risk(engine: ComprehensiveAnalyticsEngine = Depends(get_engine)):
    """Get churn risk prediction"""
    try:
        user_id = "user_123"
        profile = engine.get_user_profile(user_id)
        
        if not profile:
            return {"error": "No profile found"}
        
        # Calculate churn risk
        generator = GroqInsightsGenerator("key")
        churn_risk = await generator.predict_churn_risk(profile)
        
        return {
            "success": True,
            "churn_risk": churn_risk,
            "user_id": user_id,
            "risk_level": "high" if churn_risk > 70 else "medium" if churn_risk > 40 else "low",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to calculate churn risk")


@router.get("/export/{format}")
async def export_analytics(
    format: str = "json",
    engine: ComprehensiveAnalyticsEngine = Depends(get_engine),
):
    """Export analytics data"""
    try:
        user_id = "user_123"
        profile = engine.get_user_profile(user_id)
        feature_metrics = engine.get_feature_metrics(user_id)
        insights = engine.get_user_insights(user_id)
        
        if format == "json":
            data = {
                "profile": profile.to_dict() if profile else None,
                "metrics": feature_metrics,
                "insights": insights,
                "exported_at": datetime.now(timezone.utc).isoformat(),
            }
            
            return JSONResponse(data)
        
        elif format == "csv":
            # Generate CSV
            csv_content = "Feature,Activities,Engagement,SuccessRate\n"
            for feature, metrics in feature_metrics.items():
                if isinstance(metrics, dict):
                    csv_content += f"{feature},{metrics.get('total_activities', 0)},{metrics.get('avg_engagement', 0)},{metrics.get('success_rate', 0)}\n"
            
            return StreamingResponse(
                iter([csv_content]),
                media_type="text/csv",
                headers={"Content-Disposition": "attachment; filename=analytics.csv"}
            )
        
        else:
            raise HTTPException(status_code=400, detail="Unsupported format")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to export analytics")


# ============== HEALTH CHECK ==============

@router.get("/health")
async def analytics_health(engine: ComprehensiveAnalyticsEngine = Depends(get_engine)):
    """Health check for analytics engine"""
    try:
        stats = {
            "total_users": len(engine.user_profiles),
            "total_events": sum(len(events) for events in engine.user_events.values()),
            "active_sessions": len(engine.active_sessions),
            "engine_status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        
        return {
            "success": True,
            "stats": stats,
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "engine_status": "unhealthy",
        }
