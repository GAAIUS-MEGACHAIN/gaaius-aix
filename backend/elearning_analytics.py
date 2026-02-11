"""
E-LEARNING ANALYTICS MODULE
================================================================================
Complete analytics for E-Learning platform:
- Course creation and performance
- Student enrollment and progress
- Module and lesson tracking
- Quiz performance analysis
- Student learning paths
- Certificate tracking
- Engagement metrics
- Performance insights

Production-Ready | Enterprise Grade
================================================================================
"""

from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict, deque
import statistics
import logging

logger = logging.getLogger(__name__)


# ============== ENUMS ==============

class CourseLevel(str, Enum):
    """Course difficulty levels"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class CourseStatus(str, Enum):
    """Course status"""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class StudentProgressStatus(str, Enum):
    """Student progress in course"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class QuizType(str, Enum):
    """Types of quizzes"""
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    SHORT_ANSWER = "short_answer"
    ESSAY = "essay"
    PRACTICAL = "practical"


class LessonType(str, Enum):
    """Types of lessons"""
    VIDEO = "video"
    TEXT = "text"
    INTERACTIVE = "interactive"
    ASSIGNMENT = "assignment"
    QUIZ = "quiz"
    LIVE_CLASS = "live_class"


# ============== DATA MODELS ==============

@dataclass
class QuizMetrics:
    """Quiz performance metrics"""
    total_attempts: int = 0
    total_submitted: int = 0
    avg_score: float = 0.0
    highest_score: float = 0.0
    lowest_score: float = 0.0
    passing_rate: float = 0.0  # % of attempts that passed
    median_score: float = 0.0
    time_to_complete: List[float] = field(default_factory=list)  # seconds
    avg_time_minutes: float = 0.0
    most_difficult_questions: List[str] = field(default_factory=list)
    question_confusion_index: Dict[str, float] = field(default_factory=dict)  # Question ID -> confusion %
    attempt_analysis: Dict[str, int] = field(default_factory=dict)  # Attempt # -> count


@dataclass
class LessonMetrics:
    """Lesson engagement metrics"""
    lesson_id: str
    lesson_type: LessonType
    title: str
    total_views: int = 0
    total_starts: int = 0
    completion_rate: float = 0.0  # %
    avg_watch_time_seconds: float = 0.0
    total_watch_time_hours: float = 0.0
    engagement_score: float = 0.0  # 0-100
    avg_rating: float = 0.0
    bounce_rate: float = 0.0  # % who started but didn't finish
    replays: int = 0
    notes_taken: int = 0
    questions_asked: int = 0
    completion_times: List[float] = field(default_factory=list)  # List of completion times


@dataclass
class ModuleMetrics:
    """Module (collection of lessons) metrics"""
    module_id: str
    module_name: str
    total_lessons: int = 0
    lessons_completed_avg: float = 0.0
    module_completion_rate: float = 0.0  # % of students who completed all lessons
    avg_module_time_hours: float = 0.0
    total_student_hours: float = 0.0
    engagement_score: float = 0.0
    lesson_metrics: Dict[str, LessonMetrics] = field(default_factory=dict)


@dataclass
class StudentLearningPath:
    """Individual student's learning progress"""
    student_id: str
    student_name: str
    course_id: str
    enrollment_date: datetime = field(default_factory=datetime.now)
    start_date: Optional[datetime] = None
    completion_date: Optional[datetime] = None
    status: StudentProgressStatus = StudentProgressStatus.NOT_STARTED
    
    # Progress metrics
    lessons_started: int = 0
    lessons_completed: int = 0
    total_study_hours: float = 0.0
    modules_completed: int = 0
    last_activity_date: Optional[datetime] = None
    
    # Quiz metrics
    quiz_attempts: int = 0
    quiz_passes: int = 0
    avg_quiz_score: float = 0.0
    
    # Learning metrics
    engagement_score: float = 0.0
    learning_velocity: float = 0.0  # lessons/day
    consistency_score: float = 0.0  # 0-100 (based on study pattern)
    dropout_risk: float = 0.0  # 0-100 (higher = higher risk)
    
    # Certification
    certificate_earned: bool = False
    certificate_date: Optional[datetime] = None
    certificate_id: Optional[str] = None
    
    # Performance
    overall_course_progress: float = 0.0  # %
    lesson_progress: Dict[str, float] = field(default_factory=dict)  # Lesson ID -> %
    quiz_progress: Dict[str, float] = field(default_factory=dict)  # Quiz ID -> score


