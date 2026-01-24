================================================================================
🧪 AI TUTORING ENGINE - TESTING & VALIDATION GUIDE
================================================================================

PURPOSE: Verify AI Tutoring Engine integration and functionality

================================================================================
PRE-TEST CHECKLIST
================================================================================

□ GROQ_API_KEY environment variable is set
□ Server.py has been updated with AI Tutoring import
□ ai_tutoring_engine.py exists in backend/
□ Server is running: python run_server.py
□ Base API URL available: http://localhost:8000

To verify environment:
  PowerShell: $env:GROQ_API_KEY
  Bash: echo $GROQ_API_KEY

================================================================================
TEST 1: SERVER STARTUP VERIFICATION
================================================================================

Objective: Verify server starts with tutoring engine loaded

Steps:
  1. Start server: python run_server.py
  2. Watch for startup logs
  3. Look for this message in logs:
     "✅ AI Tutoring Engine routes registered"

Expected Result:
  ✅ Server starts without errors
  ✅ Tutoring routes registered successfully
  ✅ No "Failed to register" warnings
  ✅ Server responds to health checks

If Failed:
  - Check GROQ_API_KEY is set
  - Verify ai_tutoring_engine.py syntax
  - Check server.py imports
  - Review logs/app.log for errors

================================================================================
TEST 2: SESSION INITIALIZATION
================================================================================

Objective: Test starting a tutoring session

Command:
  curl -X POST http://localhost:8000/api/tutoring/session/start \
    -H "Content-Type: application/json" \
    -d '{
      "student_id": "test_student_001",
      "course_id": "bio_101",
      "lesson_id": "lesson_photosynthesis",
      "topic": "Photosynthesis",
      "mode": "explanation",
      "difficulty": "intermediate"
    }'

Expected Response:
  {
    "success": true,
    "session_id": "tut_test_student_001_lesson_photosynthesis_1705848600",
    "mode": "explanation",
    "started_at": "2024-01-21T10:30:00"
  }

Validation:
  ✅ "success": true
  ✅ "session_id" format matches: tut_<student>_<lesson>_<timestamp>
  ✅ "mode" matches request
  ✅ Response time < 2 seconds

Save session_id for next tests!

================================================================================
TEST 3: EXPLANATION REQUEST
================================================================================

Objective: Test AI explanation generation

Command:
  curl -X POST http://localhost:8000/api/tutoring/explanation \
    -H "Content-Type: application/json" \
    -d '{
      "topic": "Photosynthesis",
      "difficulty": "intermediate"
    }'

Expected Response:
  {
    "success": true,
    "topic": "Photosynthesis",
    "difficulty": "intermediate",
    "explanation": "Photosynthesis is the process where plants...",
    "model": "mixtral-8x7b-32768",
    "generated_at": "2024-01-21T10:30:15"
  }

Validation:
  ✅ "success": true
  ✅ "explanation" is not empty
  ✅ "explanation" length > 500 characters
  ✅ "model" = "mixtral-8x7b-32768"
  ✅ Response time < 5 seconds
  ✅ Language appropriate for difficulty level

Difficulty Variations (test all):
  - "beginner": Simpler language, analogies
  - "intermediate": Technical terms, depth
  - "advanced": Research citations, complexity
  - "expert": Cutting-edge, nuanced

================================================================================
TEST 4: PRACTICE QUESTION GENERATION
================================================================================

Objective: Test generating practice questions

Command:
  curl -X POST http://localhost:8000/api/tutoring/practice-questions \
    -H "Content-Type: application/json" \
    -d '{
      "student_id": "test_student_001",
      "lesson_id": "lesson_photosynthesis",
      "topic": "Photosynthesis",
      "difficulty": "intermediate",
      "count": 3
    }'

Expected Response:
  {
    "success": true,
    "topic": "Photosynthesis",
    "difficulty": "intermediate",
    "count": 3,
    "questions": "Question 1: What is the main purpose...\nQuestion 2: Which molecules...",
    "model": "mixtral-8x7b-32768",
    "generated_at": "2024-01-21T10:30:20"
  }

Validation:
  ✅ "success": true
  ✅ "questions" contains all 3 questions
  ✅ Questions are numbered
  ✅ Questions have multiple parts or options
  ✅ Difficulty matches request
  ✅ Response time < 5 seconds

