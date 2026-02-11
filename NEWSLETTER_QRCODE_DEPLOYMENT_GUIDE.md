# Newsletter & QR Code - Deployment Guide

## Production Deployment Instructions

This guide covers deploying the Newsletter and QR Code modules to production environments.

---

## 1. Pre-Deployment Checklist

### Backend Requirements
- [ ] Python 3.8+ installed
- [ ] FastAPI and dependencies installed
- [ ] MongoDB 4.4+ running and accessible
- [ ] All environment variables configured
- [ ] SMTP credentials verified for newsletter
- [ ] Enough disk space for QR code storage
- [ ] SSL certificates configured
- [ ] Firewall rules configured

### Frontend Requirements
- [ ] Node.js 16+ installed
- [ ] Dependencies installed (`npm install`)
- [ ] Build optimized (`npm run build`)
- [ ] Environment variables configured
- [ ] API base URL points to production backend

### Services Required
- [ ] MongoDB (primary database)
- [ ] Redis (caching - optional but recommended)
- [ ] SMTP server (newsletter emails)
- [ ] Web server (Nginx/Apache)
- [ ] Process manager (PM2, Supervisor)

---

## 2. Database Setup

### Create Indexes for Performance

```bash
# Connect to MongoDB
mongosh

# Use database
use gaaius_ai

# Create indexes for newsletters
db.subscribers.createIndex({ email: 1 }, { unique: true })
db.subscribers.createIndex({ status: 1 })
db.subscribers.createIndex({ tags: 1 })
db.subscribers.createIndex({ created_at: -1 })

db.campaigns.createIndex({ status: 1 })
db.campaigns.createIndex({ created_at: -1 })
db.campaigns.createIndex({ sent_at: -1 })

db.automations.createIndex({ enabled: 1 })
db.automations.createIndex({ created_at: -1 })

# Create indexes for QR codes
db.qrcodes.createIndex({ short_code: 1 }, { unique: true })
db.qrcodes.createIndex({ status: 1 })
db.qrcodes.createIndex({ created_at: -1 })
db.qrcodes.createIndex({ tags: 1 })

db.qrcode_scans.createIndex({ qrcode_id: 1 })
db.qrcode_scans.createIndex({ timestamp: -1 })
db.qrcode_scans.createIndex({ device_type: 1 })

db.qrcode_batches.createIndex({ status: 1 })
db.qrcode_batches.createIndex({ created_at: -1 })
```

### Verify Indexes

```bash
db.subscribers.getIndexes()
db.qrcodes.getIndexes()
```

---

## 3. Environment Configuration

### Backend Environment (.env file)

```env
# ===== DATABASE =====
MONGODB_URL=mongodb://user:password@mongodb-host:27017
DATABASE_NAME=gaaius_ai

# ===== EMAIL (NEWSLETTER) =====
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_TLS=true
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=app_specific_password
FROM_EMAIL=noreply@example.com
FROM_NAME=GAAIUS AI Platform

# ===== QR CODE =====
QR_STORAGE_PATH=/var/www/gaaius/qr-codes
QR_BASE_URL=https://qr.yourdomain.com
QR_EXPIRY_DAYS=90

# ===== SECURITY =====
JWT_SECRET=your-super-secret-key-change-this-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# ===== API CONFIGURATION =====
API_PORT=8000
API_HOST=0.0.0.0
DEBUG=false

# ===== CORS =====
FRONTEND_URL=https://yourdomain.com
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# ===== REDIS (Optional but Recommended) =====
REDIS_URL=redis://redis-host:6379
REDIS_PASSWORD=redis_password
ENABLE_CACHING=true

# ===== LOGGING =====
LOG_LEVEL=INFO
LOG_FILE=/var/log/gaaius/api.log

# ===== RATE LIMITING =====
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=1000
RATE_LIMIT_PERIOD=60

# ===== FEATURES =====
NEWSLETTER_ENABLED=true
QRCODE_ENABLED=true
QRCODE_AI_ENABLED=true
```

### Frontend Environment (.env file)

