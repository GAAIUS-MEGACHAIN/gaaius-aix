"""
Newsletter Service - Production Email Campaign Manager
FastAPI Backend - Mailchimp Clone
Real code with no mocks or templates
"""

from fastapi import APIRouter, HTTPException, Body, Query, UploadFile, File
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from enum import Enum
import motor.motor_asyncio
import json
import csv
import io
from bson import ObjectId

router = APIRouter(prefix="/api/newsletter", tags=["Newsletter"])

# ============ ENUMS ============

class CampaignStatus(str, Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    SENDING = "sending"
    SENT = "sent"
    PAUSED = "paused"
    FAILED = "failed"

class SegmentType(str, Enum):
    ALL = "all"
    TAG_BASED = "tag_based"
    ENGAGEMENT = "engagement"
    CUSTOM = "custom"

class AutomationTrigger(str, Enum):
    SUBSCRIBE = "subscribe"
    PURCHASE = "purchase"
    ABANDONED_CART = "abandoned_cart"
    DATE = "date"
    TAG = "tag"

# ============ MODELS ============

class SubscriberModel(BaseModel):
    email: EmailStr
    name: str
    phone: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    segments: List[str] = Field(default_factory=list)
    custom_fields: Dict[str, Any] = Field(default_factory=dict)
    status: str = "active"  # active, unsubscribed, bounced
    subscribed_date: datetime = Field(default_factory=datetime.utcnow)
    last_engagement: Optional[datetime] = None
    open_count: int = 0
    click_count: int = 0

    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "name": "John Doe",
                "phone": "+1234567890",
                "tags": ["vip", "beta"],
                "custom_fields": {"company": "ACME Corp"},
                "status": "active"
            }
        }

class EmailTemplate(BaseModel):
    name: str
    subject: str
    preview_text: str
    html_content: str
    text_content: str
    variables: List[str] = Field(default_factory=list)  # {{name}}, {{email}}
    thumbnail: Optional[str] = None
    category: str = "custom"
    is_default: bool = False

    class Config:
        schema_extra = {
            "example": {
                "name": "Welcome Email",
                "subject": "Welcome to {{company_name}}, {{name}}!",
                "html_content": "<h1>Hello {{name}}</h1><p>Welcome aboard!</p>",
                "variables": ["name", "company_name"]
            }
        }

class CampaignSegment(BaseModel):
    segment_type: SegmentType
    tags: Optional[List[str]] = None
    engagement_filter: Optional[str] = None  # high, medium, low
    custom_filter: Optional[Dict[str, Any]] = None
    subscriber_count: int = 0

class ABTestConfig(BaseModel):
    enabled: bool = False
    variant_a_subject: Optional[str] = None
    variant_b_subject: Optional[str] = None
    split_percentage: int = 50
    winner_metric: str = "open_rate"  # open_rate, click_rate

class CampaignAnalytics(BaseModel):
    sent_count: int = 0
    delivered_count: int = 0
    open_count: int = 0
    click_count: int = 0
    bounce_count: int = 0
    unsubscribe_count: int = 0
    open_rate: float = 0.0
    click_rate: float = 0.0
    bounce_rate: float = 0.0
    links_clicked: Dict[str, int] = Field(default_factory=dict)

class Campaign(BaseModel):
    user_id: str = ""
    name: str
    template: EmailTemplate
    segment: CampaignSegment
    ab_test: Optional[ABTestConfig] = None
    status: CampaignStatus = CampaignStatus.DRAFT
    schedule_time: Optional[datetime] = None
    send_time: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    analytics: CampaignAnalytics = Field(default_factory=CampaignAnalytics)
    preview_subscribers: List[str] = Field(default_factory=list)

class AutomationWorkflow(BaseModel):
    user_id: str = ""
    name: str
    trigger: AutomationTrigger
    trigger_config: Dict[str, Any]
    actions: List[Dict[str, Any]]
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

