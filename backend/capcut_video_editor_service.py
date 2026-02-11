"""
CapCut-like Advanced Video Editor Service
Professional video editing with trimming, effects, subtitles, music, transitions
"""

import os
import uuid
import asyncio
import json
import subprocess
from datetime import datetime, timedelta
from typing import List, Dict, Optional, BinaryIO, Tuple
from enum import Enum
import mimetypes
from io import BytesIO

import boto3
import ffmpeg
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel, Field, validator

# ==================== ENUMS ====================

class EffectType(str, Enum):
    """Video effect types"""
    NONE = "none"
    BLUR = "blur"
    BRIGHTNESS = "brightness"
    CONTRAST = "contrast"
    SATURATION = "saturation"
    HUE = "hue"
    GRAYSCALE = "grayscale"
    SEPIA = "sepia"
    GLOW = "glow"
    VIGNETTE = "vignette"
    GLITCH = "glitch"
    MOSAIC = "mosaic"
    MOTION_BLUR = "motion_blur"
    ZOOM_IN = "zoom_in"
    ZOOM_OUT = "zoom_out"
    SHAKE = "shake"
    FLIP_HORIZONTAL = "flip_horizontal"
    FLIP_VERTICAL = "flip_vertical"
    ROTATE = "rotate"

class TransitionType(str, Enum):
    """Transition effects between clips"""
    NONE = "none"
    FADE = "fade"
    SLIDE_LEFT = "slide_left"
    SLIDE_RIGHT = "slide_right"
    SLIDE_UP = "slide_up"
    SLIDE_DOWN = "slide_down"
    WIPE = "wipe"
    ZOOM = "zoom"
    BLUR = "blur"
    CROSS_DISSOLVE = "cross_dissolve"
    PUSH = "push"
    REVEAL = "reveal"
    MORPH = "morph"
    SPIN = "spin"
    FLIP = "flip"

class AudioType(str, Enum):
    """Audio track types"""
    ORIGINAL = "original"
    MUSIC = "music"
    SOUND_EFFECT = "sound_effect"
    VOICE_OVER = "voice_over"
    AMBIENT = "ambient"

class TextEffect(str, Enum):
    """Text animation styles"""
    NONE = "none"
    FADE_IN = "fade_in"
    SLIDE_IN_LEFT = "slide_in_left"
    SLIDE_IN_RIGHT = "slide_in_right"
    ZOOM_IN = "zoom_in"
    BOUNCE = "bounce"
    ROTATE = "rotate"
    SCALE = "scale"
    WAVE = "wave"
    TYPE_IN = "type_in"
    POP_IN = "pop_in"

class SubtitleType(str, Enum):
    """Subtitle formats"""
    AUTO_GENERATED = "auto_generated"
    MANUAL = "manual"
    IMPORTED = "imported"

class FilterType(str, Enum):
    """Visual filters"""
    NONE = "none"
    VINTAGE = "vintage"
    COOL = "cool"
    WARM = "warm"
    CINEMATIC = "cinematic"
    NOIR = "noir"
    RETRO = "retro"
    PASTEL = "pastel"
    VIVID = "vivid"
    MUTED = "muted"

class AspectRatio(str, Enum):
    """Video aspect ratios"""
    SQUARE = "1:1"
    PORTRAIT = "9:16"
    LANDSCAPE = "16:9"
    CINEMA = "21:9"
    TIKTOK = "9:16"
    INSTAGRAM_FEED = "1:1"
    INSTAGRAM_STORY = "9:16"
    YOUTUBE = "16:9"

class ResolutionType(str, Enum):
    """Video quality presets"""
    SD = "480p"
    HD = "720p"
    FHD = "1080p"
    QHD = "1440p"
    UHD = "2160p"

# ==================== DATA MODELS ====================

class Segment(BaseModel):
    """Video segment with timing and effects"""
    segment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    clip_index: int
    
    # Timing
    start_time_ms: int  # Start in source video
    end_time_ms: int    # End in source video
    duration_ms: int = Field(default=0)  # Calculated
    
    # Position in timeline
    timeline_position_ms: int = 0
    
    # Trimming
    trim_start_ms: int = 0
    trim_end_ms: int = 0
    
    # Speed & Duration
    speed_multiplier: float = 1.0  # 0.25x to 4x
    volume: float = 1.0  # 0 to 1
    
    # Effects
    effect_type: EffectType = EffectType.NONE
    effect_intensity: float = 0.5  # 0 to 1
    filter_type: FilterType = FilterType.NONE
    
    # Rotation & Transform
    rotation_degrees: float = 0
    scale_x: float = 1.0
    scale_y: float = 1.0
    position_x: float = 0  # -1 to 1
    position_y: float = 0  # -1 to 1
    
    # Opacity & Blend
    opacity: float = 1.0  # 0 to 1
    blend_mode: str = "normal"
    
    # Color adjustments
    brightness: float = 0  # -100 to 100
    contrast: float = 0    # -100 to 100
    saturation: float = 0  # -100 to 100
    hue: float = 0         # 0 to 360
    
    # Transition
    transition_type: TransitionType = TransitionType.NONE
    transition_duration_ms: int = 300
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

