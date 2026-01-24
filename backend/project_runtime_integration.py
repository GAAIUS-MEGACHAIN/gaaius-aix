"""
GAAIUS Project Runtime Integration
Bridges ProjectRuntime systems with FastAPI server and gaaius_builder
"""

import asyncio
import os
import json
import uuid
import logging
from pathlib import Path
from typing import Dict, Optional, Any, List
from datetime import datetime, timezone
from pydantic import BaseModel, Field

from project_runtime import ProjectRuntime, ProjectRuntimeConfig
from scaffold_generator import ScaffoldGenerator, ScaffoldConfig
from frontend_runtime_generator import FrontendRuntimeGenerator
from backend_runtime_generator import BackendRuntimeGenerator
from gaaius_builder import GaalusBuilder

logger = logging.getLogger(__name__)

# ============== PROJECT GENERATION MODELS ==============

class ProjectGenerationRequest(BaseModel):
    """Request model for project generation"""
    project_name: str = Field(..., min_length=1, max_length=100)
    project_id: Optional[str] = Field(None)
    blueprint: Dict[str, Any] = Field(...)
    project_type: str = Field(default="fullstack", pattern="^(fullstack|frontend-only|backend-only)$")
    frontend_framework: str = Field(default="react", pattern="^(react|next)$")
    backend_framework: str = Field(default="express", pattern="^(express|fastapi)$")
    database: str = Field(default="postgresql", pattern="^(postgresql|mongodb|sqlite)$")
    use_typescript: bool = Field(default=True)
    include_docker: bool = Field(default=True)
    include_github_actions: bool = Field(default=True)
    
class ProjectGenerationResponse(BaseModel):
    """Response model for project generation"""
    status: str = Field(..., description="success or error")
    project_id: str
    project_name: str
    project_path: str
    blueprint_path: str
    manifest_path: str
    steps: List[str] = Field(default_factory=list)
    message: str
    
class ProjectMetadata(BaseModel):
    """Project metadata stored in MongoDB"""
    project_id: str
    project_name: str
    project_path: str
    blueprint: Dict[str, Any]
    project_type: str
    frontend_framework: str
    backend_framework: str
    database: str
    created_at: datetime
    updated_at: datetime
    status: str = Field(default="generating")  # generating, ready, running, error
    generation_time_ms: int = 0
    error_message: Optional[str] = None
    dev_server_port: Optional[int] = None
    api_server_port: Optional[int] = None

# ============== PROJECT RUNTIME SERVICE ==============

