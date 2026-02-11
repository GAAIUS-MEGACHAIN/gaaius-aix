"""
GAAIUS E-Learning Platform - API Routes
FastAPI routes for all platform features
"""

from fastapi import FastAPI, HTTPException, Depends, File, UploadFile, Form, WebSocket
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import cv2
from typing import List, Optional
from datetime import datetime
import asyncio

from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel, EmailStr

# Import services
from backend.ai_proctoring_service import (
    AIProctoringService, FacialRecognitionService,
    ProctorSession, ExamAttempt, AICertificate
)
from backend.free_content_onboarding import FreeContentOnboardingService, FreeContent
from backend.social_service import ELearningService, Course, Enrollment

# ==================== PYDANTIC MODELS ====================

class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    username: str

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

class ExamStartRequest(BaseModel):
    exam_id: str
    user_id: str
    course_id: str

class ExamSubmitRequest(BaseModel):
    answers: List[dict]  # [{question_id, answer}]

class ContentSearchRequest(BaseModel):
    query: Optional[str] = None
    subject: Optional[str] = None
    level: Optional[str] = None

# ==================== INITIALIZE APP ====================

app = FastAPI(title="GAAIUS AI E-Learning Platform", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services (in production, use dependency injection)
async def get_db() -> AsyncIOMotorDatabase:
    # This would be replaced with actual MongoDB connection
    from motor.motor_asyncio import AsyncIOMotorClient
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    return client.gaaius_elearning

# ==================== HEALTH CHECK ====================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "GAAIUS AI E-Learning Platform"
    }

# ==================== AUTHENTICATION ROUTES ====================

