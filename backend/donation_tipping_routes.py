# ============== DONATION & TIPPING API ROUTES ==============
# FastAPI routes for all donation and tipping endpoints

from fastapi import APIRouter, Depends, HTTPException, Body, Query
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, EmailStr
from decimal import Decimal
import logging
from datetime import datetime, timezone

from .donation_tipping_service import (
    DonationTippingService,
    Tip, RecurringDonation, DonationCampaign,
    CreatorDonationSettings, CreatorEarnings, TransactionHistory,
    ThanksMessage, TipTier, PaymentMethod, DonationStatus,
    ContentType, TipVisibility, CurrencyType,
    validate_tip_amount, format_currency
)

logger = logging.getLogger(__name__)

# ============== REQUEST/RESPONSE MODELS ==============
class CreateTipRequest(BaseModel):
    """Request to create a tip"""
    creator_id: str
    content_id: Optional[str] = None
    content_type: ContentType
    amount: Decimal
    currency: CurrencyType = CurrencyType.USD
    payment_method: PaymentMethod
    message: Optional[str] = None
    donor_name: Optional[str] = None
    visibility: TipVisibility = TipVisibility.PUBLIC

class CreateCampaignRequest(BaseModel):
    """Request to create a campaign"""
    title: str = Field(..., max_length=200)
    description: str = Field(..., max_length=2000)
    goal_amount: Decimal
    currency: CurrencyType = CurrencyType.USD
    category: str = Field(..., max_length=100)
    thumbnail_url: Optional[str] = None
    reward_tiers: Optional[List[TipTier]] = None

class UpdateCreatorSettingsRequest(BaseModel):
    """Request to update creator settings"""
    donations_enabled: Optional[bool] = None
    bio: Optional[str] = None
    allow_custom_amount: Optional[bool] = None
    min_custom_amount: Optional[Decimal] = None
    max_custom_amount: Optional[Decimal] = None
    custom_tiers: Optional[List[TipTier]] = None
    thank_you_message: Optional[str] = None
    public_leaderboard: Optional[bool] = None
    notification_on_tip: Optional[bool] = None
    preferred_currency: Optional[CurrencyType] = None

class CreateRecurringDonationRequest(BaseModel):
    """Request to create recurring donation"""
    creator_id: str
    amount: Decimal
    currency: CurrencyType = CurrencyType.USD
    frequency: str = Field(..., pattern="^(weekly|monthly|yearly)$")
    payment_method: PaymentMethod
    tip_message: Optional[str] = None
    visibility: TipVisibility = TipVisibility.PUBLIC

class SendThankYouRequest(BaseModel):
    """Request to send thank you message"""
    donation_id: str
    creator_id: str
    donor_id: str
    message: str = Field(..., max_length=1000)
    is_public: bool = True
    video_url: Optional[str] = None

class TipResponse(BaseModel):
    """Response with tip details"""
    id: str
    donor_id: str
    creator_id: str
    amount: str
    currency: str
    status: str
    timestamp: str
    visibility: str
    message: Optional[str] = None
    donor_name: Optional[str] = None

class CreatorStatsResponse(BaseModel):
    """Creator donation statistics"""
    total_earned: str
    total_tips: int
    total_donors: int
    monthly_earned: str
    yearly_earned: str
    avg_tip: str
    top_tip: str
    monthly_recurring: str
    recurring_donors: int
    top_donors: List[Dict[str, Any]]
    daily_tips: Dict[str, int]

class CampaignResponse(BaseModel):
    """Campaign response"""
    id: str
    title: str
    description: str
    goal_amount: str
    current_amount: str
    donor_count: int
    currency: str
    progress: float
    status: str

# ============== SERVICE INITIALIZATION ==============
async def get_donation_service(request) -> DonationTippingService:
    """Get donation service instance"""
    try:
        # Assuming MongoDB client is available in app state
        db = request.app.mongodb.db
        return DonationTippingService(db)
    except Exception as e:
        logger.error(f"Error getting donation service: {e}")
        raise HTTPException(status_code=500, detail="Service unavailable")

# ============== ROUTERS ==============
router_donate = APIRouter(prefix="/api/donate", tags=["Donations"])
router_campaigns = APIRouter(prefix="/api/campaigns", tags=["Campaigns"])
router_creator = APIRouter(prefix="/api/creator", tags=["Creator"])

