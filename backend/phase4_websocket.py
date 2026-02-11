"""
PHASE 4: Real-time WebSocket Infrastructure
Production-grade real-time communication engine for VIDEOS platform
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Set, Optional, List, Any
from enum import Enum
import uuid
from collections import defaultdict

from fastapi import WebSocket, WebSocketDisconnect, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
import redis.asyncio as aioredis


logger = logging.getLogger(__name__)


class MessageType(str, Enum):
    """Real-time message types"""
    CHAT = "chat"
    NOTIFICATION = "notification"
    TYPING = "typing"
    STATUS = "status"
    LIVE_VIEW_UPDATE = "live_view_update"
    ENGAGEMENT_UPDATE = "engagement_update"
    SYSTEM = "system"


class ConnectionManager:
    """Manages WebSocket connections with connection pooling and recovery"""
    
    def __init__(self, redis_client: aioredis.Redis, db: AsyncIOMotorDatabase):
        self.redis = redis_client
        self.db = db
        self.active_connections: Dict[str, Set[WebSocket]] = defaultdict(set)
        self.user_sockets: Dict[str, WebSocket] = {}
        self.connection_metadata: Dict[str, Dict[str, Any]] = {}
        self.message_queue: asyncio.Queue = asyncio.Queue(maxsize=10000)
        
    async def connect(
        self, 
        websocket: WebSocket, 
        user_id: str, 
        channel: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Accept WebSocket connection with metadata tracking"""
        await websocket.accept()
        
        conn_id = str(uuid.uuid4())
        self.active_connections[channel].add(websocket)
        self.user_sockets[user_id] = websocket
        
        # Store connection metadata
        self.connection_metadata[conn_id] = {
            "user_id": user_id,
            "channel": channel,
            "connected_at": datetime.utcnow().isoformat(),
            "last_heartbeat": datetime.utcnow().isoformat(),
            "metadata": metadata or {},
        }
        
        # Store in Redis for distributed access
        await self.redis.setex(
            f"ws:connection:{conn_id}",
            3600,  # 1 hour TTL
            json.dumps(self.connection_metadata[conn_id])
        )
        
        # Track active connections per channel
        await self.redis.incr(f"channel:active:{channel}")
        
        logger.info(f"User {user_id} connected to {channel} (conn_id: {conn_id})")
        
        return conn_id
    
    async def disconnect(self, conn_id: str) -> None:
        """Gracefully disconnect WebSocket"""
        if conn_id not in self.connection_metadata:
            return
            
        metadata = self.connection_metadata[conn_id]
        user_id = metadata["user_id"]
        channel = metadata["channel"]
        
        # Find and remove socket
        for websocket in list(self.active_connections[channel]):
            try:
                await websocket.close()
                self.active_connections[channel].discard(websocket)
            except Exception:
                pass
        
        # Cleanup metadata
        del self.connection_metadata[conn_id]
        if user_id in self.user_sockets:
            del self.user_sockets[user_id]
        
        # Update Redis
        await self.redis.decr(f"channel:active:{channel}")
        await self.redis.delete(f"ws:connection:{conn_id}")
        
        logger.info(f"User {user_id} disconnected from {channel}")
    
    async def broadcast(
        self, 
        channel: str, 
        message: Dict[str, Any],
        exclude_user: Optional[str] = None
    ) -> int:
        """Broadcast message to all users in channel"""
        sent_count = 0
        failed_connections = []
        
        for websocket in list(self.active_connections[channel]):
            try:
                # Check if should exclude
                user_id = self._get_user_for_socket(websocket)
                if exclude_user and user_id == exclude_user:
                    continue
                
                # Send with timeout
                await asyncio.wait_for(
                    websocket.send_json(message),
                    timeout=5.0
                )
                sent_count += 1
            except asyncio.TimeoutError:
                failed_connections.append(websocket)
                logger.warning(f"Timeout sending to socket in {channel}")
            except Exception as e:
                failed_connections.append(websocket)
                logger.error(f"Error broadcasting to {channel}: {e}")
        
        # Clean up failed connections
        for websocket in failed_connections:
            self.active_connections[channel].discard(websocket)
        
        return sent_count
    
    async def unicast(
        self, 
        user_id: str, 
        message: Dict[str, Any]
    ) -> bool:
        """Send message to specific user"""
        if user_id not in self.user_sockets:
            return False
        
        try:
            websocket = self.user_sockets[user_id]
            await asyncio.wait_for(
                websocket.send_json(message),
                timeout=5.0
            )
            return True
        except Exception as e:
            logger.error(f"Error sending to user {user_id}: {e}")
            return False
    
    async def multicast(
        self, 
        user_ids: List[str], 
        message: Dict[str, Any]
    ) -> int:
        """Send message to multiple specific users"""
        sent_count = 0
        for user_id in user_ids:
            if await self.unicast(user_id, message):
                sent_count += 1
        return sent_count
    
    def _get_user_for_socket(self, websocket: WebSocket) -> Optional[str]:
        """Get user ID for a WebSocket"""
        for user_id, ws in self.user_sockets.items():
            if ws == websocket:
                return user_id
        return None
    
    async def get_channel_stats(self, channel: str) -> Dict[str, Any]:
        """Get real-time channel statistics"""
        active_count = await self.redis.get(f"channel:active:{channel}") or 0
        
        return {
            "channel": channel,
            "active_connections": int(active_count),
            "total_sockets": len(self.active_connections[channel]),
            "timestamp": datetime.utcnow().isoformat(),
        }


