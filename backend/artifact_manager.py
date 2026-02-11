"""
Artifact Manager - Handles storage, delivery, and lifecycle of build artifacts
"""

import os
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import hashlib
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ArtifactMetadata:
    """Metadata for a stored artifact"""
    artifact_id: str
    project_id: str
    platform: str
    framework: str
    version: str
    file_name: str
    file_size: int
    file_path: str
    checksum: str
    mime_type: str
    created_at: str
    expires_at: Optional[str]
    download_count: int = 0
    download_token: Optional[str] = None


class ArtifactStorageManager:
    """Manages artifact storage on disk"""
    
    def __init__(self, storage_root: str = "./artifacts", max_storage_gb: float = 100.0):
        self.storage_root = Path(storage_root)
        self.storage_root.mkdir(exist_ok=True)
        self.metadata_dir = self.storage_root / "metadata"
        self.metadata_dir.mkdir(exist_ok=True)
        self.max_storage_bytes = max_storage_gb * 1024 * 1024 * 1024
        self.retention_days = 30  # Default artifact retention
    
    def store_artifact(
        self,
        artifact_path: str,
        metadata: ArtifactMetadata,
        auto_cleanup: bool = True
    ) -> Tuple[bool, str]:
        """
        Store an artifact and its metadata
        Returns: (success, storage_path)
        """
        try:
            artifact_path = Path(artifact_path)
            
            # Check if we need to cleanup old artifacts
            if auto_cleanup:
                self._cleanup_old_artifacts()
            
            # Check storage quota
            current_usage = self._get_storage_usage()
            if current_usage + artifact_path.stat().st_size > self.max_storage_bytes:
                return False, "Storage quota exceeded"
            
            # Create project directory
            project_dir = self.storage_root / metadata.project_id
            project_dir.mkdir(exist_ok=True)
            
            # Create platform directory
            platform_dir = project_dir / metadata.platform
            platform_dir.mkdir(exist_ok=True)
            
            # Copy artifact
            dest_path = platform_dir / metadata.file_name
            
            if artifact_path.is_file():
                shutil.copy2(artifact_path, dest_path)
            elif artifact_path.is_dir():
                # Archive directory
                archive_path = platform_dir / metadata.file_name.replace('.zip', '')
                shutil.make_archive(str(archive_path), 'zip', artifact_path)
                dest_path = archive_path.with_suffix('.zip')
            else:
                return False, "Artifact path is not a file or directory"
            
            # Store metadata
            metadata.file_path = str(dest_path)
            self._save_metadata(metadata)
            
            logger.info(f"✅ Artifact stored: {dest_path}")
            return True, str(dest_path)
            
        except Exception as e:
            logger.error(f"❌ Failed to store artifact: {str(e)}")
            return False, str(e)
    
    def retrieve_artifact(self, artifact_id: str) -> Optional[ArtifactMetadata]:
        """Retrieve artifact metadata by ID"""
        metadata_file = self.metadata_dir / f"{artifact_id}.json"
        
        if not metadata_file.exists():
            return None
        
        try:
            with open(metadata_file, 'r') as f:
                data = json.load(f)
                return ArtifactMetadata(**data)
        except Exception as e:
            logger.error(f"Failed to retrieve artifact metadata: {e}")
            return None
    
    def list_project_artifacts(self, project_id: str) -> List[ArtifactMetadata]:
        """List all artifacts for a project"""
        artifacts = []
        
        for metadata_file in self.metadata_dir.glob("*.json"):
            try:
                with open(metadata_file, 'r') as f:
                    data = json.load(f)
                    if data.get('project_id') == project_id:
                        artifacts.append(ArtifactMetadata(**data))
            except Exception as e:
                logger.debug(f"Failed to read metadata file {metadata_file}: {e}")
        
        return sorted(artifacts, key=lambda x: x.created_at, reverse=True)
    
    def download_artifact(self, artifact_id: str) -> Tuple[Optional[str], str]:
        """
        Increment download count and return artifact path
        Returns: (artifact_path, download_token)
        """
        metadata = self.retrieve_artifact(artifact_id)
        
        if not metadata:
            return None, "Artifact not found"
        
        # Check if artifact has expired
        if metadata.expires_at:
            if datetime.fromisoformat(metadata.expires_at) < datetime.now():
                return None, "Artifact has expired"
        
        # Increment download count
        metadata.download_count += 1
        self._save_metadata(metadata)
        
        logger.info(f"📥 Artifact downloaded: {artifact_id} (count: {metadata.download_count})")
        
        return metadata.file_path, metadata.download_token or ""
    
    def delete_artifact(self, artifact_id: str) -> bool:
        """Delete an artifact and its metadata"""
        metadata = self.retrieve_artifact(artifact_id)
        
        if not metadata:
            return False
        
        try:
            # Delete file
            artifact_path = Path(metadata.file_path)
            if artifact_path.exists():
                if artifact_path.is_file():
                    artifact_path.unlink()
                elif artifact_path.is_dir():
                    shutil.rmtree(artifact_path)
            
            # Delete metadata
            metadata_file = self.metadata_dir / f"{artifact_id}.json"
            if metadata_file.exists():
                metadata_file.unlink()
            
            logger.info(f"✅ Artifact deleted: {artifact_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete artifact: {e}")
            return False
    
    def _cleanup_old_artifacts(self):
        """Remove artifacts older than retention period"""
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        deleted_count = 0
        
        for metadata_file in self.metadata_dir.glob("*.json"):
            try:
                with open(metadata_file, 'r') as f:
                    data = json.load(f)
                    created_at = datetime.fromisoformat(data['created_at'])
                    
                    if created_at < cutoff_date:
                        artifact_id = data['artifact_id']
                        self.delete_artifact(artifact_id)
                        deleted_count += 1
            except Exception as e:
                logger.debug(f"Error during cleanup: {e}")
        
        if deleted_count > 0:
            logger.info(f"🧹 Cleaned up {deleted_count} old artifacts")
    
    def _get_storage_usage(self) -> int:
        """Calculate total storage usage in bytes"""
        total_size = 0
        
        for root, dirs, files in os.walk(self.storage_root / 'metadata'):
            for file in files:
                if file.endswith('.json'):
                    file_path = Path(root) / file
                    try:
                        with open(file_path, 'r') as f:
                            data = json.load(f)
                            total_size += data.get('file_size', 0)
                    except Exception:
                        pass
        
        return total_size
    
    def _save_metadata(self, metadata: ArtifactMetadata):
        """Save artifact metadata to JSON file"""
        metadata_file = self.metadata_dir / f"{metadata.artifact_id}.json"
        
        with open(metadata_file, 'w') as f:
            json.dump(asdict(metadata), f, indent=2)


