"""
Audio Converter Service
Professional audio format conversion (MP3, WAV, FLAC, OGG, M4A, AAC, WMA, OPUS)
Uses FFmpeg for high-quality, fast conversions
"""

import os
import logging
import asyncio
import subprocess
import uuid
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Optional, Dict, List, Tuple
from datetime import datetime
import mimetypes

logger = logging.getLogger(__name__)


class AudioFormat(str, Enum):
    """Supported audio formats"""
    MP3 = "mp3"
    WAV = "wav"
    FLAC = "flac"
    OGG = "ogg"
    M4A = "m4a"
    AAC = "aac"
    OPUS = "opus"
    WMA = "wma"


class AudioBitrate(str, Enum):
    """Audio quality/bitrate options"""
    PHONE = "64"        # 64 kbps (voice, phone)
    LOW = "128"         # 128 kbps (good quality)
    MEDIUM = "192"      # 192 kbps (very good)
    HIGH = "256"        # 256 kbps (excellent)
    VERY_HIGH = "320"   # 320 kbps (highest MP3)
    LOSSLESS = "lossless"  # For FLAC, WAV, ALAC


@dataclass
class AudioFile:
    """Audio file metadata"""
    id: str
    filename: str
    original_format: str
    file_size: int  # Bytes
    duration: Optional[float] = None  # Seconds
    bitrate: Optional[str] = None  # kbps
    sample_rate: Optional[int] = None  # Hz
    channels: Optional[int] = None  # Mono=1, Stereo=2
    uploaded_at: str = None


@dataclass
class ConvertedFile:
    """Converted audio file metadata"""
    id: str
    original_file_id: str
    filename: str
    format: str
    bitrate: str
    file_size: int
    duration: Optional[float]
    converted_at: str


