"""
Snapchat Lens Studio Clone - Enterprise Filter Engine
Production-grade real-time AR filter processing
Real computer vision implementation with MediaPipe, OpenCV
"""

import cv2
import numpy as np
import mediapipe as mp
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import logging
from datetime import datetime
import base64
from PIL import Image
import io
import threading
from collections import deque

logger = logging.getLogger(__name__)


class FilterType(str, Enum):
    """Filter categories"""
    BEAUTY = "beauty"
    FACE_SHAPE = "face_shape"
    MAKEUP = "makeup"
    EYES = "eyes"
    SPECIAL_EFFECTS = "special_effects"
    ARTISTIC = "artistic"
    WEATHER = "weather"
    STICKERS = "stickers"
    AGE_SIMULATION = "age_simulation"
    MOOD = "mood"


class FilterPriority(str, Enum):
    """Filter processing priority"""
    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


@dataclass
class FaceFeatures:
    """Detected face features from MediaPipe"""
    landmarks: np.ndarray
    face_mesh: np.ndarray
    left_eye: np.ndarray
    right_eye: np.ndarray
    mouth: np.ndarray
    face_bbox: Tuple[int, int, int, int]
    face_contour: np.ndarray
    left_iris: np.ndarray
    right_iris: np.ndarray
    face_size: float
    rotation_angle: float
    pose_rotation: np.ndarray


@dataclass
class FilterMetadata:
    """Filter configuration and metadata"""
    filter_id: str
    name: str
    filter_type: FilterType
    version: str = "1.0.0"
    author: str = "System"
    created_at: datetime = field(default_factory=datetime.utcnow)
    intensity: float = 1.0
    parameters: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    priority: FilterPriority = FilterPriority.NORMAL
    enabled: bool = True


