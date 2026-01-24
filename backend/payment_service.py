"""
PHASE 9: Enterprise Payment Service
Production-grade Stripe integration, billing, subscriptions
PCI-DSS compliant (no raw card storage)
"""

import os
import logging
from typing import Dict, Optional, List, Tuple
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from enum import Enum

import stripe
from stripe.error import CardError, RateLimitError, InvalidRequestError, AuthenticationError

logger = logging.getLogger(__name__)

# Initialize Stripe
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY", "sk_test_")
STRIPE_PUBLIC_KEY = os.environ.get("STRIPE_PUBLIC_KEY", "pk_test_")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET")


# ============================================================================
# CONFIGURATION
# ============================================================================

class PricingConfig:
    """Subscription pricing"""
    PLANS = {
        "free": {
            "name": "Free",
            "monthly_price": 0.00,
            "annual_price": 0.00,
            "stripe_price_id": None,
            "features": {
                "max_simultaneous_streams": 1,
                "max_profiles": 1,
                "max_download_count": 0,
                "max_video_quality": "480p",
                "ad_supported": True,
                "offline_downloads": False
            }
        },
        "basic": {
            "name": "Basic",
            "monthly_price": 6.99,
            "annual_price": 69.99,
            "stripe_price_id_monthly": os.environ.get("STRIPE_BASIC_MONTHLY_PRICE_ID"),
            "stripe_price_id_annual": os.environ.get("STRIPE_BASIC_ANNUAL_PRICE_ID"),
            "features": {
                "max_simultaneous_streams": 1,
                "max_profiles": 2,
                "max_download_count": 100,
                "max_video_quality": "720p",
                "ad_supported": True,
                "offline_downloads": True
            }
        },
        "standard": {
            "name": "Standard",
            "monthly_price": 12.99,
            "annual_price": 129.99,
            "stripe_price_id_monthly": os.environ.get("STRIPE_STANDARD_MONTHLY_PRICE_ID"),
            "stripe_price_id_annual": os.environ.get("STRIPE_STANDARD_ANNUAL_PRICE_ID"),
            "features": {
                "max_simultaneous_streams": 2,
                "max_profiles": 3,
                "max_download_count": 500,
                "max_video_quality": "1080p",
                "ad_supported": False,
                "offline_downloads": True
            }
        },
        "premium": {
            "name": "Premium",
            "monthly_price": 19.99,
            "annual_price": 199.99,
            "stripe_price_id_monthly": os.environ.get("STRIPE_PREMIUM_MONTHLY_PRICE_ID"),
            "stripe_price_id_annual": os.environ.get("STRIPE_PREMIUM_ANNUAL_PRICE_ID"),
            "features": {
                "max_simultaneous_streams": 4,
                "max_profiles": 5,
                "max_download_count": 1000,
                "max_video_quality": "4K",
                "ad_supported": False,
                "offline_downloads": True
            }
        },
        "family": {
            "name": "Family",
            "monthly_price": 24.99,
            "annual_price": 249.99,
            "stripe_price_id_monthly": os.environ.get("STRIPE_FAMILY_MONTHLY_PRICE_ID"),
            "stripe_price_id_annual": os.environ.get("STRIPE_FAMILY_ANNUAL_PRICE_ID"),
            "features": {
                "max_simultaneous_streams": 6,
                "max_profiles": 10,
                "max_download_count": 2000,
                "max_video_quality": "4K",
                "ad_supported": False,
                "offline_downloads": True
            }
        }
    }


# ============================================================================
# PAYMENT SERVICE
# ============================================================================

