# E-COMMERCE DEPLOYMENT GUIDE

## QUICK START

### 1. Install Dependencies
```bash
pip install -r backend/ecommerce_requirements.txt
```

### 2. Configure Environment
Create `.env` file in project root:

```env
# === STRIPE PAYMENT ===
STRIPE_API_KEY=sk_live_YOUR_LIVE_KEY
STRIPE_WEBHOOK_SECRET=whsec_YOUR_WEBHOOK_SECRET
STRIPE_PUBLISHABLE_KEY=pk_live_YOUR_PUBLISHABLE_KEY

# === PAYPAL PAYMENT ===
PAYPAL_MODE=live  # or sandbox for testing
PAYPAL_CLIENT_ID=YOUR_CLIENT_ID
PAYPAL_CLIENT_SECRET=YOUR_CLIENT_SECRET

# === AWS S3 (for product images, digital files) ===
AWS_ACCESS_KEY_ID=YOUR_ACCESS_KEY
AWS_SECRET_ACCESS_KEY=YOUR_SECRET_KEY
AWS_S3_BUCKET=gaaius-ecommerce-prod
AWS_REGION=us-east-1
AWS_S3_URL_EXPIRY=3600  # seconds

# === DATABASE ===
MONGODB_URL=mongodb+srv://user:password@cluster.mongodb.net/
MONGODB_DB=gaaius_ecommerce_prod

# === SECURITY ===
SECRET_KEY=your-super-secret-key-change-this
JWT_SECRET=your-jwt-secret-key
DOWNLOAD_SECRET=your-download-token-secret
JWT_ALGORITHM=HS256

# === ENVIRONMENT ===
ENV=production
DEBUG=False
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# === FEATURES ===
ENABLE_STRIPE=true
ENABLE_PAYPAL=true
ENABLE_DIGITAL_PRODUCTS=true
ENABLE_SUBSCRIPTIONS=true

# === TAX & SHIPPING ===
DEFAULT_TAX_RATE=0.08
SHIPPING_FLAT_RATE=10.00
FREE_SHIPPING_THRESHOLD=100.00

# === EMAIL (for order confirmations) ===
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM=noreply@yourdomain.com

# === LOGGING ===
LOG_LEVEL=INFO
LOG_FILE=logs/ecommerce.log

# === RATE LIMITING ===
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=3600  # seconds
```

### 3. Initialize Database

```bash
# Create MongoDB database and indexes
python -c "
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from backend.ecommerce_service import ECommerceService

async def init():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['gaaius_ecommerce_prod']
    service = ECommerceService(db)
    await service.init_indexes()
    print('✅ Database initialized')

asyncio.run(init())
"
```

### 4. Start Development Server

```bash
cd backend
uvicorn server:app --reload --port 8000
```

Access:
- **API**: http://localhost:8000/api/shop/
- **Docs**: http://localhost:8000/docs
- **Health**: http://localhost:8000/health

---

## PRODUCTION DEPLOYMENT

### Prerequisites
- Python 3.10+
- MongoDB Atlas or self-hosted MongoDB
- AWS S3 bucket
- Stripe account with API keys
- PayPal business account

### Option 1: Docker

Create `Dockerfile`:
```dockerfile
FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY backend/ecommerce_requirements.txt .
RUN pip install --no-cache-dir -r ecommerce_requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "backend.server:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

Build and run:
```bash
# Build
docker build -t gaaius-ecommerce:latest .

# Run with environment file
docker run -d \
  --name gaaius-ecommerce \
  --env-file .env \
  -p 8000:8000 \
  -v ./logs:/app/logs \
  gaaius-ecommerce:latest
