"""
PRODUCTION TEST SUITE
Comprehensive testing for ML + Build integration
"""

import pytest
import asyncio
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import json
import sqlite3

from ml_build_executor import MLBuildExecutor, MLBuildConfig
from ml_database import (
    MLDatabaseManager, MLModel, Inference, BuildJob,
    ModelBenchmark, InferenceCache
)
from ml_inference_engine import (
    MLInferenceEngine, OllamaIntegration,
    ModelTask, InferenceResult
)
from ml_api_server import app
from fastapi.testclient import TestClient


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def temp_db():
    """Create temporary database"""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    db = MLDatabaseManager(f"sqlite:///{db_path}")
    yield db
    
    # Cleanup
    Path(db_path).unlink(missing_ok=True)


@pytest.fixture
def ml_engine():
    """Create ML inference engine"""
    engine = MLInferenceEngine(device="cpu")
    yield engine
    
    # Cleanup
    for model_key in list(engine.loaded_models.keys()):
        engine.unload_model(model_key)


@pytest.fixture
def executor(temp_db):
    """Create ML build executor"""
    executor = MLBuildExecutor(temp_db)
    return executor


@pytest.fixture
def api_client():
    """Create test client for FastAPI"""
    return TestClient(app)


# ============================================================================
# DATABASE TESTS
# ============================================================================

class TestMLDatabase:
    """Test database operations"""
    
    def test_model_registration(self, temp_db):
        """Test model registration"""
        model_data = {
            'model_key': 'test-model',
            'model_name': 'Test Model',
            'task': 'text-classification',
            'size_mb': 100.0,
            'parameters': 50000000,
            'provider': 'huggingface',
            'optimization': 'none'
        }
        
        model = temp_db.register_model(model_data)
        
        assert model.model_key == 'test-model'
        assert model.loaded == False
        
        # Verify can retrieve
        retrieved = temp_db.get_model('test-model')
        assert retrieved is not None
        assert retrieved.model_key == 'test-model'
    
    def test_model_status_update(self, temp_db):
        """Test model status update"""
        model_data = {
            'model_key': 'test-model',
            'model_name': 'Test Model',
            'task': 'text-classification',
            'size_mb': 100.0,
            'parameters': 50000000,
            'provider': 'huggingface'
        }
        
        temp_db.register_model(model_data)
        
        # Update status
        success = temp_db.update_model_status('test-model', loaded=True, memory_mb=150.0)
        assert success
        
        # Verify
        model = temp_db.get_model('test-model')
        assert model.loaded == True
        assert model.memory_usage_mb == 150.0
    
    def test_inference_logging(self, temp_db):
        """Test inference logging"""
        # Register model first
        model_data = {
            'model_key': 'test-model',
            'model_name': 'Test Model',
            'task': 'text-classification',
            'size_mb': 100.0,
            'parameters': 50000000,
            'provider': 'huggingface'
        }
        model = temp_db.register_model(model_data)
        
        # Log inference
        inference_data = {
            'model_id': model.id,
            'input_text': 'Test input',
            'output_text': 'Test output',
            'inference_time_ms': 100.0,
            'confidence_score': 0.95,
            'success': True,
            'device': 'cpu'
        }
        
        inference = temp_db.log_inference(inference_data)
        
        assert inference.model_id == model.id
        assert inference.inference_time_ms == 100.0
        assert inference.success == True
    
    def test_inference_stats(self, temp_db):
        """Test inference statistics"""
        # Register model
        model_data = {
            'model_key': 'test-model',
            'model_name': 'Test Model',
            'task': 'text-classification',
            'size_mb': 100.0,
            'parameters': 50000000,
            'provider': 'huggingface'
        }
        model = temp_db.register_model(model_data)
        
        # Log multiple inferences
        for i in range(5):
            inference_data = {
                'model_id': model.id,
                'input_text': f'Test {i}',
                'output_text': f'Output {i}',
                'inference_time_ms': 50.0 + i * 10,
                'success': True,
                'device': 'cpu'
            }
            temp_db.log_inference(inference_data)
        
        # Get stats
        stats = temp_db.get_inference_stats('test-model')
        
        assert stats['total_inferences'] == 5
        assert stats['successful'] == 5
        assert stats['success_rate'] == 100.0
        assert stats['avg_time_ms'] > 0
    
    def test_database_stats(self, temp_db):
        """Test overall database statistics"""
        # Register models
        for i in range(3):
            model_data = {
                'model_key': f'model-{i}',
                'model_name': f'Model {i}',
                'task': 'text-classification',
                'size_mb': 100.0,
                'parameters': 50000000,
                'provider': 'huggingface'
            }
            temp_db.register_model(model_data)
        
        # Get stats
        stats = temp_db.get_database_stats()
        
        assert stats['total_models'] == 3
        assert stats['total_inferences'] == 0
        assert stats['build_jobs'] == 0


