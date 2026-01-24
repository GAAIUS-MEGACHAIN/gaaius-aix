"""
GAAIUS Security & Authentication Module
JWT token management, password hashing, encryption, RBAC
"""

import os
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple
from enum import Enum
import logging
import re

import jwt
from passlib.context import CryptContext
from cryptography.fernet import Fernet
from pydantic import BaseModel, Field, validator

from backend.core.config import get_settings
from backend.core.exceptions import (
    AuthenticationError, ForbiddenError, ValidationError, ErrorCode
)

logger = logging.getLogger(__name__)
settings = get_settings()


class UserRole(str, Enum):
    """User roles for RBAC"""
    STUDENT = "student"
    INSTRUCTOR = "instructor"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


class Permission(str, Enum):
    """Granular permissions"""
    # Student permissions
    ENROLL_COURSE = "enroll_course"
    VIEW_OWN_COURSES = "view_own_courses"
    TAKE_EXAM = "take_exam"
    VIEW_OWN_GRADES = "view_own_grades"
    VIEW_OWN_CERTIFICATES = "view_own_certificates"
    
    # Instructor permissions
    CREATE_COURSE = "create_course"
    EDIT_OWN_COURSE = "edit_own_course"
    DELETE_OWN_COURSE = "delete_own_course"
    VIEW_STUDENT_SUBMISSIONS = "view_student_submissions"
    GRADE_SUBMISSIONS = "grade_submissions"
    VIEW_COURSE_ANALYTICS = "view_course_analytics"
    
    # Admin permissions
    MANAGE_USERS = "manage_users"
    MANAGE_COURSES = "manage_courses"
    VIEW_ALL_GRADES = "view_all_grades"
    MANAGE_CONTENT = "manage_content"
    VIEW_ANALYTICS = "view_analytics"
    MANAGE_SYSTEM = "manage_system"
    
    # Super admin
    SUPER_ADMIN_ALL = "super_admin_all"


# Role to permissions mapping
ROLE_PERMISSIONS: Dict[UserRole, List[Permission]] = {
    UserRole.STUDENT: [
        Permission.ENROLL_COURSE,
        Permission.VIEW_OWN_COURSES,
        Permission.TAKE_EXAM,
        Permission.VIEW_OWN_GRADES,
        Permission.VIEW_OWN_CERTIFICATES,
    ],
    UserRole.INSTRUCTOR: [
        *[p for p in Permission if p.value.startswith("view_own")],
        Permission.CREATE_COURSE,
        Permission.EDIT_OWN_COURSE,
        Permission.DELETE_OWN_COURSE,
        Permission.VIEW_STUDENT_SUBMISSIONS,
        Permission.GRADE_SUBMISSIONS,
        Permission.VIEW_COURSE_ANALYTICS,
    ],
    UserRole.ADMIN: [
        *[p for p in Permission if p != Permission.SUPER_ADMIN_ALL],
    ],
    UserRole.SUPER_ADMIN: [
        Permission.SUPER_ADMIN_ALL,
    ]
}


# Password hashing configuration
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12  # High rounds for security
)


class TokenPayload(BaseModel):
    """JWT token payload"""
    user_id: str
    email: str
    username: str
    role: UserRole
    permissions: List[Permission]
    exp: datetime
    iat: datetime
    jti: str = Field(default_factory=lambda: secrets.token_urlsafe(32))  # Token ID for revocation


class TokenData(BaseModel):
    """Decoded token data"""
    user_id: str
    email: str
    username: str
    role: UserRole
    permissions: List[Permission]
    token_id: str


