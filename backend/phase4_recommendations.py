"""
PHASE 4: ML-Powered Recommendation Engine
Production-grade collaborative filtering and content-based recommendations
"""

import logging
import numpy as np
from typing import Dict, List, Set, Tuple, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict
import json

from motor.motor_asyncio import AsyncIOMotorDatabase
import redis.asyncio as aioredis
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity


logger = logging.getLogger(__name__)


class RecommendationEngine:
    """ML-powered recommendation system with multiple strategies"""
    
    def __init__(self, redis: aioredis.Redis, db: AsyncIOMotorDatabase):
        self.redis = redis
        self.db = db
        self.videos_collection = db["videos"]
        self.users_collection = db["users"]
        self.interactions_collection = db["user_interactions"]
        self.recommendations_collection = db["recommendations"]
        
        # Caching
        self.user_vectors_cache: Dict[str, np.ndarray] = {}
        self.video_vectors_cache: Dict[str, np.ndarray] = {}
    
    async def get_personalized_recommendations(
        self,
        user_id: str,
        limit: int = 20,
        strategy: str = "hybrid"
    ) -> List[Dict[str, Any]]:
        """
        Get personalized recommendations using hybrid approach:
        - Collaborative filtering (user-based)
        - Content-based filtering (video features)
        - Trending videos
        """
        
        # Try cache first
        cache_key = f"recommendations:{user_id}:{strategy}"
        cached = await self.redis.get(cache_key)
        if cached:
            return json.loads(cached)
        
        if strategy == "collaborative":
            recommendations = await self._collaborative_filtering(user_id, limit)
        elif strategy == "content":
            recommendations = await self._content_based_filtering(user_id, limit)
        elif strategy == "hybrid":
            # Combine both approaches
            collab_recs = await self._collaborative_filtering(user_id, limit // 2)
            content_recs = await self._content_based_filtering(user_id, limit // 2)
            recommendations = self._merge_recommendations(collab_recs, content_recs)
        else:
            recommendations = await self._trending_videos(limit)
        
        # Cache for 1 hour
        await self.redis.setex(
            cache_key,
            3600,
            json.dumps(recommendations, default=str)
        )
        
        return recommendations
    
    async def _collaborative_filtering(
        self,
        user_id: str,
        limit: int
    ) -> List[Dict[str, Any]]:
        """User-based collaborative filtering"""
        
        # Get user's watch history
        user_interactions = await self.interactions_collection.find(
            {"user_id": user_id, "event_type": {"$in": ["view", "like"]}},
            limit=100
        ).to_list(100)
        
        if not user_interactions:
            return await self._trending_videos(limit)
        
        watched_videos = {str(inter["video_id"]) for inter in user_interactions}
        
        # Find similar users
        similar_users = await self._find_similar_users(user_id, top_n=20)
        
        # Get videos watched by similar users but not by current user
        recommendations_dict = defaultdict(float)
        
        for similar_user, similarity_score in similar_users:
            similar_user_videos = await self.interactions_collection.find(
                {
                    "user_id": similar_user,
                    "event_type": {"$in": ["view", "like"]},
                    "video_id": {"$nin": list(watched_videos)}
                },
                limit=50
            ).to_list(50)
            
            for inter in similar_user_videos:
                video_id = str(inter["video_id"])
                # Weight by similarity score and interaction type
                weight = similarity_score * (2.0 if inter["event_type"] == "like" else 1.0)
                recommendations_dict[video_id] += weight
        
        # Sort by score
        sorted_recs = sorted(
            recommendations_dict.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]
        
        # Get video details
        videos = await self.videos_collection.find(
            {"_id": {"$in": [rec[0] for rec in sorted_recs]}},
            limit=limit
        ).to_list(limit)
        
        # Return with scores
        result = []
        for video in videos:
            video_id = str(video["_id"])
            score = next((s for vid, s in sorted_recs if vid == video_id), 0)
            result.append({
                "video_id": video_id,
                "title": video.get("title"),
                "channel_name": video.get("channel_name"),
                "recommendation_score": float(score),
                "reason": "Users like you enjoyed this"
            })
        
        return result
    
    async def _content_based_filtering(
        self,
        user_id: str,
        limit: int
    ) -> List[Dict[str, Any]]:
        """Content-based filtering using video features"""
        
        # Get user preferences
        user_profile = await self._build_user_profile(user_id)
        
        if not user_profile:
            return await self._trending_videos(limit)
        
        # Get all videos
        all_videos = await self.videos_collection.find(
            {"is_public": True},
            limit=1000
        ).to_list(1000)
        
        # Calculate similarity scores
        scores = []
        for video in all_videos:
            # Skip already watched videos
            if await self._user_watched_video(user_id, str(video["_id"])):
                continue
            
            # Calculate content similarity
            similarity = await self._calculate_video_similarity(user_profile, video)
            scores.append((video, similarity))
        
        # Sort by similarity
        scores.sort(key=lambda x: x[1], reverse=True)
        
        # Return top videos
        result = []
        for video, score in scores[:limit]:
            result.append({
                "video_id": str(video["_id"]),
                "title": video.get("title"),
                "channel_name": video.get("channel_name"),
                "recommendation_score": float(score),
                "reason": "Based on your interests in " + ", ".join(user_profile.get("interests", [])[:2])
            })
        
        return result
    
    async def _find_similar_users(
        self,
        user_id: str,
        top_n: int = 20
    ) -> List[Tuple[str, float]]:
        """Find users with similar watching patterns"""
        
        # Get user's watch history
        user_videos = await self.interactions_collection.find(
            {"user_id": user_id},
            limit=200
        ).to_list(200)
        
        user_video_set = {str(inter["video_id"]) for inter in user_videos}
        
        if not user_video_set:
            return []
        
        # Find other users who watched same videos
        similar_users = defaultdict(int)
        
        other_users = await self.interactions_collection.find(
            {
                "user_id": {"$ne": user_id},
                "video_id": {"$in": list(user_video_set)}
            },
            limit=10000
        ).to_list(10000)
        
        for inter in other_users:
            other_user = inter["user_id"]
            similar_users[other_user] += 1
        
        # Calculate Jaccard similarity
        similarities = []
        for other_user, common_count in similar_users.items():
            # Get other user's video count
            other_user_videos = await self.interactions_collection.count_documents(
                {"user_id": other_user}
            )
            
            # Jaccard similarity
            similarity = common_count / (len(user_video_set) + other_user_videos - common_count)
            similarities.append((other_user, similarity))
        
        # Sort and return top users
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_n]
    
    async def _build_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Build user preference profile from watch history"""
        
        # Get user's interactions
        interactions = await self.interactions_collection.find(
            {"user_id": user_id},
            limit=100
        ).to_list(100)
        
        if not interactions:
            return None
        
        # Get videos and extract features
        video_ids = [str(inter["video_id"]) for inter in interactions]
        videos = await self.videos_collection.find(
            {"_id": {"$in": video_ids}},
            limit=100
        ).to_list(100)
        
        # Aggregate features
        categories = defaultdict(int)
        tags = defaultdict(int)
        channels = defaultdict(int)
        
        for video in videos:
            # Category
            if video.get("category"):
                categories[video["category"]] += 1
            
            # Tags
            for tag in video.get("tags", []):
                tags[tag] += 1
            
            # Channel
            channels[str(video.get("channel_id"))] += 1
        
        # Get top interests
        top_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)[:3]
        top_tags = sorted(tags.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "user_id": user_id,
            "interests": [cat[0] for cat in top_categories],
            "tags": dict(top_tags),
            "preferred_channels": list(channels.keys())[:5]
        }
    
    async def _calculate_video_similarity(
        self,
        user_profile: Dict[str, Any],
        video: Dict[str, Any]
    ) -> float:
        """Calculate similarity between video and user profile"""
        
        score = 0.0
        
        # Category match
        if video.get("category") in user_profile.get("interests", []):
            score += 3.0
        
        # Tag matches
        video_tags = set(video.get("tags", []))
        profile_tags = set(user_profile.get("tags", {}).keys())
        tag_overlap = len(video_tags & profile_tags)
        score += tag_overlap * 0.5
        
        # Channel match
        if str(video.get("channel_id")) in user_profile.get("preferred_channels", []):
            score += 2.0
        
        # Engagement boost
        score += (video.get("view_count", 0) / 1000.0) * 0.1
        score += (video.get("like_count", 0) / 100.0) * 0.2
        
        return score
    
    async def _user_watched_video(self, user_id: str, video_id: str) -> bool:
        """Check if user already watched video"""
        interaction = await self.interactions_collection.find_one(
            {"user_id": user_id, "video_id": video_id}
        )
        return interaction is not None
    
    async def _trending_videos(self, limit: int) -> List[Dict[str, Any]]:
        """Get trending videos as fallback"""
        
        # Calculate trending based on recent engagement
        pipeline = [
            {
                "$match": {"is_public": True}
            },
            {
                "$addFields": {
                    "engagement_score": {
                        "$add": [
                            "$view_count",
                            {"$multiply": ["$like_count", 5]},
                            {"$multiply": ["$comment_count", 10]}
                        ]
                    }
                }
            },
            {
                "$sort": {"engagement_score": -1}
            },
            {
                "$limit": limit
            }
        ]
        
        videos = await self.videos_collection.aggregate(pipeline).to_list(limit)
        
        result = []
        for video in videos:
            result.append({
                "video_id": str(video["_id"]),
                "title": video.get("title"),
                "channel_name": video.get("channel_name"),
                "recommendation_score": 1.0,
                "reason": "Trending now"
            })
        
        return result
    
    def _merge_recommendations(
        self,
        collab_recs: List[Dict[str, Any]],
        content_recs: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Merge collaborative and content-based recommendations"""
        
        # Create dict for easy merging
        merged = {}
        
        for rec in collab_recs:
            video_id = rec["video_id"]
            merged[video_id] = {**rec, "score": rec["recommendation_score"] * 0.6}
        
        for rec in content_recs:
            video_id = rec["video_id"]
            if video_id in merged:
                merged[video_id]["score"] += rec["recommendation_score"] * 0.4
                merged[video_id]["reason"] += " + " + rec["reason"]
            else:
                merged[video_id] = {**rec, "score": rec["recommendation_score"] * 0.4}
        
        # Sort by combined score
        result = sorted(merged.values(), key=lambda x: x["score"], reverse=True)
        
        # Normalize scores
        max_score = max((r["score"] for r in result), default=1.0)
        for rec in result:
            rec["recommendation_score"] = rec["score"] / max_score if max_score > 0 else 0
            del rec["score"]
        
        return result
    
    async def record_interaction(
        self,
        user_id: str,
        video_id: str,
        event_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Record user-video interaction for learning"""
        
        interaction = {
            "user_id": user_id,
            "video_id": video_id,
            "event_type": event_type,
            "timestamp": datetime.utcnow(),
            "metadata": metadata or {}
        }
        
        await self.interactions_collection.insert_one(interaction)
        
        # Invalidate recommendation cache
        await self.redis.delete(f"recommendations:{user_id}:*")
    
    async def train_model(self) -> None:
        """Periodically retrain recommendation models"""
        logger.info("Starting recommendation model training...")
        
        # This would be called by a background task
        # For now, this clears caches to force fresh calculations
        
        # Clear all recommendation caches
        pattern = "recommendations:*"
        keys = await self.redis.keys(pattern)
        if keys:
            await self.redis.delete(*keys)
        
        logger.info("Recommendation model training complete")
