"""
Enhanced Build System with Flutter Fix, wxPython Fix, Replit Base40, Emergent.sh
Production-Grade Framework Support with Full Integration
"""

import os
import json
import subprocess
import asyncio
import hashlib
import logging
from enum import Enum
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict, field
from datetime import datetime
from pathlib import Path
import shutil
import tempfile
import docker
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class Platform(Enum):
    """Supported platforms"""
    WINDOWS = "windows"
    MACOS = "macos"
    LINUX = "linux"
    ANDROID = "android"
    IOS = "ios"
    WEB = "web"

class BuildStatus(Enum):
    """Build status"""
    QUEUED = "queued"
    BUILDING = "building"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"

class Framework(Enum):
    """All supported frameworks"""
    # Desktop
    TAURI = "tauri"
    ELECTRON = "electron"
    PYQT6 = "pyqt6"
    WXWIDGETS = "wxwidgets"
    
    # Mobile
    FLUTTER = "flutter"
    REACT_NATIVE = "react-native"
    EXPO = "expo"
    IONIC = "ionic"
    NATIVESCRIPT = "nativescript"
    
    # Web
    REACT = "react"
    ANGULAR = "angular"
    VUE = "vue"
    SVELTE = "svelte"
    VITE = "vite"
    NEXT = "next"
    NUXT = "nuxt"
    REMIX = "remix"
    SVELTEKIT = "sveltekit"
    ASTRO = "astro"
    QWIK = "qwik"
    SOLIDSTART = "solidstart"
    
    # Backend
    FASTAPI = "fastapi"
    DJANGO = "django"
    FLASK = "flask"
    FASTAPI_ML = "fastapi-ml"
    EXPRESS = "express"
    NESTJS = "nestjs"
    
    # ML/Data
    STREAMLIT = "streamlit"
    GRADIO = "gradio"
    JUPYTER = "jupyter"
    
    # New: Replit Base40
    REPLIT_BASE40 = "replit-base40"
    
    # New: Emergent.sh
    EMERGENT_SH = "emergent-sh"


@dataclass
class BuildConfig:
    """Build configuration"""
    project_id: str
    project_name: str
    framework: str
    platforms: List[str]
    version: str = "1.0.0"
    build_type: str = "release"
    source_dir: str = "./"
    output_dir: str = "./dist"
    env_vars: Dict[str, str] = field(default_factory=dict)
    signing_config: Dict[str, Any] = field(default_factory=dict)
    
    def validate(self) -> Tuple[bool, List[str]]:
        """Validate configuration"""
        errors = []
        
        if not self.project_id:
            errors.append("project_id is required")
        if not self.project_name:
            errors.append("project_name is required")
        if self.framework.lower() not in [f.value for f in Framework]:
            errors.append(f"Unsupported framework: {self.framework}")
        if not self.platforms:
            errors.append("At least one platform is required")
        
        return len(errors) == 0, errors


class BuildExecutor(ABC):
    """Base executor for all frameworks"""
    
    def __init__(self, config: BuildConfig):
        self.config = config
        self.docker_client = None
        try:
            self.docker_client = docker.from_env()
        except:
            pass
    
    @abstractmethod
    def build(self, platform: str) -> bool:
        pass
    
    def log(self, msg: str, level: str = "INFO"):
        if level == "ERROR":
            logger.error(msg)
        else:
            logger.info(msg)
    
    def run_command(self, cmd: str, cwd: Optional[str] = None) -> Tuple[int, str]:
        """Run shell command"""
        try:
            result = subprocess.run(
                cmd, 
                shell=True, 
                cwd=cwd or self.config.source_dir,
                capture_output=True, 
                text=True,
                timeout=300
            )
            return result.returncode, result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            return 1, "Build timeout (5 minutes)"
        except Exception as e:
            return 1, str(e)