class ArtifactDeliveryManager:
    """Handles artifact delivery and distribution"""
    
    def __init__(self, storage_manager: ArtifactStorageManager):
        self.storage = storage_manager
        self.delivery_methods = {
            "local": self._deliver_local,
            "s3": self._deliver_s3,
            "github-release": self._deliver_github_release,
            "docker": self._deliver_docker,
        }
    
    def deliver_artifact(
        self,
        artifact_id: str,
        method: str = "local",
        config: Dict = None
    ) -> Tuple[bool, str]:
        """
        Deliver artifact using specified method
        Returns: (success, delivery_url_or_error)
        """
        metadata = self.storage.retrieve_artifact(artifact_id)
        
        if not metadata:
            return False, "Artifact not found"
        
        if method not in self.delivery_methods:
            return False, f"Unknown delivery method: {method}"
        
        try:
            delivery_fn = self.delivery_methods[method]
            result = delivery_fn(metadata, config or {})
            return result
        except Exception as e:
            logger.error(f"Delivery failed: {e}")
            return False, str(e)
    
    def _deliver_local(self, metadata: ArtifactMetadata, config: Dict) -> Tuple[bool, str]:
        """Deliver from local storage (for development)"""
        # Generate download token
        token = hashlib.sha256(
            f"{metadata.artifact_id}-{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]
        
        metadata.download_token = token
        self.storage._save_metadata(metadata)
        
        download_url = f"/api/artifacts/download/{metadata.artifact_id}?token={token}"
        logger.info(f"📦 Local delivery ready: {download_url}")
        return True, download_url
    
    def _deliver_s3(self, metadata: ArtifactMetadata, config: Dict) -> Tuple[bool, str]:
        """Deliver to AWS S3"""
        try:
            import boto3
            
            bucket = config.get('bucket', 'gaaius-artifacts')
            region = config.get('region', 'us-east-1')
            
            s3_client = boto3.client('s3', region_name=region)
            
            artifact_path = Path(metadata.file_path)
            if not artifact_path.exists():
                return False, "Artifact file not found"
            
            # Upload to S3
            s3_key = f"{metadata.project_id}/{metadata.platform}/{metadata.file_name}"
            s3_client.upload_file(str(artifact_path), bucket, s3_key)
            
            # Generate public URL
            s3_url = f"https://{bucket}.s3.{region}.amazonaws.com/{s3_key}"
            logger.info(f"☁️  Artifact uploaded to S3: {s3_url}")
            
            return True, s3_url
            
        except ImportError:
            return False, "boto3 not installed"
        except Exception as e:
            return False, str(e)
    
    def _deliver_github_release(self, metadata: ArtifactMetadata, config: Dict) -> Tuple[bool, str]:
        """Deliver to GitHub Release"""
        try:
            import requests
            
            owner = config.get('owner')
            repo = config.get('repo')
            github_token = config.get('token')
            
            if not all([owner, repo, github_token]):
                return False, "Missing GitHub configuration"
            
            artifact_path = Path(metadata.file_path)
            if not artifact_path.exists():
                return False, "Artifact file not found"
            
            # Create or get release
            release_tag = f"v{metadata.version}"
            api_url = f"https://api.github.com/repos/{owner}/{repo}/releases"
            
            headers = {
                "Authorization": f"token {github_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            # Check if release exists
            response = requests.get(f"{api_url}/tags/{release_tag}", headers=headers)
            
            if response.status_code == 404:
                # Create release
                release_data = {
                    "tag_name": release_tag,
                    "name": f"Release {metadata.version}",
                    "draft": False,
                    "prerelease": False
                }
                response = requests.post(api_url, json=release_data, headers=headers)
            
            if response.status_code not in [200, 201]:
                return False, f"GitHub API error: {response.status_code}"
            
            release_id = response.json()['id']
            
            # Upload asset
            upload_url = f"{api_url}/{release_id}/assets"
            headers['Content-Type'] = metadata.mime_type
            
            with open(artifact_path, 'rb') as f:
                response = requests.post(
                    f"{upload_url}?name={metadata.file_name}",
                    data=f,
                    headers=headers
                )
            
            if response.status_code not in [200, 201]:
                return False, f"Asset upload failed: {response.status_code}"
            
            asset_url = response.json()['browser_download_url']
            logger.info(f"🚀 Artifact released to GitHub: {asset_url}")
            
            return True, asset_url
            
        except ImportError:
            return False, "requests library not installed"
        except Exception as e:
            return False, str(e)
    
    def _deliver_docker(self, metadata: ArtifactMetadata, config: Dict) -> Tuple[bool, str]:
        """Deliver as Docker image to registry"""
        try:
            import docker
            
            registry = config.get('registry', 'docker.io')
            username = config.get('username')
            token = config.get('token')
            
            if not username:
                return False, "Docker username required"
            
            artifact_path = Path(metadata.file_path)
            if not artifact_path.exists():
                return False, "Artifact file not found"
            
            client = docker.from_env()
            
            # Build image tag
            image_tag = f"{registry}/{username}/{metadata.project_id}:{metadata.version}"
            
            logger.info(f"🐳 Building Docker image: {image_tag}")
            
            # This assumes a Dockerfile exists in artifact directory
            image, build_logs = client.images.build(
                path=str(artifact_path),
                tag=image_tag,
                rm=True
            )
            
            # Push to registry
            logger.info(f"📤 Pushing to {registry}...")
            push_logs = client.images.push(image_tag)
            
            logger.info(f"✅ Docker image pushed: {image_tag}")
            return True, image_tag
            
        except ImportError:
            return False, "docker library not installed"
        except Exception as e:
            return False, str(e)


class ArtifactAnalyzer:
    """Analyze and report on artifacts"""
    
    def __init__(self, storage_manager: ArtifactStorageManager):
        self.storage = storage_manager
    
    def get_project_statistics(self, project_id: str) -> Dict:
        """Get statistics for a project's artifacts"""
        artifacts = self.storage.list_project_artifacts(project_id)
        
        if not artifacts:
            return {
                "project_id": project_id,
                "total_artifacts": 0,
                "total_size_mb": 0,
                "platforms": [],
                "frameworks": [],
                "versions": []
            }
        
        total_size = sum(a.file_size for a in artifacts)
        platforms = list(set(a.platform for a in artifacts))
        frameworks = list(set(a.framework for a in artifacts))
        versions = list(set(a.version for a in artifacts))
        total_downloads = sum(a.download_count for a in artifacts)
        
        return {
            "project_id": project_id,
            "total_artifacts": len(artifacts),
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "total_downloads": total_downloads,
            "platforms": platforms,
            "frameworks": frameworks,
            "versions": versions,
            "latest_artifact": {
                "id": artifacts[0].artifact_id,
                "created_at": artifacts[0].created_at,
                "file_name": artifacts[0].file_name,
                "file_size_mb": round(artifacts[0].file_size / (1024 * 1024), 2)
            }
        }
    
    def export_manifest(self, project_id: str, output_file: str) -> bool:
        """Export project artifacts manifest"""
        try:
            artifacts = self.storage.list_project_artifacts(project_id)
            
            manifest = {
                "project_id": project_id,
                "exported_at": datetime.now().isoformat(),
                "artifacts": [
                    {
                        "id": a.artifact_id,
                        "platform": a.platform,
                        "framework": a.framework,
                        "version": a.version,
                        "file_name": a.file_name,
                        "file_size_mb": round(a.file_size / (1024 * 1024), 2),
                        "checksum": a.checksum,
                        "created_at": a.created_at,
                        "downloads": a.download_count
                    }
                    for a in artifacts
                ]
            }
            
            with open(output_file, 'w') as f:
                json.dump(manifest, f, indent=2)
            
            logger.info(f"✅ Manifest exported: {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export manifest: {e}")
            return False


if __name__ == "__main__":
    # Example usage
    storage = ArtifactStorageManager("./artifacts")
    delivery = ArtifactDeliveryManager(storage)
    analyzer = ArtifactAnalyzer(storage)
    
    # Print storage statistics
    usage = storage._get_storage_usage()
    print(f"Current storage usage: {usage / (1024*1024):.2f} MB")
    print(f"Max storage: {storage.max_storage_bytes / (1024*1024*1024):.2f} GB")
    print(f"Retention period: {storage.retention_days} days")
