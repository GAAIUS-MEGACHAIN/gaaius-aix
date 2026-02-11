"""
AI Filter Studio Route Registration
Integration module for FastAPI server
"""

from fastapi import APIRouter, WebSocket
from .ai_filter_studio import router as filter_router
from .ws_stream_handler import FrameStreamHandler

# Main AI Filter Studio router
ai_filter_router = APIRouter()

# Include the main filter endpoints
ai_filter_router.include_router(filter_router)

# WebSocket streaming endpoint
@ai_filter_router.websocket("/ws/stream/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time frame streaming"""
    await FrameStreamHandler.handle_stream(session_id, websocket)

def register_ai_filter_routes(app):
    """Register AI Filter Studio routes with FastAPI app"""
    app.include_router(ai_filter_router)
    print("✅ AI Filter Studio routes registered successfully")
