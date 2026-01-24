"""
GAAIUS Application Configuration Management
Production-grade environment-based configuration with validation
"""

import os
import logging
from typing import Optional, Dict, Any, List
from enum import Enum
from functools import lru_cache

logger = logging.getLogger(__name__)


class Environment(str, Enum):
    """Application environments"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class Settings:
    """Application settings - environment-based configuration"""
    
    # ==================== ENVIRONMENT ====================
    ENVIRONMENT: Environment = Environment(os.getenv("ENV", "development"))
    DEBUG: bool = ENVIRONMENT in [Environment.DEVELOPMENT, Environment.TESTING]
    
    # ==================== SERVER ====================
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8000))
    WORKERS: int = int(os.getenv("WORKERS", 4))
    API_VERSION: str = "v1"
    API_TITLE: str = "GAAIUS E-Learning Platform API"
    API_DESCRIPTION: str = "Enterprise distance learning platform with AI proctoring"
    
    # ==================== DATABASE ====================
    MONGODB_URI: str = os.getenv(
        "MONGODB_URI",
        "mongodb+srv://user:password@cluster.mongodb.net/gaaius?retryWrites=true&w=majority"
    )
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "gaaius_elearning")
    MONGODB_POOL_SIZE: int = int(os.getenv("MONGODB_POOL_SIZE", 50))
    MONGODB_MAX_IDLE_TIME_MS: int = int(os.getenv("MONGODB_MAX_IDLE_TIME_MS", 45000))
    MONGODB_CONNECT_TIMEOUT_MS: int = int(os.getenv("MONGODB_CONNECT_TIMEOUT_MS", 10000))
    MONGODB_SOCKET_TIMEOUT_MS: int = int(os.getenv("MONGODB_SOCKET_TIMEOUT_MS", 30000))
    MONGODB_SERVER_SELECTION_TIMEOUT_MS: int = int(os.getenv("MONGODB_SERVER_SELECTION_TIMEOUT_MS", 30000))
    
    # ==================== SECURITY ====================
    JWT_SECRET_KEY: str = os.getenv(
        "JWT_SECRET_KEY",
        "change-this-super-secret-key-in-production-environments"
    )
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = int(os.getenv("JWT_EXPIRATION_HOURS", 24))
    REFRESH_TOKEN_EXPIRATION_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRATION_DAYS", 7))
    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_REQUIRE_UPPERCASE: bool = True
    PASSWORD_REQUIRE_NUMBERS: bool = True
    PASSWORD_REQUIRE_SPECIAL: bool = True
    
    # API Security
    ALLOWED_ORIGINS: List[str] = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:3000,http://localhost:8000"
    ).split(",")
    ALLOW_CREDENTIALS: bool = True
    ALLOW_METHODS: List[str] = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
    ALLOW_HEADERS: List[str] = ["*"]
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_REQUESTS_PER_MINUTE", 60))
    RATE_LIMIT_AUTH_REQUESTS_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_AUTH_REQUESTS_PER_MINUTE", 5))
    RATE_LIMIT_UPLOAD_REQUESTS_PER_HOUR: int = int(os.getenv("RATE_LIMIT_UPLOAD_REQUESTS_PER_HOUR", 10))
    
    # ==================== API KEYS ====================
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_API_BASE_URL: str = os.getenv("GROQ_API_BASE_URL", "https://api.groq.com/openai/v1")
    
    # AWS
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    AWS_S3_BUCKET: str = os.getenv("AWS_S3_BUCKET", "gaaius-elearning")
    AWS_CLOUDFRONT_DOMAIN: str = os.getenv("AWS_CLOUDFRONT_DOMAIN", "")
    AWS_S3_MAX_RETRIES: int = 3
    
    # ==================== AI PROCTORING ====================
    FACIAL_RECOGNITION_TOLERANCE: float = float(os.getenv("FACIAL_RECOGNITION_TOLERANCE", 0.6))
    FACIAL_RECOGNITION_MODEL: str = os.getenv("FACIAL_RECOGNITION_MODEL", "cnn")  # cnn or hog
    MIN_FACE_SAMPLES_FOR_ENROLLMENT: int = int(os.getenv("MIN_FACE_SAMPLES_FOR_ENROLLMENT", 3))
    FACE_DETECTION_CONFIDENCE_THRESHOLD: float = 0.8
    
    # Frame Processing
    EXAM_FRAME_PROCESSING_FPS: int = int(os.getenv("EXAM_FRAME_PROCESSING_FPS", 2))
    EXAM_FRAME_BUFFER_SIZE: int = int(os.getenv("EXAM_FRAME_BUFFER_SIZE", 300))
    FRAME_PROCESSING_TIMEOUT_SECONDS: int = int(os.getenv("FRAME_PROCESSING_TIMEOUT_SECONDS", 5))
    
    # Identity Verification
    IDENTITY_VERIFICATION_INTERVAL_MINUTES: int = int(os.getenv("IDENTITY_VERIFICATION_INTERVAL_MINUTES", 5))
    IDENTITY_VERIFICATION_CONFIDENCE_THRESHOLD: float = 0.85
    IDENTITY_VERIFICATION_MAX_RETRIES: int = 3
    
    # Proctoring Rules
    PROCTORING_VIOLATION_THRESHOLD_SCORE: int = int(os.getenv("PROCTORING_VIOLATION_THRESHOLD_SCORE", 500))
    PROCTORING_AUTO_FAIL_VIOLATIONS: List[str] = [
        "multiple_faces",
        "phone_detected",
        "no_face_detected"
    ]
    PROCTORING_WARNING_VIOLATIONS: List[str] = [
        "face_out_of_frame",
        "head_turning",
        "eye_movement_suspicious"
    ]
    
    # ==================== GROQ AI ====================
    GROQ_MODEL_NAME: str = os.getenv("GROQ_MODEL_NAME", "mixtral-8x7b-32768")
    GROQ_TEMPERATURE: float = float(os.getenv("GROQ_TEMPERATURE", 0.3))
    GROQ_MAX_TOKENS: int = int(os.getenv("GROQ_MAX_TOKENS", 1024))
    GROQ_TIMEOUT_SECONDS: int = int(os.getenv("GROQ_TIMEOUT_SECONDS", 30))
    GROQ_MAX_RETRIES: int = int(os.getenv("GROQ_MAX_RETRIES", 3))
    GROQ_RETRY_BACKOFF_FACTOR: float = float(os.getenv("GROQ_RETRY_BACKOFF_FACTOR", 1.5))
    GROQ_RATE_LIMIT_PER_MINUTE: int = int(os.getenv("GROQ_RATE_LIMIT_PER_MINUTE", 30))
    
    # ==================== CONTENT SOURCES ====================
    OPENSTAX_API_TIMEOUT: int = int(os.getenv("OPENSTAX_API_TIMEOUT", 30))
    OPENSTAX_API_BASE_URL: str = "https://api.openstax.org/api/v2"
    
    LIBRIVOX_API_TIMEOUT: int = int(os.getenv("LIBRIVOX_API_TIMEOUT", 30))
    LIBRIVOX_API_BASE_URL: str = "https://librivox.org/api/cache/metadata.json"
    
    MIT_OCW_API_TIMEOUT: int = int(os.getenv("MIT_OCW_API_TIMEOUT", 30))
    MIT_OCW_API_BASE_URL: str = "https://ocw.mit.edu/api/v2"
    
    KHAN_ACADEMY_API_TIMEOUT: int = int(os.getenv("KHAN_ACADEMY_API_TIMEOUT", 30))
    KHAN_ACADEMY_API_BASE_URL: str = "https://www.khanacademy.org/api/v2"
    
    CONTENT_IMPORT_BATCH_SIZE: int = int(os.getenv("CONTENT_IMPORT_BATCH_SIZE", 100))
    CONTENT_IMPORT_MAX_CONCURRENT: int = int(os.getenv("CONTENT_IMPORT_MAX_CONCURRENT", 5))
    CONTENT_CACHE_TTL_HOURS: int = int(os.getenv("CONTENT_CACHE_TTL_HOURS", 24))
    
    # ==================== FILE UPLOAD ====================
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", 50))
    MAX_FILE_SIZE_BYTES: int = MAX_FILE_SIZE_MB * 1024 * 1024
    ALLOWED_FILE_EXTENSIONS: List[str] = ["pdf", "mp4", "jpg", "jpeg", "png", "gif", "zip", "docx"]
    ALLOWED_IMAGE_EXTENSIONS: List[str] = ["jpg", "jpeg", "png"]
    ALLOWED_VIDEO_EXTENSIONS: List[str] = ["mp4", "webm", "mov"]
    UPLOAD_TEMP_DIR: str = os.getenv("UPLOAD_TEMP_DIR", "/tmp/gaaius_uploads")
    
    # ==================== EXAM CONFIGURATION ====================
    EXAM_SESSION_TIMEOUT_MINUTES: int = int(os.getenv("EXAM_SESSION_TIMEOUT_MINUTES", 120))
    EXAM_GRACE_PERIOD_SECONDS: int = int(os.getenv("EXAM_GRACE_PERIOD_SECONDS", 300))
    EXAM_AUTO_SUBMIT_ON_TIMEOUT: bool = True
    EXAM_ALLOW_REVIEW_AFTER_SUBMIT: bool = True
    
    # ==================== LOGGING ====================
    LOG_LEVEL: str = os.getenv(
        "LOG_LEVEL",
        "DEBUG" if ENVIRONMENT == Environment.DEVELOPMENT else "INFO"
    )
    LOG_FORMAT: str = "json"  # json or text
    LOG_FILE: str = os.getenv("LOG_FILE", "logs/app.log")
    LOG_ROTATION_SIZE: str = "500 MB"
    LOG_RETENTION_DAYS: int = 30
    LOG_REQUESTS: bool = ENVIRONMENT != Environment.PRODUCTION
    LOG_DB_QUERIES: bool = ENVIRONMENT == Environment.DEVELOPMENT
    
    # ==================== MONITORING ====================
    ENABLE_METRICS: bool = ENVIRONMENT in [Environment.PRODUCTION, Environment.STAGING]
    METRICS_EXPORT_INTERVAL_SECONDS: int = int(os.getenv("METRICS_EXPORT_INTERVAL_SECONDS", 60))
    ENABLE_HEALTH_CHECK: bool = True
    ENABLE_DISTRIBUTED_TRACING: bool = ENVIRONMENT == Environment.PRODUCTION
    
    # Jaeger Tracing
    JAEGER_ENABLED: bool = ENVIRONMENT == Environment.PRODUCTION
    JAEGER_AGENT_HOST: str = os.getenv("JAEGER_AGENT_HOST", "localhost")
    JAEGER_AGENT_PORT: int = int(os.getenv("JAEGER_AGENT_PORT", 6831))
    JAEGER_SERVICE_NAME: str = "gaaius-elearning"
    JAEGER_LOG_SPANS: bool = ENVIRONMENT == Environment.DEVELOPMENT
    
    # ==================== CACHE ====================
    REDIS_ENABLED: bool = os.getenv("REDIS_ENABLED", "false").lower() == "true"
    REDIS_URL: Optional[str] = os.getenv("REDIS_URL", None)
    REDIS_SOCKET_CONNECT_TIMEOUT: int = 5
    REDIS_SOCKET_TIMEOUT: int = 5
    REDIS_RETRY_ON_TIMEOUT: bool = True
    CACHE_TTL_SECONDS: int = int(os.getenv("CACHE_TTL_SECONDS", 3600))
    CACHE_COURSE_TTL_SECONDS: int = int(os.getenv("CACHE_COURSE_TTL_SECONDS", 7200))
    
    # ==================== EMAIL ====================
    EMAIL_ENABLED: bool = os.getenv("EMAIL_ENABLED", "false").lower() == "true"
    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", 587))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    EMAIL_FROM: str = os.getenv("EMAIL_FROM", "noreply@gaaius.com")
    EMAIL_FROM_NAME: str = "GAAIUS Platform"
    
    # ==================== VALIDATION ====================
    @classmethod
    def validate(cls) -> Dict[str, Any]:
        """Validate critical configuration"""
        errors: List[str] = []
        warnings: List[str] = []
        
        # Critical validations
        if not cls.MONGODB_URI or "user:password" in cls.MONGODB_URI:
            errors.append("MONGODB_URI must be set and contain valid credentials")
        
        if cls.ENVIRONMENT == Environment.PRODUCTION:
            if not cls.GROQ_API_KEY:
                warnings.append("GROQ_API_KEY not set - AI grading will be unavailable")
            
            if cls.JWT_SECRET_KEY == "change-this-super-secret-key-in-production-environments":
                errors.append("JWT_SECRET_KEY must be changed in production")
            
            if not cls.AWS_ACCESS_KEY_ID or not cls.AWS_SECRET_ACCESS_KEY:
                warnings.append("AWS credentials not set - file uploads will be unavailable")
        
        # Logging
        if errors:
            logger.error(f"Configuration validation errors: {', '.join(errors)}")
            raise ValueError(f"Configuration validation failed: {', '.join(errors)}")
        
        for warning in warnings:
            logger.warning(f"Configuration warning: {warning}")
        
        return {
            "environment": cls.ENVIRONMENT.value,
            "debug": cls.DEBUG,
            "database": cls.DATABASE_NAME,
            "log_level": cls.LOG_LEVEL,
            "workers": cls.WORKERS
        }
    
    @classmethod
    def get_log_config(cls) -> Dict[str, Any]:
        """Get logging configuration dictionary"""
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                },
                "json": {
                    "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
                    "format": "%(asctime)s %(name)s %(levelname)s %(message)s"
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "json" if cls.LOG_FORMAT == "json" else "default",
                    "level": cls.LOG_LEVEL
                },
                "file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "filename": cls.LOG_FILE,
                    "maxBytes": 500 * 1024 * 1024,
                    "backupCount": 5,
                    "formatter": "json" if cls.LOG_FORMAT == "json" else "default",
                    "level": cls.LOG_LEVEL
                }
            },
            "root": {
                "level": cls.LOG_LEVEL,
                "handlers": ["console", "file"]
            }
        }


@lru_cache
def get_settings() -> Settings:
    """Get application settings (cached)"""
    return Settings()
