"""
GAAIUS PROJECT RUNTIME v1.0 - Backend API Tests
Tests for the new full-stack enterprise project scaffold generator endpoints:
- /api/build/runtime-status - Get runtime capabilities
- /api/build/generate-runtime - Generate full project scaffold
- /api/build/runtime-modify - Modify existing project
"""

import pytest
import requests
import os
import json

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestRuntimeStatus:
    """Tests for /api/build/runtime-status endpoint - No auth required"""
    
    def test_runtime_status_returns_200(self):
        """Test that runtime-status endpoint returns 200"""
        response = requests.get(f"{BASE_URL}/api/build/runtime-status")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print(f"✓ Runtime status endpoint returns 200")
    
    def test_runtime_status_has_name_and_version(self):
        """Test that runtime-status returns name and version"""
        response = requests.get(f"{BASE_URL}/api/build/runtime-status")
        data = response.json()
        
        assert "name" in data, "Missing 'name' field"
        assert data["name"] == "GAAIUS PROJECT RUNTIME", f"Expected 'GAAIUS PROJECT RUNTIME', got {data['name']}"
        
        assert "version" in data, "Missing 'version' field"
        assert data["version"] == "1.0.0", f"Expected '1.0.0', got {data['version']}"
        
        print(f"✓ Runtime name: {data['name']}, version: {data['version']}")
    
    def test_runtime_status_has_capabilities(self):
        """Test that runtime-status returns capabilities"""
        response = requests.get(f"{BASE_URL}/api/build/runtime-status")
        data = response.json()
        
        assert "capabilities" in data, "Missing 'capabilities' field"
        caps = data["capabilities"]
        
        # Check frontend capabilities
        assert "frontend" in caps, "Missing frontend capabilities"
        assert "React" in caps["frontend"], "React not in frontend capabilities"
        assert "TypeScript" in caps["frontend"], "TypeScript not in frontend capabilities"
        assert "Vite" in caps["frontend"], "Vite not in frontend capabilities"
        
        # Check backend capabilities
        assert "backend" in caps, "Missing backend capabilities"
        assert "Express" in caps["backend"], "Express not in backend capabilities"
        assert "MongoDB" in caps["backend"], "MongoDB not in backend capabilities"
        
        print(f"✓ Frontend capabilities: {caps['frontend']}")
        print(f"✓ Backend capabilities: {caps['backend']}")
    
    def test_runtime_status_has_supported_app_types(self):
        """Test that runtime-status returns supported app types"""
        response = requests.get(f"{BASE_URL}/api/build/runtime-status")
        data = response.json()
        
        assert "supported_app_types" in data, "Missing 'supported_app_types' field"
        app_types = data["supported_app_types"]
        
        expected_types = ["saas_dashboard", "ecommerce", "admin_panel", "ai_tool", "crypto_finance"]
        for app_type in expected_types:
            assert app_type in app_types, f"Missing app type: {app_type}"
        
        print(f"✓ Supported app types: {len(app_types)} types including {expected_types[:3]}")
    
    def test_runtime_status_has_export_options(self):
        """Test that runtime-status returns export options"""
        response = requests.get(f"{BASE_URL}/api/build/runtime-status")
        data = response.json()
        
        assert "export_options" in data, "Missing 'export_options' field"
        exports = data["export_options"]
        
        assert "web" in exports, "Missing 'web' export option"
        assert any("electron" in e.lower() for e in exports), "Missing electron export option"
        assert any("capacitor" in e.lower() for e in exports), "Missing capacitor export option"
        
        print(f"✓ Export options: {exports}")


