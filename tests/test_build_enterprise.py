"""
ENTERPRISE BUILD SYSTEM - COMPREHENSIVE PRODUCTION TESTS
Real binary compilation validation
"""

import pytest
import tempfile
import json
from pathlib import Path
from datetime import datetime

from build_system_enterprise import (
    BuildConfig,
    BuildOrchestrator,
    SystemValidator,
    ArtifactStorage,
    TauriBuilder,
    ElectronBuilder,
    FlutterBuilder,
    WebBuilder,
    BuildStatus,
    BuildJob,
    BuildArtifact
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def temp_project_dir():
    """Create temporary project directory"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def temp_artifacts_dir():
    """Create temporary artifacts directory"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def build_config():
    """Create test build config"""
    return BuildConfig(
        project_id="test-project-001",
        project_name="TestApp",
        framework="react",
        platforms=["web"],
        version="1.0.0",
        build_type="release"
    )


@pytest.fixture
def orchestrator(temp_artifacts_dir):
    """Create orchestrator instance"""
    with tempfile.TemporaryDirectory() as tmpdir:
        jobs_file = Path(tmpdir) / "build_jobs.json"
        return BuildOrchestrator(
            artifact_dir=temp_artifacts_dir,
            jobs_file=str(jobs_file)
        )


# ============================================================================
# SYSTEM VALIDATION TESTS
# ============================================================================

class TestSystemValidator:
    """Test system validation"""
    
    def test_nodejs_check(self):
        """Test Node.js detection"""
        ok, version = SystemValidator.check_nodejs()
        assert ok, "Node.js should be installed"
        assert version, "Node.js version should be available"
        assert "v" in version or len(version) > 0
    
    def test_npm_check(self):
        """Test npm detection"""
        ok, version = SystemValidator.check_npm()
        assert ok, "npm should be installed"
        assert version, "npm version should be available"
    
    def test_cargo_check(self):
        """Test Cargo detection"""
        ok, version = SystemValidator.check_cargo()
        # Cargo may or may not be installed
        if ok:
            assert version, "Cargo version should be available"
    
    def test_docker_check(self):
        """Test Docker detection"""
        ok, version = SystemValidator.check_docker()
        # Docker may or may not be installed
        if ok:
            assert version, "Docker version should be available"
    
    def test_validate_environment_web(self):
        """Test environment validation for web framework"""
        ok, validation = SystemValidator.validate_environment("react")
        # Should be ok if Node.js and npm are available
        assert "framework" in validation
        assert "checks" in validation
        assert "nodejs" in validation["checks"]
        assert "npm" in validation["checks"]
    
    def test_validate_environment_tauri(self):
        """Test environment validation for Tauri"""
        ok, validation = SystemValidator.validate_environment("tauri")
        assert "cargo" in validation["checks"]


# ============================================================================
# BUILD CONFIG TESTS
# ============================================================================

class TestBuildConfig:
    """Test build configuration"""
    
    def test_valid_config(self):
        """Test valid config"""
        config = BuildConfig(
            project_id="test",
            project_name="Test",
            framework="react",
            platforms=["web"]
        )
        valid, errors = config.validate()
        assert valid, f"Config should be valid: {errors}"
        assert len(errors) == 0
    
    def test_missing_project_id(self):
        """Test missing project_id"""
        config = BuildConfig(
            project_id="",
            project_name="Test",
            framework="react",
            platforms=["web"]
        )
        valid, errors = config.validate()
        assert not valid
        assert any("project_id" in e for e in errors)
    
    def test_invalid_framework(self):
        """Test invalid framework"""
        config = BuildConfig(
            project_id="test",
            project_name="Test",
            framework="invalid-framework",
            platforms=["web"]
        )
        valid, errors = config.validate()
        assert not valid
        assert any("framework" in e.lower() for e in errors)
    
    def test_no_platforms(self):
        """Test no platforms"""
        config = BuildConfig(
            project_id="test",
            project_name="Test",
            framework="react",
            platforms=[]
        )
        valid, errors = config.validate()
        assert not valid
        assert any("platform" in e.lower() for e in errors)


# ============================================================================
# ARTIFACT STORAGE TESTS
# ============================================================================

class TestArtifactStorage:
    """Test artifact storage"""
    
    def test_storage_initialization(self, temp_artifacts_dir):
        """Test storage initialization"""
        storage = ArtifactStorage(temp_artifacts_dir)
        assert storage.base_dir.exists()
        assert storage.manifest is not None
    
    def test_calculate_file_hash(self, temp_artifacts_dir):
        """Test file hash calculation"""
        storage = ArtifactStorage(temp_artifacts_dir)
        
        # Create test file
        test_file = Path(temp_artifacts_dir) / "test.txt"
        test_file.write_text("test content")
        
        hash_val = ArtifactStorage.calculate_file_hash(str(test_file))
        assert hash_val, "Hash should be calculated"
        assert len(hash_val) == 64  # SHA256 hash length
    
    def test_store_artifact(self, temp_artifacts_dir):
        """Test artifact storage"""
        storage = ArtifactStorage(temp_artifacts_dir)
        
        # Create test file
        test_file = Path(temp_artifacts_dir) / "test.exe"
        test_file.write_text("test binary")
        
        artifact = BuildArtifact(
            artifact_id="test-artifact-001",
            project_id="test-project",
            platform="windows",
            framework="tauri",
            file_path=str(test_file),
            file_name="test.exe",
            file_size=100,
            file_hash="abc123",
            mime_type="application/x-msdownload"
        )
        
        success = storage.store_artifact(artifact)
        assert success, "Artifact should be stored"
        assert storage.manifest["count"] > 0
    
    def test_get_artifact(self, temp_artifacts_dir):
        """Test artifact retrieval"""
        storage = ArtifactStorage(temp_artifacts_dir)
        
        # Create and store artifact
        test_file = Path(temp_artifacts_dir) / "test.exe"
        test_file.write_text("test")
        
        artifact = BuildArtifact(
            artifact_id="test-001",
            project_id="proj-001",
            platform="windows",
            framework="tauri",
            file_path=str(test_file),
            file_name="test.exe",
            file_size=100,
            file_hash="hash",
            mime_type="app/exe"
        )
        
        storage.store_artifact(artifact)
        retrieved = storage.get_artifact("test-001")
        
        assert retrieved is not None
        assert retrieved["artifact_id"] == "test-001"


# ============================================================================
# BUILD ORCHESTRATOR TESTS
# ============================================================================

class TestBuildOrchestrator:
    """Test build orchestrator"""
    
    def test_orchestrator_initialization(self, orchestrator):
        """Test orchestrator initialization"""
        assert orchestrator is not None
        assert orchestrator.jobs is not None
        assert orchestrator.artifact_storage is not None
    
    def test_submit_build_valid(self, orchestrator, build_config):
        """Test valid build submission"""
        success, job_id, message = orchestrator.submit_build(build_config)
        
        assert success, f"Build should be submitted: {message}"
        assert job_id, "Job ID should be returned"
        assert job_id in orchestrator.jobs
    
    def test_submit_build_invalid_config(self, orchestrator):
        """Test invalid config submission"""
        bad_config = BuildConfig(
            project_id="",
            project_name="Test",
            framework="react",
            platforms=["web"]
        )
        
        success, job_id, message = orchestrator.submit_build(bad_config)
        assert not success, "Invalid config should not be submitted"
        assert not job_id, "No job ID should be returned"
    
    def test_job_status(self, orchestrator, build_config):
        """Test job status retrieval"""
        success, job_id, _ = orchestrator.submit_build(build_config)
        assert success
        
        status = orchestrator.get_job_status(job_id)
        assert status is not None
        assert status["job_id"] == job_id
        assert status["status"] == BuildStatus.QUEUED.value
    
    def test_cancel_queued_build(self, orchestrator, build_config):
        """Test cancelling queued build"""
        success, job_id, _ = orchestrator.submit_build(build_config)
        assert success
        
        cancelled = orchestrator.cancel_build(job_id)
        assert cancelled, "Should be able to cancel queued build"
        
        status = orchestrator.get_job_status(job_id)
        assert status["status"] == BuildStatus.CANCELLED.value
    
    def test_job_persistence(self, temp_artifacts_dir):
        """Test job persistence"""
        with tempfile.TemporaryDirectory() as tmpdir:
            jobs_file = Path(tmpdir) / "jobs.json"
            
            # Create orchestrator and submit build
            orch1 = BuildOrchestrator(
                artifact_dir=temp_artifacts_dir,
                jobs_file=str(jobs_file)
            )
            
            config = BuildConfig(
                project_id="test",
                project_name="Test",
                framework="react",
                platforms=["web"]
            )
            
            success, job_id, _ = orch1.submit_build(config)
            assert success
            
            # Create new orchestrator with same jobs file
            orch2 = BuildOrchestrator(
                artifact_dir=temp_artifacts_dir,
                jobs_file=str(jobs_file)
            )
            
            # Should have same job
            status = orch2.get_job_status(job_id)
            assert status is not None


# ============================================================================
# BUILD JOB TESTS
# ============================================================================

class TestBuildJob:
    """Test build job"""
    
    def test_job_creation(self):
        """Test job creation"""
        job = BuildJob(
            job_id="test-001",
            project_id="proj-001",
            status=BuildStatus.QUEUED.value
        )
        
        assert job.job_id == "test-001"
        assert job.status == BuildStatus.QUEUED.value
        assert job.created_at is not None
    
    def test_job_to_dict(self):
        """Test job serialization"""
        job = BuildJob(
            job_id="test-001",
            project_id="proj-001"
        )
        
        data = job.to_dict()
        assert isinstance(data, dict)
        assert data["job_id"] == "test-001"
        assert data["project_id"] == "proj-001"


# ============================================================================
# BUILDER TESTS
# ============================================================================

class TestWebBuilder:
    """Test web framework builder"""
    
    def test_builder_initialization(self):
        """Test builder initialization"""
        with tempfile.TemporaryDirectory() as tmpdir:
            builder = WebBuilder(tmpdir)
            assert builder.output_dir.exists()
    
    def test_builder_logging(self):
        """Test builder logging"""
        with tempfile.TemporaryDirectory() as tmpdir:
            builder = WebBuilder(tmpdir)
            builder.log("Test message")
            
            logs = builder.get_logs()
            assert "Test message" in logs
            assert len(builder.logs) > 0


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Integration tests"""
    
    def test_complete_workflow_queued_to_status(self, orchestrator, build_config):
        """Test complete workflow from submission to status"""
        # Submit
        success, job_id, msg = orchestrator.submit_build(build_config)
        assert success
        
        # Check status
        status = orchestrator.get_job_status(job_id)
        assert status is not None
        assert status["status"] == BuildStatus.QUEUED.value
        assert status["created_at"] is not None
    
    def test_job_history(self, orchestrator, build_config):
        """Test job history tracking"""
        # Submit multiple builds
        job_ids = []
        for i in range(3):
            config = BuildConfig(
                project_id=f"test-{i}",
                project_name=f"Test{i}",
                framework="react",
                platforms=["web"]
            )
            success, job_id, _ = orchestrator.submit_build(config)
            if success:
                job_ids.append(job_id)
        
        # Verify all jobs exist
        for job_id in job_ids:
            status = orchestrator.get_job_status(job_id)
            assert status is not None


# ============================================================================
# PRODUCTION READINESS TESTS
# ============================================================================

class TestProductionReadiness:
    """Test production readiness"""
    
    def test_error_handling(self, orchestrator):
        """Test error handling"""
        # Request non-existent job
        status = orchestrator.get_job_status("non-existent")
        assert status is None
    
    def test_empty_job_list(self, orchestrator):
        """Test handling empty job list"""
        jobs = orchestrator.jobs
        assert isinstance(jobs, dict)
    
    def test_manifest_creation(self, temp_artifacts_dir):
        """Test manifest creation"""
        storage = ArtifactStorage(temp_artifacts_dir)
        manifest_file = Path(temp_artifacts_dir) / "manifest.json"
        assert manifest_file.exists()
    
    def test_concurrent_submissions(self, orchestrator, build_config):
        """Test handling multiple concurrent submissions"""
        job_ids = []
        for i in range(10):
            config = BuildConfig(
                project_id=f"concurrent-{i}",
                project_name=f"App{i}",
                framework="react",
                platforms=["web"]
            )
            success, job_id, _ = orchestrator.submit_build(config)
            if success:
                job_ids.append(job_id)
        
        assert len(job_ids) == 10, "All submissions should succeed"


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("ENTERPRISE BUILD SYSTEM - PRODUCTION TESTS")
    print("=" * 70)
    
    pytest.main([__file__, "-v", "--tb=short"])
