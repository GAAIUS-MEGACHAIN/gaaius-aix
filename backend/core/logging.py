"""
GAAIUS Structured Logging & Observability
JSON logging, metrics tracking, audit trails, performance monitoring
"""

import logging
import json
import time
from datetime import datetime
from typing import Optional, Dict, Any
from functools import wraps
from enum import Enum
import uuid

logger = logging.getLogger(__name__)


class LogEventType(str, Enum):
    """Types of log events"""
    # User actions
    USER_REGISTERED = "user_registered"
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    FACIAL_ENROLLMENT = "facial_enrollment"
    FACIAL_VERIFICATION = "facial_verification"
    
    # Course actions
    COURSE_CREATED = "course_created"
    COURSE_PUBLISHED = "course_published"
    COURSE_ENROLLED = "course_enrolled"
    COURSE_COMPLETED = "course_completed"
    
    # Exam actions
    EXAM_STARTED = "exam_started"
    EXAM_SUBMITTED = "exam_submitted"
    EXAM_GRADED = "exam_graded"
    EXAM_FAILED = "exam_failed"
    
    # Proctoring actions
    PROCTORING_VIOLATION = "proctoring_violation"
    PROCTORING_SESSION_ENDED = "proctoring_session_ended"
    
    # Certificate actions
    CERTIFICATE_ISSUED = "certificate_issued"
    CERTIFICATE_VERIFIED = "certificate_verified"
    
    # System actions
    API_REQUEST = "api_request"
    API_ERROR = "api_error"
    DATABASE_ERROR = "database_error"
    EXTERNAL_SERVICE_ERROR = "external_service_error"
    HEALTH_CHECK = "health_check"
    
    # Security actions
    SECURITY_VIOLATION = "security_violation"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    
    # Admin actions
    ADMIN_ACTION = "admin_action"
    SYSTEM_ALERT = "system_alert"


class StructuredLogger:
    """Structured logging with context and tracing"""
    
    @staticmethod
    def log_event(
        event_type: LogEventType,
        user_id: Optional[str] = None,
        resource_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        severity: str = "INFO",
        trace_id: Optional[str] = None
    ) -> str:
        """
        Log a structured event
        
        Args:
            event_type: Type of event
            user_id: Associated user ID
            resource_id: Associated resource ID
            resource_type: Type of resource
            details: Additional details
            severity: Log severity level
            trace_id: Trace ID for correlation
            
        Returns:
            Trace ID for event tracking
        """
        trace_id = trace_id or str(uuid.uuid4())
        
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type.value,
            "severity": severity,
            "trace_id": trace_id,
            "user_id": user_id,
            "resource_id": resource_id,
            "resource_type": resource_type,
            "details": details or {}
        }
        
        # Use appropriate log level
        log_level = getattr(logging, severity, logging.INFO)
        logger.log(log_level, json.dumps(log_entry))
        
        return trace_id
    
    @staticmethod
    def log_api_request(
        method: str,
        path: str,
        status_code: int,
        duration_ms: float,
        user_id: Optional[str] = None,
        trace_id: Optional[str] = None,
        error: Optional[str] = None
    ) -> str:
        """
        Log API request
        
        Args:
            method: HTTP method
            path: Request path
            status_code: Response status code
            duration_ms: Request duration in milliseconds
            user_id: User ID
            trace_id: Trace ID
            error: Error message if any
            
        Returns:
            Trace ID
        """
        trace_id = trace_id or str(uuid.uuid4())
        
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": LogEventType.API_REQUEST.value,
            "trace_id": trace_id,
            "user_id": user_id,
            "method": method,
            "path": path,
            "status_code": status_code,
            "duration_ms": round(duration_ms, 2),
            "error": error
        }
        
        # Log warnings for slow requests (>1000ms)
        severity = "WARNING" if duration_ms > 1000 else "INFO"
        log_level = getattr(logging, severity, logging.INFO)
        logger.log(log_level, json.dumps(log_entry))
        
        return trace_id
    
    @staticmethod
    def log_database_operation(
        operation: str,
        collection: str,
        duration_ms: float,
        result_count: int = 0,
        error: Optional[str] = None,
        trace_id: Optional[str] = None
    ) -> str:
        """
        Log database operation
        
        Args:
            operation: Operation type (insert, update, query, delete)
            collection: Collection name
            duration_ms: Operation duration
            result_count: Number of results
            error: Error message if any
            trace_id: Trace ID
            
        Returns:
            Trace ID
        """
        trace_id = trace_id or str(uuid.uuid4())
        
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "database_operation",
            "trace_id": trace_id,
            "operation": operation,
            "collection": collection,
            "duration_ms": round(duration_ms, 2),
            "result_count": result_count,
            "error": error
        }
        
        severity = "ERROR" if error else ("WARNING" if duration_ms > 500 else "DEBUG")
        log_level = getattr(logging, severity, logging.INFO)
        logger.log(log_level, json.dumps(log_entry))
        
        return trace_id
    
    @staticmethod
    def log_external_service_call(
        service_name: str,
        endpoint: str,
        duration_ms: float,
        status_code: Optional[int] = None,
        error: Optional[str] = None,
        trace_id: Optional[str] = None
    ) -> str:
        """
        Log external service call
        
        Args:
            service_name: Service name (Groq, OpenStax, etc.)
            endpoint: API endpoint called
            duration_ms: Call duration
            status_code: HTTP status code
            error: Error message if any
            trace_id: Trace ID
            
        Returns:
            Trace ID
        """
        trace_id = trace_id or str(uuid.uuid4())
        
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": LogEventType.EXTERNAL_SERVICE_ERROR.value if error else "external_service_call",
            "trace_id": trace_id,
            "service": service_name,
            "endpoint": endpoint,
            "duration_ms": round(duration_ms, 2),
            "status_code": status_code,
            "error": error
        }
        
        severity = "ERROR" if error else ("WARNING" if duration_ms > 5000 else "INFO")
        log_level = getattr(logging, severity, logging.INFO)
        logger.log(log_level, json.dumps(log_entry))
        
        return trace_id


