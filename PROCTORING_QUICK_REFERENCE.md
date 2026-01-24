# Advanced Proctoring System - Quick Reference Card

## 🚀 Quick Start (5 minutes)

### Start Services
```bash
# Terminal 1: Backend
cd backend && python server.py

# Terminal 2: Frontend
cd frontend && npm start

# Access: http://localhost:3000/exam/certification/exam-001
```

---

## 🔧 Common Tasks

### Create a Certification Exam
```bash
curl -X POST http://localhost:8000/api/v1/proctoring/exams \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Your Exam Title",
    "description": "Exam description",
    "duration_minutes": 120,
    "passing_score": 70,
    "total_questions": 100,
    "proctor_mode": "hybrid",
    "integrity_level": "high"
  }'

# Response: {"exam_id": "exam-abc123", ...}
```

### Start Exam Session
```bash
curl -X POST "http://localhost:8000/api/v1/proctoring/sessions/start?exam_id=exam-001&student_id=student-001"

# Response: {"session_id": "session-xyz789", "status": "active", ...}
```

### Verify Student Identity
```bash
curl -X POST "http://localhost:8000/api/v1/proctoring/verify/identity?exam_id=exam-001&student_id=student-001" \
  -F "captured_image=@photo.jpg"

# Response: {"verified": true, "confidence": 0.98, ...}
```

### Monitor Behavior (Call every 5 seconds)
```bash
curl -X POST "http://localhost:8000/api/v1/proctoring/monitor/behavior?exam_id=exam-001&student_id=student-001" \
  -H "Content-Type: application/json" \
  -d '{
    "gaze_direction": "center",
    "posture_normal": true,
    "hand_presence": true,
    "scroll_speed": 100
  }'

# Response: {"behavior_risk": 0.15, "violations_detected": [], "integrity_score": 0.92}
```

### Submit Exam
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

### Grade Exam
```bash
curl -X POST "http://localhost:8000/api/v1/proctoring/attempts/attempt-001/grade" \
  -H "Content-Type: application/json" \
  -d '{"score": 85.5}'
```

### Issue Certificate
```bash
curl -X POST "http://localhost:8000/api/v1/proctoring/certificates/issue" \
  -H "Content-Type: application/json" \
  -d '{
    "exam_attempt_id": "attempt-001",
    "exam_id": "exam-001",
    "student_id": "student-001",
    "student_name": "John Doe",
    "score": 85.5
  }'

# Response: {
#   "certificate_id": "cert-xyz",
#   "certificate_number": "CERT-20240122-ABC123XY",
#   "credential_url": "https://gaaius.ai/verify/...",
#   ...
# }
```

### Verify Certificate (Public)
```bash
curl "http://localhost:8000/api/v1/proctoring/certificates/CERT-20240122-ABC123XY/verify"

# Response: {"valid": true, "verified": true, "expiration_date": "2026-01-22"}
```

### Get Violations
```bash
curl "http://localhost:8000/api/v1/proctoring/violations/exam-001/student-001"

# Response: {
#   "violations": [
#     {"type": "WINDOW_CHANGE", "severity": "WARNING", "confidence": 0.92}
#   ]
# }
```

### Review Violation
```bash
curl -X POST "http://localhost:8000/api/v1/proctoring/violations/violation-id/review" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "approved",
    "notes": "False positive - student was taking notes"
  }'
```

### Get Exam Analytics
```bash
curl "http://localhost:8000/api/v1/proctoring/analytics/exam/exam-001"

# Response: {
#   "total_attempts": 50,
#   "passed_count": 42,
#   "avg_score": 78.5,
#   "avg_integrity_score": 0.88,
#   "violation_types": {...}
# }
```

### Get Student History
```bash
curl "http://localhost:8000/api/v1/proctoring/analytics/student/student-001"

# Response: {
#   "exam_attempts": 3,
#   "passed_exams": 2,
#   "certificates": ["CERT-ABC", "CERT-XYZ"],
#   "avg_integrity_score": 0.90
# }
```

### End Exam Session
```bash
curl -X POST "http://localhost:8000/api/v1/proctoring/sessions/session-id/end" \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Check Health
```bash
curl "http://localhost:8000/api/v1/proctoring/health"

# Response: {"status": "healthy", "version": "1.0.0"}
```

---

## 📊 Proctoring Modes Quick Guide

### LIVE Proctoring
```json
{
  "proctor_mode": "live",
  "integrity_level": "maximum",
  "has_human_proctor": true
}
```
- Real-time human supervision
- Manual violation review
- Most expensive, most secure

### AUTOMATED Proctoring
```json
{
  "proctor_mode": "automated",
  "integrity_level": "high",
  "has_human_proctor": false
}
```
- AI-only monitoring
- Automatic violation detection
- Scalable, cost-effective

### HYBRID Proctoring
```json
{
  "proctor_mode": "hybrid",
  "integrity_level": "high",
  "has_human_proctor": true
}
```
- AI monitoring + human review
- Flagged exams reviewed manually
- Best balance of security & cost

### OFFLINE Proctoring
```json
{
  "proctor_mode": "offline",
  "integrity_level": "low",
  "has_human_proctor": false
}
```
- No proctoring
- Low-stakes assessments
- Lowest cost

---

## 🚨 Violation Types Reference

| Type | Severity | Meaning |
|---|---|---|
| **SUSPICIOUS_BEHAVIOR** | 🔴 CRITICAL | Unusual activity pattern detected |
| **MULTIPLE_FACES** | 🔴 CRITICAL | More than one person in frame |
| **FACE_MISSING** | 🟡 CAUTION | Student's face not visible |
| **WINDOW_CHANGE** | 🟡 WARNING | Tab/window switch detected |
| **AUDIO_CHEAT** | 🔴 CRITICAL | Unauthorized audio detected |
| **COPY_PASTE** | 🔴 CRITICAL | Clipboard activity detected |
| **UNAUTHORIZED_DEVICE** | 🔴 CRITICAL | Unknown device connected |
| **RAPID_SCROLLING** | 🟡 CAUTION | Abnormally fast scrolling |
| **MOBILE_PHONE** | 🟡 CAUTION | Mobile device detected |

---

## 🎯 Integrity Score Interpretation

| Score | Rating | Status |
|---|---|---|
| **0.90-1.00** | 🟢 Excellent | No concerns |
| **0.70-0.89** | 🟡 Good | Minor warnings |
| **0.50-0.69** | 🟠 Fair | Needs review |
| **0.00-0.49** | 🔴 Poor | Major concerns |

**Auto-flag threshold:** < 0.60 (flagged for human review)

---

## 📱 Frontend Integration

### Use ProctoringDashboard
```jsx
import ProctoringDashboard from './components/ProctoringDashboard';

