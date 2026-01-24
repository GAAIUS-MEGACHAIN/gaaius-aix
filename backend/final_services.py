"""
Final 4 Advanced Services - Production Enterprise Grade
Live Shopping, E-Commerce, Subscription/Patreon, Advanced Recommendation Engine
"""

from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid
import asyncio
from pydantic import BaseModel, Field, validator

# ============================================================================
# LIVE SHOPPING SERVICE - LIVESTREAM + MARKETPLACE INTEGRATION
# ============================================================================

class LiveShoppingStatus(str, Enum):
    SCHEDULED = "scheduled"
    LIVE = "live"
    ENDED = "ended"
    ARCHIVED = "archived"

class ProductStatus(str, Enum):
    IN_STOCK = "in_stock"
    LOW_STOCK = "low_stock"
    OUT_OF_STOCK = "out_of_stock"
    DISCONTINUED = "discontinued"

@dataclass
class LiveProduct:
    """Product in live shopping session"""
    product_id: str
    name: str
    description: str
    price: float
    stock: int
    discount_percent: float = 0.0
    added_at: datetime = field(default_factory=datetime.utcnow)
    units_sold: int = 0
    
    def get_discounted_price(self) -> float:
        return self.price * (1 - self.discount_percent / 100)

@dataclass
class LiveShoppingSession:
    """Live shopping broadcast session"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    creator_id: str = ""
    stream_id: str = ""
    title: str = ""
    description: str = ""
    status: LiveShoppingStatus = LiveShoppingStatus.SCHEDULED
    start_time: datetime = field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    products: Dict[str, LiveProduct] = field(default_factory=dict)
    viewers: Set[str] = field(default_factory=set)
    peak_viewers: int = 0
    total_revenue: float = 0.0
    purchases: Dict[str, List[str]] = field(default_factory=dict)  # user_id -> [product_ids]
    chat_comments: List[Dict] = field(default_factory=list)
    discount_codes: Dict[str, Dict] = field(default_factory=dict)  # code -> {discount%, products}
    
    def get_status(self) -> str:
        if self.status == LiveShoppingStatus.LIVE:
            return f"LIVE - {len(self.viewers)} viewers"
        return self.status.value

@dataclass
class ShoppingCart:
    """Live shopping cart"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    session_id: str = ""
    items: Dict[str, int] = field(default_factory=dict)  # product_id -> quantity
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: datetime = field(default_factory=lambda: datetime.utcnow() + timedelta(hours=24))
    applied_coupon: Optional[str] = None
    
    def get_total(self, products: Dict[str, LiveProduct], discount_percent: float = 0.0) -> float:
        total = sum(products[pid].get_discounted_price() * qty 
                   for pid, qty in self.items.items() if pid in products)
        return total * (1 - discount_percent / 100)

