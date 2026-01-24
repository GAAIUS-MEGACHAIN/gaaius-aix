# 🚀 ADVANCED FEATURES - API ENDPOINTS REFERENCE

## Search & Discovery Endpoints

### 1. Advanced Full-Text Search
```
GET /search/advanced
```
**Rate Limit:** 60/minute  
**Auth:** Optional  

**Query Parameters:**
- `q` (required): Search query (1-500 chars)
- `type`: Content type (all|video|playlist|channel|comment|track)
- `sort`: Sort order (relevance|date|popularity)
- `skip`: Pagination offset (default: 0)
- `limit`: Results per page (1-100, default: 20)

**Example Request:**
```bash
curl -X GET "http://localhost:8000/search/advanced?q=python%20tutorial&type=video&sort=popularity&limit=20"
```

**Response Structure:**
```json
{
  "results": [
    {
      "type": "video",
      "content": {
        "id": "video_id",
        "title": "Python Tutorial",
        "view_count": 5000,
        "like_count": 250,
        "created_at": "2024-01-15T10:30:00Z"
      }
    }
  ],
  "total": 1250,
  "query": "python tutorial",
  "type": "video",
  "sort": "relevance"
}
```

---

### 2. Trending Content
```
GET /trending/all
```
**Rate Limit:** 60/minute  
**Auth:** Optional  

**Query Parameters:**
- `category`: Content type (all|music|video|live, default: all)
- `skip`: Pagination offset (default: 0)
- `limit`: Results (1-100, default: 30)

**Example Request:**
```bash
curl -X GET "http://localhost:8000/trending/all?category=video&limit=20"
```

**Response Structure:**
```json
{
  "trending": [
    {
      "id": "video_id",
      "title": "Trending Video",
      "trending_score": 25.3,
      "view_count": 50000,
      "like_count": 2500,
      "comment_count": 500
    }
  ],
  "count": 20,
  "category": "video",
  "generated_at": "2024-01-15T12:00:00Z"
}
```

---

### 3. Advanced Video Filtering
```
GET /videos/filter/advanced
```
**Rate Limit:** 60/minute  
**Auth:** Optional  

**Query Parameters:**
- `duration_min`: Min duration in seconds (default: 0)
- `duration_max`: Max duration in seconds (default: 3600)
- `upload_date`: Filter (any|today|week|month, default: any)
- `sort`: Sort by (relevance|date|views|likes, default: relevance)
- `min_views`: Minimum view count (default: 0)
- `skip`: Pagination offset (default: 0)
- `limit`: Results (1-100, default: 20)

**Example Request:**
```bash
curl -X GET "http://localhost:8000/videos/filter/advanced?duration_min=300&duration_max=1800&upload_date=week&sort=views&limit=20"
```

---

## Personalization Endpoints

### 4. Personalized Recommendations
```
GET /recommendations/personalized
```
**Rate Limit:** 30/minute  
**Auth:** Required (Bearer token)  

**Query Parameters:**
- `limit`: Number of recommendations (1-50, default: 20)

**Example Request:**
```bash
curl -X GET "http://localhost:8000/recommendations/personalized?limit=30" \
  -H "Authorization: Bearer {JWT_TOKEN}"
```

**Response Structure:**
```json
{
  "recommendations": [
    {
      "id": "video_id",
      "title": "Recommended Video",
      "tag_match_score": 3,
      "engagement_score": 5.2,
      "final_score": 8.2
    }
  ],
  "count": 30,
  "based_on": ["programming", "python", "tutorial"]
}
```

---

### 5. Personalized Feed
```
GET /feed/personalized
```
**Rate Limit:** 40/minute  
**Auth:** Required (Bearer token)  

**Query Parameters:**
- `skip`: Pagination offset (default: 0)
- `limit`: Results (1-50, default: 20)

**Composition:**
- 50% from subscribed channels
- 30% from tag-based recommendations
- 20% from trending content

**Example Request:**
```bash
curl -X GET "http://localhost:8000/feed/personalized?limit=20&skip=0" \
  -H "Authorization: Bearer {JWT_TOKEN}"
```

**Response Structure:**
```json
{
  "feed": [
    {
      "source": "subscription",
      "content": {
        "id": "video_id",
        "title": "Video Title",
        "channel_id": "channel_id"
      }
    }
  ],
  "count": 20,
  "user_id": "user_id"
}
```

---