class FaceDetector:
    """MediaPipe-based real-time face detection"""
    
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=4,
            refine_landmarks=True,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            smooth_landmarks=True
        )
    
    def detect_face(self, frame: np.ndarray) -> Optional[FaceFeatures]:
        """Detect face and return features"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)
        
        if not results.multi_face_landmarks:
            return None
        
        landmarks = results.multi_face_landmarks[0]
        h, w, _ = frame.shape
        
        # Extract key landmarks
        landmarks_array = np.array(
            [[lm.x * w, lm.y * h, lm.z] for lm in landmarks.landmark]
        )
        
        # Face bounding box
        min_x = int(np.min(landmarks_array[:, 0]))
        max_x = int(np.max(landmarks_array[:, 0]))
        min_y = int(np.min(landmarks_array[:, 1]))
        max_y = int(np.max(landmarks_array[:, 1]))
        
        face_bbox = (min_x, min_y, max_x, max_y)
        face_size = (max_x - min_x) * (max_y - min_y)
        
        # Eye landmarks (468 and 473 are left/right iris centers)
        left_eye = landmarks_array[33:133]
        right_eye = landmarks_array[263:362]
        mouth = landmarks_array[61:95]
        
        # Calculate rotation angle
        left_eye_center = left_eye.mean(axis=0)
        right_eye_center = right_eye.mean(axis=0)
        rotation_angle = np.arctan2(
            right_eye_center[1] - left_eye_center[1],
            right_eye_center[0] - left_eye_center[0]
        ) * 180 / np.pi
        
        # Pose for rotation
        pose_results = self.pose.process(rgb_frame)
        pose_rotation = np.array([0, 0, 0])
        if pose_results.pose_landmarks:
            # Extract head rotation from pose
            shoulder_left = pose_results.pose_landmarks[11]
            shoulder_right = pose_results.pose_landmarks[12]
            pose_rotation = np.array([
                shoulder_left.x - shoulder_right.x,
                shoulder_left.y - shoulder_right.y,
                0
            ])
        
        return FaceFeatures(
            landmarks=landmarks_array,
            face_mesh=landmarks_array,
            left_eye=left_eye,
            right_eye=right_eye,
            mouth=mouth,
            face_bbox=face_bbox,
            face_contour=landmarks_array[0:17],
            left_iris=landmarks_array[[468]],
            right_iris=landmarks_array[[473]],
            face_size=face_size,
            rotation_angle=rotation_angle,
            pose_rotation=pose_rotation
        )


class BeautyFilters:
    """Real-time beauty and skin enhancement filters"""
    
    @staticmethod
    def skin_smoothing(frame: np.ndarray, intensity: float = 0.8) -> np.ndarray:
        """Advanced skin smoothing using bilateral filtering"""
        result = frame.copy()
        
        # Apply bilateral filter for skin smoothing
        for _ in range(int(intensity * 3)):
            result = cv2.bilateralFilter(result, 9, 75, 75)
        
        # Blend with original
        result = cv2.addWeighted(result, intensity, frame, 1 - intensity, 0)
        return result
    
    @staticmethod
    def skin_brightening(frame: np.ndarray, intensity: float = 0.6) -> np.ndarray:
        """Skin brightening and whitening"""
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        
        # Enhance L channel (lightness)
        l = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(l)
        l = np.clip(l.astype(float) + (255 - l.astype(float)) * intensity * 0.3, 0, 255).astype(np.uint8)
        
        lab = cv2.merge([l, a, b])
        result = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        
        return cv2.addWeighted(result, 0.5 + intensity * 0.5, frame, 0.5 - intensity * 0.5, 0)
    
    @staticmethod
    def blusher(frame: np.ndarray, face_features: FaceFeatures, color: Tuple[int, int, int], intensity: float = 0.6) -> np.ndarray:
        """Add natural-looking blush to cheeks"""
        result = frame.copy()
        mask = np.zeros(frame.shape[:2], dtype=np.uint8)
        
        # Cheek areas (from face mesh landmarks)
        left_cheek = face_features.landmarks[[115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126]].astype(int)
        right_cheek = face_features.landmarks[[345, 346, 347, 348, 349, 350, 351, 352, 353, 354, 355, 356]].astype(int)
        
        # Draw blush areas
        for cheek in [left_cheek, right_cheek]:
            cv2.polylines(mask, [cheek[:, :2]], True, 255, -1)
        
        # Apply gaussian blur for smooth transition
        mask = cv2.GaussianBlur(mask, (51, 51), 0)
        
        # Blend blush color
        blush_frame = frame.copy()
        blush_frame[mask > 0] = cv2.addWeighted(
            blush_frame[mask > 0],
            1 - intensity,
            np.full_like(blush_frame[mask > 0]), color),
            intensity,
            0
        )
        
        return cv2.addWeighted(result, 1 - intensity * 0.5, blush_frame, intensity * 0.5, 0)
    
    @staticmethod
    def lipstick(frame: np.ndarray, face_features: FaceFeatures, color: Tuple[int, int, int], intensity: float = 0.8) -> np.ndarray:
        """Apply lipstick effect"""
        result = frame.copy()
        mask = np.zeros(frame.shape[:2], dtype=np.uint8)
        
        # Mouth region
        mouth_points = face_features.mouth[:, :2].astype(int)
        cv2.polylines(mask, [mouth_points], True, 255, -1)
        
        # Smooth edges
        mask = cv2.GaussianBlur(mask, (21, 21), 0)
        
        # Apply lipstick
        alpha = mask.astype(float) / 255.0 * intensity
        for c in range(3):
            result[:, :, c] = (
                result[:, :, c] * (1 - alpha) +
                color[c] * alpha
            )
        
        return result
    
    @staticmethod
    def eye_makeup(frame: np.ndarray, face_features: FaceFeatures, intensity: float = 0.7) -> np.ndarray:
        """Apply eye makeup (eyeliner, eyeshadow)"""
        result = frame.copy()
        
        # Eyeliner
        left_eyelid = face_features.landmarks[[33, 34, 35, 36, 37, 38, 39, 40, 41]].astype(int)
        right_eyelid = face_features.landmarks[[263, 264, 265, 266, 267, 268, 269, 270, 271]].astype(int)
        
        eyeliner_color = (20, 20, 20)  # Dark color
        thickness = int(2 * intensity)
        
        cv2.polylines(result, [left_eyelid[:, :2]], False, eyeliner_color, thickness)
        cv2.polylines(result, [right_eyelid[:, :2]], False, eyeliner_color, thickness)
        
        return result


class FaceShapeFilters:
    """Face geometry and shape modification filters"""
    
    @staticmethod
    def face_slimming(frame: np.ndarray, face_features: FaceFeatures, intensity: float = 0.6) -> np.ndarray:
        """Slim down face using liquify effect"""
        result = frame.copy()
        h, w, _ = frame.shape
        
        # Get face contour
        contour = face_features.face_contour[:, :2].astype(int)
        
        # Create liquify map
        map_x = np.arange(w, dtype=np.float32)
        map_y = np.arange(h, dtype=np.float32)
        map_x, map_y = np.meshgrid(map_x, map_y)
        
        # Inward liquify effect
        center_x = (face_features.face_bbox[0] + face_features.face_bbox[2]) / 2
        center_y = (face_features.face_bbox[1] + face_features.face_bbox[3]) / 2
        
        dx = map_x - center_x
        dy = map_y - center_y
        dist = np.sqrt(dx**2 + dy**2)
        
        # Apply inward deformation
        radius = np.sqrt((face_features.face_bbox[2] - face_features.face_bbox[0])**2 +
                        (face_features.face_bbox[3] - face_features.face_bbox[1])**2) / 2
        
        mask = (dist < radius).astype(float)
        deform = 1 - (intensity * 0.3 * mask)
        
        map_x = (map_x - center_x) * deform + center_x
        map_y = (map_y - center_y) * deform + center_y
        
        # Clamp values
        map_x = np.clip(map_x, 0, w - 1).astype(np.float32)
        map_y = np.clip(map_y, 0, h - 1).astype(np.float32)
        
        result = cv2.remap(result, map_x, map_y, cv2.INTER_LINEAR)
        return result
    
    @staticmethod
    def jawline_enhancement(frame: np.ndarray, face_features: FaceFeatures, intensity: float = 0.7) -> np.ndarray:
        """Enhance jawline definition"""
        result = frame.copy()
        
        # Jawline area (landmarks 10-16)
        jawline = face_features.face_contour[5:12, :2].astype(int)
        
        # Create shadow for definition
        mask = np.zeros(frame.shape[:2], dtype=np.uint8)
        cv2.polylines(mask, [jawline], False, 255, 3)
        mask = cv2.GaussianBlur(mask, (15, 15), 0)
        
        # Apply subtle darkening
        alpha = mask.astype(float) / 255.0 * intensity * 0.5
        for c in range(3):
            result[:, :, c] = (result[:, :, c] * (1 - alpha) + 
                              result[:, :, c] * 0.7 * alpha).astype(np.uint8)
        
        return result
    
    @staticmethod
    def big_eyes(frame: np.ndarray, face_features: FaceFeatures, intensity: float = 0.7) -> np.ndarray:
        """Enlarge eyes effect"""
        result = frame.copy()
        h, w, _ = frame.shape
        
        # Get eye centers
        left_eye_center = face_features.left_eye.mean(axis=0)
        right_eye_center = face_features.right_eye.mean(axis=0)
        
        # Create liquify maps
        map_x = np.arange(w, dtype=np.float32)
        map_y = np.arange(h, dtype=np.float32)
        map_x, map_y = np.meshgrid(map_x, map_y)
        
        # Apply outward effect for both eyes
        for eye_center in [left_eye_center, right_eye_center]:
            dx = map_x - eye_center[0]
            dy = map_y - eye_center[1]
            dist = np.sqrt(dx**2 + dy**2)
            
            eye_radius = 30 * intensity
            mask = (dist < eye_radius).astype(float)
            
            deform = 1 + (intensity * 0.3 * mask * (1 - dist / eye_radius))
            map_x = (map_x - eye_center[0]) * deform + eye_center[0]
            map_y = (map_y - eye_center[1]) * deform + eye_center[1]
        
        map_x = np.clip(map_x, 0, w - 1).astype(np.float32)
        map_y = np.clip(map_y, 0, h - 1).astype(np.float32)
        
        result = cv2.remap(result, map_x, map_y, cv2.INTER_LINEAR)
        return result


class ArtisticFilters:
    """Artistic and style transfer filters"""
    
    @staticmethod
    def cartoon_filter(frame: np.ndarray, intensity: float = 0.8) -> np.ndarray:
        """Convert to cartoon style"""
        result = frame.copy()
        
        # Bilateral filtering for smoothing
        for _ in range(int(intensity * 2)):
            result = cv2.bilateralFilter(result, 9, 75, 75)
        
        # Edge detection
        edges = cv2.Canny(result, 80, 150)
        edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        
        # Quantize colors
        data = result.reshape((-1, 3))
        data = np.float32(data)
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        _, labels, centers = cv2.kmeans(data, int(16 * intensity), None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        centers = np.uint8(centers)
        result = centers[labels.flatten()]
        result = result.reshape(frame.shape)
        
        # Combine with edges
        gray_edges = cv2.cvtColor(edges, cv2.COLOR_BGR2GRAY)
        result[gray_edges > 50] = 0
        
        return result
    
    @staticmethod
    def oil_painting(frame: np.ndarray, intensity: float = 0.7) -> np.ndarray:
        """Oil painting effect"""
        result = cv2.xphoto.oilPainting(frame, 8, int(50 * intensity), cv2.XPHOTO_THINNED)
        return cv2.addWeighted(result, intensity, frame, 1 - intensity, 0)
    
    @staticmethod
    def sketch_filter(frame: np.ndarray, intensity: float = 0.8) -> np.ndarray:
        """Pencil sketch effect"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Invert
        inv_gray = 255 - gray
        
        # Gaussian blur
        blur = cv2.GaussianBlur(inv_gray, (21, 21), 0)
        
        # Blend
        sketch = cv2.divide(gray, 255 - blur, scale=256)
        
        # Convert back to BGR
        result = cv2.cvtColor(sketch, cv2.COLOR_GRAY2BGR)
        
        return cv2.addWeighted(result, intensity, frame, 1 - intensity, 0)


