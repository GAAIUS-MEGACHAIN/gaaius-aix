"""
PHASE 9: Netflix Clone - Deployment & Quick Start Guide
Production Ready - Deploy Immediately
"""

# ============================================================================
# QUICK START (Local Development)
# ============================================================================

"""
1. SETUP DATABASE (PostgreSQL recommended)
   =====================================
   
   Option A: Local PostgreSQL
   ---------------------------
   # Install PostgreSQL 15+
   # macOS: brew install postgresql@15
   # Ubuntu: sudo apt-get install postgresql
   # Windows: Download from postgresql.org
   
   # Create database
   psql -U postgres
   CREATE DATABASE netflix_clone OWNER postgres;
   
   Option B: Docker PostgreSQL
   ---------------------------
   docker run --name netflix-db \
     -e POSTGRES_PASSWORD=password \
     -e POSTGRES_DB=netflix_clone \
     -p 5432:5432 \
     -d postgres:15-alpine
   
   Option C: Use SQLite (development only)
   ----------------------------------
   No setup needed - creates file automatically
   

2. SETUP REDIS (Caching & Rate Limiting)
   ======================================
   
   Option A: Local Redis
   ---------------------
   # macOS
   brew install redis
   redis-server
   
   # Ubuntu
   sudo apt-get install redis-server
   redis-server
   
   Option B: Docker Redis
   ----------------------
   docker run --name netflix-redis \
     -p 6379:6379 \
     -d redis:7-alpine
   

3. SETUP ELASTICSEARCH (Search)
   =============================
   
   Option A: Docker Elasticsearch
   --------------------------------
   docker run --name netflix-es \
     -e discovery.type=single-node \
     -p 9200:9200 \
     -d docker.elastic.co/elasticsearch/elasticsearch:8.10.0
   
   Option B: Local Installation
   ---------------------------
   # Download from elastic.co
   # Extract and run bin/elasticsearch
   

4. INSTALL PYTHON DEPENDENCIES
   ============================
   
   # Create virtual environment
   python -m venv .venv
   
   # Activate
   # macOS/Linux
   source .venv/bin/activate
   # Windows
   .venv\\Scripts\\activate
   
   # Install dependencies
   pip install -r requirements-phase9.txt
   

5. CONFIGURE ENVIRONMENT
   =======================
   
   # Create .env file
   cat > .env << EOF
   DATABASE_TYPE=postgresql
   DB_USER=postgres
   DB_PASSWORD=password
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=netflix_clone
   
   REDIS_HOST=localhost
   REDIS_PORT=6379
   
   ELASTICSEARCH_HOST=localhost
   ELASTICSEARCH_PORT=9200
   
   JWT_SECRET_KEY=your-secret-key-min-32-characters-here
   
   # Stripe (get from https://dashboard.stripe.com)
   STRIPE_SECRET_KEY=sk_test_xxxxx
   STRIPE_PUBLIC_KEY=pk_test_xxxxx
   STRIPE_WEBHOOK_SECRET=whsec_xxxxx
   
   # Groq API (optional, for AI moderation)
   GROQ_API_KEY=gsk_xxxxx
   
   # Sentry (optional, for error tracking)
   SENTRY_DSN=https://xxxxx@sentry.io/xxxxx
   
   LOG_LEVEL=INFO
   EOF


6. INITIALIZE DATABASE
   ====================
   
   python backend/database_models.py
   

7. RUN THE APPLICATION
   ====================
   
   # Development with auto-reload
   uvicorn backend.server:app --reload --port 8000
   
   # Production (with Gunicorn)
   gunicorn -w 4 -k uvicorn.workers.UvicornWorker backend.server:app
   

8. ACCESS THE APPLICATION
   =======================
   
   # Main API
   http://localhost:8000
   
   # API Documentation (Swagger UI)
   http://localhost:8000/docs
   
   # Alternative Docs (ReDoc)
   http://localhost:8000/redoc
   

9. TEST THE APPLICATION
   ======================
   
   # Run all tests
   pytest tests/ -v
   
   # Run specific test file
   pytest tests/test_phase9_complete.py -v
   
   # Run with coverage
   pytest tests/ --cov=backend --cov-report=html
   

10. VERIFY SETUP
    =============
    
    # Test database connection
    python -c "from backend.database_models import engine; print('✅ DB OK')"
    
    # Test Redis connection
    python -c "from backend.caching_service import redis_client; print('✅ Redis:', redis_client.is_connected())"
    
    # Test Elasticsearch
    python -c "from backend.search_service import SearchService; s = SearchService(); print('✅ ES OK' if s.es else '⚠️ ES N/A')"
    
    # Test Stripe (if configured)
    python -c "import stripe; print('✅ Stripe OK' if stripe.api_key else '⚠️ Stripe not configured')"
"""


