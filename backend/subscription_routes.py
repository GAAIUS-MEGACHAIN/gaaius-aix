"""
Subscription/Patreon REST API Endpoints
25+ endpoints for complete subscriber management and content delivery
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from typing import List, Optional, Dict, Any
from datetime import datetime

try:
    from .subscription_service import (
        SubscriptionService,
        SubscriptionTierModel,
        SubscriberModel,
        SubscriptionModel,
        PaymentModel,
        ExclusiveContentModel,
        ContentAccessModel,
        SubscriptionStatus,
        PaymentStatus,
        ContentType,
        BillingPeriod
    )
except ImportError:
    from subscription_service import (
        SubscriptionService,
        SubscriptionTierModel,
        SubscriberModel,
        SubscriptionModel,
        PaymentModel,
        ExclusiveContentModel,
        ContentAccessModel,
        SubscriptionStatus,
        PaymentStatus,
        ContentType,
        BillingPeriod
    )

router = APIRouter(prefix="/api/subscriptions", tags=["subscriptions"])


# ============================================================================
# DEPENDENCY INJECTION
# ============================================================================

async def get_subscription_service() -> SubscriptionService:
    """Get subscription service from app state"""
    from fastapi import Request
    from starlette.requests import Request as StarletteRequest
    # Will be provided via dependency in main server
    pass


# ============================================================================
# TIER MANAGEMENT (5 endpoints)
# ============================================================================

@router.post("/tiers", response_model=SubscriptionTierModel, status_code=201)
async def create_tier(
    creator_id: str = Query(..., description="Creator ID"),
    tier_data: Dict[str, Any] = Body(...),
    service: SubscriptionService = Depends(get_subscription_service)
):
    """Create a new subscription tier (e.g., Basic, Pro, VIP)"""
    try:
        tier = await service.create_tier(creator_id, tier_data)
        return tier
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/tiers", response_model=List[SubscriptionTierModel])
async def list_tiers(
    creator_id: str = Query(...),
    service: SubscriptionService = Depends(get_subscription_service)
):
    """List all tiers for a creator"""
    return await service.list_tiers(creator_id)


@router.get("/tiers/{tier_id}", response_model=SubscriptionTierModel)
async def get_tier(
    tier_id: str,
    service: SubscriptionService = Depends(get_subscription_service)
):
    """Get tier details"""
    tier = await service.get_tier(tier_id)
    if not tier:
        raise HTTPException(status_code=404, detail="Tier not found")
    return tier


@router.put("/tiers/{tier_id}", response_model=SubscriptionTierModel)
async def update_tier(
    tier_id: str,
    updates: Dict[str, Any] = Body(...),
    service: SubscriptionService = Depends(get_subscription_service)
):
    """Update tier information"""
    tier = await service.update_tier(tier_id, updates)
    if not tier:
        raise HTTPException(status_code=404, detail="Tier not found")
    return tier


@router.delete("/tiers/{tier_id}", status_code=204)
async def deactivate_tier(
    tier_id: str,
    service: SubscriptionService = Depends(get_subscription_service)
):
    """Deactivate a tier"""
    success = await service.deactivate_tier(tier_id)
    if not success:
        raise HTTPException(status_code=404, detail="Tier not found")
    return None


# ============================================================================
# SUBSCRIBER MANAGEMENT (5 endpoints)
# ============================================================================

@router.post("/subscribers", response_model=SubscriberModel, status_code=201)
async def register_subscriber(
    creator_id: str = Query(...),
    sub_data: Dict[str, Any] = Body(...),
    service: SubscriptionService = Depends(get_subscription_service)
):
    """Register a new subscriber"""
    try:
        user_id = sub_data.get("user_id")
        if not user_id:
            raise ValueError("user_id required")
        subscriber = await service.create_subscriber(creator_id, user_id, sub_data)
        return subscriber
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/subscribers", response_model=List[SubscriberModel])
async def list_subscribers(
    creator_id: str = Query(...),
    tier: Optional[str] = Query(None),
    service: SubscriptionService = Depends(get_subscription_service)
):
    """List all subscribers for a creator"""
    return await service.list_subscribers(creator_id, tier)


@router.get("/subscribers/{subscriber_id}", response_model=SubscriberModel)
async def get_subscriber(
    subscriber_id: str,
    service: SubscriptionService = Depends(get_subscription_service)
):
    """Get subscriber profile"""
    subscriber = await service.get_subscriber(subscriber_id)
    if not subscriber:
        raise HTTPException(status_code=404, detail="Subscriber not found")
    return subscriber


@router.put("/subscribers/{subscriber_id}", response_model=SubscriberModel)
async def update_subscriber(
    subscriber_id: str,
    updates: Dict[str, Any] = Body(...),
    service: SubscriptionService = Depends(get_subscription_service)
):
    """Update subscriber profile"""
    subscriber = await service.update_subscriber(subscriber_id, updates)
    if not subscriber:
        raise HTTPException(status_code=404, detail="Subscriber not found")
    return subscriber


@router.get("/subscribers/{subscriber_id}/analytics", response_model=Dict[str, Any])
async def get_subscriber_analytics(
    subscriber_id: str,
    service: SubscriptionService = Depends(get_subscription_service)
):
    """Get subscriber activity analytics"""
    return await service.get_subscriber_analytics(subscriber_id)


# ============================================================================
# SUBSCRIPTION LIFECYCLE (8 endpoints)
# ============================================================================

@router.post("/subscriptions", response_model=SubscriptionModel, status_code=201)
async def create_subscription(
    creator_id: str = Query(...),
    subscriber_id: str = Query(...),
    tier_id: str = Query(...),
    payment_method: str = Query(..., description="stripe, paypal, bank_transfer"),
    billing_period: str = Query("monthly"),
    service: SubscriptionService = Depends(get_subscription_service)
):
    """Create a new subscription"""
    try:
        subscription = await service.create_subscription(
            creator_id,
            subscriber_id,
            tier_id,
            payment_method,
            BillingPeriod(billing_period)
        )
        return subscription
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/subscriptions", response_model=List[SubscriptionModel])
async def list_subscriptions(
    creator_id: str = Query(...),
    status: Optional[str] = Query(None),
    service: SubscriptionService = Depends(get_subscription_service)
):
    """List subscriptions for a creator"""
    return await service.list_subscriptions(creator_id, status)


@router.get("/subscriptions/{subscription_id}", response_model=SubscriptionModel)
async def get_subscription(
    subscription_id: str,
    service: SubscriptionService = Depends(get_subscription_service)
):
    """Get subscription details"""
    subscription = await service.get_subscription(subscription_id)
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return subscription


@router.post("/subscriptions/{subscription_id}/activate", response_model=SubscriptionModel)
async def activate_subscription(
    subscription_id: str,
    service: SubscriptionService = Depends(get_subscription_service)
):
    """Activate a pending subscription"""
    subscription = await service.activate_subscription(subscription_id)
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return subscription


@router.post("/subscriptions/{subscription_id}/cancel", response_model=SubscriptionModel)
async def cancel_subscription(
    subscription_id: str,
    immediately: bool = Query(False, description="Cancel immediately or at period end"),
    service: SubscriptionService = Depends(get_subscription_service)
):
    """Cancel a subscription"""
    subscription = await service.cancel_subscription(subscription_id, immediately)
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return subscription


@router.post("/subscriptions/{subscription_id}/pause", response_model=SubscriptionModel)
async def pause_subscription(
    subscription_id: str,
    service: SubscriptionService = Depends(get_subscription_service)
):
    """Pause a subscription"""
    subscription = await service.pause_subscription(subscription_id)
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return subscription


@router.post("/subscriptions/{subscription_id}/resume", response_model=SubscriptionModel)
async def resume_subscription(
    subscription_id: str,
    service: SubscriptionService = Depends(get_subscription_service)
):
    """Resume a paused subscription"""
    subscription = await service.resume_subscription(subscription_id)
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return subscription


# ============================================================================
# PAYMENT PROCESSING (4 endpoints)
# ============================================================================

@router.post("/payments/process", response_model=PaymentModel, status_code=201)
async def process_payment(
    subscription_id: str = Query(...),
    service: SubscriptionService = Depends(get_subscription_service)
):
    """Process a subscription payment"""
    try:
        payment = await service.process_payment(subscription_id)
        return payment
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/subscriptions/{subscription_id}/payments", response_model=List[PaymentModel])
async def get_payment_history(
    subscription_id: str,
    service: SubscriptionService = Depends(get_subscription_service)
):
    """Get payment history for a subscription"""
    return await service.get_payment_history(subscription_id)


@router.post("/payments/{payment_id}/refund", response_model=PaymentModel)
async def refund_payment(
    payment_id: str,
    service: SubscriptionService = Depends(get_subscription_service)
):
    """Refund a payment"""
    payment = await service.refund_payment(payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment


@router.get("/creator/{creator_id}/dashboard", response_model=Dict[str, Any])
async def get_creator_dashboard(
    creator_id: str,
    service: SubscriptionService = Depends(get_subscription_service)
):
    """Get creator dashboard with revenue metrics"""
    return await service.get_creator_dashboard(creator_id)


# ============================================================================
# CONTENT MANAGEMENT (7 endpoints)
# ============================================================================

@router.post("/content", response_model=ExclusiveContentModel, status_code=201)
async def create_content(
    creator_id: str = Query(...),
    content_data: Dict[str, Any] = Body(...),
    service: SubscriptionService = Depends(get_subscription_service)
):
    """Create exclusive content"""
    try:
        content = await service.create_content(creator_id, content_data)
        return content
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/content", response_model=List[ExclusiveContentModel])
async def list_content(
    creator_id: str = Query(...),
    published_only: bool = Query(True),
    service: SubscriptionService = Depends(get_subscription_service)
):
    """List content for a creator"""
    return await service.list_content(creator_id, published_only)


@router.get("/content/{content_id}", response_model=ExclusiveContentModel)
async def get_content(
    content_id: str,
    service: SubscriptionService = Depends(get_subscription_service)
):
    """Get content details"""
    content = await service.get_content(content_id)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    return content


@router.put("/content/{content_id}", response_model=ExclusiveContentModel)
async def update_content(
    content_id: str,
    updates: Dict[str, Any] = Body(...),
    service: SubscriptionService = Depends(get_subscription_service)
):
    """Update content"""
    content = await service.update_content(content_id, updates)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    return content


@router.delete("/content/{content_id}", status_code=204)
async def delete_content(
    content_id: str,
    service: SubscriptionService = Depends(get_subscription_service)
):
    """Delete content"""
    success = await service.delete_content(content_id)
    if not success:
        raise HTTPException(status_code=404, detail="Content not found")
    return None


@router.get("/subscribers/{subscriber_id}/content", response_model=List[ExclusiveContentModel])
async def get_accessible_content(
    subscriber_id: str,
    service: SubscriptionService = Depends(get_subscription_service)
):
    """Get content accessible to subscriber (based on tier)"""
    return await service.get_accessible_content(subscriber_id)


@router.post("/content/{content_id}/access", response_model=Dict[str, Any])
async def access_content(
    content_id: str,
    subscriber_id: str = Query(...),
    service: SubscriptionService = Depends(get_subscription_service)
):
    """Record and verify content access"""
    # Check access permission
    can_access = await service.can_access_content(subscriber_id, content_id)
    if not can_access:
        raise HTTPException(status_code=403, detail="Access denied - insufficient tier")

    # Record the access
    access = await service.record_access(subscriber_id, content_id)
    return {
        "content_id": content_id,
        "subscriber_id": subscriber_id,
        "access_granted": True,
        "view_count": access.view_count if access else 1
    }


# ============================================================================
# CONTENT ACCESS CONTROL (2 endpoints)
# ============================================================================

@router.get("/subscribers/{subscriber_id}/content/{content_id}/can-access", response_model=Dict[str, Any])
async def check_content_access(
    subscriber_id: str,
    content_id: str,
    service: SubscriptionService = Depends(get_subscription_service)
):
    """Check if subscriber can access content"""
    can_access = await service.can_access_content(subscriber_id, content_id)
    content = await service.get_content(content_id)
    subscriber = await service.get_subscriber(subscriber_id)

    return {
        "can_access": can_access,
        "subscriber_tier": subscriber.current_tier if subscriber else None,
        "required_tier": content.min_tier_required if content else None,
        "reason": "OK" if can_access else "Insufficient subscription tier"
    }


@router.post("/subscribers/{subscriber_id}/content/{content_id}/view", status_code=200)
async def record_view(
    subscriber_id: str,
    content_id: str,
    duration_seconds: Optional[int] = Query(None),
    service: SubscriptionService = Depends(get_subscription_service)
):
    """Record that subscriber viewed content"""
    # Check access
    can_access = await service.can_access_content(subscriber_id, content_id)
    if not can_access:
        raise HTTPException(status_code=403, detail="Access denied")

    # Record view
    await service.record_access(subscriber_id, content_id)

    return {
        "status": "recorded",
        "message": "View recorded successfully"
    }


# ============================================================================
# WEBHOOK HANDLERS (Optional - for payment gateway callbacks)
# ============================================================================

@router.post("/webhooks/stripe")
async def stripe_webhook(
    body: Dict[str, Any] = Body(...),
    service: SubscriptionService = Depends(get_subscription_service)
):
    """Handle Stripe webhook events"""
    event_type = body.get("type")

    if event_type == "customer.subscription.updated":
        # Handle subscription updated
        pass
    elif event_type == "customer.subscription.deleted":
        # Handle subscription cancelled
        pass
    elif event_type == "invoice.payment_succeeded":
        # Handle payment success
        pass
    elif event_type == "invoice.payment_failed":
        # Handle payment failure
        pass

    return {"status": "received"}


@router.post("/webhooks/paypal")
async def paypal_webhook(
    body: Dict[str, Any] = Body(...),
    service: SubscriptionService = Depends(get_subscription_service)
):
    """Handle PayPal webhook events"""
    event_type = body.get("event_type")

    if event_type == "BILLING.SUBSCRIPTION.UPDATED":
        pass
    elif event_type == "BILLING.SUBSCRIPTION.CANCELLED":
        pass
    elif event_type == "PAYMENT.CAPTURE.COMPLETED":
        pass

    return {"status": "received"}


# ============================================================================
# CONVENIENCE ENDPOINTS
# ============================================================================

@router.get("/health")
async def subscription_health():
    """Health check for subscription service"""
    return {
        "status": "healthy",
        "service": "subscription",
        "endpoints": 25
    }
