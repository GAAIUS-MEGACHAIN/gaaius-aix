"""
PHASE 3: Production monitoring and structured logging
Tracks all API activity for auditing and debugging
"""

import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional
from pythonjsonlogger import jsonlogger
import os
from pathlib import Path


class ProductionLogger:
    """Structured logging for production environment"""
    
    def __init__(self, app_name: str = "videos-api"):
        self.app_name = app_name
        self.setup_loggers()
    
    def setup_loggers(self):
        """Setup JSON loggers for different log levels"""
        
        # Create logs directory if it doesn't exist
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Configure root logger
        self.logger = logging.getLogger(self.app_name)
        self.logger.setLevel(logging.DEBUG)
        
        # Remove any existing handlers
        self.logger.handlers = []
        
        # JSON formatter
        json_formatter = jsonlogger.JsonFormatter(
            '%(timestamp)s %(level)s %(name)s %(message)s'
        )
        
        # File handler for all logs
        all_handler = logging.FileHandler(log_dir / "app.log")
        all_handler.setLevel(logging.DEBUG)
        all_handler.setFormatter(json_formatter)
        self.logger.addHandler(all_handler)
        
        # File handler for errors only
        error_handler = logging.FileHandler(log_dir / "errors.log")
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(json_formatter)
        self.logger.addHandler(error_handler)
        
        # Console handler for development
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
    
    def log_request(self, method: str, path: str, client_ip: str, 
                   user_id: Optional[str] = None):
        """Log incoming request"""
        self.logger.info(
            f"Request received",
            extra={
                "timestamp": datetime.utcnow().isoformat(),
                "type": "request",
                "method": method,
                "path": path,
                "client_ip": client_ip,
                "user_id": user_id
            }
        )
    
    def log_response(self, method: str, path: str, status_code: int, 
                    duration_ms: float, client_ip: str,
                    user_id: Optional[str] = None):
        """Log outgoing response"""
        self.logger.info(
            f"Response sent",
            extra={
                "timestamp": datetime.utcnow().isoformat(),
                "type": "response",
                "method": method,
                "path": path,
                "status_code": status_code,
                "duration_ms": duration_ms,
                "client_ip": client_ip,
                "user_id": user_id
            }
        )
    
    def log_error(self, error_type: str, error_message: str, 
                 path: str, user_id: Optional[str] = None,
                 traceback: Optional[str] = None):
        """Log application error"""
        self.logger.error(
            f"Error occurred",
            extra={
                "timestamp": datetime.utcnow().isoformat(),
                "type": "error",
                "error_type": error_type,
                "error_message": error_message,
                "path": path,
                "user_id": user_id,
                "traceback": traceback
            }
        )
    
    def log_security_event(self, event_type: str, details: Dict[str, Any],
                          user_id: Optional[str] = None, 
                          client_ip: Optional[str] = None):
        """Log security-related events"""
        self.logger.warning(
            f"Security event",
            extra={
                "timestamp": datetime.utcnow().isoformat(),
                "type": "security",
                "event_type": event_type,
                "details": json.dumps(details),
                "user_id": user_id,
                "client_ip": client_ip
            }
        )
    
    def log_database_query(self, operation: str, collection: str,
                          duration_ms: float, user_id: Optional[str] = None):
        """Log database operations"""
        self.logger.debug(
            f"Database query executed",
            extra={
                "timestamp": datetime.utcnow().isoformat(),
                "type": "database",
                "operation": operation,
                "collection": collection,
                "duration_ms": duration_ms,
                "user_id": user_id
            }
        )
    
    def log_cache_hit(self, key: str, user_id: Optional[str] = None):
        """Log cache hit"""
        self.logger.debug(
            f"Cache hit",
            extra={
                "timestamp": datetime.utcnow().isoformat(),
                "type": "cache",
                "event": "hit",
                "key": key,
                "user_id": user_id
            }
        )
    
    def log_cache_miss(self, key: str, user_id: Optional[str] = None):
        """Log cache miss"""
        self.logger.debug(
            f"Cache miss",
            extra={
                "timestamp": datetime.utcnow().isoformat(),
                "type": "cache",
                "event": "miss",
                "key": key,
                "user_id": user_id
            }
        )


class MetricsCollector:
    """Collect and track metrics"""
    
    def __init__(self):
        self.metrics: Dict[str, Any] = {
            "requests_total": 0,
            "requests_by_method": {},
            "requests_by_path": {},
            "response_times": [],
            "errors_total": 0,
            "errors_by_type": {},
            "cache_hits": 0,
            "cache_misses": 0,
            "database_queries": 0
        }
    
    def record_request(self, method: str, path: str, status_code: int,
                      duration_ms: float):
        """Record request metrics"""
        self.metrics["requests_total"] += 1
        
        # By method
        self.metrics["requests_by_method"][method] = \
            self.metrics["requests_by_method"].get(method, 0) + 1
        
        # By path
        self.metrics["requests_by_path"][path] = \
            self.metrics["requests_by_path"].get(path, 0) + 1
        
        # Response times
        self.metrics["response_times"].append(duration_ms)
        if len(self.metrics["response_times"]) > 1000:  # Keep last 1000
            self.metrics["response_times"].pop(0)
        
        # Errors
        if status_code >= 400:
            self.metrics["errors_total"] += 1
            error_key = f"{status_code}"
            self.metrics["errors_by_type"][error_key] = \
                self.metrics["errors_by_type"].get(error_key, 0) + 1
    
    def record_cache_hit(self):
        """Record cache hit"""
        self.metrics["cache_hits"] += 1
    
    def record_cache_miss(self):
        """Record cache miss"""
        self.metrics["cache_misses"] += 1
    
    def record_database_query(self):
        """Record database query"""
        self.metrics["database_queries"] += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        avg_response_time = 0
        if self.metrics["response_times"]:
            avg_response_time = sum(self.metrics["response_times"]) / len(
                self.metrics["response_times"]
            )
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "requests": {
                "total": self.metrics["requests_total"],
                "by_method": self.metrics["requests_by_method"],
                "by_path": self.metrics["requests_by_path"]
            },
            "performance": {
                "avg_response_time_ms": round(avg_response_time, 2),
                "max_response_time_ms": max(self.metrics["response_times"]) if self.metrics["response_times"] else 0,
                "min_response_time_ms": min(self.metrics["response_times"]) if self.metrics["response_times"] else 0
            },
            "errors": {
                "total": self.metrics["errors_total"],
                "by_type": self.metrics["errors_by_type"]
            },
            "cache": {
                "hits": self.metrics["cache_hits"],
                "misses": self.metrics["cache_misses"],
                "hit_rate": round(
                    self.metrics["cache_hits"] / (self.metrics["cache_hits"] + self.metrics["cache_misses"]) * 100
                    if (self.metrics["cache_hits"] + self.metrics["cache_misses"]) > 0 else 0,
                    2
                )
            },
            "database": {
                "queries": self.metrics["database_queries"]
            }
        }


# Global instances
logger = ProductionLogger("videos-api")
metrics = MetricsCollector()
