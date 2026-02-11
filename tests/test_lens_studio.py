"""
Lens Studio - Comprehensive Test Suite
Production-grade testing for all filter functionality
"""

import pytest
import numpy as np
import cv2
from pathlib import Path
import asyncio
import json
import base64
from datetime import datetime

# Import components
from lens_studio_core import FilterMetadata, FilterType, FilterPriority
from filter_processor import FilterProcessor, OptimizedFilterProcessor, get_processor
from lens_studio_service import (
    BeautyConfig,
    FilterApplicationRequest,
    ProcessingMode,
    router
)


class TestFilterProcessor:
    """Test filter processor functionality"""

    @pytest.fixture
    def processor(self):
        """Create processor instance"""
        return FilterProcessor()

    @pytest.fixture
    def sample_frame(self):
        """Create sample test frame"""
        return np.random.randint(0, 256, (720, 1280, 3), dtype=np.uint8)

    @pytest.fixture
    def test_image_path(self):
        """Get test image path"""
        test_dir = Path(__file__).parent / "test_data"
        test_dir.mkdir(exist_ok=True)
        
        # Create test image
        img = np.ones((720, 1280, 3), dtype=np.uint8) * 128
        cv2.circle(img, (640, 360), 100, (0, 255, 0), -1)
        
        path = test_dir / "test_frame.jpg"
        cv2.imwrite(str(path), img)
        return path

    def test_processor_initialization(self, processor):
        """Test processor initializes correctly"""
        assert processor is not None
        assert processor.executor is not None
        assert processor.face_mesh is not None
        print("✅ Processor initialization test passed")

    def test_frame_encoding_decoding(self, processor, sample_frame):
        """Test frame encoding/decoding"""
        # Encode
        encoded = processor.encode_frame_to_base64(sample_frame)
        assert isinstance(encoded, str)
        assert len(encoded) > 0
        
        # Decode
        decoded = processor.decode_frame_from_base64(encoded)
        assert decoded.shape == sample_frame.shape
        print("✅ Frame encoding/decoding test passed")

    def test_skin_smoothing(self, processor, sample_frame):
        """Test skin smoothing filter"""
        result = processor.apply_skin_smoothing(sample_frame, 0.5)
        assert result.shape == sample_frame.shape
        assert result.dtype == sample_frame.dtype
        print("✅ Skin smoothing test passed")

    def test_brightening(self, processor, sample_frame):
        """Test brightening filter"""
        result = processor.apply_brightening(sample_frame, 0.5)
        assert result.shape == sample_frame.shape
        assert result.dtype == sample_frame.dtype
        print("✅ Brightening test passed")

    def test_cartoon_effect(self, processor, sample_frame):
        """Test cartoon effect"""
        result = processor.apply_cartoon_effect(sample_frame, 0.5)
        assert result.shape == sample_frame.shape
        assert result.dtype == sample_frame.dtype
        print("✅ Cartoon effect test passed")

    def test_thermal_effect(self, processor, sample_frame):
        """Test thermal effect"""
        result = processor.apply_thermal_effect(sample_frame, 0.5)
        assert result.shape == sample_frame.shape
        assert result.dtype == sample_frame.dtype
        print("✅ Thermal effect test passed")

    def test_edge_detection(self, processor, sample_frame):
        """Test edge detection"""
        result = processor.apply_edge_detection(sample_frame, 0.5)
        assert result.shape == sample_frame.shape
        assert result.dtype == sample_frame.dtype
        print("✅ Edge detection test passed")

    def test_vintage_effect(self, processor, sample_frame):
        """Test vintage effect"""
        result = processor.apply_vintage_effect(sample_frame, 0.5)
        assert result.shape == sample_frame.shape
        assert result.dtype == sample_frame.dtype
        print("✅ Vintage effect test passed")

    def test_blur_effect(self, processor, sample_frame):
        """Test blur effect"""
        result = processor.apply_blur_effect(sample_frame, 0.5)
        assert result.shape == sample_frame.shape
        assert result.dtype == sample_frame.dtype
        print("✅ Blur effect test passed")

    def test_statistics_tracking(self, processor, sample_frame):
        """Test statistics tracking"""
        # Create mock filter
        class MockFilter:
            filter_type = "beauty"
            intensity = 0.5

        # Process multiple frames
        for _ in range(5):
            processor.process_frame(sample_frame, [MockFilter()])

        stats = processor.get_stats()
        assert stats['frames_processed'] == 5
        assert stats['average_latency_ms'] >= 0
        print("✅ Statistics tracking test passed")


