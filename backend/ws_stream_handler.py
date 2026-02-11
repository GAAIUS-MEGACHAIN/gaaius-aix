"""
Real-time WebSocket handler for streaming video frames through AI filters
Production-grade streaming with frame buffering and performance monitoring
"""

import asyncio
import cv2
import numpy as np
import base64
import json
import logging
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List, Optional, Any
from datetime import datetime
import time
from collections import deque
from .ai_filter_studio import (
    FrameProcessor, BeautyFilterConfig, BackgroundFilter,
    AIEnhancementEngine, FilterType
)

logger = logging.getLogger(__name__)

class StreamMetrics:
    """Track streaming performance metrics"""
    def __init__(self, window_size: int = 30):
        self.frame_times = deque(maxlen=window_size)
        self.processing_times = deque(maxlen=window_size)
        self.frame_count = 0
        self.start_time = time.time()
    
    def add_frame(self, processing_time_ms: float):
        self.frame_count += 1
        self.frame_times.append(time.time())
        self.processing_times.append(processing_time_ms)
    
    @property
    def fps(self) -> float:
        if len(self.frame_times) < 2:
            return 0
        time_span = self.frame_times[-1] - self.frame_times[0]
        return len(self.frame_times) / time_span if time_span > 0 else 0
    
    @property
    def avg_processing_time(self) -> float:
        return sum(self.processing_times) / len(self.processing_times) if self.processing_times else 0
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            "fps": round(self.fps, 2),
            "avg_processing_ms": round(self.avg_processing_time, 2),
            "total_frames": self.frame_count,
            "uptime_seconds": round(time.time() - self.start_time, 2)
        }

class StreamSession:
    """Manage individual WebSocket streaming session"""
    def __init__(self, session_id: str, websocket: WebSocket):
        self.session_id = session_id
        self.websocket = websocket
        self.active_filters: List[str] = []
        self.beauty_config: Optional[BeautyFilterConfig] = None
        self.background_config: Optional[BackgroundFilter] = None
        self.metrics = StreamMetrics()
        self.is_recording = False
        self.frame_buffer = deque(maxlen=300)  # 10 seconds at 30fps
        self.created_at = datetime.utcnow()
        self.processor = FrameProcessor()
        self.ai_engine = AIEnhancementEngine()
        self.last_config_update = datetime.utcnow()
        # Snapchat filters support
        self.snapchat_filters: Dict[str, float] = {}
        self.social_platform: Optional[str] = None
    
    def update_filters(self, filters: List[str]):
        """Update active filters"""
        self.active_filters = filters
        logger.info(f"Session {self.session_id}: Updated filters to {filters}")
    
    def update_beauty_config(self, config: Dict):
        """Update beauty filter configuration"""
        try:
            self.beauty_config = BeautyFilterConfig(**config)
            self.last_config_update = datetime.utcnow()
            logger.info(f"Session {self.session_id}: Updated beauty config")
        except Exception as e:
            logger.error(f"Config update error: {e}")
    
    def update_background_config(self, config: Dict):
        """Update background filter configuration"""
        try:
            self.background_config = BackgroundFilter(**config)
            self.last_config_update = datetime.utcnow()
            logger.info(f"Session {self.session_id}: Updated background config")
        except Exception as e:
            logger.error(f"Config update error: {e}")

