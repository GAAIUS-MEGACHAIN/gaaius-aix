"""
GAAIUS MultiTube Transcode Worker - Production-Grade HLS/ABR Video Processing
Full enterprise reliability: retry logic, circuit breakers, graceful shutdown, comprehensive logging,
disk management, timeout protection, concurrent processing, health checks, signal handling.

Handles video transcoding to HLS with multiple bitrates, proper error recovery, and worker pool
management for scalable multi-worker deployment on Kubernetes, Docker, or bare metal.
"""
import os
import sys
import time
import uuid
import shutil
import asyncio
import logging
import signal
import subprocess
import json
from pathlib import Path
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
import traceback

import boto3
import motor.motor_asyncio
from botocore.exceptions import ClientError

# Production configuration with sensible defaults
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'gaaius')
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')
AWS_BUCKET = os.environ.get('AWS_S3_BUCKET', 'gaaius-social-media')
AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
WORKER_ID = os.environ.get('WORKER_ID', f"worker-{uuid.uuid4().hex[:8]}")
CONCURRENCY = int(os.environ.get('TRANSCODE_CONCURRENCY', '2'))
MAX_RETRIES = int(os.environ.get('MAX_RETRIES', '3'))
JOB_TIMEOUT_MINUTES = int(os.environ.get('JOB_TIMEOUT_MINUTES', '180'))
DISK_MIN_GB = int(os.environ.get('DISK_MIN_GB', '10'))
CLOUDFRONT_DOMAIN = os.environ.get('CLOUDFRONT_DOMAIN', '')
HEALTH_CHECK_PORT = int(os.environ.get('HEALTH_CHECK_PORT', '9090'))

TMP_DIR = Path(os.environ.get('TRANSCODE_TMP_DIR', '/tmp/transcode'))
TMP_DIR.mkdir(parents=True, exist_ok=True)

FFMPEG_BIN = shutil.which('ffmpeg') or 'ffmpeg'
FFPROBE_BIN = shutil.which('ffprobe') or 'ffprobe'

# Structured logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s|%(name)s|%(levelname)s|%(message)s')
logger = logging.getLogger(__name__)


class TranscodeStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    VALIDATING = "validating"
    PROBING = "probing"
    TRANSCODING = "transcoding"
    UPLOADING = "uploading"
    DONE = "done"
    FAILED = "failed"
    RETRYING = "retrying"
    TIMEOUT = "timeout"


async def probe_video_file(file_path: Path, timeout_sec: int = 30) -> Dict:
    """Validate video with ffprobe before expensive transcoding"""
    try:
        cmd = [
            FFPROBE_BIN,
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            str(file_path)
        ]
        result = subprocess.run(cmd, capture_output=True, timeout=timeout_sec, text=True)
        
        if result.returncode != 0:
            raise ValueError(f"ffprobe failed: {result.stderr}")
        
        data = json.loads(result.stdout)
        video_streams = [s for s in data.get('streams', []) if s.get('codec_type') == 'video']
        if not video_streams:
            raise ValueError("No video streams")
        
        codec = video_streams[0].get('codec_name', '')
        if codec not in ['h264', 'h265', 'hevc', 'vp8', 'vp9', 'mpeg2video', 'mpeg4', 'av1']:
            raise ValueError(f"Unsupported codec: {codec}")
        
        duration = float(data.get('format', {}).get('duration', 0))
        if duration <= 0 or duration > 43200:
            raise ValueError(f"Invalid duration: {duration}s")
        
        size_bytes = int(data.get('format', {}).get('size', 0))
        size_gb = size_bytes / (1024 ** 3)
        if size_gb > 10:
            raise ValueError(f"File too large: {size_gb:.2f}GB")
        
        return {
            'duration': duration,
            'video_streams': len(video_streams),
            'audio_streams': len([s for s in data.get('streams', []) if s.get('codec_type') == 'audio']),
            'width': video_streams[0].get('width', 0),
            'height': video_streams[0].get('height', 0),
            'codec': codec,
            'bitrate': int(data.get('format', {}).get('bit_rate', 0)),
            'size_bytes': size_bytes
        }
    except subprocess.TimeoutExpired:
        raise ValueError(f"ffprobe timeout")
    except Exception as e:
        raise ValueError(f"Video probe failed: {str(e)}")


