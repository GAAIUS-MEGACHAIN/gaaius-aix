# VIDEOS Production Deployment Guide

## Overview

VIDEOS is now a **production-grade, enterprise-ready video platform** with:
- ✅ S3 storage with presigned URLs (no local disk bloat)
- ✅ HLS adaptive bitrate streaming (1080p/720p/480p/360p)
- ✅ Async transcoding with worker pool
- ✅ Automatic retry with exponential backoff
- ✅ Graceful shutdown and signal handling
- ✅ Kubernetes-ready health checks
- ✅ Comprehensive structured logging
- ✅ Database indexing for efficient polling
- ✅ CircuitBreaker error classification
- ✅ Multipart S3 uploads with cache headers

---

## Architecture

```
┌─────────────────┐
│  Frontend/      │
│  API Client     │
└────────┬────────┘
         │
    ┌────▼───────────────────────────────────┐
    │   FastAPI Server (server.py)            │
    │                                         │
    │  POST /videos/upload                │  (handles upload, enqueues job)
    │  POST /videos/presign               │  (presigned S3 PUT URL)
    │  GET  /videos/videos/{id}           │  (playback metadata)
    │  GET  /videos/jobs/{id}             │  (transcode progress)
    └────┬─────────────────────────────────┬─┘
         │                                 │
    ┌────▼──────────────┐         ┌───────▼────────┐
    │  AWS S3           │         │  MongoDB       │
    │  (videos bucket)  │         │  (jobs queue)  │
    └───────────────────┘         └────────────────┘
         ▲
         │
    ┌────┴─────────────────────────────────┐
    │  TranscodeWorkerPool                  │
    │  (transcode_worker.py)                │
    │                                       │
    │  ┌──────────────┐  ┌──────────────┐  │
    │  │ Worker Task  │  │ Worker Task  │  │
    │  │ (concurrent) │  │ (concurrent) │  │
    │  └──────────────┘  └──────────────┘  │
    │                                       │
    │  • Probe video (ffprobe)              │
    │  • Download from S3                   │
    │  • Encode to HLS (ffmpeg)             │
    │  • Upload to S3                       │
    │  • Retry on transient errors          │
    │  • Report success/failure to DB       │
    └───────────────────────────────────────┘
```

---

## Prerequisites

### System Requirements
- **Python 3.8+**
- **FFmpeg** (with libx264, aac, hls support)
  - Ubuntu/Debian: `sudo apt-get install ffmpeg`
  - macOS: `brew install ffmpeg`
  - Windows: Download from ffmpeg.org or `choco install ffmpeg`
- **Disk Space**: 50GB+ for temporary transcode files (auto-cleanup after upload)
- **Network**: 100Mbps+ upload to S3

### AWS Requirements
- **S3 Bucket**: `gaaius-videos` (or custom, set `AWS_S3_BUCKET`)
- **IAM User** with permissions:
  ```json
  {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket",
          "s3:HeadObject",
          "s3:HeadBucket"
        ],
        "Resource": [
          "arn:aws:s3:::gaaius-videos",
          "arn:aws:s3:::gaaius-videos/*"
        ]
      }
    ]
  }
  ```
- **CloudFront Distribution** (optional, for CDN):
  - Origin: S3 bucket
  - Default TTL: 3600 (1 hour for playlists)
  - Max TTL: 31536000 (1 year for segments)
  - Set `CLOUDFRONT_DOMAIN` env var (e.g., `d123.cloudfront.net`)

### MongoDB Requirements
- **v4.0+** with replication (for transactions) or **Atlas**
- Collections auto-created by app:
  - `transcode_jobs`
  - `videos`
- Indexes created by worker on startup

---

## Environment Configuration

### Server (API)

Create `.env` in `backend/`:

