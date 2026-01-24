"""
GAAIUS Exception Handling & Error Management
Custom exceptions with comprehensive error tracking and recovery
"""

import logging
import traceback
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class ErrorCode(str, Enum):
    """Standardized error codes for API responses"""
    # Authentication & Authorization
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    TOKEN_INVALID = "TOKEN_INVALID"
    
    # Resource Errors
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    RESOURCE_ALREADY_EXISTS = "RESOURCE_ALREADY_EXISTS"
    RESOURCE_CONFLICT = "RESOURCE_CONFLICT"
    
    # Validation Errors
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_INPUT = "INVALID_INPUT"
    INVALID_FILE_TYPE = "INVALID_FILE_TYPE"
    FILE_TOO_LARGE = "FILE_TOO_LARGE"
    
    # Proctoring Errors
    FACIAL_ENROLLMENT_FAILED = "FACIAL_ENROLLMENT_FAILED"
    IDENTITY_VERIFICATION_FAILED = "IDENTITY_VERIFICATION_FAILED"
    PROCTORING_SESSION_EXPIRED = "PROCTORING_SESSION_EXPIRED"
    INSUFFICIENT_FACE_SAMPLES = "INSUFFICIENT_FACE_SAMPLES"
    FACE_NOT_DETECTED = "FACE_NOT_DETECTED"
    
    # Exam Errors
    EXAM_NOT_FOUND = "EXAM_NOT_FOUND"
    EXAM_NOT_STARTED = "EXAM_NOT_STARTED"
    EXAM_ALREADY_SUBMITTED = "EXAM_ALREADY_SUBMITTED"
    EXAM_TIME_EXPIRED = "EXAM_TIME_EXPIRED"
    EXAM_PROCTORING_FAILED = "EXAM_PROCTORING_FAILED"
    
    # Database Errors
    DATABASE_ERROR = "DATABASE_ERROR"
    DATABASE_CONNECTION_ERROR = "DATABASE_CONNECTION_ERROR"
    DATABASE_QUERY_ERROR = "DATABASE_QUERY_ERROR"
    
    # External Service Errors
    EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"
    GROQ_API_ERROR = "GROQ_API_ERROR"
    GROQ_RATE_LIMIT = "GROQ_RATE_LIMIT"
    CONTENT_SOURCE_UNAVAILABLE = "CONTENT_SOURCE_UNAVAILABLE"
    
    # File & Upload Errors
    UPLOAD_FAILED = "UPLOAD_FAILED"
    S3_UPLOAD_ERROR = "S3_UPLOAD_ERROR"
    FILE_NOT_FOUND = "FILE_NOT_FOUND"
    
    # System Errors
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    REQUEST_TIMEOUT = "REQUEST_TIMEOUT"


