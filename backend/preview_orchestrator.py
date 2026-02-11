"""
GAAIUS Preview Orchestrator (System 5)
Manages development servers and live preview for generated projects
"""

import asyncio
import subprocess
import os
import sys
import logging
import json
import socket
from pathlib import Path
from typing import Dict, Optional, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

# ============== CONSTANTS ==============

class ServerType(Enum):
    FRONTEND = "frontend"
    BACKEND = "backend"
    BOTH = "both"

class ServerStatus(Enum):
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    ERROR = "error"

DEFAULT_PORTS = {
    "frontend": 5173,
    "backend": 3001,
}

# ============== MODELS ==============

@dataclass
class ServerProcess:
    """Represents a running server process"""
    type: ServerType
    project_id: str
    port: int
    process: Optional[subprocess.Popen] = None
    status: ServerStatus = ServerStatus.STOPPED
    pid: Optional[int] = None
    started_at: Optional[datetime] = None
    last_output: str = ""
    error_message: Optional[str] = None
    
    def is_running(self) -> bool:
        """Check if process is running"""
        if not self.process:
            return False
        return self.process.poll() is None
    
    def terminate(self):
        """Terminate the process"""
        if self.process:
            try:
                self.process.terminate()
                try:
                    self.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.process.kill()
                    self.process.wait()
            except Exception as e:
                logger.error(f"Error terminating process: {e}")
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "type": self.type.value,
            "project_id": self.project_id,
            "port": self.port,
            "status": self.status.value,
            "pid": self.pid,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "is_running": self.is_running(),
            "error_message": self.error_message
        }

@dataclass
class ProjectServers:
    """Manages both frontend and backend servers for a project"""
    project_id: str
    project_path: Path
    backend_framework: str = "express"  # express or fastapi
    frontend_port: int = DEFAULT_PORTS["frontend"]
    backend_port: int = DEFAULT_PORTS["backend"]
    
    frontend_process: Optional[ServerProcess] = None
    backend_process: Optional[ServerProcess] = None
    created_at: datetime = field(default_factory=lambda: datetime.now())
    
    def get_frontend_url(self) -> str:
        """Get frontend URL"""
        return f"http://localhost:{self.frontend_port}"
    
    def get_backend_url(self) -> str:
        """Get backend API URL"""
        return f"http://localhost:{self.backend_port}"
    
    def both_running(self) -> bool:
        """Check if both servers are running"""
        return (
            self.frontend_process and self.frontend_process.is_running() and
            self.backend_process and self.backend_process.is_running()
        )
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "project_id": self.project_id,
            "project_path": str(self.project_path),
            "backend_framework": self.backend_framework,
            "frontend_port": self.frontend_port,
            "backend_port": self.backend_port,
            "created_at": self.created_at.isoformat(),
            "frontend": self.frontend_process.to_dict() if self.frontend_process else None,
            "backend": self.backend_process.to_dict() if self.backend_process else None,
            "both_running": self.both_running(),
            "urls": {
                "frontend": self.get_frontend_url(),
                "backend": self.get_backend_url()
            }
        }

# ============== PREVIEW ORCHESTRATOR ==============

