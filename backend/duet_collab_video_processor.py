"""
Duet & Collab Video Processing Worker
FFmpeg-based video processing, effects rendering, and export
"""

import os
import json
import subprocess
import logging
from typing import Dict, List, Optional
from pathlib import Path
import asyncio
from datetime import datetime
import boto3

import ffmpeg

logger = logging.getLogger(__name__)


class VideoProcessor:
    """Handles video processing for clips and exports"""
    
    EFFECTS_CONFIG = {
        "blur": {"filter": "boxblur=100:1"},
        "brightness": {"filter": "eq=brightness={intensity}"},
        "contrast": {"filter": "eq=contrast={intensity}"},
        "saturate": {"filter": "eq=saturation={intensity}"},
        "grayscale": {"filter": "format=gray"},
        "sepia": {"filter": "colorchannelmixer=.393:.769:.189:0:.349:.686:.168:0:.272:.534:.131"},
        "glow": {"filter": "split=2[main][blur];[blur]boxblur=50[blur];[main][blur]overlay=0:0"},
        "glitch": {"filter": "select=random(1),split=2[a][b];[a]crop=iw/3:ih:0:0[a1];[b]crop=iw/3:ih:iw/3:0[b1];[a1][b1]concat=n=2:v=1[out]"},
        "vignette": {"filter": "vignette=0.5"},
        "shake": {"filter": "split=2[a][b];[a]crop=iw:ih-10:0:0[a1];[b]pad=iw:ih:0:5[b1];[a1][b1]overlay=0:rh"},
        "zoom": {"filter": "scale=iw*{intensity}:ih*{intensity}"},
        "particles": {"filter": "lut=g='if(isnan(prev_calculated_g),g,prev_calculated_g)':y='if(isnan(prev_calculated_y),y,prev_calculated_y)'"}
    }
    
    def __init__(self):
        self.s3_client = boto3.client('s3')
        self.bucket_name = os.getenv('AWS_S3_BUCKET', 'gaaius-duet-videos')
        self.temp_dir = Path("/tmp/duet_processing")
        self.temp_dir.mkdir(exist_ok=True)

    async def process_uploaded_clip(self, clip_id: str, input_path: str) -> Dict[str, str]:
        """Process uploaded clip: transcode, create thumbnail, optimize"""
        logger.info(f"Processing clip: {clip_id}")
        
        try:
            temp_clip = self.temp_dir / f"{clip_id}_processed.mp4"
            thumbnail_path = self.temp_dir / f"{clip_id}_thumb.jpg"
            
            # Transcode to standard format
            await self._transcode_video(input_path, str(temp_clip))
            
            # Generate thumbnail
            await self._generate_thumbnail(str(temp_clip), str(thumbnail_path))
            
            # Upload to S3
            clip_url = await self._upload_to_s3(str(temp_clip), f"clips/{clip_id}/video.mp4")
            thumb_url = await self._upload_to_s3(str(thumbnail_path), f"clips/{clip_id}/thumbnail.jpg")
            
            # Cleanup
            temp_clip.unlink()
            thumbnail_path.unlink()
            
            logger.info(f"Clip {clip_id} processed successfully")
            
            return {
                "clip_id": clip_id,
                "clip_url": clip_url,
                "thumbnail_url": thumb_url,
                "processed_at": datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error processing clip {clip_id}: {str(e)}")
            raise

    async def apply_effects(self, clip_id: str, clip_url: str, effects: List[Dict]) -> str:
        """Apply effects to clip"""
        logger.info(f"Applying {len(effects)} effects to clip {clip_id}")
        
        try:
            # Download clip
            input_path = self.temp_dir / f"{clip_id}_input.mp4"
            await self._download_from_s3(clip_url, str(input_path))
            
            # Build filter chain
            filter_chain = self._build_filter_chain(effects)
            
            output_path = self.temp_dir / f"{clip_id}_effected.mp4"
            
            # Apply effects
            stream = ffmpeg.input(str(input_path))
            stream = ffmpeg.filter(stream, filter_chain)
            stream = ffmpeg.output(stream, str(output_path))
            
            await self._run_ffmpeg(stream)
            
            # Upload result
            result_url = await self._upload_to_s3(
                str(output_path),
                f"clips/{clip_id}/effected.mp4"
            )
            
            # Cleanup
            input_path.unlink()
            output_path.unlink()
            
            logger.info(f"Effects applied to clip {clip_id}")
            return result_url
        
        except Exception as e:
            logger.error(f"Error applying effects to {clip_id}: {str(e)}")
            raise

    async def export_session(self, session_id: str, clips: List[Dict], 
                           export_config: Dict, progress_callback=None) -> str:
        """Export complete duet session as video"""
        logger.info(f"Exporting session {session_id} with {len(clips)} clips")
        
        try:
            # Download all clips
            clip_paths = []
            for i, clip in enumerate(clips):
                clip_path = self.temp_dir / f"{session_id}_clip_{i}.mp4"
                await self._download_from_s3(clip["url"], str(clip_path))
                clip_paths.append(str(clip_path))
            
            if progress_callback:
                await progress_callback(10)
            
            # Concatenate clips
            concat_path = self.temp_dir / f"{session_id}_concat.mp4"
            await self._concatenate_videos(clip_paths, str(concat_path))
            
            if progress_callback:
                await progress_callback(40)
            
            # Apply quality settings
            output_format = export_config.get("format", "mp4")
            quality = export_config.get("quality", "high")
            
            final_path = self.temp_dir / f"{session_id}_final.{output_format}"
            
            await self._encode_with_quality(
                str(concat_path),
                str(final_path),
                quality
            )
            
            if progress_callback:
                await progress_callback(80)
            
            # Add intro/credits if requested
            if export_config.get("include_intro") or export_config.get("include_credits"):
                final_path = await self._add_intro_credits(
                    str(final_path),
                    export_config
                )
            
            if progress_callback:
                await progress_callback(90)
            
            # Upload final video
            export_url = await self._upload_to_s3(
                str(final_path),
                f"exports/{session_id}/video.{output_format}"
            )
            
            if progress_callback:
                await progress_callback(100)
            
            # Cleanup
            for path in clip_paths:
                Path(path).unlink()
            concat_path.unlink()
            final_path.unlink()
            
            logger.info(f"Session {session_id} exported successfully: {export_url}")
            return export_url
        
        except Exception as e:
            logger.error(f"Error exporting session {session_id}: {str(e)}")
            raise

    async def _transcode_video(self, input_path: str, output_path: str):
        """Transcode video to standard format"""
        stream = ffmpeg.input(input_path)
        stream = ffmpeg.output(
            stream,
            output_path,
            codec_video='h264',
            codec_audio='aac',
            bitrate_video='5000k',
            bitrate_audio='128k'
        )
        await self._run_ffmpeg(stream)

    async def _generate_thumbnail(self, video_path: str, thumbnail_path: str, 
                                  timestamp: str = "00:00:01"):
        """Generate thumbnail from video"""
        stream = ffmpeg.input(video_path, ss=timestamp)
        stream = ffmpeg.output(stream, thumbnail_path, vframes=1)
        await self._run_ffmpeg(stream)

    async def _concatenate_videos(self, video_paths: List[str], output_path: str):
        """Concatenate multiple videos"""
        # Create concat file
        concat_file = self.temp_dir / "concat.txt"
        with open(concat_file, 'w') as f:
            for path in video_paths:
                f.write(f"file '{path}'\n")
        
        stream = ffmpeg.input(str(concat_file), format='concat', safe=0)
        stream = ffmpeg.output(stream, output_path, c='copy')
        await self._run_ffmpeg(stream)
        
        concat_file.unlink()

    async def _encode_with_quality(self, input_path: str, output_path: str, quality: str):
        """Encode video with specified quality"""
        quality_settings = {
            "low": {
                "bitrate_video": "1000k",
                "bitrate_audio": "64k",
                "preset": "faster"
            },
            "medium": {
                "bitrate_video": "3000k",
                "bitrate_audio": "128k",
                "preset": "medium"
            },
            "high": {
                "bitrate_video": "8000k",
                "bitrate_audio": "192k",
                "preset": "slower"
            },
            "ultra": {
                "bitrate_video": "15000k",
                "bitrate_audio": "256k",
                "preset": "veryslow"
            }
        }
        
        settings = quality_settings.get(quality, quality_settings["high"])
        
        stream = ffmpeg.input(input_path)
        stream = ffmpeg.output(
            stream,
            output_path,
            codec_video='h264',
            codec_audio='aac',
            **settings
        )
        await self._run_ffmpeg(stream)

    async def _add_intro_credits(self, video_path: str, config: Dict) -> str:
        """Add intro and/or credits to video"""
        # This would use FFmpeg filter_complex with text/image overlays
        # Simplified version - in production would create actual intro/credits
        logger.info(f"Adding intro/credits to video")
        return video_path

    def _build_filter_chain(self, effects: List[Dict]) -> str:
        """Build FFmpeg filter chain from effects list"""
        filters = []
        
        for effect in effects:
            effect_type = effect.get("type")
            intensity = effect.get("intensity", 1.0)
            
            if effect_type in self.EFFECTS_CONFIG:
                filter_str = self.EFFECTS_CONFIG[effect_type]["filter"]
                filter_str = filter_str.format(intensity=intensity)
                filters.append(filter_str)
        
        # Combine filters with comma
        return ",".join(filters) if filters else "null"

    async def _run_ffmpeg(self, stream):
        """Run FFmpeg command asynchronously"""
        try:
            # Get FFmpeg command
            cmd = ffmpeg.compile(stream)
            
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: subprocess.run(cmd, check=True, capture_output=True)
            )
        
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg error: {e.stderr.decode()}")
            raise Exception(f"FFmpeg processing failed: {e.stderr.decode()}")

    async def _upload_to_s3(self, file_path: str, s3_key: str) -> str:
        """Upload file to S3"""
        try:
            self.s3_client.upload_file(
                file_path,
                self.bucket_name,
                s3_key
            )
            
            url = f"s3://{self.bucket_name}/{s3_key}"
            logger.info(f"Uploaded {file_path} to {url}")
            return url
        
        except Exception as e:
            logger.error(f"S3 upload error: {str(e)}")
            raise

    async def _download_from_s3(self, s3_url: str, local_path: str):
        """Download file from S3"""
        try:
            # Parse S3 URL
            # Format: s3://bucket/key
            parts = s3_url.replace("s3://", "").split("/", 1)
            bucket = parts[0]
            key = parts[1]
            
            self.s3_client.download_file(bucket, key, local_path)
            logger.info(f"Downloaded {s3_url} to {local_path}")
        
        except Exception as e:
            logger.error(f"S3 download error: {str(e)}")
            raise


