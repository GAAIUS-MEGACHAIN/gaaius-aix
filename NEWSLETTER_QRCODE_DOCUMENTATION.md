# Newsletter & QR Code Integration Documentation

## Overview

The gaaius-ai platform includes two enterprise-grade modules: **Newsletter Management** and **QR Code Generation & Tracking**. Both services are fully integrated into the frontend and backend with complete REST APIs, database models, and UI components.

---

## 1. Architecture Overview

### System Components

```
Frontend (React)
├── NewsletterDashboard.jsx       → /newsletter route
├── QRCodeDashboard.jsx           → /qrcode route
└── UI Components

Backend (FastAPI)
├── newsletter_service.py         → /api/newsletter routes
├── qrcode_service.py             → /api/qrcode routes
├── qrcode_ai_enhancements.py     → AI-powered QR features
└── Database Models (MongoDB)
```

---

## 2. Newsletter Module

### 2.1 Backend Service: `newsletter_service.py`

**Location:** `backend/newsletter_service.py`  
**Prefix:** `/api/newsletter`  
**Database:** MongoDB  
**Status:** ✅ Production Ready

#### Data Models

##### Subscriber Model
```python
{
    "email": "user@example.com",        # Required, unique
    "name": "John Doe",                 # Required
    "phone": "+1234567890",             # Optional
    "tags": ["vip", "beta"],            # Array of tags
    "segments": ["premium"],            # Array of segments
    "custom_fields": {                  # Dynamic custom fields
        "company": "ACME Corp",
        "location": "New York"
    },
    "status": "active",                 # active, unsubscribed, bounced
    "subscribed_date": "2024-01-15T...",
    "last_engagement": "2024-01-20T...",
    "open_count": 15,
    "click_count": 8
}
```

##### Email Template Model
```python
{
    "name": "Welcome Email",
    "subject": "Welcome to {{company_name}}, {{name}}!",
    "preview_text": "Get started with our platform",
    "html_content": "<h1>Hello {{name}}</h1>...",
    "text_content": "Hello {{name}}...",
    "variables": ["name", "company_name"],  # Template variables
    "thumbnail": "base64_image_data",
    "category": "custom",
    "is_default": false
}
```

##### Campaign Model
```python
{
    "name": "Spring Campaign 2024",
    "template_id": "template_123",
    "subject": "Spring Sale - 50% Off!",
    "segment": {
        "segment_type": "tag_based",    # all, tag_based, engagement, custom
        "tags": ["vip", "active"],
        "engagement_filter": "high",
        "subscriber_count": 1250
    },
    "status": "draft",                  # draft, scheduled, sending, sent, paused, failed
    "schedule_time": "2024-02-01T09:00:00",
    "ab_test": {
        "enabled": true,
        "variant_a_subject": "Subject A",
        "variant_b_subject": "Subject B",
        "split_percentage": 50
    },
    "created_at": "2024-01-15T...",
    "sent_at": "2024-02-01T...",
    "stats": {
        "sent": 1250,
        "opens": 425,
        "clicks": 89,
        "conversions": 23,
        "bounces": 12,
        "unsubscribes": 5
    }
}
```

##### Automation Model
```python
{
    "name": "Welcome Series",
    "enabled": true,
    "trigger": {
        "type": "subscribe",            # subscribe, purchase, abandoned_cart, date, tag
        "conditions": {}
    },
    "actions": [
        {
            "delay": "0h",
            "email_id": "template_123"
        },
        {
            "delay": "24h",
            "email_id": "template_124"
        }
    ],
    "statistics": {
        "triggered": 342,
        "completed": 298,
        "opens": 145,
        "clicks": 42
    }
}
```

#### API Endpoints

##### Subscriber Management

| Method | Endpoint | Description | Required Body |
|--------|----------|-------------|--------------|
| POST | `/api/newsletter/subscribers` | Add new subscriber | `{email, name, tags?, segments?, custom_fields?}` |
| GET | `/api/newsletter/subscribers` | List all subscribers | Query: `?status=active&tags=vip&limit=50&skip=0` |
| POST | `/api/newsletter/subscribers/import` | Bulk import subscribers | CSV file or JSON array |
| PUT | `/api/newsletter/subscribers/{email}` | Update subscriber | `{name?, tags?, status?, custom_fields?}` |
| DELETE | `/api/newsletter/subscribers/{email}` | Unsubscribe/delete | - |

