"""
Streaming Analytics Engine - Real-time Dashboard for Views, Engagement, Revenue
Similar to Amagi Analytics - Production-grade analytics system
"""

from fastapi import FastAPI, WebSocket, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Set
import asyncio
import json
import logging
from collections import defaultdict, deque
import numpy as np
from enum import Enum
import uuid
from dataclasses import dataclass, field, asdict
import statistics

logger = logging.getLogger(__name__)

# ============== ENUMS ==============

class MetricType(str, Enum):
    VIEW = "view"
    ENGAGEMENT = "engagement"
    REVENUE = "revenue"
    WATCH_TIME = "watch_time"
    COMPLETION = "completion"
    INTERACTION = "interaction"

class ContentType(str, Enum):
    PODCAST = "podcast"
    VIDEO = "video"
    MUSIC = "music"
    MOVIE = "movie"
    LIVE_STREAM = "live_stream"
    STORY = "story"

class RevenueSource(str, Enum):
    SUBSCRIPTION = "subscription"
    ADS = "ads"
    PREMIUM_FEATURES = "premium_features"
    MARKETPLACE = "marketplace"
    CREATOR_FUND = "creator_fund"

# ============== DATA MODELS ==============

@dataclass
class EngagementMetrics:
    """Real-time engagement metrics"""
    likes: int = 0
    shares: int = 0
    comments: int = 0
    saves: int = 0
    clicks: int = 0
    hover_time: float = 0.0  # seconds
    scroll_depth: float = 0.0  # percentage

    def total_engagement(self) -> int:
        return self.likes + self.shares + self.comments + self.saves + self.clicks

class ViewMetric(BaseModel):
    metric_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content_id: str
    content_type: ContentType
    user_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    watch_time: float  # seconds
    completion_rate: float  # 0-100%
    device_type: str  # mobile, desktop, tablet
    geo_location: str  # country code
    session_id: str
    engagement: EngagementMetrics = Field(default_factory=EngagementMetrics)
    quality: str = "1080p"  # video quality

class RevenueMetric(BaseModel):
    metric_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content_id: str
    creator_id: str
    source: RevenueSource
    amount: float
    currency: str = "USD"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    user_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class AggregatedMetrics(BaseModel):
    """Real-time aggregated metrics for dashboard"""
    period: str  # "1m", "5m", "15m", "1h"
    content_id: str
    views: int
    unique_viewers: int
    total_watch_time: float
    avg_watch_time: float
    completion_rate: float
    engagement_score: float  # weighted engagement
    total_engagement: int
    revenue: float
    revenue_per_view: float
    top_geographies: List[tuple]  # [(country, count), ...]
    top_devices: List[tuple]
    engagement_breakdown: Dict[str, int]  # likes, shares, comments, etc.
    revenue_breakdown: Dict[str, float]  # by source

@dataclass
class LiveDashboardData:
    """Real-time dashboard data structure"""
    timestamp: datetime
    total_views: int = 0
    total_unique_viewers: int = 0
    total_watch_time: float = 0.0
    avg_engagement_score: float = 0.0
    total_revenue: float = 0.0
    active_sessions: int = 0
    trending_content: List[Dict] = field(default_factory=list)
    top_creators: List[Dict] = field(default_factory=list)
    geo_heatmap: Dict[str, int] = field(default_factory=dict)
    revenue_sources: Dict[str, float] = field(default_factory=dict)
    engagement_trends: List[float] = field(default_factory=list)

# ============== STREAMING ANALYTICS ENGINE ==============