<ProctoringDashboard
  examId="exam-001"
  studentId="student-001"
  examDuration={120}
/>
```

### Use CertificationExamPage
```jsx
import CertificationExamPage from './pages/CertificationExamPage';

<CertificationExamPage
  examId="exam-001"
  courseId="course-001"
/>
```

---

## 🔐 Security Settings

### High Security (Most Common)
```json
{
  "integrity_level": "high",
  "requires_face_verification": true,
  "requires_environment_check": true,
  "continuous_monitoring": true,
  "monitoring_interval_seconds": 5,
  "allow_window_change": false,
  "allow_copy_paste": false,
  "allow_mobile_devices": false
}
```

### Maximum Security (Certifications)
```json
{
  "integrity_level": "maximum",
  "requires_face_verification": true,
  "requires_environment_check": true,
  "requires_human_proctor": true,
  "continuous_monitoring": true,
  "monitoring_interval_seconds": 2,
  "allow_window_change": false,
  "allow_copy_paste": false,
  "allow_mobile_devices": false,
  "allow_only_single_monitor": true
}
```

### Medium Security (Regular Exams)
```json
{
  "integrity_level": "medium",
  "requires_face_verification": true,
  "requires_environment_check": true,
  "continuous_monitoring": true,
  "monitoring_interval_seconds": 10,
  "allow_window_change": 3,
  "allow_copy_paste": false
}
```

### Low Security (Knowledge Checks)
```json
{
  "integrity_level": "low",
  "requires_face_verification": false,
  "requires_environment_check": false,
  "continuous_monitoring": false
}
```

---

## 🧪 Testing Checklist

- [ ] Start exam session → session_id returned
- [ ] Verify identity → face verified = true
- [ ] Check environment → environment_ok = true
- [ ] Monitor behavior → behavior_risk < 0.3
- [ ] Detect violations → violations list populated
- [ ] Submit exam → submission_time recorded
- [ ] Grade exam → score calculated
- [ ] Issue certificate → certificate_number generated
- [ ] Verify certificate → certificate valid = true
- [ ] Get analytics → statistics populated
- [ ] Check health → status = "healthy"

---

## 🐛 Troubleshooting Quick Fixes

### Endpoints not responding
```bash
# Check server is running
curl http://localhost:8000/api/v1/proctoring/health

# Check routes registered
grep -n "proctoring" backend/server.py
```

### Face verification failing
- **Problem:** Confidence < 98%
- **Solution:** Improve lighting, move closer to camera, ensure frontal view

### Certificate not issued
- **Problem:** Score < passing_score OR integrity_score < 0.6
- **Solution:** Check exam grading, verify no critical violations

### Violations false positives
- **Problem:** Students getting flagged incorrectly
- **Solution:** Adjust thresholds in proctoring_service.py

### Syntax errors in Python
```bash
# Verify files
python -m py_compile backend/proctoring_service.py
python -m py_compile backend/proctoring_routes.py
```

---

## 📚 File Locations

| File | Purpose | Lines |
|---|---|---|
| `backend/proctoring_service.py` | Core engine | 700+ |
| `backend/proctoring_routes.py` | API endpoints | 500+ |
| `backend/server.py` | Route registration | Lines 10290-10299 |
| `frontend/src/components/ProctoringDashboard.jsx` | Monitoring UI | 500+ |
| `frontend/src/pages/CertificationExamPage.jsx` | Exam delivery | 800+ |
| `PROCTORING_INTEGRATION_GUIDE.md` | Full documentation | 500+ |
| `PROCTORING_SYSTEM_COMPLETE.md` | Implementation summary | 400+ |

---

## 🔗 Related Resources

- **Full Guide:** `PROCTORING_INTEGRATION_GUIDE.md`
- **Completion Status:** `PROCTORING_SYSTEM_COMPLETE.md`
- **API Reference:** Lines 1-50 in `backend/proctoring_routes.py`
- **Data Models:** Lines 1-100 in `backend/proctoring_service.py`

---

## 💡 Pro Tips

1. **Test Mode:** Use `proctor_mode="automated"` for testing
2. **Gentle Learning:** Start with `integrity_level="low"` then increase
3. **Batch Creation:** Create multiple exams at once for efficiency
4. **Analytics:** Review `analytics/exam/{exam_id}` weekly
5. **Certificates:** Use credential URLs for LinkedIn/resume verification

---

**Last Updated:** January 22, 2024
**Quick Reference Version:** 1.0.0