class PaymentService:
    """Stripe payment handling"""
    
    @staticmethod
    def create_customer(user_id: str, email: str, name: str) -> Dict:
        """Create Stripe customer"""
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name,
                metadata={"user_id": user_id}
            )
            logger.info(f"Created Stripe customer for user {user_id}")
            return {
                "customer_id": customer.id,
                "email": customer.email
            }
        except Exception as e:
            logger.error(f"Error creating Stripe customer: {e}")
            raise
    
    @staticmethod
    def add_payment_method(customer_id: str, card_token: str) -> Dict:
        """Add payment method to customer"""
        try:
            payment_method = stripe.PaymentMethod.create(
                type="card",
                card={
                    "token": card_token
                }
            )
            
            stripe.PaymentMethod.attach(
                payment_method.id,
                customer=customer_id
            )
            
            stripe.Customer.modify(
                customer_id,
                invoice_settings={
                    "default_payment_method": payment_method.id
                }
            )
            
            logger.info(f"Added payment method to customer {customer_id}")
            return {
                "payment_method_id": payment_method.id,
                "card_last_four": payment_method.card.last4,
                "card_brand": payment_method.card.brand,
                "card_exp_month": payment_method.card.exp_month,
                "card_exp_year": payment_method.card.exp_year
            }
        except CardError as e:
            logger.error(f"Card error: {e}")
            raise
        except Exception as e:
            logger.error(f"Error adding payment method: {e}")
            raise
    
    @staticmethod
    def create_subscription(
        customer_id: str,
        price_id: str,
        billing_cycle_anchor: Optional[int] = None
    ) -> Dict:
        """Create subscription"""
        try:
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{"price": price_id}],
                payment_behavior="default_incomplete",
                expand=["latest_invoice.payment_intent"],
                billing_cycle_anchor=billing_cycle_anchor,
                off_session=True
            )
            
            logger.info(f"Created subscription for customer {customer_id}")
            return {
                "subscription_id": subscription.id,
                "status": subscription.status,
                "current_period_start": subscription.current_period_start,
                "current_period_end": subscription.current_period_end,
                "cancel_at_period_end": subscription.cancel_at_period_end
            }
        except Exception as e:
            logger.error(f"Error creating subscription: {e}")
            raise
    
    @staticmethod
    def cancel_subscription(subscription_id: str, immediately: bool = False) -> Dict:
        """Cancel subscription"""
        try:
            if immediately:
                subscription = stripe.Subscription.delete(subscription_id)
            else:
                subscription = stripe.Subscription.modify(
                    subscription_id,
                    cancel_at_period_end=True
                )
            
            logger.info(f"Cancelled subscription {subscription_id}")
            return {
                "subscription_id": subscription.id,
                "status": subscription.status,
                "cancel_at": subscription.cancel_at,
                "cancel_at_period_end": subscription.cancel_at_period_end
            }
        except Exception as e:
            logger.error(f"Error cancelling subscription: {e}")
            raise
    
    @staticmethod
    def update_subscription(subscription_id: str, price_id: str) -> Dict:
        """Update subscription (upgrade/downgrade)"""
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            
            stripe.Subscription.modify(
                subscription_id,
                items=[{
                    "id": subscription.items.data[0].id,
                    "price": price_id
                }],
                proration_behavior="always_invoice"
            )
            
            logger.info(f"Updated subscription {subscription_id} to {price_id}")
            return {
                "subscription_id": subscription.id,
                "status": subscription.status
            }
        except Exception as e:
            logger.error(f"Error updating subscription: {e}")
            raise
    
    @staticmethod
    def process_payment(
        customer_id: str,
        amount_cents: int,
        currency: str = "usd",
        description: str = ""
    ) -> Dict:
        """Process one-time payment"""
        try:
            payment_intent = stripe.PaymentIntent.create(
                customer=customer_id,
                amount=amount_cents,
                currency=currency,
                description=description,
                off_session=True,
                confirm=False
            )
            
            logger.info(f"Created payment intent for customer {customer_id}")
            return {
                "payment_intent_id": payment_intent.id,
                "amount": payment_intent.amount,
                "currency": payment_intent.currency,
                "status": payment_intent.status,
                "client_secret": payment_intent.client_secret
            }
        except Exception as e:
            logger.error(f"Error processing payment: {e}")
            raise
    
    @staticmethod
    def refund_payment(payment_id: str, amount_cents: Optional[int] = None) -> Dict:
        """Refund payment"""
        try:
            refund_params = {"charge": payment_id}
            if amount_cents:
                refund_params["amount"] = amount_cents
            
            refund = stripe.Refund.create(**refund_params)
            
            logger.info(f"Refunded payment {payment_id}")
            return {
                "refund_id": refund.id,
                "amount": refund.amount,
                "status": refund.status
            }
        except Exception as e:
            logger.error(f"Error refunding payment: {e}")
            raise
    
    @staticmethod
    def retrieve_subscription(subscription_id: str) -> Dict:
        """Get subscription details"""
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            return {
                "subscription_id": subscription.id,
                "customer_id": subscription.customer,
                "status": subscription.status,
                "current_period_start": subscription.current_period_start,
                "current_period_end": subscription.current_period_end,
                "cancel_at_period_end": subscription.cancel_at_period_end,
                "items": [{
                    "price": item.price.id,
                    "quantity": item.quantity
                } for item in subscription.items.data]
            }
        except Exception as e:
            logger.error(f"Error retrieving subscription: {e}")
            raise
    
    @staticmethod
    def list_invoices(customer_id: str, limit: int = 10) -> List[Dict]:
        """List customer invoices"""
        try:
            invoices = stripe.Invoice.list(customer=customer_id, limit=limit)
            return [{
                "invoice_id": inv.id,
                "amount": inv.amount_paid,
                "status": inv.status,
                "created": inv.created,
                "due_date": inv.due_date,
                "paid": inv.paid,
                "pdf_url": inv.pdf
            } for inv in invoices.data]
        except Exception as e:
            logger.error(f"Error listing invoices: {e}")
            raise


# ============================================================================
# WEBHOOK HANDLER
# ============================================================================