##### Campaign Management

| Method | Endpoint | Description | Required Body |
|--------|----------|-------------|--------------|
| POST | `/api/newsletter/campaigns` | Create campaign | `{name, template_id, subject, segment, ab_test?}` |
| GET | `/api/newsletter/campaigns` | List campaigns | Query: `?status=sent&limit=50&skip=0` |
| POST | `/api/newsletter/campaigns/{campaign_id}/schedule` | Schedule campaign | `{schedule_time: ISO8601}` |
| POST | `/api/newsletter/campaigns/{campaign_id}/send` | Send immediately | - |
| GET | `/api/newsletter/campaigns/{campaign_id}/analytics` | Get campaign stats | - |

##### Automation Management

| Method | Endpoint | Description | Required Body |
|--------|----------|-------------|--------------|
| POST | `/api/newsletter/automations` | Create automation | `{name, trigger, actions, enabled}` |
| GET | `/api/newsletter/automations` | List automations | Query: `?enabled=true&limit=50` |

##### Analytics & Settings

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/newsletter/analytics/overview` | Dashboard overview |
| POST | `/api/newsletter/settings/smtp` | Configure SMTP settings |
| GET | `/api/newsletter/settings/smtp` | Get SMTP settings |
| GET | `/api/newsletter/health` | Service health check |

#### Enums

```python
CampaignStatus: DRAFT, SCHEDULED, SENDING, SENT, PAUSED, FAILED
SegmentType: ALL, TAG_BASED, ENGAGEMENT, CUSTOM
AutomationTrigger: SUBSCRIBE, PURCHASE, ABANDONED_CART, DATE, TAG
```

### 2.2 Frontend Component: `NewsletterDashboard.jsx`

**Location:** `frontend/src/components/NewsletterDashboard.jsx`  
**Route:** `/newsletter`  
**Status:** ✅ Ready

#### Features
- 📧 Subscriber management interface
- 📧 Campaign creation and scheduling
- 📊 Real-time analytics dashboard
- 🔄 Automation workflow builder
- 📁 Template management
- 📥 Bulk import/export

#### UI Sections
1. **Subscribers Tab**
   - View all subscribers with filtering
   - Add/edit/remove subscribers
   - Bulk actions
   - Segmentation preview

2. **Campaigns Tab**
   - Create new campaigns
   - Template selection
   - Recipient segmentation
   - A/B test configuration
   - Schedule or send immediately
   - Campaign performance metrics

3. **Automations Tab**
   - Visual automation builder
   - Trigger configuration
   - Email sequence setup
   - Automation performance

4. **Analytics Tab**
   - Open rates
   - Click rates
   - Conversion tracking
   - Subscriber growth
   - Engagement metrics

---

## 3. QR Code Module

### 3.1 Backend Service: `qrcode_service.py`

**Location:** `backend/qrcode_service.py`  
**Prefix:** `/api/qrcode`  
**Database:** MongoDB  
**Status:** ✅ Production Ready

#### Data Models

##### QR Code Design Configuration
```python
{
    "color_dark": "#000000",           # Dark color (dark modules)
    "color_light": "#FFFFFF",          # Light color (light modules)
    "logo_url": "https://...",         # Optional logo overlay
    "pattern_type": "rounded",         # square, circle, rounded
    "border_size": 4,                  # Border (quiet zone)
    "error_correction": "H"            # L, M, Q, H (error correction level)
}
```

##### QR Code Metadata
```python
{
    "type": "url",                     # url, vcard, sms, email, wifi, event, etc.
    "title": "My Product Link",
    "description": "Product QR code",
    "campaign_name": "Spring Sale",
    "tags": ["product", "sale"],
    "expires_at": "2024-12-31T23:59:59",
    "redirect_url": "https://example.com/product",
    "landing_page": "https://example.com/landing"
}
```

##### QR Code Model (URL Type)
```python
{
    "_id": "qr_123abc",
    "url": "https://example.com/product",
    "short_code": "ab12cd",            # For short URL: qr.example.com/ab12cd
    "metadata": { ... },               # See metadata above
    "design": { ... },                 # See design config above
    "static": true,                    # Does not change after creation
    "tracking_enabled": true,
    "status": "active",                # active, paused, archived, expired
    "created_at": "2024-01-15T...",
    "updated_at": "2024-01-20T...",
    "analytics": {
        "scans": 1250,
        "unique_scans": 847,
        "first_scan": "2024-01-16T...",
        "last_scan": "2024-01-20T...",
        "devices": {
            "ios": 420,
            "android": 350,
            "desktop": 77
        },
        "locations": [
            {"country": "US", "scans": 600},
            {"country": "UK", "scans": 150}
        ],
        "referrers": {
            "direct": 500,
            "instagram": 300,
            "facebook": 200,
            "twitter": 250
        ]
    }
}
```

##### VCard (Contact) Model
```python
{
    "name": "John Doe",
    "phone": "+1-800-123-4567",
    "email": "john@example.com",
    "organization": "ACME Corp",
    "url": "https://johndoe.com",
    "address": "123 Main St, New York, NY",
    "note": "CEO"
}
```

##### WiFi Configuration
```python
{
    "ssid": "MyNetwork",
    "password": "secure_password",
    "security": "WPA"                  # OPEN, WEP, WPA
}
```

#### API Endpoints

##### QR Code Generation & Management

| Method | Endpoint | Description | Request Body |
|--------|----------|-------------|--------------|
| POST | `/api/qrcode/generate` | Generate QR code | `{type, url/data, design?, metadata?, tracking_enabled?}` |
| GET | `/api/qrcode/list` | List QR codes | Query: `?status=active&tags=sale&limit=50&skip=0` |
| GET | `/api/qrcode/{qr_id}` | Get QR code details | - |
| GET | `/api/qrcode/short/{short_code}` | Lookup by short code | - |
| PUT | `/api/qrcode/{qr_id}` | Update QR code | `{design?, metadata?, status?}` |
| DELETE | `/api/qrcode/{qr_id}` | Delete QR code | - |

##### Analytics & Tracking

| Method | Endpoint | Description | Request Body |
|--------|----------|-------------|--------------|
| POST | `/api/qrcode/{qr_id}/scan` | Record scan event | `{user_agent, ip_address?, location?}` |
| GET | `/api/qrcode/{qr_id}/analytics` | Get analytics data | Query: `?metric=scans&period=30d` |

##### Batch Operations

| Method | Endpoint | Description | Request Body |
|--------|----------|-------------|--------------|
| POST | `/api/qrcode/batch/create` | Bulk create QR codes | `{count, template, metadata_template}` |
| GET | `/api/qrcode/batch/list` | List batches | Query: `?limit=50` |
| GET | `/api/qrcode/batch/{batch_id}` | Get batch details | - |

##### Health

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/qrcode/health` | Service health check |

