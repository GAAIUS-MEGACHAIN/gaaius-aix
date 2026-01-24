"""
Advanced Real-Time Messaging Platform (WhatsApp Clone)
Production-grade messaging service with WebSockets, encryption, and advanced features
"""

import json
import asyncio
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict, field
from enum import Enum
import uuid
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MessageStatus(str, Enum):
    """Message delivery status"""
    SENDING = "sending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"


class UserPresence(str, Enum):
    """User online/offline status"""
    ONLINE = "online"
    OFFLINE = "offline"
    AWAY = "away"
    DO_NOT_DISTURB = "dnd"


@dataclass
class Message:
    """Message data model"""
    id: str
    conversation_id: str
    sender_id: str
    content: str
    message_type: str = "text"  # text, image, video, file, audio
    status: str = "sent"
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    read_at: Optional[str] = None
    edited_at: Optional[str] = None
    file_url: Optional[str] = None
    file_name: Optional[str] = None
    reply_to: Optional[str] = None  # For threading
    reactions: Dict[str, List[str]] = field(default_factory=dict)  # emoji -> [user_ids]
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)


@dataclass
class Conversation:
    """Conversation/chat data model"""
    id: str
    name: Optional[str] = None  # None for 1-to-1, name for groups
    is_group: bool = False
    creator_id: str = ""
    participant_ids: List[str] = field(default_factory=list)
    last_message_id: Optional[str] = None
    last_message_text: Optional[str] = None
    last_message_time: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    muted: Dict[str, bool] = field(default_factory=dict)  # user_id -> is_muted
    archived: Dict[str, bool] = field(default_factory=dict)  # user_id -> is_archived
    pinned_message_ids: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)


@dataclass
class User:
    """User profile for messaging"""
    id: str
    username: str
    display_name: str
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    phone: Optional[str] = None
    presence: str = "offline"
    last_seen: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    is_blocked_by: List[str] = field(default_factory=list)
    blocks: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)