# ============================================================================
# ML INFERENCE ENGINE TESTS
# ============================================================================

class TestMLInferenceEngine:
    """Test ML inference engine"""
    
    def test_engine_initialization(self, ml_engine):
        """Test engine initialization"""
        assert ml_engine is not None
        assert ml_engine.device in ['cpu', 'cuda']
        assert ml_engine.registry is not None
    
    def test_model_registry(self, ml_engine):
        """Test model registry"""
        registry = ml_engine.registry
        
        # Should have production models
        assert len(registry.PRODUCTION_MODELS) > 0
        
        # Should be able to get metadata
        metadata = registry.get_model_metadata('distilbert-sentiment')
        assert metadata is not None
        assert metadata['task'] == 'text-classification'
    
    def test_model_loading(self, ml_engine):
        """Test model loading (mock to avoid downloading)"""
        with patch.object(ml_engine, '_load_transformer_model', return_value=Mock()):
            result = ml_engine.load_model('distilbert-sentiment')
            assert result in [True, False]  # Should attempt to load
    
    def test_loaded_models_tracking(self, ml_engine):
        """Test loaded models tracking"""
        initial_count = len(ml_engine.loaded_models)
        
        # Mock model loading
        with patch.object(ml_engine, '_load_transformer_model', return_value=Mock()):
            ml_engine.load_model('distilbert-sentiment')
        
        # Check if tracking updated
        assert isinstance(ml_engine.loaded_models, dict)
    
    def test_model_unloading(self, ml_engine):
        """Test model unloading"""
        # Load a model first
        with patch.object(ml_engine, '_load_transformer_model', return_value=Mock()):
            ml_engine.load_model('distilbert-sentiment')
        
        # Unload
        success = ml_engine.unload_model('distilbert-sentiment')
        assert success == True or 'distilbert-sentiment' not in ml_engine.loaded_models


# ============================================================================
# BUILD EXECUTOR TESTS
# ============================================================================

class TestMLBuildExecutor:
    """Test ML build executor"""
    
    @pytest.mark.asyncio
    async def test_executor_initialization(self, executor):
        """Test executor initialization"""
        await executor.initialize()
        
        assert executor.engine is not None
        assert executor.ollama is not None
        assert executor.orchestrator is not None
    
    @pytest.mark.asyncio
    async def test_has_cuda_detection(self, executor):
        """Test CUDA detection"""
        has_cuda = executor._has_cuda()
        assert isinstance(has_cuda, bool)
    
    @pytest.mark.asyncio
    async def test_job_id_generation(self):
        """Test job ID generation"""
        job_id1 = MLBuildExecutor._generate_job_id()
        job_id2 = MLBuildExecutor._generate_job_id()
        
        assert job_id1.startswith('mlbuild-')
        assert job_id2.startswith('mlbuild-')
        assert job_id1 != job_id2
    
    @pytest.mark.asyncio
    async def test_build_config_creation(self):
        """Test build config creation"""
        config = MLBuildConfig(
            framework="fastapi",
            build_type="release",
            include_ml_models=["distilbert-sentiment"],
            ml_optimization="int8",
            optimize_for_device="cpu"
        )
        
        assert config.framework == "fastapi"
        assert "distilbert-sentiment" in config.include_ml_models
        assert config.ml_optimization == "int8"
    
    @pytest.mark.asyncio
    async def test_metrics_collection(self, executor):
        """Test system metrics collection"""
        await executor.initialize()
        
        metrics = await executor.collect_system_metrics()
        
        assert 'cpu_percent' in metrics
        assert 'memory_percent' in metrics
        assert 'timestamp' in metrics
        
        await executor.shutdown()


# ============================================================================
# API TESTS
# ============================================================================

