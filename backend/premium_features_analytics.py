"""
PREMIUM FEATURES ANALYTICS MODULE
================================================================================
Complete analytics for enterprise premium features:
- Video Editor Analytics (trimming, effects, subtitles)
- Duet/Collaboration Tool Analytics
- Shop/E-Commerce Analytics
- Subscription/Patreon Clone Analytics
- Events Platform Analytics
- Newsletter Service Analytics
- Affiliate Marketing Analytics

All systems include:
- Real-time tracking
- User engagement metrics
- Revenue/financial tracking
- Performance analysis
- Trend detection
- Business intelligence metrics

Production-Ready | Enterprise Grade
================================================================================
"""

from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import statistics
import logging

logger = logging.getLogger(__name__)

# ============== ENUMS ==============

class EditorEffect(str, Enum):
    """Video editor effects"""
    FILTER = "filter"
    TRANSITION = "transition"
    OVERLAY = "overlay"
    ANIMATION = "animation"
    ADJUSTMENT = "adjustment"
    CUSTOM = "custom"


class SubscriptionTier(str, Enum):
    """Subscription tiers"""
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ELITE = "elite"
    PREMIUM = "premium"


class EventType(str, Enum):
    """Event types"""
    WEBINAR = "webinar"
    CONFERENCE = "conference"
    WORKSHOP = "workshop"
    MEETUP = "meetup"
    CONCERT = "concert"
    FESTIVAL = "festival"
    NETWORKING = "networking"
    TRAINING = "training"


class EmailCampaignType(str, Enum):
    """Email campaign types"""
    NEWSLETTER = "newsletter"
    PROMOTIONAL = "promotional"
    ANNOUNCEMENT = "announcement"
    EDUCATIONAL = "educational"
    ENGAGEMENT = "engagement"
    RETENTION = "retention"
    REACTIVATION = "reactivation"


class ProductCategory(str, Enum):
    """E-commerce product categories"""
    MERCHANDISE = "merchandise"
    DIGITAL = "digital"
    COURSE = "course"
    SERVICE = "service"
    SUBSCRIPTION = "subscription"
    PHYSICAL = "physical"
    VIRTUAL = "virtual"


# ============== ANALYTICS CLASSES ==============