class LiveShoppingService:
    """Production-grade live shopping platform"""
    
    def __init__(self):
        self.sessions: Dict[str, LiveShoppingSession] = {}
        self.carts: Dict[str, ShoppingCart] = {}
        self.orders: Dict[str, Dict] = {}
    
    async def create_session(self, creator_id: str, title: str, description: str, 
                            start_time: datetime) -> LiveShoppingSession:
        """Create live shopping session"""
        session = LiveShoppingSession(
            creator_id=creator_id,
            stream_id=str(uuid.uuid4()),
            title=title,
            description=description,
            start_time=start_time
        )
        self.sessions[session.id] = session
        return session
    
    async def add_product_to_session(self, session_id: str, product_id: str, name: str,
                                     description: str, price: float, stock: int,
                                     discount_percent: float = 0.0) -> LiveProduct:
        """Add product to live session"""
        if session_id not in self.sessions:
            raise ValueError("Session not found")
        
        product = LiveProduct(product_id, name, description, price, stock, discount_percent)
        self.sessions[session_id].products[product_id] = product
        return product
    
    async def start_session(self, session_id: str) -> bool:
        """Start live session"""
        if session_id not in self.sessions:
            return False
        self.sessions[session_id].status = LiveShoppingStatus.LIVE
        self.sessions[session_id].start_time = datetime.utcnow()
        return True
    
    async def update_viewers(self, session_id: str, user_ids: Set[str]):
        """Update live viewer count"""
        if session_id not in self.sessions:
            return
        session = self.sessions[session_id]
        session.viewers = user_ids
        session.peak_viewers = max(session.peak_viewers, len(user_ids))
    
    async def add_to_cart(self, user_id: str, session_id: str, product_id: str, quantity: int):
        """Add product to shopping cart during live"""
        if session_id not in self.sessions:
            raise ValueError("Session not found")
        
        cart_key = f"{user_id}_{session_id}"
        if cart_key not in self.carts:
            cart = ShoppingCart(user_id=user_id, session_id=session_id)
            self.carts[cart_key] = cart
        else:
            cart = self.carts[cart_key]
        
        cart.items[product_id] = cart.items.get(product_id, 0) + quantity
        return cart
    
    async def apply_coupon(self, user_id: str, session_id: str, coupon_code: str) -> bool:
        """Apply discount coupon"""
        if session_id not in self.sessions:
            return False
        
        session = self.sessions[session_id]
        if coupon_code not in session.discount_codes:
            return False
        
        cart_key = f"{user_id}_{session_id}"
        if cart_key in self.carts:
            self.carts[cart_key].applied_coupon = coupon_code
            return True
        return False
    
    async def checkout(self, user_id: str, session_id: str, payment_method: str) -> Dict:
        """Complete purchase from live shopping"""
        cart_key = f"{user_id}_{session_id}"
        if cart_key not in self.carts:
            raise ValueError("Cart not found")
        
        cart = self.carts[cart_key]
        session = self.sessions[session_id]
        
        # Calculate total
        discount = 0.0
        if cart.applied_coupon:
            discount = session.discount_codes[cart.applied_coupon]['discount_percent']
        
        total = cart.get_total(session.products, discount)
        
        # Create order
        order_id = str(uuid.uuid4())
        self.orders[order_id] = {
            'user_id': user_id,
            'session_id': session_id,
            'items': dict(cart.items),
            'total': total,
            'payment_method': payment_method,
            'created_at': datetime.utcnow(),
            'status': 'completed'
        }
        
        # Update product sales
        for product_id, qty in cart.items.items():
            session.products[product_id].units_sold += qty
            session.products[product_id].stock -= qty
        
        session.total_revenue += total
        session.purchases[user_id] = list(cart.items.keys())
        
        # Clear cart
        del self.carts[cart_key]
        
        return {
            'order_id': order_id,
            'total': total,
            'items': dict(cart.items)
        }
    
    async def end_session(self, session_id: str) -> Dict:
        """End live shopping session"""
        if session_id not in self.sessions:
            raise ValueError("Session not found")
        
        session = self.sessions[session_id]
        session.status = LiveShoppingStatus.ENDED
        session.end_time = datetime.utcnow()
        
        total_sold = sum(p.units_sold for p in session.products.values())
        
        return {
            'session_id': session_id,
            'total_revenue': session.total_revenue,
            'total_items_sold': total_sold,
            'peak_viewers': session.peak_viewers,
            'unique_buyers': len(session.purchases),
            'duration_minutes': int((session.end_time - session.start_time).total_seconds() / 60)
        }
    
    async def add_comment(self, session_id: str, user_id: str, message: str):
        """Add live chat comment"""
        if session_id in self.sessions:
            self.sessions[session_id].chat_comments.append({
                'user_id': user_id,
                'message': message,
                'timestamp': datetime.utcnow()
            })

# ============================================================================
# E-COMMERCE PLATFORM SERVICE
# ============================================================================

class OrderStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class ShipmentStatus(str, Enum):
    PENDING = "pending"
    PICKED = "picked"
    PACKED = "packed"
    SHIPPED = "shipped"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    RETURNED = "returned"

