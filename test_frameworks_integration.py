"""
Integration Test for Fixed & New Frameworks
Production-Ready Testing Suite
"""

import sys
import asyncio
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from backend.frameworks_enhanced import (
    Framework, BuildConfig, BuildOrchestrator,
    FlutterBuilder, wxPythonBuilder, FastAPIMLBuilder,
    ReplitBase40Builder, EmergentShBuilder
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IntegrationTest:
    """Integration test suite"""
    
    @staticmethod
    def test_framework_enum():
        """Test framework enum"""
        frameworks = [f.value for f in Framework]
        assert len(frameworks) == 32, f"Expected 32 frameworks, got {len(frameworks)}"
        
        # Check fixed frameworks
        assert "flutter" in frameworks, "Flutter not found"
        assert "wxwidgets" in frameworks, "wxWidgets not found"
        
        # Check new frameworks
        assert "replit-base40" in frameworks, "Replit Base40 not found"
        assert "emergent-sh" in frameworks, "Emergent.sh not found"
        
        print("✅ Framework enum test passed")
        return True
    
    @staticmethod
    def test_build_config_validation():
        """Test build config validation"""
        # Valid config
        config = BuildConfig(
            project_id="test-project",
            project_name="TestApp",
            framework="flutter",
            platforms=["android", "ios"],
            version="1.0.0"
        )
        
        valid, errors = config.validate()
        assert valid, f"Config validation failed: {errors}"
        
        # Invalid config
        config = BuildConfig(
            project_id="",
            project_name="TestApp",
            framework="invalid",
            platforms=[],
            version="1.0.0"
        )
        
        valid, errors = config.validate()
        assert not valid, "Invalid config should fail"
        assert len(errors) > 0, "Expected validation errors"
        
        print("✅ Build config validation test passed")
        return True
    
    @staticmethod
    def test_flutter_builder():
        """Test Flutter builder initialization"""
        config = BuildConfig(
            project_id="test-flutter",
            project_name="FlutterApp",
            framework="flutter",
            platforms=["android", "ios"],
            version="1.0.0"
        )
        
        builder = FlutterBuilder(config)
        assert builder is not None, "Flutter builder initialization failed"
        assert builder.config.project_name == "FlutterApp"
        
        print("✅ Flutter builder test passed")
        return True
    
    @staticmethod
    def test_wxpython_builder():
        """Test wxPython builder initialization"""
        config = BuildConfig(
            project_id="test-wx",
            project_name="DesktopApp",
            framework="wxwidgets",
            platforms=["windows", "linux", "macos"],
            version="1.0.0"
        )
        
        builder = wxPythonBuilder(config)
        assert builder is not None, "wxPython builder initialization failed"
        assert builder.config.project_name == "DesktopApp"
        
        print("✅ wxPython builder test passed")
        return True
    
    @staticmethod
    def test_fastapi_ml_builder():
        """Test FastAPI-ML builder"""
        config = BuildConfig(
            project_id="test-fastapi-ml",
            project_name="MLServer",
            framework="fastapi-ml",
            platforms=["linux"],
            version="1.0.0"
        )
        
        builder = FastAPIMLBuilder(config)
        assert builder is not None, "FastAPI-ML builder initialization failed"
        dockerfile = builder._generate_dockerfile()
        assert "python:3.10" in dockerfile.lower(), "Dockerfile should contain Python 3.10"
        assert "uvicorn" in dockerfile.lower(), "Dockerfile should contain Uvicorn"
        assert "requirements.txt" in dockerfile, "Dockerfile should install requirements"
        
        print("✅ FastAPI-ML builder test passed")
        return True
    
    @staticmethod
    def test_replit_base40_builder():
        """Test Replit Base40 builder"""
        config = BuildConfig(
            project_id="test-replit",
            project_name="ReplitApp",
            framework="replit-base40",
            platforms=["replit"],
            version="1.0.0"
        )
        
        builder = ReplitBase40Builder(config)
        assert builder is not None, "Replit Base40 builder initialization failed"
        
        # Test language detection
        lang = builder._detect_language()
        assert lang is not None, "Language detection failed"
        
        # Test config generation
        config_str = builder._generate_replit_config("python")
        assert "language" in config_str, "Config should contain language"
        assert "python" in config_str, "Config should be Python"
        
        # Test script generation
        script = builder._generate_run_script("python")
        assert "#!/bin/bash" in script, "Script should be bash"
        assert "python" in script.lower(), "Script should reference Python"
        
        print("✅ Replit Base40 builder test passed")
        return True
    
    @staticmethod
    def test_emergent_sh_builder():
        """Test Emergent.sh builder"""
        config = BuildConfig(
            project_id="test-emergent",
            project_name="K8sApp",
            framework="emergent-sh",
            platforms=["kubernetes"],
            version="1.0.0"
        )
        
        builder = EmergentShBuilder(config)
        assert builder is not None, "Emergent.sh builder initialization failed"
        
        # Test config generation
        config_str = builder._generate_emergent_config()
        assert "version" in config_str, "Config should have version"
        assert "deployment" in config_str, "Config should have deployment section"
        assert "production" in config_str, "Config should have production environment"
        
        # Test manifest generation
        manifest = builder._generate_manifest()
        assert "metadata" in manifest, "Manifest should have metadata"
        assert manifest["metadata"]["name"] == "K8sApp"
        assert manifest["spec"]["replicas"] == 3, "Should have 3 replicas"
        
        # Test deploy script
        script = builder._generate_deploy_script()
        assert "#!/bin/bash" in script, "Script should be bash"
        assert "docker build" in script, "Script should build Docker image"
        assert "emergent-cli" in script, "Script should use emergent-cli"
        
        print("✅ Emergent.sh builder test passed")
        return True
    
    @staticmethod
    def test_build_orchestrator():
        """Test build orchestrator"""
        orchestrator = BuildOrchestrator
        
        # Check builders registered
        assert "flutter" in orchestrator.BUILDERS, "Flutter builder not registered"
        assert "wxwidgets" in orchestrator.BUILDERS, "wxPython builder not registered"
        assert "replit-base40" in orchestrator.BUILDERS, "Replit Base40 builder not registered"
        assert "emergent-sh" in orchestrator.BUILDERS, "Emergent.sh builder not registered"
        
        print("✅ Build orchestrator test passed")
        return True
    
    @staticmethod
    def run_all_tests():
        """Run all integration tests"""
        print("\n" + "="*60)
        print("INTEGRATION TEST SUITE - FIXED & NEW FRAMEWORKS")
        print("="*60 + "\n")
        
        tests = [
            ("Framework Enum", IntegrationTest.test_framework_enum),
            ("Build Config Validation", IntegrationTest.test_build_config_validation),
            ("Flutter Builder", IntegrationTest.test_flutter_builder),
            ("wxPython Builder", IntegrationTest.test_wxpython_builder),
            ("FastAPI-ML Builder", IntegrationTest.test_fastapi_ml_builder),
            ("Replit Base40 Builder", IntegrationTest.test_replit_base40_builder),
            ("Emergent.sh Builder", IntegrationTest.test_emergent_sh_builder),
            ("Build Orchestrator", IntegrationTest.test_build_orchestrator),
        ]
        
        results = []
        for test_name, test_func in tests:
            try:
                print(f"Running: {test_name}...", end=" ")
                result = test_func()
                results.append((test_name, True, None))
            except Exception as e:
                print(f"❌ FAILED: {str(e)}")
                results.append((test_name, False, str(e)))
        
        # Summary
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        
        passed = sum(1 for _, success, _ in results if success)
        failed = sum(1 for _, success, _ in results if not success)
        
        for test_name, success, error in results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status}: {test_name}")
            if error:
                print(f"  Error: {error}")
        
        print(f"\nTotal: {passed} passed, {failed} failed out of {len(results)}")
        
        if failed == 0:
            print("\n🎉 ALL TESTS PASSED - Framework integration successful!")
            return True
        else:
            print(f"\n⚠️  {failed} test(s) failed")
            return False


if __name__ == "__main__":
    success = IntegrationTest.run_all_tests()
    sys.exit(0 if success else 1)