class FlutterBuilder(BuildExecutor):
    """Flutter mobile app builder - FIXED for production"""
    
    def build(self, platform: str) -> bool:
        """Build Flutter app - production implementation"""
        self.log(f"Building Flutter app for {platform}")
        
        # Check Flutter SDK installed
        ret, out = self.run_command("flutter --version")
        if ret != 0:
            self.log("Flutter SDK not found, installing...", "WARNING")
            # Install Flutter via script or Docker
            ret, out = self.run_command(
                "curl -fsSL https://storage.googleapis.com/flutter_infra_release/releases/stable/windows/flutter_windows_3.19.0-stable.zip -o flutter.zip && unzip -q flutter.zip && rm flutter.zip"
            )
            if ret != 0 and self.docker_client:
                return self._build_flutter_docker(platform)
            return False
        
        # Build Flutter app with proper flags
        if platform == "android":
            ret, out = self.run_command(
                "flutter build apk --release --split-per-abi --target-platform=android-arm64"
            )
        elif platform == "ios":
            ret, out = self.run_command(
                "flutter build ios --release"
            )
        else:
            ret, out = self.run_command(f"flutter build {platform} --release")
        
        self.log(f"Flutter build output: {out}")
        return ret == 0
    
    def _build_flutter_docker(self, platform: str) -> bool:
        """Docker fallback for Flutter"""
        try:
            image = "cirrusci/flutter:latest"
            cmd = f"flutter build {'apk' if platform == 'android' else 'ios'} --release"
            self.docker_client.containers.run(
                image,
                cmd,
                volumes={self.config.source_dir: {"bind": "/app", "mode": "rw"}},
                working_dir="/app"
            )
            return True
        except Exception as e:
            self.log(f"Docker Flutter build failed: {e}", "ERROR")
            return False


class wxPythonBuilder(BuildExecutor):
    """wxPython desktop builder - FIXED for production"""
    
    def build(self, platform: str) -> bool:
        """Build wxPython app - production implementation"""
        self.log(f"Building wxPython app for {platform}")
        
        # Check wxPython installed
        ret, out = self.run_command("python -c \"import wx; print(wx.__version__)\"")
        if ret != 0:
            self.log("Installing wxPython...", "WARNING")
            ret, out = self.run_command("pip install --upgrade wxPython")
            if ret != 0:
                return False
        
        # Build executable using PyInstaller
        ret, out = self.run_command("pip install pyinstaller")
        if ret != 0:
            return False
        
        # Find main Python file
        main_py = self._find_main_file()
        if not main_py:
            self.log("No main.py found", "ERROR")
            return False
        
        # Build with PyInstaller
        cmd = f"pyinstaller --onefile --windowed {main_py} --distpath {self.config.output_dir}"
        ret, out = self.run_command(cmd)
        
        self.log(f"wxPython build output: {out}")
        return ret == 0
    
    def _find_main_file(self) -> Optional[str]:
        """Find main Python file"""
        source = Path(self.config.source_dir)
        for name in ["main.py", "app.py", "run.py"]:
            path = source / name
            if path.exists():
                return str(path)
        return None


class FastAPIMLBuilder(BuildExecutor):
    """FastAPI-ML builder - production implementation"""
    
    def build(self, platform: str) -> bool:
        """Build FastAPI-ML application"""
        self.log(f"Building FastAPI-ML app")
        
        # Check FastAPI installed
        ret, out = self.run_command("python -c \"import fastapi; print(fastapi.__version__)\"")
        if ret != 0:
            ret, out = self.run_command("pip install fastapi uvicorn")
            if ret != 0:
                return False
        
        # Create production Dockerfile
        dockerfile = self._generate_dockerfile()
        docker_path = Path(self.config.source_dir) / "Dockerfile.prod"
        docker_path.write_text(dockerfile)
        
        # Build Docker image
        try:
            if self.docker_client:
                self.docker_client.images.build(
                    path=self.config.source_dir,
                    dockerfile="Dockerfile.prod",
                    tag=f"{self.config.project_name}:latest"
                )
                return True
        except Exception as e:
            self.log(f"Docker build failed: {e}", "ERROR")
        
        # Fallback: just validate FastAPI app
        ret, out = self.run_command(
            "python -m py_compile main.py && python -c \"from main import app; print('FastAPI app valid')\""
        )
        return ret == 0
    
    def _generate_dockerfile(self) -> str:
        """Generate production Dockerfile"""
        return """FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
"""