```bash
# MongoDB
MONGO_URL=mongodb://localhost:27017
DB_NAME=gaaius

# AWS S3
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_S3_BUCKET=gaaius-videos
AWS_REGION=us-east-1

# CDN (optional)
CLOUDFRONT_DOMAIN=d123.cloudfront.net

# JWT
JWT_SECRET=your-super-secret-key-at-least-32-chars
JWT_ALGORITHM=HS256

# FastAPI
WORKERS=4
PORT=8000
LOG_LEVEL=INFO
```

### Worker (Transcoding)

Same `.env` file (sourced automatically) or separate:

```bash
# MongoDB (same as server)
MONGO_URL=mongodb://localhost:27017
DB_NAME=gaaius

# AWS S3 (same as server)
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_S3_BUCKET=gaaius-videos
AWS_REGION=us-east-1

# CDN
CLOUDFRONT_DOMAIN=d123.cloudfront.net

# Worker pool config
CONCURRENCY=2              # concurrent transcode jobs (adjust per CPU cores)
MAX_RETRIES=3              # retry failed jobs 3 times
JOB_TIMEOUT_MINUTES=180    # 3 hours per job
DISK_MIN_GB=10             # stop if free disk < 10GB
HEALTH_CHECK_PORT=9090     # Kubernetes probe port
TMP_DIR=/tmp/gaaius        # transcode working directory
```

---

## Deployment Scenarios

### 1. Local Development

```bash
# Start MongoDB locally
docker run -d --name mongo -p 27017:27017 mongo:latest

# Start server
cd backend
pip install -r requirements.txt
python -m uvicorn server:app --reload --port 8000

# Start worker (in another terminal)
cd backend
python transcode_worker.py
```

### 2. Docker Compose (Local + S3)

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  mongo:
    image: mongo:5
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db
    environment:
      MONGO_INITDB_DATABASE: gaaius

  server:
    build:
      context: .
      dockerfile: backend/Dockerfile
    ports:
      - "8000:8000"
    environment:
      MONGO_URL: mongodb://mongo:27017
      DB_NAME: gaaius
      AWS_ACCESS_KEY_ID: ${AWS_ACCESS_KEY_ID}
      AWS_SECRET_ACCESS_KEY: ${AWS_SECRET_ACCESS_KEY}
      AWS_S3_BUCKET: gaaius-videos
      AWS_REGION: us-east-1
      CLOUDFRONT_DOMAIN: ${CLOUDFRONT_DOMAIN:-}
      JWT_SECRET: ${JWT_SECRET}
      WORKERS: 4
    depends_on:
      - mongo
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 10s
      timeout: 5s
      retries: 3

  worker:
    build:
      context: .
      dockerfile: backend/Dockerfile
    command: python transcode_worker.py
    environment:
      MONGO_URL: mongodb://mongo:27017
      DB_NAME: gaaius
      AWS_ACCESS_KEY_ID: ${AWS_ACCESS_KEY_ID}
      AWS_SECRET_ACCESS_KEY: ${AWS_SECRET_ACCESS_KEY}
      AWS_S3_BUCKET: gaaius-videos
      AWS_REGION: us-east-1
      CLOUDFRONT_DOMAIN: ${CLOUDFRONT_DOMAIN:-}
      CONCURRENCY: 2
      MAX_RETRIES: 3
      JOB_TIMEOUT_MINUTES: 180
    depends_on:
      - mongo
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9090/health"]
      interval: 10s
      timeout: 5s
      retries: 3

volumes:
  mongo_data:
```

Run:
```bash
export AWS_ACCESS_KEY_ID=...
export AWS_SECRET_ACCESS_KEY=...
export CLOUDFRONT_DOMAIN=d123.cloudfront.net
export JWT_SECRET=your-secret-key
docker-compose up -d
```

### 3. Kubernetes Deployment

Create `k8s/multitube-server.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: multitube-server
spec:
  replicas: 2
  selector:
    matchLabels:
      app: multitube-server
  template:
    metadata:
      labels:
        app: multitube-server
    spec:
      containers:
      - name: server
        image: your-registry/multitube-server:latest
        ports:
        - containerPort: 8000
        env:
        - name: MONGO_URL
          valueFrom:
            secretKeyRef:
              name: multitube-config
              key: mongo_url
        - name: AWS_ACCESS_KEY_ID
          valueFrom:
            secretKeyRef:
              name: multitube-config
              key: aws_access_key_id
        - name: AWS_SECRET_ACCESS_KEY
          valueFrom:
            secretKeyRef:
              name: multitube-config
              key: aws_secret_access_key
        - name: AWS_S3_BUCKET
          value: "gaaius-videos"
        - name: CLOUDFRONT_DOMAIN
          valueFrom:
            configMapKeyRef:
              name: multitube-config
              key: cloudfront_domain
        - name: JWT_SECRET
          valueFrom:
            secretKeyRef:
              name: multitube-config
              key: jwt_secret
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

