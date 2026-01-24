"""
Lens Studio - MongoDB Database Schema & Setup
Production-grade database configuration
"""

# Database initialization script
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
import pymongo
from datetime import datetime
from bson import ObjectId

async def initialize_database(db: AsyncIOMotorDatabase):
    """Initialize all collections with proper schema and indexes"""
    
    # Create Filters Collection
    try:
        await db.create_collection(
            "filters",
            validator={
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": ["filter_id", "name", "type"],
                    "properties": {
                        "_id": {"bsonType": "objectId"},
                        "filter_id": {"bsonType": "string"},
                        "name": {"bsonType": "string"},
                        "type": {
                            "enum": [
                                "beauty",
                                "face_shape",
                                "makeup",
                                "artistic",
                                "special_effects",
                                "weather",
                                "stickers",
                                "age_simulation"
                            ]
                        },
                        "version": {"bsonType": "string"},
                        "intensity": {"bsonType": "double"},
                        "parameters": {"bsonType": "object"},
                        "tags": {
                            "bsonType": "array",
                            "items": {"bsonType": "string"}
                        },
                        "priority": {
                            "enum": ["critical", "high", "normal", "low"]
                        },
                        "author": {"bsonType": "string"},
                        "created_at": {"bsonType": "date"},
                        "enabled": {"bsonType": "bool"},
                        "usage_count": {"bsonType": "int", "minimum": 0}
                    }
                }
            }
        )
    except pymongo.errors.CollectionInvalid:
        pass  # Collection already exists
    
    # Create indexes on filters
    await db.filters.create_index([("filter_id", pymongo.ASCENDING)], unique=True)
    await db.filters.create_index([("type", pymongo.ASCENDING)])
    await db.filters.create_index([("usage_count", pymongo.DESCENDING)])
    await db.filters.create_index([("created_at", pymongo.DESCENDING)])
    await db.filters.create_index([("author", pymongo.ASCENDING)])
    
    # Create User Filter Library Collection
    try:
        await db.create_collection(
            "user_filter_libraries",
            validator={
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": ["user_id", "filter_id"],
                    "properties": {
                        "_id": {"bsonType": "objectId"},
                        "user_id": {"bsonType": "string"},
                        "filter_id": {"bsonType": "string"},
                        "liked_at": {"bsonType": "date"},
                        "used_count": {"bsonType": "int"},
                        "last_used": {"bsonType": "date"},
                        "custom_settings": {"bsonType": "object"}
                    }
                }
            }
        )
    except pymongo.errors.CollectionInvalid:
        pass
    
    await db.user_filter_libraries.create_index([("user_id", pymongo.ASCENDING)])
    await db.user_filter_libraries.create_index([("filter_id", pymongo.ASCENDING)])
    await db.user_filter_libraries.create_index(
        [("user_id", pymongo.ASCENDING), ("filter_id", pymongo.ASCENDING)],
        unique=True
    )
    
    # Create Filter Analytics Collection
    try:
        await db.create_collection(
            "filter_analytics",
            validator={
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": ["filter_id", "user_id", "timestamp"],
                    "properties": {
                        "_id": {"bsonType": "objectId"},
                        "filter_id": {"bsonType": "string"},
                        "user_id": {"bsonType": "string"},
                        "timestamp": {"bsonType": "date"},
                        "session_id": {"bsonType": "string"},
                        "processing_time_ms": {"bsonType": "int"},
                        "frame_count": {"bsonType": "int"},
                        "device_info": {"bsonType": "object"}
                    }
                }
            }
        )
    except pymongo.errors.CollectionInvalid:
        pass
    
    # Create TTL index on analytics (keep 90 days)
    await db.filter_analytics.create_index(
        [("timestamp", pymongo.ASCENDING)],
        expireAfterSeconds=7776000  # 90 days
    )
    await db.filter_analytics.create_index([("filter_id", pymongo.ASCENDING)])
    await db.filter_analytics.create_index([("user_id", pymongo.ASCENDING)])
    
    # Create Posts Collection (Social Integration)
    try:
        await db.create_collection(
            "posts",
            validator={
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": ["post_id", "user_id", "created_at"],
                    "properties": {
                        "_id": {"bsonType": "objectId"},
                        "post_id": {"bsonType": "string"},
                        "user_id": {"bsonType": "string"},
                        "caption": {"bsonType": "string"},
                        "image_data": {"bsonType": "binData"},
                        "filters_applied": {
                            "bsonType": "array",
                            "items": {"bsonType": "string"}
                        },
                        "created_at": {"bsonType": "date"},
                        "updated_at": {"bsonType": "date"},
                        "likes": {"bsonType": "int", "minimum": 0},
                        "liked_by": {
                            "bsonType": "array",
                            "items": {"bsonType": "string"}
                        },
                        "comments": {
                            "bsonType": "array",
                            "items": {
                                "bsonType": "object",
                                "properties": {
                                    "comment_id": {"bsonType": "string"},
                                    "user_id": {"bsonType": "string"},
                                    "text": {"bsonType": "string"},
                                    "created_at": {"bsonType": "date"},
                                    "likes": {"bsonType": "int"}
                                }
                            }
                        },
                        "shares": {"bsonType": "int", "minimum": 0},
                        "visibility": {"enum": ["public", "private", "friends"]},
                        "is_processed": {"bsonType": "bool"}
                    }
                }
            }
        )
    except pymongo.errors.CollectionInvalid:
        pass
    
    await db.posts.create_index([("post_id", pymongo.ASCENDING)], unique=True)
    await db.posts.create_index([("user_id", pymongo.ASCENDING)])
    await db.posts.create_index([("created_at", pymongo.DESCENDING)])
    await db.posts.create_index([("likes", pymongo.DESCENDING)])
    
    # Create Sessions Collection (For WebSocket tracking)
    try:
        await db.create_collection(
            "filter_sessions",
            validator={
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": ["session_id", "user_id", "start_time"],
                    "properties": {
                        "_id": {"bsonType": "objectId"},
                        "session_id": {"bsonType": "string"},
                        "user_id": {"bsonType": "string"},
                        "start_time": {"bsonType": "date"},
                        "end_time": {"bsonType": "date"},
                        "filters_used": {
                            "bsonType": "array",
                            "items": {"bsonType": "string"}
                        },
                        "total_frames_processed": {"bsonType": "int"},
                        "avg_fps": {"bsonType": "double"},
                        "device_type": {"bsonType": "string"},
                        "browser": {"bsonType": "string"}
                    }
                }
            }
        )
    except pymongo.errors.CollectionInvalid:
        pass
    
    # Create TTL index on sessions (keep 30 days)
    await db.filter_sessions.create_index(
        [("end_time", pymongo.ASCENDING)],
        expireAfterSeconds=2592000  # 30 days
    )
    await db.filter_sessions.create_index([("user_id", pymongo.ASCENDING)])
    
    print("✅ Database collections initialized successfully")


