# Newsletter & QR Code API Quick Reference

## Base URLs

- **Newsletter API:** `http://localhost:8000/api/newsletter`
- **QR Code API:** `http://localhost:8000/api/qrcode`
- **Interactive Docs:** `http://localhost:8000/docs`

---

## NEWSLETTER API

### Subscribers

#### Add Subscriber
```
POST /api/newsletter/subscribers
Content-Type: application/json

{
  "email": "john@example.com",
  "name": "John Doe",
  "phone": "+1234567890",
  "tags": ["vip", "beta"],
  "custom_fields": {"company": "ACME"}
}

Response: 201 Created
{
  "_id": "subscriber_id",
  "email": "john@example.com",
  "status": "active",
  "subscribed_date": "2024-01-20T10:30:00Z"
}
```

#### List Subscribers
```
GET /api/newsletter/subscribers?status=active&tags=vip&limit=50&skip=0

Response: 200 OK
{
  "subscribers": [...],
  "total": 1250,
  "limit": 50,
  "skip": 0
}
```

#### Update Subscriber
```
PUT /api/newsletter/subscribers/john@example.com
{
  "tags": ["vip", "premium"],
  "custom_fields": {"tier": "gold"}
}

Response: 200 OK
```

#### Delete Subscriber
```
DELETE /api/newsletter/subscribers/john@example.com

Response: 200 OK
```

#### Bulk Import
```
POST /api/newsletter/subscribers/import
Content-Type: multipart/form-data

[file: CSV or JSON file with subscriber data]

Response: 200 OK
{
  "imported": 1250,
  "failed": 3,
  "errors": [...]
}
```

---

### Campaigns

#### Create Campaign
```
POST /api/newsletter/campaigns
{
  "name": "Spring Sale 2024",
  "template_id": "template_123",
  "subject": "50% Off Everything!",
  "segment": {
    "segment_type": "tag_based",
    "tags": ["fashion"],
    "engagement_filter": "high"
  },
  "ab_test": {
    "enabled": true,
    "variant_a_subject": "Subject A",
    "variant_b_subject": "Subject B"
  }
}

Response: 201 Created
{
  "_id": "campaign_123",
  "status": "draft",
  "segment": {"subscriber_count": 5000}
}
```

#### List Campaigns
```
GET /api/newsletter/campaigns?status=sent&limit=20&skip=0

Response: 200 OK
{
  "campaigns": [...],
  "total": 145
}
```

#### Schedule Campaign
```
POST /api/newsletter/campaigns/campaign_123/schedule
{
  "schedule_time": "2024-02-15T09:00:00Z"
}

Response: 200 OK
{
  "campaign_id": "campaign_123",
  "status": "scheduled",
  "scheduled_for": "2024-02-15T09:00:00Z"
}
```

#### Send Campaign Now
```
POST /api/newsletter/campaigns/campaign_123/send

Response: 200 OK
{
  "campaign_id": "campaign_123",
  "status": "sending",
  "recipients": 5000
}
```

#### Get Campaign Analytics
```
GET /api/newsletter/campaigns/campaign_123/analytics

Response: 200 OK
{
  "campaign_id": "campaign_123",
  "stats": {
    "sent": 5000,
    "opens": 1250,
    "open_rate": "25%",
    "clicks": 340,
    "click_rate": "6.8%",
    "conversions": 52,
    "conversion_rate": "1.04%",
    "bounces": 15,
    "unsubscribes": 8
  }
}
```

---

### Automations

#### Create Automation
```
POST /api/newsletter/automations
{
  "name": "Welcome Series",
  "enabled": true,
  "trigger": {
    "type": "subscribe"
  },
  "actions": [
    {
      "delay": "0h",
      "email_id": "welcome_1"
    },
    {
      "delay": "24h",
      "email_id": "welcome_2"
    },
    {
      "delay": "72h",
      "email_id": "welcome_3"
    }
  ]
}

Response: 201 Created
{
  "_id": "automation_123",
  "status": "active"
}
```

#### List Automations
```
GET /api/newsletter/automations?enabled=true

Response: 200 OK
{
  "automations": [...]
}
```

---

### Analytics

#### Dashboard Overview
```
GET /api/newsletter/analytics/overview

Response: 200 OK
{
  "total_subscribers": 12500,
  "active_subscribers": 11800,
  "campaigns_sent": 145,
  "avg_open_rate": "22.5%",
  "avg_click_rate": "5.8%",
  "growth_this_month": 450,
  "top_campaigns": [...]
}
```

---

## QR CODE API

### Generate QR Code

#### URL QR Code
```
POST /api/qrcode/generate
{
  "type": "url",
  "url": "https://mystore.com/product/123",
  "metadata": {
    "title": "Product Link",
    "description": "My awesome product",
    "campaign_name": "Spring 2024",
    "tags": ["product", "sale"]
  },
  "design": {
    "color_dark": "#000000",
    "color_light": "#FFFFFF",
    "pattern_type": "rounded",
    "border_size": 4
  },
  "tracking_enabled": true
}

Response: 201 Created
{
  "_id": "qr_abc123",
  "url": "https://api.example.com/qr/qr_abc123.png",
  "short_code": "abc123",
  "short_url": "https://qr.example.com/abc123",
  "status": "active"
}
```

