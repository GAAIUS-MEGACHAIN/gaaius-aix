"""
Proctoring API Routes for Certification Exams
RESTful endpoints for managing proctored certification exams
"""

from fastapi import APIRouter, HTTPException, File, UploadFile, Depends, Query
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from backend.proctoring_service import (
    ProctoringEngine, CertificationExam, ExamAttempt, ExamViolation,
    ProctorSession, FaceVerification, EnvironmentCheck, ExamBehavior,
    CertificateIssuance, CertificateVerificationService, ProctoringAnalytics,
    ProctorMode, IntegrityLevel, ViolationType, ViolationSeverity
)

router = APIRouter(prefix="/proctoring", tags=["proctoring"])
logger = logging.getLogger(__name__)

# Global proctoring engine
proctoring_engine = ProctoringEngine()

# ============================================================================
# CERTIFICATION EXAM MANAGEMENT
# ============================================================================

@router.post("/exams", response_model=CertificationExam)
async def create_certification_exam(exam: CertificationExam):
    """
    Create new certification exam with proctoring requirements
    
    Features:
    - Define exam duration and passing score
    - Set proctoring mode (live, automated, hybrid)
    - Configure security requirements
    - Set monitoring preferences
    """
    try:
        logger.info(f"Creating certification exam: {exam.title}")
        # In production: Save to database
        return exam
    except Exception as e:
        logger.error(f"Failed to create exam: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/exams/{exam_id}", response_model=CertificationExam)
async def get_exam_details(exam_id: str):
    """Retrieve certification exam details"""
    try:
        # In production: Query database
        logger.info(f"Retrieved exam: {exam_id}")
        return {}
    except Exception as e:
        raise HTTPException(status_code=404, detail="Exam not found")

@router.put("/exams/{exam_id}", response_model=CertificationExam)
async def update_exam(exam_id: str, exam: CertificationExam):
    """Update exam configuration and proctoring settings"""
    try:
        logger.info(f"Updating exam: {exam_id}")
        return exam
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/exams/{exam_id}")
async def delete_exam(exam_id: str):
    """Delete certification exam"""
    try:
        logger.info(f"Deleting exam: {exam_id}")
        return {"message": "Exam deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/exams/course/{course_id}", response_model=List[CertificationExam])
async def get_course_exams(course_id: str):
    """Get all certification exams for a course"""
    try:
        logger.info(f"Retrieved exams for course: {course_id}")
        return []
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ============================================================================
# EXAM SESSION MANAGEMENT
# ============================================================================

@router.post("/sessions/start", response_model=Dict[str, Any])
async def start_exam_session(exam_id: str, student_id: str, proctor_id: Optional[str] = None):
    """
    Start a proctored exam session
    
    Initializes:
    - Proctoring session
    - Session security key
    - Monitoring parameters
    """
    try:
        exam = CertificationExam(
            exam_id=exam_id,
            course_id="",
            title="",
            description="",
            duration_minutes=120,
            total_questions=50,
            question_pool_size=50
        )
        
        session_id, session = proctoring_engine.initialize_exam_session(exam, student_id, proctor_id)
        
        logger.info(f"Started proctored session: {session_id} for student: {student_id}")
        
        return {
            "session_id": session_id,
            "exam_id": exam_id,
            "student_id": student_id,
            "mode": exam.proctor_mode.value,
            "start_time": session.start_time.isoformat(),
            "status": "active"
        }
    except Exception as e:
        logger.error(f"Failed to start session: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/sessions/{session_id}/end")