class WebSocketManager:
    """Manage all active WebSocket connections"""
    def __init__(self):
        self.active_sessions: Dict[str, StreamSession] = {}
        self.session_lock = asyncio.Lock()
    
    async def add_session(self, session_id: str, websocket: WebSocket) -> StreamSession:
        """Add new streaming session"""
        async with self.session_lock:
            if session_id in self.active_sessions:
                await self.active_sessions[session_id].websocket.close()
            
            session = StreamSession(session_id, websocket)
            self.active_sessions[session_id] = session
            logger.info(f"Added session: {session_id}")
            return session
    
    async def remove_session(self, session_id: str):
        """Remove streaming session"""
        async with self.session_lock:
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
                logger.info(f"Removed session: {session_id}")
    
    def get_session(self, session_id: str) -> Optional[StreamSession]:
        """Get active session"""
        return self.active_sessions.get(session_id)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics for all sessions"""
        return {
            "active_sessions": len(self.active_sessions),
            "sessions": {
                sid: session.metrics.get_stats()
                for sid, session in self.active_sessions.items()
            }
        }

# Global WebSocket manager
ws_manager = WebSocketManager()

class FrameStreamHandler:
    """Handle frame streaming and processing"""
    
    @staticmethod
    async def handle_stream(
        session_id: str,
        websocket: WebSocket
    ):
        """Main WebSocket stream handler"""
        session = await ws_manager.add_session(session_id, websocket)
        
        try:
            await websocket.accept()
            logger.info(f"WebSocket connected: {session_id}")
            
            # Send connection confirmation
            await websocket.send_json({
                "type": "connection",
                "status": "connected",
                "session_id": session_id,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Main streaming loop
            while True:
                try:
                    # Receive frame data
                    data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                    message = json.loads(data)
                    
                    message_type = message.get("type")
                    
                    if message_type == "frame":
                        await FrameStreamHandler._process_frame(session, message, websocket)
                    
                    elif message_type == "config":
                        await FrameStreamHandler._update_config(session, message)
                    
                    elif message_type == "filters":
                        session.update_filters(message.get("filters", []))
                    
                    elif message_type == "snapchat_filters":
                        session.snapchat_filters = message.get("filters", {})
                        session.social_platform = message.get("social_platform")
                        logger.info(f"Session {session.session_id}: Updated Snapchat filters: {list(session.snapchat_filters.keys())}, platform: {session.social_platform}")
                    
                    elif message_type == "record":
                        session.is_recording = message.get("enabled", False)
                    
                    elif message_type == "ping":
                        await websocket.send_json({
                            "type": "pong",
                            "timestamp": datetime.utcnow().isoformat()
                        })
                    
                    elif message_type == "close":
                        break
                
                except asyncio.TimeoutError:
                    logger.warning(f"Session {session_id}: Timeout waiting for frame")
                    # Send timeout message but keep connection alive
                    await websocket.send_json({
                        "type": "timeout_warning",
                        "message": "No frame received - connection may be lost"
                    })
                
                except json.JSONDecodeError:
                    logger.error(f"Session {session_id}: Invalid JSON")
        
        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected: {session_id}")
        
        except Exception as e:
            logger.error(f"WebSocket error ({session_id}): {e}")
        
        finally:
            await ws_manager.remove_session(session_id)
            logger.info(f"Stream session ended: {session_id}")
    
    @staticmethod
    async def _process_frame(session: StreamSession, message: Dict, websocket: WebSocket):
        """Process incoming frame"""
        try:
            frame_base64 = message.get("frame_base64")
            request_id = message.get("request_id")
            
            if not frame_base64:
                return
            
            # Decode frame
            frame_bytes = base64.b64decode(frame_base64)
            frame_array = np.frombuffer(frame_bytes, dtype=np.uint8)
            frame = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)
            
            if frame is None:
                logger.error(f"Failed to decode frame for session {session.session_id}")
                return
            
            # Process frame
            start_time = time.time()
            processed_frame, face_count, proc_time = session.processor.process_frame(
                frame,
                session.active_filters,
                session.beauty_config,
                session.background_config,
                snapchat_filters=session.snapchat_filters if session.snapchat_filters else None,
                social_platform=session.social_platform
            )
            processing_time = (time.time() - start_time) * 1000
            
            # Update metrics
            session.metrics.add_frame(proc_time)
            
            # Encode result
            _, buffer = cv2.imencode('.jpg', processed_frame, [cv2.IMWRITE_JPEG_QUALITY, 90])
            result_base64 = base64.b64encode(buffer).decode()
            
            # Store in buffer if recording
            if session.is_recording:
                session.frame_buffer.append({
                    "frame": result_base64,
                    "timestamp": datetime.utcnow(),
                    "faces": face_count
                })
            
            # Get AI suggestions periodically (every 30 frames)
            ai_suggestions = None
            if session.metrics.frame_count % 30 == 0 and "beauty" in session.active_filters:
                try:
                    ai_suggestions = session.ai_engine.generate_filter_suggestions(
                        frame_base64, FilterType.BEAUTY
                    )
                except Exception as e:
                    logger.error(f"AI suggestion error: {e}")
            
            # Send response
            response = {
                "type": "frame",
                "request_id": request_id,
                "frame_base64": result_base64,
                "detected_faces": face_count,
                "processing_time_ms": round(proc_time, 2),
                "applied_filters": session.active_filters,
                "metrics": session.metrics.get_stats()
            }
            
            if ai_suggestions:
                response["ai_suggestions"] = ai_suggestions
            
            await websocket.send_json(response)
        
        except Exception as e:
            logger.error(f"Frame processing error: {e}")
            await websocket.send_json({
                "type": "error",
                "error": str(e),
                "request_id": message.get("request_id")
            })
    
    @staticmethod
    async def _update_config(session: StreamSession, message: Dict):
        """Update filter configuration"""
        try:
            if "beauty_config" in message:
                session.update_beauty_config(message["beauty_config"])
            
            if "background_config" in message:
                session.update_background_config(message["background_config"])
            
            logger.info(f"Config updated for session {session.session_id}")
        except Exception as e:
            logger.error(f"Config update error: {e}")

async def broadcast_metrics():
    """Periodically broadcast metrics to all connected sessions"""
    while True:
        try:
            stats = ws_manager.get_stats()
            for session in ws_manager.active_sessions.values():
                try:
                    await session.websocket.send_json({
                        "type": "metrics",
                        "data": stats
                    })
                except:
                    pass
            
            await asyncio.sleep(5)  # Send every 5 seconds
        except Exception as e:
            logger.error(f"Broadcast error: {e}")
            await asyncio.sleep(5)

def get_stream_stats() -> Dict[str, Any]:
    """Get streaming statistics"""
    return ws_manager.get_stats()
