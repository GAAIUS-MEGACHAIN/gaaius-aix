"""
Preview Orchestrator API Routes
Manage development servers for generated projects
"""

from fastapi import APIRouter, HTTPException, Depends
from pathlib import Path
from typing import Optional
import logging

from preview_orchestrator import (
    get_preview_orchestrator,
    PreviewOrchestrator,
    ServerType
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/preview", tags=["Preview Orchestrator"])

# ============== ENDPOINTS ==============

@router.post("/projects/{project_id}/start")
async def start_all_servers(
    project_id: str,
    backend_framework: str = "express",
    orchestrator: PreviewOrchestrator = Depends(get_preview_orchestrator)
):
    """
    Start both frontend and backend development servers for a project.
    
    Frontend: Vite dev server on port 5173
    Backend: Express or FastAPI on port 3001
    
    Returns:
        {
            "status": "success",
            "frontend": {"success": true, "url": "http://localhost:5173"},
            "backend": {"success": true, "url": "http://localhost:3001"}
        }
    """
    try:
        # Get project path from storage (would come from ProjectRuntimeService)
        # For now, derive it
        project_path = Path(f"generated_projects/{project_id}")
        
        if not project_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Project directory not found: {project_path}"
            )
        
        result = await orchestrator.start_all(
            project_id=project_id,
            project_path=project_path,
            backend_framework=backend_framework
        )
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting servers: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/projects/{project_id}/start/frontend")
async def start_frontend_server(
    project_id: str,
    port: Optional[int] = None,
    orchestrator: PreviewOrchestrator = Depends(get_preview_orchestrator)
):
    """Start only the frontend development server"""
    try:
        project_path = Path(f"generated_projects/{project_id}")
        if not project_path.exists():
            raise HTTPException(status_code=404, detail="Project not found")
        
        success, message = await orchestrator.start_frontend(
            project_id=project_id,
            project_path=project_path,
            port=port
        )
        
        if not success:
            raise HTTPException(status_code=500, detail=message)
        
        return {
            "status": "success",
            "project_id": project_id,
            "server_type": "frontend",
            "message": message,
            "url": orchestrator.projects[project_id].get_frontend_url()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting frontend: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/projects/{project_id}/start/backend")
async def start_backend_server(
    project_id: str,
    backend_framework: str = "express",
    port: Optional[int] = None,
    orchestrator: PreviewOrchestrator = Depends(get_preview_orchestrator)
):
    """Start only the backend development server"""
    try:
        project_path = Path(f"generated_projects/{project_id}")
        if not project_path.exists():
            raise HTTPException(status_code=404, detail="Project not found")
        
        success, message = await orchestrator.start_backend(
            project_id=project_id,
            project_path=project_path,
            backend_framework=backend_framework,
            port=port
        )
        
        if not success:
            raise HTTPException(status_code=500, detail=message)
        
        return {
            "status": "success",
            "project_id": project_id,
            "server_type": "backend",
            "framework": backend_framework,
            "message": message,
            "url": orchestrator.projects[project_id].get_backend_url()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting backend: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/projects/{project_id}/stop")
async def stop_all_servers(
    project_id: str,
    orchestrator: PreviewOrchestrator = Depends(get_preview_orchestrator)
):
    """Stop both frontend and backend servers"""
    try:
        result = await orchestrator.stop_all(project_id)
        
        return {
            "status": "success",
            "project_id": project_id,
            "frontend_stopped": result["frontend"],
            "backend_stopped": result["backend"]
        }
    
    except Exception as e:
        logger.error(f"Error stopping servers: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/projects/{project_id}/stop/frontend")
async def stop_frontend_server(
    project_id: str,
    orchestrator: PreviewOrchestrator = Depends(get_preview_orchestrator)
):
    """Stop only the frontend server"""
    try:
        success = await orchestrator.stop_frontend(project_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Frontend server not found")
        
        return {
            "status": "success",
            "project_id": project_id,
            "server_type": "frontend",
            "message": "Frontend server stopped"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error stopping frontend: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/projects/{project_id}/stop/backend")
async def stop_backend_server(
    project_id: str,
    orchestrator: PreviewOrchestrator = Depends(get_preview_orchestrator)
):
    """Stop only the backend server"""
    try:
        success = await orchestrator.stop_backend(project_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Backend server not found")
        
        return {
            "status": "success",
            "project_id": project_id,
            "server_type": "backend",
            "message": "Backend server stopped"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error stopping backend: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/projects/{project_id}/status")
async def get_server_status(
    project_id: str,
    orchestrator: PreviewOrchestrator = Depends(get_preview_orchestrator)
):
    """Get the current status of a project's servers"""
    status = orchestrator.get_project_status(project_id)
    
    if status is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return {
        "status": "success",
        "project": status
    }

@router.get("/projects")
async def list_running_projects(
    orchestrator: PreviewOrchestrator = Depends(get_preview_orchestrator)
):
    """List all running projects"""
    projects = orchestrator.list_running_projects()
    
    return {
        "status": "success",
        "count": len(projects),
        "projects": projects
    }

@router.get("/health")
async def health_check(
    orchestrator: PreviewOrchestrator = Depends(get_preview_orchestrator)
):
    """Health check for preview orchestrator"""
    health = orchestrator.get_health_status()
    
    return health

@router.post("/shutdown")
async def shutdown_all(
    orchestrator: PreviewOrchestrator = Depends(get_preview_orchestrator)
):
    """Shutdown all running servers"""
    try:
        await orchestrator.stop_all_projects()
        
        return {
            "status": "success",
            "message": "All servers stopped"
        }
    
    except Exception as e:
        logger.error(f"Error shutting down: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# ============== PROXY ENDPOINT (For Preview in iframe) ==============

@router.get("/projects/{project_id}/preview")
async def get_preview(
    project_id: str,
    orchestrator: PreviewOrchestrator = Depends(get_preview_orchestrator)
):
    """
    Get preview information for embedding in iframe.
    
    Client-side can use this to embed in an iframe:
    <iframe src="http://localhost:5173" />
    
    Or with proxy if using same domain:
    <iframe src="/api/preview/projects/{project_id}/proxy" />
    """
    status = orchestrator.get_project_status(project_id)
    
    if not status:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if not status["both_running"]:
        raise HTTPException(
            status_code=400,
            detail="Servers not running. Start them first with POST /start"
        )
    
    return {
        "status": "success",
        "project_id": project_id,
        "preview_url": status["urls"]["frontend"],
        "api_url": status["urls"]["backend"],
        "can_preview": True,
        "instruction": f"Embed with: <iframe src='{status['urls']['frontend']}' />"
    }

@router.get("/info")
async def get_info():
    """Get information about preview orchestrator"""
    return {
        "name": "GAAIUS Preview Orchestrator",
        "version": "1.0.0",
        "description": "Manage development servers for generated projects",
        "capabilities": [
            "Start/stop Vite frontend dev server",
            "Start/stop Express/FastAPI backend server",
            "Monitor server health and status",
            "Manage multiple projects simultaneously",
            "Provide preview URLs for iframe embedding"
        ],
        "endpoints": {
            "POST /api/preview/projects/{id}/start": "Start both servers",
            "POST /api/preview/projects/{id}/start/frontend": "Start frontend only",
            "POST /api/preview/projects/{id}/start/backend": "Start backend only",
            "POST /api/preview/projects/{id}/stop": "Stop both servers",
            "GET /api/preview/projects/{id}/status": "Get server status",
            "GET /api/preview/projects/{id}/preview": "Get preview URL",
            "GET /api/preview/projects": "List all running projects",
            "GET /api/preview/health": "Health check",
            "POST /api/preview/shutdown": "Shutdown all servers"
        }
    }

if __name__ == "__main__":
    print("This is a FastAPI router module. Import and include in your FastAPI app.")
    print("Example: app.include_router(router)")
