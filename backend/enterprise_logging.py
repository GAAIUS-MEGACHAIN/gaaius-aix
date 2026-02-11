"""
PHASE 9: Enterprise Logging & Error Handling
Structured logging, error tracking, monitoring
Sentry integration for production error tracking
"""

import logging
import logging.handlers
import json
import traceback
import os
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from functools import wraps
import sys

from fastapi import HTTPException, status, Request
from fastapi.responses import JSONResponse

try:
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False


# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

class LogConfig:
    """Logging configuration"""
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
    LOG_FILE = os.environ.get("LOG_FILE", "netflix_clone.log")
    LOG_MAX_BYTES = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT = 10
    SENTRY_DSN = os.environ.get("SENTRY_DSN")
    SENTRY_ENVIRONMENT = os.environ.get("SENTRY_ENVIRONMENT", "production")


# ============================================================================
# STRUCTURED LOGGER
# ============================================================================

class StructuredLogger:
    """Structured logging with JSON output"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(LogConfig.LOG_LEVEL)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(LogConfig.LOG_LEVEL)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        
        # File handler with rotation
        file_handler = logging.handlers.RotatingFileHandler(
            LogConfig.LOG_FILE,
            maxBytes=LogConfig.LOG_MAX_BYTES,
            backupCount=LogConfig.LOG_BACKUP_COUNT
        )
        file_handler.setLevel(LogConfig.LOG_LEVEL)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        
        if not self.logger.handlers:
            self.logger.addHandler(console_handler)
            self.logger.addHandler(file_handler)
    
    def _log(self, level: str, message: str, data: Optional[Dict] = None, exc_info=None):
        """Log with structured data"""
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": level,
            "message": message,
            "data": data or {}
        }
        
        if exc_info:
            log_entry["exception"] = str(exc_info)
            log_entry["traceback"] = traceback.format_exc()
        
        log_message = json.dumps(log_entry) if data or exc_info else message
        
        getattr(self.logger, level.lower())(log_message, exc_info=exc_info)
    
    def debug(self, message: str, data: Optional[Dict] = None):
        self._log("DEBUG", message, data)
    
    def info(self, message: str, data: Optional[Dict] = None):
        self._log("INFO", message, data)
    
    def warning(self, message: str, data: Optional[Dict] = None):
        self._log("WARNING", message, data)
    
    def error(self, message: str, data: Optional[Dict] = None, exc_info=None):
        self._log("ERROR", message, data, exc_info)
    
    def critical(self, message: str, data: Optional[Dict] = None, exc_info=None):
        self._log("CRITICAL", message, data, exc_info)


# ============================================================================
# SENTRY INITIALIZATION
# ============================================================================

def init_sentry():
    """Initialize Sentry for error tracking"""
    if SENTRY_AVAILABLE and LogConfig.SENTRY_DSN:
        sentry_sdk.init(
            dsn=LogConfig.SENTRY_DSN,
            integrations=[FastApiIntegration()],
            environment=LogConfig.SENTRY_ENVIRONMENT,
            traces_sample_rate=0.1,
            profiles_sample_rate=0.1,
            attach_stacktrace=True,
            include_local_variables=True,
            max_breadcrumbs=50
        )
        logger = StructuredLogger(__name__)
        logger.info("✅ Sentry initialized for error tracking")
    else:
        print("⚠️ Sentry not available or not configured")


# ============================================================================
# CUSTOM EXCEPTIONS
# ============================================================================

class APIException(HTTPException):
    """Base API exception"""
    
    def __init__(
        self,
        status_code: int,
        error_code: str,
        message: str,
        details: Optional[Dict] = None
    ):
        self.status_code = status_code
        self.error_code = error_code
        self.message = message
        self.details = details or {}
    
    def to_dict(self) -> Dict:
        return {
            "error": {
                "code": self.error_code,
                "message": self.message,
                "details": self.details,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        }


class ValidationException(APIException):
    """Validation error"""
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "VALIDATION_ERROR",
            message,
            details
        )


class AuthenticationException(APIException):
    """Authentication error"""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            status.HTTP_401_UNAUTHORIZED,
            "AUTHENTICATION_ERROR",
            message
        )


class AuthorizationException(APIException):
    """Authorization error"""
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(
            status.HTTP_403_FORBIDDEN,
            "AUTHORIZATION_ERROR",
            message
        )


class ResourceNotFoundException(APIException):
    """Resource not found"""
    def __init__(self, resource: str, resource_id: str):
        super().__init__(
            status.HTTP_404_NOT_FOUND,
            "RESOURCE_NOT_FOUND",
            f"{resource} not found",
            {"resource": resource, "id": resource_id}
        )


class ConflictException(APIException):
    """Conflict error"""
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(
            status.HTTP_409_CONFLICT,
            "CONFLICT_ERROR",
            message,
            details
        )


class RateLimitException(APIException):
    """Rate limit exceeded"""
    def __init__(self, retry_after: int = 60):
        super().__init__(
            status.HTTP_429_TOO_MANY_REQUESTS,
            "RATE_LIMIT_EXCEEDED",
            "Too many requests",
            {"retry_after": retry_after}
        )


class ServiceException(APIException):
    """Internal service error"""
    def __init__(self, message: str = "Internal server error", details: Optional[Dict] = None):
        super().__init__(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "INTERNAL_SERVER_ERROR",
            message,
            details
        )


# ============================================================================
# ERROR HANDLER MIDDLEWARE
# ============================================================================

async def exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle exceptions globally"""
    logger = StructuredLogger(__name__)
    
    # Handle custom exceptions
    if isinstance(exc, APIException):
        logger.warning(
            f"API Exception: {exc.error_code}",
            {
                "error_code": exc.error_code,
                "message": exc.message,
                "status_code": exc.status_code,
                "path": str(request.url),
                "method": request.method
            }
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.to_dict()
        )
    
    # Handle HTTP exceptions
    elif isinstance(exc, HTTPException):
        logger.warning(
            f"HTTP Exception: {exc.status_code}",
            {
                "status_code": exc.status_code,
                "detail": exc.detail,
                "path": str(request.url)
            }
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": "HTTP_ERROR",
                    "message": exc.detail,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            }
        )
    
    # Handle unexpected exceptions
    else:
        logger.error(
            "Unexpected exception",
            {
                "exception_type": type(exc).__name__,
                "message": str(exc),
                "path": str(request.url),
                "method": request.method
            },
            exc_info=exc
        )
        
        # Report to Sentry if available
        if SENTRY_AVAILABLE:
            sentry_sdk.capture_exception(exc)
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected error occurred",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            }
        )


