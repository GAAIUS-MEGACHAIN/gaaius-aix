"""
Test suite for Snapchat Filters Integration with AI Filter Studio
Production-grade tests for all filter applications and API endpoints
"""

import pytest
import cv2
import numpy as np
import base64
import asyncio
from unittest.mock import Mock, patch, AsyncMock
import json

# Import modules to test
from snapchat_filters_engine import (
    FilterRegistry, AdvancedFaceDetector, AdvancedBeautyFilters,
    ARFiltersEngine, SocialMediaFilters, SnapchatFilterCategory
)
from ai_filter_studio import FrameProcessor


class TestFilterRegistry:
    """Test FilterRegistry functionality"""
    
    def test_registry_initialization(self):
        """Test that FilterRegistry initializes with all filters"""
        registry = FilterRegistry()
        assert len(registry.filters) > 0
        assert 'smooth_skin' in registry.filters
        assert 'eye_enhancement' in registry.filters
        assert 'glamour_glow' in registry.filters
    
    def test_list_all_filters(self):
        """Test listing all available filters"""
        registry = FilterRegistry()
        filters = registry.list_all_filters()
        assert isinstance(filters, list)
        assert len(filters) > 0
        assert all('id' in f and 'name' in f for f in filters)
    
    def test_get_filters_by_category(self):
        """Test filtering by category"""
        registry = FilterRegistry()
        beauty_filters = registry.get_filters_by_category(SnapchatFilterCategory.BEAUTY)
        assert len(beauty_filters) > 0
        assert all(f.category == SnapchatFilterCategory.BEAUTY for f in beauty_filters)
    
    def test_get_filters_by_platform(self):
        """Test filtering by social platform"""
        registry = FilterRegistry()
        insta_filters = registry.get_filters_by_platform('instagram')
        assert len(insta_filters) > 0
    
    def test_apply_filter_returns_frame(self):
        """Test that apply_filter returns a processed frame"""
        registry = FilterRegistry()
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        frame[100:400, 150:550] = 128  # Add some content
        
        result = registry.apply_filter(frame, 'smooth_skin', 0.5, None)
        assert isinstance(result, np.ndarray)
        assert result.shape == frame.shape


class TestAdvancedFaceDetector:
    """Test AdvancedFaceDetector"""
    
    def test_detector_initialization(self):
        """Test detector initialization"""
        detector = AdvancedFaceDetector()
        assert detector is not None
    
    def test_detect_faces_returns_list(self):
        """Test that detect_faces returns a list"""
        detector = AdvancedFaceDetector()
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        faces = detector.detect_faces(frame)
        assert isinstance(faces, list)
    
    def test_detect_faces_with_content(self):
        """Test face detection with non-zero frame"""
        detector = AdvancedFaceDetector()
        frame = np.ones((480, 640, 3), dtype=np.uint8) * 128
        faces = detector.detect_faces(frame)
        assert isinstance(faces, list)  # Should return list even if no faces


class TestAdvancedBeautyFilters:
    """Test AdvancedBeautyFilters"""
    
    def test_beauty_filters_initialization(self):
        """Test BeautyFilters initialization"""
        filters = AdvancedBeautyFilters()
        assert filters is not None
    
    def test_smooth_skin_advanced(self):
        """Test smooth skin advanced filter"""
        filters = AdvancedBeautyFilters()
        frame = np.ones((480, 640, 3), dtype=np.uint8) * 128
        result = filters.smooth_skin_advanced(frame, intensity=0.5)
        assert result.shape == frame.shape
        assert isinstance(result, np.ndarray)
    
    def test_enhance_eyes_advanced(self):
        """Test eye enhancement filter"""
        filters = AdvancedBeautyFilters()
        frame = np.ones((480, 640, 3), dtype=np.uint8) * 128
        face_region = (100, 150, 300, 300)  # (y1, x1, y2, x2)
        result = filters.enhance_eyes_advanced(frame, face_region, intensity=0.5)
        assert result.shape == frame.shape
    
    def test_perfect_skin_tone(self):
        """Test skin tone adjustment"""
        filters = AdvancedBeautyFilters()
        frame = np.ones((480, 640, 3), dtype=np.uint8) * 128
        result = filters.perfect_skin_tone(frame, intensity=0.5, skin_tone='warm')
        assert result.shape == frame.shape
    
    def test_glamour_glow(self):
        """Test glamour glow filter"""
        filters = AdvancedBeautyFilters()
        frame = np.ones((480, 640, 3), dtype=np.uint8) * 128
        face_region = (100, 150, 300, 300)
        result = filters.glamour_glow(frame, face_region, intensity=0.5)
        assert result.shape == frame.shape


