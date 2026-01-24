"""
PHASE 5 INTEGRATION - Master orchestrator for advanced analytics and business intelligence
"""

from typing import Dict, Any, Optional
from datetime import datetime
import asyncio
import logging

from .phase5_analytics import (
    Phase5AnalyticsIntegration,
    RealTimeAnalyticsCollector,
    UserSegmentation,
    CohortAnalysis,
    FunnelAnalysis,
    DashboardGenerator,
    AnalyticsEvent,
    MetricType
)
from .phase5_business_intelligence import (
    Phase5BusinessIntelligence,
    RevenueOptimizer,
    PredictiveAnalytics,
    GrowthOptimization,
    RevenueEvent,
    RevenueModel
)

logger = logging.getLogger(__name__)


class Phase5Integration:
    """Master integrator for Phase 5 infrastructure"""
    
    def __init__(self):
        self.db = None
        self.redis = None
        self.analytics = Phase5AnalyticsIntegration()
        self.business_intelligence = Phase5BusinessIntelligence()
        
        # Component managers
        self.collector = None
        self.segmentation = None
        self.cohort = None
        self.funnel = None
        self.dashboard = None
        self.revenue_optimizer = None
        self.predictive = None
        self.growth = None
        
        # Background tasks
        self.background_tasks = []
        self.running = False
    
    async def setup_phase5(self, app, db, redis_client=None):
        """Initialize Phase 5 infrastructure"""
        try:
            self.db = db
            self.redis = redis_client
            
            logger.info("Initializing Phase 5: Advanced Analytics & Business Intelligence")
            
            # Initialize analytics
            await self.analytics.initialize(db, redis_client)
            self.collector = self.analytics.collector
            self.segmentation = self.analytics.segmentation
            self.cohort = self.analytics.cohort
            self.funnel = self.analytics.funnel
            self.dashboard = self.analytics.dashboard
            
            # Initialize BI
            await self.business_intelligence.initialize(db, redis_client)
            self.revenue_optimizer = self.business_intelligence.revenue_optimizer
            self.predictive = self.business_intelligence.predictive
            self.growth = self.business_intelligence.growth
            
            # Start background tasks
            self.running = True
            self._start_background_tasks()
            
            logger.info("✅ Phase 5 infrastructure initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Phase 5 setup error: {e}", exc_info=True)
            return False
    
    def _start_background_tasks(self):
        """Start background processing tasks"""
        try:
            # Analytics flush task
            task1 = asyncio.create_task(self._analytics_flush_loop())
            self.background_tasks.append(task1)
            
            # Growth metrics task
            task2 = asyncio.create_task(self._growth_metrics_loop())
            self.background_tasks.append(task2)
            
            # Predictive analytics task
            task3 = asyncio.create_task(self._predictive_loop())
            self.background_tasks.append(task3)
            
            logger.info("Background tasks started")
        except Exception as e:
            logger.error(f"Background task startup error: {e}")
    
    async def _analytics_flush_loop(self):
        """Periodically flush analytics events"""
        while self.running:
            try:
                await asyncio.sleep(300)  # 5 minutes
                if self.collector:
                    await self.collector.flush_events()
            except Exception as e:
                logger.error(f"Analytics flush error: {e}")
    
    async def _growth_metrics_loop(self):
        """Periodically calculate growth metrics"""
        while self.running:
            try:
                await asyncio.sleep(3600)  # 1 hour
                if self.growth:
                    metrics = await self.growth.get_growth_metrics()
                    if self.redis:
                        await self.redis.setex(
                            "metrics:growth",
                            7200,
                            str(metrics)
                        )
            except Exception as e:
                logger.error(f"Growth metrics error: {e}")
    
    async def _predictive_loop(self):
        """Periodically run predictive models"""
        while self.running:
            try:
                await asyncio.sleep(7200)  # 2 hours
                if self.predictive and self.db:
                    # Predict trending topics
                    trending = await self.predictive.predict_trending_topics()
                    if self.redis:
                        await self.redis.setex(
                            "predictions:trending",
                            7200,
                            str(trending)
                        )
            except Exception as e:
                logger.error(f"Predictive analytics error: {e}")
    
    async def _on_shutdown(self):
        """Shutdown Phase 5"""
        try:
            self.running = False
            
            # Wait for tasks to complete
            if self.background_tasks:
                await asyncio.gather(*self.background_tasks, return_exceptions=True)
            
            # Shutdown components
            await self.analytics.shutdown()
            await self.business_intelligence.shutdown()
            
            logger.info("✅ Phase 5 shutdown complete")
        except Exception as e:
            logger.error(f"Phase 5 shutdown error: {e}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Get Phase 5 health status"""
        try:
            analytics_health = await self.analytics.health_check()
            bi_health = await self.business_intelligence.health_check()
            
            return {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "components": {
                    "analytics": analytics_health.get("status", "unknown"),
                    "business_intelligence": bi_health.get("status", "unknown"),
                    "background_tasks": len([t for t in self.background_tasks if not t.done()])
                },
                "subsystems": {
                    "analytics": analytics_health,
                    "business_intelligence": bi_health
                }
            }
        except Exception as e:
            logger.error(f"Health check error: {e}")
            return {"status": "error", "message": str(e)}
    
    # ============== ANALYTICS API ==============
    
    async def track_event(self, event: AnalyticsEvent):
        """Track analytics event"""
        if self.collector:
            await self.collector.track_event(event)
    
    async def get_metrics(self, metric_type: MetricType, period_days: int = 7):
        """Get aggregated metrics"""
        if self.collector:
            return await self.collector.get_metrics(metric_type, period_days)
        return []
    
    async def get_user_segments(self) -> Dict[str, list]:
        """Get user segmentation"""
        if self.segmentation:
            return await self.segmentation.segment_users()
        return {}
    
    async def get_segment_metrics(self, segment: str) -> Dict[str, Any]:
        """Get segment-specific metrics"""
        if self.segmentation:
            return await self.segmentation.get_segment_metrics(segment)
        return {}
    
    async def create_cohort(self, cohort_name: str, start_date: datetime, user_ids: list):
        """Create user cohort"""
        if self.cohort:
            return await self.cohort.create_cohort(cohort_name, start_date, user_ids)
        return None
    
    async def get_cohort_retention(self, cohort_id: str) -> Dict[int, float]:
        """Get cohort retention"""
        if self.cohort:
            return await self.cohort.get_cohort_retention(cohort_id)
        return {}
    
    async def track_funnel_step(self, funnel_name: str, user_id: str, step: int):
        """Track funnel step"""
        if self.funnel:
            await self.funnel.track_funnel_step(funnel_name, user_id, step)
    
    async def analyze_funnel(self, funnel_name: str, steps: list) -> Dict[str, Any]:
        """Analyze funnel"""
        if self.funnel:
            return await self.funnel.analyze_funnel(funnel_name, steps)
        return {}
    
    async def get_executive_dashboard(self) -> Dict[str, Any]:
        """Get executive dashboard"""
        if self.dashboard:
            return await self.dashboard.generate_executive_dashboard()
        return {}
    
    async def get_creator_dashboard(self, creator_id: str) -> Dict[str, Any]:
        """Get creator dashboard"""
        if self.dashboard:
            return await self.dashboard.generate_creator_dashboard(creator_id)
        return {}
    
    # ============== BUSINESS INTELLIGENCE API ==============
    
    async def track_revenue(self, event: RevenueEvent):
        """Track revenue event"""
        if self.revenue_optimizer:
            await self.revenue_optimizer.track_revenue(event)
    
    async def get_revenue_metrics(self, period_days: int = 30) -> Dict[str, Any]:
        """Get revenue metrics"""
        if self.revenue_optimizer:
            return await self.revenue_optimizer.get_revenue_metrics(period_days)
        return {}
    
    async def get_creator_earnings(self, creator_id: str, period_days: int = 30) -> Dict[str, Any]:
        """Get creator earnings"""
        if self.revenue_optimizer:
            return await self.revenue_optimizer.get_creator_earnings(creator_id, period_days)
        return {}
    
    async def optimize_pricing(self, video_id: str) -> Dict[str, Any]:
        """Get pricing optimization recommendation"""
        if self.revenue_optimizer:
            return await self.revenue_optimizer.optimize_pricing(video_id)
        return {}
    
    async def predict_churn_risk(self, user_id: str) -> float:
        """Predict user churn risk"""
        if self.predictive:
            return await self.predictive.predict_churn_risk(user_id)
        return 0.0
    
    async def predict_video_performance(self, video_id: str) -> Dict[str, Any]:
        """Predict video performance"""
        if self.predictive:
            return await self.predictive.predict_video_performance(video_id)
        return {}
    
    async def predict_trending_topics(self) -> list:
        """Predict trending topics"""
        if self.predictive:
            return await self.predictive.predict_trending_topics()
        return []
    
    async def calculate_ltv(self, user_id: str) -> float:
        """Calculate user lifetime value"""
        if self.growth:
            return await self.growth.calculate_ltv(user_id)
        return 0.0
    
    async def get_growth_metrics(self) -> Dict[str, Any]:
        """Get platform growth metrics"""
        if self.growth:
            return await self.growth.get_growth_metrics()
        return {}
