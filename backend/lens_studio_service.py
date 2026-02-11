"""
Lens Studio Filter Service - FastAPI Integration
Production-grade real-time filter service with WebSocket support
Handles filter application, storage, and real-time streaming
"""

from fastapi import APIRouter, WebSocket, UploadFile, File, HTTPException, Query, Depends
from fastapi.responses import JSONResponse, StreamingResponse
from typing import Dict, List, Optional, Any
import numpy as np
import cv2
import asyncio
import logging
from datetime import datetime
import motor.motor_asyncio
from bson import ObjectId
import json
from pathlib import Path
import uuid
from contextlib import asynccontextmanager

from lens_studio_core import (
    FilterProcessor,
    FilterMetadata,
    FilterType,
    FilterPriority,
    DEFAULT_FILTERS,
    FaceFeatures
)

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/api/lens-studio", tags=["lens-studio"])

# Global filter processor
filter_processor: Optional[FilterProcessor] = None

# Connected WebSocket clients
connected_clients: Dict[str, WebSocket] = {}


@asynccontextmanager
async def initialize_processor():
    """Initialize filter processor on startup"""
    global filter_processor
    filter_processor = FilterProcessor()
    logger.info("✅ Filter processor initialized")
    yield
    logger.info("🛑 Filter processor shutdown")


# ==================== FILTER MANAGEMENT ====================


@router.post("/filters")
async def create_custom_filter(
    filter_data: Dict[str, Any],
    db: motor.motor_asyncio.AsyncIOMotorDatabase = Depends()
) -> Dict[str, Any]:
    """Create new custom filter"""
    try:
        filter_id = str(uuid.uuid4())
        filter_meta = FilterMetadata(
            filter_id=filter_id,
            name=filter_data.get("name", "Custom Filter"),
            filter_type=FilterType(filter_data.get("type", "artistic")),
            intensity=float(filter_data.get("intensity", 0.7)),
            parameters=filter_data.get("parameters", {}),
            tags=filter_data.get("tags", []),
            priority=FilterPriority(filter_data.get("priority", "normal"))
        )
        
        # Save to database
        filter_doc = {
            "_id": ObjectId(),
            "filter_id": filter_id,
            "name": filter_meta.name,
            "type": filter_meta.filter_type.value,
            "intensity": filter_meta.intensity,
            "parameters": filter_meta.parameters,
            "tags": filter_meta.tags,
            "priority": filter_meta.priority.value,
            "author": filter_data.get("author", "user"),
            "created_at": datetime.utcnow(),
            "enabled": True,
            "usage_count": 0
        }
        
        result = await db.filters.insert_one(filter_doc)
        
        logger.info(f"✅ Filter created: {filter_id}")
        
        return {
            "success": True,
            "filter_id": filter_id,
            "message": "Filter created successfully"
        }
    
    except Exception as e:
        logger.error(f"❌ Error creating filter: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/filters")
async def list_filters(
    filter_type: Optional[str] = Query(None),
    db: motor.motor_asyncio.AsyncIOMotorDatabase = Depends()
) -> Dict[str, Any]:
    """List all available filters"""
    try:
        query = {}
        if filter_type:
            query["type"] = filter_type
        
        filters = await db.filters.find(query).to_list(length=100)
        
        return {
            "success": True,
            "total": len(filters),
            "filters": [
                {
                    "filter_id": f.get("filter_id"),
                    "name": f.get("name"),
                    "type": f.get("type"),
                    "intensity": f.get("intensity"),
                    "tags": f.get("tags"),
                    "enabled": f.get("enabled")
                }
                for f in filters
            ]
        }
    
    except Exception as e:
        logger.error(f"❌ Error listing filters: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/filters/free")
async def get_free_filters(
    db: motor.motor_asyncio.AsyncIOMotorDatabase = Depends()
) -> Dict[str, Any]:
    """Get all free filters (default library)"""
    try:
        filters_list = []
        
        for filter_id, filter_meta in DEFAULT_FILTERS.items():
            filters_list.append({
                "filter_id": filter_meta.filter_id,
                "name": filter_meta.name,
                "type": filter_meta.filter_type.value,
                "intensity": filter_meta.intensity,
                "tags": filter_meta.tags,
                "priority": filter_meta.priority.value
            })
        
        return {
            "success": True,
            "total": len(filters_list),
            "filters": filters_list,
            "message": "12 free professional filters available"
        }
    
    except Exception as e:
        logger.error(f"❌ Error getting free filters: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/filters/{filter_id}")
