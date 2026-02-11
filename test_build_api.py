#!/usr/bin/env python3
"""
Test the build system API endpoints
"""

import requests
import json
from time import sleep

BASE_URL = "http://localhost:8000"

# Test token (for auth)
TEST_TOKEN = "test-token-123"
HEADERS = {
    "Authorization": f"Bearer {TEST_TOKEN}",
    "Content-Type": "application/json"
}

def test_build_system():
    """Test build system endpoints"""
    
    print("=" * 60)
    print("BUILD SYSTEM API TEST")
    print("=" * 60)
    
    # 1. Submit build
    print("\n1. Submitting build request...")
    build_request = {
        "project_id": "api-test-001",
        "project_name": "APITestApp",
        "framework": "tauri",
        "platforms": ["windows", "macos"],
        "version": "1.0.0",
        "build_type": "release"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/builds/submit",
            json=build_request,
            headers=HEADERS,
            timeout=5
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            job_id = result.get("job_id")
            print(f"   Job ID: {job_id}")
            
            if not job_id:
                print("   ERROR: No job_id returned!")
                return
        else:
            print(f"   ERROR: {response.text}")
            return
    except Exception as e:
        print(f"   ERROR: {e}")
        return
    
    # 2. Execute build
    print(f"\n2. Executing build {job_id}...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/builds/{job_id}/execute",
            headers=HEADERS,
            timeout=30
        )
        print(f"   Status: {response.status_code}")
        if response.status_code != 200:
            print(f"   ERROR: {response.text}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # 3. Check status
    print(f"\n3. Checking build status...")
    try:
        response = requests.get(
            f"{BASE_URL}/api/builds/{job_id}/status",
            headers=HEADERS,
            timeout=5
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            status = response.json()
            print(f"   Build status: {status.get('status')}")
            print(f"   Progress: {status.get('progress')}%")
            artifacts = status.get('artifacts', [])
            print(f"   Artifacts: {len(artifacts)}")
            for artifact in artifacts:
                print(f"     - {artifact['file_name']} ({artifact['platform']})")
        else:
            print(f"   ERROR: {response.text}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # 4. Get logs
    print(f"\n4. Getting build logs...")
    try:
        response = requests.get(
            f"{BASE_URL}/api/builds/{job_id}/logs",
            headers=HEADERS,
            timeout=5
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            logs = response.json().get("logs", "")
            # Print first 500 chars
            print(f"   Logs (first 500 chars):\n{logs[:500]}")
        else:
            print(f"   ERROR: {response.text}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # 5. Get active builds
    print(f"\n5. Getting active builds...")
    try:
        response = requests.get(
            f"{BASE_URL}/api/builds/active",
            headers=HEADERS,
            timeout=5
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            active = response.json().get("active_builds", [])
            print(f"   Active builds: {len(active)}")
        else:
            print(f"   ERROR: {response.text}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # 6. Get build history
    print(f"\n6. Getting build history...")
    try:
        response = requests.get(
            f"{BASE_URL}/api/builds/history?limit=5",
            headers=HEADERS,
            timeout=5
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            history = response.json().get("history", [])
            print(f"   History count: {len(history)}")
            for build in history[:3]:
                print(f"     - {build['job_id'][:8]}... ({build['status']})")
        else:
            print(f"   ERROR: {response.text}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    test_build_system()
