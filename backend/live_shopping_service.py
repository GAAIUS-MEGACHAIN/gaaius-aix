"""
Live Shopping Service - Complete shopping system for livestreams, videos, music, movies
Enables shopping while watching content with floating cart, wishlist, and order tracking
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from enum import Enum
from decimal import Decimal
import uuid

from pydantic import BaseModel, Field, validator
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
import pymongo


# ==================== ENUMS ====================

class ProductStatus(str, Enum):
    """Product availability status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    OUT_OF_STOCK = "out_of_stock"
    DISCONTINUED = "discontinued"
    LIMITED = "limited"


class ShoppingCartStatus(str, Enum):
    """Shopping cart status"""
    ACTIVE = "active"
    ABANDONED = "abandoned"
    COMPLETED = "completed"
    PENDING = "pending"


class OrderStatus(str, Enum):
    """Order status"""
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    RETURNED = "returned"


class PaymentStatus(str, Enum):
    """Payment status"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    DISPUTED = "disputed"


class ContentType(str, Enum):
    """Content types where shopping is available"""
    LIVESTREAM = "livestream"
    VIDEO = "video"
    MUSIC = "music"
    MOVIE = "movie"
    PODCAST = "podcast"
    EVENT = "event"
    COURSE = "course"
    CHAT = "chat"


class PaymentMethod(str, Enum):
    """Payment methods"""
    PAYPAL = "paypal"
    STRIPE = "stripe"
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    DIGITAL_WALLET = "digital_wallet"
    BANK_TRANSFER = "bank_transfer"
    CRYPTO = "crypto"
    BUY_NOW_PAY_LATER = "bnpl"


class CurrencyType(str, Enum):
    """Supported currencies"""
    USD = "usd"
    EUR = "eur"
    GBP = "gbp"
    ZAR = "zar"
    NGN = "ngn"
    KES = "kes"
    JPY = "jpy"
    INR = "inr"
    ETH = "eth"
    BTC = "btc"


# ==================== DATA MODELS ====================

class ProductVariant(BaseModel):
    """Product variant (size, color, etc.)"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., min_length=1, max_length=100)
    value: str = Field(..., min_length=1, max_length=100)
    sku: str = Field(..., min_length=1, max_length=50)
    price_adjustment: Decimal = Field(default=Decimal("0"), decimal_places=2)
    inventory_count: int = Field(default=0, ge=0)
    image_url: Optional[str] = None


class Product(BaseModel):
    """Product model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    seller_id: str = Field(..., description="Creator/seller ID")
    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=10, max_length=5000)
    base_price: Decimal = Field(..., gt=0, decimal_places=2)
    currency: CurrencyType = Field(default=CurrencyType.USD)
    status: ProductStatus = Field(default=ProductStatus.ACTIVE)
    
    # Media
    thumbnail_url: Optional[str] = None
    images: List[str] = Field(default_factory=list)
    video_url: Optional[str] = None
    
    # Inventory
    total_inventory: int = Field(default=0, ge=0)
    low_stock_threshold: int = Field(default=10, ge=0)
    variants: List[ProductVariant] = Field(default_factory=list)
    
    # Content association
    associated_content_id: Optional[str] = None
    associated_content_type: Optional[ContentType] = None
    
    # Metadata
    category: str = Field(..., min_length=1, max_length=50)
    tags: List[str] = Field(default_factory=list)
    rating: Decimal = Field(default=Decimal("0"), ge=0, le=5, decimal_places=1)
    reviews_count: int = Field(default=0, ge=0)
    
    # Promotions
    discount_percent: Decimal = Field(default=Decimal("0"), ge=0, le=100, decimal_places=2)
    flash_sale: bool = Field(default=False)
    flash_sale_end: Optional[datetime] = None
    
    # Shipping
    weight_kg: Optional[Decimal] = None
    shipping_cost: Decimal = Field(default=Decimal("0"), decimal_places=2)
    free_shipping_over: Optional[Decimal] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('base_price', 'discount_percent', 'shipping_cost', 'free_shipping_over', pre=True)
    def convert_to_decimal(cls, v):
        if isinstance(v, (int, float)):
            return Decimal(str(v))
        return v


class CartItem(BaseModel):
    """Item in shopping cart"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    product_id: str
    quantity: int = Field(gt=0, le=100)
    variant_id: Optional[str] = None
    variant_values: Dict[str, str] = Field(default_factory=dict)
    unit_price: Decimal = Field(decimal_places=2)
    total_price: Decimal = Field(decimal_places=2)
    added_at: datetime = Field(default_factory=datetime.utcnow)
    customization_notes: Optional[str] = None