@dataclass
class Product:
    """E-commerce product"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    seller_id: str = ""
    name: str = ""
    description: str = ""
    price: float = 0.0
    cost: float = 0.0  # COGS for profit calculation
    stock: int = 0
    category: str = ""
    images: List[str] = field(default_factory=list)
    rating: float = 5.0
    review_count: int = 0
    sku: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True
    sales_count: int = 0
    revenue: float = 0.0

@dataclass
class CartItem:
    """Shopping cart item"""
    product_id: str = ""
    quantity: int = 1
    price_at_time: float = 0.0
    added_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class ShoppingCart:
    """E-commerce shopping cart"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    items: Dict[str, CartItem] = field(default_factory=dict)
    coupon_code: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def get_subtotal(self) -> float:
        return sum(item.price_at_time * item.quantity for item in self.items.values())
    
    def get_item_count(self) -> int:
        return sum(item.quantity for item in self.items.values())

@dataclass
class Order:
    """E-commerce order"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    items: Dict[str, CartItem] = field(default_factory=dict)
    subtotal: float = 0.0
    tax: float = 0.0
    shipping_cost: float = 0.0
    discount: float = 0.0
    total: float = 0.0
    status: OrderStatus = OrderStatus.PENDING
    payment_method: str = ""
    shipping_address: Dict = field(default_factory=dict)
    tracking_number: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    shipped_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    notes: str = ""

@dataclass
class Shipment:
    """Order shipment tracking"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    order_id: str = ""
    carrier: str = ""
    tracking_number: str = ""
    status: ShipmentStatus = ShipmentStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    estimated_delivery: Optional[datetime] = None
    actual_delivery: Optional[datetime] = None
    events: List[Dict] = field(default_factory=list)