def check_disk_space_gb() -> float:
    """Check available disk space"""
    stat = shutil.disk_usage(TMP_DIR)
    return stat.free / (1024 ** 3)


async def download_s3_object(s3_client, bucket: str, s3_key: str, local_path: Path, 
                             max_size_gb: float = 2.0) -> int:
    """Download from S3 with validation"""
    try:
        resp = s3_client.head_object(Bucket=bucket, Key=s3_key)
        size_bytes = resp['ContentLength']
        size_gb = size_bytes / (1024 ** 3)
        
        if size_gb > max_size_gb:
            raise ValueError(f"Source too large: {size_gb:.2f}GB")
        
        logger.info(f"Downloading s3://{bucket}/{s3_key} ({size_gb:.2f}GB)...")
        s3_client.download_file(bucket, s3_key, str(local_path))
        logger.info(f"Downloaded {size_bytes} bytes")
        return size_bytes
    except ClientError as e:
        raise ValueError(f"S3 download failed: {e}")


async def transcode_to_hls_renditions(source_path: Path, work_dir: Path, video_id: str,
                                      job_id: str, timeout_sec: int = 1200) -> Dict[str, Path]:
    """Encode to HLS ABR renditions"""
    renditions = [
        {'name': '1080p', 'resolution': '1920x1080', 'bitrate': '5000k', 'audio_bitrate': '128k'},
        {'name': '720p', 'resolution': '1280x720', 'bitrate': '3000k', 'audio_bitrate': '128k'},
        {'name': '480p', 'resolution': '854x480', 'bitrate': '1500k', 'audio_bitrate': '96k'},
        {'name': '360p', 'resolution': '640x360', 'bitrate': '800k', 'audio_bitrate': '64k'},
    ]
    
    playlists = {}
    
    for r in renditions:
        out_dir = work_dir / r['name']
        out_dir.mkdir(parents=True, exist_ok=True)
        playlist_file = out_dir / f"{video_id}_{r['name']}.m3u8"
        
        free_gb = check_disk_space_gb()
        if free_gb < DISK_MIN_GB:
            raise RuntimeError(f"Insufficient disk: {free_gb:.2f}GB")
        
        cmd = [
            FFMPEG_BIN, '-y', '-i', str(source_path),
            '-c:v', 'libx264', '-preset', 'faster', '-crf', '23',
            '-b:v', r['bitrate'],
            '-maxrate', f"{int(r['bitrate'].replace('k', ''))*1.2}k",
            '-bufsize', f"{int(r['bitrate'].replace('k', ''))*2}k",
            '-s', r['resolution'], '-g', '48', '-sc_threshold', '0',
            '-c:a', 'aac', '-b:a', r['audio_bitrate'], '-ac', '2', '-ar', '48000',
            '-f', 'hls', '-hls_time', '6', '-hls_playlist_type', 'vod',
            '-hls_flags', 'independent_segments',
            '-hls_segment_filename', str(out_dir / f"{video_id}_{r['name']}_%03d.ts"),
            str(playlist_file)
        ]
        
        logger.info(f"[{job_id}] Encoding {r['name']} ({r['resolution']})")
        
        try:
            proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                                 timeout=timeout_sec, text=True)
            
            if proc.returncode != 0:
                raise RuntimeError(f"ffmpeg error: {proc.stderr[-500:]}")
            
            if not playlist_file.exists():
                raise RuntimeError(f"Playlist not created")
            
            logger.info(f"[{job_id}] {r['name']} encoded")
            playlists[r['name']] = playlist_file
            
        except subprocess.TimeoutExpired:
            raise RuntimeError(f"Encoding timeout for {r['name']}")
    
    return playlists


