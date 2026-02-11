"""
PHASE 4: Complete Integration Module
Integrates WebSockets, Message Queues, Search, Recommendations, and Moderation
"""

import asyncio
import logging
from typing import Optional, Dict, Any

from fastapi import FastAPI, WebSocket
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorClient
import redis.asyncio as aioredis
import aio_pika

from backend.phase4_websocket import (
    ConnectionManager,
    ChatManager,
    NotificationManager,
    LiveMetricsManager,
    PresenceManager
)
from backend.phase4_message_queue import (
    MessageQueueManager,
    EventStreamManager,
    DeadLetterQueue,
    WorkerPool
)
from backend.phase4_search import ElasticsearchManager
from backend.phase4_recommendations import RecommendationEngine
from backend.phase4_moderation import ContentModerationSystem


logger = logging.getLogger(__name__)


class Phase4Integration:
    """Central integration point for all Phase 4 features"""
    
    def __init__(self):
        self.app: Optional[FastAPI] = None
        self.db: Optional[AsyncIOMotorDatabase] = None
        self.redis: Optional[aioredis.Redis] = None
        self.mongodb_client: Optional[AsyncIOMotorClient] = None
        
        # Components
        self.connection_manager: Optional[ConnectionManager] = None
        self.chat_manager: Optional[ChatManager] = None
        self.notification_manager: Optional[NotificationManager] = None
        self.live_metrics: Optional[LiveMetricsManager] = None
        self.presence_manager: Optional[PresenceManager] = None
        
        self.message_queue: Optional[MessageQueueManager] = None
        self.event_stream: Optional[EventStreamManager] = None
        self.dlq: Optional[DeadLetterQueue] = None
        self.worker_pool: Optional[WorkerPool] = None
        
        self.search_engine: Optional[ElasticsearchManager] = None
        self.recommendation_engine: Optional[RecommendationEngine] = None
        self.moderation_system: Optional[ContentModerationSystem] = None
        
        self.background_tasks = []
    
    async def setup_phase4(
        self,
        app: FastAPI,
        db: AsyncIOMotorDatabase,
        redis_url: str = "redis://localhost:6379",
        amqp_url: str = "amqp://guest:guest@localhost/",
        elasticsearch_url: str = "http://localhost:9200",
        worker_id: str = "worker-1"
    ) -> None:
        """Initialize all Phase 4 components"""
        
        logger.info("🚀 Initializing Phase 4: Advanced Platform Features")
        
        self.app = app
        self.db = db
        
        # Connect to Redis
        logger.info("📡 Connecting to Redis...")
        self.redis = await aioredis.from_url(redis_url, decode_responses=False)
        
        # Initialize WebSocket managers
        logger.info("📡 Initializing WebSocket infrastructure...")
        self.connection_manager = ConnectionManager(self.redis, db)
        self.chat_manager = ChatManager(self.redis, db)
        self.notification_manager = NotificationManager(self.redis, db)
        self.live_metrics = LiveMetricsManager(self.redis, db)
        self.presence_manager = PresenceManager(self.redis)
        
        # Initialize Message Queue
        logger.info("📨 Initializing Message Queue...")
        self.message_queue = MessageQueueManager(amqp_url, db)
        await self.message_queue.connect()
        
        # Initialize Event Streaming
        logger.info("📡 Initializing Event Streaming...")
        self.event_stream = EventStreamManager(self.redis, db)
        
        # Initialize Dead Letter Queue
        logger.info("🔄 Initializing Dead Letter Queue...")
        self.dlq = DeadLetterQueue(self.redis, db)
        
        # Initialize Worker Pool
        logger.info("👷 Initializing Worker Pool...")
        self.worker_pool = WorkerPool(self.redis, worker_id)
        await self.worker_pool.register_worker()
        
        # Initialize Elasticsearch Search
        logger.info("🔍 Initializing Elasticsearch...")
        self.search_engine = ElasticsearchManager(elasticsearch_url, db)
        await self.search_engine.initialize_indexes()
        
        # Initialize Recommendation Engine
        logger.info("🤖 Initializing ML Recommendation Engine...")
        self.recommendation_engine = RecommendationEngine(self.redis, db)
        
        # Initialize Content Moderation
        logger.info("🛡️ Initializing Content Moderation...")
        self.moderation_system = ContentModerationSystem(self.redis, db)
        
        # Register startup/shutdown events
        app.add_event_handler("startup", self._on_startup)
        app.add_event_handler("shutdown", self._on_shutdown)
        
        logger.info("✅ Phase 4 initialization complete!")
    
    async def _on_startup(self) -> None:
        """Handle application startup"""
        logger.info("📡 Phase 4 startup tasks...")
        
        # Start background tasks
        self.background_tasks = [
            asyncio.create_task(self._heartbeat_loop()),
            asyncio.create_task(self._process_dlq_loop()),
            asyncio.create_task(self._recommendation_training_loop()),
        ]
        
        logger.info("✅ Phase 4 background tasks started")
    
    async def _on_shutdown(self) -> None:
        """Handle application shutdown"""
        logger.info("🔴 Phase 4 shutdown...")
        
        # Cancel background tasks
        for task in self.background_tasks:
            task.cancel()
        
        # Close connections
        if self.redis:
            await self.redis.close()
        
        if self.message_queue:
            await self.message_queue.close()
        
        logger.info("✅ Phase 4 shutdown complete")
    
    async def _heartbeat_loop(self) -> None:
        """Periodic heartbeat for workers and metrics"""
        while True:
            try:
                await asyncio.sleep(60)  # Every minute
                
                # Worker heartbeat
                if self.worker_pool:
                    await self.worker_pool.heartbeat()
                
                # Log active connections
                stats = await self.connection_manager.get_channel_stats("main")
                logger.debug(f"Active connections: {stats['active_connections']}")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Heartbeat loop error: {e}")
    
    async def _process_dlq_loop(self) -> None:
        """Process failed messages from dead letter queue"""
        while True:
            try:
                await asyncio.sleep(300)  # Every 5 minutes
                
                if self.dlq:
                    pending = await self.dlq.get_pending_retries()
                    logger.info(f"Processing {len(pending)} pending DLQ messages")
                    
                    for entry in pending:
                        logger.info(f"Retrying DLQ message: {entry['_id']}")
                        # Re-publish to queue
                        # In production, this would re-submit to the appropriate queue
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"DLQ processing loop error: {e}")
    
    async def _recommendation_training_loop(self) -> None:
        """Periodically retrain recommendation models"""
        while True:
            try:
                await asyncio.sleep(3600)  # Every hour
                
                if self.recommendation_engine:
                    logger.info("Starting recommendation model retraining...")
                    await self.recommendation_engine.train_model()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Recommendation training loop error: {e}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Get Phase 4 health status"""
        health = {
            "websocket": await self._check_websocket_health(),
            "message_queue": await self._check_mq_health(),
            "elasticsearch": await self._check_search_health(),
            "redis": await self._check_redis_health(),
        }
        
        return {
            "phase4_status": "healthy" if all(v for v in health.values()) else "degraded",
            "components": health,
            "timestamp": asyncio.get_event_loop().time(),
        }
    
    async def _check_websocket_health(self) -> bool:
        """Check WebSocket health"""
        try:
            stats = await self.connection_manager.get_channel_stats("main")
            return True
        except Exception as e:
            logger.error(f"WebSocket health check failed: {e}")
            return False
    
    async def _check_mq_health(self) -> bool:
        """Check Message Queue health"""
        try:
            # Check if connection is alive
            return self.message_queue and self.message_queue.connection is not None
        except Exception as e:
            logger.error(f"MQ health check failed: {e}")
            return False
    
    async def _check_search_health(self) -> bool:
        """Check Elasticsearch health"""
        try:
            info = self.search_engine.es_client.info()
            return info is not None
        except Exception as e:
            logger.error(f"Search health check failed: {e}")
            return False
    
    async def _check_redis_health(self) -> bool:
        """Check Redis health"""
        try:
            pong = await self.redis.ping()
            return pong
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return False


# Global instance
phase4_integration = Phase4Integration()


async def setup_phase4(app: FastAPI, db: AsyncIOMotorDatabase) -> None:
    """Setup Phase 4 in FastAPI app"""
    await phase4_integration.setup_phase4(app, db)
