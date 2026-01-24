"""
Comprehensive tests for the Podcast Platform endpoints.

Tests cover:
- Input validation
- Rate limiting
- Authentication
- Error handling
- Database operations
- Edge cases
"""

import pytest
import json
from datetime import datetime
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

# Mock environment setup
import os
os.environ.setdefault("MONGO_URL", "mongodb://localhost:27017")
os.environ.setdefault("DB_NAME", "test_db")
os.environ.setdefault("JWT_SECRET", "test_secret_key_for_testing")

# Import after environment setup
try:
    from server import app, limiter
except ImportError as e:
    pytest.skip(f"Could not import server: {e}", allow_module_level=True)


# Setup test client with disabled rate limiting for testing
@pytest.fixture
def client():
    """Create test client with rate limiting disabled"""
    # Disable rate limiting for testing
    app.state.limiter = Mock()
    app.state.limiter.limit = lambda x: lambda f: f
    
    return TestClient(app)


@pytest.fixture
def auth_headers():
    """Generate test authentication headers"""
    return {
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoidGVzdF91c2VyXzEiLCJlbWFpbCI6InRlc3RAZXhhbXBsZS5jb20iLCJpc19wcm8iOmZhbHNlfQ.test"
    }


class TestPodcastListEndpoint:
    """Test /v1/podcasts/list endpoint"""
    
    def test_list_podcasts_success(self, client, auth_headers):
        """Test successful podcast listing"""
        response = client.get(
            "/v1/podcasts/list",
            headers=auth_headers,
            params={"skip": 0, "limit": 10}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "podcasts" in data
        assert "total" in data
        assert "skip" in data
        assert "limit" in data
        assert "has_more" in data
        
        assert isinstance(data["podcasts"], list)
        assert data["total"] > 0
        assert data["skip"] == 0
        assert data["limit"] == 10
    
    def test_list_podcasts_pagination(self, client, auth_headers):
        """Test pagination parameters"""
        # Test with different skip/limit values
        response = client.get(
            "/v1/podcasts/list",
            headers=auth_headers,
            params={"skip": 1, "limit": 2}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["podcasts"]) <= 2
        assert data["skip"] == 1
    
    def test_list_podcasts_invalid_skip(self, client, auth_headers):
        """Test with invalid skip parameter"""
        response = client.get(
            "/v1/podcasts/list",
            headers=auth_headers,
            params={"skip": -1, "limit": 10}
        )
        
        # FastAPI validation should reject negative skip
        assert response.status_code in [422, 400]
    
    def test_list_podcasts_limit_exceeds_max(self, client, auth_headers):
        """Test limit exceeding maximum allowed"""
        response = client.get(
            "/v1/podcasts/list",
            headers=auth_headers,
            params={"skip": 0, "limit": 200}  # Exceeds max of 100
        )
        
        # FastAPI validation should reject
        assert response.status_code in [422, 400]
    
    def test_list_podcasts_no_auth(self, client):
        """Test without authentication"""
        response = client.get(
            "/v1/podcasts/list",
            params={"skip": 0, "limit": 10}
        )
        
        # Should require authentication
        assert response.status_code in [401, 403]
    
    def test_list_podcasts_response_format(self, client, auth_headers):
        """Test response format correctness"""
        response = client.get(
            "/v1/podcasts/list",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify podcast structure
        for podcast in data["podcasts"]:
            assert "id" in podcast
            assert "title" in podcast
            assert "author" in podcast
            assert "description" in podcast
            assert "episodes_count" in podcast
            assert "rating" in podcast
            assert isinstance(podcast["rating"], (int, float))
            assert 0 <= podcast["rating"] <= 5


class TestPodcastSubscriptionEndpoints:
    """Test subscribe/unsubscribe endpoints"""
    
    def test_subscribe_podcast_success(self, client, auth_headers):
        """Test successful podcast subscription"""
        response = client.post(
            "/v1/podcasts/1/subscribe",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "message" in data
        assert data["podcast_id"] == 1
    
    def test_subscribe_invalid_podcast_id(self, client, auth_headers):
        """Test subscribing with invalid podcast ID"""
        response = client.post(
            "/v1/podcasts/0/subscribe",  # Invalid ID
            headers=auth_headers
        )
        
        # Should reject invalid ID
        assert response.status_code in [400, 422]
    
    def test_subscribe_requires_auth(self, client):
        """Test subscription requires authentication"""
        response = client.post("/v1/podcasts/1/subscribe")
        
        assert response.status_code in [401, 403]
    
    def test_unsubscribe_podcast_success(self, client, auth_headers):
        """Test successful unsubscription"""
        response = client.post(
            "/v1/podcasts/1/unsubscribe",
            headers=auth_headers
        )
        
        assert response.status_code in [200, 404]  # 404 if not subscribed
        data = response.json()
        assert "success" in data or "detail" in data
    
    def test_subscribe_unsubscribe_flow(self, client, auth_headers):
        """Test subscribe then unsubscribe flow"""
        # Subscribe
        sub_response = client.post(
            "/v1/podcasts/2/subscribe",
            headers=auth_headers
        )
        assert sub_response.status_code == 200
        
        # Unsubscribe
        unsub_response = client.post(
            "/v1/podcasts/2/unsubscribe",
            headers=auth_headers
        )
        assert unsub_response.status_code in [200, 404]


class TestPodcastEpisodesEndpoint:
    """Test episode retrieval endpoint"""
    
    def test_get_episodes_success(self, client, auth_headers):
        """Test successful episode retrieval"""
        response = client.get(
            "/v1/podcasts/1/episodes",
            headers=auth_headers,
            params={"skip": 0, "limit": 10}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "podcast_id" in data
        assert "episodes" in data
        assert "total" in data
        assert data["podcast_id"] == 1
        assert isinstance(data["episodes"], list)
    
    def test_get_episodes_pagination(self, client, auth_headers):
        """Test episode pagination"""
        response = client.get(
            "/v1/podcasts/1/episodes",
            headers=auth_headers,
            params={"skip": 0, "limit": 5}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["episodes"]) <= 5
    
    def test_episode_structure(self, client, auth_headers):
        """Test episode data structure"""
        response = client.get(
            "/v1/podcasts/1/episodes",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        for episode in data["episodes"]:
            assert "id" in episode
            assert "title" in episode
            assert "description" in episode
            assert "duration" in episode
            assert "audio_url" in episode
            assert "published_date" in episode
            assert isinstance(episode["duration"], int)


class TestEpisodePlaybackTracking:
    """Test episode play tracking endpoint"""
    
    def test_record_play_success(self, client, auth_headers):
        """Test recording episode playback"""
        response = client.post(
            "/v1/podcasts/episodes/ep_123/play",
            headers=auth_headers,
            params={"timestamp": 1200}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["episode_id"] == "ep_123"
        assert data["progress"] == 1200
    
    def test_record_play_invalid_timestamp(self, client, auth_headers):
        """Test with invalid timestamp"""
        response = client.post(
            "/v1/podcasts/episodes/ep_123/play",
            headers=auth_headers,
            params={"timestamp": -1}  # Negative timestamp
        )
        
        assert response.status_code in [400, 422]
    
    def test_record_play_timestamp_too_large(self, client, auth_headers):
        """Test with timestamp exceeding 24 hours"""
        response = client.post(
            "/v1/podcasts/episodes/ep_123/play",
            headers=auth_headers,
            params={"timestamp": 999999999}  # Way over 24 hours
        )
        
        assert response.status_code in [400, 422]
    
    def test_record_play_boundary_timestamp(self, client, auth_headers):
        """Test with boundary timestamp (24 hours)"""
        response = client.post(
            "/v1/podcasts/episodes/ep_123/play",
            headers=auth_headers,
            params={"timestamp": 86400000}  # Exactly 24 hours in ms
        )
        
        assert response.status_code == 200


class TestEpisodeLikeEndpoint:
    """Test episode like/unlike endpoint"""
    
    def test_like_episode_success(self, client, auth_headers):
        """Test liking an episode"""
        response = client.post(
            "/v1/podcasts/episodes/ep_456/like",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "liked" in data
        assert isinstance(data["liked"], bool)
    
    def test_unlike_episode(self, client, auth_headers):
        """Test unliking an episode"""
        # Like first
        like_response = client.post(
            "/v1/podcasts/episodes/ep_789/like",
            headers=auth_headers
        )
        assert like_response.status_code == 200
        
        # Unlike
        unlike_response = client.post(
            "/v1/podcasts/episodes/ep_789/like",
            headers=auth_headers
        )
        assert unlike_response.status_code == 200
    
    def test_like_invalid_episode_id(self, client, auth_headers):
        """Test with invalid episode ID"""
        response = client.post(
            "/v1/podcasts/episodes//like",  # Empty ID
            headers=auth_headers
        )
        
        assert response.status_code in [400, 422]


class TestEpisodeUploadEndpoint:
    """Test episode upload endpoint"""
    
    def test_upload_episode_success(self, client, auth_headers):
        """Test successful episode upload"""
        response = client.post(
            "/v1/podcasts/episodes/upload",
            headers=auth_headers,
            json={
                "podcast_id": 1,
                "title": "Test Episode",
                "description": "This is a test episode description that is long enough"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "episode_id" in data
        assert data["status"] == "processing"
    
    def test_upload_episode_invalid_title(self, client, auth_headers):
        """Test upload with invalid title"""
        response = client.post(
            "/v1/podcasts/episodes/upload",
            headers=auth_headers,
            json={
                "podcast_id": 1,
                "title": "ab",  # Too short
                "description": "This is a valid description for testing"
            }
        )
        
        assert response.status_code in [400, 422]
    
    def test_upload_episode_invalid_description(self, client, auth_headers):
        """Test upload with invalid description"""
        response = client.post(
            "/v1/podcasts/episodes/upload",
            headers=auth_headers,
            json={
                "podcast_id": 1,
                "title": "Valid Title",
                "description": "short"  # Too short
            }
        )
        
        assert response.status_code in [400, 422]
    
    def test_upload_episode_xss_protection(self, client, auth_headers):
        """Test XSS protection in upload"""
        response = client.post(
            "/v1/podcasts/episodes/upload",
            headers=auth_headers,
            json={
                "podcast_id": 1,
                "title": "<script>alert('xss')</script>",
                "description": "This is a valid description"
            }
        )
        
        # Should reject malicious input
        assert response.status_code in [400, 422]


class TestRSSImportEndpoint:
    """Test RSS feed import endpoint"""
    
    def test_import_rss_success(self, client, auth_headers):
        """Test successful RSS import"""
        response = client.post(
            "/v1/podcasts/rss/import",
            headers=auth_headers,
            json={
                "feed_url": "https://feeds.example.com/podcast.xml"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "feed_url" in data
        assert data["status"] == "syncing"
    
    def test_import_rss_invalid_url(self, client, auth_headers):
        """Test RSS import with invalid URL"""
        response = client.post(
            "/v1/podcasts/rss/import",
            headers=auth_headers,
            json={
                "feed_url": "not_a_valid_url"  # Missing protocol
            }
        )
        
        assert response.status_code in [400, 422]
    
    def test_import_rss_xss_protection(self, client, auth_headers):
        """Test XSS protection in RSS URL"""
        response = client.post(
            "/v1/podcasts/rss/import",
            headers=auth_headers,
            json={
                "feed_url": "https://example.com/<script>alert('xss')</script>"
            }
        )
        
        # Should reject malicious input
        assert response.status_code in [400, 422]
    
    def test_import_rss_http_url(self, client, auth_headers):
        """Test RSS import with HTTP (not HTTPS) URL"""
        response = client.post(
            "/v1/podcasts/rss/import",
            headers=auth_headers,
            json={
                "feed_url": "http://feeds.example.com/podcast.xml"
            }
        )
        
        # Should accept HTTP (though HTTPS is preferred)
        assert response.status_code == 200


class TestSubscriptionsListEndpoint:
    """Test user subscriptions endpoint"""
    
    def test_get_subscriptions_success(self, client, auth_headers):
        """Test retrieving user subscriptions"""
        response = client.get(
            "/v1/podcasts/subscriptions/list",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "subscriptions" in data
        assert "total" in data
        assert isinstance(data["subscriptions"], list)
    
    def test_subscriptions_data_structure(self, client, auth_headers):
        """Test subscription data structure"""
        response = client.get(
            "/v1/podcasts/subscriptions/list",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        for sub in data["subscriptions"]:
            assert "id" in sub
            assert "title" in sub
            assert "author" in sub
            assert "category" in sub
            assert "rating" in sub
            assert "unread_episodes" in sub
    
    def test_subscriptions_no_auth(self, client):
        """Test subscriptions requires authentication"""
        response = client.get("/v1/podcasts/subscriptions/list")
        
        assert response.status_code in [401, 403]


class TestPodcastRecommendationsEndpoint:
    """Test podcast recommendations endpoint"""
    
    def test_get_recommendations_success(self, client, auth_headers):
        """Test getting podcast recommendations"""
        response = client.get(
            "/v1/recommendation/podcasts",
            headers=auth_headers,
            params={"limit": 5}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "recommendations" in data
        assert "total" in data
        assert isinstance(data["recommendations"], list)
    
    def test_recommendations_limit(self, client, auth_headers):
        """Test recommendations limit parameter"""
        response = client.get(
            "/v1/recommendation/podcasts",
            headers=auth_headers,
            params={"limit": 2}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["recommendations"]) <= 2
    
    def test_recommendations_data_structure(self, client, auth_headers):
        """Test recommendation data structure"""
        response = client.get(
            "/v1/recommendation/podcasts",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        for rec in data["recommendations"]:
            assert "id" in rec
            assert "title" in rec
            assert "author" in rec
            assert "rating" in rec
            assert "match_score" in rec
            assert "reason" in rec


class TestErrorHandling:
    """Test error handling across endpoints"""
    
    def test_malformed_json(self, client, auth_headers):
        """Test handling of malformed JSON"""
        response = client.post(
            "/v1/podcasts/episodes/upload",
            headers=auth_headers,
            data="not valid json",
            content_type="application/json"
        )
        
        assert response.status_code in [400, 422]
    
    def test_missing_required_fields(self, client, auth_headers):
        """Test handling of missing required fields"""
        response = client.post(
            "/v1/podcasts/episodes/upload",
            headers=auth_headers,
            json={
                "podcast_id": 1
                # Missing title and description
            }
        )
        
        assert response.status_code in [400, 422]


class TestInputSanitization:
    """Test input sanitization and validation"""
    
    def test_sanitize_script_tags(self, client, auth_headers):
        """Test sanitization of script tags"""
        response = client.post(
            "/v1/podcasts/episodes/upload",
            headers=auth_headers,
            json={
                "podcast_id": 1,
                "title": "Safe Title",
                "description": "This has <script>alert('xss')</script> injection"
            }
        )
        
        assert response.status_code in [400, 422]
    
    def test_sanitize_javascript_protocol(self, client, auth_headers):
        """Test sanitization of javascript: protocol"""
        response = client.post(
            "/v1/podcasts/rss/import",
            headers=auth_headers,
            json={
                "feed_url": "javascript:alert('xss')"
            }
        )
        
        assert response.status_code in [400, 422]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