class Subtitle(BaseModel):
    """Subtitle/Caption in video"""
    subtitle_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    
    # Timing
    start_time_ms: int
    end_time_ms: int
    duration_ms: int = Field(default=0)
    
    # Content
    text: str = Field(..., max_length=500)
    subtitle_type: SubtitleType = SubtitleType.MANUAL
    
    # Styling
    font_family: str = "Arial"
    font_size: int = 24
    font_color: str = "#FFFFFF"  # Hex color
    background_color: Optional[str] = "#000000"
    background_opacity: float = 0.7
    
    # Position
    position_x: float = 0.5  # 0 to 1 (center is 0.5)
    position_y: float = 0.8  # 0 to 1 (bottom is 0.8)
    
    # Animation
    text_effect: TextEffect = TextEffect.NONE
    effect_duration_ms: int = 300
    
    # Formatting
    bold: bool = False
    italic: bool = False
    underline: bool = False
    shadow: bool = True
    shadow_offset: int = 2
    
    # Language
    language: str = "en"
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

class AudioTrack(BaseModel):
    """Audio track in video"""
    audio_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    
    # Track info
    audio_type: AudioType = AudioType.ORIGINAL
    file_url: str
    s3_key: Optional[str] = None
    duration_ms: int
    
    # Timing
    start_time_ms: int = 0
    end_time_ms: Optional[int] = None
    
    # Volume & EQ
    volume: float = 1.0  # 0 to 1
    fade_in_ms: int = 0
    fade_out_ms: int = 0
    
    # Audio processing
    normalize: bool = False
    remove_silence: bool = False
    eq_preset: str = "none"  # bass_boost, treble_boost, voice, etc.
    
    # Metadata
    title: str = ""
    artist: Optional[str] = None
    license_type: str = "royalty_free"
    
    muted: bool = False
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

class TextElement(BaseModel):
    """Text overlay/title"""
    text_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    
    # Timing
    start_time_ms: int
    end_time_ms: int
    
    # Content
    content: str = Field(..., max_length=200)
    
    # Styling
    font_family: str = "Arial"
    font_size: int = 48
    font_color: str = "#FFFFFF"
    font_weight: str = "normal"  # normal, bold, 900, etc.
    
    # Background
    background_color: Optional[str] = None
    background_opacity: float = 0
    padding: int = 10
    border_radius: int = 0
    
    # Position & Transform
    position_x: float = 0.5
    position_y: float = 0.5
    rotation: float = 0
    scale: float = 1.0
    
    # Animation
    text_effect: TextEffect = TextEffect.FADE_IN
    effect_duration_ms: int = 500
    
    # Alignment
    text_align: str = "center"  # left, center, right
    
    # Shadow & Stroke
    shadow: bool = True
    shadow_offset_x: int = 2
    shadow_offset_y: int = 2
    shadow_color: str = "#000000"
    shadow_blur: int = 4
    
    stroke_enabled: bool = False
    stroke_width: int = 2
    stroke_color: str = "#000000"
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

class StickersElement(BaseModel):
    """Sticker/Emoji overlay"""
    sticker_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    
    # Timing
    start_time_ms: int
    end_time_ms: int
    
    # Sticker
    sticker_url: str
    sticker_type: str = "emoji"  # emoji, shape, custom
    
    # Position
    position_x: float = 0.5
    position_y: float = 0.5
    scale: float = 1.0
    rotation: float = 0
    opacity: float = 1.0
    
    # Animation
    animate: bool = False
    animation_type: str = "bounce"  # bounce, spin, pulse, float
    animation_speed: float = 1.0
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

