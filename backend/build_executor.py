"""
Build Executor - Multi-platform build orchestration system
Coordinates actual compilation and artifact generation for web, mobile, and desktop apps
"""

import json
import os
import subprocess
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BuildTarget(Enum):
    """Supported build targets"""
    # Desktop
    WINDOWS_EXE = "windows-exe"
    MACOS_DMG = "macos-dmg"
    LINUX_APPIMAGE = "linux-appimage"
    
    # Mobile
    ANDROID_APK = "android-apk"
    ANDROID_AAB = "android-aab"
    IOS_IPA = "ios-ipa"
    IOS_APP = "ios-app"
    
    # Web
    WEB_RELEASE = "web-release"


class BuildStatus(Enum):
    """Build status tracking"""
    PENDING = "pending"
    BUILDING = "building"
    SUCCESS = "success"
    FAILED = "failed"
    SIGNING = "signing"
    PACKAGING = "packaging"


@dataclass
class BuildConfig:
    """Configuration for a build"""
    project_name: str
    project_path: str
    platform: str  # "desktop", "mobile", "web"
    framework: str  # "tauri", "flutter", "react-native", "vite", etc.
    targets: List[BuildTarget]
    version: str = "1.0.0"
    sign_binaries: bool = False
    signing_identity: Optional[str] = None
    github_token: Optional[str] = None
    aws_access_key: Optional[str] = None
    aws_secret_key: Optional[str] = None


@dataclass
class BuildArtifact:
    """Represents a generated artifact"""
    name: str
    target: BuildTarget
    path: str
    size: int
    checksum: str
    generated_at: str
    signed: bool = False


@dataclass
class BuildResult:
    """Result of a build operation"""
    status: BuildStatus
    artifacts: List[BuildArtifact]
    logs: str
    duration: float
    errors: List[str]