async def update_filter(
    filter_id: str,
    filter_data: Dict[str, Any],
    db: motor.motor_asyncio.AsyncIOMotorDatabase = Depends()
) -> Dict[str, Any]:
    """Update filter settings"""
    try:
        update_data = {}
        
        if "intensity" in filter_data:
            update_data["intensity"] = float(filter_data["intensity"])
        if "parameters" in filter_data:
            update_data["parameters"] = filter_data["parameters"]
        if "enabled" in filter_data:
            update_data["enabled"] = bool(filter_data["enabled"])
        
        result = await db.filters.update_one(
            {"filter_id": filter_id},
            {"$set": update_data}
        )
        
        logger.info(f"✅ Filter updated: {filter_id}")
        
        return {
            "success": True,
            "message": "Filter updated successfully"
        }
    
    except Exception as e:
        logger.error(f"❌ Error updating filter: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/filters/{filter_id}")
async def delete_filter(
    filter_id: str,
    db: motor.motor_asyncio.AsyncIOMotorDatabase = Depends()
) -> Dict[str, Any]:
    """Delete custom filter"""
    try:
        result = await db.filters.delete_one({"filter_id": filter_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Filter not found")
        
        logger.info(f"✅ Filter deleted: {filter_id}")
        
        return {
            "success": True,
            "message": "Filter deleted successfully"
        }
    
    except Exception as e:
        logger.error(f"❌ Error deleting filter: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== IMAGE PROCESSING ====================


@router.post("/process-image")
async def process_image(
    file: UploadFile = File(...),
    filter_ids: str = Query(""),
    db: motor.motor_asyncio.AsyncIOMotorDatabase = Depends()
) -> StreamingResponse:
    """Process single image with filters"""
    try:
        if not filter_processor:
            raise HTTPException(status_code=503, detail="Processor not initialized")
        
        # Read image
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            raise HTTPException(status_code=400, detail="Invalid image")
        
        # Prepare filters
        filters = []
        if filter_ids:
            for fid in filter_ids.split(","):
                fid = fid.strip()
                if fid in DEFAULT_FILTERS:
                    filters.append(DEFAULT_FILTERS[fid])
                else:
                    # Get from database
                    filter_doc = await db.filters.find_one({"filter_id": fid})
                    if filter_doc:
                        filters.append(FilterMetadata(
                            filter_id=filter_doc["filter_id"],
                            name=filter_doc["name"],
                            filter_type=FilterType(filter_doc["type"]),
                            intensity=filter_doc.get("intensity", 0.7),
                            parameters=filter_doc.get("parameters", {})
                        ))
        
        # Process
        result_frame, metadata = filter_processor.process_frame(frame, filters)
        
        # Encode
        _, buffer = cv2.imencode('.jpg', result_frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
        
        return StreamingResponse(
            iter([buffer.tobytes()]),
            media_type="image/jpeg"
        )
    
    except Exception as e:
        logger.error(f"❌ Error processing image: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== REAL-TIME WEBSOCKET ====================


@router.websocket("/ws/live-filter/{user_id}")
async def websocket_live_filter(websocket: WebSocket, user_id: str):
    """Real-time filter streaming via WebSocket"""
    await websocket.accept()
    connected_clients[user_id] = websocket
    
    logger.info(f"✅ User {user_id} connected to live filter")
    
    try:
        while True:
            data = await websocket.receive_json()
            
            if data.get("type") == "frame":
                try:
                    # Decode frame
                    frame_data = data.get("frame")
                    frame = filter_processor.decode_frame_from_base64(frame_data)
                    
                    # Get filters to apply
                    filter_ids = data.get("filters", [])
                    filters = []
                    
                    for fid in filter_ids:
                        if fid in DEFAULT_FILTERS:
                            filters.append(DEFAULT_FILTERS[fid])
                    
                    # Process frame
                    result_frame, metadata = filter_processor.process_frame(frame, filters)
                    
                    # Encode and send back
                    result_data = filter_processor.encode_frame_to_base64(result_frame)
                    
                    await websocket.send_json({
                        "type": "processed_frame",
                        "frame": result_data,
                        "metadata": metadata
                    })
                
                except Exception as e:
                    logger.error(f"❌ Error processing WebSocket frame: {e}")
                    await websocket.send_json({
                        "type": "error",
                        "message": str(e)
                    })
            
            elif data.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
    
    except Exception as e:
        logger.error(f"❌ WebSocket error for user {user_id}: {e}")
    
    finally:
        if user_id in connected_clients:
            del connected_clients[user_id]
        logger.info(f"✅ User {user_id} disconnected from live filter")


# ==================== ANALYTICS ====================


@router.post("/analytics/filter-usage")
async def track_filter_usage(
    filter_id: str,
    user_id: str,
    db: motor.motor_asyncio.AsyncIOMotorDatabase = Depends()
) -> Dict[str, Any]:
    """Track filter usage for analytics"""
    try:
        # Update filter usage count
        await db.filters.update_one(
            {"filter_id": filter_id},
            {"$inc": {"usage_count": 1}}
        )
        
        # Log usage
        await db.filter_analytics.insert_one({
            "filter_id": filter_id,
            "user_id": user_id,
            "timestamp": datetime.utcnow(),
            "session_id": str(uuid.uuid4())
        })
        
        return {"success": True}
    
    except Exception as e:
        logger.error(f"❌ Error tracking filter usage: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/popular-filters")
async def get_popular_filters(
    limit: int = Query(10),
    db: motor.motor_asyncio.AsyncIOMotorDatabase = Depends()
) -> Dict[str, Any]:
    """Get most popular filters"""
    try:
        filters = await db.filters.find().sort("usage_count", -1).limit(limit).to_list(length=limit)
        
        return {
            "success": True,
            "filters": [
                {
                    "filter_id": f.get("filter_id"),
                    "name": f.get("name"),
                    "usage_count": f.get("usage_count", 0)
                }
                for f in filters
            ]
        }
    
    except Exception as e:
        logger.error(f"❌ Error getting popular filters: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== SOCIAL INTEGRATION ====================


@router.post("/social/create-post-with-filter")
async def create_post_with_filter(
    image_data: UploadFile = File(...),
    filters: str = Query(""),
    caption: str = Query(""),
    user_id: str = Query(""),
    db: motor.motor_asyncio.AsyncIOMotorDatabase = Depends()
) -> Dict[str, Any]:
    """Create social post with applied filters"""
    try:
        # Read and process image
        contents = await image_data.read()
        nparr = np.frombuffer(contents, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Apply filters
        filter_list = []
        for fid in filters.split(","):
            fid = fid.strip()
            if fid in DEFAULT_FILTERS:
                filter_list.append(DEFAULT_FILTERS[fid])
        
        result_frame, _ = filter_processor.process_frame(frame, filter_list)
        
        # Save to database
        post_id = str(uuid.uuid4())
        _, buffer = cv2.imencode('.jpg', result_frame)
        
        post_doc = {
            "_id": ObjectId(),
            "post_id": post_id,
            "user_id": user_id,
            "caption": caption,
            "image_data": buffer.tobytes(),
            "filters_applied": filters.split(","),
            "created_at": datetime.utcnow(),
            "likes": 0,
            "comments": [],
            "shares": 0
        }
        
        await db.posts.insert_one(post_doc)
        
        logger.info(f"✅ Post created: {post_id}")
        
        return {
            "success": True,
            "post_id": post_id,
            "message": "Post created successfully"
        }
    
    except Exception as e:
        logger.error(f"❌ Error creating post: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/filter-performance")
async def get_filter_performance(
    days: int = Query(30),
    db: motor.motor_asyncio.AsyncIOMotorDatabase = Depends()
) -> Dict[str, Any]:
    """Get filter performance statistics"""
    try:
        from datetime import timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        analytics = await db.filter_analytics.aggregate([
            {
                "$match": {"timestamp": {"$gte": cutoff_date}}
            },
            {
                "$group": {
                    "_id": "$filter_id",
                    "usage_count": {"$sum": 1},
                    "unique_users": {"$addToSet": "$user_id"}
                }
            },
            {
                "$sort": {"usage_count": -1}
            }
        ]).to_list(length=50)
        
        return {
            "success": True,
            "period_days": days,
            "total_filters_used": len(analytics),
            "analytics": [
                {
                    "filter_id": a["_id"],
                    "usage_count": a["usage_count"],
                    "unique_users": len(a["unique_users"])
                }
                for a in analytics
            ]
        }
    
    except Exception as e:
        logger.error(f"❌ Error getting filter performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


logger.info("✅ Lens Studio FastAPI Service Ready - Production Grade")