# Sample data for initial filter library
SAMPLE_FILTERS = [
    {
        "filter_id": "skin_smoothing",
        "name": "Skin Smoothing",
        "type": "beauty",
        "version": "1.0.0",
        "intensity": 0.7,
        "parameters": {"algorithm": "bilateral_filter", "strength": 9},
        "tags": ["beauty", "skin", "professional"],
        "priority": "high",
        "author": "system",
        "created_at": datetime.utcnow(),
        "enabled": True,
        "usage_count": 0
    },
    {
        "filter_id": "skin_brightening",
        "name": "Skin Brightening",
        "type": "beauty",
        "version": "1.0.0",
        "intensity": 0.6,
        "parameters": {"algorithm": "lab_enhancement", "strength": 0.3},
        "tags": ["beauty", "skin", "whitening"],
        "priority": "high",
        "author": "system",
        "created_at": datetime.utcnow(),
        "enabled": True,
        "usage_count": 0
    },
    {
        "filter_id": "face_slimming",
        "name": "Face Slimming",
        "type": "face_shape",
        "version": "1.0.0",
        "intensity": 0.5,
        "parameters": {"algorithm": "liquify", "direction": "inward"},
        "tags": ["face_shape", "slimming", "popular"],
        "priority": "high",
        "author": "system",
        "created_at": datetime.utcnow(),
        "enabled": True,
        "usage_count": 0
    },
    {
        "filter_id": "big_eyes",
        "name": "Big Eyes",
        "type": "face_shape",
        "version": "1.0.0",
        "intensity": 0.6,
        "parameters": {"algorithm": "liquify", "direction": "outward", "radius": 30},
        "tags": ["face_shape", "eyes", "popular"],
        "priority": "high",
        "author": "system",
        "created_at": datetime.utcnow(),
        "enabled": True,
        "usage_count": 0
    },
    {
        "filter_id": "lipstick_red",
        "name": "Red Lipstick",
        "type": "makeup",
        "version": "1.0.0",
        "intensity": 0.8,
        "parameters": {"color": [50, 50, 200], "blend_mode": "multiply"},
        "tags": ["makeup", "lipstick", "red"],
        "priority": "normal",
        "author": "system",
        "created_at": datetime.utcnow(),
        "enabled": True,
        "usage_count": 0
    },
    {
        "filter_id": "lipstick_pink",
        "name": "Pink Lipstick",
        "type": "makeup",
        "version": "1.0.0",
        "intensity": 0.8,
        "parameters": {"color": [150, 100, 180], "blend_mode": "multiply"},
        "tags": ["makeup", "lipstick", "pink"],
        "priority": "normal",
        "author": "system",
        "created_at": datetime.utcnow(),
        "enabled": True,
        "usage_count": 0
    },
    {
        "filter_id": "blush_natural",
        "name": "Natural Blush",
        "type": "makeup",
        "version": "1.0.0",
        "intensity": 0.6,
        "parameters": {"color": [180, 120, 150], "blur_radius": 51},
        "tags": ["makeup", "blush", "natural"],
        "priority": "normal",
        "author": "system",
        "created_at": datetime.utcnow(),
        "enabled": True,
        "usage_count": 0
    },
    {
        "filter_id": "eye_makeup",
        "name": "Eye Makeup",
        "type": "makeup",
        "version": "1.0.0",
        "intensity": 0.7,
        "parameters": {"eyeliner_color": [20, 20, 20], "thickness": 2},
        "tags": ["makeup", "eyes", "eyeliner"],
        "priority": "normal",
        "author": "system",
        "created_at": datetime.utcnow(),
        "enabled": True,
        "usage_count": 0
    },
    {
        "filter_id": "jawline_enhance",
        "name": "Jawline Enhancement",
        "type": "face_shape",
        "version": "1.0.0",
        "intensity": 0.7,
        "parameters": {"algorithm": "shadow_enhancement", "intensity": 0.5},
        "tags": ["face_shape", "jawline", "definition"],
        "priority": "normal",
        "author": "system",
        "created_at": datetime.utcnow(),
        "enabled": True,
        "usage_count": 0
    },
    {
        "filter_id": "cartoon",
        "name": "Cartoon",
        "type": "artistic",
        "version": "1.0.0",
        "intensity": 0.8,
        "parameters": {"color_clusters": 16, "edge_threshold": 100},
        "tags": ["artistic", "cartoon", "fun"],
        "priority": "normal",
        "author": "system",
        "created_at": datetime.utcnow(),
        "enabled": True,
        "usage_count": 0
    },
    {
        "filter_id": "oil_painting",
        "name": "Oil Painting",
        "type": "artistic",
        "version": "1.0.0",
        "intensity": 0.7,
        "parameters": {"algorithm": "xphoto", "strength": 50},
        "tags": ["artistic", "painting", "creative"],
        "priority": "normal",
        "author": "system",
        "created_at": datetime.utcnow(),
        "enabled": True,
        "usage_count": 0
    },
    {
        "filter_id": "sketch",
        "name": "Pencil Sketch",
        "type": "artistic",
        "version": "1.0.0",
        "intensity": 0.8,
        "parameters": {"algorithm": "edge_detection", "blur": 21},
        "tags": ["artistic", "sketch", "drawing"],
        "priority": "normal",
        "author": "system",
        "created_at": datetime.utcnow(),
        "enabled": True,
        "usage_count": 0
    }
]


