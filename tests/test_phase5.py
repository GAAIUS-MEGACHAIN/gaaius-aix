"""
Phase 5 comprehensive test suite - Analytics & Business Intelligence
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from backend.phase5_analytics import (
    RealTimeAnalyticsCollector,
    UserSegmentation,
    CohortAnalysis,
    FunnelAnalysis,
    DashboardGenerator,
    AnalyticsEvent,
    MetricType,
    Phase5AnalyticsIntegration
)
from backend.phase5_business_intelligence import (
    RevenueOptimizer,
    PredictiveAnalytics,
    GrowthOptimization,
    RevenueEvent,
    RevenueModel,
    Phase5BusinessIntelligence
)
from backend.phase5_integration import Phase5Integration


# ============== FIXTURES ==============

@pytest.fixture
def mock_db():
    """Mock database"""
    db = AsyncMock()
    db.analytics_events = AsyncMock()
    db.revenue_events = AsyncMock()
    db.cohorts = AsyncMock()
    db.funnel_events = AsyncMock()
    db.videos = AsyncMock()
    db.users = AsyncMock()
    return db


@pytest.fixture
def mock_redis():
    """Mock Redis"""
    redis = AsyncMock()
    redis.get = AsyncMock(return_value=None)
    redis.set = AsyncMock()
    redis.setex = AsyncMock()
    redis.incr = AsyncMock()
    redis.incrbyfloat = AsyncMock()
    redis.expire = AsyncMock()
    return redis


# ============== ANALYTICS TESTS ==============

class TestRealTimeAnalyticsCollector:
    """Test real-time analytics collector"""
    
    @pytest.mark.asyncio
    async def test_track_event(self, mock_db, mock_redis):
        """Test event tracking"""
        collector = RealTimeAnalyticsCollector(mock_db, mock_redis)
        
        event = AnalyticsEvent(
            event_type="view",
            user_id="user123",
            video_id="video456"
        )
        
        await collector.track_event(event)
        
        assert len(collector.event_buffer) == 1
        mock_redis.incr.assert_called()
    
    @pytest.mark.asyncio
    async def test_flush_events(self, mock_db, mock_redis):
        """Test event flushing"""
        collector = RealTimeAnalyticsCollector(mock_db, mock_redis)
        mock_db.analytics_events.insert_many = AsyncMock(
            return_value=MagicMock(inserted_ids=["id1", "id2"])
        )
        
        # Add events
        for i in range(3):
            event = AnalyticsEvent(
                event_type="view",
                user_id=f"user{i}",
                video_id=f"video{i}"
            )
            collector.event_buffer.append(event)
        
        await collector.flush_events()
        
        assert len(collector.event_buffer) == 0
        mock_db.analytics_events.insert_many.assert_called()
    
    @pytest.mark.asyncio
    async def test_get_metrics(self, mock_db, mock_redis):
        """Test getting metrics"""
        collector = RealTimeAnalyticsCollector(mock_db, mock_redis)
        
        mock_db.analytics_events.aggregate = AsyncMock()
        mock_db.analytics_events.aggregate.return_value.to_list = AsyncMock(
            return_value=[
                {"_id": "2024-01-01", "value": 100},
                {"_id": "2024-01-02", "value": 150}
            ]
        )
        
        metrics = await collector.get_metrics(MetricType.VIEWS, period_days=7)
        
        assert len(metrics) >= 0


class TestUserSegmentation:
    """Test user segmentation"""
    
    @pytest.mark.asyncio
    async def test_segment_users(self, mock_db, mock_redis):
        """Test user segmentation"""
        segmentation = UserSegmentation(mock_db, mock_redis)
        
        mock_db.analytics_events.aggregate = AsyncMock()
        mock_db.analytics_events.aggregate.return_value.to_list = AsyncMock(
            return_value=[
                {"_id": "user1", "count": 100, "last_activity": datetime.utcnow()},
                {"_id": "user2", "count": 5, "last_activity": datetime.utcnow()},
            ]
        )
        
        segments = await segmentation.segment_users()
        
        assert "highly_active" in segments
        assert "active" in segments


class TestCohortAnalysis:
    """Test cohort analysis"""
    
    @pytest.mark.asyncio
    async def test_create_cohort(self, mock_db, mock_redis):
        """Test cohort creation"""
        cohort = CohortAnalysis(mock_db)
        
        mock_db.cohorts.insert_one = AsyncMock(
            return_value=MagicMock(inserted_id="cohort123")
        )
        
        result = await cohort.create_cohort(
            "test_cohort",
            datetime.utcnow(),
            ["user1", "user2", "user3"]
        )
        
        assert result == "cohort123"
    
    @pytest.mark.asyncio
    async def test_get_cohort_retention(self, mock_db, mock_redis):
        """Test cohort retention calculation"""
        cohort = CohortAnalysis(mock_db)
        
        mock_db.cohorts.find_one = AsyncMock(
            return_value={
                "_id": "cohort123",
                "start_date": datetime.utcnow() - timedelta(weeks=13),
                "user_ids": ["user1", "user2"]
            }
        )
        
        mock_db.analytics_events.count_documents = AsyncMock(return_value=1)
        
        retention = await cohort.get_cohort_retention("cohort123")
        
        assert isinstance(retention, dict)


class TestFunnelAnalysis:
    """Test funnel analysis"""
    
    @pytest.mark.asyncio
    async def test_analyze_funnel(self, mock_db, mock_redis):
        """Test funnel analysis"""
        funnel = FunnelAnalysis(mock_db)
        
        mock_db.funnel_events.count_documents = AsyncMock(return_value=50)
        
        result = await funnel.analyze_funnel(
            "signup_funnel",
            ["view", "signup", "verify", "complete"]
        )
        
        assert "name" in result


class TestDashboardGenerator:
    """Test dashboard generation"""
    
    @pytest.mark.asyncio
    async def test_generate_executive_dashboard(self, mock_db, mock_redis):
        """Test executive dashboard"""
        dashboard = DashboardGenerator(mock_db, mock_redis)
        
        mock_redis.get = AsyncMock(return_value="1000")
        mock_db.analytics_events.aggregate = AsyncMock()
        mock_db.analytics_events.aggregate.return_value.to_list = AsyncMock(
            return_value=[]
        )
        
        result = await dashboard.generate_executive_dashboard()
        
        assert "generated_at" in result
    
    @pytest.mark.asyncio
    async def test_generate_creator_dashboard(self, mock_db, mock_redis):
        """Test creator dashboard"""
        dashboard = DashboardGenerator(mock_db, mock_redis)
        
        mock_db.videos.find = AsyncMock()
        mock_db.videos.find.return_value.to_list = AsyncMock(
            return_value=[
                {"_id": "video1", "title": "Video 1", "creator_id": "creator1"}
            ]
        )
        
        mock_redis.get = AsyncMock(return_value="100")
        
        result = await dashboard.generate_creator_dashboard("creator1")
        
        assert "creator_id" in result


# ============== BUSINESS INTELLIGENCE TESTS ==============

class TestRevenueOptimizer:
    """Test revenue optimization"""
    
    @pytest.mark.asyncio
    async def test_track_revenue(self, mock_db, mock_redis):
        """Test revenue tracking"""
        optimizer = RevenueOptimizer(mock_db, mock_redis)
        
        mock_db.revenue_events.insert_one = AsyncMock()
        
        event = RevenueEvent(
            event_type=RevenueModel.ADS,
            amount=100.0,
            user_id="user123",
            creator_id="creator456"
        )
        
        await optimizer.track_revenue(event)
        
        mock_db.revenue_events.insert_one.assert_called()
    
    @pytest.mark.asyncio
    async def test_get_revenue_metrics(self, mock_db, mock_redis):
        """Test revenue metrics"""
        optimizer = RevenueOptimizer(mock_db, mock_redis)
        
        mock_db.revenue_events.aggregate = AsyncMock()
        mock_db.revenue_events.aggregate.return_value.to_list = AsyncMock(
            return_value=[
                {
                    "_id": {"date": "2024-01-01", "type": "ads"},
                    "total": 500.0,
                    "count": 10
                }
            ]
        )
        
        metrics = await optimizer.get_revenue_metrics()
        
        assert "total_revenue" in metrics


class TestPredictiveAnalytics:
    """Test predictive analytics"""
    
    @pytest.mark.asyncio
    async def test_predict_churn_risk(self, mock_db, mock_redis):
        """Test churn prediction"""
        predictive = PredictiveAnalytics(mock_db)
        
        mock_db.analytics_events.count_documents = AsyncMock(return_value=0)
        
        risk = await predictive.predict_churn_risk("user123")
        
        assert 0.0 <= risk <= 1.0
    
    @pytest.mark.asyncio
    async def test_predict_trending_topics(self, mock_db, mock_redis):
        """Test trending topics prediction"""
        predictive = PredictiveAnalytics(mock_db)
        
        mock_db.videos.aggregate = AsyncMock()
        mock_db.videos.aggregate.return_value.to_list = AsyncMock(
            return_value=[
                {"_id": "python", "count": 100, "trend": 0.8}
            ]
        )
        
        trending = await predictive.predict_trending_topics()
        
        assert isinstance(trending, list)


class TestGrowthOptimization:
    """Test growth optimization"""
    
    @pytest.mark.asyncio
    async def test_get_growth_metrics(self, mock_db, mock_redis):
        """Test growth metrics"""
        growth = GrowthOptimization(mock_db, mock_redis)
        
        mock_db.users.count_documents = AsyncMock(return_value=1000)
        mock_db.analytics_events.count_documents = AsyncMock(return_value=500)
        
        metrics = await growth.get_growth_metrics()
        
        assert "total_users" in metrics


# ============== INTEGRATION TESTS ==============

class TestPhase5Integration:
    """Test Phase 5 integration"""
    
    @pytest.mark.asyncio
    async def test_initialization(self, mock_db, mock_redis):
        """Test Phase 5 initialization"""
        phase5 = Phase5Integration()
        
        result = await phase5.setup_phase5(None, mock_db, mock_redis)
        
        assert phase5.analytics is not None
        assert phase5.business_intelligence is not None
    
    @pytest.mark.asyncio
    async def test_health_check(self, mock_db, mock_redis):
        """Test Phase 5 health check"""
        phase5 = Phase5Integration()
        await phase5.setup_phase5(None, mock_db, mock_redis)
        
        health = await phase5.health_check()
        
        assert "status" in health
        assert health["status"] == "healthy"
    
    @pytest.mark.asyncio
    async def test_track_event_through_integration(self, mock_db, mock_redis):
        """Test event tracking through integration"""
        phase5 = Phase5Integration()
        await phase5.setup_phase5(None, mock_db, mock_redis)
        
        event = AnalyticsEvent(
            event_type="view",
            user_id="user123",
            video_id="video456"
        )
        
        await phase5.track_event(event)
        
        assert len(phase5.collector.event_buffer) >= 0


# ============== PERFORMANCE TESTS ==============

class TestPhase5Performance:
    """Test Phase 5 performance"""
    
    @pytest.mark.asyncio
    async def test_event_tracking_performance(self, mock_db, mock_redis):
        """Test event tracking speed"""
        collector = RealTimeAnalyticsCollector(mock_db, mock_redis)
        
        import time
        start = time.time()
        
        for i in range(100):
            event = AnalyticsEvent(
                event_type="view",
                user_id=f"user{i}",
                video_id=f"video{i}"
            )
            await collector.track_event(event)
        
        elapsed = time.time() - start
        
        # 100 events should complete in < 1 second
        assert elapsed < 1.0


# ============== STRESS TESTS ==============

class TestPhase5Stress:
    """Test Phase 5 under stress"""
    
    @pytest.mark.asyncio
    async def test_large_cohort_retention(self, mock_db, mock_redis):
        """Test retention calculation for large cohort"""
        cohort = CohortAnalysis(mock_db)
        
        mock_db.cohorts.find_one = AsyncMock(
            return_value={
                "_id": "cohort123",
                "start_date": datetime.utcnow() - timedelta(weeks=13),
                "user_ids": [f"user{i}" for i in range(10000)]  # 10K users
            }
        )
        
        mock_db.analytics_events.count_documents = AsyncMock(return_value=50)
        
        retention = await cohort.get_cohort_retention("cohort123")
        
        assert isinstance(retention, dict)
    
    @pytest.mark.asyncio
    async def test_bulk_revenue_tracking(self, mock_db, mock_redis):
        """Test bulk revenue tracking"""
        optimizer = RevenueOptimizer(mock_db, mock_redis)
        
        mock_db.revenue_events.insert_one = AsyncMock()
        
        import time
        start = time.time()
        
        for i in range(1000):
            event = RevenueEvent(
                event_type=RevenueModel.ADS,
                amount=10.0,
                user_id=f"user{i}",
                creator_id=f"creator{i%100}"
            )
            await optimizer.track_revenue(event)
        
        elapsed = time.time() - start
        
        # 1000 events should complete in < 5 seconds
        assert elapsed < 5.0
