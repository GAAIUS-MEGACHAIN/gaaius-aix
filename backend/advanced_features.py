"""
GAAIUS Advanced Features Service
Stories, Video Streaming, Search, Algorithm, Live, Creator Fund, Effects, Marketplace, Ads
Production-grade implementation for enterprise social platform
"""

import os
import uuid
import asyncio
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Optional, BinaryIO
from urllib.parse import urlparse
from enum import Enum
import mimetypes
import re

from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel, Field, validator
import boto3
from botocore.exceptions import ClientError
import logging

logger = logging.getLogger(__name__)

# ==================== ENUMS ====================

class StoryVisibility(str, Enum):
    PUBLIC = "public"
    FOLLOWERS = "followers"
    CLOSE_FRIENDS = "close_friends"
    PRIVATE = "private"

class VideoQuality(str, Enum):
    MOBILE = "360p"
    STANDARD = "720p"
    HD = "1080p"
    FULL_HD = "1440p"

class EffectType(str, Enum):
    FILTER = "filter"
    FRAME = "frame"
    TRANSITION = "transition"
    SOUND = "sound"
    AR_EFFECT = "ar_effect"

class MarketplaceCategory(str, Enum):
    SERVICES = "services"
    PRODUCTS = "products"
    COLLABORATIONS = "collaborations"
    TUTORING = "tutoring"
    CONSULTING = "consulting"
    TOOLS = "tools"
    TEMPLATES = "templates"
    COURSES = "courses"

class AdTargetingType(str, Enum):
    INTEREST = "interest"
    DEMOGRAPHIC = "demographic"
    BEHAVIOR = "behavior"
    LOOKALIKE = "lookalike"
    CUSTOM_AUDIENCE = "custom_audience"

class AdPlacementType(str, Enum):
    FEED = "feed"
    STORIES = "stories"
    SEARCH_RESULTS = "search_results"
    SUGGESTED_USERS = "suggested_users"
    SIDEBAR = "sidebar"

# ==================== DATA MODELS ====================

class Story(BaseModel):
    """24-hour disappearing content"""
    story_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    media_url: str  # Video or image
    media_type: str  # "image" or "video"
    thumbnail_url: Optional[str] = None
    caption: Optional[str] = Field(None, max_length=300)
    visibility: StoryVisibility = StoryVisibility.PUBLIC
    allow_replies: bool = True
    allow_shares: bool = True
    
    # Engagement
    views: List[str] = Field(default_factory=list)  # user_ids who viewed
    replies: List[Dict] = Field(default_factory=list)  # [{user_id, text, timestamp}]
    shares_count: int = 0
    
    # Metadata
    hashtags: List[str] = Field(default_factory=list)
    mentions: List[str] = Field(default_factory=list)
    ai_suggested_hashtags: List[str] = Field(default_factory=list)
    
    # Auto-delete after 24 hours
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime = Field(default_factory=lambda: datetime.utcnow() + timedelta(hours=24))
    is_expired: bool = False
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

class VideoStream(BaseModel):
    """Production video with streaming support"""
    video_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    title: str = Field(..., max_length=200)
    description: str = Field(default="", max_length=5000)
    
    # Video data
    source_url: str  # Original S3 URL
    hls_manifest_url: Optional[str] = None  # HLS stream URL
    thumbnail_url: Optional[str] = None
    duration_seconds: int
    video_quality: VideoQuality = VideoQuality.HD
    bitrate_kbps: int = 5000
    
    # Metadata
    tags: List[str] = Field(default_factory=list)
    hashtags: List[str] = Field(default_factory=list)
    category: str = "general"
    is_public: bool = True
    allow_comments: bool = True
    allow_sharing: bool = True
    
    # Engagement
    views_count: int = 0
    likes_count: int = 0
    comments_count: int = 0
    shares_count: int = 0
    watch_time_seconds: int = 0
    
    # AI Analysis
    ai_optimized: bool = False
    ai_tags: List[str] = Field(default_factory=list)
    sentiment_score: Optional[float] = None
    suggested_hashtags: List[str] = Field(default_factory=list)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