```

### Option 2: Docker Compose

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  app:
    build: .
    container_name: gaaius-ecommerce
    ports:
      - "8000:8000"
    environment:
      - ENV=production
      - MONGODB_URL=mongodb://mongo:27017
      - MONGODB_DB=gaaius_ecommerce_prod
    env_file:
      - .env
    depends_on:
      - mongo
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped

  mongo:
    image: mongo:6.0
    container_name: gaaius-mongo
    environment:
      MONGO_INITDB_ROOT_USERNAME: root
      MONGO_INITDB_ROOT_PASSWORD: ${MONGODB_PASSWORD}
    volumes:
      - mongo_data:/data/db
    restart: unless-stopped

volumes:
  mongo_data:
```

Start services:
```bash
docker-compose up -d
```

### Option 3: Cloud Platforms

#### Heroku
```bash
# Login
heroku login

# Create app
heroku create gaaius-ecommerce

# Set environment variables
heroku config:set -a gaaius-ecommerce \
  STRIPE_API_KEY=sk_live_... \
  PAYPAL_CLIENT_ID=... \
  MONGODB_URL=...

# Deploy
git push heroku main

# View logs
heroku logs -a gaaius-ecommerce --tail
```

#### AWS EC2
```bash
# SSH into instance
ssh -i key.pem ubuntu@your-instance-ip

# Install dependencies
sudo apt-get update
sudo apt-get install python3.10 python3-pip mongodb-org

# Clone and setup
git clone https://github.com/yourusername/gaaius-ai.git
cd gaaius-ai
pip install -r backend/ecommerce_requirements.txt

# Create systemd service
sudo nano /etc/systemd/system/gaaius-ecommerce.service
```

Service file content:
```ini
[Unit]
Description=GAAIUS E-Commerce
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/gaaius-ai
Environment="PATH=/home/ubuntu/venv/bin"
ExecStart=/home/ubuntu/venv/bin/gunicorn \
    -w 4 \
    -k uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    backend.server:app

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Start service:
```bash
sudo systemctl daemon-reload
sudo systemctl start gaaius-ecommerce
sudo systemctl enable gaaius-ecommerce
```

---

## PAYMENT PROCESSOR SETUP

### Stripe Setup

1. **Create Stripe Account**
   - Visit https://dashboard.stripe.com
   - Sign up and verify email

2. **Get API Keys**
   - Navigate to Developers > API Keys
   - Copy Secret Key (sk_live_...)
   - Copy Publishable Key (pk_live_...)

3. **Configure Webhook**
   - Settings > Webhooks > Add Endpoint
   - URL: `https://yourdomain.com/api/shop/webhooks/stripe`
   - Events: `payment_intent.succeeded`, `payment_intent.payment_failed`, `charge.refunded`
   - Copy Signing Secret

4. **Add to .env**
```env
STRIPE_API_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

### PayPal Setup

1. **Create PayPal Account**
   - Visit https://developer.paypal.com
   - Sign up for business account

2. **Create App**
   - Apps & Credentials > Create App
   - Select "Merchant"
   - Copy Client ID and Secret

3. **Configure IPN**
   - Account Settings > Instant Payment Notifications
   - URL: `https://yourdomain.com/api/shop/webhooks/paypal`

4. **Add to .env**
```env
PAYPAL_MODE=live
PAYPAL_CLIENT_ID=...
PAYPAL_CLIENT_SECRET=...
```

---

## AWS S3 SETUP

### Create S3 Bucket

```bash
aws s3 mb s3://gaaius-ecommerce-prod

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket gaaius-ecommerce-prod \
  --versioning-configuration Status=Enabled

# Block public access
aws s3api put-public-access-block \
  --bucket gaaius-ecommerce-prod \
  --public-access-block-configuration \
  "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"
```

### Create IAM User

```bash
# Create user
aws iam create-user --user-name gaaius-ecommerce

# Create access key
aws iam create-access-key --user-name gaaius-ecommerce

# Attach policy
aws iam attach-user-policy \
  --user-name gaaius-ecommerce \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess
```

### Add to .env
```env
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_S3_BUCKET=gaaius-ecommerce-prod
AWS_REGION=us-east-1
```

---

