"""
Duet & Collab WebSocket Handler
Real-time collaboration, presence tracking, and live updates
"""

import json
import logging
from typing import Dict, List, Set
from datetime import datetime
from enum import Enum

from fastapi import WebSocket, WebSocketDisconnect
import asyncio

logger = logging.getLogger(__name__)


class WebSocketMessageType(str, Enum):
    """Message types for WebSocket communication"""
    # Session events
    SESSION_CREATED = "session_created"
    SESSION_UPDATED = "session_updated"
    SESSION_DELETED = "session_deleted"
    SESSION_CLOSED = "session_closed"
    
    # Clip events
    CLIP_ADDED = "clip_added"
    CLIP_UPDATED = "clip_updated"
    CLIP_DELETED = "clip_deleted"
    CLIP_PROCESSING = "clip_processing"
    CLIP_READY = "clip_ready"
    
    # Collaborator events
    COLLABORATOR_JOINED = "collaborator_joined"
    COLLABORATOR_LEFT = "collaborator_left"
    COLLABORATOR_STATUS_CHANGED = "collaborator_status_changed"
    
    # Effect events
    EFFECT_APPLIED = "effect_applied"
    EFFECT_REMOVED = "effect_removed"
    
    # Comment events
    COMMENT_ADDED = "comment_added"
    COMMENT_DELETED = "comment_deleted"
    COMMENT_PINNED = "comment_pinned"
    
    # Engagement events
    LIKE_TOGGLED = "like_toggled"
    VIEWER_COUNT_UPDATED = "viewer_count_updated"
    
    # Export events
    EXPORT_STARTED = "export_started"
    EXPORT_PROGRESS = "export_progress"
    EXPORT_COMPLETED = "export_completed"
    EXPORT_FAILED = "export_failed"
    
    # Control events
    SYNC_REQUEST = "sync_request"
    SYNC_RESPONSE = "sync_response"
    PING = "ping"
    PONG = "pong"


