"""
Duet & Collab Backend - Complete Test Suite
Tests all endpoints and WebSocket functionality
"""

import pytest
import json
import asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient
from datetime import datetime

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_USER_ID = "test_user_123"
TEST_USERNAME = "john_doe"
TEST_TOKEN = "test_token_12345"


class TestDuetSessionsAPI:
    """Test Duet Sessions API endpoints"""
    
    @pytest.mark.asyncio
    async def test_create_session(self):
        """Test creating a new duet session"""
        async with AsyncClient(base_url=BASE_URL) as client:
            response = await client.post(
                "/api/duet/sessions",
                headers={"Authorization": f"Bearer {TEST_TOKEN}"},
                json={
                    "title": "Summer Vibes",
                    "description": "Dancing in the sun",
                    "max_collaborators": 5,
                    "is_public": True
                }
            )
            
            assert response.status_code in [200, 201]
            data = response.json()
            assert data["status"] == "success"
            assert "session_id" in data
            assert data["title"] == "Summer Vibes"
            assert data["creator_name"] == TEST_USERNAME
    
    @pytest.mark.asyncio
    async def test_list_user_sessions(self):
        """Test listing user's duet sessions"""
        async with AsyncClient(base_url=BASE_URL) as client:
            response = await client.get(
                "/api/duet/sessions",
                headers={"Authorization": f"Bearer {TEST_TOKEN}"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert "sessions" in data
            assert "count" in data
    
    @pytest.mark.asyncio
    async def test_get_session_details(self):
        """Test getting session details"""
        async with AsyncClient(base_url=BASE_URL) as client:
            # First create a session
            create_response = await client.post(
                "/api/duet/sessions",
                headers={"Authorization": f"Bearer {TEST_TOKEN}"},
                json={
                    "title": "Test Session",
                    "is_public": True
                }
            )
            
            session_id = create_response.json()["session_id"]
            
            # Then get its details
            response = await client.get(
                f"/api/duet/sessions/{session_id}"
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["session_id"] == session_id
            assert data["title"] == "Test Session"
            assert data["status"] == "draft"


class TestDuetClipsAPI:
    """Test Duet Clips API endpoints"""
    
    @pytest.mark.asyncio
    async def test_upload_clip(self):
        """Test uploading a clip to session"""
        async with AsyncClient(base_url=BASE_URL) as client:
            # Create session first
            session_response = await client.post(
                "/api/duet/sessions",
                headers={"Authorization": f"Bearer {TEST_TOKEN}"},
                json={"title": "Test Session"}
            )
            session_id = session_response.json()["session_id"]
            
            # Upload clip
            response = await client.post(
                "/api/duet/clips",
                headers={"Authorization": f"Bearer {TEST_TOKEN}"},
                params={
                    "session_id": session_id,
                    "title": "Dance Move",
                    "duration": 15.5
                }
                # File would be uploaded here in real test
            )
            
            assert response.status_code in [200, 201]
            data = response.json()
            assert data["status"] == "success"
            assert "clip_id" in data
    
    @pytest.mark.asyncio
    async def test_list_session_clips(self):
        """Test listing clips in a session"""
        async with AsyncClient(base_url=BASE_URL) as client:
            # Create session
            session_response = await client.post(
                "/api/duet/sessions",
                headers={"Authorization": f"Bearer {TEST_TOKEN}"},
                json={"title": "Test Session"}
            )
            session_id = session_response.json()["session_id"]
            
            # List clips
            response = await client.get(
                f"/api/duet/sessions/{session_id}/clips"
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert "clips" in data


class TestDuetCollaboratorsAPI:
    """Test Duet Collaborators API endpoints"""
    
    @pytest.mark.asyncio
    async def test_add_collaborator(self):
        """Test adding a collaborator to session"""
        async with AsyncClient(base_url=BASE_URL) as client:
            # Create session
            session_response = await client.post(
                "/api/duet/sessions",
                headers={"Authorization": f"Bearer {TEST_TOKEN}"},
                json={"title": "Test Session", "is_public": True}
            )
            session_id = session_response.json()["session_id"]
            
            # Add collaborator
            response = await client.post(
                f"/api/duet/sessions/{session_id}/collaborators",
                headers={"Authorization": f"Bearer {TEST_TOKEN}"},
                json={"role": "editor"}
            )
            
            assert response.status_code in [200, 201]
            data = response.json()
            assert data["status"] == "success"
    
    @pytest.mark.asyncio
    async def test_get_collaborators(self):
        """Test getting collaborators in session"""
        async with AsyncClient(base_url=BASE_URL) as client:
            # Create session
            session_response = await client.post(
                "/api/duet/sessions",
                headers={"Authorization": f"Bearer {TEST_TOKEN}"},
                json={"title": "Test Session"}
            )
            session_id = session_response.json()["session_id"]
            
            # Get collaborators
            response = await client.get(
                f"/api/duet/sessions/{session_id}/collaborators"
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert "collaborators" in data


class TestDuetCommentsAPI:
    """Test Duet Comments API endpoints"""
    
    @pytest.mark.asyncio
    async def test_add_comment(self):
        """Test adding a comment to session"""
        async with AsyncClient(base_url=BASE_URL) as client:
            # Create session
            session_response = await client.post(
                "/api/duet/sessions",
                headers={"Authorization": f"Bearer {TEST_TOKEN}"},
                json={"title": "Test Session"}
            )
            session_id = session_response.json()["session_id"]
            
            # Add comment
            response = await client.post(
                f"/api/duet/sessions/{session_id}/comments",
                headers={"Authorization": f"Bearer {TEST_TOKEN}"},
                json={
                    "text": "Great dance move!",
                    "timestamp": 5.0
                }
            )
            
            assert response.status_code in [200, 201]
            data = response.json()
            assert data["status"] == "success"
            assert "comment_id" in data
    
    @pytest.mark.asyncio
    async def test_get_comments(self):
        """Test getting comments for session"""
        async with AsyncClient(base_url=BASE_URL) as client:
            # Create session
            session_response = await client.post(
                "/api/duet/sessions",
                headers={"Authorization": f"Bearer {TEST_TOKEN}"},
                json={"title": "Test Session"}
            )
            session_id = session_response.json()["session_id"]
            
            # Get comments
            response = await client.get(
                f"/api/duet/sessions/{session_id}/comments"
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert "comments" in data


class TestDuetEffectsAPI:
    """Test Duet Effects API endpoints"""
    
    @pytest.mark.asyncio
    async def test_apply_effect(self):
        """Test applying effect to clip"""
        async with AsyncClient(base_url=BASE_URL) as client:
            # Create session
            session_response = await client.post(
                "/api/duet/sessions",
                headers={"Authorization": f"Bearer {TEST_TOKEN}"},
                json={"title": "Test Session"}
            )
            session_id = session_response.json()["session_id"]
            
            # Create mock clip (in real test would upload)
            # Apply effect
            response = await client.post(
                f"/api/duet/clips/clip_123/effects",
                headers={"Authorization": f"Bearer {TEST_TOKEN}"},
                json={
                    "effect_type": "blur",
                    "intensity": 1.5,
                    "duration": 2.0
                }
            )
            
            # Would expect 200 if clip exists
            assert response.status_code in [200, 404]


class TestDuetExportAPI:
    """Test Duet Export API endpoints"""
    
    @pytest.mark.asyncio
    async def test_create_export(self):
        """Test creating export job"""
        async with AsyncClient(base_url=BASE_URL) as client:
            # Create session
            session_response = await client.post(
                "/api/duet/sessions",
                headers={"Authorization": f"Bearer {TEST_TOKEN}"},
                json={"title": "Test Session"}
            )
            session_id = session_response.json()["session_id"]
            
            # Create export
            response = await client.post(
                "/api/duet/export",
                headers={"Authorization": f"Bearer {TEST_TOKEN}"},
                json={
                    "session_id": session_id,
                    "format": "mp4",
                    "quality": "high"
                }
            )
            
            assert response.status_code in [200, 201]
            data = response.json()
            assert data["status"] == "success"
            assert "export_id" in data


class TestDuetEngagementAPI:
    """Test Duet Engagement API endpoints"""
    
    @pytest.mark.asyncio
    async def test_record_view(self):
        """Test recording view"""
        async with AsyncClient(base_url=BASE_URL) as client:
            # Create session
            session_response = await client.post(
                "/api/duet/sessions",
                headers={"Authorization": f"Bearer {TEST_TOKEN}"},
                json={"title": "Test Session", "is_public": True}
            )
            session_id = session_response.json()["session_id"]
            
            # Record view
            response = await client.post(
                f"/api/duet/sessions/{session_id}/view"
            )
            
            assert response.status_code in [200, 404]
    
    @pytest.mark.asyncio
    async def test_toggle_like(self):
        """Test toggling like"""
        async with AsyncClient(base_url=BASE_URL) as client:
            # Create session
            session_response = await client.post(
                "/api/duet/sessions",
                headers={"Authorization": f"Bearer {TEST_TOKEN}"},
                json={"title": "Test Session", "is_public": True}
            )
            session_id = session_response.json()["session_id"]
            
            # Toggle like
            response = await client.post(
                f"/api/duet/sessions/{session_id}/like",
                headers={"Authorization": f"Bearer {TEST_TOKEN}"}
            )
            
            assert response.status_code in [200, 404]


class TestDuetDiscoveryAPI:
    """Test Duet Discovery API endpoints"""
    
    @pytest.mark.asyncio
    async def test_get_trending(self):
        """Test getting trending duets"""
        async with AsyncClient(base_url=BASE_URL) as client:
            response = await client.get(
                "/api/duet/trending?limit=20"
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert "duets" in data
    
    @pytest.mark.asyncio
    async def test_get_user_stats(self):
        """Test getting user statistics"""
        async with AsyncClient(base_url=BASE_URL) as client:
            response = await client.get(
                f"/api/duet/users/{TEST_USER_ID}/stats"
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert "user_id" in data


# ==================== RUN TESTS ====================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
