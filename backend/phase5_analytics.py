"""
PHASE 5: ADVANCED ANALYTICS & INSIGHTS
Real-time analytics, dashboards, and business intelligence
Production-ready enterprise analytics platform
"""

import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class MetricType(str, Enum):
    """Analytics metric types"""
    VIEWS = "views"
    ENGAGEMENT = "engagement"
    RETENTION = "retention"
    REVENUE = "revenue"
    USER_GROWTH = "user_growth"
    CONVERSION = "conversion"
    PERFORMANCE = "performance"
    QUALITY = "quality"


@dataclass
class AnalyticsEvent:
    """Analytics event data"""
    event_type: str
    user_id: str
    video_id: Optional[str] = None
    timestamp: datetime = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
        if self.metadata is None:
            self.metadata = {}


@dataclass
class MetricAggregate:
    """Aggregated metric data"""
    metric_type: MetricType
    period_start: datetime
    period_end: datetime
    value: float
    change_percent: float = 0.0
    comparision_value: Optional[float] = None
    metadata: Dict[str, Any] = None


class RealTimeAnalyticsCollector:
    """Collects and aggregates real-time analytics"""
    
    def __init__(self, db, redis_client):
        self.db = db
        self.redis = redis_client
        self.event_buffer = []
        self.buffer_size = 100
        
    async def track_event(self, event: AnalyticsEvent):
        """Track analytics event"""
        try:
            # Add to buffer
            self.event_buffer.append(event)
            
            # Redis real-time counter
            counter_key = f"analytics:counter:{event.event_type}"
            await self.redis.incr(counter_key)
            await self.redis.expire(counter_key, 86400)  # 24h TTL
            
            # User activity tracking
            user_key = f"analytics:user:{event.user_id}:activity"
            await self.redis.incr(user_key)
            await self.redis.expire(user_key, 2592000)  # 30d TTL
            
            # Video engagement tracking
            if event.video_id:
                video_key = f"analytics:video:{event.video_id}:engagement"
                await self.redis.incr(video_key)
                await self.redis.expire(video_key, 2592000)  # 30d TTL
            
            # Flush to DB if buffer full
            if len(self.event_buffer) >= self.buffer_size:
                await self.flush_events()
                
        except Exception as e:
            logger.error(f"Event tracking error: {e}")
    
    async def flush_events(self):
        """Flush buffered events to database"""
        if not self.event_buffer or not self.db:
            return
        
        try:
            events_data = [asdict(e) for e in self.event_buffer]
            result = await self.db.analytics_events.insert_many(events_data)
            logger.info(f"Flushed {len(result.inserted_ids)} analytics events")
            self.event_buffer = []
        except Exception as e:
            logger.error(f"Event flush error: {e}")
    
    async def get_metrics(
        self,
        metric_type: MetricType,
        period_days: int = 7,
        granularity: str = "hourly"
    ) -> List[MetricAggregate]:
        """Get aggregated metrics"""
        try:
            now = datetime.utcnow()
            start_time = now - timedelta(days=period_days)
            
            # Query from MongoDB
            pipeline = [
                {"$match": {"timestamp": {"$gte": start_time, "$lte": now}}},
                {
                    "$group": {
                        "_id": {
                            "$dateToString": {
                                "format": "%Y-%m-%d" if granularity == "daily" else "%Y-%m-%d %H:00:00",
                                "date": "$timestamp"
                            }
                        },
                        "count": {"$sum": 1},
                        "value": {"$avg": "$value"} if "value" in ["$metadata"] else {"$sum": 1}
                    }
                },
                {"$sort": {"_id": 1}}
            ]
            
            results = await self.db.analytics_events.aggregate(pipeline).to_list(None)
            
            metrics = []
            for i, result in enumerate(results):
                prev_value = results[i - 1]["value"] if i > 0 else result["value"]
                change_percent = ((result["value"] - prev_value) / prev_value * 100) if prev_value > 0 else 0
                
                metrics.append(MetricAggregate(
                    metric_type=metric_type,
                    period_start=start_time,
                    period_end=now,
                    value=result["value"],
                    change_percent=change_percent,
                    comparision_value=prev_value
                ))
            
            return metrics
        except Exception as e:
            logger.error(f"Get metrics error: {e}")
            return []


