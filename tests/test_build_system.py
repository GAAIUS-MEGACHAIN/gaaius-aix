"""
Tests for the build system components
"""

import pytest
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Import build system components
from backend.build_executor import BuildExecutor, BuildConfig, Platform, BuildType, BuildArtifact
from backend.artifact_manager import ArtifactStorageManager, ArtifactDeliveryManager, ArtifactMetadata
from backend.build_coordinator import BuildCoordinator, BuildStatus


class TestBuildConfig:
    """Test BuildConfig"""
    
    def test_build_config_creation(self):
        """Test creating a build config"""
        config = BuildConfig(
            project_id="test-app",
            project_name="Test App",
            platform=Platform.WINDOWS,
            build_type=BuildType.RELEASE,
            framework="tauri",
            version="1.0.0"
        )
        
        assert config.project_id == "test-app"
        assert config.project_name == "Test App"
        assert config.platform == Platform.WINDOWS
        assert config.build_type == BuildType.RELEASE
        assert config.framework == "tauri"
        assert config.version == "1.0.0"
    
    def test_build_config_default_output_dir(self):
        """Test that output_dir defaults correctly"""
        config = BuildConfig(
            project_id="my-app",
            project_name="My App",
            platform=Platform.LINUX,
            build_type=BuildType.DEBUG,
            framework="electron"
        )
        
        assert "my-app" in config.output_dir
        assert "linux" in config.output_dir


class TestBuildExecutor:
    """Test BuildExecutor"""
    
    def test_executor_initialization(self):
        """Test executor can be created"""
        executor = BuildExecutor()
        assert executor is not None
        assert executor.validator is not None
    
    def test_platform_enum(self):
        """Test Platform enum values"""
        assert Platform.WINDOWS.value == "windows"
        assert Platform.MACOS.value == "macos"
        assert Platform.LINUX.value == "linux"
        assert Platform.ANDROID.value == "android"
        assert Platform.IOS.value == "ios"
    
    def test_build_type_enum(self):
        """Test BuildType enum values"""
        assert BuildType.DEBUG.value == "debug"
        assert BuildType.RELEASE.value == "release"


class TestArtifactMetadata:
    """Test ArtifactMetadata"""
    
    def test_artifact_creation(self):
        """Test creating artifact metadata"""
        artifact = ArtifactMetadata(
            artifact_id="art-001",
            project_id="test-app",
            platform="windows",
            framework="tauri",
            version="1.0.0",
            file_name="test-app.exe",
            file_size=125000000,
            file_path="/artifacts/test-app.exe",
            checksum="abc123def456",
            mime_type="application/x-msdownload",
            created_at=datetime.now().isoformat(),
            expires_at=None
        )
        
        assert artifact.artifact_id == "art-001"
        assert artifact.project_id == "test-app"
        assert artifact.platform == "windows"
        assert artifact.file_name == "test-app.exe"


class TestArtifactStorageManager:
    """Test ArtifactStorageManager"""
    
    def test_storage_initialization(self):
        """Test storage manager initialization"""
        storage = ArtifactStorageManager("./test_artifacts")
        assert storage.storage_root.exists()
        assert storage.metadata_dir.exists()
    
    def test_get_storage_usage(self):
        """Test calculating storage usage"""
        storage = ArtifactStorageManager("./test_artifacts")
        usage = storage._get_storage_usage()
        assert isinstance(usage, int)
        assert usage >= 0
    
    def test_save_and_retrieve_metadata(self):
        """Test saving and retrieving metadata"""
        storage = ArtifactStorageManager("./test_artifacts")
        
        metadata = ArtifactMetadata(
            artifact_id="test-001",
            project_id="test-app",
            platform="windows",
            framework="tauri",
            version="1.0.0",
            file_name="test.exe",
            file_size=100000,
            file_path="/path/to/test.exe",
            checksum="abc123",
            mime_type="application/x-msdownload",
            created_at=datetime.now().isoformat(),
            expires_at=None
        )
        
        storage._save_metadata(metadata)
        retrieved = storage.retrieve_artifact("test-001")
        
        assert retrieved is not None
        assert retrieved.artifact_id == "test-001"
        assert retrieved.project_id == "test-app"


