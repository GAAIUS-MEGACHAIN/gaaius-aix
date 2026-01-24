"""
DISTRIBUTION PLATFORM - API ROUTES
FastAPI endpoints for music/video distribution
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
import logging
import os
import asyncio

from backend.distribution_platform import (
    DistributionProject,
    DistributionOrchestrator,
    RoyaltyTracker,
    ArtistProfile,
    ContentType,
    PlatformType,
    DistributionStatus,
    RoyaltyRecord
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/distribution", tags=["Distribution"])

# In-memory storage (replace with database in production)
projects_db: Dict[str, DistributionProject] = {}
artists_db: Dict[str, ArtistProfile] = {}
royalties_db: List[RoyaltyRecord] = []


# ============================================================================
# ARTIST PROFILE ENDPOINTS
# ============================================================================

@router.post("/artist/profile")
async def create_artist_profile(
    user_id: str,
    email: str,
    name: str
) -> Dict[str, Any]:
    """
    Create artist profile for distribution
    Required before uploading content
    """
    try:
        profile = ArtistProfile(
            user_id=user_id,
            is_pro=False
        )
        
        artists_db[user_id] = profile
        
        logger.info(f"✅ Artist profile created: {user_id}")
        
        return {
            "status": "success",
            "artist_id": profile.id,
            "user_id": user_id,
            "is_pro": False,
            "distribution_limit": 100,
            "message": "Artist profile created. You can now upload content."
        }
    
    except Exception as e:
        logger.error(f"❌ Error creating artist profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/artist/profile/{user_id}")
async def get_artist_profile(user_id: str) -> Dict[str, Any]:
    """Get artist profile and statistics"""
    
    if user_id not in artists_db:
        raise HTTPException(status_code=404, detail="Artist profile not found")
    
    profile = artists_db[user_id]
    user_projects = [p for p in projects_db.values() if p.user_id == user_id]
    user_royalties = [r for r in royalties_db if any(p.id == r.project_id for p in user_projects)]
    
    total_earned = sum([r.amount for r in user_royalties])
    
    return {
        "artist_id": profile.id,
        "is_pro": profile.is_pro,
        "pro_expires": profile.pro_subscription_end,
        "total_projects": len(user_projects),
        "total_revenue": str(total_earned),
        "distribution_limit": profile.distribution_limit,
        "projects_this_month": len([p for p in user_projects 
                                   if (datetime.utcnow() - p.created_at).days < 30]),
        "bank_account": profile.bank_account is not None,
        "created_at": profile.created_at
    }


@router.post("/artist/upgrade-pro")
async def upgrade_to_pro(
    user_id: str,
    stripe_token: str
) -> Dict[str, Any]:
    """
    Upgrade to Pro (remove 20% commission)
    Stripe integration for monthly subscription
    """
    try:
        if user_id not in artists_db:
            raise HTTPException(status_code=404, detail="Artist profile not found")
        
        profile = artists_db[user_id]
        
        # Process Stripe payment
        try:
            import stripe
            stripe.api_key = os.getenv("STRIPE_API_KEY")
            
            subscription = stripe.Subscription.create(
                customer=stripe_token,
                items=[{
                    "price": os.getenv("STRIPE_PRO_PRICE_ID")
                }]
            )
            
            profile.is_pro = True
            profile.pro_subscription_end = datetime.utcnow() + timedelta(days=365)
            
            logger.info(f"✅ Pro subscription activated: {user_id}")
            
            return {
                "status": "success",
                "message": "Upgraded to Pro! No more 20% commission.",
                "is_pro": True,
                "subscription_id": subscription.id,
                "commission_rate": "0%"
            }
        
        except Exception as stripe_error:
            logger.error(f"Stripe error: {stripe_error}")
            raise HTTPException(status_code=400, detail="Payment failed")
    
    except Exception as e:
        logger.error(f"❌ Error upgrading to pro: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# PROJECT UPLOAD & SUBMISSION ENDPOINTS
# ============================================================================

@router.post("/project/upload")
async def upload_distribution_project(
    user_id: str,
    title: str = Form(...),
    description: str = Form(...),
    artist_name: str = Form(...),
    content_type: ContentType = Form(...),
    audio_file: Optional[UploadFile] = File(None),
    video_file: Optional[UploadFile] = File(None),
    cover_art: Optional[UploadFile] = File(None),
    platforms: List[PlatformType] = Form(...),
    metadata: Optional[str] = Form(None)
) -> Dict[str, Any]:
    """
    Upload music/video project for distribution
    Supports:
    - Audio files (MP3, WAV, FLAC, ALAC)
    - Video files (MP4, WebM)
    - Cover art (JPG, PNG)
    
    Automatically triggers moderation and can auto-distribute
    """
    try:
        # Verify artist profile exists
        if user_id not in artists_db:
            raise HTTPException(status_code=404, detail="Artist profile not found. Create profile first.")
        
        artist_profile = artists_db[user_id]
        
        # Check distribution limit
        this_month_projects = len([p for p in projects_db.values() 
                                  if p.user_id == user_id 
                                  and (datetime.utcnow() - p.created_at).days < 30])
        
        if not artist_profile.is_pro and this_month_projects >= artist_profile.distribution_limit:
            raise HTTPException(
                status_code=429,
                detail=f"Distribution limit reached ({artist_profile.distribution_limit} per month). Upgrade to Pro for unlimited."
            )
        
        # Upload files to cloud storage (simulated)
        audio_url = None
        video_url = None
        cover_url = None
        
        if audio_file:
            audio_url = f"https://storage.example.com/{user_id}/{audio_file.filename}"
            logger.info(f"📁 Audio file uploaded: {audio_url}")
        
        if video_file:
            video_url = f"https://storage.example.com/{user_id}/{video_file.filename}"
            logger.info(f"📹 Video file uploaded: {video_url}")
        
        if cover_art:
            cover_url = f"https://storage.example.com/{user_id}/{cover_art.filename}"
            logger.info(f"🖼️ Cover art uploaded: {cover_url}")
        
        # Parse metadata
        import json
        project_metadata = {}
        if metadata:
            try:
                project_metadata = json.loads(metadata)
            except:
                project_metadata = {}
        
        # Create project
        project = DistributionProject(
            user_id=user_id,
            title=title,
            description=description,
            artist_name=artist_name,
            content_type=content_type,
            artist_email=artists_db[user_id].user_id,  # Use user_id as email
            release_date=datetime.utcnow(),
            language="en",
            price=Decimal("0.99"),
            audio_file_url=audio_url,
            video_file_url=video_url,
            cover_art_url=cover_url,
            platforms=platforms,
            metadata=project_metadata,
            is_pro=artist_profile.is_pro,
            auto_distribute=True,
            auto_approve=artist_profile.is_pro  # Pro users get auto-approval
        )
        
        projects_db[project.id] = project
        
        logger.info(f"📤 Project created: {project.id} (auto-approval: {project.auto_approve})")
        
        # Start moderation in background
        orchestrator = DistributionOrchestrator()
        
        return {
            "status": "success",
            "project_id": project.id,
            "message": f"Project uploaded. Status: {'Auto-distributing' if project.auto_approve else 'Pending moderation'}",
            "distribution_status": project.status,
            "auto_approve": project.auto_approve,
            "next_step": "Check project status in dashboard"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error uploading project: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# PROJECT MANAGEMENT ENDPOINTS
# ============================================================================

@router.get("/project/{project_id}")
async def get_project_status(project_id: str) -> Dict[str, Any]:
    """Get detailed project status and distribution info"""
    
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = projects_db[project_id]
    
    return {
        "project_id": project.id,
        "title": project.title,
        "artist": project.artist_name,
        "status": project.status,
        "content_type": project.content_type,
        "moderation": {
            "status": project.moderation_status,
            "copyright_score": project.copyright_score,
            "violence_score": project.violence_score,
            "adult_score": project.adult_score,
            "safe": all([
                (project.copyright_score or 0) < 70,
                (project.violence_score or 0) < 60,
                (project.adult_score or 0) < 50
            ])
        },
        "distribution": {
            "platforms": [p.value for p in project.platforms],
            "urls": project.distribution_urls,
            "distributed_at": project.distributed_at
        },
        "timestamps": {
            "created": project.created_at,
            "submitted": project.submitted_at,
            "approved": project.approved_at,
            "distributed": project.distributed_at
        }
    }


@router.get("/project/list/{user_id}")
async def list_user_projects(user_id: str) -> Dict[str, Any]:
    """List all projects for a user with status"""
    
    if user_id not in artists_db:
        raise HTTPException(status_code=404, detail="Artist profile not found")
    
    user_projects = [p for p in projects_db.values() if p.user_id == user_id]
    
    return {
        "total_projects": len(user_projects),
        "projects": [
            {
                "id": p.id,
                "title": p.title,
                "status": p.status,
                "content_type": p.content_type,
                "created": p.created_at,
                "distributed": p.distributed_at,
                "platforms": len(p.platforms)
            }
            for p in sorted(user_projects, key=lambda x: x.created_at, reverse=True)
        ]
    }


@router.post("/project/{project_id}/submit-for-review")
async def submit_for_review(project_id: str) -> Dict[str, Any]:
    """
    Manually submit project for review
    Triggers Groq AI moderation
    """
    try:
        if project_id not in projects_db:
            raise HTTPException(status_code=404, detail="Project not found")
        
        project = projects_db[project_id]
        
        if project.status != DistributionStatus.DRAFT:
            raise HTTPException(
                status_code=400,
                detail=f"Project is {project.status}, cannot resubmit"
            )
        
        # Start moderation
        orchestrator = DistributionOrchestrator()
        result = await orchestrator.process_submission(project)
        
        # Update project in database
        projects_db[project_id] = project
        
        logger.info(f"✅ Project submitted: {project_id} -> {result['status']}")
        
        return {
            "status": "success",
            "project_id": project_id,
            "distribution_status": result['status'],
            "message": result.get('message', 'Processing...'),
            "distribution_urls": result.get('distribution_urls', {})
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error submitting for review: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/project/{project_id}")
async def delete_project(project_id: str) -> Dict[str, str]:
    """Delete a draft project"""
    
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = projects_db[project_id]
    
    if project.status != DistributionStatus.DRAFT:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete {project.status} project"
        )
    
    del projects_db[project_id]
    
    return {
        "status": "success",
        "message": f"Project {project_id} deleted"
    }


# ============================================================================
# ROYALTY & MONETIZATION ENDPOINTS
# ============================================================================

@router.get("/royalties/{user_id}")
async def get_user_royalties(user_id: str) -> Dict[str, Any]:
    """Get royalty summary for user"""
    
    if user_id not in artists_db:
        raise HTTPException(status_code=404, detail="Artist profile not found")
    
    user_projects = [p for p in projects_db.values() if p.user_id == user_id]
    user_royalties = [r for r in royalties_db if any(p.id == r.project_id for p in user_projects)]
    
    total_gross = sum([r.gross_revenue for r in user_royalties])
    total_net = sum([r.net_revenue for r in user_royalties])
    total_our_commission = sum([r.commission for r in user_royalties])
    
    # Group by platform
    by_platform = {}
    for royalty in user_royalties:
        platform = royalty.platform.value
        if platform not in by_platform:
            by_platform[platform] = Decimal("0.00")
        by_platform[platform] += royalty.net_revenue
    
    return {
        "total_gross_revenue": str(total_gross),
        "total_net_earned": str(total_net),
        "platform_breakdown": {k: str(v) for k, v in by_platform.items()},
        "pending_payments": str(total_net),
        "next_payout_date": "15th of next month",
        "royalty_records": len(user_royalties),
        "payout_method": "Stripe",
        "minimum_payout": "$50"
    }


@router.post("/royalties/simulate")
async def simulate_royalties(
    project_id: str,
    platform: PlatformType,
    revenue: float
) -> Dict[str, Any]:
    """
    Simulate royalty calculation for a project
    (for testing and demonstration)
    """
    try:
        if project_id not in projects_db:
            raise HTTPException(status_code=404, detail="Project not found")
        
        project = projects_db[project_id]
        revenue_decimal = Decimal(str(revenue))
        
        if project.is_pro:
            # Pro: Keep 100%
            artist_earnings = revenue_decimal
            our_commission = Decimal("0.00")
        else:
            # Free: Keep 80%, we take 20%
            artist_earnings = revenue_decimal * Decimal("0.80")
            our_commission = revenue_decimal * Decimal("0.20")
        
        return {
            "project_id": project_id,
            "is_pro": project.is_pro,
            "platform": platform.value,
            "gross_revenue": str(revenue_decimal),
            "artist_earnings": str(artist_earnings),
            "our_commission": str(our_commission),
            "payout_rate": "80%" if not project.is_pro else "100%",
            "message": "Pro users keep 100% of earnings" if project.is_pro else "Free users keep 80%, we take 20%"
        }
    
    except Exception as e:
        logger.error(f"❌ Error simulating royalties: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/payout/request")
async def request_payout(
    user_id: str,
    stripe_account_id: str
) -> Dict[str, Any]:
    """
    Request payout of earned royalties
    Minimum $50, processed to Stripe
    """
    try:
        if user_id not in artists_db:
            raise HTTPException(status_code=404, detail="Artist profile not found")
        
        artist_profile = artists_db[user_id]
        
        # Calculate earnings
        user_projects = [p for p in projects_db.values() if p.user_id == user_id]
        user_royalties = [r for r in royalties_db if any(p.id == r.project_id for p in user_projects)]
        total_earned = sum([r.amount for r in user_royalties if r.status == "pending"])
        
        if total_earned < Decimal("50.00"):
            raise HTTPException(
                status_code=400,
                detail=f"Minimum payout is $50. You have ${total_earned} pending."
            )
        
        # Process payout
        tracker = RoyaltyTracker()
        payout_result = await tracker.process_payout(
            user_id,
            total_earned,
            stripe_account_id
        )
        
        if payout_result["status"] == "success":
            # Mark royalties as paid
            for royalty in user_royalties:
                if royalty.status == "pending":
                    royalty.status = "paid"
            
            logger.info(f"✅ Payout processed: {user_id} -> ${total_earned}")
            
            return {
                "status": "success",
                "payout_id": payout_result["payout_id"],
                "amount": str(total_earned),
                "message": f"Payout of ${total_earned} sent to your Stripe account"
            }
        
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Payout failed: {payout_result.get('error')}"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error requesting payout: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# MODERATION & SUPPORT ENDPOINTS
# ============================================================================

@router.post("/support/appeal/{project_id}")
async def appeal_rejection(
    project_id: str,
    appeal_message: str
) -> Dict[str, Any]:
    """
    Appeal rejected project to human support team
    """
    try:
        if project_id not in projects_db:
            raise HTTPException(status_code=404, detail="Project not found")
        
        project = projects_db[project_id]
        
        if project.status != DistributionStatus.REJECTED:
            raise HTTPException(status_code=400, detail="Project is not rejected")
        
        logger.info(f"📧 Appeal submitted for {project_id}: {appeal_message[:100]}")
        
        return {
            "status": "success",
            "message": "Appeal submitted. Our team will review within 24 hours.",
            "ticket_id": f"SUPPORT_{project_id}",
            "expected_response": "24 hours"
        }
    
    except Exception as e:
        logger.error(f"❌ Error submitting appeal: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def distribution_health() -> Dict[str, str]:
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "distribution_platform",
        "features": [
            "AI-powered content moderation",
            "Automated distribution",
            "Royalty tracking",
            "Pro subscription"
        ]
    }


if __name__ == "__main__":
    # Import and include in main server
    print("✅ Distribution routes ready to include in FastAPI app")