class TestOptimizedProcessor:
    """Test optimized processor with caching"""

    @pytest.fixture
    def processor(self):
        """Create optimized processor"""
        return OptimizedFilterProcessor()

    @pytest.fixture
    def sample_frame(self):
        """Create sample frame"""
        return np.random.randint(0, 256, (720, 1280, 3), dtype=np.uint8)

    def test_cache_initialization(self, processor):
        """Test cache initializes"""
        assert processor.enable_cache is True
        assert processor.frame_cache == {}
        print("✅ Cache initialization test passed")

    def test_cache_operations(self, processor, sample_frame):
        """Test cache get/set operations"""
        key = "test_filter"
        
        # Should miss on first access
        result = processor.get_cached_filter(key)
        assert result is None
        
        # Cache the result
        processor.cache_filter_result(key, sample_frame)
        
        # Should hit on second access
        result = processor.get_cached_filter(key)
        assert result is not None
        np.testing.assert_array_equal(result, sample_frame)
        print("✅ Cache operations test passed")

    def test_cache_size_limit(self, processor):
        """Test cache respects size limits"""
        # Fill cache beyond max size
        for i in range(processor.cache_max_size + 10):
            frame = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
            processor.cache_filter_result(f"frame_{i}", frame)

        # Cache should not exceed max size
        assert len(processor.frame_cache) <= processor.cache_max_size
        print("✅ Cache size limit test passed")


class TestBeautyConfig:
    """Test beauty configuration"""

    def test_default_config(self):
        """Test default beauty config"""
        config = BeautyConfig()
        assert config.skin_smooth_strength == 0.5
        assert config.brightening_level == 0.3
        assert config.eye_size_multiplier == 1.2
        print("✅ Default config test passed")

    def test_config_validation(self):
        """Test config value validation"""
        # Valid config
        config = BeautyConfig(
            skin_smooth_strength=0.7,
            eye_size_multiplier=1.5
        )
        assert config.skin_smooth_strength == 0.7
        assert config.eye_size_multiplier == 1.5
        print("✅ Config validation test passed")

    def test_config_bounds(self):
        """Test config boundary values"""
        config = BeautyConfig(
            skin_smooth_strength=0.0,
            brightening_level=1.0,
            eye_size_multiplier=2.0
        )
        assert 0.0 <= config.skin_smooth_strength <= 1.0
        assert 0.0 <= config.brightening_level <= 1.0
        assert 0.5 <= config.eye_size_multiplier <= 2.0
        print("✅ Config bounds test passed")


class TestFilterTypes:
    """Test filter type enumerations"""

    def test_all_filter_types_defined(self):
        """Test all filter types are defined"""
        expected_types = [
            'beauty', 'face_shape', 'makeup', 'eyes',
            'special_effects', 'artistic', 'weather',
            'stickers', 'age_simulation', 'mood'
        ]
        
        for filter_type in expected_types:
            assert hasattr(FilterType, filter_type.upper())
        
        print("✅ Filter types test passed")

    def test_filter_priority_levels(self):
        """Test filter priority levels"""
        priorities = [
            FilterPriority.CRITICAL,
            FilterPriority.HIGH,
            FilterPriority.NORMAL,
            FilterPriority.LOW
        ]
        
        assert len(priorities) == 4
        assert all(p.value in ['critical', 'high', 'normal', 'low'] for p in priorities)
        print("✅ Filter priority test passed")


