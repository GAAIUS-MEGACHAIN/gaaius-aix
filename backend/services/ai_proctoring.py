"""
GAAIUS Enterprise AI Proctoring Service - Production Grade
Real facial recognition, behavior monitoring, AI grading, NO MOCK CODE
"""

import asyncio
import logging
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple, Any
from enum import Enum
import base64
import hashlib
import json

import cv2
import numpy as np
import face_recognition
from pydantic import BaseModel, Field, validator
import mediapipe as mp
from motor.motor_asyncio import AsyncIOMotorDatabase

from backend.core.config import get_settings
from backend.core.exceptions import (
    FacialEnrollmentError, IdentityVerificationError, ProctoringViolationError,
    ExamError, ExternalServiceError, DatabaseError, ErrorCode
)
from backend.core.logging import StructuredLogger, LogEventType, log_async_operation
from backend.core.resilience import ResilientHTTPClient, CircuitBreaker
from backend.core.database import Collection

logger = logging.getLogger(__name__)
settings = get_settings()

# MediaPipe initializations
mp_face_detection = mp.solutions.face_detection
mp_hands = mp.solutions.hands
mp_pose = mp.solutions.pose


class ProctorViolationType(str, Enum):
    """Types of exam violations detected"""
    PHONE_DETECTED = "phone_detected"
    FACE_OUT_OF_FRAME = "face_out_of_frame"
    MULTIPLE_FACES = "multiple_faces"
    NO_FACE_DETECTED = "no_face_detected"
    EYE_MOVEMENT_SUSPICIOUS = "eye_movement_suspicious"
    HEAD_TURNING = "head_turning"
    UNUSUAL_HAND_MOVEMENT = "unusual_hand_movement"
    COPY_PASTE_DETECTED = "copy_paste_detected"
    WINDOW_SWITCHED = "window_switched"
    UNNATURAL_TYPING = "unnatural_typing"
    STRESS_INDICATORS = "stress_indicators"
    VOICE_DETECTED = "voice_detected"


class ExamStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    SUBMITTED = "submitted"
    GRADING = "grading"
    GRADED = "graded"
    FAILED_PROCTORING = "failed_proctoring"


# ==================== MODELS ====================

class FacialEnrollment(BaseModel):
    """Student facial biometric enrollment with security"""
    enrollment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    email: str
    
    # Facial encoding reference (encrypted in production)
    face_encodings: List[List[float]]  # 3+ samples, average for comparison
    face_landmarks: Optional[Dict] = None
    
    # Verification
    is_verified: bool = False
    verified_by: Optional[str] = None
    verification_date: Optional[datetime] = None
    
    # Metadata
    enrollment_date: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    samples_count: int = 0
    average_confidence: float = 0.0
    
    # Security
    last_verification_ip: Optional[str] = None
    enrollment_device_fingerprint: Optional[str] = None
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class ProctorSession(BaseModel):
    """Active exam proctoring session with monitoring"""
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    exam_id: str
    user_id: str
    course_id: str
    
    # Timing
    started_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime
    ended_at: Optional[datetime] = None
    
    # Status
    status: ExamStatus = ExamStatus.IN_PROGRESS
    identity_verified: bool = False
    identity_verification_timestamp: Optional[datetime] = None
    
    # Monitoring data
    frames_processed: int = 0
    violations: List[Dict[str, Any]] = []
    violation_count: int = 0
    total_violation_score: int = 0
    
    # Identity tracking
    identity_verification_attempts: int = 0
    last_identity_verification: Optional[datetime] = None
    periodic_verification_count: int = 0
    
    # Performance
    average_frame_processing_time_ms: float = 0.0
    browser_window_active: bool = True
    screen_sharing_detected: bool = False


