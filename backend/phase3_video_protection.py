"""
Phase 3+: Advanced Video Content Protection
Prevent copyrighted videos, monetized content, and movies using Groq + free ML
Real-time content validation with multi-layer detection
"""

import hashlib
import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass, field
from enum import Enum

try:
    from groq import Groq
except ImportError:
    Groq = None

logger = logging.getLogger(__name__)


class VideoContentType(str, Enum):
    """Video content classification"""
    ORIGINAL = "original"
    MUSIC_VIDEO = "music_video"
    COVER = "cover"
    REMIX = "remix"
    CLIP = "clip"
    MOVIE = "movie"
    MONETIZED = "monetized"
    UNKNOWN = "unknown"


class CopyrightLevel(str, Enum):
    """Copyright risk levels"""
    SAFE = "safe"
    LOW_RISK = "low_risk"
    MEDIUM_RISK = "medium_risk"
    HIGH_RISK = "high_risk"
    BLOCKED = "blocked"


@dataclass
class VideoMetadata:
    """Video metadata for validation"""
    title: str
    description: str
    duration: int  # seconds
    uploader_id: str
    file_size: int
    video_hash: str = ""
    frame_count: int = 0
    audio_present: bool = False
    text_detected: str = ""
    faces_detected: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ContentValidationResult:
    """Validation result with detailed analysis"""
    video_id: str
    is_safe: bool
    copyright_level: CopyrightLevel
    content_type: VideoContentType
    confidence: float  # 0.0-1.0
    risk_factors: List[str] = field(default_factory=list)
    detected_issues: List[str] = field(default_factory=list)
    groq_analysis: Optional[str] = None
    ml_classification: Optional[str] = None
    recommended_action: str = "allow"  # allow, flag, block
    validation_timestamp: datetime = field(default_factory=datetime.utcnow)


