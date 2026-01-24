"""
PHASE 3: Database optimization and connection pooling
Improves MongoDB query performance and connection management
"""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import ASCENDING, DESCENDING, TEXT
from typing import Optional, List, Dict, Any
import os
from datetime import datetime


class DatabasePool:
    """Async MongoDB connection pool"""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.db: Optional[AsyncIOMotorDatabase] = None
        self.max_pool_size = int(os.environ.get('DB_MAX_POOL_SIZE', 50))
        self.min_pool_size = int(os.environ.get('DB_MIN_POOL_SIZE', 10))
    
    async def connect(self):
        """Create connection pool"""
        try:
            uri = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017')
            self.client = AsyncIOMotorClient(
                uri,
                maxPoolSize=self.max_pool_size,
                minPoolSize=self.min_pool_size,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=10000
            )
            
            # Test connection
            await self.client.admin.command('ping')
            
            db_name = os.environ.get('DB_NAME', 'videos_db')
            self.db = self.client[db_name]
            
            print(f"✅ Connected to MongoDB (pool: {self.min_pool_size}-{self.max_pool_size})")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            raise
    
    async def disconnect(self):
        """Close connection pool"""
        if self.client:
            self.client.close()
    
    async def get_db(self) -> AsyncIOMotorDatabase:
        """Get database instance"""
        if not self.db:
            await self.connect()
        return self.db


