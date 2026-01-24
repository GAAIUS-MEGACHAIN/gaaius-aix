"""
Social Media Platform-Specific Filters
Production-grade implementations for Instagram, TikTok, YouTube, and Facebook
Real algorithms for trending effects and platform optimization
"""

import cv2
import numpy as np
from typing import Optional, Tuple, Dict, List
import logging
from enum import Enum

logger = logging.getLogger(__name__)


class PlatformType(str, Enum):
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"
    FACEBOOK = "facebook"
    SNAPCHAT = "snapchat"


class InstagramFilters:
    """Instagram-specific filters matching app trending effects"""
    
    @staticmethod
    def clarendon_filter(frame: np.ndarray, intensity: float = 0.5) -> np.ndarray:
        """Clarendon: High contrast, bright, washed out
        Instagram's signature filter - bright, clear, high contrast"""
        result = frame.copy().astype(np.float32)
        
        # Increase brightness
        result = result * (1.0 + intensity * 0.3)
        
        # Increase contrast (LAB color space)
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB).astype(np.float32)
        l_channel = lab[:, :, 0]
        
        # Enhance L channel contrast
        mean_l = np.mean(l_channel)
        lab[:, :, 0] = np.clip(mean_l + (l_channel - mean_l) * (1 + intensity * 0.5), 0, 255)
        
        result = cv2.cvtColor(lab.astype(np.uint8), cv2.COLOR_LAB2BGR).astype(np.float32)
        
        # Reduce saturation slightly (cool tone)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[:, :, 1] = hsv[:, :, 1] * (1.0 - intensity * 0.2)
        result = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR).astype(np.float32)
        
        return np.clip(result, 0, 255).astype(np.uint8)
    
    @staticmethod
    def juno_filter(frame: np.ndarray, intensity: float = 0.5) -> np.ndarray:
        """Juno: Cool tones, pink/magenta highlights
        Popular for portrait and lifestyle content"""
        result = frame.copy().astype(np.float32)
        
        # Split channels
        b, g, r = cv2.split(result)
        
        # Enhance blue and red channels (cool + pink tones)
        b = np.clip(b + intensity * 30, 0, 255)
        r = np.clip(r + intensity * 20, 0, 255)
        g = np.clip(g - intensity * 10, 0, 255)
        
        result = cv2.merge([b, g, r])
        
        # Add slight vignette
        rows, cols = frame.shape[:2]
        kernel_x = cv2.getGaussianKernel(cols, cols / 2)
        kernel_y = cv2.getGaussianKernel(rows, rows / 2)
        kernel = kernel_y * kernel_x.T
        mask = kernel / kernel.max()
        
        for i in range(3):
            result[:, :, i] = result[:, :, i] * (0.8 + mask * (0.2 * intensity))
        
        return np.clip(result, 0, 255).astype(np.uint8)
    
    @staticmethod
    def lark_filter(frame: np.ndarray, intensity: float = 0.5) -> np.ndarray:
        """Lark: Cool, desaturated, moody aesthetic
        Popular for artistic and moody photos"""
        result = frame.copy().astype(np.float32)
        
        # Desaturate
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        result = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR).astype(np.float32)
        
        # Blend with original
        alpha = 1 - intensity * 0.6
        result = cv2.addWeighted(result, 1 - alpha, frame.astype(np.float32), alpha, 0)
        
        # Add cool tone overlay
        result[:, :, 0] = np.clip(result[:, :, 0] + intensity * 40, 0, 255)  # Blue
        result[:, :, 2] = np.clip(result[:, :, 2] - intensity * 20, 0, 255)   # Red
        
        # Reduce brightness
        result = result * (1 - intensity * 0.15)
        
        return np.clip(result, 0, 255).astype(np.uint8)
    
    @staticmethod
    def perpetua_filter(frame: np.ndarray, intensity: float = 0.5) -> np.ndarray:
        """Perpetua: Blue and teal tones, cool mood
        Great for nature and outdoor content"""
        result = frame.copy().astype(np.float32)
        
        # Apply blue-teal color cast
        b, g, r = cv2.split(result)
        
        b = np.clip(b + intensity * 50, 0, 255)
        g = np.clip(g + intensity * 20, 0, 255)
        r = np.clip(r - intensity * 15, 0, 255)
        
        result = cv2.merge([b, g, r])
        
        # Adjust brightness
        result = result * (1 + intensity * 0.1)
        
        return np.clip(result, 0, 255).astype(np.uint8)