```env
# Frontend environment variables
REACT_APP_API_BASE_URL=https://api.yourdomain.com
REACT_APP_API_TIMEOUT=30000
REACT_APP_ENABLE_ANALYTICS=true
REACT_APP_ENV=production
```

---

## 4. Backend Deployment

### Option A: Docker Deployment

#### 1. Build Docker Image

```bash
cd backend

# Build image
docker build -t gaaius-newsletter-qrcode:1.0.0 \
    -f Dockerfile \
    .

# Tag for registry
docker tag gaaius-newsletter-qrcode:1.0.0 \
    your-registry/gaaius-newsletter-qrcode:1.0.0
```

#### 2. Create docker-compose.yml

```yaml
version: '3.8'

services:
  mongodb:
    image: mongo:5.0
    container_name: gaaius_mongodb
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: secure_password
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db
    restart: unless-stopped
    networks:
      - gaaius_network

  redis:
    image: redis:7-alpine
    container_name: gaaius_redis
    ports:
      - "6379:6379"
    restart: unless-stopped
    networks:
      - gaaius_network

  backend:
    image: gaaius-newsletter-qrcode:1.0.0
    container_name: gaaius_backend
    environment:
      - MONGODB_URL=mongodb://admin:secure_password@mongodb:27017
      - REDIS_URL=redis://redis:6379
      - JWT_SECRET=${JWT_SECRET}
      - SMTP_HOST=${SMTP_HOST}
      - SMTP_USER=${SMTP_USER}
      - SMTP_PASSWORD=${SMTP_PASSWORD}
    ports:
      - "8000:8000"
    depends_on:
      - mongodb
      - redis
    volumes:
      - ./qr-codes:/var/www/gaaius/qr-codes
      - ./logs:/var/log/gaaius
    restart: unless-stopped
    networks:
      - gaaius_network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  mongodb_data:

networks:
  gaaius_network:
    driver: bridge
```

#### 3. Deploy with Docker Compose

```bash
# Create environment file
cp .env.example .env
# Edit .env with production values

# Start services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Check status
docker-compose ps
```

### Option B: Manual Deployment (Linux/Ubuntu)

#### 1. Install Dependencies

```bash
# Install Python dependencies
cd /opt/gaaius/backend
pip install -r requirements.txt

# Install system packages
sudo apt-get update
sudo apt-get install -y python3-venv python3-pip

# Create virtual environment
python3 -m venv venv
source venv/bin/activate
```

#### 2. Configure Systemd Service

```bash
# Create service file
sudo nano /etc/systemd/system/gaaius-backend.service
```

```ini
[Unit]
Description=GAAIUS Newsletter & QR Code Backend
After=network.target mongodb.service

[Service]
Type=notify
User=www-data
WorkingDirectory=/opt/gaaius/backend
Environment="PATH=/opt/gaaius/backend/venv/bin"
EnvironmentFile=/opt/gaaius/backend/.env
ExecStart=/opt/gaaius/backend/venv/bin/python server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 3. Start Service

```bash
# Enable service
sudo systemctl daemon-reload
sudo systemctl enable gaaius-backend.service

# Start service
sudo systemctl start gaaius-backend.service

# Check status
sudo systemctl status gaaius-backend.service

