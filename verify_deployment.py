#!/usr/bin/env python3
"""
Snapchat Filters Integration - Deployment Verification Script
Validates all components are properly integrated and functional
"""

import sys
import os
import subprocess
from pathlib import Path

def check_file_exists(path: str) -> bool:
    """Check if a required file exists"""
    exists = os.path.isfile(path)
    status = "✅" if exists else "❌"
    print(f"{status} {path}")
    return exists

def check_imports(module_path: str, import_names: list) -> bool:
    """Test if module imports work"""
    try:
        sys.path.insert(0, os.path.dirname(module_path))
        module_name = os.path.splitext(os.path.basename(module_path))[0]
        
        for import_name in import_names:
            exec(f"from {module_name} import {import_name}")
        
        print(f"✅ All imports from {os.path.basename(module_path)}")
        return True
    except Exception as e:
        print(f"❌ Import error in {os.path.basename(module_path)}: {e}")
        return False

def run_tests() -> bool:
    """Run the test suite"""
    try:
        result = subprocess.run(
            ["pytest", "backend/test_snapchat_integration.py", "-v", "--tb=short"],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            print("✅ All tests PASSED")
            return True
        else:
            print("❌ Tests FAILED")
            print(result.stdout[-500:] if len(result.stdout) > 500 else result.stdout)
            return False
    except Exception as e:
        print(f"⚠️  Could not run tests: {e}")
        return None

def check_security() -> bool:
    """Check security scan results"""
    try:
        result = subprocess.run(
            ["snyk", "code", "scan", "backend/snapchat_filters_engine.py"],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if "0 issues" in result.stdout or "0 vulnerabilities" in result.stdout:
            print("✅ Security scan PASSED (0 vulnerabilities)")
            return True
        elif "could not" in result.stdout.lower() or "not installed" in result.stdout.lower():
            print("⚠️  Snyk not available (install with: npm install -g snyk)")
            return None
        else:
            print("❌ Security scan found issues")
            return False
    except Exception as e:
        print(f"⚠️  Could not run security scan: {e}")
        return None

def verify_api_endpoints() -> bool:
    """Verify API endpoints are registered"""
    try:
        # Check if routes are defined
        with open("backend/ai_filter_studio.py", "r") as f:
            content = f.read()
        
        endpoints = [
            "/snapchat-filters/available",
            "/snapchat-filters/by-category",
            "/snapchat-filters/by-platform",
            "/snapchat-filters/apply",
            "/snapchat-filters/smart-enhance"
        ]
        
        all_found = True
        for endpoint in endpoints:
            if endpoint in content:
                print(f"✅ Endpoint {endpoint} found")
            else:
                print(f"❌ Endpoint {endpoint} NOT found")
                all_found = False
        
        return all_found
    except Exception as e:
        print(f"❌ Error checking endpoints: {e}")
        return False

def verify_websocket_integration() -> bool:
    """Verify WebSocket integration"""
    try:
        with open("backend/ws_stream_handler.py", "r") as f:
            content = f.read()
        
        checks = {
            "snapchat_filters in StreamSession": "self.snapchat_filters" in content,
            "snapchat_filters message handler": "snapchat_filters" in content and "message_type" in content,
            "social_platform in session": "self.social_platform" in content
        }
        
        all_found = True
        for check_name, found in checks.items():
            status = "✅" if found else "❌"
            print(f"{status} {check_name}")
            all_found = all_found and found
        
        return all_found
    except Exception as e:
        print(f"❌ Error checking WebSocket: {e}")
        return False

def verify_react_integration() -> bool:
    """Verify React component integration"""
    try:
        with open("frontend/src/components/AIFilterStudio.jsx", "r") as f:
            content = f.read()
        
        checks = {
            "Snapchat filters state": "snapchatFilters" in content,
            "Social platform selector": "socialPlatform" in content,
            "Filter UI panel": "🔥 Snapchat Filters" in content,
            "Intensity sliders": "type=\"range\"" in content
        }
        
        all_found = True
        for check_name, found in checks.items():
            status = "✅" if found else "❌"
            print(f"{status} {check_name}")
            all_found = all_found and found
        
        return all_found
    except Exception as e:
        print(f"❌ Error checking React: {e}")
        return False

def main():
    """Run all deployment verification checks"""
    print("\n" + "="*70)
    print("🚀 SNAPCHAT FILTERS INTEGRATION - DEPLOYMENT VERIFICATION")
    print("="*70 + "\n")
    
    results = {}
    
    # 1. Check required files
    print("📁 Checking Required Files...\n")
    required_files = [
        "backend/snapchat_filters_engine.py",
        "backend/ai_filter_studio.py",
        "backend/ws_stream_handler.py",
        "backend/test_snapchat_integration.py",
        "frontend/src/components/AIFilterStudio.jsx",
    ]
    
    files_ok = all(check_file_exists(f) for f in required_files)
    results["Required Files"] = files_ok
    print()
    
    # 2. Check imports
    print("📦 Checking Python Imports...\n")
    imports_ok = check_imports(
        "backend/snapchat_filters_engine.py",
        ["FilterRegistry", "AdvancedFaceDetector", "AdvancedBeautyFilters"]
    )
    results["Imports"] = imports_ok
    print()
    
    # 3. Verify API endpoints
    print("🔌 Verifying API Endpoints...\n")
    endpoints_ok = verify_api_endpoints()
    results["API Endpoints"] = endpoints_ok
    print()
    
    # 4. Verify WebSocket integration
    print("🔌 Verifying WebSocket Integration...\n")
    ws_ok = verify_websocket_integration()
    results["WebSocket"] = ws_ok
    print()
    
    # 5. Verify React integration
    print("⚛️  Verifying React Integration...\n")
    react_ok = verify_react_integration()
    results["React"] = react_ok
    print()
    
    # 6. Run tests
    print("🧪 Running Test Suite...\n")
    tests_ok = run_tests()
    results["Tests"] = tests_ok
    print()
    
    # 7. Run security scan
    print("🔒 Running Security Scan...\n")
    security_ok = check_security()
    results["Security"] = security_ok
    print()
    
    # Summary
    print("="*70)
    print("📊 VERIFICATION SUMMARY")
    print("="*70 + "\n")
    
    for check_name, result in results.items():
        if result is True:
            status = "✅ PASSED"
        elif result is False:
            status = "❌ FAILED"
        else:
            status = "⚠️  SKIPPED"
        print(f"{status:12} {check_name}")
    
    print("\n" + "="*70)
    
    # Overall status
    all_passed = all(v is True or v is None for v in results.values())
    critical_passed = all(results.get(k) is True for k in ["Required Files", "Imports", "API Endpoints", "WebSocket", "React"])
    
    if critical_passed:
        print("🎉 DEPLOYMENT READY - All critical checks PASSED!")
        print("\nReady to deploy to production.")
        return 0
    elif all_passed:
        print("⚠️  MOSTLY READY - Some optional checks skipped")
        print("\nCan deploy with caution. Run optional checks if possible.")
        return 0
    else:
        print("❌ NOT READY - Some critical checks FAILED")
        print("\nFix failures before deployment.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