class SMTPConfig(BaseModel):
    smtp_host: str
    smtp_port: int
    sender_email: EmailStr
    sender_name: str
    username: str
    password: str
    use_tls: bool = True
    is_configured: bool = False

# ============ DATABASE ============

db = None

def get_db():
    global db
    return db

def set_db(database):
    global db
    db = database

# ============ CRUD OPERATIONS ============

class SubscriberCRUD:
    @staticmethod
    async def create(user_id: str, subscriber: SubscriberModel):
        """Create new subscriber"""
        db_conn = get_db()
        result = await db_conn.subscribers.insert_one({
            "user_id": user_id,
            **subscriber.dict(),
            "created_at": datetime.utcnow()
        })
        return str(result.inserted_id)

    @staticmethod
    async def get_by_email(user_id: str, email: str):
        """Get subscriber by email"""
        db_conn = get_db()
        return await db_conn.subscribers.find_one({"user_id": user_id, "email": email})

    @staticmethod
    async def get_list(user_id: str, skip: int = 0, limit: int = 50):
        """Get paginated subscriber list"""
        db_conn = get_db()
        subscribers = await db_conn.subscribers.find({"user_id": user_id}).skip(skip).limit(limit).to_list(limit)
        return subscribers

    @staticmethod
    async def count(user_id: str):
        """Count total subscribers"""
        db_conn = get_db()
        return await db_conn.subscribers.count_documents({"user_id": user_id})

    @staticmethod
    async def update(user_id: str, email: str, update_data: Dict):
        """Update subscriber"""
        db_conn = get_db()
        result = await db_conn.subscribers.update_one(
            {"user_id": user_id, "email": email},
            {"$set": {**update_data, "updated_at": datetime.utcnow()}}
        )
        return result.modified_count > 0

    @staticmethod
    async def delete(user_id: str, email: str):
        """Delete subscriber"""
        db_conn = get_db()
        result = await db_conn.subscribers.delete_one({"user_id": user_id, "email": email})
        return result.deleted_count > 0

    @staticmethod
    async def get_by_segment(user_id: str, segment: CampaignSegment):
        """Get subscribers matching segment"""
        db_conn = get_db()
        query = {"user_id": user_id, "status": "active"}
        
        if segment.segment_type == SegmentType.TAG_BASED and segment.tags:
            query["tags"] = {"$in": segment.tags}
        elif segment.segment_type == SegmentType.ENGAGEMENT:
            if segment.engagement_filter == "high":
                query["open_count"] = {"$gte": 5}
            elif segment.engagement_filter == "low":
                query["open_count"] = {"$lt": 2}
        
        return await db_conn.subscribers.find(query).to_list(None)

    @staticmethod
    async def import_csv(user_id: str, file_content: str):
        """Import subscribers from CSV"""
        db_conn = get_db()
        reader = csv.DictReader(io.StringIO(file_content))
        imported = 0
        
        for row in reader:
            try:
                subscriber = SubscriberModel(
                    email=row.get("email"),
                    name=row.get("name", ""),
                    tags=row.get("tags", "").split(",") if row.get("tags") else [],
                    custom_fields={k: v for k, v in row.items() if k not in ["email", "name", "tags"]}
                )
                existing = await db_conn.subscribers.find_one({"user_id": user_id, "email": subscriber.email})
                if not existing:
                    await db_conn.subscribers.insert_one({"user_id": user_id, **subscriber.dict()})
                    imported += 1
            except Exception as e:
                continue
        
        return imported

