"""
AI Filter Studio - Advanced AR Filters with Groq ML Integration
Production-grade real-time filter engine with face detection, object tracking, and AI enhancements
Integrated with Snapchat-style filters for social media optimization
"""

import os
import cv2
import numpy as np
from fastapi import APIRouter, HTTPException, Body, UploadFile, File, WebSocket
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import motor.motor_asyncio
from datetime import datetime
import asyncio
import base64
from io import BytesIO
from PIL import Image, ImageFilter, ImageOps
import mediapipe as mp
from groq import Groq
import json
import hashlib
from enum import Enum
import dlib
import logging
from .snapchat_filters_engine import (
    FilterRegistry, AdvancedFaceDetector, AdvancedBeautyFilters,
    ARFiltersEngine, SocialMediaFilters, SnapchatFilterCategory
)
from .social_filters import SocialFilterRegistry, PlatformType
from .advanced_filters_library import AdvancedFilterRegistry, FilterCategory

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/ai-filter-studio", tags=["AI Filter Studio"])

# Initialize Groq client
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY", ""))

# MediaPipe initialization
mp_face_detection = mp.solutions.face_detection
mp_hands = mp.solutions.hands
mp_pose = mp.solutions.pose
mp_selfie_segmentation = mp.solutions.selfie_segmentation

# ============ ENUMS ============

class FilterType(str, Enum):
    BEAUTY = "beauty"
    FACE_SHAPE = "face_shape"
    EYES = "eyes"
    LIPS = "lips"
    SKIN_TONE = "skin_tone"
    BACKGROUND = "background"
    OBJECT_DETECTION = "object_detection"
    POSE = "pose"
    HAND = "hand"
    ARTISTIC = "artistic"
    VINTAGE = "vintage"
    CARTOON = "cartoon"
    AI_ENHANCED = "ai_enhanced"

class AIModel(str, Enum):
    GROQ_LLAMA = "groq_llama"
    FACE_DETECTION = "face_detection"
    OBJECT_DETECTION = "object_detection"
    SEGMENTATION = "segmentation"
    STYLE_TRANSFER = "style_transfer"

# ============ MODELS ============

class BeautyFilterConfig(BaseModel):
    smoothing_strength: float = Field(0.5, ge=0, le=1)
    brightness_adjustment: float = Field(0, ge=-1, le=1)
    contrast_adjustment: float = Field(0, ge=-1, le=1)
    saturation_boost: float = Field(0, ge=-1, le=1)
    eye_enlargement: float = Field(0, ge=0, le=0.3)
    eye_brightness: float = Field(0, ge=-1, le=1)
    lips_tint: Optional[str] = None
    lips_intensity: float = Field(0.5, ge=0, le=1)

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ai_filter_studio",
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/snapchat-filters/available")
async def get_snapchat_filters():
    """Get all Snapchat-style filters"""
    registry = FilterRegistry()
    return {
        "filters": registry.list_all_filters(),
        "categories": [c.value for c in SnapchatFilterCategory],
        "total_count": len(registry.filters)
    }

@router.get("/snapchat-filters/by-category/{category}")
async def get_filters_by_category(category: str):
    """Get filters by category"""
    try:
        cat = SnapchatFilterCategory(category)
        registry = FilterRegistry()
        filters = registry.get_filters_by_category(cat)
        return {
            "category": category,
            "filters": [
                {
                    'id': f.id,
                    'name': f.name,
                    'description': f.description
                }
                for f in filters
            ]
        }
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid category: {category}")

@router.get("/snapchat-filters/by-platform/{platform}")
async def get_filters_by_platform(platform: str):
    """Get filters optimized for social platform"""
    valid_platforms = ['instagram', 'tiktok', 'snapchat', 'youtube', 'facebook']
    if platform not in valid_platforms:
        raise HTTPException(status_code=400, detail=f"Invalid platform: {platform}")
    
    registry = FilterRegistry()
    filters = registry.get_filters_by_platform(platform)
    return {
        "platform": platform,
        "filters": [
            {
                'id': f.id,
                'name': f.name,
                'description': f.description
            }
            for f in filters
        ]
    }

