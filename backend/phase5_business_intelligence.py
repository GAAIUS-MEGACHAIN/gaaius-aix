"""
PHASE 5: BUSINESS INTELLIGENCE & MONETIZATION
Advanced revenue optimization, predictive analytics, and growth strategies
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import math
import logging

logger = logging.getLogger(__name__)


class RevenueModel(str, Enum):
    """Revenue stream types"""
    ADS = "ads"
    SUBSCRIPTIONS = "subscriptions"
    PPV = "ppv"  # Pay per view
    DONATIONS = "donations"
    AFFILIATE = "affiliate"
    SPONSORSHIPS = "sponsorships"
    MARKETPLACE = "marketplace"


@dataclass
class RevenueEvent:
    """Revenue tracking event"""
    event_type: RevenueModel
    amount: float
    user_id: str
    creator_id: Optional[str] = None
    video_id: Optional[str] = None
    timestamp: datetime = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
        if self.metadata is None:
            self.metadata = {}


class RevenueOptimizer:
    """Optimizes revenue from different streams"""
    
    def __init__(self, db, redis_client):
        self.db = db
        self.redis = redis_client
    
    async def track_revenue(self, event: RevenueEvent):
        """Track revenue event"""
        try:
            if not self.db:
                return
            
            # Insert to database
            await self.db.revenue_events.insert_one(asdict(event))
            
            # Update Redis counters
            counter_key = f"revenue:{event.event_type}"
            await self.redis.incrbyfloat(counter_key, event.amount)
            await self.redis.expire(counter_key, 2592000)  # 30d TTL
            
            # Creator revenue
            if event.creator_id:
                creator_key = f"revenue:creator:{event.creator_id}"
                await self.redis.incrbyfloat(creator_key, event.amount)
                await self.redis.expire(creator_key, 2592000)
            
            logger.info(f"Revenue tracked: ${event.amount} ({event.event_type})")
        except Exception as e:
            logger.error(f"Revenue tracking error: {e}")
    
    async def get_revenue_metrics(
        self,
        period_days: int = 30,
        group_by: str = "daily"
    ) -> Dict[str, Any]:
        """Get revenue metrics"""
        try:
            if not self.db:
                return {}
            
            start_date = datetime.utcnow() - timedelta(days=period_days)
            
            # Query revenue events
            pipeline = [
                {"$match": {"timestamp": {"$gte": start_date}}},
                {
                    "$group": {
                        "_id": {
                            "date": {
                                "$dateToString": {
                                    "format": "%Y-%m-%d" if group_by == "daily" else "%Y-%m",
                                    "date": "$timestamp"
                                }
                            },
                            "type": "$event_type"
                        },
                        "total": {"$sum": "$amount"},
                        "count": {"$sum": 1}
                    }
                },
                {"$sort": {"_id.date": 1}}
            ]
            
            results = await self.db.revenue_events.aggregate(pipeline).to_list(None)
            
            metrics = {
                "period_days": period_days,
                "total_revenue": 0,
                "by_stream": {},
                "by_date": {}
            }
            
            for result in results:
                revenue_type = result["_id"]["type"]
                date = result["_id"]["date"]
                amount = result["total"]
                
                metrics["total_revenue"] += amount
                
                if revenue_type not in metrics["by_stream"]:
                    metrics["by_stream"][revenue_type] = 0
                metrics["by_stream"][revenue_type] += amount
                
                if date not in metrics["by_date"]:
                    metrics["by_date"][date] = {}
                metrics["by_date"][date][revenue_type] = amount
            
            return metrics
        except Exception as e:
            logger.error(f"Revenue metrics error: {e}")
            return {}
    
    async def get_creator_earnings(self, creator_id: str, period_days: int = 30) -> Dict[str, Any]:
        """Get creator earnings breakdown"""
        try:
            if not self.db:
                return {}
            
            start_date = datetime.utcnow() - timedelta(days=period_days)
            
            pipeline = [
                {
                    "$match": {
                        "creator_id": creator_id,
                        "timestamp": {"$gte": start_date}
                    }
                },
                {
                    "$group": {
                        "_id": "$event_type",
                        "total": {"$sum": "$amount"},
                        "count": {"$sum": 1}
                    }
                }
            ]
            
            results = await self.db.revenue_events.aggregate(pipeline).to_list(None)
            
            earnings = {
                "creator_id": creator_id,
                "period_days": period_days,
                "total_earnings": 0,
                "by_type": {}
            }
            
            for result in results:
                revenue_type = result["_id"]
                amount = result["total"]
                count = result["count"]
                
                earnings["total_earnings"] += amount
                earnings["by_type"][revenue_type] = {
                    "amount": amount,
                    "transactions": count,
                    "average": amount / count if count > 0 else 0
                }
            
            return earnings
        except Exception as e:
            logger.error(f"Creator earnings error: {e}")
            return {}
    
    async def optimize_pricing(self, video_id: str) -> Dict[str, Any]:
        """Recommend pricing optimization"""
        try:
            if not self.db:
                return {}
            
            # Get video engagement metrics
            video = await self.db.videos.find_one({"_id": video_id})
            if not video:
                return {}
            
            # Get PPV events for this video
            ppv_events = await self.db.revenue_events.find({
                "video_id": video_id,
                "event_type": RevenueModel.PPV
            }).to_list(None)
            
            if not ppv_events:
                return {"recommendation": "insufficient_data"}
            
            total_revenue = sum(e["amount"] for e in ppv_events)
            total_views = len(ppv_events)
            avg_price = total_revenue / total_views if total_views > 0 else 0
            
            # Optimization recommendations
            recommendations = {
                "current_avg_price": avg_price,
                "total_transactions": total_views,
                "optimization": {}
            }
            
            # If conversion is low, recommend price reduction
            if total_views < 10:
                recommendations["optimization"]["action"] = "reduce_price"
                recommendations["optimization"]["suggested_price"] = avg_price * 0.8
                recommendations["optimization"]["reason"] = "Low conversion rate"
            # If high conversion, recommend price increase
            elif total_views > 100:
                recommendations["optimization"]["action"] = "increase_price"
                recommendations["optimization"]["suggested_price"] = avg_price * 1.2
                recommendations["optimization"]["reason"] = "High conversion rate"
            else:
                recommendations["optimization"]["action"] = "maintain"
                recommendations["optimization"]["suggested_price"] = avg_price
                recommendations["optimization"]["reason"] = "Pricing is optimal"
            
            return recommendations
        except Exception as e:
            logger.error(f"Pricing optimization error: {e}")
            return {}


class PredictiveAnalytics:
    """Predicts trends and user behavior"""
    
    def __init__(self, db):
        self.db = db
    
    async def predict_churn_risk(self, user_id: str) -> float:
        """Predict user churn risk (0-1)"""
        try:
            if not self.db:
                return 0.0
            
            # Get user activity
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            seven_days_ago = datetime.utcnow() - timedelta(days=7)
            
            activity_30d = await self.db.analytics_events.count_documents({
                "user_id": user_id,
                "timestamp": {"$gte": thirty_days_ago}
            })
            
            activity_7d = await self.db.analytics_events.count_documents({
                "user_id": user_id,
                "timestamp": {"$gte": seven_days_ago}
            })
            
            # Calculate trend
            activity_decline = (activity_30d - activity_7d) / activity_30d if activity_30d > 0 else 0
            
            # Risk factors
            risk_score = 0.0
            
            # No recent activity
            if activity_7d == 0:
                risk_score += 0.7
            # Declining activity
            elif activity_decline > 0.5:
                risk_score += 0.4
            # Low activity
            elif activity_30d < 5:
                risk_score += 0.3
            
            # Clamp to 0-1
            return min(max(risk_score, 0.0), 1.0)
        except Exception as e:
            logger.error(f"Churn prediction error: {e}")
            return 0.0
    
    async def predict_video_performance(self, video_id: str) -> Dict[str, Any]:
        """Predict video performance trajectory"""
        try:
            if not self.db:
                return {}
            
            video = await self.db.videos.find_one({"_id": video_id})
            if not video:
                return {}
            
            # Get video engagement trajectory
            now = datetime.utcnow()
            views_by_day = []
            
            for day_offset in range(0, 30):
                day_start = now - timedelta(days=30 - day_offset)
                day_end = day_start + timedelta(days=1)
                
                daily_views = await self.db.analytics_events.count_documents({
                    "video_id": video_id,
                    "event_type": "view",
                    "timestamp": {"$gte": day_start, "$lt": day_end}
                })
                
                views_by_day.append(daily_views)
            
            # Calculate trend
            if len(views_by_day) >= 2:
                recent_trend = (sum(views_by_day[-7:]) - sum(views_by_day[-14:-7])) / sum(views_by_day[-14:-7]) if sum(views_by_day[-14:-7]) > 0 else 0
            else:
                recent_trend = 0.0
            
            predictions = {
                "video_id": video_id,
                "current_views": sum(views_by_day),
                "trend": "increasing" if recent_trend > 0.1 else "stable" if recent_trend > -0.1 else "declining",
                "trend_percent": recent_trend * 100,
                "predicted_30d_views": sum(views_by_day) * (1 + recent_trend),
                "virality_score": min(max(recent_trend, 0.0), 1.0)
            }
            
            return predictions
        except Exception as e:
            logger.error(f"Video performance prediction error: {e}")
            return {}
    
    async def predict_trending_topics(self) -> List[Dict[str, Any]]:
        """Predict trending topics"""
        try:
            if not self.db:
                return []
            
            # Get recent video tags
            pipeline = [
                {
                    "$match": {
                        "timestamp": {"$gte": datetime.utcnow() - timedelta(days=7)}
                    }
                },
                {
                    "$unwind": "$tags"
                },
                {
                    "$group": {
                        "_id": "$tags",
                        "count": {"$sum": 1},
                        "trend": {"$avg": {"$cond": [{"$gte": ["$timestamp", datetime.utcnow() - timedelta(days=1)]}, 1, 0]}}
                    }
                },
                {
                    "$sort": {"trend": -1}
                },
                {
                    "$limit": 10
                }
            ]
            
            trending = await self.db.videos.aggregate(pipeline).to_list(None)
            
            return [
                {
                    "topic": t["_id"],
                    "mentions": t["count"],
                    "trend_momentum": t["trend"],
                    "growth": "up" if t["trend"] > 0.5 else "stable"
                }
                for t in trending
            ]
        except Exception as e:
            logger.error(f"Trending topics prediction error: {e}")
            return []


class GrowthOptimization:
    """Optimizes platform growth"""
    
    def __init__(self, db, redis_client):
        self.db = db
        self.redis = redis_client
    
    async def calculate_ltv(self, user_id: str) -> float:
        """Calculate user lifetime value"""
        try:
            if not self.db:
                return 0.0
            
            # Get total revenue generated by user
            pipeline = [
                {
                    "$match": {
                        "$or": [
                            {"user_id": user_id},
                            {"creator_id": user_id}
                        ]
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "total": {"$sum": "$amount"}
                    }
                }
            ]
            
            result = await self.db.revenue_events.aggregate(pipeline).to_list(1)
            
            if result:
                return float(result[0]["total"])
            return 0.0
        except Exception as e:
            logger.error(f"LTV calculation error: {e}")
            return 0.0
    
    async def calculate_cac(self, cohort_acquisition_cost: float, cohort_size: int) -> float:
        """Calculate customer acquisition cost"""
        if cohort_size == 0:
            return 0.0
        return cohort_acquisition_cost / cohort_size
    
    async def get_growth_metrics(self) -> Dict[str, Any]:
        """Get platform growth metrics"""
        try:
            if not self.db:
                return {}
            
            now = datetime.utcnow()
            week_ago = now - timedelta(days=7)
            month_ago = now - timedelta(days=30)
            
            # New users this week/month
            new_users_week = await self.db.users.count_documents({
                "created_at": {"$gte": week_ago}
            })
            
            new_users_month = await self.db.users.count_documents({
                "created_at": {"$gte": month_ago}
            })
            
            # Total users
            total_users = await self.db.users.count_documents({})
            
            # DAU/MAU
            dau = await self.db.analytics_events.count_documents({
                "timestamp": {"$gte": now - timedelta(days=1)}
            })
            
            mau = await self.db.analytics_events.count_documents({
                "timestamp": {"$gte": month_ago}
            })
            
            metrics = {
                "total_users": total_users,
                "new_users_week": new_users_week,
                "new_users_month": new_users_month,
                "dau": dau,
                "mau": mau,
                "dau_mau_ratio": dau / mau if mau > 0 else 0,
                "daily_growth_rate": new_users_week / 7 if total_users > 0 else 0
            }
            
            return metrics
        except Exception as e:
            logger.error(f"Growth metrics error: {e}")
            return {}


class Phase5BusinessIntelligence:
    """Master business intelligence integrator for Phase 5"""
    
    def __init__(self):
        self.db = None
        self.redis = None
        self.revenue_optimizer = None
        self.predictive = None
        self.growth = None
    
    async def initialize(self, db, redis_client):
        """Initialize BI infrastructure"""
        try:
            self.db = db
            self.redis = redis_client
            
            self.revenue_optimizer = RevenueOptimizer(db, redis_client)
            self.predictive = PredictiveAnalytics(db)
            self.growth = GrowthOptimization(db, redis_client)
            
            logger.info("✅ Phase 5 Business Intelligence initialized")
            return True
        except Exception as e:
            logger.error(f"BI initialization error: {e}")
            return False
    
    async def shutdown(self):
        """Shutdown BI"""
        try:
            logger.info("✅ Phase 5 Business Intelligence shutdown complete")
        except Exception as e:
            logger.error(f"BI shutdown error: {e}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for BI"""
        return {
            "status": "healthy",
            "components": {
                "revenue_optimizer": bool(self.revenue_optimizer),
                "predictive_analytics": bool(self.predictive),
                "growth_optimization": bool(self.growth)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