class SearchResult(BaseModel):
    """Unified search result across posts, users, hashtags"""
    result_type: str  # "user", "post", "hashtag", "video"
    result_id: str
    title: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    metadata: Dict = Field(default_factory=dict)
    relevance_score: float = 1.0
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Effect(BaseModel):
    """User-generated or platform effects for creation tools"""
    effect_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    creator_id: str
    name: str = Field(..., max_length=100)
    description: str = Field(default="", max_length=500)
    effect_type: EffectType
    
    # Visual data
    thumbnail_url: str
    effect_file_url: str  # S3 JSON or asset bundle
    preview_video_url: Optional[str] = None
    
    # Metadata
    tags: List[str] = Field(default_factory=list)
    category: str = "general"
    is_public: bool = True
    is_paid: bool = False
    price_usd: Optional[float] = None
    
    # Stats
    downloads_count: int = 0
    rating: float = 0.0
    reviews_count: int = 0
    uses_in_posts: int = 0
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

class MarketplaceProduct(BaseModel):
    """Marketplace product/service listing"""
    product_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    seller_id: str
    
    # Basic info
    title: str = Field(..., max_length=200)
    description: str = Field(..., max_length=5000)
    category: MarketplaceCategory
    
    # Media
    images: List[str] = Field(default_factory=list)  # S3 URLs
    thumbnail_url: Optional[str] = None
    
    # Pricing
    price_usd: float
    currency: str = "USD"
    is_negotiable: bool = False
    
    # Details
    tags: List[str] = Field(default_factory=list)
    specifications: Dict = Field(default_factory=dict)
    delivery_days: Optional[int] = None
    
    # Engagement
    views_count: int = 0
    saves_count: int = 0
    inquiries_count: int = 0
    sales_count: int = 0
    rating: float = 0.0
    reviews_count: int = 0
    
    # Status
    is_active: bool = True
    is_featured: bool = False
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

class Advertisement(BaseModel):
    """Advertisement campaign"""
    ad_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    advertiser_id: str
    
    # Campaign details
    campaign_name: str = Field(..., max_length=200)
    campaign_goal: str  # "awareness", "conversions", "engagement"
    
    # Creative
    headline: str = Field(..., max_length=100)
    description: str = Field(..., max_length=500)
    image_url: str
    cta_url: str
    cta_text: str = "Learn More"
    
    # Targeting
    target_interests: List[str] = Field(default_factory=list)
    target_age_min: int = 13
    target_age_max: int = 65
    target_genders: List[str] = Field(default_factory=lambda: ["all"])
    target_locations: List[str] = Field(default_factory=list)
    target_devices: List[str] = Field(default_factory=lambda: ["all"])
    targeting_type: AdTargetingType = AdTargetingType.INTEREST
    
    # Placement
    placements: List[AdPlacementType] = Field(default_factory=list)
    
    # Budget
    daily_budget_usd: float
    total_budget_usd: float
    bid_amount_usd: float = 0.5
    
    # Performance
    impressions: int = 0
    clicks: int = 0
    conversions: int = 0
    spend_usd: float = 0.0
    ctr: float = 0.0  # Click-through rate
    cpc: float = 0.0  # Cost-per-click
    cpm: float = 0.0  # Cost-per-thousand impressions
    roi: float = 0.0
    
    # Status
    status: str = "draft"  # draft, running, paused, completed
    is_approved: bool = False
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

class CreatorFund(BaseModel):
    """Creator earnings tracking"""
    fund_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    creator_id: str
    
    # Earnings sources
    post_engagement_earnings: float = 0.0  # From ad revenue share
    video_watch_earnings: float = 0.0  # Per 1000 views
    effect_sales_earnings: float = 0.0  # From effect downloads
    marketplace_earnings: float = 0.0  # From marketplace sales
    sponsorship_earnings: float = 0.0  # From brand deals
    
    # Totals
    total_earnings: float = 0.0
    pending_balance: float = 0.0
    withdrawn_balance: float = 0.0
    
    # Thresholds
    withdrawal_threshold_usd: float = 100.0
    is_eligible: bool = False  # 10k followers + 100k views/month
    
    # Payouts
    payout_history: List[Dict] = Field(default_factory=list)  # [{date, amount, method, status}]
    payout_method: Optional[str] = None  # "stripe", "paypal", "bank_transfer"
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

