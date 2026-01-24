"""
Phase 3 Integration Module
Integrates all Phase 3 components into the FastAPI server
Includes: Security, Caching, DB Optimization, Health Checks, Rate Limiting, Monitoring
"""

import os
import logging
from typing import Optional, Callable
from functools import wraps

# Phase 3 Components
try:
    from .security import (
        SecurityManager,
        sanitize_string,
        validate_email,
        validate_username,
        validate_video_id,
        get_security_headers,
        RateLimitTracker,
        ValidationError,
        AuthenticationError,
        AuthorizationError,
    )
    from .caching import (
        CacheManager,
        VideoCacheService,
        UserCacheService,
        ChatCacheService,
        cache_route,
        cache_db_query,
    )
    from .db_optimization import (
        DatabasePool,
        IndexManager,
        QueryOptimizer,
        QueryBuilder,
        DatabaseOptimizer,
    )
    from .health_checks import (
        HealthCheckService,
        get_health_status,
        get_readiness_status,
        get_metrics,
    )
    from .rate_limiting import (
        RateLimiter,
        RateLimitPolicy,
        RATE_LIMIT_POLICIES,
    )
    from .monitoring import (
        ProductionLogger,
        MetricsCollector,
    )
except ImportError as e:
    try:
        # Fallback to top-level imports
        from security import (
            SecurityManager,
            sanitize_string,
            validate_email,
            validate_username,
            validate_video_id,
            get_security_headers,
            RateLimitTracker,
            ValidationError,
            AuthenticationError,
            AuthorizationError,
        )
        from caching import (
            CacheManager,
            VideoCacheService,
            UserCacheService,
            ChatCacheService,
            cache_route,
            cache_db_query,
        )
        from db_optimization import (
            DatabasePool,
            IndexManager,
            QueryOptimizer,
            QueryBuilder,
            DatabaseOptimizer,
        )
        from health_checks import (
            HealthCheckService,
            get_health_status,
            get_readiness_status,
            get_metrics,
        )
        from rate_limiting import (
            RateLimiter,
            RateLimitPolicy,
            RATE_LIMIT_POLICIES,
        )
        from monitoring import (
            ProductionLogger,
            MetricsCollector,
        )
    except ImportError:
        logging.warning(f"Phase 3 modules not fully loaded: {e}")
        # Graceful degradation - Phase 3 features disabled but server still runs
        SecurityManager = None
        CacheManager = None
        DatabasePool = None
        HealthCheckService = None
        RateLimiter = None
        ProductionLogger = None


logger = logging.getLogger(__name__)


class Phase3Integration:
    """
    Manages Phase 3 integration with the FastAPI server
    Handles initialization and lifecycle of all Phase 3 components
    """

    def __init__(self, mongo_url: str, db_name: str, redis_url: str = "redis://localhost:6379"):
        """Initialize Phase 3 components"""
        self.mongo_url = mongo_url
        self.db_name = db_name
        self.redis_url = redis_url
        
        # Phase 3 Services
        self.cache_manager: Optional[CacheManager] = None
        self.db_pool: Optional[DatabasePool] = None
        self.index_manager: Optional[IndexManager] = None
        self.query_optimizer: Optional[QueryOptimizer] = None
        self.rate_limiter: Optional[RateLimiter] = None
        self.health_service: Optional[HealthCheckService] = None
        self.production_logger: Optional[ProductionLogger] = None
        self.metrics_collector: Optional[MetricsCollector] = None
        
        # Cache services
        self.video_cache: Optional[VideoCacheService] = None
        self.user_cache: Optional[UserCacheService] = None
        self.chat_cache: Optional[ChatCacheService] = None

    async def initialize(self, client, db):
        """Initialize all Phase 3 components"""
        try:
            logger.info("Initializing Phase 3 components...")

            # Initialize Cache Manager
            if CacheManager:
                self.cache_manager = CacheManager(self.redis_url)
                logger.info("✓ Cache Manager initialized")

            # Initialize Database Pool
            if DatabasePool:
                self.db_pool = DatabasePool(
                    mongo_url=self.mongo_url,
                    db_name=self.db_name,
                    min_pool_size=10,
                    max_pool_size=50
                )
                logger.info("✓ Database Pool initialized")

            # Initialize Index Manager
            if IndexManager:
                self.index_manager = IndexManager(db)
                await self.index_manager.create_indexes()
                logger.info("✓ Index Manager initialized")

            # Initialize Query Optimizer
            if QueryOptimizer:
                self.query_optimizer = QueryOptimizer()
                logger.info("✓ Query Optimizer initialized")

            # Initialize Rate Limiter
            if RateLimiter:
                self.rate_limiter = RateLimiter()
                logger.info("✓ Rate Limiter initialized")

            # Initialize Health Check Service
            if HealthCheckService:
                self.health_service = HealthCheckService(
                    mongo_client=client,
                    redis_url=self.redis_url
                )
                logger.info("✓ Health Check Service initialized")

            # Initialize Production Logger
            if ProductionLogger:
                self.production_logger = ProductionLogger()
                logger.info("✓ Production Logger initialized")

            # Initialize Metrics Collector
            if MetricsCollector:
                self.metrics_collector = MetricsCollector()
                logger.info("✓ Metrics Collector initialized")

            # Initialize Cache Services
            if self.cache_manager:
                self.video_cache = VideoCacheService(self.cache_manager)
                self.user_cache = UserCacheService(self.cache_manager)
                self.chat_cache = ChatCacheService(self.cache_manager)
                logger.info("✓ Cache Services initialized")

            logger.info("✅ Phase 3 integration complete!")
            return True

        except Exception as e:
            logger.error(f"❌ Phase 3 initialization failed: {e}")
            return False

    async def shutdown(self):
        """Shutdown Phase 3 components gracefully"""
        try:
            logger.info("Shutting down Phase 3 components...")
            
            if self.cache_manager:
                await self.cache_manager.close()
                logger.info("✓ Cache Manager shutdown")
            
            if self.db_pool:
                await self.db_pool.close()
                logger.info("✓ Database Pool shutdown")
            
            logger.info("✅ Phase 3 shutdown complete!")
        except Exception as e:
            logger.error(f"Error during Phase 3 shutdown: {e}")


