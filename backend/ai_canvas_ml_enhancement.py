"""
AI Canvas ML Enhancement Service
Integrates free ML models for image generation, enhancement, and processing
Uses: Replicate (free tier), Hugging Face Inference API, Stability AI (free tier)
"""

from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import logging
import os
import asyncio
from datetime import datetime
import base64
from io import BytesIO
import json

logger = logging.getLogger(__name__)

# Try importing free ML services
REPLICATE_AVAILABLE = False
HF_AVAILABLE = False
STABILITY_AVAILABLE = False

try:
    import replicate
    REPLICATE_AVAILABLE = True
except ImportError:
    logger.warning("Replicate not installed. Install with: pip install replicate")

try:
    from huggingface_hub import InferenceClient
    HF_AVAILABLE = True
except ImportError:
    logger.warning("Hugging Face not installed. Install with: pip install huggingface_hub")

try:
    import requests
    STABILITY_AVAILABLE = True
except ImportError:
    pass

# Models and request classes
class ImageGenerationRequest(BaseModel):
    """Request for AI image generation"""
    prompt: str
    negative_prompt: Optional[str] = None
    width: int = Field(512, ge=256, le=1024)
    height: int = Field(512, ge=256, le=1024)
    num_inference_steps: int = Field(50, ge=20, le=100)
    guidance_scale: float = Field(7.5, ge=1, le=20)
    seed: Optional[int] = None

class ImageEnhancementRequest(BaseModel):
    """Request for image enhancement"""
    image_url: str
    enhancement_type: str  # upscale, denoise, colorize, etc.
    scale_factor: Optional[int] = Field(4, ge=2, le=4)

class BackgroundRemovalRequest(BaseModel):
    """Request for background removal"""
    image_url: str

class StyleTransferRequest(BaseModel):
    """Request for style transfer"""
    content_image_url: str
    style_image_url: str
    strength: float = Field(1.0, ge=0.1, le=1.0)

class TextExtractionRequest(BaseModel):
    """Request for OCR/text extraction"""
    image_url: str

class SmartCropRequest(BaseModel):
    """Request for intelligent crop"""
    image_url: str
    aspect_ratio: str = "1:1"  # "16:9", "9:16", "1:1", etc.