class StreamingAnalyticsEngine:
    """Real-time analytics engine with sub-second latency"""
    
    def __init__(self, buffer_size: int = 10000):
        self.buffer_size = buffer_size
        
        # Real-time buffers (circular)
        self.view_buffer: deque = deque(maxlen=buffer_size)
        self.revenue_buffer: deque = deque(maxlen=buffer_size)
        
        # Aggregated metrics by time window
        self.minute_metrics: Dict[str, Dict] = defaultdict(dict)
        self.hour_metrics: Dict[str, Dict] = defaultdict(dict)
        self.day_metrics: Dict[str, Dict] = defaultdict(dict)
        
        # Content-specific tracking
        self.content_views: Dict[str, List[ViewMetric]] = defaultdict(list)
        self.content_engagement: Dict[str, EngagementMetrics] = defaultdict(EngagementMetrics)
        self.content_revenue: Dict[str, float] = defaultdict(float)
        
        # User activity tracking
        self.active_sessions: Set[str] = set()
        self.user_engagement_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        # Real-time counters
        self.total_views = 0
        self.total_revenue = 0.0
        self.unique_viewers: Set[str] = set()
        
        # Trending algorithm
        self.content_momentum: Dict[str, float] = defaultdict(float)
        self.creator_momentum: Dict[str, float] = defaultdict(float)
        
        logger.info("✅ Streaming Analytics Engine initialized")

    async def process_view_metric(self, metric: ViewMetric) -> None:
        """Process incoming view metric with real-time aggregation"""
        try:
            # Add to buffer
            self.view_buffer.append(metric)
            
            # Update counters
            self.total_views += 1
            self.unique_viewers.add(metric.user_id)
            self.active_sessions.add(metric.session_id)
            
            # Track content-specific metrics
            self.content_views[metric.content_id].append(metric)
            self.user_engagement_history[metric.user_id].append({
                'content_id': metric.content_id,
                'engagement': metric.engagement.total_engagement(),
                'timestamp': metric.timestamp
            })
            
            # Update engagement metrics
            self.content_engagement[metric.content_id].likes += metric.engagement.likes
            self.content_engagement[metric.content_id].shares += metric.engagement.shares
            self.content_engagement[metric.content_id].comments += metric.engagement.comments
            self.content_engagement[metric.content_id].saves += metric.engagement.saves
            
            # Update momentum (trending algorithm)
            engagement_weight = metric.engagement.total_engagement()
            completion_weight = metric.completion_rate / 100
            momentum_increase = (engagement_weight * 0.6) + (completion_weight * 0.4)
            self.content_momentum[metric.content_id] += momentum_increase
            
            logger.debug(f"Processed view: {metric.content_id} from {metric.user_id}")
            
        except Exception as e:
            logger.error(f"Error processing view metric: {e}")
            raise

    async def process_revenue_metric(self, metric: RevenueMetric) -> None:
        """Process revenue metrics with real-time tracking"""
        try:
            self.revenue_buffer.append(metric)
            self.total_revenue += metric.amount
            self.content_revenue[metric.content_id] += metric.amount
            
            logger.debug(f"Revenue: ${metric.amount} for {metric.content_id}")
            
        except Exception as e:
            logger.error(f"Error processing revenue metric: {e}")
            raise

    def get_content_metrics(self, content_id: str) -> AggregatedMetrics:
        """Get real-time aggregated metrics for specific content"""
        views = self.content_views.get(content_id, [])
        
        if not views:
            return AggregatedMetrics(
                period="1m",
                content_id=content_id,
                views=0,
                unique_viewers=0,
                total_watch_time=0,
                avg_watch_time=0,
                completion_rate=0,
                engagement_score=0,
                total_engagement=0,
                revenue=0,
                revenue_per_view=0,
                top_geographies=[],
                top_devices=[],
                engagement_breakdown={},
                revenue_breakdown={}
            )
        
        # Calculate metrics
        unique_viewers = len(set(v.user_id for v in views))
        total_watch_time = sum(v.watch_time for v in views)
        avg_watch_time = total_watch_time / len(views) if views else 0
        completion_rate = statistics.mean(v.completion_rate for v in views) if views else 0
        
        engagement = self.content_engagement.get(content_id, EngagementMetrics())
        total_engagement = engagement.total_engagement()
        
        # Engagement score: weighted combination
        engagement_score = (
            (engagement.likes * 1.5) +
            (engagement.shares * 3.0) +
            (engagement.comments * 2.0) +
            (engagement.saves * 2.5) +
            (engagement.clicks * 0.5)
        ) / max(len(views), 1)
        
        # Geographic distribution
        geo_count = defaultdict(int)
        device_count = defaultdict(int)
        for v in views:
            geo_count[v.geo_location] += 1
            device_count[v.device_type] += 1
        
        top_geographies = sorted(geo_count.items(), key=lambda x: x[1], reverse=True)[:10]
        top_devices = sorted(device_count.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Revenue metrics
        revenue = self.content_revenue.get(content_id, 0)
        revenue_per_view = revenue / len(views) if views else 0
        
        engagement_breakdown = {
            'likes': engagement.likes,
            'shares': engagement.shares,
            'comments': engagement.comments,
            'saves': engagement.saves,
            'clicks': engagement.clicks
        }
        
        return AggregatedMetrics(
            period="1m",
            content_id=content_id,
            views=len(views),
            unique_viewers=unique_viewers,
            total_watch_time=total_watch_time,
            avg_watch_time=avg_watch_time,
            completion_rate=completion_rate,
            engagement_score=engagement_score,
            total_engagement=total_engagement,
            revenue=revenue,
            revenue_per_view=revenue_per_view,
            top_geographies=top_geographies,
            top_devices=top_devices,
            engagement_breakdown=engagement_breakdown,
            revenue_breakdown={'total': revenue}
        )

    def get_trending_content(self, limit: int = 10) -> List[Dict]:
        """Get trending content based on real-time momentum"""
        trending = sorted(
            self.content_momentum.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]
        
        result = []
        for content_id, momentum in trending:
            metrics = self.get_content_metrics(content_id)
            result.append({
                'content_id': content_id,
                'views': metrics.views,
                'engagement_score': metrics.engagement_score,
                'momentum': momentum,
                'revenue': metrics.revenue
            })
        
        return result

    def get_dashboard_snapshot(self) -> LiveDashboardData:
        """Get complete dashboard snapshot"""
        # Calculate aggregates
        total_watch_time = sum(v.watch_time for v in self.view_buffer)
        
        # Top creators by revenue
        creator_revenue = defaultdict(float)
        for metric in self.revenue_buffer:
            creator_revenue[metric.creator_id] += metric.amount
        
        top_creators = sorted(
            creator_revenue.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        # Geographic heatmap
        geo_heatmap = defaultdict(int)
        for view in self.view_buffer:
            geo_heatmap[view.geo_location] += 1
        
        # Revenue sources breakdown
        revenue_sources = defaultdict(float)
        for metric in self.revenue_buffer:
            revenue_sources[metric.source.value] += metric.amount
        
        # Engagement trends (last 100 entries)
        engagement_trends = []
        for view in list(self.view_buffer)[-100:]:
            engagement_trends.append(view.engagement.total_engagement())
        
        return LiveDashboardData(
            timestamp=datetime.now(timezone.utc),
            total_views=self.total_views,
            total_unique_viewers=len(self.unique_viewers),
            total_watch_time=total_watch_time,
            avg_engagement_score=statistics.mean(engagement_trends) if engagement_trends else 0,
            total_revenue=self.total_revenue,
            active_sessions=len(self.active_sessions),
            trending_content=self.get_trending_content(5),
            top_creators=[
                {'creator_id': cid, 'revenue': rev}
                for cid, rev in top_creators
            ],
            geo_heatmap=dict(geo_heatmap),
            revenue_sources=dict(revenue_sources),
            engagement_trends=engagement_trends
        )

    def get_creator_analytics(self, creator_id: str) -> Dict:
        """Get detailed analytics for a specific creator"""
        creator_revenue = sum(
            m.amount for m in self.revenue_buffer
            if m.creator_id == creator_id
        )
        
        # Find content created by this creator
        creator_content = defaultdict(list)
        for content_id, views in self.content_views.items():
            # In real scenario, content would have creator_id field
            creator_content[content_id] = views
        
        metrics_list = [
            self.get_content_metrics(cid)
            for cid in creator_content.keys()
        ]
        
        total_views = sum(m.views for m in metrics_list)
        total_engagement = sum(m.total_engagement for m in metrics_list)
        avg_completion = statistics.mean(m.completion_rate for m in metrics_list) if metrics_list else 0
        
        return {
            'creator_id': creator_id,
            'total_revenue': creator_revenue,
            'total_views': total_views,
            'total_engagement': total_engagement,
            'avg_completion_rate': avg_completion,
            'content_count': len(creator_content),
            'top_content': self.get_trending_content(limit=5)
        }

    def cleanup_old_sessions(self) -> None:
        """Clean up inactive sessions"""
        # In production, track session timestamps and remove old ones
        if len(self.active_sessions) > 100000:
            self.active_sessions.clear()

# ============== WEBSOCKET CONNECTION MANAGER ==============

class AnalyticsConnectionManager:
    """Manage WebSocket connections for real-time dashboard updates"""
    
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = defaultdict(list)
        self.subscription_filters: Dict[WebSocket, Dict[str, Any]] = {}

    async def connect(self, websocket: WebSocket, client_id: str, filters: Optional[Dict] = None):
        await websocket.accept()
        self.active_connections[client_id].append(websocket)
        self.subscription_filters[websocket] = filters or {}
        logger.info(f"Analytics client connected: {client_id}")

    async def disconnect(self, websocket: WebSocket, client_id: str):
        self.active_connections[client_id].remove(websocket)
        self.subscription_filters.pop(websocket, None)
        logger.info(f"Analytics client disconnected: {client_id}")

    async def broadcast_update(self, message: Dict, content_id: Optional[str] = None):
        """Broadcast update to all connected clients"""
        for client_connections in self.active_connections.values():
            for connection in client_connections:
                try:
                    # Check filters
                    filters = self.subscription_filters.get(connection, {})
                    if content_id and filters.get('content_id') and filters['content_id'] != content_id:
                        continue
                    
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error broadcasting update: {e}")

    async def send_personal_message(self, message: Dict, websocket: WebSocket):
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")

# ============== PREDICTIVE ANALYTICS ==============

class PredictiveAnalytics:
    """Predictive analytics for content performance"""
    
    def __init__(self, engine: StreamingAnalyticsEngine):
        self.engine = engine

    def predict_completion_rate(self, content_id: str, user_profile: Dict) -> float:
        """Predict completion rate for a user"""
        views = self.engine.content_views.get(content_id, [])
        
        if not views:
            return 0.5  # Default prediction
        
        # Calculate based on content type and user history
        avg_completion = statistics.mean(v.completion_rate for v in views)
        
        # Adjust based on device type
        device_adjust = 1.0
        if user_profile.get('device_type') == 'mobile':
            device_adjust = 0.85
        
        predicted = avg_completion * device_adjust / 100
        return min(max(predicted, 0), 1)

    def predict_revenue(self, content_id: str) -> float:
        """Predict revenue for content"""
        metrics = self.engine.get_content_metrics(content_id)
        
        # Simple prediction: engagement score * conversion rate
        base_conversion = 0.05  # 5% of views convert
        predicted_revenue = metrics.views * base_conversion * metrics.engagement_score
        
        return predicted_revenue

    def identify_drop_points(self, content_id: str) -> List[Dict]:
        """Identify where viewers are dropping off"""
        views = self.engine.content_views.get(content_id, [])
        
        # Group by completion rate ranges
        drop_points = defaultdict(int)
        for view in views:
            bucket = int(view.completion_rate / 10) * 10
            drop_points[bucket] += 1
        
        # Find significant drops
        results = []
        prev_count = 0
        for bucket in sorted(drop_points.keys()):
            count = drop_points[bucket]
            if prev_count and count < prev_count * 0.7:  # 30% drop
                results.append({
                    'dropout_point': f"{bucket}%",
                    'viewers_dropped': prev_count - count,
                    'retention_rate': count / prev_count if prev_count else 0
                })
            prev_count = count
        
        return results

# ============== GLOBAL INSTANCES ==============

analytics_engine = StreamingAnalyticsEngine()
analytics_manager = AnalyticsConnectionManager()
predictive_analytics = PredictiveAnalytics(analytics_engine)

# ============== API ENDPOINTS ==============

async def get_dashboard(content_id: Optional[str] = None):
    """Get real-time dashboard data"""
    if content_id:
        return analytics_engine.get_content_metrics(content_id)
    return asdict(analytics_engine.get_dashboard_snapshot())

async def get_trending_content(limit: int = 10):
    """Get trending content"""
    return analytics_engine.get_trending_content(limit)

async def get_creator_analytics(creator_id: str):
    """Get creator-specific analytics"""
    return analytics_engine.get_creator_analytics(creator_id)

async def get_revenue_analytics(period: str = "1h"):
    """Get revenue analytics"""
    recent_revenue = list(analytics_engine.revenue_buffer)[-1000:]
    
    total = sum(r.amount for r in recent_revenue)
    by_source = defaultdict(float)
    by_creator = defaultdict(float)
    
    for metric in recent_revenue:
        by_source[metric.source.value] += metric.amount
        by_creator[metric.creator_id] += metric.amount
    
    return {
        'period': period,
        'total_revenue': total,
        'by_source': dict(by_source),
        'top_creators': sorted(by_creator.items(), key=lambda x: x[1], reverse=True)[:10]
    }

async def get_engagement_analytics(content_id: Optional[str] = None):
    """Get engagement analytics"""
    if content_id:
        metrics = analytics_engine.get_content_metrics(content_id)
        return {
            'content_id': content_id,
            'engagement_breakdown': metrics.engagement_breakdown,
            'engagement_score': metrics.engagement_score,
            'total_engagement': metrics.total_engagement
        }
    
    # Global engagement
    all_views = list(analytics_engine.view_buffer)
    total_eng = sum(v.engagement.total_engagement() for v in all_views)
    
    return {
        'global_engagement_score': total_eng / max(len(all_views), 1),
        'total_interactions': total_eng,
        'avg_completion_rate': statistics.mean(v.completion_rate for v in all_views) if all_views else 0
    }

async def get_geographic_insights():
    """Get geographic insights"""
    dashboard = analytics_engine.get_dashboard_snapshot()
    
    return {
        'heatmap': dashboard.geo_heatmap,
        'top_countries': sorted(dashboard.geo_heatmap.items(), key=lambda x: x[1], reverse=True)[:10]
    }

async def predict_performance(content_id: str, user_profile: Dict):
    """Predict content performance"""
    completion = predictive_analytics.predict_completion_rate(content_id, user_profile)
    revenue = predictive_analytics.predict_revenue(content_id)
    dropouts = predictive_analytics.identify_drop_points(content_id)
    
    return {
        'predicted_completion_rate': completion,
        'predicted_revenue': revenue,
        'dropout_analysis': dropouts
    }