class WebhookService:
    """Stripe webhook handling"""
    
    @staticmethod
    def verify_signature(payload: bytes, sig_header: str) -> Dict:
        """Verify webhook signature"""
        try:
            event = stripe.Webhook.construct_event(
                payload,
                sig_header,
                STRIPE_WEBHOOK_SECRET
            )
            return event
        except ValueError as e:
            logger.error(f"Invalid payload: {e}")
            raise
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid signature: {e}")
            raise
    
    @staticmethod
    def handle_payment_intent_succeeded(event: Dict) -> None:
        """Handle successful payment"""
        payment_intent = event['data']['object']
        customer_id = payment_intent['customer']
        amount = payment_intent['amount']
        
        logger.info(f"Payment succeeded for customer {customer_id}, amount: {amount}")
        # TODO: Update payment status in database
    
    @staticmethod
    def handle_payment_intent_payment_failed(event: Dict) -> None:
        """Handle failed payment"""
        payment_intent = event['data']['object']
        customer_id = payment_intent['customer']
        
        logger.error(f"Payment failed for customer {customer_id}")
        # TODO: Update payment status, notify user
    
    @staticmethod
    def handle_customer_subscription_updated(event: Dict) -> None:
        """Handle subscription update"""
        subscription = event['data']['object']
        customer_id = subscription['customer']
        
        logger.info(f"Subscription updated for customer {customer_id}")
        # TODO: Update subscription status in database
    
    @staticmethod
    def handle_customer_subscription_deleted(event: Dict) -> None:
        """Handle subscription cancellation"""
        subscription = event['data']['object']
        customer_id = subscription['customer']
        
        logger.info(f"Subscription deleted for customer {customer_id}")
        # TODO: Update subscription status, downgrade user
    
    @staticmethod
    def handle_invoice_payment_failed(event: Dict) -> None:
        """Handle invoice payment failure"""
        invoice = event['data']['object']
        customer_id = invoice['customer']
        
        logger.error(f"Invoice payment failed for customer {customer_id}")
        # TODO: Send notification to user


# ============================================================================
# BILLING SERVICE
# ============================================================================

class BillingService:
    """Billing and subscription management"""
    
    @staticmethod
    def get_plan_details(plan_name: str) -> Dict:
        """Get subscription plan details"""
        if plan_name not in PricingConfig.PLANS:
            raise ValueError(f"Unknown plan: {plan_name}")
        
        return PricingConfig.PLANS[plan_name]
    
    @staticmethod
    def calculate_proration(
        old_plan: str,
        new_plan: str,
        billing_cycle_end: datetime
    ) -> Dict:
        """Calculate proration credits"""
        old_price = Decimal(str(PricingConfig.PLANS[old_plan]["monthly_price"]))
        new_price = Decimal(str(PricingConfig.PLANS[new_plan]["monthly_price"]))
        
        days_remaining = (billing_cycle_end - datetime.now(timezone.utc)).days
        days_in_month = 30  # Approximate
        
        daily_old_rate = old_price / days_in_month
        daily_new_rate = new_price / days_in_month
        
        credit = daily_old_rate * days_remaining
        charge = daily_new_rate * days_remaining
        
        net = charge - credit
        
        return {
            "old_plan": old_plan,
            "new_plan": new_plan,
            "credit": float(credit),
            "charge": float(charge),
            "net": float(net),
            "days_remaining": days_remaining
        }
    
    @staticmethod
    def apply_coupon(coupon_code: str) -> Dict:
        """Apply discount coupon"""
        try:
            coupon = stripe.Coupon.retrieve(coupon_code)
            return {
                "coupon_id": coupon.id,
                "percent_off": coupon.percent_off,
                "amount_off": coupon.amount_off,
                "duration": coupon.duration,
                "duration_in_months": coupon.duration_in_months,
                "valid": True
            }
        except stripe.error.InvalidRequestError:
            return {"valid": False, "error": "Invalid coupon"}
        except Exception as e:
            logger.error(f"Error applying coupon: {e}")
            raise
    
    @staticmethod
    def generate_invoice(user_id: str, description: str, amount_cents: int) -> Dict:
        """Generate custom invoice"""
        try:
            # TODO: Get customer ID from database
            customer_id = "cus_xxx"
            
            invoice = stripe.Invoice.create(
                customer=customer_id,
                description=description,
                custom_fields=[{
                    "name": "User ID",
                    "value": user_id
                }]
            )
            
            return {
                "invoice_id": invoice.id,
                "status": invoice.status,
                "pdf_url": invoice.pdf
            }
        except Exception as e:
            logger.error(f"Error generating invoice: {e}")
            raise


if __name__ == "__main__":
    # Test Stripe connection
    try:
        account = stripe.Account.retrieve()
        print(f"✅ Connected to Stripe account: {account.email}")
    except Exception as e:
        print(f"❌ Stripe connection error: {e}")
    
    # Test pricing config
    print("\n📊 Subscription Plans:")
    for plan_name, details in PricingConfig.PLANS.items():
        print(f"  {plan_name}: ${details['monthly_price']}/month")
