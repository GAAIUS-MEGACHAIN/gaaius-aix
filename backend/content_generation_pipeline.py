"""
Universal Content Generation Pipeline
Unified content generation and processing across all platform services
"""

from typing import List, Optional, Dict, Any, Set, Tuple, AsyncGenerator
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from enum import Enum
import uuid
import json
import asyncio
from abc import ABC, abstractmethod
from collections import defaultdict

from pydantic import BaseModel, Field, validator

# ============================================================================
# ENUMS & CONSTANTS
# ============================================================================

class ContentType(str, Enum):
    """All content types across platform"""
    VIDEO = "video"
    MUSIC = "music"
    IMAGE = "image"
    AUDIO = "audio"
    DOCUMENT = "document"
    COURSE_LESSON = "course_lesson"
    MOVIE = "movie"
    PODCAST = "podcast"
    ANIMATION = "animation"
    INTERACTIVE = "interactive"
    CANVAS = "canvas"
    SOCIAL_POST = "social_post"
    THUMBNAIL = "thumbnail"
    TRANSCRIPT = "transcript"

class GenerationStatus(str, Enum):
    """Pipeline status"""
    PENDING = "pending"
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class AIProvider(str, Enum):
    """AI providers for content generation"""
    GROQ = "groq"
    OPENAI = "openai"
    COHERE = "cohere"
    OLLAMA = "ollama"
    HUGGINGFACE = "huggingface"
    STABLE_DIFFUSION = "stable_diffusion"
    ELEVEN_LABS = "eleven_labs"
    SYNTHESIA = "synthesia"

