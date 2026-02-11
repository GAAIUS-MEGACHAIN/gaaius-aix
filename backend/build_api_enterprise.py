"""
ENTERPRISE BUILD SYSTEM API
Production-grade REST API for real binary compilation
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import logging
from pathlib import Path
import json

from build_system_enterprise import (
    BuildOrchestrator,
    BuildConfig,
    SystemValidator,
    BuildStatus,
    BuildJob
)


# ============================================================================
# LOGGING
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# MODELS
# ============================================================================

class BuildRequest(BaseModel):
    """Build request model"""
    project_id: str
    project_name: str
    framework: str
    platforms: List[str]
    version: str = "1.0.0"
    build_type: str = "release"
    source_dir: str = "./"
    env_vars: Dict[str, str] = Field(default_factory=dict)


class SubmitBuildResponse(BaseModel):
    """Submit build response"""
    success: bool
    job_id: Optional[str] = None
    message: str


class BuildJobResponse(BaseModel):
    """Build job response"""
    job_id: str
    project_id: str
    status: str
    progress: int
    artifacts: List[Dict] = Field(default_factory=list)
    error_message: str = ""
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    duration_seconds: int = 0


class SystemCheckResponse(BaseModel):
    """System check response"""
    nodejs: Dict[str, Any]
    npm: Dict[str, Any]
    cargo: Dict[str, Any]
    docker: Dict[str, Any]
    ready_for_builds: bool


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    uptime_seconds: int


# ============================================================================
# FASTAPI APP
# ============================================================================

app = FastAPI(
    title="Enterprise Build System API",
    description="Production-grade real binary compilation for multiple frameworks and platforms",
    version="1.0.0"
)

# Global orchestrator
orchestrator = BuildOrchestrator(
    artifact_dir="./artifacts",
    jobs_file="build_jobs.json"
)

# Start time for uptime tracking
import time
start_time = time.time()


# ============================================================================
# HEALTH & SYSTEM CHECK
# ============================================================================

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "uptime_seconds": int(time.time() - start_time)
    }


@app.get("/api/system/check", response_model=SystemCheckResponse)
async def system_check():
    """Check system requirements"""
    nodejs_ok, nodejs_v = SystemValidator.check_nodejs()
    npm_ok, npm_v = SystemValidator.check_npm()
    cargo_ok, cargo_v = SystemValidator.check_cargo()
    docker_ok, docker_v = SystemValidator.check_docker()
    
    return {
        "nodejs": {"available": nodejs_ok, "version": nodejs_v},
        "npm": {"available": npm_ok, "version": npm_v},
        "cargo": {"available": cargo_ok, "version": cargo_v},
        "docker": {"available": docker_ok, "version": docker_v},
        "ready_for_builds": nodejs_ok and npm_ok
    }


# ============================================================================
# BUILD SUBMISSION
# ============================================================================

@app.post("/api/builds/submit", response_model=SubmitBuildResponse)
async def submit_build(request: BuildRequest):
    """Submit a build job"""
    try:
        logger.info(f"Build submission: {request.project_id}")
        
        config = BuildConfig(
            project_id=request.project_id,
            project_name=request.project_name,
            framework=request.framework,
            platforms=request.platforms,
            version=request.version,
            build_type=request.build_type,
            source_dir=request.source_dir,
            env_vars=request.env_vars
        )
        
        success, job_id, message = orchestrator.submit_build(config)
        
        if not success:
            raise HTTPException(status_code=400, detail=message)
        
        return {
            "success": True,
            "job_id": job_id,
            "message": message
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting build: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# BUILD EXECUTION
# ============================================================================

async def execute_build_background(job_id: str, config: BuildConfig, project_path: str):
    """Execute build in background"""
    try:
        logger.info(f"Starting build execution: {job_id}")
        orchestrator.execute_build(job_id, config, project_path)
    except Exception as e:
        logger.error(f"Background build failed: {str(e)}")
        if job_id in orchestrator.jobs:
            job = orchestrator.jobs[job_id]
            job.status = BuildStatus.FAILED.value
            job.error_message = str(e)
            orchestrator._save_jobs()


@app.post("/api/builds/{job_id}/execute")
async def execute_build(job_id: str, request: BuildRequest, background_tasks: BackgroundTasks):
    """Start build execution"""
    try:
        if job_id not in orchestrator.jobs:
            raise HTTPException(status_code=404, detail="Job not found")
        
        logger.info(f"Executing build: {job_id}")
        
        config = BuildConfig(
            project_id=request.project_id,
            project_name=request.project_name,
            framework=request.framework,
            platforms=request.platforms,
            version=request.version,
            build_type=request.build_type,
            source_dir=request.source_dir,
            env_vars=request.env_vars
        )
        
        # Execute in background
        background_tasks.add_task(
            execute_build_background,
            job_id=job_id,
            config=config,
            project_path=request.source_dir
        )
        
        return {
            "success": True,
            "message": "Build execution started",
            "job_id": job_id
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing build: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# BUILD STATUS & INFORMATION
# ============================================================================

@app.get("/api/builds/{job_id}/status", response_model=BuildJobResponse)
async def get_build_status(job_id: str):
    """Get build status"""
    try:
        status = orchestrator.get_job_status(job_id)
        if not status:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return status
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/builds/{job_id}/logs")
async def get_build_logs(job_id: str):
    """Get build logs"""
    try:
        status = orchestrator.get_job_status(job_id)
        if not status:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return {
            "job_id": job_id,
            "logs": status["logs"],
            "status": status["status"]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting logs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/builds/{job_id}/artifacts")
async def get_build_artifacts(job_id: str):
    """Get build artifacts"""
    try:
        status = orchestrator.get_job_status(job_id)
        if not status:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return {
            "job_id": job_id,
            "artifacts": status["artifacts"],
            "count": len(status["artifacts"])
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting artifacts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# BUILD MANAGEMENT
# ============================================================================

@app.post("/api/builds/{job_id}/cancel")
async def cancel_build(job_id: str):
    """Cancel build"""
    try:
        success = orchestrator.cancel_build(job_id)
        if not success:
            raise HTTPException(status_code=400, detail="Could not cancel build")
        
        return {
            "success": True,
            "message": "Build cancelled"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling build: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/builds/active")
async def get_active_builds():
    """Get all active builds"""
    try:
        active = [
            job.to_dict()
            for job in orchestrator.jobs.values()
            if job.status == BuildStatus.BUILDING.value
        ]
        return {
            "active_builds": active,
            "count": len(active)
        }
    
    except Exception as e:
        logger.error(f"Error getting active builds: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/builds/history")
async def get_build_history(limit: int = 50, project_id: Optional[str] = None):
    """Get build history"""
    try:
        jobs = list(orchestrator.jobs.values())
        
        if project_id:
            jobs = [j for j in jobs if j.project_id == project_id]
        
        jobs = sorted(jobs, key=lambda x: x.created_at, reverse=True)[:limit]
        
        return {
            "builds": [j.to_dict() for j in jobs],
            "count": len(jobs)
        }
    
    except Exception as e:
        logger.error(f"Error getting history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ARTIFACT DOWNLOADS
# ============================================================================

@app.get("/api/artifacts/{artifact_id}/download")
async def download_artifact(artifact_id: str):
    """Download artifact"""
    try:
        artifact = orchestrator.artifact_storage.get_artifact(artifact_id)
        if not artifact:
            raise HTTPException(status_code=404, detail="Artifact not found")
        
        file_path = Path(artifact["file_path"])
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Artifact file not found")
        
        return FileResponse(
            path=file_path,
            filename=artifact["file_name"],
            media_type=artifact["mime_type"]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading artifact: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ERROR HANDLING
# ============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


# ============================================================================
# STARTUP
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Startup event"""
    logger.info("=" * 60)
    logger.info("ENTERPRISE BUILD SYSTEM API STARTING")
    logger.info("=" * 60)
    
    # System check
    nodejs_ok, nodejs_v = SystemValidator.check_nodejs()
    npm_ok, npm_v = SystemValidator.check_npm()
    
    logger.info(f"Node.js: {'✓' if nodejs_ok else '✗'} {nodejs_v}")
    logger.info(f"npm: {'✓' if npm_ok else '✗'} {npm_v}")
    
    if nodejs_ok and npm_ok:
        logger.info("✓ System ready for builds")
    else:
        logger.warning("⚠ Missing dependencies - some builds may fail")


# ============================================================================
# SHUTDOWN
# ============================================================================

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event"""
    logger.info("Build system API shutting down")


if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting Enterprise Build System API")
    logger.info("Open browser: http://127.0.0.1:8000/docs")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