class ShoppingCart(BaseModel):
    """Shopping cart"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    items: List[CartItem] = Field(default_factory=list)
    status: ShoppingCartStatus = Field(default=ShoppingCartStatus.ACTIVE)
    
    # Cart calculations
    subtotal: Decimal = Field(default=Decimal("0"), decimal_places=2)
    tax: Decimal = Field(default=Decimal("0"), decimal_places=2)
    shipping_cost: Decimal = Field(default=Decimal("0"), decimal_places=2)
    discount: Decimal = Field(default=Decimal("0"), decimal_places=2)
    total: Decimal = Field(default=Decimal("0"), decimal_places=2)
    
    # Context
    current_content_id: Optional[str] = None
    current_content_type: Optional[ContentType] = None
    currency: CurrencyType = Field(default=CurrencyType.USD)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    abandoned_at: Optional[datetime] = None


class OrderItem(BaseModel):
    """Item in order"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    product_id: str
    product_name: str
    quantity: int = Field(gt=0)
    unit_price: Decimal = Field(decimal_places=2)
    total_price: Decimal = Field(decimal_places=2)
    variant_id: Optional[str] = None
    variant_values: Dict[str, str] = Field(default_factory=dict)


class Order(BaseModel):
    """Order model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    seller_id: str
    items: List[OrderItem]
    
    # Pricing
    subtotal: Decimal = Field(decimal_places=2)
    tax: Decimal = Field(decimal_places=2)
    shipping_cost: Decimal = Field(decimal_places=2)
    discount: Decimal = Field(decimal_places=2)
    total_amount: Decimal = Field(decimal_places=2)
    currency: CurrencyType = Field(default=CurrencyType.USD)
    
    # Status tracking
    status: OrderStatus = Field(default=OrderStatus.PENDING)
    payment_status: PaymentStatus = Field(default=PaymentStatus.PENDING)
    payment_method: PaymentMethod
    
    # Shipping
    shipping_address: Dict[str, str]
    tracking_number: Optional[str] = None
    estimated_delivery: Optional[datetime] = None
    
    # Content context
    purchased_from_content_id: Optional[str] = None
    purchased_from_content_type: Optional[ContentType] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    shipped_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None


class Wishlist(BaseModel):
    """Wishlist model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    items: List[str] = Field(default_factory=list)  # Product IDs
    is_public: bool = Field(default=False)
    is_shareable: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class SellerSettings(BaseModel):
    """Seller/creator shop settings"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    seller_id: str
    shop_name: str = Field(..., min_length=1, max_length=100)
    shop_description: Optional[str] = None
    shop_logo: Optional[str] = None
    shop_banner: Optional[str] = None
    
    # Shop configuration
    currency: CurrencyType = Field(default=CurrencyType.USD)
    tax_rate: Decimal = Field(default=Decimal("0"), ge=0, le=100, decimal_places=2)
    platform_fee_percent: Decimal = Field(default=Decimal("5"), ge=0, le=20, decimal_places=2)
    shipping_available: bool = Field(default=True)
    international_shipping: bool = Field(default=False)
    
    # Seller info
    seller_email: str
    seller_phone: Optional[str] = None
    seller_address: Dict[str, str] = Field(default_factory=dict)
    bank_account: Optional[Dict[str, str]] = None
    
    # Status
    is_active: bool = Field(default=True)
    is_verified: bool = Field(default=False)
    is_featured: bool = Field(default=False)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class SellerEarnings(BaseModel):
    """Seller earnings summary"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    seller_id: str
    total_orders: int = Field(default=0)
    total_sales: Decimal = Field(default=Decimal("0"), decimal_places=2)
    total_refunds: Decimal = Field(default=Decimal("0"), decimal_places=2)
    total_earnings: Decimal = Field(default=Decimal("0"), decimal_places=2)
    
    # Period earnings
    monthly_sales: Decimal = Field(default=Decimal("0"), decimal_places=2)
    yearly_sales: Decimal = Field(default=Decimal("0"), decimal_places=2)
    
    # Metrics
    average_order_value: Decimal = Field(default=Decimal("0"), decimal_places=2)
    conversion_rate: Decimal = Field(default=Decimal("0"), decimal_places=2)
    returned_rate: Decimal = Field(default=Decimal("0"), decimal_places=2)
    
    # Payout
    pending_payout: Decimal = Field(default=Decimal("0"), decimal_places=2)
    next_payout_date: Optional[datetime] = None
    
    # Timestamps
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# ==================== SERVICE ====================