@router.post("/snapchat-filters/apply")
async def apply_snapchat_filters(
    session_id: str = Body(...),
    frame_base64: str = Body(...),
    filter_ids: List[str] = Body(...),
    intensities: Dict[str, float] = Body(default_factory=dict)
):
    """Apply Snapchat filters to frame"""
    try:
        # Decode frame
        frame_bytes = base64.b64decode(frame_base64)
        frame_array = np.frombuffer(frame_bytes, dtype=np.uint8)
        frame = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)
        
        if frame is None:
            raise HTTPException(status_code=400, detail="Invalid frame")
        
        # Apply filters
        import time
        start_time = time.time()
        
        registry = FilterRegistry()
        face_detector = AdvancedFaceDetector()
        result = frame.copy()
        faces = face_detector.detect_faces(frame)
        
        applied_filters = []
        for filter_id in filter_ids:
            if filter_id in registry.filters:
                intensity = intensities.get(filter_id, 0.5)
                
                # Apply to faces if required
                if faces and registry.filters[filter_id].requires_faces:
                    for face in faces:
                        result = registry.apply_filter(result, filter_id, intensity, face)
                else:
                    result = registry.apply_filter(result, filter_id, intensity, None)
                
                applied_filters.append(filter_id)
        
        processing_time = (time.time() - start_time) * 1000
        
        # Encode result
        _, buffer = cv2.imencode('.jpg', result, [cv2.IMWRITE_JPEG_QUALITY, 90])
        result_base64 = base64.b64encode(buffer).decode()
        
        return {
            "session_id": session_id,
            "frame_base64": result_base64,
            "detected_faces": len(faces),
            "applied_filters": applied_filters,
            "processing_time_ms": round(processing_time, 2)
        }
    
    except Exception as e:
        logger.error(f"Filter application error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/snapchat-filters/smart-enhance")
async def smart_enhance_with_groq(
    frame_base64: str = Body(...),
    current_filters: List[str] = Body(default_factory=list),
    user_preference: str = Body(default="professional")
):
    """Use Groq AI to recommend optimal filters for frame"""
    try:
        message = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": f"""You are a professional makeup and photography AI.
A user wants to apply Snapchat-style filters to enhance their appearance.
User preference: {user_preference}
Currently applied filters: {', '.join(current_filters) if current_filters else 'none'}

Recommend the top 3-5 filters from this list for the best result:
- smooth_skin
- eye_enhancement
- perfect_skin_tone
- glamour_glow
- dog_ears
- crown_filter
- instagram_style
- tiktok_style
- youtube_professional