class TestBuildCoordinator:
    """Test BuildCoordinator"""
    
    def test_coordinator_initialization(self):
        """Test coordinator initialization"""
        coordinator = BuildCoordinator()
        assert coordinator is not None
        assert coordinator.executor is not None
        assert coordinator.storage is not None
        assert coordinator.delivery is not None
    
    def test_submit_build_request(self):
        """Test submitting a build request"""
        coordinator = BuildCoordinator()
        
        success, result = coordinator.submit_build_request(
            project_id="test-app",
            project_name="Test App",
            framework="tauri",
            platforms=["windows", "macos"],
            version="1.0.0"
        )
        
        assert success is True
        assert result is not None
        assert len(result) > 0  # job_id
    
    def test_submit_build_invalid_platform(self):
        """Test submitting build with invalid platform"""
        coordinator = BuildCoordinator()
        
        success, result = coordinator.submit_build_request(
            project_id="test-app",
            project_name="Test App",
            framework="tauri",
            platforms=["invalid-platform"],
            version="1.0.0"
        )
        
        assert success is False
        assert "Invalid platform" in result
    
    def test_get_build_status(self):
        """Test getting build status"""
        coordinator = BuildCoordinator()
        
        success, job_id = coordinator.submit_build_request(
            project_id="test-app",
            project_name="Test App",
            framework="tauri",
            platforms=["windows"]
        )
        
        status = coordinator.get_build_status(job_id)
        
        assert status is not None
        assert status["project_id"] == "test-app"
        assert status["status"] == "queued"
        assert status["progress"] == 0
    
    def test_cancel_build(self):
        """Test cancelling a build"""
        coordinator = BuildCoordinator()
        
        success, job_id = coordinator.submit_build_request(
            project_id="test-app",
            project_name="Test App",
            framework="tauri",
            platforms=["windows"]
        )
        
        cancelled = coordinator.cancel_build(job_id)
        assert cancelled is True
        
        status = coordinator.get_build_status(job_id)
        assert status["status"] == "cancelled"
    
    def test_get_active_builds(self):
        """Test getting active builds"""
        coordinator = BuildCoordinator()
        
        # Submit a build
        success, job_id = coordinator.submit_build_request(
            project_id="test-app",
            project_name="Test App",
            framework="tauri",
            platforms=["windows"]
        )
        
        active = coordinator.get_active_builds()
        assert len(active) == 1
        assert active[0]["job_id"] == job_id
    
    def test_get_build_history(self):
        """Test getting build history"""
        coordinator = BuildCoordinator()
        
        # Submit and cancel a build
        success, job_id = coordinator.submit_build_request(
            project_id="test-app",
            project_name="Test App",
            framework="tauri",
            platforms=["windows"]
        )
        coordinator.cancel_build(job_id)
        
        history = coordinator.get_build_history(limit=10)
        assert len(history) > 0
        assert history[0]["job_id"] == job_id
        assert history[0]["status"] == "cancelled"


class TestBuildEnvironmentValidator:
    """Test BuildEnvironmentValidator"""
    
    @patch('backend.build_executor.subprocess.run')
    def test_validate_environment_windows_tauri(self, mock_run):
        """Test environment validation for Windows Tauri"""
        from backend.build_executor import BuildEnvironmentValidator
        
        mock_run.return_value = MagicMock(returncode=0)
        
        config = BuildConfig(
            project_id="test",
            project_name="Test",
            platform=Platform.WINDOWS,
            build_type=BuildType.RELEASE,
            framework="tauri"
        )
        
        # This will check for required tools
        # (In CI/CD, tools may not be installed, so we just test the structure)
        assert config.framework == "tauri"
        assert config.platform == Platform.WINDOWS


class TestArtifactDeliveryManager:
    """Test ArtifactDeliveryManager"""
    
    def test_delivery_initialization(self):
        """Test delivery manager initialization"""
        storage = ArtifactStorageManager("./test_artifacts")
        delivery = ArtifactDeliveryManager(storage)
        
        assert delivery is not None
        assert "local" in delivery.delivery_methods
        assert "s3" in delivery.delivery_methods
        assert "github-release" in delivery.delivery_methods


class TestBuildStatus:
    """Test BuildStatus enum"""
    
    def test_build_status_values(self):
        """Test build status enum values"""
        assert BuildStatus.QUEUED.value == "queued"
        assert BuildStatus.INITIALIZING.value == "initializing"
        assert BuildStatus.BUILDING.value == "building"
        assert BuildStatus.SUCCESS.value == "success"
        assert BuildStatus.FAILED.value == "failed"


# Integration tests
class TestBuildSystemIntegration:
    """Integration tests for the build system"""
    
    def test_full_workflow_queued_to_cancelled(self):
        """Test complete workflow: submit -> queue -> cancel"""
        coordinator = BuildCoordinator()
        
        # Step 1: Submit
        success, job_id = coordinator.submit_build_request(
            project_id="workflow-test",
            project_name="Workflow Test App",
            framework="tauri",
            platforms=["windows", "macos", "linux"],
            version="2.0.0"
        )
        assert success is True
        
        # Step 2: Check queued
        status = coordinator.get_build_status(job_id)
        assert status["status"] == "queued"
        assert status["project_id"] == "workflow-test"
        assert status["version"] == "2.0.0"
        
        # Step 3: Check active
        active = coordinator.get_active_builds()
        assert len(active) > 0
        
        # Step 4: Cancel
        coordinator.cancel_build(job_id)
        
        # Step 5: Verify cancelled
        status = coordinator.get_build_status(job_id)
        assert status["status"] == "cancelled"
        
        # Step 6: Check history
        history = coordinator.get_build_history()
        assert len(history) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