class ChatManager:
    """Manages real-time chat messages with persistence"""
    
    def __init__(self, redis: aioredis.Redis, db: AsyncIOMotorDatabase):
        self.redis = redis
        self.db = db
        self.messages_collection = db["realtime_messages"]
    
    async def save_message(
        self,
        user_id: str,
        channel: str,
        content: str,
        message_type: MessageType = MessageType.CHAT
    ) -> Dict[str, Any]:
        """Save chat message to database and cache"""
        message_id = str(uuid.uuid4())
        
        message = {
            "_id": message_id,
            "user_id": user_id,
            "channel": channel,
            "content": content,
            "type": message_type.value,
            "created_at": datetime.utcnow(),
            "read_by": [],
        }
        
        # Save to MongoDB
        await self.messages_collection.insert_one(message)
        
        # Cache in Redis (sorted set by timestamp)
        await self.redis.zadd(
            f"chat:{channel}",
            {message_id: datetime.utcnow().timestamp()}
        )
        
        # Set expiration (30 days)
        await self.redis.expire(f"chat:{channel}", 2592000)
        
        return message
    
    async def get_recent_messages(
        self,
        channel: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get recent messages with Redis caching"""
        cache_key = f"chat_recent:{channel}"
        
        # Try cache first
        cached = await self.redis.get(cache_key)
        if cached:
            return json.loads(cached)
        
        # Query database
        messages = await self.messages_collection.find(
            {"channel": channel},
            sort=[("created_at", -1)],
            limit=limit
        ).to_list(limit)
        
        # Convert ObjectId to string
        for msg in messages:
            msg["_id"] = str(msg["_id"])
            msg["created_at"] = msg["created_at"].isoformat()
        
        messages = list(reversed(messages))
        
        # Cache for 5 minutes
        await self.redis.setex(
            cache_key,
            300,
            json.dumps(messages)
        )
        
        return messages
    
    async def mark_as_read(
        self,
        message_id: str,
        user_id: str
    ) -> bool:
        """Mark message as read by user"""
        result = await self.messages_collection.update_one(
            {"_id": message_id},
            {"$addToSet": {"read_by": user_id}}
        )
        
        # Invalidate cache
        await self.redis.delete("chat_recent:*")
        
        return result.modified_count > 0


class NotificationManager:
    """Manages real-time notifications with delivery tracking"""
    
    def __init__(self, redis: aioredis.Redis, db: AsyncIOMotorDatabase):
        self.redis = redis
        self.db = db
        self.notifications_collection = db["notifications"]
    
    async def create_notification(
        self,
        user_id: str,
        title: str,
        content: str,
        action_url: Optional[str] = None,
        notification_type: str = "info"
    ) -> Dict[str, Any]:
        """Create and store notification"""
        notification_id = str(uuid.uuid4())
        
        notification = {
            "_id": notification_id,
            "user_id": user_id,
            "title": title,
            "content": content,
            "action_url": action_url,
            "type": notification_type,
            "created_at": datetime.utcnow(),
            "read_at": None,
            "delivered_at": None,
        }
        
        # Save to database
        await self.notifications_collection.insert_one(notification)
        
        # Store in Redis with 7-day TTL
        await self.redis.setex(
            f"notification:{notification_id}",
            604800,
            json.dumps({
                "user_id": user_id,
                "title": title,
                "content": content,
                "action_url": action_url,
                "type": notification_type,
            }, default=str)
        )
        
        # Add to user's notification queue
        await self.redis.rpush(
            f"user:notifications:{user_id}",
            notification_id
        )
        
        return notification
    
    async def mark_as_delivered(
        self,
        notification_id: str
    ) -> bool:
        """Mark notification as delivered"""
        result = await self.notifications_collection.update_one(
            {"_id": notification_id},
            {"$set": {"delivered_at": datetime.utcnow()}}
        )
        return result.modified_count > 0
    
    async def mark_as_read(
        self,
        notification_id: str
    ) -> bool:
        """Mark notification as read"""
        result = await self.notifications_collection.update_one(
            {"_id": notification_id},
            {"$set": {"read_at": datetime.utcnow()}}
        )
        return result.modified_count > 0
    
    async def get_user_notifications(
        self,
        user_id: str,
        unread_only: bool = False
    ) -> List[Dict[str, Any]]:
        """Get user's notifications"""
        query = {"user_id": user_id}
        if unread_only:
            query["read_at"] = None
        
        notifications = await self.notifications_collection.find(
            query,
            sort=[("created_at", -1)],
            limit=100
        ).to_list(100)
        
        # Convert timestamps to ISO format
        for notif in notifications:
            notif["_id"] = str(notif["_id"])
            notif["created_at"] = notif["created_at"].isoformat()
            if notif["read_at"]:
                notif["read_at"] = notif["read_at"].isoformat()
            if notif["delivered_at"]:
                notif["delivered_at"] = notif["delivered_at"].isoformat()
        
        return notifications


class LiveMetricsManager:
    """Real-time metrics for live streams and video engagement"""
    
    def __init__(self, redis: aioredis.Redis, db: AsyncIOMotorDatabase):
        self.redis = redis
        self.db = db
        self.metrics_collection = db["live_metrics"]
    
    async def increment_view_count(
        self,
        video_id: str,
        user_id: str
    ) -> int:
        """Increment view count for video"""
        # Use Redis for real-time counter
        count = await self.redis.incr(f"video:views:{video_id}")
        
        # Track unique viewers
        await self.redis.sadd(f"video:viewers:{video_id}", user_id)
        
        # Persist every 100 views or on schedule
        if count % 100 == 0:
            await self._persist_metrics(video_id)
        
        return count
    
    async def add_engagement_event(
        self,
        video_id: str,
        user_id: str,
        event_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Record engagement event (like, comment, share)"""
        event = {
            "video_id": video_id,
            "user_id": user_id,
            "event_type": event_type,
            "timestamp": datetime.utcnow(),
            "metadata": metadata or {},
        }
        
        # Store in time-series Redis structure
        await self.redis.zadd(
            f"engagement:{video_id}",
            {json.dumps(event, default=str): datetime.utcnow().timestamp()}
        )
        
        # Batch insert to database every 50 events
        count = await self.redis.zcard(f"engagement:{video_id}")
        if count % 50 == 0:
            await self._flush_engagement_events(video_id)
    
    async def get_live_metrics(self, video_id: str) -> Dict[str, Any]:
        """Get real-time metrics for video"""
        views = await self.redis.get(f"video:views:{video_id}") or 0
        unique_viewers = await self.redis.scard(f"video:viewers:{video_id}")
        
        # Get recent engagement events
        recent_events = await self.redis.zrange(
            f"engagement:{video_id}",
            -100,  # Last 100 events
            -1
        )
        
        engagement_counts = defaultdict(int)
        for event_json in recent_events:
            event = json.loads(event_json)
            engagement_counts[event["event_type"]] += 1
        
        return {
            "video_id": video_id,
            "views": int(views),
            "unique_viewers": unique_viewers,
            "engagements": dict(engagement_counts),
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    async def _persist_metrics(self, video_id: str) -> None:
        """Persist real-time metrics to database"""
        views = await self.redis.get(f"video:views:{video_id}") or 0
        unique_viewers = await self.redis.scard(f"video:viewers:{video_id}")
        
        await self.metrics_collection.update_one(
            {"video_id": video_id},
            {
                "$set": {
                    "views": int(views),
                    "unique_viewers": unique_viewers,
                    "last_updated": datetime.utcnow(),
                }
            },
            upsert=True
        )
    
    async def _flush_engagement_events(self, video_id: str) -> None:
        """Flush engagement events to database"""
        events_json = await self.redis.zrange(f"engagement:{video_id}", 0, -1)
        
        if not events_json:
            return
        
        events = [json.loads(e) for e in events_json]
        
        # Batch insert
        if events:
            await self.metrics_collection.insert_many(events)
        
        # Clear Redis queue
        await self.redis.delete(f"engagement:{video_id}")


class PresenceManager:
    """Track user presence across platform"""
    
    def __init__(self, redis: aioredis.Redis):
        self.redis = redis
    
    async def set_user_online(
        self,
        user_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Mark user as online"""
        presence_data = {
            "user_id": user_id,
            "online": True,
            "last_seen": datetime.utcnow().isoformat(),
            "metadata": metadata or {},
        }
        
        # Store with 24-hour TTL
        await self.redis.setex(
            f"user:presence:{user_id}",
            86400,
            json.dumps(presence_data)
        )
        
        # Add to online users set
        await self.redis.sadd("online_users", user_id)
    
    async def set_user_offline(self, user_id: str) -> None:
        """Mark user as offline"""
        await self.redis.delete(f"user:presence:{user_id}")
        await self.redis.srem("online_users", user_id)
        
        # Store last seen time
        await self.redis.setex(
            f"user:last_seen:{user_id}",
            2592000,  # 30 days
            datetime.utcnow().isoformat()
        )
    
    async def is_user_online(self, user_id: str) -> bool:
        """Check if user is online"""
        return await self.redis.exists(f"user:presence:{user_id}") > 0
    
    async def get_online_users_count(self) -> int:
        """Get count of online users"""
        return await self.redis.scard("online_users")
    
    async def get_user_presence(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user presence data"""
        data = await self.redis.get(f"user:presence:{user_id}")
        if data:
            return json.loads(data)
        return None