class SecurityManager:
    """Comprehensive security management"""
    
    # Encryption key for sensitive data
    _encryption_key = Fernet.generate_key()
    _cipher = Fernet(_encryption_key)
    
    # Blacklisted tokens (for logout)
    _token_blacklist: set = set()
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using bcrypt
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password
            
        Raises:
            ValidationError: If password is invalid
        """
        SecurityManager._validate_password_strength(password)
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash
        
        Args:
            plain_password: Plain text password
            hashed_password: Hashed password
            
        Returns:
            True if password matches, False otherwise
        """
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def _validate_password_strength(password: str) -> None:
        """
        Validate password meets security requirements
        
        Args:
            password: Password to validate
            
        Raises:
            ValidationError: If password is weak
        """
        errors = []
        
        if len(password) < settings.PASSWORD_MIN_LENGTH:
            errors.append(f"Password must be at least {settings.PASSWORD_MIN_LENGTH} characters")
        
        if settings.PASSWORD_REQUIRE_UPPERCASE and not re.search(r'[A-Z]', password):
            errors.append("Password must contain uppercase letter")
        
        if settings.PASSWORD_REQUIRE_NUMBERS and not re.search(r'\d', password):
            errors.append("Password must contain number")
        
        if settings.PASSWORD_REQUIRE_SPECIAL and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Password must contain special character")
        
        if errors:
            raise ValidationError(
                message="Password does not meet security requirements",
                details={"errors": errors}
            )
    
    @staticmethod
    def create_access_token(
        user_id: str,
        email: str,
        username: str,
        role: UserRole,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create JWT access token
        
        Args:
            user_id: User ID
            email: User email
            username: Username
            role: User role
            expires_delta: Custom expiration time
            
        Returns:
            JWT token string
        """
        if expires_delta is None:
            expires_delta = timedelta(hours=settings.JWT_EXPIRATION_HOURS)
        
        expire = datetime.utcnow() + expires_delta
        permissions = ROLE_PERMISSIONS.get(role, [])
        
        payload = TokenPayload(
            user_id=user_id,
            email=email,
            username=username,
            role=role,
            permissions=permissions,
            exp=expire,
            iat=datetime.utcnow()
        )
        
        encoded = jwt.encode(
            payload.dict(),
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
        
        logger.info(f"Access token created for user {user_id}")
        return encoded
    
    @staticmethod
    def create_refresh_token(
        user_id: str,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create JWT refresh token
        
        Args:
            user_id: User ID
            expires_delta: Custom expiration time
            
        Returns:
            JWT refresh token string
        """
        if expires_delta is None:
            expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRATION_DAYS)
        
        expire = datetime.utcnow() + expires_delta
        payload = {
            "user_id": user_id,
            "type": "refresh",
            "exp": expire,
            "iat": datetime.utcnow(),
            "jti": secrets.token_urlsafe(32)
        }
        
        encoded = jwt.encode(
            payload,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
        
        logger.info(f"Refresh token created for user {user_id}")
        return encoded
    
    @staticmethod
    def verify_token(token: str) -> TokenData:
        """
        Verify and decode JWT token
        
        Args:
            token: JWT token string
            
        Returns:
            Decoded token data
            
        Raises:
            AuthenticationError: If token is invalid or expired
        """
        try:
            # Check if token is blacklisted
            token_id = SecurityManager._extract_token_id(token)
            if token_id in SecurityManager._token_blacklist:
                raise AuthenticationError(
                    message="Token has been revoked",
                    error_code=ErrorCode.TOKEN_EXPIRED
                )
            
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            
            return TokenData(
                user_id=payload["user_id"],
                email=payload["email"],
                username=payload["username"],
                role=UserRole(payload["role"]),
                permissions=[Permission(p) for p in payload.get("permissions", [])],
                token_id=payload.get("jti", "")
            )
            
        except jwt.ExpiredSignatureError:
            raise AuthenticationError(
                message="Token has expired",
                error_code=ErrorCode.TOKEN_EXPIRED
            )
        except jwt.InvalidTokenError as e:
            raise AuthenticationError(
                message="Invalid token",
                error_code=ErrorCode.TOKEN_INVALID,
                cause=e
            )
    
    @staticmethod
    def _extract_token_id(token: str) -> str:
        """Extract JTI (token ID) without verification"""
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
                options={"verify_signature": False}
            )
            return payload.get("jti", "")
        except:
            return ""
    
    @staticmethod
    def revoke_token(token: str) -> None:
        """
        Revoke a token (add to blacklist)
        
        Args:
            token: Token to revoke
        """
        token_id = SecurityManager._extract_token_id(token)
        if token_id:
            SecurityManager._token_blacklist.add(token_id)
            logger.info(f"Token {token_id} revoked")
    
    @staticmethod
    def encrypt_sensitive_data(data: str) -> str:
        """
        Encrypt sensitive data
        
        Args:
            data: Data to encrypt
            
        Returns:
            Encrypted data (base64)
        """
        encrypted = SecurityManager._cipher.encrypt(data.encode())
        return encrypted.decode()
    
    @staticmethod
    def decrypt_sensitive_data(encrypted_data: str) -> str:
        """
        Decrypt sensitive data
        
        Args:
            encrypted_data: Encrypted data (base64)
            
        Returns:
            Decrypted data
        """
        decrypted = SecurityManager._cipher.decrypt(encrypted_data.encode())
        return decrypted.decode()
    
    @staticmethod
    def has_permission(user_role: UserRole, required_permission: Permission) -> bool:
        """
        Check if user role has required permission
        
        Args:
            user_role: User's role
            required_permission: Required permission
            
        Returns:
            True if user has permission, False otherwise
        """
        if user_role == UserRole.SUPER_ADMIN:
            return True
        
        return required_permission in ROLE_PERMISSIONS.get(user_role, [])
    
    @staticmethod
    def check_permission(token_data: TokenData, required_permission: Permission) -> None:
        """
        Check if token has required permission
        
        Args:
            token_data: Decoded token data
            required_permission: Required permission
            
        Raises:
            ForbiddenError: If permission is not granted
        """
        if token_data.role == UserRole.SUPER_ADMIN:
            return
        
        if required_permission not in token_data.permissions:
            raise ForbiddenError(
                message=f"Permission '{required_permission.value}' is required",
                details={"required_permission": required_permission.value}
            )
    
    @staticmethod
    def generate_secure_token(length: int = 32) -> str:
        """
        Generate cryptographically secure random token
        
        Args:
            length: Token length
            
        Returns:
            Random token
        """
        return secrets.token_urlsafe(length)
    
    @staticmethod
    def hash_sensitive_field(value: str) -> str:
        """
        Hash a field for comparison (not for passwords)
        
        Args:
            value: Value to hash
            
        Returns:
            SHA256 hash
        """
        return hashlib.sha256(value.encode()).hexdigest()


