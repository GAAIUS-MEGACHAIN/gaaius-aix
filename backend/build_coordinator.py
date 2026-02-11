"""
Build Coordinator - Orchestrates the entire build pipeline
Integrates with generators, build executor, and artifact manager
"""

import uuid
import json
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
import subprocess

from build_executor import BuildConfig, BuildExecutor, Platform, BuildType, BuildArtifact
from artifact_manager import ArtifactStorageManager, ArtifactDeliveryManager, ArtifactMetadata

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BuildStatus(Enum):
    """Build status"""
    QUEUED = "queued"
    INITIALIZING = "initializing"
    GENERATING = "generating"
    BUILDING = "building"
    SIGNING = "signing"
    STORING = "storing"
    COMPLETING = "completing"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class BuildRequest:
    """Request to build an application"""
    request_id: str
    project_id: str
    project_name: str
    description: str
    framework: str
    platforms: List[Platform]
    build_type: BuildType
    version: str
    output_dir: str
    created_at: str
    created_by: str = "system"


@dataclass
class BuildJob:
    """Represents a build job"""
    job_id: str
    request: BuildRequest
    status: BuildStatus
    progress: int  # 0-100
    started_at: Optional[str]
    completed_at: Optional[str]
    artifacts: List[BuildArtifact]
    error_message: Optional[str]
    logs: str


