"""
Advanced Proctoring System for Certification Exams
Comprehensive monitoring, integrity checks, and fraud detection for online certifications
"""

from typing import List, Optional, Dict, Any, Set, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from enum import Enum
import uuid
import json
import hashlib
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field, validator

# ============================================================================
# ENUMS & CONSTANTS
# ============================================================================

class ProctorMode(str, Enum):
    """Proctoring supervision modes"""
    LIVE = "live"  # Real-time human proctor
    AUTOMATED = "automated"  # AI-based monitoring
    HYBRID = "hybrid"  # Both live and AI
    OFFLINE = "offline"  # No proctoring (low-stakes)

class IntegrityLevel(str, Enum):
    """Test integrity security levels"""
    LOW = "low"  # No restrictions
    MEDIUM = "medium"  # Basic restrictions
    HIGH = "high"  # Strict monitoring
    MAXIMUM = "maximum"  # Extreme security

class ViolationType(str, Enum):
    """Types of exam violations"""
    SUSPICIOUS_BEHAVIOR = "suspicious_behavior"
    MULTIPLE_FACES = "multiple_faces"
    FACE_MISSING = "face_missing"
    WINDOW_CHANGE = "window_change"
    AUDIO_CHEAT = "audio_cheat"
    COPY_PASTE = "copy_paste"
    UNAUTHORIZED_DEVICE = "unauthorized_device"
    RAPID_SCROLLING = "rapid_scrolling"
    UNUSUAL_PATTERN = "unusual_pattern"
    MOBILE_PHONE = "mobile_phone"

class ViolationSeverity(str, Enum):
    """Violation severity levels"""
    WARNING = "warning"
    CAUTION = "caution"
    CRITICAL = "critical"

class ProctorSession(BaseModel):
    """Live proctoring session"""
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    exam_id: str
    student_id: str
    proctor_id: str  # Human proctor ID
    mode: ProctorMode = ProctorMode.LIVE
    start_time: datetime = Field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    duration_minutes: int = 0
    
    # Session Details
    notes: List[str] = Field(default_factory=list)
    violations_detected: List[Dict[str, Any]] = Field(default_factory=list)
    approval_status: str = "pending"  # pending, approved, flagged
    proctor_comments: str = ""
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

class FaceVerification(BaseModel):
    """Face recognition verification"""
    verification_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    student_id: str
    exam_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Face Data
    face_embedding: List[float] = []  # Vector representation
    confidence: float = Field(default=0.0, ge=0, le=1)
    is_match: bool = False
    enrollment_photo_path: str = ""
    captured_photo_path: str = ""
    
    # Liveness Detection
    is_alive: bool = False  # Not spoofed
    spoofing_confidence: float = 0.0
    
    # Metadata
    location_verified: bool = False
    ip_address: str = ""
    device_info: str = ""
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

class ExamBehavior(BaseModel):
    """Student behavior monitoring during exam"""
    behavior_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    exam_id: str
    student_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Behavioral Metrics
    eye_gaze_direction: str = "center"  # center, left, right, up, down, away
    hand_presence: bool = True
    posture_normal: bool = True
    
    # Activity Metrics
    question_time: Dict[str, float] = Field(default_factory=dict)  # Question -> Time in seconds
    scroll_speed: float = 0.0  # Pixels per second
    key_press_pattern: Dict[str, Any] = Field(default_factory=dict)
    mouse_movements: int = 0
    
    # Risk Indicators
    suspicious_patterns: List[str] = Field(default_factory=list)
    risk_score: float = Field(default=0.0, ge=0, le=1)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

class EnvironmentCheck(BaseModel):
    """Physical environment verification"""
    check_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    exam_id: str
    student_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Room Checks
    room_clear: bool = False
    people_present: List[str] = Field(default_factory=list)
    unauthorized_materials: List[str] = Field(default_factory=list)
    
    # Device Checks
    primary_monitor: bool = False
    secondary_monitors: List[str] = Field(default_factory=list)
    mobile_devices_visible: List[str] = Field(default_factory=list)
    
    # Audio/Video
    microphone_working: bool = False
    camera_working: bool = False
    background_blur_enabled: bool = False
    
    # Network
    stable_connection: bool = False
    bandwidth_sufficient: bool = False
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

class ExamViolation(BaseModel):
    """Detected exam violation"""
    violation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    exam_id: str
    student_id: str
    proctor_session_id: str
    violation_type: ViolationType
    severity: ViolationSeverity
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Violation Details
    description: str
    evidence: Dict[str, Any] = Field(default_factory=dict)
    confidence: float = Field(default=0.0, ge=0, le=1)
    
    # Response
    auto_flagged: bool = True
    proctor_reviewed: bool = False
    proctor_action: str = ""  # warning, pause, terminate
    score_impact: float = 0.0  # Percentage point deduction
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