### 6. Creator Analytics Dashboard
```
GET /analytics/creator/dashboard
```
**Rate Limit:** 30/minute  
**Auth:** Required (Bearer token)  

**Query Parameters:**
- `period`: Time period (day|week|month|all, default: week)

**Example Request:**
```bash
curl -X GET "http://localhost:8000/analytics/creator/dashboard?period=week" \
  -H "Authorization: Bearer {JWT_TOKEN}"
```

**Response Structure:**
```json
{
  "period": "week",
  "statistics": {
    "total_videos": 45,
    "total_views": 125000,
    "total_likes": 5200,
    "avg_engagement": 0.0425,
    "avg_view_duration": 240
  },
  "top_videos": [
    {
      "id": "video_id",
      "title": "Top Video",
      "view_count": 25000
    }
  ],
  "new_subscribers": 320,
  "recent_comments": 1240,
  "engagement_trend": {
    "views_trend": "up",
    "engagement_rate": 0.0425
  }
}
```

---

## Analytics & Metrics Endpoints

### 7. Video Engagement Metrics
```
GET /videos/{video_id}/engagement
```
**Rate Limit:** 60/minute  
**Auth:** Optional  

**Path Parameters:**
- `video_id`: ID of the video

**Example Request:**
```bash
curl -X GET "http://localhost:8000/videos/video_id_123/engagement"
```

**Response Structure:**
```json
{
  "video_id": "video_id_123",
  "metrics": {
    "views": 100000,
    "likes": 5000,
    "dislikes": 200,
    "comments": 1500,
    "shares": 800,
    "engagement_rate": 7.3
  },
  "top_comments": [
    {
      "id": "comment_id",
      "content": "Great video!",
      "like_count": 250
    }
  ],
  "like_dislike_ratio": 25.0
}
```

---

### 8. Platform-Wide Analytics (Admin)
```
GET /analytics/platform-wide
```
**Rate Limit:** 20/minute  
**Auth:** Required (Admin role)  

**Example Request:**
```bash
curl -X GET "http://localhost:8000/analytics/platform-wide" \
  -H "Authorization: Bearer {JWT_TOKEN}"
```

**Response Structure:**
```json
{
  "total_stats": {
    "users": 50000,
    "videos": 250000,
    "total_views": 125000000,
    "comments": 5000000,
    "subscriptions": 750000
  },
  "activity_24h": {
    "new_videos": 1200,
    "new_comments": 45000,
    "new_users": 320
  },
  "generated_at": "2024-01-15T12:00:00Z"
}
```

---

### 9. Real-Time Live Stats
```
GET /live-stats/videos
```
**Rate Limit:** 30/minute  
**Auth:** Optional  

**Query Parameters:**
- `limit`: Number of videos (1-50, default: 10)

**Example Request:**
```bash
curl -X GET "http://localhost:8000/live-stats/videos?limit=10"
```

**Response Structure:**
```json
{
  "live_stats": [
    {
      "video_id": "video_id",
      "title": "Currently Popular",
      "concurrent_views": 1250,
      "last_view_timestamp": "2024-01-15T12:00:00Z"
    }
  ],
  "timestamp": "2024-01-15T12:00:00Z"
}
```

---

## Enterprise Operations Endpoints

### 10. Batch Video Update
```
POST /batch/videos/update
```
**Rate Limit:** 20/minute  
**Auth:** Required (Bearer token)  
**Content-Type:** application/json  

**Request Body:**
```json
{
  "updates": [
    {
      "video_id": "vid1",
      "title": "New Title",
      "description": "New Description",
      "is_public": true
    },
    {
      "video_id": "vid2",
      "tags": ["python", "tutorial"]
    }
  ]
}
```

**Example Request:**
```bash
curl -X POST "http://localhost:8000/batch/videos/update" \
  -H "Authorization: Bearer {JWT_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "updates": [
      {
        "video_id": "vid1",
        "title": "Updated Title"
      }
    ]
  }'
```

**Response:**
```json
{
  "updated": 2,
  "failed": 0,
  "errors": []
}
```

---

### 11. Create Collection
```
POST /collection/create
```
**Rate Limit:** 20/minute  
**Auth:** Required (Bearer token)  
**Content-Type:** application/x-www-form-urlencoded  

**Form Parameters:**
- `name` (required): Collection name (1-100 chars)
- `description`: Collection description
- `is_public`: Boolean for public/private