class UserSegmentation:
    """Segments users based on behavior"""
    
    def __init__(self, db, redis_client):
        self.db = db
        self.redis = redis_client
    
    async def segment_users(self) -> Dict[str, List[str]]:
        """Segment users by engagement level"""
        try:
            segments = {
                "highly_active": [],      # 10+ interactions/day
                "active": [],             # 3-9 interactions/day
                "moderate": [],           # 1-2 interactions/day
                "inactive": [],           # 0 interactions last 7 days
                "dormant": []             # 0 interactions last 30 days
            }
            
            if not self.db:
                return segments
            
            # Get user activity counts
            pipeline = [
                {
                    "$match": {
                        "timestamp": {"$gte": datetime.utcnow() - timedelta(days=30)}
                    }
                },
                {
                    "$group": {
                        "_id": "$user_id",
                        "count": {"$sum": 1},
                        "last_activity": {"$max": "$timestamp"}
                    }
                },
                {"$sort": {"count": -1}}
            ]
            
            users = await self.db.analytics_events.aggregate(pipeline).to_list(None)
            
            for user in users:
                user_id = user["_id"]
                count = user["count"]
                last_activity = user.get("last_activity")
                
                days_since_activity = (datetime.utcnow() - last_activity).days if last_activity else 30
                
                if days_since_activity > 30:
                    segments["dormant"].append(user_id)
                elif days_since_activity > 7:
                    segments["inactive"].append(user_id)
                elif count >= 10:
                    segments["highly_active"].append(user_id)
                elif count >= 3:
                    segments["active"].append(user_id)
                else:
                    segments["moderate"].append(user_id)
            
            # Cache segments in Redis
            cache_key = "analytics:segments"
            await self.redis.setex(cache_key, 3600, str(segments))
            
            return segments
        except Exception as e:
            logger.error(f"User segmentation error: {e}")
            return {}
    
    async def get_segment_metrics(self, segment: str) -> Dict[str, Any]:
        """Get metrics for user segment"""
        try:
            segments = await self.segment_users()
            segment_users = segments.get(segment, [])
            
            if not segment_users or not self.db:
                return {}
            
            pipeline = [
                {"$match": {"user_id": {"$in": segment_users}}},
                {
                    "$group": {
                        "_id": None,
                        "total_events": {"$sum": 1},
                        "avg_events_per_user": {"$avg": 1},
                        "total_users": {"$sum": 1}
                    }
                }
            ]
            
            result = await self.db.analytics_events.aggregate(pipeline).to_list(1)
            
            if result:
                return result[0]
            return {}
        except Exception as e:
            logger.error(f"Segment metrics error: {e}")
            return {}


class CohortAnalysis:
    """Analyzes user cohorts over time"""
    
    def __init__(self, db):
        self.db = db
    
    async def create_cohort(self, cohort_name: str, start_date: datetime, user_ids: List[str]):
        """Create a user cohort"""
        try:
            if not self.db:
                return None
            
            cohort = {
                "name": cohort_name,
                "start_date": start_date,
                "user_ids": user_ids,
                "created_at": datetime.utcnow(),
                "size": len(user_ids)
            }
            
            result = await self.db.cohorts.insert_one(cohort)
            logger.info(f"Cohort created: {cohort_name} ({len(user_ids)} users)")
            return result.inserted_id
        except Exception as e:
            logger.error(f"Cohort creation error: {e}")
            return None
    
    async def get_cohort_retention(self, cohort_id: str) -> Dict[int, float]:
        """Get cohort retention rates"""
        try:
            if not self.db:
                return {}
            
            cohort = await self.db.cohorts.find_one({"_id": cohort_id})
            if not cohort:
                return {}
            
            retention = {}
            start_date = cohort["start_date"]
            user_ids = cohort["user_ids"]
            
            for week in range(0, 13):  # 13 weeks
                week_start = start_date + timedelta(weeks=week)
                week_end = week_start + timedelta(weeks=1)
                
                # Count active users in this week
                active_count = await self.db.analytics_events.count_documents({
                    "user_id": {"$in": user_ids},
                    "timestamp": {"$gte": week_start, "$lt": week_end}
                })
                
                retention_rate = (active_count / len(user_ids)) * 100 if user_ids else 0
                retention[week] = retention_rate
            
            return retention
        except Exception as e:
            logger.error(f"Cohort retention error: {e}")
            return {}


class FunnelAnalysis:
    """Analyzes user funnels"""
    
    def __init__(self, db):
        self.db = db
    
    async def track_funnel_step(
        self,
        funnel_name: str,
        user_id: str,
        step: int,
        timestamp: datetime = None
    ):
        """Track funnel step"""
        try:
            if not self.db:
                return
            
            if timestamp is None:
                timestamp = datetime.utcnow()
            
            funnel_event = {
                "funnel": funnel_name,
                "user_id": user_id,
                "step": step,
                "timestamp": timestamp
            }
            
            await self.db.funnel_events.insert_one(funnel_event)
        except Exception as e:
            logger.error(f"Funnel tracking error: {e}")
    
    async def analyze_funnel(self, funnel_name: str, steps: List[str]) -> Dict[str, Any]:
        """Analyze funnel conversion rates"""
        try:
            if not self.db:
                return {}
            
            funnel_data = {
                "name": funnel_name,
                "steps": steps,
                "conversion_rates": {}
            }
            
            for i, step in enumerate(steps):
                # Count users who reached this step
                step_users = await self.db.funnel_events.count_documents({
                    "funnel": funnel_name,
                    "step": i
                })
                
                if i == 0:
                    funnel_data["total_entered"] = step_users
                    funnel_data["conversion_rates"][step] = 100.0
                else:
                    prev_step_users = await self.db.funnel_events.count_documents({
                        "funnel": funnel_name,
                        "step": i - 1
                    })
                    
                    conversion_rate = (step_users / prev_step_users * 100) if prev_step_users > 0 else 0
                    funnel_data["conversion_rates"][step] = conversion_rate
            
            return funnel_data
        except Exception as e:
            logger.error(f"Funnel analysis error: {e}")
            return {}