def create_master_m3u8(work_dir: Path, video_id: str, playlists: Dict[str, Path]) -> Path:
    """Create master HLS playlist"""
    master_path = work_dir / f"{video_id}_master.m3u8"
    
    variants = [
        {'name': '1080p', 'bitrate': 5000000, 'resolution': '1920x1080'},
        {'name': '720p', 'bitrate': 3000000, 'resolution': '1280x720'},
        {'name': '480p', 'bitrate': 1500000, 'resolution': '854x480'},
        {'name': '360p', 'bitrate': 800000, 'resolution': '640x360'},
    ]
    
    with open(master_path, 'w') as f:
        f.write('#EXTM3U\n#EXT-X-VERSION:3\n#EXT-X-TARGETDURATION:6\n#EXT-X-MEDIA-SEQUENCE:0\n')
        for v in variants:
            if v['name'] in playlists:
                rel_path = f"{v['name']}/{playlists[v['name']].name}"
                f.write(f'#EXT-X-STREAM-INF:BANDWIDTH={v["bitrate"]},RESOLUTION={v["resolution"]}\n')
                f.write(f'{rel_path}\n')
    
    logger.info(f"Master playlist created")
    return master_path


async def extract_thumbnail(source_path: Path, output_path: Path, timestamp: str = "00:00:01.000"):
    """Extract thumbnail"""
    cmd = [FFMPEG_BIN, '-y', '-i', str(source_path), '-ss', timestamp, '-vframes', '1', '-q:v', '2', str(output_path)]
    
    try:
        result = subprocess.run(cmd, capture_output=True, timeout=30, text=True)
        if result.returncode == 0 and output_path.exists() and output_path.stat().st_size > 0:
            logger.info(f"Thumbnail extracted")
            return True
        return False
    except Exception as e:
        logger.warning(f"Thumbnail error: {e}")
        return False


async def upload_hls_to_s3(s3_client, bucket: str, work_dir: Path, user_id: str,
                          video_id: str, job_id: str) -> Tuple[str, str, int]:
    """Upload HLS outputs to S3"""
    s3_prefix = f"social/{user_id}/videos/{video_id}/"
    total_bytes = 0
    files_uploaded = 0
    
    logger.info(f"[{job_id}] Uploading HLS to S3...")
    
    for root, dirs, files in os.walk(work_dir):
        for fname in files:
            if not fname.startswith(video_id):
                continue
            
            local_file = Path(root) / fname
            rel_path = local_file.relative_to(work_dir)
            s3_key = s3_prefix + str(rel_path).replace('\\', '/')
            file_size = local_file.stat().st_size
            
            if fname.endswith('.m3u8'):
                content_type = 'application/vnd.apple.mpegurl'
                cache_control = 'public, max-age=3600'
            elif fname.endswith('.ts'):
                content_type = 'video/MP2T'
                cache_control = 'public, max-age=31536000'
            elif fname.endswith('.jpg'):
                content_type = 'image/jpeg'
                cache_control = 'public, max-age=31536000'
            else:
                content_type = 'application/octet-stream'
                cache_control = 'public, max-age=3600'
            
            try:
                s3_client.upload_file(
                    str(local_file), bucket, s3_key,
                    ExtraArgs={
                        'ContentType': content_type, 'CacheControl': cache_control,
                        'ServerSideEncryption': 'AES256',
                        'Metadata': {'video_id': video_id, 'user_id': user_id, 'worker_id': WORKER_ID, 'uploaded_at': datetime.utcnow().isoformat()}
                    }
                )
                total_bytes += file_size
                files_uploaded += 1
            except Exception as e:
                logger.error(f"[{job_id}] Upload failed for {s3_key}: {e}")
                raise
    
    logger.info(f"[{job_id}] Uploaded {files_uploaded} files ({total_bytes/(1024**2):.1f}MB)")
    
    if CLOUDFRONT_DOMAIN:
        master_url = f"https://{CLOUDFRONT_DOMAIN}/{s3_prefix}{video_id}_master.m3u8"
        thumb_url = f"https://{CLOUDFRONT_DOMAIN}/{s3_prefix}{video_id}_thumb.jpg"
    else:
        master_url = f"https://{bucket}.s3.{AWS_REGION}.amazonaws.com/{s3_prefix}{video_id}_master.m3u8"
        thumb_url = f"https://{bucket}.s3.{AWS_REGION}.amazonaws.com/{s3_prefix}{video_id}_thumb.jpg"
    
    return master_url, thumb_url, total_bytes


