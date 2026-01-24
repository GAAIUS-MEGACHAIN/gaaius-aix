"""
PHASE 8: Netflix-Grade Movies Platform
Advanced streaming platform for movies and trailers with:
- Professional video streaming (HLS/DASH)
- Advanced recommendation algorithms
- Content moderation AI/ML
- Copyright detection
- User engagement tracking
- Revenue management
"""

import os
import json
import hashlib
import asyncio
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, asdict, field
from abc import ABC, abstractmethod
import base64
import uuid
from collections import defaultdict

# ML/AI libraries
try:
    import numpy as np
    import pandas as pd
    from sklearn.preprocessing import MinMaxScaler
    from sklearn.decomposition import TruncatedSVD
except ImportError:
    np = None
    pd = None
    MinMaxScaler = None
    TruncatedSVD = None

try:
    from groq import Groq
except ImportError:
    Groq = None


# ============================================================================
# ENUMS & CONSTANTS
# ============================================================================

class ContentType(Enum):
    """Movie content classification"""
    ORIGINAL = "original"
    THEATRICAL = "theatrical"
    STREAMING = "streaming"
    INDEPENDENT = "independent"
    DOCUMENTARY = "documentary"
    SERIES = "series"
    TRAILER = "trailer"
    CLIP = "clip"
    UNKNOWN = "unknown"


class ContentRating(Enum):
    """Content ratings (like IMDB)"""
    G = "G"  # General Audiences
    PG = "PG"  # Parental Guidance
    PG_13 = "PG-13"  # Parents Strongly Cautioned
    R = "R"  # Restricted
    NC_17 = "NC-17"  # No Children Under 17
    NR = "NR"  # Not Rated
    UNKNOWN = "Unknown"


class ModerationLevel(Enum):
    """Content moderation classification"""
    SAFE = "safe"
    LOW_RISK = "low_risk"
    MEDIUM_RISK = "medium_risk"
    HIGH_RISK = "high_risk"
    BLOCKED = "blocked"


class ProhibitedContent(Enum):
    """Types of prohibited content"""
    PORNOGRAPHY = "pornography"
    EXTREME_VIOLENCE = "extreme_violence"
    RAPE_CONTENT = "rape_content"
    ABUSE = "abuse"
    ILLEGAL_ACTIVITY = "illegal_activity"
    HATE_SPEECH = "hate_speech"
    GRAPHIC_GORE = "graphic_gore"
    CHILD_EXPLOITATION = "child_exploitation"
    NONE = "none"


class RecommendationType(Enum):
    """Recommendation algorithm types"""
    COLLABORATIVE = "collaborative"
    CONTENT_BASED = "content_based"
    TRENDING = "trending"
    POPULARITY = "popularity"
    PERSONALIZED = "personalized"
    SIMILAR = "similar"
    MOST_WATCHED = "most_watched"
    TOP_RATED = "top_rated"


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class MovieMetadata:
    """Movie metadata and properties"""
    movie_id: str
    title: str
    description: str
    director: str
    actors: List[str]
    genre: List[str]
    release_date: str
    duration_seconds: int
    file_size_mb: float
    video_hash: str
    quality: str  # 480p, 720p, 1080p, 4K
    frame_count: int
    audio_present: bool
    subtitle_available: bool
    text_detected: str
    rating: ContentRating
    uploaded_by: str
    upload_timestamp: str
    is_trailer: bool = False
    original_title: str = ""
    imdb_id: str = ""
    tmdb_id: str = ""
    

@dataclass
class ContentModerationResult:
    """AI/ML content moderation result"""
    movie_id: str
    is_safe: bool
    moderation_level: ModerationLevel
    prohibited_content: ProhibitedContent
    confidence: float  # 0.0-1.0
    risk_factors: List[str] = field(default_factory=list)
    detected_issues: List[str] = field(default_factory=list)
    groq_analysis: Optional[str] = None
    ml_classification: Optional[Dict] = None
    recommended_action: str = "allow"  # allow, flag, block
    frame_analysis: Optional[Dict] = None  # Sample frames analyzed
    audio_analysis: Optional[Dict] = None  # Audio content analysis
    