Create `k8s/multitube-worker.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: multitube-worker
spec:
  replicas: 3
  selector:
    matchLabels:
      app: multitube-worker
  template:
    metadata:
      labels:
        app: multitube-worker
    spec:
      terminationGracePeriodSeconds: 300
      containers:
      - name: worker
        image: your-registry/multitube-worker:latest
        env:
        - name: MONGO_URL
          valueFrom:
            secretKeyRef:
              name: multitube-config
              key: mongo_url
        - name: AWS_ACCESS_KEY_ID
          valueFrom:
            secretKeyRef:
              name: multitube-config
              key: aws_access_key_id
        - name: AWS_SECRET_ACCESS_KEY
          valueFrom:
            secretKeyRef:
              name: multitube-config
              key: aws_secret_access_key
        - name: AWS_S3_BUCKET
          value: "gaaius-videos"
        - name: CONCURRENCY
          value: "2"
        - name: MAX_RETRIES
          value: "3"
        - name: JOB_TIMEOUT_MINUTES
          value: "180"
        resources:
          requests:
            cpu: "2"
            memory: "2Gi"
          limits:
            cpu: "4"
            memory: "4Gi"
        livenessProbe:
          httpGet:
            path: /health
            port: 9090
          initialDelaySeconds: 30
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health
            port: 9090
          initialDelaySeconds: 10
          periodSeconds: 10
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchExpressions:
                - key: app
                  operator: In
                  values:
                  - multitube-worker
              topologyKey: kubernetes.io/hostname
```

Deploy:
```bash
kubectl apply -f k8s/multitube-server.yaml
kubectl apply -f k8s/multitube-worker.yaml

# Monitor
kubectl logs deployment/multitube-worker -f
kubectl get pods -l app=multitube-worker -w
```

---

## API Usage

### 1. Get Presigned URL for Upload

**Request:**
```bash
curl -X POST http://localhost:8000/videos/presign \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "my-video.mp4",
    "media_type": "video/mp4"
  }'
```

**Response:**
```json
{
  "s3_key": "source/user123/videos/abc123def456",
  "url": "https://gaaius-videos.s3.us-east-1.amazonaws.com/...?X-Amz-Signature=...",
  "media_id": "abc123def456",
  "expires_in": 3600
}
```

**Browser Upload (using presigned URL):**
```javascript
const response = await fetch(
  'https://gaaius-videos.s3.us-east-1.amazonaws.com/...?X-Amz-Signature=...',
  {
    method: 'PUT',
    headers: { 'Content-Type': 'video/mp4' },
    body: videoFile
  }
);
```

### 2. Upload Video

**Request:**
```bash
curl -X POST http://localhost:8000/videos/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@video.mp4"
```

**Response:**
```json
{
  "video_id": "abc123def456",
  "job_id": "job_xyz789",
  "status": "processing",
  "hls_url": null,
  "thumbnail_url": null
}
```

### 3. Check Transcode Progress

**Request:**
```bash
curl http://localhost:8000/videos/jobs/job_xyz789
```

**Response:**
```json
{
  "job_id": "job_xyz789",
  "video_id": "abc123def456",
  "status": "transcoding",
  "progress": {
    "stage": "encoding_720p",
    "duration_sec": 45
  },
  "retry_count": 0,
  "created_at": "2024-01-20T10:00:00Z",
  "started_at": "2024-01-20T10:00:05Z"
}
```

