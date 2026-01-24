"""
Adaptive Learning Paths Integration
Integrates AI Tutoring with eLearning for personalized learning journeys.
Uses proficiency tracking to dynamically adapt course progression.
"""

from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
from pydantic import BaseModel, Field

# ============================================================================
# ENUMS & CONSTANTS
# ============================================================================

class LearningPathStatus(str, Enum):
    """Learning path status"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    ABANDONED = "abandoned"

class LessonRecommendation(str, Enum):
    """Lesson recommendation type"""
    NEXT = "next"
    PREREQUISITE = "prerequisite"
    OPTIONAL = "optional"
    CHALLENGE = "challenge"
    REVIEW = "review"
    SKIP = "skip"

class ContentDifficulty(str, Enum):
    """Content difficulty levels"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

# ============================================================================
# MODELS
# ============================================================================

class ProficiencyProfile(BaseModel):
    """Student proficiency across content types"""
    student_id: str
    proficiency_scores: Dict[str, float] = Field(default_factory=dict)  # content_type -> score (0-1)
    learning_velocity: Dict[str, float] = Field(default_factory=dict)  # content_type -> velocity (lessons/day)
    estimated_completion_dates: Dict[str, datetime] = Field(default_factory=dict)
    weak_areas: List[str] = Field(default_factory=list)
    strong_areas: List[str] = Field(default_factory=list)
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class LessonAnalytics(BaseModel):
    """Analytics for a single lesson"""
    lesson_id: str
    student_id: str
    content_type: str
    detected_difficulty: ContentDifficulty
    time_spent_seconds: int = 0
    quiz_attempts: int = 0
    quiz_scores: List[float] = Field(default_factory=list)
    average_score: Optional[float] = None
    ai_tutoring_sessions: int = 0
    hints_requested: int = 0
    completed: bool = False
    completion_date: Optional[datetime] = None
    is_struggling: bool = False
    is_mastering: bool = False

class AdaptiveRecommendation(BaseModel):
    """AI-powered recommendation for next learning step"""
    lesson_id: str
    lesson_title: str
    recommendation_type: LessonRecommendation
    reason: str
    priority: int  # 1-10, higher = more urgent
    estimated_duration: int  # minutes
    difficulty_adjustment: str  # "increase", "decrease", "maintain"
    suggested_tutoring_topics: List[str] = Field(default_factory=list)
    prerequisites_met: bool = True
    confidence_score: float  # 0-1, how confident is the recommendation
    estimated_completion_time: datetime

class LearningPath(BaseModel):
    """Adaptive learning path for a student in a course"""
    path_id: str
    student_id: str
    course_id: str
    status: LearningPathStatus = LearningPathStatus.NOT_STARTED
    
    # Progress tracking
    total_lessons: int
    lessons_completed: int = 0
    average_quiz_score: float = 0.0
    estimated_completion: datetime
    
    # Adaptive elements
    current_recommended_lesson: Optional[str] = None
    upcoming_lessons: List[str] = Field(default_factory=list)
    skipped_lessons: List[str] = Field(default_factory=list)
    supplementary_lessons: List[str] = Field(default_factory=list)
    
    # Content type tracking
    content_proficiency: Dict[str, float] = Field(default_factory=dict)
    time_per_content_type: Dict[str, int] = Field(default_factory=dict)
    
    # Tutoring integration
    tutoring_sessions: int = 0
    tutoring_topics: List[str] = Field(default_factory=list)
    ai_recommendations: List[AdaptiveRecommendation] = Field(default_factory=list)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_accessed: datetime = Field(default_factory=datetime.utcnow)

class PathProgressUpdate(BaseModel):
    """Update for learning path progress"""
    lesson_id: str
    student_id: str
    course_id: str
    completion_status: bool
    quiz_score: Optional[float] = None
    time_spent_seconds: int = 0
    struggles_identified: List[str] = Field(default_factory=list)

# ============================================================================
# ADAPTIVE LEARNING ENGINE
# ============================================================================