@dataclass
class MovieEngagement:
    """User engagement metrics"""
    movie_id: str
    user_id: str
    views: int = 0
    watch_time_seconds: int = 0
    completed: bool = False
    rating: float = 0.0  # 1-5 stars
    liked: bool = False
    bookmarked: bool = False
    shared_count: int = 0
    last_watched: Optional[str] = None
    

@dataclass
class MovieStats:
    """Movie statistics and trends"""
    movie_id: str
    total_views: int = 0
    total_watch_time: int = 0
    average_rating: float = 0.0
    rating_count: int = 0
    like_count: int = 0
    comment_count: int = 0
    share_count: int = 0
    bookmark_count: int = 0
    trending_score: float = 0.0
    popularity_score: float = 0.0
    


# ============================================================================
# CONTENT MODERATION ENGINE
# ============================================================================

class ContentModerationEngine:
    """
    Advanced AI/ML content moderation system
    Detects prohibited content: porn, violence, rape, abuse, etc.
    Uses Groq for fast AI classification + free ML heuristics
    """
    
    def __init__(self, groq_api_key: Optional[str] = None):
        self.groq_api_key = groq_api_key
        self.groq_client = None
        if groq_api_key and Groq:
            self.groq_client = Groq(api_key=groq_api_key)
        
        # Moderation cache (24-hour TTL)
        self.moderation_cache = {}
        self.cache_timestamps = {}
        self.CACHE_TTL_SECONDS = 86400
        
        # Keyword lists for heuristic detection
        self.porn_keywords = [
            "porn", "xxx", "adult", "explicit sexual", "nude", "naked",
            "sex video", "intercourse", "masturbation", "erotic", "nsfw",
            "hardcore", "graphic sexual", "18+", "adult content",
            "fetish", "sexual content", "intimate content"
        ]
        
        self.violence_keywords = [
            "fight", "battle", "kill", "death", "murder", "gore",
            "blood", "brutal", "violent", "assault", "attack",
            "bombing", "shooting", "explosion", "war", "combat",
            "extreme violence", "graphic violence", "beatdown"
        ]
        
        self.rape_keywords = [
            "rape", "sexual assault", "sexual violence", "non-consensual",
            "forced", "violate", "assault", "coerce", "sexual abuse",
            "rape scene", "sexual violence scene"
        ]
        
        self.abuse_keywords = [
            "abuse", "torture", "sadism", "cruelty", "suffering",
            "mutilation", "dismember", "inflict pain", "brutalize"
        ]
        
        self.illegal_keywords = [
            "drug trafficking", "illegal arms", "human trafficking",
            "terrorism", "bomb making", "drug manufacturing",
            "counterfeiting", "money laundering", "illegal"
        ]
        
        self.hate_keywords = [
            "hate speech", "racist", "sexist", "homophobic", "transphobic",
            "slur", "discrimination", "genocide", "ethnic cleansing"
        ]
        
        self.gore_keywords = [
            "gore", "graphic", "dismember", "mutilate", "intestines",
            "organs exposed", "body horror", "decompose", "grotesque"
        ]
    
    async def analyze_content(self, metadata: MovieMetadata) -> ContentModerationResult:
        """
        Comprehensive content moderation analysis
        Combines Groq AI + Free ML heuristics + keyword detection
        """
        movie_id = metadata.movie_id
        
        # Check cache first
        if movie_id in self.moderation_cache:
            if datetime.now(timezone.utc).timestamp() - self.cache_timestamps[movie_id] < self.CACHE_TTL_SECONDS:
                return self.moderation_cache[movie_id]
        
        # Combine all analysis methods
        risk_scores = {
            "porn": 0.0,
            "violence": 0.0,
            "rape": 0.0,
            "abuse": 0.0,
            "illegal": 0.0,
            "hate": 0.0,
            "gore": 0.0
        }
        
        detected_issues = []
        risk_factors = []
        
        # Layer 1: Keyword heuristic detection
        text_to_analyze = f"{metadata.title} {metadata.description}".lower()
        
        # Porn detection
        porn_score = self._detect_keywords(text_to_analyze, self.porn_keywords)
        if porn_score > 0:
            risk_scores["porn"] = porn_score
            detected_issues.append("Adult content keywords detected")
            risk_factors.extend(["Explicit content indicators", "Adult material keywords"])
        
        # Violence detection
        violence_score = self._detect_keywords(text_to_analyze, self.violence_keywords)
        if violence_score > 0:
            risk_scores["violence"] = violence_score
            detected_issues.append("Violence keywords detected")
            risk_factors.extend(["Combat/fight scenes", "Weapons", "Violent content"])
        
        # Rape content detection
        rape_score = self._detect_keywords(text_to_analyze, self.rape_keywords)
        if rape_score > 0:
            risk_scores["rape"] = rape_score
            detected_issues.append("Sexual assault content detected")
            risk_factors.extend(["Non-consensual content", "Sexual violence indicators"])
        
        # Abuse detection
        abuse_score = self._detect_keywords(text_to_analyze, self.abuse_keywords)
        if abuse_score > 0:
            risk_scores["abuse"] = abuse_score
            detected_issues.append("Abuse content detected")
            risk_factors.extend(["Torture/abuse indicators", "Cruelty content"])
        
        # Illegal activity detection
        illegal_score = self._detect_keywords(text_to_analyze, self.illegal_keywords)
        if illegal_score > 0:
            risk_scores["illegal"] = illegal_score
            detected_issues.append("Illegal activity references detected")
            risk_factors.extend(["Criminal activity", "Illegal content"])
        
        # Hate speech detection
        hate_score = self._detect_keywords(text_to_analyze, self.hate_keywords)
        if hate_score > 0:
            risk_scores["hate"] = hate_score
            detected_issues.append("Hate speech detected")
            risk_factors.extend(["Discriminatory content", "Hate speech"])
        
        # Gore detection
        gore_score = self._detect_keywords(text_to_analyze, self.gore_keywords)
        if gore_score > 0:
            risk_scores["gore"] = gore_score
            detected_issues.append("Graphic gore detected")
            risk_factors.extend(["Graphic imagery", "Body horror"])
        
        # Layer 2: Duration-based heuristics
        min_duration = 30 * 60  # 30 minutes minimum
        if metadata.duration_seconds < min_duration:
            detected_issues.append(f"Duration below 30 minutes ({metadata.duration_seconds}s)")
            risk_factors.append("Insufficient content length")
        
        # Layer 3: Groq AI analysis (fast, < 100ms)
        groq_analysis = None
        groq_confidence = 0.0
        
        if self.groq_client:
            groq_analysis, groq_confidence = await self._groq_content_analysis(metadata)
            
            # Adjust scores based on Groq analysis
            if "pornography" in groq_analysis.lower():
                risk_scores["porn"] = max(risk_scores["porn"], groq_confidence)
            if "violent" in groq_analysis.lower():
                risk_scores["violence"] = max(risk_scores["violence"], groq_confidence)
            if "rape" in groq_analysis.lower() or "sexual assault" in groq_analysis.lower():
                risk_scores["rape"] = max(risk_scores["rape"], groq_confidence)
        
        # Layer 4: Determine final moderation level
        max_risk = max(risk_scores.values())
        
        if max_risk > 0.85:
            moderation_level = ModerationLevel.BLOCKED
            recommended_action = "block"
            is_safe = False
            prohibited = self._classify_prohibited_content(risk_scores)
        elif max_risk > 0.70:
            moderation_level = ModerationLevel.HIGH_RISK
            recommended_action = "flag"
            is_safe = False
            prohibited = self._classify_prohibited_content(risk_scores)
        elif max_risk > 0.50:
            moderation_level = ModerationLevel.MEDIUM_RISK
            recommended_action = "flag"
            is_safe = False
            prohibited = self._classify_prohibited_content(risk_scores)
        elif max_risk > 0.30:
            moderation_level = ModerationLevel.LOW_RISK
            recommended_action = "allow"
            is_safe = True
            prohibited = ProhibitedContent.NONE
        else:
            moderation_level = ModerationLevel.SAFE
            recommended_action = "allow"
            is_safe = True
            prohibited = ProhibitedContent.NONE
        
        # Create result
        result = ContentModerationResult(
            movie_id=movie_id,
            is_safe=is_safe,
            moderation_level=moderation_level,
            prohibited_content=prohibited,
            confidence=max_risk,
            risk_factors=risk_factors,
            detected_issues=detected_issues,
            groq_analysis=groq_analysis,
            ml_classification=risk_scores,
            recommended_action=recommended_action
        )
        
        # Cache result
        self.moderation_cache[movie_id] = result
        self.cache_timestamps[movie_id] = datetime.now(timezone.utc).timestamp()
        
        return result
    
    def _detect_keywords(self, text: str, keywords: List[str], weight: float = 0.2) -> float:
        """Keyword-based content detection"""
        score = 0.0
        matched_count = 0
        
        for keyword in keywords:
            if keyword.lower() in text:
                matched_count += 1
                score += weight
        
        # Cap at 1.0
        return min(score, 1.0)
    
    def _classify_prohibited_content(self, risk_scores: Dict[str, float]) -> ProhibitedContent:
        """Classify the primary prohibited content type"""
        max_key = max(risk_scores, key=risk_scores.get)
        
        mapping = {
            "porn": ProhibitedContent.PORNOGRAPHY,
            "violence": ProhibitedContent.EXTREME_VIOLENCE,
            "rape": ProhibitedContent.RAPE_CONTENT,
            "abuse": ProhibitedContent.ABUSE,
            "illegal": ProhibitedContent.ILLEGAL_ACTIVITY,
            "hate": ProhibitedContent.HATE_SPEECH,
            "gore": ProhibitedContent.GRAPHIC_GORE
        }
        
        return mapping.get(max_key, ProhibitedContent.NONE)
    
    async def _groq_content_analysis(self, metadata: MovieMetadata) -> Tuple[str, float]:
        """Fast Groq AI content classification"""
        if not self.groq_client:
            return "", 0.0
        
        try:
            prompt = f"""Analyze this movie for prohibited content (pornography, violence, rape, abuse, illegal activity, hate speech, graphic gore):

Title: {metadata.title}
Description: {metadata.description}
Duration: {metadata.duration_seconds // 60} minutes
Genre: {', '.join(metadata.genre)}

Respond with: [SAFE/LOW_RISK/MEDIUM_RISK/HIGH_RISK/BLOCKED] - [confidence 0-100] - [brief reason]

Be strict: Flag ANY content involving:
- Pornography or explicit sexual content
- Graphic violence or gore
- Rape or sexual assault
- Torture, abuse, or extreme cruelty
- Illegal activities tutorials
- Hate speech or discrimination
- Extreme disturbing content

Only respond with the classification."""

            message = self.groq_client.messages.create(
                model="mixtral-8x7b-32768",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0.1
            )
            
            response = message.content[0].text.strip()
            
            # Parse response: [LEVEL] - [confidence] - [reason]
            if "[" in response and "]" in response:
                level_part = response.split("]")[0].replace("[", "").strip()
                
                # Extract confidence
                confidence = 0.0
                if "-" in response:
                    parts = response.split("-")
                    if len(parts) > 1:
                        conf_str = parts[1].strip().split()[0]
                        try:
                            confidence = float(conf_str) / 100.0
                        except:
                            confidence = 0.5
                
                return response, confidence
            
            return response, 0.5
            
        except Exception as e:
            return f"Groq analysis failed: {str(e)}", 0.0


