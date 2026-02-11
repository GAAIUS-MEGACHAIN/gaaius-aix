#!/usr/bin/env python
"""Quick verification of orchestrator fixes"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "backend"))

from build_system_enterprise import SystemValidator, BuildConfig, BuildOrchestrator

print("\n=== ORCHESTRATOR FIX VERIFICATION ===\n")

# Test 1: npm Detection
print("TEST 1: npm Detection")
try:
    npm_ok, npm_v = SystemValidator.check_npm()
    print(f"  npm Found: {npm_ok}")
    print(f"  npm Version: {npm_v}")
    print(f"  RESULT: PASS\n" if npm_ok else "  RESULT: FAIL\n")
except Exception as e:
    print(f"  RESULT: FAIL - {e}\n")

# Test 2: validate_environment returns correct boolean
print("TEST 2: validate_environment Fix (Line 250)")
try:
    env_ok, validation = SystemValidator.validate_environment('react')
    is_bool = isinstance(env_ok, bool)
    print(f"  React environment ready: {env_ok}")
    print(f"  Returns boolean: {is_bool}")
    print(f"  Missing tools: {validation.get('missing_tools', [])}")
    status = "PASS" if is_bool and env_ok else "FAIL"
    print(f"  RESULT: {status}\n")
except Exception as e:
    print(f"  RESULT: FAIL - {e}\n")

# Test 3: Orchestrator initialization (path fix)
print("TEST 3: Orchestrator Path Fix (Lines 716-720)")
try:
    orch = BuildOrchestrator()
    jobs_file_path = str(orch.jobs_file)
    parent_exists = orch.jobs_file.parent.exists()
    has_artifact_dir = "artifacts" in jobs_file_path
    
    print(f"  Orchestrator created: True")
    print(f"  Jobs file path: {jobs_file_path}")
    print(f"  Jobs file parent exists: {parent_exists}")
    print(f"  Has artifact directory: {has_artifact_dir}")
    
    status = "PASS" if parent_exists and has_artifact_dir else "FAIL"
    print(f"  RESULT: {status}\n")
except Exception as e:
    print(f"  RESULT: FAIL - {e}\n")

# Test 4: Build submission
print("TEST 4: Build Submission")
try:
    config = BuildConfig(
        project_id="test-app",
        project_name="TestApp",
        framework="react",
        platforms=["web"]
    )
    
    success, job_id, msg = orch.submit_build(config)
    print(f"  Submission success: {success}")
    print(f"  Job ID: {job_id[:12]}...")
    print(f"  Message: {msg}")
    print(f"  RESULT: PASS\n" if success else "  RESULT: FAIL\n")
except Exception as e:
    print(f"  RESULT: FAIL - {e}\n")

print("=== VERIFICATION COMPLETE ===\n")
