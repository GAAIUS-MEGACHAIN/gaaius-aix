"""
Live Shopping Routes - REST API endpoints for shopping system
Handles products, cart, orders, wishlist, and seller operations
"""

from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, Field, validator
from decimal import Decimal
from datetime import datetime

from .live_shopping_service import (
    LiveShoppingService, Product, ShoppingCart, Order, Wishlist,
    SellerSettings, OrderStatus, PaymentMethod, ProductStatus,
    ContentType, CurrencyType, CartItem
)


# ==================== REQUEST/RESPONSE MODELS ====================

class CreateProductRequest(BaseModel):
    """Request to create product"""
    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=10, max_length=5000)
    base_price: Decimal = Field(..., gt=0, decimal_places=2)
    category: str = Field(..., min_length=1)
    thumbnail_url: Optional[str] = None
    images: List[str] = Field(default_factory=list)
    total_inventory: int = Field(default=0, ge=0)
    associated_content_id: Optional[str] = None
    associated_content_type: Optional[str] = None
    discount_percent: Decimal = Field(default=Decimal("0"), ge=0, le=100)
    shipping_cost: Decimal = Field(default=Decimal("0"), ge=0)


class AddToCartRequest(BaseModel):
    """Request to add item to cart"""
    product_id: str = Field(...)
    quantity: int = Field(gt=0, le=100)
    variant_id: Optional[str] = None
    customization_notes: Optional[str] = None


class UpdateCartItemRequest(BaseModel):
    """Request to update cart item"""
    quantity: int = Field(gt=0, le=100)


class CheckoutRequest(BaseModel):
    """Request to checkout"""
    shipping_address: dict = Field(...)
    payment_method: PaymentMethod = Field(...)


