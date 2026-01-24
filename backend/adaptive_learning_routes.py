"""
Adaptive Learning Paths API Routes
RESTful API for integrating adaptive learning with eLearning and AI Tutoring.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

from .adaptive_learning_paths import (
    LearningPath,
    AdaptiveRecommendation,
    PathProgressUpdate,
    LessonAnalytics,
    learning_path_manager,
    adaptive_course_adapter
)

# ============================================================================
# ROUTER & DEPENDENCIES
# ============================================================================

router = APIRouter(tags=["adaptive-learning"])

# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class CreateLearningPathRequest(BaseModel):
    """Request to create a new learning path"""
    student_id: str
    course_id: str
    total_lessons: int
    content_types: List[str]

class LessonAnalyticsRequest(BaseModel):
    """Submit lesson analytics and get next recommendation"""
    lesson_id: str
    student_id: str
    course_id: str
    content_type: str
    time_spent_seconds: int = 0
    quiz_attempts: int = 0
    quiz_scores: List[float] = []
    hints_requested: int = 0
    completed: bool = True

class UpdateProgressRequest(BaseModel):
    """Update learning path progress"""
    lesson_id: str
    student_id: str
    course_id: str
    completion_status: bool
    quiz_score: Optional[float] = None
    time_spent_seconds: int = 0
    struggles_identified: List[str] = []

class LessonInfo(BaseModel):
    """Lesson information for recommendations"""
    id: str
    title: str
    lesson_number: int
    content_type: str
    difficulty: str  # "easy", "medium", "hard"
    duration: int  # minutes

# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post("/learning-path/create", response_model=LearningPath)
async def create_learning_path(request: CreateLearningPathRequest):
    """
    Create a new adaptive learning path for a student.
    
    This initializes the AI-powered learning journey by:
    - Fetching initial proficiency from tutoring system
    - Setting up content type tracking
    - Creating personalized progression
    
    Example:
    ```
    POST /adaptive-learning/learning-path/create
    {
      "student_id": "student_123",
      "course_id": "course_001",
      "total_lessons": 15,
      "content_types": ["math", "science"]
    }
    ```
    """
    try:
        path = await learning_path_manager.create_path(
            request.student_id,
            request.course_id,
            request.total_lessons,
            request.content_types
        )
        return path
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating path: {str(e)}")

@router.get("/learning-path/{path_id}", response_model=LearningPath)
async def get_learning_path(path_id: str):
    """
    Retrieve a learning path by ID.
    
    Returns current progress, recommendations, and proficiency data.
    """
    path = learning_path_manager.paths.get(path_id)
    if not path:
        raise HTTPException(status_code=404, detail="Learning path not found")
    return path

@router.post("/recommendation/next", response_model=AdaptiveRecommendation)
async def get_next_recommendation(
    path_id: str = Query(...),
    lesson_id: str = Query(...),
    analytics: LessonAnalyticsRequest = None,
    available_lessons: List[LessonInfo] = None
):
    """
    Get the next recommended lesson based on student performance.
    
    This endpoint:
    - Analyzes lesson performance using tutoring proficiency data
    - Determines if student is struggling, maintaining, or mastering
    - Returns personalized next step (prerequisite, challenge, or next)
    
    Example:
    ```
    POST /adaptive-learning/recommendation/next?path_id=path_123&lesson_id=lesson_001
    {
      "lesson_id": "lesson_001",
      "student_id": "student_123",
      "course_id": "course_001",
      "content_type": "math",
      "quiz_scores": [0.85, 0.90],
      "time_spent_seconds": 1800,
      "hints_requested": 2
    }
    ```
    """
    try:
        if not analytics:
            raise ValueError("Analytics data required")
        
        # Convert request to LessonAnalytics
        lesson_analytics = LessonAnalytics(
            lesson_id=analytics.lesson_id,
            student_id=analytics.student_id,
            content_type=analytics.content_type,
            detected_difficulty="medium",
            time_spent_seconds=analytics.time_spent_seconds,
            quiz_attempts=analytics.quiz_attempts,
            quiz_scores=analytics.quiz_scores,
            average_score=sum(analytics.quiz_scores) / len(analytics.quiz_scores)
                          if analytics.quiz_scores else 0,
            hints_requested=analytics.hints_requested,
            completed=True
        )
        
        # Convert available_lessons to dicts
        lessons_dicts = [l.dict() if isinstance(l, LessonInfo) else l for l in (available_lessons or [])]
        
        recommendation = await learning_path_manager.get_next_recommendation(
            path_id,
            lesson_id,
            lesson_analytics,
            lessons_dicts
        )
        
        return recommendation
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting recommendation: {str(e)}")

@router.post("/progress/update", response_model=LearningPath)
async def update_progress(request: UpdateProgressRequest):
    """
    Update learning path with lesson completion data.
    
    This endpoint:
    - Updates proficiency scores using exponential moving average
    - Identifies struggling vs mastering students
    - Tracks tutoring topics for AI support
    - Updates estimated completion time
    
    Example:
    ```
    POST /adaptive-learning/progress/update
    {
      "lesson_id": "lesson_001",
      "student_id": "student_123",
      "course_id": "course_001",
      "completion_status": true,
      "quiz_score": 0.85,
      "time_spent_seconds": 1800,
      "struggles_identified": ["quadratic equations"]
    }
    ```
    """
    try:
        # Get path ID from student and course
        path_id = f"path_{request.student_id}_{request.course_id}"
        
        update = PathProgressUpdate(
            lesson_id=request.lesson_id,
            student_id=request.student_id,
            course_id=request.course_id,
            completion_status=request.completion_status,
            quiz_score=request.quiz_score,
            time_spent_seconds=request.time_spent_seconds,
            struggles_identified=request.struggles_identified
        )
        
        updated_path = await learning_path_manager.update_progress(path_id, update)
        return updated_path
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating progress: {str(e)}")

@router.get("/analytics/{path_id}")
async def get_learning_analytics(path_id: str):
    """
    Get comprehensive learning analytics for a path.
    
    Returns:
    - Completion percentage
    - Average quiz scores
    - Content type proficiency
    - Weak and strong areas
    - Estimated completion date
    - Tutoring session count
    
    Example Response:
    ```json
    {
      "total_lessons": 15,
      "completed_lessons": 5,
      "completion_percentage": 33.3,
      "average_quiz_score": 0.82,
      "content_proficiency": {
        "math": 0.85,
        "science": 0.78
      },
      "weak_areas": ["science"],
      "strong_areas": ["math"],
      "estimated_completion": "2026-02-21T10:30:00",
      "status": "in_progress"
    }
    ```
    """
    try:
        analytics = learning_path_manager.get_analytics(path_id)
        return analytics
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting analytics: {str(e)}")

@router.get("/course-progression/{path_id}")
async def get_course_progression(path_id: str):
    """
    Get adapted course progression for a student.
    
    Returns:
    - Current recommended lesson
    - Upcoming lessons (next 5)
    - Supplementary lessons for weak areas
    - Skipped lessons (if applicable)
    - Recent AI recommendations
    
    Example Response:
    ```json
    {
      "current_lesson": "lesson_005",
      "upcoming_lessons": ["lesson_005", "lesson_006", "lesson_007", "lesson_008", "lesson_009"],
      "supplementary_lessons": ["lesson_prereq_001"],
      "skipped_lessons": [],
      "recommendations": [
        {
          "lesson_id": "lesson_005",
          "lesson_title": "Advanced Algebra",
          "recommendation_type": "next",
          "reason": "Continue with next lesson in sequence",
          "priority": 5,
          "confidence_score": 0.90
        }
      ]
    }
    ```
    """
    try:
        progression = await adaptive_course_adapter.get_course_progression(path_id)
        return progression
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting progression: {str(e)}")

@router.get("/should-skip-lesson/{path_id}")
async def should_skip_lesson(
    path_id: str = Query(...),
    lesson_id: str = Query(...),
    content_type: str = Query(...)
):
    """
    Determine if student should skip a lesson based on proficiency.
    
    Students can skip lessons they've already mastered (>90% proficiency).
    
    Example:
    ```
    GET /adaptive-learning/should-skip-lesson?path_id=path_123&lesson_id=lesson_001&content_type=math
    ```
    
    Response:
    ```json
    {
      "should_skip": true,
      "reason": "You've mastered this content (95% proficiency)"
    }
    ```
    """
    try:
        should_skip = await adaptive_course_adapter.should_skip_lesson(
            path_id,
            lesson_id,
            content_type
        )
        
        path = learning_path_manager.paths.get(path_id)
        proficiency = path.content_proficiency.get(content_type, 0) if path else 0
        
        return {
            "should_skip": should_skip,
            "proficiency": f"{proficiency:.0%}",
            "reason": (
                f"You've mastered this content ({proficiency:.0%} proficiency)"
                if should_skip
                else f"Continue learning (proficiency: {proficiency:.0%})"
            )
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking skip status: {str(e)}")

@router.post("/tutoring-integration/link-session")
async def link_tutoring_session(
    path_id: str = Query(...),
    session_id: str = Query(...),
    topic: str = Query(...)
):
    """
    Link an AI Tutoring session to a learning path.
    
    This endpoint tracks tutoring interactions within the learning path
    to provide comprehensive learning analytics.
    
    Example:
    ```
    POST /adaptive-learning/tutoring-integration/link-session?path_id=path_123&session_id=tut_001&topic=quadratic+equations
    ```
    """
    try:
        path = learning_path_manager.paths.get(path_id)
        if not path:
            raise ValueError("Path not found")
        
        path.tutoring_sessions += 1
        path.tutoring_topics.append(topic)
        path.tutoring_topics = list(set(path.tutoring_topics))
        path.updated_at = datetime.utcnow()
        
        return {
            "success": True,
            "tutoring_sessions": path.tutoring_sessions,
            "topics_covered": path.tutoring_topics
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error linking session: {str(e)}")

@router.get("/weak-areas/{path_id}")
async def get_weak_areas(path_id: str):
    """
    Get weak areas where student needs additional support.
    
    Returns list of content types where proficiency is below 60%.
    Useful for recommending AI Tutoring sessions.
    
    Example Response:
    ```json
    {
      "weak_areas": ["science", "history"],
      "proficiency": {
        "science": 0.45,
        "history": 0.55
      },
      "recommended_tutoring_topics": [
        "Photosynthesis explanation",
        "Historical timeline review"
      ]
    }
    ```
    """
    try:
        path = learning_path_manager.paths.get(path_id)
        if not path:
            raise ValueError("Path not found")
        
        weak_areas = learning_path_manager.engine.identify_weak_areas(path)
        
        return {
            "weak_areas": weak_areas,
            "proficiency": {
                ct: path.content_proficiency.get(ct, 0)
                for ct in weak_areas
            },
            "recommended_tutoring_topics": path.tutoring_topics
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting weak areas: {str(e)}")

@router.get("/strong-areas/{path_id}")
async def get_strong_areas(path_id: str):
    """
    Get strong areas where student excels.
    
    Returns list of content types where proficiency is >= 85%.
    
    Example Response:
    ```json
    {
      "strong_areas": ["math", "technology"],
      "proficiency": {
        "math": 0.92,
        "technology": 0.88
      }
    }
    ```
    """
    try:
        path = learning_path_manager.paths.get(path_id)
        if not path:
            raise ValueError("Path not found")
        
        strong_areas = learning_path_manager.engine.identify_strong_areas(path)
        
        return {
            "strong_areas": strong_areas,
            "proficiency": {
                ct: path.content_proficiency.get(ct, 0)
                for ct in strong_areas
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting strong areas: {str(e)}")
