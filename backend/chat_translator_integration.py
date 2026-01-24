"""
Chat Integration for Auto-Translator
Middleware and utilities for translating chat messages in real-time
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from dataclasses import dataclass, asdict, field
from uuid import uuid4
from enum import Enum

from auto_translator import get_translator

logger = logging.getLogger(__name__)


class ChatMessageType(str, Enum):
    """Types of chat messages"""
    TEXT = "text"
    MEDIA = "media"
    REACTION = "reaction"
    SYSTEM = "system"
    TRANSLATION_NOTICE = "translation_notice"


@dataclass
class TranslatedChatMessage:
    """Chat message with translation"""
    id: str = field(default_factory=lambda: str(uuid4()))
    original_message: str = ""
    translated_message: str = ""
    sender_id: str = ""
    recipient_id: str = ""
    sender_language: str = "en"
    target_language: str = "en"
    message_type: str = ChatMessageType.TEXT.value
    is_translated: bool = False
    confidence: float = 1.0
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


class ChatTranslationMiddleware:
    """Middleware for automatic chat message translation"""
    
    def __init__(self):
        """Initialize chat translation middleware"""
        self.translator = get_translator()
        self.message_history: Dict[str, List[TranslatedChatMessage]] = {}
        self.max_history_per_conversation = 500
        logger.info("ChatTranslationMiddleware initialized")
    
    def process_incoming_message(
        self,
        message: str,
        sender_id: str,
        recipient_id: str,
        sender_language: Optional[str] = None,
        message_type: str = ChatMessageType.TEXT.value
    ) -> TranslatedChatMessage:
        """
        Process incoming chat message
        Automatically translates if recipient prefers a different language
        
        Args:
            message: Message text
            sender_id: Sender user ID
            recipient_id: Recipient user ID
            sender_language: Sender's language (auto-detected if None)
            message_type: Type of message
            
        Returns:
            TranslatedChatMessage with translation if needed
        """
        try:
            # Get recipient's language preference
            recipient_pref = self.translator.get_user_preference(recipient_id)
            target_language = recipient_pref.primary_language if recipient_pref else "en"
            
            # Detect sender language if not provided
            if not sender_language:
                detected, _ = self.translator.detect_language(message)
                sender_language = detected or "en"
            
            # Skip translation if same language or system message
            if sender_language == target_language or message_type == ChatMessageType.SYSTEM.value:
                translated_msg = message
                is_translated = False
                confidence = 1.0
            else:
                # Translate message
                result = self.translator.translate(
                    message,
                    source_language=sender_language,
                    target_language=target_language
                )
                translated_msg = result.translated_text
                is_translated = True
                confidence = result.confidence
            
            # Create translated message object
            translated_message = TranslatedChatMessage(
                original_message=message,
                translated_message=translated_msg,
                sender_id=sender_id,
                recipient_id=recipient_id,
                sender_language=sender_language,
                target_language=target_language,
                message_type=message_type,
                is_translated=is_translated,
                confidence=confidence
            )
            
            # Store in history
            self._add_to_history(sender_id, recipient_id, translated_message)
            
            logger.info(
                f"Message processed: {sender_id} -> {recipient_id}, "
                f"translated: {is_translated}, lang: {sender_language} -> {target_language}"
            )
            
            return translated_message
            
        except Exception as e:
            logger.error(f"Error processing chat message: {e}")
            # Return original message on error
            return TranslatedChatMessage(
                original_message=message,
                translated_message=message,
                sender_id=sender_id,
                recipient_id=recipient_id,
                is_translated=False
            )
    
    def process_group_chat_message(
        self,
        message: str,
        sender_id: str,
        group_id: str,
        recipient_ids: List[str],
        sender_language: Optional[str] = None,
        message_type: str = ChatMessageType.TEXT.value
    ) -> Dict[str, TranslatedChatMessage]:
        """
        Process group chat message
        Translates to each recipient's preferred language
        
        Args:
            message: Message text
            sender_id: Sender user ID
            group_id: Group chat ID
            recipient_ids: List of recipient user IDs
            sender_language: Sender's language
            message_type: Type of message
            
        Returns:
            Dict mapping recipient_id -> TranslatedChatMessage
        """
        try:
            translated_messages = {}
            
            # Detect sender language once
            if not sender_language:
                detected, _ = self.translator.detect_language(message)
                sender_language = detected or "en"
            
            # Translate for each recipient
            for recipient_id in recipient_ids:
                if recipient_id != sender_id:  # Don't translate for sender
                    translated_msg = self.process_incoming_message(
                        message=message,
                        sender_id=sender_id,
                        recipient_id=recipient_id,
                        sender_language=sender_language,
                        message_type=message_type
                    )
                    translated_messages[recipient_id] = translated_msg
                else:
                    # Sender gets original message
                    translated_messages[recipient_id] = TranslatedChatMessage(
                        original_message=message,
                        translated_message=message,
                        sender_id=sender_id,
                        recipient_id=recipient_id,
                        sender_language=sender_language,
                        is_translated=False
                    )
            
            logger.info(f"Group message processed: {group_id}, recipients: {len(recipient_ids)}")
            return translated_messages
            
        except Exception as e:
            logger.error(f"Error processing group chat message: {e}")
            # Return message for all recipients without translation
            return {
                recipient_id: TranslatedChatMessage(
                    original_message=message,
                    translated_message=message,
                    sender_id=sender_id,
                    recipient_id=recipient_id,
                    is_translated=False
                )
                for recipient_id in recipient_ids
            }
    
    def _add_to_history(
        self,
        sender_id: str,
        recipient_id: str,
        message: TranslatedChatMessage
    ) -> None:
        """Store message in history"""
        conversation_id = f"{min(sender_id, recipient_id)}_{max(sender_id, recipient_id)}"
        
        if conversation_id not in self.message_history:
            self.message_history[conversation_id] = []
        
        history = self.message_history[conversation_id]
        history.append(message)
        
        # Keep only recent messages
        if len(history) > self.max_history_per_conversation:
            self.message_history[conversation_id] = history[-self.max_history_per_conversation:]
    
    def get_conversation_history(
        self,
        user_id_1: str,
        user_id_2: str,
        limit: int = 50
    ) -> List[TranslatedChatMessage]:
        """Get translation history for a conversation"""
        conversation_id = f"{min(user_id_1, user_id_2)}_{max(user_id_1, user_id_2)}"
        history = self.message_history.get(conversation_id, [])
        return history[-limit:]
    
    def get_supported_chat_modes(self) -> Dict[str, Any]:
        """Get supported chat modes and their translation capabilities"""
        return {
            "direct_chat": {
                "name": "Direct Chat",
                "auto_translate": True,
                "supported_languages": len(self.translator.get_supported_languages())
            },
            "group_chat": {
                "name": "Group Chat",
                "auto_translate": True,
                "supported_languages": len(self.translator.get_supported_languages())
            },
            "live_chat": {
                "name": "Live Chat",
                "auto_translate": True,
                "supported_languages": len(self.translator.get_supported_languages())
            },
            "voice_chat": {
                "name": "Voice Chat with Live Captions",
                "auto_translate": True,
                "supported_languages": len(self.translator.get_supported_languages())
            },
            "collaborative_chat": {
                "name": "Collaborative Editing Chat",
                "auto_translate": True,
                "supported_languages": len(self.translator.get_supported_languages())
            },
            "duet_chat": {
                "name": "Duet Collaboration Chat",
                "auto_translate": True,
                "supported_languages": len(self.translator.get_supported_languages())
            },
            "team_chat": {
                "name": "Team/Creator Chat",
                "auto_translate": True,
                "supported_languages": len(self.translator.get_supported_languages())
            },
            "broadcast_chat": {
                "name": "Broadcast/Live Stream Chat",
                "auto_translate": True,
                "supported_languages": len(self.translator.get_supported_languages())
            }
        }
    
    def clear_history(self, user_id_1: str, user_id_2: str) -> None:
        """Clear conversation history"""
        conversation_id = f"{min(user_id_1, user_id_2)}_{max(user_id_1, user_id_2)}"
        if conversation_id in self.message_history:
            del self.message_history[conversation_id]


# Global instance
chat_translator = ChatTranslationMiddleware()


def get_chat_translator() -> ChatTranslationMiddleware:
    """Get chat translation middleware instance"""
    return chat_translator