Format your response as a JSON array of filter IDs with intensities (0-1).
Example: {{"filters": ["smooth_skin", "eye_enhancement"], "intensities": {{"smooth_skin": 0.7, "eye_enhancement": 0.5}}}}"""
                }
            ],
            model="mixtral-8x7b-32768",
            temperature=0.7,
            max_tokens=300
        )
        
        response_text = message.choices[0].message.content
        
        # Parse JSON from response
        import re
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            recommendations = json.loads(json_match.group())
            return {
                "recommended_filters": recommendations.get("filters", []),
                "intensities": recommendations.get("intensities", {}),
                "reasoning": response_text
            }
        
        return {"error": "Could not parse recommendations"}
    
    except Exception as e:
        logger.error(f"Groq enhancement error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============ FACE DETECTION & PROCESSING ============
router = APIRouter(prefix="/api/ai-filter-studio", tags=["AI Filter Studio"])

# Initialize Groq client
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY", ""))

# MediaPipe initialization
mp_face_detection = mp.solutions.face_detection
mp_hands = mp.solutions.hands
mp_pose = mp.solutions.pose
mp_selfie_segmentation = mp.solutions.selfie_segmentation

# ============ ENUMS ============

class FilterType(str, Enum):
    BEAUTY = "beauty"
    FACE_SHAPE = "face_shape"
    EYES = "eyes"
    LIPS = "lips"
    SKIN_TONE = "skin_tone"
    BACKGROUND = "background"
    OBJECT_DETECTION = "object_detection"
    POSE = "pose"
    HAND = "hand"
    ARTISTIC = "artistic"
    VINTAGE = "vintage"
    CARTOON = "cartoon"
    AI_ENHANCED = "ai_enhanced"

class AIModel(str, Enum):
    GROQ_LLAMA = "groq_llama"
    FACE_DETECTION = "face_detection"
    OBJECT_DETECTION = "object_detection"
    SEGMENTATION = "segmentation"
    STYLE_TRANSFER = "style_transfer"

# ============ MODELS ============

class BeautyFilterConfig(BaseModel):
    smoothing_strength: float = Field(0.5, ge=0, le=1)
    brightness_adjustment: float = Field(0, ge=-1, le=1)
    contrast_adjustment: float = Field(0, ge=-1, le=1)
    saturation_boost: float = Field(0, ge=-1, le=1)
    eye_enlargement: float = Field(0, ge=0, le=0.3)
    eye_brightness: float = Field(0, ge=-1, le=1)
    lips_tint: Optional[str] = None
    lips_intensity: float = Field(0.5, ge=0, le=1)

class BackgroundFilter(BaseModel):
    filter_type: str  # blur, replace, color, pattern
    blur_strength: Optional[int] = Field(None, ge=1, le=100)
    replacement_color: Optional[str] = None
    pattern: Optional[str] = None
    opacity: float = Field(1.0, ge=0, le=1)

class AIEnhancementRequest(BaseModel):
    filter_type: FilterType
    image_base64: str
    prompt: Optional[str] = None
    model: AIModel = AIModel.GROQ_LLAMA
    config: Optional[Dict[str, Any]] = None

class FilterSession(BaseModel):
    session_id: str
    user_id: str
    active_filters: List[str] = Field(default_factory=list)
    beauty_config: Optional[BeautyFilterConfig] = None
    face_shape_config: Optional[FaceShapeFilter] = None
    background_config: Optional[BackgroundFilter] = None
    ai_enhancements: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_used: datetime = Field(default_factory=datetime.utcnow)
    processing_stats: Dict[str, Any] = Field(default_factory=dict)

class FilterResult(BaseModel):
    session_id: str
    frame_base64: str
    detected_faces: int
    processing_time_ms: float
    applied_filters: List[str]
    ai_suggestions: Optional[List[str]] = None

# ============ FACE DETECTION & PROCESSING ============

class FaceProcessor:
    def __init__(self):
        self.face_detector = mp_face_detection.FaceDetection(
            model_selection=1, min_detection_confidence=0.7
        )
        self.face_recognizer = dlib.face_recognition_model_loader(
            "mmod_human_face_detector.dat"
        ) if os.path.exists("mmod_human_face_detector.dat") else None
        
    def detect_faces(self, frame: np.ndarray) -> List[Dict]:
        """Detect faces using MediaPipe"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_detector.process(rgb_frame)
        
        faces = []
        if results.detections:
            h, w, _ = frame.shape
            for detection in results.detections:
                bbox = detection.location_data.relative_bounding_box
                x_min = int(bbox.xmin * w)
                y_min = int(bbox.ymin * h)
                x_max = int((bbox.xmin + bbox.width) * w)
                y_max = int((bbox.ymin + bbox.height) * h)
                confidence = detection.score[0]
                
                faces.append({
                    "x_min": x_min,
                    "y_min": y_min,
                    "x_max": x_max,
                    "y_max": y_max,
                    "confidence": confidence,
                    "width": x_max - x_min,
                    "height": y_max - y_min
                })
        
        return faces

    def get_face_landmarks(self, frame: np.ndarray, face_bbox: Dict) -> Optional[Dict]:
        """Get detailed face landmarks"""
        from mediapipe.python.solutions import face_mesh
        mesh = face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1, min_detection_confidence=0.5)
        
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = mesh.process(rgb_frame)
        
        if results.multi_face_landmarks:
            return {
                "landmarks": results.multi_face_landmarks[0].landmark,
                "detected": True
            }
        
        return {"detected": False, "landmarks": []}

# ============ BEAUTY FILTERS ============

