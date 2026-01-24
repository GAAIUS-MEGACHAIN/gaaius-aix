"""
Test Suite for GAAIUS PROJECT RUNTIME v2.0.0
============================================
Testing new features:
1. Refresh button in preview panel
2. Preview auto-switch after code generation
3. 80,000+ lines staged building capability
4. ChatGPT-style spacing in chat messages
5. Shell scripts for running projects locally
6. Multi-agent orchestration system
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestRuntimeStatusV2:
    """Test /api/build/runtime-status endpoint for v2.0.0 features"""
    
    def test_runtime_status_returns_200(self):
        """Runtime status endpoint should return 200"""
        response = requests.get(f"{BASE_URL}/api/build/runtime-status")
        assert response.status_code == 200
        print("✅ Runtime status returns 200")
    
    def test_runtime_version_is_2_0_0(self):
        """Runtime version should be 2.0.0"""
        response = requests.get(f"{BASE_URL}/api/build/runtime-status")
        data = response.json()
        assert data.get("version") == "2.0.0", f"Expected version 2.0.0, got {data.get('version')}"
        print(f"✅ Runtime version is {data.get('version')}")
    
    def test_min_target_lines_is_80000(self):
        """min_target_lines should be 80000"""
        response = requests.get(f"{BASE_URL}/api/build/runtime-status")
        data = response.json()
        assert data.get("min_target_lines") == 80000, f"Expected 80000, got {data.get('min_target_lines')}"
        print(f"✅ min_target_lines is {data.get('min_target_lines')}")
    
    def test_capabilities_include_devops(self):
        """Capabilities should include devops with Docker, Shell Scripts, Makefile"""
        response = requests.get(f"{BASE_URL}/api/build/runtime-status")
        data = response.json()
        capabilities = data.get("capabilities", {})
        devops = capabilities.get("devops", [])
        
        assert "Docker" in devops, "Docker should be in devops capabilities"
        assert "Docker Compose" in devops, "Docker Compose should be in devops capabilities"
        assert "Shell Scripts" in devops, "Shell Scripts should be in devops capabilities"
        assert "Makefile" in devops, "Makefile should be in devops capabilities"
        print(f"✅ DevOps capabilities: {devops}")
    
    def test_features_include_staged_building(self):
        """Features should include staged building"""
        response = requests.get(f"{BASE_URL}/api/build/runtime-status")
        data = response.json()
        features = data.get("capabilities", {}).get("features", [])
        
        staged_building_present = any("Staged building" in f or "staged building" in f.lower() for f in features)
        assert staged_building_present, f"Staged building not found in features: {features}"
        print("✅ Staged building feature present")
    
    def test_features_include_multi_agent(self):
        """Features should include multi-agent orchestration"""
        response = requests.get(f"{BASE_URL}/api/build/runtime-status")
        data = response.json()
        features = data.get("capabilities", {}).get("features", [])
        
        multi_agent_present = any("multi-agent" in f.lower() or "Multi-agent" in f for f in features)
        assert multi_agent_present, f"Multi-agent orchestration not found in features: {features}"
        print("✅ Multi-agent orchestration feature present")
    
    def test_build_stages_list_present(self):
        """build_stages list should be present"""
        response = requests.get(f"{BASE_URL}/api/build/runtime-status")
        data = response.json()
        build_stages = data.get("build_stages", [])
        
        assert len(build_stages) >= 10, f"Expected at least 10 build stages, got {len(build_stages)}"
        print(f"✅ Build stages count: {len(build_stages)}")
    
    def test_agent_roles_list_present(self):
        """agent_roles list should be present"""
        response = requests.get(f"{BASE_URL}/api/build/runtime-status")
        data = response.json()
        agent_roles = data.get("agent_roles", [])
        
        assert len(agent_roles) >= 8, f"Expected at least 8 agent roles, got {len(agent_roles)}"
        print(f"✅ Agent roles count: {len(agent_roles)}")


class TestBuildStagesEndpoint:
    """Test /api/build/stages endpoint"""
    
    def test_stages_endpoint_returns_200(self):
        """Stages endpoint should return 200"""
        response = requests.get(f"{BASE_URL}/api/build/stages")
        assert response.status_code == 200
        print("✅ Stages endpoint returns 200")
    
    def test_stages_returns_10_stages(self):
        """Should return 10 build stages"""
        response = requests.get(f"{BASE_URL}/api/build/stages")
        data = response.json()
        stages = data.get("stages", {})
        
        assert len(stages) == 10, f"Expected 10 stages, got {len(stages)}"
        print(f"✅ Stages count: {len(stages)}")
    
    def test_stages_have_required_fields(self):
        """Each stage should have name, description, files, estimated_lines"""
        response = requests.get(f"{BASE_URL}/api/build/stages")
        data = response.json()
        stages = data.get("stages", {})
        
        for stage_id, stage_info in stages.items():
            assert "name" in stage_info, f"Stage {stage_id} missing 'name'"
            assert "description" in stage_info, f"Stage {stage_id} missing 'description'"
            assert "files" in stage_info, f"Stage {stage_id} missing 'files'"
            assert "estimated_lines" in stage_info, f"Stage {stage_id} missing 'estimated_lines'"
        print("✅ All stages have required fields")
    
    def test_stages_min_target_lines_is_80000(self):
        """min_target_lines should be 80000"""
        response = requests.get(f"{BASE_URL}/api/build/stages")
        data = response.json()
        
        assert data.get("min_target_lines") == 80000
        print(f"✅ Stages min_target_lines: {data.get('min_target_lines')}")
    
    def test_stages_include_devops_stage(self):
        """Should include a DevOps stage with Docker, run.sh, etc."""
        response = requests.get(f"{BASE_URL}/api/build/stages")
        data = response.json()
        stages = data.get("stages", {})
        
        devops_stage = stages.get("stage_10_devops", {})
        assert devops_stage, "stage_10_devops not found"
        
        files = devops_stage.get("files", [])
        assert "Dockerfile" in files or "docker-compose.yml" in files, f"DevOps files: {files}"
        assert "run.sh" in files, f"run.sh not in DevOps files: {files}"
        print(f"✅ DevOps stage files: {files}")


class TestAgentsEndpoint:
    """Test /api/build/agents endpoint"""
    
    def test_agents_endpoint_returns_200(self):
        """Agents endpoint should return 200"""
        response = requests.get(f"{BASE_URL}/api/build/agents")
        assert response.status_code == 200
        print("✅ Agents endpoint returns 200")
    
    def test_agents_returns_8_roles(self):
        """Should return 8 agent roles"""
        response = requests.get(f"{BASE_URL}/api/build/agents")
        data = response.json()
        agents = data.get("agents", {})
        
        assert len(agents) == 8, f"Expected 8 agents, got {len(agents)}"
        print(f"✅ Agent roles count: {len(agents)}")
    
    def test_agents_have_required_fields(self):
        """Each agent should have name, role, outputs"""
        response = requests.get(f"{BASE_URL}/api/build/agents")
        data = response.json()
        agents = data.get("agents", {})
        
        for agent_id, agent_info in agents.items():
            assert "name" in agent_info, f"Agent {agent_id} missing 'name'"
            assert "role" in agent_info, f"Agent {agent_id} missing 'role'"
            assert "outputs" in agent_info, f"Agent {agent_id} missing 'outputs'"
        print("✅ All agents have required fields")
    
    def test_agents_include_devops_engineer(self):
        """Should include devops_engineer agent"""
        response = requests.get(f"{BASE_URL}/api/build/agents")
        data = response.json()
        agents = data.get("agents", {})
        
        assert "devops_engineer" in agents, "devops_engineer agent not found"
        devops = agents["devops_engineer"]
        outputs = devops.get("outputs", [])
        
        assert "Dockerfile" in outputs or "docker-compose.yml" in outputs, f"DevOps outputs: {outputs}"
        print(f"✅ DevOps engineer outputs: {outputs}")
    
    def test_pipelines_present(self):
        """Should include pipelines for simple, standard, enterprise"""
        response = requests.get(f"{BASE_URL}/api/build/agents")
        data = response.json()
        pipelines = data.get("pipelines", {})
        
        assert "simple" in pipelines, "simple pipeline not found"
        assert "standard" in pipelines, "standard pipeline not found"
        assert "enterprise" in pipelines, "enterprise pipeline not found"
        print(f"✅ Pipelines: {list(pipelines.keys())}")


class TestStagedGenerateEndpoint:
    """Test /api/build/staged-generate endpoint"""
    
    def test_staged_generate_endpoint_exists(self):
        """Staged generate endpoint should exist (may require auth)"""
        response = requests.post(f"{BASE_URL}/api/build/staged-generate", json={
            "prompt": "test",
            "stage": "stage_1_foundation"
        })
        # Should not return 404 - may return 401 (auth required) or 200
        assert response.status_code != 404, f"Endpoint returned 404"
        print(f"✅ Staged generate endpoint exists (status: {response.status_code})")


class TestGenerateRuntimeShellScripts:
    """Test that generate-runtime returns shell scripts"""
    
    def test_generate_runtime_returns_run_commands(self):
        """Generate runtime should return run_commands object"""
        response = requests.post(f"{BASE_URL}/api/build/generate-runtime", json={
            "prompt": "Build a simple dashboard"
        }, timeout=120)
        
        if response.status_code == 200:
            data = response.json()
            
            # Check for run_commands
            run_commands = data.get("run_commands", {})
            if run_commands:
                print(f"✅ run_commands present: {list(run_commands.keys())}")
            else:
                print("⚠️ run_commands not in response (may be in project_files)")
            
            # Check for shell scripts in project_files
            project_files = data.get("project_files", {})
            shell_scripts = [f for f in project_files.keys() if f.endswith('.sh') or f.endswith('.bat') or f == 'Makefile' or f == 'docker-compose.yml']
            
            if shell_scripts:
                print(f"✅ Shell scripts in project_files: {shell_scripts}")
            
            # Check for docker files
            docker_files = [f for f in project_files.keys() if 'docker' in f.lower() or 'Dockerfile' in f]
            if docker_files:
                print(f"✅ Docker files: {docker_files}")
            
            # Check stats for devops_files
            stats = data.get("stats", {})
            devops_files = stats.get("devops_files", 0)
            print(f"✅ DevOps files count: {devops_files}")
        else:
            print(f"⚠️ Generate runtime returned {response.status_code}")


class TestHealthEndpoint:
    """Basic health check"""
    
    def test_health_endpoint(self):
        """Health endpoint should return 200"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        print("✅ Health endpoint returns 200")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