class TestGenerateRuntime:
    """Tests for /api/build/generate-runtime endpoint - Requires auth"""
    
    @pytest.fixture
    def auth_headers(self):
        """Get auth headers by registering/logging in a test user"""
        # Try to register a test user
        register_data = {
            "email": "runtime_test@example.com",
            "password": "TestPass123!",
            "name": "Runtime Tester"
        }
        
        # Try register first
        response = requests.post(f"{BASE_URL}/api/auth/register", json=register_data)
        
        if response.status_code == 200:
            token = response.json().get("token")
        else:
            # User exists, try login
            login_data = {
                "email": "runtime_test@example.com",
                "password": "TestPass123!"
            }
            response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
            if response.status_code != 200:
                pytest.skip("Could not authenticate for runtime tests")
            token = response.json().get("token")
        
        return {"Authorization": f"Bearer {token}"}
    
    def test_generate_runtime_requires_auth(self):
        """Test that generate-runtime requires authentication"""
        response = requests.post(f"{BASE_URL}/api/build/generate-runtime", json={"prompt": "test"})
        # Should return 401 or 403 without auth
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"
        print(f"✓ Generate runtime requires authentication (returns {response.status_code})")
    
    def test_generate_runtime_youtube_clone(self, auth_headers):
        """Test generating a YouTube clone project - should return 50+ files"""
        response = requests.post(
            f"{BASE_URL}/api/build/generate-runtime",
            json={"prompt": "Build a YouTube clone"},
            headers=auth_headers,
            timeout=180  # 3 minute timeout for full project generation
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text[:500]}"
        data = response.json()
        
        # Check success
        assert data.get("success") == True, "Expected success=True"
        
        # Check project_files exists and has 50+ files
        assert "project_files" in data, "Missing 'project_files' field"
        project_files = data["project_files"]
        file_count = len(project_files)
        
        assert file_count >= 50, f"Expected 50+ files, got {file_count}"
        print(f"✓ Generated {file_count} files for YouTube clone")
        
        # Check for enterprise folder structure
        frontend_files = [f for f in project_files.keys() if f.startswith("frontend/")]
        backend_files = [f for f in project_files.keys() if f.startswith("backend/")]
        shared_files = [f for f in project_files.keys() if f.startswith("shared/")]
        config_files = [f for f in project_files.keys() if f.startswith("config/")]
        
        assert len(frontend_files) > 0, "No frontend files generated"
        assert len(backend_files) > 0, "No backend files generated"
        
        print(f"✓ Frontend files: {len(frontend_files)}")
        print(f"✓ Backend files: {len(backend_files)}")
        print(f"✓ Shared files: {len(shared_files)}")
        print(f"✓ Config files: {len(config_files)}")
    
    def test_generate_runtime_has_package_json(self, auth_headers):
        """Test that generated project has package.json files"""
        response = requests.post(
            f"{BASE_URL}/api/build/generate-runtime",
            json={"prompt": "Build a simple dashboard"},
            headers=auth_headers,
            timeout=180
        )
        
        assert response.status_code == 200
        data = response.json()
        project_files = data.get("project_files", {})
        
        # Check for frontend package.json
        assert "frontend/package.json" in project_files, "Missing frontend/package.json"
        frontend_pkg = json.loads(project_files["frontend/package.json"])
        assert "dependencies" in frontend_pkg, "Missing dependencies in frontend package.json"
        assert "react" in frontend_pkg["dependencies"], "Missing react dependency"
        
        # Check for backend package.json
        assert "backend/package.json" in project_files, "Missing backend/package.json"
        backend_pkg = json.loads(project_files["backend/package.json"])
        assert "dependencies" in backend_pkg, "Missing dependencies in backend package.json"
        assert "express" in backend_pkg["dependencies"], "Missing express dependency"
        
        print(f"✓ Frontend package.json has react: {frontend_pkg['dependencies'].get('react')}")
        print(f"✓ Backend package.json has express: {backend_pkg['dependencies'].get('express')}")
    
    def test_generate_runtime_has_vite_config(self, auth_headers):
        """Test that generated project has vite.config.ts"""
        response = requests.post(
            f"{BASE_URL}/api/build/generate-runtime",
            json={"prompt": "Build a blog platform"},
            headers=auth_headers,
            timeout=180
        )
        
        assert response.status_code == 200
        data = response.json()
        project_files = data.get("project_files", {})
        
        assert "frontend/vite.config.ts" in project_files, "Missing frontend/vite.config.ts"
        vite_config = project_files["frontend/vite.config.ts"]
        
        assert "defineConfig" in vite_config, "vite.config.ts missing defineConfig"
        assert "react" in vite_config, "vite.config.ts missing react plugin"
        
        print(f"✓ vite.config.ts present with defineConfig and react plugin")
    
    def test_generate_runtime_has_tsconfig(self, auth_headers):
        """Test that generated project has tsconfig.json files"""
        response = requests.post(
            f"{BASE_URL}/api/build/generate-runtime",
            json={"prompt": "Build an e-commerce store"},
            headers=auth_headers,
            timeout=180
        )
        
        assert response.status_code == 200
        data = response.json()
        project_files = data.get("project_files", {})
        
        assert "frontend/tsconfig.json" in project_files, "Missing frontend/tsconfig.json"
        assert "backend/tsconfig.json" in project_files, "Missing backend/tsconfig.json"
        
        frontend_tsconfig = json.loads(project_files["frontend/tsconfig.json"])
        assert "compilerOptions" in frontend_tsconfig, "Missing compilerOptions in frontend tsconfig"
        
        print(f"✓ tsconfig.json files present for frontend and backend")
    
    def test_generate_runtime_has_react_components(self, auth_headers):
        """Test that generated project has React components"""
        response = requests.post(
            f"{BASE_URL}/api/build/generate-runtime",
            json={"prompt": "Build a social media app"},
            headers=auth_headers,
            timeout=180
        )
        
        assert response.status_code == 200
        data = response.json()
        project_files = data.get("project_files", {})
        
        # Check for key React files
        expected_files = [
            "frontend/src/App.tsx",
            "frontend/src/main.tsx",
            "frontend/src/components/Layout.tsx",
            "frontend/src/components/Sidebar.tsx",
            "frontend/src/components/Header.tsx"
        ]
        
        for expected_file in expected_files:
            assert expected_file in project_files, f"Missing {expected_file}"
        
        # Check App.tsx has React content
        app_tsx = project_files.get("frontend/src/App.tsx", "")
        assert "import" in app_tsx, "App.tsx missing imports"
        assert "export" in app_tsx, "App.tsx missing export"
        
        print(f"✓ React components present: Layout, Sidebar, Header, App.tsx, main.tsx")
    
    def test_generate_runtime_has_backend_files(self, auth_headers):
        """Test that generated project has backend server files"""
        response = requests.post(
            f"{BASE_URL}/api/build/generate-runtime",
            json={"prompt": "Build a task management app"},
            headers=auth_headers,
            timeout=180
        )
        
        assert response.status_code == 200
        data = response.json()
        project_files = data.get("project_files", {})
        
        # Check for key backend files
        expected_files = [
            "backend/src/server.ts",
            "backend/src/routes/index.ts",
            "backend/src/routes/auth.ts",
            "backend/src/middleware/auth.ts"
        ]
        
        for expected_file in expected_files:
            assert expected_file in project_files, f"Missing {expected_file}"
        
        # Check server.ts has Express content
        server_ts = project_files.get("backend/src/server.ts", "")
        assert "express" in server_ts.lower(), "server.ts missing express"
        
        print(f"✓ Backend files present: server.ts, routes, middleware")
    
    def test_generate_runtime_returns_stats(self, auth_headers):
        """Test that generate-runtime returns project stats"""
        response = requests.post(
            f"{BASE_URL}/api/build/generate-runtime",
            json={"prompt": "Build a portfolio website"},
            headers=auth_headers,
            timeout=180
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "stats" in data, "Missing 'stats' field"
        stats = data["stats"]
        
        assert "total_files" in stats, "Missing total_files in stats"
        assert "total_lines" in stats, "Missing total_lines in stats"
        assert "frontend_files" in stats, "Missing frontend_files in stats"
        assert "backend_files" in stats, "Missing backend_files in stats"
        
        print(f"✓ Stats: {stats['total_files']} files, {stats['total_lines']} lines")
        print(f"✓ Frontend: {stats['frontend_files']} files, Backend: {stats['backend_files']} files")
    
    def test_generate_runtime_returns_blueprint(self, auth_headers):
        """Test that generate-runtime returns blueprint info"""
        response = requests.post(
            f"{BASE_URL}/api/build/generate-runtime",
            json={"prompt": "Build a Netflix clone"},
            headers=auth_headers,
            timeout=180
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "blueprint" in data, "Missing 'blueprint' field"
        blueprint = data["blueprint"]
        
        assert "app_name" in blueprint, "Missing app_name in blueprint"
        assert "app_type" in blueprint, "Missing app_type in blueprint"
        assert "features" in blueprint, "Missing features in blueprint"
        
        print(f"✓ Blueprint: {blueprint['app_name']} ({blueprint['app_type']})")
        print(f"✓ Features: {blueprint.get('features', [])[:5]}")


class TestRuntimeModify:
    """Tests for /api/build/runtime-modify endpoint"""
    
    @pytest.fixture
    def auth_headers(self):
        """Get auth headers"""
        login_data = {
            "email": "runtime_test@example.com",
            "password": "TestPass123!"
        }
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        if response.status_code != 200:
            # Try register
            register_data = {
                "email": "runtime_test@example.com",
                "password": "TestPass123!",
                "name": "Runtime Tester"
            }
            response = requests.post(f"{BASE_URL}/api/auth/register", json=register_data)
            if response.status_code != 200:
                pytest.skip("Could not authenticate")
        
        token = response.json().get("token")
        return {"Authorization": f"Bearer {token}"}
    
    def test_runtime_modify_requires_auth(self):
        """Test that runtime-modify requires authentication"""
        response = requests.post(f"{BASE_URL}/api/build/runtime-modify", json={
            "prompt": "Add a new page",
            "existing_files": {"test.tsx": "// test"}
        })
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print(f"✓ Runtime modify requires authentication")
    
    def test_runtime_modify_requires_existing_files(self, auth_headers):
        """Test that runtime-modify requires existing_files"""
        response = requests.post(
            f"{BASE_URL}/api/build/runtime-modify",
            json={"prompt": "Add a new page"},
            headers=auth_headers
        )
        assert response.status_code == 400, f"Expected 400 without existing_files, got {response.status_code}"
        print(f"✓ Runtime modify requires existing_files parameter")


class TestHealthEndpoint:
    """Basic health check"""
    
    def test_health_endpoint(self):
        """Test health endpoint"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        print(f"✓ Health endpoint returns healthy status")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