class LiveShoppingService:
    """Complete Live Shopping Service"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        """Initialize service with database"""
        self.db = db
        self.products_collection = db["live_shopping_products"]
        self.carts_collection = db["live_shopping_carts"]
        self.orders_collection = db["live_shopping_orders"]
        self.wishlists_collection = db["live_shopping_wishlists"]
        self.seller_settings_collection = db["live_shopping_seller_settings"]
        self.seller_earnings_collection = db["live_shopping_seller_earnings"]
        self.cart_items_collection = db["live_shopping_cart_items"]
        self.order_items_collection = db["live_shopping_order_items"]
        
    async def create_indices(self):
        """Create database indices for performance"""
        try:
            await self.products_collection.create_index([("seller_id", pymongo.ASCENDING)])
            await self.products_collection.create_index([("status", pymongo.ASCENDING)])
            await self.products_collection.create_index([("associated_content_id", pymongo.ASCENDING)])
            await self.products_collection.create_index([("category", pymongo.ASCENDING)])
            
            await self.carts_collection.create_index([("user_id", pymongo.ASCENDING)])
            await self.carts_collection.create_index([("status", pymongo.ASCENDING)])
            
            await self.orders_collection.create_index([("user_id", pymongo.ASCENDING)])
            await self.orders_collection.create_index([("seller_id", pymongo.ASCENDING)])
            await self.orders_collection.create_index([("status", pymongo.ASCENDING)])
            
            await self.wishlists_collection.create_index([("user_id", pymongo.ASCENDING)])
            await self.seller_settings_collection.create_index([("seller_id", pymongo.ASCENDING)])
            
        except Exception as e:
            print(f"Error creating indices: {e}")
    
    # ==================== PRODUCT OPERATIONS ====================
    
    async def create_product(self, product: Product) -> Dict[str, Any]:
        """Create new product"""
        try:
            product_dict = product.dict()
            product_dict["created_at"] = datetime.utcnow()
            product_dict["updated_at"] = datetime.utcnow()
            
            result = await self.products_collection.insert_one(product_dict)
            
            return {
                "success": True,
                "product_id": str(product.id),
                "message": f"Product '{product.name}' created successfully"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_product(self, product_id: str) -> Optional[Dict]:
        """Get product details"""
        try:
            product = await self.products_collection.find_one({"id": product_id})
            return product
        except Exception as e:
            return None
    
    async def get_seller_products(self, seller_id: str, skip: int = 0, limit: int = 50) -> List[Dict]:
        """Get all products for seller"""
        try:
            products = await self.products_collection.find(
                {"seller_id": seller_id}
            ).skip(skip).limit(limit).to_list(length=limit)
            return products
        except Exception as e:
            return []
    
    async def get_products_by_content(self, content_id: str, content_type: str) -> List[Dict]:
        """Get products associated with content (video, livestream, music, etc.)"""
        try:
            products = await self.products_collection.find(
                {
                    "associated_content_id": content_id,
                    "associated_content_type": content_type,
                    "status": ProductStatus.ACTIVE
                }
            ).to_list(length=None)
            return products
        except Exception as e:
            return []
    
    async def search_products(self, query: str, category: Optional[str] = None, 
                             skip: int = 0, limit: int = 50) -> List[Dict]:
        """Search products"""
        try:
            search_filter = {
                "status": ProductStatus.ACTIVE,
                "$text": {"$search": query}
            }
            if category:
                search_filter["category"] = category
            
            products = await self.products_collection.find(search_filter).skip(skip).limit(limit).to_list(length=limit)
            return products
        except Exception as e:
            return []
    
    async def update_product_inventory(self, product_id: str, quantity_change: int) -> bool:
        """Update product inventory"""
        try:
            await self.products_collection.update_one(
                {"id": product_id},
                {
                    "$inc": {"total_inventory": quantity_change},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
            return True
        except Exception as e:
            return False
    
    # ==================== SHOPPING CART OPERATIONS ====================
    
    async def get_or_create_cart(self, user_id: str) -> Dict[str, Any]:
        """Get existing cart or create new one"""
        try:
            cart = await self.carts_collection.find_one(
                {"user_id": user_id, "status": ShoppingCartStatus.ACTIVE}
            )
            
            if cart:
                return cart
            
            # Create new cart
            new_cart = ShoppingCart(user_id=user_id)
            cart_dict = new_cart.dict()
            
            await self.carts_collection.insert_one(cart_dict)
            return cart_dict
        except Exception as e:
            return {"error": str(e)}
    
    async def add_to_cart(self, user_id: str, product_id: str, quantity: int,
                         variant_id: Optional[str] = None,
                         variant_values: Optional[Dict] = None,
                         customization_notes: Optional[str] = None) -> Dict[str, Any]:
        """Add product to cart"""
        try:
            # Get product
            product = await self.get_product(product_id)
            if not product:
                return {"success": False, "error": "Product not found"}
            
            # Get or create cart
            cart = await self.get_or_create_cart(user_id)
            
            # Calculate price
            unit_price = Decimal(str(product["base_price"]))
            if variant_id and variant_values:
                for variant in product.get("variants", []):
                    if variant["id"] == variant_id:
                        unit_price += Decimal(str(variant["price_adjustment"]))
                        break
            
            # Apply discount if active
            if product.get("flash_sale"):
                discount_percent = Decimal(str(product.get("discount_percent", 0)))
                unit_price = unit_price * (Decimal("1") - (discount_percent / Decimal("100")))
            
            total_price = unit_price * Decimal(str(quantity))
            
            # Create cart item
            cart_item = CartItem(
                product_id=product_id,
                quantity=quantity,
                variant_id=variant_id,
                variant_values=variant_values or {},
                unit_price=unit_price,
                total_price=total_price,
                customization_notes=customization_notes
            )
            
            # Add to cart
            await self.carts_collection.update_one(
                {"id": cart["id"]},
                {
                    "$push": {"items": cart_item.dict()},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
            
            # Recalculate cart totals
            await self._recalculate_cart(cart["id"])
            
            return {
                "success": True,
                "cart_id": cart["id"],
                "message": f"Added {quantity}x {product['name']} to cart"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def remove_from_cart(self, cart_id: str, item_id: str) -> Dict[str, Any]:
        """Remove item from cart"""
        try:
            await self.carts_collection.update_one(
                {"id": cart_id},
                {
                    "$pull": {"items": {"id": item_id}},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
            
            # Recalculate totals
            await self._recalculate_cart(cart_id)
            
            return {"success": True, "message": "Item removed from cart"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def update_cart_item_quantity(self, cart_id: str, item_id: str, quantity: int) -> Dict[str, Any]:
        """Update quantity of cart item"""
        try:
            if quantity <= 0:
                return await self.remove_from_cart(cart_id, item_id)
            
            # Get cart
            cart = await self.carts_collection.find_one({"id": cart_id})
            if not cart:
                return {"success": False, "error": "Cart not found"}
            
            # Find and update item
            for item in cart["items"]:
                if item["id"] == item_id:
                    old_quantity = item["quantity"]
                    item["quantity"] = quantity
                    item["total_price"] = item["unit_price"] * Decimal(str(quantity))
                    break
            
            await self.carts_collection.update_one(
                {"id": cart_id},
                {
                    "$set": {
                        "items": cart["items"],
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            # Recalculate totals
            await self._recalculate_cart(cart_id)
            
            return {"success": True, "message": f"Quantity updated to {quantity}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _recalculate_cart(self, cart_id: str) -> None:
        """Recalculate cart totals"""
        try:
            cart = await self.carts_collection.find_one({"id": cart_id})
            if not cart:
                return
            
            # Calculate subtotal
            subtotal = Decimal("0")
            for item in cart.get("items", []):
                subtotal += Decimal(str(item["total_price"]))
            
            # Calculate tax (10% default)
            tax = subtotal * Decimal("0.1")
            
            # Get shipping cost
            shipping_cost = Decimal("0")
            
            # Calculate total
            total = subtotal + tax + shipping_cost
            
            await self.carts_collection.update_one(
                {"id": cart_id},
                {
                    "$set": {
                        "subtotal": subtotal,
                        "tax": tax,
                        "shipping_cost": shipping_cost,
                        "total": total,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
        except Exception as e:
            print(f"Error recalculating cart: {e}")
    
    async def clear_cart(self, cart_id: str) -> Dict[str, Any]:
        """Clear all items from cart"""
        try:
            await self.carts_collection.update_one(
                {"id": cart_id},
                {
                    "$set": {
                        "items": [],
                        "subtotal": Decimal("0"),
                        "tax": Decimal("0"),
                        "shipping_cost": Decimal("0"),
                        "total": Decimal("0"),
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            return {"success": True, "message": "Cart cleared"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ==================== WISHLIST OPERATIONS ====================
    
    async def create_wishlist(self, user_id: str, name: str, description: Optional[str] = None) -> Dict[str, Any]:
        """Create new wishlist"""
        try:
            wishlist = Wishlist(user_id=user_id, name=name, description=description)
            wishlist_dict = wishlist.dict()
            
            await self.wishlists_collection.insert_one(wishlist_dict)
            
            return {
                "success": True,
                "wishlist_id": wishlist.id,
                "message": f"Wishlist '{name}' created"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def add_to_wishlist(self, wishlist_id: str, product_id: str) -> Dict[str, Any]:
        """Add product to wishlist"""
        try:
            wishlist = await self.wishlists_collection.find_one({"id": wishlist_id})
            if not wishlist:
                return {"success": False, "error": "Wishlist not found"}
            
            if product_id not in wishlist["items"]:
                await self.wishlists_collection.update_one(
                    {"id": wishlist_id},
                    {
                        "$push": {"items": product_id},
                        "$set": {"updated_at": datetime.utcnow()}
                    }
                )
            
            return {"success": True, "message": "Added to wishlist"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def remove_from_wishlist(self, wishlist_id: str, product_id: str) -> Dict[str, Any]:
        """Remove product from wishlist"""
        try:
            await self.wishlists_collection.update_one(
                {"id": wishlist_id},
                {
                    "$pull": {"items": product_id},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
            
            return {"success": True, "message": "Removed from wishlist"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_wishlist(self, wishlist_id: str) -> Optional[Dict]:
        """Get wishlist details"""
        try:
            wishlist = await self.wishlists_collection.find_one({"id": wishlist_id})
            return wishlist
        except Exception as e:
            return None
    
    async def get_user_wishlists(self, user_id: str) -> List[Dict]:
        """Get all wishlists for user"""
        try:
            wishlists = await self.wishlists_collection.find(
                {"user_id": user_id}
            ).to_list(length=None)
            return wishlists
        except Exception as e:
            return []
    
    # ==================== ORDER OPERATIONS ====================
    
    async def create_order(self, user_id: str, cart_id: str, shipping_address: Dict[str, str],
                          payment_method: PaymentMethod) -> Dict[str, Any]:
        """Create order from cart"""
        try:
            # Get cart
            cart = await self.carts_collection.find_one({"id": cart_id})
            if not cart or not cart.get("items"):
                return {"success": False, "error": "Cart is empty"}
            
            # Group items by seller
            items_by_seller = {}
            for item in cart["items"]:
                product = await self.get_product(item["product_id"])
                if not product:
                    continue
                
                seller_id = product["seller_id"]
                if seller_id not in items_by_seller:
                    items_by_seller[seller_id] = []
                
                order_item = OrderItem(
                    product_id=item["product_id"],
                    product_name=product["name"],
                    quantity=item["quantity"],
                    unit_price=item["unit_price"],
                    total_price=item["total_price"],
                    variant_id=item.get("variant_id"),
                    variant_values=item.get("variant_values", {})
                )
                items_by_seller[seller_id].append(order_item)
            
            # Create orders for each seller
            order_ids = []
            for seller_id, order_items in items_by_seller.items():
                order = Order(
                    user_id=user_id,
                    seller_id=seller_id,
                    items=order_items,
                    subtotal=cart["subtotal"],
                    tax=cart["tax"],
                    shipping_cost=cart["shipping_cost"],
                    discount=cart["discount"],
                    total_amount=cart["total"],
                    currency=CurrencyType(cart.get("currency", "usd")),
                    payment_method=payment_method,
                    shipping_address=shipping_address,
                    purchased_from_content_id=cart.get("current_content_id"),
                    purchased_from_content_type=cart.get("current_content_type")
                )
                
                order_dict = order.dict()
                order_dict["created_at"] = datetime.utcnow()
                order_dict["updated_at"] = datetime.utcnow()
                
                result = await self.orders_collection.insert_one(order_dict)
                order_ids.append(order.id)
                
                # Update inventory
                for item in order_items:
                    await self.update_product_inventory(item.product_id, -item.quantity)
                
                # Update seller earnings
                await self._update_seller_earnings(seller_id, order.total_amount)
            
            # Mark cart as completed
            await self.carts_collection.update_one(
                {"id": cart_id},
                {
                    "$set": {
                        "status": ShoppingCartStatus.COMPLETED,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            return {
                "success": True,
                "order_ids": order_ids,
                "message": f"Order created successfully"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_order(self, order_id: str) -> Optional[Dict]:
        """Get order details"""
        try:
            order = await self.orders_collection.find_one({"id": order_id})
            return order
        except Exception as e:
            return None
    
    async def get_user_orders(self, user_id: str, skip: int = 0, limit: int = 50) -> List[Dict]:
        """Get all orders for user"""
        try:
            orders = await self.orders_collection.find(
                {"user_id": user_id}
            ).skip(skip).limit(limit).to_list(length=limit)
            return orders
        except Exception as e:
            return []
    
    async def get_seller_orders(self, seller_id: str, skip: int = 0, limit: int = 50) -> List[Dict]:
        """Get all orders for seller"""
        try:
            orders = await self.orders_collection.find(
                {"seller_id": seller_id}
            ).skip(skip).limit(limit).to_list(length=limit)
            return orders
        except Exception as e:
            return []
    
    async def update_order_status(self, order_id: str, status: OrderStatus,
                                 tracking_number: Optional[str] = None) -> Dict[str, Any]:
        """Update order status"""
        try:
            update_data = {
                "status": status,
                "updated_at": datetime.utcnow()
            }
            
            if tracking_number:
                update_data["tracking_number"] = tracking_number
            
            if status == OrderStatus.SHIPPED:
                update_data["shipped_at"] = datetime.utcnow()
            elif status == OrderStatus.DELIVERED:
                update_data["delivered_at"] = datetime.utcnow()
            
            await self.orders_collection.update_one(
                {"id": order_id},
                {"$set": update_data}
            )
            
            return {"success": True, "message": f"Order status updated to {status}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ==================== SELLER OPERATIONS ====================
    
    async def create_seller_settings(self, seller_settings: SellerSettings) -> Dict[str, Any]:
        """Create seller shop settings"""
        try:
            settings_dict = seller_settings.dict()
            settings_dict["created_at"] = datetime.utcnow()
            settings_dict["updated_at"] = datetime.utcnow()
            
            await self.seller_settings_collection.insert_one(settings_dict)
            
            return {
                "success": True,
                "seller_id": seller_settings.seller_id,
                "message": f"Shop '{seller_settings.shop_name}' created"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_seller_settings(self, seller_id: str) -> Optional[Dict]:
        """Get seller shop settings"""
        try:
            settings = await self.seller_settings_collection.find_one({"seller_id": seller_id})
            return settings
        except Exception as e:
            return None
    
    async def _update_seller_earnings(self, seller_id: str, amount: Decimal) -> None:
        """Update seller earnings"""
        try:
            earnings = await self.seller_earnings_collection.find_one({"seller_id": seller_id})
            
            if earnings:
                new_total = Decimal(str(earnings["total_sales"])) + amount
                await self.seller_earnings_collection.update_one(
                    {"seller_id": seller_id},
                    {
                        "$inc": {
                            "total_orders": 1,
                            "total_sales": amount,
                            "monthly_sales": amount,
                            "yearly_sales": amount
                        },
                        "$set": {
                            "updated_at": datetime.utcnow()
                        }
                    }
                )
            else:
                seller_earnings = SellerEarnings(
                    seller_id=seller_id,
                    total_orders=1,
                    total_sales=amount,
                    monthly_sales=amount,
                    yearly_sales=amount
                )
                await self.seller_earnings_collection.insert_one(seller_earnings.dict())
        except Exception as e:
            print(f"Error updating seller earnings: {e}")
    
    async def get_seller_earnings(self, seller_id: str) -> Optional[Dict]:
        """Get seller earnings summary"""
        try:
            earnings = await self.seller_earnings_collection.find_one({"seller_id": seller_id})
            return earnings
        except Exception as e:
            return None
    
    async def get_seller_dashboard_stats(self, seller_id: str) -> Dict[str, Any]:
        """Get seller dashboard statistics"""
        try:
            earnings = await self.get_seller_earnings(seller_id)
            products = await self.get_seller_products(seller_id)
            orders = await self.get_seller_orders(seller_id)
            
            return {
                "success": True,
                "total_products": len(products),
                "total_orders": len(orders),
                "total_sales": earnings.get("total_sales", 0) if earnings else 0,
                "monthly_sales": earnings.get("monthly_sales", 0) if earnings else 0,
                "total_earnings": earnings.get("total_earnings", 0) if earnings else 0,
                "pending_payout": earnings.get("pending_payout", 0) if earnings else 0,
                "average_order_value": earnings.get("average_order_value", 0) if earnings else 0
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