class ProjectRuntimeService:
    """Service that manages project generation and lifecycle"""
    
    def __init__(self, base_path: str = "generated_projects"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.runtime = ProjectRuntime()
        self.projects: Dict[str, ProjectMetadata] = {}
        logger.info(f"ProjectRuntimeService initialized with base_path: {self.base_path}")
    
    async def generate_project(
        self,
        request: ProjectGenerationRequest,
        db=None
    ) -> ProjectGenerationResponse:
        """
        Generate a complete project from blueprint
        
        Args:
            request: ProjectGenerationRequest
            db: MongoDB database connection (optional)
        
        Returns:
            ProjectGenerationResponse with project details
        """
        start_time = datetime.now(timezone.utc)
        project_id = request.project_id or str(uuid.uuid4())
        project_path = self.base_path / project_id
        
        logger.info(f"Starting project generation: {project_id}")
        
        try:
            # Create config for ProjectRuntime
            config = ProjectRuntimeConfig(
                project_id=project_id,
                project_name=request.project_name,
                project_path=str(project_path),
                blueprint=request.blueprint,
                project_type=request.project_type,
                frontend_framework=request.frontend_framework,
                backend_framework=request.backend_framework,
                database=request.database,
                use_typescript=request.use_typescript,
                include_docker=request.include_docker,
                include_github_actions=request.include_github_actions
            )
            
            # Generate project asynchronously
            result = await self.runtime.generate_project(config)
            
            generation_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            
            # Create metadata
            metadata = ProjectMetadata(
                project_id=project_id,
                project_name=request.project_name,
                project_path=str(project_path),
                blueprint=request.blueprint,
                project_type=request.project_type,
                frontend_framework=request.frontend_framework,
                backend_framework=request.backend_framework,
                database=request.database,
                created_at=start_time,
                updated_at=datetime.now(timezone.utc),
                status="ready",
                generation_time_ms=int(generation_time)
            )
            
            # Store in memory
            self.projects[project_id] = metadata
            
            # Save to MongoDB if available
            if db:
                await self._save_to_db(db, metadata)
            
            # Save manifest
            blueprint_path = project_path / "gaaius.json"
            manifest_path = project_path / "gaaius_manifest.json"
            
            logger.info(f"Project generated successfully: {project_id}")
            
            return ProjectGenerationResponse(
                status="success",
                project_id=project_id,
                project_name=request.project_name,
                project_path=str(project_path),
                blueprint_path=str(blueprint_path),
                manifest_path=str(manifest_path),
                steps=result.get("steps", []),
                message=f"Project '{request.project_name}' generated successfully in {generation_time:.0f}ms"
            )
        
        except Exception as e:
            logger.error(f"Project generation failed: {str(e)}", exc_info=True)
            
            # Create error metadata
            metadata = ProjectMetadata(
                project_id=project_id,
                project_name=request.project_name,
                project_path=str(project_path),
                blueprint=request.blueprint,
                project_type=request.project_type,
                frontend_framework=request.frontend_framework,
                backend_framework=request.backend_framework,
                database=request.database,
                created_at=start_time,
                updated_at=datetime.now(timezone.utc),
                status="error",
                error_message=str(e)
            )
            self.projects[project_id] = metadata
            
            if db:
                await self._save_to_db(db, metadata)
            
            return ProjectGenerationResponse(
                status="error",
                project_id=project_id,
                project_name=request.project_name,
                project_path=str(project_path),
                blueprint_path="",
                manifest_path="",
                message=f"Project generation failed: {str(e)}"
            )
    
    async def _save_to_db(self, db, metadata: ProjectMetadata):
        """Save project metadata to MongoDB"""
        try:
            projects_collection = db["projects"]
            await projects_collection.insert_one(metadata.dict(by_alias=True))
            logger.info(f"Project metadata saved to DB: {metadata.project_id}")
        except Exception as e:
            logger.error(f"Failed to save project metadata to DB: {str(e)}")
    
    async def get_project(self, project_id: str) -> Optional[ProjectMetadata]:
        """Get project metadata"""
        return self.projects.get(project_id)
    
    async def list_projects(self) -> List[ProjectMetadata]:
        """List all projects"""
        return list(self.projects.values())
    
    async def delete_project(self, project_id: str) -> bool:
        """Delete a project"""
        try:
            project = self.projects.get(project_id)
            if not project:
                return False
            
            # Delete directory
            project_path = Path(project.project_path)
            if project_path.exists():
                import shutil
                shutil.rmtree(project_path)
            
            # Remove from memory
            del self.projects[project_id]
            logger.info(f"Project deleted: {project_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete project: {str(e)}")
            return False
    
    async def start_dev_servers(self, project_id: str) -> Dict[str, Any]:
        """Start dev servers for a project"""
        try:
            project = self.projects.get(project_id)
            if not project:
                return {"status": "error", "message": "Project not found"}
            
            if project.status != "ready":
                return {"status": "error", "message": f"Project status is {project.status}, must be ready"}
            
            project_path = Path(project.project_path)
            instructions = self.runtime.start_dev_server(str(project_path))
            
            project.updated_at = datetime.now(timezone.utc)
            project.status = "running"
            
            return {
                "status": "success",
                "project_id": project_id,
                "instructions": instructions,
                "frontend_url": "http://localhost:5173",
                "api_url": "http://localhost:3001",
                "message": "Dev servers started. Check instructions for details."
            }
        except Exception as e:
            logger.error(f"Failed to start dev servers: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def get_project_structure(self, project_id: str) -> Dict[str, Any]:
        """Get the file structure of a project"""
        try:
            project = self.projects.get(project_id)
            if not project:
                return {"status": "error", "message": "Project not found"}
            
            project_path = Path(project.project_path)
            structure = self._build_tree(project_path)
            
            return {
                "status": "success",
                "project_id": project_id,
                "structure": structure
            }
        except Exception as e:
            logger.error(f"Failed to get project structure: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def _build_tree(self, path: Path, prefix: str = "", max_depth: int = 4, current_depth: int = 0) -> Dict:
        """Build directory tree structure"""
        if current_depth >= max_depth:
            return {}
        
        try:
            tree = {}
            items = sorted(path.iterdir())
            
            # Filter out common non-essential directories
            skip_dirs = {'.git', '.next', 'dist', 'build', '__pycache__', 'node_modules', '.venv', 'venv'}
            items = [i for i in items if i.name not in skip_dirs]
            
            for item in items:
                if item.is_file():
                    tree[item.name] = {"type": "file", "size": item.stat().st_size}
                elif item.is_dir():
                    tree[item.name] = {"type": "dir", "children": self._build_tree(item, current_depth + 1)}
            
            return tree
        except Exception as e:
            logger.error(f"Error building tree for {path}: {str(e)}")
            return {}

# ============== GLOBAL SERVICE INSTANCE ==============

project_runtime_service: Optional[ProjectRuntimeService] = None

def get_project_runtime_service() -> ProjectRuntimeService:
    """Get or create the project runtime service"""
    global project_runtime_service
    if project_runtime_service is None:
        project_runtime_service = ProjectRuntimeService()
    return project_runtime_service

# ============== HELPER FUNCTIONS ==============

async def convert_blueprint_for_runtime(gaaius_blueprint: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert a GAAIUS blueprint to ProjectRuntime blueprint format
    This bridges gaaius_builder output to ProjectRuntime input
    """
    return {
        "app_type": gaaius_blueprint.get("app_type", "custom"),
        "app_name": gaaius_blueprint.get("app_name", "MyApp"),
        "description": gaaius_blueprint.get("description", ""),
        "pages": gaaius_blueprint.get("pages", []),
        "features": gaaius_blueprint.get("features", []),
        "layout": gaaius_blueprint.get("layout", {}),
        "theme": gaaius_blueprint.get("theme", "light"),
        "database_models": gaaius_blueprint.get("database_models", []),
        "api_endpoints": gaaius_blueprint.get("api_endpoints", []),
    }

# ============== EXAMPLE USAGE ==============

async def example_generation():
    """Example of how to use ProjectRuntimeService"""
    service = get_project_runtime_service()
    
    # Create a request
    request = ProjectGenerationRequest(
        project_name="My SaaS App",
        blueprint={
            "app_type": "saas_dashboard",
            "pages": ["Dashboard", "Analytics", "Settings"],
            "features": ["auth", "search", "notifications"],
            "layout": {"type": "sidebar"}
        },
        project_type="fullstack",
        frontend_framework="react",
        backend_framework="express",
        use_typescript=True
    )
    
    # Generate project
    response = await service.generate_project(request)
    print(json.dumps(response.dict(), indent=2))
    
    # Get project
    project = await service.get_project(response.project_id)
    print(f"\nProject status: {project.status}")
    print(f"Generated in: {project.generation_time_ms}ms")
    
    # List projects
    projects = await service.list_projects()
    print(f"\nTotal projects: {len(projects)}")
    
    # Start dev servers
    dev_result = await service.start_dev_servers(response.project_id)
    print(f"\nDev servers: {dev_result}")
    
    # Get structure
    structure = await service.get_project_structure(response.project_id)
    print(f"\nProject structure: {json.dumps(structure, indent=2)}")

if __name__ == "__main__":
    asyncio.run(example_generation())