class GAAIUSException(Exception):
    """Base exception for all GAAIUS errors"""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.INTERNAL_SERVER_ERROR,
        http_status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        self.message = message
        self.error_code = error_code
        self.http_status_code = http_status_code
        self.details = details or {}
        self.cause = cause
        self.timestamp = datetime.utcnow().isoformat()
        self.stack_trace = traceback.format_exc()
        
        super().__init__(self.message)
        
        self._log_error()
    
    def _log_error(self):
        """Log error with appropriate level"""
        log_data = {
            "error_code": self.error_code.value,
            "http_status": self.http_status_code,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp
        }
        
        if self.http_status_code >= 500:
            logger.error(f"Server error: {log_data}", exc_info=self.cause)
        elif self.http_status_code >= 400:
            logger.warning(f"Client error: {log_data}")
        else:
            logger.info(f"Exception: {log_data}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API response"""
        response = {
            "error": {
                "code": self.error_code.value,
                "message": self.message,
                "timestamp": self.timestamp
            }
        }
        
        if self.details:
            response["error"]["details"] = self.details
        
        return response


class AuthenticationError(GAAIUSException):
    """Authentication and authorization errors"""
    
    def __init__(
        self,
        message: str = "Authentication failed",
        error_code: ErrorCode = ErrorCode.UNAUTHORIZED,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            http_status_code=401,
            details=details,
            cause=cause
        )


class ForbiddenError(GAAIUSException):
    """Access forbidden error"""
    
    def __init__(
        self,
        message: str = "Access forbidden",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code=ErrorCode.FORBIDDEN,
            http_status_code=403,
            details=details
        )


class ValidationError(GAAIUSException):
    """Request validation errors"""
    
    def __init__(
        self,
        message: str = "Validation failed",
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        super().__init__(
            message=message,
            error_code=ErrorCode.VALIDATION_ERROR,
            http_status_code=422,
            details=details,
            cause=cause
        )


class ResourceNotFoundError(GAAIUSException):
    """Resource not found error"""
    
    def __init__(
        self,
        message: str = "Resource not found",
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None
    ):
        details = {}
        if resource_type:
            details["resource_type"] = resource_type
        if resource_id:
            details["resource_id"] = resource_id
        
        super().__init__(
            message=message,
            error_code=ErrorCode.RESOURCE_NOT_FOUND,
            http_status_code=404,
            details=details
        )


class ConflictError(GAAIUSException):
    """Resource conflict error"""
    
    def __init__(
        self,
        message: str = "Resource conflict",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code=ErrorCode.RESOURCE_CONFLICT,
            http_status_code=409,
            details=details
        )


class FacialEnrollmentError(GAAIUSException):
    """Facial enrollment specific errors"""
    
    def __init__(
        self,
        message: str = "Facial enrollment failed",
        reason: Optional[str] = None,
        cause: Optional[Exception] = None
    ):
        details = {"reason": reason} if reason else {}
        super().__init__(
            message=message,
            error_code=ErrorCode.FACIAL_ENROLLMENT_FAILED,
            http_status_code=400,
            details=details,
            cause=cause
        )


class IdentityVerificationError(GAAIUSException):
    """Identity verification failures"""
    
    def __init__(
        self,
        message: str = "Identity verification failed",
        confidence: Optional[float] = None,
        required_confidence: float = 0.85,
        cause: Optional[Exception] = None
    ):
        details = {}
        if confidence is not None:
            details["confidence"] = confidence
            details["required"] = required_confidence
        
        super().__init__(
            message=message,
            error_code=ErrorCode.IDENTITY_VERIFICATION_FAILED,
            http_status_code=403,
            details=details,
            cause=cause
        )


class ProctoringViolationError(GAAIUSException):
    """Proctoring violations that fail an exam"""
    
    def __init__(
        self,
        message: str = "Proctoring violation detected",
        violations: Optional[list] = None,
        violation_score: int = 0
    ):
        details = {}
        if violations:
            details["violations"] = violations
        if violation_score:
            details["violation_score"] = violation_score
        
        super().__init__(
            message=message,
            error_code=ErrorCode.EXAM_PROCTORING_FAILED,
            http_status_code=403,
            details=details
        )


class ExamError(GAAIUSException):
    """Exam-specific errors"""
    
    def __init__(
        self,
        message: str = "Exam error",
        error_code: ErrorCode = ErrorCode.EXAM_NOT_FOUND,
        exam_id: Optional[str] = None,
        cause: Optional[Exception] = None
    ):
        details = {}
        if exam_id:
            details["exam_id"] = exam_id
        
        super().__init__(
            message=message,
            error_code=error_code,
            http_status_code=400,
            details=details,
            cause=cause
        )


class DatabaseError(GAAIUSException):
    """Database operation errors"""
    
    def __init__(
        self,
        message: str = "Database error",
        error_code: ErrorCode = ErrorCode.DATABASE_ERROR,
        operation: Optional[str] = None,
        cause: Optional[Exception] = None
    ):
        details = {}
        if operation:
            details["operation"] = operation
        
        super().__init__(
            message=message,
            error_code=error_code,
            http_status_code=500,
            details=details,
            cause=cause
        )


class ExternalServiceError(GAAIUSException):
    """External API errors (Groq, content sources, etc.)"""
    
    def __init__(
        self,
        message: str = "External service error",
        service_name: Optional[str] = None,
        error_code: ErrorCode = ErrorCode.EXTERNAL_SERVICE_ERROR,
        cause: Optional[Exception] = None
    ):
        details = {}
        if service_name:
            details["service"] = service_name
        
        super().__init__(
            message=message,
            error_code=error_code,
            http_status_code=502,
            details=details,
            cause=cause
        )


class RateLimitError(GAAIUSException):
    """Rate limit exceeded error"""
    
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after_seconds: Optional[int] = None
    ):
        details = {}
        if retry_after_seconds:
            details["retry_after"] = retry_after_seconds
        
        super().__init__(
            message=message,
            error_code=ErrorCode.RATE_LIMIT_EXCEEDED,
            http_status_code=429,
            details=details
        )


class RequestTimeoutError(GAAIUSException):
    """Request timeout error"""
    
    def __init__(
        self,
        message: str = "Request timeout",
        timeout_seconds: Optional[float] = None,
        cause: Optional[Exception] = None
    ):
        details = {}
        if timeout_seconds:
            details["timeout_seconds"] = timeout_seconds
        
        super().__init__(
            message=message,
            error_code=ErrorCode.REQUEST_TIMEOUT,
            http_status_code=504,
            details=details,
            cause=cause
        )


class FileUploadError(GAAIUSException):
    """File upload and processing errors"""
    
    def __init__(
        self,
        message: str = "File upload failed",
        error_code: ErrorCode = ErrorCode.UPLOAD_FAILED,
        filename: Optional[str] = None,
        cause: Optional[Exception] = None
    ):
        details = {}
        if filename:
            details["filename"] = filename
        
        super().__init__(
            message=message,
            error_code=error_code,
            http_status_code=400,
            details=details,
            cause=cause
        )


class GroqAPIError(ExternalServiceError):
    """Groq API specific errors"""
    
    def __init__(
        self,
        message: str = "Groq API error",
        error_code: ErrorCode = ErrorCode.GROQ_API_ERROR,
        groq_error_code: Optional[str] = None,
        cause: Optional[Exception] = None
    ):
        details = {}
        if groq_error_code:
            details["groq_error"] = groq_error_code
        
        super().__init__(
            message=message,
            service_name="Groq API",
            error_code=error_code,
            cause=cause
        )
        self.details.update(details)


class ContentSourceError(ExternalServiceError):
    """Content source integration errors"""
    
    def __init__(
        self,
        message: str = "Content source error",
        source_name: Optional[str] = None,
        cause: Optional[Exception] = None
    ):
        super().__init__(
            message=message,
            service_name=source_name or "Content Source",
            error_code=ErrorCode.CONTENT_SOURCE_UNAVAILABLE,
            cause=cause
        )