@dataclass
class CourseMetrics:
    """Complete course analytics"""
    course_id: str
    course_name: str
    instructor_id: str
    course_level: CourseLevel = CourseLevel.BEGINNER
    status: CourseStatus = CourseStatus.DRAFT
    created_date: datetime = field(default_factory=datetime.now)
    published_date: Optional[datetime] = None
    
    # Content metrics
    total_modules: int = 0
    total_lessons: int = 0
    total_quizzes: int = 0
    total_assignments: int = 0
    total_duration_hours: float = 0.0
    avg_lesson_duration_minutes: float = 0.0
    
    # Enrollment metrics
    total_enrolled: int = 0
    total_active_students: int = 0
    new_enrollments_this_week: int = 0
    new_enrollments_this_month: int = 0
    
    # Progress metrics
    completion_rate: float = 0.0  # % of enrolled students who completed
    avg_completion_time_hours: float = 0.0
    median_completion_time_hours: float = 0.0
    dropout_count: int = 0
    dropout_rate: float = 0.0
    
    # Performance metrics
    avg_course_rating: float = 0.0
    student_satisfaction: float = 0.0
    avg_student_score: float = 0.0
    passing_rate: float = 0.0
    
    # Engagement metrics
    avg_engagement_score: float = 0.0
    total_student_hours: float = 0.0
    avg_study_hours_per_student: float = 0.0
    
    # Module breakdown
    module_metrics: Dict[str, ModuleMetrics] = field(default_factory=dict)
    
    # Student tracking
    student_progress: Dict[str, StudentLearningPath] = field(default_factory=dict)
    
    # Recent activity
    recent_enrollments: List[str] = field(default_factory=list)
    recent_completions: List[str] = field(default_factory=list)
    at_risk_students: List[str] = field(default_factory=list)


@dataclass
class ELearningPlatformStats:
    """Overall platform statistics"""
    total_courses: int = 0
    published_courses: int = 0
    total_instructors: int = 0
    total_students: int = 0
    active_students_today: int = 0
    total_enrollments: int = 0
    
    # Learning metrics
    total_student_hours: float = 0.0
    avg_student_hours_per_month: float = 0.0
    total_lessons_completed: int = 0
    avg_course_completion_rate: float = 0.0
    
    # Quiz metrics
    total_quiz_attempts: int = 0
    avg_quiz_score: float = 0.0
    overall_passing_rate: float = 0.0
    
    # Certification
    total_certificates_issued: int = 0
    certificates_this_month: int = 0
    
    # Performance
    platform_rating: float = 0.0
    student_satisfaction: float = 0.0
    
    # Growth
    growth_rate_percent: float = 0.0
    retention_rate: float = 0.0
    
    # Popular content
    most_popular_course_id: Optional[str] = None
    most_completed_course_id: Optional[str] = None
    trending_courses: List[str] = field(default_factory=list)


@dataclass
class StudentCertificate:
    """Student certificate record"""
    certificate_id: str
    student_id: str
    student_name: str
    course_id: str
    course_name: str
    issued_date: datetime = field(default_factory=datetime.now)
    expiry_date: Optional[datetime] = None
    skill_badges: List[str] = field(default_factory=list)
    verification_code: str = ""
    credential_url: str = ""


# ============== ANALYTICS ENGINE ==============