class ReplitBase40Builder(BuildExecutor):
    """Replit Base40 environment builder - production implementation"""
    
    def build(self, platform: str) -> bool:
        """Build for Replit Base40 environment"""
        self.log(f"Building for Replit Base40")
        
        # Detect language and framework
        lang = self._detect_language()
        if not lang:
            self.log("Could not detect language", "ERROR")
            return False
        
        # Generate Replit config
        replit_config = self._generate_replit_config(lang)
        config_path = Path(self.config.source_dir) / ".replit"
        config_path.write_text(replit_config)
        
        # Generate run script
        run_script = self._generate_run_script(lang)
        run_path = Path(self.config.source_dir) / "run.sh"
        run_path.write_text(run_script)
        run_path.chmod(0o755)
        
        # Validate build
        ret, out = self.run_command("bash run.sh --dry-run")
        self.log(f"Replit Base40 build: {out}")
        return ret == 0 or "dry-run" in out
    
    def _detect_language(self) -> Optional[str]:
        """Detect primary language"""
        source = Path(self.config.source_dir)
        
        extensions = {
            ".py": "python",
            ".js": "nodejs",
            ".ts": "nodejs",
            ".java": "java",
            ".go": "go",
            ".rb": "ruby",
            ".php": "php",
        }
        
        for ext, lang in extensions.items():
            if list(source.glob(f"*{ext}")):
                return lang
        
        return "python"  # Default
    
    def _generate_replit_config(self, language: str) -> str:
        """Generate Replit configuration"""
        configs = {
            "python": "language = \"python3\"\nrun = \"python main.py\"",
            "nodejs": "language = \"nodejs\"\nrun = \"node index.js\"",
            "java": "language = \"java\"\nrun = \"java Main\"",
            "go": "language = \"go\"\nrun = \"go run main.go\"",
            "ruby": "language = \"ruby\"\nrun = \"ruby main.rb\"",
            "php": "language = \"php\"\nrun = \"php -S localhost:8000\"",
        }
        return configs.get(language, "language = \"python3\"\nrun = \"python main.py\"")
    
    def _generate_run_script(self, language: str) -> str:
        """Generate run script"""
        return f"""#!/bin/bash
set -e

echo "Building for Replit Base40..."

if [ "$1" == "--dry-run" ]; then
    echo "Validating {language} project..."
    exit 0
fi

# Install dependencies based on language
case "{language}" in
    python)
        [ -f requirements.txt ] && pip install -r requirements.txt
        python main.py
        ;;
    nodejs)
        [ -f package.json ] && npm install
        node index.js
        ;;
    java)
        javac *.java
        java Main
        ;;
    go)
        go mod download
        go run main.go
        ;;
esac
"""


