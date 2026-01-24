"""
PHASE 4: Message Queue & Event Streaming Infrastructure
Production-grade async task processing and event streaming
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, Callable, List
from enum import Enum
from datetime import datetime
import uuid
from dataclasses import dataclass, asdict
from functools import wraps

import aio_pika
from aio_pika import Channel, Exchange, Queue
from motor.motor_asyncio import AsyncIOMotorDatabase
import redis.asyncio as aioredis


logger = logging.getLogger(__name__)


class EventType(str, Enum):
    """Event types for event streaming"""
    VIDEO_UPLOADED = "video.uploaded"
    VIDEO_PROCESSED = "video.processed"
    VIDEO_DELETED = "video.deleted"
    USER_REGISTERED = "user.registered"
    USER_FOLLOWED = "user.followed"
    COMMENT_POSTED = "comment.posted"
    VIDEO_LIKED = "video.liked"
    LIVE_STREAM_STARTED = "live_stream.started"
    LIVE_STREAM_ENDED = "live_stream.ended"
    MONETIZATION_EVENT = "monetization.event"
    CONTENT_FLAGGED = "content.flagged"
    RECOMMENDATION_UPDATED = "recommendation.updated"


@dataclass
class Event:
    """Event structure for event streaming"""
    event_type: EventType
    entity_id: str
    entity_type: str
    user_id: str
    timestamp: str
    data: Dict[str, Any]
    event_id: str = None
    
    def __post_init__(self):
        if self.event_id is None:
            self.event_id = str(uuid.uuid4())
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict())


class MessageQueueManager:
    """RabbitMQ-based message queue for async task processing"""
    
    def __init__(self, amqp_url: str, db: AsyncIOMotorDatabase):
        self.amqp_url = amqp_url
        self.db = db
        self.connection: Optional[aio_pika.Connection] = None
        self.channel: Optional[Channel] = None
        self.exchanges: Dict[str, Exchange] = {}
        self.queues: Dict[str, Queue] = {}
        self.handlers: Dict[str, List[Callable]] = {}
        self.tasks_collection = db["message_queue_tasks"]
    
    async def connect(self) -> None:
        """Connect to RabbitMQ"""
        try:
            self.connection = await aio_pika.connect_robust(self.amqp_url)
            self.channel = await self.connection.channel()
            logger.info("Connected to RabbitMQ")
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise
    
    async def close(self) -> None:
        """Close RabbitMQ connection"""
        if self.connection:
            await self.connection.close()
    
    async def declare_queue(
        self,
        queue_name: str,
        durable: bool = True,
        max_retries: int = 3
    ) -> Queue:
        """Declare queue with retry logic"""
        if queue_name in self.queues:
            return self.queues[queue_name]
        
        queue = await self.channel.declare_queue(
            queue_name,
            durable=durable,
            arguments={
                "x-max-priority": 10,  # Priority queue support
                "x-message-ttl": 86400000,  # 24 hours
            }
        )
        
        self.queues[queue_name] = queue
        logger.info(f"Declared queue: {queue_name}")
        return queue
    
    async def declare_exchange(
        self,
        exchange_name: str,
        exchange_type: str = "topic"
    ) -> Exchange:
        """Declare exchange for pub/sub"""
        if exchange_name in self.exchanges:
            return self.exchanges[exchange_name]
        
        exchange = await self.channel.declare_exchange(
            exchange_name,
            aio_pika.ExchangeType(exchange_type),
            durable=True
        )
        
        self.exchanges[exchange_name] = exchange
        logger.info(f"Declared exchange: {exchange_name}")
        return exchange
    
    async def publish_task(
        self,
        queue_name: str,
        task_type: str,
        payload: Dict[str, Any],
        priority: int = 5,
        delay_seconds: int = 0
    ) -> str:
        """Publish async task to queue"""
        task_id = str(uuid.uuid4())
        
        task_message = {
            "task_id": task_id,
            "task_type": task_type,
            "payload": payload,
            "created_at": datetime.utcnow().isoformat(),
            "retry_count": 0,
        }
        
        queue = await self.declare_queue(queue_name)
        
        # Create message with priority
        message = aio_pika.Message(
            body=json.dumps(task_message).encode(),
            priority=priority,
            content_type="application/json",
        )
        
        # Publish message
        await self.channel.default_exchange.publish(
            message,
            routing_key=queue_name
        )
        
        # Store in database for tracking
        await self.tasks_collection.insert_one({
            "_id": task_id,
            "queue_name": queue_name,
            "task_type": task_type,
            "payload": payload,
            "status": "queued",
            "created_at": datetime.utcnow(),
            "started_at": None,
            "completed_at": None,
            "error": None,
        })
        
        logger.info(f"Published task {task_id} to {queue_name}")
        return task_id
    
    async def consume_tasks(
        self,
        queue_name: str,
        handler: Callable,
        prefetch_count: int = 10
    ) -> None:
        """Consume tasks from queue with handler"""
        queue = await self.declare_queue(queue_name)
        await self.channel.set_qos(prefetch_count=prefetch_count)
        
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                try:
                    task = json.loads(message.body.decode())
                    
                    # Update status
                    await self.tasks_collection.update_one(
                        {"_id": task["task_id"]},
                        {
                            "$set": {
                                "status": "processing",
                                "started_at": datetime.utcnow(),
                            }
                        }
                    )
                    
                    # Call handler
                    await handler(task)
                    
                    # Mark as completed
                    await self.tasks_collection.update_one(
                        {"_id": task["task_id"]},
                        {
                            "$set": {
                                "status": "completed",
                                "completed_at": datetime.utcnow(),
                            }
                        }
                    )
                    
                    # Acknowledge message
                    await message.ack()
                    
                    logger.info(f"Task {task['task_id']} completed")
                    
                except Exception as e:
                    logger.error(f"Error processing task: {e}")
                    
                    task = json.loads(message.body.decode())
                    retry_count = task.get("retry_count", 0)
                    
                    if retry_count < 3:
                        # Re-queue with incremented retry count
                        task["retry_count"] = retry_count + 1
                        message.body = json.dumps(task).encode()
                        await self.channel.default_exchange.publish(
                            message,
                            routing_key=queue_name
                        )
                    else:
                        # Max retries exceeded
                        await self.tasks_collection.update_one(
                            {"_id": task["task_id"]},
                            {
                                "$set": {
                                    "status": "failed",
                                    "error": str(e),
                                    "completed_at": datetime.utcnow(),
                                }
                            }
                        )
                    
                    await message.ack()


class EventStreamManager:
    """Event streaming for real-time data processing"""
    
    def __init__(self, redis: aioredis.Redis, db: AsyncIOMotorDatabase):
        self.redis = redis
        self.db = db
        self.events_collection = db["events"]
        self.subscribers: Dict[EventType, List[Callable]] = {}
    
    async def publish_event(self, event: Event) -> None:
        """Publish event to stream"""
        # Store in database
        await self.events_collection.insert_one({
            "_id": event.event_id,
            "event_type": event.event_type.value,
            "entity_id": event.entity_id,
            "entity_type": event.entity_type,
            "user_id": event.user_id,
            "timestamp": datetime.fromisoformat(event.timestamp),
            "data": event.data,
        })
        
        # Publish to Redis stream
        await self.redis.xadd(
            f"stream:{event.event_type.value}",
            {
                "event_id": event.event_id,
                "entity_id": event.entity_id,
                "data": event.to_json(),
            }
        )
        
        # Set stream retention
        await self.redis.xtrim(
            f"stream:{event.event_type.value}",
            maxlen=10000
        )
        
        logger.info(f"Published event: {event.event_type.value} ({event.event_id})")
        
        # Trigger subscribers
        await self._trigger_subscribers(event)
    
    def subscribe(self, event_type: EventType, handler: Callable) -> None:
        """Subscribe to events"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(handler)
        logger.info(f"Subscribed to {event_type.value}")
    
    async def _trigger_subscribers(self, event: Event) -> None:
        """Trigger all subscribers for event"""
        if event.event_type not in self.subscribers:
            return
        
        for handler in self.subscribers[event.event_type]:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception as e:
                logger.error(f"Error in event handler: {e}")
    
    async def get_event_history(
        self,
        event_type: EventType,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get event history from Redis stream"""
        stream_key = f"stream:{event_type.value}"
        
        # Get last N events from stream
        events_data = await self.redis.xrevrange(stream_key, count=limit)
        
        events = []
        for event_id, event_dict in events_data:
            event_dict = {k.decode(): v.decode() for k, v in event_dict.items()}
            events.append({
                "event_id": event_id.decode(),
                **event_dict
            })
        
        return events
    
    async def get_entity_events(
        self,
        entity_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get all events for specific entity"""
        events = await self.events_collection.find(
            {"entity_id": entity_id},
            sort=[("timestamp", -1)],
            limit=limit
        ).to_list(limit)
        
        # Convert timestamps
        for event in events:
            event["_id"] = str(event["_id"])
            event["timestamp"] = event["timestamp"].isoformat()
        
        return events


class DeadLetterQueue:
    """Manage failed messages with retry logic"""
    
    def __init__(self, redis: aioredis.Redis, db: AsyncIOMotorDatabase):
        self.redis = redis
        self.db = db
        self.dlq_collection = db["dead_letter_queue"]
    
    async def add_to_dlq(
        self,
        message: Dict[str, Any],
        error: str,
        retry_count: int
    ) -> str:
        """Add failed message to DLQ"""
        dlq_id = str(uuid.uuid4())
        
        dlq_entry = {
            "_id": dlq_id,
            "message": message,
            "error": error,
            "retry_count": retry_count,
            "failed_at": datetime.utcnow(),
            "retry_after": datetime.utcnow() + asyncio.timedelta(
                minutes=2 ** retry_count  # Exponential backoff
            ),
            "resolved": False,
        }
        
        await self.dlq_collection.insert_one(dlq_entry)
        
        # Add to Redis sorted set for scheduled retry
        await self.redis.zadd(
            "dlq:retry_schedule",
            {dlq_id: dlq_entry["retry_after"].timestamp()}
        )
        
        logger.error(f"Added message to DLQ: {dlq_id} (retry #{retry_count})")
        return dlq_id
    
    async def get_pending_retries(self) -> List[Dict[str, Any]]:
        """Get messages ready for retry"""
        now = datetime.utcnow().timestamp()
        
        # Get all messages due for retry
        dlq_ids = await self.redis.zrangebyscore(
            "dlq:retry_schedule",
            0,
            now
        )
        
        pending = []
        for dlq_id in dlq_ids:
            entry = await self.dlq_collection.find_one(
                {"_id": dlq_id.decode(), "resolved": False}
            )
            if entry:
                pending.append(entry)
        
        return pending
    
    async def mark_resolved(self, dlq_id: str) -> None:
        """Mark DLQ entry as resolved"""
        await self.dlq_collection.update_one(
            {"_id": dlq_id},
            {"$set": {"resolved": True, "resolved_at": datetime.utcnow()}}
        )
        
        await self.redis.zrem("dlq:retry_schedule", dlq_id)


class WorkerPool:
    """Distributed worker pool for parallel task processing"""
    
    def __init__(self, redis: aioredis.Redis, worker_id: str):
        self.redis = redis
        self.worker_id = worker_id
        self.active = False
    
    async def register_worker(self) -> None:
        """Register worker in pool"""
        worker_info = {
            "worker_id": self.worker_id,
            "registered_at": datetime.utcnow().isoformat(),
            "status": "idle",
        }
        
        await self.redis.setex(
            f"worker:{self.worker_id}",
            300,  # 5-minute TTL
            json.dumps(worker_info)
        )
        
        logger.info(f"Worker {self.worker_id} registered")
    
    async def heartbeat(self) -> None:
        """Send heartbeat to keep worker alive"""
        await self.redis.expire(f"worker:{self.worker_id}", 300)
    
    async def get_active_workers(self) -> int:
        """Get count of active workers"""
        keys = await self.redis.keys("worker:*")
        return len(keys)
    
    async def set_status(self, status: str) -> None:
        """Update worker status"""
        worker_info = await self.redis.get(f"worker:{self.worker_id}")
        if worker_info:
            data = json.loads(worker_info)
            data["status"] = status
            await self.redis.setex(
                f"worker:{self.worker_id}",
                300,
                json.dumps(data)
            )
