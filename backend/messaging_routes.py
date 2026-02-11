"""
FastAPI routes for messaging platform
Real-time messaging endpoints with WebSocket support
"""

from fastapi import APIRouter, WebSocket, File, UploadFile, Query, Depends, HTTPException
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime

from backend.messaging_service import (
    get_messaging_service,
    MessagingService,
    MessageStatus
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/messages", tags=["messaging"])


# ============================================================================
# CONVERSATION ENDPOINTS
# ============================================================================

@router.post("/conversation")
async def create_conversation(
    creator_id: str,
    participant_ids: List[str],
    name: Optional[str] = None,
    is_group: bool = False
) -> JSONResponse:
    """Create new conversation"""
    try:
        service = get_messaging_service()
        
        conversation = await service.conversation_manager.create_conversation(
            creator_id=creator_id,
            participant_ids=participant_ids,
            name=name,
            is_group=is_group
        )
        
        return JSONResponse({
            "status": "success",
            "data": conversation.to_dict(),
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Error creating conversation: {e}")
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )


@router.post("/conversation/one-to-one")
async def create_or_get_one_to_one(
    user_id: str,
    other_user_id: str
) -> JSONResponse:
    """Get or create 1-to-1 conversation"""
    try:
        service = get_messaging_service()
        
        conversation = await service.create_or_get_conversation(
            user_id=user_id,
            other_user_id=other_user_id
        )
        
        if not conversation:
            raise Exception("Failed to create conversation")
        
        return JSONResponse({
            "status": "success",
            "data": conversation.to_dict(),
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Error creating 1-to-1 conversation: {e}")
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )


@router.get("/conversations/{user_id}")
async def get_conversations(
    user_id: str,
    limit: int = Query(50, ge=1, le=100)
) -> JSONResponse:
    """Get user's conversations"""
    try:
        service = get_messaging_service()
        
        conversations = await service.conversation_manager.get_conversations(
            user_id=user_id,
            limit=limit
        )
        
        return JSONResponse({
            "status": "success",
            "data": [c.to_dict() for c in conversations],
            "count": len(conversations),
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Error getting conversations: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )


@router.post("/conversation/{conversation_id}/add-participant")
async def add_participant(
    conversation_id: str,
    user_id: str
) -> JSONResponse:
    """Add user to group conversation"""
    try:
        service = get_messaging_service()
        
        success = await service.conversation_manager.add_participant(
            conversation_id=conversation_id,
            user_id=user_id
        )
        
        if not success:
            raise Exception("Failed to add participant")
        
        return JSONResponse({
            "status": "success",
            "message": f"User {user_id} added to conversation",
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Error adding participant: {e}")
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )


@router.post("/conversation/{conversation_id}/remove-participant")
async def remove_participant(
    conversation_id: str,
    user_id: str
) -> JSONResponse:
    """Remove user from group conversation"""
    try:
        service = get_messaging_service()
        
        success = await service.conversation_manager.remove_participant(
            conversation_id=conversation_id,
            user_id=user_id
        )
        
        if not success:
            raise Exception("Failed to remove participant")
        
        return JSONResponse({
            "status": "success",
            "message": f"User {user_id} removed from conversation",
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Error removing participant: {e}")
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )


# ============================================================================
# MESSAGE ENDPOINTS
# ============================================================================

@router.post("/send")
async def send_message(
    conversation_id: str,
    sender_id: str,
    content: str,
    message_type: str = "text",
    file_url: Optional[str] = None,
    file_name: Optional[str] = None
) -> JSONResponse:
    """Send message to conversation"""
    try:
        service = get_messaging_service()
        
        message = await service.send_message(
            conversation_id=conversation_id,
            sender_id=sender_id,
            content=content,
            message_type=message_type,
            file_url=file_url,
            file_name=file_name
        )
        
        if not message:
            raise Exception("Failed to send message")
        
        return JSONResponse({
            "status": "success",
            "data": message.to_dict(),
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )


@router.get("/messages/{conversation_id}")
async def get_messages(
    conversation_id: str,
    user_id: str,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
) -> JSONResponse:
    """Get messages for conversation"""
    try:
        service = get_messaging_service()
        
        messages = await service.get_messages(
            conversation_id=conversation_id,
            user_id=user_id,
            limit=limit,
            offset=offset
        )
        
        return JSONResponse({
            "status": "success",
            "data": [m.to_dict() for m in messages],
            "count": len(messages),
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Error getting messages: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )


@router.post("/message/{message_id}/read")
async def mark_as_read(
    conversation_id: str,
    user_id: str,
    message_ids: List[str]
) -> JSONResponse:
    """Mark messages as read"""
    try:
        service = get_messaging_service()
        
        success = await service.mark_as_read(
            conversation_id=conversation_id,
            user_id=user_id,
            message_ids=message_ids
        )
        
        if not success:
            raise Exception("Failed to mark as read")
        
        return JSONResponse({
            "status": "success",
            "message": "Messages marked as read",
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Error marking as read: {e}")
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )


@router.delete("/message/{message_id}")
async def delete_message(
    message_id: str,
    user_id: str
) -> JSONResponse:
    """Delete message"""
    try:
        service = get_messaging_service()
        
        success = await service.message_manager.delete_message(message_id)
        
        if not success:
            raise Exception("Message not found")
        
        return JSONResponse({
            "status": "success",
            "message": "Message deleted",
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Error deleting message: {e}")
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )


@router.get("/search/{conversation_id}")
async def search_messages(
    conversation_id: str,
    query: str = Query(..., min_length=1)
) -> JSONResponse:
    """Search messages in conversation"""
    try:
        service = get_messaging_service()
        
        results = await service.message_manager.search_messages(
            conversation_id=conversation_id,
            query=query
        )
        
        return JSONResponse({
            "status": "success",
            "data": [m.to_dict() for m in results],
            "count": len(results),
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Error searching messages: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )


# ============================================================================
# USER MANAGEMENT ENDPOINTS
# ============================================================================

@router.post("/user/block")
async def block_user(
    user_id: str,
    blocked_user_id: str
) -> JSONResponse:
    """Block user from messaging"""
    try:
        service = get_messaging_service()
        
        success = await service.block_user(
            user_id=user_id,
            blocked_user_id=blocked_user_id
        )
        
        if not success:
            raise Exception("Failed to block user")
        
        return JSONResponse({
            "status": "success",
            "message": f"User {blocked_user_id} blocked",
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Error blocking user: {e}")
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )


@router.post("/user/unblock")
async def unblock_user(
    user_id: str,
    blocked_user_id: str
) -> JSONResponse:
    """Unblock user"""
    try:
        service = get_messaging_service()
        
        success = await service.unblock_user(
            user_id=user_id,
            blocked_user_id=blocked_user_id
        )
        
        if not success:
            raise Exception("Failed to unblock user")
        
        return JSONResponse({
            "status": "success",
            "message": f"User {blocked_user_id} unblocked",
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Error unblocking user: {e}")
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )


@router.get("/contacts/{user_id}")
async def get_contacts(
    user_id: str
) -> JSONResponse:
    """Get user's contacts"""
    try:
        service = get_messaging_service()
        
        contacts = await service.get_contacts(user_id)
        
        return JSONResponse({
            "status": "success",
            "data": contacts,
            "count": len(contacts),
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Error getting contacts: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )


@router.get("/user/{user_id}/presence")
async def get_user_presence(
    user_id: str
) -> JSONResponse:
    """Get user's presence status"""
    try:
        service = get_messaging_service()
        
        presence = await service.realtime_engine.get_presence(user_id)
        
        return JSONResponse({
            "status": "success",
            "data": {
                "user_id": user_id,
                "presence": presence,
                "timestamp": datetime.utcnow().isoformat()
            },
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Error getting presence: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )


# ============================================================================
# WEBSOCKET ENDPOINT
# ============================================================================

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket endpoint for real-time messaging"""
    try:
        service = get_messaging_service()
        
        await service.realtime_engine.connect(user_id, websocket)
        
        try:
            while True:
                data = await websocket.receive_json()
                
                message_type = data.get("type")
                
                if message_type == "message":
                    # Handle message
                    await service.send_message(
                        conversation_id=data.get("conversation_id"),
                        sender_id=user_id,
                        content=data.get("content"),
                        message_type=data.get("message_type", "text")
                    )
                
                elif message_type == "typing":
                    # Handle typing indicator
                    await service.realtime_engine.broadcast_typing(
                        conversation_id=data.get("conversation_id"),
                        user_id=user_id,
                        is_typing=data.get("is_typing", False)
                    )
                
                elif message_type == "presence":
                    # Handle presence update
                    await service.realtime_engine.set_presence(
                        user_id,
                        data.get("presence", "online")
                    )
        
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
        finally:
            await service.realtime_engine.disconnect(user_id)
    
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
        await websocket.close(code=1000)


# ============================================================================
# FILE UPLOAD ENDPOINT
# ============================================================================

@router.post("/upload-file")
async def upload_file(
    conversation_id: str,
    sender_id: str,
    file: UploadFile = File(...)
) -> JSONResponse:
    """Upload file for sharing in conversation"""
    try:
        # In production, save to S3/storage
        file_content = await file.read()
        
        # Generate file URL
        file_url = f"/api/v1/messages/files/{file.filename}"
        
        # Send as message
        service = get_messaging_service()
        
        message = await service.send_message(
            conversation_id=conversation_id,
            sender_id=sender_id,
            content=f"Shared file: {file.filename}",
            message_type="file",
            file_url=file_url,
            file_name=file.filename
        )
        
        if not message:
            raise Exception("Failed to upload file")
        
        return JSONResponse({
            "status": "success",
            "data": {
                "file_url": file_url,
                "file_name": file.filename,
                "message": message.to_dict()
            },
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )


# ============================================================================
# HEALTH CHECK
# ============================================================================

@router.get("/health")
async def health_check() -> JSONResponse:
    """Health check endpoint"""
    try:
        service = get_messaging_service()
        
        return JSONResponse({
            "status": "healthy",
            "service": "messaging",
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )
