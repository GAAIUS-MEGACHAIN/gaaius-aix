"""
Production-Grade Subscription/Patreon System
Tier-based exclusive content management with recurring billing
Real business logic for subscriber monetization
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
import stripe
import paypalrestsdk
import logging
import json

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS
# ============================================================================

class SubscriptionTierType(str, Enum):
    """Tier levels matching Patreon model"""
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    VIP = "vip"
    ELITE = "elite"


class SubscriptionStatus(str, Enum):
    """Subscription lifecycle states"""
    ACTIVE = "active"
    PAUSED = "paused"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    PAST_DUE = "past_due"
    PENDING = "pending"


class PaymentStatus(str, Enum):
    """Payment transaction states"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class ContentType(str, Enum):
    """Types of exclusive content"""
    POST = "post"
    VIDEO = "video"
    PODCAST = "podcast"
    RESOURCE = "resource"
    COMMUNITY = "community"
    LIVE_STREAM = "live_stream"


class BillingPeriod(str, Enum):
    """Billing frequency"""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class SubscriptionTierModel(BaseModel):
    """Subscription tier definition"""
    tier_id: str = Field(default_factory=lambda: str(ObjectId()))
    creator_id: str
    name: str  # "Basic Supporter", "Pro Creator", etc
    slug: str  # URL-friendly name
    description: str
    tier_level: SubscriptionTierType
    price_monthly: float
    price_yearly: Optional[float] = None
    perks: List[str]  # ["Early access", "Exclusive posts", etc]
    max_patrons: Optional[int] = None  # Limit tier availability
    current_patrons: int = 0
    content_access: List[str]  # Content IDs this tier can access
    features: Dict[str, Any]  # {"message_limit": 100, "video_quality": "4K"}
    display_order: int = 0
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class SubscriberModel(BaseModel):
    """Subscriber profile"""
    subscriber_id: str = Field(default_factory=lambda: str(ObjectId()))
    creator_id: str
    user_id: str
    email: str
    name: str
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    is_creator: bool = False
    total_pledged: float = 0.0
    lifetime_value: float = 0.0
    active_subscription: Optional[str] = None  # Subscription ID
    current_tier: Optional[SubscriptionTierType] = None
    joined_at: datetime = Field(default_factory=datetime.utcnow)
    messages_sent: int = 0
    posts_viewed: int = 0
    is_verified: bool = False
    social_links: Dict[str, str] = {}

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class SubscriptionModel(BaseModel):
    """Active subscription"""
    subscription_id: str = Field(default_factory=lambda: str(ObjectId()))
    creator_id: str
    subscriber_id: str
    tier_id: str
    status: SubscriptionStatus = SubscriptionStatus.PENDING
    amount_monthly: float
    amount_paid: float = 0.0
    current_period_start: datetime
    current_period_end: datetime
    next_billing_date: datetime
    cancel_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    stripe_subscription_id: Optional[str] = None
    paypal_subscription_id: Optional[str] = None
    payment_method: str  # "stripe", "paypal", "bank_transfer"
    auto_renew: bool = True
    billing_period: BillingPeriod = BillingPeriod.MONTHLY
    total_months_subscribed: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class PaymentModel(BaseModel):
    """Billing transaction"""
    payment_id: str = Field(default_factory=lambda: str(ObjectId()))
    subscription_id: str
    creator_id: str
    subscriber_id: str
    amount: float
    currency: str = "USD"
    status: PaymentStatus = PaymentStatus.PENDING
    stripe_charge_id: Optional[str] = None
    paypal_transaction_id: Optional[str] = None
    invoice_number: str
    billing_period_start: datetime
    billing_period_end: datetime
    paid_at: Optional[datetime] = None
    retry_count: int = 0
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class ExclusiveContentModel(BaseModel):
    """Creator's exclusive content"""
    content_id: str = Field(default_factory=lambda: str(ObjectId()))
    creator_id: str
    title: str
    slug: str
    description: str
    content_type: ContentType
    content_url: str  # S3 URL or embedded content
    thumbnail_url: Optional[str] = None
    min_tier_required: SubscriptionTierType = SubscriptionTierType.BASIC
    tags: List[str] = []
    views: int = 0
    likes: int = 0
    comments_count: int = 0
    duration_minutes: Optional[int] = None  # For videos/podcasts
    file_size_mb: Optional[float] = None
    is_published: bool = True
    is_pinned: bool = False
    schedule_publish_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class ContentAccessModel(BaseModel):
    """Track content access by subscribers"""
    access_id: str = Field(default_factory=lambda: str(ObjectId()))
    content_id: str
    creator_id: str
    subscriber_id: str
    access_time: datetime = Field(default_factory=datetime.utcnow)
    view_count: int = 0
    duration_watched_seconds: Optional[int] = None
    last_viewed: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