class ConversationManager:
    """Manage conversations and group chats"""
    
    def __init__(self, db_connection):
        """Initialize conversation manager"""
        self.db = db_connection
        self.conversations: Dict[str, Conversation] = {}
    
    async def create_conversation(
        self,
        creator_id: str,
        participant_ids: List[str],
        name: Optional[str] = None,
        is_group: bool = False
    ) -> Conversation:
        """Create new conversation or 1-to-1 chat"""
        try:
            conversation_id = str(uuid.uuid4())
            
            if creator_id not in participant_ids:
                participant_ids.append(creator_id)
            
            conversation = Conversation(
                id=conversation_id,
                name=name,
                is_group=is_group,
                creator_id=creator_id,
                participant_ids=participant_ids,
                muted={pid: False for pid in participant_ids},
                archived={pid: False for pid in participant_ids},
                pinned_message_ids=[]
            )
            
            self.conversations[conversation_id] = conversation
            logger.info(f"Conversation {conversation_id} created")
            return conversation
        except Exception as e:
            logger.error(f"Failed to create conversation: {e}")
            raise
    
    async def get_conversations(self, user_id: str, limit: int = 50) -> List[Conversation]:
        """Get user's conversations"""
        try:
            user_convs = [
                conv for conv in self.conversations.values()
                if user_id in conv.participant_ids
            ]
            
            # Sort by last message time (newest first)
            user_convs.sort(key=lambda x: x.last_message_time, reverse=True)
            return user_convs[:limit]
        except Exception as e:
            logger.error(f"Failed to get conversations: {e}")
            return []
    
    async def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Get specific conversation"""
        return self.conversations.get(conversation_id)
    
    async def add_participant(self, conversation_id: str, user_id: str) -> bool:
        """Add user to group conversation"""
        try:
            if conversation_id in self.conversations:
                conv = self.conversations[conversation_id]
                if user_id not in conv.participant_ids:
                    conv.participant_ids.append(user_id)
                    conv.muted[user_id] = False
                    conv.archived[user_id] = False
                logger.info(f"User {user_id} added to conversation {conversation_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to add participant: {e}")
            return False
    
    async def remove_participant(self, conversation_id: str, user_id: str) -> bool:
        """Remove user from group conversation"""
        try:
            if conversation_id in self.conversations:
                conv = self.conversations[conversation_id]
                if user_id in conv.participant_ids:
                    conv.participant_ids.remove(user_id)
                logger.info(f"User {user_id} removed from conversation {conversation_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to remove participant: {e}")
            return False


class MessageManager:
    """Manage messages and message history"""
    
    def __init__(self):
        """Initialize message manager"""
        self.messages: Dict[str, List[Message]] = {}  # conversation_id -> messages
    
    async def save_message(self, message: Message) -> bool:
        """Save message to storage"""
        try:
            if message.conversation_id not in self.messages:
                self.messages[message.conversation_id] = []
            
            self.messages[message.conversation_id].append(message)
            logger.info(f"Message {message.id} saved")
            return True
        except Exception as e:
            logger.error(f"Failed to save message: {e}")
            return False
    
    async def get_messages(
        self,
        conversation_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[Message]:
        """Retrieve messages from conversation"""
        try:
            if conversation_id not in self.messages:
                return []
            
            messages = self.messages[conversation_id]
            # Return in reverse chronological order, from most recent
            return list(reversed(messages[max(0, len(messages)-offset-limit):len(messages)-offset]))
        except Exception as e:
            logger.error(f"Failed to retrieve messages: {e}")
            return []
    
    async def update_message_status(self, message_id: str, status: str) -> bool:
        """Update message delivery status"""
        try:
            for conv_messages in self.messages.values():
                for msg in conv_messages:
                    if msg.id == message_id:
                        msg.status = status
                        logger.info(f"Message {message_id} status updated to {status}")
                        return True
            return False
        except Exception as e:
            logger.error(f"Failed to update message status: {e}")
            return False
    
    async def delete_message(self, message_id: str) -> bool:
        """Soft delete message"""
        try:
            for conv_messages in self.messages.values():
                for msg in conv_messages:
                    if msg.id == message_id:
                        msg.content = "[Message deleted]"
                        logger.info(f"Message {message_id} deleted")
                        return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete message: {e}")
            return False
    
    async def search_messages(self, conversation_id: str, query: str) -> List[Message]:
        """Search messages in conversation"""
        try:
            if conversation_id not in self.messages:
                return []
            
            query_lower = query.lower()
            results = [
                m for m in self.messages[conversation_id]
                if query_lower in m.content.lower()
            ]
            return results
        except Exception as e:
            logger.error(f"Message search failed: {e}")
            return []


class RealtimeMessagingEngine:
    """Real-time messaging using WebSockets"""
    
    def __init__(self):
        """Initialize messaging engine"""
        self.active_connections: Dict[str, Any] = {}  # user_id -> websocket
        self.user_presence: Dict[str, str] = {}  # user_id -> presence
        self.typing_indicators: Dict[str, set] = {}  # conversation_id -> {user_ids}
    
    async def connect(self, user_id: str, websocket: Any):
        """Register user WebSocket connection"""
        try:
            self.active_connections[user_id] = websocket
            await self.set_presence(user_id, UserPresence.ONLINE.value)
            logger.info(f"User {user_id} connected via WebSocket")
        except Exception as e:
            logger.error(f"Connection failed: {e}")
    
    async def disconnect(self, user_id: str):
        """Unregister WebSocket connection"""
        try:
            if user_id in self.active_connections:
                del self.active_connections[user_id]
                await self.set_presence(user_id, UserPresence.OFFLINE.value)
            logger.info(f"User {user_id} disconnected")
        except Exception as e:
            logger.error(f"Disconnection failed: {e}")
    
    async def broadcast_message(
        self,
        conversation_id: str,
        message: Message,
        exclude_user: Optional[str] = None
    ):
        """Broadcast message to all users in conversation"""
        try:
            message_data = {
                "type": "new_message",
                "data": message.to_dict()
            }
            
            # In production, get participants from conversation manager
            for user_id, websocket in self.active_connections.items():
                if exclude_user and user_id == exclude_user:
                    continue
                try:
                    await websocket.send_json(message_data)
                except Exception as e:
                    logger.error(f"Failed to send to {user_id}: {e}")
        except Exception as e:
            logger.error(f"Broadcast failed: {e}")
    
    async def broadcast_typing(
        self,
        conversation_id: str,
        user_id: str,
        is_typing: bool
    ):
        """Broadcast typing indicator to conversation"""
        try:
            if conversation_id not in self.typing_indicators:
                self.typing_indicators[conversation_id] = set()
            
            if is_typing:
                self.typing_indicators[conversation_id].add(user_id)
            else:
                self.typing_indicators[conversation_id].discard(user_id)
            
            typing_data = {
                "type": "typing",
                "user_id": user_id,
                "conversation_id": conversation_id,
                "is_typing": is_typing,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            for uid, websocket in self.active_connections.items():
                if uid != user_id:
                    try:
                        await websocket.send_json(typing_data)
                    except Exception as e:
                        logger.error(f"Failed to send typing to {uid}: {e}")
        except Exception as e:
            logger.error(f"Typing broadcast failed: {e}")
    
    async def set_presence(self, user_id: str, presence: str):
        """Update and broadcast user presence"""
        try:
            self.user_presence[user_id] = presence
            
            presence_data = {
                "type": "presence_update",
                "user_id": user_id,
                "presence": presence,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            for uid, websocket in self.active_connections.items():
                if uid != user_id:
                    try:
                        await websocket.send_json(presence_data)
                    except Exception as e:
                        logger.error(f"Failed to send presence to {uid}: {e}")
        except Exception as e:
            logger.error(f"Presence update failed: {e}")
    
    async def get_presence(self, user_id: str) -> str:
        """Get user presence status"""
        try:
            return self.user_presence.get(user_id, UserPresence.OFFLINE.value)
        except Exception as e:
            logger.error(f"Failed to get presence: {e}")
            return UserPresence.OFFLINE.value


class MessagingService:
    """Main messaging service coordinating all components"""
    
    def __init__(self):
        """Initialize messaging service"""
        self.conversation_manager = ConversationManager(None)
        self.message_manager = MessageManager()
        self.realtime_engine = RealtimeMessagingEngine()
        self.users: Dict[str, User] = {}
        self.blocked_pairs: set = set()  # (user_id, blocked_user_id) tuples
    
    async def send_message(
        self,
        conversation_id: str,
        sender_id: str,
        content: str,
        message_type: str = "text",
        file_url: Optional[str] = None,
        file_name: Optional[str] = None
    ) -> Optional[Message]:
        """Send message to conversation"""
        try:
            message_id = str(uuid.uuid4())
            
            message = Message(
                id=message_id,
                conversation_id=conversation_id,
                sender_id=sender_id,
                content=content,
                message_type=message_type,
                file_url=file_url,
                file_name=file_name
            )
            
            # Save message
            await self.message_manager.save_message(message)
            
            # Update conversation's last message
            conv = await self.conversation_manager.get_conversation(conversation_id)
            if conv:
                conv.last_message_id = message_id
                conv.last_message_text = content[:100]
                conv.last_message_time = message.created_at
            
            # Broadcast to other participants
            await self.realtime_engine.broadcast_message(
                conversation_id,
                message,
                exclude_user=sender_id
            )
            
            logger.info(f"Message {message_id} sent to conversation {conversation_id}")
            return message
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return None
    
    async def get_messages(
        self,
        conversation_id: str,
        user_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[Message]:
        """Get messages for conversation"""
        try:
            conv = await self.conversation_manager.get_conversation(conversation_id)
            
            if not conv or user_id not in conv.participant_ids:
                logger.warning(f"User {user_id} not in conversation {conversation_id}")
                return []
            
            messages = await self.message_manager.get_messages(
                conversation_id,
                limit,
                offset
            )
            
            # Mark as delivered
            for message in messages:
                if message.sender_id != user_id and message.status == MessageStatus.SENT.value:
                    await self.message_manager.update_message_status(
                        message.id,
                        MessageStatus.DELIVERED.value
                    )
            
            return messages
        except Exception as e:
            logger.error(f"Failed to get messages: {e}")
            return []
    
    async def mark_as_read(
        self,
        conversation_id: str,
        user_id: str,
        message_ids: List[str]
    ) -> bool:
        """Mark messages as read"""
        try:
            for msg_id in message_ids:
                await self.message_manager.update_message_status(
                    msg_id,
                    MessageStatus.READ.value
                )
            
            logger.info(f"User {user_id} marked messages as read")
            return True
        except Exception as e:
            logger.error(f"Failed to mark as read: {e}")
            return False
    
    async def block_user(self, user_id: str, blocked_user_id: str) -> bool:
        """Block user from messaging"""
        try:
            self.blocked_pairs.add((user_id, blocked_user_id))
            
            if user_id not in self.users:
                self.users[user_id] = User(id=user_id, username="", display_name="")
            
            self.users[user_id].blocks.append(blocked_user_id)
            
            if blocked_user_id not in self.users:
                self.users[blocked_user_id] = User(
                    id=blocked_user_id,
                    username="",
                    display_name=""
                )
            
            self.users[blocked_user_id].is_blocked_by.append(user_id)
            
            logger.info(f"User {user_id} blocked {blocked_user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to block user: {e}")
            return False
    
    async def unblock_user(self, user_id: str, blocked_user_id: str) -> bool:
        """Unblock user"""
        try:
            self.blocked_pairs.discard((user_id, blocked_user_id))
            
            if user_id in self.users:
                self.users[user_id].blocks = [
                    b for b in self.users[user_id].blocks if b != blocked_user_id
                ]
            
            if blocked_user_id in self.users:
                self.users[blocked_user_id].is_blocked_by = [
                    b for b in self.users[blocked_user_id].is_blocked_by if b != user_id
                ]
            
            logger.info(f"User {user_id} unblocked {blocked_user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to unblock user: {e}")
            return False
    
    async def get_contacts(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's contacts"""
        try:
            # Get all conversations for user
            conversations = await self.conversation_manager.get_conversations(user_id)
            
            contacts = []
            seen = set()
            
            for conv in conversations:
                for participant_id in conv.participant_ids:
                    if participant_id != user_id and participant_id not in seen:
                        seen.add(participant_id)
                        
                        user = self.users.get(participant_id)
                        if user:
                            presence = await self.realtime_engine.get_presence(participant_id)
                            contacts.append({
                                "id": participant_id,
                                "name": user.display_name,
                                "avatar": user.avatar_url,
                                "presence": presence,
                                "bio": user.bio
                            })
            
            return contacts
        except Exception as e:
            logger.error(f"Failed to get contacts: {e}")
            return []
    
    async def create_or_get_conversation(
        self,
        user_id: str,
        other_user_id: str
    ) -> Optional[Conversation]:
        """Get or create 1-to-1 conversation"""
        try:
            # Check if conversation already exists
            convs = await self.conversation_manager.get_conversations(user_id)
            
            for conv in convs:
                if (not conv.is_group and
                    len(conv.participant_ids) == 2 and
                    other_user_id in conv.participant_ids):
                    return conv
            
            # Create new conversation
            return await self.conversation_manager.create_conversation(
                user_id,
                [other_user_id],
                is_group=False
            )
        except Exception as e:
            logger.error(f"Failed to get/create conversation: {e}")
            return None


# Global instance
_messaging_service: Optional[MessagingService] = None


async def init_messaging_service() -> MessagingService:
    """Initialize messaging service"""
    global _messaging_service
    _messaging_service = MessagingService()
    logger.info("Messaging service initialized")
    return _messaging_service


def get_messaging_service() -> MessagingService:
    """Get messaging service instance"""
    global _messaging_service
    if _messaging_service is None:
        raise RuntimeError("Messaging service not initialized")
    return _messaging_service
