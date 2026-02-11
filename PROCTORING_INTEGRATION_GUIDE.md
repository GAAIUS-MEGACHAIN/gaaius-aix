# Advanced Proctoring System Integration Guide

## Overview

The Advanced Proctoring System is a comprehensive certification exam platform that combines AI-powered proctoring, identity verification, behavior monitoring, and certificate issuance. It integrates seamlessly into the eLearning platform alongside AI Tutoring and Adaptive Learning.

---

## System Architecture

### 1. Backend Components

#### `backend/proctoring_service.py` (700+ lines)
Core proctoring engine with the following models and classes:

**Data Models:**
- `CertificationExam` - Exam configuration and proctoring requirements
- `ExamAttempt` - Individual attempt tracking with security metadata
- `ProctorSession` - Live proctoring session management
- `FaceVerification` - Identity verification with face recognition
- `ExamBehavior` - Real-time behavior monitoring data
- `EnvironmentCheck` - Physical environment verification
- `ExamViolation` - Violation detection and severity tracking
- `CertificateIssuance` - Certificate records with integrity verification

**ProctoringEngine Class:**
```python
engine = ProctoringEngine(db_session, config)

# Initialize proctored exam session
session = engine.initialize_exam_session(
    exam_id="exam-001",
    student_id="student-001",
    duration_minutes=120
)

# Verify student identity
face_verified = engine.verify_student_identity(
    exam_id="exam-001",
    student_id="student-001",
    captured_image=image_bytes,
    face_embedding=embedding
)

# Check environment
env_ok = engine.check_environment(
    exam_id="exam-001",
    session_id=session.id,
    environment_data={
        "room_clear": True,
        "monitors": 1,
        "audio_available": True,
        "video_available": True,
        "connection_quality": 0.95
    }
)

# Monitor behavior
behavior = engine.monitor_behavior(
    session_id=session.id,
    behavior_data={
        "gaze_direction": "center",
        "posture_normal": True,
        "hand_presence": True,
        "scroll_speed": 100,
        "timestamp": "2024-01-22T10:30:00Z"
    }
)

# Calculate integrity score
score = engine.calculate_integrity_score(
    exam_id="exam-001",
    student_id="student-001"
)

# Flag for review if needed
should_review = engine.should_flag_for_review(score)
```

**CertificateVerificationService Class:**
```python
cert_service = CertificateVerificationService(db_session)

# Generate certificate
cert = cert_service.generate_certificate(
    exam_attempt_id="attempt-001",
    student_name="John Doe",
    score=85.5
)

# Verify certificate (public)
is_valid = cert_service.verify_certificate(
    certificate_number="CERT-20240122-ABC123XY"
)

# Verify with hash
is_valid = cert_service.verify_certificate(
    certificate_number="CERT-20240122-ABC123XY",
    hash_verification=True
)
```

### 2. API Endpoints

All endpoints are registered at `/api/v1/proctoring/*`

#### Exam Management
```
POST   /proctoring/exams
GET    /proctoring/exams/{exam_id}
PUT    /proctoring/exams/{exam_id}
DELETE /proctoring/exams/{exam_id}
GET    /proctoring/exams/course/{course_id}
```

#### Session Management
```
POST   /proctoring/sessions/start
POST   /proctoring/sessions/{session_id}/end
GET    /proctoring/sessions/{session_id}
```

#### Identity Verification
```
POST   /proctoring/verify/identity
POST   /proctoring/verify/environment
```

#### Behavior Monitoring
```
POST   /proctoring/monitor/behavior
```

#### Violation Detection
```
GET    /proctoring/violations/{exam_id}/{student_id}
POST   /proctoring/violations/{violation_id}/review
GET    /proctoring/violations/stats/{exam_id}
```

#### Exam Submission & Grading
```
POST   /proctoring/attempts/{attempt_id}/submit
POST   /proctoring/attempts/{attempt_id}/grade
```