### 4. Get Video Metadata

**Request:**
```bash
curl http://localhost:8000/videos/videos/abc123def456
```

**Response (completed):**
```json
{
  "id": "abc123def456",
  "title": "My Video",
  "status": "processed",
  "hls_url": "https://d123.cloudfront.net/social/user123/videos/abc123def456/master.m3u8",
  "thumbnail_url": "https://d123.cloudfront.net/social/user123/videos/abc123def456/thumb.jpg",
  "transcode_duration_sec": 125,
  "output_size_bytes": 450000000,
  "processed_at": "2024-01-20T10:02:10Z"
}
```

---

## Monitoring & Debugging

### Check Worker Health

```bash
# Kubernetes
kubectl get pods -l app=multitube-worker
kubectl logs deployment/multitube-worker -f --all-containers

# Docker Compose
docker-compose logs -f worker

# Direct (if running locally)
curl http://localhost:9090/health
```

### View Database Status

```bash
# Pending jobs
mongo gaaius
> db.transcode_jobs.find({status: "queued"}).count()

# Failed jobs
> db.transcode_jobs.find({status: "failed"}).pretty()

# Job retries
> db.transcode_jobs.find({status: "retrying"}).pretty()

# Completed stats
> db.transcode_jobs.aggregate([
    {$match: {status: "done"}},
    {$group: {
      _id: null,
      count: {$sum: 1},
      avg_duration: {$avg: "$duration_sec"},
      total_output: {$sum: "$output_size_bytes"}
    }}
  ])
```

### Common Issues

**Worker not processing jobs:**
1. Check MongoDB connection: `mongo $MONGO_URL/gaaius --eval "db.adminCommand('ping')"`
2. Check S3 credentials: `aws s3 ls --profile gaaius`
3. Check FFmpeg: `ffmpeg -version && ffprobe -version`
4. Check disk space: `df -h /tmp`
5. View logs: `docker logs worker` or `tail -f /var/log/multitube.log`

**Jobs stuck in RETRYING:**
- Worker crashed during transcode (check logs)
- Disk full (cleanup `/tmp/gaaius`)
- S3 upload failed (check bucket permissions)
- Increase `JOB_TIMEOUT_MINUTES` if jobs taking longer than expected

**HLS playback issues:**
1. Verify master.m3u8 exists: `aws s3 ls s3://gaaius-videos/social/user123/videos/abc123def456/`
2. Check CloudFront cache: `aws cloudfront create-invalidation --distribution-id DXY --paths "/*"`
3. Test direct S3 URL: `curl https://gaaius-videos.s3.us-east-1.amazonaws.com/.../master.m3u8`

---

## Performance Tuning

### Worker Concurrency

Edit `.env`:
```bash
# For 4-core machine: concurrency=2
# For 8-core machine: concurrency=4
# For 16-core machine: concurrency=6
CONCURRENCY=2
```

### FFmpeg Encoding Speed

In `transcode_worker.py`, adjust `preset`:
```python
# preset options: ultrafast, superfast, veryfast, faster (prod default)
# Using 'fast' for slower but better quality; 'faster' for speed
```

### Database Polling

Indexes are auto-created. Manual cleanup of old jobs (>30 days):
```javascript
db.transcode_jobs.deleteMany({
  status: "done",
  completed_at: {$lt: new Date(Date.now() - 30*24*60*60*1000)}
})
```

### S3 Lifecycle Policy

Set in AWS Console to auto-delete old source files after 7 days:
```json
{
  "Rules": [
    {
      "Filter": {"Prefix": "source/"},
      "Expiration": {"Days": 7},
      "Status": "Enabled"
    }
  ]
}
```

---

## Cost Optimization