# ============================================================================
# DOCKER DEPLOYMENT
# ============================================================================

"""
1. BUILD DOCKER IMAGE
   ====================
   
   Create Dockerfile:
   -----------------
   FROM python:3.11-slim
   
   WORKDIR /app
   
   # Install system dependencies
   RUN apt-get update && apt-get install -y \
       postgresql-client \
       && rm -rf /var/lib/apt/lists/*
   
   # Copy requirements
   COPY requirements-phase9.txt .
   
   # Install Python dependencies
   RUN pip install --no-cache-dir -r requirements-phase9.txt
   
   # Copy application
   COPY . .
   
   # Create non-root user
   RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
   USER appuser
   
   # Health check
   HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
       CMD python -c "import requests; requests.get('http://localhost:8000/health')"
   
   # Run application
   CMD ["uvicorn", "backend.server:app", "--host", "0.0.0.0", "--port", "8000"]


2. BUILD IMAGE
   ============
   
   docker build -t netflix-clone:latest .


3. RUN CONTAINER
   ==============
   
   docker run -d \
     --name netflix-app \
     -p 8000:8000 \
     --env-file .env \
     --link netflix-db:db \
     --link netflix-redis:redis \
     --link netflix-es:es \
     netflix-clone:latest


4. DOCKER COMPOSE (Recommended)
   =============================
   
   Create docker-compose.yml:
   -------------------------
   version: '3.8'
   
   services:
     # PostgreSQL Database
     db:
       image: postgres:15-alpine
       container_name: netflix-db
       environment:
         POSTGRES_DB: netflix_clone
         POSTGRES_USER: postgres
         POSTGRES_PASSWORD: password
       ports:
         - "5432:5432"
       volumes:
         - postgres_data:/var/lib/postgresql/data
       healthcheck:
         test: ["CMD-SHELL", "pg_isready -U postgres"]
         interval: 10s
         timeout: 5s
         retries: 5
     
     # Redis Cache
     redis:
       image: redis:7-alpine
       container_name: netflix-redis
       ports:
         - "6379:6379"
       healthcheck:
         test: ["CMD", "redis-cli", "ping"]
         interval: 10s
         timeout: 5s
         retries: 5
     
     # Elasticsearch
     elasticsearch:
       image: docker.elastic.co/elasticsearch/elasticsearch:8.10.0
       container_name: netflix-es
       environment:
         discovery.type: single-node
         xpack.security.enabled: "false"
       ports:
         - "9200:9200"
       healthcheck:
         test: ["CMD-SHELL", "curl -s http://localhost:9200 | grep -q 'version'"]
         interval: 10s
         timeout: 5s
         retries: 5
     
     # Netflix Clone API
     api:
       build: .
       container_name: netflix-api
       ports:
         - "8000:8000"
       environment:
         DATABASE_TYPE: postgresql
         DB_HOST: db
         DB_PORT: 5432
         DB_NAME: netflix_clone
         DB_USER: postgres
         DB_PASSWORD: password
         REDIS_HOST: redis
         REDIS_PORT: 6379
         ELASTICSEARCH_HOST: elasticsearch
         ELASTICSEARCH_PORT: 9200
         JWT_SECRET_KEY: your-secret-key-here
       depends_on:
         db:
           condition: service_healthy
         redis:
           condition: service_healthy
         elasticsearch:
           condition: service_healthy
       healthcheck:
         test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
         interval: 30s
         timeout: 10s
         retries: 3
     
   volumes:
     postgres_data:
   
   
   Run stack:
   docker-compose up -d
   
   View logs:
   docker-compose logs -f api
   
   Stop stack:
   docker-compose down


5. HEALTH CHECK
   =============
   
   curl http://localhost:8000/health
   
   Should return: {"status": "healthy", "timestamp": "2024-01-17T..."}
"""


# ============================================================================
# KUBERNETES DEPLOYMENT
# ============================================================================

