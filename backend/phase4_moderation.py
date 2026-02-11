"""
PHASE 4: ML-Based Content Moderation System
Production-grade content moderation with manual review queue and appeals
"""

import logging
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime, timedelta
import uuid
import re

from motor.motor_asyncio import AsyncIOMotorDatabase
import redis.asyncio as aioredis


logger = logging.getLogger(__name__)


class ContentFlag(str, Enum):
    """Content flag types"""
    SPAM = "spam"
    EXPLICIT = "explicit"
    HARASSMENT = "harassment"
    MISLEADING = "misleading"
    COPYRIGHT = "copyright"
    OTHER = "other"


class ModerationAction(str, Enum):
    """Actions taken by moderators"""
    APPROVE = "approve"
    REJECT = "reject"
    STRIKE = "strike"
    SUSPEND = "suspend"
    PERMANENT_BAN = "permanent_ban"
    WARNING = "warning"


class ModerationStatus(str, Enum):
    """Status of moderation review"""
    PENDING = "pending"
    REVIEWING = "reviewing"
    RESOLVED = "resolved"
    APPEALED = "appealed"


class ContentModerationSystem:
    """ML-powered content moderation with manual review"""
    
    def __init__(self, redis: aioredis.Redis, db: AsyncIOMotorDatabase):
        self.redis = redis
        self.db = db
        self.flagged_content_collection = db["flagged_content"]
        self.moderation_queue_collection = db["moderation_queue"]
        self.moderation_actions_collection = db["moderation_actions"]
        self.user_strikes_collection = db["user_strikes"]
        self.appeals_collection = db["appeals"]
    
    async def flag_content(
        self,
        content_id: str,
        content_type: str,  # "video", "comment", "channel"
        flag_type: ContentFlag,
        reporter_id: str,
        reason: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Flag content for review"""
        
        flag_id = str(uuid.uuid4())
        
        flag_entry = {
            "_id": flag_id,
            "content_id": content_id,
            "content_type": content_type,
            "flag_type": flag_type.value,
            "reporter_id": reporter_id,
            "reason": reason,
            "metadata": metadata or {},
            "created_at": datetime.utcnow(),
            "automation_score": await self._calculate_automation_score(
                flag_type, reason, content_type
            ),
            "status": "pending",
            "auto_action": None,
        }
        
        await self.flagged_content_collection.insert_one(flag_entry)
        
        # Add to moderation queue
        await self._add_to_moderation_queue(flag_id, flag_entry)
        
        logger.info(f"Content flagged: {flag_id} ({flag_type.value})")
        return flag_id
    
    async def get_moderation_queue(
        self,
        priority: str = "all",
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get items for moderator review"""
        
        query = {"status": ModerationStatus.REVIEWING.value}
        
        if priority in ["high", "medium", "low"]:
            query["priority"] = priority
        
        items = await self.moderation_queue_collection.find(
            query,
            sort=[("priority", -1), ("created_at", 1)],
            skip=offset,
            limit=limit
        ).to_list(limit)
        
        return items
    
    async def review_flagged_content(
        self,
        flag_id: str,
        moderator_id: str,
        action: ModerationAction,
        reason: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Submit moderation review"""
        
        # Get original flag
        flag_entry = await self.flagged_content_collection.find_one({"_id": flag_id})
        if not flag_entry:
            return False
        
        # Create action record
        action_record = {
            "_id": str(uuid.uuid4()),
            "flag_id": flag_id,
            "moderator_id": moderator_id,
            "action": action.value,
            "reason": reason,
            "metadata": metadata or {},
            "created_at": datetime.utcnow(),
            "content_id": flag_entry["content_id"],
            "content_type": flag_entry["content_type"],
        }
        
        await self.moderation_actions_collection.insert_one(action_record)
        
        # Update flag status
        await self.flagged_content_collection.update_one(
            {"_id": flag_id},
            {
                "$set": {
                    "status": ModerationStatus.RESOLVED.value,
                    "moderator_id": moderator_id,
                    "reviewed_at": datetime.utcnow(),
                    "action": action.value,
                }
            }
        )
        
        # Apply consequences if needed
        if action in [
            ModerationAction.STRIKE,
            ModerationAction.SUSPEND,
            ModerationAction.PERMANENT_BAN
        ]:
            await self._apply_user_strike(
                flag_entry.get("creator_id"),
                action,
                flag_id,
                reason
            )
        
        # Remove from moderation queue
        await self.moderation_queue_collection.delete_one({"flag_id": flag_id})
        
        logger.info(f"Moderation review completed: {flag_id} - {action.value}")
        return True
    
    async def appeal_moderation(
        self,
        flag_id: str,
        user_id: str,
        appeal_reason: str
    ) -> str:
        """Allow user to appeal moderation decision"""
        
        # Get original moderation action
        action = await self.moderation_actions_collection.find_one(
            {"flag_id": flag_id}
        )
        
        if not action:
            return None
        
        appeal_id = str(uuid.uuid4())
        
        appeal_record = {
            "_id": appeal_id,
            "flag_id": flag_id,
            "user_id": user_id,
            "appeal_reason": appeal_reason,
            "original_action": action["action"],
            "original_moderator_id": action["moderator_id"],
            "created_at": datetime.utcnow(),
            "status": "pending",
            "reviewed_by": None,
            "appeal_decision": None,
        }
        
        await self.appeals_collection.insert_one(appeal_record)
        
        # Update flag status
        await self.flagged_content_collection.update_one(
            {"_id": flag_id},
            {"$set": {"status": ModerationStatus.APPEALED.value}}
        )
        
        logger.info(f"Appeal submitted: {appeal_id} for flag {flag_id}")
        return appeal_id
    
    async def review_appeal(
        self,
        appeal_id: str,
        senior_moderator_id: str,
        decision: str,  # "upheld" or "overturned"
        reason: str
    ) -> bool:
        """Senior moderator review of appeal"""
        
        appeal = await self.appeals_collection.find_one({"_id": appeal_id})
        if not appeal:
            return False
        
        # Update appeal
        await self.appeals_collection.update_one(
            {"_id": appeal_id},
            {
                "$set": {
                    "status": "resolved",
                    "reviewed_by": senior_moderator_id,
                    "appeal_decision": decision,
                    "review_reason": reason,
                    "reviewed_at": datetime.utcnow(),
                }
            }
        )
        
        # If overturned, restore content
        if decision == "overturned":
            flag_id = appeal["flag_id"]
            await self.flagged_content_collection.update_one(
                {"_id": flag_id},
                {"$set": {"status": "cleared"}}
            )
            
            # Potentially remove strikes if applicable
            logger.info(f"Appeal {appeal_id} overturned - action reversed")
        
        return True
    
    async def get_user_violations(self, user_id: str) -> Dict[str, Any]:
        """Get user's violation history"""
        
        strikes = await self.user_strikes_collection.find(
            {"user_id": user_id},
            sort=[("created_at", -1)]
        ).to_list(100)
        
        # Convert timestamps
        for strike in strikes:
            strike["_id"] = str(strike["_id"])
            strike["created_at"] = strike["created_at"].isoformat()
        
        # Calculate total violations
        active_strikes = [
            s for s in strikes
            if datetime.fromisoformat(s["created_at"]) > datetime.utcnow() - timedelta(days=90)
        ]
        
        return {
            "user_id": user_id,
            "total_strikes": len(strikes),
            "active_strikes": len(active_strikes),
            "status": self._determine_user_status(active_strikes),
            "strikes": strikes
        }
    
    async def _add_to_moderation_queue(
        self,
        flag_id: str,
        flag_entry: Dict[str, Any]
    ) -> None:
        """Add flagged content to moderation queue"""
        
        # Calculate priority based on automation score and flag type
        priority = self._calculate_priority(flag_entry)
        
        queue_entry = {
            "flag_id": flag_id,
            "content_id": flag_entry["content_id"],
            "content_type": flag_entry["content_type"],
            "flag_type": flag_entry["flag_type"],
            "automation_score": flag_entry["automation_score"],
            "priority": priority,
            "created_at": datetime.utcnow(),
            "status": ModerationStatus.REVIEWING.value,
        }
        
        await self.moderation_queue_collection.insert_one(queue_entry)
    
    async def _calculate_automation_score(
        self,
        flag_type: ContentFlag,
        reason: str,
        content_type: str
    ) -> float:
        """Calculate automation confidence score (0-1)"""
        
        score = 0.0
        
        # High confidence flags
        if flag_type == ContentFlag.SPAM:
            # Check for spam patterns
            spam_patterns = [
                r"buy now", r"click here", r"visit website",
                r"make money", r"free money", r"limited offer"
            ]
            for pattern in spam_patterns:
                if re.search(pattern, reason, re.IGNORECASE):
                    score += 0.2
            score = min(0.9, score)  # Cap at 0.9
        
        elif flag_type == ContentFlag.EXPLICIT:
            score = 0.7  # Requires manual review
        
        elif flag_type == ContentFlag.HARASSMENT:
            score = 0.6  # Definitely needs human review
        
        elif flag_type == ContentFlag.COPYRIGHT:
            score = 0.8  # Usually high confidence
        
        return score
    
    def _calculate_priority(self, flag_entry: Dict[str, Any]) -> str:
        """Calculate moderation priority"""
        
        automation_score = flag_entry.get("automation_score", 0)
        flag_type = flag_entry.get("flag_type")
        
        # High priority: high automation score + serious violation
        if automation_score >= 0.8 or flag_type in ["harassment", "explicit"]:
            return "high"
        
        # Medium priority: moderate confidence
        elif automation_score >= 0.5:
            return "medium"
        
        # Low priority: low confidence
        else:
            return "low"
    
    async def _apply_user_strike(
        self,
        user_id: str,
        action: ModerationAction,
        flag_id: str,
        reason: str
    ) -> None:
        """Apply strike/suspension to user"""
        
        strike_entry = {
            "_id": str(uuid.uuid4()),
            "user_id": user_id,
            "action": action.value,
            "reason": reason,
            "flag_id": flag_id,
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(days=90),  # 90-day suspension
        }
        
        await self.user_strikes_collection.insert_one(strike_entry)
        
        # Store in Redis for quick lookup
        await self.redis.setex(
            f"user:strikes:{user_id}",
            7776000,  # 90 days
            action.value
        )
        
        logger.info(f"Strike applied to user {user_id}: {action.value}")
    
    def _determine_user_status(self, active_strikes: List[Dict[str, Any]]) -> str:
        """Determine user's current status based on strikes"""
        
        if not active_strikes:
            return "good_standing"
        
        has_ban = any(s["action"] == "permanent_ban" for s in active_strikes)
        if has_ban:
            return "permanently_banned"
        
        has_suspend = any(s["action"] == "suspend" for s in active_strikes)
        if has_suspend:
            return "suspended"
        
        strike_count = len(active_strikes)
        if strike_count >= 3:
            return "at_risk"
        
        return "flagged"


class TextAnalyzer:
    """Analyze text content for policy violations"""
    
    BANNED_KEYWORDS = {
        "hate": ["hateful word 1", "hateful word 2"],  # Placeholder
        "violence": ["violent word 1", "violent word 2"],  # Placeholder
        "harassment": ["harassment word 1"],  # Placeholder
    }
    
    @classmethod
    def analyze_text(cls, text: str) -> Dict[str, Any]:
        """Analyze text for violations"""
        
        violations = []
        risk_score = 0.0
        
        text_lower = text.lower()
        
        # Check for banned keywords
        for violation_type, keywords in cls.BANNED_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text_lower:
                    violations.append(violation_type)
                    risk_score += 0.3
        
        # Check for excessive links
        link_count = len(re.findall(r"https?://", text))
        if link_count > 5:
            violations.append("excessive_links")
            risk_score += 0.2
        
        # Check for caps lock abuse
        caps_ratio = sum(1 for c in text if c.isupper()) / max(1, len(text))
        if caps_ratio > 0.3:
            violations.append("caps_lock_abuse")
            risk_score += 0.1
        
        return {
            "violations": violations,
            "risk_score": min(1.0, risk_score),
            "recommended_action": cls._recommend_action(violations, risk_score)
        }
    
    @classmethod
    def _recommend_action(cls, violations: List[str], risk_score: float) -> Optional[str]:
        """Recommend moderation action"""
        
        if risk_score >= 0.8:
            return "reject"
        elif risk_score >= 0.5:
            return "review"
        elif risk_score >= 0.2:
            return "flag_for_review"
        else:
            return None