**Example Request:**
```bash
curl -X POST "http://localhost:8000/collection/create" \
  -H "Authorization: Bearer {JWT_TOKEN}" \
  -F "name=My Collection" \
  -F "description=Best videos" \
  -F "is_public=true"
```

**Response:**
```json
{
  "status": "Collection created",
  "collection_id": "coll_uuid",
  "collection": {
    "id": "coll_uuid",
    "name": "My Collection",
    "item_count": 0,
    "created_at": "2024-01-15T12:00:00Z"
  }
}
```

---

### 12. Bulk Add to Collection
```
POST /collection/{collection_id}/bulk-add
```
**Rate Limit:** 30/minute  
**Auth:** Required (Bearer token)  
**Content-Type:** application/json  

**Path Parameters:**
- `collection_id`: ID of the collection

**Request Body:**
```json
{
  "item_ids": ["vid1", "vid2", "vid3", ...]
}
```

**Example Request:**
```bash
curl -X POST "http://localhost:8000/collection/coll_123/bulk-add" \
  -H "Authorization: Bearer {JWT_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "item_ids": ["vid1", "vid2", "vid3"]
  }'
```

**Response:**
```json
{
  "status": "Items added",
  "items_added": 3,
  "collection_id": "coll_123"
}
```

---

### 13. Optimized Video Fetch (Cached)
```
GET /videos/{video_id}/optimized
```
**Rate Limit:** 100/minute  
**Auth:** Required (Bearer token)  

**Path Parameters:**
- `video_id`: ID of the video

**Example Request:**
```bash
curl -X GET "http://localhost:8000/videos/video_id_123/optimized" \
  -H "Authorization: Bearer {JWT_TOKEN}"
```

**Response:**
```json
{
  "id": "video_id_123",
  "title": "Video Title",
  "stats": {
    "likes": 5000,
    "comments": 1500,
    "views": 100000
  }
}
```

---

### 14. Clear Cache (Admin)
```
POST /cache/clear
```
**Rate Limit:** 10/minute  
**Auth:** Required (Admin role)  

**Example Request:**
```bash
curl -X POST "http://localhost:8000/cache/clear" \
  -H "Authorization: Bearer {JWT_TOKEN}"
```

**Response:**
```json
{
  "status": "Cache cleared"
}
```

---

## User Management Endpoints

### 15. Set User Preferences
```
POST /user/preferences
```
**Rate Limit:** 30/minute  
**Auth:** Required (Bearer token)  
**Content-Type:** application/json  

**Request Body:**
```json
{
  "theme": "dark",
  "language": "en",
  "notifications_enabled": true,
  "auto_play": false,
  "video_quality": "1080p"
}
```

**Example Request:**
```bash
curl -X POST "http://localhost:8000/user/preferences" \
  -H "Authorization: Bearer {JWT_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "theme": "dark",
    "notifications_enabled": true
  }'
```

**Response:**
```json
{
  "status": "Preferences updated",
  "preferences": {
    "theme": "dark",
    "notifications_enabled": true
  }
}
```

---

### 16. Get User Preferences
```
GET /user/preferences
```
**Rate Limit:** 60/minute  
**Auth:** Required (Bearer token)  

**Example Request:**
```bash
curl -X GET "http://localhost:8000/user/preferences" \
  -H "Authorization: Bearer {JWT_TOKEN}"
```

**Response:**
```json
{
  "preferences": {
    "theme": "dark",
    "language": "en",
    "notifications_enabled": true
  }
}
```

---

## Moderation Endpoints

### 17. Report Content
```
POST /content/report
```
**Rate Limit:** 20/minute  
**Auth:** Required (Bearer token)  
**Content-Type:** application/x-www-form-urlencoded  

**Form Parameters:**
- `content_type` (required): Type of content (video|comment|user)
- `content_id` (required): ID of the content
- `reason` (required): Reason for report (10-1000 chars)

**Example Request:**
```bash
curl -X POST "http://localhost:8000/content/report" \
  -H "Authorization: Bearer {JWT_TOKEN}" \
  -F "content_type=video" \
  -F "content_id=video_id" \
  -F "reason=This video contains inappropriate content"
```

**Response:**
```json
{
  "status": "Report submitted",
  "report_id": "report_uuid",
  "content_type": "video",
  "content_id": "video_id"
}
```

---