class ProcessingStage(str, Enum):
    """Pipeline stages"""
    VALIDATION = "validation"
    GENERATION = "generation"
    PROCESSING = "processing"
    OPTIMIZATION = "optimization"
    QUALITY_CHECK = "quality_check"
    STORAGE = "storage"
    INDEXING = "indexing"
    DELIVERY = "delivery"

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class ContentGenerationRequest(BaseModel):
    """Unified content generation request"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    content_type: ContentType
    title: str = Field(..., min_length=3, max_length=300)
    description: Optional[str] = None
    prompt: str = Field(..., min_length=10, max_length=5000)
    
    # Source integration
    source_course_id: Optional[str] = None
    source_module_id: Optional[str] = None
    source_lesson_id: Optional[str] = None
    source_project_id: Optional[str] = None
    
    # Generation parameters
    ai_provider: AIProvider = AIProvider.GROQ
    model: str = "default"
    style: Optional[str] = None
    duration: Optional[int] = None  # Seconds for video/audio
    resolution: Optional[str] = None  # For video: 720p, 1080p, 4k
    quality: str = "high"  # low, medium, high, ultra
    
    # Processing options
    with_subtitles: bool = False
    with_transcript: bool = False
    auto_thumbnail: bool = True
    auto_tags: bool = True
    auto_seo: bool = True
    
    # Distribution
    auto_publish: bool = False
    distribute_to: List[str] = Field(default_factory=list)  # platforms
    
    # Metadata
    tags: List[str] = Field(default_factory=list)
    language: str = "en"
    visibility: str = "private"  # private, draft, public
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    priority: int = Field(default=5, ge=1, le=10)  # 10 = highest

class ContentGenerationJob(BaseModel):
    """Active content generation job"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    request_id: str
    user_id: str
    content_type: ContentType
    
    status: GenerationStatus = GenerationStatus.PENDING
    current_stage: ProcessingStage = ProcessingStage.VALIDATION
    progress: int = Field(default=0, ge=0, le=100)
    
    # Execution
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    estimated_completion: Optional[datetime] = None
    
    # Results
    output_url: Optional[str] = None
    output_paths: Dict[str, str] = Field(default_factory=dict)  # type -> path
    file_size: int = 0
    duration: Optional[int] = None
    
    # Tracking
    ai_provider_used: Optional[str] = None
    cost_estimate: float = 0.0
    actual_cost: float = 0.0
    tokens_used: int = 0
    
    # Error handling
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    
    # Logs
    logs: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class GeneratedContent(BaseModel):
    """Generated content metadata"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    job_id: str
    request_id: str
    user_id: str
    content_type: ContentType
    
    # Content info
    title: str
    description: Optional[str] = None
    url: str
    file_path: str
    file_size: int
    duration: Optional[int] = None
    
    # Processing artifacts
    thumbnail_url: Optional[str] = None
    preview_url: Optional[str] = None
    transcript_url: Optional[str] = None
    subtitles_url: Optional[str] = None
    
    # Metadata
    ai_provider: str
    model_used: str
    tags: List[str] = Field(default_factory=list)
    language: str
    quality: str
    
    # Distribution
    published: bool = False
    published_to: List[str] = Field(default_factory=list)
    views: int = 0
    likes: int = 0
    downloads: int = 0
    
    # Linked to platform
    linked_course_id: Optional[str] = None
    linked_lesson_id: Optional[str] = None
    linked_project_id: Optional[str] = None
    
    # SEO
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None
    seo_keywords: List[str] = Field(default_factory=list)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ContentTemplate(BaseModel):
    """Reusable content generation template"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    content_type: ContentType
    
    # Template structure
    prompt_template: str
    default_parameters: Dict[str, Any] = Field(default_factory=dict)
    
    # Processing
    ai_provider: AIProvider
    model: str
    style: Optional[str] = None
    
    # Quick settings
    preset_tags: List[str] = Field(default_factory=list)
    preset_language: str = "en"
    
    # Usage tracking
    usage_count: int = 0
    average_quality_score: float = 0.0
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class BatchGenerationJob(BaseModel):
    """Batch content generation"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    name: str
    description: str
    
    # Batch info
    total_items: int
    completed_items: int = 0
    failed_items: int = 0
    progress: int = 0
    
    # Requests in batch
    request_ids: List[str] = Field(default_factory=list)
    job_ids: List[str] = Field(default_factory=list)
    
    status: GenerationStatus = GenerationStatus.PENDING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    # Batch settings
    parallel_jobs: int = Field(default=3, ge=1, le=10)
    retry_failed: bool = True
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ContentQualityMetrics(BaseModel):
    """Quality metrics for generated content"""
    content_id: str
    
    # Visual quality (for images/videos)
    resolution_score: Optional[float] = None  # 0-1
    color_accuracy: Optional[float] = None  # 0-1
    lighting_quality: Optional[float] = None  # 0-1
    
    # Audio quality (for audio/video)
    audio_clarity: Optional[float] = None  # 0-1
    audio_levels: Optional[float] = None  # 0-1
    background_noise: Optional[float] = None  # 0-1 (lower is better)
    
    # Text quality (for documents/transcripts)
    grammar_score: Optional[float] = None  # 0-1
    readability_score: Optional[float] = None  # 0-1
    plagiarism_score: Optional[float] = None  # 0-1 (lower is better)
    
    # Overall
    overall_quality: float = Field(ge=0, le=1)
    quality_level: str  # poor, fair, good, excellent
    
    # Review
    manual_review_required: bool = False
    reviewer_id: Optional[str] = None
    review_notes: Optional[str] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

# ============================================================================
# CONTENT GENERATION PIPELINE SERVICE
# ============================================================================

class ContentGenerationPipeline:
    """Universal content generation pipeline"""
    
    def __init__(self):
        # Storage
        self.requests: Dict[str, ContentGenerationRequest] = {}
        self.jobs: Dict[str, ContentGenerationJob] = {}
        self.content: Dict[str, GeneratedContent] = {}
        self.templates: Dict[str, ContentTemplate] = {}
        self.batch_jobs: Dict[str, BatchGenerationJob] = {}
        self.quality_metrics: Dict[str, ContentQualityMetrics] = {}
        
        # Processing queues by priority
        self.processing_queues: Dict[int, List[str]] = defaultdict(list)
        self.active_jobs: Set[str] = set()
        
        # Provider limits
        self.provider_limits = {
            AIProvider.GROQ: 100,
            AIProvider.OPENAI: 50,
            AIProvider.COHERE: 75,
            AIProvider.OLLAMA: 200,
            AIProvider.HUGGINGFACE: 100,
        }
        
        # Provider usage tracking
        self.provider_usage: Dict[str, int] = defaultdict(int)

    # ========== REQUEST MANAGEMENT ==========
    
    async def create_generation_request(self, request_data: ContentGenerationRequest) -> ContentGenerationRequest:
        """Create content generation request"""
        if request_data.id in self.requests:
            raise ValueError("Request already exists")
        
        self.requests[request_data.id] = request_data
        return request_data

    async def get_request(self, request_id: str) -> Optional[ContentGenerationRequest]:
        """Get generation request"""
        return self.requests.get(request_id)

    async def list_requests(self, user_id: str) -> List[ContentGenerationRequest]:
        """List user requests"""
        return [r for r in self.requests.values() if r.user_id == user_id]

    # ========== JOB MANAGEMENT ==========
    
    async def create_job(self, request_id: str) -> ContentGenerationJob:
        """Create generation job from request"""
        request = self.requests.get(request_id)
        if not request:
            raise ValueError("Request not found")
        
        job = ContentGenerationJob(
            request_id=request_id,
            user_id=request.user_id,
            content_type=request.content_type,
            estimated_completion=datetime.utcnow() + timedelta(minutes=30)
        )
        
        self.jobs[job.id] = job
        self.processing_queues[request.priority].append(job.id)
        
        return job

    async def get_job(self, job_id: str) -> Optional[ContentGenerationJob]:
        """Get job details"""
        return self.jobs.get(job_id)

    async def start_job(self, job_id: str) -> ContentGenerationJob:
        """Start processing job"""
        if job_id not in self.jobs:
            raise ValueError("Job not found")
        
        job = self.jobs[job_id]
        job.status = GenerationStatus.PROCESSING
        job.start_time = datetime.utcnow()
        job.current_stage = ProcessingStage.VALIDATION
        self.active_jobs.add(job_id)
        
        return job

    async def update_job_progress(self, job_id: str, progress: int, stage: ProcessingStage, log_entry: Optional[Dict] = None) -> ContentGenerationJob:
        """Update job progress"""
        if job_id not in self.jobs:
            raise ValueError("Job not found")
        
        job = self.jobs[job_id]
        job.progress = progress
        job.current_stage = stage
        
        if log_entry:
            job.logs.append({
                **log_entry,
                "timestamp": datetime.utcnow().isoformat(),
                "stage": stage.value
            })
        
        return job

    async def complete_job(self, job_id: str, output_url: str, output_paths: Dict[str, str] = None, file_size: int = 0, duration: int = None) -> ContentGenerationJob:
        """Complete job successfully"""
        if job_id not in self.jobs:
            raise ValueError("Job not found")
        
        job = self.jobs[job_id]
        job.status = GenerationStatus.COMPLETED
        job.progress = 100
        job.current_stage = ProcessingStage.DELIVERY
        job.end_time = datetime.utcnow()
        job.output_url = output_url
        job.output_paths = output_paths or {}
        job.file_size = file_size
        job.duration = duration
        
        self.active_jobs.discard(job_id)
        
        return job

    async def fail_job(self, job_id: str, error_message: str) -> ContentGenerationJob:
        """Mark job as failed"""
        if job_id not in self.jobs:
            raise ValueError("Job not found")
        
        job = self.jobs[job_id]
        job.status = GenerationStatus.FAILED
        job.error_message = error_message
        job.end_time = datetime.utcnow()
        job.retry_count += 1
        
        self.active_jobs.discard(job_id)
        
        # Requeue if retries available
        if job.retry_count < job.max_retries:
            request = self.requests.get(job.request_id)
            if request:
                self.processing_queues[request.priority].append(job_id)
                job.status = GenerationStatus.QUEUED
        
        return job

    async def cancel_job(self, job_id: str) -> ContentGenerationJob:
        """Cancel job"""
        if job_id not in self.jobs:
            raise ValueError("Job not found")
        
        job = self.jobs[job_id]
        job.status = GenerationStatus.CANCELLED
        self.active_jobs.discard(job_id)
        
        return job

    async def get_user_jobs(self, user_id: str) -> List[ContentGenerationJob]:
        """Get all jobs for user"""
        return [j for j in self.jobs.values() if j.user_id == user_id]

    # ========== CONTENT MANAGEMENT ==========
    
    async def register_generated_content(self, content_data: GeneratedContent) -> GeneratedContent:
        """Register generated content"""
        self.content[content_data.id] = content_data
        return content_data

    async def get_generated_content(self, content_id: str) -> Optional[GeneratedContent]:
        """Get generated content"""
        return self.content.get(content_id)

    async def get_content_by_job(self, job_id: str) -> List[GeneratedContent]:
        """Get all content from job"""
        return [c for c in self.content.values() if c.job_id == job_id]

    async def publish_content(self, content_id: str, platforms: List[str] = None) -> GeneratedContent:
        """Publish content to platforms"""
        if content_id not in self.content:
            raise ValueError("Content not found")
        
        content = self.content[content_id]
        content.published = True
        content.published_to = platforms or []
        
        return content

    async def update_content_stats(self, content_id: str, views: int = 0, likes: int = 0, downloads: int = 0) -> GeneratedContent:
        """Update content engagement stats"""
        if content_id not in self.content:
            raise ValueError("Content not found")
        
        content = self.content[content_id]
        content.views += views
        content.likes += likes
        content.downloads += downloads
        content.updated_at = datetime.utcnow()
        
        return content

    # ========== TEMPLATES ==========
    
    async def create_template(self, template_data: ContentTemplate) -> ContentTemplate:
        """Create content generation template"""
        self.templates[template_data.id] = template_data
        return template_data

    async def get_template(self, template_id: str) -> Optional[ContentTemplate]:
        """Get template"""
        return self.templates.get(template_id)

    async def list_templates(self, content_type: Optional[ContentType] = None) -> List[ContentTemplate]:
        """List templates"""
        templates = list(self.templates.values())
        if content_type:
            templates = [t for t in templates if t.content_type == content_type]
        return sorted(templates, key=lambda t: t.usage_count, reverse=True)

    async def use_template(self, template_id: str) -> ContentTemplate:
        """Increment template usage"""
        if template_id not in self.templates:
            raise ValueError("Template not found")
        
        template = self.templates[template_id]
        template.usage_count += 1
        return template

    # ========== BATCH OPERATIONS ==========
    
    async def create_batch_job(self, batch_data: BatchGenerationJob) -> BatchGenerationJob:
        """Create batch generation job"""
        self.batch_jobs[batch_data.id] = batch_data
        return batch_data

    async def get_batch_job(self, batch_id: str) -> Optional[BatchGenerationJob]:
        """Get batch job"""
        return self.batch_jobs.get(batch_id)

    async def add_to_batch(self, batch_id: str, request_id: str) -> BatchGenerationJob:
        """Add request to batch"""
        if batch_id not in self.batch_jobs:
            raise ValueError("Batch not found")
        
        batch = self.batch_jobs[batch_id]
        batch.request_ids.append(request_id)
        batch.total_items += 1
        
        return batch

    async def update_batch_progress(self, batch_id: str, completed: int, failed: int) -> BatchGenerationJob:
        """Update batch progress"""
        if batch_id not in self.batch_jobs:
            raise ValueError("Batch not found")
        
        batch = self.batch_jobs[batch_id]
        batch.completed_items = completed
        batch.failed_items = failed
        batch.progress = int((completed / batch.total_items * 100)) if batch.total_items > 0 else 0
        
        return batch

    async def complete_batch(self, batch_id: str) -> BatchGenerationJob:
        """Mark batch as complete"""
        if batch_id not in self.batch_jobs:
            raise ValueError("Batch not found")
        
        batch = self.batch_jobs[batch_id]
        batch.status = GenerationStatus.COMPLETED
        batch.end_time = datetime.utcnow()
        
        return batch

    # ========== QUALITY ASSURANCE ==========
    
    async def create_quality_metrics(self, metrics_data: ContentQualityMetrics) -> ContentQualityMetrics:
        """Create quality metrics"""
        self.quality_metrics[metrics_data.content_id] = metrics_data
        return metrics_data

    async def get_quality_metrics(self, content_id: str) -> Optional[ContentQualityMetrics]:
        """Get content quality metrics"""
        return self.quality_metrics.get(content_id)

    async def calculate_overall_quality(self, content_id: str) -> float:
        """Calculate overall quality score"""
        if content_id not in self.quality_metrics:
            return 0.0
        
        metrics = self.quality_metrics[content_id]
        scores = []
        
        # Collect all available scores
        if metrics.resolution_score: scores.append(metrics.resolution_score)
        if metrics.color_accuracy: scores.append(metrics.color_accuracy)
        if metrics.audio_clarity: scores.append(metrics.audio_clarity)
        if metrics.grammar_score: scores.append(metrics.grammar_score)
        if metrics.readability_score: scores.append(metrics.readability_score)
        
        return sum(scores) / len(scores) if scores else 0.0

    # ========== ANALYTICS ==========
    
    async def get_pipeline_stats(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get pipeline statistics"""
        jobs = [j for j in self.jobs.values() if not user_id or j.user_id == user_id]
        
        return {
            "total_jobs": len(jobs),
            "completed_jobs": len([j for j in jobs if j.status == GenerationStatus.COMPLETED]),
            "failed_jobs": len([j for j in jobs if j.status == GenerationStatus.FAILED]),
            "processing_jobs": len([j for j in jobs if j.status == GenerationStatus.PROCESSING]),
            "queued_jobs": len([j for j in jobs if j.status == GenerationStatus.QUEUED]),
            "total_content_generated": len([c for c in self.content.values() if not user_id or c.user_id == user_id]),
            "average_generation_time": self._calculate_avg_time(jobs),
            "content_by_type": self._count_by_type(jobs),
            "provider_usage": dict(self.provider_usage),
            "active_jobs": len(self.active_jobs)
        }

    def _calculate_avg_time(self, jobs: List[ContentGenerationJob]) -> float:
        """Calculate average generation time"""
        completed = [j for j in jobs if j.status == GenerationStatus.COMPLETED and j.start_time and j.end_time]
        if not completed:
            return 0.0
        
        times = [(j.end_time - j.start_time).total_seconds() for j in completed]
        return sum(times) / len(times)

    def _count_by_type(self, jobs: List[ContentGenerationJob]) -> Dict[str, int]:
        """Count jobs by content type"""
        counts = defaultdict(int)
        for job in jobs:
            counts[job.content_type.value] += 1
        return dict(counts)

    async def get_user_content_library(self, user_id: str) -> Dict[str, Any]:
        """Get user's content library"""
        user_content = [c for c in self.content.values() if c.user_id == user_id]
        
        return {
            "total_items": len(user_content),
            "total_size": sum(c.file_size for c in user_content),
            "published_items": len([c for c in user_content if c.published]),
            "content_by_type": self._count_content_by_type(user_content),
            "total_views": sum(c.views for c in user_content),
            "total_downloads": sum(c.downloads for c in user_content),
            "content": sorted(user_content, key=lambda c: c.created_at, reverse=True)
        }

    def _count_content_by_type(self, content: List[GeneratedContent]) -> Dict[str, int]:
        """Count content by type"""
        counts = defaultdict(int)
        for c in content:
            counts[c.content_type.value] += 1
        return dict(counts)

    # ========== DISTRIBUTION & INTEGRATION ==========
    
    async def link_to_course(self, content_id: str, course_id: str, lesson_id: Optional[str] = None) -> GeneratedContent:
        """Link generated content to course"""
        if content_id not in self.content:
            raise ValueError("Content not found")
        
        content = self.content[content_id]
        content.linked_course_id = course_id
        content.linked_lesson_id = lesson_id
        
        return content

    async def get_course_generated_content(self, course_id: str) -> List[GeneratedContent]:
        """Get all generated content for course"""
        return [c for c in self.content.values() if c.linked_course_id == course_id]

    async def get_lesson_generated_content(self, lesson_id: str) -> List[GeneratedContent]:
        """Get all generated content for lesson"""
        return [c for c in self.content.values() if c.linked_lesson_id == lesson_id]
