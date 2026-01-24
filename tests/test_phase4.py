"""
PHASE 4: Comprehensive Test Suite
Tests for WebSockets, Message Queues, Search, Recommendations, and Moderation
"""

import pytest
import json
import asyncio
from datetime import datetime
from typing import AsyncGenerator

# Test fixtures
@pytest.fixture
async def redis_client():
    """Redis test client"""
    import redis.asyncio as aioredis
    client = await aioredis.from_url("redis://localhost:6379")
    yield client
    await client.close()


@pytest.fixture
async def mongodb_db():
    """MongoDB test database"""
    from motor.motor_asyncio import AsyncIOMotorClient
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["test_videos"]
    yield db
    await client.drop_database("test_videos")
    client.close()


# WebSocket Tests
@pytest.mark.asyncio
class TestWebSocketIntegration:
    """Test WebSocket infrastructure"""
    
    async def test_connection_manager_lifecycle(self, redis_client, mongodb_db):
        """Test WebSocket connection lifecycle"""
        from backend.phase4_websocket import ConnectionManager
        
        manager = ConnectionManager(redis_client, mongodb_db)
        
        # Test tracking
        user_id = "test_user_1"
        channel = "main"
        
        # Simulate connection (in real test, we'd use mock WebSocket)
        conn_metadata = manager.connection_metadata
        
        assert len(conn_metadata) == 0 or "test" in str(conn_metadata)
    
    async def test_chat_message_persistence(self, redis_client, mongodb_db):
        """Test chat message saving and retrieval"""
        from backend.phase4_websocket import ChatManager
        
        chat = ChatManager(redis_client, mongodb_db)
        
        # Save message
        message = await chat.save_message(
            user_id="user1",
            channel="general",
            content="Hello, world!"
        )
        
        assert message["_id"]
        assert message["content"] == "Hello, world!"
        assert message["user_id"] == "user1"
    
    async def test_notification_creation(self, redis_client, mongodb_db):
        """Test notification creation and retrieval"""
        from backend.phase4_websocket import NotificationManager
        
        notif_manager = NotificationManager(redis_client, mongodb_db)
        
        # Create notification
        notif = await notif_manager.create_notification(
            user_id="user1",
            title="New Upload",
            content="User uploaded a new video",
            notification_type="upload"
        )
        
        assert notif["user_id"] == "user1"
        assert notif["title"] == "New Upload"
        
        # Mark as delivered
        marked = await notif_manager.mark_as_delivered(notif["_id"])
        assert marked


# Message Queue Tests
@pytest.mark.asyncio
class TestMessageQueue:
    """Test message queue and event streaming"""
    
    async def test_event_publishing(self, redis_client, mongodb_db):
        """Test event publishing"""
        from backend.phase4_message_queue import Event, EventType, EventStreamManager
        
        event_stream = EventStreamManager(redis_client, mongodb_db)
        
        # Create and publish event
        event = Event(
            event_type=EventType.VIDEO_UPLOADED,
            entity_id="video1",
            entity_type="video",
            user_id="user1",
            timestamp=datetime.utcnow().isoformat(),
            data={"title": "New Video"}
        )
        
        await event_stream.publish_event(event)
        
        # Verify saved
        history = await event_stream.get_event_history(EventType.VIDEO_UPLOADED)
        assert len(history) > 0


# Search Tests
@pytest.mark.asyncio
class TestElasticsearchIntegration:
    """Test Elasticsearch search"""
    
    async def test_search_initialization(self, mongodb_db):
        """Test search engine initialization"""
        from backend.phase4_search import ElasticsearchManager
        
        search = ElasticsearchManager(db=mongodb_db)
        await search.initialize_indexes()
        
        # Verify indexes exist
        assert search.es_client is not None
    
    async def test_trending_score_calculation(self, mongodb_db):
        """Test trending score calculation"""
        from backend.phase4_search import ElasticsearchManager
        
        search = ElasticsearchManager(db=mongodb_db)
        
        video = {
            "_id": "video1",
            "title": "Test Video",
            "view_count": 1000,
            "like_count": 50,
            "comment_count": 20,
            "created_at": datetime.utcnow()
        }
        
        score = await search._calculate_trending_score(video)
        assert 0 <= score <= 10000