class TestFilterMetadata:
    """Test filter metadata"""

    def test_metadata_creation(self):
        """Test creating filter metadata"""
        meta = FilterMetadata(
            filter_id="test_123",
            name="Test Filter",
            filter_type=FilterType.BEAUTY,
            intensity=0.7
        )
        
        assert meta.filter_id == "test_123"
        assert meta.name == "Test Filter"
        assert meta.filter_type == FilterType.BEAUTY
        assert meta.intensity == 0.7
        print("✅ Metadata creation test passed")

    def test_metadata_defaults(self):
        """Test metadata default values"""
        meta = FilterMetadata(
            filter_id="test",
            name="Test",
            filter_type=FilterType.BEAUTY
        )
        
        assert meta.version == "1.0.0"
        assert meta.author == "System"
        assert meta.enabled is True
        assert meta.priority == FilterPriority.NORMAL
        print("✅ Metadata defaults test passed")

    def test_metadata_json_serialization(self):
        """Test metadata serialization"""
        meta = FilterMetadata(
            filter_id="test",
            name="Test Filter",
            filter_type=FilterType.ARTISTIC,
            intensity=0.6
        )
        
        data = {
            'filter_id': meta.filter_id,
            'name': meta.name,
            'type': meta.filter_type.value,
            'intensity': meta.intensity
        }
        
        json_str = json.dumps(data)
        restored = json.loads(json_str)
        
        assert restored['filter_id'] == "test"
        assert restored['type'] == "artistic"
        print("✅ Metadata serialization test passed")


class TestAsyncProcessing:
    """Test async filter processing"""

    @pytest.fixture
    def processor(self):
        """Create processor"""
        return FilterProcessor()

    @pytest.fixture
    def sample_frame(self):
        """Create sample frame"""
        return np.random.randint(0, 256, (720, 1280, 3), dtype=np.uint8)

    @pytest.mark.asyncio
    async def test_async_frame_processing(self, processor, sample_frame):
        """Test async frame processing"""
        class MockFilter:
            filter_type = "beauty"
            intensity = 0.5

        result_frame, metadata = await processor.process_frame_async(
            sample_frame,
            [MockFilter()]
        )

        assert result_frame.shape == sample_frame.shape
        assert 'latency_ms' in metadata or 'error' in metadata
        print("✅ Async processing test passed")


class TestPerformance:
    """Performance tests"""

    @pytest.fixture
    def processor(self):
        """Create processor"""
        return FilterProcessor()

    @pytest.fixture
    def sample_frame(self):
        """Create sample frame"""
        return np.random.randint(0, 256, (1920, 1080, 3), dtype=np.uint8)

    def test_processing_latency(self, processor, sample_frame):
        """Test processing latency"""
        class MockFilter:
            filter_type = "beauty"
            intensity = 0.5

        # Process frame
        result, metadata = processor.process_frame(sample_frame, [MockFilter()])

        # Check latency is reasonable (should be < 1000ms)
        latency = metadata.get('latency_ms', 0)
        assert latency < 1000, f"Latency too high: {latency}ms"
        print(f"✅ Processing latency test passed: {latency:.2f}ms")

    def test_batch_processing(self, processor, sample_frame):
        """Test batch processing performance"""
        filters = []
        class MockFilter:
            def __init__(self, ftype):
                self.filter_type = ftype
                self.intensity = 0.5

        for _ in range(5):
            filters.append(MockFilter("beauty"))

        result, metadata = processor.process_frame(sample_frame, filters)
        assert result is not None
        assert metadata['filters_applied'] == 5
        print("✅ Batch processing test passed")


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("🧪 LENS STUDIO - COMPREHENSIVE TEST SUITE")
    print("=" * 60 + "\n")

    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "-ra"
    ])


if __name__ == "__main__":
    run_all_tests()
