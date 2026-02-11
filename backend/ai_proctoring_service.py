"""
GAAIUS AI Proctoring & Identity Verification Service
Free distance learning exam proctoring with Groq AI and facial recognition
Detects cheating, monitors behavior, validates student identity
"""

import os
import uuid
import asyncio
import base64
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from enum import Enum
import hashlib
import numpy as np

import cv2
import face_recognition
from pydantic import BaseModel, Field
import aiohttp
from motor.motor_asyncio import AsyncIOMotorDatabase
import mediapipe as mp

# ==================== ENUMS ====================

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

class VerificationStatus(str, Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    FAILED = "failed"
    RESUBMIT = "resubmit"

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
    """Student facial biometric enrollment"""
    enrollment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    email: str
    
    # Facial encoding reference
    face_encodings: List[List[float]]  # Multiple face samples for accuracy
    face_landmarks: Optional[Dict] = None
    
    # Verification
    is_verified: bool = False
    verified_by: Optional[str] = None  # Admin who verified
    verification_date: Optional[datetime] = None
    
    # Metadata
    enrollment_date: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    status: VerificationStatus = VerificationStatus.PENDING
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

class ProctorSession(BaseModel):
    """Active exam proctoring session"""
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    exam_id: str
    user_id: str
    course_id: str
    
    # Session timing
    started_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime
    paused_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    
    # Status
    status: ExamStatus = ExamStatus.IN_PROGRESS
    identity_verified: bool = False
    identity_verification_timestamp: Optional[datetime] = None
    
    # Monitoring
    video_stream_frames: int = 0  # Total frames captured
    violations: List[Dict] = Field(default_factory=list)  # [{violation_type, severity, timestamp}]
    violation_count: int = 0
    
    # AI Flags
    ai_suspicion_level: float = 0.0  # 0-100 (percentage)
    ai_confidence_score: float = 0.0  # 0-100 (how confident we are)
    
    # Verification snapshots
    initial_face_encoding: Optional[List[float]] = None  # Face at session start
    periodic_verifications: List[Dict] = Field(default_factory=list)  # [{timestamp, verified}]
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

class BehaviorFrame(BaseModel):
    """Single frame analysis during exam"""
    frame_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Face analysis
    face_detected: bool
    face_confidence: float  # 0-1
    face_encoding: Optional[List[float]] = None
    is_same_person: Optional[bool] = None  # Compared to enrollment
    
    # Head/Eye tracking
    head_pose: Dict = Field(default_factory=dict)  # {yaw, pitch, roll}
    eye_gaze_direction: Dict = Field(default_factory=dict)  # {x, y}
    eye_openness: float = 0.0  # 0-1
    blink_rate: float = 0.0  # blinks per minute
    
    # Hand/Body
    hand_detected: bool = False
    hand_raised: bool = False
    body_in_frame: bool = True
    unusual_movement: bool = False
    
    # Environment
    phone_detected: bool = False
    other_faces_detected: int = 0
    ambient_noise_level: float = 0.0  # 0-100
    
    # Violations
    detected_violations: List[str] = Field(default_factory=list)
    severity_score: float = 0.0  # 0-100
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

class ExamAttempt(BaseModel):
    """Complete exam attempt with proctoring data"""
    attempt_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    exam_id: str
    user_id: str
    course_id: str
    
    # Session
    proctor_session_id: str
    
    # Answers
    answers: List[Dict] = Field(default_factory=list)  # [{question_id, answer, timestamp}]
    
    # Scoring
    raw_score: float = 0.0
    adjusted_score: float = 0.0  # After proctoring analysis
    passing: bool = False
    
    # Proctoring Results
    violations_detected: List[Dict] = Field(default_factory=list)
    total_violations: int = 0
    proctoring_passed: bool = True
    
    # Exam metadata
    duration_minutes: int = 0
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    
    # AI Grading
    ai_graded: bool = False
    ai_model_used: str = "groq"
    grading_feedback: Optional[str] = None
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

class AICertificate(BaseModel):
    """AI-Generated Certificate"""
    certificate_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    course_id: str
    exam_id: str
    attempt_id: str
    
    # Certificate Details
    certificate_number: str  # Unique, tamper-proof
    course_title: str
    student_name: str
    
    # Achievement
    final_score: float
    passing_grade: str  # A+, A, B, C, etc.
    is_with_distinction: bool  # 80%+
    
    # Verification
    issued_date: datetime = Field(default_factory=datetime.utcnow)
    expiration_date: Optional[datetime] = None
    verification_code: str  # QR-scannable
    blockchain_hash: Optional[str] = None  # For tamper-proofing
    
    # PDF Generation
    pdf_url: str
    qr_code_url: str
    
    # Status
    is_revoked: bool = False
    revocation_reason: Optional[str] = None
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

# ==================== FACIAL RECOGNITION SERVICE ====================

class FacialRecognitionService:
    """AI-powered facial recognition & biometric verification"""
    
    def __init__(self):
        """Initialize face recognition models"""
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
        # Initialize MediaPipe for advanced face detection
        self.mp_face_detection = mp.solutions.face_detection
        self.mp_hands = mp.solutions.hands
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        
        self.face_detector = self.mp_face_detection.FaceDetection(
            model_selection=0,
            min_detection_confidence=0.7
        )
        self.hands_detector = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.7
        )
        self.pose_detector = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            min_detection_confidence=0.7
        )
    
    def extract_face_encoding(self, image_path: str) -> Optional[List[float]]:
        """Extract face encoding from image using face_recognition lib"""
        try:
            image = face_recognition.load_image_file(image_path)
            face_encodings = face_recognition.face_encodings(image)
            
            if face_encodings:
                return face_encodings[0].tolist()
            return None
        except Exception as e:
            print(f"Error extracting face encoding: {e}")
            return None
    
    def extract_face_encodings_from_frame(self, frame: np.ndarray) -> Tuple[List[List[float]], List]:
        """Extract multiple face encodings from video frame"""
        try:
            face_locations = face_recognition.face_locations(frame)
            face_encodings = face_recognition.face_encodings(frame, face_locations)
            return [enc.tolist() for enc in face_encodings], face_locations
        except:
            return [], []
    
    def compare_faces(self, face_encoding1: List[float], face_encoding2: List[float], tolerance: float = 0.6) -> Tuple[bool, float]:
        """Compare two face encodings
        
        Returns:
            (is_same_person, similarity_score)
        """
        try:
            enc1 = np.array(face_encoding1)
            enc2 = np.array(face_encoding2)
            
            distance = np.linalg.norm(enc1 - enc2)
            is_match = distance < tolerance
            similarity = max(0, 1 - (distance / 2)) * 100  # Convert to percentage
            
            return is_match, similarity
        except:
            return False, 0.0
    
    def analyze_frame_for_violations(self, frame: np.ndarray, enrollment_encoding: Optional[List[float]] = None) -> BehaviorFrame:
        """Comprehensive frame analysis for cheating detection"""
        
        frame_analysis = BehaviorFrame(session_id="temp")
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, c = frame.shape
        
        # ========== FACE DETECTION & VERIFICATION ==========
        face_results = self.face_detector.process(rgb_frame)
        
        if face_results.detections:
            frame_analysis.face_detected = True
            frame_analysis.other_faces_detected = len(face_results.detections) - 1  # Exclude primary
            
            detection = face_results.detections[0]
            frame_analysis.face_confidence = detection.score[0]
            
            # Extract face encoding
            bbox = detection.location_data.relative_bounding_box
            x_min = int(bbox.xmin * w)
            y_min = int(bbox.ymin * h)
            x_max = int((bbox.xmin + bbox.width) * w)
            y_max = int((bbox.ymin + bbox.height) * h)
            
            face_roi = frame[max(0, y_min):min(h, y_max), max(0, x_min):min(w, x_max)]
            face_encodings, _ = self.extract_face_encodings_from_frame(face_roi)
            
            if face_encodings:
                frame_analysis.face_encoding = face_encodings[0]
                
                # Compare with enrollment
                if enrollment_encoding:
                    is_same, similarity = self.compare_faces(face_encodings[0], enrollment_encoding)
                    frame_analysis.is_same_person = is_same
                    
                    if not is_same and similarity < 60:
                        frame_analysis.detected_violations.append(ProctorViolationType.FACE_OUT_OF_FRAME)
            
            # Check for multiple faces
            if len(face_results.detections) > 1:
                frame_analysis.detected_violations.append(ProctorViolationType.MULTIPLE_FACES)
                frame_analysis.severity_score += 30
        else:
            frame_analysis.face_detected = False
            frame_analysis.detected_violations.append(ProctorViolationType.NO_FACE_DETECTED)
            frame_analysis.severity_score += 50
        
        # ========== HEAD POSE & EYE GAZE ==========
        face_landmarks = self.mp_face_detection.get_landmarks(face_results)
        
        if face_landmarks:
            # Get head rotation
            h_pose = self._estimate_head_pose(frame, face_landmarks)
            frame_analysis.head_pose = h_pose
            
            # Check for suspicious head movement
            if abs(h_pose.get('yaw', 0)) > 30:  # Looking too far to side
                frame_analysis.detected_violations.append(ProctorViolationType.HEAD_TURNING)
                frame_analysis.severity_score += 20
        
        # ========== HAND DETECTION ==========
        hand_results = self.hands_detector.process(rgb_frame)
        
        if hand_results.multi_hand_landmarks:
            frame_analysis.hand_detected = True
            
            # Check for raised hand (suspicious behavior)
            for hand_landmarks in hand_results.multi_hand_landmarks:
                # Get hand height
                hand_y = [lm.y for lm in hand_landmarks.landmark]
                avg_hand_y = np.mean(hand_y)
                
                if avg_hand_y < 0.3:  # Hand raised high
                    frame_analysis.hand_raised = True
                    frame_analysis.detected_violations.append(ProctorViolationType.UNUSUAL_HAND_MOVEMENT)
                    frame_analysis.severity_score += 15
        
        # ========== BODY POSITION ==========
        pose_results = self.pose_detector.process(rgb_frame)
        
        if pose_results.pose_landmarks:
            # Check if person is centered in frame
            shoulders = [pose_results.pose_landmarks[11], pose_results.pose_landmarks[12]]
            shoulder_x = [s.x for s in shoulders]
            
            if min(shoulder_x) < 0.1 or max(shoulder_x) > 0.9:
                frame_analysis.body_in_frame = False
                frame_analysis.detected_violations.append(ProctorViolationType.FACE_OUT_OF_FRAME)
                frame_analysis.severity_score += 25
        
        # ========== PHONE & OBJECT DETECTION ==========
        frame_analysis.phone_detected = self._detect_phone(frame)
        if frame_analysis.phone_detected:
            frame_analysis.detected_violations.append(ProctorViolationType.PHONE_DETECTED)
            frame_analysis.severity_score += 40
        
        # ========== AUDIO DETECTION ==========
        # (Simplified - in real scenario use speech recognition)
        # Can integrate with Groq's audio APIs
        
        return frame_analysis
    
    def _estimate_head_pose(self, frame: np.ndarray, landmarks: List) -> Dict:
        """Estimate head rotation angles (yaw, pitch, roll)"""
        # Simplified implementation
        # In production, use 3D face model (dlib, TensorFlow)
        return {
            "yaw": 0.0,      # Left/right rotation
            "pitch": 0.0,    # Up/down rotation
            "roll": 0.0      # Tilt
        }
    
    def _detect_phone(self, frame: np.ndarray) -> bool:
        """Detect mobile phone in frame using object detection"""
        # Simplified - could use YOLO or TensorFlow object detection
        # For now, detect rectangular objects with phone-like aspect ratio
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 100, 200)
        contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = w / h if h > 0 else 0
            
            # Phone aspect ratio typically 0.4-0.7
            if 0.3 < aspect_ratio < 0.8 and w > 50 and h > 100:
                return True
        
        return False