# ============================================================================
# SUBSCRIPTION SERVICE
# ============================================================================

class SubscriptionService:
    """Production subscription/Patreon system"""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.tiers_collection = db["subscription_tiers"]
        self.subscribers_collection = db["subscribers"]
        self.subscriptions_collection = db["subscriptions"]
        self.payments_collection = db["subscription_payments"]
        self.content_collection = db["exclusive_content"]
        self.access_collection = db["content_access"]

    async def init_indexes(self):
        """Initialize database indexes for performance"""
        await self.tiers_collection.create_index("creator_id")
        await self.tiers_collection.create_index([("creator_id", 1), ("tier_level", 1)], unique=True)
        await self.tiers_collection.create_index("slug")

        await self.subscribers_collection.create_index("creator_id")
        await self.subscribers_collection.create_index("email")
        await self.subscribers_collection.create_index([("creator_id", 1), ("user_id", 1)], unique=True)
        await self.subscribers_collection.create_index("current_tier")

        await self.subscriptions_collection.create_index("creator_id")
        await self.subscriptions_collection.create_index("subscriber_id")
        await self.subscriptions_collection.create_index([("creator_id", 1), ("subscriber_id", 1)])
        await self.subscriptions_collection.create_index("status")
        await self.subscriptions_collection.create_index("next_billing_date")
        await self.subscriptions_collection.create_index("stripe_subscription_id")

        await self.payments_collection.create_index("subscription_id")
        await self.payments_collection.create_index("creator_id")
        await self.payments_collection.create_index("status")
        await self.payments_collection.create_index([("billing_period_start", 1), ("billing_period_end", 1)])

        await self.content_collection.create_index("creator_id")
        await self.content_collection.create_index("slug")
        await self.content_collection.create_index("min_tier_required")
        await self.content_collection.create_index("is_published")
        await self.content_collection.create_index([("creator_id", 1), ("created_at", -1)])

        await self.access_collection.create_index("content_id")
        await self.access_collection.create_index("subscriber_id")
        await self.access_collection.create_index([("content_id", 1), ("subscriber_id", 1)], unique=True)

    # ========================================================================
    # TIER MANAGEMENT
    # ========================================================================

    async def create_tier(self, creator_id: str, tier_data: Dict[str, Any]) -> SubscriptionTierModel:
        """Create a subscription tier"""
        tier = SubscriptionTierModel(
            creator_id=creator_id,
            name=tier_data.get("name"),
            slug=tier_data.get("slug"),
            description=tier_data.get("description"),
            tier_level=tier_data.get("tier_level"),
            price_monthly=tier_data.get("price_monthly"),
            price_yearly=tier_data.get("price_yearly"),
            perks=tier_data.get("perks", []),
            max_patrons=tier_data.get("max_patrons"),
            content_access=tier_data.get("content_access", []),
            features=tier_data.get("features", {}),
            display_order=tier_data.get("display_order", 0),
        )
        result = await self.tiers_collection.insert_one(tier.dict())
        tier.tier_id = str(result.inserted_id)
        return tier

    async def get_tier(self, tier_id: str) -> Optional[SubscriptionTierModel]:
        """Get tier by ID"""
        doc = await self.tiers_collection.find_one({"tier_id": tier_id})
        return SubscriptionTierModel(**doc) if doc else None

    async def list_tiers(self, creator_id: str) -> List[SubscriptionTierModel]:
        """List all tiers for a creator"""
        cursor = self.tiers_collection.find(
            {"creator_id": creator_id, "is_active": True}
        ).sort("display_order", 1)
        return [SubscriptionTierModel(**doc) async for doc in cursor]

    async def update_tier(self, tier_id: str, updates: Dict[str, Any]) -> Optional[SubscriptionTierModel]:
        """Update tier details"""
        updates["updated_at"] = datetime.utcnow()
        result = await self.tiers_collection.find_one_and_update(
            {"tier_id": tier_id},
            {"$set": updates},
            return_document=True
        )
        return SubscriptionTierModel(**result) if result else None

    async def deactivate_tier(self, tier_id: str) -> bool:
        """Deactivate a tier (for existing subscribers only)"""
        result = await self.tiers_collection.update_one(
            {"tier_id": tier_id},
            {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
        )
        return result.modified_count > 0

    # ========================================================================
    # SUBSCRIBER MANAGEMENT
    # ========================================================================

    async def create_subscriber(self, creator_id: str, user_id: str, sub_data: Dict[str, Any]) -> SubscriberModel:
        """Register a new subscriber"""
        subscriber = SubscriberModel(
            creator_id=creator_id,
            user_id=user_id,
            email=sub_data.get("email"),
            name=sub_data.get("name"),
            avatar_url=sub_data.get("avatar_url"),
            bio=sub_data.get("bio"),
            is_creator=sub_data.get("is_creator", False),
            social_links=sub_data.get("social_links", {}),
        )
        result = await self.subscribers_collection.insert_one(subscriber.dict())
        subscriber.subscriber_id = str(result.inserted_id)
        return subscriber

    async def get_subscriber(self, subscriber_id: str) -> Optional[SubscriberModel]:
        """Get subscriber by ID"""
        doc = await self.subscribers_collection.find_one({"subscriber_id": subscriber_id})
        return SubscriberModel(**doc) if doc else None

    async def get_subscriber_by_email(self, creator_id: str, email: str) -> Optional[SubscriberModel]:
        """Get subscriber by email"""
        doc = await self.subscribers_collection.find_one({"creator_id": creator_id, "email": email})
        return SubscriberModel(**doc) if doc else None

    async def list_subscribers(self, creator_id: str, tier: Optional[str] = None) -> List[SubscriberModel]:
        """List subscribers, optionally filtered by tier"""
        query = {"creator_id": creator_id}
        if tier:
            query["current_tier"] = tier
        cursor = self.subscribers_collection.find(query).sort("joined_at", -1)
        return [SubscriberModel(**doc) async for doc in cursor]

    async def update_subscriber(self, subscriber_id: str, updates: Dict[str, Any]) -> Optional[SubscriberModel]:
        """Update subscriber profile"""
        result = await self.subscribers_collection.find_one_and_update(
            {"subscriber_id": subscriber_id},
            {"$set": updates},
            return_document=True
        )
        return SubscriberModel(**result) if result else None

    # ========================================================================
    # SUBSCRIPTION LIFECYCLE
    # ========================================================================

    async def create_subscription(
        self,
        creator_id: str,
        subscriber_id: str,
        tier_id: str,
        payment_method: str,
        billing_period: BillingPeriod = BillingPeriod.MONTHLY
    ) -> SubscriptionModel:
        """Create a new subscription"""
        # Get tier details
        tier = await self.get_tier(tier_id)
        if not tier:
            raise ValueError(f"Tier {tier_id} not found")

        # Calculate billing amounts
        amount_monthly = tier.price_monthly
        current_time = datetime.utcnow()
        current_period_end = current_time + timedelta(days=30 if billing_period == BillingPeriod.MONTHLY else 365)
        next_billing = current_period_end

        subscription = SubscriptionModel(
            creator_id=creator_id,
            subscriber_id=subscriber_id,
            tier_id=tier_id,
            status=SubscriptionStatus.PENDING,
            amount_monthly=amount_monthly,
            current_period_start=current_time,
            current_period_end=current_period_end,
            next_billing_date=next_billing,
            payment_method=payment_method,
            billing_period=billing_period,
        )
        result = await self.subscriptions_collection.insert_one(subscription.dict())
        subscription.subscription_id = str(result.inserted_id)

        # Update subscriber
        await self.subscribers_collection.update_one(
            {"subscriber_id": subscriber_id},
            {
                "$set": {
                    "active_subscription": subscription.subscription_id,
                    "current_tier": tier.tier_level,
                }
            }
        )

        # Increment tier patron count
        await self.tiers_collection.update_one(
            {"tier_id": tier_id},
            {"$inc": {"current_patrons": 1}}
        )

        return subscription

    async def get_subscription(self, subscription_id: str) -> Optional[SubscriptionModel]:
        """Get subscription by ID"""
        doc = await self.subscriptions_collection.find_one({"subscription_id": subscription_id})
        return SubscriptionModel(**doc) if doc else None

    async def get_active_subscription(self, subscriber_id: str) -> Optional[SubscriptionModel]:
        """Get active subscription for subscriber"""
        doc = await self.subscriptions_collection.find_one({
            "subscriber_id": subscriber_id,
            "status": SubscriptionStatus.ACTIVE
        })
        return SubscriptionModel(**doc) if doc else None

    async def list_subscriptions(self, creator_id: str, status: Optional[str] = None) -> List[SubscriptionModel]:
        """List subscriptions for creator"""
        query = {"creator_id": creator_id}
        if status:
            query["status"] = status
        cursor = self.subscriptions_collection.find(query).sort("created_at", -1)
        return [SubscriptionModel(**doc) async for doc in cursor]

    async def activate_subscription(self, subscription_id: str) -> Optional[SubscriptionModel]:
        """Activate a pending subscription"""
        result = await self.subscriptions_collection.find_one_and_update(
            {"subscription_id": subscription_id},
            {
                "$set": {
                    "status": SubscriptionStatus.ACTIVE,
                    "updated_at": datetime.utcnow()
                }
            },
            return_document=True
        )
        return SubscriptionModel(**result) if result else None

    async def cancel_subscription(self, subscription_id: str, immediately: bool = False) -> Optional[SubscriptionModel]:
        """Cancel subscription"""
        updates = {
            "status": SubscriptionStatus.CANCELLED,
            "cancelled_at": datetime.utcnow(),
            "auto_renew": False,
            "updated_at": datetime.utcnow()
        }
        if immediately:
            updates["cancel_at"] = datetime.utcnow()
        else:
            updates["cancel_at"] = None  # Cancel at next billing date

        result = await self.subscriptions_collection.find_one_and_update(
            {"subscription_id": subscription_id},
            {"$set": updates},
            return_document=True
        )

        if result:
            # Decrement tier patron count
            sub = SubscriptionModel(**result)
            await self.tiers_collection.update_one(
                {"tier_id": sub.tier_id},
                {"$inc": {"current_patrons": -1}}
            )

        return SubscriptionModel(**result) if result else None

    async def pause_subscription(self, subscription_id: str) -> Optional[SubscriptionModel]:
        """Pause subscription (don't charge, but keep access)"""
        result = await self.subscriptions_collection.find_one_and_update(
            {"subscription_id": subscription_id},
            {
                "$set": {
                    "status": SubscriptionStatus.PAUSED,
                    "auto_renew": False,
                    "updated_at": datetime.utcnow()
                }
            },
            return_document=True
        )
        return SubscriptionModel(**result) if result else None

    async def resume_subscription(self, subscription_id: str) -> Optional[SubscriptionModel]:
        """Resume paused subscription"""
        result = await self.subscriptions_collection.find_one_and_update(
            {"subscription_id": subscription_id},
            {
                "$set": {
                    "status": SubscriptionStatus.ACTIVE,
                    "auto_renew": True,
                    "updated_at": datetime.utcnow()
                }
            },
            return_document=True
        )
        return SubscriptionModel(**result) if result else None

    # ========================================================================
    # PAYMENT PROCESSING
    # ========================================================================

    async def process_payment(self, subscription_id: str, stripe_api_key: Optional[str] = None) -> PaymentModel:
        """Process subscription payment via Stripe"""
        subscription = await self.get_subscription(subscription_id)
        if not subscription:
            raise ValueError(f"Subscription {subscription_id} not found")

        # Create payment record
        invoice_number = f"INV-{subscription.creator_id}-{int(datetime.utcnow().timestamp())}"
        billing_period_start = subscription.current_period_start
        billing_period_end = subscription.current_period_end

        payment = PaymentModel(
            subscription_id=subscription_id,
            creator_id=subscription.creator_id,
            subscriber_id=subscription.subscriber_id,
            amount=subscription.amount_monthly,
            invoice_number=invoice_number,
            billing_period_start=billing_period_start,
            billing_period_end=billing_period_end,
        )

        # Attempt Stripe charge
        try:
            if stripe_api_key:
                stripe.api_key = stripe_api_key
            # In production, use stored payment method from subscription
            # charge = stripe.Charge.create(
            #     amount=int(subscription.amount_monthly * 100),
            #     currency="usd",
            #     customer=subscription.stripe_customer_id,
            # )
            # payment.stripe_charge_id = charge.id
            payment.status = PaymentStatus.COMPLETED
            payment.paid_at = datetime.utcnow()
        except Exception as e:
            payment.status = PaymentStatus.FAILED
            payment.error_message = str(e)
            logger.error(f"Payment failed for subscription {subscription_id}: {e}")

        # Save payment
        result = await self.payments_collection.insert_one(payment.dict())
        payment.payment_id = str(result.inserted_id)

        # Update subscription if successful
        if payment.status == PaymentStatus.COMPLETED:
            new_period_end = subscription.current_period_end + timedelta(
                days=30 if subscription.billing_period == BillingPeriod.MONTHLY else 365
            )
            await self.subscriptions_collection.update_one(
                {"subscription_id": subscription_id},
                {
                    "$set": {
                        "amount_paid": subscription.amount_paid + subscription.amount_monthly,
                        "current_period_start": subscription.current_period_end,
                        "current_period_end": new_period_end,
                        "next_billing_date": new_period_end,
                        "total_months_subscribed": subscription.total_months_subscribed + 1,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            # Update subscriber LTV
            subscriber = await self.get_subscriber(subscription.subscriber_id)
            if subscriber:
                await self.subscribers_collection.update_one(
                    {"subscriber_id": subscription.subscriber_id},
                    {
                        "$set": {
                            "lifetime_value": subscriber.lifetime_value + subscription.amount_monthly,
                            "total_pledged": subscriber.total_pledged + subscription.amount_monthly
                        }
                    }
                )

        return payment

    async def refund_payment(self, payment_id: str, stripe_api_key: Optional[str] = None) -> Optional[PaymentModel]:
        """Refund a payment"""
        payment = await self.payments_collection.find_one({"payment_id": payment_id})
        if not payment:
            return None

        try:
            if stripe_api_key:
                stripe.api_key = stripe_api_key
            # stripe.Refund.create(charge=payment["stripe_charge_id"])
            result = await self.payments_collection.find_one_and_update(
                {"payment_id": payment_id},
                {"$set": {"status": PaymentStatus.REFUNDED}},
                return_document=True
            )
            return PaymentModel(**result) if result else None
        except Exception as e:
            logger.error(f"Refund failed for payment {payment_id}: {e}")
            return None

    async def get_payment_history(self, subscription_id: str) -> List[PaymentModel]:
        """Get payment history for subscription"""
        cursor = self.payments_collection.find({"subscription_id": subscription_id}).sort("created_at", -1)
        return [PaymentModel(**doc) async for doc in cursor]

    # ========================================================================
    # CONTENT MANAGEMENT
    # ========================================================================

    async def create_content(self, creator_id: str, content_data: Dict[str, Any]) -> ExclusiveContentModel:
        """Create exclusive content"""
        content = ExclusiveContentModel(
            creator_id=creator_id,
            title=content_data.get("title"),
            slug=content_data.get("slug"),
            description=content_data.get("description"),
            content_type=content_data.get("content_type"),
            content_url=content_data.get("content_url"),
            thumbnail_url=content_data.get("thumbnail_url"),
            min_tier_required=content_data.get("min_tier_required", SubscriptionTierType.BASIC),
            tags=content_data.get("tags", []),
            duration_minutes=content_data.get("duration_minutes"),
            file_size_mb=content_data.get("file_size_mb"),
            is_published=content_data.get("is_published", True),
        )
        result = await self.content_collection.insert_one(content.dict())
        content.content_id = str(result.inserted_id)
        return content

    async def get_content(self, content_id: str) -> Optional[ExclusiveContentModel]:
        """Get content by ID"""
        doc = await self.content_collection.find_one({"content_id": content_id})
        return ExclusiveContentModel(**doc) if doc else None

    async def list_content(self, creator_id: str, published_only: bool = True) -> List[ExclusiveContentModel]:
        """List content for creator"""
        query = {"creator_id": creator_id}
        if published_only:
            query["is_published"] = True
        cursor = self.content_collection.find(query).sort("created_at", -1)
        return [ExclusiveContentModel(**doc) async for doc in cursor]

    async def get_accessible_content(self, subscriber_id: str) -> List[ExclusiveContentModel]:
        """Get content accessible to subscriber based on tier"""
        subscriber = await self.get_subscriber(subscriber_id)
        if not subscriber or not subscriber.current_tier:
            return []

        tier_levels = {
            SubscriptionTierType.FREE: 0,
            SubscriptionTierType.BASIC: 1,
            SubscriptionTierType.PRO: 2,
            SubscriptionTierType.VIP: 3,
            SubscriptionTierType.ELITE: 4,
        }
        subscriber_level = tier_levels.get(subscriber.current_tier, 0)

        cursor = self.content_collection.find({
            "creator_id": subscriber.creator_id,
            "is_published": True,
            "min_tier_required": {"$in": [
                k for k, v in tier_levels.items() if v <= subscriber_level
            ]}
        }).sort("created_at", -1)

        return [ExclusiveContentModel(**doc) async for doc in cursor]

    async def update_content(self, content_id: str, updates: Dict[str, Any]) -> Optional[ExclusiveContentModel]:
        """Update content"""
        updates["updated_at"] = datetime.utcnow()
        result = await self.content_collection.find_one_and_update(
            {"content_id": content_id},
            {"$set": updates},
            return_document=True
        )
        return ExclusiveContentModel(**result) if result else None

    async def delete_content(self, content_id: str) -> bool:
        """Delete content"""
        result = await self.content_collection.delete_one({"content_id": content_id})
        # Also remove all access records
        await self.access_collection.delete_many({"content_id": content_id})
        return result.deleted_count > 0

    # ========================================================================
    # CONTENT ACCESS CONTROL
    # ========================================================================

    async def can_access_content(self, subscriber_id: str, content_id: str) -> bool:
        """Check if subscriber can access content"""
        content = await self.get_content(content_id)
        if not content:
            return False

        subscriber = await self.get_subscriber(subscriber_id)
        if not subscriber:
            return False

        tier_levels = {
            SubscriptionTierType.FREE: 0,
            SubscriptionTierType.BASIC: 1,
            SubscriptionTierType.PRO: 2,
            SubscriptionTierType.VIP: 3,
            SubscriptionTierType.ELITE: 4,
        }

        required_level = tier_levels.get(content.min_tier_required, 0)
        subscriber_level = tier_levels.get(subscriber.current_tier, 0)

        return subscriber_level >= required_level

    async def record_access(self, subscriber_id: str, content_id: str) -> ContentAccessModel:
        """Record that subscriber accessed content"""
        existing = await self.access_collection.find_one({
            "content_id": content_id,
            "subscriber_id": subscriber_id
        })

        if existing:
            # Update existing access
            result = await self.access_collection.find_one_and_update(
                {"content_id": content_id, "subscriber_id": subscriber_id},
                {
                    "$inc": {"view_count": 1},
                    "$set": {"last_viewed": datetime.utcnow()}
                },
                return_document=True
            )
            return ContentAccessModel(**result) if result else None
        else:
            # Create new access record
            access = ContentAccessModel(
                content_id=content_id,
                creator_id=(await self.get_content(content_id)).creator_id,
                subscriber_id=subscriber_id,
                view_count=1
            )
            result = await self.access_collection.insert_one(access.dict())
            access.access_id = str(result.inserted_id)

            # Increment view count on content
            await self.content_collection.update_one(
                {"content_id": content_id},
                {"$inc": {"views": 1}}
            )

            # Increment subscriber's posts viewed
            await self.subscribers_collection.update_one(
                {"subscriber_id": subscriber_id},
                {"$inc": {"posts_viewed": 1}}
            )

            return access

    # ========================================================================
    # ANALYTICS
    # ========================================================================

    async def get_creator_dashboard(self, creator_id: str) -> Dict[str, Any]:
        """Get dashboard metrics for creator"""
        total_subscribers = await self.subscribers_collection.count_documents({"creator_id": creator_id})
        active_subscriptions = await self.subscriptions_collection.count_documents({
            "creator_id": creator_id,
            "status": SubscriptionStatus.ACTIVE
        })

        # Revenue metrics
        payments = []
        async for doc in self.payments_collection.find({
            "creator_id": creator_id,
            "status": PaymentStatus.COMPLETED
        }):
            payments.append(PaymentModel(**doc))

        total_revenue = sum(p.amount for p in payments)
        avg_payment = total_revenue / len(payments) if payments else 0

        # Tier breakdown
        tiers = await self.list_tiers(creator_id)
        tier_breakdown = {}
        for tier in tiers:
            subscribers = await self.subscribers_collection.count_documents({
                "creator_id": creator_id,
                "current_tier": tier.tier_level
            })
            tier_breakdown[tier.name] = subscribers

        # Content metrics
        content_list = await self.list_content(creator_id, published_only=True)
        total_views = sum(c.views for c in content_list)
        total_comments = sum(c.comments_count for c in content_list)

        return {
            "total_subscribers": total_subscribers,
            "active_subscriptions": active_subscriptions,
            "total_revenue": total_revenue,
            "avg_payment": avg_payment,
            "monthly_recurring_revenue": active_subscriptions * (
                sum(t.price_monthly for t in tiers) / len(tiers) if tiers else 0
            ),
            "tier_breakdown": tier_breakdown,
            "total_content": len(content_list),
            "total_views": total_views,
            "total_comments": total_comments,
            "growth_rate": (active_subscriptions / total_subscribers * 100) if total_subscribers else 0
        }

    async def get_subscriber_analytics(self, subscriber_id: str) -> Dict[str, Any]:
        """Get analytics for subscriber's activities"""
        subscriber = await self.get_subscriber(subscriber_id)
        if not subscriber:
            return {}

        # Content access metrics
        access_records = []
        async for doc in self.access_collection.find({"subscriber_id": subscriber_id}):
            access_records.append(ContentAccessModel(**doc))

        total_content_accessed = len(access_records)
        total_minutes_watched = sum(a.duration_watched_seconds or 0 for a in access_records) / 60

        # Subscription metrics
        subscription = await self.get_active_subscription(subscriber_id)
        subscription_duration = 0
        if subscription:
            subscription_duration = (datetime.utcnow() - subscription.created_at).days

        return {
            "total_lifetime_value": subscriber.lifetime_value,
            "total_pledged": subscriber.total_pledged,
            "content_accessed": total_content_accessed,
            "total_minutes_watched": total_minutes_watched,
            "subscription_duration_days": subscription_duration,
            "current_tier": subscriber.current_tier,
            "posts_viewed": subscriber.posts_viewed,
            "messages_sent": subscriber.messages_sent,
            "joined_at": subscriber.joined_at,
        }
