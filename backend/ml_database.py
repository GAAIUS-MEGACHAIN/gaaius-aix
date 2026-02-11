"""
PRODUCTION DATABASE LAYER
SQLite + SQLAlchemy for ML model tracking, inference history, and statistics
"""

from sqlalchemy import (
    create_engine, Column, String, Integer, Float, DateTime, 
    Boolean, ForeignKey, JSON, Text, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from datetime import datetime
from pathlib import Path
import logging
from typing import List, Optional, Dict, Any

logger = logging.getLogger(__name__)

Base = declarative_base()
DATABASE_URL = "sqlite:///./ml_models.db"

# ============================================================================
# DATABASE MODELS
# ============================================================================

class MLModel(Base):
    """ML Model tracking"""
    __tablename__ = "ml_models"
    
    id = Column(Integer, primary_key=True, index=True)
    model_key = Column(String(256), unique=True, index=True, nullable=False)
    model_name = Column(String(256), nullable=False)
    task = Column(String(100), index=True, nullable=False)
    
    # Model specs
    size_mb = Column(Float, nullable=False)
    parameters = Column(Integer, nullable=False)
    provider = Column(String(100), nullable=False)  # huggingface, pytorch, onnx, etc
    
    # Status
    loaded = Column(Boolean, default=False)
    optimization = Column(String(100), default="none")  # none, int8, float16, distill
    device = Column(String(50))  # cuda, cpu, metal, etc
    
    # Performance
    avg_inference_time_ms = Column(Float, default=0.0)
    min_inference_time_ms = Column(Float, default=0.0)
    max_inference_time_ms = Column(Float, default=0.0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    last_used_at = Column(DateTime, default=datetime.utcnow, index=True)
    total_inferences = Column(Integer, default=0)
    memory_usage_mb = Column(Float, default=0.0)
    
    # Configuration
    quantized = Column(Boolean, default=False)
    cached = Column(Boolean, default=False)
    config = Column(JSON)  # Store model-specific config
    
    # Relationships
    inferences = relationship("Inference", back_populates="model", cascade="all, delete-orphan")
    benchmarks = relationship("ModelBenchmark", back_populates="model", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_task_device', 'task', 'device'),
        Index('idx_loaded_task', 'loaded', 'task'),
    )


class Inference(Base):
    """Inference execution records"""
    __tablename__ = "inferences"
    
    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(Integer, ForeignKey("ml_models.id"), index=True, nullable=False)
    
    # Input/Output
    input_hash = Column(String(256), index=True)  # SHA256 of input
    input_text = Column(Text)  # For text inputs (truncated to 1000 chars)
    output_text = Column(Text)  # Model output (truncated)
    
    # Performance
    inference_time_ms = Column(Float, nullable=False)
    tokens_processed = Column(Integer, default=0)
    tokens_generated = Column(Integer, default=0)
    
    # Quality
    confidence_score = Column(Float)  # For classification tasks
    success = Column(Boolean, default=True)
    error_message = Column(String(500))  # If failed
    
    # Environment
    device = Column(String(50))  # Device used for inference
    batch_size = Column(Integer, default=1)
    
    # Metadata
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    cache_hit = Column(Boolean, default=False)
    optimization_applied = Column(String(100))
    
    # Relationships
    model = relationship("MLModel", back_populates="inferences")
    
    __table_args__ = (
        Index('idx_model_timestamp', 'model_id', 'timestamp'),
        Index('idx_success', 'success'),
    )


class ModelBenchmark(Base):
    """Model benchmark results"""
    __tablename__ = "model_benchmarks"
    
    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(Integer, ForeignKey("ml_models.id"), index=True, nullable=False)
    
    # Benchmark config
    num_runs = Column(Integer, nullable=False)
    batch_size = Column(Integer, default=1)
    device = Column(String(50), nullable=False)
    optimization = Column(String(100))
    
    # Results
    avg_time_ms = Column(Float, nullable=False)
    min_time_ms = Column(Float, nullable=False)
    max_time_ms = Column(Float, nullable=False)
    std_dev_ms = Column(Float)
    throughput_samples_per_sec = Column(Float)
    memory_peak_mb = Column(Float)
    
    # Input size
    input_size_tokens = Column(Integer)
    input_size_pixels = Column(Integer)  # For vision models
    
    # Metadata
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    notes = Column(Text)
    
    # Relationships
    model = relationship("MLModel", back_populates="benchmarks")


class BuildJob(Base):
    """Build jobs with ML metadata"""
    __tablename__ = "build_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String(256), unique=True, index=True, nullable=False)
    
    # Build config
    framework = Column(String(100), index=True, nullable=False)
    build_type = Column(String(50), nullable=False)  # release, debug, optimize
    
    # ML integration
    ml_models = Column(JSON)  # List of ML models to include
    ml_optimization = Column(String(100))  # Optimization strategy
    
    # Status
    status = Column(String(50), index=True, default="pending")  # pending, running, success, failed
    progress = Column(Float, default=0.0)
    
    # Performance
    total_time_seconds = Column(Float)
    compilation_time_seconds = Column(Float)
    ml_loading_time_seconds = Column(Float)
    
    # Output
    artifact_path = Column(String(500))
    artifact_size_mb = Column(Float)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    error_message = Column(Text)
    logs = Column(Text)  # Build logs
    
    __table_args__ = (
        Index('idx_framework_status', 'framework', 'status'),
        Index('idx_created_status', 'created_at', 'status'),
    )


class InferenceCache(Base):
    """Cache frequently accessed inference results"""
    __tablename__ = "inference_cache"
    
    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(Integer, ForeignKey("ml_models.id"), index=True, nullable=False)
    
    input_hash = Column(String(256), unique=True, index=True, nullable=False)
    output = Column(JSON, nullable=False)
    
    hits = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_accessed = Column(DateTime, default=datetime.utcnow, index=True)
    
    ttl_seconds = Column(Integer, default=86400)  # 24 hours


class SystemMetrics(Base):
    """System performance metrics"""
    __tablename__ = "system_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Resource usage
    cpu_percent = Column(Float)
    memory_percent = Column(Float)
    memory_mb = Column(Float)
    gpu_memory_mb = Column(Float)
    
    # Throughput
    inferences_per_second = Column(Float)
    avg_latency_ms = Column(Float)
    p95_latency_ms = Column(Float)
    p99_latency_ms = Column(Float)
    
    # Models
    models_loaded = Column(Integer)
    total_model_memory_mb = Column(Float)
    
    # Status
    uptime_seconds = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)


# ============================================================================
# DATABASE MANAGER
# ============================================================================

class MLDatabaseManager:
    """Production database management"""
    
    def __init__(self, db_url: str = DATABASE_URL):
        self.db_url = db_url
        self.engine = create_engine(
            db_url,
            connect_args={"check_same_thread": False},
            pool_pre_ping=True  # Test connections before use
        )
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
        
        # Create tables
        Base.metadata.create_all(bind=self.engine)
        logger.info(f"Database initialized: {db_url}")
    
    def get_session(self) -> Session:
        """Get database session"""
        return self.SessionLocal()
    
    # ======================================================================
    # MODEL OPERATIONS
    # ======================================================================
    
    def register_model(self, model_data: Dict[str, Any]) -> MLModel:
        """Register a model in database"""
        session = self.get_session()
        try:
            model = MLModel(**model_data)
            session.add(model)
            session.commit()
            session.refresh(model)
            logger.info(f"Model registered: {model.model_key}")
            return model
        finally:
            session.close()
    
    def get_model(self, model_key: str) -> Optional[MLModel]:
        """Get model by key"""
        session = self.get_session()
        try:
            return session.query(MLModel).filter(
                MLModel.model_key == model_key
            ).first()
        finally:
            session.close()
    
    def update_model_status(self, model_key: str, loaded: bool, 
                          memory_mb: float = 0.0) -> bool:
        """Update model load status"""
        session = self.get_session()
        try:
            model = session.query(MLModel).filter(
                MLModel.model_key == model_key
            ).first()
            
            if not model:
                return False
            
            model.loaded = loaded
            model.memory_usage_mb = memory_mb
            model.last_used_at = datetime.utcnow()
            session.commit()
            return True
        finally:
            session.close()
    
    def get_all_models(self, task: Optional[str] = None) -> List[MLModel]:
        """Get all models, optionally filtered by task"""
        session = self.get_session()
        try:
            query = session.query(MLModel)
            if task:
                query = query.filter(MLModel.task == task)
            return query.all()
        finally:
            session.close()
    
    def get_loaded_models(self) -> List[MLModel]:
        """Get all loaded models"""
        session = self.get_session()
        try:
            return session.query(MLModel).filter(
                MLModel.loaded == True
            ).all()
        finally:
            session.close()
    
    # ======================================================================
    # INFERENCE OPERATIONS
    # ======================================================================
    
    def log_inference(self, inference_data: Dict[str, Any]) -> Inference:
        """Log inference execution"""
        session = self.get_session()
        try:
            inference = Inference(**inference_data)
            session.add(inference)
            session.commit()
            session.refresh(inference)
            return inference
        finally:
            session.close()
    
    def get_inference_stats(self, model_key: str, 
                          hours: int = 24) -> Dict[str, Any]:
        """Get inference statistics for a model"""
        session = self.get_session()
        try:
            from sqlalchemy import func
            from datetime import datetime, timedelta
            
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            model = session.query(MLModel).filter(
                MLModel.model_key == model_key
            ).first()
            
            if not model:
                return {}
            
            stats = session.query(
                func.count(Inference.id).label('total'),
                func.avg(Inference.inference_time_ms).label('avg_time'),
                func.min(Inference.inference_time_ms).label('min_time'),
                func.max(Inference.inference_time_ms).label('max_time'),
                func.sum(func.cast(Inference.success, Integer)).label('successful')
            ).filter(
                Inference.model_id == model.id,
                Inference.timestamp >= cutoff_time
            ).first()
            
            return {
                'total_inferences': stats.total or 0,
                'avg_time_ms': float(stats.avg_time or 0),
                'min_time_ms': float(stats.min_time or 0),
                'max_time_ms': float(stats.max_time or 0),
                'successful': stats.successful or 0,
                'success_rate': (stats.successful / stats.total * 100) if stats.total else 0
            }
        finally:
            session.close()
    
    def cache_hit(self, input_hash: str) -> Optional[Dict]:
        """Check and update cache hit"""
        session = self.get_session()
        try:
            cache = session.query(InferenceCache).filter(
                InferenceCache.input_hash == input_hash
            ).first()
            
            if cache:
                cache.hits += 1
                cache.last_accessed = datetime.utcnow()
                session.commit()
                return cache.output
            
            return None
        finally:
            session.close()
    
    def cache_inference(self, model_id: int, input_hash: str, 
                       output: Dict, ttl_seconds: int = 86400) -> bool:
        """Cache inference result"""
        session = self.get_session()
        try:
            cache_entry = InferenceCache(
                model_id=model_id,
                input_hash=input_hash,
                output=output,
                ttl_seconds=ttl_seconds
            )
            session.add(cache_entry)
            session.commit()
            return True
        except Exception as e:
            logger.error(f"Cache write failed: {str(e)}")
            return False
        finally:
            session.close()
    
    # ======================================================================
    # BENCHMARK OPERATIONS
    # ======================================================================
    
    def log_benchmark(self, benchmark_data: Dict[str, Any]) -> ModelBenchmark:
        """Log benchmark results"""
        session = self.get_session()
        try:
            benchmark = ModelBenchmark(**benchmark_data)
            session.add(benchmark)
            session.commit()
            session.refresh(benchmark)
            return benchmark
        finally:
            session.close()
    
    def get_benchmark_history(self, model_key: str) -> List[Dict]:
        """Get benchmark history for a model"""
        session = self.get_session()
        try:
            model = session.query(MLModel).filter(
                MLModel.model_key == model_key
            ).first()
            
            if not model:
                return []
            
            benchmarks = session.query(ModelBenchmark).filter(
                ModelBenchmark.model_id == model.id
            ).order_by(ModelBenchmark.timestamp.desc()).limit(10).all()
            
            return [
                {
                    'avg_time_ms': b.avg_time_ms,
                    'min_time_ms': b.min_time_ms,
                    'max_time_ms': b.max_time_ms,
                    'throughput': b.throughput_samples_per_sec,
                    'device': b.device,
                    'timestamp': b.timestamp.isoformat()
                }
                for b in benchmarks
            ]
        finally:
            session.close()
    
    # ======================================================================
    # BUILD JOB OPERATIONS
    # ======================================================================
    
    def create_build_job(self, job_data: Dict[str, Any]) -> BuildJob:
        """Create build job record"""
        session = self.get_session()
        try:
            job = BuildJob(**job_data)
            session.add(job)
            session.commit()
            session.refresh(job)
            return job
        finally:
            session.close()
    
    def update_build_job(self, job_id: str, update_data: Dict[str, Any]) -> bool:
        """Update build job"""
        session = self.get_session()
        try:
            job = session.query(BuildJob).filter(
                BuildJob.job_id == job_id
            ).first()
            
            if not job:
                return False
            
            for key, value in update_data.items():
                if hasattr(job, key):
                    setattr(job, key, value)
            
            session.commit()
            return True
        finally:
            session.close()
    
    def get_build_job(self, job_id: str) -> Optional[BuildJob]:
        """Get build job details"""
        session = self.get_session()
        try:
            return session.query(BuildJob).filter(
                BuildJob.job_id == job_id
            ).first()
        finally:
            session.close()
    
    # ======================================================================
    # METRICS OPERATIONS
    # ======================================================================
    
    def log_metrics(self, metrics_data: Dict[str, Any]) -> SystemMetrics:
        """Log system metrics"""
        session = self.get_session()
        try:
            metrics = SystemMetrics(**metrics_data)
            session.add(metrics)
            session.commit()
            session.refresh(metrics)
            return metrics
        finally:
            session.close()
    
    def get_recent_metrics(self, limit: int = 100) -> List[Dict]:
        """Get recent system metrics"""
        session = self.get_session()
        try:
            metrics = session.query(SystemMetrics).order_by(
                SystemMetrics.timestamp.desc()
            ).limit(limit).all()
            
            return [
                {
                    'cpu_percent': m.cpu_percent,
                    'memory_percent': m.memory_percent,
                    'inferences_per_second': m.inferences_per_second,
                    'models_loaded': m.models_loaded,
                    'timestamp': m.timestamp.isoformat()
                }
                for m in metrics
            ]
        finally:
            session.close()
    
    # ======================================================================
    # CLEANUP OPERATIONS
    # ======================================================================
    
    def cleanup_old_inferences(self, days: int = 30) -> int:
        """Delete old inference records"""
        session = self.get_session()
        try:
            from sqlalchemy import func
            from datetime import datetime, timedelta
            
            cutoff = datetime.utcnow() - timedelta(days=days)
            
            count = session.query(Inference).filter(
                Inference.timestamp < cutoff
            ).delete()
            
            session.commit()
            logger.info(f"Deleted {count} old inferences")
            return count
        finally:
            session.close()
    
    def cleanup_old_cache(self, hours: int = 24) -> int:
        """Delete expired cache entries"""
        session = self.get_session()
        try:
            from datetime import datetime, timedelta
            
            cutoff = datetime.utcnow() - timedelta(hours=hours)
            
            count = session.query(InferenceCache).filter(
                InferenceCache.last_accessed < cutoff
            ).delete()
            
            session.commit()
            logger.info(f"Deleted {count} old cache entries")
            return count
        finally:
            session.close()
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        session = self.get_session()
        try:
            from sqlalchemy import func
            
            return {
                'total_models': session.query(func.count(MLModel.id)).scalar() or 0,
                'loaded_models': session.query(func.count(MLModel.id)).filter(
                    MLModel.loaded == True
                ).scalar() or 0,
                'total_inferences': session.query(func.count(Inference.id)).scalar() or 0,
                'cache_entries': session.query(func.count(InferenceCache.id)).scalar() or 0,
                'build_jobs': session.query(func.count(BuildJob.id)).scalar() or 0,
                'successful_jobs': session.query(func.count(BuildJob.id)).filter(
                    BuildJob.status == 'success'
                ).scalar() or 0
            }
        finally:
            session.close()


# ============================================================================
# INITIALIZATION
# ============================================================================

def initialize_database() -> MLDatabaseManager:
    """Initialize production database"""
    db_path = Path("ml_models.db")
    
    manager = MLDatabaseManager(f"sqlite:///{db_path}")
    logger.info(f"Database initialized at {db_path}")
    
    return manager


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize and test
    db = initialize_database()
    stats = db.get_database_stats()
    print("Database Statistics:", stats)