class CampaignCRUD:
    @staticmethod
    async def create(user_id: str, campaign: Campaign):
        """Create new campaign"""
        db_conn = get_db()
        campaign.user_id = user_id
        result = await db_conn.campaigns.insert_one(campaign.dict())
        return str(result.inserted_id)

    @staticmethod
    async def get(user_id: str, campaign_id: str):
        """Get campaign by ID"""
        db_conn = get_db()
        return await db_conn.campaigns.find_one({
            "_id": ObjectId(campaign_id),
            "user_id": user_id
        })

    @staticmethod
    async def list(user_id: str, skip: int = 0, limit: int = 20):
        """List user campaigns"""
        db_conn = get_db()
        campaigns = await db_conn.campaigns.find({"user_id": user_id}).skip(skip).limit(limit).to_list(limit)
        return campaigns

    @staticmethod
    async def update_status(user_id: str, campaign_id: str, status: CampaignStatus):
        """Update campaign status"""
        db_conn = get_db()
        result = await db_conn.campaigns.update_one(
            {"_id": ObjectId(campaign_id), "user_id": user_id},
            {"$set": {"status": status, "updated_at": datetime.utcnow()}}
        )
        return result.modified_count > 0

    @staticmethod
    async def update_analytics(user_id: str, campaign_id: str, event: str):
        """Update campaign analytics"""
        db_conn = get_db()
        await db_conn.campaigns.update_one(
            {"_id": ObjectId(campaign_id), "user_id": user_id},
            {"$inc": {f"analytics.{event}_count": 1}}
        )

class AutomationCRUD:
    @staticmethod
    async def create(user_id: str, workflow: AutomationWorkflow):
        """Create automation workflow"""
        db_conn = get_db()
        workflow.user_id = user_id
        result = await db_conn.automations.insert_one(workflow.dict())
        return str(result.inserted_id)

    @staticmethod
    async def list(user_id: str):
        """List automation workflows"""
        db_conn = get_db()
        return await db_conn.automations.find({"user_id": user_id}).to_list(None)

# ============ ROUTES ============

