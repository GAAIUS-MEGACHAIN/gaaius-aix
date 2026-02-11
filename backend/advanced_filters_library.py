"""
Advanced Filters Library - Premium Free Algorithms
Production-grade independent filters using state-of-the-art algorithms
Includes beauty, artistic, cinematic, and trending effects
"""

import cv2
import numpy as np
from typing import Optional, Tuple, Dict, List
import logging
from enum import Enum

logger = logging.getLogger(__name__)


class FilterCategory(str, Enum):
    BEAUTY = "beauty"
    ARTISTIC = "artistic"
    CINEMATIC = "cinematic"
    VINTAGE = "vintage"
    PROFESSIONAL = "professional"
    TRENDING = "trending"
    HDR = "hdr"
    RETRO = "retro"
    NATURE = "nature"
    PORTRAIT = "portrait"


class BeautyAdvanced:
    """Advanced beauty algorithms"""
    
    @staticmethod
    def face_glow(frame: np.ndarray, intensity: float = 0.5) -> np.ndarray:
        """Hollywood glow effect - professional beauty"""
        result = frame.copy().astype(np.float32)
        
        # Create glow layer
        blurred = cv2.GaussianBlur(result, (51, 51), 0)
        
        # Blend with additive mode
        result = result + blurred * intensity * 0.3
        result = np.clip(result, 0, 255)
        
        # Enhance skin tone
        hsv = cv2.cvtColor(result.astype(np.uint8), cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] * (1 - intensity * 0.15), 0, 255)
        result = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
        
        return np.clip(result, 0, 255).astype(np.uint8)
    
    @staticmethod
    def skin_tone_perfect(frame: np.ndarray, intensity: float = 0.5) -> np.ndarray:
        """Perfect skin tone correction using LAB color space"""
        # Convert to LAB
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB).astype(np.float32)
        
        # Adjust skin color in AB channels
        # A channel: red-green (skin should be slightly red)
        # B channel: yellow-blue (skin should be slightly yellow)
        lab[:, :, 1] = lab[:, :, 1] + intensity * 5  # Add red
        lab[:, :, 2] = lab[:, :, 2] + intensity * 3  # Add yellow
        
        # Slightly boost luminance
        lab[:, :, 0] = np.clip(lab[:, :, 0] * (1 + intensity * 0.1), 0, 255)
        
        result = cv2.cvtColor(lab.astype(np.uint8), cv2.COLOR_LAB2BGR)
        return result
    
    @staticmethod
    def porcelain_skin(frame: np.ndarray, intensity: float = 0.5) -> np.ndarray:
        """Porcelain smooth skin with pore reduction"""
        result = frame.copy().astype(np.float32)
        
        # Bilateral filter for edge-preserving smoothing
        for _ in range(2):
            result = cv2.bilateralFilter(result.astype(np.uint8), 9, 75, 75).astype(np.float32)
        
        # Blend with original
        alpha = 1 - intensity * 0.6
        result = cv2.addWeighted(result, intensity * 0.6, frame.astype(np.float32), alpha, 0)
        
        # Enhance with unsharp mask for texture
        blurred = cv2.GaussianBlur(result, (3, 3), 0)
        result = result + (result - blurred) * intensity * 0.3
        
        return np.clip(result, 0, 255).astype(np.uint8)
    
    @staticmethod
    def eye_sparkle(frame: np.ndarray, intensity: float = 0.5) -> np.ndarray:
        """Add sparkle to eyes"""
        result = frame.copy().astype(np.float32)
        
        # Create sparkle effect by boosting bright areas
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0
        
        # Create sparkle mask
        _, sparkle_mask = cv2.threshold((gray * 255).astype(np.uint8), 200, 255, cv2.THRESH_BINARY)
        sparkle_mask = sparkle_mask.astype(np.float32) / 255.0
        
        # Apply sparkle effect
        for i in range(3):
            result[:, :, i] = result[:, :, i] + sparkle_mask * intensity * 80
        
        return np.clip(result, 0, 255).astype(np.uint8)
    
    @staticmethod
    def rosy_cheeks(frame: np.ndarray, intensity: float = 0.5) -> np.ndarray:
        """Add natural rosy cheek blush"""
        result = frame.copy().astype(np.float32)
        
        # Create rosy overlay (pinkish)
        rows, cols = frame.shape[:2]
        
        # Focus on center-bottom area (cheek area)
        cheek_mask = np.zeros((rows, cols), dtype=np.float32)
        center_y = int(rows * 0.6)
        center_x_left = int(cols * 0.3)
        center_x_right = int(cols * 0.7)
        
        # Create Gaussian blobs for cheeks
        for cx, cy in [(center_x_left, center_y), (center_x_right, center_y)]:
            for i in range(rows):
                for j in range(cols):
                    dist = np.sqrt((i - cy) ** 2 + (j - cx) ** 2)
                    cheek_mask[i, j] += np.exp(-(dist ** 2) / (2 * 60 ** 2))
        
        cheek_mask = np.clip(cheek_mask, 0, 1)
        
        # Apply pink tint to cheeks
        result[:, :, 0] = np.clip(result[:, :, 0] - intensity * cheek_mask * 30, 0, 255)  # Blue
        result[:, :, 2] = np.clip(result[:, :, 2] + intensity * cheek_mask * 50, 0, 255)   # Red
        
        return np.clip(result, 0, 255).astype(np.uint8)


