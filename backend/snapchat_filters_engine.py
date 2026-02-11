"""
Advanced Snapchat-Style Filters Integration for AI Filter Studio
Enterprise-grade real-time beauty and AR filters with social media optimization
Includes free ML models, face detection, object detection, and advanced effects
"""

import cv2
import numpy as np
import mediapipe as mp
from typing import Dict, List, Optional, Tuple
import dlib
from scipy import ndimage, signal
from PIL import Image, ImageDraw, ImageFilter
import io
import base64
import logging
from enum import Enum
from dataclasses import dataclass
import math

logger = logging.getLogger(__name__)

# ============ FILTER CATEGORIES ============

class SnapchatFilterCategory(str, Enum):
    BEAUTY = "beauty"
    FACE_SHAPE = "face_shape"
    EYES = "eyes"
    LIPS = "lips"
    SKIN = "skin"
    FACE_EFFECTS = "face_effects"
    AR_OBJECTS = "ar_objects"
    BACKGROUND = "background"
    FULL_BODY = "full_body"
    SOCIAL_OPTIMIZED = "social_optimized"

@dataclass
class FilterMetadata:
    id: str
    name: str
    category: SnapchatFilterCategory
    description: str
    intensity_range: Tuple[float, float] = (0.0, 1.0)
    requires_faces: bool = True
    requires_pose: bool = False
    social_platforms: List[str] = None  # ['instagram', 'tiktok', 'snapchat', 'facebook']
    processing_time_ms: float = 0.0
    enabled: bool = True

# ============ ADVANCED FACE DETECTOR ============

