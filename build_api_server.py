#!/usr/bin/env python3
"""
Standalone Build System API Server
No dependencies on complex server setup
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
import logging
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / 'backend'))

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import build system
from build_system_simple import SimpleBuildCoordinator, BuildConfig, BuildStatus

# Create FastAPI app
app = FastAPI(title="GAAIUS Build System API", version="1.0.0")

# Initialize build coordinator
build_coordinator = SimpleBuildCoordinator(output_dir="./artifacts")

# Request models
class BuildRequestModel(BaseModel):
    """Build request"""
    project_id: str
    project_name: str
    framework: str
    platforms: List[str]
    version: str = "1.0.0"
    build_type: str = "release"


# Routes

@app.post("/api/builds/submit")
async def submit_build(request: BuildRequestModel):
    """Submit a build request"""
    try:
        config = BuildConfig(
            project_id=request.project_id,
            project_name=request.project_name,
            framework=request.framework,
            platforms=request.platforms,
            version=request.version,
            build_type=request.build_type
        )
        
        job_id = build_coordinator.submit_build_request(config)
        
        return {
            "status": "submitted",
            "job_id": job_id,
            "message": f"Build job {job_id} created"
        }
    except Exception as e:
        logger.error(f"Error submitting build: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/builds/{job_id}/execute")
async def execute_build(job_id: str, request: BuildRequestModel):
    """Execute a build job"""
    try:
        # Get config from request
        config = BuildConfig(
            project_id=request.project_id,
            project_name=request.project_name,
            framework=request.framework,
            platforms=request.platforms,
            version=request.version,
            build_type=request.build_type
        )
        
        # Execute build
        success = build_coordinator.execute_build(job_id, config, "./")
        
        if success:
            return {
                "status": "completed",
                "job_id": job_id,
                "message": "Build executed successfully"
            }
        else:
            return {
                "status": "failed",
                "job_id": job_id,
                "message": "Build execution failed"
            }, 400
    except Exception as e:
        logger.error(f"Error executing build: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/builds/{job_id}/status")
async def get_build_status(job_id: str):
    """Get build status"""
    try:
        status = build_coordinator.get_job_status(job_id)
        
        if not status:
            raise HTTPException(status_code=404, detail=f"Build job {job_id} not found")
        
        return {
            "job_id": job_id,
            "status": status['status'],
            "progress": status['progress'],
            "artifacts": status['artifacts'],
            "created_at": status['created_at'],
            "completed_at": status['completed_at']
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting build status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/builds/{job_id}/logs")
async def get_build_logs(job_id: str):
    """Get build logs"""
    try:
        logs = build_coordinator.get_job_logs(job_id)
        return {
            "job_id": job_id,
            "logs": logs
        }
    except Exception as e:
        logger.error(f"Error getting build logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/builds/{job_id}/cancel")
async def cancel_build(job_id: str):
    """Cancel a build"""
    try:
        success = build_coordinator.cancel_build(job_id)
        
        if success:
            return {
                "status": "cancelled",
                "job_id": job_id,
                "message": "Build cancelled"
            }
        else:
            raise HTTPException(status_code=400, detail="Build cannot be cancelled")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling build: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/builds/active")
async def get_active_builds():
    """Get active builds"""
    try:
        active = build_coordinator.get_active_builds()
        return {"active_builds": active}
    except Exception as e:
        logger.error(f"Error getting active builds: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/builds/history")
async def get_build_history(limit: int = 50):
    """Get build history"""
    try:
        history = build_coordinator.get_build_history(limit=limit)
        return {"history": history}
    except Exception as e:
        logger.error(f"Error getting build history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "GAAIUS Build System",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    logger.info("Starting GAAIUS Build System API on http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=False)