async def seed_initial_filters(db: AsyncIOMotorDatabase):
    """Insert sample filters into database"""
    try:
        result = await db.filters.insert_many(SAMPLE_FILTERS)
        print(f"✅ Inserted {len(result.inserted_ids)} sample filters")
    except pymongo.errors.DuplicateKeyError:
        print("⚠️ Filters already exist in database")


# Aggregation queries for analytics
ANALYTICS_QUERIES = {
    "popular_filters": [
        {
            "$group": {
                "_id": "$filter_id",
                "usage_count": {"$sum": 1},
                "unique_users": {"$addToSet": "$user_id"}
            }
        },
        {"$sort": {"usage_count": -1}},
        {"$limit": 10}
    ],
    
    "filter_performance_by_day": [
        {
            "$group": {
                "_id": {
                    "$dateToString": {
                        "format": "%Y-%m-%d",
                        "date": "$timestamp"
                    }
                },
                "usage_count": {"$sum": 1},
                "avg_processing_time": {"$avg": "$processing_time_ms"}
            }
        },
        {"$sort": {"_id": -1}},
        {"$limit": 30}
    ],
    
    "user_engagement": [
        {
            "$group": {
                "_id": "$user_id",
                "total_filters_used": {"$sum": 1},
                "unique_filters": {"$addToSet": "$filter_id"},
                "last_active": {"$max": "$timestamp"}
            }
        },
        {"$sort": {"total_filters_used": -1}},
        {"$limit": 100}
    ],
    
    "filter_adoption": [
        {
            "$group": {
                "_id": "$filter_id",
                "total_users": {"$addToSet": "$user_id"},
                "total_uses": {"$sum": 1}
            }
        },
        {
            "$addFields": {
                "unique_users": {"$size": "$total_users"}
            }
        },
        {"$sort": {"unique_users": -1}},
        {"$limit": 20}
    ]
}


print("✅ Database schema and utilities loaded")