class PreviewOrchestrator:
    """
    Manages development servers for generated projects.
    
    Responsibilities:
    1. Start Vite frontend dev server (port 5173)
    2. Start Express/FastAPI backend dev server (port 3001)
    3. Monitor process health
    4. Manage logs and output
    5. Graceful shutdown
    """
    
    def __init__(self):
        self.projects: Dict[str, ProjectServers] = {}
        self.port_mapping: Dict[int, str] = {}  # port -> project_id
        logger.info("PreviewOrchestrator initialized")
    
    # ============== PORT MANAGEMENT ==============
    
    def _find_available_port(self, start_port: int = 5173) -> int:
        """Find an available port starting from start_port"""
        port = start_port
        while port in self.port_mapping:
            port += 1
        
        # Verify port is actually available
        while not self._is_port_available(port):
            port += 1
        
        return port
    
    @staticmethod
    def _is_port_available(port: int) -> bool:
        """Check if a port is available"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('127.0.0.1', port))
                s.close()
            return True
        except OSError:
            return False
    
    # ============== FRONTEND SERVER ==============
    
    async def start_frontend(
        self,
        project_id: str,
        project_path: Path,
        port: Optional[int] = None
    ) -> Tuple[bool, str]:
        """
        Start Vite development server for frontend.
        
        Args:
            project_id: Project identifier
            project_path: Path to project root
            port: Port to run on (auto-selects if None)
        
        Returns:
            (success: bool, message: str)
        """
        try:
            if port is None:
                port = self._find_available_port(DEFAULT_PORTS["frontend"])
            
            frontend_path = project_path / "frontend"
            
            if not frontend_path.exists():
                return False, f"Frontend directory not found: {frontend_path}"
            
            # Check if package.json exists
            package_json = frontend_path / "package.json"
            if not package_json.exists():
                return False, f"package.json not found in {frontend_path}"
            
            logger.info(f"Starting frontend server for {project_id} on port {port}")
            
            # Determine npm/yarn command
            yarn_lock = frontend_path / "yarn.lock"
            npm_cmd = "yarn" if yarn_lock.exists() else "npm"
            
            # Start process
            process = subprocess.Popen(
                [npm_cmd, "run", "dev", "--", "--port", str(port)],
                cwd=str(frontend_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            
            # Create server record
            server = ServerProcess(
                type=ServerType.FRONTEND,
                project_id=project_id,
                port=port,
                process=process,
                status=ServerStatus.STARTING,
                pid=process.pid,
                started_at=datetime.now()
            )
            
            # Get or create project servers
            if project_id not in self.projects:
                self.projects[project_id] = ProjectServers(
                    project_id=project_id,
                    project_path=project_path
                )
            
            self.projects[project_id].frontend_process = server
            self.port_mapping[port] = project_id
            
            # Wait briefly for startup
            await asyncio.sleep(2)
            
            if server.is_running():
                server.status = ServerStatus.RUNNING
                logger.info(f"Frontend server started: {project_id} on port {port}")
                return True, f"Frontend server running on {server.get_frontend_url()}"
            else:
                # Get error output
                _, stderr = process.communicate(timeout=5)
                server.status = ServerStatus.ERROR
                server.error_message = stderr
                logger.error(f"Frontend server failed: {stderr}")
                return False, f"Frontend server failed to start: {stderr[:500]}"
        
        except Exception as e:
            logger.error(f"Error starting frontend server: {e}", exc_info=True)
            return False, f"Error starting frontend server: {str(e)}"
    
    # ============== BACKEND SERVER ==============
    
    async def start_backend(
        self,
        project_id: str,
        project_path: Path,
        backend_framework: str = "express",
        port: Optional[int] = None
    ) -> Tuple[bool, str]:
        """
        Start backend development server (Express or FastAPI).
        
        Args:
            project_id: Project identifier
            project_path: Path to project root
            backend_framework: "express" or "fastapi"
            port: Port to run on (auto-selects if None)
        
        Returns:
            (success: bool, message: str)
        """
        try:
            if port is None:
                port = self._find_available_port(DEFAULT_PORTS["backend"])
            
            backend_path = project_path / "backend"
            
            if not backend_path.exists():
                return False, f"Backend directory not found: {backend_path}"
            
            logger.info(f"Starting {backend_framework} server for {project_id} on port {port}")
            
            if backend_framework == "express":
                return await self._start_express_backend(
                    project_id, backend_path, port
                )
            elif backend_framework == "fastapi":
                return await self._start_fastapi_backend(
                    project_id, backend_path, port
                )
            else:
                return False, f"Unknown backend framework: {backend_framework}"
        
        except Exception as e:
            logger.error(f"Error starting backend server: {e}", exc_info=True)
            return False, f"Error starting backend server: {str(e)}"
    
    async def _start_express_backend(
        self,
        project_id: str,
        backend_path: Path,
        port: int
    ) -> Tuple[bool, str]:
        """Start Express development server"""
        try:
            # Check package.json
            package_json = backend_path / "package.json"
            if not package_json.exists():
                return False, f"package.json not found in {backend_path}"
            
            # Determine npm/yarn
            yarn_lock = backend_path / "yarn.lock"
            npm_cmd = "yarn" if yarn_lock.exists() else "npm"
            
            # Set environment
            env = os.environ.copy()
            env["PORT"] = str(port)
            env["NODE_ENV"] = "development"
            
            # Start process
            process = subprocess.Popen(
                [npm_cmd, "run", "dev"],
                cwd=str(backend_path),
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            
            # Create server record
            server = ServerProcess(
                type=ServerType.BACKEND,
                project_id=project_id,
                port=port,
                process=process,
                status=ServerStatus.STARTING,
                pid=process.pid,
                started_at=datetime.now()
            )
            
            # Get or create project servers
            if project_id not in self.projects:
                self.projects[project_id] = ProjectServers(
                    project_id=project_id,
                    project_path=backend_path.parent,
                    backend_framework="express"
                )
            
            self.projects[project_id].backend_process = server
            self.port_mapping[port] = project_id
            
            # Wait for startup
            await asyncio.sleep(2)
            
            if server.is_running():
                server.status = ServerStatus.RUNNING
                logger.info(f"Express server started: {project_id} on port {port}")
                return True, f"Express server running on {server.get_backend_url()}"
            else:
                _, stderr = process.communicate(timeout=5)
                server.status = ServerStatus.ERROR
                server.error_message = stderr
                return False, f"Express server failed: {stderr[:500]}"
        
        except Exception as e:
            logger.error(f"Express startup error: {e}", exc_info=True)
            return False, str(e)
    
    async def _start_fastapi_backend(
        self,
        project_id: str,
        backend_path: Path,
        port: int
    ) -> Tuple[bool, str]:
        """Start FastAPI development server"""
        try:
            # Look for main.py or app.py
            main_file = backend_path / "main.py"
            if not main_file.exists():
                main_file = backend_path / "app.py"
            
            if not main_file.exists():
                return False, "main.py or app.py not found in backend"
            
            # Set environment
            env = os.environ.copy()
            env["PYTHONUNBUFFERED"] = "1"
            
            # Start uvicorn
            process = subprocess.Popen(
                [
                    sys.executable, "-m", "uvicorn",
                    f"main:app",
                    "--host", "127.0.0.1",
                    "--port", str(port),
                    "--reload"
                ],
                cwd=str(backend_path),
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            
            # Create server record
            server = ServerProcess(
                type=ServerType.BACKEND,
                project_id=project_id,
                port=port,
                process=process,
                status=ServerStatus.STARTING,
                pid=process.pid,
                started_at=datetime.now()
            )
            
            # Get or create project servers
            if project_id not in self.projects:
                self.projects[project_id] = ProjectServers(
                    project_id=project_id,
                    project_path=backend_path.parent,
                    backend_framework="fastapi"
                )
            
            self.projects[project_id].backend_process = server
            self.port_mapping[port] = project_id
            
            # Wait for startup
            await asyncio.sleep(3)
            
            if server.is_running():
                server.status = ServerStatus.RUNNING
                logger.info(f"FastAPI server started: {project_id} on port {port}")
                return True, f"FastAPI server running on {server.get_backend_url()}"
            else:
                _, stderr = process.communicate(timeout=5)
                server.status = ServerStatus.ERROR
                server.error_message = stderr
                return False, f"FastAPI server failed: {stderr[:500]}"
        
        except Exception as e:
            logger.error(f"FastAPI startup error: {e}", exc_info=True)
            return False, str(e)
    
    # ============== LIFECYCLE MANAGEMENT ==============
    
    async def start_all(
        self,
        project_id: str,
        project_path: Path,
        backend_framework: str = "express"
    ) -> Dict[str, any]:
        """
        Start both frontend and backend servers.
        
        Returns:
            {
                "status": "success/error",
                "project_id": str,
                "frontend": { "success": bool, "message": str, "url": str },
                "backend": { "success": bool, "message": str, "url": str }
            }
        """
        logger.info(f"Starting all servers for {project_id}")
        
        # Start both concurrently
        frontend_result = await self.start_frontend(project_id, project_path)
        backend_result = await self.start_backend(
            project_id, project_path, backend_framework
        )
        
        overall_status = "success" if (frontend_result[0] and backend_result[0]) else "error"
        
        result = {
            "status": overall_status,
            "project_id": project_id,
            "frontend": {
                "success": frontend_result[0],
                "message": frontend_result[1],
                "url": self.projects[project_id].get_frontend_url() if frontend_result[0] else None
            },
            "backend": {
                "success": backend_result[0],
                "message": backend_result[1],
                "url": self.projects[project_id].get_backend_url() if backend_result[0] else None
            }
        }
        
        logger.info(f"All servers started: {json.dumps(result, indent=2)}")
        return result
    
    async def stop_frontend(self, project_id: str) -> bool:
        """Stop frontend server"""
        if project_id not in self.projects:
            return False
        
        project = self.projects[project_id]
        if project.frontend_process:
            project.frontend_process.terminate()
            if project.frontend_process.port in self.port_mapping:
                del self.port_mapping[project.frontend_process.port]
            project.frontend_process = None
            logger.info(f"Frontend stopped: {project_id}")
            return True
        
        return False
    
    async def stop_backend(self, project_id: str) -> bool:
        """Stop backend server"""
        if project_id not in self.projects:
            return False
        
        project = self.projects[project_id]
        if project.backend_process:
            project.backend_process.terminate()
            if project.backend_process.port in self.port_mapping:
                del self.port_mapping[project.backend_process.port]
            project.backend_process = None
            logger.info(f"Backend stopped: {project_id}")
            return True
        
        return False
    
    async def stop_all(self, project_id: str) -> Dict[str, bool]:
        """Stop both servers"""
        return {
            "frontend": await self.stop_frontend(project_id),
            "backend": await self.stop_backend(project_id)
        }
    
    async def stop_all_projects(self):
        """Stop all running servers"""
        logger.info("Stopping all servers...")
        for project_id in list(self.projects.keys()):
            await self.stop_all(project_id)
    
    # ============== STATUS & MONITORING ==============
    
    def get_project_status(self, project_id: str) -> Optional[Dict]:
        """Get status of a project's servers"""
        if project_id not in self.projects:
            return None
        
        return self.projects[project_id].to_dict()
    
    def list_running_projects(self) -> List[Dict]:
        """List all running projects"""
        return [p.to_dict() for p in self.projects.values()]
    
    def get_health_status(self) -> Dict:
        """Get health status of orchestrator"""
        running_projects = len([
            p for p in self.projects.values()
            if p.both_running()
        ])
        
        return {
            "status": "healthy",
            "total_projects": len(self.projects),
            "running_projects": running_projects,
            "used_ports": list(self.port_mapping.keys())
        }

# ============== GLOBAL INSTANCE ==============

_orchestrator_instance: Optional[PreviewOrchestrator] = None

def get_preview_orchestrator() -> PreviewOrchestrator:
    """Get or create the preview orchestrator instance"""
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = PreviewOrchestrator()
    return _orchestrator_instance

# ============== EXAMPLE USAGE ==============

async def example_usage():
    """Example of how to use PreviewOrchestrator"""
    orchestrator = get_preview_orchestrator()
    
    # Start both servers
    result = await orchestrator.start_all(
        project_id="my-project",
        project_path=Path("generated_projects/my-project"),
        backend_framework="express"
    )
    
    print(json.dumps(result, indent=2))
    
    # Check status
    status = orchestrator.get_project_status("my-project")
    print(json.dumps(status, indent=2))
    
    # List running
    running = orchestrator.list_running_projects()
    print(f"Running projects: {len(running)}")
    
    # Health check
    health = orchestrator.get_health_status()
    print(json.dumps(health, indent=2))
    
    # Cleanup
    await orchestrator.stop_all("my-project")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(example_usage())
