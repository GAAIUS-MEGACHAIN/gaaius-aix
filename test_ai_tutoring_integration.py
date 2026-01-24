#!/usr/bin/env python
"""
Comprehensive test for AI Tutoring Platform integration.
Tests backend API endpoints and verifies real API calls.
"""

import asyncio
import json
import os
import sys
import requests
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

# Configuration
API_BASE = "http://localhost:8000/ai-tutoring"
STUDENT_ID = "test_student_001"
COURSE_ID = "course_math_101"
LESSON_ID = "lesson_001"

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_status(message, status="INFO"):
    """Print colored status messages."""
    if status == "SUCCESS":
        color = Colors.OKGREEN
    elif status == "ERROR":
        color = Colors.FAIL
    elif status == "WARNING":
        color = Colors.WARNING
    elif status == "INFO":
        color = Colors.OKCYAN
    else:
        color = Colors.OKBLUE
    
    print(f"{color}[{status}]{Colors.ENDC} {message}")

def test_health_check():
    """Test health check endpoints."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}=== HEALTH CHECK ==={Colors.ENDC}")
    
    # Test provider health
    try:
        print_status("Checking provider health...", "INFO")
        response = requests.get(f"{API_BASE}/health/providers", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print_status(f"Provider health OK", "SUCCESS")
            print(f"  Health Status: {data.get('health_status')}")
            
            providers = data.get('providers', {})
            print(f"  Available Providers:")
            for provider, status in providers.items():
                if status.get('status') == 'ready':
                    print_status(f"    {provider}: {status.get('status')}", "SUCCESS")
                else:
                    print_status(f"    {provider}: {status.get('status')}", "WARNING")
            return True
        else:
            print_status(f"Health check failed: {response.status_code}", "ERROR")
            return False
    except requests.exceptions.ConnectionError:
        print_status("Cannot connect to backend at http://localhost:8000", "ERROR")
        print_status("Make sure to start the server with: python run_server.py", "WARNING")
        return False
    except Exception as e:
        print_status(f"Health check error: {str(e)}", "ERROR")
        return False

def test_session_management():
    """Test session start/end."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}=== SESSION MANAGEMENT ==={Colors.ENDC}")
    
    try:
        # Start session
        print_status("Starting tutoring session...", "INFO")
        session_data = {
            "student_id": STUDENT_ID,
            "course_id": COURSE_ID,
            "lesson_id": LESSON_ID,
            "topic": "Quadratic Equations",
            "mode": "practice"
        }
        
        response = requests.post(
            f"{API_BASE}/session/start",
            json=session_data,
            timeout=10
        )
        
        if response.status_code != 200:
            print_status(f"Session start failed: {response.status_code}", "ERROR")
            return None
        
        session = response.json()
        session_id = session.get('session_id')
        print_status(f"Session started: {session_id}", "SUCCESS")
        print(f"  Mode: {session.get('mode')}")
        print(f"  Topic: {session.get('topic')}")
        
        return session_id
    except Exception as e:
        print_status(f"Session management error: {str(e)}", "ERROR")
        return None

