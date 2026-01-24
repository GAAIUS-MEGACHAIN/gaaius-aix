"""
E-Learning Platform Service - Complete Production Implementation
Advanced course management with certificates, progress tracking, and instructor payouts
"""

from typing import List, Optional, Dict, Any, Set, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from enum import Enum
import uuid
import json
from abc import ABC, abstractmethod

from pydantic import BaseModel, Field, validator

# ============================================================================
# ENUMS & CONSTANTS
# ============================================================================

class CourseLevel(str, Enum):
    """Difficulty levels"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class CourseStatus(str, Enum):
    """Course publication status"""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    SUSPENDED = "suspended"

class LessonStatus(str, Enum):
    """Lesson status"""
    DRAFT = "draft"
    PUBLISHED = "published"
    LOCKED = "locked"

class QuizType(str, Enum):
    """Quiz question types"""
    MULTIPLE_CHOICE = "multiple_choice"
    SHORT_ANSWER = "short_answer"
    ESSAY = "essay"
    PRACTICAL = "practical"
    TRUE_FALSE = "true_false"

class CertificateStatus(str, Enum):
    """Certificate status"""
    EARNED = "earned"
    REVOKED = "revoked"
    PENDING = "pending"

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class CourseMetadata(BaseModel):
    """Course metadata"""
    title: str = Field(..., min_length=5, max_length=255)
    description: str = Field(..., min_length=20, max_length=5000)
    instructor: str = Field(..., min_length=2, max_length=255)
    category: str = Field(..., regex="^[a-z-]+$")
    level: CourseLevel = CourseLevel.BEGINNER
    price: float = Field(default=0.0, ge=0, le=999.99)
    thumbnail_url: Optional[str] = None
    preview_video_url: Optional[str] = None
    language: str = Field(default="en", regex="^[a-z]{2}(-[A-Z]{2})?$")
    tags: List[str] = Field(default_factory=list, max_items=10)
    prerequisites: List[str] = Field(default_factory=list, max_items=5)
    
    @validator('title')
    def validate_title(cls, v):
        if not v.strip():
            raise ValueError("Title cannot be empty")
        return v.strip()

class Lesson(BaseModel):
    """Course lesson"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    course_id: str
    title: str = Field(..., min_length=3, max_length=255)
    description: str = Field(..., min_length=10)
    content: str = Field(...)  # Markdown content
    lesson_number: int = Field(..., gt=0)
    section_id: str = ""
    duration_minutes: int = Field(..., gt=0, le=480)  # Max 8 hours
    video_url: Optional[str] = None
    resources: List[Dict[str, str]] = Field(default_factory=list)  # Download links
    status: LessonStatus = LessonStatus.DRAFT
    locked: bool = True
    requires_lesson_id: Optional[str] = None  # Prerequisite lesson
    completion_required: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

class QuizQuestion(BaseModel):
    """Quiz question model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    quiz_id: str
    question: str = Field(..., min_length=10)
    question_type: QuizType
    points: int = Field(default=1, gt=0, le=100)
    options: List[str] = Field(default_factory=list, max_items=10)  # For multiple choice
    correct_answer: str = ""  # Index or text
    explanation: Optional[str] = None
    order: int = Field(default=0, ge=0)

class Quiz(BaseModel):
    """Lesson quiz"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    lesson_id: str
    title: str = Field(..., min_length=3, max_length=255)
    description: Optional[str] = None
    questions: List[QuizQuestion] = Field(default_factory=list)
    passing_score: int = Field(default=70, ge=0, le=100)
    time_limit_minutes: Optional[int] = Field(None, gt=0, le=480)
    attempts_allowed: int = Field(default=3, gt=0, le=100)
    show_answers_after: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Assignment(BaseModel):
    """Course assignment"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    lesson_id: str
    title: str = Field(..., min_length=3, max_length=255)
    description: str = Field(..., min_length=20)
    instructions: str = Field(...)
    due_date: Optional[datetime] = None
    max_score: int = Field(default=100, gt=0, le=1000)
    rubric: Dict[str, Any] = Field(default_factory=dict)  # Grading criteria
    allow_late_submission: bool = True
    late_penalty_percent: int = Field(default=10, ge=0, le=100)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Certificate(BaseModel):
    """Course completion certificate"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    course_id: str
    instructor: str
    course_title: str
    issued_date: datetime = Field(default_factory=datetime.utcnow)
    expires_date: Optional[datetime] = None
    status: CertificateStatus = CertificateStatus.EARNED
    verification_code: str = Field(default_factory=lambda: str(uuid.uuid4()))
    credential_url: Optional[str] = None

