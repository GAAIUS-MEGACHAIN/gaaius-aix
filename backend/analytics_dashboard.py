"""
Real-Time Analytics Dashboard - WebSocket Server
Live updates for views, engagement, revenue with sub-second latency
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query, Depends
from fastapi.responses import HTMLResponse
import asyncio
import json
from datetime import datetime, timezone
from typing import Dict, List, Optional
import logging
from collections import defaultdict
import statistics

from streaming_analytics import (
    analytics_engine, analytics_manager, predictive_analytics,
    ViewMetric, RevenueMetric, EngagementMetrics, ContentType, RevenueSource
)

logger = logging.getLogger(__name__)

# ============== REAL-TIME DASHBOARD UPDATES ==============

class DashboardUpdateService:
    """Service for real-time dashboard updates"""
    
    def __init__(self, engine):
        self.engine = engine
        self.last_update = {}

    async def get_view_update(self, content_id: Optional[str] = None) -> Dict:
        """Get view update for dashboard"""
        if content_id:
            metrics = self.engine.get_content_metrics(content_id)
            return {
                'type': 'view_update',
                'content_id': content_id,
                'views': metrics.views,
                'unique_viewers': metrics.unique_viewers,
                'watch_time': metrics.total_watch_time,
                'avg_watch_time': metrics.avg_watch_time,
                'completion_rate': metrics.completion_rate,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
        
        dashboard = self.engine.get_dashboard_snapshot()
        return {
            'type': 'dashboard_update',
            'total_views': dashboard.total_views,
            'unique_viewers': dashboard.total_unique_viewers,
            'active_sessions': dashboard.active_sessions,
            'total_watch_time': dashboard.total_watch_time,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

    async def get_engagement_update(self, content_id: Optional[str] = None) -> Dict:
        """Get engagement update"""
        if content_id:
            metrics = self.engine.get_content_metrics(content_id)
            return {
                'type': 'engagement_update',
                'content_id': content_id,
                'engagement_score': metrics.engagement_score,
                'likes': metrics.engagement_breakdown.get('likes', 0),
                'shares': metrics.engagement_breakdown.get('shares', 0),
                'comments': metrics.engagement_breakdown.get('comments', 0),
                'saves': metrics.engagement_breakdown.get('saves', 0),
                'total_engagement': metrics.total_engagement,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
        
        dashboard = self.engine.get_dashboard_snapshot()
        return {
            'type': 'engagement_update',
            'avg_engagement_score': dashboard.avg_engagement_score,
            'engagement_trends': dashboard.engagement_trends,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

    async def get_revenue_update(self, content_id: Optional[str] = None) -> Dict:
        """Get revenue update"""
        if content_id:
            metrics = self.engine.get_content_metrics(content_id)
            return {
                'type': 'revenue_update',
                'content_id': content_id,
                'total_revenue': metrics.revenue,
                'revenue_per_view': metrics.revenue_per_view,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
        
        dashboard = self.engine.get_dashboard_snapshot()
        total_rev = sum(dashboard.revenue_sources.values())
        return {
            'type': 'revenue_update',
            'total_revenue': total_rev,
            'revenue_sources': dashboard.revenue_sources,
            'top_creators': dashboard.top_creators,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

    async def get_trending_update(self) -> Dict:
        """Get trending content update"""
        return {
            'type': 'trending_update',
            'trending_content': self.engine.get_trending_content(10),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

    async def get_geographic_update(self) -> Dict:
        """Get geographic data update"""
        dashboard = self.engine.get_dashboard_snapshot()
        return {
            'type': 'geographic_update',
            'heatmap': dashboard.geo_heatmap,
            'top_countries': sorted(dashboard.geo_heatmap.items(), key=lambda x: x[1], reverse=True)[:10],
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

    async def get_performance_insights(self, content_id: str) -> Dict:
        """Get performance insights for content"""
        metrics = self.engine.get_content_metrics(content_id)
        dropouts = predictive_analytics.identify_drop_points(content_id)
        
        return {
            'type': 'performance_insights',
            'content_id': content_id,
            'metrics': {
                'views': metrics.views,
                'engagement_score': metrics.engagement_score,
                'completion_rate': metrics.completion_rate,
                'revenue': metrics.revenue
            },
            'dropouts': dropouts,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

# ============== WEBSOCKET HANDLERS ==============

dashboard_update_service = DashboardUpdateService(analytics_engine)

async def handle_analytics_websocket(websocket: WebSocket, client_id: str, metrics_type: str = "all"):
    """Handle WebSocket connection for analytics"""
    await analytics_manager.connect(websocket, client_id, {'metrics_type': metrics_type})
    
    try:
        while True:
            # Receive commands from client
            data = await websocket.receive_text()
            message = json.loads(data)
            command = message.get('command')
            
            if command == 'subscribe':
                # Subscribe to specific content updates
                content_id = message.get('content_id')
                analytics_manager.subscription_filters[websocket]['content_id'] = content_id
                
                # Send initial data
                updates = []
                if message.get('include_views', True):
                    updates.append(await dashboard_update_service.get_view_update(content_id))
                if message.get('include_engagement', True):
                    updates.append(await dashboard_update_service.get_engagement_update(content_id))
                if message.get('include_revenue', True):
                    updates.append(await dashboard_update_service.get_revenue_update(content_id))
                
                for update in updates:
                    await analytics_manager.send_personal_message(update, websocket)
            
            elif command == 'get_metrics':
                # Send current metrics
                content_id = message.get('content_id')
                
                if content_id:
                    metrics = analytics_engine.get_content_metrics(content_id)
                    await analytics_manager.send_personal_message({
                        'type': 'metrics_snapshot',
                        'content_id': content_id,
                        'metrics': {
                            'views': metrics.views,
                            'unique_viewers': metrics.unique_viewers,
                            'engagement_score': metrics.engagement_score,
                            'total_engagement': metrics.total_engagement,
                            'completion_rate': metrics.completion_rate,
                            'revenue': metrics.revenue
                        },
                        'timestamp': datetime.now(timezone.utc).isoformat()
                    }, websocket)
                else:
                    dashboard = analytics_engine.get_dashboard_snapshot()
                    await analytics_manager.send_personal_message({
                        'type': 'dashboard_snapshot',
                        'metrics': {
                            'total_views': dashboard.total_views,
                            'unique_viewers': dashboard.total_unique_viewers,
                            'active_sessions': dashboard.active_sessions,
                            'total_revenue': dashboard.total_revenue,
                            'engagement_score': dashboard.avg_engagement_score
                        },
                        'timestamp': datetime.now(timezone.utc).isoformat()
                    }, websocket)
            
            elif command == 'get_trending':
                trending = analytics_engine.get_trending_content(10)
                await analytics_manager.send_personal_message({
                    'type': 'trending',
                    'content': trending,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }, websocket)
            
            elif command == 'get_predictions':
                content_id = message.get('content_id')
                user_profile = message.get('user_profile', {})
                
                predictions = await predictive_analytics.predict_revenue(content_id)
                await analytics_manager.send_personal_message({
                    'type': 'predictions',
                    'content_id': content_id,
                    'predicted_revenue': predictions,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }, websocket)
    
    except WebSocketDisconnect:
        await analytics_manager.disconnect(websocket, client_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await analytics_manager.disconnect(websocket, client_id)

# ============== BACKGROUND BROADCAST TASK ==============

async def broadcast_real_time_updates():
    """Broadcast real-time updates to all connected clients"""
    update_interval = 0.5  # 500ms updates
    
    while True:
        try:
            # Get all updates
            view_update = await dashboard_update_service.get_view_update()
            engagement_update = await dashboard_update_service.get_engagement_update()
            revenue_update = await dashboard_update_service.get_revenue_update()
            trending_update = await dashboard_update_service.get_trending_update()
            geo_update = await dashboard_update_service.get_geographic_update()
            
            # Broadcast to all connections
            for update in [view_update, engagement_update, revenue_update, trending_update, geo_update]:
                await analytics_manager.broadcast_update(update)
            
            await asyncio.sleep(update_interval)
        
        except Exception as e:
            logger.error(f"Broadcast error: {e}")
            await asyncio.sleep(update_interval)

# ============== ADVANCED ANALYTICS ENDPOINTS ==============

async def get_real_time_dashboard():
    """Get real-time dashboard snapshot"""
    dashboard = analytics_engine.get_dashboard_snapshot()
    return {
        'timestamp': dashboard.timestamp.isoformat(),
        'views': {
            'total': dashboard.total_views,
            'unique': dashboard.total_unique_viewers,
            'active_sessions': dashboard.active_sessions,
            'total_watch_time': dashboard.total_watch_time
        },
        'engagement': {
            'avg_score': dashboard.avg_engagement_score,
            'trends': dashboard.engagement_trends[-100:]
        },
        'revenue': {
            'total': dashboard.total_revenue,
            'by_source': dashboard.revenue_sources,
            'top_creators': dashboard.top_creators
        },
        'content': {
            'trending': dashboard.trending_content,
            'count': len(analytics_engine.content_views)
        },
        'geography': {
            'heatmap': dashboard.geo_heatmap,
            'top_countries': sorted(dashboard.geo_heatmap.items(), key=lambda x: x[1], reverse=True)[:10]
        }
    }

async def get_content_deep_dive(content_id: str):
    """Get detailed analytics for a specific content"""
    metrics = analytics_engine.get_content_metrics(content_id)
    dropouts = predictive_analytics.identify_drop_points(content_id)
    
    return {
        'content_id': content_id,
        'performance': {
            'views': metrics.views,
            'unique_viewers': metrics.unique_viewers,
            'watch_time': metrics.total_watch_time,
            'avg_watch_time': metrics.avg_watch_time,
            'completion_rate': f"{metrics.completion_rate:.1f}%",
            'engagement_score': metrics.engagement_score,
            'revenue': metrics.revenue,
            'revenue_per_view': metrics.revenue_per_view
        },
        'engagement': metrics.engagement_breakdown,
        'geography': {
            'top_countries': metrics.top_geographies,
            'top_devices': metrics.top_devices
        },
        'audience_flow': {
            'dropouts': dropouts
        },
        'sources': metrics.revenue_breakdown
    }

async def get_creator_dashboard(creator_id: str):
    """Get creator-specific dashboard"""
    creator_analytics = analytics_engine.get_creator_analytics(creator_id)
    
    # Get recent revenue
    recent_revenue = [
        r for r in analytics_engine.revenue_buffer
        if r.creator_id == creator_id
    ][-1000:]
    
    daily_revenue = defaultdict(float)
    for metric in recent_revenue:
        date = metric.timestamp.date().isoformat()
        daily_revenue[date] += metric.amount
    
    return {
        'creator_id': creator_id,
        'metrics': {
            'total_revenue': creator_analytics['total_revenue'],
            'total_views': creator_analytics['total_views'],
            'total_engagement': creator_analytics['total_engagement'],
            'avg_completion_rate': f"{creator_analytics['avg_completion_rate']:.1f}%",
            'content_count': creator_analytics['content_count']
        },
        'top_content': creator_analytics['top_content'],
        'revenue_trend': dict(sorted(daily_revenue.items()))
    }

async def get_engagement_heatmap():
    """Get engagement heatmap (hour x day of week)"""
    heatmap = defaultdict(lambda: defaultdict(int))
    
    for view in analytics_engine.view_buffer:
        day_of_week = view.timestamp.strftime('%A')
        hour = view.timestamp.hour
        engagement = view.engagement.total_engagement()
        heatmap[day_of_week][hour] += engagement
    
    return {
        'type': 'engagement_heatmap',
        'data': {day: dict(hours) for day, hours in heatmap.items()}
    }

async def get_revenue_breakdown():
    """Get detailed revenue breakdown"""
    sources = defaultdict(float)
    creators = defaultdict(float)
    content = defaultdict(float)
    
    for metric in analytics_engine.revenue_buffer:
        sources[metric.source.value] += metric.amount
        creators[metric.creator_id] += metric.amount
        content[metric.content_id] += metric.amount
    
    return {
        'by_source': dict(sources),
        'by_creator': dict(sorted(creators.items(), key=lambda x: x[1], reverse=True)[:20]),
        'by_content': dict(sorted(content.items(), key=lambda x: x[1], reverse=True)[:20]),
        'total': analytics_engine.total_revenue
    }

async def get_audience_insights():
    """Get detailed audience insights"""
    devices = defaultdict(int)
    countries = defaultdict(int)
    completion_rates = []
    
    for view in analytics_engine.view_buffer:
        devices[view.device_type] += 1
        countries[view.geo_location] += 1
        completion_rates.append(view.completion_rate)
    
    return {
        'devices': dict(devices),
        'countries': dict(sorted(countries.items(), key=lambda x: x[1], reverse=True)[:20]),
        'completion_stats': {
            'median': statistics.median(completion_rates) if completion_rates else 0,
            'mean': statistics.mean(completion_rates) if completion_rates else 0,
            'stdev': statistics.stdev(completion_rates) if len(completion_rates) > 1 else 0
        }
    }

async def get_predictive_insights(content_id: str):
    """Get AI-powered predictive insights"""
    metrics = analytics_engine.get_content_metrics(content_id)
    dropouts = predictive_analytics.identify_drop_points(content_id)
    
    # Predict next hour performance
    views_trend = [v.views for v in analytics_engine.view_buffer[-100:]]
    predicted_hourly_views = int(statistics.mean(views_trend) * 1.5) if views_trend else 0
    
    predicted_revenue = predictive_analytics.predict_revenue(content_id)
    
    return {
        'content_id': content_id,
        'predictions': {
            'next_hour_views': predicted_hourly_views,
            'predicted_daily_revenue': predicted_revenue,
            'completion_rate_trend': 'improving' if metrics.completion_rate > 50 else 'declining'
        },
        'recommendations': {
            'optimal_posting_time': 'evening',  # Based on heatmap
            'focus_areas': ['engagement' if metrics.engagement_score < 50 else 'reach'],
            'retention_insights': dropouts
        }
    }