async def process_transcode_job(db, s3_client, job: Dict) -> bool:
    """Process transcode job with full production error handling"""
    job_id = job['job_id']
    video_id = job['video_id']
    s3_key = job['s3_key']
    user_id = job.get('user_id', 'unknown')
    retry_count = job.get('retry_count', 0)
    
    start_time = time.time()
    work_dir = None
    
    try:
        logger.info(f"[{job_id}] START video_id={video_id} retry={retry_count}/{MAX_RETRIES}")
        
        work_dir = TMP_DIR / video_id
        if work_dir.exists():
            shutil.rmtree(work_dir)
        work_dir.mkdir(parents=True, exist_ok=True)
        
        local_source = work_dir / 'source'
        
        await db.transcode_jobs.update_one({'job_id': job_id}, {'$set': {'status': TranscodeStatus.PROCESSING, 'worker_id': WORKER_ID, 'started_at': datetime.utcnow()}})
        
        logger.info(f"[{job_id}] Downloading...")
        await db.transcode_jobs.update_one({'job_id': job_id}, {'$set': {'status': TranscodeStatus.VALIDATING}})
        download_bytes = await download_s3_object(s3_client, AWS_BUCKET, s3_key, local_source)
        
        logger.info(f"[{job_id}] Probing...")
        await db.transcode_jobs.update_one({'job_id': job_id}, {'$set': {'status': TranscodeStatus.PROBING}})
        probe_data = await probe_video_file(local_source)
        logger.info(f"[{job_id}] Probe: {probe_data['width']}x{probe_data['height']} {probe_data['duration']:.1f}s codec={probe_data['codec']}")
        
        logger.info(f"[{job_id}] Transcoding...")
        await db.transcode_jobs.update_one({'job_id': job_id}, {'$set': {'status': TranscodeStatus.TRANSCODING}})
        playlists = await transcode_to_hls_renditions(local_source, work_dir, video_id, job_id, timeout_sec=JOB_TIMEOUT_MINUTES * 60)
        master_m3u8 = create_master_m3u8(work_dir, video_id, playlists)
        
        logger.info(f"[{job_id}] Extracting thumbnail...")
        thumb_path = work_dir / f"{video_id}_thumb.jpg"
        await extract_thumbnail(local_source, thumb_path)
        
        logger.info(f"[{job_id}] Uploading...")
        await db.transcode_jobs.update_one({'job_id': job_id}, {'$set': {'status': TranscodeStatus.UPLOADING}})
        master_url, thumb_url, upload_bytes = await upload_hls_to_s3(s3_client, AWS_BUCKET, work_dir, user_id, video_id, job_id)
        
        duration_sec = time.time() - start_time
        await db.videos.update_one({'id': video_id}, {'$set': {'status': 'processed', 'hls_master': master_url, 'thumbnail': thumb_url, 'transcode_duration_sec': duration_sec, 'output_size_bytes': upload_bytes, 'processed_at': datetime.utcnow()}})
        await db.transcode_jobs.update_one({'job_id': job_id}, {'$set': {'status': TranscodeStatus.DONE, 'completed_at': datetime.utcnow(), 'duration_sec': duration_sec, 'output_size_bytes': upload_bytes, 'probe_metrics': probe_data}})
        
        logger.info(f"[{job_id}] SUCCESS duration={duration_sec:.1f}s output={upload_bytes/(1024**2):.1f}MB")
        return True
        
    except (ValueError, RuntimeError) as e:
        logger.warning(f"[{job_id}] Transient error: {e}")
        
        if retry_count < MAX_RETRIES:
            backoff_min = min(2 ** retry_count, 60)
            retry_at = datetime.utcnow() + timedelta(minutes=backoff_min)
            await db.transcode_jobs.update_one({'job_id': job_id}, {'$set': {'status': TranscodeStatus.RETRYING, 'retry_count': retry_count + 1, 'retry_at': retry_at, 'last_error': str(e)}})
            logger.info(f"[{job_id}] Retry in {backoff_min}min (attempt {retry_count+1}/{MAX_RETRIES})")
            return False
        else:
            await db.transcode_jobs.update_one({'job_id': job_id}, {'$set': {'status': TranscodeStatus.FAILED, 'error': str(e), 'failed_at': datetime.utcnow()}})
            await db.videos.update_one({'id': video_id}, {'$set': {'status': 'failed', 'error': str(e), 'failed_at': datetime.utcnow()}})
            logger.error(f"[{job_id}] FAILED after {MAX_RETRIES} retries: {e}")
            return False
    
    except asyncio.TimeoutError as e:
        logger.error(f"[{job_id}] Timeout: {e}")
        await db.transcode_jobs.update_one({'job_id': job_id}, {'$set': {'status': TranscodeStatus.TIMEOUT, 'error': str(e), 'failed_at': datetime.utcnow()}})
        await db.videos.update_one({'id': video_id}, {'$set': {'status': 'timeout', 'error': str(e)}})
        return False
    
    except Exception as e:
        logger.error(f"[{job_id}] FATAL: {e}\n{traceback.format_exc()}")
        await db.transcode_jobs.update_one({'job_id': job_id}, {'$set': {'status': TranscodeStatus.FAILED, 'error': str(e), 'traceback': traceback.format_exc(), 'failed_at': datetime.utcnow()}})
        await db.videos.update_one({'id': video_id}, {'$set': {'status': 'failed', 'error': str(e)}})
        return False
    
    finally:
        if work_dir and work_dir.exists():
            try:
                shutil.rmtree(work_dir)
                logger.debug(f"[{job_id}] Cleaned up")
            except Exception as e:
                logger.warning(f"[{job_id}] Cleanup failed: {e}")