class Progress(BaseModel):
    """Student progress tracking"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    course_id: str
    lessons_completed: int = 0
    lessons_total: int = 0
    completion_percentage: float = Field(default=0.0, ge=0, le=100)
    last_accessed: datetime = Field(default_factory=datetime.utcnow)
    time_spent_minutes: int = 0
    quiz_scores: Dict[str, float] = Field(default_factory=dict)  # quiz_id -> score
    assignment_grades: Dict[str, float] = Field(default_factory=dict)  # assignment_id -> grade
    average_score: float = Field(default=0.0, ge=0, le=100)
    status: str = "in_progress"  # in_progress, completed, dropped
    enrolled_date: datetime = Field(default_factory=datetime.utcnow)
    completed_date: Optional[datetime] = None

class Enrollment(BaseModel):
    """Course enrollment"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    course_id: str
    enrolled_date: datetime = Field(default_factory=datetime.utcnow)
    payment_method: Optional[str] = None
    amount_paid: float = 0.0
    completion_date: Optional[datetime] = None
    status: str = "active"  # active, completed, dropped, suspended

class CourseReview(BaseModel):
    """Course review and rating"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    course_id: str
    user_id: str
    rating: int = Field(..., ge=1, le=5)
    review_text: Optional[str] = Field(None, max_length=2000)
    helpful_count: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)

# ============================================================================
# DATACLASSES
# ============================================================================

@dataclass
class Course:
    """Internal course representation"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    instructor_id: str = ""
    metadata: CourseMetadata = field(default_factory=dict)
    lessons: List[Lesson] = field(default_factory=list)
    sections: Dict[str, str] = field(default_factory=dict)  # section_id -> title
    status: CourseStatus = CourseStatus.DRAFT
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    student_count: int = 0
    average_rating: float = 0.0
    total_reviews: int = 0

# ============================================================================
# GRADING ENGINE
# ============================================================================

class GradingEngine:
    """Advanced grading and scoring system"""
    
    @staticmethod
    def calculate_quiz_score(answers: Dict[str, str], quiz: Quiz) -> Tuple[float, Dict[str, bool]]:
        """
        Calculate quiz score with detailed feedback
        
        Returns:
            (score_percent, question_results)
        """
        total_points = sum(q.points for q in quiz.questions)
        earned_points = 0
        question_results = {}
        
        for question in quiz.questions:
            user_answer = answers.get(question.id, "")
            is_correct = user_answer.lower().strip() == question.correct_answer.lower().strip()
            question_results[question.id] = is_correct
            
            if is_correct:
                earned_points += question.points
        
        score_percent = (earned_points / total_points * 100) if total_points > 0 else 0
        return score_percent, question_results
    
    @staticmethod
    def calculate_assignment_grade(
        submission_score: float,
        rubric_scores: Dict[str, float],
        due_date: Optional[datetime] = None
    ) -> float:
        """Calculate assignment grade with late penalties"""
        base_grade = submission_score
        
        # Apply late penalty
        if due_date and datetime.utcnow() > due_date:
            days_late = (datetime.utcnow() - due_date).days
            if days_late > 0:
                penalty = min(30, days_late * 5)  # 5% per day, max 30%
                base_grade = base_grade * (1 - penalty / 100)
        
        # Apply rubric weighting
        if rubric_scores:
            weighted_grade = 0
            for criterion, weight in rubric_scores.items():
                weighted_grade += weight
            return min(100, base_grade * (weighted_grade / len(rubric_scores)))
        
        return min(100, base_grade)
    
    @staticmethod
    def calculate_course_grade(progress: Progress) -> float:
        """Calculate overall course grade"""
        grades = []
        
        # Quiz grades (40% weight)
        if progress.quiz_scores:
            quiz_avg = sum(progress.quiz_scores.values()) / len(progress.quiz_scores)
            grades.append(quiz_avg * 0.40)
        
        # Assignment grades (40% weight)
        if progress.assignment_grades:
            assignment_avg = sum(progress.assignment_grades.values()) / len(progress.assignment_grades)
            grades.append(assignment_avg * 0.40)
        
        # Completion (20% weight)
        if progress.lessons_total > 0:
            completion_score = (progress.lessons_completed / progress.lessons_total) * 100
            grades.append(completion_score * 0.20)
        
        return sum(grades) if grades else 0