class AdaptiveLearningEngine:
    """
    Main engine for adaptive learning path management.
    Uses AI Tutoring proficiency data to personalize course progression.
    """
    
    def __init__(self, tutoring_api_url: str = "http://localhost:8000/ai-tutoring"):
        """Initialize the adaptive learning engine."""
        self.tutoring_api_url = tutoring_api_url
        self.min_proficiency_threshold = 0.6  # 60% proficiency required to progress
        self.struggle_threshold = 0.4  # < 40% indicates struggling
        self.mastery_threshold = 0.85  # >= 85% indicates mastery
    
    async def initialize_learning_path(
        self,
        student_id: str,
        course_id: str,
        total_lessons: int,
        content_types: List[str]
    ) -> LearningPath:
        """
        Initialize an adaptive learning path for a student.
        
        Args:
            student_id: Student ID from tutoring system
            course_id: Course ID from eLearning system
            total_lessons: Total number of lessons in course
            content_types: List of content types covered
        
        Returns:
            Initialized LearningPath with first recommendations
        """
        path = LearningPath(
            path_id=f"path_{student_id}_{course_id}",
            student_id=student_id,
            course_id=course_id,
            total_lessons=total_lessons,
            content_proficiency={ct: 0.5 for ct in content_types},  # Start at 50%
            estimated_completion=datetime.utcnow() + timedelta(days=30)
        )
        
        # Get initial proficiency from tutoring system
        proficiency = await self._fetch_student_proficiency(student_id)
        path.content_proficiency.update(proficiency.proficiency_scores)
        
        return path
    
    async def get_next_lesson_recommendation(
        self,
        path: LearningPath,
        current_lesson_id: str,
        lesson_analytics: LessonAnalytics,
        available_lessons: List[Dict[str, Any]]
    ) -> AdaptiveRecommendation:
        """
        Get AI-powered recommendation for next lesson based on proficiency.
        
        Args:
            path: Current learning path
            current_lesson_id: Just completed lesson
            lesson_analytics: Analytics from current lesson
            available_lessons: List of available lessons with metadata
        
        Returns:
            Recommendation for next step
        """
        # Update proficiency based on performance
        content_type = lesson_analytics.content_type
        quiz_score = lesson_analytics.average_score or 0.0
        
        # Update content proficiency (exponential moving average)
        alpha = 0.3
        current_proficiency = path.content_proficiency.get(content_type, 0.5)
        new_proficiency = (alpha * quiz_score) + ((1 - alpha) * current_proficiency)
        path.content_proficiency[content_type] = new_proficiency
        
        # Determine if student is struggling or mastering
        is_struggling = quiz_score < self.struggle_threshold
        is_mastering = quiz_score >= self.mastery_threshold
        lesson_analytics.is_struggling = is_struggling
        lesson_analytics.is_mastering = is_mastering
        
        # Find next lesson
        if is_struggling:
            # Recommend prerequisite or review lesson
            recommendation = await self._recommend_remedial_lesson(
                path, available_lessons, content_type, lesson_analytics
            )
        elif is_mastering:
            # Recommend advanced or challenge lesson
            recommendation = await self._recommend_challenge_lesson(
                path, available_lessons, content_type, lesson_analytics
            )
        else:
            # Recommend next sequential lesson
            recommendation = await self._recommend_next_lesson(
                path, available_lessons, content_type
            )
        
        path.ai_recommendations.append(recommendation)
        return recommendation
    
    async def _recommend_remedial_lesson(
        self,
        path: LearningPath,
        available_lessons: List[Dict[str, Any]],
        content_type: str,
        analytics: LessonAnalytics
    ) -> AdaptiveRecommendation:
        """Recommend a remedial lesson for struggling student."""
        # Find similar lessons with lower difficulty
        remedial_lessons = [
            l for l in available_lessons
            if l.get('content_type') == content_type
            and l.get('difficulty') in ['easy', 'medium']
            and l.get('id') not in path.skipped_lessons
        ]
        
        if remedial_lessons:
            lesson = remedial_lessons[0]
            tutoring_topics = self._identify_tutoring_topics(analytics)
            
            return AdaptiveRecommendation(
                lesson_id=lesson['id'],
                lesson_title=lesson['title'],
                recommendation_type=LessonRecommendation.REVIEW,
                reason=f"You scored {analytics.average_score:.0%} on {content_type}. "
                       f"Let's review this concept before moving on.",
                priority=9,
                estimated_duration=lesson.get('duration', 30),
                difficulty_adjustment="decrease",
                suggested_tutoring_topics=tutoring_topics,
                prerequisites_met=True,
                confidence_score=0.95,
                estimated_completion_time=datetime.utcnow() + timedelta(days=1)
            )
        else:
            # Fallback to next lesson
            return await self._recommend_next_lesson(path, available_lessons, content_type)
    
    async def _recommend_challenge_lesson(
        self,
        path: LearningPath,
        available_lessons: List[Dict[str, Any]],
        content_type: str,
        analytics: LessonAnalytics
    ) -> AdaptiveRecommendation:
        """Recommend a challenge lesson for mastering student."""
        # Find advanced lessons
        challenge_lessons = [
            l for l in available_lessons
            if l.get('content_type') == content_type
            and l.get('difficulty') in ['hard', 'advanced']
            and l.get('id') not in [p for p in path.upcoming_lessons]
        ]
        
        if challenge_lessons:
            lesson = challenge_lessons[0]
            
            return AdaptiveRecommendation(
                lesson_id=lesson['id'],
                lesson_title=lesson['title'],
                recommendation_type=LessonRecommendation.CHALLENGE,
                reason=f"Excellent work! You scored {analytics.average_score:.0%}. "
                       f"Ready for a challenge?",
                priority=7,
                estimated_duration=lesson.get('duration', 45),
                difficulty_adjustment="increase",
                suggested_tutoring_topics=[],
                prerequisites_met=True,
                confidence_score=0.92,
                estimated_completion_time=datetime.utcnow() + timedelta(days=2)
            )
        else:
            return await self._recommend_next_lesson(path, available_lessons, content_type)
    
    async def _recommend_next_lesson(
        self,
        path: LearningPath,
        available_lessons: List[Dict[str, Any]],
        content_type: str
    ) -> AdaptiveRecommendation:
        """Recommend the next sequential lesson."""
        # Find next lesson not yet completed
        next_lessons = [
            l for l in available_lessons
            if l.get('id') not in [path.lessons_completed]
            and l.get('lesson_number', 0) > path.lessons_completed
        ]
        
        if next_lessons:
            lesson = next_lessons[0]
            
            return AdaptiveRecommendation(
                lesson_id=lesson['id'],
                lesson_title=lesson['title'],
                recommendation_type=LessonRecommendation.NEXT,
                reason="Continue with the next lesson in the course.",
                priority=5,
                estimated_duration=lesson.get('duration', 30),
                difficulty_adjustment="maintain",
                suggested_tutoring_topics=[],
                prerequisites_met=True,
                confidence_score=0.90,
                estimated_completion_time=datetime.utcnow() + timedelta(days=1)
            )
        else:
            # All lessons completed
            return AdaptiveRecommendation(
                lesson_id="course_complete",
                lesson_title="Course Complete!",
                recommendation_type=LessonRecommendation.SKIP,
                reason="Congratulations! You've completed all lessons.",
                priority=0,
                estimated_duration=0,
                difficulty_adjustment="maintain",
                suggested_tutoring_topics=[],
                prerequisites_met=True,
                confidence_score=1.0,
                estimated_completion_time=datetime.utcnow()
            )
    
    async def update_learning_path(
        self,
        path: LearningPath,
        update: PathProgressUpdate
    ) -> LearningPath:
        """Update learning path based on lesson completion."""
        # Increment completion count
        path.lessons_completed += 1
        
        # Update average score
        if update.quiz_score:
            avg = path.average_quiz_score
            path.average_quiz_score = (
                (avg * (path.lessons_completed - 1) + update.quiz_score) 
                / path.lessons_completed
            )
        
        # Update time tracking
        for ct in path.content_proficiency.keys():
            if ct not in path.time_per_content_type:
                path.time_per_content_type[ct] = 0
            path.time_per_content_type[ct] += update.time_spent_seconds
        
        # Log tutoring topics if struggles identified
        if update.struggles_identified:
            path.tutoring_topics.extend(update.struggles_identified)
            path.tutoring_topics = list(set(path.tutoring_topics))  # Remove duplicates
        
        # Update status
        if path.lessons_completed == path.total_lessons:
            path.status = LearningPathStatus.COMPLETED
        elif path.lessons_completed > 0:
            path.status = LearningPathStatus.IN_PROGRESS
        
        path.updated_at = datetime.utcnow()
        return path
    
    def identify_weak_areas(self, path: LearningPath) -> List[str]:
        """Identify content areas where student is struggling."""
        weak_areas = [
            ct for ct, score in path.content_proficiency.items()
            if score < self.struggle_threshold
        ]
        return weak_areas
    
    def identify_strong_areas(self, path: LearningPath) -> List[str]:
        """Identify content areas where student excels."""
        strong_areas = [
            ct for ct, score in path.content_proficiency.items()
            if score >= self.mastery_threshold
        ]
        return strong_areas
    
    def calculate_estimated_completion(self, path: LearningPath, avg_lessons_per_day: float = 0.5) -> datetime:
        """
        Calculate estimated completion date based on current progress and learning velocity.
        
        Args:
            path: Current learning path
            avg_lessons_per_day: Average lessons completed per day
        
        Returns:
            Estimated completion datetime
        """
        lessons_remaining = path.total_lessons - path.lessons_completed
        days_remaining = lessons_remaining / avg_lessons_per_day if avg_lessons_per_day > 0 else 30
        return datetime.utcnow() + timedelta(days=days_remaining)
    
    def get_learning_analytics(self, path: LearningPath) -> Dict[str, Any]:
        """Generate comprehensive learning analytics for a path."""
        return {
            'total_lessons': path.total_lessons,
            'completed_lessons': path.lessons_completed,
            'completion_percentage': (path.lessons_completed / path.total_lessons * 100) if path.total_lessons > 0 else 0,
            'average_quiz_score': path.average_quiz_score,
            'content_proficiency': path.content_proficiency,
            'weak_areas': self.identify_weak_areas(path),
            'strong_areas': self.identify_strong_areas(path),
            'estimated_completion': path.estimated_completion,
            'status': path.status.value,
            'tutoring_sessions': path.tutoring_sessions,
            'time_per_content_type': path.time_per_content_type,
        }
    
    # Helper methods
    
    async def _fetch_student_proficiency(self, student_id: str) -> ProficiencyProfile:
        """Fetch proficiency data from tutoring system."""
        # This would call the AI Tutoring API
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.tutoring_api_url}/student/{student_id}/proficiency"
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return ProficiencyProfile(
                            student_id=student_id,
                            proficiency_scores=data.get('estimated_proficiency', {})
                        )
        except Exception as e:
            print(f"Error fetching proficiency: {e}")
        
        # Return default if fetch fails
        return ProficiencyProfile(student_id=student_id)
    
    def _identify_tutoring_topics(self, analytics: LessonAnalytics) -> List[str]:
        """Identify topics that need tutoring support."""
        topics = []
        
        if analytics.average_score and analytics.average_score < self.struggle_threshold:
            topics.append(f"Review {analytics.content_type}")
        
        if analytics.quiz_attempts > 3:
            topics.append(f"Concept explanation for {analytics.content_type}")
        
        if analytics.hints_requested > 5:
            topics.append(f"Detailed walkthrough of {analytics.content_type}")
        
        return topics


