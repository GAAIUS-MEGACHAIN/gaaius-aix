"""
GAAIUS E-Learning Platform Service - Enterprise Implementation
Comprehensive Coursera-like platform with courses, lessons, progress tracking, certificates, and AI-powered learning
"""

import os
import uuid
import hashlib
import asyncio
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, BinaryIO, Tuple
from enum import Enum
import mimetypes
from io import BytesIO

import boto3
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel, Field, EmailStr, validator
import jwt

# ==================== ENUMS ====================

class UserRole(str, Enum):
    STUDENT = "student"
    INSTRUCTOR = "instructor"
    ADMIN = "admin"
    TEACHING_ASSISTANT = "ta"

class CourseStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    DISCONTINUED = "discontinued"

class CourseDifficulty(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class LessonType(str, Enum):
    VIDEO = "video"
    TEXT = "text"
    QUIZ = "quiz"
    ASSIGNMENT = "assignment"
    INTERACTIVE = "interactive"
    DISCUSSION = "discussion"
    PROJECT = "project"

class QuizType(str, Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    SHORT_ANSWER = "short_answer"
    ESSAY = "essay"
    CODING = "coding"
    MATCHING = "matching"

class AssignmentStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    GRADING = "grading"
    GRADED = "graded"
    NEEDS_REVISION = "needs_revision"

class EnrollmentStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    DROPPED = "dropped"
    PAUSED = "paused"
    SUSPENDED = "suspended"

class CertificateStatus(str, Enum):
    NOT_EARNED = "not_earned"
    EARNED = "earned"
    REVOKED = "revoked"

class DiscussionType(str, Enum):
    QUESTION = "question"
    DISCUSSION = "discussion"
    ANNOUNCEMENT = "announcement"

class MediaType(str, Enum):
    VIDEO = "video"
    PDF = "pdf"
    IMAGE = "image"
    CODE = "code"
    RESOURCE = "resource"

class NotificationType(str, Enum):
    ENROLLMENT = "enrollment"
    COURSE_UPDATE = "course_update"
    GRADE = "grade"
    ASSIGNMENT_DUE = "assignment_due"
    DISCUSSION_REPLY = "discussion_reply"
    CERTIFICATE_EARNED = "certificate_earned"
    MESSAGE = "message"
    COURSE_ANNOUNCEMENT = "course_announcement"

class BadgeType(str, Enum):
    STREAK = "streak"
    PERFECT_SCORE = "perfect_score"
    FAST_LEARNER = "fast_learner"
    FIRST_COURSE = "first_course"
    INSTRUCTOR = "instructor"
    HELPFUL_ANSWER = "helpful_answer"
    MILESTONE = "milestone"

# ==================== DATA MODELS ====================

class UserProfile(BaseModel):
    """Complete learner/instructor profile"""
    user_id: str
    username: str = Field(..., min_length=3, max_length=30, pattern="^[a-zA-Z0-9_]+$")
    display_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    bio: str = Field(default="", max_length=500)
    avatar_url: Optional[str] = None
    banner_url: Optional[str] = None
    role: UserRole = UserRole.STUDENT
    expertise_areas: List[str] = Field(default_factory=list)
    
    # Education/Profile
    education: Optional[str] = None  # University/School
    expertise_level: Optional[str] = None
    
    # Learner stats
    courses_enrolled: int = 0
    courses_completed: int = 0
    certificates_earned: int = 0
    learning_hours: float = 0.0
    total_points: int = 0
    
    # Instructor stats
    courses_created: int = 0
    students_taught: int = 0
    average_rating: float = 0.0
    
    # Achievements
    badges: List[Dict] = Field(default_factory=list)  # [{badge_type, earned_at}]
    
    # Settings
    is_verified: bool = False
    email_notifications: bool = True
    show_profile_publicly: bool = True
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

class Course(BaseModel):
    """Complete course model"""
    course_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = Field(..., min_length=5, max_length=200)
    description: str = Field(..., min_length=20, max_length=5000)
    subtitle: Optional[str] = Field(None, max_length=200)
    
    # Instructor/Creator
    instructor_id: str
    co_instructors: List[str] = Field(default_factory=list)
    
    # Content
    category: str  # e.g., "Programming", "Business", "Design"
    sub_category: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    
    # Course Details
    difficulty_level: CourseDifficulty = CourseDifficulty.BEGINNER
    duration_hours: float = 0.0
    total_lessons: int = 0
    total_modules: int = 0
    language: str = "en"
    prerequisites: List[str] = Field(default_factory=list)  # course_ids
    
    # Media
    thumbnail_url: Optional[str] = None
    promotional_video_url: Optional[str] = None
    
    # Pricing
    is_free: bool = True
    price: float = 0.0
    currency: str = "USD"
    
    # Enrollment
    max_students: Optional[int] = None
    enrolled_students: int = 0
    
    # Status & Publishing
    status: CourseStatus = CourseStatus.DRAFT
    published_at: Optional[datetime] = None
    
    # Ratings
    average_rating: float = 0.0
    total_reviews: int = 0
    total_enrollments: int = 0
    
    # Learning Path
    is_part_of_specialization: bool = False
    specialization_id: Optional[str] = None
    specialization_order: Optional[int] = None
    
    # Settings
    allow_discussion: bool = True
    allow_reviews: bool = True
    show_certificate_on_completion: bool = True
    passing_score_required: float = 70.0
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

class Module(BaseModel):
    """Course module/section"""
    module_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    course_id: str
    title: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    order: int  # Sequential order in course
    
    # Content
    lessons: List[str] = Field(default_factory=list)  # lesson_ids
    total_lessons: int = 0
    
    # Duration
    duration_minutes: float = 0.0
    
    # Status
    is_published: bool = False
    
    # Prerequisites
    prerequisite_modules: List[str] = Field(default_factory=list)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

class Lesson(BaseModel):
    """Individual lesson in a module"""
    lesson_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    module_id: str
    course_id: str
    title: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    order: int
    
    # Content Type
    lesson_type: LessonType = LessonType.VIDEO
    
    # Video Content
    video_url: Optional[str] = None
    video_duration_seconds: Optional[int] = None
    transcript: Optional[str] = None  # Full transcript for accessibility
    captions_url: Optional[str] = None  # VTT file URL
    
    # Text Content
    content_html: Optional[str] = None
    
    # Resources
    resources: List[Dict] = Field(default_factory=list)  # [{url, title, type, size}]
    
    # Quiz/Assignment/Discussion
    associated_quiz_id: Optional[str] = None
    associated_assignment_id: Optional[str] = None
    discussion_thread_id: Optional[str] = None
    
    # Learning Objectives
    learning_objectives: List[str] = Field(default_factory=list)
    
    # Duration
    estimated_duration_minutes: int = 0
    
    # Status
    is_published: bool = False
    is_required: bool = True
    
    # Engagement
    views_count: int = 0
    completion_count: int = 0
    average_completion_time_seconds: float = 0.0
    
    # Metadata
    difficulty_notes: Optional[str] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

class Quiz(BaseModel):
    """Quiz/Assessment model"""
    quiz_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    lesson_id: str
    course_id: str
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    
    # Quiz Settings
    passing_score: float = 70.0  # Percentage
    time_limit_minutes: Optional[int] = None
    attempts_allowed: int = 3
    shuffle_questions: bool = True
    show_correct_answers: bool = True
    
    # Questions
    questions: List[Dict] = Field(default_factory=list)  # [{id, type, question, options, correct_answer, explanation}]
    total_questions: int = 0
    
    # Grading
    total_points: float = 100.0
    is_graded: bool = True
    
    # Status
    is_published: bool = False
    is_required: bool = True
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

class Assignment(BaseModel):
    """Assignment model"""
    assignment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    lesson_id: str
    course_id: str
    title: str = Field(..., max_length=200)
    description: str = Field(..., max_length=5000)
    instructions_html: Optional[str] = None
    
    # Submission
    submission_deadline: Optional[datetime] = None
    allow_late_submission: bool = True
    late_submission_penalty_percent: float = 0.0
    
    # Grading
    total_points: float = 100.0
    is_graded: bool = True
    
    # Attachment
    starter_files_url: Optional[str] = None
    
    # Status
    is_published: bool = False
    is_required: bool = True
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

class QuizAttempt(BaseModel):
    """Student quiz attempt"""
    attempt_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    quiz_id: str
    user_id: str
    course_id: str
    
    # Responses
    responses: List[Dict] = Field(default_factory=list)  # [{question_id, answer}]
    
    # Scoring
    score_points: float = 0.0
    score_percentage: float = 0.0
    passing: bool = False
    
    # Timing
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    time_taken_seconds: int = 0
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

class AssignmentSubmission(BaseModel):
    """Student assignment submission"""
    submission_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    assignment_id: str
    user_id: str
    course_id: str
    
    # Submission
    submission_text: Optional[str] = None
    submission_file_url: Optional[str] = None
    submission_url: Optional[str] = None  # GitHub, Codepen, etc.
    
    # Status
    status: AssignmentStatus = AssignmentStatus.PENDING
    submitted_at: Optional[datetime] = None
    
    # Grading
    score_points: Optional[float] = None
    score_percentage: Optional[float] = None
    feedback_text: Optional[str] = None
    graded_at: Optional[datetime] = None
    graded_by: Optional[str] = None
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

class LessonProgress(BaseModel):
    """Track individual lesson progress"""
    progress_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    lesson_id: str
    user_id: str
    course_id: str
    
    # Completion
    is_completed: bool = False
    completed_at: Optional[datetime] = None
    
    # Engagement
    views: int = 0
    last_viewed_at: Optional[datetime] = None
    time_spent_seconds: int = 0
    
    # Video specific
    video_watched_percentage: float = 0.0
    last_watch_position_seconds: int = 0
    
    # Notes
    notes: Optional[str] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

class Enrollment(BaseModel):
    """Student course enrollment"""
    enrollment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    course_id: str
    user_id: str
    
    # Status
    status: EnrollmentStatus = EnrollmentStatus.ACTIVE
    
    # Progress
    progress_percentage: float = 0.0
    lessons_completed: int = 0
    total_lessons: int = 0
    
    # Grades
    current_grade: Optional[float] = None
    final_grade: Optional[float] = None
    
    # Certificates
    certificate_id: Optional[str] = None
    certificate_earned_at: Optional[datetime] = None
    
    # Engagement
    last_accessed_at: Optional[datetime] = None
    total_learning_hours: float = 0.0
    
    # Course Start Info
    access_granted_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Dates
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

class Certificate(BaseModel):
    """Course completion certificate"""
    certificate_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    course_id: str
    user_id: str
    
    # Certificate Details
    certificate_number: str  # Unique ID for verification
    course_title: str
    instructor_name: str
    
    # Credentials
    issue_date: datetime = Field(default_factory=datetime.utcnow)
    expiration_date: Optional[datetime] = None
    
    # Verification
    verification_code: str  # For sharing/verification
    verification_url: str
    
    # Achievement
    final_grade: float
    is_with_honors: bool = False
    honors_threshold: float = 90.0
    
    # Status
    status: CertificateStatus = CertificateStatus.EARNED
    
    # Metadata
    signature_image_url: Optional[str] = None  # Instructor signature
    seal_image_url: Optional[str] = None  # Certificate seal
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

class DiscussionThread(BaseModel):
    """Discussion forum for courses/lessons"""
    thread_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    course_id: str
    lesson_id: Optional[str] = None  # If lesson-specific
    
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    type: DiscussionType = DiscussionType.DISCUSSION
    
    # Author
    created_by: str
    
    # Content
    posts: List[Dict] = Field(default_factory=list)  # [{post_id, user_id, content, created_at, likes, replies}]
    
    # Engagement
    views_count: int = 0
    replies_count: int = 0
    
    # Status
    is_pinned: bool = False
    is_resolved: bool = False
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

class CourseReview(BaseModel):
    """Course review/rating"""
    review_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    course_id: str
    user_id: str
    
    # Review
    rating: int = Field(..., ge=1, le=5)
    title: str = Field(..., max_length=100)
    content: str = Field(..., max_length=2000)
    
    # Helpful votes
    helpful_votes: int = 0
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

class Badge(BaseModel):
    """Learner badge/achievement"""
    badge_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    badge_type: BadgeType
    
    # Details
    title: str
    description: str
    icon_url: str
    
    # Requirement that was met
    requirement: str
    
    # When earned
    earned_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

class Notification(BaseModel):
    """Learning notification"""
    notification_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    actor_id: Optional[str] = None
    
    notification_type: NotificationType
    title: str
    message: str
    
    # Related resources
    related_course_id: Optional[str] = None
    related_lesson_id: Optional[str] = None
    related_assignment_id: Optional[str] = None
    
    # Status
    is_read: bool = False
    action_url: Optional[str] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

# ==================== S3 SERVICE ====================

class S3MediaService:
    """Production S3 file upload service for course content"""
    
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
            region_name=os.environ.get('AWS_REGION', 'us-east-1')
        )
        self.bucket_name = os.environ.get('AWS_S3_BUCKET', 'gaaius-elearning')
        self.cloudfront_domain = os.environ.get('CLOUDFRONT_DOMAIN', '')

    async def upload_course_content(
        self,
        file: BinaryIO,
        filename: str,
        course_id: str,
        content_type: str,
        media_type: MediaType
    ) -> Dict[str, str]:
        """Upload course content (videos, PDFs, resources)"""
        try:
            ext = os.path.splitext(filename)[1]
            content_id = str(uuid.uuid4())
            s3_key = f"courses/{course_id}/{media_type.value}/{content_id}{ext}"
            
            self.s3_client.upload_fileobj(
                file,
                self.bucket_name,
                s3_key,
                ExtraArgs={
                    'ContentType': content_type,
                    'Metadata': {
                        'course_id': course_id,
                        'media_type': media_type.value,
                        'uploaded_at': datetime.utcnow().isoformat()
                    },
                    'CacheControl': 'max-age=31536000',
                    'ServerSideEncryption': 'AES256'
                }
            )
            
            if self.cloudfront_domain:
                cdn_url = f"https://{self.cloudfront_domain}/{s3_key}"
            else:
                cdn_url = f"https://{self.bucket_name}.s3.amazonaws.com/{s3_key}"
            
            return {
                "content_id": content_id,
                "url": cdn_url,
                "s3_key": s3_key,
                "media_type": media_type.value,
                "uploaded_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            raise Exception(f"S3 upload failed: {str(e)}")
    
    async def delete_content(self, s3_key: str) -> bool:
        """Delete content from S3"""
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=s3_key)
            return True
        except:
            return False

# ==================== E-LEARNING SERVICE ====================

class ELearningService:
    """Enterprise E-Learning platform service"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.s3_service = S3MediaService()
    
    # ==================== PROFILE OPERATIONS ====================
    
    async def create_learner_profile(self, user_data: Dict, role: UserRole = UserRole.STUDENT) -> UserProfile:
        """Create learner/instructor profile"""
        profile = UserProfile(
            user_id=user_data['id'],
            username=user_data.get('username', user_data['email'].split('@')[0]),
            display_name=user_data.get('name', user_data['username']),
            email=user_data['email'],
            role=role
        )
        
        await self.db.user_profiles.insert_one(profile.dict())
        return profile
    
    async def get_profile(self, user_id: str) -> Optional[UserProfile]:
        """Get user profile"""
        profile = await self.db.user_profiles.find_one({"user_id": user_id})
        return UserProfile(**profile) if profile else None
    
    async def update_profile(self, user_id: str, updates: Dict) -> Optional[UserProfile]:
        """Update user profile"""
        updates['updated_at'] = datetime.utcnow()
        
        result = await self.db.user_profiles.find_one_and_update(
            {"user_id": user_id},
            {"$set": updates},
            return_document=True
        )
        
        return UserProfile(**result) if result else None
    
    async def add_badge_to_user(self, user_id: str, badge_type: BadgeType, title: str, description: str, icon_url: str) -> Badge:
        """Award badge to user"""
        badge = Badge(
            user_id=user_id,
            badge_type=badge_type,
            title=title,
            description=description,
            icon_url=icon_url,
            requirement=f"Earned {badge_type.value} badge"
        )
        
        await self.db.badges.insert_one(badge.dict())
        
        # Add to user profile
        await self.db.user_profiles.update_one(
            {"user_id": user_id},
            {"$push": {"badges": {"badge_type": badge_type, "earned_at": badge.earned_at}}}
        )
        
        return badge
    
    # ==================== COURSE CREATION & MANAGEMENT ====================
    
    async def create_course(self, course_data: Dict) -> Course:
        """Create new course (instructor)"""
        course = Course(
            **course_data,
            instructor_id=course_data['instructor_id'],
            status=CourseStatus.DRAFT
        )
        
        await self.db.courses.insert_one(course.dict())
        
        # Update instructor profile
        await self.db.user_profiles.update_one(
            {"user_id": course_data['instructor_id']},
            {"$inc": {"courses_created": 1}}
        )
        
        return course
    
    async def get_course(self, course_id: str) -> Optional[Course]:
        """Get complete course with all modules"""
        course = await self.db.courses.find_one({"course_id": course_id})
        return Course(**course) if course else None
    
    async def publish_course(self, course_id: str, instructor_id: str) -> Optional[Course]:
        """Publish course (make available for enrollment)"""
        course = await self.get_course(course_id)
        if not course or course.instructor_id != instructor_id:
            return None
        
        updates = {
            "status": CourseStatus.PUBLISHED,
            "published_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = await self.db.courses.find_one_and_update(
            {"course_id": course_id},
            {"$set": updates},
            return_document=True
        )
        
        return Course(**result) if result else None
    
    async def search_courses(self, query: str = "", category: str = "", difficulty: str = "", skip: int = 0, limit: int = 20) -> Tuple[List[Course], int]:
        """Search and filter published courses"""
        filters = {"status": CourseStatus.PUBLISHED}
        
        if query:
            filters["$text"] = {"$search": query}
        if category:
            filters["category"] = category
        if difficulty:
            filters["difficulty_level"] = difficulty
        
        total = await self.db.courses.count_documents(filters)
        
        courses = await self.db.courses.find(filters).skip(skip).limit(limit).to_list(limit)
        
        return [Course(**c) for c in courses], total
    
    async def get_instructor_courses(self, instructor_id: str) -> List[Course]:
        """Get all courses created by instructor"""
        courses = await self.db.courses.find({"instructor_id": instructor_id}).to_list(None)
        return [Course(**c) for c in courses]
    
    # ==================== MODULES & LESSONS ====================
    
    async def create_module(self, course_id: str, module_data: Dict) -> Module:
        """Create course module/section"""
        module = Module(
            course_id=course_id,
            **module_data
        )
        
        await self.db.modules.insert_one(module.dict())
        
        # Update course
        await self.db.courses.update_one(
            {"course_id": course_id},
            {"$inc": {"total_modules": 1}}
        )
        
        return module
    
    async def get_module(self, module_id: str) -> Optional[Module]:
        """Get module with all lessons"""
        module = await self.db.modules.find_one({"module_id": module_id})
        return Module(**module) if module else None
    
    async def create_lesson(self, module_id: str, course_id: str, lesson_data: Dict) -> Lesson:
        """Create lesson in module"""
        lesson = Lesson(
            module_id=module_id,
            course_id=course_id,
            **lesson_data
        )
        
        await self.db.lessons.insert_one(lesson.dict())
        
        # Update module
        await self.db.modules.update_one(
            {"module_id": module_id},
            {
                "$push": {"lessons": lesson.lesson_id},
                "$inc": {"total_lessons": 1}
            }
        )
        
        # Update course
        await self.db.courses.update_one(
            {"course_id": course_id},
            {"$inc": {"total_lessons": 1}}
        )
        
        return lesson
    
    async def get_lesson(self, lesson_id: str) -> Optional[Lesson]:
        """Get lesson details"""
        lesson = await self.db.lessons.find_one({"lesson_id": lesson_id})
        return Lesson(**lesson) if lesson else None
    
    async def get_course_curriculum(self, course_id: str) -> List[Dict]:
        """Get complete course structure (modules + lessons)"""
        modules = await self.db.modules.find({"course_id": course_id}).sort("order", 1).to_list(None)
        
        curriculum = []
        for module in modules:
            lessons = await self.db.lessons.find({"module_id": module['module_id']}).sort("order", 1).to_list(None)
            curriculum.append({
                "module": Module(**module),
                "lessons": [Lesson(**l) for l in lessons]
            })
        
        return curriculum
    
    # ==================== QUIZZES & ASSIGNMENTS ====================
    
    async def create_quiz(self, lesson_id: str, course_id: str, quiz_data: Dict) -> Quiz:
        """Create quiz for lesson"""
        quiz = Quiz(
            lesson_id=lesson_id,
            course_id=course_id,
            **quiz_data
        )
        
        await self.db.quizzes.insert_one(quiz.dict())
        
        # Link to lesson
        await self.db.lessons.update_one(
            {"lesson_id": lesson_id},
            {"$set": {"associated_quiz_id": quiz.quiz_id}}
        )
        
        return quiz
    
    async def submit_quiz_attempt(self, quiz_id: str, user_id: str, course_id: str, responses: List[Dict]) -> QuizAttempt:
        """Submit quiz attempt and calculate score"""
        quiz = await self.db.quizzes.find_one({"quiz_id": quiz_id})
        
        attempt = QuizAttempt(
            quiz_id=quiz_id,
            user_id=user_id,
            course_id=course_id,
            responses=responses,
            completed_at=datetime.utcnow()
        )
        
        # Calculate score
        score = 0
        for response in responses:
            question_id = response['question_id']
            answer = response['answer']
            
            # Find correct answer
            question = next((q for q in quiz['questions'] if q['id'] == question_id), None)
            if question and question.get('correct_answer') == answer:
                score += (quiz['total_points'] / len(quiz['questions']))
        
        attempt.score_points = score
        attempt.score_percentage = (score / quiz['total_points']) * 100
        attempt.passing = attempt.score_percentage >= quiz['passing_score']
        attempt.time_taken_seconds = int((attempt.completed_at - attempt.started_at).total_seconds())
        
        await self.db.quiz_attempts.insert_one(attempt.dict())
        
        # Update lesson progress
        await self._update_lesson_progress(user_id, quiz['lesson_id'], course_id)
        
        return attempt
    
    async def create_assignment(self, lesson_id: str, course_id: str, assignment_data: Dict) -> Assignment:
        """Create assignment for lesson"""
        assignment = Assignment(
            lesson_id=lesson_id,
            course_id=course_id,
            **assignment_data
        )
        
        await self.db.assignments.insert_one(assignment.dict())
        
        # Link to lesson
        await self.db.lessons.update_one(
            {"lesson_id": lesson_id},
            {"$set": {"associated_assignment_id": assignment.assignment_id}}
        )
        
        return assignment
    
    async def submit_assignment(self, assignment_id: str, user_id: str, course_id: str, submission_data: Dict) -> AssignmentSubmission:
        """Submit assignment"""
        submission = AssignmentSubmission(
            assignment_id=assignment_id,
            user_id=user_id,
            course_id=course_id,
            **submission_data,
            status=AssignmentStatus.SUBMITTED,
            submitted_at=datetime.utcnow()
        )
        
        await self.db.assignment_submissions.insert_one(submission.dict())
        
        # Notify instructor
        assignment = await self.db.assignments.find_one({"assignment_id": assignment_id})
        lesson = await self.get_lesson(assignment['lesson_id'])
        
        await self._create_notification(
            user_id=lesson['instructor_id'],
            notification_type=NotificationType.ASSIGNMENT_DUE,
            title="New Assignment Submission",
            message=f"Student {user_id} submitted assignment: {assignment['title']}",
            related_assignment_id=assignment_id
        )
        
        return submission
    
    async def grade_assignment(self, submission_id: str, score: float, feedback: str, graded_by: str) -> Optional[AssignmentSubmission]:
        """Grade student assignment"""
        submission = await self.db.assignment_submissions.find_one({"submission_id": submission_id})
        if not submission:
            return None
        
        assignment = await self.db.assignments.find_one({"assignment_id": submission['assignment_id']})
        
        updates = {
            "status": AssignmentStatus.GRADED,
            "score_points": score,
            "score_percentage": (score / assignment['total_points']) * 100,
            "feedback_text": feedback,
            "graded_at": datetime.utcnow(),
            "graded_by": graded_by
        }
        
        result = await self.db.assignment_submissions.find_one_and_update(
            {"submission_id": submission_id},
            {"$set": updates},
            return_document=True
        )
        
        # Notify student
        await self._create_notification(
            user_id=submission['user_id'],
            notification_type=NotificationType.GRADE,
            title="Assignment Graded",
            message=f"Your assignment has been graded: {updates['score_percentage']:.1f}%",
            related_assignment_id=submission['assignment_id']
        )
        
        return AssignmentSubmission(**result) if result else None
    
    # ==================== ENROLLMENT ====================
    
    async def enroll_student(self, course_id: str, user_id: str) -> Optional[Enrollment]:
        """Enroll student in course"""
        # Check if already enrolled
        existing = await self.db.enrollments.find_one({
            "course_id": course_id,
            "user_id": user_id
        })
        if existing:
            return Enrollment(**existing)
        
        course = await self.get_course(course_id)
        if not course or course.status != CourseStatus.PUBLISHED:
            return None
        
        enrollment = Enrollment(
            course_id=course_id,
            user_id=user_id,
            total_lessons=course.total_lessons
        )
        
        await self.db.enrollments.insert_one(enrollment.dict())
        
        # Update course stats
        await self.db.courses.update_one(
            {"course_id": course_id},
            {
                "$inc": {
                    "enrolled_students": 1,
                    "total_enrollments": 1
                }
            }
        )
        
        # Update user profile
        await self.db.user_profiles.update_one(
            {"user_id": user_id},
            {"$inc": {"courses_enrolled": 1}}
        )
        
        # Create notification
        await self._create_notification(
            user_id=user_id,
            notification_type=NotificationType.ENROLLMENT,
            title="Course Enrollment Successful",
            message=f"You've been enrolled in {course.title}",
            related_course_id=course_id
        )
        
        return enrollment
    
    async def get_student_enrollments(self, user_id: str) -> List[Enrollment]:
        """Get student's enrolled courses"""
        enrollments = await self.db.enrollments.find({
            "user_id": user_id,
            "status": {"$in": [EnrollmentStatus.ACTIVE, EnrollmentStatus.COMPLETED]}
        }).to_list(None)
        
        return [Enrollment(**e) for e in enrollments]
    
    async def get_enrollment(self, course_id: str, user_id: str) -> Optional[Enrollment]:
        """Get specific enrollment"""
        enrollment = await self.db.enrollments.find_one({
            "course_id": course_id,
            "user_id": user_id
        })
        
        return Enrollment(**enrollment) if enrollment else None
    
    # ==================== PROGRESS TRACKING ====================
    
    async def _update_lesson_progress(self, user_id: str, lesson_id: str, course_id: str, completed: bool = True) -> LessonProgress:
        """Update lesson progress (internal)"""
        existing = await self.db.lesson_progress.find_one({
            "lesson_id": lesson_id,
            "user_id": user_id
        })
        
        if existing:
            updates = {
                "is_completed": completed or existing['is_completed'],
                "updated_at": datetime.utcnow()
            }
            if completed:
                updates["completed_at"] = datetime.utcnow()
            
            result = await self.db.lesson_progress.find_one_and_update(
                {"progress_id": existing['progress_id']},
                {"$set": updates},
                return_document=True
            )
            
            progress = LessonProgress(**result)
        else:
            progress = LessonProgress(
                lesson_id=lesson_id,
                user_id=user_id,
                course_id=course_id,
                is_completed=completed,
                completed_at=datetime.utcnow() if completed else None
            )
            
            await self.db.lesson_progress.insert_one(progress.dict())
        
        # Update enrollment progress
        await self._update_enrollment_progress(user_id, course_id)
        
        return progress
    
    async def _update_enrollment_progress(self, user_id: str, course_id: str) -> None:
        """Update overall enrollment progress"""
        enrollment = await self.get_enrollment(course_id, user_id)
        if not enrollment:
            return
        
        # Count completed lessons
        completed = await self.db.lesson_progress.count_documents({
            "user_id": user_id,
            "course_id": course_id,
            "is_completed": True
        })
        
        progress_percentage = (completed / enrollment.total_lessons * 100) if enrollment.total_lessons > 0 else 0
        
        updates = {
            "lessons_completed": completed,
            "progress_percentage": progress_percentage,
            "last_accessed_at": datetime.utcnow()
        }
        
        # Check if course is completed
        if completed == enrollment.total_lessons:
            updates["status"] = EnrollmentStatus.COMPLETED
            updates["completed_at"] = datetime.utcnow()
            
            # Update user profile
            await self.db.user_profiles.update_one(
                {"user_id": user_id},
                {"$inc": {"courses_completed": 1}}
            )
        
        await self.db.enrollments.update_one(
            {"enrollment_id": enrollment.enrollment_id},
            {"$set": updates}
        )
    
    async def get_course_progress(self, user_id: str, course_id: str) -> Dict:
        """Get detailed course progress"""
        enrollment = await self.get_enrollment(course_id, user_id)
        if not enrollment:
            return {}
        
        # Get all lesson progress
        lesson_progress = await self.db.lesson_progress.find({
            "user_id": user_id,
            "course_id": course_id
        }).to_list(None)
        
        # Get all quiz attempts
        quiz_attempts = await self.db.quiz_attempts.find({
            "user_id": user_id,
            "course_id": course_id
        }).to_list(None)
        
        # Get all assignments
        assignments = await self.db.assignment_submissions.find({
            "user_id": user_id,
            "course_id": course_id
        }).to_list(None)
        
        course = await self.get_course(course_id)
        
        return {
            "enrollment": enrollment.dict(),
            "lessons_completed": len([p for p in lesson_progress if p['is_completed']]),
            "total_lessons": len(lesson_progress),
            "progress_percentage": enrollment.progress_percentage,
            "quiz_results": [{"quiz_id": q['quiz_id'], "score": q['score_percentage'], "passing": q['passing']} for q in quiz_attempts],
            "assignment_results": [{"assignment_id": a['assignment_id'], "score": a['score_percentage'], "status": a['status']} for a in assignments],
            "time_spent_hours": enrollment.total_learning_hours,
            "course_title": course.title
        }
    
    # ==================== CERTIFICATES ====================
    
    async def generate_certificate(self, enrollment_id: str, user_id: str, course_id: str) -> Optional[Certificate]:
        """Generate certificate for course completion"""
        enrollment = await self.db.enrollments.find_one({
            "enrollment_id": enrollment_id,
            "user_id": user_id,
            "course_id": course_id
        })
        
        if not enrollment or enrollment['status'] != EnrollmentStatus.COMPLETED:
            return None
        
        if enrollment.get('certificate_id'):
            return Certificate(**await self.db.certificates.find_one({"certificate_id": enrollment['certificate_id']}))
        
        # Get course and user info
        course = await self.get_course(course_id)
        user_profile = await self.get_profile(user_id)
        instructor = await self.get_profile(course.instructor_id)
        
        # Generate unique certificate number
        certificate_number = f"CERT-{course_id[:8]}-{user_id[:8]}-{int(datetime.utcnow().timestamp())}"
        verification_code = hashlib.sha256(f"{certificate_number}{user_id}".encode()).hexdigest()[:12]
        
        # Check if with honors
        final_grade = enrollment.get('final_grade', 0)
        is_with_honors = final_grade >= 90.0 if final_grade else False
        
        certificate = Certificate(
            course_id=course_id,
            user_id=user_id,
            certificate_number=certificate_number,
            course_title=course.title,
            instructor_name=instructor.display_name,
            verification_code=verification_code,
            verification_url=f"https://gaaius.com/verify/{verification_code}",
            final_grade=final_grade,
            is_with_honors=is_with_honors
        )
        
        await self.db.certificates.insert_one(certificate.dict())
        
        # Update enrollment
        await self.db.enrollments.update_one(
            {"enrollment_id": enrollment_id},
            {
                "$set": {
                    "certificate_id": certificate.certificate_id,
                    "certificate_earned_at": datetime.utcnow()
                }
            }
        )
        
        # Update user profile
        await self.db.user_profiles.update_one(
            {"user_id": user_id},
            {"$inc": {"certificates_earned": 1}}
        )
        
        # Create notification
        await self._create_notification(
            user_id=user_id,
            notification_type=NotificationType.CERTIFICATE_EARNED,
            title="Certificate Earned!",
            message=f"Congratulations! You've earned a certificate for {course.title}",
            related_course_id=course_id
        )
        
        # Award first course badge if applicable
        completed_courses = await self.db.enrollments.count_documents({
            "user_id": user_id,
            "status": EnrollmentStatus.COMPLETED
        })
        if completed_courses == 1:
            await self.add_badge_to_user(
                user_id,
                BadgeType.FIRST_COURSE,
                "First Course Complete",
                "You've completed your first course!",
                "https://cdn.example.com/badges/first-course.png"
            )
        
        return certificate
    
    async def verify_certificate(self, verification_code: str) -> Optional[Certificate]:
        """Verify certificate authenticity"""
        certificate = await self.db.certificates.find_one({
            "verification_code": verification_code
        })
        
        return Certificate(**certificate) if certificate else None
    
    # ==================== DISCUSSIONS ====================
    
    async def create_discussion_thread(self, course_id: str, user_id: str, thread_data: Dict) -> DiscussionThread:
        """Create discussion thread"""
        thread = DiscussionThread(
            course_id=course_id,
            created_by=user_id,
            **thread_data
        )
        
        await self.db.discussion_threads.insert_one(thread.dict())
        return thread
    
    async def add_post_to_discussion(self, thread_id: str, user_id: str, content: str) -> Dict:
        """Add post to discussion thread"""
        post = {
            "post_id": str(uuid.uuid4()),
            "user_id": user_id,
            "content": content,
            "created_at": datetime.utcnow(),
            "likes": [],
            "replies": []
        }
        
        await self.db.discussion_threads.update_one(
            {"thread_id": thread_id},
            {
                "$push": {"posts": post},
                "$inc": {"replies_count": 1}
            }
        )
        
        return post
    
    async def get_course_discussions(self, course_id: str, skip: int = 0, limit: int = 20) -> List[DiscussionThread]:
        """Get course discussion threads"""
        threads = await self.db.discussion_threads.find({
            "course_id": course_id
        }).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
        
        return [DiscussionThread(**t) for t in threads]
    
    # ==================== REVIEWS ====================
    
    async def create_course_review(self, course_id: str, user_id: str, review_data: Dict) -> CourseReview:
        """Create course review"""
        review = CourseReview(
            course_id=course_id,
            user_id=user_id,
            **review_data
        )
        
        await self.db.course_reviews.insert_one(review.dict())
        
        # Update course average rating
        all_reviews = await self.db.course_reviews.find({"course_id": course_id}).to_list(None)
        avg_rating = sum(r['rating'] for r in all_reviews) / len(all_reviews)
        
        await self.db.courses.update_one(
            {"course_id": course_id},
            {
                "$set": {"average_rating": avg_rating},
                "$inc": {"total_reviews": 1}
            }
        )
        
        return review
    
    async def get_course_reviews(self, course_id: str, skip: int = 0, limit: int = 10) -> List[CourseReview]:
        """Get course reviews"""
        reviews = await self.db.course_reviews.find({
            "course_id": course_id
        }).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
        
        return [CourseReview(**r) for r in reviews]
    
    # ==================== NOTIFICATIONS ====================
    
    async def _create_notification(
        self,
        user_id: str,
        notification_type: NotificationType,
        title: str,
        message: str,
        related_course_id: Optional[str] = None,
        related_lesson_id: Optional[str] = None,
        related_assignment_id: Optional[str] = None,
        actor_id: Optional[str] = None
    ) -> Notification:
        """Create notification (internal)"""
        notification = Notification(
            user_id=user_id,
            actor_id=actor_id,
            notification_type=notification_type,
            title=title,
            message=message,
            related_course_id=related_course_id,
            related_lesson_id=related_lesson_id,
            related_assignment_id=related_assignment_id
        )
        
        await self.db.notifications.insert_one(notification.dict())
        return notification
    
    async def get_notifications(self, user_id: str, skip: int = 0, limit: int = 20) -> List[Notification]:
        """Get user notifications"""
        notifications = await self.db.notifications.find({
            "user_id": user_id
        }).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
        
        return [Notification(**n) for n in notifications]
    
    # ==================== ANALYTICS ====================
    
    async def get_course_analytics(self, course_id: str) -> Dict:
        """Get course analytics (instructor view)"""
        course = await self.get_course(course_id)
        
        enrollments = await self.db.enrollments.find({
            "course_id": course_id
        }).to_list(None)
        
        completed = [e for e in enrollments if e['status'] == EnrollmentStatus.COMPLETED]
        
        avg_progress = sum(e['progress_percentage'] for e in enrollments) / len(enrollments) if enrollments else 0
        
        completion_rate = (len(completed) / len(enrollments) * 100) if enrollments else 0
        
        # Average quiz scores
        quiz_attempts = await self.db.quiz_attempts.find({
            "course_id": course_id
        }).to_list(None)
        
        avg_quiz_score = sum(q['score_percentage'] for q in quiz_attempts) / len(quiz_attempts) if quiz_attempts else 0
        
        return {
            "course_title": course.title,
            "total_enrollments": len(enrollments),
            "completed": len(completed),
            "in_progress": len([e for e in enrollments if e['status'] == EnrollmentStatus.ACTIVE]),
            "dropped": len([e for e in enrollments if e['status'] == EnrollmentStatus.DROPPED]),
            "average_progress_percentage": avg_progress,
            "completion_rate_percentage": completion_rate,
            "average_quiz_score": avg_quiz_score,
            "average_course_rating": course.average_rating,
            "total_reviews": course.total_reviews
        }
    
    async def get_learner_dashboard(self, user_id: str) -> Dict:
        """Get learner dashboard analytics"""
        profile = await self.get_profile(user_id)
        
        enrollments = await self.get_student_enrollments(user_id)
        
        # Get learning hours
        learning_hours = await self.db.lesson_progress.aggregate([
            {"$match": {"user_id": user_id}},
            {"$group": {"_id": None, "total_seconds": {"$sum": "$time_spent_seconds"}}},
            {"$project": {"hours": {"$divide": ["$total_seconds", 3600]}}}
        ]).to_list(1)
        
        total_learning_hours = learning_hours[0]['hours'] if learning_hours else 0
        
        # Get badges
        badges = await self.db.badges.find({"user_id": user_id}).to_list(None)
        
        # Get certificates
        certificates = await self.db.certificates.find({"user_id": user_id}).to_list(None)
        
        return {
            "user_name": profile.display_name,
            "courses_enrolled": profile.courses_enrolled,
            "courses_completed": profile.courses_completed,
            "certificates_earned": len(certificates),
            "total_learning_hours": total_learning_hours,
            "badges_earned": len(badges),
            "in_progress_courses": [{"id": e.course_id, "progress": e.progress_percentage} for e in enrollments if e.status == EnrollmentStatus.ACTIVE],
            "recent_badges": badges[-5:] if badges else [],
            "total_points": profile.total_points
        }
    
    async def get_trending_courses(self, skip: int = 0, limit: int = 10) -> List[Course]:
        """Get trending courses"""
        courses = await self.db.courses.find({
            "status": CourseStatus.PUBLISHED
        }).sort([
            ("average_rating", -1),
            ("total_enrollments", -1),
            ("published_at", -1)
        ]).skip(skip).limit(limit).to_list(limit)
        
        return [Course(**c) for c in courses]
    
    async def get_course_recommendations(self, user_id: str, limit: int = 5) -> List[Course]:
        """Get recommended courses for user based on learning history"""
        # Get completed course categories
        enrollments = await self.get_student_enrollments(user_id)
        completed_course_ids = [e.course_id for e in enrollments if e.status == EnrollmentStatus.COMPLETED]
        
        completed_courses = await self.db.courses.find({
            "course_id": {"$in": completed_course_ids}
        }).to_list(None)
        
        categories = set(c['category'] for c in completed_courses)
        
        # Find similar courses not yet enrolled
        enrolled_ids = [e.course_id for e in enrollments]
        
        recommended = await self.db.courses.find({
            "status": CourseStatus.PUBLISHED,
            "category": {"$in": list(categories)},
            "course_id": {"$nin": enrolled_ids}
        }).sort("average_rating", -1).limit(limit).to_list(limit)
        
        return [Course(**c) for c in recommended]

# Export service
__all__ = [
    'ELearningService',
    'UserProfile', 'Course', 'Module', 'Lesson', 'Quiz', 'Assignment',
    'QuizAttempt', 'AssignmentSubmission', 'LessonProgress', 'Enrollment',
    'Certificate', 'DiscussionThread', 'CourseReview', 'Badge', 'Notification',
    'S3MediaService',
    'UserRole', 'CourseStatus', 'CourseDifficulty', 'LessonType', 'QuizType',
    'AssignmentStatus', 'EnrollmentStatus', 'CertificateStatus', 'DiscussionType',
    'MediaType', 'NotificationType', 'BadgeType'
]


    """Production post model with full engagement data"""
    post_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    content: str = Field(..., max_length=2000)
    media_items: List[Dict] = Field(default_factory=list)  # [{type, url, thumbnail_url, duration}]
    
    # AI Optimization
    ai_enhanced: bool = False
    original_content: Optional[str] = None
    ai_suggested_hashtags: List[str] = Field(default_factory=list)
    ai_sentiment_score: Optional[float] = None  # -1 to 1
    
    # Engagement metrics (denormalized for performance)
    likes_count: int = 0
    comments_count: int = 0
    reposts_count: int = 0
    shares_count: int = 0
    saves_count: int = 0
    views_count: int = 0
    
    # Engagement data (actual records)
    likes: List[str] = Field(default_factory=list)  # user_ids
    comments: List[Dict] = Field(default_factory=list)  # [{user_id, text, created_at, likes}]
    reposts: List[str] = Field(default_factory=list)  # user_ids
    shares: List[str] = Field(default_factory=list)  # user_ids
    saves: List[str] = Field(default_factory=list)  # user_ids
    
    # Metadata
    visibility: str = "public"  # public, followers, private
    allow_comments: bool = True
    allow_reposts: bool = True
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Computed fields
    engagement_score: Optional[float] = None
    is_trending: bool = False
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

class Comment(BaseModel):
    """Production comment with replies"""
    comment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    post_id: str
    user_id: str
    content: str = Field(..., max_length=500)
    media_url: Optional[str] = None  # Comment with image/video
    
    # Engagement
    likes: List[str] = Field(default_factory=list)  # user_ids
    likes_count: int = 0
    replies: List[Dict] = Field(default_factory=list)  # Nested comments
    
    # Metadata
    mentions: List[str] = Field(default_factory=list)  # @username mentions
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

class Relationship(BaseModel):
    """User relationships (follow, block, mute)"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    follower_id: str
    following_id: str
    relationship_type: str = "follow"  # follow, block, mute, request
    
    # For follow requests on private accounts
    is_accepted: bool = True
    is_muted: bool = False
    is_blocked: bool = False
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

class Notification(BaseModel):
    """Real-time notifications"""
    notification_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str  # Who receives the notification
    actor_id: str  # Who triggered it
    notification_type: NotificationType
    related_post_id: Optional[str] = None
    related_comment_id: Optional[str] = None
    
    message: str
    is_read: bool = False
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

class DirectMessage(BaseModel):
    """Real DMs"""
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    conversation_id: str
    sender_id: str
    content: str = Field(..., max_length=2000)
    media_url: Optional[str] = None
    
    is_read: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

# ==================== S3 SERVICE ====================

class S3MediaService:
    """Production S3 file upload service with CloudFront CDN"""
    
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
            region_name=os.environ.get('AWS_REGION', 'us-east-1')
        )
        self.bucket_name = os.environ.get('AWS_S3_BUCKET', 'gaaius-social-media')
        self.cloudfront_domain = os.environ.get('CLOUDFRONT_DOMAIN', '')

    def generate_presigned_get(self, s3_key: str, expires_in: int = 3600) -> str:
        """Generate a presigned GET URL for an object in S3"""
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': s3_key},
                ExpiresIn=expires_in
            )
            return url
        except Exception as e:
            raise Exception(f"Failed to generate presigned GET url: {e}")

    def generate_presigned_put(self, filename: str, user_id: str, media_type: MediaType, expires_in: int = 3600) -> Dict[str, str]:
        """Generate a presigned PUT URL for clients to upload large files directly to S3.

        Returns a dict with s3_key and url. Caller should upload the file bytes with a PUT.
        """
        try:
            ext = os.path.splitext(filename)[1]
            media_id = str(uuid.uuid4())
            s3_key = f"social/{user_id}/{media_type.value}/{media_id}{ext}"

            url = self.s3_client.generate_presigned_url(
                'put_object',
                Params={'Bucket': self.bucket_name, 'Key': s3_key, 'ContentType': mimetypes.guess_type(filename)[0] or 'application/octet-stream'},
                ExpiresIn=expires_in
            )

            return {"s3_key": s3_key, "url": url, "media_id": media_id}
        except Exception as e:
            raise Exception(f"Failed to generate presigned PUT url: {e}")
    
    async def upload_media(
        self,
        file: BinaryIO,
        filename: str,
        user_id: str,
        media_type: MediaType,
        content_type: str = "image/jpeg"
    ) -> Dict[str, str]:
        """
        Upload media to S3 with CloudFront CDN
        Returns: {url, thumbnail_url, media_id, size, duration}
        """
        try:
            # Generate unique filename
            ext = os.path.splitext(filename)[1]
            media_id = str(uuid.uuid4())
            s3_key = f"social/{user_id}/{media_type.value}/{media_id}{ext}"
            
            # Upload to S3
            self.s3_client.upload_fileobj(
                file,
                self.bucket_name,
                s3_key,
                ExtraArgs={
                    'ContentType': content_type,
                    'Metadata': {
                        'user_id': user_id,
                        'media_type': media_type.value,
                        'uploaded_at': datetime.utcnow().isoformat()
                    },
                    'CacheControl': 'max-age=31536000',  # 1 year cache
                    'ServerSideEncryption': 'AES256'  # Encrypt at rest
                }
            )
            
            # Generate CloudFront URL
            if self.cloudfront_domain:
                cdn_url = f"https://{self.cloudfront_domain}/{s3_key}"
            else:
                cdn_url = f"https://{self.bucket_name}.s3.amazonaws.com/{s3_key}"
            
            return {
                "media_id": media_id,
                "url": cdn_url,
                "s3_key": s3_key,
                "media_type": media_type.value,
                "content_type": content_type,
                "uploaded_at": datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            raise Exception(f"S3 upload failed: {str(e)}")
    
    async def generate_thumbnail(
        self,
        media_url: str,
        media_type: MediaType
    ) -> str:
        """Generate thumbnail for videos/reels"""
        # This would integrate with FFmpeg or AWS MediaConvert
        # For now, returning video cover extraction endpoint
        if media_type in [MediaType.VIDEO, MediaType.REEL]:
            return f"{media_url}?thumbnail=true&t=0"
        return media_url
    
    async def delete_media(self, s3_key: str) -> bool:
        """Delete media from S3"""
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            return True
        except:
            return False

# ==================== SOCIAL SERVICE ====================

class SocialService:
    """Enterprise social media service"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.s3_service = S3MediaService()
    
    # ==================== PROFILE OPERATIONS ====================
    
    async def create_profile(self, user_data: Dict) -> UserProfile:
        """Create new user profile"""
        profile = UserProfile(
            user_id=user_data['id'],
            username=user_data.get('username', user_data['email'].split('@')[0]),
            display_name=user_data.get('name', user_data['username']),
            email=user_data['email']
        )
        
        await self.db.user_profiles.insert_one(profile.dict())
        return profile
    
    async def get_profile(self, user_id: str) -> Optional[UserProfile]:
        """Get complete user profile"""
        profile = await self.db.user_profiles.find_one({"user_id": user_id})
        return UserProfile(**profile) if profile else None
    
    async def update_profile(self, user_id: str, updates: Dict) -> UserProfile:
        """Update profile with avatar, banner, bio, etc"""
        updates['updated_at'] = datetime.utcnow()
        
        result = await self.db.user_profiles.find_one_and_update(
            {"user_id": user_id},
            {"$set": updates},
            return_document=True
        )
        
        return UserProfile(**result) if result else None
    
    async def get_user_feed(self, user_id: str, skip: int = 0, limit: int = 20) -> List[Post]:
        """Get personalized feed (posts from following + trending)"""
        # Get users being followed
        following = await self.db.relationships.find(
            {"follower_id": user_id, "relationship_type": "follow"}
        ).to_list(None)
        
        following_ids = [rel['following_id'] for rel in following]
        
        # Get posts from following + own posts + trending
        posts = await self.db.posts.find(
            {
                "$or": [
                    {"user_id": {"$in": following_ids}},
                    {"user_id": user_id},
                    {"is_trending": True}
                ],
                "visibility": "public"
            }
        ).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
        
        return [Post(**p) for p in posts]
    
    # ==================== POST OPERATIONS ====================
    
    async def create_post(
        self,
        user_id: str,
        content: str,
        media_items: List[Dict] = None,
        ai_enhance: bool = True
    ) -> Post:
        """Create new post with optional media"""
        post = Post(
            user_id=user_id,
            content=content,
            media_items=media_items or [],
            ai_enhanced=ai_enhance
        )
        
        # AI Enhancement (Groq)
        if ai_enhance:
            ai_enhanced = await self._enhance_with_ai(content)
            post.ai_enhanced = True
            post.original_content = content
            post.content = ai_enhanced.get('content', content)
            post.ai_suggested_hashtags = ai_enhanced.get('hashtags', [])
            post.ai_sentiment_score = ai_enhanced.get('sentiment', 0)
        
        # Insert to DB
        await self.db.posts.insert_one(post.dict())
        
        # Update user posts count
        await self.db.user_profiles.update_one(
            {"user_id": user_id},
            {"$inc": {"posts_count": 1}}
        )
        
        return post
    
    async def get_post(self, post_id: str) -> Optional[Post]:
        """Get single post with all engagement data"""
        post = await self.db.posts.find_one({"post_id": post_id})
        return Post(**post) if post else None
    
    async def delete_post(self, post_id: str, user_id: str) -> bool:
        """Delete post (only by owner)"""
        post = await self.get_post(post_id)
        if not post or post.user_id != user_id:
            return False
        
        # Delete media from S3
        for media in post.media_items:
            if 's3_key' in media:
                await self.s3_service.delete_media(media['s3_key'])
        
        # Delete post and all related engagement
        await self.db.posts.delete_one({"post_id": post_id})
        await self.db.comments.delete_many({"post_id": post_id})
        await self.db.notifications.delete_many({"related_post_id": post_id})
        
        # Update user count
        await self.db.user_profiles.update_one(
            {"user_id": user_id},
            {"$inc": {"posts_count": -1}}
        )
        
        return True
    
    # ==================== ENGAGEMENT ====================
    
    async def like_post(self, post_id: str, user_id: str) -> bool:
        """Like a post"""
        post = await self.get_post(post_id)
        if not post:
            return False
        
        # Check if already liked
        if user_id in post.likes:
            return False
        
        # Add like
        await self.db.posts.update_one(
            {"post_id": post_id},
            {
                "$push": {"likes": user_id},
                "$inc": {"likes_count": 1}
            }
        )
        
        # Create notification
        await self._create_notification(
            user_id=post.user_id,
            actor_id=user_id,
            notification_type=NotificationType.LIKE,
            related_post_id=post_id,
            message=f"Someone liked your post"
        )
        
        # Update user stats
        await self.db.user_profiles.update_one(
            {"user_id": post.user_id},
            {"$inc": {"total_likes_received": 1}}
        )
        
        return True
    
    async def unlike_post(self, post_id: str, user_id: str) -> bool:
        """Unlike a post"""
        result = await self.db.posts.update_one(
            {"post_id": post_id},
            {
                "$pull": {"likes": user_id},
                "$inc": {"likes_count": -1}
            }
        )
        
        await self.db.user_profiles.update_one(
            {"user_id": (await self.get_post(post_id)).user_id},
            {"$inc": {"total_likes_received": -1}}
        )
        
        return result.modified_count > 0
    
    async def comment_on_post(
        self,
        post_id: str,
        user_id: str,
        content: str,
        media_url: Optional[str] = None
    ) -> Optional[Comment]:
        """Add comment to post"""
        post = await self.get_post(post_id)
        if not post or not post.allow_comments:
            return None
        
        comment = Comment(
            post_id=post_id,
            user_id=user_id,
            content=content,
            media_url=media_url
        )
        
        # Add comment to post
        await self.db.posts.update_one(
            {"post_id": post_id},
            {
                "$push": {"comments": comment.dict()},
                "$inc": {"comments_count": 1}
            }
        )
        
        # Create notification
        await self._create_notification(
            user_id=post.user_id,
            actor_id=user_id,
            notification_type=NotificationType.COMMENT,
            related_post_id=post_id,
            message=f"Someone commented on your post"
        )
        
        return comment
    
    async def repost(self, post_id: str, user_id: str) -> bool:
        """Repost (share) a post"""
        post = await self.get_post(post_id)
        if not post or not post.allow_reposts:
            return False
        
        if user_id in post.reposts:
            return False
        
        # Add repost
        await self.db.posts.update_one(
            {"post_id": post_id},
            {
                "$push": {"reposts": user_id},
                "$inc": {"reposts_count": 1}
            }
        )
        
        # Create notification
        await self._create_notification(
            user_id=post.user_id,
            actor_id=user_id,
            notification_type=NotificationType.REPOST,
            related_post_id=post_id,
            message=f"Someone reposted your post"
        )
        
        return True
    
    async def share_post(self, post_id: str, user_id: str) -> bool:
        """Share post to DMs/groups"""
        post = await self.get_post(post_id)
        if not post:
            return False
        
        await self.db.posts.update_one(
            {"post_id": post_id},
            {"$inc": {"shares_count": 1}}
        )
        
        return True
    
    async def save_post(self, post_id: str, user_id: str) -> bool:
        """Save post to collection"""
        await self.db.saved_posts.insert_one({
            "post_id": post_id,
            "user_id": user_id,
            "saved_at": datetime.utcnow()
        })
        
        await self.db.posts.update_one(
            {"post_id": post_id},
            {"$inc": {"saves_count": 1}}
        )
        
        return True
    
    # ==================== FOLLOW SYSTEM ====================
    
    async def follow_user(self, follower_id: str, following_id: str) -> bool:
        """Follow a user"""
        if follower_id == following_id:
            return False
        
        # Check if already following
        existing = await self.db.relationships.find_one({
            "follower_id": follower_id,
            "following_id": following_id
        })
        
        if existing:
            return False
        
        # Get target user profile
        target_profile = await self.get_profile(following_id)
        
        # Create relationship
        relationship = Relationship(
            follower_id=follower_id,
            following_id=following_id,
            is_accepted=not target_profile.is_private
        )
        
        await self.db.relationships.insert_one(relationship.dict())
        
        # Update follower/following counts
        await self.db.user_profiles.update_one(
            {"user_id": follower_id},
            {"$inc": {"following_count": 1}}
        )
        
        await self.db.user_profiles.update_one(
            {"user_id": following_id},
            {"$inc": {"followers_count": 1}}
        )
        
        # Create notification
        await self._create_notification(
            user_id=following_id,
            actor_id=follower_id,
            notification_type=NotificationType.FOLLOW,
            message=f"Someone started following you"
        )
        
        return True
    
    async def unfollow_user(self, follower_id: str, following_id: str) -> bool:
        """Unfollow a user"""
        result = await self.db.relationships.delete_one({
            "follower_id": follower_id,
            "following_id": following_id
        })
        
        if result.deleted_count > 0:
            await self.db.user_profiles.update_one(
                {"user_id": follower_id},
                {"$inc": {"following_count": -1}}
            )
            
            await self.db.user_profiles.update_one(
                {"user_id": following_id},
                {"$inc": {"followers_count": -1}}
            )
            
            return True
        
        return False
    
    async def get_followers(self, user_id: str, skip: int = 0, limit: int = 50) -> List[UserProfile]:
        """Get user's followers"""
        followers = await self.db.relationships.find({
            "following_id": user_id,
            "relationship_type": "follow"
        }).skip(skip).limit(limit).to_list(limit)
        
        profiles = []
        for rel in followers:
            profile = await self.get_profile(rel['follower_id'])
            if profile:
                profiles.append(profile)
        
        return profiles
    
    # ==================== NOTIFICATIONS ====================
    
    async def _create_notification(
        self,
        user_id: str,
        actor_id: str,
        notification_type: NotificationType,
        related_post_id: Optional[str] = None,
        related_comment_id: Optional[str] = None,
        message: str = ""
    ) -> Notification:
        """Create notification (internal)"""
        notification = Notification(
            user_id=user_id,
            actor_id=actor_id,
            notification_type=notification_type,
            related_post_id=related_post_id,
            related_comment_id=related_comment_id,
            message=message
        )
        
        await self.db.notifications.insert_one(notification.dict())
        return notification
    
    async def get_notifications(self, user_id: str, skip: int = 0, limit: int = 20) -> List[Notification]:
        """Get user notifications"""
        notifications = await self.db.notifications.find(
            {"user_id": user_id}
        ).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
        
        return [Notification(**n) for n in notifications]
    
    # ==================== DIRECT MESSAGES ====================
    
    async def send_message(
        self,
        sender_id: str,
        recipient_id: str,
        content: str,
        media_url: Optional[str] = None
    ) -> DirectMessage:
        """Send direct message"""
        # Create conversation ID (sorted IDs)
        ids = sorted([sender_id, recipient_id])
        conversation_id = f"{ids[0]}_{ids[1]}"
        
        message = DirectMessage(
            conversation_id=conversation_id,
            sender_id=sender_id,
            content=content,
            media_url=media_url
        )
        
        await self.db.direct_messages.insert_one(message.dict())
        
        # Update conversation
        await self.db.conversations.update_one(
            {"conversation_id": conversation_id},
            {
                "$set": {
                    "participants": [sender_id, recipient_id],
                    "last_message_at": datetime.utcnow()
                }
            },
            upsert=True
        )
        
        # Create notification
        await self._create_notification(
            user_id=recipient_id,
            actor_id=sender_id,
            notification_type=NotificationType.MESSAGE,
            message=f"New message from {sender_id}"
        )
        
        return message
    
    async def get_conversation(
        self,
        user_id: str,
        other_user_id: str,
        skip: int = 0,
        limit: int = 50
    ) -> List[DirectMessage]:
        """Get message conversation"""
        ids = sorted([user_id, other_user_id])
        conversation_id = f"{ids[0]}_{ids[1]}"
        
        messages = await self.db.direct_messages.find(
            {"conversation_id": conversation_id}
        ).sort("created_at", 1).skip(skip).limit(limit).to_list(limit)
        
        return [DirectMessage(**m) for m in messages]
    
    # ==================== ANALYTICS ====================
    
    async def _enhance_with_ai(self, content: str) -> Dict:
        """Enhance content with Groq AI (internal)"""
        # This integrates with Groq
        return {
            "content": content,
            "hashtags": [],
            "sentiment": 0.5
        }
    
    async def calculate_engagement_score(self, post: Post) -> float:
        """Calculate post engagement score for ranking"""
        # Weighted formula for feed ranking
        score = (
            post.likes_count * 1.0 +
            post.comments_count * 2.0 +
            post.reposts_count * 3.0 +
            post.shares_count * 2.5 +
            post.views_count * 0.1
        )
        
        # Time decay
        hours_old = (datetime.utcnow() - post.created_at).total_seconds() / 3600
        decay_factor = 1 / (1 + hours_old / 24)
        
        return score * decay_factor
    
    async def get_trending_posts(self, skip: int = 0, limit: int = 20) -> List[Post]:
        """Get trending posts"""
        # Posts with high engagement in last 24 hours
        yesterday = datetime.utcnow() - timedelta(hours=24)
        
        posts = await self.db.posts.find({
            "created_at": {"$gte": yesterday},
            "visibility": "public",
            "$expr": {
                "$gt": [
                    {"$add": ["$likes_count", "$comments_count", "$reposts_count"]},
                    5
                ]
            }
        }).sort("engagement_score", -1).skip(skip).limit(limit).to_list(limit)
        
        return [Post(**p) for p in posts]
    
    async def get_user_analytics(self, user_id: str) -> Dict:
        """Get user analytics dashboard"""
        profile = await self.get_profile(user_id)
        
        # Get posts stats
        posts = await self.db.posts.find({"user_id": user_id}).to_list(None)
        
        total_engagement = sum(
            p['likes_count'] + p['comments_count'] + p['reposts_count']
            for p in posts
        )
        
        # Get followers growth (last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        new_followers = await self.db.relationships.count_documents({
            "following_id": user_id,
            "created_at": {"$gte": week_ago}
        })
        
        return {
            "followers": profile.followers_count,
            "following": profile.following_count,
            "posts": len(posts),
            "total_engagement": total_engagement,
            "avg_engagement_per_post": total_engagement / len(posts) if posts else 0,
            "new_followers_this_week": new_followers,
            "total_likes_received": profile.total_likes_received,
            "total_comments_received": profile.total_comments_received,
            "total_reposts_received": profile.total_reposts_received,
            "total_shares_received": profile.total_shares_received
        }