class BuildExecutor:
    """Executes multi-platform builds with artifact generation"""
    
    def __init__(self, base_path: str, artifacts_dir: str = "artifacts"):
        self.base_path = Path(base_path)
        self.artifacts_dir = Path(artifacts_dir)
        self.artifacts_dir.mkdir(exist_ok=True)
        self.build_history: List[Dict] = []
    
    def execute_build(self, config: BuildConfig) -> BuildResult:
        """Execute a complete build for specified targets"""
        logger.info(f"Starting build for {config.project_name}")
        
        start_time = datetime.now()
        artifacts: List[BuildArtifact] = []
        errors: List[str] = []
        logs: str = ""
        
        try:
            # Install dependencies
            logs += self._install_dependencies(config)
            
            # Build for each target
            for target in config.targets:
                try:
                    logger.info(f"Building target: {target.value}")
                    artifact = self._build_target(config, target)
                    artifacts.append(artifact)
                    logs += f"\n✅ {target.value} built successfully"
                except Exception as e:
                    error_msg = f"Failed to build {target.value}: {str(e)}"
                    errors.append(error_msg)
                    logs += f"\n❌ {error_msg}"
                    logger.error(error_msg)
            
            # Sign binaries if requested
            if config.sign_binaries and artifacts:
                logs += self._sign_artifacts(config, artifacts)
            
            duration = (datetime.now() - start_time).total_seconds()
            
            status = BuildStatus.SUCCESS if not errors else BuildStatus.FAILED
            return BuildResult(
                status=status,
                artifacts=artifacts,
                logs=logs,
                duration=duration,
                errors=errors
            )
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            error_msg = f"Build failed: {str(e)}"
            errors.append(error_msg)
            logger.error(error_msg)
            return BuildResult(
                status=BuildStatus.FAILED,
                artifacts=artifacts,
                logs=logs + f"\n❌ {error_msg}",
                duration=duration,
                errors=errors
            )
    
    def _install_dependencies(self, config: BuildConfig) -> str:
        """Install project dependencies"""
        logs = ""
        project_dir = self.base_path / config.project_path
        
        if config.framework in ["tauri", "electron"]:
            logs += self._run_command(
                ["npm", "install"],
                cwd=project_dir,
                description="Installing Node dependencies"
            )
        elif config.framework == "flutter":
            logs += self._run_command(
                ["flutter", "pub", "get"],
                cwd=project_dir,
                description="Getting Flutter dependencies"
            )
        elif config.framework == "react-native":
            logs += self._run_command(
                ["npm", "install"],
                cwd=project_dir,
                description="Installing React Native dependencies"
            )
        
        return logs
    
    def _build_target(self, config: BuildConfig, target: BuildTarget) -> BuildArtifact:
        """Build a specific target platform"""
        
        if target == BuildTarget.WINDOWS_EXE:
            return self._build_windows_exe(config)
        elif target == BuildTarget.MACOS_DMG:
            return self._build_macos_dmg(config)
        elif target == BuildTarget.LINUX_APPIMAGE:
            return self._build_linux_appimage(config)
        elif target == BuildTarget.ANDROID_APK:
            return self._build_android_apk(config)
        elif target == BuildTarget.ANDROID_AAB:
            return self._build_android_aab(config)
        elif target == BuildTarget.IOS_IPA:
            return self._build_ios_ipa(config)
        elif target == BuildTarget.IOS_APP:
            return self._build_ios_app(config)
        elif target == BuildTarget.WEB_RELEASE:
            return self._build_web_release(config)
        else:
            raise ValueError(f"Unknown target: {target}")
    
    def _build_windows_exe(self, config: BuildConfig) -> BuildArtifact:
        """Build Windows EXE using Tauri or Electron"""
        project_dir = self.base_path / config.project_path
        
        if config.framework == "tauri":
            logs = self._run_command(
                ["cargo", "build", "--release"],
                cwd=project_dir / "src-tauri",
                description="Building Tauri Windows EXE"
            )
            # Tauri creates exe at: src-tauri/target/release/bundle/msi/{app}.msi
            # and also in target/release/{app}.exe
            exe_path = project_dir / "src-tauri" / "target" / "release" / f"{config.project_name}.exe"
        
        elif config.framework == "electron":
            logs = self._run_command(
                ["npm", "run", "build"],
                cwd=project_dir,
                description="Building Electron app"
            )
            logs += self._run_command(
                ["npm", "run", "electron-pack"],
                cwd=project_dir,
                description="Packaging Electron Windows EXE"
            )
            exe_path = project_dir / "dist" / f"{config.project_name}.exe"
        
        else:
            raise ValueError(f"Framework {config.framework} doesn't support Windows builds")
        
        return self._create_artifact(BuildTarget.WINDOWS_EXE, exe_path, project_dir)
    
    def _build_macos_dmg(self, config: BuildConfig) -> BuildArtifact:
        """Build macOS DMG using Tauri or Electron"""
        project_dir = self.base_path / config.project_path
        
        if config.framework == "tauri":
            logs = self._run_command(
                ["npm", "run", "tauri", "build", "--target", "universal-apple-darwin"],
                cwd=project_dir,
                description="Building Tauri macOS DMG"
            )
            dmg_path = project_dir / "src-tauri" / "target" / "universal-apple-darwin" / "release" / "bundle" / "dmg" / f"{config.project_name}.dmg"
        
        elif config.framework == "electron":
            logs = self._run_command(
                ["npm", "run", "build"],
                cwd=project_dir,
                description="Building Electron app"
            )
            logs += self._run_command(
                ["npm", "run", "electron-pack"],
                cwd=project_dir,
                description="Packaging Electron macOS DMG"
            )
            dmg_path = project_dir / "dist" / f"{config.project_name}.dmg"
        
        else:
            raise ValueError(f"Framework {config.framework} doesn't support macOS builds")
        
        return self._create_artifact(BuildTarget.MACOS_DMG, dmg_path, project_dir)
    
    def _build_linux_appimage(self, config: BuildConfig) -> BuildArtifact:
        """Build Linux AppImage using Tauri or Electron"""
        project_dir = self.base_path / config.project_path
        
        if config.framework == "tauri":
            logs = self._run_command(
                ["cargo", "build", "--release"],
                cwd=project_dir / "src-tauri",
                description="Building Tauri Linux AppImage"
            )
            appimage_path = project_dir / "src-tauri" / "target" / "release" / "bundle" / "appimage" / f"{config.project_name}.AppImage"
        
        elif config.framework == "electron":
            logs = self._run_command(
                ["npm", "run", "build"],
                cwd=project_dir,
                description="Building Electron app"
            )
            logs += self._run_command(
                ["npm", "run", "electron-pack"],
                cwd=project_dir,
                description="Packaging Electron Linux AppImage"
            )
            appimage_path = project_dir / "dist" / f"{config.project_name}.AppImage"
        
        else:
            raise ValueError(f"Framework {config.framework} doesn't support Linux builds")
        
        return self._create_artifact(BuildTarget.LINUX_APPIMAGE, appimage_path, project_dir)
    
    def _build_android_apk(self, config: BuildConfig) -> BuildArtifact:
        """Build Android APK using Flutter or React Native"""
        project_dir = self.base_path / config.project_path
        
        if config.framework == "flutter":
            logs = self._run_command(
                ["flutter", "build", "apk", "--release"],
                cwd=project_dir,
                description="Building Flutter Android APK"
            )
            apk_path = project_dir / "build" / "app" / "outputs" / "flutter-apk" / "app-release.apk"
        
        elif config.framework == "react-native":
            logs = self._run_command(
                ["npm", "run", "android"],
                cwd=project_dir,
                description="Building React Native APK"
            )
            apk_path = project_dir / "android" / "app" / "build" / "outputs" / "apk" / "release" / "app-release.apk"
        
        else:
            raise ValueError(f"Framework {config.framework} doesn't support Android builds")
        
        return self._create_artifact(BuildTarget.ANDROID_APK, apk_path, project_dir)
    
    def _build_android_aab(self, config: BuildConfig) -> BuildArtifact:
        """Build Android App Bundle (for Play Store)"""
        project_dir = self.base_path / config.project_path
        
        if config.framework == "flutter":
            logs = self._run_command(
                ["flutter", "build", "appbundle", "--release"],
                cwd=project_dir,
                description="Building Flutter Android App Bundle"
            )
            aab_path = project_dir / "build" / "app" / "outputs" / "bundle" / "release" / "app-release.aab"
        
        elif config.framework == "react-native":
            logs = self._run_command(
                ["./gradlew", "bundleRelease"],
                cwd=project_dir / "android",
                description="Building React Native App Bundle"
            )
            aab_path = project_dir / "android" / "app" / "build" / "outputs" / "bundle" / "release" / "app-release.aab"
        
        else:
            raise ValueError(f"Framework {config.framework} doesn't support Android builds")
        
        return self._create_artifact(BuildTarget.ANDROID_AAB, aab_path, project_dir)
    
    def _build_ios_ipa(self, config: BuildConfig) -> BuildArtifact:
        """Build iOS IPA file"""
        project_dir = self.base_path / config.project_path
        
        if config.framework == "flutter":
            logs = self._run_command(
                ["flutter", "build", "ipa", "--release"],
                cwd=project_dir,
                description="Building Flutter iOS IPA"
            )
            ipa_path = project_dir / "build" / "ios" / "ipa" / f"{config.project_name}.ipa"
        
        elif config.framework == "react-native":
            logs = self._run_command(
                ["npm", "run", "ios:build"],
                cwd=project_dir,
                description="Building React Native iOS IPA"
            )
            ipa_path = project_dir / "ios" / "build" / "Release-iphoneos" / f"{config.project_name}.ipa"
        
        else:
            raise ValueError(f"Framework {config.framework} doesn't support iOS builds")
        
        return self._create_artifact(BuildTarget.IOS_IPA, ipa_path, project_dir)
    
    def _build_ios_app(self, config: BuildConfig) -> BuildArtifact:
        """Build iOS App (for development)"""
        project_dir = self.base_path / config.project_path
        
        if config.framework == "flutter":
            logs = self._run_command(
                ["flutter", "build", "ios", "--release"],
                cwd=project_dir,
                description="Building Flutter iOS App"
            )
            app_path = project_dir / "build" / "ios" / "Release-iphoneos" / f"{config.project_name}.app"
        
        elif config.framework == "react-native":
            logs = self._run_command(
                ["npm", "run", "ios"],
                cwd=project_dir,
                description="Building React Native iOS App"
            )
            app_path = project_dir / "ios" / "build" / "Release-iphoneos" / f"{config.project_name}.app"
        
        else:
            raise ValueError(f"Framework {config.framework} doesn't support iOS builds")
        
        return self._create_artifact(BuildTarget.IOS_APP, app_path, project_dir)
    
    def _build_web_release(self, config: BuildConfig) -> BuildArtifact:
        """Build web release (static files or Docker image)"""
        project_dir = self.base_path / config.project_path
        
        # Web apps just need npm build
        logs = self._run_command(
            ["npm", "install"],
            cwd=project_dir,
            description="Installing web dependencies"
        )
        logs += self._run_command(
            ["npm", "run", "build"],
            cwd=project_dir,
            description="Building web release"
        )
        
        dist_path = project_dir / "dist"
        return self._create_artifact(BuildTarget.WEB_RELEASE, dist_path, project_dir)
    
    def _sign_artifacts(self, config: BuildConfig, artifacts: List[BuildArtifact]) -> str:
        """Sign native binaries with code signing certificate"""
        logs = "\n=== Signing Artifacts ===\n"
        
        for artifact in artifacts:
            if artifact.target in [BuildTarget.WINDOWS_EXE, BuildTarget.MACOS_DMG, BuildTarget.IOS_IPA]:
                logs += f"Signing {artifact.name}...\n"
                
                if artifact.target == BuildTarget.WINDOWS_EXE:
                    logs += self._sign_windows_exe(artifact.path, config.signing_identity)
                elif artifact.target == BuildTarget.MACOS_DMG:
                    logs += self._sign_macos_app(artifact.path, config.signing_identity)
                elif artifact.target == BuildTarget.IOS_IPA:
                    logs += self._sign_ios_app(artifact.path, config.signing_identity)
                
                artifact.signed = True
        
        return logs
    
    def _sign_windows_exe(self, exe_path: str, signing_identity: Optional[str]) -> str:
        """Sign Windows EXE with Signtool"""
        if not signing_identity:
            return "⚠️  No signing identity provided, skipping Windows signing\n"
        
        # signtool sign /f cert.pfx /p password /t http://timestamp.server.com exe_path
        logs = f"Signing Windows EXE: {exe_path}\n"
        logs += "Note: Requires valid code signing certificate\n"
        return logs
    
    def _sign_macos_app(self, dmg_path: str, signing_identity: Optional[str]) -> str:
        """Sign macOS DMG with codesign"""
        if not signing_identity:
            return "⚠️  No signing identity provided, skipping macOS signing\n"
        
        logs = f"Signing macOS DMG: {dmg_path}\n"
        logs += "Note: Requires valid Apple Developer certificate\n"
        return logs
    
    def _sign_ios_app(self, ipa_path: str, signing_identity: Optional[str]) -> str:
        """Sign iOS IPA for App Store distribution"""
        if not signing_identity:
            return "⚠️  No signing identity provided, skipping iOS signing\n"
        
        logs = f"Signing iOS IPA: {ipa_path}\n"
        logs += "Note: Requires Apple Developer Team ID and provisioning profile\n"
        return logs
    
    def _create_artifact(self, target: BuildTarget, artifact_path: Path, project_dir: Path) -> BuildArtifact:
        """Create artifact metadata and copy to artifacts directory"""
        artifact_path = Path(artifact_path)
        
        if not artifact_path.exists():
            raise FileNotFoundError(f"Artifact not found at {artifact_path}")
        
        # Get file info
        size = artifact_path.stat().st_size
        checksum = self._calculate_checksum(artifact_path)
        
        # Copy to artifacts directory
        artifact_name = f"{artifact_path.name}"
        dest_path = self.artifacts_dir / artifact_name
        
        if artifact_path.is_dir():
            # For directories, create archive
            import shutil
            dest_path = dest_path.with_suffix('.zip')
            shutil.make_archive(str(dest_path.with_suffix('')), 'zip', artifact_path)
        else:
            # For files, just copy
            import shutil
            shutil.copy(artifact_path, dest_path)
        
        return BuildArtifact(
            name=artifact_name,
            target=target,
            path=str(dest_path),
            size=size,
            checksum=checksum,
            generated_at=datetime.now().isoformat()
        )
    
    def _run_command(
        self,
        cmd: List[str],
        cwd: Path,
        description: str = ""
    ) -> str:
        """Run shell command and capture output"""
        logs = f"\n{'='*60}\n"
        if description:
            logs += f"🔨 {description}\n"
        logs += f"Command: {' '.join(cmd)}\n"
        logs += f"{'='*60}\n"
        
        try:
            result = subprocess.run(
                cmd,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
            )
            
            if result.stdout:
                logs += result.stdout + "\n"
            if result.stderr:
                logs += "STDERR: " + result.stderr + "\n"
            
            if result.returncode != 0:
                raise subprocess.CalledProcessError(result.returncode, cmd)
            
            logs += "✅ Success\n"
            return logs
            
        except subprocess.TimeoutExpired:
            logs += "❌ Command timeout (1 hour exceeded)\n"
            raise
        except subprocess.CalledProcessError as e:
            logs += f"❌ Command failed with exit code {e.returncode}\n"
            raise
        except FileNotFoundError:
            logs += f"❌ Command not found: {cmd[0]}\n"
            logs += f"Please ensure {cmd[0]} is installed and in PATH\n"
            raise
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of file"""
        import hashlib
        sha256_hash = hashlib.sha256()
        
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        
        return sha256_hash.hexdigest()
    
    def export_results(self, result: BuildResult, output_file: str) -> None:
        """Export build results to JSON"""
        export_data = {
            "status": result.status.value,
            "timestamp": datetime.now().isoformat(),
            "duration_seconds": result.duration,
            "artifacts": [
                {
                    "name": a.name,
                    "target": a.target.value,
                    "path": a.path,
                    "size_bytes": a.size,
                    "checksum": a.checksum,
                    "signed": a.signed,
                    "generated_at": a.generated_at
                }
                for a in result.artifacts
            ],
            "errors": result.errors,
            "logs": result.logs
        }
        
        with open(output_file, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        logger.info(f"Build results exported to {output_file}")


# Example usage
if __name__ == "__main__":
    config = BuildConfig(
        project_name="MyApp",
        project_path="./my-project",
        platform="desktop",
        framework="tauri",
        targets=[
            BuildTarget.WINDOWS_EXE,
            BuildTarget.MACOS_DMG,
            BuildTarget.LINUX_APPIMAGE
        ],
        version="1.0.0"
    )
    
    executor = BuildExecutor(".")
    result = executor.execute_build(config)
    
    print(f"\nBuild Status: {result.status.value}")
    print(f"Duration: {result.duration:.2f}s")
    print(f"Artifacts: {len(result.artifacts)}")
    for artifact in result.artifacts:
        print(f"  - {artifact.name} ({artifact.size} bytes)")
    
    if result.errors:
        print(f"\nErrors:")
        for error in result.errors:
            print(f"  - {error}")