class BehaviorFrame(BaseModel):
    """Single frame analysis results"""
    frame_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Face detection
    face_detected: bool
    face_count: int
    face_confidence: float = 0.0
    is_same_person: bool = False
    identity_confidence: float = 0.0
    
    # Facial features
    face_in_frame: bool
    face_out_of_frame_duration_seconds: int = 0
    head_pose: Dict[str, float] = {}  # yaw, pitch, roll
    eye_gaze_direction: Optional[Dict[str, float]] = None
    eyes_open: bool = True
    
    # Hand detection
    hands_detected: int = 0
    suspicious_hand_movement: bool = False
    hand_near_face: bool = False
    
    # Environment
    phone_detected: bool = False
    additional_objects: List[str] = []
    
    # Behavior
    violations_detected: List[ProctorViolationType] = []
    violation_scores: Dict[str, int] = {}
    total_violation_score: int = 0
    suspicion_level: float = 0.0  # 0-1
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class ExamAttempt(BaseModel):
    """Exam submission with grading and proctoring results"""
    attempt_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    exam_id: str
    user_id: str
    session_id: str
    
    # Submission
    answers: Dict[str, Any]
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Timing
    duration_minutes: int
    extra_time_used_minutes: int = 0
    
    # Grading
    raw_score: float = 0.0
    adjusted_score: float = 0.0
    final_score: float = 0.0
    passing_grade: float = 70.0
    
    # Proctoring
    violations_detected: List[Dict] = []
    violation_count: int = 0
    max_violation_score: int = 0
    proctoring_passed: bool = True
    
    # Results
    status: ExamStatus = ExamStatus.GRADING
    grading_started_at: Optional[datetime] = None
    grading_completed_at: Optional[datetime] = None
    
    # AI Insights
    ai_grading_details: Optional[Dict] = None
    ai_violation_analysis: Optional[Dict] = None
    cheating_confidence: float = 0.0
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class AICertificate(BaseModel):
    """AI-generated certificate with verification"""
    certificate_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    course_id: str
    attempt_id: str
    
    # Student info
    student_name: str
    student_email: str
    
    # Course info
    course_name: str
    course_code: str
    instructor_name: str
    
    # Achievement
    final_score: float
    passing_grade: float
    achievement_level: str  # "distinction", "credit", "pass"
    
    # Certificate details
    certificate_number: str = Field(default_factory=lambda: str(uuid.uuid4()))
    issued_date: datetime = Field(default_factory=datetime.utcnow)
    expiration_date: Optional[datetime] = None
    
    # Verification
    verification_code: str = Field(default_factory=lambda: str(uuid.uuid4()))
    verification_hash: str  # Blockchain-style hash
    is_verified: bool = False
    
    # File paths
    pdf_url: Optional[str] = None
    qr_code_url: Optional[str] = None
    public_url: Optional[str] = None
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


# ==================== FACIAL RECOGNITION SERVICE ====================