def log_async_operation(operation_name: str):
    """Decorator for logging async operations"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            trace_id = str(uuid.uuid4())
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                
                StructuredLogger.log_event(
                    event_type=LogEventType.API_REQUEST,
                    details={
                        "operation": operation_name,
                        "status": "success",
                        "duration_ms": round(duration_ms, 2)
                    },
                    trace_id=trace_id
                )
                
                return result
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                
                StructuredLogger.log_event(
                    event_type=LogEventType.API_ERROR,
                    details={
                        "operation": operation_name,
                        "error": str(e),
                        "duration_ms": round(duration_ms, 2)
                    },
                    severity="ERROR",
                    trace_id=trace_id
                )
                raise
        
        return wrapper
    return decorator


def log_sync_operation(operation_name: str):
    """Decorator for logging sync operations"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            trace_id = str(uuid.uuid4())
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                
                StructuredLogger.log_event(
                    event_type=LogEventType.API_REQUEST,
                    details={
                        "operation": operation_name,
                        "status": "success",
                        "duration_ms": round(duration_ms, 2)
                    },
                    trace_id=trace_id
                )
                
                return result
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                
                StructuredLogger.log_event(
                    event_type=LogEventType.API_ERROR,
                    details={
                        "operation": operation_name,
                        "error": str(e),
                        "duration_ms": round(duration_ms, 2)
                    },
                    severity="ERROR",
                    trace_id=trace_id
                )
                raise
        
        return wrapper
    return decorator


class MetricsCollector:
    """Collect and track system metrics"""
    
    _metrics: Dict[str, Dict[str, Any]] = {
        "api_requests": {"total": 0, "errors": 0, "avg_duration_ms": 0},
        "database_operations": {"total": 0, "errors": 0, "avg_duration_ms": 0},
        "external_calls": {"total": 0, "errors": 0, "avg_duration_ms": 0},
        "exams_started": {"total": 0},
        "exams_completed": {"total": 0},
        "certificates_issued": {"total": 0},
        "users_registered": {"total": 0},
        "facial_enrollments": {"total": 0, "successful": 0}
    }
    
    @staticmethod
    def record_metric(metric_name: str, value: int = 1):
        """Record a metric"""
        if metric_name not in MetricsCollector._metrics:
            MetricsCollector._metrics[metric_name] = {"total": 0}
        
        if "total" in MetricsCollector._metrics[metric_name]:
            MetricsCollector._metrics[metric_name]["total"] += value
    
    @staticmethod
    def get_metrics() -> Dict[str, Dict[str, Any]]:
        """Get all collected metrics"""
        return MetricsCollector._metrics.copy()
    
    @staticmethod
    def reset_metrics():
        """Reset all metrics"""
        for metric in MetricsCollector._metrics:
            MetricsCollector._metrics[metric] = {"total": 0}
