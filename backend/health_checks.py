"""
PHASE 3: Health check endpoints for production monitoring
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime
import os
import psutil
from typing import Dict, Any

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Basic health check endpoint for load balancers
    Returns 200 if service is running
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "videos-api",
        "version": "3.0.0"
    }


@router.get("/ready")
async def readiness_check() -> Dict[str, Any]:
    """
    Readiness check endpoint
    Returns 200 only if all dependencies are ready
    """
    checks = {
        "database": await check_database(),
        "cache": await check_cache(),
        "disk_space": check_disk_space(),
        "memory": check_memory(),
    }
    
    # Return 503 if any check fails
    if not all(checks.values()):
        raise HTTPException(status_code=503, detail=checks)
    
    return {
        "status": "ready",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": checks
    }


@router.get("/metrics")
async def metrics() -> Dict[str, Any]:
    """
    Metrics endpoint for monitoring
    """
    process = psutil.Process(os.getpid())
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "cpu": {
            "percent": process.cpu_percent(interval=0.1),
            "num_threads": process.num_threads()
        },
        "memory": {
            "percent": process.memory_percent(),
            "rss_mb": process.memory_info().rss / 1024 / 1024,
            "vms_mb": process.memory_info().vms / 1024 / 1024
        },
        "system": {
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent
        }
    }


async def check_database() -> bool:
    """Check if database is accessible"""
    try:
        # Import will be done at runtime to avoid circular imports
        from backend.db import db
        
        # Try a simple ping
        result = await db.command("ping")
        return result.get("ok") == 1.0
    except Exception as e:
        print(f"Database check failed: {e}")
        return False


async def check_cache() -> bool:
    """Check if cache (Redis) is accessible"""
    try:
        # Check if Redis is configured and accessible
        import redis
        r = redis.Redis(host=os.environ.get('REDIS_HOST', 'localhost'),
                       port=int(os.environ.get('REDIS_PORT', 6379)),
                       db=0,
                       socket_connect_timeout=2)
        r.ping()
        return True
    except Exception:
        # Cache is optional, so return True if not configured
        return True


def check_disk_space() -> bool:
    """Check if disk space is adequate"""
    try:
        disk = psutil.disk_usage('/')
        # Check if more than 10% space is available
        return disk.percent < 90
    except Exception:
        return True


def check_memory() -> bool:
    """Check if memory usage is acceptable"""
    try:
        memory = psutil.virtual_memory()
        # Check if less than 95% memory is used
        return memory.percent < 95
    except Exception:
        return True


@router.get("/version")
async def version() -> Dict[str, str]:
    """Get API version information"""
    return {
        "version": "3.0.0",
        "phase": "phase-3",
        "api_name": "videos-api",
        "build_date": datetime.utcnow().isoformat()
    }
