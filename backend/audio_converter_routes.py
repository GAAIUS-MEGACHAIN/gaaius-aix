"""
Audio Converter API Routes
Endpoints for audio format conversion with quality options
"""

import logging
import os
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from backend.audio_converter_service import (
    get_conversion_manager,
    AudioFormat,
    AudioBitrate,
)

logger = logging.getLogger(__name__)
router = APIRouter(tags=["audio-converter"])


# Request/Response Models
class ConversionRequest(BaseModel):
    """Audio conversion request"""
    user_id: str
    audio_file_id: str
    target_format: str  # mp3, wav, flac, ogg, m4a, aac, opus, wma
    target_bitrate: str = "256"  # 64, 128, 192, 256, 320, lossless


class AudioFileResponse(BaseModel):
    """Audio file response"""
    id: str
    filename: str
    format: str
    file_size: int
    duration: Optional[float]
    bitrate: Optional[str]
    sample_rate: Optional[int]
    channels: Optional[int]
    uploaded_at: str


class ConvertedFileResponse(BaseModel):
    """Converted file response"""
    id: str
    original_file_id: str
    filename: str
    format: str
    bitrate: str
    file_size: int
    duration: Optional[float]
    converted_at: str


# API Endpoints

@router.post("/audio/upload")
async def upload_audio(
    user_id: str,
    file: UploadFile = File(...),
) -> AudioFileResponse:
    """
    Upload audio file for conversion
    
    Supported formats: MP3, WAV, FLAC, OGG, M4A, AAC, WMA, OPUS
    """
    try:
        manager = get_conversion_manager()
        
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        # Sanitize filename to prevent path traversal (CWE-23)
        # Remove any directory separators and parent directory references
        safe_filename = os.path.basename(file.filename)
        if not safe_filename or safe_filename.startswith('.'):
            raise HTTPException(status_code=400, detail="Invalid filename")
        
        # Save uploaded file temporarily
        upload_dir = os.path.join(os.getcwd(), "temp_audio")
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, safe_filename)
        
        # Verify the resolved path is still within upload_dir (defense in depth)
        resolved_path = os.path.abspath(file_path)
        resolved_upload_dir = os.path.abspath(upload_dir)
        if not resolved_path.startswith(resolved_upload_dir):
            raise HTTPException(status_code=400, detail="Invalid file path")
        
        # Save file
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Register uploaded file
        audio_file = await manager.upload_audio(user_id, file_path)
        
        if not audio_file:
            raise HTTPException(status_code=400, detail="Failed to process audio file")
        
        logger.info(f"User {user_id} uploaded audio: {safe_filename}")
        
        return AudioFileResponse(
            id=audio_file.id,
            filename=audio_file.filename,
            format=audio_file.original_format,
            file_size=audio_file.file_size,
            duration=audio_file.duration,
            bitrate=audio_file.bitrate,
            sample_rate=audio_file.sample_rate,
            channels=audio_file.channels,
            uploaded_at=audio_file.uploaded_at,
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/audio/convert")
async def convert_audio(request: ConversionRequest) -> ConvertedFileResponse:
    """
    Convert uploaded audio to target format and bitrate
    
    Supported formats:
    - MP3 (64-320 kbps)
    - WAV (lossless)
    - FLAC (lossless)
    - OGG (64-256 kbps)
    - M4A/AAC (64-320 kbps)
    - OPUS (64-256 kbps)
    - WMA (64-320 kbps)
    """
    try:
        manager = get_conversion_manager()
        
        # Validate format
        try:
            target_format = AudioFormat(request.target_format)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported format: {request.target_format}"
            )
        
        # Validate bitrate
        try:
            target_bitrate = AudioBitrate(request.target_bitrate)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported bitrate: {request.target_bitrate}"
            )
        
        # Convert
        converted_file, error = await manager.convert_audio(
            request.user_id,
            request.audio_file_id,
            target_format,
            target_bitrate,
        )
        
        if error:
            raise HTTPException(status_code=400, detail=error)
        
        if not converted_file:
            raise HTTPException(status_code=500, detail="Conversion failed")
        
        logger.info(f"Converted audio for user {request.user_id}")
        
        return ConvertedFileResponse(
            id=converted_file.id,
            original_file_id=converted_file.original_file_id,
            filename=converted_file.filename,
            format=converted_file.format,
            bitrate=converted_file.bitrate,
            file_size=converted_file.file_size,
            duration=converted_file.duration,
            converted_at=converted_file.converted_at,
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Conversion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/audio/file/{file_id}")
async def get_audio_file(file_id: str) -> AudioFileResponse:
    """Get uploaded audio file info"""
    try:
        manager = get_conversion_manager()
        audio_file = manager.get_uploaded_file(file_id)
        
        if not audio_file:
            raise HTTPException(status_code=404, detail="Audio file not found")
        
        return AudioFileResponse(
            id=audio_file.id,
            filename=audio_file.filename,
            format=audio_file.original_format,
            file_size=audio_file.file_size,
            duration=audio_file.duration,
            bitrate=audio_file.bitrate,
            sample_rate=audio_file.sample_rate,
            channels=audio_file.channels,
            uploaded_at=audio_file.uploaded_at,
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/audio/converted/{file_id}")
async def get_converted_file(file_id: str) -> ConvertedFileResponse:
    """Get converted audio file info"""
    try:
        manager = get_conversion_manager()
        converted_file = manager.get_converted_file(file_id)
        
        if not converted_file:
            raise HTTPException(status_code=404, detail="Converted file not found")
        
        return ConvertedFileResponse(
            id=converted_file.id,
            original_file_id=converted_file.original_file_id,
            filename=converted_file.filename,
            format=converted_file.format,
            bitrate=converted_file.bitrate,
            file_size=converted_file.file_size,
            duration=converted_file.duration,
            converted_at=converted_file.converted_at,
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/audio/history/{user_id}")
async def get_conversion_history(user_id: str) -> List[ConvertedFileResponse]:
    """Get all conversions for user"""
    try:
        manager = get_conversion_manager()
        conversions = manager.get_user_conversions(user_id)
        
        return [
            ConvertedFileResponse(
                id=c.id,
                original_file_id=c.original_file_id,
                filename=c.filename,
                format=c.format,
                bitrate=c.bitrate,
                file_size=c.file_size,
                duration=c.duration,
                converted_at=c.converted_at,
            )
            for c in conversions
        ]
    
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/audio/delete/{file_id}")
async def delete_converted_file(file_id: str) -> dict:
    """Delete converted audio file"""
    try:
        manager = get_conversion_manager()
        
        if not manager.delete_converted_file(file_id):
            raise HTTPException(status_code=404, detail="File not found")
        
        return {"status": "success", "message": "File deleted"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/audio/formats")
async def get_supported_formats() -> dict:
    """Get list of supported formats and bitrates"""
    return {
        "formats": [
            {"name": "MP3", "value": "mp3", "lossless": False},
            {"name": "WAV", "value": "wav", "lossless": True},
            {"name": "FLAC", "value": "flac", "lossless": True},
            {"name": "OGG Vorbis", "value": "ogg", "lossless": False},
            {"name": "M4A/AAC", "value": "m4a", "lossless": False},
            {"name": "AAC", "value": "aac", "lossless": False},
            {"name": "Opus", "value": "opus", "lossless": False},
            {"name": "WMA", "value": "wma", "lossless": False},
        ],
        "bitrates": [
            {"label": "Phone (64 kbps)", "value": "64", "quality": "low"},
            {"label": "Good (128 kbps)", "value": "128", "quality": "good"},
            {"label": "Very Good (192 kbps)", "value": "192", "quality": "very_good"},
            {"label": "Excellent (256 kbps)", "value": "256", "quality": "excellent"},
            {"label": "Highest (320 kbps)", "value": "320", "quality": "highest"},
            {"label": "Lossless", "value": "lossless", "quality": "lossless"},
        ],
    }


@router.get("/audio/health")
async def health_check() -> dict:
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "audio-converter",
        "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
    }