# View logs
sudo journalctl -u gaaius-backend.service -f
```

#### 4. Setup Nginx Reverse Proxy

```nginx
# /etc/nginx/sites-available/gaaius-api
upstream gaaius_backend {
    server 127.0.0.1:8000;
}

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;

    location / {
        proxy_pass http://gaaius_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # QR code static files
    location /static/qrcodes/ {
        alias /var/www/gaaius/qr-codes/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name api.yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

Enable Nginx configuration:
```bash
sudo ln -s /etc/nginx/sites-available/gaaius-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 5. Frontend Deployment

### Build for Production

```bash
cd frontend

# Install dependencies
npm install

# Build optimized bundle
npm run build

# Result: build/ directory ready for deployment
```

### Option A: Deploy to CDN/Static Host

```bash
# Upload build folder to S3
aws s3 sync build/ s3://your-bucket/gaaius-web/

# Or upload to your web server
scp -r build/* user@server:/var/www/gaaius-web/
```

### Option B: Docker Deployment

```dockerfile
# Dockerfile for frontend
FROM node:16-alpine as builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
```

#### Nginx Configuration for Frontend

```nginx
# /etc/nginx/conf.d/gaaius-frontend.conf
server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    root /var/www/gaaius-web;
    index index.html;

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 365d;
        add_header Cache-Control "public, immutable";
    }

    # SPA routing
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API proxy
    location /api {
        proxy_pass https://api.yourdomain.com;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 6. SSL/TLS Setup

### Using Let's Encrypt with Certbot

```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Generate certificate
sudo certbot certonly --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal setup
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer

# Check renewal
sudo certbot renew --dry-run
```

---

## 7. Monitoring & Health Checks

### Health Check Endpoints

```bash
# Newsletter service
curl -s https://api.yourdomain.com/api/newsletter/health | jq

# QR Code service
curl -s https://api.yourdomain.com/api/qrcode/health | jq

# Both should return:
# {
#   "status": "healthy",
#   "database": "connected",
#   "timestamp": "2024-01-20T10:30:00Z"
# }
```

### Setup Monitoring

```bash
# Install Node Exporter (Prometheus metrics)
cd /opt
wget https://github.com/prometheus/node_exporter/releases/download/v1.5.0/node_exporter-1.5.0.linux-amd64.tar.gz
tar xvfz node_exporter-1.5.0.linux-amd64.tar.gz
sudo mv node_exporter-1.5.0.linux-amd64/node_exporter /usr/local/bin/
```

### Uptime Monitoring

```bash
# Monitor with cron job
* * * * * curl -s https://api.yourdomain.com/api/newsletter/health || echo "Newsletter down"
* * * * * curl -s https://api.yourdomain.com/api/qrcode/health || echo "QR Code down"
```

---

## 8. Backup Strategy

### Database Backups

```bash
# Backup MongoDB
mongodump --uri="mongodb://user:password@host:27017/gaaius_ai" \
          --out=/backups/gaaius-$(date +%Y%m%d)

# Automated daily backup
0 2 * * * mongodump --uri="mongodb://user:password@host:27017/gaaius_ai" \
                    --out=/backups/gaaius-$(date +\%Y\%m\%d) && \
            tar czf /backups/gaaius-$(date +\%Y\%m\%d).tar.gz /backups/gaaius-$(date +\%Y\%m\%d)
```

### QR Code Storage Backup

```bash
# Backup QR codes
tar czf /backups/qrcodes-$(date +%Y%m%d).tar.gz /var/www/gaaius/qr-codes/

# Automated daily backup
0 3 * * * tar czf /backups/qrcodes-$(date +\%Y\%m\%d).tar.gz /var/www/gaaius/qr-codes/ && \
          find /backups -name "qrcodes-*.tar.gz" -mtime +30 -delete
```

---

## 9. Performance Tuning

### Database Optimization

```javascript
// Monitor slow queries
db.setProfilingLevel(1, { slowms: 100 })

// Check query performance
db.system.profile.find({ millis: { $gt: 100 } }).limit(5)
```

### Backend Tuning

```python
# In server.py
import gunicorn.app.base

# Use Gunicorn with multiple workers
# gunicorn -w 4 -b 0.0.0.0:8000 server:app
```

### Frontend Optimization

```bash
# Analyze bundle size
npm install webpack-bundle-analyzer
npm run build -- --analyze

# Optimize images
find build -name "*.png" -exec optipng -o7 {} \;
find build -name "*.jpg" -exec jpegoptim {} \;
```

---

## 10. Security Hardening

### Rate Limiting

```python
# In server.py
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/newsletter/subscribers")
@limiter.limit("100/minute")
async def add_subscriber(...):
    pass
```

### CORS Configuration

```python
# Restrict to production domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com", "https://www.yourdomain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
```

### API Key Authentication

```bash
# Generate secure API keys
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Add to .env
NEWSLETTER_API_KEY=your_generated_key_here
QRCODE_API_KEY=your_generated_key_here
```

---

## 11. Logging & Error Tracking

### Centralized Logging

```bash
# Install ELK stack components
docker run -d --name elasticsearch docker.elastic.co/elasticsearch/elasticsearch:8.0.0
docker run -d --name logstash docker.elastic.co/logstash/logstash:8.0.0
docker run -d --name kibana docker.elastic.co/kibana/kibana:8.0.0
```

### Error Tracking with Sentry

```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="https://your-sentry-dsn@sentry.io/project-id",
    integrations=[FastApiIntegration()],
    environment="production",
    traces_sample_rate=0.1
)
```

---

## 12. Scaling Strategy

### Horizontal Scaling

```bash
# Load balancer configuration (HAProxy)
# /etc/haproxy/haproxy.cfg
backend backend_api
    balance roundrobin
    server backend1 10.0.1.10:8000 check
    server backend2 10.0.1.11:8000 check
    server backend3 10.0.1.12:8000 check
```

### Database Scaling

```javascript
// MongoDB Replication
rs.initiate({
    _id: "rs0",
    members: [
        {_id: 0, host: "db1:27017"},
        {_id: 1, host: "db2:27017"},
        {_id: 2, host: "db3:27017"}
    ]
})
```

---

## 13. Deployment Validation

### Post-Deployment Checklist

- [ ] Backend service healthy: `/api/newsletter/health` returns OK
- [ ] QR Code service healthy: `/api/qrcode/health` returns OK
- [ ] Frontend loads at custom domain
- [ ] Can create newsletter subscriber
- [ ] Can create newsletter campaign
- [ ] Can send test campaign
- [ ] Can generate QR code
- [ ] QR analytics working
- [ ] Database backups running
- [ ] SSL certificates valid
- [ ] Monitoring alerts configured
- [ ] Error tracking active (Sentry)
- [ ] Logs aggregating (ELK/CloudWatch)

### Performance Validation

```bash
# Load test
ab -n 1000 -c 100 https://api.yourdomain.com/api/newsletter/health

# Response time check
curl -w "Time: %{time_total}s\n" https://api.yourdomain.com/api/qrcode/list

# Database query performance
mongo --eval "db.subscribers.aggregate([{$group: {_id: null, count: {$sum: 1}}}])"
```

---

## 14. Disaster Recovery

### Recovery Procedures

```bash
# Restore from MongoDB backup
mongorestore /backups/gaaius-20240120/

# Restore QR code files
tar xzf /backups/qrcodes-20240120.tar.gz -C /

# Verify restore
mongosh --eval "db.subscribers.count()"
ls -la /var/www/gaaius/qr-codes/ | head
```

### Failover Procedures

```bash
# Switch to secondary database
rs.stepDown()

# Verify failover
rs.status()

# Check backend reconnection
curl https://api.yourdomain.com/api/newsletter/health
```

---

## 15. Support & Maintenance

### Regular Maintenance Tasks

- **Weekly:** Check service health, review error logs
- **Monthly:** Optimize database, analyze performance metrics
- **Quarterly:** Security audit, dependency updates
- **Annually:** Capacity planning, architecture review

### Update Procedure

```bash
# Backend update
cd backend
git pull origin main
pip install -r requirements.txt
systemctl restart gaaius-backend

# Frontend update
cd frontend
git pull origin main
npm install
npm run build
cp -r build/* /var/www/gaaius-web/
```

---

## 16. Useful Commands

```bash
# View backend logs
sudo journalctl -u gaaius-backend.service -n 100 -f

# Restart services
sudo systemctl restart gaaius-backend.service
sudo systemctl restart nginx

# Check disk usage
du -sh /var/www/gaaius/*
du -sh /backups/*

# MongoDB connection test
mongosh "mongodb://user:password@host:27017/gaaius_ai"

# API endpoint test
curl -H "Authorization: Bearer YOUR_TOKEN" \
     https://api.yourdomain.com/api/newsletter/health
```

---

**Deployment Status:** ✅ Production Ready  
**Last Updated:** January 2024  
**Version:** 2.0.0