class MLEnhancementService:
    """Service for free ML model integrations"""

    def __init__(self):
        self.replicate_token = os.getenv("REPLICATE_API_TOKEN")
        self.hf_token = os.getenv("HUGGINGFACE_API_TOKEN")
        self.stability_key = os.getenv("STABILITY_API_KEY")

        if REPLICATE_AVAILABLE and self.replicate_token:
            replicate.Client(api_token=self.replicate_token)
            logger.info("✅ Replicate initialized")

        if HF_AVAILABLE and self.hf_token:
            self.hf_client = InferenceClient(api_key=self.hf_token)
            logger.info("✅ Hugging Face Inference Client initialized")
        else:
            self.hf_client = None

    async def generate_image(self, request: ImageGenerationRequest) -> Dict[str, Any]:
        """Generate image using free tier Stable Diffusion (via Replicate)"""
        if not REPLICATE_AVAILABLE or not self.replicate_token:
            return {"error": "Replicate not configured"}

        try:
            # Use Stable Diffusion v2.1 (free tier available)
            output = await asyncio.to_thread(
                replicate.run,
                "stability-ai/stable-diffusion-v2",
                input={
                    "prompt": request.prompt,
                    "negative_prompt": request.negative_prompt or "",
                    "width": request.width,
                    "height": request.height,
                    "num_inference_steps": request.num_inference_steps,
                    "guidance_scale": request.guidance_scale,
                    "seed": request.seed
                }
            )

            return {
                "success": True,
                "image_url": output[0] if isinstance(output, list) else output,
                "prompt": request.prompt,
                "model": "stable-diffusion-v2",
                "generated_at": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Image generation error: {e}")
            return {"error": str(e)}

    async def enhance_image(self, request: ImageEnhancementRequest) -> Dict[str, Any]:
        """Enhance image using Hugging Face models"""
        if not HF_AVAILABLE or not self.hf_client:
            return {"error": "Hugging Face not configured"}

        try:
            # Download image from URL
            image_data = await asyncio.to_thread(
                self._fetch_image, request.image_url
            )

            if request.enhancement_type == "upscale":
                # Use Real-ESRGAN for upscaling
                output = await asyncio.to_thread(
                    self.hf_client.image_to_image,
                    image=image_data,
                    model="philipnewton/RealESRGAN_x4plus"
                )
            elif request.enhancement_type == "denoise":
                # Use denoising model
                output = await asyncio.to_thread(
                    self.hf_client.image_to_image,
                    image=image_data,
                    model="Disumbrationist/Anime2Sketch"
                )
            elif request.enhancement_type == "colorize":
                # Use colorization model
                output = await asyncio.to_thread(
                    self.hf_client.image_to_image,
                    image=image_data,
                    model="Norod78/Anime2Sketch"
                )
            else:
                return {"error": f"Unknown enhancement type: {request.enhancement_type}"}

            # Convert output to base64
            enhanced_b64 = base64.b64encode(output.getvalue()).decode()

            return {
                "success": True,
                "image": f"data:image/png;base64,{enhanced_b64}",
                "enhancement_type": request.enhancement_type,
                "model": "hugging-face-inference",
                "generated_at": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Image enhancement error: {e}")
            return {"error": str(e)}

    async def remove_background(self, request: BackgroundRemovalRequest) -> Dict[str, Any]:
        """Remove background using Hugging Face"""
        if not HF_AVAILABLE or not self.hf_client:
            return {"error": "Hugging Face not configured"}

        try:
            image_data = await asyncio.to_thread(
                self._fetch_image, request.image_url
            )

            # Use BRIA background removal model
            output = await asyncio.to_thread(
                self.hf_client.image_to_image,
                image=image_data,
                model="briaai/BRIA-RMBG-1.4"
            )

            result_b64 = base64.b64encode(output.getvalue()).decode()

            return {
                "success": True,
                "image": f"data:image/png;base64,{result_b64}",
                "model": "bria-rmbg-1.4",
                "generated_at": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Background removal error: {e}")
            return {"error": str(e)}

    async def style_transfer(self, request: StyleTransferRequest) -> Dict[str, Any]:
        """Apply style transfer using Replicate"""
        if not REPLICATE_AVAILABLE or not self.replicate_token:
            return {"error": "Replicate not configured"}

        try:
            # Fetch both images
            content_img = await asyncio.to_thread(
                self._fetch_image, request.content_image_url
            )
            style_img = await asyncio.to_thread(
                self._fetch_image, request.style_image_url
            )

            # Use neural style transfer model
            output = await asyncio.to_thread(
                replicate.run,
                "evals/neural-style-transfer",
                input={
                    "content_image": str(content_img),
                    "style_image": str(style_img),
                    "strength": request.strength
                }
            )

            return {
                "success": True,
                "image_url": output,
                "model": "neural-style-transfer",
                "generated_at": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Style transfer error: {e}")
            return {"error": str(e)}

    async def extract_text(self, request: TextExtractionRequest) -> Dict[str, Any]:
        """Extract text from image using OCR (Hugging Face)"""
        if not HF_AVAILABLE or not self.hf_client:
            return {"error": "Hugging Face not configured"}

        try:
            image_data = await asyncio.to_thread(
                self._fetch_image, request.image_url
            )

            # Use EasyOCR or similar OCR model
            output = await asyncio.to_thread(
                self.hf_client.document_question_answering,
                image=image_data,
                question="What text is visible in this image?"
            )

            return {
                "success": True,
                "text": output,
                "model": "ocr-inference",
                "generated_at": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Text extraction error: {e}")
            return {"error": str(e)}

    async def smart_crop(self, request: SmartCropRequest) -> Dict[str, Any]:
        """Intelligent crop using object detection"""
        if not HF_AVAILABLE or not self.hf_client:
            return {"error": "Hugging Face not configured"}

        try:
            image_data = await asyncio.to_thread(
                self._fetch_image, request.image_url
            )

            # Use object detection to find interesting regions
            output = await asyncio.to_thread(
                self.hf_client.object_detection,
                image=image_data
            )

            # Parse aspect ratio
            aspect_ratio = request.aspect_ratio.split(":")
            target_ratio = float(aspect_ratio[0]) / float(aspect_ratio[1])

            crop_data = {
                "aspect_ratio": request.aspect_ratio,
                "suggested_crop": self._calculate_crop(output, target_ratio),
                "detected_objects": output
            }

            return {
                "success": True,
                "crop_data": crop_data,
                "model": "yolov8-detection",
                "generated_at": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Smart crop error: {e}")
            return {"error": str(e)}

    def _fetch_image(self, url: str) -> bytes:
        """Fetch image from URL"""
        import requests
        response = requests.get(url)
        response.raise_for_status()
        return response.content

    def _calculate_crop(self, detections: List[Dict], aspect_ratio: float) -> Dict:
        """Calculate optimal crop based on detected objects"""
        if not detections:
            return {"x": 0, "y": 0, "width": 100, "height": 100}

        # Find bounding box containing all detected objects
        x_coords = [d["box"]["xmin"] + d["box"]["xmax"] for d in detections]
        y_coords = [d["box"]["ymin"] + d["box"]["ymax"] for d in detections]

        min_x = min([d["box"]["xmin"] for d in detections])
        max_x = max([d["box"]["xmax"] for d in detections])
        min_y = min([d["box"]["ymin"] for d in detections])
        max_y = max([d["box"]["ymax"] for d in detections])

        width = max_x - min_x
        height = max_y - min_y

        # Adjust for aspect ratio
        if width / height > aspect_ratio:
            height = width / aspect_ratio
        else:
            width = height * aspect_ratio

        return {
            "x": int(min_x),
            "y": int(min_y),
            "width": int(width),
            "height": int(height)
        }

# Global ML service instance
ml_service = MLEnhancementService()

# API Routes
router = APIRouter(prefix="/api/ai-canvas/ml-enhancement", tags=["ML Enhancement"])

@router.post("/generate-image")
async def generate_image(request: ImageGenerationRequest):
    """Generate image using Stable Diffusion"""
    return await ml_service.generate_image(request)

@router.post("/enhance-image")
async def enhance_image(request: ImageEnhancementRequest):
    """Enhance image with upscaling, denoising, or colorization"""
    return await ml_service.enhance_image(request)

@router.post("/remove-background")
async def remove_background(request: BackgroundRemovalRequest):
    """Remove background from image"""
    return await ml_service.remove_background(request)

@router.post("/style-transfer")
async def apply_style_transfer(request: StyleTransferRequest):
    """Apply style transfer between images"""
    return await ml_service.style_transfer(request)

@router.post("/extract-text")
async def extract_text(request: TextExtractionRequest):
    """Extract text from image using OCR"""
    return await ml_service.extract_text(request)

@router.post("/smart-crop")
async def get_smart_crop(request: SmartCropRequest):
    """Get intelligent crop suggestion based on content"""
    return await ml_service.smart_crop(request)
