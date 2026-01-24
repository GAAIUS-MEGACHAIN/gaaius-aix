"""
PHASE 9: Enterprise Database Models
Production-grade SQLAlchemy models for Netflix Clone
PostgreSQL/MySQL/SQLite compatible
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict, Any
from decimal import Decimal
import uuid
import enum
import json

from sqlalchemy import (
    Column, String, Integer, Float, DateTime, Boolean, 
    ForeignKey, Text, Enum, Numeric, BigInteger, Index,
    UniqueConstraint, CheckConstraint, Table, JSON, create_engine,
    event, pool
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.types import TypeDecorator

# ============================================================================
# UUID TYPE (Compatible with all databases)
# ============================================================================

class GUID(TypeDecorator):
    """Platform-independent GUID type"""
    impl = String(36)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return uuid.UUID(value)


# ============================================================================
# DATABASE BASE
# ============================================================================

Base = declarative_base()


# ============================================================================
# ENUMS
# ============================================================================

class SubscriptionPlanEnum(enum.Enum):
    FREE = "free"
    BASIC = "basic"
    STANDARD = "standard"
    PREMIUM = "premium"
    FAMILY = "family"
    STUDENT = "student"


class VideoQualityEnum(enum.Enum):
    SD_480P = "480p"
    HD_720P = "720p"
    FULL_HD_1080P = "1080p"
    ULTRA_HD_4K = "4K"


class PaymentStatusEnum(enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"
    DISPUTED = "disputed"


class DeviceTypeEnum(enum.Enum):
    WEB = "web"
    MOBILE = "mobile"
    TABLET = "tablet"
    SMART_TV = "smart_tv"
    DESKTOP = "desktop"
    STREAMING_DEVICE = "streaming_device"


class ContentTypeEnum(enum.Enum):
    MOVIE = "movie"
    SERIES = "series"
    DOCUMENTARY = "documentary"
    SPECIAL = "special"
    TRAILER = "trailer"
    SHORT_FILM = "short_film"
    LIVE_EVENT = "live_event"


class ModerationStatusEnum(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    FLAGGED = "flagged"
    UNDER_REVIEW = "under_review"


class ContentRatingEnum(enum.Enum):
    G = "G"
    PG = "PG"
    PG_13 = "PG-13"
    R = "R"
    NC_17 = "NC-17"
    TV_Y = "TV-Y"
    TV_Y7 = "TV-Y7"
    TV_G = "TV-G"
    TV_PG = "TV-PG"
    TV_14 = "TV-14"
    TV_MA = "TV-MA"
    NR = "NR"


class UserRoleEnum(enum.Enum):
    USER = "user"
    ADMIN = "admin"
    MODERATOR = "moderator"
    CONTENT_CREATOR = "content_creator"
    SUPPORT_AGENT = "support_agent"


class NotificationTypeEnum(enum.Enum):
    NEW_CONTENT = "new_content"
    RECOMMENDATION = "recommendation"
    PAYMENT_RECEIPT = "payment_receipt"
    SUBSCRIPTION_EXPIRING = "subscription_expiring"
    DOWNLOAD_COMPLETE = "download_complete"
    SYSTEM_MESSAGE = "system_message"


# ============================================================================
# USERS TABLE
# ============================================================================

class User(Base):
    __tablename__ = "users"

    id = Column(GUID(), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    email_verified = Column(Boolean, default=False)
    phone_verified = Column(Boolean, default=False)

    first_name = Column(String(100))
    last_name = Column(String(100))
    avatar_url = Column(String(500))
    bio = Column(Text)
    birth_date = Column(DateTime(timezone=True))
    country = Column(String(2), index=True)
    language = Column(String(5), default="en")
    timezone = Column(String(50), default="UTC")

    # Account status
    is_active = Column(Boolean, default=True, index=True)
    is_banned = Column(Boolean, default=False)
    ban_reason = Column(Text)

    # Subscription
    subscription_plan = Column(Enum(SubscriptionPlanEnum), default=SubscriptionPlanEnum.FREE, index=True)
    subscription_start_date = Column(DateTime(timezone=True))
    subscription_end_date = Column(DateTime(timezone=True))
    is_subscription_active = Column(Boolean, default=False, index=True)
    next_billing_date = Column(DateTime(timezone=True))

    # Preferences
    preferred_quality = Column(Enum(VideoQualityEnum), default=VideoQualityEnum.FULL_HD_1080P)
    auto_play_enabled = Column(Boolean, default=True)
    autoplay_next_episode = Column(Boolean, default=True)
    subtitle_enabled = Column(Boolean, default=True)
    subtitle_language = Column(String(5), default="en")
    audio_language = Column(String(5), default="en")

    # Parental controls
    parental_control_enabled = Column(Boolean, default=False)
    parental_pin = Column(String(255))
    max_rating = Column(Enum(ContentRatingEnum))

    # Role and permissions
    role = Column(Enum(UserRoleEnum), default=UserRoleEnum.USER, index=True)

    # Two-factor authentication
    two_factor_enabled = Column(Boolean, default=False)
    two_factor_secret = Column(String(255))

    # Last activity
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    last_login_at = Column(DateTime(timezone=True), index=True)
    last_active_at = Column(DateTime(timezone=True))

    # Relationships
    profiles = relationship("Profile", back_populates="user", cascade="all, delete-orphan")
    watchlist = relationship("Watchlist", back_populates="user", cascade="all, delete-orphan")
    watch_history = relationship("WatchHistory", back_populates="user", cascade="all, delete-orphan")
    ratings = relationship("Rating", back_populates="user", cascade="all, delete-orphan")
    devices = relationship("UserDevice", back_populates="user", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="user", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")
    downloads = relationship("Download", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint('email', name='uq_user_email'),
        UniqueConstraint('username', name='uq_user_username'),
        Index('ix_user_created_at', 'created_at'),
        Index('ix_user_subscription_plan', 'subscription_plan'),
        Index('ix_user_last_login_at', 'last_login_at'),
    )


# ============================================================================
# PROFILES TABLE
# ============================================================================

class Profile(Base):
    __tablename__ = "profiles"

    id = Column(GUID(), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(GUID(), ForeignKey('users.id'), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    avatar_url = Column(String(500))
    pin = Column(String(255))
    is_admin = Column(Boolean, default=False)

    language = Column(String(5), default="en")
    subtitle_language = Column(String(5), default="en")
    auto_play = Column(Boolean, default=True)
    show_mature_content = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    last_active_at = Column(DateTime(timezone=True))

    user = relationship("User", back_populates="profiles")
    watch_history = relationship("WatchHistory", back_populates="profile", cascade="all, delete-orphan")

    __table_args__ = (
        Index('ix_profile_user_id', 'user_id'),
    )


# ============================================================================
# CONTENT TABLE
# ============================================================================

class Content(Base):
    __tablename__ = "content"

    id = Column(GUID(), primary_key=True, default=lambda: str(uuid.uuid4()))
    content_type = Column(Enum(ContentTypeEnum), nullable=False, index=True)
    title = Column(String(500), nullable=False, index=True)
    slug = Column(String(600), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=False)
    long_description = Column(Text)

    duration_minutes = Column(Integer)
    release_date = Column(DateTime(timezone=True), nullable=False, index=True)
    production_year = Column(Integer, index=True)

    genres = Column(JSON, nullable=False, default=list)
    cast = Column(JSON, default=list)
    directors = Column(JSON, default=list)
    writers = Column(JSON, default=list)
    producers = Column(JSON, default=list)
    country = Column(String(100))
    language = Column(String(5))

    imdb_id = Column(String(20), index=True)
    imdb_rating = Column(Float)
    age_rating = Column(Enum(ContentRatingEnum))

    poster_url = Column(String(500), nullable=False)
    banner_url = Column(String(500))
    trailer_url = Column(String(500))
    thumbnail_url = Column(String(500))

    # Streaming
    hls_stream_url = Column(String(500))
    dash_stream_url = Column(String(500))
    available_qualities = Column(JSON, default=list)
    default_quality = Column(Enum(VideoQualityEnum), default=VideoQualityEnum.FULL_HD_1080P)

    subtitles_available = Column(JSON, default=list)
    audio_tracks = Column(JSON, default=list)

    # Moderation
    moderation_status = Column(Enum(ModerationStatusEnum), default=ModerationStatusEnum.PENDING, index=True)
    moderation_reason = Column(Text)
    moderation_reviewed_by = Column(GUID(), ForeignKey('users.id'))
    moderation_reviewed_at = Column(DateTime(timezone=True))

    # Publishing
    is_published = Column(Boolean, default=False, index=True)
    published_at = Column(DateTime(timezone=True))

    # Availability
    is_available = Column(Boolean, default=True, index=True)
    available_regions = Column(JSON, default=list)
    availability_start = Column(DateTime(timezone=True))
    availability_end = Column(DateTime(timezone=True))

    # Statistics
    total_views = Column(BigInteger, default=0)
    total_ratings = Column(Integer, default=0)
    average_rating = Column(Float, default=0.0)
    total_watched_minutes = Column(BigInteger, default=0)

    # Metadata
    maturity_level = Column(Integer, default=0)
    is_trending = Column(Boolean, default=False)
    trending_score = Column(Float, default=0.0)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    episodes = relationship("Episode", back_populates="series", cascade="all, delete-orphan")
    watch_history = relationship("WatchHistory", back_populates="content", cascade="all, delete-orphan")
    ratings = relationship("Rating", back_populates="content", cascade="all, delete-orphan")
    watchlist_items = relationship("Watchlist", back_populates="content", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="content", cascade="all, delete-orphan")
    downloads = relationship("Download", back_populates="content", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint('slug', name='uq_content_slug'),
        Index('ix_content_type', 'content_type'),
        Index('ix_content_release_date', 'release_date'),
        Index('ix_content_is_published', 'is_published'),
        Index('ix_content_moderation_status', 'moderation_status'),
        Index('ix_content_is_trending', 'is_trending'),
    )


# ============================================================================
# EPISODES TABLE
# ============================================================================

class Episode(Base):
    __tablename__ = "episodes"

    id = Column(GUID(), primary_key=True, default=lambda: str(uuid.uuid4()))
    series_id = Column(GUID(), ForeignKey('content.id'), nullable=False, index=True)
    season_number = Column(Integer, nullable=False)
    episode_number = Column(Integer, nullable=False)

    title = Column(String(500), nullable=False)
    description = Column(Text)
    duration_minutes = Column(Integer, nullable=False)

    thumbnail_url = Column(String(500))
    hls_stream_url = Column(String(500))
    dash_stream_url = Column(String(500))

    air_date = Column(DateTime(timezone=True))
    director = Column(String(200))
    writer = Column(String(200))

    total_views = Column(BigInteger, default=0)
    average_rating = Column(Float, default=0.0)

    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), onupdate=datetime.now(timezone.utc))

    series = relationship("Content", back_populates="episodes")
    watch_history = relationship("WatchHistory", back_populates="episode", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint('series_id', 'season_number', 'episode_number', name='uq_episode'),
        Index('ix_episode_series_id', 'series_id'),
        CheckConstraint('season_number > 0', name='ck_season_positive'),
        CheckConstraint('episode_number > 0', name='ck_episode_positive'),
    )


# ============================================================================
# WATCHLIST TABLE
# ============================================================================

class Watchlist(Base):
    __tablename__ = "watchlist"

    id = Column(GUID(), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(GUID(), ForeignKey('users.id'), nullable=False, index=True)
    content_id = Column(GUID(), ForeignKey('content.id'), nullable=False, index=True)

    added_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc), index=True)
    list_position = Column(Integer)
    list_name = Column(String(100), default="My List")

    user = relationship("User", back_populates="watchlist")
    content = relationship("Content", back_populates="watchlist_items")

    __table_args__ = (
        UniqueConstraint('user_id', 'content_id', name='uq_watchlist_item'),
        Index('ix_watchlist_user_content', 'user_id', 'content_id'),
    )


# ============================================================================
# WATCH HISTORY TABLE
# ============================================================================

class WatchHistory(Base):
    __tablename__ = "watch_history"

    id = Column(GUID(), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(GUID(), ForeignKey('users.id'), nullable=False, index=True)
    profile_id = Column(GUID(), ForeignKey('profiles.id'), nullable=False)
    content_id = Column(GUID(), ForeignKey('content.id'), nullable=False, index=True)
    episode_id = Column(GUID(), ForeignKey('episodes.id'))

    watch_time_seconds = Column(Integer, default=0)
    duration_seconds = Column(Integer)
    quality_watched = Column(Enum(VideoQualityEnum))
    device_type = Column(Enum(DeviceTypeEnum))

    started_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    last_watched_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc), index=True)
    completed = Column(Boolean, default=False)

    user = relationship("User", back_populates="watch_history")
    profile = relationship("Profile", back_populates="watch_history")
    content = relationship("Content", back_populates="watch_history")
    episode = relationship("Episode", back_populates="watch_history")

    __table_args__ = (
        Index('ix_watch_history_user_id', 'user_id'),
        Index('ix_watch_history_content_id', 'content_id'),
        Index('ix_watch_history_last_watched_at', 'last_watched_at'),
    )


# ============================================================================
# RATINGS TABLE
# ============================================================================

class Rating(Base):
    __tablename__ = "ratings"

    id = Column(GUID(), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(GUID(), ForeignKey('users.id'), nullable=False, index=True)
    content_id = Column(GUID(), ForeignKey('content.id'), nullable=False, index=True)

    rating_value = Column(Integer, nullable=False)
    review_text = Column(Text)
    is_spoiler = Column(Boolean, default=False)

    likes = Column(Integer, default=0)
    dislikes = Column(Integer, default=0)
    helpful_count = Column(Integer, default=0)

    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=datetime.now(timezone.utc))

    user = relationship("User", back_populates="ratings")
    content = relationship("Content", back_populates="ratings")

    __table_args__ = (
        UniqueConstraint('user_id', 'content_id', name='uq_rating_per_user'),
        Index('ix_rating_content_id', 'content_id'),
        CheckConstraint('rating_value >= 1 AND rating_value <= 10', name='ck_rating_range'),
    )


# ============================================================================
# SUBSCRIPTION PLANS
# ============================================================================

class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"

    id = Column(GUID(), primary_key=True, default=lambda: str(uuid.uuid4()))
    plan_name = Column(Enum(SubscriptionPlanEnum), unique=True, nullable=False, index=True)
    display_name = Column(String(100), nullable=False)
    description = Column(Text)

    monthly_price = Column(Numeric(10, 2), nullable=False)
    annual_price = Column(Numeric(10, 2))

    max_simultaneous_streams = Column(Integer, default=1)
    max_download_count = Column(Integer, default=0)
    max_profiles = Column(Integer, default=1)
    max_video_quality = Column(Enum(VideoQualityEnum), default=VideoQualityEnum.SD_480P)
    ad_supported = Column(Boolean, default=False)
    hd_available = Column(Boolean, default=False)
    ultra_hd_available = Column(Boolean, default=False)
    offline_downloads = Column(Boolean, default=False)

    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))

    subscriptions = relationship("Subscription", back_populates="plan")

    __table_args__ = (
        UniqueConstraint('plan_name', name='uq_plan_name'),
    )


# ============================================================================
# SUBSCRIPTIONS
# ============================================================================

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(GUID(), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(GUID(), ForeignKey('users.id'), nullable=False, index=True)
    plan_id = Column(GUID(), ForeignKey('subscription_plans.id'), nullable=False)

    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    is_active = Column(Boolean, default=True, index=True)

    auto_renew = Column(Boolean, default=True)
    renewal_date = Column(DateTime(timezone=True))

    cancelled_at = Column(DateTime(timezone=True))
    cancellation_reason = Column(String(500))

    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), onupdate=datetime.now(timezone.utc))

    user = relationship("User", back_populates="subscriptions")
    plan = relationship("SubscriptionPlan", back_populates="subscriptions")
    payments = relationship("Payment", back_populates="subscription")

    __table_args__ = (
        Index('ix_subscription_user_id', 'user_id'),
        Index('ix_subscription_is_active', 'is_active'),
    )


# ============================================================================
# PAYMENTS
# ============================================================================

class Payment(Base):
    __tablename__ = "payments"

    id = Column(GUID(), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(GUID(), ForeignKey('users.id'), nullable=False, index=True)
    subscription_id = Column(GUID(), ForeignKey('subscriptions.id'))

    stripe_payment_id = Column(String(255), unique=True, index=True)
    stripe_customer_id = Column(String(255), index=True)

    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="USD")
    status = Column(Enum(PaymentStatusEnum), default=PaymentStatusEnum.PENDING, index=True)

    card_last_four = Column(String(4))
    card_brand = Column(String(50))
    card_exp_month = Column(Integer)
    card_exp_year = Column(Integer)

    description = Column(String(255))
    receipt_url = Column(String(500))
    invoice_url = Column(String(500))

    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc), index=True)
    processed_at = Column(DateTime(timezone=True))
    refunded_at = Column(DateTime(timezone=True))

    user = relationship("User", back_populates="payments")
    subscription = relationship("Subscription", back_populates="payments")

    __table_args__ = (
        UniqueConstraint('stripe_payment_id', name='uq_stripe_payment_id'),
        Index('ix_payment_user_id', 'user_id'),
        Index('ix_payment_status', 'status'),
    )


# ============================================================================
# USER DEVICES
# ============================================================================

class UserDevice(Base):
    __tablename__ = "user_devices"

    id = Column(GUID(), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(GUID(), ForeignKey('users.id'), nullable=False, index=True)

    device_name = Column(String(255), nullable=False)
    device_type = Column(Enum(DeviceTypeEnum), nullable=False)
    device_id = Column(String(255), unique=True, index=True)

    os = Column(String(50))
    os_version = Column(String(50))
    browser = Column(String(50))
    browser_version = Column(String(50))

    ip_address = Column(String(45))
    user_agent = Column(String(500))

    is_active = Column(Boolean, default=True)
    is_trusted = Column(Boolean, default=False)

    last_used_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))

    user = relationship("User", back_populates="devices")

    __table_args__ = (
        Index('ix_user_devices_user_id', 'user_id'),
    )


# ============================================================================
# DOWNLOADS
# ============================================================================

class Download(Base):
    __tablename__ = "downloads"

    id = Column(GUID(), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(GUID(), ForeignKey('users.id'), nullable=False, index=True)
    content_id = Column(GUID(), ForeignKey('content.id'), nullable=False)
    episode_id = Column(GUID(), ForeignKey('episodes.id'))

    quality = Column(Enum(VideoQualityEnum), nullable=False)
    file_size_mb = Column(Integer)
    file_path = Column(String(500))

    is_downloading = Column(Boolean, default=False)
    download_progress = Column(Float, default=0.0)
    is_complete = Column(Boolean, default=False)

    expires_at = Column(DateTime(timezone=True))

    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    downloaded_at = Column(DateTime(timezone=True))

    user = relationship("User", back_populates="downloads")
    content = relationship("Content", back_populates="downloads")

    __table_args__ = (
        Index('ix_download_user_id', 'user_id'),
        Index('ix_download_content_id', 'content_id'),
    )


# ============================================================================
# RECOMMENDATIONS
# ============================================================================

class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(GUID(), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(GUID(), ForeignKey('users.id'), nullable=False, index=True)
    content_id = Column(GUID(), ForeignKey('content.id'), nullable=False, index=True)

    algorithm = Column(String(50), nullable=False)
    confidence_score = Column(Float, default=0.0)
    reason = Column(String(255))

    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))

    __table_args__ = (
        Index('ix_recommendation_user_id', 'user_id'),
    )


# ============================================================================
# SESSIONS
# ============================================================================

class Session(Base):
    __tablename__ = "sessions"

    id = Column(GUID(), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(GUID(), ForeignKey('users.id'), nullable=False, index=True)

    session_token = Column(String(500), unique=True, nullable=False, index=True)
    refresh_token = Column(String(500), unique=True)

    device_id = Column(String(255))
    ip_address = Column(String(45))
    user_agent = Column(String(500))

    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    expires_at = Column(DateTime(timezone=True), nullable=False)
    last_activity_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))

    user = relationship("User", back_populates="sessions")

    __table_args__ = (
        UniqueConstraint('session_token', name='uq_session_token'),
        Index('ix_session_user_id', 'user_id'),
    )


# ============================================================================
# NOTIFICATIONS
# ============================================================================

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(GUID(), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(GUID(), ForeignKey('users.id'), nullable=False, index=True)

    notification_type = Column(Enum(NotificationTypeEnum), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    data = Column(JSON, default=dict)

    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime(timezone=True))

    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc), index=True)

    user = relationship("User", back_populates="notifications")

    __table_args__ = (
        Index('ix_notification_user_id', 'user_id'),
        Index('ix_notification_is_read', 'is_read'),
    )


# ============================================================================
# ANALYTICS
# ============================================================================

class Analytics(Base):
    __tablename__ = "analytics"

    id = Column(GUID(), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(GUID(), ForeignKey('users.id'), index=True)
    content_id = Column(GUID(), ForeignKey('content.id'), index=True)

    event_type = Column(String(50), nullable=False, index=True)
    event_data = Column(JSON, default=dict)

    device_type = Column(Enum(DeviceTypeEnum))
    country = Column(String(2))
    city = Column(String(100))

    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc), index=True)

    __table_args__ = (
        Index('ix_analytics_user_id', 'user_id'),
        Index('ix_analytics_content_id', 'content_id'),
        Index('ix_analytics_event_type', 'event_type'),
        Index('ix_analytics_created_at', 'created_at'),
    )


# ============================================================================
# DATABASE SESSION MANAGEMENT
# ============================================================================

def get_database_url() -> str:
    """Get database URL from environment"""
    import os
    db_type = os.environ.get('DATABASE_TYPE', 'sqlite').lower()
    
    if db_type == 'postgresql':
        return f"postgresql://{os.environ.get('DB_USER', 'user')}:{os.environ.get('DB_PASSWORD', 'password')}@{os.environ.get('DB_HOST', 'localhost')}:{os.environ.get('DB_PORT', '5432')}/{os.environ.get('DB_NAME', 'netflix_clone')}"
    elif db_type == 'mysql':
        return f"mysql+pymysql://{os.environ.get('DB_USER', 'user')}:{os.environ.get('DB_PASSWORD', 'password')}@{os.environ.get('DB_HOST', 'localhost')}:{os.environ.get('DB_PORT', '3306')}/{os.environ.get('DB_NAME', 'netflix_clone')}"
    else:
        return f"sqlite:///{os.environ.get('DB_PATH', './netflix_clone.db')}"


def create_db_engine(database_url: str):
    """Create SQLAlchemy engine with connection pooling"""
    if 'sqlite' in database_url:
        return create_engine(
            database_url,
            connect_args={'check_same_thread': False},
            poolclass=pool.StaticPool
        )
    else:
        return create_engine(
            database_url,
            pool_size=20,
            max_overflow=40,
            pool_pre_ping=True,
            echo=False
        )


# Create engine
DATABASE_URL = get_database_url()
engine = create_db_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dependency for FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database"""
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialized successfully")


if __name__ == "__main__":
    init_db()
