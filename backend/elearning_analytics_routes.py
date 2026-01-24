"""
E-LEARNING ANALYTICS API ROUTES
================================================================================
REST API endpoints for E-Learning analytics
Comprehensive course, student, and performance tracking
================================================================================
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import logging

from elearning_analytics import (
    ELearningAnalyticsEngine,
    initialize_elearning_analytics,
    get_elearning_analytics_engine,
    CourseLevel,
    StudentProgressStatus,
    LessonType,
)

logger = logging.getLogger(__name__)

# ============== ROUTER SETUP ==============

router = APIRouter(prefix="/api/analytics/elearning", tags=["elearning-analytics"])


def get_engine() -> ELearningAnalyticsEngine:
    """Get or initialize E-Learning analytics engine"""
    engine = get_elearning_analytics_engine()
    if not engine:
        engine = initialize_elearning_analytics()
    return engine


# ============== COURSE MANAGEMENT ==============

@router.post("/courses/create")
async def create_course(
    course_name: str,
    instructor_id: str,
    level: str = "beginner",
    engine: ELearningAnalyticsEngine = Depends(get_engine),
):
    """Create new course and start tracking"""
    try:
        import uuid
        course_id = str(uuid.uuid4())
        
        course_level = CourseLevel(level.lower())
        course = await engine.track_course_creation(
            course_id=course_id,
            course_name=course_name,
            instructor_id=instructor_id,
            level=course_level,
        )
        
        return {
            "success": True,
            "course_id": course_id,
            "course_name": course_name,
            "level": level,
            "created_at": course.created_date.isoformat(),
        }
    except Exception as e:
        logger.error(f"Error creating course: {e}")
        raise HTTPException(status_code=500, detail="Failed to create course")


@router.post("/courses/{course_id}/publish")
async def publish_course(
    course_id: str,
    engine: ELearningAnalyticsEngine = Depends(get_engine),
):
    """Publish course"""
    try:
        success = await engine.track_course_publish(course_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Course not found")
        
        return {
            "success": True,
            "course_id": course_id,
            "message": "Course published successfully",
            "published_at": datetime.utcnow().isoformat(),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error publishing course: {e}")
        raise HTTPException(status_code=500, detail="Failed to publish course")


@router.get("/courses/{course_id}")
async def get_course_analytics(
    course_id: str,
    engine: ELearningAnalyticsEngine = Depends(get_engine),
):
    """Get complete course analytics"""
    try:
        course = engine.get_course_analytics(course_id)
        
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        return {
            "course_id": course.course_id,
            "course_name": course.course_name,
            "instructor_id": course.instructor_id,
            "level": course.course_level.value,
            "status": course.status.value,
            "created_date": course.created_date.isoformat(),
            "published_date": course.published_date.isoformat() if course.published_date else None,
            "total_modules": course.total_modules,
            "total_lessons": course.total_lessons,
            "total_quizzes": course.total_quizzes,
            "total_duration_hours": round(course.total_duration_hours, 2),
            "total_enrolled": course.total_enrolled,
            "total_active_students": course.total_active_students,
            "completion_rate": round(course.completion_rate, 2),
            "dropout_rate": round(course.dropout_rate, 2),
            "avg_completion_time_hours": round(course.avg_completion_time_hours, 2),
            "avg_course_rating": round(course.avg_course_rating, 2),
            "avg_student_score": round(course.avg_student_score, 2),
            "passing_rate": round(course.passing_rate, 2),
            "avg_engagement_score": round(course.avg_engagement_score, 2),
            "total_student_hours": round(course.total_student_hours, 2),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting course analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get course analytics")


@router.get("/courses/{course_id}/completion-analysis")
async def get_completion_analysis(
    course_id: str,
    engine: ELearningAnalyticsEngine = Depends(get_engine),
):
    """Get detailed completion analysis"""
    try:
        analysis = engine.get_course_completion_analysis(course_id)
        
        if not analysis:
            raise HTTPException(status_code=404, detail="Course not found")
        
        return analysis
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting completion analysis: {e}")
        raise HTTPException(status_code=500, detail="Failed to get completion analysis")


# ============== MODULE & LESSON MANAGEMENT ==============

@router.post("/courses/{course_id}/modules/add")
async def add_module(
    course_id: str,
    module_name: str,
    lesson_count: int = 0,
    engine: ELearningAnalyticsEngine = Depends(get_engine),
):
    """Add module to course"""
    try:
        import uuid
        module_id = str(uuid.uuid4())
        
        success = await engine.add_module(
            course_id=course_id,
            module_id=module_id,
            module_name=module_name,
            lesson_count=lesson_count,
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Course not found")
        
        return {
            "success": True,
            "module_id": module_id,
            "module_name": module_name,
            "lesson_count": lesson_count,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding module: {e}")
        raise HTTPException(status_code=500, detail="Failed to add module")


@router.post("/courses/{course_id}/modules/{module_id}/lessons/add")
async def add_lesson(
    course_id: str,
    module_id: str,
    title: str,
    lesson_type: str,
    duration_minutes: float = 0.0,
    engine: ELearningAnalyticsEngine = Depends(get_engine),
):
    """Add lesson to module"""
    try:
        import uuid
        lesson_id = str(uuid.uuid4())
        
        lesson_enum = LessonType(lesson_type.upper())
        success = await engine.add_lesson(
            course_id=course_id,
            module_id=module_id,
            lesson_id=lesson_id,
            lesson_type=lesson_enum,
            title=title,
            duration_minutes=duration_minutes,
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Course or module not found")
        
        return {
            "success": True,
            "lesson_id": lesson_id,
            "title": title,
            "type": lesson_type,
            "duration_minutes": duration_minutes,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding lesson: {e}")
        raise HTTPException(status_code=500, detail="Failed to add lesson")


@router.get("/courses/{course_id}/modules/{module_id}/lesson-effectiveness")
async def get_lesson_effectiveness(
    course_id: str,
    module_id: str,
    engine: ELearningAnalyticsEngine = Depends(get_engine),
):
    """Get lesson effectiveness analysis"""
    try:
        effectiveness = engine.get_lesson_effectiveness(course_id, module_id)
        
        if not effectiveness:
            raise HTTPException(status_code=404, detail="Course or module not found")
        
        return effectiveness
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting lesson effectiveness: {e}")
        raise HTTPException(status_code=500, detail="Failed to get lesson effectiveness")


# ============== STUDENT ENROLLMENT & PROGRESS ==============

@router.post("/students/enroll")
async def enroll_student(
    student_id: str,
    student_name: str,
    course_id: str,
    engine: ELearningAnalyticsEngine = Depends(get_engine),
):
    """Enroll student in course"""
    try:
        path = await engine.track_enrollment(
            student_id=student_id,
            student_name=student_name,
            course_id=course_id,
        )
        
        if not path:
            raise HTTPException(status_code=404, detail="Course not found")
        
        return {
            "success": True,
            "student_id": student_id,
            "student_name": student_name,
            "course_id": course_id,
            "enrolled_at": path.enrollment_date.isoformat(),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error enrolling student: {e}")
        raise HTTPException(status_code=500, detail="Failed to enroll student")


@router.get("/students/{student_id}/progress/{course_id}")
async def get_student_progress(
    student_id: str,
    course_id: str,
    engine: ELearningAnalyticsEngine = Depends(get_engine),
):
    """Get student progress in course"""
    try:
        progress = engine.get_student_progress(student_id, course_id)
        
        if not progress:
            raise HTTPException(status_code=404, detail="Student or course not found")
        
        return {
            "student_id": student_id,
            "student_name": progress.student_name,
            "course_id": course_id,
            "status": progress.status.value,
            "enrolled_date": progress.enrollment_date.isoformat(),
            "start_date": progress.start_date.isoformat() if progress.start_date else None,
            "completion_date": progress.completion_date.isoformat() if progress.completion_date else None,
            "lessons_started": progress.lessons_started,
            "lessons_completed": progress.lessons_completed,
            "total_study_hours": round(progress.total_study_hours, 2),
            "modules_completed": progress.modules_completed,
            "overall_progress": round(progress.overall_course_progress, 2),
            "quiz_attempts": progress.quiz_attempts,
            "quiz_passes": progress.quiz_passes,
            "avg_quiz_score": round(progress.avg_quiz_score, 2),
            "engagement_score": round(progress.engagement_score, 2),
            "dropout_risk": round(progress.dropout_risk, 2),
            "certificate_earned": progress.certificate_earned,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting student progress: {e}")
        raise HTTPException(status_code=500, detail="Failed to get student progress")


# ============== LESSON TRACKING ==============

@router.post("/lessons/{lesson_id}/start")
async def track_lesson_start(
    student_id: str,
    course_id: str,
    lesson_id: str,
    engine: ELearningAnalyticsEngine = Depends(get_engine),
):
    """Track lesson start"""
    try:
        success = await engine.track_lesson_start(
            student_id=student_id,
            course_id=course_id,
            lesson_id=lesson_id,
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Student or course not found")
        
        return {
            "success": True,
            "lesson_id": lesson_id,
            "started_at": datetime.utcnow().isoformat(),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error tracking lesson start: {e}")
        raise HTTPException(status_code=500, detail="Failed to track lesson start")


@router.post("/lessons/{lesson_id}/complete")
async def track_lesson_completion(
    student_id: str,
    course_id: str,
    lesson_id: str,
    watch_time_minutes: float,
    engagement_score: float = 0.0,
    notes_count: int = 0,
    engine: ELearningAnalyticsEngine = Depends(get_engine),
):
    """Track lesson completion"""
    try:
        success = await engine.track_lesson_completion(
            student_id=student_id,
            course_id=course_id,
            lesson_id=lesson_id,
            watch_time_minutes=watch_time_minutes,
            engagement_score=engagement_score,
            notes_count=notes_count,
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Student, course, or lesson not found")
        
        return {
            "success": True,
            "lesson_id": lesson_id,
            "watch_time_minutes": watch_time_minutes,
            "engagement_score": engagement_score,
            "completed_at": datetime.utcnow().isoformat(),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error tracking lesson completion: {e}")
        raise HTTPException(status_code=500, detail="Failed to track lesson completion")


# ============== QUIZ TRACKING ==============

@router.post("/quizzes/{quiz_id}/attempt")
async def track_quiz_attempt(
    student_id: str,
    course_id: str,
    quiz_id: str,
    score: float,
    max_score: float = 100.0,
    time_minutes: float = 0.0,
    passed: bool = False,
    engine: ELearningAnalyticsEngine = Depends(get_engine),
):
    """Track quiz attempt"""
    try:
        success = await engine.track_quiz_attempt(
            student_id=student_id,
            course_id=course_id,
            quiz_id=quiz_id,
            score=score,
            max_score=max_score,
            time_minutes=time_minutes,
            passed=passed,
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Student or course not found")
        
        return {
            "success": True,
            "quiz_id": quiz_id,
            "score": round(score, 2),
            "max_score": max_score,
            "percentage": round(score / max_score * 100, 2) if max_score > 0 else 0,
            "passed": passed,
            "time_minutes": time_minutes,
            "attempted_at": datetime.utcnow().isoformat(),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error tracking quiz attempt: {e}")
        raise HTTPException(status_code=500, detail="Failed to track quiz attempt")


@router.get("/courses/{course_id}/quiz-performance")
async def get_quiz_performance_analysis(
    course_id: str,
    engine: ELearningAnalyticsEngine = Depends(get_engine),
):
    """Get quiz performance analysis"""
    try:
        analysis = engine.get_quiz_performance_analysis(course_id)
        
        if not analysis:
            raise HTTPException(status_code=404, detail="Course not found")
        
        return analysis
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting quiz performance: {e}")
        raise HTTPException(status_code=500, detail="Failed to get quiz performance")


# ============== COURSE COMPLETION & CERTIFICATION ==============

@router.post("/courses/{course_id}/complete")
async def complete_course(
    student_id: str,
    course_id: str,
    final_score: float,
    engine: ELearningAnalyticsEngine = Depends(get_engine),
):
    """Complete course and issue certificate"""
    try:
        certificate = await engine.track_course_completion(
            student_id=student_id,
            course_id=course_id,
            final_score=final_score,
        )
        
        if not certificate:
            raise HTTPException(status_code=404, detail="Student or course not found")
        
        return {
            "success": True,
            "student_id": student_id,
            "course_id": course_id,
            "final_score": round(final_score, 2),
            "certificate_id": certificate.certificate_id,
            "certificate_issued": True,
            "verification_code": certificate.verification_code,
            "issued_at": certificate.issued_date.isoformat(),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error completing course: {e}")
        raise HTTPException(status_code=500, detail="Failed to complete course")


@router.get("/certificates/{certificate_id}")
async def get_certificate(
    certificate_id: str,
    engine: ELearningAnalyticsEngine = Depends(get_engine),
):
    """Get certificate details"""
    try:
        cert = next((c for c in engine.certificates if c.certificate_id == certificate_id), None)
        
        if not cert:
            raise HTTPException(status_code=404, detail="Certificate not found")
        
        return {
            "certificate_id": cert.certificate_id,
            "student_id": cert.student_id,
            "student_name": cert.student_name,
            "course_id": cert.course_id,
            "course_name": cert.course_name,
            "issued_date": cert.issued_date.isoformat(),
            "verification_code": cert.verification_code,
            "credential_url": cert.credential_url,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting certificate: {e}")
        raise HTTPException(status_code=500, detail="Failed to get certificate")


# ============== PLATFORM ANALYTICS ==============

@router.get("/platform")
async def get_platform_analytics(
    engine: ELearningAnalyticsEngine = Depends(get_engine),
):
    """Get platform-wide E-Learning analytics"""
    try:
        stats = engine.get_platform_analytics()
        
        return {
            "total_courses": stats.total_courses,
            "published_courses": stats.published_courses,
            "total_instructors": stats.total_instructors,
            "total_students": stats.total_students,
            "active_students_today": stats.active_students_today,
            "total_enrollments": stats.total_enrollments,
            "total_student_hours": round(stats.total_student_hours, 2),
            "total_lessons_completed": stats.total_lessons_completed,
            "avg_course_completion_rate": round(stats.avg_course_completion_rate, 2),
            "total_quiz_attempts": stats.total_quiz_attempts,
            "avg_quiz_score": round(stats.avg_quiz_score, 2),
            "overall_passing_rate": round(stats.overall_passing_rate, 2),
            "total_certificates_issued": stats.total_certificates_issued,
            "certificates_this_month": stats.certificates_this_month,
            "platform_rating": round(stats.platform_rating, 2),
            "student_satisfaction": round(stats.student_satisfaction, 2),
            "retention_rate": round(stats.retention_rate, 2),
            "growth_rate_percent": round(stats.growth_rate_percent, 2),
        }
    except Exception as e:
        logger.error(f"Error getting platform analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get platform analytics")


@router.get("/courses/trending")
async def get_trending_courses(
    limit: int = Query(10, ge=1, le=50),
    engine: ELearningAnalyticsEngine = Depends(get_engine),
):
    """Get trending courses"""
    try:
        trending = engine.get_trending_courses(limit)
        return {"trending_courses": trending}
    except Exception as e:
        logger.error(f"Error getting trending courses: {e}")
        raise HTTPException(status_code=500, detail="Failed to get trending courses")


@router.get("/courses/{course_id}/top-performers")
async def get_top_performers(
    course_id: str,
    limit: int = Query(10, ge=1, le=50),
    engine: ELearningAnalyticsEngine = Depends(get_engine),
):
    """Get top performing students in course"""
    try:
        performers = engine.get_top_performers(course_id, limit)
        
        return {
            "course_id": course_id,
            "top_performers": [
                {
                    "student_id": p.student_id,
                    "student_name": p.student_name,
                    "avg_quiz_score": round(p.avg_quiz_score, 2),
                    "overall_progress": round(p.overall_course_progress, 2),
                    "engagement_score": round(p.engagement_score, 2),
                }
                for p in performers
            ],
        }
    except Exception as e:
        logger.error(f"Error getting top performers: {e}")
        raise HTTPException(status_code=500, detail="Failed to get top performers")


@router.get("/courses/{course_id}/at-risk-students")
async def get_at_risk_students(
    course_id: str,
    risk_threshold: float = Query(0.6, ge=0.0, le=1.0),
    engine: ELearningAnalyticsEngine = Depends(get_engine),
):
    """Get students at risk of dropping out"""
    try:
        at_risk = engine.get_at_risk_students(course_id, risk_threshold)
        
        return {
            "course_id": course_id,
            "risk_threshold": risk_threshold,
            "at_risk_count": len(at_risk),
            "at_risk_students": [
                {
                    "student_id": s.student_id,
                    "student_name": s.student_name,
                    "progress": round(s.overall_course_progress, 2),
                    "dropout_risk": round(s.dropout_risk, 2),
                    "last_activity": s.last_activity_date.isoformat() if s.last_activity_date else None,
                }
                for s in at_risk
            ],
        }
    except Exception as e:
        logger.error(f"Error getting at-risk students: {e}")
        raise HTTPException(status_code=500, detail="Failed to get at-risk students")


@router.get("/courses/{course_id}/engagement-trends")
async def get_engagement_trends(
    course_id: str,
    days: int = Query(30, ge=1, le=365),
    engine: ELearningAnalyticsEngine = Depends(get_engine),
):
    """Get engagement trends"""
    try:
        trends = engine.get_engagement_trends(course_id, days)
        
        if not trends:
            raise HTTPException(status_code=404, detail="Course not found")
        
        return trends
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting engagement trends: {e}")
        raise HTTPException(status_code=500, detail="Failed to get engagement trends")