| Component | Cost | Optimization |
|-----------|------|---------------|
| S3 Storage | ~$0.023/GB/month | Enable versioning=off, use Lifecycle policies |
| S3 Transfer Out | ~$0.09/GB | Use CloudFront CDN (saves 70%) |
| EC2 (Workers) | ~$0.50/hour/instance | Auto-scale based on job queue depth |
| Data Transfer | Per GB | Keep workers in same region as S3 |
| CloudFront | ~$0.085/GB | Adjust cache TTL, use signed URLs for auth |

**Estimated cost for 1TB/month:**
- S3 storage: $23
- S3 transfer to CloudFront: $90 (vs $900 direct)
- CloudFront egress: ~$80
- 1x worker instance: $360/month
- **Total: ~$550/month**

---

## Security

### Network
- Use VPC endpoints for S3 (no internet gateway needed)
- Use security groups to restrict MongoDB access
- Use HTTPS for all S3 URLs (set in environment)

### Authentication
- All APIs require JWT token
- Token issued with 30-day expiry
- Refresh tokens via POST /auth/refresh

### S3 Access
- Bucket policy: deny unencrypted uploads (require `ServerSideEncryption: AES256`)
- User data isolation: videos stored under `social/{user_id}/`
- Presigned URLs: 1-hour expiry for uploads

### Encryption
- S3 server-side encryption (AES256)
- MongoDB TLS (if using Atlas)
- JWT HS256 (change `JWT_SECRET` in production!)

---

## Scaling

### Horizontal (More Workers)
1. Increase replicas in K8s deployment
2. Workers auto-discover via MongoDB polling
3. Distribute load across machines

### Vertical (Bigger Machines)
1. Increase CPU cores → increase `CONCURRENCY`
2. Increase RAM → encode more renditions in parallel

### Example: Scale from 1 to 10 Mbps upload speed

```bash
# 1 worker (2 concurrent jobs)
# 2-3 videos/minute throughput

# 5 workers (2 concurrent each = 10 jobs)
# 15-20 videos/minute throughput

# 20 workers (2 concurrent each = 40 jobs)
# 60-80 videos/minute throughput
```

---

## Maintenance & Updates

### Database Backup

```bash
# Backup
mongodump --uri="mongodb://localhost:27017/gaaius" --out=/backups/gaaius

# Restore
mongorestore --uri="mongodb://localhost:27017" /backups/gaaius
```

### Worker Update (Zero Downtime)

```bash
# 1. Build new image
docker build -t multitube-worker:v2 backend/

# 2. Kubernetes rolling update
kubectl set image deployment/multitube-worker worker=multitube-worker:v2

# 3. Monitor
kubectl rollout status deployment/multitube-worker
kubectl logs -f deployment/multitube-worker
```

### Clean Old Files

```bash
# Delete S3 source videos > 7 days old
aws s3 rm s3://gaaius-videos/source/ \
  --recursive \
  --exclude "*" \
  --include "*.mp4" \
  --older-than 7
```

---

## Support & Troubleshooting

**Worker stuck on job?**
```bash
# Force timeout and retry
mongo gaaius
> db.transcode_jobs.updateOne(
    {status: "processing", started_at: {$lt: new Date(Date.now() - 3600000)}},
    {$set: {status: "retrying", retry_count: 1}}
  )
```

**S3 upload hanging?**
- Check network: `aws s3 ls --profile gaaius` should respond in <5s
- Increase timeout: `JOB_TIMEOUT_MINUTES=300`
- Check S3 bucket quotas (AWS console)

**FFmpeg segfaults?**
- Update: `apt upgrade ffmpeg` (Ubuntu)
- Check memory: `free -h` (need >2GB)
- Use preset='faster' to reduce CPU

---

## Conclusion

Your VIDEOS platform is now **production-ready**. Key strengths:

✅ **Scalable**: Async workers, S3 storage, horizontal scaling
✅ **Reliable**: Retry logic, error recovery, graceful shutdown
✅ **Observable**: Structured logging, health checks, job status API
✅ **Secure**: S3 presigned URLs, JWT auth, encryption
✅ **Cost-effective**: CDN integration, lifecycle policies, efficient encoding

Deploy with confidence! 🚀