## MONGODB SETUP

### MongoDB Atlas (Cloud - Recommended)

1. **Create Cluster**
   - Visit https://www.mongodb.com/cloud/atlas
   - Create free cluster

2. **Get Connection String**
   - Clusters > Connect > Connection String
   - Copy URI: `mongodb+srv://user:pass@cluster.mongodb.net/`

3. **Create Database User**
   - Database Access > Add New Database User
   - Username: `ecommerce_user`
   - Password: (strong password)
   - Add User

4. **Whitelist IP**
   - Network Access > Add IP Address
   - Allow 0.0.0.0/0 for development, specific IPs for production

5. **Add to .env**
```env
MONGODB_URL=mongodb+srv://ecommerce_user:password@cluster.mongodb.net/
MONGODB_DB=gaaius_ecommerce_prod
```

### MongoDB Community (Self-Hosted)

```bash
# Install MongoDB
sudo apt-get install mongodb-org

# Start service
sudo systemctl start mongod

# Verify
mongo --eval "db.version()"

# Create database user
mongo admin --eval "
  db.createUser({
    user: 'ecommerce_user',
    pwd: 'strong-password',
    roles: ['readWrite']
  })
"

# Add to .env
MONGODB_URL=mongodb://ecommerce_user:strong-password@localhost:27017/
MONGODB_DB=gaaius_ecommerce_prod
```

---

## MONITORING & LOGGING

### Application Logs

```bash
# View logs
tail -f logs/ecommerce.log

# Filter by level
grep ERROR logs/ecommerce.log

# Monitor in real-time
journalctl -u gaaius-ecommerce.service -f
```

### Error Tracking (Sentry)

1. Create account at https://sentry.io
2. Create project (Python > FastAPI)
3. Get DSN: `https://...@sentry.io/...`
4. Add to .env:
```env
SENTRY_DSN=https://...@sentry.io/...
SENTRY_ENVIRONMENT=production
```

### Application Monitoring

```python
# Check service health
curl http://localhost:8000/health

# Response:
{
    "status": "healthy",
    "database": "connected",
    "stripe": "configured",
    "paypal": "configured",
    "s3": "accessible"
}
```

---

## TESTING BEFORE PRODUCTION

### 1. Test Payment Processing

**Stripe Test Cards:**
```
Success: 4242 4242 4242 4242
Decline: 4000 0000 0000 0002
3D Secure: 4000 0000 0000 3220
```

**PayPal Test Accounts:**
- Sandbox: https://sandbox.paypal.com
- Use test credentials from developer account

### 2. Test Order Workflow

```bash
# 1. Create product
curl -X POST http://localhost:8000/api/shop/products \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Product",
    "description": "Testing",
    "category": "merchandise",
    "product_type": "physical",
    "base_price": 29.99,
    "images": [{"url": "https://example.com/img.jpg", "alt_text": "Test"}]
  }'

# 2. Publish product
curl -X POST "http://localhost:8000/api/shop/products/PRODUCT_ID/publish" \
  -H "Authorization: Bearer <token>"

# 3. Add to cart
curl -X POST "http://localhost:8000/api/shop/cart/add?product_id=PRODUCT_ID&quantity=1" \
  -H "Authorization: Bearer <token>"

# 4. Create order
curl -X POST http://localhost:8000/api/shop/checkout \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Test User",
    "email": "test@example.com",
    "phone": "555-0000",
    "street1": "123 Test St",
    "city": "Test City",
    "state": "TS",
    "postal_code": "12345",
    "country": "US",
    "payment_method": "stripe"
  }'

# 5. Process payment (use test card)
curl -X POST "http://localhost:8000/api/shop/payment/stripe?order_id=ORDER_ID&payment_method_id=pm_test" \
  -H "Authorization: Bearer <token>"
```

### 3. Run Test Suite

```bash
pytest backend/test_ecommerce.py -v --tb=short
```

---

## PERFORMANCE OPTIMIZATION