class ECommerceService:
    """Production-grade e-commerce platform"""
    
    def __init__(self):
        self.products: Dict[str, Product] = {}
        self.carts: Dict[str, ShoppingCart] = {}
        self.orders: Dict[str, Order] = {}
        self.shipments: Dict[str, Shipment] = {}
        self.inventory_locks: Dict[str, Dict] = {}  # order_id -> {product_id: qty}
    
    async def create_product(self, seller_id: str, name: str, description: str,
                            price: float, cost: float, stock: int, category: str,
                            images: List[str]) -> Product:
        """Create product listing"""
        product = Product(
            seller_id=seller_id,
            name=name,
            description=description,
            price=price,
            cost=cost,
            stock=stock,
            category=category,
            images=images,
            sku=f"SKU-{uuid.uuid4().hex[:8].upper()}"
        )
        self.products[product.id] = product
        return product
    
    async def get_cart(self, user_id: str) -> ShoppingCart:
        """Get or create user cart"""
        for cart in self.carts.values():
            if cart.user_id == user_id:
                return cart
        
        cart = ShoppingCart(user_id=user_id)
        self.carts[cart.id] = cart
        return cart
    
    async def add_to_cart(self, user_id: str, product_id: str, quantity: int) -> ShoppingCart:
        """Add item to cart"""
        if product_id not in self.products:
            raise ValueError("Product not found")
        
        cart = await self.get_cart(user_id)
        product = self.products[product_id]
        
        cart_item = CartItem(
            product_id=product_id,
            quantity=quantity,
            price_at_time=product.price
        )
        
        if product_id in cart.items:
            cart.items[product_id].quantity += quantity
        else:
            cart.items[product_id] = cart_item
        
        cart.updated_at = datetime.utcnow()
        return cart
    
    async def checkout(self, user_id: str, payment_method: str, 
                      shipping_address: Dict) -> Order:
        """Process order checkout"""
        cart = await self.get_cart(user_id)
        if not cart.items:
            raise ValueError("Cart is empty")
        
        # Create order
        order = Order(
            user_id=user_id,
            items=dict(cart.items),
            subtotal=cart.get_subtotal(),
            payment_method=payment_method,
            shipping_address=shipping_address
        )
        
        # Calculate costs
        order.tax = order.subtotal * 0.1  # 10% tax
        order.shipping_cost = 10.0 if order.subtotal < 100 else 0.0  # Free shipping over $100
        
        # Apply coupon if exists
        if cart.coupon_code:
            order.discount = order.subtotal * 0.1  # Assuming 10% discount
        
        order.total = order.subtotal + order.tax + order.shipping_cost - order.discount
        order.status = OrderStatus.PAID
        
        # Lock inventory
        for product_id, item in order.items.items():
            if product_id in self.products:
                self.products[product_id].stock -= item.quantity
                self.products[product_id].sales_count += item.quantity
                self.products[product_id].revenue += item.price_at_time * item.quantity
        
        self.orders[order.id] = order
        
        # Clear cart
        cart.items.clear()
        
        return order
    
    async def create_shipment(self, order_id: str, carrier: str) -> Shipment:
        """Create shipment for order"""
        if order_id not in self.orders:
            raise ValueError("Order not found")
        
        order = self.orders[order_id]
        shipment = Shipment(
            order_id=order_id,
            carrier=carrier,
            tracking_number=f"{carrier.upper()}-{uuid.uuid4().hex[:8].upper()}",
            estimated_delivery=datetime.utcnow() + timedelta(days=5)
        )
        
        self.shipments[shipment.id] = shipment
        order.tracking_number = shipment.tracking_number
        order.status = OrderStatus.SHIPPED
        order.shipped_at = datetime.utcnow()
        
        return shipment
    
    async def update_shipment_status(self, shipment_id: str, status: ShipmentStatus,
                                    location: Optional[str] = None) -> Shipment:
        """Update shipment status"""
        if shipment_id not in self.shipments:
            raise ValueError("Shipment not found")
        
        shipment = self.shipments[shipment_id]
        shipment.status = status
        shipment.events.append({
            'status': status.value,
            'location': location,
            'timestamp': datetime.utcnow()
        })
        
        if status == ShipmentStatus.DELIVERED:
            shipment.actual_delivery = datetime.utcnow()
            order = self.orders[shipment.order_id]
            order.status = OrderStatus.DELIVERED
            order.delivered_at = datetime.utcnow()
        
        return shipment
    
    async def search_products(self, query: str, category: Optional[str] = None,
                             min_price: float = 0, max_price: float = 999999) -> List[Product]:
        """Search products"""
        results = []
        for product in self.products.values():
            if not product.is_active:
                continue
            
            matches_query = query.lower() in product.name.lower() or query.lower() in product.description.lower()
            matches_category = category is None or product.category == category
            matches_price = min_price <= product.price <= max_price
            
            if matches_query and matches_category and matches_price:
                results.append(product)
        
        return sorted(results, key=lambda p: p.sales_count, reverse=True)

# ============================================================================
# SUBSCRIPTION / PATREON CLONE SERVICE
# ============================================================================

class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    CANCELLED = "cancelled"
    EXPIRED = "expired"

@dataclass
class SubscriptionTier:
    """Subscription tier"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    creator_id: str = ""
    name: str = ""
    description: str = ""
    price: float = 0.0
    benefits: List[str] = field(default_factory=list)
    member_count: int = 0
    monthly_revenue: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class Subscription:
    """User subscription to creator"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    creator_id: str = ""
    tier_id: str = ""
    tier_name: str = ""
    monthly_price: float = 0.0
    status: SubscriptionStatus = SubscriptionStatus.ACTIVE
    started_at: datetime = field(default_factory=datetime.utcnow)
    renews_at: datetime = field(default_factory=lambda: datetime.utcnow() + timedelta(days=30))
    cancelled_at: Optional[datetime] = None
    last_payment: Optional[datetime] = None