#### Certificate Management
```
POST   /proctoring/certificates/issue
GET    /proctoring/certificates/{certificate_number}/verify
POST   /proctoring/certificates/{certificate_id}/revoke
```

#### Analytics
```
GET    /proctoring/analytics/exam/{exam_id}
GET    /proctoring/analytics/student/{student_id}
GET    /proctoring/health
```

### 3. Frontend Components

#### ProctoringDashboard.jsx
Real-time exam monitoring interface with:
- Live webcam stream with face capture
- Integrity score visualization (0-100%)
- Face verification status
- Environment check status
- Countdown timer (HH:MM:SS)
- Violation detection list
- Environment checklist
- Proctor notes
- Action buttons (re-verify, check environment, end session)

#### CertificationExamPage.jsx
Complete exam delivery system with:
- Pre-exam proctoring setup
- Question delivery (multiple choice format)
- Answer tracking
- Real-time integrity monitoring
- Exam submission
- Certificate issuance and preview
- Certificate download/share functionality

---

## Integration Steps

### Step 1: Verify Backend Installation

Check that proctoring routes are registered in `backend/server.py`:

```python
# Lines 10290-10299 in server.py
from backend.proctoring_routes import router as router_proctoring
app.include_router(router_proctoring, prefix="/api/v1", tags=["proctoring"])
```

**Test endpoints:**
```bash
# Health check
curl http://localhost:8000/api/v1/proctoring/health

# Create exam
curl -X POST http://localhost:8000/api/v1/proctoring/exams \
  -H "Content-Type: application/json" \
  -d '{
    "title": "JavaScript Certification",
    "duration_minutes": 120,
    "passing_score": 70,
    "proctor_mode": "hybrid",
    "integrity_level": "high"
  }'
```

### Step 2: Add Proctoring to Course Structure

Update `backend/courses.py` to include proctoring requirements:

```python
class CourseWithCertification(CourseBase):
    """Course with certification exam proctoring"""
    has_certification: bool = False
    certification_exam_id: Optional[str] = None
    certification_requirements: Optional[dict] = None

# In course model
course.certification_requirements = {
    "proctor_mode": "hybrid",
    "integrity_level": "high",
    "min_passing_score": 70,
    "duration_minutes": 120
}
```

### Step 3: Integrate Proctoring into eLearning Routes

Add certification exam routes to `frontend/src/App.js`:

```jsx
// Import certification page
import CertificationExamPage from './pages/CertificationExamPage';

// Add route
<Route path="/exam/certification/:examId" element={<CertificationExamPage />} />

// Add sidebar button
<SidebarButton icon={Award} label="Certifications" path="/certifications" />
```

### Step 4: Create Certification Management Page

```jsx
// frontend/src/pages/CertificationsPage.jsx

import React, { useState, useEffect } from 'react';
import CertificationExamPage from '../components/CertificationExamPage';
import { Award, Download, Share2, Check } from 'lucide-react';
import axios from 'axios';

export default function CertificationsPage() {
  const [availableExams, setAvailableExams] = useState([]);
  const [completedCerts, setCompletedCerts] = useState([]);
  const [selectedExam, setSelectedExam] = useState(null);

  useEffect(() => {
    loadCertifications();
  }, []);

  const loadCertifications = async () => {
    try {
      // Load available exams
      const examsRes = await axios.get('/api/v1/proctoring/exams/course/course-001');
      setAvailableExams(examsRes.data);

      // Load student's completed certifications
      const certsRes = await axios.get('/api/v1/proctoring/analytics/student/student-001');
      setCompletedCerts(certsRes.data.completed_certificates);
    } catch (error) {
      console.error('Failed to load certifications:', error);
    }
  };

  if (selectedExam) {
    return <CertificationExamPage examId={selectedExam} courseId="course-001" />;
  }

  return (
    <div>
      <h1>Professional Certifications</h1>

      {/* Available Exams */}
      <div>
        <h2>Available Exams</h2>
        {availableExams.map(exam => (
          <div key={exam.exam_id}>
            <h3>{exam.title}</h3>
            <button onClick={() => setSelectedExam(exam.exam_id)}>
              Start Exam
            </button>
          </div>
        ))}
      </div>

      {/* Completed Certifications */}
      <div>
        <h2>Your Certificates</h2>
        {completedCerts.map(cert => (
          <div key={cert.certificate_id}>
            <p>{cert.student_name}</p>
            <p>Score: {cert.score.toFixed(1)}%</p>
            <button><Download /> Download</button>
            <button><Share2 /> Share</button>
          </div>
        ))}
      </div>
    </div>
  );
}
```