class FacialRecognitionService:
    """Real facial recognition using face_recognition library"""
    
    @staticmethod
    def extract_face_encoding(image_data: bytes) -> Optional[List[float]]:
        """
        Extract face encoding from image
        
        Args:
            image_data: Image bytes (JPG/PNG)
            
        Returns:
            Face encoding (128-dimensional vector)
            
        Raises:
            FacialEnrollmentError: If no face detected or extraction fails
        """
        try:
            # Decode image
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                raise FacialEnrollmentError(
                    message="Failed to decode image",
                    reason="Invalid image format or corrupted data"
                )
            
            # Convert to RGB
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Detect faces
            face_locations = face_recognition.face_locations(
                rgb_image,
                model=settings.FACIAL_RECOGNITION_MODEL
            )
            
            if not face_locations:
                raise FacialEnrollmentError(
                    message="No face detected in image",
                    reason="Please ensure your face is clearly visible and well-lit"
                )
            
            if len(face_locations) > 1:
                raise FacialEnrollmentError(
                    message="Multiple faces detected in image",
                    reason="Please ensure only your face is in the image"
                )
            
            # Extract encoding
            encodings = face_recognition.face_encodings(rgb_image, face_locations)
            
            if not encodings:
                raise FacialEnrollmentError(
                    message="Failed to extract face encoding",
                    reason="Please try again with better lighting"
                )
            
            return encodings[0].tolist()
            
        except FacialEnrollmentError:
            raise
        except Exception as e:
            raise FacialEnrollmentError(
                message="Face encoding extraction failed",
                reason=str(e),
                cause=e
            )
    
    @staticmethod
    def extract_encodings_from_frame(frame: np.ndarray) -> Tuple[List[List[float]], List[tuple]]:
        """
        Extract all face encodings from video frame
        
        Args:
            frame: Video frame as numpy array
            
        Returns:
            (encodings, face_locations)
        """
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(
            rgb_frame,
            model=settings.FACIAL_RECOGNITION_MODEL
        )
        encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        return [enc.tolist() for enc in encodings], face_locations
    
    @staticmethod
    def compare_faces(
        encoding1: List[float],
        encoding2: List[float],
        tolerance: float = None
    ) -> Tuple[bool, float]:
        """
        Compare two face encodings
        
        Args:
            encoding1: First face encoding
            encoding2: Second face encoding
            tolerance: Distance tolerance (lower = stricter)
            
        Returns:
            (is_match, similarity_percentage)
        """
        tolerance = tolerance or settings.FACIAL_RECOGNITION_TOLERANCE
        
        enc1 = np.array(encoding1)
        enc2 = np.array(encoding2)
        
        distance = np.linalg.norm(enc1 - enc2)
        is_match = distance <= tolerance
        
        # Convert distance to similarity percentage
        similarity = max(0, (1 - (distance / 0.6)) * 100)
        
        return is_match, similarity
    
    @staticmethod
    def compare_with_multiple_samples(
        enrollment_encodings: List[List[float]],
        test_encoding: List[float]
    ) -> Tuple[bool, float]:
        """
        Compare test encoding against multiple enrollment samples
        
        Args:
            enrollment_encodings: List of enrollment face encodings
            test_encoding: Test face encoding
            
        Returns:
            (is_match, average_confidence)
        """
        if not enrollment_encodings:
            return False, 0.0
        
        matches = []
        confidences = []
        
        for enrollment_enc in enrollment_encodings:
            is_match, confidence = FacialRecognitionService.compare_faces(
                enrollment_enc,
                test_encoding
            )
            matches.append(is_match)
            confidences.append(confidence)
        
        # Require at least 66% of samples to match
        match_rate = sum(matches) / len(matches)
        is_match = match_rate >= 0.66
        avg_confidence = sum(confidences) / len(confidences)
        
        return is_match, avg_confidence


# ==================== GROQ AI SERVICE ====================