def setup_phase3_middleware(app, phase3: Phase3Integration):
    """Setup Phase 3 middleware on FastAPI app"""
    from fastapi import Request
    from time import time

    @app.middleware("http")
    async def phase3_middleware(request: Request, call_next):
        """Middleware to add Phase 3 monitoring and security"""
        start_time = time()

        # Security headers
        if phase3.production_logger:
            # Log request
            await phase3.production_logger.log_request(
                method=request.method,
                path=request.url.path,
                client=request.client.host if request.client else "unknown"
            )

        # Rate limiting check
        if phase3.rate_limiter:
            endpoint = request.url.path
            client_ip = request.client.host if request.client else "127.0.0.1"
            
            is_allowed = await phase3.rate_limiter.check_rate_limit(
                endpoint=endpoint,
                client_ip=client_ip
            )
            
            if not is_allowed:
                return JSONResponse(
                    status_code=429,
                    content={"error": "Rate limit exceeded"}
                )

        # Process request
        response = await call_next(request)

        # Track metrics
        if phase3.metrics_collector:
            process_time = time() - start_time
            await phase3.metrics_collector.track_request(
                endpoint=request.url.path,
                method=request.method,
                status_code=response.status_code,
                duration=process_time
            )

        # Add security headers
        if SecurityManager:
            headers = get_security_headers()
            for header, value in headers.items():
                response.headers[header] = value

        return response

    logger.info("✓ Phase 3 middleware setup complete")


def setup_phase3_routes(app, phase3: Phase3Integration):
    """Setup Phase 3 health and monitoring routes"""
    from fastapi import APIRouter
    from fastapi.responses import JSONResponse

    router = APIRouter(prefix="/api", tags=["phase3"])

    @router.get("/health")
    async def health_check():
        """Health check endpoint"""
        if phase3.health_service:
            status = await phase3.health_service.get_health_status()
            return JSONResponse(
                status_code=200 if status["healthy"] else 503,
                content=status
            )
        return {"status": "ok"}

    @router.get("/ready")
    async def readiness_check():
        """Readiness probe for load balancers"""
        if phase3.health_service:
            status = await phase3.health_service.get_readiness_status()
            return JSONResponse(
                status_code=200 if status["ready"] else 503,
                content=status
            )
        return {"ready": True}

    @router.get("/metrics")
    async def metrics_endpoint():
        """Metrics endpoint for monitoring"""
        if phase3.metrics_collector:
            metrics = await phase3.metrics_collector.get_metrics()
            return metrics
        return {"metrics": "unavailable"}

    @router.get("/version")
    async def version_endpoint():
        """Version information endpoint"""
        return {
            "version": "3.0.0",
            "phase": "3",
            "status": "production",
            "components": {
                "security": "enabled" if phase3.production_logger else "disabled",
                "caching": "enabled" if phase3.cache_manager else "disabled",
                "database_optimization": "enabled" if phase3.db_pool else "disabled",
                "rate_limiting": "enabled" if phase3.rate_limiter else "disabled",
                "monitoring": "enabled" if phase3.metrics_collector else "disabled",
            }
        }

    app.include_router(router)
    logger.info("✓ Phase 3 routes setup complete")


# Export for use in server.py
__all__ = [
    'Phase3Integration',
    'setup_phase3_middleware',
    'setup_phase3_routes',
    'SecurityManager',
    'CacheManager',
    'DatabasePool',
    'RateLimiter',
    'ProductionLogger',
    'MetricsCollector',
]