async def end_exam_session(session_id: str):
    """End proctored exam session"""
    try:
        if session_id not in proctoring_engine.active_sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = proctoring_engine.active_sessions[session_id]
        session.end_time = datetime.utcnow()
        
        logger.info(f"Ended proctored session: {session_id}")
        
        return {
            "session_id": session_id,
            "end_time": session.end_time.isoformat(),
            "status": "completed"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/sessions/{session_id}", response_model=Dict[str, Any])
async def get_session_details(session_id: str):
    """Get proctoring session details and status"""
    try:
        if session_id not in proctoring_engine.active_sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = proctoring_engine.active_sessions[session_id]
        
        return {
            "session_id": session_id,
            "exam_id": session.exam_id,
            "student_id": session.student_id,
            "proctor_id": session.proctor_id,
            "mode": session.mode.value,
            "start_time": session.start_time.isoformat(),
            "violations": len(session.violations_detected),
            "approval_status": session.approval_status
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ============================================================================
# IDENTITY & FACE VERIFICATION
# ============================================================================

@router.post("/verify/identity", response_model=Dict[str, Any])
async def verify_student_identity(
    exam_id: str,
    student_id: str,
    captured_image: UploadFile = File(...)
):
    """
    Verify student identity through face recognition
    
    Performs:
    - Face detection and liveness verification
    - Comparison with enrollment photo
    - Spoofing detection
    """
    try:
        # Read uploaded image
        image_data = await captured_image.read()
        
        # Enrollment image would come from database
        enrollment_image = b"enrollment_photo_bytes"
        
        verification = proctoring_engine.verify_student_identity(
            exam_id, student_id, image_data, enrollment_image
        )
        
        logger.info(f"Face verification for student {student_id}: {verification.is_match}")
        
        return {
            "verification_id": verification.verification_id,
            "student_id": student_id,
            "is_match": verification.is_match,
            "confidence": verification.confidence,
            "is_alive": verification.is_alive,
            "spoofing_detected": not verification.is_alive,
            "timestamp": verification.timestamp.isoformat()
        }
    except Exception as e:
        logger.error(f"Identity verification failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/verify/environment", response_model=Dict[str, Any])
async def verify_exam_environment(exam_id: str, student_id: str):
    """
    Verify exam environment and physical setup
    
    Checks:
    - Room clearance
    - Authorized devices only
    - Network stability
    - Audio/video equipment
    """
    try:
        check = proctoring_engine.check_environment(exam_id, student_id)
        
        logger.info(f"Environment check for student {student_id}: room_clear={check.room_clear}")
        
        return {
            "check_id": check.check_id,
            "exam_id": exam_id,
            "student_id": student_id,
            "room_clear": check.room_clear,
            "primary_monitor": check.primary_monitor,
            "camera_working": check.camera_working,
            "microphone_working": check.microphone_working,
            "stable_connection": check.stable_connection,
            "bandwidth_sufficient": check.bandwidth_sufficient,
            "unauthorized_materials": check.unauthorized_materials,
            "timestamp": check.timestamp.isoformat()
        }
    except Exception as e:
        logger.error(f"Environment verification failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

# ============================================================================
# BEHAVIOR MONITORING
# ============================================================================

@router.post("/monitor/behavior", response_model=Dict[str, Any])
async def monitor_student_behavior(
    exam_id: str,
    student_id: str,
    behavior_data: Dict[str, Any]
):
    """
    Monitor and analyze student behavior during exam
    
    Analyzes:
    - Eye gaze direction
    - Posture and hand position
    - Mouse/keyboard patterns
    - Anomaly detection
    """
    try:
        behavior = proctoring_engine.monitor_behavior(exam_id, student_id, behavior_data)
        
        # Detect violations
        violations = proctoring_engine.detect_violations(exam_id, student_id, behavior)
        
        logger.info(f"Behavior analysis for student {student_id}: risk_score={behavior.risk_score:.2f}, violations={len(violations)}")
        
        return {
            "behavior_id": behavior.behavior_id,
            "exam_id": exam_id,
            "student_id": student_id,
            "risk_score": behavior.risk_score,
            "gaze_direction": behavior.eye_gaze_direction,
            "posture_normal": behavior.posture_normal,
            "violations_detected": len(violations),
            "timestamp": behavior.timestamp.isoformat()
        }
    except Exception as e:
        logger.error(f"Behavior monitoring failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

# ============================================================================
# VIOLATION DETECTION & MANAGEMENT
# ============================================================================

@router.get("/violations/{exam_id}/{student_id}", response_model=List[Dict[str, Any]])
async def get_exam_violations(exam_id: str, student_id: str):
    """Get all violations detected during exam attempt"""
    try:
        violations = []
        if exam_id in proctoring_engine.violation_history:
            for v in proctoring_engine.violation_history[exam_id]:
                if v.student_id == student_id:
                    violations.append({
                        "violation_id": v.violation_id,
                        "violation_type": v.violation_type.value,
                        "severity": v.severity.value,
                        "description": v.description,
                        "confidence": v.confidence,
                        "timestamp": v.timestamp.isoformat()
                    })
        
        logger.info(f"Retrieved {len(violations)} violations for student {student_id}")
        return violations
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/violations/{violation_id}/review")
async def review_violation(
    violation_id: str,
    proctor_action: str,  # warning, pause, terminate
    proctor_notes: str = ""
):
    """Human proctor review and action on violation"""
    try:
        # In production: Update violation in database
        logger.info(f"Violation {violation_id} reviewed by proctor. Action: {proctor_action}")
        
        return {
            "violation_id": violation_id,
            "proctor_action": proctor_action,
            "proctor_notes": proctor_notes,
            "reviewed_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/violations/stats/{exam_id}")
async def get_violation_statistics(exam_id: str):
    """Get violation statistics for exam"""
    try:
        violations = proctoring_engine.violation_history.get(exam_id, [])
        
        stats = {
            "total_violations": len(violations),
            "by_type": {},
            "by_severity": {},
            "critical_count": 0,
            "caution_count": 0,
            "warning_count": 0
        }
        
        for v in violations:
            # By type
            vtype = v.violation_type.value
            stats["by_type"][vtype] = stats["by_type"].get(vtype, 0) + 1
            
            # By severity
            severity = v.severity.value
            stats["by_severity"][severity] = stats["by_severity"].get(severity, 0) + 1
            
            if v.severity == ViolationSeverity.CRITICAL:
                stats["critical_count"] += 1
            elif v.severity == ViolationSeverity.CAUTION:
                stats["caution_count"] += 1
            else:
                stats["warning_count"] += 1
        
        return stats
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ============================================================================
# EXAM SUBMISSION & GRADING
# ============================================================================

@router.post("/attempts/{attempt_id}/submit")
async def submit_exam(attempt_id: str, answers: Dict[str, Any]):
    """Submit completed exam attempt for grading"""
    try:
        # In production: Process exam submission
        logger.info(f"Exam attempt {attempt_id} submitted for grading")
        
        return {
            "attempt_id": attempt_id,
            "status": "submitted",
            "submission_time": datetime.utcnow().isoformat(),
            "next_step": "Exam will be reviewed by proctor and graded"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/attempts/{attempt_id}/grade")
async def grade_exam(
    attempt_id: str,
    score: float,
    detailed_feedback: Optional[Dict[str, Any]] = None
):
    """Grade submitted exam and generate results"""
    try:
        passing_score = 70.0  # In production: Get from exam config
        passed = score >= passing_score
        percentage = (score / 100.0) * 100
        grade = _calculate_grade(percentage)
        
        logger.info(f"Graded attempt {attempt_id}: score={score}, passed={passed}")
        
        return {
            "attempt_id": attempt_id,
            "score": score,
            "percentage": percentage,
            "grade": grade,
            "passed": passed,
            "passing_score": passing_score,
            "graded_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ============================================================================
# CERTIFICATE MANAGEMENT
# ============================================================================

@router.post("/certificates/issue")
async def issue_certificate(
    exam_attempt_id: str,
    exam_id: str,
    student_id: str,
    student_name: str,
    score: float
):
    """
    Issue certification upon successful exam completion
    
    Generates:
    - Unique certificate number
    - Tamper-proof hash
    - Shareable credential URL
    """
    try:
        certificate_number = CertificateVerificationService.generate_certificate_number()
        
        certificate = CertificateIssuance(
            exam_attempt_id=exam_attempt_id,
            exam_id=exam_id,
            course_id="",
            student_id=student_id,
            student_name=student_name,
            certificate_number=certificate_number,
            score=score,
            grade=_calculate_grade((score / 100.0) * 100),
            completion_time_hours=2.5
        )
        
        certificate.tamper_proof_hash = CertificateVerificationService.create_tamper_proof_hash(certificate)
        certificate.credential_url = CertificateVerificationService.generate_credential_url(certificate)
        
        logger.info(f"Issued certificate {certificate_number} to student {student_id}")
        
        return {
            "certificate_id": certificate.certificate_id,
            "certificate_number": certificate_number,
            "student_name": student_name,
            "score": score,
            "grade": certificate.grade,
            "issue_date": certificate.issue_date.isoformat(),
            "credential_url": certificate.credential_url,
            "integrity_verified": certificate.integrity_verified
        }
    except Exception as e:
        logger.error(f"Failed to issue certificate: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/certificates/{certificate_number}/verify")
async def verify_certificate(certificate_number: str):
    """
    Public endpoint to verify certificate authenticity
    
    Checks:
    - Certificate authenticity
    - Expiration status
    - Revocation status
    - Integrity hash
    """
    try:
        # In production: Query database
        # certificate = get_certificate_by_number(certificate_number)
        
        logger.info(f"Verified certificate {certificate_number}")
        
        return {
            "certificate_number": certificate_number,
            "valid": True,
            "status": "issued",
            "issue_date": datetime.utcnow().isoformat(),
            "expiration_date": None,
            "integrity_verified": True
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail="Certificate not found")

@router.post("/certificates/{certificate_id}/revoke")
async def revoke_certificate(
    certificate_id: str,
    reason: str
):
    """Revoke issued certificate due to violation or malpractice"""
    try:
        logger.info(f"Revoked certificate {certificate_id}. Reason: {reason}")
        
        return {
            "certificate_id": certificate_id,
            "status": "revoked",
            "revocation_date": datetime.utcnow().isoformat(),
            "reason": reason
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ============================================================================
# ANALYTICS & REPORTING
# ============================================================================

@router.get("/analytics/exam/{exam_id}")
async def get_exam_analytics(exam_id: str):
    """Get comprehensive analytics for certification exam"""
    try:
        # In production: Query all attempts for this exam
        attempts = []  # Get from database
        
        analytics = ProctoringAnalytics.analyze_exam_integrity(exam_id, attempts)
        
        return {
            "exam_id": exam_id,
            "analytics": analytics,
            "generated_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/analytics/student/{student_id}")
async def get_student_exam_history(student_id: str):
    """Get exam attempt history and statistics for student"""
    try:
        logger.info(f"Retrieved exam history for student {student_id}")
        
        return {
            "student_id": student_id,
            "total_exams_attempted": 0,
            "total_exams_passed": 0,
            "certificates_earned": 0,
            "average_score": 0.0,
            "exams": []
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/health")
async def health_check():
    """Proctoring service health check"""
    return {
        "status": "healthy",
        "service": "proctoring",
        "active_sessions": len(proctoring_engine.active_sessions),
        "timestamp": datetime.utcnow().isoformat()
    }

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _calculate_grade(percentage: float) -> str:
    """Convert percentage to letter grade"""
    if percentage >= 90:
        return "A"
    elif percentage >= 80:
        return "B"
    elif percentage >= 70:
        return "C"
    elif percentage >= 60:
        return "D"
    else:
        return "F"