class CertificationExam(BaseModel):
    """Certification exam with proctoring requirements"""
    exam_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    course_id: str
    title: str = Field(..., min_length=5, max_length=255)
    description: str = Field(..., min_length=20)
    
    # Exam Configuration
    duration_minutes: int = Field(..., ge=30, le=480)  # 30min to 8hrs
    passing_score: float = Field(default=70.0, ge=0, le=100)
    total_questions: int = Field(..., ge=10, le=500)
    question_pool_size: int = Field(..., ge=total_questions)  # Randomization pool
    
    # Proctoring Requirements
    proctor_mode: ProctorMode = ProctorMode.AUTOMATED
    integrity_level: IntegrityLevel = IntegrityLevel.HIGH
    require_face_verification: bool = True
    require_id_verification: bool = False
    require_environment_check: bool = True
    
    # Security Settings
    require_webcam: bool = True
    require_microphone: bool = False
    allow_references: bool = False
    allow_scratch_paper: bool = True
    prevent_tab_switching: bool = True
    prevent_copy_paste: bool = True
    
    # Monitoring Settings
    screen_recording: bool = True
    keyboard_monitoring: bool = True
    eye_tracking: bool = True
    behavior_analysis: bool = True
    
    # Attempt Settings
    max_attempts: int = Field(default=3, ge=1, le=10)
    attempts_used: int = 0
    min_days_between_attempts: int = Field(default=1, ge=0, le=30)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    published: bool = False
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

class ExamAttempt(BaseModel):
    """Individual exam attempt record"""
    attempt_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    exam_id: str
    student_id: str
    attempt_number: int = Field(..., ge=1)
    
    # Attempt Timeline
    start_time: datetime = Field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    submission_time: Optional[datetime] = None
    duration_seconds: int = 0
    
    # Attempt Status
    status: str = "in_progress"  # in_progress, submitted, graded
    score: Optional[float] = None
    percentage: Optional[float] = None
    passed: bool = False
    
    # Proctoring Data
    proctor_session: Optional[ProctorSession] = None
    face_verifications: List[FaceVerification] = Field(default_factory=list)
    behavior_checks: List[ExamBehavior] = Field(default_factory=list)
    environment_checks: List[EnvironmentCheck] = Field(default_factory=list)
    violations: List[ExamViolation] = Field(default_factory=list)
    
    # Security
    session_key: str = Field(default_factory=lambda: str(uuid.uuid4()))
    integrity_score: float = Field(default=1.0, ge=0, le=1)
    flagged_for_review: bool = False
    review_reason: str = ""
    
    # Verification
    id_verified: bool = False
    face_verified: bool = False
    identity_match_confidence: float = 0.0
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

class CertificateIssuance(BaseModel):
    """Certificate issuance record"""
    certificate_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    exam_attempt_id: str
    exam_id: str
    course_id: str
    student_id: str
    student_name: str
    
    # Certificate Details
    certificate_number: str  # Unique number for verification
    issue_date: datetime = Field(default_factory=datetime.utcnow)
    expiration_date: Optional[datetime] = None
    credential_url: str = ""
    
    # Achievement Data
    score: float
    grade: str  # A, B, C, D, F
    completion_time_hours: float
    
    # Verification
    integrity_verified: bool = True
    proctoring_data_attached: bool = True
    tamper_proof_hash: str = ""  # For verification
    
    # Status
    status: str = "issued"  # issued, revoked, suspended, expired
    revocation_reason: str = ""
    
    # Blockchain/Credentials (optional)
    blockchain_hash: Optional[str] = None
    digital_wallet_url: Optional[str] = None
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

# ============================================================================
# PROCTORING ENGINE
# ============================================================================