class VideoEditorAnalytics:
    """Analytics for video editor with trimming, effects, and subtitles"""
    
    @staticmethod
    def analyze_editor_usage(events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze video editor usage patterns"""
        editor_events = [e for e in events if e.get('feature') == 'video_editor']
        
        if not editor_events:
            return {
                'total_edits': 0,
                'total_users': 0,
                'avg_editing_duration': 0,
                'effects_used': {},
                'subtitles_added': 0,
                'trims_performed': 0,
            }
        
        unique_users = len(set(e.get('user_id') for e in editor_events))
        
        # Trim operations
        trim_events = [e for e in editor_events if e.get('activity') == 'trim']
        avg_trim_time = statistics.mean([e.get('duration_seconds', 0) for e in trim_events]) if trim_events else 0
        
        # Effects
        effect_events = [e for e in editor_events if e.get('activity') == 'effect']
        effects_used = defaultdict(int)
        for e in effect_events:
            effect_type = e.get('metadata', {}).get('effect_type', 'unknown')
            effects_used[effect_type] += 1
        
        # Subtitles
        subtitle_events = [e for e in editor_events if e.get('activity') == 'subtitle']
        
        # Exports
        export_events = [e for e in editor_events if e.get('activity') == 'export']
        
        return {
            'total_edits': len(editor_events),
            'unique_editors': unique_users,
            'avg_editing_duration': statistics.mean([e.get('duration_seconds', 0) for e in editor_events]) if editor_events else 0,
            'total_trims': len(trim_events),
            'avg_trim_duration': avg_trim_time,
            'total_effects_applied': len(effect_events),
            'effects_breakdown': dict(effects_used),
            'total_subtitles_added': len(subtitle_events),
            'total_exports': len(export_events),
            'export_formats': [e.get('metadata', {}).get('format') for e in export_events],
            'avg_video_length': statistics.mean([e.get('metadata', {}).get('video_duration', 0) for e in editor_events if e.get('metadata', {}).get('video_duration')]),
            'success_rate': (len([e for e in editor_events if e.get('success', False)]) / len(editor_events)) * 100 if editor_events else 0,
            'editor_completion_rate': (len(export_events) / len([e for e in editor_events if e.get('activity') in ['trim', 'effect', 'subtitle']]) * 100) if editor_events else 0,
        }


class DuetCollabAnalytics:
    """Analytics for duet and collaboration tool"""
    
    @staticmethod
    def analyze_collaborations(events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze duet/collab video creation patterns"""
        collab_events = [e for e in events if e.get('feature') == 'duet_collab']
        
        if not collab_events:
            return {
                'total_collaborations': 0,
                'active_duet_creators': 0,
                'avg_collaboration_size': 0,
                'completed_duets': 0,
                'avg_remix_views': 0,
            }
        
        # Duet initiations
        initiation_events = [e for e in collab_events if e.get('activity') == 'initiate']
        
        # Collaborations completed
        completion_events = [e for e in collab_events if e.get('activity') == 'complete']
        
        # Unique participants
        all_participants = set()
        for e in collab_events:
            all_participants.add(e.get('user_id'))
            all_participants.update(e.get('metadata', {}).get('participants', []))
        
        # Remixes/reuses
        remix_events = [e for e in collab_events if e.get('activity') == 'remix']
        
        return {
            'total_duet_initiations': len(initiation_events),
            'total_collaborations': len(collab_events),
            'unique_participants': len(all_participants),
            'completed_duets': len(completion_events),
            'duet_completion_rate': (len(completion_events) / len(initiation_events) * 100) if initiation_events else 0,
            'total_remixes': len(remix_events),
            'avg_participants_per_duet': (sum([len(e.get('metadata', {}).get('participants', [])) for e in collab_events]) / len(collab_events)) if collab_events else 0,
            'collab_retention_rate': (len([e for e in collab_events if e.get('success', False)]) / len(collab_events) * 100) if collab_events else 0,
            'avg_duet_views': statistics.mean([e.get('metadata', {}).get('views', 0) for e in completion_events]) if completion_events else 0,
            'most_active_collaborators': len([e for e in collab_events if e.get('metadata', {}).get('collaboration_count', 0) > 5]),
        }


class ShopAnalytics:
    """Analytics for e-commerce shop"""
    
    @staticmethod
    def analyze_shop_operations(events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze shop and merchandise operations"""
        shop_events = [e for e in events if e.get('feature') == 'shop']
        
        if not shop_events:
            return {
                'total_sales': 0,
                'total_revenue': 0,
                'products_listed': 0,
                'conversion_rate': 0,
                'avg_order_value': 0,
            }
        
        # Sales events
        sale_events = [e for e in shop_events if e.get('activity') == 'purchase']
        
        # Product listings
        listing_events = [e for e in shop_events if e.get('activity') == 'list']
        
        # Cart operations
        cart_events = [e for e in shop_events if e.get('activity') == 'cart']
        
        # Checkout operations
        checkout_events = [e for e in shop_events if e.get('activity') == 'checkout']
        
        total_revenue = sum([e.get('metadata', {}).get('amount', 0) for e in sale_events])
        unique_buyers = len(set(e.get('user_id') for e in sale_events))
        
        return {
            'total_products_listed': len(listing_events),
            'active_products': len(set(e.get('metadata', {}).get('product_id') for e in shop_events)),
            'total_sales': len(sale_events),
            'unique_buyers': unique_buyers,
            'total_revenue': total_revenue,
            'avg_order_value': total_revenue / len(sale_events) if sale_events else 0,
            'cart_additions': len(cart_events),
            'cart_abandonment_rate': ((len(cart_events) - len(checkout_events)) / len(cart_events) * 100) if cart_events else 0,
            'checkout_completion_rate': (len(sale_events) / len(checkout_events) * 100) if checkout_events else 0,
            'product_categories': [e.get('metadata', {}).get('category') for e in listing_events],
            'repeat_buyers': len([uid for uid in set(e.get('user_id') for e in sale_events) if len([e for e in sale_events if e.get('user_id') == uid]) > 1]),
            'inventory_turnover': len(sale_events) / len(listing_events) if listing_events else 0,
        }


class SubscriptionAnalytics:
    """Analytics for subscription/Patreon-like platform"""
    
    @staticmethod
    def analyze_subscriptions(events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze subscription and exclusive content access"""
        sub_events = [e for e in events if e.get('feature') == 'subscription']
        
        if not sub_events:
            return {
                'total_subscribers': 0,
                'monthly_recurring_revenue': 0,
                'churn_rate': 0,
                'tier_distribution': {},
            }
        
        # Subscription creation
        new_sub_events = [e for e in sub_events if e.get('activity') == 'subscribe']
        
        # Cancellations
        cancel_events = [e for e in sub_events if e.get('activity') == 'cancel']
        
        # Tier changes
        upgrade_events = [e for e in sub_events if e.get('activity') == 'upgrade']
        downgrade_events = [e for e in sub_events if e.get('activity') == 'downgrade']
        
        # Exclusive content access
        content_access_events = [e for e in sub_events if e.get('activity') == 'access_exclusive']
        
        # Revenue
        subscription_revenue = sum([e.get('metadata', {}).get('amount', 0) for e in new_sub_events])
        
        # Tier distribution
        tier_dist = defaultdict(int)
        for e in sub_events:
            tier = e.get('metadata', {}).get('tier', 'unknown')
            tier_dist[tier] += 1
        
        return {
            'total_subscribers': len(set(e.get('user_id') for e in new_sub_events)),
            'active_subscriptions': len(new_sub_events) - len(cancel_events),
            'new_subscriptions': len(new_sub_events),
            'cancellations': len(cancel_events),
            'churn_rate': (len(cancel_events) / len(new_sub_events) * 100) if new_sub_events else 0,
            'total_upgrades': len(upgrade_events),
            'total_downgrades': len(downgrade_events),
            'monthly_recurring_revenue': subscription_revenue,
            'tier_distribution': dict(tier_dist),
            'exclusive_content_accesses': len(content_access_events),
            'avg_subscription_value': subscription_revenue / len(new_sub_events) if new_sub_events else 0,
            'subscriber_lifetime_value': subscription_revenue / len(set(e.get('user_id') for e in new_sub_events)) if new_sub_events else 0,
            'net_subscriber_growth': len(new_sub_events) - len(cancel_events),
        }


class EventsAnalytics:
    """Analytics for events platform"""
    
    @staticmethod
    def analyze_events(events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze event creation, ticket sales, and attendance"""
        event_events = [e for e in events if e.get('feature') == 'events_platform']
        
        if not event_events:
            return {
                'total_events': 0,
                'total_tickets_sold': 0,
                'total_revenue': 0,
                'attendance_rate': 0,
                'avg_event_size': 0,
            }
        
        # Event creation
        creation_events = [e for e in event_events if e.get('activity') == 'create']
        
        # Ticket sales
        ticket_sales = [e for e in event_events if e.get('activity') == 'buy_ticket']
        
        # RSVP events
        rsvp_events = [e for e in event_events if e.get('activity') == 'rsvp']
        
        # Attendance
        attendance_events = [e for e in event_events if e.get('activity') == 'attend']
        
        total_revenue = sum([e.get('metadata', {}).get('ticket_price', 0) for e in ticket_sales])
        
        return {
            'total_events_created': len(creation_events),
            'total_rsvps': len(rsvp_events),
            'total_tickets_sold': len(ticket_sales),
            'unique_attendees': len(set(e.get('user_id') for e in attendance_events)),
            'actual_attendance': len(attendance_events),
            'attendance_rate': (len(attendance_events) / len(rsvp_events) * 100) if rsvp_events else 0,
            'total_revenue': total_revenue,
            'avg_revenue_per_event': total_revenue / len(creation_events) if creation_events else 0,
            'avg_event_attendance': len(attendance_events) / len(creation_events) if creation_events else 0,
            'event_types': [e.get('metadata', {}).get('event_type') for e in creation_events],
            'venue_capacity_utilization': (len(attendance_events) / sum([e.get('metadata', {}).get('capacity', 1) for e in creation_events]) * 100) if creation_events else 0,
            'repeat_attendees': len([uid for uid in set(e.get('user_id') for e in attendance_events) if len([e for e in attendance_events if e.get('user_id') == uid]) > 1]),
        }


class NewsletterAnalytics:
    """Analytics for newsletter/email service"""
    
    @staticmethod
    def analyze_newsletter(events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze email campaigns and subscriber engagement"""
        newsletter_events = [e for e in events if e.get('feature') == 'newsletter']
        
        if not newsletter_events:
            return {
                'campaigns_sent': 0,
                'subscribers': 0,
                'open_rate': 0,
                'click_rate': 0,
                'unsubscribe_rate': 0,
            }
        
        # Campaign sends
        send_events = [e for e in newsletter_events if e.get('activity') == 'send']
        
        # Opens
        open_events = [e for e in newsletter_events if e.get('activity') == 'open']
        
        # Clicks
        click_events = [e for e in newsletter_events if e.get('activity') == 'click']
        
        # Unsubscribes
        unsubscribe_events = [e for e in newsletter_events if e.get('activity') == 'unsubscribe']
        
        # Subscribers
        subscriber_events = [e for e in newsletter_events if e.get('activity') == 'subscribe']
        
        total_recipients = sum([e.get('metadata', {}).get('recipient_count', 0) for e in send_events])
        
        return {
            'total_campaigns_sent': len(send_events),
            'total_subscribers': len(set(e.get('user_id') for e in subscriber_events)),
            'active_subscribers': len(set(e.get('user_id') for e in subscriber_events)) - len(unsubscribe_events),
            'total_recipients': total_recipients,
            'total_opens': len(open_events),
            'open_rate': (len(open_events) / total_recipients * 100) if total_recipients > 0 else 0,
            'total_clicks': len(click_events),
            'click_through_rate': (len(click_events) / len(open_events) * 100) if open_events else 0,
            'total_unsubscribes': len(unsubscribe_events),
            'unsubscribe_rate': (len(unsubscribe_events) / total_recipients * 100) if total_recipients > 0 else 0,
            'avg_open_rate_per_campaign': statistics.mean([e.get('metadata', {}).get('open_rate', 0) for e in send_events]) if send_events else 0,
            'campaign_types': [e.get('metadata', {}).get('campaign_type') for e in send_events],
            'bounce_rate': (len([e for e in send_events if e.get('metadata', {}).get('bounced', 0) > 0]) / len(send_events) * 100) if send_events else 0,
        }


class AffiliateMarketingAnalytics:
    """Analytics for affiliate marketing and referral programs"""
    
    @staticmethod
    def analyze_affiliates(events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze affiliate performance and commission tracking"""
        affiliate_events = [e for e in events if e.get('feature') == 'affiliate_marketing']
        
        if not affiliate_events:
            return {
                'total_affiliates': 0,
                'referral_clicks': 0,
                'conversions': 0,
                'total_commissions': 0,
                'conversion_rate': 0,
            }
        
        # Link clicks
        click_events = [e for e in affiliate_events if e.get('activity') == 'click']
        
        # Conversions
        conversion_events = [e for e in affiliate_events if e.get('activity') == 'conversion']
        
        # Commission payouts
        payout_events = [e for e in affiliate_events if e.get('activity') == 'payout']
        
        total_commissions = sum([e.get('metadata', {}).get('commission_amount', 0) for e in payout_events])
        unique_affiliates = len(set(e.get('user_id') for e in affiliate_events))
        
        return {
            'total_active_affiliates': unique_affiliates,
            'total_referral_clicks': len(click_events),
            'total_conversions': len(conversion_events),
            'conversion_rate': (len(conversion_events) / len(click_events) * 100) if click_events else 0,
            'unique_referred_users': len(set(e.get('metadata', {}).get('referred_user_id') for e in conversion_events)),
            'total_commissions_paid': total_commissions,
            'avg_commission_per_affiliate': total_commissions / unique_affiliates if unique_affiliates > 0 else 0,
            'total_payouts': len(payout_events),
            'top_performing_affiliates': len([uid for uid in set(e.get('user_id') for e in click_events) if len([e for e in conversion_events if e.get('user_id') == uid]) > 5]),
            'affiliate_retention_rate': (len([e for e in affiliate_events if e.get('activity') in ['click', 'conversion']]) / len(affiliate_events) * 100) if affiliate_events else 0,
            'avg_clicks_per_affiliate': len(click_events) / unique_affiliates if unique_affiliates > 0 else 0,
            'avg_conversions_per_affiliate': len(conversion_events) / unique_affiliates if unique_affiliates > 0 else 0,
            'link_sources': [e.get('metadata', {}).get('link_source') for e in click_events],
        }