### Step 5: Connect Adaptive Learning to Proctoring

Pass proficiency levels to proctoring system:

```python
# In adaptive_learning_routes.py
@router.post("/recommendations/exam")
def get_exam_recommendations(student_id: str, course_id: str):
    """Get recommended exams based on learning proficiency"""
    
    # Get student proficiency
    path = learning_path_service.get_student_path(student_id, course_id)
    proficiency = path.proficiency_score
    
    # Get recommended exams
    exams = proctoring_service.get_recommended_exams(
        student_proficiency=proficiency,
        min_score_threshold=proficiency * 100
    )
    
    return {"recommended_exams": exams}
```

---

## Proctoring Modes

### 1. LIVE Proctoring
- Real-time human proctor supervision
- Live monitoring of exam session
- Real-time violation alerts
- Manual review of suspicious activity
- Best for: High-stakes certifications

**Usage:**
```python
exam = CertificationExam(
    proctor_mode="live",
    integrity_level="maximum",
    has_human_proctor=True
)
```

### 2. AUTOMATED Proctoring
- AI-powered behavior monitoring
- Automatic violation detection
- Pattern-based integrity analysis
- No human interaction required
- Best for: Mid-level assessments

**Usage:**
```python
exam = CertificationExam(
    proctor_mode="automated",
    integrity_level="high"
)
```

### 3. HYBRID Proctoring
- Combination of AI and human oversight
- AI flags suspicious activity
- Human proctor reviews flagged sessions
- Most cost-effective for compliance
- Best for: Professional certifications

**Usage:**
```python
exam = CertificationExam(
    proctor_mode="hybrid",
    integrity_level="high",
    has_human_proctor=True
)
```

### 4. OFFLINE Proctoring
- No real-time proctoring
- No behavior monitoring
- Low security level
- Best for: Low-stakes knowledge checks

**Usage:**
```python
exam = CertificationExam(
    proctor_mode="offline",
    integrity_level="low"
)
```

---

## Violation Types and Responses

The system detects 9 types of violations:

| Violation Type | Severity | Response |
|---|---|---|
| **SUSPICIOUS_BEHAVIOR** | CRITICAL | Flag for manual review |
| **MULTIPLE_FACES** | CRITICAL | Pause exam, require verification |
| **FACE_MISSING** | CAUTION | Warning, 3-strike rule |
| **WINDOW_CHANGE** | WARNING | Record event, 5-strike rule |
| **AUDIO_CHEAT** | CRITICAL | Record audio sample, flag |
| **COPY_PASTE** | CRITICAL | Disable clipboard, flag |
| **UNAUTHORIZED_DEVICE** | CRITICAL | Record device ID, flag |
| **RAPID_SCROLLING** | CAUTION | Record scroll pattern |
| **MOBILE_PHONE** | CAUTION | Warning, record detection |

### Integrity Score Calculation

```
Base Score = 1.0 (100%)

Deductions:
- CRITICAL violation: -0.30 per violation
- CAUTION violation: -0.10 per violation
- WARNING violation: -0.05 per violation
- Face not verified: -0.20
- Behavior risk: -0.20 * avg_behavior_risk

Final Score = max(0, Base Score - Deductions)
```

---

## API Response Examples

### Start Session
```json
{
  "session_id": "session-abc123",
  "exam_id": "exam-001",
  "student_id": "student-001",
  "mode": "hybrid",
  "start_time": "2024-01-22T10:00:00Z",
  "status": "active",
  "session_key": "sk_1234567890abcdef"
}
```