@dataclass
class ExclusiveContent:
    """Content exclusive to subscription tier"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    creator_id: str = ""
    title: str = ""
    description: str = ""
    content_url: str = ""
    tier_id: str = ""  # Empty = all tiers
    posted_at: datetime = field(default_factory=datetime.utcnow)
    views: int = 0
    likes: int = 0

class SubscriptionService:
    """Production-grade subscription/Patreon platform"""
    
    def __init__(self):
        self.tiers: Dict[str, SubscriptionTier] = {}
        self.subscriptions: Dict[str, Subscription] = {}
        self.exclusive_content: Dict[str, ExclusiveContent] = {}
        self.earnings: Dict[str, Dict] = {}  # creator_id -> earnings data
    
    async def create_tier(self, creator_id: str, name: str, description: str,
                         price: float, benefits: List[str]) -> SubscriptionTier:
        """Create subscription tier"""
        tier = SubscriptionTier(
            creator_id=creator_id,
            name=name,
            description=description,
            price=price,
            benefits=benefits
        )
        self.tiers[tier.id] = tier
        
        if creator_id not in self.earnings:
            self.earnings[creator_id] = {
                'total_members': 0,
                'monthly_revenue': 0.0,
                'tiers': {}
            }
        
        return tier
    
    async def subscribe(self, user_id: str, creator_id: str, tier_id: str,
                       payment_method: str) -> Subscription:
        """Subscribe to creator tier"""
        if tier_id not in self.tiers:
            raise ValueError("Tier not found")
        
        tier = self.tiers[tier_id]
        
        # Create subscription
        subscription = Subscription(
            user_id=user_id,
            creator_id=creator_id,
            tier_id=tier_id,
            tier_name=tier.name,
            monthly_price=tier.price
        )
        
        self.subscriptions[subscription.id] = subscription
        
        # Update tier member count
        tier.member_count += 1
        tier.monthly_revenue += tier.price
        
        # Update earnings
        if creator_id not in self.earnings:
            self.earnings[creator_id] = {
                'total_members': 0,
                'monthly_revenue': 0.0,
                'tiers': {}
            }
        
        self.earnings[creator_id]['total_members'] += 1
        self.earnings[creator_id]['monthly_revenue'] += tier.price
        
        if tier_id not in self.earnings[creator_id]['tiers']:
            self.earnings[creator_id]['tiers'][tier_id] = {'members': 0, 'revenue': 0.0}
        
        self.earnings[creator_id]['tiers'][tier_id]['members'] += 1
        self.earnings[creator_id]['tiers'][tier_id]['revenue'] += tier.price
        
        return subscription
    
    async def post_exclusive_content(self, creator_id: str, title: str, description: str,
                                     content_url: str, tier_id: Optional[str] = None) -> ExclusiveContent:
        """Post exclusive content"""
        content = ExclusiveContent(
            creator_id=creator_id,
            title=title,
            description=description,
            content_url=content_url,
            tier_id=tier_id or ""
        )
        self.exclusive_content[content.id] = content
        return content
    
    async def get_exclusive_content(self, user_id: str, creator_id: str) -> List[ExclusiveContent]:
        """Get accessible exclusive content"""
        # Find user's subscription to creator
        user_subscriptions = [s for s in self.subscriptions.values()
                             if s.user_id == user_id and s.creator_id == creator_id]
        
        if not user_subscriptions:
            return []
        
        # Get subscription tier
        subscriber_tier = user_subscriptions[0].tier_id
        
        # Get all content accessible to this tier
        accessible = []
        for content in self.exclusive_content.values():
            if content.creator_id == creator_id:
                if not content.tier_id or content.tier_id == subscriber_tier:
                    accessible.append(content)
        
        return accessible
    
    async def cancel_subscription(self, subscription_id: str) -> Subscription:
        """Cancel subscription"""
        if subscription_id not in self.subscriptions:
            raise ValueError("Subscription not found")
        
        subscription = self.subscriptions[subscription_id]
        subscription.status = SubscriptionStatus.CANCELLED
        subscription.cancelled_at = datetime.utcnow()
        
        # Update tier member count
        tier = self.tiers[subscription.tier_id]
        tier.member_count -= 1
        tier.monthly_revenue -= subscription.monthly_price
        
        # Update earnings
        self.earnings[subscription.creator_id]['total_members'] -= 1
        self.earnings[subscription.creator_id]['monthly_revenue'] -= subscription.monthly_price
        
        return subscription
    
    async def get_creator_earnings(self, creator_id: str) -> Dict:
        """Get creator earnings dashboard"""
        if creator_id not in self.earnings:
            return {'total_members': 0, 'monthly_revenue': 0.0, 'tiers': {}}
        
        return self.earnings[creator_id]

# ============================================================================
# ADVANCED RECOMMENDATION ENGINE - CROSS-PLATFORM
# ============================================================================

@dataclass
class UserProfile:
    """User engagement profile"""
    user_id: str = ""
    interests: Dict[str, float] = field(default_factory=dict)  # category -> interest_score
    watched_content: Set[str] = field(default_factory=set)
    liked_content: Set[str] = field(default_factory=set)
    shared_content: Set[str] = field(default_factory=set)
    time_on_category: Dict[str, int] = field(default_factory=dict)  # category -> minutes

class AdvancedRecommendationEngine:
    """Production-grade cross-platform recommendation engine"""
    
    def __init__(self):
        self.user_profiles: Dict[str, UserProfile] = {}
        self.content_embeddings: Dict[str, Dict[str, float]] = {}  # content_id -> embeddings
        self.user_similarity_cache: Dict[str, Dict[str, float]] = {}
        self.trending_content: Dict[str, float] = {}  # content_id -> trend_score
    
    async def track_engagement(self, user_id: str, content_id: str, action: str,
                              category: str, time_spent_minutes: int = 0):
        """Track user engagement across platform"""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = UserProfile(user_id=user_id)
        
        profile = self.user_profiles[user_id]
        
        # Track engagement
        if action == "view":
            profile.watched_content.add(content_id)
        elif action == "like":
            profile.liked_content.add(content_id)
        elif action == "share":
            profile.shared_content.add(content_id)
        
        # Update category interest
        if category not in profile.interests:
            profile.interests[category] = 0.0
        
        # Engagement scoring: view=1.0, like=3.0, share=5.0
        engagement_score = {
            'view': 1.0,
            'like': 3.0,
            'share': 5.0,
            'comment': 2.0
        }.get(action, 1.0)
        
        profile.interests[category] += engagement_score
        
        # Track time spent
        if category not in profile.time_on_category:
            profile.time_on_category[category] = 0
        profile.time_on_category[category] += time_spent_minutes
        
        # Update trending
        self.trending_content[content_id] = self.trending_content.get(content_id, 0.0) + engagement_score
    
    async def get_personalized_recommendations(self, user_id: str, limit: int = 10) -> List[Dict]:
        """Get personalized recommendations across all services"""
        if user_id not in self.user_profiles:
            return await self._get_trending_for_new_user(limit)
        
        profile = self.user_profiles[user_id]
        
        # Find similar users
        similar_users = await self._find_similar_users(user_id, top_k=5)
        
        # Collect content from similar users
        recommended = {}
        for similar_uid, similarity_score in similar_users:
            if similar_uid in self.user_profiles:
                similar_profile = self.user_profiles[similar_uid]
                for content_id in similar_profile.liked_content:
                    if content_id not in profile.watched_content:
                        if content_id not in recommended:
                            recommended[content_id] = 0.0
                        recommended[content_id] += similarity_score * 2.0
        
        # Collaborative filtering - content-based recommendations
        for liked_content in profile.liked_content:
            similar_content = await self._find_similar_content(liked_content, top_k=5)
            for content_id, similarity in similar_content:
                if content_id not in profile.watched_content:
                    if content_id not in recommended:
                        recommended[content_id] = 0.0
                    recommended[content_id] += similarity * 1.5
        
        # Sort by recommendation score
        ranked = sorted(recommended.items(), key=lambda x: x[1], reverse=True)[:limit]
        
        return [{'content_id': cid, 'score': score} for cid, score in ranked]
    
    async def _find_similar_users(self, user_id: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """Find similar users using interest overlap"""
        if user_id not in self.user_profiles:
            return []
        
        user_interests = self.user_profiles[user_id].interests
        similarities = []
        
        for other_id, other_profile in self.user_profiles.items():
            if other_id == user_id:
                continue
            
            # Calculate similarity using cosine-like metric
            common_categories = set(user_interests.keys()) & set(other_profile.interests.keys())
            if not common_categories:
                continue
            
            similarity = sum(
                min(user_interests[cat], other_profile.interests[cat])
                for cat in common_categories
            ) / (sum(user_interests.values()) + sum(other_profile.interests.values()))
            
            similarities.append((other_id, similarity))
        
        return sorted(similarities, key=lambda x: x[1], reverse=True)[:top_k]
    
    async def _find_similar_content(self, content_id: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """Find similar content using embeddings"""
        if content_id not in self.content_embeddings:
            return []
        
        target_embedding = self.content_embeddings[content_id]
        similarities = []
        
        for other_id, other_embedding in self.content_embeddings.items():
            if other_id == content_id:
                continue
            
            # Calculate cosine similarity
            similarity = self._cosine_similarity(target_embedding, other_embedding)
            similarities.append((other_id, similarity))
        
        return sorted(similarities, key=lambda x: x[1], reverse=True)[:top_k]
    
    async def _get_trending_for_new_user(self, limit: int) -> List[Dict]:
        """Get trending content for new users"""
        trending = sorted(self.trending_content.items(), key=lambda x: x[1], reverse=True)[:limit]
        return [{'content_id': cid, 'score': score, 'reason': 'trending'} for cid, score in trending]
    
    def _cosine_similarity(self, vec1: Dict[str, float], vec2: Dict[str, float]) -> float:
        """Calculate cosine similarity between two vectors"""
        dot_product = sum(vec1.get(k, 0) * v for k, v in vec2.items())
        mag1 = (sum(v**2 for v in vec1.values())**0.5)
        mag2 = (sum(v**2 for v in vec2.values())**0.5)
        
        if mag1 == 0 or mag2 == 0:
            return 0.0
        
        return dot_product / (mag1 * mag2)

# ============================================================================
# SERVICE INITIALIZATION & SINGLETONS
# ============================================================================

_live_shopping_service: Optional[LiveShoppingService] = None
_ecommerce_service: Optional[ECommerceService] = None
_subscription_service: Optional[SubscriptionService] = None
_recommendation_engine: Optional[AdvancedRecommendationEngine] = None

def get_live_shopping_service() -> LiveShoppingService:
    """Get or create live shopping service singleton"""
    global _live_shopping_service
    if _live_shopping_service is None:
        _live_shopping_service = LiveShoppingService()
    return _live_shopping_service

def get_ecommerce_service() -> ECommerceService:
    """Get or create e-commerce service singleton"""
    global _ecommerce_service
    if _ecommerce_service is None:
        _ecommerce_service = ECommerceService()
    return _ecommerce_service

def get_subscription_service() -> SubscriptionService:
    """Get or create subscription service singleton"""
    global _subscription_service
    if _subscription_service is None:
        _subscription_service = SubscriptionService()
    return _subscription_service

def get_recommendation_engine() -> AdvancedRecommendationEngine:
    """Get or create recommendation engine singleton"""
    global _recommendation_engine
    if _recommendation_engine is None:
        _recommendation_engine = AdvancedRecommendationEngine()
    return _recommendation_engine

def init_all_final_services() -> Dict[str, any]:
    """Initialize all final services"""
    return {
        'live_shopping': get_live_shopping_service(),
        'ecommerce': get_ecommerce_service(),
        'subscription': get_subscription_service(),
        'recommendation': get_recommendation_engine()
    }