#### VCard QR Code
```
POST /api/qrcode/generate
{
  "type": "vcard",
  "data": {
    "name": "John Doe",
    "phone": "+1-800-123-4567",
    "email": "john@example.com",
    "organization": "ACME Corp",
    "url": "https://johndoe.com",
    "address": "123 Main St, NY"
  },
  "metadata": {
    "title": "Business Card"
  }
}

Response: 201 Created
```

#### WiFi QR Code
```
POST /api/qrcode/generate
{
  "type": "wifi",
  "data": {
    "ssid": "MyNetwork",
    "password": "secure_pass",
    "security": "WPA"
  }
}

Response: 201 Created
```

---

### QR Code Management

#### List QR Codes
```
GET /api/qrcode/list?status=active&tags=sale&limit=50&skip=0

Response: 200 OK
{
  "qrcodes": [...],
  "total": 342
}
```

#### Get QR Code Details
```
GET /api/qrcode/qr_abc123

Response: 200 OK
{
  "_id": "qr_abc123",
  "url": "https://mystore.com/product/123",
  "short_code": "abc123",
  "type": "url",
  "status": "active",
  "tracking_enabled": true,
  "created_at": "2024-01-20T10:30:00Z",
  "analytics": {
    "scans": 1250,
    "unique_scans": 847
  }
}
```

#### Lookup by Short Code
```
GET /api/qrcode/short/abc123

Response: 200 OK
{
  "_id": "qr_abc123",
  ...full QR code object...
}
```

#### Update QR Code
```
PUT /api/qrcode/qr_abc123
{
  "status": "paused",
  "design": {
    "color_dark": "#1a1a1a"
  }
}

Response: 200 OK
```

#### Delete QR Code
```
DELETE /api/qrcode/qr_abc123

Response: 200 OK
```

---

### Tracking & Analytics

#### Record Scan
```
POST /api/qrcode/qr_abc123/scan
{
  "user_agent": "Mozilla/5.0...",
  "ip_address": "192.168.1.1",
  "location": {
    "country": "US",
    "city": "New York"
  }
}

Response: 200 OK
{
  "scan_id": "scan_xyz789",
  "recorded_at": "2024-01-20T10:35:00Z"
}
```

#### Get Analytics
```
GET /api/qrcode/qr_abc123/analytics?metric=scans&period=30d

Response: 200 OK
{
  "qr_id": "qr_abc123",
  "metrics": {
    "scans": 1250,
    "unique_scans": 847,
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
      "facebook": 200
    }
  }
}
```

---

### Batch Operations

#### Create Batch
```
POST /api/qrcode/batch/create
{
  "count": 100,
  "template": {
    "type": "url",
    "design": {
      "color_dark": "#000000"
    },
    "metadata": {
      "campaign_name": "Product Catalog",
      "tags": ["batch-2024-01"]
    }
  }
}

Response: 201 Created
{
  "batch_id": "batch_xyz789",
  "count": 100,
  "status": "processing"
}
```

#### List Batches
```
GET /api/qrcode/batch/list?limit=20

Response: 200 OK
{
  "batches": [...]
}
```

#### Get Batch Details
```
GET /api/qrcode/batch/batch_xyz789

Response: 200 OK
{
  "batch_id": "batch_xyz789",
  "count": 100,
  "status": "completed",
  "qrcodes": [
    {
      "_id": "qr_1",
      "short_code": "abc001"
    },
    ...
  ]
}
```

---

## Health Checks

### Newsletter Health
```
GET /api/newsletter/health

Response: 200 OK
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2024-01-20T10:30:00Z"
}
```

### QR Code Health
```
GET /api/qrcode/health

Response: 200 OK
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2024-01-20T10:30:00Z"
}
```

---

## Authentication

All requests require JWT token in header:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## Common Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK - Request successful |
| 201 | Created - Resource created |
| 400 | Bad Request - Invalid parameters |
| 401 | Unauthorized - Missing/invalid token |
| 404 | Not Found - Resource doesn't exist |
| 409 | Conflict - Resource already exists |
| 500 | Server Error |

---

## Error Response Format

```json
{
  "detail": "Descriptive error message",
  "error_code": "ERROR_TYPE",
  "timestamp": "2024-01-20T10:30:00Z"
}
```

---

## Query Parameters

### Common Pagination
- `limit`: Number of records (default: 50, max: 100)
- `skip`: Number to skip (default: 0)

### Filtering
- `status`: Filter by status
- `tags`: Filter by tags (comma-separated)
- `created_from`: From date (ISO 8601)
- `created_to`: To date (ISO 8601)

### Sorting
- `sort_by`: Field to sort by
- `sort_order`: "asc" or "desc"

---

## Examples with cURL

### Create Newsletter Subscriber
```bash
curl -X POST http://localhost:8000/api/newsletter/subscribers \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "name": "Test User",
    "tags": ["test"]
  }'
```

### Generate QR Code
```bash
curl -X POST http://localhost:8000/api/qrcode/generate \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "url",
    "url": "https://example.com",
    "tracking_enabled": true
  }'
```

### Get QR Analytics
```bash
curl -X GET http://localhost:8000/api/qrcode/qr_abc123/analytics \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Webhook Events (Coming Soon)

- `subscriber.subscribed` - New subscriber added
- `subscriber.unsubscribed` - Subscriber removed
- `campaign.sent` - Campaign delivery complete
- `qrcode.scanned` - QR code scanned
- `batch.completed` - Batch operation complete

---

**Last Updated:** January 2024