class BeautyFilterEngine:
    def __init__(self):
        self.face_processor = FaceProcessor()
        
    def apply_beauty_filter(self, frame: np.ndarray, config: BeautyFilterConfig) -> np.ndarray:
        """Apply comprehensive beauty filter"""
        result = frame.copy()
        
        # Skin smoothing using bilateral filter
        if config.smoothing_strength > 0:
            kernel_size = int(15 * config.smoothing_strength) * 2 + 1
            result = cv2.bilateralFilter(result, kernel_size, 75, 75)
        
        # Brightness adjustment
        if config.brightness_adjustment != 0:
            hsv = cv2.cvtColor(result, cv2.COLOR_BGR2HSV).astype(np.float32)
            hsv[:, :, 2] *= (1 + config.brightness_adjustment)
            hsv[:, :, 2] = np.clip(hsv[:, :, 2], 0, 255)
            result = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
        
        # Contrast adjustment
        if config.contrast_adjustment != 0:
            result = cv2.convertScaleAbs(result, alpha=1 + config.contrast_adjustment, beta=0)
        
        # Saturation boost
        if config.saturation_boost != 0:
            hsv = cv2.cvtColor(result, cv2.COLOR_BGR2HSV).astype(np.float32)
            hsv[:, :, 1] *= (1 + config.saturation_boost)
            hsv[:, :, 1] = np.clip(hsv[:, :, 1], 0, 255)
            result = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
        
        # Detect and enhance eyes
        if config.eye_enlargement > 0 or config.eye_brightness > 0:
            faces = self.face_processor.detect_faces(result)
            for face in faces:
                result = self._enhance_eyes(result, face, config)
        
        # Enhance lips
        if config.lips_intensity > 0:
            faces = self.face_processor.detect_faces(result)
            for face in faces:
                result = self._enhance_lips(result, face, config)
        
        return result
    
    def _enhance_eyes(self, frame: np.ndarray, face: Dict, config: BeautyFilterConfig) -> np.ndarray:
        """Enhance eyes - enlarge and brighten"""
        result = frame.copy()
        
        # Estimate eye positions (simplified)
        face_width = face["width"]
        face_height = face["height"]
        
        # Left eye
        left_eye_x = face["x_min"] + int(face_width * 0.33)
        left_eye_y = face["y_min"] + int(face_height * 0.33)
        
        # Right eye
        right_eye_x = face["x_min"] + int(face_width * 0.67)
        right_eye_y = face["y_min"] + int(face_height * 0.33)
        
        eye_radius = int(face_height * 0.1)
        
        for eye_x, eye_y in [(left_eye_x, left_eye_y), (right_eye_x, right_eye_y)]:
            # Brighten eye region
            if config.eye_brightness > 0:
                cv2.circle(result, (eye_x, eye_y), eye_radius, (255, 255, 255), -1)
                result = cv2.addWeighted(result, config.eye_brightness, frame, 1 - config.eye_brightness, 0)
        
        return result
    
    def _enhance_lips(self, frame: np.ndarray, face: Dict, config: BeautyFilterConfig) -> np.ndarray:
        """Enhance lips with color tint"""
        result = frame.copy()
        
        # Estimate lips position
        face_width = face["width"]
        face_height = face["height"]
        lips_x = face["x_min"] + int(face_width * 0.5)
        lips_y = face["y_min"] + int(face_height * 0.7)
        lips_radius = int(face_width * 0.15)
        
        # Create lips mask
        mask = np.zeros(frame.shape[:2], dtype=np.uint8)
        cv2.circle(mask, (lips_x, lips_y), lips_radius, 255, -1)
        
        # Apply color tint
        if config.lips_tint:
            # Parse color (RGB hex)
            color_hex = config.lips_tint.lstrip("#")
            r = int(color_hex[0:2], 16)
            g = int(color_hex[2:4], 16)
            b = int(color_hex[4:6], 16)
            
            overlay = result.copy()
            cv2.circle(overlay, (lips_x, lips_y), lips_radius, (b, g, r), -1)
            result = cv2.addWeighted(overlay, config.lips_intensity, result, 1 - config.lips_intensity, 0)
        
        return result

# ============ BACKGROUND FILTERS ============

class BackgroundFilterEngine:
    def __init__(self):
        self.segmentation = mp_selfie_segmentation.SelfieSegmentation(model_selection=1)
    
    def apply_background_filter(self, frame: np.ndarray, config: BackgroundFilter) -> np.ndarray:
        """Apply background effects"""
        # Get segmentation
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.segmentation.process(rgb_frame)
        mask = results.segmentation_mask
        
        if config.filter_type == "blur":
            background = cv2.GaussianBlur(frame, (config.blur_strength, config.blur_strength), 0)
            output_frame = np.where(mask[..., None] > 0.5, frame, background)
            return output_frame.astype(np.uint8)
        
        elif config.filter_type == "color":
            color_hex = config.replacement_color.lstrip("#")
            b = int(color_hex[4:6], 16)
            g = int(color_hex[2:4], 16)
            r = int(color_hex[0:2], 16)
            
            bg_color = np.full_like(frame, (b, g, r))
            output_frame = np.where(mask[..., None] > 0.5, frame, bg_color)
            return output_frame.astype(np.uint8)
        
        return frame

# ============ AI ENHANCEMENT WITH GROQ ============

