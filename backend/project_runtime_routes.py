"""
GAAIUS Project Runtime API Routes
FastAPI router for project generation, management, and deployment endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query
from typing import Optional
import logging
import asyncio

from project_runtime_integration import (
    ProjectRuntimeService,
    ProjectGenerationRequest,
    ProjectGenerationResponse,
    get_project_runtime_service,
    convert_blueprint_for_runtime
)

logger = logging.getLogger(__name__)

# Create router with /api prefix
router = APIRouter(prefix="/api/runtime", tags=["Project Runtime"])

# ============== ENDPOINTS ==============

@router.post("/projects/generate", response_model=ProjectGenerationResponse)
async def generate_project(
    request: ProjectGenerationRequest,
    service: ProjectRuntimeService = Depends(get_project_runtime_service)
) -> ProjectGenerationResponse:
    """
    Generate a complete full-stack project from a blueprint.
    
    This endpoint orchestrates:
    1. Scaffold generation (directory structure + configs)
    2. Frontend runtime (React components)
    3. Backend runtime (Express/FastAPI APIs)
    4. Dependency installation (npm/pip)
    5. Project manifest creation
    
    Returns a project ready to run with `npm run dev` and `npm run dev` (backend).
    
    Example blueprint:
    ```json
    {
      "app_type": "saas_dashboard",
      "pages": ["Dashboard", "Analytics", "Settings"],
      "features": ["auth", "search", "notifications"],
      "layout": {"type": "sidebar"}
    }
    ```
    """
    logger.info(f"Generating project: {request.project_name}")
    try:
        response = await service.generate_project(request)
        return response
    except Exception as e:
        logger.error(f"Project generation failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Project generation failed: {str(e)}"
        )

@router.get("/projects/{project_id}")
async def get_project(
    project_id: str,
    service: ProjectRuntimeService = Depends(get_project_runtime_service)
):
    """Get project metadata and status"""
    project = await service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return {
        "status": "success",
        "project": {
            "id": project.project_id,
            "name": project.project_name,
            "path": project.project_path,
            "type": project.project_type,
            "frontend_framework": project.frontend_framework,
            "backend_framework": project.backend_framework,
            "database": project.database,
            "status": project.status,
            "created_at": project.created_at,
            "updated_at": project.updated_at,
            "generation_time_ms": project.generation_time_ms,
            "error_message": project.error_message
        }
    }

@router.get("/projects")
async def list_projects(
    status: Optional[str] = Query(None, description="Filter by status: ready, running, error"),
    limit: int = Query(50, ge=1, le=500),
    service: ProjectRuntimeService = Depends(get_project_runtime_service)
):
    """List all projects, optionally filtered by status"""
    projects = await service.list_projects()
    
    # Filter by status if provided
    if status:
        projects = [p for p in projects if p.status == status]
    
    # Limit results
    projects = projects[-limit:]
    
    return {
        "status": "success",
        "count": len(projects),
        "projects": [
            {
                "id": p.project_id,
                "name": p.project_name,
                "type": p.project_type,
                "status": p.status,
                "created_at": p.created_at,
                "generation_time_ms": p.generation_time_ms
            }
            for p in projects
        ]
    }

@router.post("/projects/{project_id}/start-servers")
async def start_dev_servers(
    project_id: str,
    background_tasks: BackgroundTasks,
    service: ProjectRuntimeService = Depends(get_project_runtime_service)
):
    """
    Start development servers for a project.
    
    Starts:
    - Frontend: Vite dev server on port 5173
    - Backend: Express/FastAPI dev server on port 3001
    
    Run in background to avoid blocking the response.
    """
    result = await service.start_dev_servers(project_id)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@router.get("/projects/{project_id}/structure")
async def get_project_structure(
    project_id: str,
    service: ProjectRuntimeService = Depends(get_project_runtime_service)
):
    """Get the directory structure of a project"""
    result = await service.get_project_structure(project_id)
    if result["status"] == "error":
        raise HTTPException(status_code=404, detail=result["message"])
    return result

@router.delete("/projects/{project_id}")
async def delete_project(
    project_id: str,
    service: ProjectRuntimeService = Depends(get_project_runtime_service)
):
    """Delete a project and its generated files"""
    success = await service.delete_project(project_id)
    if not success:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return {
        "status": "success",
        "message": f"Project {project_id} deleted successfully"
    }

@router.post("/projects/{project_id}/rebuild")
async def rebuild_project(
    project_id: str,
    service: ProjectRuntimeService = Depends(get_project_runtime_service)
):
    """
    Rebuild a project (reinstall dependencies, regenerate files).
    
    Useful if the project gets corrupted or dependencies need to be updated.
    """
    project = await service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Create a new request from stored blueprint
    request = ProjectGenerationRequest(
        project_id=project_id,
        project_name=project.project_name,
        blueprint=project.blueprint,
        project_type=project.project_type,
        frontend_framework=project.frontend_framework,
        backend_framework=project.backend_framework,
        database=project.database,
        use_typescript=True,
        include_docker=True,
        include_github_actions=True
    )
    
    # Regenerate
    response = await service.generate_project(request)
    return response

@router.get("/projects/{project_id}/logs")
async def get_project_logs(
    project_id: str,
    service: ProjectRuntimeService = Depends(get_project_runtime_service)
):
    """Get generation logs for a project"""
    project = await service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # TODO: Implement log storage and retrieval
    return {
        "status": "success",
        "project_id": project_id,
        "logs": []  # Would be populated from storage
    }

@router.post("/projects/{project_id}/export")
async def export_project(
    project_id: str,
    format: str = Query("zip", regex="^(zip|docker|github|vercel)$"),
    service: ProjectRuntimeService = Depends(get_project_runtime_service)
):
    """
    Export a project in various formats.
    
    Formats:
    - zip: Download as ZIP file
    - docker: Prepare Docker deployment files
    - github: Create GitHub repository
    - vercel: Deploy to Vercel
    """
    project = await service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # TODO: Implement export functionality for each format
    return {
        "status": "success",
        "message": f"Export to {format} will be available soon",
        "format": format,
        "project_id": project_id
    }

@router.get("/projects/{project_id}/preview")
async def get_preview_url(
    project_id: str,
    service: ProjectRuntimeService = Depends(get_project_runtime_service)
):
    """
    Get preview URL for a running project.
    
    If the project has dev servers running, returns the preview URL
    where the application can be viewed in a browser.
    """
    project = await service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if project.status != "running":
        raise HTTPException(
            status_code=400,
            detail=f"Project is {project.status}, must be running. Start servers first."
        )
    
    return {
        "status": "success",
        "preview_url": "http://localhost:5173",
        "api_url": "http://localhost:3001",
        "project_id": project_id,
        "message": "Project is running. Open preview URL in your browser."
    }

# ============== HEALTH & INFO ==============

@router.get("/health")
async def health_check(service: ProjectRuntimeService = Depends(get_project_runtime_service)):
    """Health check for the runtime service"""
    projects = await service.list_projects()
    running = len([p for p in projects if p.status == "running"])
    
    return {
        "status": "healthy",
        "total_projects": len(projects),
        "running_projects": running,
        "service": "ProjectRuntimeService"
    }

@router.get("/info")
async def get_info():
    """Get information about the runtime service"""
    return {
        "name": "GAAIUS Project Runtime",
        "version": "1.0.0",
        "description": "Generate full-stack applications from blueprints",
        "capabilities": [
            "Project generation (scaffold + frontend + backend)",
            "Dependency installation",
            "Dev server management",
            "Project export and deployment",
            "Live preview with iframe proxy"
        ],
        "supported_frameworks": {
            "frontend": ["react", "next"],
            "backend": ["express", "fastapi"],
            "database": ["postgresql", "mongodb", "sqlite"]
        },
        "endpoints": {
            "POST /api/runtime/projects/generate": "Generate a new project",
            "GET /api/runtime/projects": "List all projects",
            "GET /api/runtime/projects/{id}": "Get project details",
            "POST /api/runtime/projects/{id}/start-servers": "Start dev servers",
            "GET /api/runtime/projects/{id}/structure": "Get project structure",
            "DELETE /api/runtime/projects/{id}": "Delete a project",
            "POST /api/runtime/projects/{id}/rebuild": "Rebuild a project",
            "GET /api/runtime/projects/{id}/preview": "Get preview URL",
            "POST /api/runtime/projects/{id}/export": "Export project",
        }
    }

if __name__ == "__main__":
    print("This is a FastAPI router module. Import and include in your FastAPI app.")
    print("Example: app.include_router(router)")