class TikTokFilters:
    """TikTok-specific filters for trending effects and viral aesthetics"""
    
    @staticmethod
    def duotone_filter(frame: np.ndarray, intensity: float = 0.5, color1: Tuple[int, int, int] = (255, 100, 50), color2: Tuple[int, int, int] = (50, 100, 255)) -> np.ndarray:
        """Duotone: Two-color effect popular on TikTok
        Creates trendy two-tone color grading"""
        result = frame.copy().astype(np.float32)
        
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0
        
        # Create duotone effect
        color1 = np.array(color1, dtype=np.float32)
        color2 = np.array(color2, dtype=np.float32)
        
        for i in range(3):
            result[:, :, i] = (gray * color1[i] + (1 - gray) * color2[i]) * intensity + result[:, :, i] * (1 - intensity)
        
        return np.clip(result, 0, 255).astype(np.uint8)
    
    @staticmethod
    def neon_glow_filter(frame: np.ndarray, intensity: float = 0.5) -> np.ndarray:
        """Neon Glow: Bright neon effect with glow
        TikTok trending effect for dance and music videos"""
        result = frame.copy().astype(np.float32)
        
        # Increase saturation
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] * (1 + intensity * 0.8), 0, 255)
        hsv[:, :, 2] = np.clip(hsv[:, :, 2] * (1 + intensity * 0.3), 0, 255)
        result = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR).astype(np.float32)
        
        # Add glow effect
        blurred = cv2.GaussianBlur(result, (21, 21), 0)
        result = cv2.addWeighted(result, 1 - intensity * 0.3, blurred, intensity * 0.3, 0)
        
        return np.clip(result, 0, 255).astype(np.uint8)
    
    @staticmethod
    def cyberpunk_filter(frame: np.ndarray, intensity: float = 0.5) -> np.ndarray:
        """Cyberpunk: High contrast, magenta and cyan
        Trendy cyberpunk aesthetic on TikTok"""
        result = frame.copy().astype(np.float32)
        
        # High contrast
        result = result - 50
        result = np.clip(result * (1 + intensity * 0.5), 0, 255)
        
        # Apply magenta-cyan split
        rows, cols = frame.shape[:2]
        
        # Left side: magenta, Right side: cyan
        split_col = cols // 2
        
        # Magenta effect (left)
        result[:, :split_col, 0] = np.clip(result[:, :split_col, 0] + intensity * 50, 0, 255)  # B
        result[:, :split_col, 2] = np.clip(result[:, :split_col, 2] + intensity * 50, 0, 255)  # R
        
        # Cyan effect (right)
        result[:, split_col:, 0] = np.clip(result[:, split_col:, 0] + intensity * 50, 0, 255)  # B
        result[:, split_col:, 1] = np.clip(result[:, split_col:, 1] + intensity * 30, 0, 255)  # G
        
        return np.clip(result, 0, 255).astype(np.uint8)
    
    @staticmethod
    def glitch_effect(frame: np.ndarray, intensity: float = 0.5) -> np.ndarray:
        """Glitch: Digital distortion effect
        Popular for tech and gaming content on TikTok"""
        result = frame.copy()
        
        # Random horizontal shifts (glitch effect)
        num_shifts = max(1, int(intensity * 5))
        for _ in range(num_shifts):
            start_row = np.random.randint(0, result.shape[0] - 20)
            shift_amount = int(intensity * 30)
            result[start_row:start_row + 20, :] = np.roll(result[start_row:start_row + 20, :], shift_amount, axis=1)
        
        # Channel shift (RGB displacement)
        b, g, r = cv2.split(result)
        shift = int(intensity * 5)
        b = np.roll(b, shift, axis=1)
        r = np.roll(r, -shift, axis=1)
        result = cv2.merge([b, g, r])
        
        return result
    
    @staticmethod
    def soft_focus_filter(frame: np.ndarray, intensity: float = 0.5) -> np.ndarray:
        """Soft Focus: Dreamy, soft aesthetic
        Popular for emotional and intimate TikTok videos"""
        result = frame.copy().astype(np.float32)
        
        # Create soft focus effect
        blurred = cv2.GaussianBlur(result, (25, 25), 0)
        result = cv2.addWeighted(result, 1 - intensity * 0.4, blurred, intensity * 0.4, 0)
        
        # Add slight color boost
        result = result * (1 + intensity * 0.1)
        
        return np.clip(result, 0, 255).astype(np.uint8)
    
    @staticmethod
    def y2k_filter(frame: np.ndarray, intensity: float = 0.5) -> np.ndarray:
        """Y2K: 2000s retro aesthetic with pink and purple tones
        Trending nostalgic effect on TikTok"""
        result = frame.copy().astype(np.float32)
        
        # Retro color grading: pink + purple
        b, g, r = cv2.split(result)
        
        b = np.clip(b * (1 + intensity * 0.3), 0, 255)
        g = np.clip(g * (1 - intensity * 0.1), 0, 255)
        r = np.clip(r * (1 + intensity * 0.2), 0, 255)
        
        result = cv2.merge([b, g, r])
        
        # Add slight desaturation for retro feel
        hsv = cv2.cvtColor(result.astype(np.uint8), cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[:, :, 1] = hsv[:, :, 1] * (1 - intensity * 0.2)
        result = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
        
        return np.clip(result, 0, 255).astype(np.uint8)


class YoutubeFilters:
    """YouTube-optimized filters for better video quality and engagement"""
    
    @staticmethod
    def cinema_filter(frame: np.ndarray, intensity: float = 0.5) -> np.ndarray:
        """Cinema: Professional cinematic look with letterbox aesthetic"""
        result = frame.copy().astype(np.float32)
        
        # Enhance colors for video
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] * (1 + intensity * 0.3), 0, 255)
        hsv[:, :, 2] = np.clip(hsv[:, :, 2] * (1 + intensity * 0.15), 0, 255)
        result = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR).astype(np.float32)
        
        # Professional contrast
        result = result - 40
        result = np.clip(result * (1 + intensity * 0.3), 0, 255)
        
        return np.clip(result, 0, 255).astype(np.uint8)
    
    @staticmethod
    def vibrant_filter(frame: np.ndarray, intensity: float = 0.5) -> np.ndarray:
        """Vibrant: Enhanced colors for maximum engagement"""
        result = frame.copy().astype(np.float32)
        
        # Maximum saturation boost
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] * (1 + intensity * 0.6), 0, 255)
        result = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR).astype(np.float32)
        
        # Contrast boost
        result = np.clip(result * (1 + intensity * 0.2) - intensity * 10, 0, 255)
        
        return np.clip(result, 0, 255).astype(np.uint8)