class AIEnhancementEngine:
    def __init__(self):
        self.groq_client = groq_client
    
    def generate_filter_suggestions(self, frame_base64: str, filter_type: FilterType) -> List[str]:
        """Use Groq to generate filter suggestions"""
        try:
            prompt = f"""You are an expert AR filter designer. Analyze this image and suggest specific filter enhancements for {filter_type.value} filters.
            
Provide 3-5 specific, actionable suggestions that would improve the user's appearance using AR filters.
Format: Each suggestion on a new line starting with a dash.
Keep each suggestion under 50 characters."""

            message = self.groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model="mixtral-8x7b-32768",
                temperature=0.7,
                max_tokens=200
            )
            
            response_text = message.choices[0].message.content
            suggestions = [s.strip("- ") for s in response_text.split("\n") if s.strip().startswith("-")]
            return suggestions[:5]
        except Exception as e:
            logger.error(f"Groq suggestion error: {e}")
            return []
    
    def optimize_filter_parameters(self, current_config: Dict, user_feedback: str) -> Dict:
        """Use Groq to optimize filter settings based on feedback"""
        try:
            prompt = f"""You are an AR filter optimization expert. 
Current filter configuration: {json.dumps(current_config, default=str)}
User feedback: {user_feedback}

Suggest specific parameter adjustments to improve the filter result.
Return as JSON with parameter names as keys and new values (0-1 scale where applicable).
Keep response concise."""

            message = self.groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model="mixtral-8x7b-32768",
                temperature=0.5,
                max_tokens=300
            )
            
            response_text = message.choices[0].message.content
            try:
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
            except:
                pass
            
            return current_config
        except Exception as e:
            logger.error(f"Groq optimization error: {e}")
            return current_config

# ============ FRAME PROCESSOR ============

class FrameProcessor:
    def __init__(self):
        self.beauty_engine = BeautyFilterEngine()
        self.background_engine = BackgroundFilterEngine()
        self.ai_engine = AIEnhancementEngine()
        # Snapchat filters integration
        self.filter_registry = FilterRegistry()
        self.snapchat_detector = AdvancedFaceDetector()
        self.beauty_filters = AdvancedBeautyFilters()
        self.ar_filters = ARFiltersEngine()
        self.social_filters = SocialMediaFilters()
    
    def process_frame(
        self,
        frame: np.ndarray,
        active_filters: List[str],
        beauty_config: Optional[BeautyFilterConfig] = None,
        background_config: Optional[BackgroundFilter] = None,
        snapchat_filters: Optional[Dict[str, float]] = None,
        social_platform: Optional[str] = None
    ) -> tuple[np.ndarray, int]:
        """Process frame with active filters including Snapchat-style filters"""
        import time
        start_time = time.time()
        
        result = frame.copy()
        face_count = 0
        
        # Detect faces
        faces = self.beauty_engine.face_processor.detect_faces(result)
        face_count = len(faces)
        
        # Apply Snapchat filters if specified
        if snapchat_filters:
            for filter_id, intensity in snapchat_filters.items():
                if filter_id in self.filter_registry.filters:
                    if faces and self.filter_registry.filters[filter_id].requires_faces:
                        for face in faces:
                            result = self.filter_registry.apply_filter(result, filter_id, intensity, face)
                    else:
                        result = self.filter_registry.apply_filter(result, filter_id, intensity, None)
        
        # Apply social platform optimization
        if social_platform and social_platform in ['instagram', 'tiktok', 'youtube', 'facebook', 'snapchat']:
            if faces:
                result = self.social_filters.apply_platform_filter(result, social_platform, faces)
        
        # Apply beauty filters
        if "beauty" in active_filters and beauty_config:
            result = self.beauty_engine.apply_beauty_filter(result, beauty_config)
        
        # Apply background filter
        if "background" in active_filters and background_config:
            result = self.background_engine.apply_background_filter(result, background_config)
        
        # Apply other filters
        if "cartoon" in active_filters:
            result = self._apply_cartoon_filter(result)
        
        if "vintage" in active_filters:
            result = self._apply_vintage_filter(result)
        
        if "artistic" in active_filters:
            result = self._apply_artistic_filter(result)
        
        processing_time = (time.time() - start_time) * 1000
        return result, face_count, processing_time
    
    def _apply_cartoon_filter(self, frame: np.ndarray) -> np.ndarray:
        """Apply cartoon effect"""
        # Reduce colors
        data = frame.reshape((-1, 3))
        data = np.float32(data)
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        ret, label, center = cv2.kmeans(data, 8, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        center = np.uint8(center)
        result = center[label.flatten()]
        result = result.reshape(frame.shape)
        
        # Add edge detection
        gray = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
        edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9)
        edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        
        return cv2.bitwise_and(result, edges)
    
    def _apply_vintage_filter(self, frame: np.ndarray) -> np.ndarray:
        """Apply vintage effect"""
        # Reduce saturation
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[:, :, 1] *= 0.5
        result = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
        
        # Add warm tone
        result[:, :, 0] = np.clip(result[:, :, 0] * 0.8, 0, 255)  # Blue
        result[:, :, 2] = np.clip(result[:, :, 2] * 1.2, 0, 255)  # Red
        
        return result
    
    def _apply_artistic_filter(self, frame: np.ndarray) -> np.ndarray:
        """Apply artistic effect"""
        # Stylization
        result = cv2.stylization(frame, sigma_s=60, sigma_r=0.4)
        return result