@app.post("/api/auth/register")
async def register(
    request: UserRegisterRequest,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Register new user"""
    try:
        # Check if user exists
        existing = await db.users.find_one({"email": request.email})
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Hash password (use bcrypt in production)
        password_hash = request.password  # Simplified
        
        # Create user
        user = {
            "email": request.email,
            "password": password_hash,
            "full_name": request.full_name,
            "username": request.username,
            "created_at": datetime.utcnow()
        }
        
        result = await db.users.insert_one(user)
        
        return {
            "user_id": str(result.inserted_id),
            "email": request.email,
            "message": "User registered. Next: enroll facial biometrics"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/auth/login")
async def login(
    request: UserLoginRequest,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Login user"""
    try:
        user = await db.users.find_one({"email": request.email})
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # In production: use JWT tokens
        return {
            "user_id": str(user["_id"]),
            "email": user["email"],
            "token": "jwt_token_here"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/auth/facial-enroll")
async def facial_enroll(
    user_id: str = Form(...),
    file: UploadFile = File(...),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Enroll facial biometric (upload selfie)"""
    try:
        proctoring = AIProctoringService(db)
        
        # Save uploaded file
        contents = await file.read()
        file_path = f"/tmp/{user_id}_{file.filename}"
        
        with open(file_path, "wb") as f:
            f.write(contents)
        
        # Enroll facial biometric
        user = await db.users.find_one({"_id": user_id})
        enrollment = await proctoring.enroll_facial_biometric(
            user_id=user_id,
            email=user["email"],
            image_path=file_path
        )
        
        return {
            "enrolled": True,
            "enrollment_id": enrollment.enrollment_id,
            "message": "Facial biometric enrolled. Add 2 more samples for accuracy.",
            "samples_collected": 1,
            "samples_needed": 3
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/auth/facial-enroll/add")
async def add_facial_sample(
    user_id: str = Form(...),
    file: UploadFile = File(...),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Add additional facial sample"""
    try:
        proctoring = AIProctoringService(db)
        
        contents = await file.read()
        file_path = f"/tmp/{user_id}_{file.filename}"
        
        with open(file_path, "wb") as f:
            f.write(contents)
        
        enrollment = await proctoring.add_facial_sample(user_id, file_path)
        
        return {
            "success": True,
            "samples_collected": len(enrollment.face_encodings),
            "samples_needed": 3,
            "message": "Sample added. " + ("Enrollment complete!" if len(enrollment.face_encodings) >= 3 else "Add more samples.")
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== CONTENT ROUTES ====================

@app.get("/api/content/search")
async def search_content(
    query: Optional[str] = None,
    subject: Optional[str] = None,
    level: Optional[str] = None,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Search free content"""
    try:
        content_service = FreeContentOnboardingService(db)
        
        results = await content_service.search_content(
            query=query,
            subject=subject,
            level=level
        )
        
        return {
            "count": len(results),
            "content": [
                {
                    "id": c.content_id,
                    "title": c.title,
                    "description": c.description,
                    "source": c.source,
                    "subject": c.subject,
                    "level": c.level,
                    "type": c.content_type,
                    "url": c.content_url,
                    "rating": c.average_rating
                }
                for c in results
            ]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/content/{content_id}")
async def get_content(
    content_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get content details"""
    try:
        content = await db.free_content.find_one({"content_id": content_id})
        
        if not content:
            raise HTTPException(status_code=404, detail="Content not found")
        
        # Update access count
        await db.free_content.update_one(
            {"content_id": content_id},
            {"$inc": {"times_accessed": 1}}
        )
        
        return FreeContent(**content)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== COURSE ROUTES ====================

@app.get("/api/courses")
async def list_courses(
    skip: int = 0,
    limit: int = 20,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """List all courses"""
    try:
        elearning = ELearningService(db)
        courses, total = await elearning.search_courses(skip=skip, limit=limit)
        
        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "courses": [
                {
                    "id": c.course_id,
                    "title": c.title,
                    "description": c.description,
                    "instructor_id": c.instructor_id,
                    "category": c.category,
                    "difficulty": c.difficulty_level,
                    "duration_hours": c.duration_hours,
                    "rating": c.average_rating,
                    "enrollments": c.enrolled_students
                }
                for c in courses
            ]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/courses/{course_id}")
async def get_course(
    course_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get course details with curriculum"""
    try:
        elearning = ELearningService(db)
        
        course = await elearning.get_course(course_id)
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        curriculum = await elearning.get_course_curriculum(course_id)
        
        return {
            "course": {
                "id": course.course_id,
                "title": course.title,
                "description": course.description,
                "instructor_id": course.instructor_id,
                "category": course.category,
                "difficulty": course.difficulty_level,
                "duration_hours": course.duration_hours,
                "total_modules": course.total_modules,
                "total_lessons": course.total_lessons
            },
            "curriculum": [
                {
                    "module": {
                        "id": item["module"].module_id,
                        "title": item["module"].title,
                        "order": item["module"].order
                    },
                    "lessons": [
                        {
                            "id": l.lesson_id,
                            "title": l.title,
                            "type": l.lesson_type,
                            "order": l.order,
                            "duration": l.estimated_duration_minutes
                        }
                        for l in item["lessons"]
                    ]
                }
                for item in curriculum
            ]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/courses/{course_id}/enroll")
async def enroll_course(
    course_id: str,
    user_id: str = Form(...),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Enroll student in course"""
    try:
        elearning = ELearningService(db)
        
        enrollment = await elearning.enroll_student(course_id, user_id)
        
        if not enrollment:
            raise HTTPException(status_code=400, detail="Could not enroll")
        
        return {
            "enrolled": True,
            "enrollment_id": enrollment.enrollment_id,
            "status": enrollment.status,
            "progress": enrollment.progress_percentage
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== EXAM ROUTES ====================

@app.post("/api/exams/{exam_id}/start")
async def start_exam(
    exam_id: str,
    user_id: str = Form(...),
    course_id: str = Form(...),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Start proctored exam"""
    try:
        proctoring = AIProctoringService(db)
        
        # Start proctoring session
        session = await proctoring.start_exam_session(
            exam_id=exam_id,
            user_id=user_id,
            course_id=course_id,
            duration_minutes=60
        )
        
        return {
            "session_id": session.session_id,
            "exam_id": exam_id,
            "status": "ready_for_identity_verification",
            "message": "Please verify your identity before starting exam"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/exams/{exam_id}/verify-identity")
async def verify_identity(
    session_id: str = Form(...),
    file: UploadFile = File(...),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Verify student identity at exam start"""
    try:
        proctoring = AIProctoringService(db)
        
        # Read image
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Verify identity
        result = await proctoring.verify_identity_at_session_start(session_id, frame)
        
        if not result["verified"]:
            raise HTTPException(status_code=401, detail="Identity verification failed")
        
        return {
            "verified": True,
            "confidence": result["confidence"],
            "message": "Identity verified. You may begin the exam."
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/api/exams/{session_id}/stream")
async def exam_stream(
    websocket: WebSocket,
    session_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """WebSocket for streaming exam frames and proctoring"""
    await websocket.accept()
    
    proctoring = AIProctoringService(db)
    frame_count = 0
    
    try:
        while True:
            # Receive frame from client
            data = await websocket.receive_bytes()
            
            # Decode frame
            nparr = np.frombuffer(data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            # Process frame
            frame_analysis = await proctoring.process_exam_frame(session_id, frame, frame_count)
            
            # Periodic re-verification every 5 minutes (30 frames at 10 FPS)
            if frame_count % 3000 == 0:
                # Send request for re-verification
                await websocket.send_json({
                    "type": "verify_identity",
                    "message": "Please show your face for identity verification"
                })
            
            # Send analysis back
            await websocket.send_json({
                "frame": frame_count,
                "violations": frame_analysis.detected_violations,
                "severity": frame_analysis.severity_score,
                "is_same_person": frame_analysis.is_same_person
            })
            
            frame_count += 1
            
            # Break if too many violations
            if frame_analysis.severity_score > 500:
                await websocket.send_json({
                    "type": "terminate",
                    "reason": "Exam terminated due to proctoring violations"
                })
                break
    
    except Exception as e:
        await websocket.send_json({"error": str(e)})
    
    finally:
        await websocket.close()

@app.post("/api/exams/{exam_id}/submit")
async def submit_exam(
    exam_id: str,
    request: ExamSubmitRequest,
    session_id: str = Form(...),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Submit exam for grading"""
    try:
        proctoring = AIProctoringService(db)
        
        # Get exam config
        exam = await db.exams.find_one({"exam_id": exam_id})
        if not exam:
            raise HTTPException(status_code=404, detail="Exam not found")
        
        # Submit and grade
        attempt = await proctoring.submit_exam(
            session_id=session_id,
            answers=request.answers,
            exam_config=exam
        )
        
        return {
            "attempt_id": attempt.attempt_id,
            "raw_score": attempt.raw_score,
            "adjusted_score": attempt.adjusted_score,
            "passing": attempt.passing,
            "violations_detected": len(attempt.violations_detected),
            "proctoring_passed": attempt.proctoring_passed,
            "feedback": attempt.grading_feedback
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== CERTIFICATE ROUTES ====================

@app.post("/api/certificates/generate")
async def generate_certificate(
    attempt_id: str = Form(...),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Generate certificate for passing exam"""
    try:
        proctoring = AIProctoringService(db)
        
        certificate = await proctoring.issue_certificate(attempt_id)
        
        return {
            "certificate_id": certificate.certificate_id,
            "certificate_number": certificate.certificate_number,
            "course_title": certificate.course_title,
            "student_name": certificate.student_name,
            "score": certificate.final_score,
            "grade": certificate.passing_grade,
            "distinction": certificate.is_with_distinction,
            "verification_code": certificate.verification_code,
            "pdf_url": certificate.pdf_url,
            "qr_code_url": certificate.qr_code_url
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/certificates/{certificate_id}/download")
async def download_certificate(
    certificate_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Download certificate PDF"""
    try:
        certificate = await db.certificates.find_one({"certificate_id": certificate_id})
        
        if not certificate:
            raise HTTPException(status_code=404, detail="Certificate not found")
        
        # In production, fetch from S3
        return FileResponse(
            path=f"certificates/{certificate_id}.pdf",
            filename=f"{certificate['student_name']}_certificate.pdf"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/certificates/verify/{verification_code}")
async def verify_certificate(
    verification_code: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Verify certificate (public endpoint)"""
    try:
        proctoring = AIProctoringService(db)
        
        certificate = await proctoring.verify_certificate(verification_code)
        
        if not certificate:
            return JSONResponse(
                status_code=404,
                content={"verified": False, "message": "Certificate not found"}
            )
        
        return {
            "verified": True,
            "certificate_number": certificate.certificate_number,
            "student_name": certificate.student_name,
            "course_title": certificate.course_title,
            "final_score": certificate.final_score,
            "issued_date": certificate.issued_date.isoformat(),
            "distinction": certificate.is_with_distinction
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== DASHBOARD ROUTES ====================

@app.get("/api/dashboard/student/{user_id}")
async def student_dashboard(
    user_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Student learning dashboard"""
    try:
        elearning = ELearningService(db)
        
        dashboard = await elearning.get_learner_dashboard(user_id)
        
        return dashboard
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard/instructor/{instructor_id}")
async def instructor_dashboard(
    instructor_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Instructor analytics dashboard"""
    try:
        elearning = ELearningService(db)
        
        courses = await elearning.get_instructor_courses(instructor_id)
        
        analytics = []
        for course in courses:
            course_analytics = await elearning.get_course_analytics(course.course_id)
            analytics.append(course_analytics)
        
        return {
            "instructor_id": instructor_id,
            "courses_created": len(courses),
            "total_students": sum(a["total_enrollments"] for a in analytics),
            "total_completions": sum(a["completed"] for a in analytics),
            "courses": analytics
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== RUN SERVER ====================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True
    )