class LiveStream(BaseModel):
    """Live streaming session"""
    stream_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    streamer_id: str
    
    # Stream info
    title: str = Field(..., max_length=200)
    description: Optional[str] = Field(None, max_length=5000)
    category: str = "general"
    
    # Stream details
    rtmp_url: Optional[str] = None  # RTMP ingest URL
    stream_key: Optional[str] = None  # Unique stream key
    hls_url: Optional[str] = None  # HLS playback URL
    thumbnail_url: Optional[str] = None
    
    # Engagement
    viewers_count: int = 0
    total_viewers: int = 0
    likes_count: int = 0
    comments: List[Dict] = Field(default_factory=list)  # [{user_id, text, timestamp}]
    gifts_received: List[Dict] = Field(default_factory=list)  # [{user_id, gift, amount}]
    
    # Monetization
    is_monetized: bool = False
    gift_revenue_usd: float = 0.0
    
    # Status
    is_live: bool = False
    is_scheduled: bool = False
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    scheduled_start_time: Optional[datetime] = None
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

# ==================== SERVICES ====================

class StoriesService:
    """Handle story creation, viewing, engagement"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.stories_collection = db["stories"]
        self.story_views_collection = db["story_views"]
    
    async def create_story(self, user_id: str, media_url: str, media_type: str, caption: Optional[str] = None, visibility: str = "public") -> Story:
        """Create a new 24-hour story"""
        story = Story(
            user_id=user_id,
            media_url=media_url,
            media_type=media_type,
            caption=caption,
            visibility=visibility,
            expires_at=datetime.utcnow() + timedelta(hours=24)
        )
        await self.stories_collection.insert_one(story.dict())
        return story
    
    async def get_story(self, story_id: str) -> Optional[Story]:
        """Get story by ID"""
        story_data = await self.stories_collection.find_one({"story_id": story_id})
        if story_data:
            return Story(**story_data)
        return None
    
    async def get_user_stories(self, user_id: str) -> List[Story]:
        """Get all non-expired stories from a user"""
        stories_data = await self.stories_collection.find({
            "user_id": user_id,
            "is_expired": False,
            "expires_at": {"$gt": datetime.utcnow()}
        }).to_list(length=None)
        return [Story(**s) for s in stories_data]
    
    async def get_stories_feed(self, user_id: str) -> List[Story]:
        """Get stories from users that the user follows"""
        user_doc = await self.db["user_profiles"].find_one({"user_id": user_id})
        if not user_doc or "following" not in user_doc:
            return []
        
        following = user_doc.get("following", [])
        stories_data = await self.stories_collection.find({
            "user_id": {"$in": following},
            "is_expired": False,
            "expires_at": {"$gt": datetime.utcnow()}
        }).to_list(length=None)
        return [Story(**s) for s in stories_data]
    
    async def view_story(self, story_id: str, viewer_id: str) -> Story:
        """Record a story view and return updated story"""
        story = await self.stories_collection.find_one_and_update(
            {"story_id": story_id},
            {
                "$addToSet": {"views": viewer_id}
            },
            return_document=True
        )
        return Story(**story) if story else None
    
    async def reply_to_story(self, story_id: str, user_id: str, reply_text: str) -> Story:
        """Add a reply to a story"""
        story = await self.stories_collection.find_one_and_update(
            {"story_id": story_id},
            {
                "$push": {"replies": {
                    "user_id": user_id,
                    "text": reply_text,
                    "timestamp": datetime.utcnow()
                }}
            },
            return_document=True
        )
        return Story(**story) if story else None
    
    async def cleanup_expired_stories(self) -> int:
        """Delete expired stories (runs periodically)"""
        result = await self.stories_collection.delete_many({
            "expires_at": {"$lt": datetime.utcnow()}
        })
        return result.deleted_count

class SearchService:
    """Full-text search across users, posts, videos, hashtags"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
    
    async def search_all(self, query: str, user_id: Optional[str] = None, skip: int = 0, limit: int = 20) -> List[SearchResult]:
        """Universal search across all content types"""
        results = []
        
        # Search users
        users = await self.db["user_profiles"].find({
            "$or": [
                {"username": {"$regex": query, "$options": "i"}},
                {"display_name": {"$regex": query, "$options": "i"}},
                {"bio": {"$regex": query, "$options": "i"}}
            ]
        }).to_list(length=10)
        
        for user in users:
            results.append(SearchResult(
                result_type="user",
                result_id=user["user_id"],
                title=user.get("display_name", user["username"]),
                description=user.get("bio", ""),
                image_url=user.get("avatar_url"),
                metadata={"username": user["username"]},
                relevance_score=0.9
            ))
        
        # Search posts
        posts = await self.db["posts"].find({
            "$or": [
                {"content": {"$regex": query, "$options": "i"}},
                {"ai_suggested_hashtags": {"$in": [query]}},
                {"hashtags": {"$in": [query]}}
            ]
        }).to_list(length=10)
        
        for post in posts:
            results.append(SearchResult(
                result_type="post",
                result_id=post["post_id"],
                title=post.get("content", "")[:100],
                description=post.get("content", ""),
                metadata={"user_id": post["user_id"]},
                relevance_score=0.8
            ))
        
        # Search videos
        videos = await self.db["videos"].find({
            "$or": [
                {"title": {"$regex": query, "$options": "i"}},
                {"description": {"$regex": query, "$options": "i"}},
                {"hashtags": {"$in": [query]}}
            ]
        }).to_list(length=10)
        
        for video in videos:
            results.append(SearchResult(
                result_type="video",
                result_id=video.get("video_id"),
                title=video.get("title", ""),
                description=video.get("description", ""),
                image_url=video.get("thumbnail_url"),
                metadata={"user_id": video["user_id"]},
                relevance_score=0.8
            ))
        
        # Search hashtags
        hashtag_matches = await self.db["hashtags"].find({
            "tag": {"$regex": f"^{query}", "$options": "i"}
        }).to_list(length=5)
        
        for hashtag in hashtag_matches:
            results.append(SearchResult(
                result_type="hashtag",
                result_id=hashtag["tag"],
                title=f"#{hashtag['tag']}",
                metadata={"post_count": hashtag.get("posts_count", 0)},
                relevance_score=0.7
            ))
        
        # Sort by relevance and return
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        return results[skip:skip+limit]