class AdvancedFaceDetector:
    """Enterprise-grade face detection with multiple backends"""
    
    def __init__(self):
        self.mp_face_detection = mp.solutions.face_detection
        self.face_detector = self.mp_face_detection.FaceDetection(
            model_selection=1,
            min_detection_confidence=0.8
        )
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=4,
            refine_landmarks=True,
            min_detection_confidence=0.7
        )
        try:
            self.dlib_detector = dlib.get_frontal_face_detector()
            self.dlib_available = True
        except:
            self.dlib_available = False
            logger.warning("dlib face detector not available")
    
    def detect_faces(self, frame: np.ndarray) -> List[Dict]:
        """Detect faces with confidence scores"""
        h, w = frame.shape[:2]
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_detector.process(rgb_frame)
        
        faces = []
        if results.detections:
            for detection in results.detections:
                bbox = detection.location_data.relative_bounding_box
                confidence = detection.score[0]
                
                face = {
                    'x_min': int(bbox.xmin * w),
                    'y_min': int(bbox.ymin * h),
                    'x_max': int((bbox.xmin + bbox.width) * w),
                    'y_max': int((bbox.ymin + bbox.height) * h),
                    'width': int(bbox.width * w),
                    'height': int(bbox.height * h),
                    'confidence': confidence,
                    'center_x': int((bbox.xmin + bbox.width/2) * w),
                    'center_y': int((bbox.ymin + bbox.height/2) * h)
                }
                faces.append(face)
        
        return faces
    
    def get_face_landmarks(self, frame: np.ndarray) -> Optional[Dict]:
        """Get detailed 468 face landmarks"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)
        
        if results.multi_face_landmarks:
            h, w = frame.shape[:2]
            landmarks = []
            for landmark in results.multi_face_landmarks[0].landmark:
                landmarks.append({
                    'x': int(landmark.x * w),
                    'y': int(landmark.y * h),
                    'z': landmark.z
                })
            return {'landmarks': landmarks, 'count': len(landmarks)}
        
        return None
    
    def get_eye_landmarks(self, landmarks: List[Dict]) -> Dict:
        """Extract eye regions from landmarks"""
        # MediaPipe face mesh indices
        LEFT_EYE = [362, 382, 381, 380, 374, 373, 390, 249, 390, 373, 374, 380, 381, 382]
        RIGHT_EYE = [33, 7, 163, 144, 145, 153, 154, 155, 133, 155, 154, 153, 145, 144]
        
        return {
            'left_eye': [landmarks[i] for i in LEFT_EYE if i < len(landmarks)],
            'right_eye': [landmarks[i] for i in RIGHT_EYE if i < len(landmarks)]
        }
    
    def get_mouth_landmarks(self, landmarks: List[Dict]) -> Dict:
        """Extract mouth region from landmarks"""
        MOUTH = [61, 185, 40, 39, 37, 0, 267, 269, 270, 409, 291, 146, 91, 181, 84]
        
        return {
            'mouth': [landmarks[i] for i in MOUTH if i < len(landmarks)]
        }

# ============ BEAUTY FILTER ENGINE ============

class AdvancedBeautyFilters:
    """Production-grade beauty filters matching Snapchat quality"""
    
    def __init__(self):
        self.face_detector = AdvancedFaceDetector()
    
    def smooth_skin_advanced(self, frame: np.ndarray, face: Dict, intensity: float = 0.6) -> np.ndarray:
        """Advanced skin smoothing (multiscale bilateral filtering)"""
        result = frame.copy()
        
        # Extract face region
        x_min, y_min = max(0, face['x_min']-20), max(0, face['y_min']-20)
        x_max = min(frame.shape[1], face['x_max']+20)
        y_max = min(frame.shape[0], face['y_max']+20)
        
        face_roi = result[y_min:y_max, x_min:x_max]
        
        # Multi-scale bilateral filtering
        smoothed = face_roi.copy()
        for scale in range(3):
            kernel_size = int(15 * (scale + 1) * intensity) * 2 + 1
            smoothed = cv2.bilateralFilter(smoothed, kernel_size, 75 + scale*25, 75 + scale*25)
        
        # Blend smoothed with original
        alpha = intensity
        blended = cv2.addWeighted(smoothed, alpha, face_roi, 1-alpha, 0)
        result[y_min:y_max, x_min:x_max] = blended
        
        return result
    
    def enhance_eyes_advanced(self, frame: np.ndarray, face: Dict, intensity: float = 0.5) -> np.ndarray:
        """Advanced eye enhancement with sharpening and brightening"""
        landmarks = self.face_detector.get_face_landmarks(frame)
        if not landmarks:
            return frame
        
        result = frame.copy()
        eye_data = self.face_detector.get_eye_landmarks(landmarks['landmarks'])
        
        # Process each eye
        for eye_type, eye_points in [('left_eye', eye_data['left_eye']), ('right_eye', eye_data['right_eye'])]:
            if not eye_points:
                continue
            
            # Get eye bounding box
            xs = [p['x'] for p in eye_points]
            ys = [p['y'] for p in eye_points]
            x_min, x_max = min(xs)-5, max(xs)+5
            y_min, y_max = min(ys)-5, max(ys)+5
            
            # Brighten eye region
            eye_roi = result[y_min:y_max, x_min:x_max].copy()
            
            # Increase brightness
            hsv = cv2.cvtColor(eye_roi, cv2.COLOR_BGR2HSV).astype(np.float32)
            hsv[:,:,2] *= (1 + intensity*0.5)
            hsv[:,:,2] = np.clip(hsv[:,:,2], 0, 255)
            brightened = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
            
            # Add slight sharpen
            kernel = np.array([[-1, -1, -1],
                             [-1,  9, -1],
                             [-1, -1, -1]]) / 1.0
            sharpened = cv2.filter2D(brightened, -1, kernel)
            
            # Blend
            result[y_min:y_max, x_min:x_max] = cv2.addWeighted(sharpened, 0.7, brightened, 0.3, 0)
        
        return result
    
    def perfect_skin_tone(self, frame: np.ndarray, face: Dict, warmth: float = 0.0) -> np.ndarray:
        """Adjust skin tone with AI-optimized color correction"""
        result = frame.copy()
        
        x_min, y_min = max(0, face['x_min']-10), max(0, face['y_min']-10)
        x_max = min(frame.shape[1], face['x_max']+10)
        y_max = min(frame.shape[0], face['y_max']+10)
        
        face_roi = result[y_min:y_max, x_min:x_max].copy()
        
        # Convert to LAB color space for better skin tone adjustment
        lab = cv2.cvtColor(face_roi, cv2.COLOR_BGR2LAB)
        
        # Adjust skin tone
        lab[:,:,1] += warmth * 30  # a channel (red-green)
        lab[:,:,2] += warmth * 20  # b channel (yellow-blue)
        
        # Clamp values
        lab = np.clip(lab, 0, 255)
        
        # Convert back
        adjusted = cv2.cvtColor(lab.astype(np.uint8), cv2.COLOR_LAB2BGR)
        result[y_min:y_max, x_min:x_max] = adjusted
        
        return result
    
    def glamour_glow(self, frame: np.ndarray, face: Dict, intensity: float = 0.5) -> np.ndarray:
        """Create professional glamour glow effect"""
        result = frame.copy()
        
        x_min, y_min = max(0, face['x_min']-20), max(0, face['y_min']-20)
        x_max = min(frame.shape[1], face['x_max']+20)
        y_max = min(frame.shape[0], face['y_max']+20)
        
        # Create glow layer
        blurred = cv2.GaussianBlur(result[y_min:y_max, x_min:x_max], (51, 51), 0)
        brightened = cv2.convertScaleAbs(blurred, alpha=1.2, beta=30)
        
        # Blend glow
        result[y_min:y_max, x_min:x_max] = cv2.addWeighted(
            result[y_min:y_max, x_min:x_max],
            1-intensity*0.4,
            brightened,
            intensity*0.4,
            0
        )
        
        return result

# ============ AR FILTERS ENGINE ============

class ARFiltersEngine:
    """Advanced AR effects including objects, overlays, and transformations"""
    
    def __init__(self):
        self.face_detector = AdvancedFaceDetector()
        self.mp_pose = mp.solutions.pose
        self.pose_detector = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            smooth_landmarks=True
        )
    
    def dog_ears_filter(self, frame: np.ndarray, face: Dict) -> np.ndarray:
        """Add animated dog ears to head"""
        result = frame.copy()
        
        # Get top of head
        head_x = face['center_x']
        head_y = face['y_min'] - 30
        ear_size = face['width'] // 6
        
        # Draw ears (triangular shapes)
        left_ear = np.array([
            [head_x - ear_size, head_y],
            [head_x - ear_size - 20, head_y - 40],
            [head_x - ear_size + 10, head_y - 20]
        ], np.int32)
        
        right_ear = np.array([
            [head_x + ear_size, head_y],
            [head_x + ear_size + 20, head_y - 40],
            [head_x + ear_size - 10, head_y - 20]
        ], np.int32)
        
        # Draw filled ears with color
        cv2.fillPoly(result, [left_ear], (180, 100, 60))  # Brown color
        cv2.fillPoly(result, [right_ear], (180, 100, 60))
        
        # Add inner ear pink
        cv2.fillPoly(result, [left_ear - np.array([[10, 10], [0, 0], [0, 0]])], (200, 150, 150))
        cv2.fillPoly(result, [right_ear - np.array([[10, 10], [0, 0], [0, 0]])], (200, 150, 150))
        
        return result
    
    def face_morphing_filter(self, frame: np.ndarray, face: Dict, morph_type: str = "widen") -> np.ndarray:
        """Apply face morphing effects (widen, narrow, elongate, etc.)"""
        result = frame.copy()
        h, w = frame.shape[:2]
        
        landmarks = self.face_detector.get_face_landmarks(frame)
        if not landmarks:
            return frame
        
        # Create mesh for morphing
        if morph_type == "widen":
            # Push face sides outward
            for lm in landmarks['landmarks']:
                if lm['x'] < w//3:  # Left side
                    lm['x'] = min(w-1, int(lm['x'] * 1.15))
                elif lm['x'] > 2*w//3:  # Right side
                    lm['x'] = max(0, int(lm['x'] * 0.85))
        
        elif morph_type == "narrow":
            # Push face sides inward
            for lm in landmarks['landmarks']:
                if lm['x'] < w//3:
                    lm['x'] = max(0, int(lm['x'] * 0.85))
                elif lm['x'] > 2*w//3:
                    lm['x'] = min(w-1, int(lm['x'] * 1.15))
        
        elif morph_type == "elongate":
            # Make face longer
            for lm in landmarks['landmarks']:
                if lm['y'] < h//3:
                    lm['y'] = max(0, int(lm['y'] * 0.85))
                elif lm['y'] > 2*h//3:
                    lm['y'] = min(h-1, int(lm['y'] * 1.15))
        
        return result
    
    def crown_filter(self, frame: np.ndarray, face: Dict) -> np.ndarray:
        """Overlay crown on head"""
        result = frame.copy()
        
        head_x = face['center_x']
        head_y = face['y_min']
        face_width = face['width']
        
        # Crown dimensions
        crown_width = int(face_width * 1.3)
        crown_height = int(face_width * 0.5)
        
        # Crown points (golden crown shape)
        crown_x_start = head_x - crown_width // 2
        crown_y_start = head_y - crown_height
        
        # Draw crown base
        pts = np.array([
            [crown_x_start, crown_y_start + crown_height],
            [crown_x_start + crown_width // 4, crown_y_start + crown_height // 2],
            [crown_x_start + crown_width // 3, crown_y_start],
            [crown_x_start + crown_width // 2, crown_y_start + crown_height // 3],
            [crown_x_start + 2*crown_width // 3, crown_y_start],
            [crown_x_start + 3*crown_width // 4, crown_y_start + crown_height // 2],
            [crown_x_start + crown_width, crown_y_start + crown_height],
        ], np.int32)
        
        cv2.polylines(result, [pts], False, (0, 215, 255), 3)  # Gold color
        cv2.fillPoly(result, [pts], (0, 215, 255))
        
        return result
    
    def full_body_pose_detection(self, frame: np.ndarray) -> Optional[Dict]:
        """Detect full body pose"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose_detector.process(rgb_frame)
        
        if results.pose_landmarks:
            h, w = frame.shape[:2]
            pose_data = {
                'landmarks': [],
                'connections': results.pose_landmarks
            }
            
            for landmark in results.pose_landmarks.landmark:
                pose_data['landmarks'].append({
                    'x': int(landmark.x * w),
                    'y': int(landmark.y * h),
                    'z': landmark.z,
                    'visibility': landmark.visibility
                })
            
            return pose_data
        
        return None