class AudioConverter:
    """Core audio conversion service using FFmpeg"""
    
    def __init__(self, ffmpeg_path: str = "ffmpeg"):
        """Initialize converter with ffmpeg binary"""
        self.ffmpeg = ffmpeg_path
        self.temp_dir = os.path.join(os.getcwd(), "temp_audio")
        self.output_dir = os.path.join(os.getcwd(), "converted_audio")
        
        # Create directories
        os.makedirs(self.temp_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Format codec mappings
        self.codec_map = {
            AudioFormat.MP3: {"codec": "libmp3lame", "ext": "mp3", "container": "mp3"},
            AudioFormat.WAV: {"codec": "pcm_s16le", "ext": "wav", "container": "wav"},
            AudioFormat.FLAC: {"codec": "flac", "ext": "flac", "container": "flac"},
            AudioFormat.OGG: {"codec": "libvorbis", "ext": "ogg", "container": "ogg"},
            AudioFormat.M4A: {"codec": "aac", "ext": "m4a", "container": "ipod"},
            AudioFormat.AAC: {"codec": "aac", "ext": "aac", "container": "aac"},
            AudioFormat.OPUS: {"codec": "libopus", "ext": "opus", "container": "opus"},
            AudioFormat.WMA: {"codec": "wmav2", "ext": "wma", "container": "asf"},
        }
        
        logger.info(f"AudioConverter initialized with ffmpeg at {ffmpeg_path}")
    
    async def get_file_info(self, file_path: str) -> Optional[AudioFile]:
        """Get audio file metadata using ffprobe"""
        try:
            if not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                return None
            
            # Use ffprobe to get file info
            cmd = [
                "ffprobe",
                "-v", "error",
                "-show_entries", "format=duration,bit_rate;stream=channels,sample_rate",
                "-of", "default=noprint_wrappers=1:nokey=1:nokey_type=1",
                file_path
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=30)
            
            info_lines = stdout.decode().strip().split('\n')
            
            file_size = os.path.getsize(file_path)
            filename = os.path.basename(file_path)
            original_format = self._detect_format(filename)
            
            duration = None
            bitrate = None
            sample_rate = None
            channels = None
            
            try:
                if len(info_lines) >= 4:
                    duration = float(info_lines[0]) if info_lines[0] != "N/A" else None
                    br = info_lines[1] if info_lines[1] != "N/A" else "0"
                    bitrate = str(int(int(br) / 1000)) if br != "0" else None
                    sample_rate = int(info_lines[2])
                    channels = int(info_lines[3])
            except (ValueError, IndexError):
                pass
            
            audio_file = AudioFile(
                id=f"audio_{uuid.uuid4().hex[:12]}",
                filename=filename,
                original_format=original_format,
                file_size=file_size,
                duration=duration,
                bitrate=bitrate,
                sample_rate=sample_rate,
                channels=channels,
                uploaded_at=datetime.utcnow().isoformat() + "Z",
            )
            
            logger.info(f"Analyzed audio: {filename} ({duration}s, {channels}ch, {sample_rate}Hz)")
            return audio_file
        
        except Exception as e:
            logger.error(f"Error getting file info: {e}")
            return None
    
    async def convert(
        self,
        input_path: str,
        output_format: AudioFormat,
        output_bitrate: AudioBitrate = AudioBitrate.HIGH,
        output_filename: Optional[str] = None,
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Convert audio file to specified format
        
        Args:
            input_path: Path to input audio file
            output_format: Target format
            output_bitrate: Target quality/bitrate
            output_filename: Optional custom output filename
        
        Returns:
            Tuple of (output_path, error_message)
        """
        try:
            if not os.path.exists(input_path):
                return None, f"Input file not found"
            
            # Determine output filename
            if not output_filename:
                base_name = os.path.splitext(os.path.basename(input_path))[0]
                extension = self.codec_map[output_format]["ext"]
                output_filename = f"{base_name}.{extension}"
            
            output_path = os.path.join(self.output_dir, output_filename)
            
            # Build ffmpeg command
            codec_info = self.codec_map[output_format]
            
            cmd = ["ffmpeg", "-i", input_path, "-y", "-loglevel", "error"]
            
            # Add audio codec
            cmd.extend(["-c:a", codec_info["codec"]])
            
            # Add bitrate (skip for lossless formats)
            if output_bitrate != AudioBitrate.LOSSLESS:
                cmd.extend(["-b:a", f"{output_bitrate.value}k"])
            
            # Format-specific options
            if output_format == AudioFormat.MP3:
                cmd.extend(["-q:a", "4"])  # VBR quality (0-9, 4=high)
            elif output_format == AudioFormat.FLAC:
                cmd.extend(["-compression_level", "8"])
            elif output_format == AudioFormat.OPUS:
                cmd.extend(["-b:a", f"{output_bitrate.value}k"])
            
            # Output file
            cmd.append(output_path)
            
            # Run conversion
            logger.info(f"Converting to {output_format.value} ({output_bitrate.value}kbps)")
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            _, stderr = await asyncio.wait_for(process.communicate(), timeout=300)
            
            if process.returncode != 0:
                error = stderr.decode().strip()
                logger.error(f"FFmpeg error: {error}")
                return None, "Conversion failed"
            
            if os.path.exists(output_path):
                output_size = os.path.getsize(output_path)
                logger.info(f"Conversion successful: {output_filename} ({output_size} bytes)")
                return output_path, None
            else:
                return None, "Output file not created"
        
        except asyncio.TimeoutError:
            return None, "Conversion timeout (>5 minutes)"
        except Exception as e:
            logger.error(f"Conversion error: {e}")
            return None, str(e)
    
    async def batch_convert(
        self,
        input_paths: List[str],
        output_format: AudioFormat,
        output_bitrate: AudioBitrate = AudioBitrate.HIGH,
    ) -> Dict[str, Dict]:
        """Convert multiple audio files"""
        results = {}
        
        for input_path in input_paths:
            filename = os.path.basename(input_path)
            output_path, error = await self.convert(
                input_path,
                output_format,
                output_bitrate
            )
            
            results[filename] = {
                "success": output_path is not None,
                "output_path": output_path,
                "error": error,
                "output_size": os.path.getsize(output_path) if output_path else None,
            }
        
        return results
    
    def _detect_format(self, filename: str) -> str:
        """Detect audio format from filename"""
        _, ext = os.path.splitext(filename)
        ext = ext.lstrip(".").lower()
        
        format_map = {
            "mp3": "mp3", "wav": "wav", "flac": "flac", "ogg": "ogg",
            "m4a": "m4a", "aac": "aac", "opus": "opus", "wma": "wma",
        }
        
        return format_map.get(ext, ext)


class ConversionManager:
    """Manages conversion jobs and history"""
    
    def __init__(self, converter: Optional[AudioConverter] = None):
        """Initialize manager"""
        self.converter = converter or AudioConverter()
        self.uploaded_files: Dict[str, AudioFile] = {}
        self.converted_files: Dict[str, ConvertedFile] = {}
        self.user_conversions: Dict[str, List[str]] = {}  # user_id -> conversion_ids
        logger.info("ConversionManager initialized")
    
    async def upload_audio(
        self,
        user_id: str,
        file_path: str,
    ) -> Optional[AudioFile]:
        """Register uploaded audio file"""
        try:
            audio_file = await self.converter.get_file_info(file_path)
            
            if not audio_file:
                return None
            
            self.uploaded_files[audio_file.id] = audio_file
            
            if user_id not in self.user_conversions:
                self.user_conversions[user_id] = []
            
            logger.info(f"User {user_id} uploaded audio: {audio_file.filename}")
            return audio_file
        
        except Exception as e:
            logger.error(f"Error uploading audio: {e}")
            return None
    
    async def convert_audio(
        self,
        user_id: str,
        audio_file_id: str,
        target_format: AudioFormat,
        target_bitrate: AudioBitrate = AudioBitrate.HIGH,
    ) -> Tuple[Optional[ConvertedFile], Optional[str]]:
        """Convert audio file"""
        try:
            if audio_file_id not in self.uploaded_files:
                return None, "Audio file not found"
            
            audio_file = self.uploaded_files[audio_file_id]
            
            # Create temp file path
            input_path = os.path.join(os.getcwd(), "temp_audio", audio_file.filename)
            if not os.path.exists(input_path):
                return None, "Input file not accessible"
            
            # Convert
            output_path, error = await self.converter.convert(
                input_path,
                target_format,
                target_bitrate
            )
            
            if error:
                return None, error
            
            # Create converted file record
            output_size = os.path.getsize(output_path) if output_path else 0
            
            converted_file = ConvertedFile(
                id=f"conv_{uuid.uuid4().hex[:12]}",
                original_file_id=audio_file_id,
                filename=os.path.basename(output_path),
                format=target_format.value,
                bitrate=target_bitrate.value,
                file_size=output_size,
                duration=audio_file.duration,
                converted_at=datetime.utcnow().isoformat() + "Z",
            )
            
            self.converted_files[converted_file.id] = converted_file
            self.user_conversions[user_id].append(converted_file.id)
            
            logger.info(f"Converted {audio_file.filename} to {target_format.value}")
            return converted_file, None
        
        except Exception as e:
            logger.error(f"Conversion error: {e}")
            return None, str(e)
    
    def get_uploaded_file(self, file_id: str) -> Optional[AudioFile]:
        """Get uploaded audio file info"""
        return self.uploaded_files.get(file_id)
    
    def get_converted_file(self, file_id: str) -> Optional[ConvertedFile]:
        """Get converted audio file info"""
        return self.converted_files.get(file_id)
    
    def get_user_conversions(self, user_id: str) -> List[ConvertedFile]:
        """Get all conversions for user"""
        conversion_ids = self.user_conversions.get(user_id, [])
        return [self.converted_files[cid] for cid in conversion_ids if cid in self.converted_files]
    
    def delete_converted_file(self, file_id: str) -> bool:
        """Delete converted audio file"""
        if file_id in self.converted_files:
            del self.converted_files[file_id]
            logger.info(f"Deleted converted file: {file_id}")
            return True
        return False


# Global singleton
_conversion_manager: Optional[ConversionManager] = None


def init_audio_converter_service() -> ConversionManager:
    """Initialize audio converter service"""
    global _conversion_manager
    _conversion_manager = ConversionManager()
    logger.info("Audio converter service initialized")
    return _conversion_manager


def get_conversion_manager() -> ConversionManager:
    """Get conversion manager instance"""
    global _conversion_manager
    if _conversion_manager is None:
        _conversion_manager = ConversionManager()
    return _conversion_manager