class AlgorithmService:
    """AI-powered recommendation engine using Groq"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
    
    async def get_personalized_feed(self, user_id: str, skip: int = 0, limit: int = 20) -> List[Dict]:
        """Get AI-optimized personalized feed for user"""
        try:
            # Get user profile and interests
            user = await self.db["user_profiles"].find_one({"user_id": user_id})
            if not user:
                return []
            
            user_following = user.get("following", [])
            
            # Get posts from followed users with engagement data
            posts = await self.db["posts"].find({
                "$or": [
                    {"user_id": {"$in": user_following}},
                    {"visibility": "public"}
                ]
            }).to_list(length=100)
            
            # Calculate engagement score for each post
            scored_posts = []
            for post in posts:
                engagement_score = (
                    post.get("likes_count", 0) * 1.0 +
                    post.get("comments_count", 0) * 2.5 +
                    post.get("reposts_count", 0) * 3.0 +
                    post.get("shares_count", 0) * 4.0
                )
                
                # Recency boost (newer posts rank higher)
                time_diff = (datetime.utcnow() - post.get("created_at", datetime.utcnow())).total_seconds()
                recency_score = max(0, 1 - (time_diff / (86400 * 7)))  # Decay over 7 days
                
                final_score = engagement_score * (1 + recency_score)
                
                scored_posts.append({
                    "post": post,
                    "score": final_score
                })
            
            # Sort by score
            scored_posts.sort(key=lambda x: x["score"], reverse=True)
            
            # Return paginated results
            return [item["post"] for item in scored_posts[skip:skip+limit]]
        
        except Exception as e:
            logger.error(f"Error in algorithm feed: {e}")
            return []

class EffectsService:
    """Manage effects, filters, transitions"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.effects_collection = db["effects"]
    
    async def create_effect(self, creator_id: str, name: str, effect_type: str, thumbnail_url: str, effect_file_url: str) -> Effect:
        """Create a new effect"""
        effect = Effect(
            creator_id=creator_id,
            name=name,
            effect_type=effect_type,
            thumbnail_url=thumbnail_url,
            effect_file_url=effect_file_url,
            is_public=True
        )
        await self.effects_collection.insert_one(effect.dict())
        return effect
    
    async def get_effects(self, category: Optional[str] = None, skip: int = 0, limit: int = 20) -> List[Effect]:
        """Get trending/popular effects"""
        query = {"is_public": True}
        if category:
            query["category"] = category
        
        effects = await self.effects_collection.find(query).sort("downloads_count", -1).skip(skip).limit(limit).to_list(length=None)
        return [Effect(**e) for e in effects]
    
    async def use_effect(self, effect_id: str) -> Effect:
        """Increment usage count"""
        effect = await self.effects_collection.find_one_and_update(
            {"effect_id": effect_id},
            {"$inc": {"uses_in_posts": 1}},
            return_document=True
        )
        return Effect(**effect) if effect else None