# ============ API ENDPOINTS ============

@router.post("/session/create")
async def create_session(user_id: str = Body(...)):
    """Create new filter session"""
    import uuid
    session_id = str(uuid.uuid4())
    
    session = FilterSession(
        session_id=session_id,
        user_id=user_id
    )
    
    # Store in database (implement with MongoDB)
    return {
        "session_id": session_id,
        "user_id": user_id,
        "created_at": session.created_at
    }

@router.post("/frame/process")
async def process_frame(
    session_id: str = Body(...),
    frame_base64: str = Body(...),
    active_filters: List[str] = Body(...),
    beauty_config: Optional[Dict] = Body(None),
    background_config: Optional[Dict] = Body(None)
):
    """Process video frame with filters"""
    try:
        # Decode frame
        frame_bytes = base64.b64decode(frame_base64)
        frame_array = np.frombuffer(frame_bytes, dtype=np.uint8)
        frame = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)
        
        # Create configs
        beauty_cfg = BeautyFilterConfig(**beauty_config) if beauty_config else None
        bg_cfg = BackgroundFilter(**background_config) if background_config else None
        
        # Process
        processor = FrameProcessor()
        result_frame, face_count, processing_time = processor.process_frame(
            frame, active_filters, beauty_cfg, bg_cfg
        )
        
        # Encode result
        _, buffer = cv2.imencode('.jpg', result_frame)
        result_base64 = base64.b64encode(buffer).decode()
        
        return {
            "session_id": session_id,
            "frame_base64": result_base64,
            "detected_faces": face_count,
            "processing_time_ms": processing_time,
            "applied_filters": active_filters
        }
    except Exception as e:
        logger.error(f"Frame processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ai/enhance")
async def ai_enhance_frame(request: AIEnhancementRequest):
    """Apply AI enhancement to frame"""
    try:
        # Decode frame
        frame_bytes = base64.b64decode(request.image_base64)
        image = Image.open(BytesIO(frame_bytes))
        frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Get AI suggestions
        ai_engine = AIEnhancementEngine()
        suggestions = ai_engine.generate_filter_suggestions(
            request.image_base64,
            request.filter_type
        )
        
        # Apply enhancements based on config
        processor = FrameProcessor()
        if request.config:
            beauty_cfg = BeautyFilterConfig(**request.config)
            enhanced_frame, _, _ = processor.process_frame(
                frame, [request.filter_type.value], beauty_cfg
            )
        else:
            enhanced_frame = frame
        
        # Encode result
        _, buffer = cv2.imencode('.jpg', enhanced_frame)
        result_base64 = base64.b64encode(buffer).decode()
        
        return {
            "frame_base64": result_base64,
            "ai_suggestions": suggestions,
            "applied_filters": [request.filter_type.value],
            "model_used": request.model.value
        }
    except Exception as e:
        logger.error(f"AI enhancement error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/filters/available")
async def get_available_filters():
    """Get all available filters"""
    return {
        "filters": [
            {
                "name": "Beauty",
                "type": "beauty",
                "description": "Skin smoothing, brightening, eye and lip enhancement",
                "configurable": True
            },
            {
                "name": "Background Blur",
                "type": "background",
                "description": "Professional background blur effect",
                "configurable": True
            },
            {
                "name": "Cartoon",
                "type": "cartoon",
                "description": "Transform to cartoon style",
                "configurable": False
            },
            {
                "name": "Vintage",
                "type": "vintage",
                "description": "Classic vintage film effect",
                "configurable": False
            },
            {
                "name": "Artistic",
                "type": "artistic",
                "description": "Artistic stylization effect",
                "configurable": False
            }
        ]
    }

@router.post("/suggestions/generate")
async def generate_suggestions(
    frame_base64: str = Body(...),
    filter_type: FilterType = Body(...)
):
    """Generate AI suggestions for filter improvements"""
    try:
        ai_engine = AIEnhancementEngine()
        suggestions = ai_engine.generate_filter_suggestions(frame_base64, filter_type)
        
        return {
            "filter_type": filter_type.value,
            "suggestions": suggestions
        }
    except Exception as e:
        logger.error(f"Suggestion generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/parameters/optimize")