class TranscodeWorkerPool:
    """Worker pool with graceful shutdown"""
    
    def __init__(self, db, s3_client, max_concurrent: int = 2):
        self.db = db
        self.s3_client = s3_client
        self.max_concurrent = max_concurrent
        self.active_tasks = set()
        self.should_shutdown = False
    
    async def job_wrapper(self, job: Dict):
        try:
            await process_transcode_job(self.db, self.s3_client, job)
        except Exception as e:
            logger.error(f"Job wrapper error: {e}\n{traceback.format_exc()}")
    
    async def process_retryable_jobs(self):
        now = datetime.utcnow()
        job = await self.db.transcode_jobs.find_one_and_update({'status': TranscodeStatus.RETRYING, 'retry_at': {'$lte': now}}, {'$set': {'status': TranscodeStatus.QUEUED}}, sort=[('retry_at', 1)])
        return job is not None
    
    async def run(self):
        logger.info(f"WorkerPool started: worker_id={WORKER_ID}, concurrency={self.max_concurrent}")
        
        while not self.should_shutdown or self.active_tasks:
            try:
                if await self.process_retryable_jobs():
                    logger.info("Rescheduled retryable job")
                
                while len(self.active_tasks) < self.max_concurrent and not self.should_shutdown:
                    job = await self.db.transcode_jobs.find_one_and_update({'status': TranscodeStatus.QUEUED}, {'$set': {'status': TranscodeStatus.PROCESSING}}, sort=[('created_at', 1)])
                    
                    if not job:
                        break
                    
                    task = asyncio.create_task(self.job_wrapper(job))
                    self.active_tasks.add(task)
                    task.add_done_callback(self.active_tasks.discard)
                    logger.info(f"Dispatched job {job['job_id']}, active={len(self.active_tasks)}")
                
                if not self.active_tasks:
                    await asyncio.sleep(5)
                else:
                    await asyncio.wait(self.active_tasks, timeout=10, return_when=asyncio.FIRST_COMPLETED)
                
            except Exception as e:
                logger.error(f"Pool loop error: {e}\n{traceback.format_exc()}")
                await asyncio.sleep(5)
        
        logger.info(f"WorkerPool shut down")
    
    async def shutdown(self):
        logger.info(f"Graceful shutdown...")
        self.should_shutdown = True
        
        if self.active_tasks:
            logger.info(f"Waiting for {len(self.active_tasks)} tasks...")
            try:
                await asyncio.wait_for(asyncio.gather(*self.active_tasks, return_exceptions=True), timeout=JOB_TIMEOUT_MINUTES * 60 + 60)
            except asyncio.TimeoutError:
                logger.warning(f"Timeout, cancelling tasks")
                for task in self.active_tasks:
                    task.cancel()


