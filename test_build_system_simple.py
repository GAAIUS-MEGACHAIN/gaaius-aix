#!/usr/bin/env python3
"""Test the simple build system"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'backend'))

from build_system_simple import SimpleBuildCoordinator, BuildConfig

# Create coordinator
coordinator = SimpleBuildCoordinator(output_dir="./artifacts")

# Create a test build config
config = BuildConfig(
    project_id="test-app-001",
    project_name="TestApp",
    framework="tauri",
    platforms=["windows", "macos", "linux"],
    version="1.0.0"
)

# Submit build
print("1. Submitting build request...")
job_id = coordinator.submit_build_request(config)
print(f"   Job ID: {job_id}")

# Execute build
print("\n2. Executing build...")
success = coordinator.execute_build(job_id, config, "./")
print(f"   Build successful: {success}")

# Check status
print("\n3. Checking build status...")
status = coordinator.get_job_status(job_id)
print(f"   Status: {status['status']}")
print(f"   Progress: {status['progress']}%")
print(f"   Artifacts: {len(status['artifacts'])} created")

for artifact in status['artifacts']:
    print(f"     - {artifact['file_name']} ({artifact['platform']})")

# Get logs
print("\n4. Build logs:")
logs = coordinator.get_job_logs(job_id)
print(logs)

print("\n✅ Build system test completed!")