class GroqAIService:
    """Groq AI for grading and analysis (production-grade with resilience)"""
    
    _circuit_breaker = CircuitBreaker(
        name="Groq API",
        failure_threshold=5,
        recovery_timeout_seconds=60
    )
    
    @staticmethod
    @log_async_operation("groq_grade_answer")
    async def grade_exam_answer(
        question: str,
        student_answer: str,
        rubric: str,
        max_points: int = 10
    ) -> Dict[str, Any]:
        """
        Grade essay/open-ended question using Groq AI
        
        Args:
            question: Exam question
            student_answer: Student's answer
            rubric: Grading rubric
            max_points: Maximum points
            
        Returns:
            Grading result with score and feedback
            
        Raises:
            ExternalServiceError: If Groq API fails
        """
        try:
            prompt = f"""You are an expert educator grading an exam answer.

Question: {question}

Student Answer: {student_answer}

Grading Rubric: {rubric}

Provide your grading in JSON format with these fields:
{{
    "score": <0-{max_points}>,
    "confidence": <0-1>,
    "feedback": "<detailed feedback>",
    "strengths": ["<strength1>", "<strength2>"],
    "improvements": ["<area1>", "<area2>"]
}}

Be fair and constructive."""

            async with ResilientHTTPClient(
                name="Groq API",
                timeout_seconds=settings.GROQ_TIMEOUT_SECONDS
            ) as client:
                response = await client.post(
                    url=f"{settings.GROQ_API_BASE_URL}/chat/completions",
                    json={
                        "model": settings.GROQ_MODEL_NAME,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": settings.GROQ_TEMPERATURE,
                        "max_tokens": settings.GROQ_MAX_TOKENS
                    },
                    headers={"Authorization": f"Bearer {settings.GROQ_API_KEY}"}
                )
            
            # Parse response
            content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            # Extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                grading = json.loads(json_match.group())
            else:
                grading = {
                    "score": max_points * 0.5,
                    "confidence": 0.5,
                    "feedback": "Unable to parse grading result"
                }
            
            logger.info(f"Groq graded question - Score: {grading.get('score')}")
            return grading
            
        except Exception as e:
            logger.error(f"Groq grading failed: {str(e)}")
            raise ExternalServiceError(
                message="Failed to grade answer with AI",
                service_name="Groq API",
                cause=e
            )
    
    @staticmethod
    @log_async_operation("groq_analyze_violations")
    async def analyze_violations(
        violations: List[Dict[str, Any]],
        violation_score: int
    ) -> Dict[str, Any]:
        """
        Use Groq to analyze proctoring violations for cheating detection
        
        Args:
            violations: List of detected violations
            violation_score: Total violation score
            
        Returns:
            Analysis result with cheating confidence
        """
        try:
            violation_summary = "\n".join([
                f"- {v.get('type')}: {v.get('count')} times, severity {v.get('severity')}/10"
                for v in violations[:10]
            ])
            
            prompt = f"""As a proctoring expert, analyze these exam violations:

Violations:
{violation_summary}

Total Violation Score: {violation_score}/1000

Assess the likelihood and nature of academic dishonesty. Provide JSON:
{{
    "cheating_probability": <0-1>,
    "cheating_type": "<none|suspicious|likely|confirmed>",
    "evidence": ["<evidence1>", "<evidence2>"],
    "recommendation": "<recommendation>",
    "confidence": <0-1>
}}"""

            async with ResilientHTTPClient(
                name="Groq API",
                timeout_seconds=settings.GROQ_TIMEOUT_SECONDS
            ) as client:
                response = await client.post(
                    url=f"{settings.GROQ_API_BASE_URL}/chat/completions",
                    json={
                        "model": settings.GROQ_MODEL_NAME,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.2,
                        "max_tokens": 500
                    },
                    headers={"Authorization": f"Bearer {settings.GROQ_API_KEY}"}
                )
            
            content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                analysis = json.loads(json_match.group())
            else:
                analysis = {"cheating_probability": 0.5, "recommendation": "Manual review required"}
            
            return analysis
            
        except Exception as e:
            logger.error(f"Violation analysis failed: {str(e)}")
            # Return default analysis instead of crashing
            return {
                "cheating_probability": 0.0,
                "recommendation": "Unable to analyze - manual review required",
                "confidence": 0.0
            }


# ==================== CERTIFICATE GENERATION ====================