class BuildCoordinator:
    """Orchestrates the complete build pipeline"""
    
    def __init__(
        self,
        project_root: str = "./",
        artifacts_root: str = "./artifacts",
        max_concurrent_builds: int = 3
    ):
        self.project_root = Path(project_root)
        self.artifacts_root = Path(artifacts_root)
        self.max_concurrent_builds = max_concurrent_builds
        
        # Initialize managers
        self.executor = BuildExecutor()
        self.storage = ArtifactStorageManager(str(artifacts_root))
        self.delivery = ArtifactDeliveryManager(self.storage)
        
        # Build tracking
        self.active_builds: Dict[str, BuildJob] = {}
        self.build_history: List[BuildJob] = []
    
    def submit_build_request(
        self,
        project_id: str,
        project_name: str,
        framework: str,
        platforms: List[str],
        version: str = "1.0.0",
        build_type: str = "release",
        description: str = "",
        output_dir: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Submit a new build request
        Returns: (success, request_id_or_error)
        """
        
        # Check concurrent builds
        if len(self.active_builds) >= self.max_concurrent_builds:
            return False, "Build queue is full. Maximum concurrent builds reached."
        
        try:
            # Validate inputs
            platform_enums = []
            for p in platforms:
                try:
                    platform_enums.append(Platform(p.lower()))
                except ValueError:
                    return False, f"Invalid platform: {p}"
            
            try:
                build_type_enum = BuildType(build_type.lower())
            except ValueError:
                return False, f"Invalid build type: {build_type}"
            
            # Create request
            request_id = str(uuid.uuid4())
            request = BuildRequest(
                request_id=request_id,
                project_id=project_id,
                project_name=project_name,
                description=description,
                framework=framework,
                platforms=platform_enums,
                build_type=build_type_enum,
                version=version,
                output_dir=output_dir or f"./builds/{project_id}",
                created_at=datetime.now().isoformat()
            )
            
            # Create job
            job = BuildJob(
                job_id=str(uuid.uuid4()),
                request=request,
                status=BuildStatus.QUEUED,
                progress=0,
                started_at=None,
                completed_at=None,
                artifacts=[],
                error_message=None,
                logs=""
            )
            
            self.active_builds[job.job_id] = job
            logger.info(f"✅ Build request submitted: {request_id}")
            
            return True, job.job_id
            
        except Exception as e:
            logger.error(f"Failed to submit build request: {e}")
            return False, str(e)
    
    def execute_build(self, job_id: str) -> bool:
        """Execute a queued build job"""
        
        if job_id not in self.active_builds:
            logger.error(f"Build job not found: {job_id}")
            return False
        
        job = self.active_builds[job_id]
        request = job.request
        
        try:
            job.status = BuildStatus.INITIALIZING
            job.started_at = datetime.now().isoformat()
            job.logs += f"\n{'='*70}\n"
            job.logs += f"🚀 Starting build: {request.project_name} v{request.version}\n"
            job.logs += f"{'='*70}\n"
            job.progress = 5
            
            # Step 1: Validate project directory
            job.status = BuildStatus.INITIALIZING
            project_path = self.project_root / request.output_dir
            
            if not project_path.exists():
                raise Exception(f"Project path not found: {project_path}")
            
            job.logs += f"\n✅ Project found at: {project_path}\n"
            job.progress = 10
            
            # Step 2: Build for each platform
            job.status = BuildStatus.BUILDING
            successful_builds = 0
            failed_platforms = []
            
            for platform in request.platforms:
                try:
                    job.logs += f"\n{'='*70}\n"
                    job.logs += f"🔨 Building for {platform.value}...\n"
                    job.logs += f"{'='*70}\n"
                    job.progress = 20 + (successful_builds * 50 // len(request.platforms))
                    
                    # Create build config
                    config = BuildConfig(
                        project_id=request.project_id,
                        project_name=request.project_name,
                        platform=platform,
                        build_type=request.build_type,
                        framework=request.framework,
                        version=request.version,
                        output_dir=str(project_path)
                    )
                    
                    # Execute build
                    success, artifact, error = self.executor.execute_build(config, str(project_path))
                    
                    if success and artifact:
                        job.artifacts.append(artifact)
                        successful_builds += 1
                        job.logs += f"✅ {platform.value} build successful\n"
                        job.logs += f"   Artifact: {artifact.file_name}\n"
                        job.logs += f"   Size: {artifact.file_size / (1024*1024):.2f} MB\n"
                    else:
                        failed_platforms.append((platform.value, error or "Unknown error"))
                        job.logs += f"❌ {platform.value} build failed: {error}\n"
                
                except Exception as e:
                    failed_platforms.append((platform.value, str(e)))
                    job.logs += f"❌ {platform.value} build error: {str(e)}\n"
            
            # Step 3: Store artifacts
            job.status = BuildStatus.STORING
            job.progress = 75
            
            stored_artifacts = []
            for artifact in job.artifacts:
                try:
                    job.logs += f"\n📦 Storing artifact: {artifact.file_name}\n"
                    
                    # Create metadata
                    metadata = ArtifactMetadata(
                        artifact_id=artifact.artifact_id,
                        project_id=request.project_id,
                        platform=artifact.platform.value,
                        framework=request.framework,
                        version=request.version,
                        file_name=artifact.file_name,
                        file_size=artifact.file_size,
                        file_path=artifact.file_path,
                        checksum=artifact.checksum,
                        mime_type=artifact.mime_type,
                        created_at=artifact.created_at,
                        expires_at=None
                    )
                    
                    # Store artifact
                    success, message = self.storage.store_artifact(
                        artifact.file_path,
                        metadata,
                        auto_cleanup=True
                    )
                    
                    if success:
                        stored_artifacts.append(metadata)
                        job.logs += f"✅ Artifact stored: {message}\n"
                    else:
                        job.logs += f"⚠️  Failed to store artifact: {message}\n"
                
                except Exception as e:
                    job.logs += f"⚠️  Error storing artifact: {str(e)}\n"
            
            # Step 4: Finalize
            job.status = BuildStatus.COMPLETING
            job.progress = 90
            
            job.logs += f"\n{'='*70}\n"
            job.logs += f"📊 Build Summary\n"
            job.logs += f"{'='*70}\n"
            job.logs += f"Total artifacts: {len(job.artifacts)}\n"
            job.logs += f"Successfully stored: {len(stored_artifacts)}\n"
            
            if failed_platforms:
                job.logs += f"\nFailed platforms:\n"
                for platform, error in failed_platforms:
                    job.logs += f"  - {platform}: {error}\n"
            
            # Determine final status
            if job.artifacts:
                job.status = BuildStatus.SUCCESS
                job.progress = 100
                job.logs += f"\n✅ Build completed successfully!\n"
            else:
                job.status = BuildStatus.FAILED
                job.error_message = "No artifacts generated"
                job.logs += f"\n❌ Build failed - no artifacts generated\n"
            
            job.completed_at = datetime.now().isoformat()
            
            # Move to history
            self.build_history.append(job)
            del self.active_builds[job_id]
            
            logger.info(f"✅ Build completed: {job_id}")
            return job.status == BuildStatus.SUCCESS
            
        except Exception as e:
            job.status = BuildStatus.FAILED
            job.error_message = str(e)
            job.logs += f"\n❌ Build failed: {str(e)}\n"
            job.completed_at = datetime.now().isoformat()
            
            logger.error(f"Build execution failed: {e}")
            
            # Move to history
            self.build_history.append(job)
            del self.active_builds[job_id]
            
            return False
    
    def get_build_status(self, job_id: str) -> Optional[Dict]:
        """Get status of a build job"""
        
        # Check active builds
        if job_id in self.active_builds:
            job = self.active_builds[job_id]
        else:
            # Check history
            job = next((j for j in self.build_history if j.job_id == job_id), None)
            if not job:
                return None
        
        return {
            "job_id": job.job_id,
            "request_id": job.request.request_id,
            "project_id": job.request.project_id,
            "project_name": job.request.project_name,
            "status": job.status.value,
            "progress": job.progress,
            "framework": job.request.framework,
            "version": job.request.version,
            "platforms": [p.value for p in job.request.platforms],
            "started_at": job.started_at,
            "completed_at": job.completed_at,
            "artifacts_count": len(job.artifacts),
            "artifacts": [
                {
                    "id": a.artifact_id,
                    "name": a.file_name,
                    "platform": a.platform.value,
                    "size_mb": round(a.file_size / (1024*1024), 2),
                    "checksum": a.checksum
                }
                for a in job.artifacts
            ],
            "error": job.error_message,
            "is_active": job_id in self.active_builds
        }
    
    def cancel_build(self, job_id: str) -> bool:
        """Cancel a queued or running build"""
        if job_id not in self.active_builds:
            return False
        
        job = self.active_builds[job_id]
        job.status = BuildStatus.CANCELLED
        job.completed_at = datetime.now().isoformat()
        
        self.build_history.append(job)
        del self.active_builds[job_id]
        
        logger.info(f"Build cancelled: {job_id}")
        return True
    
    def get_build_logs(self, job_id: str) -> Optional[str]:
        """Get complete logs for a build"""
        if job_id in self.active_builds:
            return self.active_builds[job_id].logs
        
        job = next((j for j in self.build_history if j.job_id == job_id), None)
        return job.logs if job else None
    
    def get_active_builds(self) -> List[Dict]:
        """Get all active builds"""
        return [
            {
                "job_id": job.job_id,
                "project_name": job.request.project_name,
                "status": job.status.value,
                "progress": job.progress,
                "started_at": job.started_at
            }
            for job in self.active_builds.values()
        ]
    
    def get_build_history(self, limit: int = 50) -> List[Dict]:
        """Get build history"""
        return [
            {
                "job_id": job.job_id,
                "project_name": job.request.project_name,
                "status": job.status.value,
                "completed_at": job.completed_at,
                "artifacts_count": len(job.artifacts)
            }
            for job in sorted(self.build_history, key=lambda x: x.completed_at, reverse=True)[:limit]
        ]
    
    def deliver_artifact(
        self,
        artifact_id: str,
        delivery_method: str = "local",
        config: Dict = None
    ) -> Tuple[bool, str]:
        """
        Deliver an artifact using specified method
        Returns: (success, delivery_url_or_error)
        """
        return self.delivery.deliver_artifact(artifact_id, delivery_method, config or {})
    
    def export_build_manifest(self, job_id: str, output_file: str) -> bool:
        """Export build manifest"""
        job = None
        
        if job_id in self.active_builds:
            job = self.active_builds[job_id]
        else:
            job = next((j for j in self.build_history if j.job_id == job_id), None)
        
        if not job:
            return False
        
        try:
            manifest = {
                "job_id": job.job_id,
                "project_id": job.request.project_id,
                "project_name": job.request.project_name,
                "status": job.status.value,
                "framework": job.request.framework,
                "version": job.request.version,
                "started_at": job.started_at,
                "completed_at": job.completed_at,
                "artifacts": [
                    {
                        "id": a.artifact_id,
                        "name": a.file_name,
                        "platform": a.platform.value,
                        "size_mb": round(a.file_size / (1024*1024), 2),
                        "checksum": a.checksum,
                        "mime_type": a.mime_type
                    }
                    for a in job.artifacts
                ],
                "exported_at": datetime.now().isoformat()
            }
            
            with open(output_file, 'w') as f:
                json.dump(manifest, f, indent=2)
            
            logger.info(f"Manifest exported: {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export manifest: {e}")
            return False


if __name__ == "__main__":
    # Example usage
    coordinator = BuildCoordinator()
    
    # Submit build request
    success, job_id = coordinator.submit_build_request(
        project_id="my-app",
        project_name="My App",
        framework="tauri",
        platforms=["windows", "macos", "linux"],
        version="1.0.0"
    )
    
    if success:
        print(f"✅ Build submitted: {job_id}")
        
        # Execute build
        # coordinator.execute_build(job_id)
        
        # Get status
        status = coordinator.get_build_status(job_id)
        print(json.dumps(status, indent=2))
    else:
        print(f"❌ Build submission failed: {job_id}")
