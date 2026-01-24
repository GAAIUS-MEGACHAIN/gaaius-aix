"""
Final 4 Services Routes - Live Shopping, E-Commerce, Subscription, Recommendations
"""

from fastapi import APIRouter, HTTPException, Query, Body
from typing import List, Optional, Dict
from datetime import datetime

from backend.final_services import (
    get_live_shopping_service,
    get_ecommerce_service,
    get_subscription_service,
    get_recommendation_engine,
    ShoppingCart,
    Product,
    Order,
    Subscription,
    ExclusiveContent
)

# ============================================================================
# LIVE SHOPPING ROUTES
# ============================================================================

router_live_shopping = APIRouter(prefix="/api/v1/live-shopping", tags=["Live Shopping"])

@router_live_shopping.post("/sessions/create")
async def create_live_session(
    creator_id: str = Query(...),
    title: str = Query(...),
    description: str = Query(...),
    start_time: datetime = Query(...)
):
    """Create live shopping session"""
    service = get_live_shopping_service()
    session = await service.create_session(creator_id, title, description, start_time)
    return {
        "session_id": session.id,
        "stream_id": session.stream_id,
        "status": "scheduled",
        "start_time": start_time
    }

@router_live_shopping.post("/{session_id}/products/add")
async def add_product_to_session(
    session_id: str,
    product_id: str = Query(...),
    name: str = Query(...),
    description: str = Query(...),
    price: float = Query(...),
    stock: int = Query(...),
    discount_percent: float = Query(default=0.0)
):
    """Add product to live session"""
    service = get_live_shopping_service()
    try:
        product = await service.add_product_to_session(
            session_id, product_id, name, description, price, stock, discount_percent
        )
        return {
            "product_id": product.product_id,
            "price": product.price,
            "discount_percent": discount_percent,
            "final_price": product.get_discounted_price(),
            "stock": stock
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router_live_shopping.post("/{session_id}/start")
async def start_live_session(session_id: str):
    """Start live shopping session"""
    service = get_live_shopping_service()
    success = await service.start_session(session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"status": "live"}

@router_live_shopping.post("/{session_id}/viewers/update")
async def update_live_viewers(
    session_id: str,
    user_ids: List[str] = Body(...)
):
    """Update live viewer count"""
    service = get_live_shopping_service()
    await service.update_viewers(session_id, set(user_ids))
    return {"viewer_count": len(user_ids)}

@router_live_shopping.post("/{session_id}/cart/add")
async def add_to_live_cart(
    session_id: str,
    user_id: str = Query(...),
    product_id: str = Query(...),
    quantity: int = Query(default=1)
):
    """Add product to live shopping cart"""
    service = get_live_shopping_service()
    try:
        cart = await service.add_to_cart(user_id, session_id, product_id, quantity)
        return {"status": "added", "item_count": len(cart.items)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router_live_shopping.post("/{session_id}/coupon/apply")
async def apply_live_coupon(
    session_id: str,
    user_id: str = Query(...),
    coupon_code: str = Query(...)
):
    """Apply coupon to live shopping"""
    service = get_live_shopping_service()
    success = await service.apply_coupon(user_id, session_id, coupon_code)
    if not success:
        raise HTTPException(status_code=400, detail="Coupon invalid or session not found")
    return {"status": "applied", "code": coupon_code}

@router_live_shopping.post("/{session_id}/checkout")
async def checkout_live_shopping(
    session_id: str,
    user_id: str = Query(...),
    payment_method: str = Query(...)
):
    """Complete live shopping purchase"""
    service = get_live_shopping_service()
    try:
        result = await service.checkout(user_id, session_id, payment_method)
        return {
            "status": "success",
            "order_id": result['order_id'],
            "total": result['total'],
            "items": result['items']
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router_live_shopping.post("/{session_id}/comment")
async def add_live_comment(
    session_id: str,
    user_id: str = Query(...),
    message: str = Query(...)
):
    """Add chat comment during live"""
    service = get_live_shopping_service()
    await service.add_comment(session_id, user_id, message)
    return {"status": "posted"}

@router_live_shopping.post("/{session_id}/end")
async def end_live_session(session_id: str):
    """End live shopping session"""
    service = get_live_shopping_service()
    try:
        stats = await service.end_session(session_id)
        return stats
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# ============================================================================
# E-COMMERCE ROUTES
# ============================================================================

router_ecommerce = APIRouter(prefix="/api/v1/shop", tags=["E-Commerce"])

@router_ecommerce.post("/products/create")
async def create_product(
    seller_id: str = Query(...),
    name: str = Query(...),
    description: str = Query(...),
    price: float = Query(...),
    cost: float = Query(...),
    stock: int = Query(...),
    category: str = Query(...),
    images: List[str] = Query(...)
):
    """Create product listing"""
    service = get_ecommerce_service()
    product = await service.create_product(
        seller_id, name, description, price, cost, stock, category, images
    )
    return {
        "product_id": product.id,
        "sku": product.sku,
        "status": "active",
        "price": price,
        "stock": stock
    }

@router_ecommerce.get("/cart")
async def get_cart(user_id: str = Query(...)):
    """Get shopping cart"""
    service = get_ecommerce_service()
    cart = await service.get_cart(user_id)
    return {
        "cart_id": cart.id,
        "items": len(cart.items),
        "subtotal": cart.get_subtotal(),
        "item_count": cart.get_item_count()
    }

@router_ecommerce.post("/cart/add")
async def add_to_shopping_cart(
    user_id: str = Query(...),
    product_id: str = Query(...),
    quantity: int = Query(default=1)
):
    """Add item to shopping cart"""
    service = get_ecommerce_service()
    try:
        cart = await service.add_to_cart(user_id, product_id, quantity)
        return {
            "status": "added",
            "items_in_cart": len(cart.items),
            "subtotal": cart.get_subtotal()
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router_ecommerce.post("/checkout")
async def checkout_shop(
    user_id: str = Query(...),
    payment_method: str = Query(...),
    shipping_address: Dict = Body(...)
):
    """Complete checkout"""
    service = get_ecommerce_service()
    try:
        order = await service.checkout(user_id, payment_method, shipping_address)
        return {
            "order_id": order.id,
            "status": "paid",
            "subtotal": order.subtotal,
            "tax": order.tax,
            "shipping": order.shipping_cost,
            "discount": order.discount,
            "total": order.total,
            "items": len(order.items)
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router_ecommerce.post("/{order_id}/ship")
async def ship_order(
    order_id: str,
    carrier: str = Query(...)
):
    """Create shipment for order"""
    service = get_ecommerce_service()
    try:
        shipment = await service.create_shipment(order_id, carrier)
        return {
            "shipment_id": shipment.id,
            "tracking_number": shipment.tracking_number,
            "carrier": carrier,
            "status": "picked",
            "estimated_delivery": shipment.estimated_delivery
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router_ecommerce.post("/shipment/{shipment_id}/update")
async def update_shipment_status(
    shipment_id: str,
    status: str = Query(...),
    location: Optional[str] = Query(None)
):
    """Update shipment status"""
    service = get_ecommerce_service()
    try:
        from backend.final_services import ShipmentStatus
        shipment = await service.update_shipment_status(
            shipment_id, ShipmentStatus(status), location
        )
        return {
            "tracking_number": shipment.tracking_number,
            "status": shipment.status.value,
            "location": location,
            "estimated_delivery": shipment.estimated_delivery
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router_ecommerce.get("/search")
async def search_shop(
    query: str = Query(...),
    category: Optional[str] = Query(None),
    min_price: float = Query(default=0),
    max_price: float = Query(default=999999)
):
    """Search products"""
    service = get_ecommerce_service()
    products = await service.search_products(query, category, min_price, max_price)
    return {
        "results": len(products),
        "products": [
            {
                "product_id": p.id,
                "name": p.name,
                "price": p.price,
                "rating": p.rating,
                "reviews": p.review_count,
                "sales": p.sales_count
            }
            for p in products[:20]
        ]
    }

# ============================================================================
# SUBSCRIPTION / PATREON ROUTES
# ============================================================================

router_subscription = APIRouter(prefix="/api/v1/subscription", tags=["Subscription"])

@router_subscription.post("/tiers/create")
async def create_subscription_tier(
    creator_id: str = Query(...),
    name: str = Query(...),
    description: str = Query(...),
    price: float = Query(...),
    benefits: List[str] = Body(...)
):
    """Create subscription tier"""
    service = get_subscription_service()
    tier = await service.create_tier(creator_id, name, description, price, benefits)
    return {
        "tier_id": tier.id,
        "name": name,
        "price": price,
        "benefits": benefits,
        "members": 0
    }

@router_subscription.post("/subscribe")
async def subscribe_to_creator(
    user_id: str = Query(...),
    creator_id: str = Query(...),
    tier_id: str = Query(...),
    payment_method: str = Query(...)
):
    """Subscribe to creator tier"""
    service = get_subscription_service()
    try:
        subscription = await service.subscribe(user_id, creator_id, tier_id, payment_method)
        return {
            "subscription_id": subscription.id,
            "status": "active",
            "tier": subscription.tier_name,
            "price_per_month": subscription.monthly_price,
            "renews_at": subscription.renews_at
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router_subscription.post("/{creator_id}/exclusive-content/post")
async def post_exclusive_content(
    creator_id: str,
    title: str = Query(...),
    description: str = Query(...),
    content_url: str = Query(...),
    tier_id: Optional[str] = Query(None)
):
    """Post exclusive subscriber content"""
    service = get_subscription_service()
    content = await service.post_exclusive_content(
        creator_id, title, description, content_url, tier_id
    )
    return {
        "content_id": content.id,
        "status": "posted",
        "tier": tier_id or "all",
        "posted_at": content.posted_at
    }

@router_subscription.get("/{creator_id}/exclusive-content")
async def get_exclusive_content(
    creator_id: str,
    user_id: str = Query(...)
):
    """Get accessible exclusive content"""
    service = get_subscription_service()
    content_list = await service.get_exclusive_content(user_id, creator_id)
    return {
        "items": len(content_list),
        "content": [
            {
                "content_id": c.id,
                "title": c.title,
                "posted_at": c.posted_at,
                "views": c.views
            }
            for c in content_list
        ]
    }

@router_subscription.post("/{subscription_id}/cancel")
async def cancel_subscription(subscription_id: str):
    """Cancel subscription"""
    service = get_subscription_service()
    try:
        subscription = await service.cancel_subscription(subscription_id)
        return {
            "status": "cancelled",
            "cancelled_at": subscription.cancelled_at
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router_subscription.get("/{creator_id}/earnings")
async def get_subscription_earnings(creator_id: str):
    """Get creator earnings dashboard"""
    service = get_subscription_service()
    earnings = await service.get_creator_earnings(creator_id)
    return {
        "total_members": earnings['total_members'],
        "monthly_revenue": earnings['monthly_revenue'],
        "tiers": earnings['tiers'],
        "average_tier_price": (
            earnings['monthly_revenue'] / earnings['total_members']
            if earnings['total_members'] > 0 else 0
        )
    }

# ============================================================================
# RECOMMENDATION ENGINE ROUTES
# ============================================================================

router_recommendation = APIRouter(prefix="/api/v1/recommendations", tags=["Recommendations"])

@router_recommendation.post("/track")
async def track_user_engagement(
    user_id: str = Query(...),
    content_id: str = Query(...),
    action: str = Query(...),
    category: str = Query(...),
    time_spent_minutes: int = Query(default=0)
):
    """Track user engagement for recommendations"""
    engine = get_recommendation_engine()
    await engine.track_engagement(user_id, content_id, action, category, time_spent_minutes)
    return {"status": "tracked"}

@router_recommendation.get("/personalized")
async def get_personalized_recommendations(
    user_id: str = Query(...),
    limit: int = Query(default=10, ge=1, le=100)
):
    """Get personalized recommendations"""
    engine = get_recommendation_engine()
    recommendations = await engine.get_personalized_recommendations(user_id, limit)
    return {
        "recommendations": recommendations,
        "count": len(recommendations),
        "user_id": user_id
    }

@router_recommendation.post("/profile/build")
async def build_user_profile(
    user_id: str = Query(...),
    favorite_categories: List[str] = Body(...),
    watch_time_history: Dict[str, int] = Body(...)
):
    """Build initial user profile from preferences"""
    engine = get_recommendation_engine()
    
    # Track initial interests
    for category in favorite_categories:
        await engine.track_engagement(user_id, "", "view", category, 0)
    
    return {
        "status": "profile_created",
        "categories": favorite_categories,
        "ready_for_recommendations": True
    }

@router_recommendation.get("/trending")
async def get_trending_content(limit: int = Query(default=20, le=100)):
    """Get trending content across platform"""
    engine = get_recommendation_engine()
    trending = sorted(
        engine.trending_content.items(),
        key=lambda x: x[1],
        reverse=True
    )[:limit]
    return {
        "trending": [
            {"content_id": cid, "trend_score": score}
            for cid, score in trending
        ]
    }

# ============================================================================
# COMBINED FINAL ROUTES
# ============================================================================

def get_all_final_routers():
    """Get all final 4 service routers"""
    return [
        router_live_shopping,
        router_ecommerce,
        router_subscription,
        router_recommendation
    ]