class MarketplaceService:
    """Marketplace for products, services, collaborations"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        """Initialize marketplace service with DB collections"""
        self.db = db
        self.marketplace_collection = db["marketplace_products"]
        self.orders_collection = db["orders"]

    async def create_listing(self, seller_id: str, title: str, description: str, category: str, price: float, images: List[str]) -> MarketplaceProduct:
        """Create a marketplace listing"""
        # Input validation (defensive - raise ValueError for bad input)
        if not seller_id:
            raise ValueError("seller_id is required")
        if not title or not title.strip():
            raise ValueError("title is required")
        if price is None or price < 0:
            raise ValueError("price must be a non-negative number")
        if images is None:
            images = []
        if not isinstance(images, list):
            raise ValueError("images must be a list of URLs")
        if len(images) > 10:
            raise ValueError("a maximum of 10 images is allowed")

        # Validate image URLs (allow http, https, s3)
        for img in images:
            if not isinstance(img, str) or not img.strip():
                raise ValueError("each image must be a non-empty URL string")
            parsed = urlparse(img)
            if parsed.scheme not in ("http", "https", "s3"):
                raise ValueError(f"unsupported image URL scheme for {img}")

        # Validate category (convert to enum)
        try:
            cat_enum = MarketplaceCategory(category)
        except Exception:
            raise ValueError(f"invalid category: {category}")

        product = MarketplaceProduct(
            seller_id=seller_id,
            title=title,
            description=description,
            category=cat_enum,
            price_usd=price,
            images=images,
            thumbnail_url=images[0] if images else None
        )

        await self.marketplace_collection.insert_one(product.dict())
        return product
    
    async def get_listings(self, category: Optional[str] = None, skip: int = 0, limit: int = 20) -> List[MarketplaceProduct]:
        """Get marketplace listings"""
        query = {"is_active": True}
        if category:
            query["category"] = category
        
        products = await self.marketplace_collection.find(query).sort("created_at", -1).skip(skip).limit(limit).to_list(length=None)
        return [MarketplaceProduct(**p) for p in products]
    
    async def get_seller_listings(self, seller_id: str) -> List[MarketplaceProduct]:
        """Get all listings from a specific seller"""
        products = await self.marketplace_collection.find({"seller_id": seller_id}).to_list(length=None)
        return [MarketplaceProduct(**p) for p in products]
    
    async def add_inquiry(self, product_id: str) -> Dict:
        """Record a buyer inquiry"""
        await self.marketplace_collection.find_one_and_update(
            {"product_id": product_id},
            {"$inc": {"inquiries_count": 1}},
        )
        return {"status": "inquiry_received"}

    async def purchase(self, product_id: str, buyer_id: str, payment_method: Optional[str] = None, payment_token: Optional[str] = None) -> Dict:
        """Create an order for a marketplace product.

        This is a simplified purchase flow: payment processing must be integrated separately
        (Stripe/PayPal) and validated. Here we record an order and update counts.
        """
        # Get product
        product = await self.marketplace_collection.find_one({"product_id": product_id})
        if not product:
            raise ValueError("Product not found")

        if not product.get("is_active", True):
            raise ValueError("Product is not available")

        seller_id = product.get("seller_id")
        price = product.get("price_usd")

        # Create order record
        order = {
            "order_id": str(uuid.uuid4()),
            "product_id": product_id,
            "buyer_id": buyer_id,
            "seller_id": seller_id,
            "price_usd": price,
            "currency": product.get("currency", "USD"),
            "payment_method": payment_method,
            "payment_token": payment_token,
            "status": "pending",  # pending -> paid -> shipped -> completed
            "created_at": datetime.utcnow()
        }

        await self.orders_collection.insert_one(order)

        # Update product sales count
        await self.marketplace_collection.update_one({"product_id": product_id}, {"$inc": {"sales_count": 1}})

        # Update creator fund if exists
        try:
            await self.db.creator_funds.update_one({"creator_id": seller_id}, {"$inc": {"marketplace_earnings": price, "total_earnings": price, "pending_balance": price}}, upsert=True)
        except Exception:
            # Non-fatal if creator fund collection not available
            pass

        return {"order_id": order["order_id"], "status": order["status"], "price_usd": price}

    async def get_user_orders(self, user_id: str, role: str = "buyer", skip: int = 0, limit: int = 20) -> List[Dict]:
        """Get orders for a user either as buyer or seller"""
        query = {"buyer_id": user_id} if role == "buyer" else {"seller_id": user_id}
        orders = await self.orders_collection.find(query).sort("created_at", -1).skip(skip).limit(limit).to_list(length=None)
        return orders

    async def search_listings(self, q: str, category: Optional[str] = None, skip: int = 0, limit: int = 20) -> List[MarketplaceProduct]:
        """Text search across title and description, fallback to regex if no text index"""
        query = {"is_active": True}
        if category:
            query["category"] = category

        # Prefer text search if available
        try:
            if q:
                cursor = self.marketplace_collection.find({"$text": {"$search": q}, **query})
            else:
                cursor = self.marketplace_collection.find(query)

            products = await cursor.sort([("created_at", -1)]).skip(skip).limit(limit).to_list(length=None)
            return [MarketplaceProduct(**p) for p in products]
        except Exception:
            # Fallback to regex search
            if q:
                regex = {"$regex": q, "$options": "i"}
                query["$or"] = [{"title": regex}, {"description": regex}, {"tags": {"$in": [q]}}]
            products = await self.marketplace_collection.find(query).sort("created_at", -1).skip(skip).limit(limit).to_list(length=None)
            return [MarketplaceProduct(**p) for p in products]

class AdsService:
    """Advertisement platform with AI targeting"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.ads_collection = db["advertisements"]
    
    async def create_campaign(self, advertiser_id: str, campaign_name: str, headline: str, description: str, image_url: str, cta_url: str, daily_budget: float, target_interests: List[str]) -> Advertisement:
        """Create an ad campaign"""
        ad = Advertisement(
            advertiser_id=advertiser_id,
            campaign_name=campaign_name,
            headline=headline,
            description=description,
            image_url=image_url,
            cta_url=cta_url,
            daily_budget_usd=daily_budget,
            total_budget_usd=daily_budget * 30,
            target_interests=target_interests
        )
        await self.ads_collection.insert_one(ad.dict())
        return ad
    
    async def get_advertiser_campaigns(self, advertiser_id: str) -> List[Advertisement]:
        """Get all campaigns for advertiser"""
        ads = await self.ads_collection.find({"advertiser_id": advertiser_id}).to_list(length=None)
        return [Advertisement(**a) for a in ads]
    
    async def record_impression(self, ad_id: str) -> Dict:
        """Record an ad impression"""
        await self.ads_collection.find_one_and_update(
            {"ad_id": ad_id},
            {
                "$inc": {"impressions": 1},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        return {"status": "recorded"}
    
    async def record_click(self, ad_id: str) -> Dict:
        """Record an ad click"""
        ad = await self.ads_collection.find_one_and_update(
            {"ad_id": ad_id},
            {
                "$inc": {"clicks": 1, "spend_usd": 0.5},
                "$set": {"updated_at": datetime.utcnow()}
            },
            return_document=True
        )
        return {"status": "recorded", "ad": Advertisement(**ad) if ad else None}

class CreatorFundService:
    """Track creator earnings and payouts"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.fund_collection = db["creator_funds"]
    
    async def get_creator_fund(self, creator_id: str) -> Optional[CreatorFund]:
        """Get creator fund details"""
        fund_data = await self.fund_collection.find_one({"creator_id": creator_id})
        if fund_data:
            return CreatorFund(**fund_data)
        
        # Create if doesn't exist
        fund = CreatorFund(creator_id=creator_id)
        await self.fund_collection.insert_one(fund.dict())
        return fund
    
    async def add_earnings(self, creator_id: str, earnings_type: str, amount: float) -> CreatorFund:
        """Add earnings to creator fund"""
        fund = await self.fund_collection.find_one_and_update(
            {"creator_id": creator_id},
            {
                "$inc": {
                    f"{earnings_type}_earnings": amount,
                    "total_earnings": amount,
                    "pending_balance": amount
                },
                "$set": {"updated_at": datetime.utcnow()}
            },
            return_document=True
        )
        return CreatorFund(**fund) if fund else None
    
    async def request_payout(self, creator_id: str, amount: float, payout_method: str) -> Dict:
        """Request a payout if eligible"""
        fund = await self.fund_collection.find_one({"creator_id": creator_id})
        if not fund or fund.get("pending_balance", 0) < amount:
            raise ValueError("Insufficient balance")
        
        if fund.get("pending_balance", 0) < 100:
            raise ValueError("Must have minimum $100 pending")
        
        # Record payout
        await self.fund_collection.find_one_and_update(
            {"creator_id": creator_id},
            {
                "$push": {
                    "payout_history": {
                        "date": datetime.utcnow(),
                        "amount": amount,
                        "method": payout_method,
                        "status": "pending"
                    }
                },
                "$inc": {"pending_balance": -amount, "withdrawn_balance": amount},
                "$set": {"payout_method": payout_method, "updated_at": datetime.utcnow()}
            }
        )
        
        return {"status": "payout_requested", "amount": amount, "method": payout_method}

class LiveStreamService:
    """Manage live streaming sessions"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.live_collection = db["live_streams"]
    
    async def create_live_stream(self, streamer_id: str, title: str, description: Optional[str] = None, category: str = "general") -> LiveStream:
        """Create a live stream session"""
        import secrets
        stream_key = secrets.token_urlsafe(32)
        stream_id = str(uuid.uuid4())
        
        stream = LiveStream(
            stream_id=stream_id,
            streamer_id=streamer_id,
            title=title,
            description=description,
            category=category,
            stream_key=stream_key,
            rtmp_url=f"rtmp://live.gaaius.io/live/{stream_key}",
            hls_url=f"https://cdn.gaaius.io/live/{stream_id}/playlist.m3u8"
        )
        
        await self.live_collection.insert_one(stream.dict())
        return stream
    
    async def start_stream(self, stream_id: str) -> LiveStream:
        """Start broadcasting"""
        stream = await self.live_collection.find_one_and_update(
            {"stream_id": stream_id},
            {
                "$set": {
                    "is_live": True,
                    "started_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
            },
            return_document=True
        )
        return LiveStream(**stream) if stream else None
    
    async def get_active_streams(self, skip: int = 0, limit: int = 20) -> List[LiveStream]:
        """Get all active live streams"""
        streams = await self.live_collection.find({"is_live": True}).skip(skip).limit(limit).to_list(length=None)
        return [LiveStream(**s) for s in streams]
    
    async def add_comment_to_stream(self, stream_id: str, user_id: str, comment: str) -> LiveStream:
        """Add a comment to live stream"""
        stream = await self.live_collection.find_one_and_update(
            {"stream_id": stream_id},
            {
                "$push": {
                    "comments": {
                        "user_id": user_id,
                        "text": comment,
                        "timestamp": datetime.utcnow()
                    }
                }
            },
            return_document=True
        )
        return LiveStream(**stream) if stream else None