class GroqVideoAnalyzer:
    """Groq-powered video content analysis"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "mixtral-8x7b-32768"):
        if Groq:
            self.client = Groq(api_key=api_key) if api_key else Groq()
        else:
            self.client = None
        self.model = model
        self.analysis_cache = {}
    
    async def analyze_content(self, metadata: VideoMetadata) -> Dict:
        """Use Groq to analyze video content"""
        cache_key = metadata.video_hash
        if cache_key in self.analysis_cache:
            cached, ts = self.analysis_cache[cache_key]
            if datetime.utcnow() - ts < timedelta(hours=24):
                return cached
        
        if not self.client:
            return self._fallback_analysis(metadata)
        
        try:
            prompt = (
                f"Analyze this video upload:\n"
                f"Title: {metadata.title}\n"
                f"Description: {metadata.description}\n"
                f"Duration: {metadata.duration}s\n"
                f"Size: {metadata.file_size} bytes\n"
                f"Audio: {metadata.audio_present}\n"
                f"\nIs this likely: movie/copyrighted/monetized/original?\n"
                f"Respond JSON: {{'type': 'original|movie|monetized|copyrighted', "
                f"'confidence': 0.0-1.0, 'reason': '...'}}"
            )
            
            msg = await asyncio.to_thread(
                self.client.messages.create,
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.3
            )
            
            analysis = msg.choices[0].message.content
            self.analysis_cache[cache_key] = (analysis, datetime.utcnow())
            return json.loads(analysis) if "{" in analysis else self._fallback_analysis(metadata)
        
        except Exception as e:
            logger.error(f"Groq analysis error: {e}")
            return self._fallback_analysis(metadata)
    
    def _fallback_analysis(self, metadata: VideoMetadata) -> Dict:
        """Fallback when Groq unavailable"""
        return {
            "type": "original",
            "confidence": 0.5,
            "reason": "Fallback analysis"
        }


class FreeMachineLearningDetector:
    """
    Free ML models for content detection
    Uses pattern-based heuristics + simulated ML inference
    """
    
    def __init__(self):
        """Initialize ML detector"""
        self.movie_keywords = [
            "trailer", "movie", "film", "cinema", "theatrical",
            "dvd", "bluray", "4k", "720p", "1080p", "streaming service",
            "full movie", "complete", "watch online", "download"
        ]
        
        self.monetized_keywords = [
            "sponsored", "ad", "advertisement", "promoted",
            "affiliate", "review", "unboxing", "haul",
            "make money", "earn", "clickbait"
        ]
        
        self.copyrighted_keywords = [
            "official", "exclusive", "world premiere",
            "concert", "performance", "live stream",
            "bbc", "cnn", "nbc", "fox", "paramount",
            "hbo", "netflix", "amazon prime"
        ]
    
    async def detect_movie_content(self, metadata: VideoMetadata) -> Tuple[float, List[str]]:
        """Detect if video is a movie or film"""
        risk_factors = []
        score = 0.0
        
        title_lower = metadata.title.lower()
        desc_lower = metadata.description.lower()
        combined = f"{title_lower} {desc_lower}"
        
        # Movie keyword detection
        movie_count = sum(1 for kw in self.movie_keywords if kw in combined)
        if movie_count > 0:
            score += 0.3 * (movie_count / len(self.movie_keywords))
            risk_factors.append(f"Movie keywords detected: {movie_count}")
        
        # Duration heuristic (movies typically 80+ min)
        if metadata.duration > 4800:  # 80 minutes
            score += 0.3
            risk_factors.append(f"Long duration: {metadata.duration}s (movie-like)")
        
        # File size heuristic (movies typically 500MB+)
        if metadata.file_size > 500 * 1024 * 1024:
            score += 0.2
            risk_factors.append(f"Large file: {metadata.file_size / (1024**3):.1f}GB (movie-like)")
        
        return min(1.0, score), risk_factors
    
    async def detect_monetized_content(self, metadata: VideoMetadata) -> Tuple[float, List[str]]:
        """Detect if video is monetized/promotional"""
        risk_factors = []
        score = 0.0
        
        title_lower = metadata.title.lower()
        desc_lower = metadata.description.lower()
        combined = f"{title_lower} {desc_lower}"
        
        # Monetized keyword detection
        monetized_count = sum(1 for kw in self.monetized_keywords if kw in combined)
        if monetized_count > 0:
            score += 0.4 * (monetized_count / len(self.monetized_keywords))
            risk_factors.append(f"Monetization indicators: {monetized_count}")
        
        # URL presence (affiliate links)
        if "http" in desc_lower or ".com" in desc_lower:
            score += 0.2
            risk_factors.append("URLs detected in description (potential affiliate)")
        
        # Call-to-action patterns
        if any(cta in combined for cta in ["subscribe", "follow", "link in bio", "use code"]):
            score += 0.2
            risk_factors.append("Call-to-action patterns detected")
        
        return min(1.0, score), risk_factors
    
    async def detect_copyrighted_content(self, metadata: VideoMetadata) -> Tuple[float, List[str]]:
        """Detect copyrighted or third-party content"""
        risk_factors = []
        score = 0.0
        
        title_lower = metadata.title.lower()
        desc_lower = metadata.description.lower()
        combined = f"{title_lower} {desc_lower}"
        
        # Copyrighted keyword detection
        copyright_count = sum(1 for kw in self.copyrighted_keywords if kw in combined)
        if copyright_count > 0:
            score += 0.35 * (copyright_count / len(self.copyrighted_keywords))
            risk_factors.append(f"Copyright indicators: {copyright_count}")
        
        # "Official" or "Exclusive" claims
        if "official" in combined or "exclusive" in combined:
            score += 0.3
            risk_factors.append("'Official' or 'Exclusive' claims detected")
        
        # Entity attribution
        if any(entity in combined for entity in ["by ", "from ", "presented by", "featuring"]):
            score += 0.15
            risk_factors.append("Third-party attribution patterns")
        
        return min(1.0, score), risk_factors
    
    async def detect_duplicate_content(self, metadata: VideoMetadata, 
                                      known_videos: Dict[str, str]) -> Tuple[bool, str]:
        """Detect if video is a duplicate/reupload"""
        # Hash-based duplicate detection
        if metadata.video_hash in known_videos:
            return True, f"Exact match: {known_videos[metadata.video_hash]}"
        
        # Simulated perceptual hashing (would use real hashing in production)
        hash_prefix = metadata.video_hash[:16]
        for known_hash, video_id in known_videos.items():
            if known_hash.startswith(hash_prefix) and len(known_hash) > 16:
                return True, f"Similar to: {video_id}"
        
        return False, ""


class VideoUploadValidator:
    """
    Comprehensive video upload validation
    Multi-layer defense: Groq + ML detection + heuristics
    """
    
    def __init__(self, groq_api_key: Optional[str] = None):
        """Initialize validator"""
        self.groq_analyzer = GroqVideoAnalyzer(api_key=groq_api_key)
        self.ml_detector = FreeMachineLearningDetector()
        self.validated_videos = {}
        self.known_videos = {}  # video_hash -> video_id mapping
        self.blocked_users = set()
        self.violation_counts = {}  # user_id -> count
    
    async def validate_upload(self, metadata: VideoMetadata) -> ContentValidationResult:
        """
        Validate video upload with multi-layer detection
        Returns: ContentValidationResult with detailed analysis
        """
        risk_factors = []
        detected_issues = []
        
        # Layer 1: User validation
        if metadata.uploader_id in self.blocked_users:
            return ContentValidationResult(
                video_id=metadata.video_hash,
                is_safe=False,
                copyright_level=CopyrightLevel.BLOCKED,
                content_type=VideoContentType.UNKNOWN,
                confidence=1.0,
                detected_issues=["User account flagged for violations"],
                recommended_action="block"
            )
        
        # Layer 2: Duplicate detection
        is_duplicate, dup_info = await self.ml_detector.detect_duplicate_content(
            metadata, self.known_videos
        )
        if is_duplicate:
            detected_issues.append(f"Duplicate content: {dup_info}")
            risk_factors.append("Reupload detected")
        
        # Layer 3: ML-based detection
        movie_score, movie_factors = await self.ml_detector.detect_movie_content(metadata)
        if movie_score > 0.6:
            detected_issues.append(f"Movie-like content detected (score: {movie_score:.2%})")
            risk_factors.extend(movie_factors)
        
        monetized_score, monetized_factors = await self.ml_detector.detect_monetized_content(metadata)
        if monetized_score > 0.5:
            detected_issues.append(f"Monetized content detected (score: {monetized_score:.2%})")
            risk_factors.extend(monetized_factors)
        
        copyright_score, copyright_factors = await self.ml_detector.detect_copyrighted_content(metadata)
        if copyright_score > 0.6:
            detected_issues.append(f"Copyrighted content detected (score: {copyright_score:.2%})")
            risk_factors.extend(copyright_factors)
        
        # Layer 4: Groq AI analysis
        groq_result = await self.groq_analyzer.analyze_content(metadata)
        groq_analysis = json.dumps(groq_result)
        groq_type = groq_result.get("type", "unknown")
        groq_confidence = groq_result.get("confidence", 0.5)
        
        if groq_type in ["movie", "monetized", "copyrighted"] and groq_confidence > 0.7:
            detected_issues.append(f"Groq flagged as {groq_type} ({groq_confidence:.0%})")
        
        # Determine copyright level and action
        max_risk = max(movie_score, monetized_score, copyright_score, groq_confidence or 0)
        
        if is_duplicate:
            copyright_level = CopyrightLevel.BLOCKED
            recommended_action = "block"
            confidence = 1.0
        elif max_risk > 0.8:
            copyright_level = CopyrightLevel.BLOCKED
            recommended_action = "block"
            confidence = max_risk
        elif max_risk > 0.6:
            copyright_level = CopyrightLevel.HIGH_RISK
            recommended_action = "flag"
            confidence = max_risk
        elif max_risk > 0.4:
            copyright_level = CopyrightLevel.MEDIUM_RISK
            recommended_action = "flag"
            confidence = max_risk
        elif max_risk > 0.2:
            copyright_level = CopyrightLevel.LOW_RISK
            recommended_action = "allow"
            confidence = max_risk
        else:
            copyright_level = CopyrightLevel.SAFE
            recommended_action = "allow"
            confidence = max_risk
        
        # Determine content type
        if groq_type == "movie":
            content_type = VideoContentType.MOVIE
        elif groq_type == "monetized":
            content_type = VideoContentType.MONETIZED
        elif groq_type == "copyrighted":
            content_type = VideoContentType.COVER
        else:
            content_type = VideoContentType.ORIGINAL
        
        # Create result
        result = ContentValidationResult(
            video_id=metadata.video_hash,
            is_safe=copyright_level in [CopyrightLevel.SAFE, CopyrightLevel.LOW_RISK],
            copyright_level=copyright_level,
            content_type=content_type,
            confidence=confidence,
            risk_factors=risk_factors,
            detected_issues=detected_issues,
            groq_analysis=groq_analysis,
            ml_classification=f"movie:{movie_score:.0%}, monetized:{monetized_score:.0%}, copyrighted:{copyright_score:.0%}",
            recommended_action=recommended_action
        )
        
        # Store validation
        self.validated_videos[metadata.video_hash] = result
        
        # Track violations for user
        if recommended_action == "block":
            self.violation_counts[metadata.uploader_id] = self.violation_counts.get(metadata.uploader_id, 0) + 1
            if self.violation_counts[metadata.uploader_id] >= 3:
                self.blocked_users.add(metadata.uploader_id)
                logger.warning(f"User {metadata.uploader_id} blocked after 3 violations")
        
        logger.info(f"Validation: {result.video_id[:8]}... -> {result.recommended_action} ({result.copyright_level.value})")
        return result
    
    def get_validation_result(self, video_hash: str) -> Optional[ContentValidationResult]:
        """Get stored validation result"""
        return self.validated_videos.get(video_hash)
    
    async def bulk_validate(self, metadata_list: List[VideoMetadata]) -> List[ContentValidationResult]:
        """Validate multiple uploads"""
        results = []
        for metadata in metadata_list:
            result = await self.validate_upload(metadata)
            results.append(result)
        return results
    
    def register_video(self, video_hash: str, video_id: str):
        """Register validated video for duplicate detection"""
        self.known_videos[video_hash] = video_id
    
    def unblock_user(self, user_id: str):
        """Unblock user (after appeal/correction)"""
        self.blocked_users.discard(user_id)
        self.violation_counts[user_id] = 0
    
    def get_user_status(self, user_id: str) -> Dict:
        """Get user upload status"""
        return {
            "user_id": user_id,
            "is_blocked": user_id in self.blocked_users,
            "violation_count": self.violation_counts.get(user_id, 0),
            "validated_videos": len([v for v in self.validated_videos.values() 
                                     if v.video_id.startswith(user_id[:4])])
        }


class Phase3VideoProtection:
    """Master orchestrator for advanced video protection"""
    
    def __init__(self, groq_api_key: Optional[str] = None):
        self.validator = VideoUploadValidator(groq_api_key=groq_api_key)
    
    async def validate_video_upload(self, metadata: VideoMetadata) -> ContentValidationResult:
        """Validate incoming video upload"""
        return await self.validator.validate_upload(metadata)
    
    async def health_check(self) -> Dict:
        """System health check"""
        return {
            "status": "healthy",
            "validated_videos": len(self.validator.validated_videos),
            "blocked_users": len(self.validator.blocked_users),
            "known_videos": len(self.validator.known_videos),
            "groq_available": self.validator.groq_analyzer.client is not None
        }
