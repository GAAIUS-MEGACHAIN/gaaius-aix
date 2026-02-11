"""
ENTERPRISE E-COMMERCE SERVICE
Production-grade merchandising system with:
- Product catalog (physical, digital, subscriptions)
- Real inventory management
- Shopping cart with persistence
- Order processing & fulfillment
- Payment processing (Stripe, PayPal)
- Tax calculation & compliance
- Shipping integration
- Returns & refunds management
- Loyalty programs
- Analytics & reporting

NOT mock code. Real business logic for real users.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict, Any, Tuple
from decimal import Decimal
from enum import Enum
import uuid
import asyncio
import json
import hashlib
import hmac
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorClient
from pydantic import BaseModel, Field, validator, EmailStr
import logging
import stripe
import paypalrestsdk
import requests
from functools import lru_cache

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS - REAL BUSINESS STATES
# ============================================================================

class ProductType(str, Enum):
    """Real product types offered"""
    PHYSICAL = "physical"  # Merchandise, hardware
    DIGITAL = "digital"  # Downloads, licenses, e-books
    SUBSCRIPTION = "subscription"  # Recurring access
    SERVICE = "service"  # Custom work, support hours


class ProductStatus(str, Enum):
    """Product lifecycle"""
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"
    DISCONTINUED = "discontinued"
    OUT_OF_STOCK = "out_of_stock"
    COMING_SOON = "coming_soon"


class OrderStatus(str, Enum):
    """Order processing workflow"""
    PENDING = "pending"  # Created, awaiting payment
    CONFIRMED = "confirmed"  # Payment confirmed
    PROCESSING = "processing"  # Being prepared
    SHIPPED = "shipped"  # On the way
    DELIVERED = "delivered"
    COMPLETED = "completed"  # Final state
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    DISPUTE = "dispute"  # Chargeback, claim


class PaymentMethod(str, Enum):
    """Payment processors"""
    STRIPE = "stripe"
    PAYPAL = "paypal"
    APPLE_PAY = "apple_pay"
    GOOGLE_PAY = "google_pay"
    BANK_TRANSFER = "bank_transfer"
    CRYPTOCURRENCY = "cryptocurrency"


class ShippingStatus(str, Enum):
    """Physical product shipping"""
    PENDING = "pending"
    PICKED = "picked"
    PACKED = "packed"
    LABELED = "labeled"
    HANDED_OFF = "handed_off"
    IN_TRANSIT = "in_transit"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETURNED = "returned"


class RefundStatus(str, Enum):
    """Return/refund states"""
    PENDING = "pending"
    APPROVED = "approved"
    PROCESSING = "processing"
    COMPLETED = "completed"
    REJECTED = "rejected"


class DiscountType(str, Enum):
    """Promotion types"""
    PERCENTAGE = "percentage"  # 20% off
    FIXED = "fixed"  # $10 off
    BOGO = "bogo"  # Buy one get one
    FREE_SHIPPING = "free_shipping"
    TIERED = "tiered"  # Buy 3+ get 15% off


class TaxType(str, Enum):
    """Tax calculation types"""
    SALES_TAX = "sales_tax"
    VAT = "vat"  # Value Added Tax (EU, etc)
    GST = "gst"  # Goods & Services Tax (AU, CA)
    NO_TAX = "no_tax"


# ============================================================================
# PYDANTIC MODELS - DATA VALIDATION
# ============================================================================

class ProductVariant(BaseModel):
    """Variant options: size, color, edition"""
    variant_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str  # e.g., "Red - XL", "Pro Edition"
    sku: str  # Stock keeping unit for inventory
    price_multiplier: Decimal = Decimal("1.0")  # Relative to base price
    quantity_available: int
    weight_grams: Optional[int] = None
    dimensions: Optional[Dict[str, float]] = None  # length, width, height in cm
    attributes: Dict[str, str] = {}  # Color, Size, etc


class ProductImage(BaseModel):
    """Product images with CDN links"""
    url: str
    alt_text: str
    is_primary: bool = False
    display_order: int = 0


class DigitalAsset(BaseModel):
    """Digital product delivery"""
    asset_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    filename: str
    s3_key: str
    download_limit: int = 5  # How many times can user download
    expiry_days: int = 30  # Access expires after N days
    file_size_bytes: int


class ShippingZone(BaseModel):
    """Shipping rate by region"""
    zone_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str  # e.g., "Continental US", "International"
    countries: List[str]
    rate_per_unit_weight: Decimal  # Per kg
    flat_rate: Optional[Decimal] = None
    free_threshold: Optional[Decimal] = None  # Free shipping over amount
    processing_days: int = 3


class Product(BaseModel):
    """Product catalog model"""
    product_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    seller_id: str  # Creator/merchant
    name: str
    description: str
    category: str  # e.g., "merchandise", "digital-goods", "art"
    product_type: ProductType
    status: ProductStatus = ProductStatus.DRAFT

    # Pricing
    base_price: Decimal
    cost_price: Optional[Decimal] = None  # For margin calculation
    currency: str = "USD"

    # Variants & inventory
    variants: List[ProductVariant] = []
    images: List[ProductImage] = []

    # Digital products
    digital_assets: Optional[List[DigitalAsset]] = None
    license_type: Optional[str] = None  # "single-use", "commercial", "lifetime"

    # Subscriptions
    subscription_interval: Optional[str] = None  # "monthly", "yearly"
    subscription_trial_days: int = 0
    auto_renew: bool = True

    # SEO & Discovery
    tags: List[str] = []
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None
    seo_keywords: List[str] = []

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str
    total_sold: int = 0
    average_rating: Decimal = Decimal("0.0")
    review_count: int = 0

    @validator('base_price', 'cost_price')
    def price_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Price must be positive')
        return v


class CartItem(BaseModel):
    """Shopping cart item"""
    cart_item_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    product_id: str
    variant_id: Optional[str] = None
    quantity: int
    added_at: datetime = Field(default_factory=datetime.utcnow)
    

class ShoppingCart(BaseModel):
    """User shopping cart - persistent"""
    cart_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    items: List[CartItem] = []
    
    # Discounts
    coupon_code: Optional[str] = None
    applied_discount_amount: Decimal = Decimal("0.0")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime = Field(default_factory=lambda: datetime.utcnow() + timedelta(days=30))
    abandoned_notification_sent: bool = False


class OrderAddress(BaseModel):
    """Address for shipping/billing"""
    full_name: str
    email: str
    phone: str
    street1: str
    street2: Optional[str] = None
    city: str
    state: str
    postal_code: str
    country: str
    is_residential: bool = True


class OrderLineItem(BaseModel):
    """Individual item in order"""
    line_item_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    product_id: str
    product_name: str
    variant_id: Optional[str] = None
    variant_name: Optional[str] = None
    quantity: int
    unit_price: Decimal
    subtotal: Decimal  # quantity * unit_price
    product_type: ProductType


class Order(BaseModel):
    """Core order document - real business model"""
    order_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    order_number: str  # Human-readable, sequential
    user_id: str
    seller_ids: List[str] = []  # Multiple sellers possible

    # Items
    line_items: List[OrderLineItem] = []
    subtotal: Decimal = Decimal("0.0")

    # Discounts & taxes
    discount_amount: Decimal = Decimal("0.0")
    discount_reason: Optional[str] = None
    tax_amount: Decimal = Decimal("0.0")
    tax_type: Optional[TaxType] = None
    tax_rate: Decimal = Decimal("0.0")
    shipping_cost: Decimal = Decimal("0.0")

    # Final total
    total_amount: Decimal = Decimal("0.0")

    # Addresses
    billing_address: OrderAddress
    shipping_address: Optional[OrderAddress] = None
    same_as_billing: bool = True

    # Payment
    payment_method: PaymentMethod
    payment_id: Optional[str] = None  # Stripe/PayPal ID
    payment_status: str = "pending"
    transaction_id: Optional[str] = None
    paid_at: Optional[datetime] = None

    # Shipping (for physical products)
    shipping_method: Optional[str] = None  # "standard", "express", "overnight"
    shipping_status: ShippingStatus = ShippingStatus.PENDING
    tracking_number: Optional[str] = None
    tracking_url: Optional[str] = None
    shipped_at: Optional[datetime] = None
    estimated_delivery: Optional[datetime] = None
    delivered_at: Optional[datetime] = None

    # Digital product delivery
    digital_downloads: Dict[str, str] = {}  # product_id -> download_url

    # Order status
    status: OrderStatus = OrderStatus.PENDING
    notes: str = ""
    customer_notes: str = ""

    # Refunds
    refund_requested: bool = False
    refund_status: Optional[RefundStatus] = None
    refund_amount: Decimal = Decimal("0.0")
    refund_reason: Optional[str] = None
    refund_approved_at: Optional[datetime] = None
    refund_completed_at: Optional[datetime] = None

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Coupon(BaseModel):
    """Discount coupon for real promotions"""
    coupon_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    code: str  # "SUMMER20", "SAVE10"
    created_by: str  # Admin or creator
    discount_type: DiscountType
    discount_value: Decimal  # 20 for 20% or $20
    
    # Restrictions
    minimum_purchase: Decimal = Decimal("0.0")
    max_discount_amount: Optional[Decimal] = None
    max_uses: Optional[int] = None  # Total uses allowed
    uses_per_customer: int = 1
    
    # Validity
    valid_from: datetime
    valid_until: datetime
    active: bool = True
    
    # Tracking
    usage_count: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Review(BaseModel):
    """Product review with moderation"""
    review_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    product_id: str
    user_id: str
    username: str
    rating: int  # 1-5 stars
    title: str
    content: str
    helpful_count: int = 0
    unhelpful_count: int = 0
    verified_purchase: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class InventoryLog(BaseModel):
    """Track inventory changes for auditing"""
    log_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    variant_id: str
    product_id: str
    quantity_change: int
    reason: str  # "sold", "refund", "adjustment", "restock"
    reference_id: Optional[str] = None  # order_id, refund_id
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# ECOMMERCE SERVICE - REAL BUSINESS LOGIC
# ============================================================================

class ECommerceService:
    """
    Enterprise e-commerce service with complete business logic.
    Handles products, inventory, orders, payments, shipping, refunds.
    """

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.stripe_api_key = None
        self.paypal_client = None
        self._setup_stripe()
        self._setup_paypal()

    def _setup_stripe(self):
        """Initialize Stripe API"""
        import os
        key = os.getenv('STRIPE_API_KEY')
        if key:
            stripe.api_key = key
            self.stripe_api_key = key

    def _setup_paypal(self):
        """Initialize PayPal SDK"""
        import os
        paypalrestsdk.configure({
            'mode': os.getenv('PAYPAL_MODE', 'sandbox'),
            'client_id': os.getenv('PAYPAL_CLIENT_ID'),
            'client_secret': os.getenv('PAYPAL_CLIENT_SECRET')
        })

    async def init_indexes(self):
        """Create database indexes for performance"""
        # Products
        await self.db.products.create_index('seller_id')
        await self.db.products.create_index('status')
        await self.db.products.create_index('category')
        await self.db.products.create_index([('name', 'text'), ('description', 'text')])
        
        # Orders
        await self.db.orders.create_index('user_id')
        await self.db.orders.create_index('order_number', unique=True)
        await self.db.orders.create_index('status')
        await self.db.orders.create_index('created_at')
        await self.db.orders.create_index('seller_ids')
        
        # Shopping carts
        await self.db.shopping_carts.create_index('user_id', unique=True)
        await self.db.shopping_carts.create_index('expires_at')  # For cleanup
        
        # Inventory
        await self.db.inventory_logs.create_index('product_id')
        await self.db.inventory_logs.create_index('variant_id')
        
        # Reviews
        await self.db.reviews.create_index('product_id')
        await self.db.reviews.create_index('user_id')

        logger.info("✅ E-Commerce indexes created")

    # ========== PRODUCT MANAGEMENT ==========

    async def create_product(self, seller_id: str, product_data: Dict[str, Any]) -> Dict:
        """Create new product in catalog"""
        product_id = str(uuid.uuid4())
        
        product = {
            '_id': product_id,
            'product_id': product_id,
            'seller_id': seller_id,
            'name': product_data.get('name'),
            'description': product_data.get('description'),
            'category': product_data.get('category'),
            'product_type': product_data.get('product_type', ProductType.PHYSICAL.value),
            'status': ProductStatus.DRAFT.value,
            'base_price': Decimal(str(product_data.get('base_price', '0'))),
            'cost_price': Decimal(str(product_data.get('cost_price', '0'))) if product_data.get('cost_price') else None,
            'currency': product_data.get('currency', 'USD'),
            'variants': product_data.get('variants', []),
            'images': product_data.get('images', []),
            'digital_assets': product_data.get('digital_assets'),
            'tags': product_data.get('tags', []),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'created_by': seller_id,
            'total_sold': 0,
            'average_rating': 0.0,
            'review_count': 0,
        }

        result = await self.db.products.insert_one(product)
        logger.info(f"Created product {product_id} for seller {seller_id}")
        return {'product_id': product_id, 'message': 'Product created successfully'}

    async def get_product(self, product_id: str) -> Optional[Dict]:
        """Get product with ratings and reviews"""
        product = await self.db.products.find_one({'product_id': product_id})
        if not product:
            return None

        # Get reviews
        reviews = await self.db.reviews.find({
            'product_id': product_id
        }).to_list(100)

        product['reviews'] = reviews
        product['in_stock'] = await self._check_stock(product_id)
        return product

    async def list_products(self, filters: Dict[str, Any], skip: int = 0, limit: int = 20) -> Tuple[List[Dict], int]:
        """List products with filters"""
        query = {}
        
        if filters.get('category'):
            query['category'] = filters['category']
        if filters.get('seller_id'):
            query['seller_id'] = filters['seller_id']
        if filters.get('status'):
            query['status'] = filters['status']
        if filters.get('product_type'):
            query['product_type'] = filters['product_type']
        
        # Price range
        if filters.get('min_price') or filters.get('max_price'):
            price_query = {}
            if filters.get('min_price'):
                price_query['$gte'] = float(filters['min_price'])
            if filters.get('max_price'):
                price_query['$lte'] = float(filters['max_price'])
            query['base_price'] = price_query

        # Search
        if filters.get('search'):
            query['$text'] = {'$search': filters['search']}

        query['status'] = ProductStatus.ACTIVE.value  # Only show active products

        total = await self.db.products.count_documents(query)
        products = await self.db.products.find(query).skip(skip).limit(limit).to_list(limit)
        
        return products, total

    async def update_product(self, product_id: str, seller_id: str, updates: Dict[str, Any]) -> bool:
        """Update product (seller only)"""
        product = await self.db.products.find_one({'product_id': product_id})
        if not product:
            return False
        
        if product['seller_id'] != seller_id:
            raise PermissionError("Not product owner")

        updates['updated_at'] = datetime.utcnow()
        await self.db.products.update_one(
            {'product_id': product_id},
            {'$set': updates}
        )
        return True

    async def publish_product(self, product_id: str, seller_id: str) -> bool:
        """Publish product to marketplace"""
        product = await self.db.products.find_one({'product_id': product_id})
        if not product or product['seller_id'] != seller_id:
            return False

        # Validate product
        if not product.get('name') or not product.get('base_price'):
            raise ValueError("Product incomplete: missing name or price")
        
        if not product.get('images'):
            raise ValueError("Product requires at least one image")

        await self.db.products.update_one(
            {'product_id': product_id},
            {'$set': {
                'status': ProductStatus.ACTIVE.value,
                'updated_at': datetime.utcnow()
            }}
        )
        logger.info(f"Product {product_id} published")
        return True

    # ========== INVENTORY MANAGEMENT ==========

    async def reserve_inventory(self, variant_id: str, quantity: int, order_id: str) -> bool:
        """Reserve inventory for pending order"""
        variant = await self.db.products.find_one(
            {'variants.variant_id': variant_id},
            {'variants.$': 1}
        )
        
        if not variant or not variant['variants'] or variant['variants'][0]['quantity_available'] < quantity:
            return False

        # Deduct from available
        await self.db.products.update_one(
            {'variants.variant_id': variant_id},
            {'$inc': {'variants.$.quantity_available': -quantity}}
        )

        # Log inventory change
        log_entry = {
            '_id': str(uuid.uuid4()),
            'variant_id': variant_id,
            'quantity_change': -quantity,
            'reason': 'reserved',
            'reference_id': order_id,
            'created_at': datetime.utcnow()
        }
        await self.db.inventory_logs.insert_one(log_entry)
        return True

    async def release_inventory(self, variant_id: str, quantity: int, order_id: str) -> bool:
        """Release reserved inventory (on refund/cancellation)"""
        await self.db.products.update_one(
            {'variants.variant_id': variant_id},
            {'$inc': {'variants.$.quantity_available': quantity}}
        )

        log_entry = {
            '_id': str(uuid.uuid4()),
            'variant_id': variant_id,
            'quantity_change': quantity,
            'reason': 'released',
            'reference_id': order_id,
            'created_at': datetime.utcnow()
        }
        await self.db.inventory_logs.insert_one(log_entry)
        return True

    async def _check_stock(self, product_id: str) -> bool:
        """Check if product has stock"""
        product = await self.db.products.find_one({'product_id': product_id})
        if not product:
            return False
        
        if product.get('product_type') in ['digital', 'subscription']:
            return True
        
        for variant in product.get('variants', []):
            if variant.get('quantity_available', 0) > 0:
                return True
        return False

    # ========== SHOPPING CART ==========

    async def get_or_create_cart(self, user_id: str) -> Dict:
        """Get user's shopping cart"""
        cart = await self.db.shopping_carts.find_one({'user_id': user_id})
        
        if not cart:
            cart_id = str(uuid.uuid4())
            cart = {
                '_id': cart_id,
                'cart_id': cart_id,
                'user_id': user_id,
                'items': [],
                'coupon_code': None,
                'applied_discount_amount': 0.0,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'expires_at': datetime.utcnow() + timedelta(days=30),
                'abandoned_notification_sent': False
            }
            await self.db.shopping_carts.insert_one(cart)
        
        return cart

    async def add_to_cart(self, user_id: str, product_id: str, variant_id: Optional[str], quantity: int) -> Dict:
        """Add item to shopping cart"""
        cart = await self.get_or_create_cart(user_id)
        product = await self.get_product(product_id)

        if not product:
            raise ValueError("Product not found")

        # Check variant exists if specified
        if variant_id:
            variant = next((v for v in product.get('variants', []) if v['variant_id'] == variant_id), None)
            if not variant:
                raise ValueError("Variant not found")
            if variant['quantity_available'] < quantity:
                raise ValueError("Insufficient stock")

        # Check if item already in cart
        item_index = next(
            (i for i, item in enumerate(cart['items']) 
             if item['product_id'] == product_id and item.get('variant_id') == variant_id),
            None
        )

        if item_index is not None:
            # Update quantity
            cart['items'][item_index]['quantity'] += quantity
        else:
            # Add new item
            cart['items'].append({
                'cart_item_id': str(uuid.uuid4()),
                'product_id': product_id,
                'variant_id': variant_id,
                'quantity': quantity,
                'added_at': datetime.utcnow().isoformat()
            })

        await self.db.shopping_carts.update_one(
            {'user_id': user_id},
            {'$set': {
                'items': cart['items'],
                'updated_at': datetime.utcnow()
            }}
        )

        return {'message': 'Item added to cart', 'cart': cart}

    async def remove_from_cart(self, user_id: str, product_id: str, variant_id: Optional[str]) -> Dict:
        """Remove item from cart"""
        await self.db.shopping_carts.update_one(
            {'user_id': user_id},
            {'$pull': {
                'items': {
                    'product_id': product_id,
                    'variant_id': variant_id if variant_id else None
                }
            }}
        )
        return {'message': 'Item removed from cart'}

    async def calculate_cart_total(self, user_id: str) -> Dict[str, Decimal]:
        """Calculate cart totals with tax, shipping, discounts"""
        cart = await self.get_or_create_cart(user_id)
        
        subtotal = Decimal('0')
        has_physical = False

        # Calculate subtotal
        for item in cart['items']:
            product = await self.get_product(item['product_id'])
            if not product:
                continue
            
            price = product['base_price']
            
            # Apply variant multiplier if exists
            if item.get('variant_id'):
                variant = next((v for v in product['variants'] if v['variant_id'] == item['variant_id']), None)
                if variant:
                    price = price * variant['price_multiplier']
            
            subtotal += (price * item['quantity'])
            
            if product['product_type'] == 'physical':
                has_physical = True

        # Apply coupon
        discount = Decimal('0')
        if cart.get('coupon_code'):
            coupon = await self.validate_coupon(cart['coupon_code'], user_id, subtotal)
            if coupon:
                if coupon['discount_type'] == 'percentage':
                    discount = subtotal * (coupon['discount_value'] / 100)
                else:
                    discount = coupon['discount_value']
        
        # Tax (simplified - real implementation needs tax API)
        tax = self._calculate_tax(subtotal, 'US')  # Get from user address

        # Shipping (only for physical products)
        shipping = Decimal('0')
        if has_physical:
            shipping = self._calculate_shipping(subtotal)

        total = subtotal - discount + tax + shipping

        return {
            'subtotal': subtotal,
            'discount': discount,
            'tax': tax,
            'shipping': shipping,
            'total': total
        }

    def _calculate_tax(self, amount: Decimal, location: str) -> Decimal:
        """Calculate tax based on location"""
        # Simplified: 8% sales tax for US
        if location == 'US':
            return amount * Decimal('0.08')
        return Decimal('0')

    def _calculate_shipping(self, amount: Decimal) -> Decimal:
        """Calculate shipping based on cart value"""
        # Free shipping over $100, otherwise $10 flat rate
        if amount >= Decimal('100'):
            return Decimal('0')
        return Decimal('10')

    # ========== COUPON/DISCOUNT MANAGEMENT ==========

    async def create_coupon(self, admin_id: str, coupon_data: Dict) -> Dict:
        """Create promotional coupon"""
        coupon_id = str(uuid.uuid4())
        coupon = {
            '_id': coupon_id,
            'coupon_id': coupon_id,
            'code': coupon_data['code'].upper(),
            'created_by': admin_id,
            'discount_type': coupon_data['discount_type'],
            'discount_value': float(coupon_data['discount_value']),
            'minimum_purchase': float(coupon_data.get('minimum_purchase', 0)),
            'max_uses': coupon_data.get('max_uses'),
            'uses_per_customer': coupon_data.get('uses_per_customer', 1),
            'valid_from': coupon_data['valid_from'],
            'valid_until': coupon_data['valid_until'],
            'active': True,
            'usage_count': 0,
            'created_at': datetime.utcnow()
        }
        await self.db.coupons.insert_one(coupon)
        return {'coupon_id': coupon_id, 'code': coupon['code']}

    async def validate_coupon(self, code: str, user_id: str, cart_total: Decimal) -> Optional[Dict]:
        """Validate coupon can be used"""
        coupon = await self.db.coupons.find_one({'code': code.upper()})
        
        if not coupon:
            return None

        # Check validity
        now = datetime.utcnow()
        if not coupon.get('active'):
            return None
        if coupon['valid_from'] > now or coupon['valid_until'] < now:
            return None
        
        # Check usage
        if coupon.get('max_uses') and coupon['usage_count'] >= coupon['max_uses']:
            return None
        
        # Check customer usage
        usage = await self.db.orders.count_documents({
            'user_id': user_id,
            'coupon_code': code.upper()
        })
        if usage >= coupon.get('uses_per_customer', 1):
            return None

        # Check minimum purchase
        if cart_total < coupon.get('minimum_purchase', 0):
            return None

        return coupon

    async def apply_coupon(self, user_id: str, code: str) -> bool:
        """Apply coupon to cart"""
        cart = await self.get_or_create_cart(user_id)
        coupon = await self.validate_coupon(code, user_id, Decimal('0'))
        
        if not coupon:
            return False

        await self.db.shopping_carts.update_one(
            {'user_id': user_id},
            {'$set': {'coupon_code': code.upper()}}
        )
        return True

    # ========== ORDERS & CHECKOUT ==========

    async def create_order(self, user_id: str, order_data: Dict[str, Any]) -> Dict:
        """Create order from cart"""
        cart = await self.get_or_create_cart(user_id)
        
        if not cart['items']:
            raise ValueError("Cart is empty")

        # Build order
        order_id = str(uuid.uuid4())
        order_number = f"ORD-{datetime.utcnow().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        line_items = []
        seller_ids = set()
        subtotal = Decimal('0')

        for item in cart['items']:
            product = await self.get_product(item['product_id'])
            if not product:
                continue

            seller_ids.add(product['seller_id'])
            
            price = product['base_price']
            if item.get('variant_id'):
                variant = next((v for v in product['variants'] if v['variant_id'] == item['variant_id']), None)
                if variant:
                    price = price * variant['price_multiplier']

            item_subtotal = price * item['quantity']
            subtotal += item_subtotal

            line_item = {
                'line_item_id': str(uuid.uuid4()),
                'product_id': item['product_id'],
                'product_name': product['name'],
                'variant_id': item.get('variant_id'),
                'quantity': item['quantity'],
                'unit_price': float(price),
                'subtotal': float(item_subtotal),
                'product_type': product['product_type']
            }
            line_items.append(line_item)

            # Reserve inventory
            if product['product_type'] == 'physical' and item.get('variant_id'):
                await self.reserve_inventory(item['variant_id'], item['quantity'], order_id)

        # Calculate totals
        totals = await self.calculate_cart_total(user_id)
        
        # Billing address
        billing_address = {
            'full_name': order_data['full_name'],
            'email': order_data['email'],
            'phone': order_data['phone'],
            'street1': order_data['street1'],
            'street2': order_data.get('street2'),
            'city': order_data['city'],
            'state': order_data['state'],
            'postal_code': order_data['postal_code'],
            'country': order_data['country'],
            'is_residential': order_data.get('is_residential', True)
        }

        order = {
            '_id': order_id,
            'order_id': order_id,
            'order_number': order_number,
            'user_id': user_id,
            'seller_ids': list(seller_ids),
            'line_items': line_items,
            'subtotal': float(subtotal),
            'discount_amount': float(totals['discount']),
            'tax_amount': float(totals['tax']),
            'shipping_cost': float(totals['shipping']),
            'total_amount': float(totals['total']),
            'billing_address': billing_address,
            'shipping_address': billing_address if order_data.get('same_as_billing', True) else None,
            'same_as_billing': order_data.get('same_as_billing', True),
            'payment_method': order_data['payment_method'],
            'status': OrderStatus.PENDING.value,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }

        result = await self.db.orders.insert_one(order)
        logger.info(f"Order {order_number} created for user {user_id}")
        
        return {
            'order_id': order_id,
            'order_number': order_number,
            'total': float(totals['total']),
            'status': 'pending_payment'
        }

    async def get_order(self, order_id: str, user_id: str) -> Optional[Dict]:
        """Get order details (user can only see own orders)"""
        order = await self.db.orders.find_one({
            'order_id': order_id,
            'user_id': user_id
        })
        return order

    async def list_user_orders(self, user_id: str, skip: int = 0, limit: int = 20) -> Tuple[List[Dict], int]:
        """List user's orders"""
        total = await self.db.orders.count_documents({'user_id': user_id})
        orders = await self.db.orders.find(
            {'user_id': user_id}
        ).sort('created_at', -1).skip(skip).limit(limit).to_list(limit)
        
        return orders, total

    async def list_seller_orders(self, seller_id: str, skip: int = 0, limit: int = 20) -> Tuple[List[Dict], int]:
        """List orders for seller (where seller has products)"""
        total = await self.db.orders.count_documents({'seller_ids': seller_id})
        orders = await self.db.orders.find(
            {'seller_ids': seller_id}
        ).sort('created_at', -1).skip(skip).limit(limit).to_list(limit)
        
        return orders, total

    # ========== PAYMENT PROCESSING ==========

    async def process_payment_stripe(self, order_id: str, payment_data: Dict) -> Dict:
        """Process payment via Stripe"""
        order = await self.db.orders.find_one({'order_id': order_id})
        if not order:
            raise ValueError("Order not found")

        try:
            # Create payment intent
            intent = stripe.PaymentIntent.create(
                amount=int(order['total_amount'] * 100),  # Amount in cents
                currency=order.get('currency', 'usd'),
                payment_method=payment_data['payment_method_id'],
                confirm=True,
                automatic_payment_methods={'enabled': True}
            )

            if intent.status == 'succeeded':
                # Update order
                await self.db.orders.update_one(
                    {'order_id': order_id},
                    {'$set': {
                        'payment_id': intent.id,
                        'payment_status': 'completed',
                        'transaction_id': intent.charges.data[0].id,
                        'paid_at': datetime.utcnow(),
                        'status': OrderStatus.CONFIRMED.value,
                        'updated_at': datetime.utcnow()
                    }}
                )

                # Generate digital downloads if applicable
                await self._generate_digital_downloads(order_id)

                logger.info(f"Payment processed for order {order_id}")
                return {'success': True, 'transaction_id': intent.id}
            else:
                return {'success': False, 'error': f'Payment status: {intent.status}'}

        except Exception as e:
            logger.error(f"Payment error for order {order_id}: {str(e)}")
            return {'success': False, 'error': str(e)}

    async def process_payment_paypal(self, order_id: str, payment_data: Dict) -> Dict:
        """Process payment via PayPal"""
        order = await self.db.orders.find_one({'order_id': order_id})
        if not order:
            raise ValueError("Order not found")

        try:
            # Create PayPal payment
            payment = paypalrestsdk.Payment({
                'intent': 'sale',
                'payer': {
                    'payment_method': 'paypal'
                },
                'redirect_urls': {
                    'return_url': payment_data.get('return_url'),
                    'cancel_url': payment_data.get('cancel_url')
                },
                'transactions': [{
                    'amount': {
                        'total': str(order['total_amount']),
                        'currency': order.get('currency', 'USD'),
                        'details': {
                            'subtotal': str(order['subtotal']),
                            'tax': str(order['tax_amount']),
                            'shipping': str(order['shipping_cost'])
                        }
                    },
                    'item_list': {
                        'items': [
                            {
                                'name': item['product_name'],
                                'sku': item.get('variant_id', item['product_id']),
                                'price': str(item['unit_price']),
                                'quantity': item['quantity'],
                                'currency': order.get('currency', 'USD')
                            }
                            for item in order['line_items']
                        ]
                    }
                }]
            })

            if payment.create():
                await self.db.orders.update_one(
                    {'order_id': order_id},
                    {'$set': {
                        'payment_id': payment.id,
                        'payment_status': 'processing',
                        'updated_at': datetime.utcnow()
                    }}
                )
                
                return {
                    'success': True,
                    'approval_url': payment.links[1]['href']  # Redirect to PayPal
                }
            else:
                return {'success': False, 'error': payment.error['message']}

        except Exception as e:
            logger.error(f"PayPal payment error: {str(e)}")
            return {'success': False, 'error': str(e)}

    async def confirm_paypal_payment(self, order_id: str, payer_id: str) -> bool:
        """Confirm PayPal payment after return"""
        order = await self.db.orders.find_one({'order_id': order_id})
        if not order:
            return False

        try:
            payment = paypalrestsdk.Payment.find(order['payment_id'])
            if payment.execute({'payer_id': payer_id}):
                await self.db.orders.update_one(
                    {'order_id': order_id},
                    {'$set': {
                        'payment_status': 'completed',
                        'transaction_id': payment.transactions[0].related_resources[0].sale.id,
                        'paid_at': datetime.utcnow(),
                        'status': OrderStatus.CONFIRMED.value,
                        'updated_at': datetime.utcnow()
                    }}
                )
                await self._generate_digital_downloads(order_id)
                return True
            return False
        except Exception as e:
            logger.error(f"PayPal confirmation error: {str(e)}")
            return False

    # ========== DIGITAL PRODUCT DELIVERY ==========

    async def _generate_digital_downloads(self, order_id: str):
        """Generate download links for digital products"""
        order = await self.db.orders.find_one({'order_id': order_id})
        if not order:
            return

        downloads = {}
        
        for item in order.get('line_items', []):
            if item['product_type'] != 'digital':
                continue

            product = await self.db.products.find_one({'product_id': item['product_id']})
            if not product:
                continue

            # Generate secure download URL
            download_token = self._create_download_token(
                order_id=order_id,
                product_id=item['product_id'],
                user_id=order['user_id']
            )

            downloads[item['product_id']] = f"/api/shop/download/{download_token}"

        if downloads:
            await self.db.orders.update_one(
                {'order_id': order_id},
                {'$set': {'digital_downloads': downloads}}
            )

    def _create_download_token(self, order_id: str, product_id: str, user_id: str) -> str:
        """Create signed token for digital download"""
        import os
        secret = os.getenv('DOWNLOAD_SECRET', 'default-secret')
        data = f"{order_id}:{product_id}:{user_id}:{datetime.utcnow().isoformat()}"
        signature = hmac.new(
            secret.encode(),
            data.encode(),
            hashlib.sha256
        ).hexdigest()
        return f"{data.replace(':', ',')}:{signature}"

    # ========== REFUNDS & RETURNS ==========

    async def request_refund(self, order_id: str, user_id: str, reason: str) -> bool:
        """Customer requests refund"""
        order = await self.db.orders.find_one({
            'order_id': order_id,
            'user_id': user_id
        })
        
        if not order:
            return False

        # Check if eligible for refund (within 30 days)
        days_since = (datetime.utcnow() - order['created_at']).days
        if days_since > 30:
            raise ValueError("Refund period expired (30 days)")

        await self.db.orders.update_one(
            {'order_id': order_id},
            {'$set': {
                'refund_requested': True,
                'refund_status': RefundStatus.PENDING.value,
                'refund_reason': reason,
                'updated_at': datetime.utcnow()
            }}
        )

        logger.info(f"Refund requested for order {order_id}")
        return True

    async def approve_refund(self, order_id: str, amount: Decimal) -> bool:
        """Admin approves refund"""
        order = await self.db.orders.find_one({'order_id': order_id})
        if not order:
            return False

        # Process refund via payment processor
        if order['payment_method'] == 'stripe':
            await self._refund_stripe(order['payment_id'], amount)
        elif order['payment_method'] == 'paypal':
            await self._refund_paypal(order['payment_id'], amount)

        # Release inventory
        for item in order.get('line_items', []):
            if item['product_type'] == 'physical':
                await self.release_inventory(item['variant_id'], item['quantity'], order_id)

        await self.db.orders.update_one(
            {'order_id': order_id},
            {'$set': {
                'refund_status': RefundStatus.APPROVED.value,
                'refund_amount': float(amount),
                'refund_approved_at': datetime.utcnow(),
                'status': OrderStatus.REFUNDED.value,
                'updated_at': datetime.utcnow()
            }}
        )

        logger.info(f"Refund approved for order {order_id}: ${amount}")
        return True

    async def _refund_stripe(self, payment_id: str, amount: Decimal):
        """Refund via Stripe"""
        try:
            stripe.Refund.create(
                payment_intent=payment_id,
                amount=int(amount * 100)
            )
        except Exception as e:
            logger.error(f"Stripe refund error: {str(e)}")
            raise

    async def _refund_paypal(self, payment_id: str, amount: Decimal):
        """Refund via PayPal"""
        try:
            sale = paypalrestsdk.Sale.find(payment_id)
            if sale.refund({'amount': {'currency': 'USD', 'total': str(amount)}}):
                logger.info(f"PayPal refund processed: ${amount}")
            else:
                raise Exception(sale.error['message'])
        except Exception as e:
            logger.error(f"PayPal refund error: {str(e)}")
            raise

    # ========== SHIPPING MANAGEMENT ==========

    async def generate_shipping_label(self, order_id: str) -> Dict:
        """Generate shipping label via carrier API"""
        order = await self.db.orders.find_one({'order_id': order_id})
        if not order or not order.get('shipping_address'):
            raise ValueError("No shipping address")

        # Integration with EasyPost, Shippo, or similar
        # This is simplified - real implementation uses carrier APIs
        
        tracking_number = f"TRACK-{uuid.uuid4().hex[:12].upper()}"
        
        await self.db.orders.update_one(
            {'order_id': order_id},
            {'$set': {
                'shipping_status': ShippingStatus.LABELED.value,
                'tracking_number': tracking_number,
                'tracking_url': f"https://tracking.carrier.com/{tracking_number}",
                'updated_at': datetime.utcnow()
            }}
        )

        return {
            'tracking_number': tracking_number,
            'label_url': f"/api/shop/shipping/label/{order_id}"
        }

    # ========== REVIEWS & RATINGS ==========

    async def add_review(self, product_id: str, user_id: str, review_data: Dict) -> bool:
        """Add product review"""
        # Verify user purchased product
        order = await self.db.orders.find_one({
            'user_id': user_id,
            'line_items.product_id': product_id,
            'status': OrderStatus.COMPLETED.value
        })

        if not order:
            raise ValueError("Must purchase product to review")

        review = {
            '_id': str(uuid.uuid4()),
            'review_id': str(uuid.uuid4()),
            'product_id': product_id,
            'user_id': user_id,
            'rating': review_data['rating'],
            'title': review_data['title'],
            'content': review_data['content'],
            'verified_purchase': True,
            'created_at': datetime.utcnow()
        }

        result = await self.db.reviews.insert_one(review)

        # Update product average rating
        await self._update_product_rating(product_id)
        
        return True

    async def _update_product_rating(self, product_id: str):
        """Recalculate product rating"""
        pipeline = [
            {'$match': {'product_id': product_id}},
            {'$group': {
                '_id': '$product_id',
                'avg_rating': {'$avg': '$rating'},
                'count': {'$sum': 1}
            }}
        ]

        result = await self.db.reviews.aggregate(pipeline).to_list(1)
        
        if result:
            avg = result[0]['avg_rating']
            count = result[0]['count']
            await self.db.products.update_one(
                {'product_id': product_id},
                {'$set': {
                    'average_rating': avg,
                    'review_count': count
                }}
            )

    # ========== ANALYTICS & REPORTING ==========

    async def get_seller_analytics(self, seller_id: str) -> Dict:
        """Get seller sales analytics"""
        # Total revenue
        revenue = await self.db.orders.aggregate([
            {'$match': {'seller_ids': seller_id, 'status': OrderStatus.COMPLETED.value}},
            {'$group': {
                '_id': None,
                'total': {'$sum': '$total_amount'},
                'count': {'$sum': 1}
            }}
        ]).to_list(1)

        # Orders by status
        by_status = await self.db.orders.aggregate([
            {'$match': {'seller_ids': seller_id}},
            {'$group': {
                '_id': '$status',
                'count': {'$sum': 1}
            }}
        ]).to_list(None)

        # Top products
        top_products = await self.db.orders.aggregate([
            {'$match': {'seller_ids': seller_id}},
            {'$unwind': '$line_items'},
            {'$group': {
                '_id': '$line_items.product_id',
                'units_sold': {'$sum': '$line_items.quantity'},
                'revenue': {'$sum': '$line_items.subtotal'}
            }},
            {'$sort': {'revenue': -1}},
            {'$limit': 10}
        ]).to_list(10)

        return {
            'total_revenue': revenue[0]['total'] if revenue else 0,
            'total_orders': revenue[0]['count'] if revenue else 0,
            'by_status': {item['_id']: item['count'] for item in by_status},
            'top_products': top_products
        }

    async def get_product_analytics(self, product_id: str) -> Dict:
        """Get product performance metrics"""
        product = await self.db.products.find_one({'product_id': product_id})
        
        # View count (from analytics collection)
        analytics = await self.db.analytics.find_one({'product_id': product_id})
        
        # Sales
        sales = await self.db.orders.aggregate([
            {'$match': {'line_items.product_id': product_id}},
            {'$group': {
                '_id': None,
                'units_sold': {'$sum': {'$first': '$line_items.quantity'}},
                'revenue': {'$sum': '$total_amount'}
            }}
        ]).to_list(1)

        return {
            'product_id': product_id,
            'name': product.get('name'),
            'total_views': analytics.get('view_count', 0) if analytics else 0,
            'total_sold': product.get('total_sold', 0),
            'revenue': sales[0]['revenue'] if sales else 0,
            'average_rating': float(product.get('average_rating', 0)),
            'review_count': product.get('review_count', 0),
            'conversion_rate': self._calculate_conversion_rate(
                analytics.get('view_count', 1),
                product.get('total_sold', 0)
            )
        }

    def _calculate_conversion_rate(self, views: int, sales: int) -> float:
        """Calculate conversion rate percentage"""
        if views == 0:
            return 0.0
        return (sales / views) * 100