#### QR Code Types Supported

```python
URL          # Simple URL redirect
VCARD        # Contact information
SMS          # SMS message
EMAIL        # Email address
WIFI         # WiFi network connection
EVENT        # Calendar event
PRODUCT      # E-commerce product
COUPON       # Discount coupon
PAYMENT      # Payment link
SOCIAL       # Social media profile
```

#### Enums

```python
QRCodeFormat: PNG, SVG, PDF, EPS
TrackingStatus: ACTIVE, PAUSED, ARCHIVED, EXPIRED
AnalyticsMetric: SCANS, UNIQUE_SCANS, DEVICES, LOCATIONS, REFERRERS
```

### 3.2 QR Code AI Enhancements: `qrcode_ai_enhancements.py`

**Location:** `backend/qrcode_ai_enhancements.py`  
**Status:** ✅ AI-Powered Features

#### Capabilities
- 🤖 Intelligent design recommendations
- 🎨 Color palette generation
- 📊 Performance predictions
- 💡 Content optimization suggestions
- 🔍 Pattern recognition for QR effectiveness

### 3.3 Frontend Component: `QRCodeDashboard.jsx`

**Location:** `frontend/src/components/QRCodeDashboard.jsx`  
**Route:** `/qrcode`  
**Status:** ✅ Ready