# ============================================================================
# CERTIFICATE GENERATOR
# ============================================================================

class CertificateGenerator:
    """Certificate generation and verification"""
    
    @staticmethod
    def generate_certificate(
        user_id: str,
        course_id: str,
        course_title: str,
        instructor: str,
        expiry_days: int = 365
    ) -> Certificate:
        """Generate certificate"""
        expires = datetime.utcnow() + timedelta(days=expiry_days) if expiry_days > 0 else None
        
        return Certificate(
            user_id=user_id,
            course_id=course_id,
            course_title=course_title,
            instructor=instructor,
            issued_date=datetime.utcnow(),
            expires_date=expires,
            status=CertificateStatus.EARNED
        )
    
    @staticmethod
    def verify_certificate(certificate: Certificate, current_date: datetime = None) -> bool:
        """Verify certificate validity"""
        if certificate.status != CertificateStatus.EARNED:
            return False
        
        current = current_date or datetime.utcnow()
        
        if certificate.expires_date and current > certificate.expires_date:
            return False
        
        return True
    
    @staticmethod
    def generate_credential_url(certificate: Certificate, base_url: str) -> str:
        """Generate shareable certificate URL"""
        return f"{base_url}/verify/{certificate.verification_code}"

# ============================================================================
# CONTENT RECOMMENDATION ENGINE
# ============================================================================

class RecommendationEngine:
    """ML-powered course recommendations"""
    
    def __init__(self):
        self.enrollments: Dict[str, List[str]] = {}  # user_id -> [course_ids]
        self.user_preferences: Dict[str, Dict[str, float]] = {}  # user_id -> {category: score}
    
    async def track_user_interest(self, user_id: str, course_id: str, action: str, weight: float = 1.0):
        """Track user interaction with course"""
        if user_id not in self.enrollments:
            self.enrollments[user_id] = []
        
        if user_id not in self.user_preferences:
            self.user_preferences[user_id] = {}
    
    async def get_recommendations(
        self,
        user_id: str,
        courses: List[Course],
        limit: int = 10
    ) -> List[Course]:
        """Get personalized recommendations"""
        if user_id not in self.user_preferences:
            # Return popular courses for new users
            return sorted(
                courses,
                key=lambda c: c.average_rating,
                reverse=True
            )[:limit]
        
        preferences = self.user_preferences[user_id]
        enrolled = set(self.enrollments.get(user_id, []))
        
        # Score courses based on preferences
        scored_courses = []
        for course in courses:
            if course.id in enrolled:
                continue
            
            category_score = preferences.get(course.metadata.category, 0)
            rating_score = course.average_rating / 5.0
            
            # Combine scores
            total_score = (category_score * 0.6) + (rating_score * 0.4)
            scored_courses.append((course, total_score))
        
        # Sort by score and return top N
        return [c for c, _ in sorted(scored_courses, key=lambda x: x[1], reverse=True)][:limit]

# ============================================================================
# E-LEARNING SERVICE (Main Orchestrator)
# ============================================================================