Test Different Counts:
  - count: 1 (single question)
  - count: 3 (multiple questions)
  - count: 5 (max questions)

================================================================================
TEST 5: ANSWER EVALUATION
================================================================================

Objective: Test answer evaluation and feedback

Command:
  curl -X POST http://localhost:8000/api/tutoring/evaluate-answer \
    -H "Content-Type: application/json" \
    -d '{
      "question": "What is photosynthesis?",
      "student_answer": "Process where plants use sunlight to make food",
      "correct_answer": "Process where plants use light energy, water, and CO2 to produce glucose and oxygen"
    }'

Expected Response:
  {
    "success": true,
    "evaluation": "Your answer captures...",
    "score": 75,
    "feedback": "Good start, but you missed...",
    "model": "mixtral-8x7b-32768",
    "generated_at": "2024-01-21T10:30:25"
  }

Validation:
  ✅ "success": true
  ✅ "score" is 0-100
  ✅ "evaluation" explains what's correct
  ✅ "feedback" identifies gaps
  ✅ Response time < 3 seconds

Test Multiple Answers:
  - Correct answer: score should be 90+
  - Partial answer: score should be 60-80
  - Wrong answer: score should be 0-40
  - Blank answer: score should be 0

================================================================================
TEST 6: SOCRATIC METHOD
================================================================================

Objective: Test Socratic questioning

Command:
  curl -X POST http://localhost:8000/api/tutoring/socratic-question \
    -H "Content-Type: application/json" \
    -d '{
      "topic": "Photosynthesis",
      "student_response": "Plants make food from sunlight"
    }'

Expected Response:
  {
    "success": true,
    "question": "That'\''s a good start! Now, where does...",
    "hint": "Think about what else plants need...",
    "method": "socratic",
    "model": "mixtral-8x7b-32768",
    "generated_at": "2024-01-21T10:30:30"
  }

Validation:
  ✅ "success": true
  ✅ "question" builds on student response
  ✅ "question" is open-ended, not yes/no
  ✅ "hint" provided if available
  ✅ "method" = "socratic"
  ✅ Response time < 3 seconds

Socratic Progression (test sequence):
  Response 1: "Plants need sunlight"
    → Question: "What else do plants need?"
  Response 2: "They need water"
    → Question: "Where does the energy go?"
  Response 3: "Into glucose"
    → Question: "What happens to the glucose?"

================================================================================
TEST 7: STUDY PLAN GENERATION
================================================================================

Objective: Test generating personalized study plans

Command:
  curl -X POST http://localhost:8000/api/tutoring/study-plan \
    -H "Content-Type: application/json" \
    -d '{
      "student_id": "test_student_001",
      "weak_topics": ["Photosynthesis", "Cellular Respiration"],
      "strong_topics": ["Basic Cell Biology"],
      "current_level": "intermediate"
    }'

Expected Response:
  {
    "success": true,
    "study_plan": "2-Week Study Plan:\nWeek 1: Photosynthesis basics...",
    "estimated_hours": 10,
    "milestones": ["Complete photosynthesis quiz by Wed"],
    "model": "mixtral-8x7b-32768",
    "generated_at": "2024-01-21T10:30:35"
  }

Validation:
  ✅ "success": true
  ✅ "study_plan" length > 500 characters
  ✅ "study_plan" includes timeline
  ✅ "study_plan" references weak topics
  ✅ "milestones" array has items
  ✅ Response time < 5 seconds

Content Validation:
  ✅ Mentions weak topics in plan
  ✅ Prioritizes weak areas
  ✅ Includes review of strong areas
  ✅ Has specific daily/weekly breakdown
  ✅ Includes assessment points

================================================================================
TEST 8: SESSION RETRIEVAL
================================================================================

Objective: Test retrieving session details

Command (replace session_id with actual from Test 2):
  curl -X GET http://localhost:8000/api/tutoring/session/tut_test_student_001_lesson_photosynthesis_1705848600 \
    -H "Content-Type: application/json"

Expected Response:
  {
    "success": true,
    "session_id": "tut_test_student_001_lesson_photosynthesis_1705848600",
    "student_id": "test_student_001",
    "mode": "explanation",
    "status": "active",
    "started_at": "2024-01-21T10:30:00",
    "messages": []
  }

Validation:
  ✅ "success": true
  ✅ "session_id" matches request
  ✅ "status" = "active" or "completed"
  ✅ "started_at" timestamp valid
  ✅ Response time < 1 second