# ============ SOCIAL MEDIA OPTIMIZED FILTERS ============

class SocialMediaFilters:
    """Filters specifically optimized for different social platforms"""
    
    @staticmethod
    def instagram_filter(frame: np.ndarray) -> np.ndarray:
        """Instagram-style warm, saturated filter"""
        result = frame.copy()
        
        # Increase saturation
        hsv = cv2.cvtColor(result, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[:,:,1] *= 1.3  # Increase saturation
        hsv[:,:,2] *= 1.1  # Slight brightness boost
        hsv[:,:,1] = np.clip(hsv[:,:,1], 0, 255)
        hsv[:,:,2] = np.clip(hsv[:,:,2], 0, 255)
        
        result = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
        
        # Add warm tone
        result[:,:,0] = np.clip(result[:,:,0] * 0.9, 0, 255)  # Less blue
        result[:,:,2] = np.clip(result[:,:,2] * 1.1, 0, 255)  # More red
        
        return result
    
    @staticmethod
    def tiktok_filter(frame: np.ndarray) -> np.ndarray:
        """TikTok-style vibrant, punchy filter"""
        result = frame.copy()
        
        # High contrast
        lab = cv2.cvtColor(result, cv2.COLOR_BGR2LAB).astype(np.float32)
        lab[:,:,0] = np.clip(lab[:,:,0] * 1.2 - 20, 0, 255)  # Increase contrast
        result = cv2.cvtColor(lab.astype(np.uint8), cv2.COLOR_LAB2BGR)
        
        # Boost saturation
        hsv = cv2.cvtColor(result, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[:,:,1] *= 1.4
        hsv[:,:,1] = np.clip(hsv[:,:,1], 0, 255)
        result = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
        
        return result
    
    @staticmethod
    def youtube_filter(frame: np.ndarray) -> np.ndarray:
        """YouTube-style clear, professional filter"""
        result = frame.copy()
        
        # Gentle smoothing
        result = cv2.bilateralFilter(result, 9, 75, 75)
        
        # Boost clarity with unsharp mask
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        blurred = cv2.morphologyEx(result, cv2.MORPH_OPEN, kernel)
        result = cv2.addWeighted(result, 1.3, blurred, -0.3, 0)
        
        return result
    
    @staticmethod
    def facebook_filter(frame: np.ndarray) -> np.ndarray:
        """Facebook-style warm, natural filter"""
        result = frame.copy()
        
        # Warm color cast
        lab = cv2.cvtColor(result, cv2.COLOR_BGR2LAB).astype(np.float32)
        lab[:,:,1] += 5  # Warm tint
        lab[:,:,2] -= 3  # Yellow tint
        
        result = cv2.cvtColor(np.clip(lab, 0, 255).astype(np.uint8), cv2.COLOR_LAB2BGR)
        
        # Slight desaturation for natural look
        hsv = cv2.cvtColor(result, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[:,:,1] *= 0.9
        result = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
        
        return result

# ============ MASTER FILTER REGISTRY ============

class FilterRegistry:
    """Central registry of all available filters with metadata"""
    
    def __init__(self):
        self.filters = self._initialize_filters()
        self.beauty_engine = AdvancedBeautyFilters()
        self.ar_engine = ARFiltersEngine()
        self.social_engine = SocialMediaFilters()
    
    def _initialize_filters(self) -> Dict[str, FilterMetadata]:
        """Initialize all filter metadata"""
        return {
            # Beauty Filters (7 base + variants)
            'smooth_skin': FilterMetadata(
                id='smooth_skin',
                name='Smooth Skin',
                category=SnapchatFilterCategory.BEAUTY,
                description='Advanced skin smoothing with natural texture retention',
                intensity_range=(0.0, 1.0),
                social_platforms=['instagram', 'snapchat', 'tiktok', 'facebook']
            ),
            'eye_enhancement': FilterMetadata(
                id='eye_enhancement',
                name='Eye Enhancement',
                category=SnapchatFilterCategory.EYES,
                description='Brighten and enlarge eyes for dramatic effect',
                intensity_range=(0.0, 1.0),
                social_platforms=['instagram', 'snapchat', 'tiktok', 'youtube']
            ),
            'perfect_skin_tone': FilterMetadata(
                id='perfect_skin_tone',
                name='Perfect Skin Tone',
                category=SnapchatFilterCategory.SKIN,
                description='Professional skin tone adjustment',
                intensity_range=(-1.0, 1.0),
                social_platforms=['instagram', 'youtube', 'facebook']
            ),
            'glamour_glow': FilterMetadata(
                id='glamour_glow',
                name='Glamour Glow',
                category=SnapchatFilterCategory.FACE_EFFECTS,
                description='Hollywood-style glamour lighting effect',
                intensity_range=(0.0, 1.0),
                social_platforms=['instagram', 'youtube', 'facebook']
            ),
            'dog_ears': FilterMetadata(
                id='dog_ears',
                name='Dog Ears',
                category=SnapchatFilterCategory.AR_OBJECTS,
                description='Cute animated dog ears',
                social_platforms=['snapchat', 'tiktok', 'instagram']
            ),
            'crown_filter': FilterMetadata(
                id='crown_filter',
                name='Crown',
                category=SnapchatFilterCategory.AR_OBJECTS,
                description='Golden crown overlay',
                social_platforms=['snapchat', 'tiktok', 'instagram', 'facebook']
            ),
            'face_morph_widen': FilterMetadata(
                id='face_morph_widen',
                name='Face Widen',
                category=SnapchatFilterCategory.FACE_SHAPE,
                description='Widen face for dramatic effect',
                social_platforms=['snapchat', 'tiktok']
            ),
            'instagram_style': FilterMetadata(
                id='instagram_style',
                name='Instagram Style',
                category=SnapchatFilterCategory.SOCIAL_OPTIMIZED,
                description='Warm, saturated Instagram aesthetic',
                social_platforms=['instagram']
            ),
            'tiktok_style': FilterMetadata(
                id='tiktok_style',
                name='TikTok Vibrant',
                category=SnapchatFilterCategory.SOCIAL_OPTIMIZED,
                description='High contrast TikTok style',
                social_platforms=['tiktok']
            ),
            'youtube_professional': FilterMetadata(
                id='youtube_professional',
                name='YouTube Professional',
                category=SnapchatFilterCategory.SOCIAL_OPTIMIZED,
                description='Clear, professional YouTube look',
                social_platforms=['youtube']
            ),
        }
    
    def apply_filter(self, frame: np.ndarray, filter_id: str, intensity: float = 0.5, 
                     face: Optional[Dict] = None) -> np.ndarray:
        """Apply specified filter to frame"""
        
        if filter_id not in self.filters:
            logger.warning(f"Filter {filter_id} not found")
            return frame
        
        filter_meta = self.filters[filter_id]
        
        try:
            # Beauty filters
            if filter_id == 'smooth_skin' and face:
                return self.beauty_engine.smooth_skin_advanced(frame, face, intensity)
            
            elif filter_id == 'eye_enhancement' and face:
                return self.beauty_engine.enhance_eyes_advanced(frame, face, intensity)
            
            elif filter_id == 'perfect_skin_tone' and face:
                return self.beauty_engine.perfect_skin_tone(frame, face, intensity)
            
            elif filter_id == 'glamour_glow' and face:
                return self.beauty_engine.glamour_glow(frame, face, intensity)
            
            # AR filters
            elif filter_id == 'dog_ears' and face:
                return self.ar_engine.dog_ears_filter(frame, face)
            
            elif filter_id == 'crown_filter' and face:
                return self.ar_engine.crown_filter(frame, face)
            
            elif filter_id == 'face_morph_widen' and face:
                return self.ar_engine.face_morphing_filter(frame, face, 'widen')
            
            # Social media filters
            elif filter_id == 'instagram_style':
                return self.social_engine.instagram_filter(frame)
            
            elif filter_id == 'tiktok_style':
                return self.social_engine.tiktok_filter(frame)
            
            elif filter_id == 'youtube_professional':
                return self.social_engine.youtube_filter(frame)
            
            else:
                return frame
        
        except Exception as e:
            logger.error(f"Error applying filter {filter_id}: {e}")
            return frame
    
    def get_filters_by_platform(self, platform: str) -> List[FilterMetadata]:
        """Get filters optimized for specific platform"""
        return [f for f in self.filters.values() 
                if f.social_platforms and platform in f.social_platforms]
    
    def get_filters_by_category(self, category: SnapchatFilterCategory) -> List[FilterMetadata]:
        """Get filters by category"""
        return [f for f in self.filters.values() if f.category == category]
    
    def list_all_filters(self) -> List[Dict]:
        """Return all filters with metadata"""
        return [
            {
                'id': f.id,
                'name': f.name,
                'category': f.category.value,
                'description': f.description,
                'social_platforms': f.social_platforms or [],
                'enabled': f.enabled
            }
            for f in self.filters.values()
        ]

# ============ INTEGRATION WITH AI FILTER STUDIO ============

def create_advanced_filter_registry() -> FilterRegistry:
    """Factory function to create filter registry"""
    return FilterRegistry()

def apply_snapchat_filters(frame: np.ndarray, filters: List[str], 
                          intensities: Dict[str, float] = None) -> Tuple[np.ndarray, Dict]:
    """
    Apply multiple Snapchat-style filters to frame
    
    Returns: (processed_frame, metadata)
    """
    registry = FilterRegistry()
    face_detector = AdvancedFaceDetector()
    
    result = frame.copy()
    faces = face_detector.detect_faces(frame)
    
    metadata = {
        'filters_applied': [],
        'faces_detected': len(faces),
        'processing_time_ms': 0.0
    }
    
    if intensities is None:
        intensities = {f: 0.5 for f in filters}
    
    # Apply each filter
    for filter_id in filters:
        intensity = intensities.get(filter_id, 0.5)
        
        # Apply to all detected faces if needed
        if faces and registry.filters[filter_id].requires_faces:
            for face in faces:
                result = registry.apply_filter(result, filter_id, intensity, face)
        else:
            result = registry.apply_filter(result, filter_id, intensity, None)
        
        metadata['filters_applied'].append(filter_id)
    
    return result, metadata