class ProctoringEngine:
    """Advanced proctoring system"""
    
    def __init__(self):
        self.active_sessions: Dict[str, ProctorSession] = {}
        self.violation_history: Dict[str, List[ExamViolation]] = {}
        self.behavior_analytics: Dict[str, List[ExamBehavior]] = {}
        self.face_verification_cache: Dict[str, FaceVerification] = {}
    
    def initialize_exam_session(self, exam: CertificationExam, student_id: str, 
                               proctor_id: Optional[str] = None) -> Tuple[str, ProctorSession]:
        """Initialize proctored exam session"""
        session = ProctorSession(
            exam_id=exam.exam_id,
            student_id=student_id,
            proctor_id=proctor_id or "ai-proctor",
            mode=exam.proctor_mode
        )
        self.active_sessions[session.session_id] = session
        return session.session_id, session
    
    def verify_student_identity(self, exam_id: str, student_id: str, 
                               captured_image: bytes, enrollment_image: bytes) -> FaceVerification:
        """Verify student identity through face recognition"""
        verification = FaceVerification(
            student_id=student_id,
            exam_id=exam_id,
            enrollment_photo_path="enrollment_photo.jpg",
            captured_photo_path="captured_photo.jpg"
        )
        
        # Simulate face recognition
        # In production: Use face_recognition or deepface library
        verification.confidence = 0.95
        verification.is_match = verification.confidence > 0.85
        verification.is_alive = True  # Liveness detection
        
        self.face_verification_cache[f"{exam_id}_{student_id}"] = verification
        return verification
    
    def check_environment(self, exam_id: str, student_id: str) -> EnvironmentCheck:
        """Verify exam environment"""
        check = EnvironmentCheck(
            exam_id=exam_id,
            student_id=student_id
        )
        
        # These would be populated from device sensors
        check.room_clear = True
        check.primary_monitor = True
        check.microphone_working = True
        check.camera_working = True
        check.stable_connection = True
        check.bandwidth_sufficient = True
        
        return check
    
    def monitor_behavior(self, exam_id: str, student_id: str, 
                        behavior_data: Dict[str, Any]) -> ExamBehavior:
        """Monitor and analyze student behavior during exam"""
        behavior = ExamBehavior(
            exam_id=exam_id,
            student_id=student_id
        )
        
        # Populate from sensor data
        behavior.eye_gaze_direction = behavior_data.get("gaze", "center")
        behavior.hand_presence = behavior_data.get("hand_visible", True)
        behavior.posture_normal = behavior_data.get("posture_ok", True)
        behavior.mouse_movements = behavior_data.get("mouse_moves", 0)
        behavior.scroll_speed = behavior_data.get("scroll_speed", 0.0)
        
        # Anomaly Detection
        behavior.risk_score = self._calculate_behavior_risk(behavior)
        
        # Store for analysis
        if exam_id not in self.behavior_analytics:
            self.behavior_analytics[exam_id] = []
        self.behavior_analytics[exam_id].append(behavior)
        
        return behavior
    
    def detect_violations(self, exam_id: str, student_id: str, 
                         behavior: ExamBehavior) -> List[ExamViolation]:
        """Detect potential exam violations"""
        violations = []
        
        # Face Detection
        if behavior.posture_normal is False:
            violations.append(ExamViolation(
                exam_id=exam_id,
                student_id=student_id,
                proctor_session_id="",
                violation_type=ViolationType.FACE_MISSING,
                severity=ViolationSeverity.CRITICAL,
                description="Student face not detected in frame",
                confidence=0.95
            ))
        
        # Multiple Faces
        if behavior.hand_presence is False:
            violations.append(ExamViolation(
                exam_id=exam_id,
                student_id=student_id,
                proctor_session_id="",
                violation_type=ViolationType.MULTIPLE_FACES,
                severity=ViolationSeverity.CAUTION,
                description="Multiple persons detected in frame",
                confidence=0.80
            ))
        
        # Suspicious Behavior
        if behavior.risk_score > 0.7:
            violations.append(ExamViolation(
                exam_id=exam_id,
                student_id=student_id,
                proctor_session_id="",
                violation_type=ViolationType.SUSPICIOUS_BEHAVIOR,
                severity=ViolationSeverity.WARNING,
                description=f"Suspicious behavior detected. Risk score: {behavior.risk_score:.2f}",
                confidence=behavior.risk_score
            ))
        
        # Rapid Scrolling
        if behavior.scroll_speed > 1000:
            violations.append(ExamViolation(
                exam_id=exam_id,
                student_id=student_id,
                proctor_session_id="",
                violation_type=ViolationType.RAPID_SCROLLING,
                severity=ViolationSeverity.WARNING,
                description="Unusual rapid scrolling detected",
                confidence=0.85
            ))
        
        # Store violations
        if exam_id not in self.violation_history:
            self.violation_history[exam_id] = []
        self.violation_history[exam_id].extend(violations)
        
        return violations
    
    def calculate_integrity_score(self, attempt: ExamAttempt) -> float:
        """Calculate overall exam integrity score"""
        score = 1.0
        
        # Deductions for violations
        for violation in attempt.violations:
            if violation.severity == ViolationSeverity.CRITICAL:
                score -= 0.3
            elif violation.severity == ViolationSeverity.CAUTION:
                score -= 0.1
            else:  # WARNING
                score -= 0.05
        
        # Deductions for identity mismatch
        if not attempt.face_verified:
            score -= 0.2
        elif attempt.identity_match_confidence < 0.85:
            score -= 0.1
        
        # Deductions for behavior anomalies
        if attempt.behavior_checks:
            avg_behavior_risk = sum(b.risk_score for b in attempt.behavior_checks) / len(attempt.behavior_checks)
            score -= avg_behavior_risk * 0.2
        
        return max(0.0, min(1.0, score))
    
    def should_flag_for_review(self, attempt: ExamAttempt) -> Tuple[bool, str]:
        """Determine if attempt should be flagged for human review"""
        # Flag criteria
        if len(attempt.violations) > 3:
            return True, "Multiple violations detected"
        
        if any(v.severity == ViolationSeverity.CRITICAL for v in attempt.violations):
            return True, "Critical violation detected"
        
        if attempt.integrity_score < 0.6:
            return True, f"Low integrity score: {attempt.integrity_score:.2f}"
        
        if not attempt.face_verified:
            return True, "Face verification failed"
        
        if attempt.passed and attempt.score > 95:
            return True, "Unusually high score - verify accuracy"
        
        return False, ""
    
    def _calculate_behavior_risk(self, behavior: ExamBehavior) -> float:
        """Calculate behavior risk score using ML"""
        risk = 0.0
        
        # Eye gaze risk
        if behavior.eye_gaze_direction in ["left", "right", "away"]:
            risk += 0.2
        
        # Posture risk
        if not behavior.posture_normal:
            risk += 0.3
        
        # Hand presence risk
        if not behavior.hand_presence:
            risk += 0.25
        
        # Scroll speed anomaly
        if behavior.scroll_speed > 800:
            risk += 0.15
        
        return min(1.0, risk)