### Verify Identity Response
```json
{
  "verified": true,
  "confidence": 0.98,
  "face_embedding": [0.1, 0.2, ...],
  "liveness_score": 0.95,
  "timestamp": "2024-01-22T10:05:00Z"
}
```

### Monitoring Response
```json
{
  "session_id": "session-abc123",
  "behavior_risk": 0.15,
  "violations_detected": ["WINDOW_CHANGE"],
  "integrity_score": 0.92,
  "status": "normal",
  "recommendations": []
}
```

### Certificate Issuance
```json
{
  "certificate_id": "cert-xyz789",
  "certificate_number": "CERT-20240122-ABC123XY",
  "student_name": "John Doe",
  "exam_title": "Advanced JavaScript Certification",
  "score": 85.5,
  "grade": "B",
  "issue_date": "2024-01-22",
  "expiration_date": "2026-01-22",
  "integrity_verified": true,
  "credential_url": "https://gaaius.ai/verify/CERT-20240122-ABC123XY"
}
```

---

## Testing Endpoints

### 1. Create an Exam
```bash
curl -X POST http://localhost:8000/api/v1/proctoring/exams \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Python Certification",
    "description": "Master Python programming",
    "duration_minutes": 120,
    "passing_score": 70,
    "total_questions": 100,
    "proctor_mode": "hybrid",
    "integrity_level": "high"
  }'
```

### 2. Start Exam Session
```bash
curl -X POST "http://localhost:8000/api/v1/proctoring/sessions/start?exam_id=exam-001&student_id=student-001" \
  -H "Content-Type: application/json"
```

### 3. Verify Identity
```bash
# (Requires image upload)
curl -X POST "http://localhost:8000/api/v1/proctoring/verify/identity?exam_id=exam-001&student_id=student-001" \
  -F "captured_image=@photo.jpg" \
  -H "Accept: application/json"
```

### 4. Monitor Behavior
```bash
curl -X POST "http://localhost:8000/api/v1/proctoring/monitor/behavior?exam_id=exam-001&student_id=student-001" \
  -H "Content-Type: application/json" \
  -d '{
    "gaze_direction": "center",
    "posture_normal": true,
    "hand_presence": true,
    "scroll_speed": 100
  }'
```

### 5. Submit Exam
```bash
curl -X POST "http://localhost:8000/api/v1/proctoring/attempts/attempt-001/submit" \
  -H "Content-Type: application/json" \
  -d '{
    "answers": {
      "q1": "Option A",
      "q2": "Option C"
    }
  }'
```

### 6. Issue Certificate
```bash
curl -X POST http://localhost:8000/api/v1/proctoring/certificates/issue \
  -H "Content-Type: application/json" \
  -d '{
    "exam_attempt_id": "attempt-001",
    "exam_id": "exam-001",
    "student_id": "student-001",
    "student_name": "John Doe",
    "score": 85.5
  }'
```

### 7. Verify Certificate
```bash
curl http://localhost:8000/api/v1/proctoring/certificates/CERT-20240122-ABC123XY/verify
```

---

## Database Schema Integration

Add these tables to your database:

