#!/usr/bin/env python
"""
Test Orchestrator Workflow - Comprehensive Test
"""
import sys
from pathlib import Path
import shutil

sys.path.insert(0, str(Path(__file__).parent / "backend"))

from build_system_enterprise import (
    BuildConfig,
    BuildOrchestrator,
    SystemValidator,
)

def cleanup_artifacts():
    """Clean up test artifacts"""
    artifacts_dir = Path("./artifacts")
    if artifacts_dir.exists():
        shutil.rmtree(artifacts_dir)

def main():
    print("\n" + "="*70)
    print("  TEST 4: ORCHESTRATOR WORKFLOW")
    print("="*70 + "\n")
    
    # Clean up first
    cleanup_artifacts()
    
    try:
        # Step 1: Initialize orchestrator
        print("Step 1: Initializing orchestrator...")
        orchestrator = BuildOrchestrator()
        print("  ✓ Orchestrator initialized: OK\n")
        
        # Step 2: Verify npm is detected
        print("Step 2: Verifying system tools...")
        npm_ok, npm_v = SystemValidator.check_npm()
        print(f"  npm detected: {npm_ok} - {npm_v}")
        
        if not npm_ok:
            print("  ✗ npm not detected - test cannot continue")
            return False
        print()
        
        # Step 3: Validate environment for React
        print("Step 3: Validating environment for React framework...")
        env_ok, validation = SystemValidator.validate_environment("react")
        print(f"  Environment OK: {env_ok}")
        print(f"  Missing tools: {validation['missing_tools']}")
        
        if not env_ok:
            print(f"  ✗ Environment validation failed: {validation['missing_tools']}")
            return False
        print()
        
        # Step 4: Create valid build configs
        print("Step 4: Creating build configurations...")
        config1 = BuildConfig(
            project_id="test-app-1",
            project_name="TestApp1",
            framework="react",
            platforms=["web"]
        )
        
        config2 = BuildConfig(
            project_id="test-app-2",
            project_name="TestApp2",
            framework="electron",
            platforms=["windows"]
        )
        print("  ✓ Configurations created\n")
        
        # Step 5: Submit builds
        print("Step 5: Submitting builds...")
        success1, job_id1, msg1 = orchestrator.submit_build(config1)
        print(f"  Build 1 (React): {msg1}")
        print(f"    Success: {success1}, Job ID: {job_id1[:8]}...\n" if success1 else f"    FAILED: {msg1}\n")
        
        success2, job_id2, msg2 = orchestrator.submit_build(config2)
        print(f"  Build 2 (Electron): {msg2}")
        print(f"    Success: {success2}, Job ID: {job_id2[:8]}...\n" if success2 else f"    FAILED: {msg2}\n")
        
        if not (success1 and success2):
            print("  ✗ Build submission failed")
            return False
        
        # Step 6: Check job status
        print("Step 6: Checking job status...")
        status1 = orchestrator.check_job_status(job_id1)
        status2 = orchestrator.check_job_status(job_id2)
        
        if status1:
            print(f"  Build 1 status: {status1.get('status', 'unknown')}")
        if status2:
            print(f"  Build 2 status: {status2.get('status', 'unknown')}")
        
        if not (status1 and status2):
            print("  ✗ Status check failed")
            return False
        print()
        
        # Step 7: Check build history
        print("Step 7: Checking build history...")
        history = orchestrator.get_build_history()
        print(f"  Total builds: {len(history)}")
        
        if len(history) < 2:
            print("  ✗ Build history incomplete")
            return False
        print()
        
        # Step 8: Test job cancellation
        print("Step 8: Testing job cancellation...")
        cancelled = orchestrator.cancel_job(job_id1)
        print(f"  Job cancellation: {'Success' if cancelled else 'Failed'}\n")
        
        # Step 9: Verify jobs file exists
        print("Step 9: Verifying jobs persistence...")
        jobs_file = Path("./artifacts/build_jobs.json")
        exists = jobs_file.exists()
        print(f"  Jobs file exists: {exists}")
        print(f"  Jobs file path: {jobs_file.absolute()}\n")
        
        if not exists:
            print("  ✗ Jobs file not created")
            return False
        
        print("="*70)
        print("  RESULT: ✓ ORCHESTRATOR WORKFLOW TEST PASSED")
        print("="*70 + "\n")
        
        return True
        
    except Exception as e:
        print(f"  ✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
