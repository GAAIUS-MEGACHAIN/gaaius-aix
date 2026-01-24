"""
Build Service - Replit-like IDE Backend
Provides file management, code execution, package installation, and project scaffolding
"""

import os
import json
import asyncio
import subprocess
import tempfile
import shutil
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.responses import FileResponse, StreamingResponse
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/build", tags=["build-service"])

# Models
class FileCreateRequest(BaseModel):
    path: str
    content: str = ""
    isDirectory: bool = False

class FileUpdateRequest(BaseModel):
    path: str
    content: str

class ExecutionRequest(BaseModel):
    code: str
    language: str  # "python" | "javascript" | "shell"
    timeout: int = 30

class PackageInstallRequest(BaseModel):
    package: str
    language: str  # "python" | "javascript"

class ProjectRequest(BaseModel):
    name: str
    template: str = "blank"  # blank | python | javascript | fullstack

class ProjectResponse(BaseModel):
    id: str
    name: str
    created_at: str
    files: Dict[str, str] = {}

# Store active projects in memory (in production, use database)
ACTIVE_PROJECTS: Dict[str, Dict[str, Any]] = {}
PROJECTS_DIR = Path(tempfile.gettempdir()) / "gaaius_projects"
PROJECTS_DIR.mkdir(exist_ok=True)