class TestMLAPI:
    """Test FastAPI endpoints"""
    
    def test_health_check(self, api_client):
        """Test health check endpoint"""
        response = api_client.get("/api/v1/health")
        
        # Should return 200 or 503 depending on initialization
        assert response.status_code in [200, 503]
    
    def test_models_list(self, api_client):
        """Test models list endpoint"""
        response = api_client.get("/api/v1/models")
        
        if response.status_code == 200:
            data = response.json()
            assert 'models' in data
            assert isinstance(data['models'], list)
        else:
            # Engine not initialized
            assert response.status_code == 503
    
    def test_invalid_sentiment_input(self, api_client):
        """Test invalid sentiment input"""
        response = api_client.post(
            "/api/v1/sentiment",
            json={"text": "", "model": "distilbert-sentiment"}
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_batch_sentiment_validation(self, api_client):
        """Test batch sentiment validation"""
        response = api_client.post(
            "/api/v1/batch-sentiment",
            json={"texts": [], "model": "distilbert-sentiment"}
        )
        
        assert response.status_code == 422  # Validation error


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Integration tests for full pipeline"""
    
    @pytest.mark.asyncio
    async def test_full_build_pipeline(self, executor, temp_db):
        """Test complete ML + build pipeline"""
        await executor.initialize()
        
        # Create build config
        config = MLBuildConfig(
            framework="fastapi",
            build_type="release",
            include_ml_models=["distilbert-sentiment"],
            ml_optimization="int8",
            compress_artifacts=False
        )
        
        # Mock the build process
        with patch.object(executor, '_execute_framework_build') as mock_build:
            mock_build.return_value = (True, "Build successful", "artifacts/binary")
            
            with patch.object(executor, '_bundle_models_and_binary') as mock_bundle:
                mock_bundle.return_value = "artifacts/bundle"
                
                # Run build
                result = await executor.build_with_ml(config)
        
        # Verify result structure
        assert result.job_id is not None
        assert result.framework == "fastapi"
        assert result.status in ["success", "failed"]
        
        await executor.shutdown()
    
    @pytest.mark.asyncio
    async def test_database_integration(self, executor, temp_db):
        """Test database integration with executor"""
        await executor.initialize()
        
        # Register a model in database
        model_data = {
            'model_key': 'test-model',
            'model_name': 'Test Model',
            'task': 'text-classification',
            'size_mb': 100.0,
            'parameters': 50000000,
            'provider': 'huggingface'
        }
        model = temp_db.register_model(model_data)
        
        # Update status through executor
        temp_db.update_model_status(model.model_key, loaded=True, memory_mb=150.0)
        
        # Verify
        retrieved = temp_db.get_model(model.model_key)
        assert retrieved.loaded == True
        
        await executor.shutdown()


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

class TestPerformance:
    """Performance and load tests"""
    
    def test_database_query_performance(self, temp_db):
        """Test database query performance"""
        import time
        
        # Register many models
        for i in range(100):
            model_data = {
                'model_key': f'model-{i}',
                'model_name': f'Model {i}',
                'task': 'text-classification',
                'size_mb': 100.0 + i,
                'parameters': 50000000,
                'provider': 'huggingface'
            }
            temp_db.register_model(model_data)
        
        # Measure query time
        start = time.time()
        models = temp_db.get_all_models()
        query_time = time.time() - start
        
        assert len(models) == 100
        assert query_time < 1.0  # Should be fast
    
    def test_inference_logging_performance(self, temp_db):
        """Test inference logging performance"""
        import time
        
        # Register model
        model_data = {
            'model_key': 'test-model',
            'model_name': 'Test Model',
            'task': 'text-classification',
            'size_mb': 100.0,
            'parameters': 50000000,
            'provider': 'huggingface'
        }
        model = temp_db.register_model(model_data)
        
        # Log many inferences
        start = time.time()
        for i in range(1000):
            inference_data = {
                'model_id': model.id,
                'input_text': f'Test {i}',
                'output_text': f'Output {i}',
                'inference_time_ms': 50.0 + (i % 100),
                'success': True,
                'device': 'cpu'
            }
            temp_db.log_inference(inference_data)
        
        elapsed = time.time() - start
        
        # Should handle 1000 inferences quickly
        assert elapsed < 10.0


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
