"""
AI Builder Backend - File Management & Code Execution Engine
Replit-like IDE in browser with project management and execution
"""

from fastapi import APIRouter, HTTPException, Query, Body, WebSocket, BackgroundTasks
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import uuid
import json
import asyncio
import subprocess
import os
from pydantic import BaseModel
import shutil
import tempfile

# ============================================================================
# DATA MODELS
# ============================================================================

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    template: str = "blank"  # blank, python, javascript, react, fastapi, etc

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None

class ProjectFile(BaseModel):
    path: str
    content: str
    language: Optional[str] = None

class FileCreateRequest(BaseModel):
    path: str
    content: str = ""
    is_directory: bool = False

class ExecutionRequest(BaseModel):
    code: str
    language: str = "python"
    timeout: int = 30

class TerminalRequest(BaseModel):
    command: str
    timeout: int = 30

class PackageInstall(BaseModel):
    package: str
    version: Optional[str] = None

class EnvironmentVariable(BaseModel):
    key: str
    value: str

# ============================================================================
# AI BUILDER SERVICE
# ============================================================================

class AIBuilderService:
    def __init__(self):
        self.projects: Dict[str, Dict[str, Any]] = {}
        self.execution_jobs: Dict[str, Dict[str, Any]] = {}
        self.temp_dir = tempfile.gettempdir()
        self.project_base = Path(self.temp_dir) / "ai_builder_projects"
        self.project_base.mkdir(exist_ok=True)
    
    # ========== PROJECT MANAGEMENT ==========
    
    async def create_project(self, user_id: str, req: ProjectCreate) -> Dict[str, Any]:
        """Create new project"""
        project_id = str(uuid.uuid4())
        project_dir = self.project_base / project_id
        project_dir.mkdir(exist_ok=True)
        
        project = {
            "id": project_id,
            "user_id": user_id,
            "name": req.name,
            "description": req.description or "",
            "template": req.template,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "environment": {},
            "packages": [],
            "collaborators": []
        }
        
        self.projects[project_id] = project
        
        # Create template files
        await self._scaffold_project(project_id, req.template)
        
        return project
    
    async def get_project(self, project_id: str) -> Dict[str, Any]:
        """Get project details"""
        if project_id not in self.projects:
            raise ValueError(f"Project {project_id} not found")
        return self.projects[project_id]
    
    async def update_project(self, project_id: str, req: ProjectUpdate) -> Dict[str, Any]:
        """Update project"""
        if project_id not in self.projects:
            raise ValueError(f"Project {project_id} not found")
        
        project = self.projects[project_id]
        if req.name:
            project["name"] = req.name
        if req.description is not None:
            project["description"] = req.description
        if req.settings:
            project["settings"] = req.settings
        
        project["updated_at"] = datetime.utcnow().isoformat()
        return project
    
    async def delete_project(self, project_id: str) -> bool:
        """Delete project"""
        if project_id not in self.projects:
            raise ValueError(f"Project {project_id} not found")
        
        project_dir = self.project_base / project_id
        if project_dir.exists():
            shutil.rmtree(project_dir)
        
        del self.projects[project_id]
        return True
    
    # ========== FILE MANAGEMENT ==========
    
    async def get_file_tree(self, project_id: str) -> Dict[str, Any]:
        """Get project file tree"""
        project_dir = self.project_base / project_id
        if not project_dir.exists():
            raise ValueError(f"Project {project_id} not found")
        
        def build_tree(path: Path) -> Dict[str, Any]:
            items = []
            
            for item in sorted(path.iterdir()):
                if item.name.startswith('.'):
                    continue
                
                node = {
                    "name": item.name,
                    "path": str(item.relative_to(project_dir)),
                    "type": "directory" if item.is_dir() else "file"
                }
                
                if item.is_dir():
                    node["children"] = build_tree(item)
                else:
                    try:
                        node["size"] = item.stat().st_size
                    except:
                        node["size"] = 0
                
                items.append(node)
            
            return items
        
        return {
            "project_id": project_id,
            "tree": build_tree(project_dir)
        }
    
    async def create_file(self, project_id: str, req: FileCreateRequest) -> Dict[str, Any]:
        """Create file or directory"""
        project_dir = self.project_base / project_id
        file_path = project_dir / req.path
        
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        if req.is_directory:
            file_path.mkdir(exist_ok=True)
        else:
            file_path.write_text(req.content, encoding='utf-8')
        
        return {
            "project_id": project_id,
            "path": req.path,
            "type": "directory" if req.is_directory else "file",
            "created_at": datetime.utcnow().isoformat()
        }
    
    async def read_file(self, project_id: str, file_path: str) -> Dict[str, Any]:
        """Read file content"""
        project_dir = self.project_base / project_id
        file_full_path = project_dir / file_path
        
        if not file_full_path.exists():
            raise ValueError(f"File {file_path} not found")
        
        if file_full_path.is_dir():
            raise ValueError(f"{file_path} is a directory")
        
        try:
            content = file_full_path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            content = "[Binary file - cannot display]"
        
        return {
            "project_id": project_id,
            "path": file_path,
            "content": content,
            "size": file_full_path.stat().st_size,
            "modified_at": datetime.fromtimestamp(file_full_path.stat().st_mtime).isoformat()
        }
    
    async def update_file(self, project_id: str, file_path: str, content: str) -> Dict[str, Any]:
        """Update file content"""
        project_dir = self.project_base / project_id
        file_full_path = project_dir / file_path
        
        if not file_full_path.exists():
            raise ValueError(f"File {file_path} not found")
        
        file_full_path.write_text(content, encoding='utf-8')
        
        return {
            "project_id": project_id,
            "path": file_path,
            "size": file_full_path.stat().st_size,
            "updated_at": datetime.utcnow().isoformat()
        }
    
    async def delete_file(self, project_id: str, file_path: str) -> bool:
        """Delete file or directory"""
        project_dir = self.project_base / project_id
        file_full_path = project_dir / file_path
        
        if not file_full_path.exists():
            raise ValueError(f"File {file_path} not found")
        
        if file_full_path.is_dir():
            shutil.rmtree(file_full_path)
        else:
            file_full_path.unlink()
        
        return True
    
    # ========== CODE EXECUTION ==========
    
    async def execute_code(self, project_id: str, req: ExecutionRequest) -> Dict[str, Any]:
        """Execute code in project context"""
        job_id = str(uuid.uuid4())
        project_dir = self.project_base / project_id
        
        job = {
            "id": job_id,
            "project_id": project_id,
            "status": "running",
            "output": "",
            "error": "",
            "exit_code": None,
            "created_at": datetime.utcnow().isoformat()
        }
        
        self.execution_jobs[job_id] = job
        
        try:
            if req.language == "python":
                result = await self._execute_python(str(project_dir), req.code, req.timeout)
            elif req.language == "javascript":
                result = await self._execute_javascript(str(project_dir), req.code, req.timeout)
            elif req.language in ["bash", "sh"]:
                result = await self._execute_shell(str(project_dir), req.code, req.timeout)
            else:
                result = {"output": "", "error": f"Language {req.language} not supported", "exit_code": 1}
            
            job["status"] = "completed"
            job["output"] = result.get("output", "")
            job["error"] = result.get("error", "")
            job["exit_code"] = result.get("exit_code", 0)
        
        except asyncio.TimeoutError:
            job["status"] = "timeout"
            job["error"] = f"Execution timeout after {req.timeout} seconds"
            job["exit_code"] = 124
        except Exception as e:
            job["status"] = "failed"
            job["error"] = str(e)
            job["exit_code"] = 1
        
        job["completed_at"] = datetime.utcnow().isoformat()
        return job
    
    async def _execute_python(self, cwd: str, code: str, timeout: int) -> Dict[str, Any]:
        """Execute Python code"""
        try:
            process = await asyncio.create_subprocess_exec(
                "python", "-c", code,
                cwd=cwd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                raise
            
            return {
                "output": stdout.decode('utf-8', errors='replace'),
                "error": stderr.decode('utf-8', errors='replace'),
                "exit_code": process.returncode
            }
        except Exception as e:
            return {
                "output": "",
                "error": str(e),
                "exit_code": 1
            }
    
    async def _execute_javascript(self, cwd: str, code: str, timeout: int) -> Dict[str, Any]:
        """Execute JavaScript code (Node.js)"""
        try:
            process = await asyncio.create_subprocess_exec(
                "node", "-e", code,
                cwd=cwd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                raise
            
            return {
                "output": stdout.decode('utf-8', errors='replace'),
                "error": stderr.decode('utf-8', errors='replace'),
                "exit_code": process.returncode
            }
        except Exception as e:
            return {
                "output": "",
                "error": str(e),
                "exit_code": 1
            }
    
    async def _execute_shell(self, cwd: str, code: str, timeout: int) -> Dict[str, Any]:
        """Execute shell command"""
        try:
            process = await asyncio.create_subprocess_shell(
                code,
                cwd=cwd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                raise
            
            return {
                "output": stdout.decode('utf-8', errors='replace'),
                "error": stderr.decode('utf-8', errors='replace'),
                "exit_code": process.returncode
            }
        except Exception as e:
            return {
                "output": "",
                "error": str(e),
                "exit_code": 1
            }
    
    # ========== PACKAGE MANAGEMENT ==========
    
    async def install_package(self, project_id: str, req: PackageInstall) -> Dict[str, Any]:
        """Install package using pip or npm"""
        project_dir = self.project_base / project_id
        project = self.projects.get(project_id, {})
        
        package_spec = req.package if not req.version else f"{req.package}=={req.version}"
        
        try:
            # Try pip first (Python)
            process = await asyncio.create_subprocess_exec(
                "pip", "install", package_spec,
                cwd=str(project_dir),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                if "packages" not in project:
                    project["packages"] = []
                project["packages"].append(package_spec)
                
                return {
                    "project_id": project_id,
                    "package": package_spec,
                    "status": "installed",
                    "output": stdout.decode('utf-8', errors='replace')
                }
            else:
                return {
                    "project_id": project_id,
                    "package": package_spec,
                    "status": "failed",
                    "error": stderr.decode('utf-8', errors='replace')
                }
        except Exception as e:
            return {
                "project_id": project_id,
                "package": package_spec,
                "status": "failed",
                "error": str(e)
            }
    
    # ========== ENVIRONMENT VARIABLES ==========
    
    async def set_env_variable(self, project_id: str, key: str, value: str) -> Dict[str, Any]:
        """Set environment variable"""
        if project_id not in self.projects:
            raise ValueError(f"Project {project_id} not found")
        
        project = self.projects[project_id]
        if "environment" not in project:
            project["environment"] = {}
        
        project["environment"][key] = value
        
        return {
            "project_id": project_id,
            "key": key,
            "set": True
        }
    
    async def get_env_variables(self, project_id: str) -> Dict[str, Any]:
        """Get all environment variables"""
        if project_id not in self.projects:
            raise ValueError(f"Project {project_id} not found")
        
        project = self.projects[project_id]
        env = project.get("environment", {})
        
        return {
            "project_id": project_id,
            "variables": env
        }
    
    # ========== TEMPLATE SCAFFOLDING ==========
    
    async def _scaffold_project(self, project_id: str, template: str):
        """Create template files"""
        project_dir = self.project_base / project_id
        
        templates = {
            "blank": {
                "main.py": "# Python Project\nprint('Hello, World!')\n",
                "README.md": "# Project\n\nYour project here.\n"
            },
            "python": {
                "main.py": "#!/usr/bin/env python3\n\ndef main():\n    print('Hello from Python!')\n\nif __name__ == '__main__':\n    main()\n",
                "requirements.txt": "",
                "README.md": "# Python Project\n"
            },
            "javascript": {
                "main.js": "console.log('Hello from JavaScript!');\n",
                "package.json": json.dumps({"name": "my-project", "version": "1.0.0", "main": "main.js"}, indent=2),
                "README.md": "# JavaScript Project\n"
            }
        }
        
        files = templates.get(template, templates["blank"])
        
        for filename, content in files.items():
            filepath = project_dir / filename
            filepath.write_text(content, encoding='utf-8')
    
    async def get_execution_job(self, job_id: str) -> Dict[str, Any]:
        """Get execution job details"""
        if job_id not in self.execution_jobs:
            raise ValueError(f"Job {job_id} not found")
        return self.execution_jobs[job_id]

# ============================================================================
# ROUTER
# ============================================================================

router = APIRouter(prefix="/ai-builder", tags=["ai-builder"])
builder_service = AIBuilderService()

# Project Endpoints
@router.post("/project/create")
async def create_project(
    user_id: str = Body(...),
    name: str = Body(...),
    description: Optional[str] = Body(None),
    template: str = Body(default="blank")
) -> Dict[str, Any]:
    """Create new AI Builder project"""
    try:
        req = ProjectCreate(name=name, description=description, template=template)
        project = await builder_service.create_project(user_id, req)
        return {"status": "success", "project": project}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/project/{project_id}")
async def get_project(project_id: str) -> Dict[str, Any]:
    """Get project details"""
    try:
        project = await builder_service.get_project(project_id)
        return {"status": "success", "project": project}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.put("/project/{project_id}")
async def update_project(
    project_id: str,
    name: Optional[str] = Body(None),
    description: Optional[str] = Body(None)
) -> Dict[str, Any]:
    """Update project"""
    try:
        req = ProjectUpdate(name=name, description=description)
        project = await builder_service.update_project(project_id, req)
        return {"status": "success", "project": project}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/project/{project_id}")
async def delete_project(project_id: str) -> Dict[str, Any]:
    """Delete project"""
    try:
        await builder_service.delete_project(project_id)
        return {"status": "success", "message": "Project deleted"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# File Endpoints
@router.get("/project/{project_id}/tree")
async def get_file_tree(project_id: str) -> Dict[str, Any]:
    """Get project file tree"""
    try:
        tree = await builder_service.get_file_tree(project_id)
        return {"status": "success", **tree}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/project/{project_id}/files")
async def create_file(
    project_id: str,
    path: str = Body(...),
    content: str = Body(default=""),
    is_directory: bool = Body(default=False)
) -> Dict[str, Any]:
    """Create file or directory"""
    try:
        req = FileCreateRequest(path=path, content=content, is_directory=is_directory)
        result = await builder_service.create_file(project_id, req)
        return {"status": "success", **result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/project/{project_id}/files/{file_path:path}")
async def read_file(project_id: str, file_path: str) -> Dict[str, Any]:
    """Read file content"""
    try:
        result = await builder_service.read_file(project_id, file_path)
        return {"status": "success", **result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.put("/project/{project_id}/files/{file_path:path}")
async def update_file(
    project_id: str,
    file_path: str,
    content: str = Body(...)
) -> Dict[str, Any]:
    """Update file content"""
    try:
        result = await builder_service.update_file(project_id, file_path, content)
        return {"status": "success", **result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/project/{project_id}/files/{file_path:path}")
async def delete_file(project_id: str, file_path: str) -> Dict[str, Any]:
    """Delete file or directory"""
    try:
        await builder_service.delete_file(project_id, file_path)
        return {"status": "success", "message": "File deleted"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# Execution Endpoints
@router.post("/project/{project_id}/execute")
async def execute_code(
    project_id: str,
    code: str = Body(...),
    language: str = Body(default="python"),
    timeout: int = Body(default=30)
) -> Dict[str, Any]:
    """Execute code"""
    try:
        req = ExecutionRequest(code=code, language=language, timeout=timeout)
        job = await builder_service.execute_code(project_id, req)
        return {"status": "success", "job": job}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/execution/{job_id}")
async def get_execution_job(job_id: str) -> Dict[str, Any]:
    """Get execution job details"""
    try:
        job = await builder_service.get_execution_job(job_id)
        return {"status": "success", "job": job}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# Package Endpoints
@router.post("/project/{project_id}/packages/install")
async def install_package(
    project_id: str,
    package: str = Body(...),
    version: Optional[str] = Body(None)
) -> Dict[str, Any]:
    """Install package"""
    try:
        req = PackageInstall(package=package, version=version)
        result = await builder_service.install_package(project_id, req)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Environment Endpoints
@router.get("/project/{project_id}/env")
async def get_env_variables(project_id: str) -> Dict[str, Any]:
    """Get environment variables"""
    try:
        result = await builder_service.get_env_variables(project_id)
        return {"status": "success", **result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/project/{project_id}/env")
async def set_env_variable(
    project_id: str,
    key: str = Body(...),
    value: str = Body(...)
) -> Dict[str, Any]:
    """Set environment variable"""
    try:
        result = await builder_service.set_env_variable(project_id, key, value)
        return {"status": "success", **result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