# ============================================================================
# LEARNING PATH MANAGER
# ============================================================================

class LearningPathManager:
    """
    Manages learning paths for multiple students across courses.
    """
    
    def __init__(self):
        """Initialize the learning path manager."""
        self.engine = AdaptiveLearningEngine()
        self.paths: Dict[str, LearningPath] = {}  # In-memory storage (use DB in production)
    
    async def create_path(
        self,
        student_id: str,
        course_id: str,
        total_lessons: int,
        content_types: List[str]
    ) -> LearningPath:
        """Create a new learning path for a student."""
        path = await self.engine.initialize_learning_path(
            student_id, course_id, total_lessons, content_types
        )
        self.paths[path.path_id] = path
        return path
    
    async def get_next_recommendation(
        self,
        path_id: str,
        current_lesson_id: str,
        analytics: LessonAnalytics,
        available_lessons: List[Dict[str, Any]]
    ) -> AdaptiveRecommendation:
        """Get next lesson recommendation."""
        path = self.paths.get(path_id)
        if not path:
            raise ValueError(f"Path {path_id} not found")
        
        return await self.engine.get_next_lesson_recommendation(
            path, current_lesson_id, analytics, available_lessons
        )
    
    async def update_progress(
        self,
        path_id: str,
        update: PathProgressUpdate
    ) -> LearningPath:
        """Update learning path progress."""
        path = self.paths.get(path_id)
        if not path:
            raise ValueError(f"Path {path_id} not found")
        
        updated_path = await self.engine.update_learning_path(path, update)
        self.paths[path_id] = updated_path
        return updated_path
    
    def get_analytics(self, path_id: str) -> Dict[str, Any]:
        """Get learning analytics for a path."""
        path = self.paths.get(path_id)
        if not path:
            raise ValueError(f"Path {path_id} not found")
        
        return self.engine.get_learning_analytics(path)