class DuetCollabWebSocketManager:
    """Manages WebSocket connections for real-time collaboration"""
    
    def __init__(self):
        # session_id -> {user_id -> WebSocket}
        self.active_sessions: Dict[str, Dict[str, WebSocket]] = {}
        # user_id -> set of session_ids
        self.user_sessions: Dict[str, Set[str]] = {}
        # session_id -> {user_id -> {status, timestamp, ...}}
        self.presence_data: Dict[str, Dict[str, Dict]] = {}
        # Lock for thread-safe operations
        self.lock = asyncio.Lock()

    async def connect(self, session_id: str, user_id: str, websocket: WebSocket):
        """Register a new connection"""
        await websocket.accept()
        
        async with self.lock:
            # Add to active sessions
            if session_id not in self.active_sessions:
                self.active_sessions[session_id] = {}
                self.presence_data[session_id] = {}
            
            self.active_sessions[session_id][user_id] = websocket
            
            # Track user's sessions
            if user_id not in self.user_sessions:
                self.user_sessions[user_id] = set()
            self.user_sessions[user_id].add(session_id)
            
            # Update presence
            self.presence_data[session_id][user_id] = {
                "user_id": user_id,
                "status": "viewing",
                "connected_at": datetime.utcnow().isoformat(),
                "is_online": True
            }
        
        # Notify others that user joined
        await self.broadcast(
            session_id,
            {
                "type": WebSocketMessageType.COLLABORATOR_JOINED.value,
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat()
            },
            exclude_user=user_id
        )
        
        # Send current presence to new user
        await websocket.send_json({
            "type": "presence_snapshot",
            "collaborators": list(self.presence_data[session_id].values())
        })
        
        logger.info(f"User {user_id} connected to session {session_id}")

    async def disconnect(self, session_id: str, user_id: str):
        """Handle user disconnect"""
        async with self.lock:
            if session_id in self.active_sessions:
                self.active_sessions[session_id].pop(user_id, None)
                
                # Remove empty sessions
                if not self.active_sessions[session_id]:
                    del self.active_sessions[session_id]
                    del self.presence_data[session_id]
            
            # Remove from user sessions
            if user_id in self.user_sessions:
                self.user_sessions[user_id].discard(session_id)
                if not self.user_sessions[user_id]:
                    del self.user_sessions[user_id]
            
            # Update presence
            if session_id in self.presence_data:
                self.presence_data[session_id].pop(user_id, None)
        
        # Notify others that user left
        await self.broadcast(
            session_id,
            {
                "type": WebSocketMessageType.COLLABORATOR_LEFT.value,
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        logger.info(f"User {user_id} disconnected from session {session_id}")

    async def broadcast(self, session_id: str, message: dict, exclude_user: str = None):
        """Broadcast message to all users in a session"""
        async with self.lock:
            if session_id not in self.active_sessions:
                return
            
            websockets = self.active_sessions[session_id]
        
        if not websockets:
            return
        
        # Add server timestamp
        message["server_timestamp"] = datetime.utcnow().isoformat()
        
        # Send to all connected users
        disconnected_users = []
        for user_id, websocket in websockets.items():
            if exclude_user and user_id == exclude_user:
                continue
            
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error sending message to {user_id}: {str(e)}")
                disconnected_users.append(user_id)
        
        # Cleanup disconnected users
        for user_id in disconnected_users:
            await self.disconnect(session_id, user_id)

    async def update_presence(self, session_id: str, user_id: str, status: str):
        """Update user's presence status"""
        async with self.lock:
            if session_id in self.presence_data and user_id in self.presence_data[session_id]:
                self.presence_data[session_id][user_id]["status"] = status
                self.presence_data[session_id][user_id]["last_activity"] = datetime.utcnow().isoformat()
        
        # Broadcast status change
        await self.broadcast(
            session_id,
            {
                "type": WebSocketMessageType.COLLABORATOR_STATUS_CHANGED.value,
                "user_id": user_id,
                "status": status,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

    async def notify_clip_added(self, session_id: str, clip_data: dict):
        """Notify all users of new clip"""
        await self.broadcast(
            session_id,
            {
                "type": WebSocketMessageType.CLIP_ADDED.value,
                "clip": clip_data,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

    async def notify_effect_applied(self, session_id: str, clip_id: str, effect_data: dict):
        """Notify all users of applied effect"""
        await self.broadcast(
            session_id,
            {
                "type": WebSocketMessageType.EFFECT_APPLIED.value,
                "clip_id": clip_id,
                "effect": effect_data,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

    async def notify_comment_added(self, session_id: str, comment_data: dict):
        """Notify all users of new comment"""
        await self.broadcast(
            session_id,
            {
                "type": WebSocketMessageType.COMMENT_ADDED.value,
                "comment": comment_data,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

    async def notify_export_progress(self, session_id: str, export_id: str, progress: int):
        """Notify progress on export"""
        await self.broadcast(
            session_id,
            {
                "type": WebSocketMessageType.EXPORT_PROGRESS.value,
                "export_id": export_id,
                "progress": progress,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

    async def notify_export_completed(self, session_id: str, export_id: str, video_url: str):
        """Notify export completion"""
        await self.broadcast(
            session_id,
            {
                "type": WebSocketMessageType.EXPORT_COMPLETED.value,
                "export_id": export_id,
                "video_url": video_url,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

    async def update_viewer_count(self, session_id: str, count: int):
        """Update live viewer count"""
        await self.broadcast(
            session_id,
            {
                "type": WebSocketMessageType.VIEWER_COUNT_UPDATED.value,
                "live_viewers": count,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

    async def get_online_count(self, session_id: str) -> int:
        """Get number of online users in session"""
        async with self.lock:
            if session_id in self.active_sessions:
                return len(self.active_sessions[session_id])
        return 0

    async def get_presence(self, session_id: str) -> List[dict]:
        """Get presence data for session"""
        async with self.lock:
            if session_id in self.presence_data:
                return list(self.presence_data[session_id].values())
        return []

    async def close_session(self, session_id: str):
        """Close session and disconnect all users"""
        async with self.lock:
            if session_id in self.active_sessions:
                websockets = list(self.active_sessions[session_id].values())
        
        # Notify all users
        await self.broadcast(
            session_id,
            {
                "type": WebSocketMessageType.SESSION_CLOSED.value,
                "message": "Session has been closed by creator",
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        # Close all connections
        for websocket in websockets:
            try:
                await websocket.close(code=1000)
            except Exception as e:
                logger.error(f"Error closing connection: {str(e)}")


# Global manager instance
duet_ws_manager = DuetCollabWebSocketManager()


# ==================== WEBSOCKET ENDPOINT HANDLER ====================

async def handle_duet_websocket(websocket: WebSocket, session_id: str, user_id: str):
    """Handle WebSocket connection for duet collaboration"""
    
    try:
        # Connect user to session
        await duet_ws_manager.connect(session_id, user_id, websocket)
        
        # Keep connection alive and handle incoming messages
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            message_type = message.get("type")
            
            # Handle ping-pong
            if message_type == WebSocketMessageType.PING.value:
                await websocket.send_json({
                    "type": WebSocketMessageType.PONG.value,
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            # Handle status updates
            elif message_type == WebSocketMessageType.COLLABORATOR_STATUS_CHANGED.value:
                status = message.get("status", "idle")
                await duet_ws_manager.update_presence(session_id, user_id, status)
            
            # Handle clip addition
            elif message_type == WebSocketMessageType.CLIP_ADDED.value:
                await duet_ws_manager.notify_clip_added(
                    session_id,
                    {
                        **message.get("clip", {}),
                        "contributor_id": user_id
                    }
                )
            
            # Handle effect application
            elif message_type == WebSocketMessageType.EFFECT_APPLIED.value:
                await duet_ws_manager.notify_effect_applied(
                    session_id,
                    message.get("clip_id"),
                    message.get("effect")
                )
            
            # Handle comment addition
            elif message_type == WebSocketMessageType.COMMENT_ADDED.value:
                await duet_ws_manager.notify_comment_added(
                    session_id,
                    {
                        **message.get("comment", {}),
                        "author_id": user_id
                    }
                )
            
            # Handle sync requests
            elif message_type == WebSocketMessageType.SYNC_REQUEST.value:
                presence = await duet_ws_manager.get_presence(session_id)
                await websocket.send_json({
                    "type": WebSocketMessageType.SYNC_RESPONSE.value,
                    "collaborators": presence,
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            # Broadcast other messages to all users
            else:
                await duet_ws_manager.broadcast(
                    session_id,
                    message,
                    exclude_user=user_id
                )
            
            logger.debug(f"Message from {user_id}: {message_type}")
    
    except WebSocketDisconnect:
        await duet_ws_manager.disconnect(session_id, user_id)
    
    except Exception as e:
        logger.error(f"WebSocket error for {user_id}: {str(e)}")
        try:
            await websocket.close(code=1011, reason=str(e))
        except:
            pass
        await duet_ws_manager.disconnect(session_id, user_id)


# ==================== HELPER FUNCTIONS ====================

async def notify_all_sessions(message: dict):
    """Broadcast message to all active sessions"""
    async with duet_ws_manager.lock:
        sessions = list(duet_ws_manager.active_sessions.keys())
    
    for session_id in sessions:
        await duet_ws_manager.broadcast(session_id, message)


async def cleanup_inactive_users(session_id: str, timeout_seconds: int = 300):
    """Remove inactive users from session after timeout"""
    async with duet_ws_manager.lock:
        if session_id not in duet_ws_manager.presence_data:
            return
        
        presence = duet_ws_manager.presence_data[session_id]
        now = datetime.utcnow()
    
    inactive_users = []
    for user_id, data in presence.items():
        last_activity = datetime.fromisoformat(data["last_activity"])
        if (now - last_activity).total_seconds() > timeout_seconds:
            inactive_users.append(user_id)
    
    for user_id in inactive_users:
        await duet_ws_manager.disconnect(session_id, user_id)
        logger.info(f"Removed inactive user {user_id} from session {session_id}")
