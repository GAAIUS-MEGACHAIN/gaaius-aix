#!/usr/bin/env python
"""
Verification script for Orchestrator fixes
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "backend"))

from build_system_enterprise import SystemValidator, BuildConfig, BuildOrchestrator

print("\n" + "="*70)
print("  ORCHESTRATOR FIX VERIFICATION")
print("="*70 + "\n")

# Test 1: Verify npm detection
print("TEST 1: npm Detection")
print("-" * 70)
npm_ok, npm_v = SystemValidator.check_npm()
print(f"npm Found: {npm_ok}")
print(f"npm Version: {npm_v}")
print(f"Status: {'✓ PASS' if npm_ok else '✗ FAIL'}\n")

# Test 2: Verify validate_environment logic
print("TEST 2: Environment Validation Logic")
print("-" * 70)
frameworks = ["react", "electron", "tauri", "flutter"]
all_valid = True

for fw in frameworks:
    env_ok, validation = SystemValidator.validate_environment(fw)
    missing = validation.get("missing_tools", [])
    
    # For React and Electron, we should have env_ok=True (only need npm/node)
    # For Tauri, we need npm/node AND cargo
    # For Flutter, we need npm/node AND docker (for mobile)
    
    print(f"{fw.upper():12} - Ready: {env_ok:5} - Missing: {missing if missing else 'None'}")
    
    if fw in ["react", "electron"]:
        if not env_ok:
            all_valid = False

print(f"Status: {'✓ PASS' if all_valid else '✗ FAIL'}\n")

# Test 3: Verify orchestrator initialization
print("TEST 3: Orchestrator Initialization")
print("-" * 70)
try:
    orchestrator = BuildOrchestrator()
    jobs_file = Path("./artifacts/build_jobs.json")
    
    print(f"Orchestrator Created: True")
    print(f"Jobs File Path: {orchestrator.jobs_file}")
    print(f"Jobs File Exists: {jobs_file.exists()}")
    print(f"Artifact Directory Exists: {Path('./artifacts').exists()}")
    print(f"Status: ✓ PASS\n")
    
except Exception as e:
    print(f"Status: ✗ FAIL - {e}\n")

# Test 4: Verify build submission
print("TEST 4: Build Submission")
print("-" * 70)
try:
    config = BuildConfig(
        project_id="test-app",
        project_name="TestApp",
        framework="react",
        platforms=["web"]
    )
    
    success, job_id, msg = orchestrator.submit_build(config)
    
    print(f"Build Submission Success: {success}")
    print(f"Job ID: {job_id[:12]}... (truncated)")
    print(f"Message: {msg}")
    print(f"Status: {'✓ PASS' if success else '✗ FAIL'}\n")
    
except Exception as e:
    print(f"Status: ✗ FAIL - {e}\n")

# Test 5: Verify job retrieval
print("TEST 5: Job Status Retrieval")
print("-" * 70)
try:
    if 'job_id' in locals():
        status = orchestrator.check_job_status(job_id)
        
        if status:
            print(f"Job Status Retrieved: True")
            print(f"Job Status Value: {status.get('status', 'unknown')}")
            print(f"Status: ✓ PASS\n")
        else:
            print(f"Status: ✗ FAIL - Could not retrieve job status\n")
    else:
        print(f"Status: SKIPPED - No job_id from previous test\n")
        
except Exception as e:
    print(f"Status: ✗ FAIL - {e}\n")

print("="*70)
print("  VERIFICATION COMPLETE")
print("="*70 + "\n")