class IndexManager:
    """Manage database indexes for performance"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
    
    async def create_all_indexes(self):
        """Create all optimized indexes"""
        try:
            # Videos collection indexes
            videos = self.db['videos']
            await videos.create_index([('user_id', ASCENDING)])
            await videos.create_index([('channel_id', ASCENDING)])
            await videos.create_index([('created_at', DESCENDING)])
            await videos.create_index([('view_count', DESCENDING)])
            await videos.create_index([('title', TEXT)])
            await videos.create_index([('user_id', ASCENDING), ('created_at', DESCENDING)])
            
            # Users collection indexes
            users = self.db['users']
            await users.create_index([('username', ASCENDING)], unique=True)
            await users.create_index([('email', ASCENDING)], unique=True)
            await users.create_index([('created_at', DESCENDING)])
            
            # Comments collection indexes
            comments = self.db['comments']
            await comments.create_index([('video_id', ASCENDING)])
            await comments.create_index([('user_id', ASCENDING)])
            await comments.create_index([('created_at', DESCENDING)])
            await comments.create_index([('video_id', ASCENDING), ('created_at', DESCENDING)])
            
            # Playlists collection indexes
            playlists = self.db['playlists']
            await playlists.create_index([('user_id', ASCENDING)])
            await playlists.create_index([('created_at', DESCENDING)])
            
            # Chat sessions indexes
            chat_sessions = self.db['chat_sessions']
            await chat_sessions.create_index([('user_id', ASCENDING)])
            await chat_sessions.create_index([('created_at', DESCENDING)])
            await chat_sessions.create_index([('user_id', ASCENDING), ('created_at', DESCENDING)])
            
            # Messages indexes
            messages = self.db['messages']
            await messages.create_index([('session_id', ASCENDING)])
            await messages.create_index([('created_at', DESCENDING)])
            await messages.create_index([('session_id', ASCENDING), ('created_at', DESCENDING)])
            
            print("✅ All database indexes created")
        except Exception as e:
            print(f"❌ Index creation failed: {e}")
    
    async def analyze_indexes(self):
        """Get index statistics"""
        try:
            stats = {}
            for collection_name in await self.db.list_collection_names():
                collection = self.db[collection_name]
                indexes = await collection.list_indexes()
                stats[collection_name] = len(list(indexes))
            
            return stats
        except Exception as e:
            print(f"❌ Index analysis failed: {e}")
            return {}


class QueryOptimizer:
    """Optimize MongoDB queries"""
    
    @staticmethod
    def build_pagination(page: int = 1, limit: int = 20) -> tuple:
        """Build pagination skip and limit"""
        skip = (page - 1) * limit
        return skip, limit
    
    @staticmethod
    def build_sort_pipeline(sort_by: str = '-created_at') -> List[tuple]:
        """Build MongoDB sort specification"""
        sorts = []
        for field in sort_by.split(','):
            field = field.strip()
            if field.startswith('-'):
                sorts.append((field[1:], DESCENDING))
            else:
                sorts.append((field, ASCENDING))
        return sorts
    
    @staticmethod
    def build_projection(fields: Optional[List[str]] = None) -> Dict[str, int]:
        """Build field projection to reduce data transfer"""
        if not fields:
            return {}
        
        projection = {}
        for field in fields:
            projection[field] = 1
        
        return projection
    
    @staticmethod
    def build_filter(filters: Dict[str, Any]) -> Dict[str, Any]:
        """Build optimized MongoDB filter"""
        mongo_filter = {}
        
        for key, value in filters.items():
            if value is None:
                continue
            
            if isinstance(value, str) and key.endswith('_id'):
                # ObjectId comparison
                from bson.objectid import ObjectId
                try:
                    mongo_filter[key] = ObjectId(value)
                except:
                    mongo_filter[key] = value
            elif isinstance(value, list):
                # Array query
                mongo_filter[key] = {'$in': value}
            elif isinstance(value, dict) and 'min' in value or 'max' in value:
                # Range query
                range_query = {}
                if 'min' in value:
                    range_query['$gte'] = value['min']
                if 'max' in value:
                    range_query['$lte'] = value['max']
                mongo_filter[key] = range_query
            else:
                mongo_filter[key] = value
        
        return mongo_filter


class QueryBuilder:
    """Build optimized aggregation pipelines"""
    
    @staticmethod
    def match_stage(filters: Dict[str, Any]) -> Dict:
        """Create $match stage"""
        return {'$match': QueryOptimizer.build_filter(filters)}
    
    @staticmethod
    def sort_stage(sort_by: str = '-created_at') -> Dict:
        """Create $sort stage"""
        sorts = {}
        for field, direction in QueryOptimizer.build_sort_pipeline(sort_by):
            sorts[field] = 1 if direction == ASCENDING else -1
        return {'$sort': sorts}
    
    @staticmethod
    def skip_stage(skip: int) -> Dict:
        """Create $skip stage"""
        return {'$skip': skip}
    
    @staticmethod
    def limit_stage(limit: int) -> Dict:
        """Create $limit stage"""
        return {'$limit': limit}
    
    @staticmethod
    def project_stage(fields: Optional[List[str]] = None) -> Dict:
        """Create $project stage"""
        projection = {'_id': 1}
        if fields:
            for field in fields:
                projection[field] = 1
        return {'$project': projection}
    
    @staticmethod
    def lookup_stage(from_collection: str, local_field: str, 
                    foreign_field: str, as_field: str) -> Dict:
        """Create $lookup stage for joins"""
        return {
            '$lookup': {
                'from': from_collection,
                'localField': local_field,
                'foreignField': foreign_field,
                'as': as_field
            }
        }
    
    @staticmethod
    def group_stage(group_id: str, **aggregations) -> Dict:
        """Create $group stage"""
        group = {'_id': group_id}
        group.update(aggregations)
        return {'$group': group}
    
    @staticmethod
    def build_pipeline(stages: List[Dict]) -> List[Dict]:
        """Build complete aggregation pipeline"""
        return stages


class DatabaseOptimizer:
    """Main database optimization service"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.index_manager = IndexManager(db)
        self.query_optimizer = QueryOptimizer()
        self.query_builder = QueryBuilder()
    
    async def optimize_collection(self, collection_name: str):
        """Optimize a specific collection"""
        try:
            collection = self.db[collection_name]
            
            # Get collection stats
            stats = await self.db.command('collStats', collection_name)
            
            return {
                'name': collection_name,
                'document_count': stats.get('count', 0),
                'size_bytes': stats.get('size', 0),
                'avg_document_size': stats.get('avgObjSize', 0),
                'indexes': await self.index_manager.analyze_indexes()
            }
        except Exception as e:
            print(f"❌ Optimization failed for {collection_name}: {e}")
            return None
    
    async def get_slow_queries(self) -> List[Dict]:
        """Get slow queries from profiling"""
        try:
            profiling = self.db['system.profile']
            slow_queries = []
            
            async for doc in profiling.find(
                {'millis': {'$gt': 100}}
            ).sort('ts', -1).limit(10):
                slow_queries.append({
                    'command': doc.get('command'),
                    'duration_ms': doc.get('millis'),
                    'timestamp': doc.get('ts')
                })
            
            return slow_queries
        except Exception as e:
            print(f"❌ Could not get slow queries: {e}")
            return []


# Global database pool
db_pool = DatabasePool()