class ELearningAnalyticsEngine:
    """Complete E-Learning analytics engine"""
    
    def __init__(self, max_history_days: int = 365):
        """
        Initialize analytics engine
        
        Args:
            max_history_days: Days of history to keep
        """
        self.max_history_days = max_history_days
        self.courses: Dict[str, CourseMetrics] = {}
        self.platform_stats = ELearningPlatformStats()
        self.student_paths: Dict[str, StudentLearningPath] = {}
        self.certificates: List[StudentCertificate] = []
        logger.info("E-Learning Analytics Engine initialized")
    
    # ============== COURSE ANALYTICS ==============
    
    async def track_course_creation(
        self,
        course_id: str,
        course_name: str,
        instructor_id: str,
        level: CourseLevel = CourseLevel.BEGINNER,
    ) -> CourseMetrics:
        """Track new course creation"""
        course = CourseMetrics(
            course_id=course_id,
            course_name=course_name,
            instructor_id=instructor_id,
            course_level=level,
        )
        self.courses[course_id] = course
        self.platform_stats.total_courses += 1
        logger.info(f"Course created: {course_name} (ID: {course_id})")
        return course
    
    async def track_course_publish(self, course_id: str) -> bool:
        """Track course publication"""
        if course_id not in self.courses:
            return False
        
        course = self.courses[course_id]
        course.status = CourseStatus.PUBLISHED
        course.published_date = datetime.now(timezone.utc)
        self.platform_stats.published_courses += 1
        logger.info(f"Course published: {course.course_name}")
        return True
    
    async def add_module(
        self,
        course_id: str,
        module_id: str,
        module_name: str,
        lesson_count: int = 0,
    ) -> bool:
        """Add module to course"""
        if course_id not in self.courses:
            return False
        
        course = self.courses[course_id]
        module = ModuleMetrics(
            module_id=module_id,
            module_name=module_name,
            total_lessons=lesson_count,
        )
        course.module_metrics[module_id] = module
        course.total_modules += 1
        logger.info(f"Module added to {course.course_name}: {module_name}")
        return True
    
    async def add_lesson(
        self,
        course_id: str,
        module_id: str,
        lesson_id: str,
        lesson_type: LessonType,
        title: str,
        duration_minutes: float = 0.0,
    ) -> bool:
        """Add lesson to module"""
        if course_id not in self.courses or module_id not in self.courses[course_id].module_metrics:
            return False
        
        course = self.courses[course_id]
        module = course.module_metrics[module_id]
        
        lesson = LessonMetrics(
            lesson_id=lesson_id,
            lesson_type=lesson_type,
            title=title,
        )
        module.lesson_metrics[lesson_id] = lesson
        course.total_lessons += 1
        course.total_duration_hours += duration_minutes / 60
        
        logger.info(f"Lesson added: {title} to {module.module_name}")
        return True
    
    # ============== STUDENT ENROLLMENT ==============
    
    async def track_enrollment(
        self,
        student_id: str,
        student_name: str,
        course_id: str,
    ) -> Optional[StudentLearningPath]:
        """Track student enrollment in course"""
        if course_id not in self.courses:
            return None
        
        course = self.courses[course_id]
        
        # Create learning path
        path = StudentLearningPath(
            student_id=student_id,
            student_name=student_name,
            course_id=course_id,
        )
        
        self.student_paths[f"{student_id}_{course_id}"] = path
        course.student_progress[student_id] = path
        course.total_enrolled += 1
        course.total_active_students += 1
        course.recent_enrollments.append(student_id)
        
        self.platform_stats.total_students += 1
        self.platform_stats.total_enrollments += 1
        
        logger.info(f"Student {student_name} enrolled in {course.course_name}")
        return path
    
    # ============== LESSON TRACKING ==============
    
    async def track_lesson_start(
        self,
        student_id: str,
        course_id: str,
        lesson_id: str,
    ) -> bool:
        """Track when student starts lesson"""
        path_key = f"{student_id}_{course_id}"
        if path_key not in self.student_paths:
            return False
        
        path = self.student_paths[path_key]
        path.lessons_started += 1
        path.last_activity_date = datetime.now(timezone.utc)
        path.status = StudentProgressStatus.IN_PROGRESS
        
        if path.start_date is None:
            path.start_date = datetime.now(timezone.utc)
        
        return True
    
    async def track_lesson_completion(
        self,
        student_id: str,
        course_id: str,
        lesson_id: str,
        watch_time_minutes: float,
        engagement_score: float = 0.0,
        notes_count: int = 0,
    ) -> bool:
        """Track lesson completion"""
        path_key = f"{student_id}_{course_id}"
        if path_key not in self.student_paths:
            return False
        
        path = self.student_paths[path_key]
        course = self.courses[course_id]
        
        # Find lesson
        lesson = None
        for module in course.module_metrics.values():
            if lesson_id in module.lesson_metrics:
                lesson = module.lesson_metrics[lesson_id]
                break
        
        if lesson is None:
            return False
        
        # Update student path
        path.lessons_completed += 1
        path.total_study_hours += watch_time_minutes / 60
        path.engagement_score = (path.engagement_score + engagement_score) / 2
        path.last_activity_date = datetime.now(timezone.utc)
        
        # Update lesson metrics
        lesson.total_views += 1
        lesson.completion_rate = (path.lessons_completed / path.lessons_started * 100) if path.lessons_started > 0 else 0
        lesson.avg_watch_time_seconds = (lesson.avg_watch_time_seconds + watch_time_minutes * 60) / 2
        lesson.total_watch_time_hours += watch_time_minutes / 60
        lesson.engagement_score = engagement_score
        lesson.notes_taken += notes_count
        lesson.completion_times.append(watch_time_minutes)
        
        # Update platform stats
        self.platform_stats.total_lessons_completed += 1
        self.platform_stats.total_student_hours += watch_time_minutes / 60
        
        logger.info(f"Lesson {lesson_id} completed by {student_id}")
        return True
    
    # ============== QUIZ TRACKING ==============
    
    async def track_quiz_attempt(
        self,
        student_id: str,
        course_id: str,
        quiz_id: str,
        score: float,
        max_score: float = 100.0,
        time_minutes: float = 0.0,
        passed: bool = False,
    ) -> bool:
        """Track quiz attempt"""
        path_key = f"{student_id}_{course_id}"
        if path_key not in self.student_paths:
            return False
        
        path = self.student_paths[path_key]
        course = self.courses[course_id]
        
        # Find quiz
        quiz = None
        for module in course.module_metrics.values():
            if quiz_id in module.lesson_metrics:
                lesson = module.lesson_metrics[quiz_id]
                if isinstance(lesson, LessonMetrics) and lesson.lesson_type == LessonType.QUIZ:
                    if not hasattr(lesson, 'quiz_metrics'):
                        lesson.quiz_metrics = QuizMetrics()
                    quiz = lesson.quiz_metrics
                    break
        
        # Update student path
        path.quiz_attempts += 1
        if passed:
            path.quiz_passes += 1
        path.avg_quiz_score = (path.avg_quiz_score + score) / 2
        
        # Update platform stats
        self.platform_stats.total_quiz_attempts += 1
        self.platform_stats.avg_quiz_score = (self.platform_stats.avg_quiz_score + score) / 2
        
        logger.info(f"Quiz {quiz_id} attempted by {student_id} - Score: {score}/{max_score}")
        return True
    
    # ============== MODULE COMPLETION ==============
    
    async def track_module_completion(
        self,
        student_id: str,
        course_id: str,
        module_id: str,
    ) -> bool:
        """Track module completion"""
        path_key = f"{student_id}_{course_id}"
        if path_key not in self.student_paths:
            return False
        
        path = self.student_paths[path_key]
        course = self.courses[course_id]
        
        if module_id not in course.module_metrics:
            return False
        
        path.modules_completed += 1
        
        # Update progress
        total_progress = (path.modules_completed / course.total_modules * 100) if course.total_modules > 0 else 0
        path.overall_course_progress = min(100.0, total_progress)
        
        logger.info(f"Module {module_id} completed by {student_id}")
        return True
    
    # ============== COURSE COMPLETION & CERTIFICATION ==============
    
    async def track_course_completion(
        self,
        student_id: str,
        course_id: str,
        final_score: float,
    ) -> Optional[StudentCertificate]:
        """Track course completion and issue certificate"""
        path_key = f"{student_id}_{course_id}"
        if path_key not in self.student_paths:
            return None
        
        path = self.student_paths[path_key]
        course = self.courses[course_id]
        
        path.completion_date = datetime.now(timezone.utc)
        path.status = StudentProgressStatus.COMPLETED
        path.overall_course_progress = 100.0
        
        # Update course metrics
        course.total_active_students -= 1
        course.recent_completions.append(student_id)
        course.completion_rate = (len(course.recent_completions) / course.total_enrolled * 100) if course.total_enrolled > 0 else 0
        
        # Calculate completion time
        if path.start_date:
            completion_hours = (path.completion_date - path.start_date).total_seconds() / 3600
            course.avg_completion_time_hours = (course.avg_completion_time_hours + completion_hours) / 2
        
        # Issue certificate
        import uuid
        cert_id = str(uuid.uuid4())
        certificate = StudentCertificate(
            certificate_id=cert_id,
            student_id=student_id,
            student_name=path.student_name,
            course_id=course_id,
            course_name=course.course_name,
            verification_code=str(uuid.uuid4())[:8].upper(),
        )
        
        path.certificate_earned = True
        path.certificate_date = datetime.now(timezone.utc)
        path.certificate_id = cert_id
        
        self.certificates.append(certificate)
        self.platform_stats.total_certificates_issued += 1
        self.platform_stats.certificates_this_month += 1
        
        logger.info(f"Certificate issued to {path.student_name} for {course.course_name}")
        return certificate
    
    # ============== ANALYTICS QUERIES ==============
    
    def get_course_analytics(self, course_id: str) -> Optional[CourseMetrics]:
        """Get complete analytics for a course"""
        return self.courses.get(course_id)
    
    def get_student_progress(self, student_id: str, course_id: str) -> Optional[StudentLearningPath]:
        """Get student progress in course"""
        path_key = f"{student_id}_{course_id}"
        return self.student_paths.get(path_key)
    
    def get_at_risk_students(self, course_id: str, risk_threshold: float = 0.6) -> List[StudentLearningPath]:
        """Get students at risk of dropping out"""
        if course_id not in self.courses:
            return []
        
        course = self.courses[course_id]
        at_risk = [
            path for path in course.student_progress.values()
            if path.dropout_risk > risk_threshold * 100
        ]
        return at_risk
    
    def get_course_completion_analysis(self, course_id: str) -> Dict[str, Any]:
        """Get detailed completion analysis"""
        if course_id not in self.courses:
            return {}
        
        course = self.courses[course_id]
        completed = [p for p in course.student_progress.values() if p.status == StudentProgressStatus.COMPLETED]
        abandoned = [p for p in course.student_progress.values() if p.status == StudentProgressStatus.ABANDONED]
        in_progress = [p for p in course.student_progress.values() if p.status == StudentProgressStatus.IN_PROGRESS]
        
        return {
            "total_enrolled": course.total_enrolled,
            "completed": len(completed),
            "in_progress": len(in_progress),
            "abandoned": len(abandoned),
            "completion_rate": course.completion_rate,
            "dropout_rate": course.dropout_rate,
            "avg_completion_time_hours": course.avg_completion_time_hours,
            "avg_student_satisfaction": course.student_satisfaction,
        }
    
    def get_lesson_effectiveness(self, course_id: str, module_id: str) -> Dict[str, Any]:
        """Analyze lesson effectiveness"""
        if course_id not in self.courses or module_id not in self.courses[course_id].module_metrics:
            return {}
        
        module = self.courses[course_id].module_metrics[module_id]
        lessons_stats = []
        
        for lesson_id, lesson in module.lesson_metrics.items():
            lessons_stats.append({
                "lesson_id": lesson_id,
                "title": lesson.title,
                "completion_rate": lesson.completion_rate,
                "engagement_score": lesson.engagement_score,
                "avg_watch_time_minutes": lesson.avg_watch_time_seconds / 60,
                "bounce_rate": lesson.bounce_rate,
                "rating": lesson.avg_rating,
            })
        
        return {
            "module_id": module_id,
            "module_name": module.module_name,
            "lessons": lessons_stats,
            "module_completion_rate": module.module_completion_rate,
            "avg_module_time_hours": module.avg_module_time_hours,
        }
    
    def get_quiz_performance_analysis(self, course_id: str) -> Dict[str, Any]:
        """Analyze quiz performance across course"""
        if course_id not in self.courses:
            return {}
        
        course = self.courses[course_id]
        quizzes_data = []
        
        for module in course.module_metrics.values():
            for lesson_id, lesson in module.lesson_metrics.items():
                if lesson.lesson_type == LessonType.QUIZ and hasattr(lesson, 'quiz_metrics'):
                    quiz = lesson.quiz_metrics
                    quizzes_data.append({
                        "quiz_id": lesson_id,
                        "title": lesson.title,
                        "avg_score": quiz.avg_score,
                        "passing_rate": quiz.passing_rate,
                        "attempts": quiz.total_attempts,
                        "time_to_complete_minutes": quiz.avg_time_minutes,
                    })
        
        return {
            "course_id": course_id,
            "total_quizzes": len(quizzes_data),
            "quizzes": quizzes_data,
            "overall_avg_score": course.avg_student_score,
            "overall_passing_rate": course.passing_rate,
        }
    
    def get_platform_analytics(self) -> ELearningPlatformStats:
        """Get platform-wide analytics"""
        # Calculate aggregate stats
        if self.courses:
            self.platform_stats.avg_course_completion_rate = statistics.mean(
                [c.completion_rate for c in self.courses.values()]
            )
        
        if self.certificates:
            self.platform_stats.total_certificates_issued = len(self.certificates)
        
        return self.platform_stats
    
    def get_trending_courses(self, limit: int = 10) -> List[str]:
        """Get trending courses by enrollment"""
        sorted_courses = sorted(
            self.courses.items(),
            key=lambda x: x[1].total_enrolled,
            reverse=True,
        )
        return [course_id for course_id, _ in sorted_courses[:limit]]
    
    def get_top_performers(self, course_id: str, limit: int = 10) -> List[StudentLearningPath]:
        """Get top performing students"""
        if course_id not in self.courses:
            return []
        
        course = self.courses[course_id]
        sorted_students = sorted(
            course.student_progress.values(),
            key=lambda x: x.avg_quiz_score,
            reverse=True,
        )
        return sorted_students[:limit]
    
    def get_engagement_trends(self, course_id: str, days: int = 30) -> Dict[str, Any]:
        """Get engagement trends over time"""
        if course_id not in self.courses:
            return {}
        
        course = self.courses[course_id]
        return {
            "course_id": course_id,
            "total_engagement_score": course.avg_engagement_score,
            "total_student_hours": course.total_student_hours,
            "active_students": course.total_active_students,
            "new_enrollments": course.new_enrollments_this_month,
        }


# ============== SINGLETON INSTANCE ==============

_elearning_analytics_engine: Optional[ELearningAnalyticsEngine] = None


def initialize_elearning_analytics() -> ELearningAnalyticsEngine:
    """Initialize E-Learning analytics engine"""
    global _elearning_analytics_engine
    if _elearning_analytics_engine is None:
        _elearning_analytics_engine = ELearningAnalyticsEngine()
    return _elearning_analytics_engine


def get_elearning_analytics_engine() -> Optional[ELearningAnalyticsEngine]:
    """Get E-Learning analytics engine"""
    return _elearning_analytics_engine