"""
1. CREATE NAMESPACE
   =================
   
   kubectl create namespace netflix


2. CREATE CONFIGMAP
   =================
   
   kubectl create configmap netflix-config \
     --from-literal=DATABASE_TYPE=postgresql \
     --from-literal=DB_HOST=postgres-service \
     --from-literal=REDIS_HOST=redis-service \
     --from-literal=ELASTICSEARCH_HOST=elasticsearch-service \
     -n netflix


3. CREATE SECRETS
   ===============
   
   kubectl create secret generic netflix-secrets \
     --from-literal=JWT_SECRET_KEY=your-secret-key-here \
     --from-literal=DB_PASSWORD=secure_password \
     --from-literal=STRIPE_SECRET_KEY=sk_live_xxxxx \
     --from-literal=GROQ_API_KEY=gsk_xxxxx \
     -n netflix


4. CREATE DEPLOYMENT
   ==================
   
   Create deployment.yaml:
   ----------------------
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: netflix-api
     namespace: netflix
   spec:
     replicas: 3
     selector:
       matchLabels:
         app: netflix-api
     template:
       metadata:
         labels:
           app: netflix-api
       spec:
         containers:
         - name: api
           image: netflix-clone:latest
           ports:
           - containerPort: 8000
           env:
           - name: DATABASE_TYPE
             valueFrom:
               configMapKeyRef:
                 name: netflix-config
                 key: DATABASE_TYPE
           - name: JWT_SECRET_KEY
             valueFrom:
               secretKeyRef:
                 name: netflix-secrets
                 key: JWT_SECRET_KEY
           livenessProbe:
             httpGet:
               path: /health
               port: 8000
             initialDelaySeconds: 30
             periodSeconds: 10
           readinessProbe:
             httpGet:
               path: /health
               port: 8000
             initialDelaySeconds: 5
             periodSeconds: 5
           resources:
             requests:
               memory: "256Mi"
               cpu: "250m"
             limits:
               memory: "512Mi"
               cpu: "500m"


5. CREATE SERVICE
   ===============
   
   Create service.yaml:
   -------------------
   apiVersion: v1
   kind: Service
   metadata:
     name: netflix-service
     namespace: netflix
   spec:
     selector:
       app: netflix-api
     ports:
     - protocol: TCP
       port: 80
       targetPort: 8000
     type: LoadBalancer


6. APPLY MANIFESTS
   ================
   
   kubectl apply -f deployment.yaml
   kubectl apply -f service.yaml


7. CHECK DEPLOYMENT
   =================
   
   # Check pods
   kubectl get pods -n netflix
   
   # Check service
   kubectl get svc -n netflix
   
   # Check logs
   kubectl logs -f deployment/netflix-api -n netflix


8. SCALE DEPLOYMENT
   ==================================================
   
   kubectl scale deployment netflix-api --replicas=5 -n netflix
"""


# ============================================================================
# PRODUCTION DEPLOYMENT CHECKLIST
# ============================================================================

"""
PRE-DEPLOYMENT:
===============

❌ Security
  ☐ Change all default passwords
  ☐ Set strong JWT_SECRET_KEY (min 32 chars, random)
  ☐ Enable SSL/HTTPS certificates
  ☐ Configure CORS properly
  ☐ Set up firewall rules
  ☐ Enable database encryption at rest
  ☐ Configure backups
  ☐ Review security headers

❌ Configuration
  ☐ Set LOG_LEVEL=WARNING (not DEBUG)
  ☐ Configure Sentry DSN
  ☐ Set up monitoring alerts
  ☐ Configure database connection pooling
  ☐ Set Redis persistence
  ☐ Configure Elasticsearch sharding
  ☐ Set rate limits appropriately

❌ Database
  ☐ Run migrations
  ☐ Create indexes
  ☐ Set up read replicas
  ☐ Configure automated backups
  ☐ Test disaster recovery

❌ Infrastructure
  ☐ Set up load balancer
  ☐ Configure auto-scaling
  ☐ Set up CDN for static content
  ☐ Configure DNS
  ☐ Set up monitoring/metrics
  ☐ Configure log aggregation


DEPLOYMENT:
===========

❌ Code
  ☐ Run full test suite
  ☐ Code review completed
  ☐ Security scan (Snyk)
  ☐ Build Docker image
  ☐ Push to registry

❌ Database
  ☐ Initialize database
  ☐ Verify connectivity
  ☐ Run migrations
  ☐ Verify data integrity

❌ Services
  ☐ Start Redis
  ☐ Start Elasticsearch
  ☐ Verify Stripe integration
  ☐ Verify email service

❌ Application
  ☐ Deploy application
  ☐ Verify health checks pass
  ☐ Check logs for errors
  ☐ Verify API responses


POST-DEPLOYMENT:
================

❌ Verification
  ☐ Run smoke tests
  ☐ Test authentication flow
  ☐ Test payment flow (test mode)
  ☐ Test search functionality
  ☐ Verify analytics tracking
  ☐ Check rate limiting

❌ Monitoring
  ☐ Verify metrics are collected
  ☐ Check Sentry events
  ☐ Review logs
  ☐ Monitor resource usage
  ☐ Check error rates

❌ Performance
  ☐ Run load tests
  ☐ Verify response times
  ☐ Check cache hit rates
  ☐ Monitor database queries
  ☐ Check queue depths

❌ Security
  ☐ Verify SSL/HTTPS
  ☐ Test rate limiting under load
  ☐ Verify no sensitive logs
  ☐ Check security headers
  ☐ Verify access controls
"""