# ==================== GROQ AI INTEGRATION ====================

class GroqAIService:
    """Groq-powered AI for exam grading and proctoring analysis"""
    
    def __init__(self):
        self.api_key = os.environ.get('GROQ_API_KEY')
        self.api_url = "https://api.groq.com/openai/v1"
        self.model = "mixtral-8x7b-32768"  # Fast model for real-time analysis
    
    async def grade_exam_answer(self, question: str, student_answer: str, correct_answer: Optional[str] = None, rubric: Optional[str] = None) -> Dict:
        """Use Groq to grade essay/open-ended answers"""
        
        prompt = f"""
Grade this student's exam answer objectively.

QUESTION: {question}

STUDENT ANSWER: {student_answer}

{f'CORRECT ANSWER/MODEL SOLUTION: {correct_answer}' if correct_answer else ''}

{f'GRADING RUBRIC: {rubric}' if rubric else 'Use standard grading criteria'}

Provide:
1. Score (0-100)
2. Brief feedback
3. Key points covered/missed
4. Suggestions for improvement

Format as JSON.
"""
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                    "max_tokens": 500
                }
                
                async with session.post(f"{self.api_url}/chat/completions", json=payload, headers=headers) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        response_text = data['choices'][0]['message']['content']
                        
                        # Parse JSON response
                        try:
                            result = json.loads(response_text)
                        except:
                            result = {"raw_response": response_text, "score": 50}
                        
                        return result
                    else:
                        return {"error": "Groq API error", "score": 0}
        except Exception as e:
            return {"error": str(e), "score": 0}
    
    async def analyze_proctoring_violations(self, violations: List[Dict], violation_count: int, ai_suspicion_level: float) -> Dict:
        """Use Groq to analyze proctoring violations and determine if exam passed"""
        
        prompt = f"""
Analyze these exam proctoring violations and determine if the exam should be marked as suspicious.

VIOLATIONS DETECTED:
{json.dumps(violations, indent=2)}

TOTAL VIOLATION COUNT: {violation_count}

AI SUSPICION LEVEL: {ai_suspicion_level}%

Evaluate:
1. Severity of violations (minor, moderate, critical)
2. Likelihood of cheating (0-100%)
3. Recommendation (accept/flag/fail/review)
4. Required actions

Format as JSON.
"""
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                    "max_tokens": 600
                }
                
                async with session.post(f"{self.api_url}/chat/completions", json=payload, headers=headers) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        response_text = data['choices'][0]['message']['content']
                        
                        try:
                            result = json.loads(response_text)
                        except:
                            result = {"raw_response": response_text, "recommendation": "review"}
                        
                        return result
                    else:
                        return {"error": "Groq API error", "recommendation": "review"}
        except Exception as e:
            return {"error": str(e), "recommendation": "review"}