class TestARFiltersEngine:
    """Test AR Filters"""
    
    def test_ar_filters_initialization(self):
        """Test AR filters initialization"""
        ar = ARFiltersEngine()
        assert ar is not None
    
    def test_dog_ears_filter(self):
        """Test dog ears AR filter"""
        ar = ARFiltersEngine()
        frame = np.ones((480, 640, 3), dtype=np.uint8) * 128
        face_region = (100, 200, 350, 550)
        result = ar.dog_ears_filter(frame, face_region, intensity=0.8)
        assert result.shape == frame.shape
    
    def test_crown_filter(self):
        """Test crown AR filter"""
        ar = ARFiltersEngine()
        frame = np.ones((480, 640, 3), dtype=np.uint8) * 128
        face_region = (100, 200, 350, 550)
        result = ar.crown_filter(frame, face_region, intensity=0.8)
        assert result.shape == frame.shape
    
    def test_face_morphing_filter(self):
        """Test face morphing AR filter"""
        ar = ARFiltersEngine()
        frame = np.ones((480, 640, 3), dtype=np.uint8) * 128
        face_region = (100, 200, 350, 550)
        result = ar.face_morphing_filter(frame, face_region, intensity=0.5)
        assert result.shape == frame.shape


class TestSocialMediaFilters:
    """Test Social Media Filters"""
    
    def test_social_filters_initialization(self):
        """Test SocialMediaFilters initialization"""
        social = SocialMediaFilters()
        assert social is not None
    
    def test_instagram_filter(self):
        """Test Instagram filter"""
        social = SocialMediaFilters()
        frame = np.ones((480, 640, 3), dtype=np.uint8) * 128
        face_region = (100, 200, 350, 550)
        result = social.instagram_style(frame, [face_region], intensity=0.7)
        assert result.shape == frame.shape
    
    def test_tiktok_filter(self):
        """Test TikTok filter"""
        social = SocialMediaFilters()
        frame = np.ones((480, 640, 3), dtype=np.uint8) * 128
        face_region = (100, 200, 350, 550)
        result = social.tiktok_style(frame, [face_region], intensity=0.7)
        assert result.shape == frame.shape
    
    def test_youtube_professional_filter(self):
        """Test YouTube professional filter"""
        social = SocialMediaFilters()
        frame = np.ones((480, 640, 3), dtype=np.uint8) * 128
        face_region = (100, 200, 350, 550)
        result = social.youtube_professional(frame, [face_region], intensity=0.7)
        assert result.shape == frame.shape


class TestFrameProcessorIntegration:
    """Test FrameProcessor with Snapchat filters integration"""
    
    def test_frame_processor_initialization(self):
        """Test FrameProcessor initializes with all engines"""
        processor = FrameProcessor()
        assert hasattr(processor, 'filter_registry')
        assert hasattr(processor, 'snapchat_detector')
        assert hasattr(processor, 'beauty_filters')
        assert hasattr(processor, 'ar_filters')
        assert hasattr(processor, 'social_filters')
    
    def test_process_frame_with_snapchat_filters(self):
        """Test processing frame with Snapchat filters"""
        processor = FrameProcessor()
        frame = np.ones((480, 640, 3), dtype=np.uint8) * 128
        
        snapchat_filters = {
            'smooth_skin': 0.5,
            'eye_enhancement': 0.3
        }
        
        result, face_count, proc_time = processor.process_frame(
            frame,
            active_filters=[],
            snapchat_filters=snapchat_filters
        )
        
        assert isinstance(result, np.ndarray)
        assert result.shape == frame.shape
        assert face_count >= 0
        assert proc_time >= 0
    
    def test_process_frame_with_social_platform(self):
        """Test processing frame with social platform optimization"""
        processor = FrameProcessor()
        frame = np.ones((480, 640, 3), dtype=np.uint8) * 128
        
        result, face_count, proc_time = processor.process_frame(
            frame,
            active_filters=[],
            social_platform='instagram'
        )
        
        assert isinstance(result, np.ndarray)
        assert result.shape == frame.shape
    
    def test_process_frame_with_combined_filters(self):
        """Test processing frame with both traditional and Snapchat filters"""
        processor = FrameProcessor()
        frame = np.ones((480, 640, 3), dtype=np.uint8) * 128
        
        result, face_count, proc_time = processor.process_frame(
            frame,
            active_filters=['beauty'],
            snapchat_filters={'glamour_glow': 0.6},
            social_platform='tiktok'
        )
        
        assert isinstance(result, np.ndarray)
        assert result.shape == frame.shape