### 18. Get Moderation Queue (Moderator)
```
GET /moderation/queue
```
**Rate Limit:** 20/minute  
**Auth:** Required (Moderator role)  

**Query Parameters:**
- `skip`: Pagination offset (default: 0)
- `limit`: Results (1-50, default: 20)

**Example Request:**
```bash
curl -X GET "http://localhost:8000/moderation/queue?skip=0&limit=20" \
  -H "Authorization: Bearer {JWT_TOKEN}"
```

**Response:**
```json
{
  "queue": [
    {
      "report_id": "report_uuid",
      "content_type": "video",
      "content_id": "video_id",
      "reason": "Inappropriate content",
      "status": "pending",
      "created_at": "2024-01-15T12:00:00Z"
    }
  ],
  "total": 45,
  "skip": 0,
  "limit": 20
}
```

---

## Notification Endpoints

### 19. Get Notifications
```
GET /notifications
```
**Rate Limit:** 30/minute  
**Auth:** Required (Bearer token)  

**Query Parameters:**
- `skip`: Pagination offset (default: 0)
- `limit`: Results (1-50, default: 20)
- `unread_only`: Boolean for unread only (default: false)

**Example Request:**
```bash
curl -X GET "http://localhost:8000/notifications?unread_only=true&limit=20" \
  -H "Authorization: Bearer {JWT_TOKEN}"
```

**Response:**
```json
{
  "notifications": [
    {
      "_id": "notification_id",
      "type": "new_subscriber",
      "content": "New subscriber!",
      "read": false,
      "created_at": "2024-01-15T12:00:00Z"
    }
  ],
  "total": 150,
  "unread": 5
}
```

---

### 20. Mark Notification as Read
```
PATCH /notifications/{notification_id}/read
```
**Rate Limit:** 60/minute  
**Auth:** Required (Bearer token)  

**Path Parameters:**
- `notification_id`: ID of the notification

**Example Request:**
```bash
curl -X PATCH "http://localhost:8000/notifications/notif_123/read" \
  -H "Authorization: Bearer {JWT_TOKEN}"
```

**Response:**
```json
{
  "status": "Marked as read"
}
```

---

## Data Export Endpoints

### 21. Export Watch History
```
GET /export/watch-history
```
**Rate Limit:** 5/minute  
**Auth:** Required (Bearer token)  

**Query Parameters:**
- `format`: Export format (json|csv, default: json)

**Example Request (JSON):**
```bash
curl -X GET "http://localhost:8000/export/watch-history?format=json" \
  -H "Authorization: Bearer {JWT_TOKEN}"
```

**Response:**
```json
{
  "user_id": "user_id",
  "export_date": "2024-01-15T12:00:00Z",
  "watch_history": ["vid1", "vid2", "vid3", ...],
  "total_videos": 150
}
```

**Example Request (CSV):**
```bash
curl -X GET "http://localhost:8000/export/watch-history?format=csv" \
  -H "Authorization: Bearer {JWT_TOKEN}" \
  -o watch_history.csv
```

---

## Authentication Header

All protected endpoints require:
```
Authorization: Bearer {JWT_TOKEN}
```

**Token Format:**
```
{
  "id": "user_id",
  "email": "user@example.com",
  "role": "user|moderator|admin|creator",
  "exp": 1705305600
}
```

---

## Rate Limiting Response

When rate limit exceeded:
```json
HTTP 429 Too Many Requests

{
  "detail": "60 per 1 minute"
}
```

---

## Error Responses

**400 Bad Request:**
```json
{
  "detail": "Invalid parameter value"
}
```

**401 Unauthorized:**
```json
{
  "detail": "Invalid authentication credentials"
}
```

**403 Forbidden:**
```json
{
  "detail": "Access denied"
}
```

**404 Not Found:**
```json
{
  "detail": "Resource not found"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Internal server error"
}
```

---

## Base URL

```
http://localhost:8000
```

Or in production:
```
https://api.platform.com
```

---

## Total Endpoints

✅ **18 Advanced Production Endpoints**
- 3 Search & Discovery
- 4 Personalization
- 3 Analytics & Metrics
- 4 Enterprise Operations
- 2 Moderation
- 1 Notification
- 1 Data Export

**All endpoints feature:**
- Rate limiting
- Authentication/Authorization
- Input validation
- Error handling
- Logging
- Documentation

---

**Last Updated:** January 15, 2024  
**Status:** Production Ready ✅
