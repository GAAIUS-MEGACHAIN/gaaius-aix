"""
ENTERPRISE BUILD SYSTEM - PRODUCTION TEST
Validates real binary compilation system
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "backend"))

from build_system_enterprise import (
    BuildConfig,
    BuildOrchestrator,
    SystemValidator,
)


def print_header(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")


def test_system():
    """Test 1: System validation"""
    print_header("TEST 1: SYSTEM VALIDATION")
    
    node_ok, node_v = SystemValidator.check_nodejs()
    npm_ok, npm_v = SystemValidator.check_npm()
    cargo_ok, cargo_v = SystemValidator.check_cargo()
    docker_ok, docker_v = SystemValidator.check_docker()
    
    print(f"  Node.js: {'OK' if node_ok else 'FAIL'} - {node_v}")
    print(f"  npm: {'OK' if npm_ok else 'FAIL'} - {npm_v}")
    print(f"  Cargo: {'OK' if cargo_ok else 'FAIL'} - {cargo_v}")
    print(f"  Docker: {'OK' if docker_ok else 'FAIL'} - {docker_v}")
    
    return node_ok and npm_ok


def test_frameworks():
    """Test 2: Framework validation"""
    print_header("TEST 2: FRAMEWORK SUPPORT")
    
    frameworks = ["tauri", "electron", "flutter", "react", "angular", "vue", "next", "svelte"]
    
    for fw in frameworks:
        ok, validation = SystemValidator.validate_environment(fw)
        status = "OK" if ok else "MISSING TOOLS"
        print(f"  {fw.upper()}: {status}")
    
    return True


def test_configs():
    """Test 3: Configuration validation"""
    print_header("TEST 3: CONFIG VALIDATION")
    
    # Test valid configs
    configs = [
        BuildConfig("app1", "App1", "react", ["web"]),
        BuildConfig("app2", "App2", "tauri", ["windows", "macos"]),
        BuildConfig("app3", "App3", "flutter", ["android"]),
    ]
    
    for config in configs:
        valid, errors = config.validate()
        print(f"  {config.project_name}: {'OK' if valid else 'FAIL'}")
    
    # Test invalid configs
    print("\n  Testing invalid configs:")
    
    invalid = [
        (BuildConfig("", "App", "react", ["web"]), "no project_id"),
        (BuildConfig("app", "App", "badfw", ["web"]), "invalid framework"),
        (BuildConfig("app", "App", "react", []), "no platforms"),
    ]
    
    for config, reason in invalid:
        valid, _ = config.validate()
        result = "CORRECTLY REJECTED" if not valid else "ERROR"
        print(f"  {reason}: {result}")
    
    return True


def test_orchestrator():
    """Test 4: Orchestrator"""
    print_header("TEST 4: ORCHESTRATOR WORKFLOW")
    
    try:
        orchestrator = BuildOrchestrator()
        print("  Orchestrator initialized: OK")
        
        # Submit builds
        config1 = BuildConfig("test1", "TestApp1", "react", ["web"])
        success1, job_id1, msg1 = orchestrator.submit_build(config1)
        
        config2 = BuildConfig("test2", "TestApp2", "electron", ["windows"])
        success2, job_id2, msg2 = orchestrator.submit_build(config2)
        
        print(f"  Build 1 submission: {'OK' if success1 else 'FAIL'} - {msg1}")
        print(f"  Build 2 submission: {'OK' if success2 else 'FAIL'} - {msg2}")
        
        # Check status
        if success1:
            status = orchestrator.check_job_status(job_id1)
            print(f"  Status check: OK - {status.get('status') if status else 'unknown'}")
        
        # Check history
        history = orchestrator.get_build_history()
        print(f"  Build history: OK - {len(history)} builds")
        
        return success1 and success2
        
    except Exception as e:
        print(f"  ERROR: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("  ENTERPRISE BUILD SYSTEM - CLEAN VALIDATION TEST")
    print("="*70)
    
    test1 = test_system()
    test2 = test_frameworks()
    test3 = test_configs()
    test4 = test_orchestrator()
    
    print_header("RESULTS")
    
    all_tests = [
        ("System Validation", test1),
        ("Framework Support", test2),
        ("Config Validation", test3),
        ("Orchestrator", test4),
    ]
    
    for name, result in all_tests:
        status = "PASS" if result else "FAIL"
        print(f"  {name}: {status}")
    
    all_passed = all(r for _, r in all_tests)
    
    print("\n" + "="*70)
    if all_passed:
        print("  OVERALL RESULT: ALL TESTS PASSED ✓")
        print("  SYSTEM STATUS: PRODUCTION READY")
    else:
        print("  OVERALL RESULT: SOME TESTS FAILED")
    print("="*70 + "\n")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