class BuildService:
    """Service for managing development projects"""
    
    @staticmethod
    def create_project(name: str, template: str = "blank") -> Dict[str, Any]:
        """Create a new project"""
        project_id = str(uuid.uuid4())[:8]
        project_path = PROJECTS_DIR / project_id
        project_path.mkdir(exist_ok=True)
        
        files = {}
        
        if template == "blank":
            files = {
                "index.html": "<!DOCTYPE html>\n<html>\n<head><title>My App</title></head>\n<body></body>\n</html>",
                "README.md": f"# {name}\n\nBuilt with GAAIUS AI Builder",
            }
        
        elif template == "python":
            files = {
                "main.py": "# Python Project\nif __name__ == '__main__':\n    print('Hello, World!')",
                "requirements.txt": "",
                "README.md": f"# {name}\n\nPython project built with GAAIUS",
            }
        
        elif template == "javascript":
            files = {
                "index.js": "// JavaScript Project\nconsole.log('Hello, World!');",
                "package.json": json.dumps({"name": name, "version": "1.0.0", "main": "index.js"}, indent=2),
                "README.md": f"# {name}\n\nJavaScript project built with GAAIUS",
            }
        
        elif template == "fullstack":
            files = {
                "index.html": "<!DOCTYPE html>\n<html>\n<head><title>Full Stack App</title></head>\n<body><h1>Welcome!</h1></body>\n</html>",
                "app.py": "from flask import Flask, jsonify\napp = Flask(__name__)\n\n@app.route('/api/hello')\ndef hello():\n    return jsonify({'message': 'Hello from Flask!'})",
                "requirements.txt": "flask\nflask-cors",
                "README.md": f"# {name}\n\nFull stack project",
            }
        
        # Write files to disk
        for path, content in files.items():
            file_path = project_path / path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)
        
        project_data = {
            "id": project_id,
            "name": name,
            "template": template,
            "path": str(project_path),
            "created_at": datetime.now().isoformat(),
            "files": files,
        }
        
        ACTIVE_PROJECTS[project_id] = project_data
        logger.info(f"Created project {project_id}: {name}")
        return project_data
    
    @staticmethod
    def get_project(project_id: str) -> Dict[str, Any]:
        """Get project details"""
        if project_id not in ACTIVE_PROJECTS:
            raise HTTPException(status_code=404, detail="Project not found")
        return ACTIVE_PROJECTS[project_id]
    
    @staticmethod
    def list_projects() -> List[Dict[str, Any]]:
        """List all projects"""
        return list(ACTIVE_PROJECTS.values())
    
    @staticmethod
    def get_file_tree(project_id: str, path: str = "") -> Dict[str, Any]:
        """Get file tree structure"""
        project = BuildService.get_project(project_id)
        project_path = Path(project["path"])
        
        if path:
            current_path = project_path / path
        else:
            current_path = project_path
        
        if not current_path.exists():
            raise HTTPException(status_code=404, detail="Path not found")
        
        tree = {
            "path": str(current_path.relative_to(project_path)),
            "name": current_path.name or "root",
            "type": "directory" if current_path.is_dir() else "file",
            "children": [] if current_path.is_file() else []
        }
        
        if current_path.is_dir():
            try:
                for item in sorted(current_path.iterdir()):
                    if item.is_dir():
                        tree["children"].append({
                            "path": str(item.relative_to(project_path)),
                            "name": item.name,
                            "type": "directory",
                            "children": []
                        })
                    else:
                        tree["children"].append({
                            "path": str(item.relative_to(project_path)),
                            "name": item.name,
                            "type": "file"
                        })
            except PermissionError:
                pass
        
        return tree
    
    @staticmethod
    def read_file(project_id: str, file_path: str) -> str:
        """Read file content"""
        project = BuildService.get_project(project_id)
        project_path = Path(project["path"])
        full_path = project_path / file_path
        
        # Security: prevent directory traversal
        if not full_path.resolve().is_relative_to(project_path.resolve()):
            raise HTTPException(status_code=403, detail="Access denied")
        
        if not full_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        try:
            return full_path.read_text()
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    @staticmethod
    def create_file(project_id: str, file_path: str, content: str = "", is_directory: bool = False) -> Dict[str, str]:
        """Create file or directory"""
        project = BuildService.get_project(project_id)
        project_path = Path(project["path"])
        full_path = project_path / file_path
        
        # Security: prevent directory traversal
        if not full_path.resolve().is_relative_to(project_path.resolve()):
            raise HTTPException(status_code=403, detail="Access denied")
        
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        if is_directory:
            full_path.mkdir(exist_ok=True)
        else:
            full_path.write_text(content)
        
        # Update in-memory files
        if not is_directory:
            ACTIVE_PROJECTS[project_id]["files"][file_path] = content
        
        return {"path": file_path, "status": "created"}
    
    @staticmethod
    def update_file(project_id: str, file_path: str, content: str) -> Dict[str, str]:
        """Update file content"""
        project = BuildService.get_project(project_id)
        project_path = Path(project["path"])
        full_path = project_path / file_path
        
        # Security: prevent directory traversal
        if not full_path.resolve().is_relative_to(project_path.resolve()):
            raise HTTPException(status_code=403, detail="Access denied")
        
        if not full_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        try:
            full_path.write_text(content)
            ACTIVE_PROJECTS[project_id]["files"][file_path] = content
            return {"path": file_path, "status": "updated"}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    @staticmethod
    def delete_file(project_id: str, file_path: str) -> Dict[str, str]:
        """Delete file or directory"""
        project = BuildService.get_project(project_id)
        project_path = Path(project["path"])
        full_path = project_path / file_path
        
        # Security: prevent directory traversal
        if not full_path.resolve().is_relative_to(project_path.resolve()):
            raise HTTPException(status_code=403, detail="Access denied")
        
        if not full_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        try:
            if full_path.is_dir():
                shutil.rmtree(full_path)
            else:
                full_path.unlink()
            
            if file_path in ACTIVE_PROJECTS[project_id]["files"]:
                del ACTIVE_PROJECTS[project_id]["files"][file_path]
            
            return {"path": file_path, "status": "deleted"}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    @staticmethod
    async def execute_code(project_id: str, code: str, language: str, timeout: int = 30) -> Dict[str, Any]:
        """Execute code and return output"""
        if language not in ["python", "javascript", "shell"]:
            raise HTTPException(status_code=400, detail="Unsupported language")
        
        project = BuildService.get_project(project_id)
        project_path = Path(project["path"])
        
        try:
            if language == "python":
                result = await BuildService._execute_python(code, project_path, timeout)
            elif language == "javascript":
                result = await BuildService._execute_javascript(code, project_path, timeout)
            else:  # shell
                result = await BuildService._execute_shell(code, project_path, timeout)
            
            return result
        except asyncio.TimeoutError:
            return {"error": f"Execution timeout ({timeout}s)", "output": "", "code": 1}
        except Exception as e:
            return {"error": str(e), "output": "", "code": 1}
    
    @staticmethod
    async def _execute_python(code: str, project_path: Path, timeout: int) -> Dict[str, Any]:
        """Execute Python code"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        try:
            process = await asyncio.create_subprocess_exec(
                "python", temp_file,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(project_path)
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
                "output": stdout.decode() + stderr.decode(),
                "code": process.returncode,
                "error": None if process.returncode == 0 else "Process exited with code " + str(process.returncode)
            }
        finally:
            Path(temp_file).unlink()
    
    @staticmethod
    async def _execute_javascript(code: str, project_path: Path, timeout: int) -> Dict[str, Any]:
        """Execute JavaScript code"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        try:
            process = await asyncio.create_subprocess_exec(
                "node", temp_file,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(project_path)
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
                "output": stdout.decode() + stderr.decode(),
                "code": process.returncode,
                "error": None if process.returncode == 0 else "Process exited with code " + str(process.returncode)
            }
        finally:
            Path(temp_file).unlink()
    
    @staticmethod
    async def _execute_shell(code: str, project_path: Path, timeout: int) -> Dict[str, Any]:
        """Execute shell command"""
        process = await asyncio.create_subprocess_shell(
            code,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(project_path)
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
            "output": stdout.decode() + stderr.decode(),
            "code": process.returncode,
            "error": None if process.returncode == 0 else "Process exited with code " + str(process.returncode)
        }
    
    @staticmethod
    async def install_package(project_id: str, package: str, language: str) -> Dict[str, Any]:
        """Install a package"""
        if language not in ["python", "javascript"]:
            raise HTTPException(status_code=400, detail="Unsupported language")
        
        project = BuildService.get_project(project_id)
        project_path = Path(project["path"])
        
        try:
            if language == "python":
                cmd = ["pip", "install", package]
            else:  # javascript
                cmd = ["npm", "install", package]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(project_path)
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=60
            )
            
            return {
                "package": package,
                "language": language,
                "output": stdout.decode() + stderr.decode(),
                "code": process.returncode,
                "success": process.returncode == 0
            }
        except asyncio.TimeoutError:
            return {"error": "Installation timeout", "code": 1, "success": False}
        except Exception as e:
            return {"error": str(e), "code": 1, "success": False}
    
    @staticmethod
    def delete_project(project_id: str) -> Dict[str, str]:
        """Delete a project"""
        project = BuildService.get_project(project_id)
        project_path = Path(project["path"])
        
        try:
            if project_path.exists():
                shutil.rmtree(project_path)
            del ACTIVE_PROJECTS[project_id]
            return {"id": project_id, "status": "deleted"}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))