#### Features
- 🔲 QR code generator with real-time preview
- 🎨 Advanced design customization
- 📊 Comprehensive analytics dashboard
- 📱 Device-specific tracking
- 🌍 Geolocation analytics
- 🏷️ Batch generation and management
- 📥 Export in multiple formats

#### UI Sections

1. **Generator Tab**
   - QR code type selection (URL, VCard, WiFi, etc.)
   - Content input
   - Design customization (colors, patterns, logo)
   - Real-time preview
   - Download/export options

2. **QR Code Library Tab**
   - View all generated QR codes
   - Search and filter
   - Bulk actions
   - Quick edit functionality

3. **Analytics Tab**
   - Total scans over time
   - Unique vs. total scans
   - Device breakdown (iOS, Android, Desktop)
   - Geographic distribution
   - Referrer sources
   - Engagement metrics

4. **Batch Manager Tab**
   - Create batch campaigns
   - Template-based generation
   - Bulk download
   - Batch analytics

---

## 4. Database Schema

### Newsletter Collections

#### subscribers
```
{
    _id: ObjectId,
    email: String (unique),
    name: String,
    phone: String,
    tags: Array<String>,
    segments: Array<String>,
    custom_fields: Object,
    status: String,
    subscribed_date: Date,
    last_engagement: Date,
    open_count: Number,
    click_count: Number,
    created_at: Date,
    updated_at: Date
}
```

#### campaigns
```
{
    _id: ObjectId,
    name: String,
    template_id: ObjectId,
    subject: String,
    segment: Object,
    status: String,
    schedule_time: Date,
    sent_at: Date,
    stats: Object,
    ab_test: Object,
    created_at: Date,
    updated_at: Date
}
```

#### automations
```
{
    _id: ObjectId,
    name: String,
    trigger: Object,
    actions: Array,
    enabled: Boolean,
    statistics: Object,
    created_at: Date,
    updated_at: Date
}
```

### QR Code Collections

#### qrcodes
```
{
    _id: ObjectId,
    url: String,
    short_code: String,
    type: String,
    metadata: Object,
    design: Object,
    static: Boolean,
    tracking_enabled: Boolean,
    status: String,
    analytics: Object,
    created_at: Date,
    updated_at: Date
}
```

#### qrcode_scans
```
{
    _id: ObjectId,
    qrcode_id: ObjectId,
    timestamp: Date,
    user_agent: String,
    ip_address: String,
    country: String,
    city: String,
    device_type: String,
    os: String,
    browser: String,
    referrer: String
}
```

#### qrcode_batches
```
{
    _id: ObjectId,
    name: String,
    count: Number,
    template: Object,
    qrcodes: Array<ObjectId>,
    status: String,
    created_at: Date,
    completed_at: Date
}
```

---

## 5. Integration Points

### Frontend Routes

```typescript
// Newsletter
navigate("/newsletter")     // Full newsletter dashboard

// QR Code
navigate("/qrcode")         // Full QR code dashboard
```

### Backend Routes Registration (server.py)

```python
# Lines 84-86: Import routers
from .newsletter_service import router as newsletter_router
from .qrcode_service import router as qrcode_router
from .qrcode_ai_enhancements import router as qrcode_ai_router

# Lines 10013-10035: Register routers
app.include_router(newsletter_router)
app.include_router(qrcode_router)
app.include_router(qrcode_ai_router)
```

### API Client Configuration

The frontend uses a configured `api` instance (axios-based) with:
- Base URL: Backend server URL
- Authentication: JWT token support
- Error handling: Automatic error interception
- CORS: Enabled for cross-origin requests

---

## 6. Authentication & Authorization

Both modules integrate with the platform's authentication system:

- **Required:** JWT token in Authorization header
- **Format:** `Authorization: Bearer <token>`
- **Validation:** Server-side JWT verification
- **Scope:** User-specific data isolation

---

## 7. Error Handling

### Common HTTP Status Codes

| Status | Meaning | Example |
|--------|---------|---------|
| 200 | Success | Campaign sent successfully |
| 201 | Created | New QR code generated |
| 400 | Bad Request | Missing required fields |
| 401 | Unauthorized | Invalid or expired token |
| 404 | Not Found | QR code or campaign not found |
| 409 | Conflict | Duplicate email subscriber |
| 500 | Server Error | Database connection error |

### Error Response Format