# ============================================================================
# DECORATORS
# ============================================================================

def log_execution(func):
    """Log function execution"""
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        logger = StructuredLogger(func.__module__)
        start_time = datetime.now(timezone.utc)
        
        try:
            logger.info(f"Executing {func.__name__}", {"args": str(args)[:100]})
            result = await func(*args, **kwargs)
            
            duration = (datetime.now(timezone.utc) - start_time).total_seconds()
            logger.info(
                f"Completed {func.__name__}",
                {"duration_seconds": duration, "status": "success"}
            )
            return result
        except Exception as e:
            duration = (datetime.now(timezone.utc) - start_time).total_seconds()
            logger.error(
                f"Failed {func.__name__}",
                {"duration_seconds": duration, "error": str(e)},
                exc_info=e
            )
            raise
    
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        logger = StructuredLogger(func.__module__)
        start_time = datetime.now(timezone.utc)
        
        try:
            logger.info(f"Executing {func.__name__}")
            result = func(*args, **kwargs)
            
            duration = (datetime.now(timezone.utc) - start_time).total_seconds()
            logger.info(
                f"Completed {func.__name__}",
                {"duration_seconds": duration, "status": "success"}
            )
            return result
        except Exception as e:
            duration = (datetime.now(timezone.utc) - start_time).total_seconds()
            logger.error(
                f"Failed {func.__name__}",
                {"duration_seconds": duration, "error": str(e)},
                exc_info=e
            )
            raise
    
    return async_wrapper if hasattr(func, '__await__') else sync_wrapper


# ============================================================================
# REQUEST/RESPONSE LOGGING
# ============================================================================