# API Routes

@router.post("/project/create", response_model=ProjectResponse)
async def create_project(request: ProjectRequest):
    """Create a new project"""
    project = BuildService.create_project(request.name, request.template)
    return ProjectResponse(**project)


@router.get("/project/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: str):
    """Get project details"""
    project = BuildService.get_project(project_id)
    return ProjectResponse(**project)


@router.get("/projects")
async def list_projects():
    """List all projects"""
    return BuildService.list_projects()


@router.get("/project/{project_id}/files")
async def get_file_tree(project_id: str, path: str = ""):
    """Get file tree"""
    return BuildService.get_file_tree(project_id, path)


@router.get("/project/{project_id}/file")
async def read_file(project_id: str, path: str):
    """Read file content"""
    content = BuildService.read_file(project_id, path)
    return {"path": path, "content": content}


@router.post("/project/{project_id}/file")
async def create_file(project_id: str, request: FileCreateRequest):
    """Create file or directory"""
    return BuildService.create_file(project_id, request.path, request.content, request.isDirectory)


@router.put("/project/{project_id}/file")
async def update_file(project_id: str, request: FileUpdateRequest):
    """Update file content"""
    return BuildService.update_file(project_id, request.path, request.content)


@router.delete("/project/{project_id}/file")
async def delete_file(project_id: str, path: str):
    """Delete file"""
    return BuildService.delete_file(project_id, path)


@router.post("/project/{project_id}/execute")
async def execute_code(project_id: str, request: ExecutionRequest):
    """Execute code"""
    result = await BuildService.execute_code(project_id, request.code, request.language, request.timeout)
    return result


@router.post("/project/{project_id}/package/install")
async def install_package(project_id: str, request: PackageInstallRequest):
    """Install a package"""
    result = await BuildService.install_package(project_id, request.package, request.language)
    return result


@router.delete("/project/{project_id}")
async def delete_project(project_id: str):
    """Delete project"""
    return BuildService.delete_project(project_id)