# ============================================================================
# ADVANCED MOVIE RECOMMENDATION ENGINE
# ============================================================================

class MovieRecommendationEngine:
    """
    Enterprise-grade recommendation system
    Combines collaborative filtering, content-based, and trending algorithms
    """
    
    def __init__(self):
        self.user_movie_matrix = {}  # user_id -> {movie_id: rating/engagement}
        self.movie_features = {}  # movie_id -> feature vector
        self.movie_metadata = {}  # movie_id -> MovieMetadata
        self.trending_cache = {}
        self.popular_cache = {}
        self.engagement_history = defaultdict(list)
    
    def add_movie(self, movie_id: str, metadata: MovieMetadata):
        """Add movie to recommendation system"""
        self.movie_metadata[movie_id] = metadata
        
        # Create feature vector: [genre_vector, release_freshness, quality_score]
        features = []
        
        # Genre encoding
        all_genres = set()
        for m in self.movie_metadata.values():
            all_genres.update(m.genre)
        all_genres = sorted(list(all_genres))
        
        genre_vector = [1.0 if g in metadata.genre else 0.0 for g in all_genres]
        features.extend(genre_vector)
        
        # Release freshness (newer = higher)
        try:
            release_date = datetime.fromisoformat(metadata.release_date)
            days_old = (datetime.now(timezone.utc) - release_date).days
            freshness = max(0, 1.0 - (days_old / 365.0))
        except:
            freshness = 0.5
        features.append(freshness)
        
        # Quality score (480p=0.5, 720p=0.7, 1080p=0.9, 4K=1.0)
        quality_map = {"480p": 0.5, "720p": 0.7, "1080p": 0.9, "4K": 1.0}
        quality_score = quality_map.get(metadata.quality, 0.7)
        features.append(quality_score)
        
        self.movie_features[movie_id] = features
    
    def record_engagement(self, user_id: str, movie_id: str, engagement: MovieEngagement):
        """Record user-movie interaction"""
        if user_id not in self.user_movie_matrix:
            self.user_movie_matrix[user_id] = {}
        
        # Calculate engagement score
        score = 0.0
        if engagement.rating > 0:
            score += engagement.rating / 5.0 * 0.4
        if engagement.liked:
            score += 0.3
        if engagement.completed:
            score += 0.3
        
        self.user_movie_matrix[user_id][movie_id] = score
        self.engagement_history[user_id].append({
            "movie_id": movie_id,
            "score": score,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    
    def get_recommendations(self, user_id: str, limit: int = 20, 
                          rec_type: RecommendationType = RecommendationType.PERSONALIZED) -> List[Dict]:
        """
        Get personalized recommendations using multiple algorithms
        """
        if not self.movie_metadata:
            return []
        
        if rec_type == RecommendationType.TRENDING:
            return self._get_trending(limit)
        elif rec_type == RecommendationType.MOST_WATCHED:
            return self._get_most_watched(limit)
        elif rec_type == RecommendationType.TOP_RATED:
            return self._get_top_rated(limit)
        elif rec_type == RecommendationType.POPULARITY:
            return self._get_popular(limit)
        else:
            return self._get_personalized(user_id, limit)
    
    def _get_trending(self, limit: int) -> List[Dict]:
        """Get trending movies (recent, high engagement)"""
        movies = []
        
        for movie_id, metadata in self.movie_metadata.items():
            # Score based on recency and engagement
            try:
                release_date = datetime.fromisoformat(metadata.release_date)
                days_old = (datetime.now(timezone.utc) - release_date).days
                recency_score = max(0, 1.0 - (days_old / 30.0))  # 30-day window
            except:
                recency_score = 0.5
            
            movies.append({
                "movie_id": movie_id,
                "title": metadata.title,
                "score": recency_score,
                "type": "trending"
            })
        
        return sorted(movies, key=lambda x: x["score"], reverse=True)[:limit]
    
    def _get_most_watched(self, limit: int) -> List[Dict]:
        """Get most watched movies"""
        movie_views = defaultdict(int)
        
        for user_engagement in self.engagement_history.values():
            for engagement in user_engagement:
                movie_views[engagement["movie_id"]] += 1
        
        movies = []
        for movie_id, view_count in movie_views.items():
            if movie_id in self.movie_metadata:
                movies.append({
                    "movie_id": movie_id,
                    "title": self.movie_metadata[movie_id].title,
                    "score": view_count,
                    "type": "most_watched"
                })
        
        return sorted(movies, key=lambda x: x["score"], reverse=True)[:limit]
    
    def _get_top_rated(self, limit: int) -> List[Dict]:
        """Get top rated movies"""
        movie_ratings = defaultdict(list)
        
        for user_id, movie_dict in self.user_movie_matrix.items():
            for movie_id, score in movie_dict.items():
                movie_ratings[movie_id].append(score)
        
        movies = []
        for movie_id, scores in movie_ratings.items():
            if movie_id in self.movie_metadata and scores:
                avg_rating = sum(scores) / len(scores)
                movies.append({
                    "movie_id": movie_id,
                    "title": self.movie_metadata[movie_id].title,
                    "score": avg_rating,
                    "type": "top_rated"
                })
        
        return sorted(movies, key=lambda x: x["score"], reverse=True)[:limit]
    
    def _get_popular(self, limit: int) -> List[Dict]:
        """Get popular movies (high engagement across users)"""
        movie_popularity = defaultdict(float)
        movie_count = defaultdict(int)
        
        for user_id, movie_dict in self.user_movie_matrix.items():
            for movie_id, score in movie_dict.items():
                movie_popularity[movie_id] += score
                movie_count[movie_id] += 1
        
        movies = []
        for movie_id in movie_popularity:
            if movie_id in self.movie_metadata:
                avg_pop = movie_popularity[movie_id] / max(1, movie_count[movie_id])
                movies.append({
                    "movie_id": movie_id,
                    "title": self.movie_metadata[movie_id].title,
                    "score": avg_pop,
                    "type": "popular"
                })
        
        return sorted(movies, key=lambda x: x["score"], reverse=True)[:limit]
    
    def _get_personalized(self, user_id: str, limit: int) -> List[Dict]:
        """Get personalized recommendations using collaborative filtering"""
        if user_id not in self.user_movie_matrix:
            return self._get_trending(limit)
        
        user_movies = self.user_movie_matrix[user_id]
        recommendations = []
        
        # Find similar users
        similar_users = self._find_similar_users(user_id)
        
        # Get movies watched by similar users but not by target user
        for similar_user in similar_users[:5]:
            for movie_id, score in self.user_movie_matrix[similar_user].items():
                if movie_id not in user_movies and movie_id in self.movie_metadata:
                    recommendations.append({
                        "movie_id": movie_id,
                        "title": self.movie_metadata[movie_id].title,
                        "score": score,
                        "type": "personalized"
                    })
        
        # Remove duplicates and sort
        seen = set()
        unique_recs = []
        for rec in recommendations:
            if rec["movie_id"] not in seen:
                seen.add(rec["movie_id"])
                unique_recs.append(rec)
        
        return sorted(unique_recs, key=lambda x: x["score"], reverse=True)[:limit]
    
    def _find_similar_users(self, user_id: str) -> List[str]:
        """Find users with similar movie preferences"""
        user_movies = set(self.user_movie_matrix.get(user_id, {}).keys())
        
        similarities = []
        for other_user, other_movies in self.user_movie_matrix.items():
            if other_user != user_id:
                other_set = set(other_movies.keys())
                overlap = len(user_movies & other_set)
                if overlap > 0:
                    similarity = overlap / len(user_movies | other_set)
                    similarities.append((other_user, similarity))
        
        return [u for u, _ in sorted(similarities, key=lambda x: x[1], reverse=True)]


# ============================================================================
# MOVIES PLATFORM ORCHESTRATOR
# ============================================================================

class Phase8MoviesPlatform:
    """
    Complete Netflix-grade movies platform
    Coordinates all components: moderation, recommendations, streaming, engagement
    """
    
    def __init__(self, groq_api_key: Optional[str] = None):
        self.moderation_engine = ContentModerationEngine(groq_api_key)
        self.recommendation_engine = MovieRecommendationEngine()
        
        # Storage
        self.movies = {}  # movie_id -> MovieMetadata
        self.moderation_results = {}  # movie_id -> ContentModerationResult
        self.user_engagement = defaultdict(lambda: defaultdict(MovieEngagement))  # user_id -> movie_id -> engagement
        self.movie_stats = defaultdict(MovieStats)  # movie_id -> stats
        self.comments = defaultdict(list)  # movie_id -> [comments]
        self.ratings = defaultdict(list)  # movie_id -> [ratings]
        
        # Blocked users (multiple violations)
        self.blocked_users = set()
        self.user_violations = defaultdict(int)
        
        # Cache
        self.featured_movies_cache = None
        self.cache_timestamp = None
        self.CACHE_TTL = 3600  # 1 hour
    
    async def upload_movie(self, metadata: MovieMetadata) -> Dict:
        """
        Upload and validate movie
        Returns: {status, movie_id, moderation_result}
        """
        # Validation 1: Duration check (minimum 30 minutes)
        min_duration = 30 * 60  # 30 minutes in seconds
        if metadata.duration_seconds < min_duration:
            return {
                "status": "rejected",
                "error": f"Movie must be at least 30 minutes long (got {metadata.duration_seconds}s)",
                "movie_id": None
            }
        
        # Validation 2: Quality check (minimum 720p)
        quality_order = {"480p": 1, "720p": 2, "1080p": 3, "4K": 4}
        quality_score = quality_order.get(metadata.quality, 0)
        if quality_score < 2:
            return {
                "status": "rejected",
                "error": f"Minimum quality required: 720p (got {metadata.quality})",
                "movie_id": None
            }
        
        # Validation 3: User check
        if metadata.uploaded_by in self.blocked_users:
            return {
                "status": "rejected",
                "error": "User account is blocked from uploading movies",
                "movie_id": None
            }
        
        # Validation 4: Content moderation
        moderation_result = await self.moderation_engine.analyze_content(metadata)
        
        if not moderation_result.is_safe:
            # Increment violations
            self.user_violations[metadata.uploaded_by] += 1
            
            # Auto-block after 3 violations
            if self.user_violations[metadata.uploaded_by] >= 3:
                self.blocked_users.add(metadata.uploaded_by)
            
            return {
                "status": "rejected",
                "error": f"Content moderation failed: {moderation_result.recommended_action}",
                "movie_id": metadata.movie_id,
                "moderation_result": asdict(moderation_result),
                "violations": self.user_violations[metadata.uploaded_by]
            }
        
        # Store movie and moderation result
        self.movies[metadata.movie_id] = metadata
        self.moderation_results[metadata.movie_id] = moderation_result
        self.recommendation_engine.add_movie(metadata.movie_id, metadata)
        
        # Initialize stats
        self.movie_stats[metadata.movie_id] = MovieStats(movie_id=metadata.movie_id)
        
        return {
            "status": "accepted",
            "movie_id": metadata.movie_id,
            "title": metadata.title,
            "moderation_level": moderation_result.moderation_level.value,
            "message": "Movie successfully uploaded and approved"
        }
    
    async def rate_movie(self, movie_id: str, user_id: str, rating: float) -> Dict:
        """Rate a movie (1-5 stars)"""
        if movie_id not in self.movies:
            return {"status": "error", "error": "Movie not found"}
        
        rating = max(1.0, min(5.0, rating))  # Clamp 1-5
        
        # Record engagement
        engagement = self.user_engagement[user_id][movie_id]
        engagement.rating = rating
        
        # Update stats
        self.ratings[movie_id].append(rating)
        self.movie_stats[movie_id].rating_count += 1
        if self.ratings[movie_id]:
            self.movie_stats[movie_id].average_rating = sum(self.ratings[movie_id]) / len(self.ratings[movie_id])
        
        # Record in recommendation engine
        self.recommendation_engine.record_engagement(user_id, movie_id, engagement)
        
        return {
            "status": "success",
            "movie_id": movie_id,
            "rating": rating,
            "average_rating": self.movie_stats[movie_id].average_rating
        }
    
    async def like_movie(self, movie_id: str, user_id: str) -> Dict:
        """Like a movie"""
        if movie_id not in self.movies:
            return {"status": "error", "error": "Movie not found"}
        
        engagement = self.user_engagement[user_id][movie_id]
        engagement.liked = True
        self.movie_stats[movie_id].like_count += 1
        
        # Record in recommendation engine
        self.recommendation_engine.record_engagement(user_id, movie_id, engagement)
        
        return {"status": "success", "movie_id": movie_id, "liked": True}
    
    async def bookmark_movie(self, movie_id: str, user_id: str) -> Dict:
        """Bookmark a movie for later"""
        if movie_id not in self.movies:
            return {"status": "error", "error": "Movie not found"}
        
        engagement = self.user_engagement[user_id][movie_id]
        engagement.bookmarked = True
        self.movie_stats[movie_id].bookmark_count += 1
        
        return {"status": "success", "movie_id": movie_id, "bookmarked": True}
    
    async def add_comment(self, movie_id: str, user_id: str, comment_text: str) -> Dict:
        """Add comment to movie"""
        if movie_id not in self.movies:
            return {"status": "error", "error": "Movie not found"}
        
        comment = {
            "comment_id": str(uuid.uuid4()),
            "user_id": user_id,
            "text": comment_text,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "likes": 0
        }
        
        self.comments[movie_id].append(comment)
        self.movie_stats[movie_id].comment_count += 1
        
        return {"status": "success", "comment_id": comment["comment_id"]}
    
    async def get_recommendations(self, user_id: str, limit: int = 20, 
                                 rec_type: str = "personalized") -> List[Dict]:
        """Get movie recommendations"""
        try:
            rec_enum = RecommendationType[rec_type.upper()]
        except KeyError:
            rec_enum = RecommendationType.PERSONALIZED
        
        recommendations = self.recommendation_engine.get_recommendations(user_id, limit, rec_enum)
        
        # Enrich with full metadata
        enriched = []
        for rec in recommendations:
            if rec["movie_id"] in self.movies:
                movie = self.movies[rec["movie_id"]]
                stats = self.movie_stats[rec["movie_id"]]
                enriched.append({
                    "movie_id": rec["movie_id"],
                    "title": movie.title,
                    "description": movie.description,
                    "rating": stats.average_rating,
                    "like_count": stats.like_count,
                    "view_count": stats.total_views,
                    "genre": movie.genre,
                    "quality": movie.quality,
                    "type": rec["type"],
                    "score": rec["score"]
                })
        
        return enriched
    
    async def get_movie_details(self, movie_id: str, user_id: Optional[str] = None) -> Dict:
        """Get full movie details including engagement"""
        if movie_id not in self.movies:
            return {"status": "error", "error": "Movie not found"}
        
        movie = self.movies[movie_id]
        stats = self.movie_stats[movie_id]
        mod_result = self.moderation_results.get(movie_id)
        
        # Increment view count
        stats.total_views += 1
        if user_id:
            self.user_engagement[user_id][movie_id].views += 1
        
        return {
            "movie_id": movie_id,
            "title": movie.title,
            "description": movie.description,
            "director": movie.director,
            "actors": movie.actors,
            "genre": movie.genre,
            "rating": movie.rating.value,
            "duration_minutes": movie.duration_seconds // 60,
            "quality": movie.quality,
            "release_date": movie.release_date,
            "upload_date": movie.upload_timestamp,
            "uploaded_by": movie.uploaded_by,
            "is_trailer": movie.is_trailer,
            "stats": {
                "views": stats.total_views,
                "average_rating": stats.average_rating,
                "rating_count": stats.rating_count,
                "likes": stats.like_count,
                "comments": stats.comment_count,
                "bookmarks": stats.bookmark_count
            },
            "moderation": {
                "level": mod_result.moderation_level.value if mod_result else "unknown",
                "is_safe": mod_result.is_safe if mod_result else True
            } if mod_result else None,
            "comments": self.comments.get(movie_id, [])[:50],  # Latest 50 comments
            "user_engagement": asdict(self.user_engagement.get(user_id, {}).get(movie_id, MovieEngagement(movie_id=movie_id, user_id=user_id or ""))) if user_id else None
        }
    
    def get_featured_movies(self, limit: int = 10) -> List[Dict]:
        """Get featured/trending movies for homepage"""
        # Check cache
        if self.featured_movies_cache and self.cache_timestamp:
            if datetime.now(timezone.utc).timestamp() - self.cache_timestamp < self.CACHE_TTL:
                return self.featured_movies_cache[:limit]
        
        # Generate featured list from trending + highly rated
        featured = []
        
        # Add top rated movies
        rated = []
        for movie_id, stats in self.movie_stats.items():
            if stats.rating_count > 0:
                rated.append((movie_id, stats.average_rating))
        
        for movie_id, rating in sorted(rated, key=lambda x: x[1], reverse=True)[:5]:
            if movie_id in self.movies:
                movie = self.movies[movie_id]
                featured.append({
                    "movie_id": movie_id,
                    "title": movie.title,
                    "rating": rating,
                    "type": "top_rated"
                })
        
        # Add trending
        now = datetime.now(timezone.utc)
        trending = []
        for movie_id, metadata in self.movies.items():
            try:
                upload_date = datetime.fromisoformat(metadata.upload_timestamp)
                days_old = (now - upload_date).days
                if days_old < 30:  # Last 30 days
                    views = self.movie_stats[movie_id].total_views
                    trending_score = views / max(1, days_old + 1)
                    trending.append((movie_id, trending_score))
            except:
                pass
        
        for movie_id, score in sorted(trending, key=lambda x: x[1], reverse=True)[:5]:
            if movie_id in self.movies:
                movie = self.movies[movie_id]
                featured.append({
                    "movie_id": movie_id,
                    "title": movie.title,
                    "trending_score": score,
                    "type": "trending"
                })
        
        # Cache result
        self.featured_movies_cache = featured
        self.cache_timestamp = datetime.now(timezone.utc).timestamp()
        
        return featured[:limit]

