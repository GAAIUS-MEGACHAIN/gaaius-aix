#!/usr/bin/env python3
"""
PHASE 4 QUICK REFERENCE - Commands and Operations
"""

QUICK_COMMANDS = """
╔═══════════════════════════════════════════════════════════════════════════╗
║                  PHASE 4: QUICK REFERENCE GUIDE                          ║
║              Commands, Operations, and Integration Steps                  ║
╚═══════════════════════════════════════════════════════════════════════════╝


🚀 GETTING STARTED
═══════════════════════════════════════════════════════════════════════════

1. Install Dependencies
   $ pip install -r requirements.txt

2. Start Services (Docker Compose - optional)
   $ docker-compose up -d

3. Run Tests
   $ pytest tests/test_phase4.py -v

4. Import in Your Application
   from backend.phase4_integration import setup_phase4


📝 FASTAPI INTEGRATION
═══════════════════════════════════════════════════════════════════════════

# Add to backend/server.py

from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from backend.phase4_integration import Phase4Integration

app = FastAPI()
phase4 = Phase4Integration()

@app.on_event("startup")
async def startup_event():
    await phase4.setup_phase4(app)
    print("✅ Phase 4 initialized successfully")

@app.on_event("shutdown")
async def shutdown_event():
    await phase4._on_shutdown()
    print("✅ Phase 4 shutdown complete")

# Health Check
@app.get("/health/phase4")
async def phase4_health():
    return await phase4.health_check()


🌐 WEBSOCKET ENDPOINTS
═══════════════════════════════════════════════════════════════════════════

# Chat Channel
$ wscat -c ws://localhost:8000/ws/chat/general
> {"type": "message", "content": "Hello, World!", "user": "alice"}

# Notifications
$ wscat -c ws://localhost:8000/ws/notifications
< {"type": "notification", "message": "Video published"}

# Live Metrics
$ wscat -c ws://localhost:8000/ws/live/video123
< {"type": "metrics", "views": 1250, "likes": 50}


🔍 SEARCH OPERATIONS
═══════════════════════════════════════════════════════════════════════════

# Full-text Search
GET /search/videos?q=machine%20learning&category=tech

# With Filters
GET /search/videos?q=python&duration_min=5&duration_max=30&rating_min=4.5

# Autocomplete Suggestions
GET /search/suggestions?q=python%20tu

# Trending Videos
GET /trending?period=7d

# Related Videos
GET /related/video123?limit=10


💡 RECOMMENDATIONS API
═══════════════════════════════════════════════════════════════════════════

# Get Personalized Recommendations
GET /recommendations/user123

# Get Collaborative Filtering Only
GET /recommendations/user123?strategy=collaborative

# Get Content-Based Only
GET /recommendations/user123?strategy=content

# Track User Interaction
POST /interactions/track
{
  "user_id": "user123",
  "video_id": "video456",
  "interaction_type": "watch",
  "duration": 1200
}


🛡️ CONTENT MODERATION
═══════════════════════════════════════════════════════════════════════════

# Flag Content
POST /moderate/flag
{
  "video_id": "video123",
  "flag_type": "explicit_content",
  "reason": "Contains explicit material"
}

# Get Moderation Queue
GET /moderate/queue?priority=high&limit=10

# Review Flagged Content
POST /moderate/review
{
  "flag_id": "flag_123",
  "action": "strike",
  "reason": "Violates community guidelines"
}

# Appeal Moderation Decision
POST /moderate/appeal
{
  "flag_id": "flag_123",
  "reason": "False positive - educational content"
}

# Get User Violations
GET /moderate/violations/user123


📊 MESSAGE QUEUE OPERATIONS
═══════════════════════════════════════════════════════════════════════════

# Publish Event to Queue
POST /queue/publish
{
  "task_type": "index_video",
  "video_id": "video123",
  "priority": 5
}

# Check Queue Status
GET /queue/status

# Check Dead Letter Queue
GET /queue/dlq

# Retry Failed Messages
POST /queue/retry-dlq?max_age_hours=1


⚙️ SYSTEM OPERATIONS
═══════════════════════════════════════════════════════════════════════════

# System Health Check
GET /health/phase4

# Real-time Metrics
GET /metrics/realtime

# Recommendation Engine Metrics
GET /metrics/recommendations

# Message Queue Metrics
GET /metrics/queue

# Search Engine Metrics
GET /metrics/search


🧪 TESTING COMMANDS
═══════════════════════════════════════════════════════════════════════════

# Run All Phase 4 Tests
$ pytest tests/test_phase4.py -v

# Run Specific Test Class
$ pytest tests/test_phase4.py::TestWebSocketIntegration -v

# Run Performance Tests
$ pytest tests/test_phase4.py::TestPhase4Performance -v

# Run Stress Tests
$ pytest tests/test_phase4.py::TestPhase4Stress -v

# Run with Coverage
$ pytest tests/test_phase4.py --cov=backend --cov-report=html

# Run Tests in Parallel
$ pytest tests/test_phase4.py -n auto


📦 DOCKER COMMANDS
═══════════════════════════════════════════════════════════════════════════

# Start All Services
$ docker-compose up -d

# View Logs
$ docker-compose logs -f

# Stop Services
$ docker-compose down

# Restart Services
$ docker-compose restart

# Access RabbitMQ Admin
http://localhost:15672 (guest/guest)

# Access Elasticsearch
http://localhost:9200

# Access MongoDB
mongodb://localhost:27017


🔧 ENVIRONMENT CONFIGURATION
═══════════════════════════════════════════════════════════════════════════

Create .env file:

# Redis
REDIS_URL=redis://localhost:6379
REDIS_DB=0

# RabbitMQ
AMQP_URL=amqp://guest:guest@localhost:5672/
RABBITMQ_VHOST=/

# Elasticsearch
ELASTICSEARCH_URL=http://localhost:9200
ES_INDEX_PREFIX=videos

# MongoDB
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB=videos_app

# Application
DEBUG=False
LOG_LEVEL=INFO
WORKERS=4


📋 MONITORING & OBSERVABILITY
═══════════════════════════════════════════════════════════════════════════

# View Logs
$ tail -f logs/phase4.log

# Monitor WebSocket Connections
$ watch -n 1 'curl http://localhost:8000/health/phase4'

# Monitor Message Queue Depth
$ curl http://localhost:8000/metrics/queue | jq '.queue_depth'

# Monitor Recommendation Cache Hit Rate
$ curl http://localhost:8000/metrics/recommendations | jq '.cache_hit_rate'

# Real-time Metrics
$ watch -n 1 'curl http://localhost:8000/metrics/realtime'


🐛 TROUBLESHOOTING
═══════════════════════════════════════════════════════════════════════════

# Check RabbitMQ Connection
$ python -c "import aio_pika; print('✅ aio-pika installed')"

# Check Elasticsearch Connection
$ curl -X GET "localhost:9200/_cluster/health"

# Check Redis Connection
$ redis-cli ping

# Check MongoDB Connection
$ mongo --eval "db.adminCommand('ping')"

# View Phase 4 Debug Logs
$ grep "Phase4" logs/*.log | tail -50

# Test WebSocket Connection
$ python -c "
import asyncio
from websockets import connect
async def test():
    async with connect('ws://localhost:8000/ws/chat/test') as ws:
        print('✅ WebSocket connected')
asyncio.run(test())
"


📈 PERFORMANCE TUNING
═══════════════════════════════════════════════════════════════════════════

# Optimize Redis
redis-cli CONFIG SET maxmemory-policy allkeys-lru

# Optimize RabbitMQ Prefetch
connection.channel().basic_qos(prefetch_count=10)

# Optimize Elasticsearch Refresh
PUT /videos/_settings
{
  "index": {
    "refresh_interval": "30s"
  }
}

# Optimize MongoDB Indexes
db.videos.createIndex({"created_at": -1})
db.interactions.createIndex({"user_id": 1, "created_at": -1})


🚀 DEPLOYMENT
═══════════════════════════════════════════════════════════════════════════

# Build Docker Image
$ docker build -f backend/Dockerfile -t videos-api:phase4 .

# Push to Registry
$ docker tag videos-api:phase4 registry.example.com/videos-api:phase4
$ docker push registry.example.com/videos-api:phase4

# Deploy to Kubernetes
$ kubectl apply -f k8s/phase4-deployment.yaml

# Scale Workers
$ kubectl scale deployment videos-worker --replicas=10

# Check Deployment Status
$ kubectl get pods -l app=videos-api


📊 EXAMPLE WORKFLOWS
═══════════════════════════════════════════════════════════════════════════

# Complete Search + Recommendation Workflow
1. GET /search/videos?q=python - Search for videos
2. GET /recommendations/user123 - Get personalized recommendations
3. POST /interactions/track - Track user interaction
4. GET /related/video123 - Get related content

# Complete Moderation Workflow
1. POST /moderate/flag - Flag content
2. GET /moderate/queue - Check queue
3. POST /moderate/review - Submit decision
4. GET /moderate/violations/user123 - View violations

# Complete Chat Workflow
1. WS /ws/chat/general - Join channel
2. Send message via WebSocket
3. GET /chat/general/history - Get message history
4. WS /ws/notifications - Receive notifications


💾 DATABASE OPERATIONS
═══════════════════════════════════════════════════════════════════════════

# Backup MongoDB
$ mongodump --uri="mongodb://localhost:27017/videos_app" --out=backup

# Restore MongoDB
$ mongorestore --uri="mongodb://localhost:27017/videos_app" backup/videos_app

# Backup Redis
$ redis-cli --rdb /path/to/dump.rdb

# Elasticsearch Snapshot
POST /_snapshot/my_backup
{
  "type": "fs",
  "settings": {
    "location": "/mnt/snapshots"
  }
}


🎯 COMMON TASKS
═══════════════════════════════════════════════════════════════════════════

# Index All Videos
curl -X POST http://localhost:8000/search/reindex

# Retrain Recommendation Models
curl -X POST http://localhost:8000/recommendations/retrain

# Clear Recommendation Cache
curl -X DELETE http://localhost:8000/recommendations/cache

# Process DLQ Messages
curl -X POST http://localhost:8000/queue/process-dlq

# Get System Stats
curl http://localhost:8000/metrics/system


═══════════════════════════════════════════════════════════════════════════

Need help? Check:
  📖 PHASE4_STATUS.md - Detailed status
  🚀 PHASE4_DELIVERY_SUMMARY.py - Complete overview
  📝 Backend module docstrings for API details
  🧪 tests/test_phase4.py - Usage examples

═══════════════════════════════════════════════════════════════════════════
"""

if __name__ == "__main__":
    import sys
    if sys.stdout.encoding != 'utf-8':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    print(QUICK_COMMANDS)
    print("\n✅ Phase 4 Quick Reference Ready")