async def log_request_middleware(request: Request, call_next):
    """Log HTTP requests"""
    logger = StructuredLogger(__name__)
    start_time = datetime.now(timezone.utc)
    
    # Get request body if available
    body = None
    if request.method in ["POST", "PUT", "PATCH"]:
        try:
            body = await request.body()
            await request._receive()  # Reset body stream
        except:
            pass
    
    response = await call_next(request)
    
    # Calculate response time
    duration = (datetime.now(timezone.utc) - start_time).total_seconds()
    
    # Log
    log_data = {
        "method": request.method,
        "path": request.url.path,
        "status_code": response.status_code,
        "duration_seconds": duration,
        "client_ip": request.client.host if request.client else None,
        "user_agent": request.headers.get("user-agent")
    }
    
    if response.status_code >= 400:
        logger.warning(f"HTTP {response.status_code}", log_data)
    else:
        logger.debug(f"HTTP {response.status_code}", log_data)
    
    # Add headers
    response.headers["X-Process-Time"] = str(duration)
    
    return response


# ============================================================================
# MONITORING & METRICS
# ============================================================================

class MetricsCollector:
    """Collect application metrics"""
    
    def __init__(self):
        self.metrics = {
            "requests_total": 0,
            "requests_errors": 0,
            "requests_4xx": 0,
            "requests_5xx": 0,
            "average_response_time": 0.0,
            "database_queries": 0,
            "cache_hits": 0,
            "cache_misses": 0
        }
    
    def record_request(self, status_code: int, duration: float):
        """Record HTTP request"""
        self.metrics["requests_total"] += 1
        
        if status_code >= 500:
            self.metrics["requests_5xx"] += 1
            self.metrics["requests_errors"] += 1
        elif status_code >= 400:
            self.metrics["requests_4xx"] += 1
        
        # Calculate rolling average
        total_time = self.metrics["average_response_time"] * (self.metrics["requests_total"] - 1)
        self.metrics["average_response_time"] = (total_time + duration) / self.metrics["requests_total"]
    
    def record_cache_hit(self):
        """Record cache hit"""
        self.metrics["cache_hits"] += 1
    
    def record_cache_miss(self):
        """Record cache miss"""
        self.metrics["cache_misses"] += 1
    
    def get_metrics(self) -> Dict:
        """Get current metrics"""
        cache_total = self.metrics["cache_hits"] + self.metrics["cache_misses"]
        cache_hit_rate = (
            self.metrics["cache_hits"] / cache_total * 100 if cache_total > 0 else 0
        )
        
        return {
            **self.metrics,
            "cache_hit_rate": f"{cache_hit_rate:.2f}%",
            "error_rate": f"{(self.metrics['requests_errors'] / max(1, self.metrics['requests_total']) * 100):.2f}%"
        }


# Global metrics collector
metrics = MetricsCollector()


# ============================================================================
# LOGGER INSTANCES
# ============================================================================

logger = StructuredLogger(__name__)
app_logger = StructuredLogger("netflix_clone")
auth_logger = StructuredLogger("netflix_clone.auth")
db_logger = StructuredLogger("netflix_clone.db")
api_logger = StructuredLogger("netflix_clone.api")
payment_logger = StructuredLogger("netflix_clone.payment")
search_logger = StructuredLogger("netflix_clone.search")


if __name__ == "__main__":
    # Test logging
    print("🧪 Testing Enterprise Logging\n")
    
    test_logger = StructuredLogger("test")
    
    test_logger.debug("Debug message", {"level": "debug"})
    test_logger.info("Info message", {"level": "info"})
    test_logger.warning("Warning message", {"level": "warning"})
    
    try:
        1 / 0
    except Exception as e:
        test_logger.error("Error message", {"level": "error"}, exc_info=e)
    
    # Test metrics
    print("\n📊 Testing Metrics Collector\n")
    collector = MetricsCollector()
    collector.record_request(200, 0.150)
    collector.record_request(200, 0.120)
    collector.record_request(404, 0.080)
    collector.record_request(500, 0.500)
    collector.record_cache_hit()
    collector.record_cache_hit()
    collector.record_cache_miss()
    
    print(json.dumps(collector.get_metrics(), indent=2))
    
    print("\n✅ Enterprise logging configured successfully")