class VideoProject(BaseModel):
    """Complete video editing project"""
    project_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    
    # Project Info
    title: str = Field(..., max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    thumbnail_url: Optional[str] = None
    
    # Content
    video_clips: List[str] = Field(default_factory=list)  # clip_ids
    total_clips: int = 0
    
    # Segments (processed clips with timing)
    segments: List[Segment] = Field(default_factory=list)
    
    # Audio tracks
    audio_tracks: List[str] = Field(default_factory=list)  # audio_ids
    
    # Subtitles
    subtitles: List[str] = Field(default_factory=list)  # subtitle_ids
    
    # Text overlays
    text_elements: List[str] = Field(default_factory=list)  # text_ids
    
    # Stickers
    stickers: List[str] = Field(default_factory=list)  # sticker_ids
    
    # Video settings
    aspect_ratio: AspectRatio = AspectRatio.PORTRAIT
    resolution: ResolutionType = ResolutionType.FHD
    fps: int = 30
    bitrate: str = "5000k"
    
    # Timeline duration
    total_duration_ms: int = 0
    
    # Background
    background_color: str = "#000000"
    background_image_url: Optional[str] = None
    
    # Watermark
    watermark_url: Optional[str] = None
    watermark_opacity: float = 0.5
    watermark_position: str = "bottom_right"
    
    # Export settings
    auto_caption: bool = False
    caption_language: str = "en"
    include_subtitles: bool = True
    
    # Status
    status: str = "draft"  # draft, editing, rendering, completed, failed
    progress_percentage: int = 0
    
    # Render
    render_url: Optional[str] = None
    render_size_mb: Optional[float] = None
    render_time_seconds: Optional[int] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

class VideoClip(BaseModel):
    """Original video clip"""
    clip_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    
    # File info
    file_url: str
    s3_key: str
    original_filename: str
    file_size_bytes: int
    
    # Video info
    duration_ms: int
    width: int
    height: int
    fps: float
    codec: str
    bitrate: str
    
    # Metadata
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    last_used_at: Optional[datetime] = None
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

# ==================== S3 SERVICE ====================

class S3VideoService:
    """S3 service for video files"""
    
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
            region_name=os.environ.get('AWS_REGION', 'us-east-1')
        )
        self.bucket_name = os.environ.get('AWS_S3_BUCKET', 'gaaius-video-editor')
        self.cloudfront_domain = os.environ.get('CLOUDFRONT_DOMAIN', '')
    
    async def upload_video_clip(
        self,
        file: BinaryIO,
        filename: str,
        user_id: str,
        content_type: str = "video/mp4"
    ) -> Dict[str, str]:
        """Upload video clip to S3"""
        try:
            ext = os.path.splitext(filename)[1]
            clip_id = str(uuid.uuid4())
            s3_key = f"videos/{user_id}/clips/{clip_id}{ext}"
            
            # Upload to S3
            self.s3_client.upload_fileobj(
                file,
                self.bucket_name,
                s3_key,
                ExtraArgs={
                    'ContentType': content_type,
                    'Metadata': {
                        'user_id': user_id,
                        'uploaded_at': datetime.utcnow().isoformat()
                    },
                    'CacheControl': 'max-age=31536000',
                    'ServerSideEncryption': 'AES256'
                }
            )
            
            # Generate CDN URL
            if self.cloudfront_domain:
                cdn_url = f"https://{self.cloudfront_domain}/{s3_key}"
            else:
                cdn_url = f"https://{self.bucket_name}.s3.amazonaws.com/{s3_key}"
            
            return {
                "clip_id": clip_id,
                "url": cdn_url,
                "s3_key": s3_key,
                "filename": filename,
                "uploaded_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            raise Exception(f"Video upload failed: {str(e)}")
    
    async def upload_audio(
        self,
        file: BinaryIO,
        filename: str,
        user_id: str,
        content_type: str = "audio/mpeg"
    ) -> Dict[str, str]:
        """Upload audio file"""
        try:
            ext = os.path.splitext(filename)[1]
            audio_id = str(uuid.uuid4())
            s3_key = f"audio/{user_id}/{audio_id}{ext}"
            
            self.s3_client.upload_fileobj(
                file,
                self.bucket_name,
                s3_key,
                ExtraArgs={
                    'ContentType': content_type,
                    'Metadata': {
                        'user_id': user_id,
                        'uploaded_at': datetime.utcnow().isoformat()
                    },
                    'CacheControl': 'max-age=31536000',
                    'ServerSideEncryption': 'AES256'
                }
            )
            
            if self.cloudfront_domain:
                cdn_url = f"https://{self.cloudfront_domain}/{s3_key}"
            else:
                cdn_url = f"https://{self.bucket_name}.s3.amazonaws.com/{s3_key}"
            
            return {
                "audio_id": audio_id,
                "url": cdn_url,
                "s3_key": s3_key,
                "uploaded_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            raise Exception(f"Audio upload failed: {str(e)}")
    
    async def delete_file(self, s3_key: str) -> bool:
        """Delete file from S3"""
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=s3_key)
            return True
        except:
            return False

# ==================== VIDEO PROCESSING SERVICE ====================

class FFmpegService:
    """FFmpeg-based video processing"""
    
    @staticmethod
    async def get_video_info(file_path: str) -> Dict:
        """Extract video metadata using FFprobe"""
        try:
            probe = ffmpeg.probe(file_path)
            video = next((s for s in probe['streams'] if s['codec_type'] == 'video'), None)
            audio = next((s for s in probe['streams'] if s['codec_type'] == 'audio'), None)
            
            duration_ms = int(float(probe['format']['duration']) * 1000)
            
            return {
                "duration_ms": duration_ms,
                "width": video['width'] if video else 1280,
                "height": video['height'] if video else 720,
                "fps": eval(video['r_frame_rate']) if video and 'r_frame_rate' in video else 30,
                "codec": video['codec_name'] if video else 'h264',
                "bitrate": probe['format'].get('bit_rate', '5000000'),
                "has_audio": audio is not None
            }
        except Exception as e:
            raise Exception(f"FFprobe failed: {str(e)}")
    
    @staticmethod
    async def trim_video(
        input_path: str,
        output_path: str,
        start_ms: int,
        end_ms: int
    ) -> bool:
        """Trim video segment"""
        try:
            start_sec = start_ms / 1000
            duration_sec = (end_ms - start_ms) / 1000
            
            stream = ffmpeg.input(input_path, ss=start_sec, t=duration_sec)
            stream = ffmpeg.output(stream, output_path, codec='copy')
            ffmpeg.run(stream, capture_stdout=True, capture_stderr=True)
            
            return True
        except Exception as e:
            raise Exception(f"Trim failed: {str(e)}")
    
    @staticmethod
    async def apply_effect(
        input_path: str,
        output_path: str,
        effect_type: EffectType,
        intensity: float = 0.5
    ) -> bool:
        """Apply effect to video"""
        try:
            filter_str = ""
            
            if effect_type == EffectType.BLUR:
                filter_str = f"boxblur={int(5 * intensity)}"
            elif effect_type == EffectType.BRIGHTNESS:
                filter_str = f"brightness={0.5 + intensity}"
            elif effect_type == EffectType.CONTRAST:
                filter_str = f"contrast={1 + intensity}"
            elif effect_type == EffectType.SATURATION:
                filter_str = f"saturate={1 + intensity * 2}"
            elif effect_type == EffectType.GRAYSCALE:
                filter_str = "format=gray"
            elif effect_type == EffectType.SEPIA:
                filter_str = "colorchannelmixer=.393:.769:.189:0:.349:.686:.168:0:.272:.534:.131"
            elif effect_type == EffectType.VIGNETTE:
                filter_str = "vignette=PI/4"
            elif effect_type == EffectType.GLITCH:
                filter_str = "crop=w=iw/2:h=ih:x=iw/4:y=0"
            else:
                filter_str = "null"
            
            stream = ffmpeg.input(input_path)
            stream = ffmpeg.filter(stream, filter_str)
            stream = ffmpeg.output(stream, output_path)
            ffmpeg.run(stream, capture_stdout=True, capture_stderr=True)
            
            return True
        except Exception as e:
            raise Exception(f"Effect application failed: {str(e)}")
    
    @staticmethod
    async def apply_filter(
        input_path: str,
        output_path: str,
        filter_type: FilterType
    ) -> bool:
        """Apply color filter/LUT"""
        try:
            filter_map = {
                FilterType.VINTAGE: "eq=saturation=0.7:brightness=0.1",
                FilterType.COOL: "colortemperature=8000",
                FilterType.WARM: "colortemperature=3000",
                FilterType.CINEMATIC: "curves=cs=cinematic",
                FilterType.NOIR: "format=gray:eq=contrast=1.5",
                FilterType.PASTEL: "eq=saturation=0.5:brightness=0.15",
                FilterType.VIVID: "saturate=1.5",
                FilterType.MUTED: "eq=saturation=0.3",
                FilterType.NONE: "null"
            }
            
            filter_str = filter_map.get(filter_type, "null")
            
            stream = ffmpeg.input(input_path)
            stream = ffmpeg.filter(stream, filter_str)
            stream = ffmpeg.output(stream, output_path)
            ffmpeg.run(stream, capture_stdout=True, capture_stderr=True)
            
            return True
        except Exception as e:
            raise Exception(f"Filter application failed: {str(e)}")
    
    @staticmethod
    async def concat_videos(
        video_paths: List[str],
        output_path: str,
        preserve_audio: bool = True
    ) -> bool:
        """Concatenate multiple video clips"""
        try:
            clips = [ffmpeg.input(p) for p in video_paths]
            concat = ffmpeg.concat(*clips, v=1, a=int(preserve_audio))
            stream = ffmpeg.output(concat, output_path)
            ffmpeg.run(stream, capture_stdout=True, capture_stderr=True)
            
            return True
        except Exception as e:
            raise Exception(f"Concatenation failed: {str(e)}")
    
    @staticmethod
    async def add_subtitle(
        input_path: str,
        output_path: str,
        subtitle_file: str
    ) -> bool:
        """Burn subtitles into video"""
        try:
            stream = ffmpeg.input(input_path)
            stream = ffmpeg.filter(
                stream,
                f"subtitles={subtitle_file}:force_style='FontSize=24,FontName=Arial'"
            )
            stream = ffmpeg.output(stream, output_path)
            ffmpeg.run(stream, capture_stdout=True, capture_stderr=True)
            
            return True
        except Exception as e:
            raise Exception(f"Subtitle addition failed: {str(e)}")
    
    @staticmethod
    async def add_audio(
        video_path: str,
        audio_path: str,
        output_path: str,
        mix: bool = False
    ) -> bool:
        """Add audio track to video"""
        try:
            v_stream = ffmpeg.input(video_path)
            a_stream = ffmpeg.input(audio_path)
            
            if mix:
                # Mix audio tracks
                stream = ffmpeg.output(v_stream, a_stream, output_path, shortest=None)
            else:
                # Replace audio
                stream = ffmpeg.output(v_stream['v'], a_stream['a'], output_path, shortest=None)
            
            ffmpeg.run(stream, capture_stdout=True, capture_stderr=True)
            
            return True
        except Exception as e:
            raise Exception(f"Audio addition failed: {str(e)}")
    
    @staticmethod
    async def change_speed(
        input_path: str,
        output_path: str,
        speed_multiplier: float
    ) -> bool:
        """Change video speed"""
        try:
            # setpts filter for speed
            stream = ffmpeg.input(input_path)
            stream = ffmpeg.filter(stream, f"setpts=PTS/{speed_multiplier}")
            stream = ffmpeg.output(stream, output_path)
            ffmpeg.run(stream, capture_stdout=True, capture_stderr=True)
            
            return True
        except Exception as e:
            raise Exception(f"Speed change failed: {str(e)}")
    
    @staticmethod
    async def scale_video(
        input_path: str,
        output_path: str,
        width: int,
        height: int
    ) -> bool:
        """Resize video"""
        try:
            stream = ffmpeg.input(input_path)
            stream = ffmpeg.filter(stream, f"scale={width}:{height}")
            stream = ffmpeg.output(stream, output_path)
            ffmpeg.run(stream, capture_stdout=True, capture_stderr=True)
            
            return True
        except Exception as e:
            raise Exception(f"Scaling failed: {str(e)}")
    
    @staticmethod
    async def export_video(
        segments: List[Dict],
        output_path: str,
        resolution: ResolutionType,
        fps: int = 30
    ) -> bool:
        """Export final video from segments"""
        try:
            # Complex filtering
            scale_map = {
                ResolutionType.SD: "854x480",
                ResolutionType.HD: "1280x720",
                ResolutionType.FHD: "1920x1080",
                ResolutionType.QHD: "2560x1440",
                ResolutionType.UHD: "3840x2160"
            }
            
            scale = scale_map.get(resolution, "1920x1080")
            
            # This is simplified - actual implementation would be much more complex
            # For now, placeholder implementation
            return True
        except Exception as e:
            raise Exception(f"Export failed: {str(e)}")

# ==================== VIDEO EDITOR SERVICE ====================

class VideoEditorService:
    """CapCut-like professional video editing service"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.s3_service = S3VideoService()
        self.ffmpeg_service = FFmpegService()
    
    # ==================== PROJECT OPERATIONS ====================
    
    async def create_project(
        self,
        user_id: str,
        title: str,
        description: Optional[str] = None,
        aspect_ratio: AspectRatio = AspectRatio.PORTRAIT
    ) -> VideoProject:
        """Create new video editing project"""
        project = VideoProject(
            user_id=user_id,
            title=title,
            description=description,
            aspect_ratio=aspect_ratio
        )
        
        await self.db.video_projects.insert_one(project.dict())
        return project
    
    async def get_project(self, project_id: str, user_id: Optional[str] = None) -> Optional[VideoProject]:
        """Get project details"""
        query = {"project_id": project_id}
        if user_id:
            query["user_id"] = user_id
        
        project = await self.db.video_projects.find_one(query)
        return VideoProject(**project) if project else None
    
    async def list_projects(self, user_id: str, skip: int = 0, limit: int = 20) -> Tuple[List[VideoProject], int]:
        """List user's projects"""
        total = await self.db.video_projects.count_documents({"user_id": user_id})
        
        projects = await self.db.video_projects.find({
            "user_id": user_id
        }).sort("updated_at", -1).skip(skip).limit(limit).to_list(limit)
        
        return [VideoProject(**p) for p in projects], total
    
    async def update_project(self, project_id: str, user_id: str, updates: Dict) -> Optional[VideoProject]:
        """Update project"""
        updates['updated_at'] = datetime.utcnow()
        
        result = await self.db.video_projects.find_one_and_update(
            {"project_id": project_id, "user_id": user_id},
            {"$set": updates},
            return_document=True
        )
        
        return VideoProject(**result) if result else None
    
    async def delete_project(self, project_id: str, user_id: str) -> bool:
        """Delete project and all related files"""
        project = await self.get_project(project_id, user_id)
        if not project:
            return False
        
        # Delete all S3 files
        for clip_id in project.video_clips:
            clip = await self.db.video_clips.find_one({"clip_id": clip_id})
            if clip:
                await self.s3_service.delete_file(clip['s3_key'])
        
        for audio_id in project.audio_tracks:
            audio = await self.db.audio_tracks.find_one({"audio_id": audio_id})
            if audio:
                await self.s3_service.delete_file(audio['s3_key'])
        
        # Delete project and all sub-documents
        await self.db.video_projects.delete_one({"project_id": project_id})
        await self.db.video_clips.delete_many({"project_id": project_id})
        await self.db.subtitles.delete_many({"project_id": project_id})
        await self.db.audio_tracks.delete_many({"project_id": project_id})
        await self.db.text_elements.delete_many({"project_id": project_id})
        await self.db.stickers.delete_many({"project_id": project_id})
        
        return True
    
    # ==================== VIDEO CLIP OPERATIONS ====================
    
    async def add_video_clip(
        self,
        project_id: str,
        user_id: str,
        file: BinaryIO,
        filename: str
    ) -> Optional[VideoClip]:
        """Upload and add video clip to project"""
        # Upload to S3
        upload_result = await self.s3_service.upload_video_clip(file, filename, user_id)
        
        # Get video info
        video_info = await self.ffmpeg_service.get_video_info(filename)
        
        # Create clip
        clip = VideoClip(
            user_id=user_id,
            file_url=upload_result['url'],
            s3_key=upload_result['s3_key'],
            original_filename=filename,
            file_size_bytes=file.seek(0, 2),
            **video_info
        )
        
        await self.db.video_clips.insert_one(clip.dict())
        
        # Add to project
        await self.db.video_projects.update_one(
            {"project_id": project_id},
            {
                "$push": {"video_clips": clip.clip_id},
                "$inc": {"total_clips": 1}
            }
        )
        
        return clip
    
    async def remove_video_clip(self, project_id: str, clip_id: str, user_id: str) -> bool:
        """Remove clip from project"""
        clip = await self.db.video_clips.find_one({"clip_id": clip_id})
        if not clip or clip['user_id'] != user_id:
            return False
        
        # Delete from S3
        await self.s3_service.delete_file(clip['s3_key'])
        
        # Remove from project
        await self.db.video_projects.update_one(
            {"project_id": project_id},
            {
                "$pull": {"video_clips": clip_id},
                "$inc": {"total_clips": -1}
            }
        )
        
        # Delete clip
        await self.db.video_clips.delete_one({"clip_id": clip_id})
        
        return True
    
    # ==================== SEGMENT/TIMELINE OPERATIONS ====================
    
    async def create_segment(
        self,
        project_id: str,
        clip_id: str,
        start_time_ms: int,
        end_time_ms: int,
        clip_index: int
    ) -> Optional[Segment]:
        """Create segment from clip"""
        clip = await self.db.video_clips.find_one({"clip_id": clip_id})
        if not clip:
            return None
        
        segment = Segment(
            clip_index=clip_index,
            start_time_ms=start_time_ms,
            end_time_ms=end_time_ms,
            duration_ms=end_time_ms - start_time_ms,
            trim_start_ms=0,
            trim_end_ms=end_time_ms - start_time_ms
        )
        
        # Add segment to project
        await self.db.video_projects.update_one(
            {"project_id": project_id},
            {"$push": {"segments": segment.dict()}}
        )
        
        return segment
    
    async def update_segment(
        self,
        project_id: str,
        segment_id: str,
        updates: Dict
    ) -> Optional[Segment]:
        """Update segment properties (effects, timing, etc)"""
        updates['updated_at'] = datetime.utcnow()
        
        # Update in segments array
        result = await self.db.video_projects.find_one_and_update(
            {"project_id": project_id, "segments.segment_id": segment_id},
            {"$set": {"segments.$": updates}},
            return_document=True
        )
        
        if result:
            for seg in result['segments']:
                if seg['segment_id'] == segment_id:
                    return Segment(**seg)
        
        return None
    
    async def trim_segment(
        self,
        project_id: str,
        segment_id: str,
        trim_start_ms: int,
        trim_end_ms: int
    ) -> Optional[Segment]:
        """Trim segment timing"""
        return await self.update_segment(project_id, segment_id, {
            "trim_start_ms": trim_start_ms,
            "trim_end_ms": trim_end_ms,
            "duration_ms": trim_end_ms - trim_start_ms
        })
    
    async def apply_effect_to_segment(
        self,
        project_id: str,
        segment_id: str,
        effect_type: EffectType,
        intensity: float = 0.5
    ) -> Optional[Segment]:
        """Apply effect to segment"""
        return await self.update_segment(project_id, segment_id, {
            "effect_type": effect_type,
            "effect_intensity": intensity
        })
    
    async def apply_filter_to_segment(
        self,
        project_id: str,
        segment_id: str,
        filter_type: FilterType
    ) -> Optional[Segment]:
        """Apply color filter to segment"""
        return await self.update_segment(project_id, segment_id, {
            "filter_type": filter_type
        })
    
    # ==================== SUBTITLE OPERATIONS ====================
    
    async def add_subtitle(
        self,
        project_id: str,
        text: str,
        start_time_ms: int,
        end_time_ms: int,
        style: Dict = None
    ) -> Optional[Subtitle]:
        """Add subtitle/caption to video"""
        subtitle = Subtitle(
            project_id=project_id,
            text=text,
            start_time_ms=start_time_ms,
            end_time_ms=end_time_ms,
            duration_ms=end_time_ms - start_time_ms
        )
        
        # Apply custom styling
        if style:
            for key, value in style.items():
                if hasattr(subtitle, key):
                    setattr(subtitle, key, value)
        
        await self.db.subtitles.insert_one(subtitle.dict())
        
        # Add to project
        await self.db.video_projects.update_one(
            {"project_id": project_id},
            {"$push": {"subtitles": subtitle.subtitle_id}}
        )
        
        return subtitle
    
    async def generate_auto_subtitles(
        self,
        project_id: str,
        language: str = "en"
    ) -> List[Subtitle]:
        """Generate subtitles automatically from audio"""
        # This would integrate with speech-to-text service (Groq, Whisper, etc.)
        # Placeholder implementation
        
        project = await self.get_project(project_id)
        if not project or not project.video_clips:
            return []
        
        # Would use speech recognition API here
        subtitles = []
        
        await self.db.video_projects.update_one(
            {"project_id": project_id},
            {"$set": {"auto_caption": True, "caption_language": language}}
        )
        
        return subtitles
    
    async def update_subtitle(
        self,
        subtitle_id: str,
        updates: Dict
    ) -> Optional[Subtitle]:
        """Update subtitle text or styling"""
        updates['updated_at'] = datetime.utcnow()
        
        result = await self.db.subtitles.find_one_and_update(
            {"subtitle_id": subtitle_id},
            {"$set": updates},
            return_document=True
        )
        
        return Subtitle(**result) if result else None
    
    async def delete_subtitle(self, project_id: str, subtitle_id: str) -> bool:
        """Delete subtitle"""
        await self.db.subtitles.delete_one({"subtitle_id": subtitle_id})
        await self.db.video_projects.update_one(
            {"project_id": project_id},
            {"$pull": {"subtitles": subtitle_id}}
        )
        
        return True
    
    # ==================== AUDIO OPERATIONS ====================
    
    async def add_audio_track(
        self,
        project_id: str,
        file: BinaryIO,
        filename: str,
        user_id: str,
        audio_type: AudioType = AudioType.MUSIC
    ) -> Optional[AudioTrack]:
        """Add audio track (music, voice-over, etc)"""
        # Upload to S3
        upload_result = await self.s3_service.upload_audio(file, filename, user_id)
        
        # Get audio info using FFprobe
        try:
            audio_info = await FFmpegService.get_video_info(filename)
            duration_ms = audio_info['duration_ms']
        except:
            duration_ms = 0
        
        audio = AudioTrack(
            project_id=project_id,
            audio_type=audio_type,
            file_url=upload_result['url'],
            s3_key=upload_result['s3_key'],
            duration_ms=duration_ms,
            title=filename
        )
        
        await self.db.audio_tracks.insert_one(audio.dict())
        
        # Add to project
        await self.db.video_projects.update_one(
            {"project_id": project_id},
            {"$push": {"audio_tracks": audio.audio_id}}
        )
        
        return audio
    
    async def adjust_audio_volume(
        self,
        audio_id: str,
        volume: float
    ) -> Optional[AudioTrack]:
        """Adjust audio volume (0 to 1)"""
        result = await self.db.audio_tracks.find_one_and_update(
            {"audio_id": audio_id},
            {"$set": {"volume": max(0, min(1, volume))}},
            return_document=True
        )
        
        return AudioTrack(**result) if result else None
    
    async def add_audio_fade(
        self,
        audio_id: str,
        fade_in_ms: int = 0,
        fade_out_ms: int = 0
    ) -> Optional[AudioTrack]:
        """Add fade in/out to audio"""
        result = await self.db.audio_tracks.find_one_and_update(
            {"audio_id": audio_id},
            {
                "$set": {
                    "fade_in_ms": fade_in_ms,
                    "fade_out_ms": fade_out_ms
                }
            },
            return_document=True
        )
        
        return AudioTrack(**result) if result else None
    
    async def remove_audio_track(self, project_id: str, audio_id: str) -> bool:
        """Remove audio track from project"""
        audio = await self.db.audio_tracks.find_one({"audio_id": audio_id})
        if not audio:
            return False
        
        # Delete from S3
        await self.s3_service.delete_file(audio['s3_key'])
        
        # Remove from project
        await self.db.video_projects.update_one(
            {"project_id": project_id},
            {"$pull": {"audio_tracks": audio_id}}
        )
        
        await self.db.audio_tracks.delete_one({"audio_id": audio_id})
        
        return True
    
    # ==================== TEXT OPERATIONS ====================
    
    async def add_text_element(
        self,
        project_id: str,
        content: str,
        start_time_ms: int,
        end_time_ms: int,
        style: Dict = None
    ) -> Optional[TextElement]:
        """Add text overlay/title"""
        text = TextElement(
            project_id=project_id,
            content=content,
            start_time_ms=start_time_ms,
            end_time_ms=end_time_ms
        )
        
        # Apply custom styling
        if style:
            for key, value in style.items():
                if hasattr(text, key):
                    setattr(text, key, value)
        
        await self.db.text_elements.insert_one(text.dict())
        
        # Add to project
        await self.db.video_projects.update_one(
            {"project_id": project_id},
            {"$push": {"text_elements": text.text_id}}
        )
        
        return text
    
    async def update_text_element(
        self,
        text_id: str,
        updates: Dict
    ) -> Optional[TextElement]:
        """Update text content or styling"""
        updates['updated_at'] = datetime.utcnow()
        
        result = await self.db.text_elements.find_one_and_update(
            {"text_id": text_id},
            {"$set": updates},
            return_document=True
        )
        
        return TextElement(**result) if result else None
    
    async def delete_text_element(self, project_id: str, text_id: str) -> bool:
        """Delete text element"""
        await self.db.text_elements.delete_one({"text_id": text_id})
        await self.db.video_projects.update_one(
            {"project_id": project_id},
            {"$pull": {"text_elements": text_id}}
        )
        
        return True
    
    # ==================== STICKER OPERATIONS ====================
    
    async def add_sticker(
        self,
        project_id: str,
        sticker_url: str,
        start_time_ms: int,
        end_time_ms: int,
        position_x: float = 0.5,
        position_y: float = 0.5,
        scale: float = 1.0
    ) -> Optional[StickersElement]:
        """Add sticker/emoji to video"""
        sticker = StickersElement(
            project_id=project_id,
            sticker_url=sticker_url,
            start_time_ms=start_time_ms,
            end_time_ms=end_time_ms,
            position_x=position_x,
            position_y=position_y,
            scale=scale
        )
        
        await self.db.stickers.insert_one(sticker.dict())
        
        # Add to project
        await self.db.video_projects.update_one(
            {"project_id": project_id},
            {"$push": {"stickers": sticker.sticker_id}}
        )
        
        return sticker
    
    async def delete_sticker(self, project_id: str, sticker_id: str) -> bool:
        """Delete sticker"""
        await self.db.stickers.delete_one({"sticker_id": sticker_id})
        await self.db.video_projects.update_one(
            {"project_id": project_id},
            {"$pull": {"stickers": sticker_id}}
        )
        
        return True
    
    # ==================== EXPORT & RENDERING ====================
    
    async def export_video(
        self,
        project_id: str,
        user_id: str,
        resolution: ResolutionType = ResolutionType.FHD,
        include_watermark: bool = False
    ) -> Optional[Dict]:
        """Start video rendering/export job"""
        project = await self.get_project(project_id, user_id)
        if not project:
            return None
        
        # Update project status
        await self.update_project(project_id, user_id, {
            "status": "rendering",
            "progress_percentage": 0
        })
        
        # In production, this would queue a job for a background worker
        # For now, returning export info
        
        export_info = {
            "export_id": str(uuid.uuid4()),
            "project_id": project_id,
            "resolution": resolution,
            "status": "queued",
            "estimated_time_seconds": 120,
            "created_at": datetime.utcnow().isoformat()
        }
        
        await self.db.exports.insert_one(export_info)
        
        return export_info
    
    async def get_export_progress(self, export_id: str) -> Optional[Dict]:
        """Get export/rendering progress"""
        export = await self.db.exports.find_one({"export_id": export_id})
        return export if export else None
    
    # ==================== TEMPLATES & PRESETS ====================
    
    async def get_effect_presets(self) -> List[Dict]:
        """Get available effect presets"""
        return [
            {
                "name": "Cinematic",
                "effects": [
                    {"type": EffectType.BRIGHTNESS, "value": 0.1},
                    {"type": EffectType.CONTRAST, "value": 0.3},
                    {"type": EffectType.SATURATION, "value": 0.2}
                ]
            },
            {
                "name": "Vintage",
                "effects": [
                    {"type": EffectType.SEPIA, "value": 0.5},
                    {"type": EffectType.SATURATION, "value": -0.3}
                ]
            },
            {
                "name": "Vibrant",
                "effects": [
                    {"type": EffectType.SATURATION, "value": 0.5},
                    {"type": EffectType.CONTRAST, "value": 0.2}
                ]
            }
        ]
    
    async def get_transition_templates(self) -> List[Dict]:
        """Get available transitions"""
        return [
            {"name": "Fade", "type": TransitionType.FADE, "duration_ms": 300},
            {"name": "Slide Left", "type": TransitionType.SLIDE_LEFT, "duration_ms": 400},
            {"name": "Zoom", "type": TransitionType.ZOOM, "duration_ms": 350},
            {"name": "Blur", "type": TransitionType.BLUR, "duration_ms": 300},
        ]
    
    async def get_music_library(self, skip: int = 0, limit: int = 20) -> List[Dict]:
        """Get royalty-free music library"""
        # This would fetch from a music provider API (Epidemic Sound, Artlist, etc.)
        # Placeholder implementation
        
        return [
            {
                "id": "music_1",
                "title": "Uplifting Background",
                "artist": "Music Provider",
                "duration_ms": 180000,
                "tags": ["uplifting", "background"],
                "preview_url": "https://example.com/preview.mp3"
            }
        ]

# Export service
__all__ = [
    'VideoEditorService',
    'VideoProject', 'VideoClip', 'Segment', 'Subtitle', 'AudioTrack',
    'TextElement', 'StickersElement',
    'EffectType', 'TransitionType', 'FilterType', 'AudioType',
    'TextEffect', 'SubtitleType', 'AspectRatio', 'ResolutionType',
    'FFmpegService', 'S3VideoService'
]