# Global processor instance
video_processor = VideoProcessor()


# ==================== BACKGROUND TASK HANDLERS ====================

async def process_clip_task(clip_id: str, input_path: str, 
                           service, progress_callback=None):
    """Background task to process uploaded clip"""
    try:
        if progress_callback:
            await progress_callback(10, "Starting processing")
        
        result = await video_processor.process_uploaded_clip(clip_id, input_path)
        
        if progress_callback:
            await progress_callback(100, "Processing complete")
        
        # Update clip status in database
        from duet_collab_service import ClipStatus
        await service.update_clip_status(clip_id, ClipStatus.READY)
    
    except Exception as e:
        logger.error(f"Error in clip processing task: {str(e)}")
        from duet_collab_service import ClipStatus
        await service.update_clip_status(clip_id, ClipStatus.ERROR)


async def apply_effects_task(clip_id: str, clip_url: str, effects: List[Dict],
                            service, ws_manager):
    """Background task to apply effects to clip"""
    try:
        result_url = await video_processor.apply_effects(clip_id, clip_url, effects)
        
        # Notify via WebSocket
        session_id = effects[0].get("session_id") if effects else None
        if session_id:
            await ws_manager.notify_effect_applied(
                session_id,
                clip_id,
                {"url": result_url, "applied_at": datetime.utcnow().isoformat()}
            )
    
    except Exception as e:
        logger.error(f"Error in effects application task: {str(e)}")


async def export_session_task(export_id: str, session_id: str, clips: List[Dict],
                             export_config: Dict, service, ws_manager):
    """Background task to export session"""
    try:
        async def progress_callback(progress: int, message: str = ""):
            await service.update_export_progress(export_id, progress)
            await ws_manager.notify_export_progress(session_id, export_id, progress)
        
        # Download clips and process
        video_url = await video_processor.export_session(
            session_id,
            clips,
            export_config,
            progress_callback
        )
        
        # Mark as complete
        await service.mark_export_complete(export_id, video_url)
        
        # Notify via WebSocket
        await ws_manager.notify_export_completed(session_id, export_id, video_url)
    
    except Exception as e:
        logger.error(f"Error in export task: {str(e)}")
        await service.exports_collection.update_one(
            {"export_id": export_id},
            {"$set": {"status": "failed", "error": str(e)}}
        )