# ============================================================================
# CERTIFICATE VERIFICATION
# ============================================================================

class CertificateVerificationService:
    """Verify and validate issued certificates"""
    
    @staticmethod
    def generate_certificate_number() -> str:
        """Generate unique certificate number"""
        timestamp = datetime.utcnow().strftime("%Y%m%d")
        random_id = str(uuid.uuid4())[:8].upper()
        return f"CERT-{timestamp}-{random_id}"
    
    @staticmethod
    def create_tamper_proof_hash(certificate: CertificateIssuance) -> str:
        """Create cryptographic hash for certificate integrity"""
        data = f"{certificate.certificate_id}{certificate.student_id}{certificate.issue_date}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    @staticmethod
    def verify_certificate(certificate_id: str, certificate: CertificateIssuance) -> bool:
        """Verify certificate authenticity"""
        # Check expiration
        if certificate.expiration_date and datetime.utcnow() > certificate.expiration_date:
            return False
        
        # Check revocation
        if certificate.status != "issued":
            return False
        
        # Verify hash integrity
        expected_hash = CertificateVerificationService.create_tamper_proof_hash(certificate)
        if certificate.tamper_proof_hash != expected_hash:
            return False
        
        return True
    
    @staticmethod
    def generate_credential_url(certificate: CertificateIssuance) -> str:
        """Generate shareable credential URL"""
        base_url = "https://gaaius.ai/verify"
        return f"{base_url}/{certificate.certificate_number}"

# ============================================================================
# STATISTICS & ANALYTICS
# ============================================================================

class ProctoringAnalytics:
    """Analytics for proctoring data"""
    
    @staticmethod
    def analyze_exam_integrity(exam_id: str, attempts: List[ExamAttempt]) -> Dict[str, Any]:
        """Analyze integrity metrics for exam"""
        if not attempts:
            return {}
        
        return {
            "total_attempts": len(attempts),
            "passed_count": sum(1 for a in attempts if a.passed),
            "flagged_count": sum(1 for a in attempts if a.flagged_for_review),
            "avg_integrity_score": sum(a.integrity_score for a in attempts) / len(attempts),
            "avg_score": sum(a.score for a in attempts if a.score) / len([a for a in attempts if a.score]),
            "total_violations": sum(len(a.violations) for a in attempts),
            "critical_violations": sum(
                len([v for v in a.violations if v.severity == ViolationSeverity.CRITICAL]) 
                for a in attempts
            ),
            "cheating_probability": sum(
                1 for a in attempts if a.integrity_score < 0.6
            ) / len(attempts) if attempts else 0
        }