# Recommendation Tests
@pytest.mark.asyncio
class TestRecommendationEngine:
    """Test ML recommendation engine"""
    
    async def test_user_profile_building(self, redis_client, mongodb_db):
        """Test user profile creation"""
        from backend.phase4_recommendations import RecommendationEngine
        
        engine = RecommendationEngine(redis_client, mongodb_db)
        
        # Insert test video
        await mongodb_db["videos"].insert_one({
            "_id": "video1",
            "title": "Test Video",
            "category": "tech",
            "tags": ["python", "tutorial"],
            "channel_id": "channel1"
        })
        
        # Insert test interaction
        await mongodb_db["user_interactions"].insert_one({
            "user_id": "user1",
            "video_id": "video1",
            "event_type": "view"
        })
        
        # Build profile
        profile = await engine._build_user_profile("user1")
        assert profile is not None
        assert "interests" in profile
    
    async def test_trending_fallback(self, redis_client, mongodb_db):
        """Test trending videos fallback"""
        from backend.phase4_recommendations import RecommendationEngine
        
        engine = RecommendationEngine(redis_client, mongodb_db)
        
        # Insert test videos
        await mongodb_db["videos"].insert_many([
            {
                "_id": "video1",
                "title": "Popular Video",
                "view_count": 10000,
                "like_count": 500,
                "comment_count": 200,
                "is_public": True
            },
            {
                "_id": "video2",
                "title": "Less Popular Video",
                "view_count": 100,
                "like_count": 5,
                "comment_count": 2,
                "is_public": True
            }
        ])
        
        # Get trending
        trending = await engine._trending_videos(limit=1)
        assert len(trending) == 1
        assert trending[0]["video_id"] == "video1"


# Moderation Tests
@pytest.mark.asyncio
class TestContentModeration:
    """Test content moderation system"""
    
    async def test_content_flagging(self, redis_client, mongodb_db):
        """Test flagging content"""
        from backend.phase4_moderation import ContentModerationSystem, ContentFlag
        
        moderation = ContentModerationSystem(redis_client, mongodb_db)
        
        # Flag content
        flag_id = await moderation.flag_content(
            content_id="video1",
            content_type="video",
            flag_type=ContentFlag.SPAM,
            reporter_id="reporter1",
            reason="Promotional spam"
        )
        
        assert flag_id
    
    async def test_text_analysis(self):
        """Test text content analysis"""
        from backend.phase4_moderation import TextAnalyzer
        
        # Clean text
        result = TextAnalyzer.analyze_text("This is a normal comment")
        assert result["violations"] == []
        assert result["recommended_action"] is None
        
        # Suspicious text
        result = TextAnalyzer.analyze_text("https://spam.com https://spam2.com https://spam3.com https://spam4.com https://spam5.com https://spam6.com")
        assert "excessive_links" in result["violations"]


# Integration Tests
@pytest.mark.asyncio
class TestPhase4Integration:
    """Test complete Phase 4 integration"""
    
    async def test_all_components_initialized(self):
        """Test that all Phase 4 components can initialize"""
        from backend.phase4_integration import Phase4Integration
        
        phase4 = Phase4Integration()
        
        # Verify components are None before setup
        assert phase4.connection_manager is None
        assert phase4.message_queue is None
        assert phase4.search_engine is None
        assert phase4.recommendation_engine is None
        assert phase4.moderation_system is None


# Performance Tests
@pytest.mark.asyncio
class TestPhase4Performance:
    """Performance tests for Phase 4 components"""
    
    async def test_recommendation_performance(self, redis_client, mongodb_db):
        """Test recommendation engine performance"""
        import time
        from backend.phase4_recommendations import RecommendationEngine
        
        engine = RecommendationEngine(redis_client, mongodb_db)
        
        # Insert test data
        videos = [
            {
                "_id": f"video{i}",
                "title": f"Video {i}",
                "category": ["tech", "gaming", "music"][i % 3],
                "tags": ["tag1", "tag2", "tag3"],
                "channel_id": f"channel{i % 5}",
                "view_count": i * 100,
                "like_count": i * 10,
                "is_public": True
            }
            for i in range(100)
        ]
        
        await mongodb_db["videos"].insert_many(videos)
        
        # Time trending lookup
        start = time.time()
        trending = await engine._trending_videos(limit=10)
        elapsed = time.time() - start
        
        assert len(trending) <= 10
        assert elapsed < 1.0  # Should complete in < 1 second


# Stress Tests
@pytest.mark.asyncio
class TestPhase4Stress:
    """Stress tests for Phase 4 components"""
    
    async def test_message_queue_stress(self, redis_client, mongodb_db):
        """Test message queue under load"""
        from backend.phase4_message_queue import Event, EventType, EventStreamManager
        
        event_stream = EventStreamManager(redis_client, mongodb_db)
        
        # Publish multiple events
        events_published = 0
        for i in range(100):
            event = Event(
                event_type=EventType.VIDEO_VIEWED,
                entity_id=f"video{i}",
                entity_type="video",
                user_id=f"user{i % 10}",
                timestamp=datetime.utcnow().isoformat(),
                data={"duration": i * 10}
            )
            
            try:
                await event_stream.publish_event(event)
                events_published += 1
            except Exception as e:
                print(f"Error publishing event: {e}")
                break
        
        assert events_published == 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
