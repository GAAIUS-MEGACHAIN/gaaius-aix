# ============== DONATION & TIPPING SERVICE ==============
# Comprehensive support for creator tipping across all platform features
# Supports: Direct tips, campaigns, recurring donations, multi-currency

from pydantic import BaseModel, Field, EmailStr, validator, field_validator
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, timezone
from enum import Enum
import uuid
import logging
from decimal import Decimal
import hashlib
import hmac
import asyncio

logger = logging.getLogger(__name__)

# ============== ENUMS ==============
class TipAmountType(str, Enum):
    """Predefined tip amounts"""
    SMALL = "small"      # $1-2
    MEDIUM = "medium"    # $5-10
    LARGE = "large"      # $25-50
    XLARGE = "xlarge"    # $100+
    CUSTOM = "custom"    # User-defined

class PaymentMethod(str, Enum):
    """Supported payment methods"""
    PAYPAL = "paypal"
    STRIPE = "stripe"
    PAYFAST = "payfast"
    CRYPTOCURRENCY = "crypto"
    BANK_TRANSFER = "bank_transfer"

class DonationStatus(str, Enum):
    """Donation/tip status"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    DISPUTED = "disputed"

class ContentType(str, Enum):
    """Content types that can receive tips"""
    VIDEO = "video"
    MUSIC = "music"
    AUDIO = "audio"
    ARTICLE = "article"
    COURSE = "course"
    LIVESTREAM = "livestream"
    EVENT = "event"
    CHAT = "chat"
    PROJECT = "project"
    PRODUCT = "product"
    STREAM = "stream"

class TipVisibility(str, Enum):
    """Who can see the tip"""
    PUBLIC = "public"          # Shown in creator's tips
    PRIVATE = "private"        # Only creator sees
    ANONYMOUS = "anonymous"    # Visible but anonymous

class CurrencyType(str, Enum):
    """Supported currencies"""
    USD = "usd"
    ZAR = "zar"
    EUR = "eur"
    GBP = "gbp"
    NGN = "ngn"  # Nigerian Naira
    KES = "kes"  # Kenyan Shilling
    ETH = "eth"  # Ethereum
    BTC = "btc"  # Bitcoin
    JPY = "jpy"
    INR = "inr"

# ============== DATA MODELS ==============
class TipTier(BaseModel):
    """Predefined tip tier"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., max_length=100)
    amount: Decimal
    currency: CurrencyType = CurrencyType.USD
    description: Optional[str] = None
    emoji: Optional[str] = None
    perks: List[str] = Field(default_factory=list)
    active: bool = True

    class Config:
        json_encoders = {Decimal: str}

class Tip(BaseModel):
    """Individual tip/donation"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    donor_id: str
    creator_id: str
    content_id: Optional[str] = None
    content_type: ContentType
    amount: Decimal
    currency: CurrencyType = CurrencyType.USD
    payment_method: PaymentMethod
    
    # Message from donor
    message: Optional[str] = Field(None, max_length=500)
    donor_name: Optional[str] = None  # Custom name if anonymous
    visibility: TipVisibility = TipVisibility.PUBLIC
    
    # Transaction details
    transaction_id: Optional[str] = None
    status: DonationStatus = DonationStatus.PENDING
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Metadata
    is_recurring: bool = False
    recurring_id: Optional[str] = None  # Links to recurring donation
    platform_fee: Decimal = Decimal("0")
    creator_net: Decimal = Field(default_factory=lambda: Decimal("0"))
    
    # Processing
    processed_at: Optional[datetime] = None
    refund_reason: Optional[str] = None
    refunded_at: Optional[datetime] = None
    thanked: bool = False

    class Config:
        json_encoders = {
            Decimal: str,
            datetime: lambda v: v.isoformat()
        }

class RecurringDonation(BaseModel):
    """Recurring monthly/weekly donation"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    donor_id: str
    creator_id: str
    amount: Decimal
    currency: CurrencyType = CurrencyType.USD
    frequency: str = Field(..., pattern="^(weekly|monthly|yearly)$")
    payment_method: PaymentMethod
    
    next_charge: datetime
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    ended_at: Optional[datetime] = None
    
    subscription_id: Optional[str] = None  # Payment provider subscription ID
    active: bool = True
    auto_renew: bool = True
    
    # Settings
    tip_message: Optional[str] = Field(None, max_length=200)
    visibility: TipVisibility = TipVisibility.PUBLIC

    class Config:
        json_encoders = {
            Decimal: str,
            datetime: lambda v: v.isoformat()
        }

