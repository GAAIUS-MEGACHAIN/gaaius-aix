"""
Content Generation Pipeline Routes
REST API for universal content generation across all platform services
"""

from fastapi import APIRouter, HTTPException, Query, Body, Depends, BackgroundTasks
from fastapi.responses import JSONResponse, StreamingResponse
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uuid

from content_generation_pipeline import (
    ContentGenerationPipeline,
    ContentGenerationRequest,
    ContentGenerationJob,
    GeneratedContent,
    ContentTemplate,
    BatchGenerationJob,
    ContentQualityMetrics,
    ContentType,
    GenerationStatus,
    ProcessingStage,
    AIProvider
)

# ============================================================================
# SERVICE INITIALIZATION
# ============================================================================

router = APIRouter(prefix="/content-generation", tags=["content-generation"])
pipeline_service = ContentGenerationPipeline()

# ============================================================================
# REQUEST ENDPOINTS
# ============================================================================

@router.post("/request/create")
async def create_generation_request(
    user_id: str = Body(...),
    content_type: str = Body(...),
    title: str = Body(...),
    prompt: str = Body(...),
    description: Optional[str] = Body(None),
    ai_provider: str = Body(default="groq"),
    style: Optional[str] = Body(None),
    duration: Optional[int] = Body(None),
    with_subtitles: bool = Body(default=False),
    with_transcript: bool = Body(default=False),
    auto_publish: bool = Body(default=False),
    tags: List[str] = Body(default_factory=list),
    priority: int = Body(default=5),
    service: ContentGenerationPipeline = Depends(lambda: pipeline_service)
) -> Dict[str, Any]:
    """Create content generation request"""
    try:
        request = ContentGenerationRequest(
            user_id=user_id,
            content_type=ContentType(content_type),
            title=title,
            prompt=prompt,
            description=description,
            ai_provider=AIProvider(ai_provider),
            style=style,
            duration=duration,
            with_subtitles=with_subtitles,
            with_transcript=with_transcript,
            auto_publish=auto_publish,
            tags=tags,
            priority=priority
        )
        
        created_request = await service.create_generation_request(request)
        
        return {
            "status": "success",
            "request": created_request.dict(),
            "message": "Content generation request created"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/request/{request_id}")
async def get_generation_request(
    request_id: str,
    service: ContentGenerationPipeline = Depends(lambda: pipeline_service)
) -> Dict[str, Any]:
    """Get generation request details"""
    request = await service.get_request(request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    return {
        "status": "success",
        "request": request.dict()
    }

@router.get("/requests")
async def list_user_requests(
    user_id: str = Query(...),
    service: ContentGenerationPipeline = Depends(lambda: pipeline_service)
) -> Dict[str, Any]:
    """List user's generation requests"""
    requests = await service.list_requests(user_id)
    
    return {
        "status": "success",
        "requests": [r.dict() for r in requests],
        "total": len(requests)
    }

# ============================================================================
# JOB MANAGEMENT ENDPOINTS
# ============================================================================

@router.post("/job/start")
async def start_generation_job(
    request_id: str = Body(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    service: ContentGenerationPipeline = Depends(lambda: pipeline_service)
) -> Dict[str, Any]:
    """Start content generation job"""
    try:
        # Create job
        job = await service.create_job(request_id)
        job = await service.start_job(job.id)
        
        # TODO: Add background task to process content
        # background_tasks.add_task(process_content_generation, job.id)
        
        return {
            "status": "success",
            "job": job.dict(),
            "message": "Content generation started"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/job/{job_id}")
async def get_job(
    job_id: str,
    service: ContentGenerationPipeline = Depends(lambda: pipeline_service)
) -> Dict[str, Any]:
    """Get job details and progress"""
    job = await service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {
        "status": "success",
        "job": job.dict()
    }

@router.get("/jobs")
async def list_user_jobs(
    user_id: str = Query(...),
    service: ContentGenerationPipeline = Depends(lambda: pipeline_service)
) -> Dict[str, Any]:
    """List user's generation jobs"""
    jobs = await service.get_user_jobs(user_id)
    
    return {
        "status": "success",
        "jobs": [j.dict() for j in jobs],
        "total": len(jobs)
    }

@router.post("/job/{job_id}/update-progress")
async def update_job_progress(
    job_id: str,
    progress: int = Body(...),
    stage: str = Body(...),
    log_message: Optional[str] = Body(None),
    service: ContentGenerationPipeline = Depends(lambda: pipeline_service)
) -> Dict[str, Any]:
    """Update job progress"""
    try:
        log_entry = {"message": log_message} if log_message else None
        job = await service.update_job_progress(
            job_id, 
            progress, 
            ProcessingStage(stage),
            log_entry
        )
        
        return {
            "status": "success",
            "job": job.dict(),
            "message": "Job progress updated"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/job/{job_id}/complete")
async def complete_job(
    job_id: str,
    output_url: str = Body(...),
    file_size: int = Body(default=0),
    duration: Optional[int] = Body(None),
    service: ContentGenerationPipeline = Depends(lambda: pipeline_service)
) -> Dict[str, Any]:
    """Mark job as complete"""
    try:
        job = await service.complete_job(
            job_id,
            output_url,
            file_size=file_size,
            duration=duration
        )
        
        return {
            "status": "success",
            "job": job.dict(),
            "message": "Job completed successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/job/{job_id}/fail")
async def fail_job(
    job_id: str,
    error_message: str = Body(...),
    service: ContentGenerationPipeline = Depends(lambda: pipeline_service)
) -> Dict[str, Any]:
    """Mark job as failed"""
    try:
        job = await service.fail_job(job_id, error_message)
        
        return {
            "status": "success",
            "job": job.dict(),
            "message": "Job marked as failed"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/job/{job_id}/cancel")
async def cancel_job(
    job_id: str,
    service: ContentGenerationPipeline = Depends(lambda: pipeline_service)
) -> Dict[str, Any]:
    """Cancel generation job"""
    try:
        job = await service.cancel_job(job_id)
        
        return {
            "status": "success",
            "job": job.dict(),
            "message": "Job cancelled"
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# ============================================================================
# CONTENT ENDPOINTS
# ============================================================================

@router.post("/content/register")
async def register_content(
    job_id: str = Body(...),
    request_id: str = Body(...),
    user_id: str = Body(...),
    content_type: str = Body(...),
    title: str = Body(...),
    url: str = Body(...),
    file_path: str = Body(...),
    file_size: int = Body(...),
    ai_provider: str = Body(...),
    model: str = Body(...),
    tags: List[str] = Body(default_factory=list),
    language: str = Body(default="en"),
    service: ContentGenerationPipeline = Depends(lambda: pipeline_service)
) -> Dict[str, Any]:
    """Register generated content"""
    try:
        content = GeneratedContent(
            job_id=job_id,
            request_id=request_id,
            user_id=user_id,
            content_type=ContentType(content_type),
            title=title,
            url=url,
            file_path=file_path,
            file_size=file_size,
            ai_provider=ai_provider,
            model_used=model,
            tags=tags,
            language=language,
            quality="high"
        )
        
        registered = await service.register_generated_content(content)
        
        return {
            "status": "success",
            "content": registered.dict(),
            "message": "Content registered"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/content/{content_id}")
async def get_content(
    content_id: str,
    service: ContentGenerationPipeline = Depends(lambda: pipeline_service)
) -> Dict[str, Any]:
    """Get content details"""
    content = await service.get_generated_content(content_id)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    return {
        "status": "success",
        "content": content.dict()
    }

@router.get("/content/job/{job_id}")
async def get_job_content(
    job_id: str,
    service: ContentGenerationPipeline = Depends(lambda: pipeline_service)
) -> Dict[str, Any]:
    """Get all content from job"""
    content_list = await service.get_content_by_job(job_id)
    
    return {
        "status": "success",
        "content": [c.dict() for c in content_list],
        "total": len(content_list)
    }

@router.post("/content/{content_id}/publish")
async def publish_content(
    content_id: str,
    platforms: List[str] = Body(default_factory=list),
    service: ContentGenerationPipeline = Depends(lambda: pipeline_service)
) -> Dict[str, Any]:
    """Publish content"""
    try:
        content = await service.publish_content(content_id, platforms)
        
        return {
            "status": "success",
            "content": content.dict(),
            "message": "Content published"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/content/{content_id}/stats")
async def update_content_stats(
    content_id: str,
    views: int = Body(default=0),
    likes: int = Body(default=0),
    downloads: int = Body(default=0),
    service: ContentGenerationPipeline = Depends(lambda: pipeline_service)
) -> Dict[str, Any]:
    """Update content engagement stats"""
    try:
        content = await service.update_content_stats(
            content_id,
            views=views,
            likes=likes,
            downloads=downloads
        )
        
        return {
            "status": "success",
            "content": content.dict()
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/library")
async def get_content_library(
    user_id: str = Query(...),
    service: ContentGenerationPipeline = Depends(lambda: pipeline_service)
) -> Dict[str, Any]:
    """Get user's content library"""
    library = await service.get_user_content_library(user_id)
    
    return {
        "status": "success",
        "library": library
    }

# ============================================================================
# TEMPLATE ENDPOINTS
# ============================================================================

@router.post("/template/create")
async def create_template(
    name: str = Body(...),
    description: str = Body(...),
    content_type: str = Body(...),
    prompt_template: str = Body(...),
    ai_provider: str = Body(...),
    model: str = Body(...),
    created_by: str = Body(...),
    service: ContentGenerationPipeline = Depends(lambda: pipeline_service)
) -> Dict[str, Any]:
    """Create content template"""
    try:
        template = ContentTemplate(
            name=name,
            description=description,
            content_type=ContentType(content_type),
            prompt_template=prompt_template,
            ai_provider=AIProvider(ai_provider),
            model=model,
            created_by=created_by
        )
        
        created = await service.create_template(template)
        
        return {
            "status": "success",
            "template": created.dict(),
            "message": "Template created"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/templates")
async def list_templates(
    content_type: Optional[str] = Query(None),
    service: ContentGenerationPipeline = Depends(lambda: pipeline_service)
) -> Dict[str, Any]:
    """List templates"""
    content_type_enum = ContentType(content_type) if content_type else None
    templates = await service.list_templates(content_type_enum)
    
    return {
        "status": "success",
        "templates": [t.dict() for t in templates],
        "total": len(templates)
    }

@router.get("/template/{template_id}")
async def get_template(
    template_id: str,
    service: ContentGenerationPipeline = Depends(lambda: pipeline_service)
) -> Dict[str, Any]:
    """Get template details"""
    template = await service.get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    await service.use_template(template_id)
    
    return {
        "status": "success",
        "template": template.dict()
    }

# ============================================================================
# BATCH ENDPOINTS
# ============================================================================

@router.post("/batch/create")
async def create_batch(
    user_id: str = Body(...),
    name: str = Body(...),
    description: str = Body(...),
    parallel_jobs: int = Body(default=3),
    service: ContentGenerationPipeline = Depends(lambda: pipeline_service)
) -> Dict[str, Any]:
    """Create batch generation job"""
    try:
        batch = BatchGenerationJob(
            user_id=user_id,
            name=name,
            description=description,
            parallel_jobs=parallel_jobs
        )
        
        created = await service.create_batch_job(batch)
        
        return {
            "status": "success",
            "batch": created.dict(),
            "message": "Batch job created"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/batch/{batch_id}/add")
async def add_to_batch(
    batch_id: str,
    request_id: str = Body(...),
    service: ContentGenerationPipeline = Depends(lambda: pipeline_service)
) -> Dict[str, Any]:
    """Add request to batch"""
    try:
        batch = await service.add_to_batch(batch_id, request_id)
        
        return {
            "status": "success",
            "batch": batch.dict(),
            "message": "Request added to batch"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/batch/{batch_id}")
async def get_batch(
    batch_id: str,
    service: ContentGenerationPipeline = Depends(lambda: pipeline_service)
) -> Dict[str, Any]:
    """Get batch details"""
    batch = await service.get_batch_job(batch_id)
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    
    return {
        "status": "success",
        "batch": batch.dict()
    }

@router.post("/batch/{batch_id}/complete")
async def complete_batch(
    batch_id: str,
    service: ContentGenerationPipeline = Depends(lambda: pipeline_service)
) -> Dict[str, Any]:
    """Mark batch as complete"""
    try:
        batch = await service.complete_batch(batch_id)
        
        return {
            "status": "success",
            "batch": batch.dict(),
            "message": "Batch completed"
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# ============================================================================
# QUALITY ASSURANCE ENDPOINTS
# ============================================================================

@router.post("/quality/assess")
async def create_quality_assessment(
    content_id: str = Body(...),
    overall_quality: float = Body(...),
    quality_level: str = Body(...),
    resolution_score: Optional[float] = Body(None),
    audio_clarity: Optional[float] = Body(None),
    grammar_score: Optional[float] = Body(None),
    manual_review_required: bool = Body(default=False),
    service: ContentGenerationPipeline = Depends(lambda: pipeline_service)
) -> Dict[str, Any]:
    """Create quality assessment"""
    try:
        metrics = ContentQualityMetrics(
            content_id=content_id,
            resolution_score=resolution_score,
            audio_clarity=audio_clarity,
            grammar_score=grammar_score,
            overall_quality=overall_quality,
            quality_level=quality_level,
            manual_review_required=manual_review_required
        )
        
        created = await service.create_quality_metrics(metrics)
        
        return {
            "status": "success",
            "metrics": created.dict(),
            "message": "Quality assessment created"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/quality/{content_id}")
async def get_quality_metrics(
    content_id: str,
    service: ContentGenerationPipeline = Depends(lambda: pipeline_service)
) -> Dict[str, Any]:
    """Get content quality metrics"""
    metrics = await service.get_quality_metrics(content_id)
    if not metrics:
        raise HTTPException(status_code=404, detail="Metrics not found")
    
    return {
        "status": "success",
        "metrics": metrics.dict()
    }

# ============================================================================
# ANALYTICS ENDPOINTS
# ============================================================================

@router.get("/analytics/stats")
async def get_pipeline_stats(
    user_id: Optional[str] = Query(None),
    service: ContentGenerationPipeline = Depends(lambda: pipeline_service)
) -> Dict[str, Any]:
    """Get pipeline statistics"""
    stats = await service.get_pipeline_stats(user_id)
    
    return {
        "status": "success",
        "stats": stats
    }

# ============================================================================
# INTEGRATION ENDPOINTS
# ============================================================================

@router.post("/integrate/course/{content_id}")
async def link_to_course(
    content_id: str,
    course_id: str = Body(...),
    lesson_id: Optional[str] = Body(None),
    service: ContentGenerationPipeline = Depends(lambda: pipeline_service)
) -> Dict[str, Any]:
    """Link generated content to course"""
    try:
        content = await service.link_to_course(content_id, course_id, lesson_id)
        
        return {
            "status": "success",
            "content": content.dict(),
            "message": "Content linked to course"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/integrate/course/{course_id}/content")
async def get_course_content(
    course_id: str,
    service: ContentGenerationPipeline = Depends(lambda: pipeline_service)
) -> Dict[str, Any]:
    """Get all generated content for course"""
    content_list = await service.get_course_generated_content(course_id)
    
    return {
        "status": "success",
        "content": [c.dict() for c in content_list],
        "total": len(content_list)
    }

@router.get("/integrate/lesson/{lesson_id}/content")
async def get_lesson_content(
    lesson_id: str,
    service: ContentGenerationPipeline = Depends(lambda: pipeline_service)
) -> Dict[str, Any]:
    """Get all generated content for lesson"""
    content_list = await service.get_lesson_generated_content(lesson_id)
    
    return {
        "status": "success",
        "content": [c.dict() for c in content_list],
        "total": len(content_list)
    }