================================================================================
TEST 9: COMPLETE TUTORING RESPONSE
================================================================================

Objective: Test complete tutoring workflow

Command:
  curl -X POST http://localhost:8000/api/tutoring/tutoring-response \
    -H "Content-Type: application/json" \
    -d '{
      "session_id": "tut_test_student_001_lesson_photosynthesis_1705848600",
      "student_message": "I don'\''t understand how plants get energy",
      "mode": "explanation"
    }'

Expected Response:
  {
    "success": true,
    "response": "Great question! Let me explain...",
    "follow_up": "Do you understand why light is important?",
    "resources": ["https://example.com/photosynthesis"],
    "model": "mixtral-8x7b-32768",
    "generated_at": "2024-01-21T10:30:40"
  }

Validation:
  ✅ "success": true
  ✅ "response" directly addresses question
  ✅ "follow_up" continues learning
  ✅ Response time < 5 seconds
  ✅ Response is clear and helpful

================================================================================
TEST 10: ERROR HANDLING
================================================================================

Objective: Verify error handling and fallbacks

Test Missing Required Field:
  curl -X POST http://localhost:8000/api/tutoring/explanation \
    -H "Content-Type: application/json" \
    -d '{"difficulty": "intermediate"}'

Expected: 422 error with field validation message

Test Invalid Difficulty:
  curl -X POST http://localhost:8000/api/tutoring/explanation \
    -H "Content-Type: application/json" \
    -d '{"topic": "Test", "difficulty": "impossible"}'

Expected: 422 error with valid enum values

Test Groq API Unavailable:
  1. Set GROQ_API_KEY to invalid value
  2. Make API call
  3. Expect fallback response with guidance

Expected: 
  {
    "success": false,
    "error": "AI service unavailable",
    "fallback": "Try these resources: ...",
    "status_code": 503
  }

Validation:
  ✅ Error messages are clear
  ✅ Status codes correct (400, 422, 500, 503)
  ✅ No stack traces exposed
  ✅ Helpful guidance provided

================================================================================
PERFORMANCE TESTING
================================================================================

Objective: Measure response times and throughput

Test 1: Single Request Performance
  Measure: Time to complete /api/tutoring/explanation
  Expected: < 5 seconds
  Actual: _____ seconds

Test 2: Multiple Concurrent Requests
  Command: Run 10 requests simultaneously
  Expected: All complete < 10 seconds
  Actual: _____ seconds

Test 3: Question Generation Performance
  Measure: Time to generate 5 practice questions
  Expected: < 5 seconds
  Actual: _____ seconds

Test 4: Study Plan Generation
  Measure: Time to generate complete study plan
  Expected: < 10 seconds
  Actual: _____ seconds

Performance Benchmarks:
  Explanation:    < 5 sec  (LLM generation)
  Questions:      < 5 sec  (LLM generation)
  Answer Eval:    < 3 sec  (LLM comparison)
  Socratic:       < 3 sec  (LLM response)
  Study Plan:     < 10 sec (Complex LLM task)
  Session:        < 1 sec  (Database lookup)

================================================================================
INTEGRATION TESTING
================================================================================

Objective: Test integration with eLearning platform

Test Scenario 1: Student Tutoring Session
  1. Create student in eLearning
  2. Enroll in course
  3. Start lesson
  4. Click "Ask Tutor"
  5. Verify session creates
  6. Verify response displays
  7. Verify session stored

Test Scenario 2: Progress Tracking
  1. Start tutoring session
  2. Generate practice questions
  3. Submit answers
  4. Check elearning_analytics updated
  5. Verify performance recorded

Test Scenario 3: Study Plan Generation
  1. Identify weak areas
  2. Generate study plan
  3. Student follows plan
  4. Progress tracked
  5. Plan updates with progress

================================================================================
LOGGING VERIFICATION
================================================================================

Check Logs For:
  ✅ Session creation log
  ✅ API request logs
  ✅ Response time logs
  ✅ Error logs (if any)
  ✅ Performance metrics

Log Location: logs/app.log

Sample Log Entries (expected):
  [2024-01-21 10:30:00] INFO: Started tutoring session: tut_student_001_lesson_789_1705848600
  [2024-01-21 10:30:02] INFO: Generated explanation for topic: Photosynthesis
  [2024-01-21 10:30:05] INFO: Evaluated answer - Score: 75/100
  [2024-01-21 10:30:10] DEBUG: Groq API response time: 2.3s