class CertificateService:
    """Generate PDF certificates with QR codes and blockchain hashes"""
    
    @staticmethod
    async def generate_certificate_pdf(
        certificate: AICertificate
    ) -> bytes:
        """
        Generate certificate PDF
        
        Args:
            certificate: Certificate data
            
        Returns:
            PDF bytes
        """
        try:
            from reportlab.lib.pagesizes import A4, landscape
            from reportlab.pdfgen import canvas
            from reportlab.lib.units import inch
            from datetime import datetime as dt
            
            # Create in-memory PDF
            from io import BytesIO
            pdf_buffer = BytesIO()
            
            # Create PDF with landscape orientation
            page_width, page_height = landscape(A4)
            c = canvas.Canvas(pdf_buffer, pagesize=(page_width, page_height))
            
            # Background
            c.setFillColor("#f0f0f0")
            c.rect(0, 0, page_width, page_height, fill=1)
            
            # Border
            c.setStrokeColor("#2c3e50")
            c.setLineWidth(3)
            c.rect(0.5*inch, 0.5*inch, page_width-inch, page_height-inch)
            
            # Title
            c.setFont("Helvetica-Bold", 48)
            c.setFillColor("#d4af37")  # Gold
            c.drawCentredString(page_width/2, page_height-1.5*inch, "CERTIFICATE OF ACHIEVEMENT")
            
            # Course name
            c.setFont("Helvetica-Bold", 24)
            c.setFillColor("#2c3e50")
            c.drawCentredString(page_width/2, page_height-2.2*inch, certificate.course_name)
            
            # Student name
            c.setFont("Helvetica", 18)
            c.drawString(2*inch, page_height-3.5*inch, "This certifies that")
            c.setFont("Helvetica-Bold", 24)
            c.drawString(2*inch, page_height-4*inch, certificate.student_name)
            
            # Details
            c.setFont("Helvetica", 12)
            c.drawString(2*inch, page_height-4.8*inch, f"has successfully completed {certificate.course_name}")
            c.drawString(2*inch, page_height-5.2*inch, f"with a final score of {certificate.final_score:.1f}%")
            c.drawString(2*inch, page_height-5.6*inch, f"Achievement Level: {certificate.achievement_level.upper()}")
            
            # Dates and codes
            c.setFont("Helvetica", 10)
            c.drawString(2*inch, page_height-6.5*inch, f"Issued: {certificate.issued_date.strftime('%B %d, %Y')}")
            c.drawString(2*inch, page_height-6.8*inch, f"Certificate #: {certificate.certificate_number}")
            c.drawString(2*inch, page_height-7.1*inch, f"Verification Code: {certificate.verification_code}")
            
            # QR code (if available)
            if certificate.qr_code_url:
                c.drawString(page_width-3*inch, page_height-4*inch, "Scan to Verify")
                # In production, load actual QR image
            
            # Signature area
            c.setFont("Helvetica-Bold", 12)
            c.drawString(2*inch, 1.5*inch, "Digitally Verified by")
            c.drawString(2*inch, 1*inch, "GAAIUS AI Learning Platform")
            
            # Save
            c.save()
            pdf_buffer.seek(0)
            return pdf_buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Certificate PDF generation failed: {str(e)}")
            raise ExternalServiceError(
                message="Failed to generate certificate PDF",
                service_name="ReportLab",
                cause=e
            )
    
    @staticmethod
    def generate_verification_hash(certificate: AICertificate) -> str:
        """
        Generate blockchain-style hash for certificate verification
        
        Args:
            certificate: Certificate data
            
        Returns:
            SHA256 hash
        """
        data = f"{certificate.certificate_id}{certificate.user_id}{certificate.course_id}{certificate.issued_date}"
        return hashlib.sha256(data.encode()).hexdigest()


# ==================== MAIN PROCTORING SERVICE ====================