class CreateWishlistRequest(BaseModel):
    """Request to create wishlist"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None


class CreateSellerShopRequest(BaseModel):
    """Request to create seller shop"""
    shop_name: str = Field(..., min_length=1, max_length=100)
    shop_description: Optional[str] = None
    seller_email: str = Field(...)
    currency: CurrencyType = Field(default=CurrencyType.USD)


class ProductResponse(BaseModel):
    """Product response"""
    id: str
    name: str
    description: str
    base_price: Decimal
    thumbnail_url: Optional[str]
    status: ProductStatus
    total_inventory: int
    rating: Decimal
    discount_percent: Decimal


class CartResponse(BaseModel):
    """Shopping cart response"""
    id: str
    items_count: int
    subtotal: Decimal
    tax: Decimal
    shipping_cost: Decimal
    total: Decimal


class OrderResponse(BaseModel):
    """Order response"""
    id: str
    status: OrderStatus
    total_amount: Decimal
    items_count: int
    created_at: datetime


class SellerStatsResponse(BaseModel):
    """Seller statistics response"""
    total_products: int
    total_orders: int
    total_sales: Decimal
    monthly_sales: Decimal


# ==================== ROUTERS ====================

# Product Routes
router_products = APIRouter(prefix="/api/products", tags=["Products"])

@router_products.post("/", response_model=dict)
async def create_product(
    request: CreateProductRequest,
    seller_id: str = Query(...),
    service: LiveShoppingService = Depends()
):
    """Create new product"""
    try:
        product = Product(
            seller_id=seller_id,
            name=request.name,
            description=request.description,
            base_price=request.base_price,
            category=request.category,
            thumbnail_url=request.thumbnail_url,
            images=request.images,
            total_inventory=request.total_inventory,
            associated_content_id=request.associated_content_id,
            associated_content_type=request.associated_content_type,
            discount_percent=request.discount_percent,
            shipping_cost=request.shipping_cost
        )
        
        return await service.create_product(product)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router_products.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: str,
    service: LiveShoppingService = Depends()
):
    """Get product details"""
    try:
        product = await service.get_product(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router_products.get("/seller/{seller_id}")
async def get_seller_products(
    seller_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    service: LiveShoppingService = Depends()
):
    """Get products for seller"""
    try:
        products = await service.get_seller_products(seller_id, skip, limit)
        return {"products": products, "count": len(products)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router_products.get("/content/{content_id}")
async def get_products_by_content(
    content_id: str,
    content_type: ContentType = Query(...),
    service: LiveShoppingService = Depends()
):
    """Get products for specific content (livestream, video, music, etc.)"""
    try:
        products = await service.get_products_by_content(content_id, content_type)
        return {"products": products, "count": len(products)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router_products.get("/search")
async def search_products(
    query: str = Query(..., min_length=1),
    category: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    service: LiveShoppingService = Depends()
):
    """Search products"""
    try:
        products = await service.search_products(query, category, skip, limit)
        return {"products": products, "count": len(products)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Shopping Cart Routes
router_cart = APIRouter(prefix="/api/cart", tags=["Shopping Cart"])

@router_cart.get("/{user_id}", response_model=dict)
async def get_user_cart(
    user_id: str,
    service: LiveShoppingService = Depends()
):
    """Get user's shopping cart"""
    try:
        cart = await service.get_or_create_cart(user_id)
        return CartResponse(
            id=cart["id"],
            items_count=len(cart.get("items", [])),
            subtotal=cart.get("subtotal", 0),
            tax=cart.get("tax", 0),
            shipping_cost=cart.get("shipping_cost", 0),
            total=cart.get("total", 0)
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router_cart.post("/{user_id}/add")
async def add_to_cart(
    user_id: str,
    request: AddToCartRequest,
    service: LiveShoppingService = Depends()
):
    """Add product to cart"""
    try:
        result = await service.add_to_cart(
            user_id=user_id,
            product_id=request.product_id,
            quantity=request.quantity,
            variant_id=request.variant_id,
            customization_notes=request.customization_notes
        )
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error"))
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router_cart.delete("/{user_id}/items/{item_id}")
async def remove_from_cart(
    user_id: str,
    item_id: str,
    service: LiveShoppingService = Depends()
):
    """Remove item from cart"""
    try:
        cart = await service.get_or_create_cart(user_id)
        result = await service.remove_from_cart(cart["id"], item_id)
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error"))
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router_cart.put("/{user_id}/items/{item_id}")
async def update_cart_item(
    user_id: str,
    item_id: str,
    request: UpdateCartItemRequest,
    service: LiveShoppingService = Depends()
):
    """Update cart item quantity"""
    try:
        cart = await service.get_or_create_cart(user_id)
        result = await service.update_cart_item_quantity(cart["id"], item_id, request.quantity)
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error"))
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router_cart.delete("/{user_id}/clear")
async def clear_cart(
    user_id: str,
    service: LiveShoppingService = Depends()
):
    """Clear shopping cart"""
    try:
        cart = await service.get_or_create_cart(user_id)
        result = await service.clear_cart(cart["id"])
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error"))
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Orders Routes
router_orders = APIRouter(prefix="/api/orders", tags=["Orders"])

@router_orders.post("/checkout/{user_id}")
async def checkout(
    user_id: str,
    request: CheckoutRequest,
    service: LiveShoppingService = Depends()
):
    """Create order from cart (checkout)"""
    try:
        cart = await service.get_or_create_cart(user_id)
        result = await service.create_order(
            user_id=user_id,
            cart_id=cart["id"],
            shipping_address=request.shipping_address,
            payment_method=request.payment_method
        )
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error"))
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router_orders.get("/{order_id}", response_model=dict)
async def get_order(
    order_id: str,
    service: LiveShoppingService = Depends()
):
    """Get order details"""
    try:
        order = await service.get_order(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        return order
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router_orders.get("/user/{user_id}")
async def get_user_orders(
    user_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    service: LiveShoppingService = Depends()
):
    """Get all orders for user"""
    try:
        orders = await service.get_user_orders(user_id, skip, limit)
        return {"orders": orders, "count": len(orders)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router_orders.get("/seller/{seller_id}")
async def get_seller_orders(
    seller_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    service: LiveShoppingService = Depends()
):
    """Get all orders for seller"""
    try:
        orders = await service.get_seller_orders(seller_id, skip, limit)
        return {"orders": orders, "count": len(orders)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router_orders.put("/{order_id}/status")
async def update_order_status(
    order_id: str,
    status: OrderStatus = Query(...),
    tracking_number: Optional[str] = None,
    service: LiveShoppingService = Depends()
):
    """Update order status"""
    try:
        result = await service.update_order_status(order_id, status, tracking_number)
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error"))
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Wishlist Routes
router_wishlist = APIRouter(prefix="/api/wishlist", tags=["Wishlist"])

@router_wishlist.post("/")
async def create_wishlist(
    user_id: str = Query(...),
    request: CreateWishlistRequest = None,
    service: LiveShoppingService = Depends()
):
    """Create new wishlist"""
    try:
        result = await service.create_wishlist(user_id, request.name, request.description)
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error"))
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router_wishlist.get("/{wishlist_id}")
async def get_wishlist(
    wishlist_id: str,
    service: LiveShoppingService = Depends()
):
    """Get wishlist details"""
    try:
        wishlist = await service.get_wishlist(wishlist_id)
        if not wishlist:
            raise HTTPException(status_code=404, detail="Wishlist not found")
        return wishlist
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router_wishlist.get("/user/{user_id}")
async def get_user_wishlists(
    user_id: str,
    service: LiveShoppingService = Depends()
):
    """Get all wishlists for user"""
    try:
        wishlists = await service.get_user_wishlists(user_id)
        return {"wishlists": wishlists, "count": len(wishlists)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router_wishlist.post("/{wishlist_id}/add/{product_id}")
async def add_to_wishlist(
    wishlist_id: str,
    product_id: str,
    service: LiveShoppingService = Depends()
):
    """Add product to wishlist"""
    try:
        result = await service.add_to_wishlist(wishlist_id, product_id)
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error"))
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router_wishlist.delete("/{wishlist_id}/remove/{product_id}")
async def remove_from_wishlist(
    wishlist_id: str,
    product_id: str,
    service: LiveShoppingService = Depends()
):
    """Remove product from wishlist"""
    try:
        result = await service.remove_from_wishlist(wishlist_id, product_id)
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error"))
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Seller Routes
router_seller = APIRouter(prefix="/api/seller", tags=["Seller Shop"])

@router_seller.post("/shop")
async def create_seller_shop(
    seller_id: str = Query(...),
    request: CreateSellerShopRequest = None,
    service: LiveShoppingService = Depends()
):
    """Create seller shop"""
    try:
        seller_settings = SellerSettings(
            seller_id=seller_id,
            shop_name=request.shop_name,
            shop_description=request.shop_description,
            seller_email=request.seller_email,
            currency=request.currency
        )
        
        result = await service.create_seller_settings(seller_settings)
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error"))
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router_seller.get("/{seller_id}/shop")
async def get_seller_shop(
    seller_id: str,
    service: LiveShoppingService = Depends()
):
    """Get seller shop settings"""
    try:
        settings = await service.get_seller_settings(seller_id)
        if not settings:
            raise HTTPException(status_code=404, detail="Shop not found")
        return settings
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router_seller.get("/{seller_id}/dashboard")
async def get_seller_dashboard(
    seller_id: str,
    service: LiveShoppingService = Depends()
):
    """Get seller dashboard stats"""
    try:
        stats = await service.get_seller_dashboard_stats(seller_id)
        if not stats.get("success"):
            raise HTTPException(status_code=400, detail=stats.get("error"))
        return stats
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router_seller.get("/{seller_id}/earnings")
async def get_seller_earnings(
    seller_id: str,
    service: LiveShoppingService = Depends()
):
    """Get seller earnings summary"""
    try:
        earnings = await service.get_seller_earnings(seller_id)
        if not earnings:
            raise HTTPException(status_code=404, detail="Earnings not found")
        return earnings
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