class RateLimiter:
    """Simple in-memory rate limiter"""
    
    _requests: Dict[str, List[datetime]] = {}
    
    @staticmethod
    def is_allowed(
        identifier: str,
        max_requests: int,
        window_seconds: int = 60
    ) -> Tuple[bool, Optional[int]]:
        """
        Check if request is allowed under rate limit
        
        Args:
            identifier: Unique identifier (IP, user ID, etc.)
            max_requests: Max requests allowed
            window_seconds: Time window in seconds
            
        Returns:
            (is_allowed, retry_after_seconds)
        """
        now = datetime.utcnow()
        window_start = now - timedelta(seconds=window_seconds)
        
        if identifier not in RateLimiter._requests:
            RateLimiter._requests[identifier] = []
        
        # Remove old requests outside window
        RateLimiter._requests[identifier] = [
            req_time for req_time in RateLimiter._requests[identifier]
            if req_time > window_start
        ]
        
        # Check if within limit
        if len(RateLimiter._requests[identifier]) < max_requests:
            RateLimiter._requests[identifier].append(now)
            return True, None
        
        # Calculate retry after
        oldest_request = min(RateLimiter._requests[identifier])
        retry_after = int((oldest_request + timedelta(seconds=window_seconds) - now).total_seconds()) + 1
        
        return False, retry_after