class ArtisticFilters:
    """Advanced artistic effects"""
    
    @staticmethod
    def oil_painting(frame: np.ndarray, intensity: float = 0.5) -> np.ndarray:
        """Oil painting effect"""
        kernel_size = max(3, int(5 + intensity * 10))
        if kernel_size % 2 == 0:
            kernel_size += 1
        
        result = cv2.xphoto.oilPainting(frame, kernel_size, 1)
        
        # Blend with original
        alpha = intensity
        result = cv2.addWeighted(result, alpha, frame, 1 - alpha, 0)
        
        return result
    
    @staticmethod
    def pencil_sketch(frame: np.ndarray, intensity: float = 0.5) -> np.ndarray:
        """Pencil sketch effect"""
        # Pencil sketch
        _, sketch = cv2.pencilSketch(frame, sigma_s=60, sigma_r=0.4, shade_factor=0.02)
        
        # Blend with original
        result = cv2.addWeighted(sketch, intensity, frame, 1 - intensity, 0)
        
        return result
    
    @staticmethod
    def watercolor(frame: np.ndarray, intensity: float = 0.5) -> np.ndarray:
        """Watercolor painting effect"""
        result = cv2.xphoto.createEdgePreservingFilter().filter(frame, sigma_s=60, sigma_r=0.4)
        
        # Apply color quantization for watercolor feel
        data = result.reshape((-1, 3))
        data = np.float32(data)
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        _, label, center = cv2.kmeans(data, int(20 - intensity * 15), None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        center = np.uint8(center)
        result = center[label.flatten()]
        result = result.reshape(frame.shape)
        
        # Blend
        result = cv2.addWeighted(result, intensity, frame, 1 - intensity, 0)
        
        return result
    
    @staticmethod
    def cartoon(frame: np.ndarray, intensity: float = 0.5) -> np.ndarray:
        """Cartoon effect with edge detection"""
        # Apply bilateral filter
        cartoon = cv2.bilateralFilter(frame, 9, 75, 75)
        
        # Edge detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        edges = cv2.Laplacian(gray, cv2.CV_8U)
        _, edges = cv2.threshold(edges, 100, 255, cv2.THRESH_BINARY)
        
        # Create mask
        edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        
        # Combine
        result = cartoon.copy().astype(np.float32)
        result = result - (edges.astype(np.float32) * intensity * 0.5)
        
        return np.clip(result, 0, 255).astype(np.uint8)


class CinematicFilters:
    """Professional cinematic effects"""
    
    @staticmethod
    def cinematic_blue_orange(frame: np.ndarray, intensity: float = 0.5) -> np.ndarray:
        """Popular blue-orange cinematic grade"""
        result = frame.copy().astype(np.float32)
        
        # Split channels
        b, g, r = cv2.split(result)
        
        # Apply color cast: boost blue in shadows, orange in highlights
        # Shadows (low values): add blue
        shadow_mask = (r + g + b) / 3 < 128
        
        b[shadow_mask] = np.clip(b[shadow_mask] + intensity * 40, 0, 255)
        r[~shadow_mask] = np.clip(r[~shadow_mask] + intensity * 30, 0, 255)
        g[~shadow_mask] = np.clip(g[~shadow_mask] + intensity * 10, 0, 255)
        
        result = cv2.merge([b, g, r])
        
        # Add slight desaturation
        hsv = cv2.cvtColor(result.astype(np.uint8), cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[:, :, 1] = hsv[:, :, 1] * (1 - intensity * 0.1)
        result = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
        
        return np.clip(result, 0, 255).astype(np.uint8)
    
    @staticmethod
    def teal_orange(frame: np.ndarray, intensity: float = 0.5) -> np.ndarray:
        """Professional teal-orange color grade"""
        result = frame.copy().astype(np.float32)
        
        # Convert to HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV).astype(np.float32)
        
        # Target teal for highlights (blue-green)
        # Target orange for shadows
        
        brightness = hsv[:, :, 2]
        
        # Adjust hue
        hue_shift = np.where(brightness > 128, -30, 30) * intensity
        hsv[:, :, 0] = (hsv[:, :, 0] + hue_shift) % 180
        
        # Boost saturation
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] * (1 + intensity * 0.3), 0, 255)
        
        result = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
        
        return np.clip(result, 0, 255).astype(np.uint8)
    
    @staticmethod
    def film_noir(frame: np.ndarray, intensity: float = 0.5) -> np.ndarray:
        """Classic black and white film noir"""
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        result = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        
        # Add high contrast
        result = result - 50
        result = np.clip(result * (1 + intensity * 0.5), 0, 255)
        
        # Add grain
        noise = np.random.normal(0, intensity * 10, result.shape).astype(np.int32)
        result = np.clip(result.astype(np.int32) + noise, 0, 255).astype(np.uint8)
        
        return result