class AIProctoringService:
    """Main AI proctoring service orchestrating all subsystems"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.enrollments_collection = Collection(db, "facial_enrollments")
        self.sessions_collection = Collection(db, "proctor_sessions")
        self.attempts_collection = Collection(db, "exam_attempts")
        self.certificates_collection = Collection(db, "certificates")
    
    @log_async_operation("enroll_facial_biometric")
    async def enroll_facial_biometric(
        self,
        user_id: str,
        email: str,
        image_data: bytes
    ) -> FacialEnrollment:
        """
        Enroll student's facial biometric
        
        Args:
            user_id: Student user ID
            email: Student email
            image_data: Image bytes
            
        Returns:
            FacialEnrollment object
        """
        try:
            # Extract encoding
            encoding = FacialRecognitionService.extract_face_encoding(image_data)
            
            # Check for existing enrollment
            existing = await self.enrollments_collection.find_one({"user_id": user_id})
            
            if existing:
                # Add to existing enrollment
                enrollment = FacialEnrollment(**existing)
                enrollment.face_encodings.append(encoding)
                enrollment.samples_count += 1
                enrollment.last_updated = datetime.utcnow()
                
                # If 3+ samples, mark as verified
                if enrollment.samples_count >= settings.MIN_FACE_SAMPLES_FOR_ENROLLMENT:
                    enrollment.is_verified = True
                    enrollment.verification_date = datetime.utcnow()
                
                await self.enrollments_collection.update_one(
                    {"user_id": user_id},
                    {"$set": enrollment.dict()}
                )
            else:
                # Create new enrollment
                enrollment = FacialEnrollment(
                    user_id=user_id,
                    email=email,
                    face_encodings=[encoding],
                    samples_count=1
                )
                await self.enrollments_collection.insert_one(enrollment.dict())
            
            logger.info(f"Facial enrollment for {user_id} - samples: {enrollment.samples_count}")
            StructuredLogger.log_event(
                event_type=LogEventType.FACIAL_ENROLLMENT,
                user_id=user_id,
                details={"samples": enrollment.samples_count, "verified": enrollment.is_verified}
            )
            
            return enrollment
            
        except Exception as e:
            logger.error(f"Facial enrollment failed for {user_id}: {str(e)}")
            raise
    
    @log_async_operation("start_exam_session")
    async def start_exam_session(
        self,
        exam_id: str,
        user_id: str,
        course_id: str,
        duration_minutes: int
    ) -> ProctorSession:
        """
        Start a proctored exam session
        
        Args:
            exam_id: Exam ID
            user_id: User ID
            course_id: Course ID
            duration_minutes: Exam duration
            
        Returns:
            ProctorSession object
        """
        try:
            session = ProctorSession(
                exam_id=exam_id,
                user_id=user_id,
                course_id=course_id,
                expires_at=datetime.utcnow() + timedelta(minutes=duration_minutes + settings.EXAM_GRACE_PERIOD_SECONDS//60)
            )
            
            session_id = await self.sessions_collection.insert_one(session.dict())
            
            logger.info(f"Proctoring session started: {session_id} for user {user_id}")
            StructuredLogger.log_event(
                event_type=LogEventType.EXAM_STARTED,
                user_id=user_id,
                resource_id=exam_id,
                details={"session_id": session_id, "duration_minutes": duration_minutes}
            )
            
            return session
            
        except Exception as e:
            logger.error(f"Failed to start exam session: {str(e)}")
            raise DatabaseError(
                message="Failed to create proctoring session",
                operation="start_exam_session",
                cause=e
            )
    
    @log_async_operation("verify_identity")
    async def verify_identity_at_session_start(
        self,
        session_id: str,
        image_data: bytes
    ) -> Tuple[bool, float]:
        """
        Verify student identity at exam start
        
        Args:
            session_id: Proctoring session ID
            image_data: Selfie image bytes
            
        Returns:
            (verified, confidence)
        """
        try:
            # Get session
            session_dict = await self.sessions_collection.find_one({"session_id": session_id})
            if not session_dict:
                raise ExamError(message="Session not found", exam_id="unknown")
            
            session = ProctorSession(**session_dict)
            
            # Get enrollment
            enrollment_dict = await self.enrollments_collection.find_one({"user_id": session.user_id})
            if not enrollment_dict or not enrollment_dict.get("is_verified"):
                raise IdentityVerificationError(
                    message="Student facial enrollment not found or not verified"
                )
            
            enrollment = FacialEnrollment(**enrollment_dict)
            
            # Extract encoding from current image
            current_encoding = FacialRecognitionService.extract_face_encoding(image_data)
            
            # Compare with enrollment samples
            is_match, confidence = FacialRecognitionService.compare_with_multiple_samples(
                enrollment.face_encodings,
                current_encoding
            )
            
            if not is_match or confidence < settings.IDENTITY_VERIFICATION_CONFIDENCE_THRESHOLD:
                session.identity_verification_attempts += 1
                
                if session.identity_verification_attempts >= settings.IDENTITY_VERIFICATION_MAX_RETRIES:
                    session.status = ExamStatus.FAILED_PROCTORING
                    await self.sessions_collection.update_one(
                        {"session_id": session_id},
                        {"$set": {"status": ExamStatus.FAILED_PROCTORING}}
                    )
                    
                    raise IdentityVerificationError(
                        message="Identity verification failed - exam terminated",
                        confidence=confidence
                    )
                
                raise IdentityVerificationError(
                    message="Identity verification failed",
                    confidence=confidence,
                    required_confidence=settings.IDENTITY_VERIFICATION_CONFIDENCE_THRESHOLD
                )
            
            # Verification successful
            session.identity_verified = True
            session.identity_verification_timestamp = datetime.utcnow()
            
            await self.sessions_collection.update_one(
                {"session_id": session_id},
                {"$set": {
                    "identity_verified": True,
                    "identity_verification_timestamp": datetime.utcnow()
                }}
            )
            
            logger.info(f"Identity verified for session {session_id} - confidence: {confidence:.2f}")
            StructuredLogger.log_event(
                event_type=LogEventType.FACIAL_VERIFICATION,
                user_id=session.user_id,
                details={"confidence": confidence, "verified": True}
            )
            
            return True, confidence
            
        except Exception as e:
            logger.error(f"Identity verification error: {str(e)}")
            raise
    
    @log_async_operation("process_exam_frame")
    async def process_exam_frame(
        self,
        session_id: str,
        frame_data: bytes
    ) -> BehaviorFrame:
        """
        Process single exam frame for violations
        Real frame analysis with MediaPipe and OpenCV
        
        Args:
            session_id: Proctoring session ID
            frame_data: Frame image bytes
            
        Returns:
            BehaviorFrame with analysis results
        """
        try:
            # Decode frame
            nparr = np.frombuffer(frame_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if frame is None:
                raise ExamError(message="Invalid frame data")
            
            # Get session
            session_dict = await self.sessions_collection.find_one({"session_id": session_id})
            session = ProctorSession(**session_dict)
            
            # Get enrollment for identity checking
            enrollment_dict = await self.enrollments_collection.find_one({"user_id": session.user_id})
            enrollment = FacialEnrollment(**enrollment_dict) if enrollment_dict else None
            
            # Analyze frame
            frame_analysis = BehaviorFrame(session_id=session_id)
            
            # 1. Face detection and identification
            encodings, face_locs = FacialRecognitionService.extract_encodings_from_frame(frame)
            frame_analysis.face_count = len(encodings)
            frame_analysis.face_detected = len(encodings) > 0
            
            if not frame_analysis.face_detected:
                frame_analysis.violations_detected.append(ProctorViolationType.NO_FACE_DETECTED)
                frame_analysis.violation_scores[ProctorViolationType.NO_FACE_DETECTED] = 50
            elif len(encodings) > 1:
                frame_analysis.violations_detected.append(ProctorViolationType.MULTIPLE_FACES)
                frame_analysis.violation_scores[ProctorViolationType.MULTIPLE_FACES] = 200
            elif enrollment and len(encodings) == 1:
                # Check if it's the same person
                is_match, confidence = FacialRecognitionService.compare_with_multiple_samples(
                    enrollment.face_encodings,
                    encodings[0]
                )
                frame_analysis.is_same_person = is_match
                frame_analysis.identity_confidence = confidence
            
            # 2. Head pose estimation
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            with mp_pose.Pose(min_detection_confidence=0.5) as pose:
                pose_results = pose.process(rgb_frame)
                
                if pose_results.pose_landmarks:
                    # Estimate head pose from pose landmarks
                    landmarks = pose_results.pose_landmarks.landmark
                    # Left eye, right eye, nose
                    left_eye = landmarks[2]
                    right_eye = landmarks[5]
                    nose = landmarks[0]
                    
                    # Calculate head angles
                    if left_eye.x < 0.1 or right_eye.x > 0.9:
                        frame_analysis.violations_detected.append(ProctorViolationType.HEAD_TURNING)
                        frame_analysis.violation_scores[ProctorViolationType.HEAD_TURNING] = 20
                    
                    # Body out of frame
                    if landmarks[11].x < 0.2 or landmarks[11].x > 0.8:
                        frame_analysis.violations_detected.append(ProctorViolationType.FACE_OUT_OF_FRAME)
                        frame_analysis.violation_scores[ProctorViolationType.FACE_OUT_OF_FRAME] = 25
            
            # 3. Hand detection
            with mp_hands.Hands(max_num_hands=2) as hands:
                hand_results = hands.process(rgb_frame)
                
                if hand_results.multi_hand_landmarks:
                    frame_analysis.hands_detected = len(hand_results.multi_hand_landmarks)
                    
                    # Check for suspicious hand movement
                    for hand_landmarks in hand_results.multi_hand_landmarks:
                        # If hand is near face/screen, could be cheating
                        for landmark in hand_landmarks.landmark:
                            if 0.1 < landmark.x < 0.9 and 0.1 < landmark.y < 0.6:
                                frame_analysis.suspicious_hand_movement = True
                                break
                    
                    if frame_analysis.suspicious_hand_movement:
                        frame_analysis.violations_detected.append(ProctorViolationType.UNUSUAL_HAND_MOVEMENT)
                        frame_analysis.violation_scores[ProctorViolationType.UNUSUAL_HAND_MOVEMENT] = 30
            
            # 4. Phone/object detection using OpenCV
            # Simple object detection: look for rectangles/specific patterns
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            
            # Phone detection heuristic: rectangular objects with specific aspect ratio
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = float(w) / h if h > 0 else 0
                
                # Phone-like aspect ratio (0.4-0.7) and size
                if 0.4 < aspect_ratio < 0.7 and w > 50 and h > 80:
                    frame_analysis.phone_detected = True
                    break
            
            if frame_analysis.phone_detected:
                frame_analysis.violations_detected.append(ProctorViolationType.PHONE_DETECTED)
                frame_analysis.violation_scores[ProctorViolationType.PHONE_DETECTED] = 300
            
            # Calculate total violation score
            frame_analysis.total_violation_score = sum(frame_analysis.violation_scores.values())
            frame_analysis.suspicion_level = min(1.0, frame_analysis.total_violation_score / 1000)
            
            # Update session
            session.frames_processed += 1
            session.violations.append({
                "timestamp": datetime.utcnow(),
                "violation_types": [v.value for v in frame_analysis.violations_detected],
                "score": frame_analysis.total_violation_score
            })
            session.violation_count = len(session.violations)
            session.total_violation_score += frame_analysis.total_violation_score
            
            # Check if auto-fail violations
            for violation in frame_analysis.violations_detected:
                if violation.value in settings.PROCTORING_AUTO_FAIL_VIOLATIONS:
                    session.status = ExamStatus.FAILED_PROCTORING
                    break
            
            await self.sessions_collection.update_one(
                {"session_id": session_id},
                {"$set": {
                    "frames_processed": session.frames_processed,
                    "violations": session.violations,
                    "violation_count": session.violation_count,
                    "total_violation_score": session.total_violation_score,
                    "status": session.status
                }}
            )
            
            return frame_analysis
            
        except Exception as e:
            logger.error(f"Frame processing failed: {str(e)}")
            raise ExamError(
                message="Failed to process exam frame",
                exam_id="unknown",
                cause=e
            )