class ELearningService:
    """Complete production-grade e-learning platform"""
    
    def __init__(self):
        self.courses: Dict[str, Course] = {}
        self.lessons: Dict[str, List[Lesson]] = {}
        self.quizzes: Dict[str, List[Quiz]] = {}
        self.assignments: Dict[str, List[Assignment]] = {}
        self.enrollments: Dict[str, List[Enrollment]] = {}
        self.progress: Dict[str, Progress] = {}
        self.certificates: Dict[str, List[Certificate]] = {}
        self.reviews: Dict[str, List[CourseReview]] = {}
        
        self.grading_engine = GradingEngine()
        self.certificate_generator = CertificateGenerator()
        self.recommendation_engine = RecommendationEngine()
    
    # ========================================================================
    # COURSE MANAGEMENT
    # ========================================================================
    
    async def create_course(self, instructor_id: str, metadata: CourseMetadata) -> Course:
        """Create new course"""
        course = Course(instructor_id=instructor_id, metadata=metadata)
        self.courses[course.id] = course
        self.lessons[course.id] = []
        self.quizzes[course.id] = []
        self.assignments[course.id] = []
        self.enrollments[course.id] = []
        self.reviews[course.id] = []
        return course
    
    async def publish_course(self, course_id: str) -> Course:
        """Publish course"""
        course = self.courses[course_id]
        course.status = CourseStatus.PUBLISHED
        course.updated_at = datetime.utcnow()
        return course
    
    async def get_course(self, course_id: str) -> Course:
        """Get course details"""
        if course_id not in self.courses:
            raise ValueError("Course not found")
        return self.courses[course_id]
    
    async def list_courses(self, limit: int = 50, offset: int = 0) -> List[Course]:
        """List all published courses"""
        courses = [c for c in self.courses.values() if c.status == CourseStatus.PUBLISHED]
        return courses[offset:offset + limit]
    
    async def search_courses(self, query: str, category: Optional[str] = None, limit: int = 20) -> List[Course]:
        """Search courses"""
        query_lower = query.lower()
        results = []
        
        for course in self.courses.values():
            if course.status != CourseStatus.PUBLISHED:
                continue
            
            if category and course.metadata.category != category:
                continue
            
            if (query_lower in course.metadata.title.lower() or
                query_lower in course.metadata.description.lower() or
                query_lower in course.metadata.instructor.lower()):
                results.append(course)
        
        return results[:limit]
    
    # ========================================================================
    # LESSON MANAGEMENT
    # ========================================================================
    
    async def create_lesson(
        self,
        course_id: str,
        title: str,
        description: str,
        content: str,
        lesson_number: int,
        duration_minutes: int,
        video_url: Optional[str] = None,
        section_id: str = ""
    ) -> Lesson:
        """Create lesson"""
        lesson = Lesson(
            course_id=course_id,
            title=title,
            description=description,
            content=content,
            lesson_number=lesson_number,
            duration_minutes=duration_minutes,
            video_url=video_url,
            section_id=section_id
        )
        
        self.lessons[course_id].append(lesson)
        return lesson
    
    async def publish_lesson(self, course_id: str, lesson_id: str) -> Lesson:
        """Publish lesson"""
        lesson = next(l for l in self.lessons[course_id] if l.id == lesson_id)
        lesson.status = LessonStatus.PUBLISHED
        lesson.updated_at = datetime.utcnow()
        return lesson
    
    async def get_lesson(self, course_id: str, lesson_id: str) -> Lesson:
        """Get lesson content"""
        return next(l for l in self.lessons[course_id] if l.id == lesson_id)
    
    async def list_lessons(self, course_id: str) -> List[Lesson]:
        """List course lessons"""
        return sorted(self.lessons[course_id], key=lambda l: l.lesson_number)
    
    # ========================================================================
    # QUIZ MANAGEMENT
    # ========================================================================
    
    async def create_quiz(
        self,
        lesson_id: str,
        title: str,
        questions: List[QuizQuestion],
        passing_score: int = 70
    ) -> Quiz:
        """Create lesson quiz"""
        quiz = Quiz(
            lesson_id=lesson_id,
            title=title,
            questions=questions,
            passing_score=passing_score
        )
        return quiz
    
    async def submit_quiz_answers(
        self,
        user_id: str,
        course_id: str,
        quiz_id: str,
        answers: Dict[str, str]
    ) -> Tuple[float, bool, Dict]:
        """Submit and grade quiz"""
        quiz = next(q for qs in self.quizzes.values() for q in qs if q.id == quiz_id)
        score, results = self.grading_engine.calculate_quiz_score(answers, quiz)
        passed = score >= quiz.passing_score
        
        # Update progress
        if course_id in [p.course_id for p in self.progress.values() if p.user_id == user_id]:
            prog = next(p for p in self.progress.values() if p.user_id == user_id and p.course_id == course_id)
            prog.quiz_scores[quiz_id] = score
        
        return score, passed, results
    
    # ========================================================================
    # ASSIGNMENT MANAGEMENT
    # ========================================================================
    
    async def create_assignment(
        self,
        lesson_id: str,
        title: str,
        description: str,
        instructions: str,
        max_score: int = 100
    ) -> Assignment:
        """Create assignment"""
        assignment = Assignment(
            lesson_id=lesson_id,
            title=title,
            description=description,
            instructions=instructions,
            max_score=max_score
        )
        return assignment
    
    async def grade_assignment(
        self,
        user_id: str,
        course_id: str,
        assignment_id: str,
        score: float,
        feedback: str = ""
    ) -> float:
        """Grade assignment"""
        assignment = next(a for as_ in self.assignments.values() for a in as_ if a.id == assignment_id)
        grade = self.grading_engine.calculate_assignment_grade(score, {})
        
        # Update progress
        if course_id in [p.course_id for p in self.progress.values() if p.user_id == user_id]:
            prog = next(p for p in self.progress.values() if p.user_id == user_id and p.course_id == course_id)
            prog.assignment_grades[assignment_id] = grade
        
        return grade
    
    # ========================================================================
    # ENROLLMENT & PROGRESS
    # ========================================================================
    
    async def enroll_student(
        self,
        user_id: str,
        course_id: str,
        payment_method: Optional[str] = None,
        amount_paid: float = 0.0
    ) -> Enrollment:
        """Enroll student in course"""
        enrollment = Enrollment(
            user_id=user_id,
            course_id=course_id,
            payment_method=payment_method,
            amount_paid=amount_paid
        )
        
        self.enrollments[course_id].append(enrollment)
        
        # Create progress tracking
        course = self.courses[course_id]
        lessons_total = len(self.lessons[course_id])
        
        progress = Progress(
            user_id=user_id,
            course_id=course_id,
            lessons_total=lessons_total
        )
        
        self.progress[f"{user_id}:{course_id}"] = progress
        self.courses[course_id].student_count += 1
        
        return enrollment
    
    async def mark_lesson_complete(self, user_id: str, course_id: str, lesson_id: str):
        """Mark lesson as complete"""
        progress_key = f"{user_id}:{course_id}"
        if progress_key in self.progress:
            prog = self.progress[progress_key]
            prog.lessons_completed += 1
            prog.completion_percentage = (prog.lessons_completed / prog.lessons_total * 100) if prog.lessons_total > 0 else 0
            prog.last_accessed = datetime.utcnow()
    
    async def get_progress(self, user_id: str, course_id: str) -> Progress:
        """Get student progress"""
        progress_key = f"{user_id}:{course_id}"
        return self.progress.get(progress_key)
    
    async def complete_course(self, user_id: str, course_id: str) -> Optional[Certificate]:
        """Mark course as complete and generate certificate"""
        progress_key = f"{user_id}:{course_id}"
        if progress_key not in self.progress:
            return None
        
        prog = self.progress[progress_key]
        if prog.completion_percentage < 80:  # Require 80% completion
            return None
        
        prog.status = "completed"
        prog.completed_date = datetime.utcnow()
        
        course = self.courses[course_id]
        certificate = self.certificate_generator.generate_certificate(
            user_id,
            course_id,
            course.metadata.title,
            course.metadata.instructor
        )
        
        if course_id not in self.certificates:
            self.certificates[course_id] = []
        
        self.certificates[course_id].append(certificate)
        return certificate
    
    # ========================================================================
    # CERTIFICATES
    # ========================================================================
    
    async def get_certificate(self, certificate_id: str) -> Optional[Certificate]:
        """Get certificate by ID"""
        for certs in self.certificates.values():
            for cert in certs:
                if cert.id == certificate_id:
                    return cert
        return None
    
    async def verify_certificate(self, verification_code: str) -> Tuple[bool, Optional[Certificate]]:
        """Verify certificate authenticity"""
        for certs in self.certificates.values():
            for cert in certs:
                if cert.verification_code == verification_code:
                    is_valid = self.certificate_generator.verify_certificate(cert)
                    return is_valid, cert
        return False, None
    
    async def revoke_certificate(self, certificate_id: str):
        """Revoke certificate"""
        for certs in self.certificates.values():
            for cert in certs:
                if cert.id == certificate_id:
                    cert.status = CertificateStatus.REVOKED
    
    # ========================================================================
    # REVIEWS & RATINGS
    # ========================================================================
    
    async def submit_review(
        self,
        user_id: str,
        course_id: str,
        rating: int,
        review_text: Optional[str] = None
    ) -> CourseReview:
        """Submit course review"""
        review = CourseReview(
            course_id=course_id,
            user_id=user_id,
            rating=rating,
            review_text=review_text
        )
        
        self.reviews[course_id].append(review)
        
        # Update course average rating
        course = self.courses[course_id]
        reviews = self.reviews[course_id]
        course.average_rating = sum(r.rating for r in reviews) / len(reviews)
        course.total_reviews = len(reviews)
        
        return review
    
    async def get_reviews(self, course_id: str, limit: int = 20) -> List[CourseReview]:
        """Get course reviews"""
        reviews = self.reviews.get(course_id, [])
        return sorted(reviews, key=lambda r: r.helpful_count, reverse=True)[:limit]
    
    # ========================================================================
    # RECOMMENDATIONS
    # ========================================================================
    
    async def get_recommended_courses(self, user_id: str, limit: int = 10) -> List[Course]:
        """Get personalized course recommendations"""
        all_courses = list(self.courses.values())
        return await self.recommendation_engine.get_recommendations(user_id, all_courses, limit)
    
    # ========================================================================
    # ANALYTICS & MONETIZATION
    # ========================================================================
    
    async def get_instructor_earnings(self, instructor_id: str) -> Dict[str, Any]:
        """Calculate instructor earnings"""
        instructor_courses = [c for c in self.courses.values() if c.instructor_id == instructor_id]
        
        total_revenue = 0.0
        course_breakdown = {}
        
        for course in instructor_courses:
            course_enrollments = self.enrollments.get(course.id, [])
            course_revenue = sum(e.amount_paid for e in course_enrollments if e.status == "active")
            total_revenue += course_revenue
            
            course_breakdown[course.id] = {
                'title': course.metadata.title,
                'students': len(course_enrollments),
                'revenue': course_revenue,
                'average_rating': course.average_rating
            }
        
        return {
            'instructor_id': instructor_id,
            'total_revenue': total_revenue,
            'courses': course_breakdown,
            'total_students': sum(c.student_count for c in instructor_courses)
        }
    
    async def get_platform_analytics(self) -> Dict[str, Any]:
        """Get overall platform analytics"""
        total_courses = len([c for c in self.courses.values() if c.status == CourseStatus.PUBLISHED])
        total_students = sum(c.student_count for c in self.courses.values())
        total_earnings = sum(
            sum(e.amount_paid for e in enrolls if e.status == "active")
            for enrolls in self.enrollments.values()
        )
        
        return {
            'total_courses': total_courses,
            'total_students': total_students,
            'total_earnings': total_earnings,
            'average_course_rating': sum(c.average_rating for c in self.courses.values()) / total_courses if total_courses > 0 else 0
        }

# ============================================================================
# INITIALIZATION
# ============================================================================

_elearning_service: Optional[ELearningService] = None

def init_elearning_service() -> ELearningService:
    """Initialize e-learning service"""
    global _elearning_service
    _elearning_service = ELearningService()
    return _elearning_service

def get_elearning_service() -> ELearningService:
    """Get e-learning service singleton"""
    global _elearning_service
    if _elearning_service is None:
        _elearning_service = init_elearning_service()
    return _elearning_service