# ============== DONATION ENDPOINTS ==============
@router_donate.post("/{creator_id}", response_model=Dict[str, Any])
async def create_tip(
    creator_id: str,
    tip_request: CreateTipRequest,
    request,
    donor_id: str = Query(...)
):
    """Create a new tip/donation"""
    try:
        if not validate_tip_amount(tip_request.amount):
            raise HTTPException(status_code=400, detail="Invalid tip amount")
        
        service = await get_donation_service(request)
        
        tip_data = {
            "donor_id": donor_id,
            "creator_id": creator_id,
            **tip_request.dict()
        }
        
        tip = await service.create_tip(tip_data)
        
        return {
            "success": True,
            "message": f"Tip of {format_currency(tip_request.amount, tip_request.currency)} created successfully",
            "tip_id": tip.id,
            "status": tip.status.value,
            "amount": str(tip.amount),
            "creator_fee": str(tip.creator_net)
        }
    except Exception as e:
        logger.error(f"Error creating tip: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router_donate.get("/creator/{creator_id}/tips", response_model=List[TipResponse])
async def get_creator_tips(
    creator_id: str,
    request,
    limit: int = Query(50, ge=1, le=100)
):
    """Get all tips for a creator"""
    try:
        service = await get_donation_service(request)
        tips = await service.get_creator_tips(creator_id, limit)
        
        return [
            TipResponse(
                id=tip.id,
                donor_id=tip.donor_id,
                creator_id=tip.creator_id,
                amount=str(tip.amount),
                currency=tip.currency.value,
                status=tip.status.value,
                timestamp=tip.timestamp.isoformat(),
                visibility=tip.visibility.value,
                message=tip.message,
                donor_name=tip.donor_name if tip.visibility != TipVisibility.PRIVATE else None
            )
            for tip in tips
        ]
    except Exception as e:
        logger.error(f"Error fetching creator tips: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router_donate.get("/content/{content_id}")
async def get_content_tips(
    content_id: str,
    request
):
    """Get tips for specific content"""
    try:
        service = await get_donation_service(request)
        tips = await service.get_content_tips(content_id)
        
        return {
            "success": True,
            "content_id": content_id,
            "tips_count": len(tips),
            "total_amount": str(sum(Decimal(str(tip.amount)) for tip in tips)),
            "tips": [
                {
                    "id": tip.id,
                    "amount": str(tip.amount),
                    "currency": tip.currency.value,
                    "message": tip.message,
                    "timestamp": tip.timestamp.isoformat()
                }
                for tip in tips
            ]
        }
    except Exception as e:
        logger.error(f"Error fetching content tips: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router_donate.get("/top-donors/{creator_id}")
async def get_top_donors(
    creator_id: str,
    request,
    limit: int = Query(10, ge=1, le=50)
):
    """Get top donors for a creator"""
    try:
        service = await get_donation_service(request)
        top_donors = await service.get_top_donors(creator_id, limit)
        
        return {
            "success": True,
            "creator_id": creator_id,
            "top_donors": top_donors
        }
    except Exception as e:
        logger.error(f"Error fetching top donors: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============== CAMPAIGN ENDPOINTS ==============
@router_campaigns.post("/", response_model=Dict[str, Any])
async def create_campaign(
    campaign_request: CreateCampaignRequest,
    request,
    creator_id: str = Query(...)
):
    """Create a new fundraising campaign"""
    try:
        service = await get_donation_service(request)
        
        campaign_data = {
            "creator_id": creator_id,
            **campaign_request.dict()
        }
        
        campaign = await service.create_campaign(campaign_data)
        
        return {
            "success": True,
            "message": "Campaign created successfully",
            "campaign_id": campaign.id,
            "title": campaign.title,
            "goal_amount": str(campaign.goal_amount)
        }
    except Exception as e:
        logger.error(f"Error creating campaign: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router_campaigns.get("/", response_model=List[CampaignResponse])
async def get_campaigns(
    request,
    creator_id: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100)
):
    """Get fundraising campaigns"""
    try:
        service = await get_donation_service(request)
        campaigns = await service.get_campaigns(creator_id, limit)
        
        return [
            CampaignResponse(
                id=campaign.id,
                title=campaign.title,
                description=campaign.description,
                goal_amount=str(campaign.goal_amount),
                current_amount=str(campaign.current_amount),
                donor_count=campaign.donor_count,
                currency=campaign.currency.value,
                progress=min(100, float((campaign.current_amount / campaign.goal_amount * 100) if campaign.goal_amount > 0 else 0)),
                status="Active" if campaign.active else "Inactive"
            )
            for campaign in campaigns
        ]
    except Exception as e:
        logger.error(f"Error fetching campaigns: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router_campaigns.get("/{campaign_id}", response_model=Dict[str, Any])
async def get_campaign_details(
    campaign_id: str,
    request
):
    """Get campaign details"""
    try:
        service = await get_donation_service(request)
        campaign = await service.get_campaign_details(campaign_id)
        
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        progress = float((campaign.current_amount / campaign.goal_amount * 100) if campaign.goal_amount > 0 else 0)
        
        return {
            "success": True,
            "id": campaign.id,
            "title": campaign.title,
            "description": campaign.description,
            "creator_id": campaign.creator_id,
            "goal_amount": str(campaign.goal_amount),
            "current_amount": str(campaign.current_amount),
            "donor_count": campaign.donor_count,
            "progress": progress,
            "currency": campaign.currency.value,
            "category": campaign.category,
            "created": campaign.start_date.isoformat(),
            "active": campaign.active
        }
    except Exception as e:
        logger.error(f"Error fetching campaign details: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router_campaigns.post("/{campaign_id}/donate", response_model=Dict[str, Any])
async def donate_to_campaign(
    campaign_id: str,
    request,
    donor_id: str = Query(...),
    amount: Decimal = Body(...),
    currency: CurrencyType = Body(CurrencyType.USD),
    payment_method: PaymentMethod = Body(...),
    message: Optional[str] = Body(None)
):
    """Donate to a campaign"""
    try:
        campaign_doc = request.app.mongodb.db.donation_campaigns
        campaign = await campaign_doc.find_one({"id": campaign_id})
        
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        service = await get_donation_service(request)
        
        donation_data = {
            "donor_id": donor_id,
            "creator_id": campaign["creator_id"],
            "content_id": campaign_id,
            "content_type": ContentType.PROJECT,
            "amount": amount,
            "currency": currency,
            "payment_method": payment_method,
            "message": message,
            "status": DonationStatus.COMPLETED
        }
        
        tip = await service.donate_to_campaign(campaign_id, donation_data)
        
        return {
            "success": True,
            "message": f"Donation of {format_currency(amount, currency)} received!",
            "donation_id": tip.id,
            "campaign_id": campaign_id
        }
    except Exception as e:
        logger.error(f"Error donating to campaign: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============== CREATOR ENDPOINTS ==============
@router_creator.get("/{creator_id}/stats", response_model=CreatorStatsResponse)
async def get_creator_stats(
    creator_id: str,
    request
):
    """Get creator's donation statistics"""
    try:
        service = await get_donation_service(request)
        stats = await service.get_donation_stats(creator_id)
        
        return CreatorStatsResponse(**stats)
    except Exception as e:
        logger.error(f"Error fetching creator stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router_creator.get("/{creator_id}/earnings", response_model=Dict[str, Any])
async def get_creator_earnings(
    creator_id: str,
    request
):
    """Get creator's earnings summary"""
    try:
        service = await get_donation_service(request)
        earnings = await service.get_creator_earnings(creator_id)
        
        return {
            "success": True,
            "total_earned": str(earnings.total_earned),
            "total_tips": earnings.total_tips,
            "total_donors": earnings.total_donors,
            "monthly_earned": str(earnings.monthly_earned),
            "yearly_earned": str(earnings.yearly_earned),
            "monthly_recurring": str(earnings.monthly_recurring),
            "recurring_donors": earnings.recurring_donors,
            "avg_tip": str(earnings.avg_tip_amount or Decimal("0")),
            "top_tip": str(earnings.top_tip_amount or Decimal("0")),
            "currency": earnings.currency.value
        }
    except Exception as e:
        logger.error(f"Error fetching creator earnings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router_creator.get("/{creator_id}/settings", response_model=Dict[str, Any])
async def get_creator_settings(
    creator_id: str,
    request
):
    """Get creator's donation settings"""
    try:
        service = await get_donation_service(request)
        settings = await service.get_creator_settings(creator_id)
        
        return {
            "success": True,
            "creator_id": settings.creator_id,
            "donations_enabled": settings.donations_enabled,
            "payment_methods": [pm.value for pm in settings.payment_methods],
            "custom_tiers": settings.custom_tiers,
            "allow_custom_amount": settings.allow_custom_amount,
            "min_custom_amount": str(settings.min_custom_amount),
            "max_custom_amount": str(settings.max_custom_amount),
            "thank_you_message": settings.thank_you_message,
            "preferred_currency": settings.preferred_currency.value
        }
    except Exception as e:
        logger.error(f"Error fetching creator settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router_creator.put("/{creator_id}/settings", response_model=Dict[str, Any])
async def update_creator_settings(
    creator_id: str,
    settings_request: UpdateCreatorSettingsRequest,
    request
):
    """Update creator's donation settings"""
    try:
        service = await get_donation_service(request)
        
        settings_data = settings_request.dict(exclude_unset=True)
        updated_settings = await service.update_creator_settings(creator_id, settings_data)
        
        return {
            "success": True,
            "message": "Settings updated successfully",
            "creator_id": updated_settings.creator_id
        }
    except Exception as e:
        logger.error(f"Error updating creator settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router_creator.post("/{creator_id}/thank-you/{donation_id}", response_model=Dict[str, Any])
async def send_thank_you(
    creator_id: str,
    donation_id: str,
    thank_you_request: SendThankYouRequest,
    request
):
    """Send thank you message to donor"""
    try:
        service = await get_donation_service(request)
        
        thank_you_data = {
            "creator_id": creator_id,
            "donor_id": thank_you_request.donor_id,
            "message": thank_you_request.message,
            "is_public": thank_you_request.is_public,
            "video_url": thank_you_request.video_url
        }
        
        thanks = await service.send_thank_you(donation_id, thank_you_data)
        
        return {
            "success": True,
            "message": "Thank you message sent!",
            "thanks_id": thanks.id
        }
    except Exception as e:
        logger.error(f"Error sending thank you: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============== EXPORTS ==============
__all__ = [
    "router_donate",
    "router_campaigns",
    "router_creator"
]