# ============================================================================
# COURSE ADAPTER
# ============================================================================

class AdaptiveCourseAdapter:
    """
    Adapts course content and progression based on student proficiency.
    """
    
    def __init__(self, path_manager: LearningPathManager):
        """Initialize the course adapter."""
        self.path_manager = path_manager
    
    async def get_course_progression(
        self,
        path_id: str
    ) -> Dict[str, Any]:
        """
        Get adapted course progression for a student.
        
        Returns lesson recommendations, skipped lessons, and supplementary content.
        """
        path = self.path_manager.paths.get(path_id)
        if not path:
            raise ValueError(f"Path {path_id} not found")
        
        return {
            'current_lesson': path.current_recommended_lesson,
            'upcoming_lessons': path.upcoming_lessons[:5],  # Next 5
            'supplementary_lessons': path.supplementary_lessons,
            'skipped_lessons': path.skipped_lessons,
            'recommendations': [
                r.dict() for r in path.ai_recommendations[-3:]  # Last 3 recommendations
            ]
        }
    
    async def should_skip_lesson(
        self,
        path_id: str,
        lesson_id: str,
        content_type: str
    ) -> bool:
        """
        Determine if student should skip a lesson based on proficiency.
        """
        path = self.path_manager.paths.get(path_id)
        if not path:
            return False
        
        proficiency = path.content_proficiency.get(content_type, 0.5)
        # Skip if proficiency > 90% (clearly mastered)
        return proficiency > 0.90


# Export instances
learning_path_manager = LearningPathManager()
adaptive_course_adapter = AdaptiveCourseAdapter(learning_path_manager)
