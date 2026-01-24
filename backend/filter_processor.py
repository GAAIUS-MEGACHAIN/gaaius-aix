"""
Filter Processor - Real-time frame processing engine
Handles batch filter application with performance optimization
"""

import cv2
import numpy as np
import mediapipe as mp
from typing import List, Tuple, Optional, Dict, Any
import logging
import base64
from io import BytesIO
from PIL import Image
import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

logger = logging.getLogger(__name__)


class FilterProcessor:
    """Production-grade real-time filter processing engine"""

    def __init__(self, max_workers: int = 4):
        """Initialize filter processor with thread pool"""
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.frame_buffer = {}
        self.processing_stats = {
            'frames_processed': 0,
            'average_latency': 0.0,
            'filter_cache': {}
        }

        # Initialize MediaPipe
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=4,
            refine_landmarks=True,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )

        logger.info("✅ FilterProcessor initialized")

    def detect_faces(self, frame: np.ndarray) -> Optional[Dict[str, Any]]:
        """Detect faces and extract landmarks"""
        try:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.face_mesh.process(rgb_frame)

            if not results.multi_face_landmarks:
                return None

            h, w, _ = frame.shape
            landmarks_data = []

            for face_landmarks in results.multi_face_landmarks:
                landmarks = np.array(
                    [[lm.x * w, lm.y * h, lm.z] for lm in face_landmarks.landmark]
                )

                # Face bounding box
                min_x = int(np.min(landmarks[:, 0]))
                max_x = int(np.max(landmarks[:, 0]))
                min_y = int(np.min(landmarks[:, 1]))
                max_y = int(np.max(landmarks[:, 1]))

                landmarks_data.append({
                    'landmarks': landmarks,
                    'bbox': (min_x, min_y, max_x - min_x, max_y - min_y),
                    'face_width': max_x - min_x,
                    'face_height': max_y - min_y
                })

            return {'faces': landmarks_data, 'frame_shape': frame.shape}

        except Exception as e:
            logger.error(f"Face detection error: {e}")
            return None

    def apply_skin_smoothing(self, frame: np.ndarray, strength: float) -> np.ndarray:
        """Apply bilateral filtering for skin smoothing"""
        d = 9
        sigma_color = 75 + (strength * 50)
        sigma_space = 75 + (strength * 50)

        smoothed = cv2.bilateralFilter(frame, d, int(sigma_color), int(sigma_space))
        result = cv2.addWeighted(frame, 1 - strength, smoothed, strength, 0)
        return result

    def apply_brightening(self, frame: np.ndarray, level: float) -> np.ndarray:
        """Apply brightening effect"""
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)

        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        l = cv2.addWeighted(l, 1 + (level * 0.3), l, 0, level * 20)

        lab = cv2.merge([l, a, b])
        result = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        return result

    def apply_cartoon_effect(self, frame: np.ndarray, intensity: float) -> np.ndarray:
        """Apply cartoon filter effect"""
        num_colors = int(8 + intensity * 16)

        data = frame.reshape((-1, 3)).astype(np.float32)
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        _, labels, centers = cv2.kmeans(
            data, num_colors, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS
        )

        centers = np.uint8(centers)
        result = centers[labels.flatten()].reshape(frame.shape)

        gray = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 100, 200)
        edges_colored = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

        result = cv2.subtract(result, edges_colored)
        return result

    def apply_thermal_effect(self, frame: np.ndarray, intensity: float) -> np.ndarray:
        """Apply thermal imaging effect"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)

        thermal = cv2.applyColorMap(enhanced, cv2.COLORMAP_JET)
        result = cv2.addWeighted(frame, 1 - intensity, thermal, intensity, 0)
        return result

    def apply_edge_detection(self, frame: np.ndarray, intensity: float) -> np.ndarray:
        """Apply edge detection filter"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        edges_colored = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

        result = cv2.addWeighted(frame, 1 - intensity, edges_colored, intensity, 0)
        return result

    def apply_vintage_effect(self, frame: np.ndarray, intensity: float) -> np.ndarray:
        """Apply vintage film effect"""
        result = frame.copy().astype(np.float32)

        # Sepia tone
        kernel = np.array(
            [[0.272, 0.534, 0.131],
             [0.349, 0.686, 0.168],
             [0.393, 0.769, 0.189]]
        )

        result = cv2.transform(result, kernel)
        result = np.clip(result, 0, 255)

        # Reduce contrast
        result = cv2.addWeighted(result, 0.9, np.full_like(result, 128), 0.1, 0)

        # Add grain
        noise = np.random.normal(0, intensity * 15, result.shape)
        result = np.clip(result + noise, 0, 255)

        return result.astype(np.uint8)

    def apply_blur_effect(self, frame: np.ndarray, intensity: float) -> np.ndarray:
        """Apply background blur effect"""
        kernel_size = int(5 + intensity * 25)
        if kernel_size % 2 == 0:
            kernel_size += 1

        blurred = cv2.GaussianBlur(frame, (kernel_size, kernel_size), 0)
        result = cv2.addWeighted(frame, 0.7, blurred, 0.3, 0)
        return result

    def process_frame(
        self,
        frame: np.ndarray,
        filters: List[Any]
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Process frame with multiple filters
        Returns: (processed_frame, metadata)
        """
        start_time = datetime.utcnow()
        result_frame = frame.copy()

        try:
            # Detect faces
            face_data = self.detect_faces(frame)

            for filter_obj in filters:
                filter_type = getattr(filter_obj, 'filter_type', None)
                intensity = getattr(filter_obj, 'intensity', 0.5)

                if filter_type == 'beauty':
                    result_frame = self.apply_skin_smoothing(result_frame, intensity)
                    result_frame = self.apply_brightening(result_frame, intensity)

                elif filter_type == 'cartoon':
                    result_frame = self.apply_cartoon_effect(result_frame, intensity)

                elif filter_type == 'thermal':
                    result_frame = self.apply_thermal_effect(result_frame, intensity)

                elif filter_type == 'edge_detect':
                    result_frame = self.apply_edge_detection(result_frame, intensity)

                elif filter_type == 'vintage':
                    result_frame = self.apply_vintage_effect(result_frame, intensity)

                elif filter_type == 'blur':
                    result_frame = self.apply_blur_effect(result_frame, intensity)

            # Calculate latency
            elapsed = (datetime.utcnow() - start_time).total_seconds() * 1000
            self.processing_stats['frames_processed'] += 1
            self.processing_stats['average_latency'] = (
                (self.processing_stats['average_latency'] +
                 elapsed) / 2
            )

            metadata = {
                'frames_processed': self.processing_stats['frames_processed'],
                'latency_ms': elapsed,
                'filters_applied': len(filters),
                'faces_detected': len(face_data['faces']) if face_data else 0,
                'timestamp': start_time.isoformat()
            }

            return result_frame, metadata

        except Exception as e:
            logger.error(f"Frame processing error: {e}")
            return frame, {'error': str(e), 'timestamp': start_time.isoformat()}

    @staticmethod
    def encode_frame_to_base64(frame: np.ndarray) -> str:
        """Encode frame to base64 for transmission"""
        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        return base64.b64encode(buffer).decode('utf-8')

    @staticmethod
    def decode_frame_from_base64(frame_data: str) -> np.ndarray:
        """Decode base64 frame to numpy array"""
        decoded = base64.b64decode(frame_data)
        frame = cv2.imdecode(np.frombuffer(decoded, np.uint8), cv2.IMREAD_COLOR)
        return frame

    def get_stats(self) -> Dict[str, Any]:
        """Get processing statistics"""
        return {
            'frames_processed': self.processing_stats['frames_processed'],
            'average_latency_ms': round(self.processing_stats['average_latency'], 2),
            'timestamp': datetime.utcnow().isoformat()
        }

    def reset_stats(self):
        """Reset processing statistics"""
        self.processing_stats = {
            'frames_processed': 0,
            'average_latency': 0.0,
            'filter_cache': {}
        }
        logger.info("📊 Statistics reset")

    async def process_frame_async(
        self,
        frame: np.ndarray,
        filters: List[Any]
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Async wrapper for frame processing"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self.process_frame,
            frame,
            filters
        )

    def cleanup(self):
        """Cleanup resources"""
        self.executor.shutdown(wait=True)
        self.face_mesh.close()
        logger.info("🛑 FilterProcessor cleanup complete")


class OptimizedFilterProcessor(FilterProcessor):
    """
    Optimized version with caching and GPU acceleration potential
    """

    def __init__(self, max_workers: int = 4, enable_cache: bool = True):
        super().__init__(max_workers)
        self.enable_cache = enable_cache
        self.frame_cache = {}
        self.cache_max_size = 100

    def get_cached_filter(self, filter_key: str) -> Optional[np.ndarray]:
        """Get cached filter result"""
        if self.enable_cache and filter_key in self.frame_cache:
            return self.frame_cache[filter_key]
        return None

    def cache_filter_result(self, filter_key: str, result: np.ndarray):
        """Cache filter result"""
        if not self.enable_cache:
            return

        if len(self.frame_cache) >= self.cache_max_size:
            # Remove oldest entry
            oldest_key = list(self.frame_cache.keys())[0]
            del self.frame_cache[oldest_key]

        self.frame_cache[filter_key] = result

    def process_frame_optimized(
        self,
        frame: np.ndarray,
        filters: List[Any]
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Process with optimization techniques"""
        # Downscale for faster processing
        h, w = frame.shape[:2]
        scale = 0.5
        frame_small = cv2.resize(frame, (int(w * scale), int(h * scale)))

        # Process small frame
        result_small, metadata = self.process_frame(frame_small, filters)

        # Upscale back
        result = cv2.resize(result_small, (w, h))

        return result, metadata


# Singleton instance
_processor_instance: Optional[FilterProcessor] = None


def get_processor(optimized: bool = False) -> FilterProcessor:
    """Get or create processor instance"""
    global _processor_instance

    if _processor_instance is None:
        if optimized:
            _processor_instance = OptimizedFilterProcessor()
        else:
            _processor_instance = FilterProcessor()

    return _processor_instance


def cleanup_processor():
    """Cleanup processor instance"""
    global _processor_instance
    if _processor_instance:
        _processor_instance.cleanup()
        _processor_instance = None


logger.info("✅ Filter Processor Module Ready - Production Grade")