# ==================== CERTIFICATE GENERATION ====================

class CertificateGenerationService:
    """AI-powered certificate generation and blockchain verification"""
    
    def __init__(self):
        self.groq_service = GroqAIService()
    
    async def generate_ai_certificate(self, exam_attempt: ExamAttempt, course_info: Dict, user_profile: Dict) -> AICertificate:
        """Generate tamper-proof AI certificate"""
        
        # Calculate grade letter
        score = exam_attempt.adjusted_score
        if score >= 90:
            grade = "A+"
        elif score >= 85:
            grade = "A"
        elif score >= 80:
            grade = "B+"
        elif score >= 75:
            grade = "B"
        elif score >= 70:
            grade = "C"
        else:
            grade = "F"
        
        is_distinction = score >= 80
        
        # Generate unique certificate number
        cert_number = f"GAAIUS-{course_info['course_id'][:8]}-{user_profile['user_id'][:8]}-{int(datetime.utcnow().timestamp())}"
        
        # Generate verification code
        verification_string = f"{cert_number}{user_profile['user_id']}{exam_attempt.exam_id}".encode()
        verification_code = hashlib.sha256(verification_string).hexdigest()[:16]
        
        # Create blockchain hash (simplified - in production use real blockchain)
        blockchain_data = f"{cert_number}{score}{user_profile['email']}".encode()
        blockchain_hash = hashlib.sha256(blockchain_data).hexdigest()
        
        certificate = AICertificate(
            user_id=user_profile['user_id'],
            course_id=course_info['course_id'],
            exam_id=exam_attempt.exam_id,
            attempt_id=exam_attempt.attempt_id,
            certificate_number=cert_number,
            course_title=course_info['title'],
            student_name=user_profile['display_name'],
            final_score=score,
            passing_grade=grade,
            is_with_distinction=is_distinction,
            verification_code=verification_code,
            blockchain_hash=blockchain_hash,
            pdf_url="",  # Will be generated
            qr_code_url=""  # Will be generated
        )
        
        return certificate
    
    def generate_certificate_pdf(self, certificate: AICertificate) -> bytes:
        """Generate PDF certificate (using reportlab)"""
        
        try:
            from reportlab.lib.pagesizes import A4, landscape
            from reportlab.lib.units import inch
            from reportlab.pdfgen import canvas
            from reportlab.lib.colors import HexColor
            from datetime import datetime
            
            # Create PDF
            from io import BytesIO
            buffer = BytesIO()
            
            c = canvas.Canvas(buffer, pagesize=landscape(A4))
            width, height = landscape(A4)
            
            # Background
            c.setFillColor(HexColor("#f5f5f5"))
            c.rect(0, 0, width, height, fill=1)
            
            # Border
            c.setLineWidth(3)
            c.setStrokeColor(HexColor("#1a4d7a"))
            c.rect(30, 30, width - 60, height - 60)
            
            # Header
            c.setFont("Helvetica-Bold", 48)
            c.setFillColor(HexColor("#1a4d7a"))
            c.drawString(width/2 - 200, height - 120, "CERTIFICATE OF ACHIEVEMENT")
            
            # Course title
            c.setFont("Helvetica-Bold", 24)
            c.drawString(width/2 - 150, height - 200, certificate.course_title)
            
            # Student name
            c.setFont("Helvetica-Bold", 20)
            c.drawString(width/2 - 100, height - 280, f"This is proudly presented to")
            
            c.setFont("Helvetica-Bold", 32)
            c.setFillColor(HexColor("#d4af37"))  # Gold
            c.drawString(width/2 - 180, height - 340, certificate.student_name.upper())
            
            # Achievement text
            c.setFont("Helvetica", 14)
            c.setFillColor(HexColor("#000000"))
            c.drawString(width/2 - 250, height - 400, "For successfully completing the course and demonstrating mastery")
            c.drawString(width/2 - 250, height - 430, "of the learning objectives with a final score of")
            
            # Score
            c.setFont("Helvetica-Bold", 18)
            c.setFillColor(HexColor("#1a4d7a"))
            c.drawString(width/2 - 50, height - 470, f"{certificate.final_score:.1f}%")
            
            # Grade
            if certificate.is_with_distinction:
                c.setFont("Helvetica-Bold", 16)
                c.setFillColor(HexColor("#ff6b6b"))
                c.drawString(width/2 - 100, height - 510, "With Distinction!")
            
            # Date and Certificate Number
            c.setFont("Helvetica", 11)
            c.setFillColor(HexColor("#666666"))
            c.drawString(150, 80, f"Certificate #: {certificate.certificate_number}")
            c.drawString(150, 60, f"Issued: {certificate.issued_date.strftime('%B %d, %Y')}")
            c.drawString(width - 450, 80, f"Verification Code: {certificate.verification_code}")
            
            # Footer seal
            c.setFont("Helvetica-Bold", 10)
            c.setFillColor(HexColor("#1a4d7a"))
            c.drawString(width/2 - 100, 30, "GAAIUS AI-Powered Learning Platform | Verified & Authenticated")
            
            c.save()
            
            buffer.seek(0)
            return buffer.getvalue()
        
        except Exception as e:
            print(f"Error generating certificate PDF: {e}")
            return b""
    
    def generate_qr_code(self, verification_code: str) -> str:
        """Generate QR code for certificate verification"""
        
        try:
            import qrcode
            from io import BytesIO
            
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            
            qr.add_data(f"https://gaaius.com/verify/{verification_code}")
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            
            # Convert to base64 for embedding
            img_base64 = base64.b64encode(buffer.getvalue()).decode()
            return f"data:image/png;base64,{img_base64}"
        
        except Exception as e:
            print(f"Error generating QR code: {e}")
            return ""

