import requests
import sys
import json
import time
from datetime import datetime

class GAAIUSAPITester:
    def __init__(self, base_url="https://app-scaffolder-1.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.session_id = None
        self.token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []
        self.passed_tests = []

    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            self.passed_tests.append(name)
            print(f"✅ {name} - PASSED")
        else:
            self.failed_tests.append({"test": name, "details": details})
            print(f"❌ {name} - FAILED: {details}")

    def run_test(self, name, method, endpoint, expected_status, data=None, files=None, timeout=30):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'} if not files else {}
        
        # Add auth token if available
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'

        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=timeout)
            elif method == 'POST':
                if files:
                    # Remove Content-Type for file uploads
                    headers.pop('Content-Type', None)
                    response = requests.post(url, files=files, headers=headers, timeout=timeout)
                else:
                    response = requests.post(url, json=data, headers=headers, timeout=timeout)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=timeout)

            success = response.status_code == expected_status
            
            if success:
                self.log_test(name, True)
                try:
                    return True, response.json() if response.content else {}
                except:
                    return True, {"status": "success", "content_type": response.headers.get('content-type', 'unknown')}
            else:
                error_detail = f"Expected {expected_status}, got {response.status_code}"
                try:
                    error_detail += f" - {response.json()}"
                except:
                    error_detail += f" - {response.text[:200]}"
                self.log_test(name, False, error_detail)
                return False, {}

        except requests.exceptions.Timeout:
            self.log_test(name, False, f"Request timeout after {timeout}s")
            return False, {}
        except Exception as e:
            self.log_test(name, False, f"Request error: {str(e)}")
            return False, {}

    def test_health_check(self):
        """Test health check endpoint"""
        success, response = self.run_test(
            "Health Check",
            "GET",
            "health",
            200
        )
        if success:
            print(f"   Health Status: {response}")
            # Check if all required services are available
            if response.get('groq') and response.get('huggingface'):
                print("   ✅ All AI services available")
            else:
                print(f"   ⚠️  Some services unavailable: {response}")
        return success

    def test_user_registration(self):
        """Test user registration"""
        test_email = f"test_{int(time.time())}@example.com"
        success, response = self.run_test(
            "User Registration",
            "POST",
            "auth/register",
            200,
            data={
                "email": test_email,
                "password": "testpass123",
                "name": "Test User"
            }
        )
        if success and 'token' in response:
            self.token = response['token']
            self.user_id = response['user']['id']
            print(f"   Registered user: {response['user']['email']}")
            print(f"   User ID: {self.user_id}")
        return success

    def test_user_login(self):
        """Test user login with existing credentials"""
        # Try to login with a test account
        success, response = self.run_test(
            "User Login",
            "POST",
            "auth/login",
            200,
            data={
                "email": "test@example.com",
                "password": "testpass123"
            }
        )
        if success and 'token' in response:
            # Don't overwrite token from registration if we have one
            if not self.token:
                self.token = response['token']
                self.user_id = response['user']['id']
            print(f"   Logged in user: {response['user']['email']}")
        return success

    def test_get_current_user(self):
        """Test getting current user with token"""
        if not self.token:
            print("❌ No token available for auth test")
            return False
            
        success, response = self.run_test(
            "Get Current User",
            "GET",
            "auth/me",
            200
        )
        if success:
            print(f"   Current user: {response.get('email', 'Unknown')}")
            print(f"   Pro status: {response.get('is_pro', False)}")
        return success

    def test_payment_config(self):
        """Test payment configuration endpoint"""
        success, response = self.run_test(
            "Payment Config",
            "GET",
            "payment/config",
            200
        )
        if success:
            print(f"   PayPal Client ID: {response.get('paypal_client_id', 'Not set')[:20]}...")
            print(f"   Pro Price USD: ${response.get('pro_price_usd', 'Unknown')}")
        return success

    def test_create_session(self):
        """Test session creation"""
        success, response = self.run_test(
            "Create Session",
            "POST",
            "sessions?name=Test Chat",
            200
        )
        if success and 'id' in response:
            self.session_id = response['id']
            print(f"   Created session: {self.session_id}")
        return success

    def test_get_sessions(self):
        """Test getting sessions list"""
        success, response = self.run_test(
            "Get Sessions",
            "GET",
            "sessions",
            200
        )
        if success:
            print(f"   Found {len(response)} sessions")
        return success

    def test_chat_functionality(self):
        """Test chat with Groq"""
        if not self.session_id:
            print("❌ No session available for chat test")
            return False

        success, response = self.run_test(
            "Chat with Groq",
            "POST",
            "chat",
            200,
            data={
                "session_id": self.session_id,
                "message": "Hello! Please respond with exactly 'GAAIUS AI is working' to confirm you're functioning."
            },
            timeout=60  # Groq might take longer
        )
        
        if success:
            print(f"   AI Response: {response.get('content', '')[:100]}...")
            print(f"   Model Used: {response.get('model_used', 'Unknown')}")
        return success

    def test_chat_history(self):
        """Test getting chat history"""
        if not self.session_id:
            print("❌ No session available for history test")
            return False

        success, response = self.run_test(
            "Get Chat History",
            "GET",
            f"chat/{self.session_id}/history",
            200
        )
        
        if success:
            print(f"   Found {len(response)} messages in history")
        return success

    def test_image_generation(self):
        """Test image generation with HuggingFace FLUX"""
        success, response = self.run_test(
            "Image Generation (HuggingFace FLUX)",
            "POST",
            "image/generate",
            200,
            data={
                "prompt": "A simple red circle on white background",
                "session_id": self.session_id
            },
            timeout=120  # Image generation takes time
        )
        
        if success:
            print(f"   Generated image: {response.get('image_url', '')[:50]}...")
            print(f"   Model Used: {response.get('model_used', 'Unknown')}")
        return success

    def test_tts(self):
        """Test text-to-speech with HuggingFace MMS-TTS"""
        success, response = self.run_test(
            "Text-to-Speech (HuggingFace MMS-TTS)",
            "POST",
            "tts",
            200,
            data={
                "text": "Hello, this is GAAIUS AI speaking.",
                "voice": "en"
            },
            timeout=60
        )
        
        if success:
            print(f"   TTS Response: Audio file generated")
        return success

    def test_file_generation(self):
        """Test file generation with Groq"""
        success, response = self.run_test(
            "File Generation (Groq)",
            "POST",
            "file/generate",
            200,
            data={
                "prompt": "Create a simple Python hello world function",
                "file_type": "code"
            },
            timeout=60
        )
        
        if success:
            print(f"   Generated file: {response.get('file_url', '')[:50]}...")
            print(f"   Model Used: {response.get('model_used', 'Unknown')}")
            if response.get('content'):
                print(f"   Content preview: {response['content'][:100]}...")
        return success

    def test_video_generation(self):
        """Test video generation - This will take several minutes"""
        print("⚠️  Video generation test will take 2-5 minutes...")
        success, response = self.run_test(
            "Video Generation",
            "POST",
            "video/generate",
            200,
            data={
                "prompt": "A simple animation of a bouncing ball",
                "duration": 5,
                "style": "cinematic",
                "session_id": self.session_id
            },
            timeout=300  # Video generation takes much longer
        )
        
        if success:
            print(f"   Generated video: {response.get('video_url', '')[:50]}...")
            print(f"   Model Used: {response.get('model_used', 'Unknown')}")
        return success

    def test_tts(self):
        """Test text-to-speech with HuggingFace MMS-TTS"""
        success, response = self.run_test(
            "Text-to-Speech (HuggingFace MMS-TTS)",
            "POST",
            "tts",
            200,
            data={
                "text": "Hello, this is GAAIUS AI speaking.",
                "voice": "en"
            },
            timeout=60
        )
        
        if success:
            print(f"   TTS Response: Audio file generated")
        return success

    def test_file_generation(self):
        """Test file generation with Groq"""
        success, response = self.run_test(
            "File Generation (Groq)",
            "POST",
            "file/generate",
            200,
            data={
                "prompt": "Create a simple Python hello world function",
                "file_type": "code"
            },
            timeout=60
        )
        
        if success:
            print(f"   Generated file: {response.get('file_url', '')[:50]}...")
            print(f"   Model Used: {response.get('model_used', 'Unknown')}")
            if response.get('content'):
                print(f"   Content preview: {response['content'][:100]}...")
        return success

    def test_generations_history(self):
        """Test getting generations history"""
        success, response = self.run_test(
            "Get Generations",
            "GET",
            "generations",
            200
        )
        
        if success:
            print(f"   Found {len(response)} generations")
        return success

    def test_delete_session(self):
        """Test session deletion"""
        if not self.session_id:
            print("❌ No session available for deletion test")
            return False

        success, response = self.run_test(
            "Delete Session",
            "DELETE",
            f"sessions/{self.session_id}",
            200
        )
        return success

    def test_projects_api(self):
        """Test projects creation and listing"""
        if not self.token:
            print("❌ No token available for projects test")
            return False

        # Test project creation
        success, response = self.run_test(
            "Create Project",
            "POST",
            "projects",
            200,
            data={
                "name": "Test Project",
                "description": "A test project for API testing",
                "type": "web"
            }
        )
        
        project_id = None
        if success and 'id' in response:
            project_id = response['id']
            print(f"   Created project: {project_id}")
        
        # Test projects listing
        success2, response2 = self.run_test(
            "List Projects",
            "GET",
            "projects",
            200
        )
        
        if success2:
            print(f"   Found {len(response2)} projects")
        
        return success and success2

    def test_audio_narration(self):
        """Test the new audio narration endpoint"""
        success, response = self.run_test(
            "Audio Narration Generation",
            "POST",
            "audio/generate",
            200,
            data={
                "prompt": "Hello, this is a test of the audio narration feature.",
                "duration": 10,
                "type": "music"
            },
            timeout=60
        )
        
        if success:
            print(f"   Generated audio: {response.get('audio_url', '')[:50]}...")
            print(f"   Language: {response.get('language', 'Unknown')}")
            if response.get('content'):
                print(f"   Narration text: {response['content'][:100]}...")
        return success

    def test_build_functionality(self):
        """Test the build/generate-full endpoint"""
        success, response = self.run_test(
            "Build Full Project Generation",
            "POST",
            "build/generate-full",
            200,
            data={
                "prompt": "Create a simple landing page with a header and footer",
                "current_files": {},
                "project_type": "web"
            },
            timeout=60
        )
        
        if success:
            files = response.get('files', {})
            print(f"   Generated {len(files)} files")
            for filename in files.keys():
                print(f"     - {filename}")
            print(f"   Message: {response.get('message', 'No message')}")
        return success

    def test_document_generation(self):
        """Test document generation endpoint as requested"""
        success, response = self.run_test(
            "Document Generation (Invoice)",
            "POST",
            "document/generate",
            200,
            data={
                "prompt": "Create a simple invoice for $100",
                "document_type": "invoice",
                "document_name": "test_invoice"
            },
            timeout=60
        )
        
        if success:
            print(f"   Generated document: {response.get('filename', 'Unknown')}")
            print(f"   File URL: {response.get('file_url', '')[:50]}...")
            print(f"   Message: {response.get('message', 'No message')}")
        return success

    def test_build_generate(self):
        """Test build generation endpoint as requested"""
        success, response = self.run_test(
            "Build Generation (Button Component)",
            "POST",
            "build/generate",
            200,
            data={
                "prompt": "create a button component",
                "current_code": ""
            },
            timeout=60
        )
        
        if success:
            print(f"   Generated code length: {len(response.get('code', ''))}")
            print(f"   Model Used: {response.get('model_used', 'Unknown')}")
            if response.get('code'):
                print(f"   Code preview: {response['code'][:100]}...")
        return success

    def test_chat_flow(self):
        """Test complete chat flow: create session then chat"""
        # First create a session
        session_success, session_response = self.run_test(
            "Create Session for Chat",
            "POST",
            "sessions?name=Test",
            200
        )
        
        if not session_success or 'id' not in session_response:
            return False
            
        session_id = session_response['id']
        print(f"   Created session: {session_id}")
        
        # Then test chat
        chat_success, chat_response = self.run_test(
            "Chat with Session",
            "POST",
            "chat",
            200,
            data={
                "session_id": session_id,
                "message": "Hello"
            },
            timeout=60
        )
        
        if chat_success:
            print(f"   AI Response: {chat_response.get('content', '')[:100]}...")
            print(f"   Model Used: {chat_response.get('model_used', 'Unknown')}")
        
        return session_success and chat_success

    def test_build_platform_status(self):
        """Test GAAIUS BUILD BRAIN v2.0 platform status endpoint"""
        success, response = self.run_test(
            "Build Platform Status",
            "GET",
            "build/platform-status",
            200
        )
        
        if success:
            version = response.get('version', 'Unknown')
            print(f"   Platform Version: {version}")
            if version == "2.0.0":
                print("   ✅ Correct version 2.0.0 returned")
            else:
                print(f"   ⚠️  Expected version 2.0.0, got {version}")
            print(f"   Status: {response.get('status', 'Unknown')}")
        return success

    def test_build_init(self):
        """Test GAAIUS BUILD platform initialization"""
        success, response = self.run_test(
            "Build Platform Init",
            "GET",
            "build/init",
            200
        )
        
        if success:
            print(f"   Platform Info: {response.get('platform', 'Unknown')}")
            print(f"   Features: {len(response.get('features', []))} available")
        return success

    def test_build_generate_crypto_dashboard(self):
        """Test build generation with crypto dashboard prompt - Review Request Test"""
        success, response = self.run_test(
            "Build Generate (Crypto Dashboard)",
            "POST",
            "build/generate",
            200,
            data={
                "prompt": "Build a crypto dashboard",
                "current_code": "",
                "use_blueprint": True
            },
            timeout=90
        )
        
        if success:
            code = response.get('code', '')
            quality_score = response.get('quality_score', 0)
            quality_passed = response.get('quality_passed', False)
            code_length = len(code)
            
            print(f"   Generated code length: {code_length} chars")
            print(f"   Quality score: {quality_score}")
            print(f"   Quality passed: {quality_passed}")
            print(f"   Model used: {response.get('model_used', 'Unknown')}")
            
            # Check requirements from review request
            requirements_met = True
            
            if quality_score > 70:
                print("   ✅ Quality score > 70")
            else:
                print(f"   ❌ Quality score {quality_score} <= 70")
                requirements_met = False
                
            if code_length > 5000:
                print("   ✅ Code length > 5000 chars")
            else:
                print(f"   ❌ Code length {code_length} <= 5000 chars")
                requirements_met = False
                
            if quality_passed:
                print("   ✅ Quality passed: true")
            else:
                print(f"   ❌ Quality passed: {quality_passed}")
                requirements_met = False
                
            if code:
                print(f"   Code preview: {code[:150]}...")
                
            # Check if it's enterprise-grade HTML
            if 'html' in code.lower() and ('class=' in code or 'style=' in code):
                print("   ✅ Contains HTML with styling")
            else:
                print("   ⚠️  May not contain enterprise-grade HTML")
                
            if not requirements_met:
                self.log_test("Crypto Dashboard Requirements Check", False, "Quality score <= 70 OR code length <= 5000 OR quality_passed != true")
            else:
                self.log_test("Crypto Dashboard Requirements Check", True)
                
        return success

    def test_build_generate_netflix_clone(self):
        """Test build generation with Netflix clone prompt - Review Request Test"""
        success, response = self.run_test(
            "Build Generate (Netflix Clone)",
            "POST",
            "build/generate",
            200,
            data={
                "prompt": "Build a Netflix clone",
                "current_code": "",
                "use_blueprint": True
            },
            timeout=90
        )
        
        if success:
            code = response.get('code', '')
            quality_score = response.get('quality_score', 0)
            quality_passed = response.get('quality_passed', False)
            code_length = len(code)
            
            print(f"   Generated code length: {code_length} chars")
            print(f"   Quality score: {quality_score}")
            print(f"   Quality passed: {quality_passed}")
            print(f"   Model used: {response.get('model_used', 'Unknown')}")
            
            # Check for high quality code indicators
            if quality_score > 70:
                print("   ✅ High quality score > 70")
            else:
                print(f"   ⚠️  Quality score {quality_score} <= 70")
                
            if code_length > 5000:
                print("   ✅ Substantial code length > 5000 chars")
            else:
                print(f"   ⚠️  Code length {code_length} <= 5000 chars")
                
            # Check for Netflix-like features in code
            netflix_features = ['video', 'movie', 'stream', 'player', 'carousel', 'grid', 'card']
            found_features = [feature for feature in netflix_features if feature in code.lower()]
            
            if found_features:
                print(f"   ✅ Netflix-like features found: {', '.join(found_features)}")
            else:
                print("   ⚠️  No obvious Netflix-like features detected")
                
            if code:
                print(f"   Code preview: {code[:150]}...")
                
        return success

    def test_build_templates(self):
        """Test GET /api/build/templates - Review Request Test"""
        success, response = self.run_test(
            "Build Templates",
            "GET",
            "build/templates",
            200
        )
        
        if success:
            templates = response.get('templates', [])
            print(f"   Available templates: {len(templates)}")
            
            if templates:
                print("   ✅ Templates returned successfully")
                # Show first few template names
                for i, template in enumerate(templates[:3]):
                    if isinstance(template, dict):
                        name = template.get('name', f'Template {i+1}')
                        print(f"     - {name}")
                    else:
                        print(f"     - {template}")
                if len(templates) > 3:
                    print(f"     ... and {len(templates) - 3} more")
            else:
                print("   ❌ No templates returned")
                
        return success
        """Test component library button generation"""
        success, response = self.run_test(
            "Build Component (Button)",
            "GET",
            "build/component/button?label=Test&variant=primary",
            200
        )
        
        if success:
            html = response.get('html', '')
            print(f"   Generated HTML length: {len(html)} chars")
            if 'button' in html.lower() and 'Test' in html:
                print("   ✅ Button HTML contains expected elements")
            else:
                print("   ⚠️  Button HTML may not contain expected elements")
            print(f"   HTML preview: {html[:100]}...")
        return success

    def test_build_layout_grid(self):
        """Test layout engine grid generation"""
        success, response = self.run_test(
            "Build Layout (Grid)",
            "POST",
            "build/layout",
            200,
            data={
                "type": "grid",
                "columns": 3,
                "items": ["Card 1", "Card 2", "Card 3"]
            }
        )
        
        if success:
            html = response.get('html', '')
            layout_type = response.get('type', '')
            print(f"   Generated layout type: {layout_type}")
            print(f"   HTML length: {len(html)} chars")
            if 'grid' in html.lower() and 'Card 1' in html:
                print("   ✅ Grid layout contains expected elements")
            else:
                print("   ⚠️  Grid layout may not contain expected elements")
            print(f"   HTML preview: {html[:100]}...")
        return success

    def test_build_ide_config(self):
        """Test IDE configuration endpoint"""
        success, response = self.run_test(
            "Build IDE Config",
            "GET",
            "build/ide-config",
            200
        )
        
        if success:
            print(f"   IDE Config keys: {list(response.keys())}")
            if 'monaco' in response or 'editor' in response or 'theme' in response:
                print("   ✅ Monaco Editor configuration returned")
            else:
                print("   ⚠️  Monaco Editor configuration may be missing")
        return success

    def test_build_validate_schema(self):
        """Test schema validation endpoint"""
        success, response = self.run_test(
            "Build Validate Schema",
            "POST",
            "build/validate-schema",
            200,
            data={
                "type": "blueprint",
                "content": {
                    "app_name": "Test",
                    "app_type": "dashboard",
                    "platform": ["web"],
                    "pages": [{"name": "Home", "components": ["Hero"]}],
                    "features": ["auth"]
                }
            }
        )
        
        if success:
            is_valid = response.get('valid', False)
            errors = response.get('errors', [])
            print(f"   Schema valid: {is_valid}")
            print(f"   Validation errors: {len(errors)}")
            if is_valid:
                print("   ✅ Blueprint schema validation passed")
            else:
                print(f"   ❌ Blueprint schema validation failed: {errors}")
        return success

    def run_requested_tests(self):
        """Run the specific GAAIUS BUILD BRAIN v2.0 tests requested in the review"""
        print("🚀 Starting GAAIUS AI Builder API Tests - Review Request")
        print(f"🌐 Testing against: {self.base_url}")
        print("=" * 60)

        # Test the 4 specific endpoints requested in the review
        print("\n🔍 Testing GAAIUS AI Builder API Endpoints...")
        
        # 1. GET /api/build/platform-status - Should return platform status v2.0.0
        print("\n1️⃣  Testing Platform Status...")
        self.test_build_platform_status()
        
        # 2. POST /api/build/generate - Test with prompt "Build a crypto dashboard"
        print("\n2️⃣  Testing Build Generation (Crypto Dashboard)...")
        self.test_build_generate_crypto_dashboard()
        
        # 3. POST /api/build/generate - Test with prompt "Build a Netflix clone"
        print("\n3️⃣  Testing Build Generation (Netflix Clone)...")
        self.test_build_generate_netflix_clone()
        
        # 4. GET /api/build/templates - Should return available templates
        print("\n4️⃣  Testing Build Templates...")
        self.test_build_templates()

        # Print summary
        print("\n" + "=" * 60)
        print("📊 GAAIUS AI BUILDER API TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {self.tests_run}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {len(self.failed_tests)}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if self.failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in self.failed_tests:
                print(f"   • {test['test']}: {test['details']}")
        
        if self.passed_tests:
            print("\n✅ PASSED TESTS:")
            for test in self.passed_tests:
                print(f"   • {test}")

        return self.tests_passed == self.tests_run

    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting GAAIUS AI Backend API Tests")
        print(f"🌐 Testing against: {self.base_url}")
        print("=" * 60)

        # Core functionality tests
        self.test_health_check()
        
        # Authentication tests
        print("\n🔐 Testing Authentication...")
        self.test_user_registration()
        self.test_user_login()
        self.test_get_current_user()
        
        # Payment configuration
        self.test_payment_config()
        
        # Session management
        print("\n💬 Testing Session Management...")
        self.test_create_session()
        self.test_get_sessions()
        
        # Chat functionality
        print("\n🤖 Testing Chat Functionality...")
        self.test_chat_functionality()
        time.sleep(2)  # Brief pause between tests
        self.test_chat_history()
        
        # Generation tests (these take longer)
        print("\n🎨 Testing AI Generation Features...")
        self.test_image_generation()
        self.test_tts()
        self.test_file_generation()
        
        # Test new features specifically mentioned in review request
        print("\n🔧 Testing New Features...")
        self.test_projects_api()
        self.test_audio_narration()
        self.test_build_functionality()
        
        # Skip video test for now as it takes too long for initial testing
        print("⏭️  Skipping video generation test (takes 2-5 minutes)")
        
        # History and cleanup
        self.test_generations_history()
        self.test_delete_session()

        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {self.tests_run}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {len(self.failed_tests)}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if self.failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in self.failed_tests:
                print(f"   • {test['test']}: {test['details']}")
        
        if self.passed_tests:
            print("\n✅ PASSED TESTS:")
            for test in self.passed_tests:
                print(f"   • {test}")

        return self.tests_passed == self.tests_run

def main():
    tester = GAAIUSAPITester()
    # Run the specific tests requested in the review
    success = tester.run_requested_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())