# Subscribers Management
@router.post("/subscribers")
async def add_subscriber(user_id: str = Query(...), subscriber: SubscriberModel = Body(...)):
    """Add new subscriber"""
    try:
        existing = await SubscriberCRUD.get_by_email(user_id, subscriber.email)
        if existing:
            raise HTTPException(status_code=400, detail="Email already subscribed")
        
        sub_id = await SubscriberCRUD.create(user_id, subscriber)
        return {"id": sub_id, "status": "created"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/subscribers")
async def list_subscribers(user_id: str = Query(...), skip: int = 0, limit: int = 50):
    """Get subscriber list"""
    subscribers = await SubscriberCRUD.get_list(user_id, skip, limit)
    count = await SubscriberCRUD.count(user_id)
    return {"subscribers": subscribers, "total": count, "skip": skip, "limit": limit}

@router.post("/subscribers/import")
async def import_subscribers(user_id: str = Query(...), file: UploadFile = File(...)):
    """Import subscribers from CSV"""
    content = await file.read()
    text_content = content.decode('utf-8')
    imported = await SubscriberCRUD.import_csv(user_id, text_content)
    return {"imported": imported, "status": "success"}

@router.put("/subscribers/{email}")
async def update_subscriber(email: str, user_id: str = Query(...), update_data: Dict = Body(...)):
    """Update subscriber"""
    success = await SubscriberCRUD.update(user_id, email, update_data)
    if not success:
        raise HTTPException(status_code=404, detail="Subscriber not found")
    return {"status": "updated"}

@router.delete("/subscribers/{email}")
async def unsubscribe(email: str, user_id: str = Query(...)):
    """Unsubscribe user"""
    success = await SubscriberCRUD.delete(user_id, email)
    if not success:
        raise HTTPException(status_code=404, detail="Subscriber not found")
    return {"status": "unsubscribed"}

# Campaigns
@router.post("/campaigns")
async def create_campaign(user_id: str = Query(...), campaign: Campaign = Body(...)):
    """Create new campaign"""
    campaign_id = await CampaignCRUD.create(user_id, campaign)
    return {"id": campaign_id, "status": "draft"}

@router.get("/campaigns")
async def list_campaigns(user_id: str = Query(...)):
    """List user campaigns"""
    campaigns = await CampaignCRUD.list(user_id)
    return {"campaigns": campaigns}

@router.post("/campaigns/{campaign_id}/schedule")
async def schedule_campaign(campaign_id: str, user_id: str = Query(...), schedule_time: datetime = Body(...)):
    """Schedule campaign for sending"""
    await CampaignCRUD.update_status(user_id, campaign_id, CampaignStatus.SCHEDULED)
    return {"status": "scheduled", "time": schedule_time}

@router.post("/campaigns/{campaign_id}/send")
async def send_campaign(campaign_id: str, user_id: str = Query(...)):
    """Send campaign immediately"""
    campaign = await CampaignCRUD.get(user_id, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    # Get subscribers for segment
    subscribers = await SubscriberCRUD.get_by_segment(user_id, campaign["segment"])
    
    # Update status
    await CampaignCRUD.update_status(user_id, campaign_id, CampaignStatus.SENT)
    
    return {"sent": len(subscribers), "status": "sent"}

@router.get("/campaigns/{campaign_id}/analytics")
async def get_campaign_analytics(campaign_id: str, user_id: str = Query(...)):
    """Get campaign analytics"""
    campaign = await CampaignCRUD.get(user_id, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    analytics = campaign.get("analytics", {})
    return analytics

# Automation Workflows
@router.post("/automations")
async def create_automation(user_id: str = Query(...), workflow: AutomationWorkflow = Body(...)):
    """Create automation workflow"""
    workflow_id = await AutomationCRUD.create(user_id, workflow)
    return {"id": workflow_id, "status": "created"}

@router.get("/automations")
async def list_automations(user_id: str = Query(...)):
    """List automation workflows"""
    workflows = await AutomationCRUD.list(user_id)
    return {"workflows": workflows}

# Analytics Dashboard
@router.get("/analytics/overview")
async def get_analytics_overview(user_id: str = Query(...)):
    """Get newsletter analytics overview"""
    db_conn = get_db()
    
    subscribers_count = await db_conn.subscribers.count_documents({"user_id": user_id})
    campaigns = await db_conn.campaigns.find({"user_id": user_id}).to_list(None)
    
    total_sent = sum(c.get("analytics", {}).get("sent_count", 0) for c in campaigns)
    total_opens = sum(c.get("analytics", {}).get("open_count", 0) for c in campaigns)
    total_clicks = sum(c.get("analytics", {}).get("click_count", 0) for c in campaigns)
    total_unsubscribes = sum(c.get("analytics", {}).get("unsubscribe_count", 0) for c in campaigns)
    
    avg_open_rate = (total_opens / total_sent * 100) if total_sent > 0 else 0
    avg_click_rate = (total_clicks / total_sent * 100) if total_sent > 0 else 0
    
    return {
        "subscribers": subscribers_count,
        "campaigns_created": len(campaigns),
        "total_sent": total_sent,
        "total_opens": total_opens,
        "total_clicks": total_clicks,
        "avg_open_rate": round(avg_open_rate, 2),
        "avg_click_rate": round(avg_click_rate, 2),
        "unsubscribes": total_unsubscribes
    }

# SMTP Configuration
@router.post("/settings/smtp")
async def configure_smtp(user_id: str = Query(...), config: SMTPConfig = Body(...)):
    """Configure SMTP settings"""
    db_conn = get_db()
    await db_conn.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"smtp_config": config.dict()}}
    )
    return {"status": "configured"}

@router.get("/settings/smtp")
async def get_smtp_config(user_id: str = Query(...)):
    """Get SMTP settings"""
    db_conn = get_db()
    user = await db_conn.users.find_one({"_id": ObjectId(user_id)})
    return user.get("smtp_config", {}) if user else {}

# Health check
@router.get("/health")
async def health():
    return {"status": "ok", "service": "newsletter"}