# ==================== MAIN PROCTORING SERVICE ====================

class AIProctoringService:
    """Main service orchestrating exam proctoring"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.facial_service = FacialRecognitionService()
        self.groq_service = GroqAIService()
        self.cert_service = CertificateGenerationService()
    
    # ==================== ENROLLMENT & IDENTITY ====================
    
    async def enroll_facial_biometric(self, user_id: str, email: str, image_path: str) -> FacialEnrollment:
        """Enroll student facial biometrics (3 sample images recommended)"""
        
        face_encoding = self.facial_service.extract_face_encoding(image_path)
        
        if not face_encoding:
            raise Exception("Could not detect face in image. Please provide a clear photo.")
        
        enrollment = FacialEnrollment(
            user_id=user_id,
            email=email,
            face_encodings=[face_encoding]
        )
        
        await self.db.facial_enrollments.insert_one(enrollment.dict())
        return enrollment
    
    async def add_facial_sample(self, user_id: str, image_path: str) -> FacialEnrollment:
        """Add additional facial sample to enrollment (for improved accuracy)"""
        
        face_encoding = self.facial_service.extract_face_encoding(image_path)
        
        if not face_encoding:
            raise Exception("Could not detect face. Please try again.")
        
        enrollment = await self.db.facial_enrollments.find_one({"user_id": user_id})
        
        if not enrollment:
            raise Exception("User not enrolled. Please complete enrollment first.")
        
        # Add to existing encodings
        enrollment['face_encodings'].append(face_encoding)
        
        # Update in database
        await self.db.facial_enrollments.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "face_encodings": enrollment['face_encodings'],
                    "last_updated": datetime.utcnow()
                }
            }
        )
        
        return FacialEnrollment(**enrollment)
    
    async def verify_student_identity(self, user_id: str, frame: np.ndarray, required_confidence: float = 0.95) -> Tuple[bool, float]:
        """Verify student identity at exam start or during periodic checks"""
        
        # Get enrollment
        enrollment = await self.db.facial_enrollments.find_one({"user_id": user_id})
        
        if not enrollment:
            return False, 0.0
        
        # Extract face from current frame
        current_encodings, _ = self.facial_service.extract_face_encodings_from_frame(frame)
        
        if not current_encodings:
            return False, 0.0
        
        current_encoding = current_encodings[0]
        
        # Compare against all enrollment samples
        match_scores = []
        for enrolled_encoding in enrollment['face_encodings']:
            is_match, similarity = self.facial_service.compare_faces(current_encoding, enrolled_encoding)
            match_scores.append(similarity)
        
        avg_similarity = np.mean(match_scores) / 100  # Convert to 0-1
        
        return avg_similarity >= required_confidence, avg_similarity
    
    # ==================== EXAM SESSION MANAGEMENT ====================
    
    async def start_exam_session(self, exam_id: str, user_id: str, course_id: str, duration_minutes: int) -> ProctorSession:
        """Initialize proctored exam session"""
        
        # Verify enrollment exists
        enrollment = await self.db.facial_enrollments.find_one({"user_id": user_id})
        if not enrollment:
            raise Exception("User must complete facial biometric enrollment first")
        
        session = ProctorSession(
            exam_id=exam_id,
            user_id=user_id,
            course_id=course_id,
            expires_at=datetime.utcnow() + timedelta(minutes=duration_minutes + 5)  # 5 min buffer
        )
        
        await self.db.proctor_sessions.insert_one(session.dict())
        return session
    
    async def verify_identity_at_session_start(self, session_id: str, frame: np.ndarray) -> Dict:
        """Perform initial identity verification before exam starts"""
        
        session = await self.db.proctor_sessions.find_one({"session_id": session_id})
        if not session:
            raise Exception("Invalid session")
        
        verified, confidence = await self.verify_student_identity(session['user_id'], frame)
        
        if verified:
            # Extract and store face encoding for periodic comparison
            encodings, _ = self.facial_service.extract_face_encodings_from_frame(frame)
            initial_encoding = encodings[0] if encodings else None
            
            await self.db.proctor_sessions.update_one(
                {"session_id": session_id},
                {
                    "$set": {
                        "identity_verified": True,
                        "identity_verification_timestamp": datetime.utcnow(),
                        "initial_face_encoding": initial_encoding
                    }
                }
            )
        
        return {
            "verified": verified,
            "confidence": confidence,
            "message": "Identity verified. Exam can proceed." if verified else "Identity verification failed. Please try again."
        }
    
    async def process_exam_frame(self, session_id: str, frame: np.ndarray, frame_number: int = 0) -> BehaviorFrame:
        """Process single video frame during exam"""
        
        session = await self.db.proctor_sessions.find_one({"session_id": session_id})
        if not session:
            raise Exception("Invalid session")
        
        # Get enrollment for comparison
        enrollment = await self.db.facial_enrollments.find_one({"user_id": session['user_id']})
        enrollment_encoding = enrollment['face_encodings'][0] if enrollment and enrollment['face_encodings'] else None
        
        # Analyze frame
        frame_analysis = self.facial_service.analyze_frame_for_violations(frame, enrollment_encoding)
        frame_analysis.session_id = session_id
        
        # Save frame analysis
        await self.db.behavior_frames.insert_one(frame_analysis.dict())
        
        # Update session violations
        if frame_analysis.detected_violations:
            await self.db.proctor_sessions.update_one(
                {"session_id": session_id},
                {
                    "$push": {
                        "violations": {
                            "violations": frame_analysis.detected_violations,
                            "timestamp": datetime.utcnow(),
                            "severity": frame_analysis.severity_score
                        }
                    },
                    "$inc": {"violation_count": 1, "video_stream_frames": 1},
                    "$set": {
                        "ai_suspicion_level": min(100, session.get('ai_suspicion_level', 0) + frame_analysis.severity_score / 10)
                    }
                }
            )
        else:
            await self.db.proctor_sessions.update_one(
                {"session_id": session_id},
                {"$inc": {"video_stream_frames": 1}}
            )
        
        return frame_analysis
    
    async def periodic_identity_verification(self, session_id: str, frame: np.ndarray) -> bool:
        """Verify student identity periodically during exam (every 5 mins)"""
        
        session = await self.db.proctor_sessions.find_one({"session_id": session_id})
        if not session:
            return False
        
        verified, confidence = await self.verify_student_identity(session['user_id'], frame)
        
        if verified:
            await self.db.proctor_sessions.update_one(
                {"session_id": session_id},
                {
                    "$push": {
                        "periodic_verifications": {
                            "timestamp": datetime.utcnow(),
                            "verified": True,
                            "confidence": confidence
                        }
                    }
                }
            )
        else:
            # Flag as violation
            await self.db.proctor_sessions.update_one(
                {"session_id": session_id},
                {
                    "$push": {
                        "violations": {
                            "violations": [ProctorViolationType.FACE_OUT_OF_FRAME],
                            "timestamp": datetime.utcnow(),
                            "severity": 50
                        },
                        "periodic_verifications": {
                            "timestamp": datetime.utcnow(),
                            "verified": False,
                            "confidence": confidence
                        }
                    },
                    "$inc": {"violation_count": 1}
                }
            )
        
        return verified
    
    # ==================== EXAM GRADING WITH AI ====================
    
    async def submit_exam(self, session_id: str, answers: List[Dict], exam_config: Dict) -> ExamAttempt:
        """Submit exam for grading and proctoring analysis"""
        
        session = await self.db.proctor_sessions.find_one({"session_id": session_id})
        if not session:
            raise Exception("Invalid session")
        
        # Create attempt record
        attempt = ExamAttempt(
            exam_id=session['exam_id'],
            user_id=session['user_id'],
            course_id=session['course_id'],
            proctor_session_id=session_id,
            answers=answers,
            duration_minutes=int((datetime.utcnow() - session['started_at']).total_seconds() / 60)
        )
        
        # ========== GRADE EACH ANSWER WITH GROQ ==========
        total_points = 0
        raw_score = 0
        
        for question_config in exam_config.get('questions', []):
            question_id = question_config['id']
            
            # Find student's answer
            student_response = next((a for a in answers if a['question_id'] == question_id), None)
            if not student_response:
                continue
            
            student_answer = student_response.get('answer', '')
            question_text = question_config.get('question', '')
            question_type = question_config.get('type', 'multiple_choice')
            points = question_config.get('points', 0)
            
            total_points += points
            
            if question_type == 'multiple_choice':
                # Simple comparison
                if student_answer == question_config.get('correct_answer'):
                    raw_score += points
            else:
                # Use Groq for essay/open-ended questions
                grading_result = await self.groq_service.grade_exam_answer(
                    question=question_text,
                    student_answer=student_answer,
                    correct_answer=question_config.get('model_answer'),
                    rubric=question_config.get('rubric')
                )
                
                if 'score' in grading_result:
                    # Normalize score to question points
                    normalized_score = (grading_result['score'] / 100) * points
                    raw_score += normalized_score
        
        attempt.raw_score = raw_score if total_points == 0 else (raw_score / total_points) * 100
        
        # ========== ANALYZE PROCTORING VIOLATIONS ==========
        violations_analysis = await self.groq_service.analyze_proctoring_violations(
            violations=session.get('violations', []),
            violation_count=session.get('violation_count', 0),
            ai_suspicion_level=session.get('ai_suspicion_level', 0.0)
        )
        
        attempt.violations_detected = session.get('violations', [])
        attempt.total_violations = session.get('violation_count', 0)
        attempt.proctoring_passed = violations_analysis.get('recommendation') != 'fail'
        
        # ========== ADJUST SCORE BASED ON PROCTORING ==========
        if not attempt.proctoring_passed:
            attempt.status = ExamStatus.FAILED_PROCTORING
            attempt.adjusted_score = 0  # Fail due to cheating
        else:
            # Apply minor penalties if moderate violations
            if violations_analysis.get('severity') == 'moderate':
                attempt.adjusted_score = attempt.raw_score * 0.95  # 5% penalty
            else:
                attempt.adjusted_score = attempt.raw_score
        
        attempt.passing = attempt.adjusted_score >= exam_config.get('passing_score', 70)
        attempt.completed_at = datetime.utcnow()
        attempt.ai_graded = True
        attempt.ai_model_used = "groq"
        attempt.grading_feedback = violations_analysis.get('feedback', '')
        attempt.status = ExamStatus.GRADED
        
        # Save attempt
        await self.db.exam_attempts.insert_one(attempt.dict())
        
        # Update session
        await self.db.proctor_sessions.update_one(
            {"session_id": session_id},
            {
                "$set": {
                    "status": ExamStatus.GRADED,
                    "ended_at": datetime.utcnow(),
                    "ai_confidence_score": violations_analysis.get('confidence', 0)
                }
            }
        )
        
        return attempt
    
    # ==================== CERTIFICATE ISSUANCE ====================
    
    async def issue_certificate(self, attempt_id: str) -> AICertificate:
        """Generate and issue certificate upon passing exam"""
        
        attempt = await self.db.exam_attempts.find_one({"attempt_id": attempt_id})
        if not attempt or not attempt.get('passing'):
            raise Exception("Exam must be passed to receive certificate")
        
        # Get course info
        exam = await self.db.exams.find_one({"exam_id": attempt['exam_id']})
        course = await self.db.courses.find_one({"course_id": attempt['course_id']})
        user_profile = await self.db.user_profiles.find_one({"user_id": attempt['user_id']})
        
        # Generate certificate
        certificate = await self.cert_service.generate_ai_certificate(
            ExamAttempt(**attempt),
            course.dict(),
            user_profile.dict()
        )
        
        # Generate PDF
        pdf_bytes = self.cert_service.generate_certificate_pdf(certificate)
        
        # Generate QR code
        qr_code = self.cert_service.generate_qr_code(certificate.verification_code)
        
        certificate.pdf_url = "s3://gaaius-certificates/" + certificate.certificate_id + ".pdf"
        certificate.qr_code_url = qr_code
        
        # Save certificate
        await self.db.certificates.insert_one(certificate.dict())
        
        # Update user profile
        await self.db.user_profiles.update_one(
            {"user_id": attempt['user_id']},
            {"$inc": {"certificates_earned": 1}}
        )
        
        return certificate
    
    async def verify_certificate(self, verification_code: str) -> Optional[AICertificate]:
        """Verify certificate authenticity"""
        
        certificate = await self.db.certificates.find_one({
            "verification_code": verification_code,
            "is_revoked": False
        })
        
        return AICertificate(**certificate) if certificate else None

# Export
__all__ = [
    'AIProctoringService',
    'FacialRecognitionService',
    'GroqAIService',
    'CertificateGenerationService',
    'FacialEnrollment', 'ProctorSession', 'BehaviorFrame', 'ExamAttempt', 'AICertificate',
    'ProctorViolationType', 'VerificationStatus', 'ExamStatus'
]