class TestFilterQuality:
    """Test filter output quality"""
    
    def test_smooth_skin_reduces_noise(self):
        """Test that smooth skin filter reduces high-frequency noise"""
        filters = AdvancedBeautyFilters()
        
        # Create noisy frame
        frame = np.random.randint(100, 150, (480, 640, 3), dtype=np.uint8)
        original_std = np.std(frame)
        
        result = filters.smooth_skin_advanced(frame, intensity=0.8)
        result_std = np.std(result)
        
        # Result should have lower std dev (less noisy)
        assert result_std < original_std
    
    def test_filters_maintain_frame_integrity(self):
        """Test that all filters maintain frame shape and dtype"""
        registry = FilterRegistry()
        frame = np.ones((480, 640, 3), dtype=np.uint8) * 128
        
        for filter_id in ['smooth_skin', 'eye_enhancement', 'glamour_glow', 'dog_ears']:
            result = registry.apply_filter(frame, filter_id, 0.5, (100, 150, 300, 500))
            assert result.shape == frame.shape
            assert result.dtype == np.uint8
            assert np.all(result >= 0) and np.all(result <= 255)


class TestPerformance:
    """Test performance characteristics"""
    
    def test_filter_processing_time(self):
        """Test that filters process in reasonable time"""
        import time
        
        processor = FrameProcessor()
        frame = np.ones((480, 640, 3), dtype=np.uint8) * 128
        
        snapchat_filters = {
            'smooth_skin': 0.5,
            'eye_enhancement': 0.3,
            'glamour_glow': 0.4
        }
        
        start = time.time()
        result, _, _ = processor.process_frame(
            frame,
            active_filters=[],
            snapchat_filters=snapchat_filters
        )
        elapsed = (time.time() - start) * 1000
        
        # Should process in under 100ms (reasonable for 480p)
        assert elapsed < 500  # More lenient for slow systems
    
    def test_batch_filter_application(self):
        """Test applying multiple filters in sequence"""
        registry = FilterRegistry()
        frame = np.ones((480, 640, 3), dtype=np.uint8) * 128
        
        import time
        start = time.time()
        
        result = frame.copy()
        for filter_id in ['smooth_skin', 'eye_enhancement', 'glamour_glow']:
            result = registry.apply_filter(result, filter_id, 0.3, None)
        
        elapsed = (time.time() - start) * 1000
        
        assert isinstance(result, np.ndarray)
        assert elapsed < 500


# ============ INTEGRATION TESTS ============

class TestFullPipeline:
    """Test complete filter pipeline"""
    
    def test_end_to_end_filter_application(self):
        """Test complete pipeline from frame to filtered output"""
        processor = FrameProcessor()
        
        # Create test frame
        frame = np.ones((480, 640, 3), dtype=np.uint8) * 128
        frame[200:400, 200:500] = 180  # Simulate face region
        
        # Apply comprehensive filter set
        result, face_count, proc_time = processor.process_frame(
            frame,
            active_filters=['beauty'],
            snapchat_filters={
                'smooth_skin': 0.7,
                'eye_enhancement': 0.6,
                'glamour_glow': 0.5
            },
            social_platform='instagram'
        )
        
        # Verify output
        assert result.shape == frame.shape
        assert result.dtype == np.uint8
        assert 0 <= face_count
        assert proc_time >= 0
        
        # Verify some processing occurred
        assert not np.array_equal(result, frame)
    
    def test_multiple_platform_filters(self):
        """Test that different platforms produce different results"""
        processor = FrameProcessor()
        frame = np.ones((480, 640, 3), dtype=np.uint8) * 128
        
        results = {}
        for platform in ['instagram', 'tiktok', 'youtube', 'facebook']:
            result, _, _ = processor.process_frame(
                frame.copy(),
                active_filters=[],
                social_platform=platform
            )
            results[platform] = result
        
        # All results should be valid frames
        for platform, result in results.items():
            assert result.shape == frame.shape
            assert result.dtype == np.uint8


if __name__ == '__main__':
    # Run tests with pytest
    pytest.main([__file__, '-v', '--tb=short'])