```json
{
    "detail": "Error message describing what went wrong",
    "error_code": "INVALID_EMAIL",
    "timestamp": "2024-01-20T10:30:00Z"
}
```

---

## 8. Rate Limiting & Quotas

### Newsletter Service
- **Subscriber import:** 10,000 per batch
- **Campaign sending:** 100,000 emails per hour
- **API calls:** 1,000 requests per minute

### QR Code Service
- **QR generation:** 10,000 per day
- **Batch creation:** 1,000 per batch
- **API calls:** 2,000 requests per minute

---

## 9. Usage Examples

### Newsletter: Create & Send Campaign

```bash
# 1. Create campaign
POST /api/newsletter/campaigns
{
    "name": "Spring Sale",
    "template_id": "template_123",
    "subject": "50% Off Spring Collection!",
    "segment": {
        "segment_type": "tag_based",
        "tags": ["fashion", "active"]
    }
}

# 2. Schedule for later
POST /api/newsletter/campaigns/{campaign_id}/schedule
{
    "schedule_time": "2024-02-15T09:00:00Z"
}

# Or send immediately
POST /api/newsletter/campaigns/{campaign_id}/send

# 3. Get analytics
GET /api/newsletter/campaigns/{campaign_id}/analytics
```

### QR Code: Generate & Track

```bash
# 1. Generate QR code
POST /api/qrcode/generate
{
    "type": "url",
    "url": "https://mystore.com/product/123",
    "metadata": {
        "title": "Product Link",
        "campaign_name": "Spring 2024",
        "tags": ["product", "sale"]
    },
    "design": {
        "color_dark": "#1a1a1a",
        "pattern_type": "rounded"
    },
    "tracking_enabled": true
}

# 2. Get analytics
GET /api/qrcode/{qr_id}/analytics?metric=scans&period=30d

# 3. Batch create (e.g., for product catalog)
POST /api/qrcode/batch/create
{
    "count": 100,
    "template": {
        "design": { ... },
        "campaign_name": "Product Catalog"
    }
}
```

---

## 10. Performance Considerations

### Optimizations Implemented

- **Database Indexing:** Indexed on email, status, created_at
- **Caching:** Redis caching for frequently accessed data
- **Pagination:** All list endpoints support limit/skip
- **Batch Operations:** Bulk actions for improved throughput
- **Analytics:** Incremental aggregation to avoid recalculation

### Monitoring

- Health check endpoints: `/api/newsletter/health`, `/api/qrcode/health`
- Metrics tracking for performance
- Error logging with timestamps
- Audit trails for all actions

---

## 11. Deployment Checklist

- ✅ Backend services deployed and accessible
- ✅ Frontend components compiled and bundled
- ✅ Database collections created with proper indexing
- ✅ SMTP credentials configured for newsletter
- ✅ Environment variables set (.env file)
- ✅ API endpoints registered with CORS
- ✅ Authentication system integrated
- ✅ Rate limiting configured
- ✅ Error handling tested
- ✅ Analytics tracking enabled

---

## 12. Troubleshooting

### Newsletter Service Not Responding

1. Check service status: `GET /api/newsletter/health`
2. Verify database connection: Check MongoDB logs
3. Verify SMTP configuration: `GET /api/newsletter/settings/smtp`
4. Check application logs: `backend/logs/`

### QR Codes Not Generating

1. Check service status: `GET /api/qrcode/health`
2. Verify qrcode library: `pip list | grep qrcode`
3. Check MongoDB connection
4. Verify design parameters are valid

### Analytics Not Showing

1. Ensure tracking_enabled=true when generating QR codes
2. Check analytics aggregation job status
3. Verify MongoDB has scan records: db.qrcode_scans.count()

---

## 13. API Documentation Links

- **Interactive Docs (Swagger):** `http://localhost:8000/docs`
- **Alternative Docs (ReDoc):** `http://localhost:8000/redoc`

---

## 14. Contact & Support

- **Backend Issues:** Check `backend/server.py` logs
- **Frontend Issues:** Check browser console and `frontend/logs/`
- **Database Issues:** Check MongoDB connection string in `.env`

---

**Last Updated:** January 2024  
**Status:** ✅ Production Ready  
**Version:** 2.0.0