### Database Optimization

```python
# Verify indexes
mongo> db.orders.getIndexes()

# Monitor queries
mongo> db.setProfilingLevel(1)
```

### Caching Layer (Optional)

Add Redis for caching:
```python
import redis

cache = redis.Redis(host='localhost', port=6379, db=0)

# Cache product listings
cache.setex('products:page:1', 3600, json.dumps(products))
```

### Load Testing

```bash
# Using Apache Bench
ab -n 1000 -c 10 http://localhost:8000/api/shop/products

# Using wrk
wrk -t4 -c100 -d30s http://localhost:8000/api/shop/products
```

---

## SCALING FOR PRODUCTION

### Horizontal Scaling

```yaml
# docker-compose.yml with load balancer
version: '3.8'

services:
  nginx:
    image: nginx:latest
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - app1
      - app2
      - app3

  app1:
    build: .
    environment:
      - PORT=8001

  app2:
    build: .
    environment:
      - PORT=8002

  app3:
    build: .
    environment:
      - PORT=8003

  mongo:
    image: mongo:6.0
    volumes:
      - mongo_data:/data/db

volumes:
  mongo_data:
```

### Database Sharding

For very large scale, implement MongoDB sharding:
```bash
# Initialize sharded cluster
mongosh --port 27017 --eval "
  sh.addShard('rs0/localhost:27001')
  sh.enableSharding('gaaius_ecommerce_prod')
  sh.shardCollection('gaaius_ecommerce_prod.orders', { user_id: 1 })
"
```

---

## BACKUP & DISASTER RECOVERY

### MongoDB Backups

```bash
# Daily backup
mongodump --uri "mongodb+srv://user:pass@cluster/" --out ./backups/$(date +%Y%m%d)

# Restore from backup
mongorestore --uri "mongodb+srv://user:pass@cluster/" ./backups/20240120
```

### S3 Backups

```bash
# Sync S3 to local
aws s3 sync s3://gaaius-ecommerce-prod ./backups/s3/$(date +%Y%m%d)

# Cross-region backup
aws s3 sync s3://gaaius-ecommerce-prod s3://gaaius-ecommerce-backup/
```

---

## SECURITY CHECKLIST

- [ ] SSL/TLS certificate installed (HTTPS)
- [ ] Environment variables secured (not in code)
- [ ] Database authentication enabled
- [ ] S3 bucket policy restricts public access
- [ ] API keys rotated regularly
- [ ] Rate limiting enabled
- [ ] CORS origins restricted to your domain
- [ ] Webhook signatures verified
- [ ] PCI DSS compliance verified (Stripe/PayPal handle cards)
- [ ] Regular security audits performed
- [ ] Monitoring and alerting configured
- [ ] Incident response plan documented

---

## TROUBLESHOOTING

### Payment Processing Issues

```bash
# Check Stripe connectivity
curl -H "Authorization: Bearer sk_live_..." https://api.stripe.com/v1/balance

# Check PayPal connectivity
curl -X POST https://api.paypal.com/v1/oauth2/token \
  -u "client_id:secret" \
  -d "grant_type=client_credentials"
```

### Database Connection Issues

```bash
# Test MongoDB connection
mongosh "mongodb+srv://user:pass@cluster/"

# Check indexes
db.products.getIndexes()

# Repair collection
db.products.validate()
```

### S3 Upload Issues

```bash
# Test S3 access
aws s3 ls s3://gaaius-ecommerce-prod

# Check permissions
aws iam get-user --user-name gaaius-ecommerce
```

---

## NEXT STEPS

1. ✅ Configure all payment processors
2. ✅ Set up AWS S3
3. ✅ Configure MongoDB
4. ✅ Run test suite
5. ✅ Deploy to staging
6. ✅ Test payment workflows
7. ✅ Configure monitoring
8. ✅ Deploy to production
9. ✅ Monitor for issues

**Status**: Ready for production deployment