class DonationCampaign(BaseModel):
    """Fundraising campaign"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    creator_id: str
    title: str = Field(..., max_length=200)
    description: str = Field(..., max_length=2000)
    goal_amount: Decimal
    currency: CurrencyType = CurrencyType.USD
    
    current_amount: Decimal = Field(default_factory=lambda: Decimal("0"))
    donor_count: int = 0
    
    start_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    end_date: Optional[datetime] = None
    
    category: str = Field(..., max_length=100)
    thumbnail_url: Optional[str] = None
    
    # Rewards
    rewards_enabled: bool = True
    reward_tiers: List[TipTier] = Field(default_factory=list)
    
    active: bool = True
    featured: bool = False

    class Config:
        json_encoders = {
            Decimal: str,
            datetime: lambda v: v.isoformat()
        }

class CreatorDonationSettings(BaseModel):
    """Creator's donation settings"""
    creator_id: str
    
    # Basic settings
    donations_enabled: bool = True
    bio: Optional[str] = Field(None, max_length=500)
    
    # Tip tiers
    custom_tiers: List[TipTier] = Field(default_factory=list)
    allow_custom_amount: bool = True
    min_custom_amount: Decimal = Decimal("0.50")
    max_custom_amount: Decimal = Decimal("10000")
    
    # Fundraising
    fundraising_enabled: bool = True
    current_campaign_id: Optional[str] = None
    
    # Payment methods
    payment_methods: List[PaymentMethod] = Field(default_factory=list)
    paypal_email: Optional[EmailStr] = None
    stripe_account_id: Optional[str] = None
    payfast_merchant_id: Optional[str] = None
    
    # Preferences
    thank_you_message: Optional[str] = Field(None, max_length=500)
    public_leaderboard: bool = True
    show_donor_names: bool = True
    notification_on_tip: bool = True
    
    # Currency preferences
    preferred_currency: CurrencyType = CurrencyType.USD
    
    # Fees
    platform_fee_percent: Decimal = Field(default=Decimal("5"))  # Default 5%
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        json_encoders = {
            Decimal: str,
            datetime: lambda v: v.isoformat()
        }

class CreatorEarnings(BaseModel):
    """Creator earnings summary"""
    creator_id: str
    
    total_earned: Decimal = Field(default_factory=lambda: Decimal("0"))
    total_tips: int = 0
    total_donors: int = 0
    
    # Period earnings
    monthly_earned: Decimal = Field(default_factory=lambda: Decimal("0"))
    monthly_tips: int = 0
    yearly_earned: Decimal = Field(default_factory=lambda: Decimal("0"))
    
    # Top tips
    top_tip_amount: Optional[Decimal] = None
    avg_tip_amount: Optional[Decimal] = None
    
    # Recurring
    monthly_recurring: Decimal = Field(default_factory=lambda: Decimal("0"))
    recurring_donors: int = 0
    
    # Pending payout
    pending_payout: Decimal = Field(default_factory=lambda: Decimal("0"))
    last_payout: Optional[datetime] = None
    
    currency: CurrencyType = CurrencyType.USD
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        json_encoders = {
            Decimal: str,
            datetime: lambda v: v.isoformat()
        }

