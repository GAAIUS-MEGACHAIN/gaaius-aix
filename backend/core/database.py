"""
GAAIUS Database Layer with Connection Management
MongoDB async driver with pooling, transactions, indexes, migrations
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from contextlib import asynccontextmanager

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
import pymongo
from pymongo.errors import DuplicateKeyError, OperationFailure

from backend.core.config import get_settings
from backend.core.exceptions import DatabaseError, ErrorCode
from backend.core.logging import StructuredLogger, LogEventType

logger = logging.getLogger(__name__)
settings = get_settings()


class DatabaseManager:
    """Manages MongoDB connections and lifecycle"""
    
    _client: Optional[AsyncIOMotorClient] = None
    _db: Optional[AsyncIOMotorDatabase] = None
    
    @classmethod
    async def connect(cls) -> AsyncIOMotorDatabase:
        """
        Connect to MongoDB with optimal configuration
        
        Returns:
            AsyncIOMotorDatabase instance
            
        Raises:
            DatabaseError: If connection fails
        """
        try:
            cls._client = AsyncIOMotorClient(
                settings.MONGODB_URI,
                maxPoolSize=settings.MONGODB_POOL_SIZE,
                minPoolSize=10,
                maxIdleTimeMS=settings.MONGODB_MAX_IDLE_TIME_MS,
                connectTimeoutMS=settings.MONGODB_CONNECT_TIMEOUT_MS,
                socketTimeoutMS=settings.MONGODB_SOCKET_TIMEOUT_MS,
                serverSelectionTimeoutMS=settings.MONGODB_SERVER_SELECTION_TIMEOUT_MS,
                retryWrites=True,
                w="majority",
                journal=True
            )
            
            # Test connection
            await cls._client.admin.command('ping')
            
            cls._db = cls._client[settings.DATABASE_NAME]
            
            logger.info(f"Connected to MongoDB: {settings.DATABASE_NAME}")
            StructuredLogger.log_event(
                event_type=LogEventType.HEALTH_CHECK,
                details={"service": "mongodb", "status": "connected"}
            )
            
            return cls._db
        except Exception as e:
            logger.error(f"MongoDB connection failed: {str(e)}")
            raise DatabaseError(
                message="Failed to connect to MongoDB",
                error_code=ErrorCode.DATABASE_CONNECTION_ERROR,
                cause=e
            )
    
    @classmethod
    async def disconnect(cls):
        """Disconnect from MongoDB"""
        if cls._client:
            cls._client.close()
            logger.info("Disconnected from MongoDB")
    
    @classmethod
    def get_db(cls) -> AsyncIOMotorDatabase:
        """Get database instance"""
        if not cls._db:
            raise DatabaseError(
                message="Database not connected",
                error_code=ErrorCode.DATABASE_CONNECTION_ERROR
            )
        return cls._db


class Collection:
    """Base collection wrapper with common operations"""
    
    def __init__(self, db: AsyncIOMotorDatabase, name: str):
        self.db = db
        self.collection: AsyncIOMotorCollection = db[name]
        self.name = name
    
    async def find_one(
        self,
        filter: Dict[str, Any],
        projection: Optional[Dict] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Find a single document
        
        Args:
            filter: Query filter
            projection: Fields to return
            
        Returns:
            Document or None
        """
        try:
            return await self.collection.find_one(filter, projection)
        except OperationFailure as e:
            raise DatabaseError(
                message=f"Failed to find document in {self.name}",
                operation="find_one",
                cause=e
            )
    
    async def find_many(
        self,
        filter: Dict[str, Any],
        projection: Optional[Dict] = None,
        skip: int = 0,
        limit: int = 100,
        sort: Optional[List[tuple]] = None
    ) -> List[Dict[str, Any]]:
        """
        Find multiple documents
        
        Args:
            filter: Query filter
            projection: Fields to return
            skip: Number of documents to skip
            limit: Max documents to return
            sort: Sort specifications
            
        Returns:
            List of documents
        """
        try:
            query = self.collection.find(filter, projection)
            
            if sort:
                query = query.sort(sort)
            
            query = query.skip(skip).limit(limit)
            
            return await query.to_list(length=limit)
        except OperationFailure as e:
            raise DatabaseError(
                message=f"Failed to find documents in {self.name}",
                operation="find_many",
                cause=e
            )
    
    async def count(self, filter: Dict[str, Any]) -> int:
        """Count documents matching filter"""
        try:
            return await self.collection.count_documents(filter)
        except OperationFailure as e:
            raise DatabaseError(
                message=f"Failed to count documents in {self.name}",
                operation="count",
                cause=e
            )
    
    async def insert_one(self, document: Dict[str, Any]) -> str:
        """
        Insert a single document
        
        Args:
            document: Document to insert
            
        Returns:
            Inserted document ID
            
        Raises:
            DatabaseError: If insert fails
        """
        try:
            # Add timestamps if not present
            if "created_at" not in document:
                document["created_at"] = datetime.utcnow()
            if "updated_at" not in document:
                document["updated_at"] = datetime.utcnow()
            
            result = await self.collection.insert_one(document)
            return str(result.inserted_id)
        except DuplicateKeyError as e:
            raise DatabaseError(
                message=f"Duplicate key in {self.name}",
                error_code=ErrorCode.RESOURCE_ALREADY_EXISTS,
                cause=e
            )
        except OperationFailure as e:
            raise DatabaseError(
                message=f"Failed to insert document in {self.name}",
                operation="insert_one",
                cause=e
            )
    
    async def insert_many(self, documents: List[Dict[str, Any]]) -> List[str]:
        """
        Insert multiple documents
        
        Args:
            documents: Documents to insert
            
        Returns:
            List of inserted document IDs
        """
        try:
            # Add timestamps
            now = datetime.utcnow()
            for doc in documents:
                if "created_at" not in doc:
                    doc["created_at"] = now
                if "updated_at" not in doc:
                    doc["updated_at"] = now
            
            result = await self.collection.insert_many(documents)
            return [str(id) for id in result.inserted_ids]
        except OperationFailure as e:
            raise DatabaseError(
                message=f"Failed to insert documents in {self.name}",
                operation="insert_many",
                cause=e
            )
    
    async def update_one(
        self,
        filter: Dict[str, Any],
        update: Dict[str, Any]
    ) -> int:
        """
        Update a single document
        
        Args:
            filter: Query filter
            update: Update operations
            
        Returns:
            Number of modified documents
        """
        try:
            # Add updated_at timestamp
            if "$set" not in update:
                update["$set"] = {}
            update["$set"]["updated_at"] = datetime.utcnow()
            
            result = await self.collection.update_one(filter, update)
            return result.modified_count
        except OperationFailure as e:
            raise DatabaseError(
                message=f"Failed to update document in {self.name}",
                operation="update_one",
                cause=e
            )
    
    async def update_many(
        self,
        filter: Dict[str, Any],
        update: Dict[str, Any]
    ) -> int:
        """Update multiple documents"""
        try:
            if "$set" not in update:
                update["$set"] = {}
            update["$set"]["updated_at"] = datetime.utcnow()
            
            result = await self.collection.update_many(filter, update)
            return result.modified_count
        except OperationFailure as e:
            raise DatabaseError(
                message=f"Failed to update documents in {self.name}",
                operation="update_many",
                cause=e
            )
    
    async def delete_one(self, filter: Dict[str, Any]) -> int:
        """Delete a single document"""
        try:
            result = await self.collection.delete_one(filter)
            return result.deleted_count
        except OperationFailure as e:
            raise DatabaseError(
                message=f"Failed to delete document in {self.name}",
                operation="delete_one",
                cause=e
            )
    
    async def delete_many(self, filter: Dict[str, Any]) -> int:
        """Delete multiple documents"""
        try:
            result = await self.collection.delete_many(filter)
            return result.deleted_count
        except OperationFailure as e:
            raise DatabaseError(
                message=f"Failed to delete documents in {self.name}",
                operation="delete_many",
                cause=e
            )
    
    async def create_index(
        self,
        keys: List[tuple],
        unique: bool = False,
        sparse: bool = False
    ):
        """Create index on collection"""
        try:
            await self.collection.create_index(
                keys,
                unique=unique,
                sparse=sparse
            )
            logger.info(f"Created index on {self.name}: {keys}")
        except Exception as e:
            logger.error(f"Failed to create index: {e}")
    
    async def create_indexes(self):
        """Create all necessary indexes - override in subclass"""
        pass
    
    async def aggregate(
        self,
        pipeline: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Execute aggregation pipeline"""
        try:
            cursor = self.collection.aggregate(pipeline)
            return await cursor.to_list(length=None)
        except OperationFailure as e:
            raise DatabaseError(
                message=f"Aggregation failed on {self.name}",
                operation="aggregate",
                cause=e
            )


class DatabaseTransaction:
    """Context manager for database transactions"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.session = None
    
    async def __aenter__(self):
        """Start transaction"""
        self.session = await self.db.client.start_session()
        await self.session.start_transaction()
        return self.session
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """End transaction (commit or rollback)"""
        try:
            if exc_type is None:
                await self.session.commit_transaction()
            else:
                await self.session.abort_transaction()
        finally:
            await self.session.end_session()


class IndexManager:
    """Manage database indexes for performance"""
    
    @staticmethod
    async def create_all_indexes(db: AsyncIOMotorDatabase):
        """Create all necessary indexes"""
        # Users collection
        users = db["users"]
        await users.create_index([("email", pymongo.ASCENDING)], unique=True)
        await users.create_index([("username", pymongo.ASCENDING)], unique=True)
        await users.create_index([("created_at", pymongo.DESCENDING)])
        
        # Courses collection
        courses = db["courses"]
        await courses.create_index([("instructor_id", pymongo.ASCENDING)])
        await courses.create_index([("category", pymongo.ASCENDING)])
        await courses.create_index([("status", pymongo.ASCENDING)])
        await courses.create_index([("created_at", pymongo.DESCENDING)])
        
        # Enrollments collection
        enrollments = db["enrollments"]
        await enrollments.create_index([("user_id", pymongo.ASCENDING), ("course_id", pymongo.ASCENDING)], unique=True)
        await enrollments.create_index([("user_id", pymongo.ASCENDING)])
        await enrollments.create_index([("course_id", pymongo.ASCENDING)])
        
        # Exams collection
        exams = db["exams"]
        await exams.create_index([("course_id", pymongo.ASCENDING)])
        
        # Exam Attempts
        attempts = db["exam_attempts"]
        await attempts.create_index([("user_id", pymongo.ASCENDING), ("exam_id", pymongo.ASCENDING)])
        await attempts.create_index([("submitted_at", pymongo.DESCENDING)])
        
        # Proctor Sessions
        sessions = db["proctor_sessions"]
        await sessions.create_index([("user_id", pymongo.ASCENDING)])
        await sessions.create_index([("exam_id", pymongo.ASCENDING)])
        await sessions.create_index([("expires_at", pymongo.ASCENDING)])
        
        # Facial Enrollments
        faces = db["facial_enrollments"]
        await faces.create_index([("user_id", pymongo.ASCENDING)], unique=True)
        await faces.create_index([("email", pymongo.ASCENDING)])
        
        # Certificates
        certs = db["certificates"]
        await certs.create_index([("user_id", pymongo.ASCENDING)])
        await certs.create_index([("course_id", pymongo.ASCENDING)])
        await certs.create_index([("verification_code", pymongo.ASCENDING)], unique=True)
        
        logger.info("All database indexes created")