```sql
-- Certification Exams
CREATE TABLE certification_exams (
    exam_id VARCHAR(36) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    duration_minutes INT,
    passing_score FLOAT,
    total_questions INT,
    proctor_mode VARCHAR(20),
    integrity_level VARCHAR(20),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Exam Attempts
CREATE TABLE exam_attempts (
    attempt_id VARCHAR(36) PRIMARY KEY,
    exam_id VARCHAR(36),
    student_id VARCHAR(36),
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    submission_time TIMESTAMP,
    score FLOAT,
    passed BOOLEAN,
    integrity_score FLOAT,
    flagged_for_review BOOLEAN,
    FOREIGN KEY (exam_id) REFERENCES certification_exams(exam_id)
);

-- Certificates
CREATE TABLE certificates (
    certificate_id VARCHAR(36) PRIMARY KEY,
    certificate_number VARCHAR(50) UNIQUE,
    attempt_id VARCHAR(36),
    student_name VARCHAR(255),
    score FLOAT,
    grade VARCHAR(5),
    issue_date DATE,
    expiration_date DATE,
    integrity_hash VARCHAR(255),
    revoked BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (attempt_id) REFERENCES exam_attempts(attempt_id)
);

-- Violations
CREATE TABLE exam_violations (
    violation_id VARCHAR(36) PRIMARY KEY,
    attempt_id VARCHAR(36),
    violation_type VARCHAR(50),
    severity VARCHAR(20),
    evidence TEXT,
    confidence FLOAT,
    detected_at TIMESTAMP,
    FOREIGN KEY (attempt_id) REFERENCES exam_attempts(attempt_id)
);
```

---

## Security Considerations

### 1. Face Recognition
- Uses OpenFace or similar libraries
- Stores face embeddings (not raw images)
- 98%+ confidence threshold for verification
- Liveness detection prevents spoofing

### 2. Violation Thresholds
- Configurable per exam mode
- Progressive penalties for repeated violations
- Automatic flagging at critical severity
- Human review for flagged attempts

### 3. Certificate Integrity
- SHA256 hash verification
- Certificate number format: CERT-YYYYMMDD-RANDOMID
- Tamper-proof storage
- Public verification endpoint

### 4. Data Privacy
- Behavior data not permanently stored
- Video/audio deleted after exam
- Encrypted session storage
- Compliance with GDPR/CCPA

---

## Troubleshooting

### Proctoring Routes Not Working
```python
# Check server.py for registration
grep -n "proctoring_routes" backend/server.py

# Should see:
# from backend.proctoring_routes import router as router_proctoring
# app.include_router(router_proctoring, prefix="/api/v1")
```

### Face Verification Failing
```
Common causes:
1. Insufficient lighting - Advise student to improve lighting
2. Face at wrong angle - Need frontal view
3. Confidence < 98% - Request student to move closer
4. Spoofing detected - Liveness check failed
```

### Certificate Not Issued
```
Check:
1. Exam score >= passing_score
2. Integrity score >= 0.6
3. No critical violations
4. Student identity verified
```

### Violation False Positives
```
Adjust in config:
- gaze_tolerance: Increase if eye tracking too strict
- scroll_threshold: Increase if normal scrolling flagged
- posture_threshold: Increase if movement too restricted
```

---

## Best Practices

1. **Pre-Exam Checks**
   - Test camera and microphone before exam starts
   - Verify environment meets requirements
   - Confirm internet connection stability

2. **During Exam**
   - Continuous behavior monitoring at 5-second intervals
   - Warn student of violations before failing
   - Allow 3 warnings before critical violations

3. **Post-Exam**
   - Review flagged attempts within 24 hours
   - Keep violation evidence for 6 months
   - Archive certificates indefinitely

4. **Compliance**
   - Document all violations
   - Maintain audit trail
   - Allow student appeals within 30 days

---

## Support & Documentation

**Files:**
- Backend: `backend/proctoring_service.py`, `backend/proctoring_routes.py`
- Frontend: `frontend/src/components/ProctoringDashboard.jsx`, `frontend/src/pages/CertificationExamPage.jsx`
- Integration: `frontend/src/pages/CertificationsPage.jsx`

**API Base:** `http://localhost:8000/api/v1/proctoring`

**Quick Links:**
- [API Documentation](#api-endpoints)
- [Violation Reference](#violation-types-and-responses)
- [Testing Guide](#testing-endpoints)

---

## Next Steps

1. ✅ Install backend proctoring service
2. ✅ Create certification exams
3. ⏳ Set up proctor roles and assignments
4. ⏳ Configure security thresholds
5. ⏳ Train on platform usage
6. ⏳ Launch pilot certification program

---

**Last Updated:** January 22, 2024
**Version:** 1.0.0
**Status:** Production Ready