class FacebookFilters:
    """Facebook-optimized filters for social engagement and story content"""
    
    @staticmethod
    def warm_filter(frame: np.ndarray, intensity: float = 0.5) -> np.ndarray:
        """Warm: Golden warm tones for friendly, welcoming content"""
        result = frame.copy().astype(np.float32)
        
        b, g, r = cv2.split(result)
        
        # Enhance warm tones
        r = np.clip(r + intensity * 40, 0, 255)
        g = np.clip(g + intensity * 20, 0, 255)
        b = np.clip(b - intensity * 10, 0, 255)
        
        result = cv2.merge([b, g, r])
        
        return np.clip(result, 0, 255).astype(np.uint8)
    
    @staticmethod
    def story_highlight_filter(frame: np.ndarray, intensity: float = 0.5) -> np.ndarray:
        """Story Highlight: Bright, eye-catching for Facebook Stories"""
        result = frame.copy().astype(np.float32)
        
        # Increase brightness
        result = result * (1 + intensity * 0.3)
        
        # Increase saturation
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] * (1 + intensity * 0.4), 0, 255)
        result = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR).astype(np.float32)
        
        return np.clip(result, 0, 255).astype(np.uint8)


class SocialFilterRegistry:
    """Central registry for all social media platform filters"""
    
    def __init__(self):
        self.filters = {
            # Instagram filters
            'clarendon': {
                'name': 'Clarendon',
                'description': 'Bright, high contrast',
                'platform': 'instagram',
                'category': 'beauty',
                'func': InstagramFilters.clarendon_filter
            },
            'juno': {
                'name': 'Juno',
                'description': 'Cool pink highlights',
                'platform': 'instagram',
                'category': 'mood',
                'func': InstagramFilters.juno_filter
            },
            'lark': {
                'name': 'Lark',
                'description': 'Cool moody aesthetic',
                'platform': 'instagram',
                'category': 'artistic',
                'func': InstagramFilters.lark_filter
            },
            'perpetua': {
                'name': 'Perpetua',
                'description': 'Blue teal tones',
                'platform': 'instagram',
                'category': 'nature',
                'func': InstagramFilters.perpetua_filter
            },
            
            # TikTok filters
            'duotone': {
                'name': 'Duotone',
                'description': 'Two-color trendy effect',
                'platform': 'tiktok',
                'category': 'trending',
                'func': TikTokFilters.duotone_filter
            },
            'neon_glow': {
                'name': 'Neon Glow',
                'description': 'Bright neon effect',
                'platform': 'tiktok',
                'category': 'trending',
                'func': TikTokFilters.neon_glow_filter
            },
            'cyberpunk': {
                'name': 'Cyberpunk',
                'description': 'Magenta-cyan split',
                'platform': 'tiktok',
                'category': 'futuristic',
                'func': TikTokFilters.cyberpunk_filter
            },
            'glitch': {
                'name': 'Glitch',
                'description': 'Digital distortion',
                'platform': 'tiktok',
                'category': 'tech',
                'func': TikTokFilters.glitch_effect
            },
            'soft_focus': {
                'name': 'Soft Focus',
                'description': 'Dreamy aesthetic',
                'platform': 'tiktok',
                'category': 'mood',
                'func': TikTokFilters.soft_focus_filter
            },
            'y2k': {
                'name': 'Y2K',
                'description': 'Retro 2000s aesthetic',
                'platform': 'tiktok',
                'category': 'retro',
                'func': TikTokFilters.y2k_filter
            },
            
            # YouTube filters
            'cinema': {
                'name': 'Cinema',
                'description': 'Professional cinematic',
                'platform': 'youtube',
                'category': 'professional',
                'func': YoutubeFilters.cinema_filter
            },
            'vibrant': {
                'name': 'Vibrant',
                'description': 'Enhanced colors',
                'platform': 'youtube',
                'category': 'engagement',
                'func': YoutubeFilters.vibrant_filter
            },
            
            # Facebook filters
            'warm': {
                'name': 'Warm',
                'description': 'Golden warm tones',
                'platform': 'facebook',
                'category': 'friendly',
                'func': FacebookFilters.warm_filter
            },
            'story_highlight': {
                'name': 'Story Highlight',
                'description': 'Bright eye-catching',
                'platform': 'facebook',
                'category': 'stories',
                'func': FacebookFilters.story_highlight_filter
            }
        }
    
    def get_filters_by_platform(self, platform: str) -> List[Dict]:
        """Get all filters for a specific platform"""
        return [
            {
                'id': k,
                'name': v['name'],
                'description': v['description'],
                'category': v['category']
            }
            for k, v in self.filters.items()
            if v['platform'] == platform
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
                'platform': v['platform'],
                'category': v['category']
            }
            for k, v in self.filters.items()
        ]