Filter Logs:
  grep "tutoring" logs/app.log                    (all tutoring logs)
  grep "ERROR" logs/app.log | grep "tutoring"    (tutoring errors)
  grep -i "groq" logs/app.log                    (LLM logs)

================================================================================
SECURITY TESTING
================================================================================

Test 1: API Key Not Exposed
  ✅ Check source code: GROQ_API_KEY not in ai_tutoring_engine.py
  ✅ Check responses: No API key in JSON responses
  ✅ Check logs: No API key logged

Test 2: Input Validation
  ✅ Long strings rejected
  ✅ Special characters handled
  ✅ Null values rejected
  ✅ Type mismatches caught

Test 3: Student Data Privacy
  ✅ Sessions isolated by student_id
  ✅ No cross-student data leakage
  ✅ Session data not logged externally
  ✅ GDPR-compliant (stateless)

================================================================================
FINAL CHECKLIST
================================================================================

All Tests Passed:
  □ Test 1: Server startup - PASS/FAIL
  □ Test 2: Session creation - PASS/FAIL
  □ Test 3: Explanation - PASS/FAIL
  □ Test 4: Practice questions - PASS/FAIL
  □ Test 5: Answer evaluation - PASS/FAIL
  □ Test 6: Socratic method - PASS/FAIL
  □ Test 7: Study plan - PASS/FAIL
  □ Test 8: Session retrieval - PASS/FAIL
  □ Test 9: Complete response - PASS/FAIL
  □ Test 10: Error handling - PASS/FAIL
  □ Performance tests - PASS/FAIL
  □ Integration tests - PASS/FAIL
  □ Logging verification - PASS/FAIL
  □ Security testing - PASS/FAIL

Issues Found:
  (List any issues encountered)

Recommendations:
  (List any improvements needed)

Date Tested: ___________
Tester: ________________
Status: ✅ READY FOR PRODUCTION / ⚠️ NEEDS FIXES

================================================================================
DEPLOYMENT CHECKLIST
================================================================================

Before Deploying to Production:
  □ All tests pass
  □ GROQ_API_KEY set in production environment
  □ Groq account has sufficient quota
  □ Server logs configured
  □ Error handling verified
  □ Performance acceptable
  □ Security tested
  □ Documentation complete
  □ Team trained on features
  □ Monitoring configured
  □ Backup plan in place

Deployment Steps:
  1. Set GROQ_API_KEY in production
  2. Deploy ai_tutoring_engine.py
  3. Deploy server.py updates
  4. Run full test suite
  5. Monitor logs for errors
  6. Announce feature to students
  7. Track usage and feedback
  8. Iterate based on feedback

================================================================================
SUCCESS CRITERIA
================================================================================

✅ CORE REQUIREMENTS:
  - AI Tutoring Engine fully operational
  - 7 API endpoints working
  - Groq LLM integration successful
  - Session management functioning
  - Error handling robust
  - Response times acceptable
  - No security vulnerabilities

✅ INTEGRATION REQUIREMENTS:
  - eLearning platform accepts tutoring requests
  - Sessions tracked and stored
  - Student analytics updated
  - UI displays tutoring responses
  - Progress tracked accurately

✅ QUALITY REQUIREMENTS:
  - 100% of tests pass
  - No critical errors
  - Performance > 90% success rate
  - Student satisfaction > 4/5
  - Response quality high

================================================================================
SUPPORT & TROUBLESHOOTING
================================================================================

Common Issues:

1. "GROQ_API_KEY not configured"
   → Set environment variable
   → Restart server
   → Test configuration

2. "Tutoring routes not registered"
   → Check server.py imports
   → Verify ai_tutoring_engine.py syntax
   → Check logs for import errors

3. "Slow response times"
   → Check Groq API status
   → Reduce max_tokens
   → Check network latency
   → Monitor server resources

4. "Poor response quality"
   → Review prompts
   → Adjust temperature setting
   → Provide more context
   → Check LLM model status

For Additional Help:
  - Check logs: tail -f logs/app.log
  - Monitor status: curl http://localhost:8000/health
  - Review documentation: ELEARNING_AI_TUTORING_COMPLETE.md
  - Check implementation: backend/ai_tutoring_engine.py

================================================================================