class FilterProcessor:
    """Main filter processing engine"""
    
    def __init__(self):
        self.face_detector = FaceDetector()
        self.beauty_filters = BeautyFilters()
        self.face_shape_filters = FaceShapeFilters()
        self.artistic_filters = ArtisticFilters()
        self.filters_cache = {}
        self.frame_buffer = deque(maxlen=30)
        self.processing_lock = threading.Lock()
    
    def process_frame(
        self,
        frame: np.ndarray,
        filters: List[FilterMetadata]
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Process frame with multiple filters"""
        
        with self.processing_lock:
            result = frame.copy()
            face_features = self.face_detector.detect_face(result)
            
            metadata = {
                "processed": True,
                "filters_applied": [],
                "face_detected": face_features is not None,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            if not face_features:
                return result, metadata
            
            # Sort filters by priority
            sorted_filters = sorted(filters, key=lambda f: f.priority.value)
            
            for filter_meta in sorted_filters:
                if not filter_meta.enabled:
                    continue
                
                try:
                    result = self._apply_filter(result, filter_meta, face_features)
                    metadata["filters_applied"].append(filter_meta.filter_id)
                except Exception as e:
                    logger.error(f"Error applying filter {filter_meta.filter_id}: {e}")
            
            return result, metadata
    
    def _apply_filter(
        self,
        frame: np.ndarray,
        filter_meta: FilterMetadata,
        face_features: FaceFeatures
    ) -> np.ndarray:
        """Apply single filter to frame"""
        
        intensity = filter_meta.intensity
        
        if filter_meta.filter_type == FilterType.BEAUTY:
            if filter_meta.filter_id == "skin_smoothing":
                return self.beauty_filters.skin_smoothing(frame, intensity)
            elif filter_meta.filter_id == "skin_brightening":
                return self.beauty_filters.skin_brightening(frame, intensity)
            elif filter_meta.filter_id == "blusher":
                color = filter_meta.parameters.get("color", (200, 100, 100))
                return self.beauty_filters.blusher(frame, face_features, color, intensity)
            elif filter_meta.filter_id == "lipstick":
                color = filter_meta.parameters.get("color", (100, 50, 150))
                return self.beauty_filters.lipstick(frame, face_features, color, intensity)
            elif filter_meta.filter_id == "eye_makeup":
                return self.beauty_filters.eye_makeup(frame, face_features, intensity)
        
        elif filter_meta.filter_type == FilterType.FACE_SHAPE:
            if filter_meta.filter_id == "face_slimming":
                return self.face_shape_filters.face_slimming(frame, face_features, intensity)
            elif filter_meta.filter_id == "jawline_enhancement":
                return self.face_shape_filters.jawline_enhancement(frame, face_features, intensity)
            elif filter_meta.filter_id == "big_eyes":
                return self.face_shape_filters.big_eyes(frame, face_features, intensity)
        
        elif filter_meta.filter_type == FilterType.ARTISTIC:
            if filter_meta.filter_id == "cartoon":
                return self.artistic_filters.cartoon_filter(frame, intensity)
            elif filter_meta.filter_id == "oil_painting":
                return self.artistic_filters.oil_painting(frame, intensity)
            elif filter_meta.filter_id == "sketch":
                return self.artistic_filters.sketch_filter(frame, intensity)
        
        return frame
    
    def encode_frame_to_base64(self, frame: np.ndarray) -> str:
        """Convert numpy array frame to base64 string"""
        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 90])
        return base64.b64encode(buffer).decode('utf-8')
    
    def decode_frame_from_base64(self, frame_data: str) -> np.ndarray:
        """Convert base64 string to numpy array frame"""
        buffer = base64.b64decode(frame_data)
        nparr = np.frombuffer(buffer, np.uint8)
        return cv2.imdecode(nparr, cv2.IMREAD_COLOR)


# Predefined filters library
DEFAULT_FILTERS = {
    "skin_smoothing": FilterMetadata(
        filter_id="skin_smoothing",
        name="Skin Smoothing",
        filter_type=FilterType.BEAUTY,
        intensity=0.7,
        parameters={}
    ),
    "skin_brightening": FilterMetadata(
        filter_id="skin_brightening",
        name="Skin Brightening",
        filter_type=FilterType.BEAUTY,
        intensity=0.6,
        parameters={}
    ),
    "face_slimming": FilterMetadata(
        filter_id="face_slimming",
        name="Face Slimming",
        filter_type=FilterType.FACE_SHAPE,
        intensity=0.5,
        parameters={}
    ),
    "big_eyes": FilterMetadata(
        filter_id="big_eyes",
        name="Big Eyes",
        filter_type=FilterType.FACE_SHAPE,
        intensity=0.6,
        parameters={}
    ),
    "cartoon": FilterMetadata(
        filter_id="cartoon",
        name="Cartoon",
        filter_type=FilterType.ARTISTIC,
        intensity=0.8,
        parameters={}
    ),
    "lipstick_red": FilterMetadata(
        filter_id="lipstick_red",
        name="Red Lipstick",
        filter_type=FilterType.MAKEUP,
        intensity=0.8,
        parameters={"color": (50, 50, 200)}
    ),
    "lipstick_pink": FilterMetadata(
        filter_id="lipstick_pink",
        name="Pink Lipstick",
        filter_type=FilterType.MAKEUP,
        intensity=0.8,
        parameters={"color": (150, 100, 180)}
    ),
    "blush_natural": FilterMetadata(
        filter_id="blush_natural",
        name="Natural Blush",
        filter_type=FilterType.MAKEUP,
        intensity=0.6,
        parameters={"color": (180, 120, 150)}
    ),
    "jawline_enhance": FilterMetadata(
        filter_id="jawline_enhance",
        name="Jawline Enhancement",
        filter_type=FilterType.FACE_SHAPE,
        intensity=0.7,
        parameters={}
    ),
    "eye_makeup": FilterMetadata(
        filter_id="eye_makeup",
        name="Eye Makeup",
        filter_type=FilterType.MAKEUP,
        intensity=0.7,
        parameters={}
    ),
    "oil_painting": FilterMetadata(
        filter_id="oil_painting",
        name="Oil Painting",
        filter_type=FilterType.ARTISTIC,
        intensity=0.7,
        parameters={}
    ),
    "sketch": FilterMetadata(
        filter_id="sketch",
        name="Pencil Sketch",
        filter_type=FilterType.ARTISTIC,
        intensity=0.8,
        parameters={}
    ),
}


logger.info("✅ Lens Studio Core Engine Initialized - Production Ready")