async def optimize_parameters(
    current_config: Dict = Body(...),
    user_feedback: str = Body(...)
):
    """Optimize filter parameters using AI"""
    try:
        ai_engine = AIEnhancementEngine()
        optimized_config = ai_engine.optimize_filter_parameters(current_config, user_feedback)
        
        return {
            "optimized_config": optimized_config,
            "feedback_applied": user_feedback
        }
    except Exception as e:
        logger.error(f"Parameter optimization error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """Health check"""
    return {
        "status": "healthy",
        "service": "ai_filter_studio",
        "timestamp": datetime.utcnow().isoformat()
    }


# ============ SOCIAL MEDIA FILTERS ENDPOINTS ============

@router.get("/social-filters/available")
async def get_social_filters():
    """Get all social media platform filters"""
    registry = SocialFilterRegistry()
    return {
        "filters": registry.list_all_filters(),
        "platforms": [p.value for p in PlatformType],
        "total_count": len(registry.filters)
    }

@router.get("/social-filters/by-platform/{platform}")
async def get_social_filters_by_platform(platform: str):
    """Get filters for specific social platform"""
    valid_platforms = [p.value for p in PlatformType]
    if platform not in valid_platforms:
        raise HTTPException(status_code=400, detail=f"Invalid platform: {platform}")
    
    registry = SocialFilterRegistry()
    filters = registry.get_filters_by_platform(platform)
    return {
        "platform": platform,
        "filters": filters,
        "count": len(filters)
    }

@router.post("/social-filters/apply")
async def apply_social_filters(
    platform: str = Body(...),
    filter_ids: List[str] = Body(...),
    frame_base64: str = Body(...),
    intensities: Dict[str, float] = Body(default_factory=dict)
):
    """Apply social media filters to frame"""
    try:
        # Decode frame
        frame_bytes = base64.b64decode(frame_base64)
        frame_array = np.frombuffer(frame_bytes, dtype=np.uint8)
        frame = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)
        
        if frame is None:
            raise HTTPException(status_code=400, detail="Invalid frame")
        
        # Apply filters
        import time
        start_time = time.time()
        
        registry = SocialFilterRegistry()
        result = frame.copy()
        
        applied_filters = []
        for filter_id in filter_ids:
            if filter_id in registry.filters:
                intensity = intensities.get(filter_id, 0.5)
                result = registry.apply_filter(result, filter_id, intensity)
                applied_filters.append(filter_id)
        
        processing_time = (time.time() - start_time) * 1000
        
        # Encode result
        _, buffer = cv2.imencode('.jpg', result, [cv2.IMWRITE_JPEG_QUALITY, 90])
        result_base64 = base64.b64encode(buffer).decode()
        
        return {
            "platform": platform,
            "frame_base64": result_base64,
            "applied_filters": applied_filters,
            "processing_time_ms": round(processing_time, 2)
        }
    
    except Exception as e:
        logger.error(f"Social filter application error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/social-filters/batch-apply")
async def batch_apply_social_filters(
    platform: str = Body(...),
    filters_config: Dict[str, float] = Body(...),
    frame_base64: str = Body(...)
):
    """Apply multiple filters with custom intensities"""
    try:
        frame_bytes = base64.b64decode(frame_base64)
        frame_array = np.frombuffer(frame_bytes, dtype=np.uint8)
        frame = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)
        
        if frame is None:
            raise HTTPException(status_code=400, detail="Invalid frame")
        
        import time
        start_time = time.time()
        
        registry = SocialFilterRegistry()
        result = frame.copy()
        
        for filter_id, intensity in filters_config.items():
            if filter_id in registry.filters:
                result = registry.apply_filter(result, filter_id, intensity)
        
        processing_time = (time.time() - start_time) * 1000
        
        _, buffer = cv2.imencode('.jpg', result, [cv2.IMWRITE_JPEG_QUALITY, 90])
        result_base64 = base64.b64encode(buffer).decode()
        
        return {
            "platform": platform,
            "frame_base64": result_base64,
            "applied_filters": list(filters_config.keys()),
            "processing_time_ms": round(processing_time, 2)
        }
    
    except Exception as e:
        logger.error(f"Batch filter error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============ ADVANCED FILTERS ENDPOINTS ============

@router.get("/advanced-filters/available")
async def get_available_advanced_filters():
    """Get all available advanced filters organized by category"""
    try:
        registry = AdvancedFilterRegistry()
        return {
            "filters": registry.list_all_filters(),
            "categories": registry.get_all_categories(),
            "total_count": len(registry.filters)
        }
    except Exception as e:
        logger.error(f"Error fetching advanced filters: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/advanced-filters/by-category/{category}")
async def get_filters_by_category(category: str):
    """Get filters by category (beauty, artistic, cinematic, etc.)"""
    try:
        registry = AdvancedFilterRegistry()
        
        # Validate category
        valid_categories = [c.value for c in FilterCategory]
        if category not in valid_categories:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid category. Valid categories: {valid_categories}"
            )
        
        filter_category = FilterCategory(category)
        filters = registry.get_filters_by_category(filter_category)
        
        return {
            "category": category,
            "filters": filters,
            "count": len(filters)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching filters by category: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/advanced-filters/apply")
async def apply_advanced_filter(
    filter_id: str = Body(...),
    intensity: float = Body(..., ge=0.0, le=1.0),
    frame_base64: str = Body(...)
):
    """Apply a single advanced filter to a frame"""
    try:
        # Decode frame
        frame_bytes = base64.b64decode(frame_base64)
        frame_array = np.frombuffer(frame_bytes, dtype=np.uint8)
        frame = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)
        
        if frame is None:
            raise HTTPException(status_code=400, detail="Invalid frame data")
        
        import time
        start_time = time.time()
        
        # Apply filter
        registry = AdvancedFilterRegistry()
        result = registry.apply_filter(frame, filter_id, intensity)
        
        if result is None or np.array_equal(result, frame):
            raise HTTPException(status_code=404, detail=f"Filter '{filter_id}' not found")
        
        processing_time = (time.time() - start_time) * 1000
        
        # Encode result
        _, buffer = cv2.imencode('.jpg', result, [cv2.IMWRITE_JPEG_QUALITY, 90])
        result_base64 = base64.b64encode(buffer).decode()
        
        # Get filter info
        filter_info = registry.filters.get(filter_id, {})
        
        return {
            "filter_id": filter_id,
            "filter_name": filter_info.get('name', 'Unknown'),
            "category": filter_info.get('category', {}).value if isinstance(filter_info.get('category'), FilterCategory) else 'unknown',
            "intensity": intensity,
            "frame_base64": result_base64,
            "processing_time_ms": round(processing_time, 2)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error applying advanced filter: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/advanced-filters/batch-apply")
async def batch_apply_advanced_filters(
    filters_config: List[Dict[str, Any]] = Body(...),
    frame_base64: str = Body(...)
):
    """Apply multiple advanced filters sequentially with custom intensities"""
    try:
        # Decode frame
        frame_bytes = base64.b64decode(frame_base64)
        frame_array = np.frombuffer(frame_bytes, dtype=np.uint8)
        frame = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)
        
        if frame is None:
            raise HTTPException(status_code=400, detail="Invalid frame data")
        
        import time
        start_time = time.time()
        
        registry = AdvancedFilterRegistry()
        result = frame.copy()
        applied_filters = []
        
        # Apply filters sequentially
        for filter_config in filters_config:
            filter_id = filter_config.get('filter_id')
            intensity = filter_config.get('intensity', 0.5)
            
            if not filter_id:
                continue
            
            # Validate intensity
            intensity = max(0.0, min(1.0, intensity))
            
            result = registry.apply_filter(result, filter_id, intensity)
            applied_filters.append({
                'filter_id': filter_id,
                'intensity': intensity,
                'name': registry.filters.get(filter_id, {}).get('name', 'Unknown')
            })
        
        processing_time = (time.time() - start_time) * 1000
        
        # Encode result
        _, buffer = cv2.imencode('.jpg', result, [cv2.IMWRITE_JPEG_QUALITY, 90])
        result_base64 = base64.b64encode(buffer).decode()
        
        return {
            "frame_base64": result_base64,
            "applied_filters": applied_filters,
            "total_filters_applied": len(applied_filters),
            "processing_time_ms": round(processing_time, 2)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in batch apply advanced filters: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/advanced-filters/preview")
async def get_filter_preview(filter_id: str):
    """Get filter information and description"""
    try:
        registry = AdvancedFilterRegistry()
        
        if filter_id not in registry.filters:
            raise HTTPException(status_code=404, detail=f"Filter '{filter_id}' not found")
        
        filter_info = registry.filters[filter_id]
        
        return {
            "filter_id": filter_id,
            "name": filter_info.get('name'),
            "description": filter_info.get('description'),
            "category": filter_info.get('category', {}).value if isinstance(filter_info.get('category'), FilterCategory) else 'unknown',
            "intensity_range": {
                "min": 0.0,
                "max": 1.0,
                "default": 0.5
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting filter preview: {e}")
        raise HTTPException(status_code=500, detail=str(e))