# ============================================================================
# TROUBLESHOOTING
# ============================================================================

"""
COMMON ISSUES:
==============

1. Database Connection Failed
   ========================
   
   Error: "connection refused"
   
   Solution:
   ☐ Check PostgreSQL is running: psql -U postgres -c "\\l"
   ☐ Verify DB_HOST, DB_PORT in .env
   ☐ Check database exists: createdb netflix_clone
   ☐ Verify user has permissions: psql -U postgres -d netflix_clone


2. Redis Connection Failed
   =======================
   
   Error: "REDIS_HOST: [Errno 111] Connection refused"
   
   Solution:
   ☐ Check Redis is running: redis-cli ping
   ☐ Verify REDIS_HOST, REDIS_PORT in .env
   ☐ Check firewall allows port 6379


3. Elasticsearch Connection Failed
   ===============================
   
   Error: "Connection refused" on port 9200
   
   Solution:
   ☐ Check Elasticsearch is running
   ☐ Verify ELASTICSEARCH_HOST, ELASTICSEARCH_PORT
   ☐ Check xpack.security.enabled=false for development


4. JWT Secret Too Short
   ====================
   
   Error: "JWT_SECRET_KEY too short"
   
   Solution:
   ☐ Generate secure key: python -c "import secrets; print(secrets.token_urlsafe(32))"
   ☐ Update JWT_SECRET_KEY in .env (min 32 chars)


5. Rate Limiting Not Working
   ==========================
   
   Error: "rate limiting not applied"
   
   Solution:
   ☐ Verify Redis is connected
   ☐ Check RATE_LIMIT_ENABLED=true in config
   ☐ Verify rate limit keys in Redis: redis-cli KEYS "ratelimit*"


6. Stripe Integration Failed
   ==========================
   
   Error: "Invalid API Key" or "Connection error"
   
   Solution:
   ☐ Verify STRIPE_SECRET_KEY is correct
   ☐ Use sk_test_ for testing, sk_live_ for production
   ☐ Check key has correct permissions
   ☐ Verify firewall allows outbound to api.stripe.com


7. Out of Memory
   =============
   
   Error: "MemoryError" or "out of memory"
   
   Solution:
   ☐ Reduce cache TTLs in CacheConfig
   ☐ Limit max workers in production
   ☐ Enable connection pooling
   ☐ Monitor memory with: docker stats
"""


# ============================================================================
# MONITORING & MAINTENANCE
# ============================================================================

"""
HEALTH CHECK ENDPOINT:
======================

curl -X GET http://localhost:8000/health

Expected Response:
{
  "status": "healthy",
  "timestamp": "2024-01-17T12:34:56Z",
  "database": "connected",
  "redis": "connected",
  "elasticsearch": "connected",
  "uptime_seconds": 3600
}


METRICS ENDPOINT:
=================

curl -X GET http://localhost:8000/metrics

Returns Prometheus metrics:
- api_requests_total
- api_request_duration_seconds
- database_queries_total
- cache_hit_rate
- error_rate


LOG AGGREGATION:
================

Logs are written to:
- Console (development)
- File: netflix_clone.log (10MB rotation, 10 backups)
- Sentry (if configured)

Format: JSON for easy parsing
Example: {"timestamp": "...", "level": "ERROR", "message": "...", "data": {...}}


DATABASE MAINTENANCE:
====================

# Backup
pg_dump netflix_clone > backup_2024-01-17.sql

# Restore
psql netflix_clone < backup_2024-01-17.sql

# Vacuum (maintenance)
psql -d netflix_clone -c "VACUUM ANALYZE;"

# Monitor slow queries
psql -d netflix_clone
SET log_min_duration_statement = 1000;


REDIS MAINTENANCE:
==================

# Clear cache
redis-cli FLUSHALL

# Check memory usage
redis-cli INFO memory

# Backup RDB
redis-cli BGSAVE

# Monitor keys
redis-cli MONITOR


ELASTICSEARCH MAINTENANCE:
==========================

# Check cluster health
curl http://localhost:9200/_cluster/health

# Get indices
curl http://localhost:9200/_cat/indices

# Delete old indices
curl -X DELETE http://localhost:9200/netflix_logs-2024-01-01
"""

print("""
╔══════════════════════════════════════════════════════════════╗
║   PHASE 9: NETFLIX CLONE - DEPLOYMENT & QUICK START         ║
║                                                              ║
║   📦 Local Development: < 10 minutes setup                  ║
║   🐳 Docker: docker-compose up                             ║
║   ☸️  Kubernetes: kubectl apply -f manifests/             ║
║                                                              ║
║   Ready to deploy to production! ✅                          ║
║                                                              ║
║   Documentation: See above for detailed instructions         ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
""")