class TransactionHistory(BaseModel):
    """User's transaction history"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    transaction_type: str = Field(..., pattern="^(donation|refund|payout|subscription)$")
    amount: Decimal
    currency: CurrencyType
    
    description: str
    related_id: Optional[str] = None  # Tip ID, Campaign ID, etc.
    status: str = Field(..., pattern="^(completed|pending|failed)$")
    
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_encoders = {
            Decimal: str,
            datetime: lambda v: v.isoformat()
        }

class ThanksMessage(BaseModel):
    """Creator's thank you message to donor"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    donation_id: str
    creator_id: str
    donor_id: str
    
    message: str = Field(..., max_length=1000)
    is_public: bool = True
    video_url: Optional[str] = None  # Optional video thank you
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    viewed_at: Optional[datetime] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# ============== SERVICE CLASS ==============
class DonationTippingService:
    """Main service for donations and tipping"""
    
    def __init__(self, db):
        self.db = db
        self.logger = logging.getLogger(__name__)
        
        # Default tip tiers
        self.default_tiers = [
            TipTier(name="☕ Coffee", amount=Decimal("2"), emoji="☕", description="Buy a creator a coffee"),
            TipTier(name="🎁 Gift", amount=Decimal("5"), emoji="🎁", description="Small gift"),
            TipTier(name="🌟 Star", amount=Decimal("10"), emoji="🌟", description="You're a star!"),
            TipTier(name="💎 Diamond", amount=Decimal("25"), emoji="💎", description="Premium support"),
            TipTier(name="👑 Royalty", amount=Decimal("50"), emoji="👑", description="VIP supporter"),
            TipTier(name="🚀 Legend", amount=Decimal("100"), emoji="🚀", description="Legendary support"),
        ]
    
    async def create_tip(self, tip_data: Dict[str, Any]) -> Tip:
        """Create a new tip/donation"""
        try:
            tip_data.setdefault('id', str(uuid.uuid4()))
            tip = Tip(**tip_data)
            
            # Calculate fees and net amount if completed
            if tip.status == DonationStatus.COMPLETED:
                settings = await self.get_creator_settings(tip.creator_id)
                fee_percent = settings.platform_fee_percent / 100
                tip.platform_fee = (tip.amount * fee_percent).quantize(Decimal("0.01"))
                tip.creator_net = tip.amount - tip.platform_fee
                tip.processed_at = datetime.now(timezone.utc)
            
            # Store in database
            tip_dict = tip.dict(by_alias=False)
            tip_dict['amount'] = str(tip.amount)
            tip_dict['platform_fee'] = str(tip.platform_fee)
            tip_dict['creator_net'] = str(tip.creator_net)
            
            await self.db.donations.insert_one(tip_dict)
            self.logger.info(f"Tip created: {tip.id} to creator {tip.creator_id}")
            
            return tip
        except Exception as e:
            self.logger.error(f"Error creating tip: {e}")
            raise
    
    async def get_creator_tips(self, creator_id: str, limit: int = 50) -> List[Tip]:
        """Get all tips for a creator"""
        try:
            tips = await self.db.donations.find(
                {"creator_id": creator_id, "status": "completed"},
                sort=[("timestamp", -1)],
                limit=limit
            ).to_list(None)
            
            return [Tip(**tip) for tip in tips] if tips else []
        except Exception as e:
            self.logger.error(f"Error fetching creator tips: {e}")
            return []
    
    async def get_content_tips(self, content_id: str) -> List[Tip]:
        """Get tips for specific content"""
        try:
            tips = await self.db.donations.find(
                {"content_id": content_id, "status": "completed"},
                sort=[("timestamp", -1)]
            ).to_list(None)
            
            return [Tip(**tip) for tip in tips] if tips else []
        except Exception as e:
            self.logger.error(f"Error fetching content tips: {e}")
            return []
    
    async def get_creator_earnings(self, creator_id: str) -> CreatorEarnings:
        """Get creator's earnings summary"""
        try:
            # Fetch all completed tips
            tips = await self.db.donations.find(
                {"creator_id": creator_id, "status": "completed"}
            ).to_list(None)
            
            now = datetime.now(timezone.utc)
            month_ago = now - timedelta(days=30)
            year_ago = now - timedelta(days=365)
            
            total_earned = Decimal("0")
            monthly_earned = Decimal("0")
            yearly_earned = Decimal("0")
            donors = set()
            tip_amounts = []
            
            for tip in tips:
                tip_amount = Decimal(str(tip.get("creator_net", tip.get("amount", 0))))
                total_earned += tip_amount
                tip_amounts.append(tip_amount)
                
                tip_date = tip.get("processed_at", tip.get("timestamp"))
                if isinstance(tip_date, str):
                    tip_date = datetime.fromisoformat(tip_date.replace('Z', '+00:00'))
                
                if tip_date >= month_ago:
                    monthly_earned += tip_amount
                if tip_date >= year_ago:
                    yearly_earned += tip_amount
                
                donors.add(tip.get("donor_id"))
            
            avg_tip = (total_earned / len(tips)).quantize(Decimal("0.01")) if tips else Decimal("0")
            top_tip = max(tip_amounts) if tip_amounts else None
            
            earnings = CreatorEarnings(
                creator_id=creator_id,
                total_earned=total_earned,
                total_tips=len(tips),
                total_donors=len(donors),
                monthly_earned=monthly_earned,
                yearly_earned=yearly_earned,
                avg_tip_amount=avg_tip,
                top_tip_amount=top_tip
            )
            
            return earnings
        except Exception as e:
            self.logger.error(f"Error calculating earnings: {e}")
            raise
    
    async def get_creator_settings(self, creator_id: str) -> CreatorDonationSettings:
        """Get or create creator donation settings"""
        try:
            settings_doc = await self.db.creator_donation_settings.find_one(
                {"creator_id": creator_id}
            )
            
            if not settings_doc:
                new_settings = CreatorDonationSettings(
                    creator_id=creator_id,
                    payment_methods=[PaymentMethod.PAYPAL, PaymentMethod.STRIPE],
                    custom_tiers=self.default_tiers
                )
                settings_dict = new_settings.dict(by_alias=False)
                settings_dict['custom_tiers'] = [t.dict(by_alias=False) for t in new_settings.custom_tiers]
                settings_dict['min_custom_amount'] = str(new_settings.min_custom_amount)
                settings_dict['max_custom_amount'] = str(new_settings.max_custom_amount)
                settings_dict['platform_fee_percent'] = str(new_settings.platform_fee_percent)
                
                await self.db.creator_donation_settings.insert_one(settings_dict)
                return new_settings
            
            return CreatorDonationSettings(**settings_doc)
        except Exception as e:
            self.logger.error(f"Error fetching creator settings: {e}")
            raise
    
    async def update_creator_settings(self, creator_id: str, settings_data: Dict[str, Any]) -> CreatorDonationSettings:
        """Update creator donation settings"""
        try:
            settings_data["updated_at"] = datetime.now(timezone.utc)
            
            result = await self.db.creator_donation_settings.update_one(
                {"creator_id": creator_id},
                {"$set": settings_data}
            )
            
            if result.matched_count == 0:
                # Create new settings if doesn't exist
                settings_data["creator_id"] = creator_id
                await self.db.creator_donation_settings.insert_one(settings_data)
            
            self.logger.info(f"Creator settings updated: {creator_id}")
            return await self.get_creator_settings(creator_id)
        except Exception as e:
            self.logger.error(f"Error updating creator settings: {e}")
            raise
    
    async def create_campaign(self, campaign_data: Dict[str, Any]) -> DonationCampaign:
        """Create a fundraising campaign"""
        try:
            campaign_data.setdefault('id', str(uuid.uuid4()))
            campaign = DonationCampaign(**campaign_data)
            
            # Add default tip tiers if not provided
            if not campaign.reward_tiers:
                campaign.reward_tiers = self.default_tiers
            
            campaign_dict = campaign.dict(by_alias=False)
            campaign_dict['goal_amount'] = str(campaign.goal_amount)
            campaign_dict['current_amount'] = str(campaign.current_amount)
            campaign_dict['reward_tiers'] = [t.dict(by_alias=False) for t in campaign.reward_tiers]
            
            await self.db.donation_campaigns.insert_one(campaign_dict)
            self.logger.info(f"Campaign created: {campaign.id}")
            
            return campaign
        except Exception as e:
            self.logger.error(f"Error creating campaign: {e}")
            raise
    
    async def get_campaigns(self, creator_id: Optional[str] = None, limit: int = 20) -> List[DonationCampaign]:
        """Get fundraising campaigns"""
        try:
            query = {"active": True}
            if creator_id:
                query["creator_id"] = creator_id
            
            campaigns = await self.db.donation_campaigns.find(
                query,
                sort=[("start_date", -1)],
                limit=limit
            ).to_list(None)
            
            return [DonationCampaign(**c) for c in campaigns] if campaigns else []
        except Exception as e:
            self.logger.error(f"Error fetching campaigns: {e}")
            return []
    
    async def get_campaign_details(self, campaign_id: str) -> Optional[DonationCampaign]:
        """Get campaign details with tips"""
        try:
            campaign = await self.db.donation_campaigns.find_one(
                {"id": campaign_id}
            )
            
            if campaign:
                return DonationCampaign(**campaign)
            return None
        except Exception as e:
            self.logger.error(f"Error fetching campaign: {e}")
            return None
    
    async def donate_to_campaign(self, campaign_id: str, donation_data: Dict[str, Any]) -> Tip:
        """Donate to a fundraising campaign"""
        try:
            # Create tip linked to campaign
            donation_data.setdefault('content_id', campaign_id)
            donation_data.setdefault('content_type', ContentType.PROJECT)
            
            tip = await self.create_tip(donation_data)
            
            # Update campaign stats
            await self.db.donation_campaigns.update_one(
                {"id": campaign_id},
                {
                    "$inc": {
                        "current_amount": float(tip.amount),
                        "donor_count": 1
                    }
                }
            )
            
            self.logger.info(f"Donation to campaign: {campaign_id}")
            return tip
        except Exception as e:
            self.logger.error(f"Error donating to campaign: {e}")
            raise
    
    async def send_thank_you(self, donation_id: str, thank_you_data: Dict[str, Any]) -> ThanksMessage:
        """Send thank you message from creator"""
        try:
            thank_you_data.setdefault('id', str(uuid.uuid4()))
            thank_you_data['donation_id'] = donation_id
            thanks = ThanksMessage(**thank_you_data)
            
            thanks_dict = thanks.dict(by_alias=False)
            await self.db.thank_you_messages.insert_one(thanks_dict)
            
            # Update tip as thanked
            await self.db.donations.update_one(
                {"id": donation_id},
                {"$set": {"thanked": True}}
            )
            
            self.logger.info(f"Thank you sent for donation: {donation_id}")
            return thanks
        except Exception as e:
            self.logger.error(f"Error sending thank you: {e}")
            raise
    
    async def refund_donation(self, donation_id: str, reason: str) -> bool:
        """Refund a donation"""
        try:
            result = await self.db.donations.update_one(
                {"id": donation_id},
                {
                    "$set": {
                        "status": DonationStatus.REFUNDED.value,
                        "refund_reason": reason,
                        "refunded_at": datetime.now(timezone.utc)
                    }
                }
            )
            
            self.logger.info(f"Donation refunded: {donation_id}")
            return result.modified_count > 0
        except Exception as e:
            self.logger.error(f"Error refunding donation: {e}")
            return False
    
    async def get_top_donors(self, creator_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top donors for a creator"""
        try:
            pipeline = [
                {"$match": {"creator_id": creator_id, "status": "completed"}},
                {"$group": {
                    "_id": "$donor_id",
                    "total_donated": {"$sum": {"$toDecimal": "$amount"}},
                    "donation_count": {"$sum": 1},
                    "last_donation": {"$max": "$timestamp"}
                }},
                {"$sort": {"total_donated": -1}},
                {"$limit": limit}
            ]
            
            top_donors = await self.db.donations.aggregate(pipeline).to_list(None)
            return top_donors if top_donors else []
        except Exception as e:
            self.logger.error(f"Error fetching top donors: {e}")
            return []
    
    async def get_donation_stats(self, creator_id: str) -> Dict[str, Any]:
        """Get comprehensive donation statistics"""
        try:
            earnings = await self.get_creator_earnings(creator_id)
            top_donors = await self.get_top_donors(creator_id)
            
            tips = await self.db.donations.find(
                {"creator_id": creator_id, "status": "completed"}
            ).to_list(None)
            
            # Calculate stats
            daily_tips = {}
            for tip in tips:
                date_val = tip.get("timestamp")
                if isinstance(date_val, str):
                    date_val = datetime.fromisoformat(date_val.replace('Z', '+00:00'))
                date = date_val.date() if date_val else datetime.now(timezone.utc).date()
                date_str = str(date)
                daily_tips[date_str] = daily_tips.get(date_str, 0) + 1
            
            return {
                "total_earned": str(earnings.total_earned),
                "total_tips": earnings.total_tips,
                "total_donors": earnings.total_donors,
                "monthly_earned": str(earnings.monthly_earned),
                "monthly_recurring": str(earnings.monthly_recurring),
                "avg_tip": str(earnings.avg_tip_amount or Decimal("0")),
                "top_tip": str(earnings.top_tip_amount or Decimal("0")),
                "top_donors": top_donors[:5],
                "daily_tips": daily_tips
            }
        except Exception as e:
            self.logger.error(f"Error calculating donation stats: {e}")
            raise

# ============== HELPER FUNCTIONS ==============
def calculate_payout_amount(gross_amount: Decimal, platform_fee_percent: Decimal) -> Decimal:
    """Calculate payout to creator after platform fee"""
    fee = (gross_amount * platform_fee_percent / 100).quantize(Decimal("0.01"))
    return (gross_amount - fee).quantize(Decimal("0.01"))

def validate_tip_amount(amount: Decimal, min_amount: Decimal = Decimal("0.50")) -> bool:
    """Validate tip amount"""
    return amount >= min_amount and amount <= Decimal("10000")

def format_currency(amount: Decimal, currency: CurrencyType) -> str:
    """Format amount with currency symbol"""
    symbols = {
        CurrencyType.USD: "$",
        CurrencyType.ZAR: "R",
        CurrencyType.EUR: "€",
        CurrencyType.GBP: "£",
        CurrencyType.NGN: "₦",
        CurrencyType.KES: "KSh",
        CurrencyType.JPY: "¥",
        CurrencyType.INR: "₹",
    }
    return f"{symbols.get(currency, currency.value)}{amount:.2f}"

# ============== EXPORTS ==============
__all__ = [
    "DonationTippingService",
    "Tip",
    "RecurringDonation",
    "DonationCampaign",
    "CreatorDonationSettings",
    "CreatorEarnings",
    "TransactionHistory",
    "ThanksMessage",
    "TipTier",
    "TipAmountType",
    "PaymentMethod",
    "DonationStatus",
    "ContentType",
    "TipVisibility",
    "CurrencyType",
    "calculate_payout_amount",
    "validate_tip_amount",
    "format_currency"
]