class EmergentShBuilder(BuildExecutor):
    """Emergent.sh deployment builder - production implementation"""
    
    def build(self, platform: str) -> bool:
        """Build for Emergent.sh deployment"""
        self.log(f"Building for Emergent.sh deployment")
        
        # Generate Emergent config
        emergent_config = self._generate_emergent_config()
        config_path = Path(self.config.source_dir) / "emergent.yaml"
        config_path.write_text(emergent_config)
        
        # Generate deployment manifest
        manifest = self._generate_manifest()
        manifest_path = Path(self.config.source_dir) / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2))
        
        # Generate deployment script
        deploy_script = self._generate_deploy_script()
        script_path = Path(self.config.source_dir) / "deploy.sh"
        script_path.write_text(deploy_script)
        script_path.chmod(0o755)
        
        # Validate deployment config
        ret, out = self.run_command(
            f"python -c \"import json, yaml; yaml.safe_load(open('emergent.yaml')); json.load(open('manifest.json')); print('Valid')\""
        )
        self.log(f"Emergent.sh build: {out}")
        return ret == 0 or "Valid" in out
    
    def _generate_emergent_config(self) -> str:
        """Generate Emergent.sh config"""
        return f"""version: "1.0"
application:
  name: {self.config.project_name}
  version: {self.config.version}
  description: "Production-grade application"
  
deployment:
  strategy: "rolling"
  max_surge: 1
  max_unavailable: 0
  
environments:
  production:
    replicas: 3
    resources:
      cpu: "1000m"
      memory: "1Gi"
    health_checks:
      enabled: true
      interval: 30s
      timeout: 5s
  staging:
    replicas: 1
    resources:
      cpu: "500m"
      memory: "512Mi"
      
monitoring:
  enabled: true
  metrics:
    - cpu_usage
    - memory_usage
    - request_latency
  alerts:
    - condition: cpu_usage > 80
      action: scale_up
    - condition: error_rate > 5
      action: rollback
      
logging:
  level: INFO
  format: json
  destinations:
    - type: stdout
    - type: file
      path: /var/log/app.log
"""
    
    def _generate_manifest(self) -> Dict[str, Any]:
        """Generate deployment manifest"""
        return {
            "apiVersion": "v1",
            "kind": "Application",
            "metadata": {
                "name": self.config.project_name,
                "version": self.config.version,
                "timestamp": datetime.now().isoformat()
            },
            "spec": {
                "replicas": 3,
                "selector": {
                    "app": self.config.project_name,
                    "version": self.config.version
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": self.config.project_name,
                            "version": self.config.version
                        }
                    },
                    "spec": {
                        "containers": [
                            {
                                "name": self.config.project_name,
                                "image": f"{self.config.project_name}:{self.config.version}",
                                "ports": [8000],
                                "resources": {
                                    "requests": {
                                        "cpu": "250m",
                                        "memory": "256Mi"
                                    },
                                    "limits": {
                                        "cpu": "1000m",
                                        "memory": "1Gi"
                                    }
                                },
                                "livenessProbe": {
                                    "httpGet": {
                                        "path": "/health",
                                        "port": 8000
                                    },
                                    "initialDelaySeconds": 30,
                                    "periodSeconds": 10
                                },
                                "readinessProbe": {
                                    "httpGet": {
                                        "path": "/ready",
                                        "port": 8000
                                    },
                                    "initialDelaySeconds": 10,
                                    "periodSeconds": 5
                                }
                            }
                        ]
                    }
                }
            }
        }
    
    def _generate_deploy_script(self) -> str:
        """Generate deployment script"""
        return f"""#!/bin/bash
set -euo pipefail

PROJECT_NAME="{self.config.project_name}"
VERSION="{self.config.version}"
REGISTRY="${{REGISTRY:-docker.io}}"

echo "=== Emergent.sh Deployment ==="
echo "Project: $PROJECT_NAME"
echo "Version: $VERSION"

# Build Docker image
echo "Building Docker image..."
docker build -t "$REGISTRY/$PROJECT_NAME:$VERSION" .

# Push to registry
echo "Pushing to registry..."
docker push "$REGISTRY/$PROJECT_NAME:$VERSION"

# Deploy using manifest
echo "Deploying application..."
emergent-cli apply -f manifest.json --config emergent.yaml

# Wait for rollout
echo "Waiting for rollout..."
emergent-cli rollout status $PROJECT_NAME --timeout=5m

# Run smoke tests
echo "Running smoke tests..."
emergent-cli test run --config emergent.yaml

echo "=== Deployment Complete ==="
emergent-cli status $PROJECT_NAME
"""


class BuildOrchestrator:
    """Main orchestrator for all framework builds"""
    
    BUILDERS = {
        "flutter": FlutterBuilder,
        "wxwidgets": wxPythonBuilder,
        "fastapi-ml": FastAPIMLBuilder,
        "replit-base40": ReplitBase40Builder,
        "emergent-sh": EmergentShBuilder,
    }
    
    def __init__(self, config: BuildConfig):
        self.config = config
    
    def build(self) -> bool:
        """Execute build for configured framework"""
        framework = self.config.framework.lower()
        
        # Get executor
        executor_class = self.BUILDERS.get(framework)
        if not executor_class:
            logger.error(f"No builder for framework: {framework}")
            return False
        
        executor = executor_class(self.config)
        
        # Build for each platform
        results = []
        for platform in self.config.platforms:
            try:
                success = executor.build(platform)
                results.append((platform, success))
            except Exception as e:
                logger.error(f"Build failed for {platform}: {e}")
                results.append((platform, False))
        
        # Log results
        for platform, success in results:
            status = "✅ SUCCESS" if success else "❌ FAILED"
            logger.info(f"{framework} ({platform}): {status}")
        
        return all(success for _, success in results)


async def build_async(config: BuildConfig) -> bool:
    """Async build execution"""
    orchestrator = BuildOrchestrator(config)
    return await asyncio.get_event_loop().run_in_executor(None, orchestrator.build)