class VintageFilters:
    """Vintage and retro effects"""
    
    @staticmethod
    def sepia(frame: np.ndarray, intensity: float = 0.5) -> np.ndarray:
        """Classic sepia tone"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        result = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        
        # Apply sepia
        sepia_kernel = np.array([[0.272, 0.534, 0.131],
                                 [0.349, 0.686, 0.168],
                                 [0.393, 0.769, 0.189]])
        
        result = cv2.transform(result, sepia_kernel)
        result = np.clip(result, 0, 255).astype(np.uint8)
        
        # Blend
        result = cv2.addWeighted(result, intensity, frame, 1 - intensity, 0)
        
        return result
    
    @staticmethod
    def faded_vintage(frame: np.ndarray, intensity: float = 0.5) -> np.ndarray:
        """Faded vintage film effect"""
        result = frame.copy().astype(np.float32)
        
        # Reduce contrast
        result = result - 50
        result = result * (1 - intensity * 0.3)
        
        # Add yellow-red cast
        result[:, :, 0] = np.clip(result[:, :, 0] - intensity * 30, 0, 255)  # Blue
        result[:, :, 1] = np.clip(result[:, :, 1] + intensity * 20, 0, 255)   # Green
        result[:, :, 2] = np.clip(result[:, :, 2] + intensity * 30, 0, 255)   # Red
        
        # Reduce saturation
        hsv = cv2.cvtColor(result.astype(np.uint8), cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[:, :, 1] = hsv[:, :, 1] * (1 - intensity * 0.4)
        result = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
        
        return np.clip(result, 0, 255).astype(np.uint8)
    
    @staticmethod
    def polaroid(frame: np.ndarray, intensity: float = 0.5) -> np.ndarray:
        """Instant Polaroid camera effect"""
        result = frame.copy().astype(np.float32)
        
        # Boost highlights
        result = result * (1 + intensity * 0.2)
        
        # Add reddish-yellow cast
        result[:, :, 0] = np.clip(result[:, :, 0] - intensity * 20, 0, 255)
        result[:, :, 2] = np.clip(result[:, :, 2] + intensity * 40, 0, 255)
        
        # Vignette
        rows, cols = frame.shape[:2]
        kernel_x = cv2.getGaussianKernel(cols, cols / 2)
        kernel_y = cv2.getGaussianKernel(rows, rows / 2)
        kernel = kernel_y * kernel_x.T
        mask = kernel / kernel.max()
        
        for i in range(3):
            result[:, :, i] = result[:, :, i] * (0.7 + mask * 0.3 * intensity)
        
        return np.clip(result, 0, 255).astype(np.uint8)


class SpecialEffects:
    """Special effects filters"""
    
    @staticmethod
    def hdr_tone_mapping(frame: np.ndarray, intensity: float = 0.5) -> np.ndarray:
        """HDR tone mapping effect"""
        # Create Mertens tone mapper
        tonemap = cv2.createTonemap(gamma=2.2)
        hdr = tonemap.process((frame.astype(np.float32) / 255.0).astype(np.float32))
        
        # Convert back to 8-bit
        result = np.clip(hdr * 255, 0, 255).astype(np.uint8)
        
        # Blend with original
        result = cv2.addWeighted(result, intensity, frame, 1 - intensity, 0)
        
        return result
    
    @staticmethod
    def vivid_contrast(frame: np.ndarray, intensity: float = 0.5) -> np.ndarray:
        """Vivid color with high contrast"""
        result = frame.copy().astype(np.float32)
        
        # Increase contrast
        result = result - 128
        result = result * (1 + intensity * 0.8)
        result = result + 128
        
        # Increase saturation
        hsv = cv2.cvtColor(np.clip(result, 0, 255).astype(np.uint8), cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] * (1 + intensity * 0.5), 0, 255)
        hsv[:, :, 2] = np.clip(hsv[:, :, 2] * (1 + intensity * 0.2), 0, 255)
        
        result = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
        
        return np.clip(result, 0, 255).astype(np.uint8)
    
    @staticmethod
    def blur_background_portrait(frame: np.ndarray, intensity: float = 0.5) -> np.ndarray:
        """Intelligent background blur for portrait effect"""
        # Apply Gaussian blur
        kernel_size = int(5 + intensity * 20)
        if kernel_size % 2 == 0:
            kernel_size += 1
        
        blurred = cv2.GaussianBlur(frame, (kernel_size, kernel_size), 0)
        
        # Create edge-aware mask (keep sharp edges)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        
        # Dilate edges
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        edges = cv2.dilate(edges, kernel, iterations=2)
        
        # Create mask
        mask = (edges > 0).astype(np.float32)
        
        # Blend
        result = frame.copy().astype(np.float32)
        blurred_f = blurred.astype(np.float32)
        
        for i in range(3):
            result[:, :, i] = result[:, :, i] * (1 - mask * (1 - intensity)) + blurred_f[:, :, i] * mask * (1 - intensity)
        
        return np.clip(result, 0, 255).astype(np.uint8)
    
    @staticmethod
    def nature_enhancement(frame: np.ndarray, intensity: float = 0.5) -> np.ndarray:
        """Enhance nature colors"""
        result = frame.copy().astype(np.float32)
        
        # Boost greens and blues
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV).astype(np.float32)
        
        # Green range: 35-85, Blue range: 100-130
        green_mask = (hsv[:, :, 0] > 35) & (hsv[:, :, 0] < 85)
        blue_mask = (hsv[:, :, 0] > 100) & (hsv[:, :, 0] < 130)
        
        # Boost saturation for these colors
        hsv[green_mask | blue_mask, 1] = np.clip(
            hsv[green_mask | blue_mask, 1] * (1 + intensity * 0.4), 0, 255
        )
        
        # Slightly boost value
        hsv[:, :, 2] = np.clip(hsv[:, :, 2] * (1 + intensity * 0.1), 0, 255)
        
        result = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
        
        return result


class AdvancedFilterRegistry:
    """Central registry for all advanced filters"""
    
    def __init__(self):
        self.filters = {
            # Beauty filters
            'face_glow': {
                'name': 'Face Glow',
                'description': 'Hollywood glow effect',
                'category': FilterCategory.BEAUTY,
                'func': BeautyAdvanced.face_glow
            },
            'skin_tone_perfect': {
                'name': 'Perfect Skin Tone',
                'description': 'LAB color space correction',
                'category': FilterCategory.BEAUTY,
                'func': BeautyAdvanced.skin_tone_perfect
            },
            'porcelain_skin': {
                'name': 'Porcelain Skin',
                'description': 'Smooth pore reduction',
                'category': FilterCategory.BEAUTY,
                'func': BeautyAdvanced.porcelain_skin
            },
            'eye_sparkle': {
                'name': 'Eye Sparkle',
                'description': 'Add sparkle to eyes',
                'category': FilterCategory.BEAUTY,
                'func': BeautyAdvanced.eye_sparkle
            },
            'rosy_cheeks': {
                'name': 'Rosy Cheeks',
                'description': 'Natural blush effect',
                'category': FilterCategory.BEAUTY,
                'func': BeautyAdvanced.rosy_cheeks
            },
            
            # Artistic filters
            'oil_painting': {
                'name': 'Oil Painting',
                'description': 'Artistic oil painting',
                'category': FilterCategory.ARTISTIC,
                'func': ArtisticFilters.oil_painting
            },
            'pencil_sketch': {
                'name': 'Pencil Sketch',
                'description': 'Hand-drawn sketch',
                'category': FilterCategory.ARTISTIC,
                'func': ArtisticFilters.pencil_sketch
            },
            'watercolor': {
                'name': 'Watercolor',
                'description': 'Watercolor painting',
                'category': FilterCategory.ARTISTIC,
                'func': ArtisticFilters.watercolor
            },
            'cartoon_effect': {
                'name': 'Cartoon',
                'description': 'Cartoon style',
                'category': FilterCategory.ARTISTIC,
                'func': ArtisticFilters.cartoon
            },
            
            # Cinematic filters
            'cinematic_blue_orange': {
                'name': 'Blue-Orange Cinematic',
                'description': 'Professional color grade',
                'category': FilterCategory.CINEMATIC,
                'func': CinematicFilters.cinematic_blue_orange
            },
            'teal_orange': {
                'name': 'Teal-Orange',
                'description': 'Trendy color grade',
                'category': FilterCategory.CINEMATIC,
                'func': CinematicFilters.teal_orange
            },
            'film_noir': {
                'name': 'Film Noir',
                'description': 'Classic B&W with grain',
                'category': FilterCategory.CINEMATIC,
                'func': CinematicFilters.film_noir
            },
            
            # Vintage filters
            'sepia': {
                'name': 'Sepia',
                'description': 'Classic sepia tone',
                'category': FilterCategory.VINTAGE,
                'func': VintageFilters.sepia
            },
            'faded_vintage': {
                'name': 'Faded Vintage',
                'description': 'Aged film effect',
                'category': FilterCategory.VINTAGE,
                'func': VintageFilters.faded_vintage
            },
            'polaroid': {
                'name': 'Polaroid',
                'description': 'Instant camera effect',
                'category': FilterCategory.VINTAGE,
                'func': VintageFilters.polaroid
            },
            
            # Special effects
            'hdr_tone_mapping': {
                'name': 'HDR Tone Mapping',
                'description': 'Professional HDR effect',
                'category': FilterCategory.HDR,
                'func': SpecialEffects.hdr_tone_mapping
            },
            'vivid_contrast': {
                'name': 'Vivid Contrast',
                'description': 'High contrast vivid',
                'category': FilterCategory.PROFESSIONAL,
                'func': SpecialEffects.vivid_contrast
            },
            'portrait_blur': {
                'name': 'Portrait Blur',
                'description': 'Background blur effect',
                'category': FilterCategory.PORTRAIT,
                'func': SpecialEffects.blur_background_portrait
            },
            'nature_enhancement': {
                'name': 'Nature Enhancement',
                'description': 'Boost greens and blues',
                'category': FilterCategory.NATURE,
                'func': SpecialEffects.nature_enhancement
            }
        }
    
    def get_filters_by_category(self, category: FilterCategory) -> List[Dict]:
        """Get filters by category"""
        return [
            {
                'id': k,
                'name': v['name'],
                'description': v['description'],
                'category': v['category'].value
            }
            for k, v in self.filters.items()
            if v['category'] == category
        ]
    
    def apply_filter(self, frame: np.ndarray, filter_id: str, intensity: float = 0.5) -> np.ndarray:
        """Apply a filter to a frame"""
        if filter_id not in self.filters:
            logger.warning(f"Filter {filter_id} not found")
            return frame
        
        try:
            filter_func = self.filters[filter_id]['func']
            return filter_func(frame, intensity)
        except Exception as e:
            logger.error(f"Error applying filter {filter_id}: {e}")
            return frame
    
    def list_all_filters(self) -> List[Dict]:
        """List all available filters"""
        return [
            {
                'id': k,
                'name': v['name'],
                'description': v['description'],
                'category': v['category'].value
            }
            for k, v in self.filters.items()
        ]
    
    def get_all_categories(self) -> List[str]:
        """Get all filter categories"""
        categories = set()
        for filter_info in self.filters.values():
            categories.add(filter_info['category'].value)
        return sorted(list(categories))