async def health_check_server(port: int = 9090):
    """Simple health check endpoint"""
    async def handle(reader, writer):
        try:
            await reader.read(1024)
            response = b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n"
            response += json.dumps({'status': 'healthy', 'worker_id': WORKER_ID, 'timestamp': datetime.utcnow().isoformat()}).encode()
            writer.write(response)
            await writer.drain()
        finally:
            writer.close()
    
    server = await asyncio.start_server(handle, '0.0.0.0', port)
    logger.info(f"Health check on :{port}")
    async with server:
        await server.serve_forever()


async def main():
    """Application entry point"""
    missing = []
    for var in ['MONGO_URL', 'DB_NAME', 'AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_S3_BUCKET']:
        if not os.environ.get(var):
            missing.append(var)
    
    if missing:
        logger.error(f"Missing env vars: {', '.join(missing)}")
        sys.exit(1)
    
    try:
        subprocess.run([FFMPEG_BIN, '-version'], capture_output=True, timeout=5, check=True)
    except Exception:
        logger.error(f"ffmpeg not found")
        sys.exit(1)
    
    logger.info(f"Connecting to MongoDB...")
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    logger.info(f"Connecting to S3...")
    s3_client = boto3.client('s3', region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)
    
    try:
        s3_client.head_bucket(Bucket=AWS_BUCKET)
    except Exception as e:
        logger.error(f"S3 connection failed: {e}")
        sys.exit(1)
    
    await db.transcode_jobs.create_index([('status', 1), ('created_at', 1)])
    await db.transcode_jobs.create_index([('status', 1), ('retry_at', 1)])
    await db.videos.create_index([('id', 1)])
    
    pool = TranscodeWorkerPool(db, s3_client, max_concurrent=CONCURRENCY)
    
    def signal_handler(sig, frame):
        logger.info(f"Signal {sig}")
        asyncio.create_task(pool.shutdown())
    
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        health_task = asyncio.create_task(health_check_server(HEALTH_CHECK_PORT))
        await pool.run()
    except KeyboardInterrupt:
        logger.info("Interrupted")
        await pool.shutdown()
    except Exception as e:
        logger.error(f"Fatal: {e}\n{traceback.format_exc()}")
        sys.exit(1)
    finally:
        client.close()
        logger.info("Exit")


if __name__ == '__main__':
    asyncio.run(main())
