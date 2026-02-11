"""
PRODUCTION BUILD + ML INTEGRATION
Orchestrates ML model loading/compilation with framework builds
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any
import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
import time
import psutil

from ml_inference_engine import MLInferenceEngine, OllamaIntegration
from ml_database import MLDatabaseManager, MLModel, Inference, BuildJob
from build_system_enterprise import BuildOrchestrator, BuildConfig, Framework

logger = logging.getLogger(__name__)


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class MLBuildConfig:
    """Configuration for ML-enhanced builds"""
    
    # Base build config
    framework: str
    build_type: str = "release"
    
    # ML configuration
    include_ml_models: List[str] = field(default_factory=list)
    ml_optimization: str = "int8"  # none, int8, float16, distill
    optimize_for_device: str = "cpu"  # cpu, cuda, metal
    
    # Compilation targets
    target_os: str = "linux"
    target_arch: str = "x86_64"
    
    # Advanced
    quantize_models: bool = True
    bundle_ollama: bool = False
    compress_artifacts: bool = True
    enable_inference_cache: bool = True


@dataclass
class MLBuildResult:
    """Result of ML-enhanced build"""
    
    job_id: str
    status: str  # success, failed, partial
    framework: str
    
    # Build artifacts
    binary_path: str
    model_paths: Dict[str, str] = field(default_factory=dict)
    total_size_mb: float = 0.0
    
    # Performance
    build_time_seconds: float = 0.0
    ml_loading_time_seconds: float = 0.0
    total_time_seconds: float = 0.0
    
    # Optimization stats
    optimization_applied: Dict[str, Any] = field(default_factory=dict)
    inference_stats: Dict[str, Any] = field(default_factory=dict)
    
    # Logs
    build_log: str = ""
    ml_log: str = ""
    error_message: Optional[str] = None


# ============================================================================
# ML BUILD EXECUTOR
# ============================================================================

class MLBuildExecutor:
    """Execute builds with integrated ML models"""
    
    def __init__(self, db_manager: MLDatabaseManager):
        self.db = db_manager
        self.engine = None
        self.ollama = None
        self.orchestrator = None
        self.metrics_log = []
    
    async def initialize(self):
        """Initialize ML and build systems"""
        logger.info("Initializing ML build executor...")
        
        # Initialize ML engine
        device = "cuda" if self._has_cuda() else "cpu"
        self.engine = MLInferenceEngine(device=device)
        
        # Initialize Ollama
        self.ollama = OllamaIntegration()
        
        # Initialize build orchestrator
        self.orchestrator = BuildOrchestrator()
        
        logger.info(f"ML build executor initialized (device: {device})")
    
    @staticmethod
    def _has_cuda() -> bool:
        """Check if CUDA is available"""
        try:
            import torch
            return torch.cuda.is_available()
        except:
            return False
    
    async def build_with_ml(self, config: MLBuildConfig) -> MLBuildResult:
        """
        Execute build with integrated ML models
        
        This is the main orchestration function that:
        1. Loads specified ML models
        2. Optimizes models for target device
        3. Compiles framework
        4. Bundles models with binary
        5. Generates deployment package
        """
        
        job_id = self._generate_job_id()
        result = MLBuildResult(
            job_id=job_id,
            status="running",
            framework=config.framework
        )
        
        try:
            start_time = time.time()
            logger.info(f"Starting ML build job {job_id}")
            
            # ================================================================
            # PHASE 1: LOAD AND OPTIMIZE ML MODELS
            # ================================================================
            
            ml_start = time.time()
            logger.info(f"Phase 1: Loading ML models {config.include_ml_models}")
            
            model_paths = {}
            optimization_stats = {}
            
            for model_key in config.include_ml_models:
                try:
                    logger.info(f"Loading model: {model_key}")
                    
                    # Load model with optimization
                    success = self.engine.load_model(
                        model_key,
                        optimize=config.quantize_models
                    )
                    
                    if success:
                        # Get model info
                        metadata = self.engine.registry.get_model_metadata(model_key)
                        model_paths[model_key] = f"models/{model_key}"
                        
                        optimization_stats[model_key] = {
                            "optimization": config.ml_optimization,
                            "device": config.optimize_for_device,
                            "size_mb": metadata.get("size_mb", 0),
                            "loaded_successfully": True
                        }
                        
                        # Log to database
                        self.db.update_model_status(
                            model_key,
                            loaded=True,
                            memory_mb=metadata.get("size_mb", 0)
                        )
                    else:
                        optimization_stats[model_key]["loaded_successfully"] = False
                
                except Exception as e:
                    logger.error(f"Failed to load model {model_key}: {str(e)}")
                    optimization_stats[model_key] = {
                        "error": str(e),
                        "loaded_successfully": False
                    }
            
            ml_load_time = time.time() - ml_start
            result.ml_loading_time_seconds = ml_load_time
            result.optimization_applied = optimization_stats
            
            logger.info(f"ML phase completed in {ml_load_time:.2f}s")
            
            # ================================================================
            # PHASE 2: COMPILE FRAMEWORK
            # ================================================================
            
            build_start = time.time()
            logger.info(f"Phase 2: Compiling {config.framework}")
            
            # Create build config for orchestrator
            build_cfg = BuildConfig(
                project_name=f"ml-{config.framework}-{job_id[:8]}",
                framework=config.framework,
                build_type=config.build_type
            )
            
            # Execute build
            build_success, build_log, binary_path = await self._execute_framework_build(
                build_cfg
            )
            
            build_time = time.time() - build_start
            result.build_time_seconds = build_time
            result.build_log = build_log
            
            if not build_success:
                result.status = "failed"
                result.error_message = "Framework compilation failed"
                logger.error(f"Build failed: {build_log}")
                return result
            
            result.binary_path = binary_path
            logger.info(f"Build completed in {build_time:.2f}s")
            
            # ================================================================
            # PHASE 3: BUNDLE MODELS WITH BINARY
            # ================================================================
            
            logger.info("Phase 3: Bundling models with binary")
            
            bundle_path = await self._bundle_models_and_binary(
                binary_path,
                model_paths,
                config
            )
            
            result.model_paths = model_paths
            
            # ================================================================
            # PHASE 4: OPTIMIZATION AND COMPRESSION
            # ================================================================
            
            if config.compress_artifacts:
                logger.info("Phase 4: Compressing artifacts")
                
                compressed_path = await self._compress_artifacts(bundle_path)
                result.binary_path = compressed_path
            
            # ================================================================
            # PHASE 5: INFERENCE STATISTICS
            # ================================================================
            
            logger.info("Phase 5: Collecting inference statistics")
            
            inference_stats = {}
            for model_key in config.include_ml_models:
                stats = self.db.get_inference_stats(model_key)
                inference_stats[model_key] = stats
            
            result.inference_stats = inference_stats
            
            # ================================================================
            # FINALIZATION
            # ================================================================
            
            result.total_time_seconds = time.time() - start_time
            result.status = "success"
            
            # Calculate artifact size
            try:
                result.total_size_mb = Path(result.binary_path).stat().st_size / (1024 * 1024)
            except:
                result.total_size_mb = 0.0
            
            logger.info(f"ML build completed successfully in {result.total_time_seconds:.2f}s")
            
            # Log to database
            self.db.create_build_job({
                "job_id": job_id,
                "framework": config.framework,
                "build_type": config.build_type,
                "ml_models": config.include_ml_models,
                "ml_optimization": config.ml_optimization,
                "status": "success",
                "total_time_seconds": result.total_time_seconds,
                "ml_loading_time_seconds": result.ml_loading_time_seconds,
                "compilation_time_seconds": result.build_time_seconds,
                "artifact_path": result.binary_path,
                "artifact_size_mb": result.total_size_mb
            })
            
            return result
        
        except Exception as e:
            logger.error(f"ML build failed: {str(e)}")
            result.status = "failed"
            result.error_message = str(e)
            return result
    
    async def _execute_framework_build(self, config: BuildConfig) -> tuple:
        """Execute framework compilation"""
        try:
            # Use orchestrator to build
            success, logs = self.orchestrator.submit_build_job(
                project_name=config.project_name,
                framework=config.framework,
                build_type=config.build_type
            )
            
            binary_path = f"artifacts/{config.project_name}/build/output"
            
            return success, logs, binary_path
        
        except Exception as e:
            logger.error(f"Framework build failed: {str(e)}")
            return False, str(e), ""
    
    async def _bundle_models_and_binary(self, binary_path: str, 
                                       model_paths: Dict[str, str],
                                       config: MLBuildConfig) -> str:
        """Bundle ML models with compiled binary"""
        try:
            bundle_dir = Path("artifacts") / f"bundle-{datetime.now().isoformat()}"
            bundle_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy binary
            import shutil
            binary_src = Path(binary_path)
            if binary_src.exists():
                shutil.copy(binary_src, bundle_dir / "binary")
            
            # Copy models
            models_dir = bundle_dir / "models"
            models_dir.mkdir(exist_ok=True)
            
            for model_key in config.include_ml_models:
                # Save model metadata
                metadata = self.engine.registry.get_model_metadata(model_key)
                model_file = models_dir / f"{model_key}.json"
                
                with open(model_file, 'w') as f:
                    json.dump(metadata, f, indent=2)
            
            # Create manifest
            manifest = {
                "binary": str(bundle_dir / "binary"),
                "models": {k: str(models_dir / f"{k}.json") for k in config.include_ml_models},
                "framework": config.framework,
                "created_at": datetime.now().isoformat(),
                "ml_optimization": config.ml_optimization,
                "target_device": config.optimize_for_device
            }
            
            with open(bundle_dir / "manifest.json", 'w') as f:
                json.dump(manifest, f, indent=2)
            
            logger.info(f"Bundle created at {bundle_dir}")
            return str(bundle_dir)
        
        except Exception as e:
            logger.error(f"Bundling failed: {str(e)}")
            raise
    
    async def _compress_artifacts(self, bundle_path: str) -> str:
        """Compress artifacts for deployment"""
        try:
            import shutil
            
            bundle = Path(bundle_path)
            compress_path = bundle.parent / f"{bundle.name}.tar.gz"
            
            shutil.make_archive(
                str(compress_path)[:-7],  # Remove .tar.gz
                'gztar',
                bundle.parent,
                bundle.name
            )
            
            logger.info(f"Compressed to {compress_path}")
            return str(compress_path)
        
        except Exception as e:
            logger.error(f"Compression failed: {str(e)}")
            return bundle_path
    
    async def benchmark_ml_models(self, model_keys: List[str], 
                                 num_runs: int = 10) -> Dict[str, Dict]:
        """Benchmark ML models"""
        results = {}
        
        for model_key in model_keys:
            try:
                from ml_inference_engine import ModelOptimizer
                
                result = ModelOptimizer.benchmark_model(
                    model_key,
                    self.engine,
                    num_runs
                )
                
                results[model_key] = result
                
                # Log to database
                self.db.log_benchmark({
                    "model_id": self._get_model_id(model_key),
                    "num_runs": num_runs,
                    "device": self.engine.device,
                    "avg_time_ms": result.get("avg_time_ms", 0),
                    "min_time_ms": result.get("min_time_ms", 0),
                    "max_time_ms": result.get("max_time_ms", 0),
                    "throughput_samples_per_sec": result.get("throughput", 0)
                })
            
            except Exception as e:
                logger.error(f"Benchmark failed for {model_key}: {str(e)}")
                results[model_key] = {"error": str(e)}
        
        return results
    
    def _get_model_id(self, model_key: str) -> int:
        """Get model database ID"""
        model = self.db.get_model(model_key)
        return model.id if model else -1
    
    @staticmethod
    def _generate_job_id() -> str:
        """Generate unique job ID"""
        import uuid
        return f"mlbuild-{uuid.uuid4().hex[:8]}"
    
    async def collect_system_metrics(self):
        """Collect and log system metrics"""
        try:
            metrics = {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "memory_mb": psutil.virtual_memory().used / (1024 * 1024),
                "models_loaded": len(self.engine.loaded_models) if self.engine else 0,
                "timestamp": datetime.now().isoformat()
            }
            
            self.metrics_log.append(metrics)
            
            if self.db:
                self.db.log_metrics(metrics)
            
            return metrics
        
        except Exception as e:
            logger.error(f"Metrics collection failed: {str(e)}")
            return {}
    
    async def shutdown(self):
        """Cleanup and shutdown"""
        logger.info("Shutting down ML build executor...")
        
        if self.engine:
            for model_key in list(self.engine.loaded_models.keys()):
                self.engine.unload_model(model_key)
        
        logger.info("Shutdown complete")


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

async def example_ml_build():
    """Example of ML-enhanced build"""
    
    # Initialize database
    db = MLDatabaseManager()
    
    # Initialize executor
    executor = MLBuildExecutor(db)
    await executor.initialize()
    
    # Configure build with ML models
    config = MLBuildConfig(
        framework="fastapi",
        build_type="release",
        include_ml_models=[
            "distilbert-sentiment",
            "mobilenet-v2",
            "roberta-qa"
        ],
        ml_optimization="int8",
        optimize_for_device="cuda" if executor._has_cuda() else "cpu",
        quantize_models=True,
        compress_artifacts=True
    )
    
    # Execute build
    result = await executor.build_with_ml(config)
    
    print(f"\n{'='*70}")
    print(f"ML BUILD RESULT")
    print(f"{'='*70}")
    print(f"Job ID: {result.job_id}")
    print(f"Status: {result.status}")
    print(f"Framework: {result.framework}")
    print(f"Binary: {result.binary_path}")
    print(f"Total Size: {result.total_size_mb:.2f} MB")
    print(f"Total Time: {result.total_time_seconds:.2f}s")
    print(f"  - Build Time: {result.build_time_seconds:.2f}s")
    print(f"  - ML Loading: {result.ml_loading_time_seconds:.2f}s")
    print(f"Models Bundled: {list(result.model_paths.keys())}")
    print(f"{'='*70}\n")
    
    await executor.shutdown()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    asyncio.run(example_ml_build())