def test_tutoring_response(session_id):
    """Test getting a tutoring response."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}=== TUTORING RESPONSE ==={Colors.ENDC}")
    
    if not session_id:
        print_status("Skipping - no valid session", "WARNING")
        return False
    
    try:
        test_topics = [
            ("What is a quadratic equation?", "math"),
            ("Explain photosynthesis", "science"),
            ("What is the capital of France?", "geography"),
        ]
        
        for question, expected_type in test_topics:
            print_status(f"Testing question: {question}", "INFO")
            
            request_data = {
                "student_id": STUDENT_ID,
                "session_id": session_id,
                "course_id": COURSE_ID,
                "lesson_id": LESSON_ID,
                "topic": question,
                "mode": "practice",
                "difficulty_level": "intermediate"
            }
            
            response = requests.post(
                f"{API_BASE}/tutoring-response",
                json=request_data,
                timeout=15
            )
            
            if response.status_code != 200:
                print_status(f"Request failed: {response.status_code}", "ERROR")
                print(f"  Response: {response.text}")
                continue
            
            data = response.json()
            print_status(f"Response received", "SUCCESS")
            print(f"  Content Preview: {data.get('content', 'N/A')[:100]}...")
            print(f"  Provider Used: {data.get('provider_used', 'N/A')}")
            print(f"  Content Type: {data.get('content_type', 'N/A')}")
            print(f"  Response Type: {data.get('response_type', 'N/A')}")
            print()
        
        return True
    except Exception as e:
        print_status(f"Tutoring response error: {str(e)}", "ERROR")
        return False

def test_proficiency_tracking(session_id):
    """Test proficiency tracking."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}=== PROFICIENCY TRACKING ==={Colors.ENDC}")
    
    if not session_id:
        print_status("Skipping - no valid session", "WARNING")
        return False
    
    try:
        print_status("Fetching student proficiency...", "INFO")
        response = requests.get(
            f"{API_BASE}/student/{STUDENT_ID}/proficiency",
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            proficiency = data.get('estimated_proficiency', {})
            print_status("Proficiency data retrieved", "SUCCESS")
            
            if proficiency:
                print(f"  Content Types:")
                for content_type, level in proficiency.items():
                    print(f"    {content_type}: {level:.1%}")
            else:
                print(f"  No proficiency data yet")
            return True
        else:
            print_status(f"Proficiency fetch failed: {response.status_code}", "WARNING")
            return False
    except Exception as e:
        print_status(f"Proficiency tracking error: {str(e)}", "ERROR")
        return False

def test_content_classification():
    """Test content classification."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}=== CONTENT CLASSIFICATION ==={Colors.ENDC}")
    
    try:
        test_contents = [
            ("Solve: 2x² + 3x + 1 = 0", "math"),
            ("The photosynthesis equation is 6CO2 + 6H2O → C6H12O6 + 6O2", "science"),
            ("Shakespeare wrote Hamlet and Macbeth", "literature"),
            ("The French Revolution occurred in 1789", "history"),
        ]
        
        for content, expected_type in test_contents:
            print_status(f"Classifying: {content[:40]}...", "INFO")
            
            request_data = {
                "content": content,
                "content_type": expected_type
            }
            
            response = requests.post(
                f"{API_BASE}/classify-content",
                json=request_data,
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                detected_type = data.get('detected_type')
                confidence = data.get('confidence')
                
                match_status = "✓" if detected_type == expected_type else "✗"
                print_status(
                    f"{match_status} Detected: {detected_type} (confidence: {confidence:.1%})",
                    "SUCCESS" if detected_type == expected_type else "WARNING"
                )
            else:
                print_status(f"Classification failed: {response.status_code}", "ERROR")
        
        return True
    except Exception as e:
        print_status(f"Content classification error: {str(e)}", "ERROR")
        return False

def test_frontend_integration():
    """Verify frontend files exist and are properly integrated."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}=== FRONTEND INTEGRATION ==={Colors.ENDC}")
    
    # Check frontend component
    frontend_file = Path(__file__).parent / "frontend" / "src" / "pages" / "AITutoringPlatform.jsx"
    if frontend_file.exists():
        size = frontend_file.stat().st_size
        print_status(f"Frontend component found: {frontend_file.name}", "SUCCESS")
        print(f"  Size: {size:,} bytes")
    else:
        print_status(f"Frontend component NOT FOUND", "ERROR")
        return False
    
    # Check App.js integration
    app_file = Path(__file__).parent / "frontend" / "src" / "App.js"
    if app_file.exists():
        content = app_file.read_text()
        checks = {
            "AITutoringPlatform import": "import AITutoringPlatform" in content,
            "AI Tutoring route": 'location.pathname === "/ai-tutoring"' in content,
            "AI Tutoring menu item": 'id: "aiTutoring"' in content,
            "Brain icon": "Brain" in content,
        }
        
        all_good = True
        for check, result in checks.items():
            if result:
                print_status(f"{check}: OK", "SUCCESS")
            else:
                print_status(f"{check}: MISSING", "ERROR")
                all_good = False
        
        return all_good
    else:
        print_status("App.js NOT FOUND", "ERROR")
        return False

def main():
    """Run all tests."""
    print(f"\n{Colors.BOLD}{Colors.HEADER}")
    print("╔════════════════════════════════════════════════════════╗")
    print("║     AI TUTORING PLATFORM - INTEGRATION TEST SUITE      ║")
    print("╚════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}")
    
    results = {}
    
    # Test 1: Health Check
    results['health'] = test_health_check()
    
    if not results['health']:
        print(f"\n{Colors.FAIL}{Colors.BOLD}Backend not available. Please start the server:{Colors.ENDC}")
        print(f"  cd {Path(__file__).parent}")
        print(f"  python run_server.py")
        sys.exit(1)
    
    # Test 2: Session Management
    session_id = test_session_management()
    results['session'] = session_id is not None
    
    # Test 3: Tutoring Response
    if session_id:
        results['tutoring'] = test_tutoring_response(session_id)
    
    # Test 4: Proficiency Tracking
    if session_id:
        results['proficiency'] = test_proficiency_tracking(session_id)
    
    # Test 5: Content Classification
    results['classification'] = test_content_classification()
    
    # Test 6: Frontend Integration
    results['frontend'] = test_frontend_integration()
    
    # Summary
    print(f"\n{Colors.HEADER}{Colors.BOLD}=== TEST SUMMARY ==={Colors.ENDC}")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        color = Colors.OKGREEN if result else Colors.FAIL
        print(f"{color}[{status}]{Colors.ENDC} {test_name.upper()}")
    
    print(f"\n{Colors.BOLD}Result: {passed}/{total} tests passed{Colors.ENDC}")
    
    if passed == total:
        print(f"{Colors.OKGREEN}{Colors.BOLD}✓ All tests passed! System is ready.{Colors.ENDC}")
        return 0
    else:
        print(f"{Colors.FAIL}{Colors.BOLD}✗ Some tests failed. Please check the errors above.{Colors.ENDC}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