class DashboardGenerator:
    """Generates analytics dashboards"""
    
    def __init__(self, db, redis_client):
        self.db = db
        self.redis = redis_client
        self.collector = RealTimeAnalyticsCollector(db, redis_client)
        self.segmentation = UserSegmentation(db, redis_client)
        self.cohort = CohortAnalysis(db)
        self.funnel = FunnelAnalysis(db)
    
    async def generate_executive_dashboard(self) -> Dict[str, Any]:
        """Generate executive summary dashboard"""
        try:
            dashboard = {
                "generated_at": datetime.utcnow().isoformat(),
                "summary": {},
                "metrics": {},
                "segments": {},
                "trends": {}
            }
            
            # Key metrics
            if self.redis:
                total_views = await self.redis.get("analytics:counter:views") or "0"
                total_engagements = await self.redis.get("analytics:counter:engagement") or "0"
                
                dashboard["summary"]["total_views"] = int(total_views)
                dashboard["summary"]["total_engagements"] = int(total_engagements)
            
            # User segments
            segments = await self.segmentation.segment_users()
            dashboard["segments"]["highly_active"] = len(segments.get("highly_active", []))
            dashboard["segments"]["active"] = len(segments.get("active", []))
            dashboard["segments"]["inactive"] = len(segments.get("inactive", []))
            
            # Metrics
            metrics = await self.collector.get_metrics(MetricType.VIEWS, period_days=7)
            dashboard["metrics"]["views_7d"] = [
                {
                    "period": m.period_start.isoformat(),
                    "value": m.value,
                    "change": m.change_percent
                }
                for m in metrics
            ]
            
            return dashboard
        except Exception as e:
            logger.error(f"Dashboard generation error: {e}")
            return {}
    
    async def generate_creator_dashboard(self, creator_id: str) -> Dict[str, Any]:
        """Generate creator-specific dashboard"""
        try:
            if not self.db:
                return {}
            
            dashboard = {
                "creator_id": creator_id,
                "generated_at": datetime.utcnow().isoformat(),
                "videos": [],
                "top_videos": [],
                "growth": {}
            }
            
            # Get creator videos
            videos = await self.db.videos.find({"creator_id": creator_id}).to_list(None)
            
            for video in videos:
                video_id = str(video["_id"])
                
                # Get video stats
                views = await self.redis.get(f"analytics:video:{video_id}:views") or "0"
                engagements = await self.redis.get(f"analytics:video:{video_id}:engagement") or "0"
                
                video_stats = {
                    "video_id": video_id,
                    "title": video.get("title"),
                    "views": int(views),
                    "engagements": int(engagements),
                    "engagement_rate": float(int(engagements)) / (float(int(views)) * 100) if int(views) > 0 else 0
                }
                
                dashboard["videos"].append(video_stats)
            
            # Top videos
            dashboard["top_videos"] = sorted(
                dashboard["videos"],
                key=lambda v: v["views"],
                reverse=True
            )[:10]
            
            return dashboard
        except Exception as e:
            logger.error(f"Creator dashboard error: {e}")
            return {}


class Phase5AnalyticsIntegration:
    """Master analytics integrator for Phase 5"""
    
    def __init__(self):
        self.db = None
        self.redis = None
        self.collector = None
        self.segmentation = None
        self.cohort = None
        self.funnel = None
        self.dashboard = None
    
    async def initialize(self, db, redis_client):
        """Initialize analytics infrastructure"""
        try:
            self.db = db
            self.redis = redis_client
            
            self.collector = RealTimeAnalyticsCollector(db, redis_client)
            self.segmentation = UserSegmentation(db, redis_client)
            self.cohort = CohortAnalysis(db)
            self.funnel = FunnelAnalysis(db)
            self.dashboard = DashboardGenerator(db, redis_client)
            
            logger.info("✅ Phase 5 Analytics initialized")
            return True
        except Exception as e:
            logger.error(f"Analytics initialization error: {e}")
            return False
    
    async def shutdown(self):
        """Shutdown analytics"""
        try:
            if self.collector:
                await self.collector.flush_events()
            logger.info("✅ Phase 5 Analytics shutdown complete")
        except Exception as e:
            logger.error(f"Analytics shutdown error: {e}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for analytics"""
        return {
            "status": "healthy",
            "components": {
                "collector": bool(self.collector),
                "segmentation": bool(self.segmentation),
                "cohort": bool(self.cohort),
                "funnel": bool(self.funnel),
                "dashboard": bool(self.dashboard)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
