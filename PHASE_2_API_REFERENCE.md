# PHASE 2 API REFERENCE - COMPLETE ENDPOINT GUIDE

## Quick Navigation

- [Live Streaming](#live-streaming-4-endpoints)
- [Monetization](#monetization-3-endpoints)
- [Premium Subscriptions](#premium-subscriptions-2-endpoints)
- [Social Features](#social-features-6-endpoints)
- [Direct Messaging](#direct-messaging-2-endpoints)
- [Hashtags & Trending](#hashtags--trending-2-endpoints)
- [Content Features](#content-features-2-endpoints)
- [Video Processing](#video-processing--encoding-2-endpoints)
- [Advanced Search](#advanced-search-2-endpoints)
- [Notifications](#notifications-2-endpoints)
- [User Profiles](#user-profile-enhancements-2-endpoints)
- [Content Moderation](#content-moderation-1-endpoint)
- [Smart Playlists](#smart-playlists-1-endpoint)

---

## Live Streaming (4 Endpoints)

### 1. Start Live Stream
**POST** `/live/stream/start`

```bash
curl -X POST "http://localhost:8000/live/stream/start" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "title=Live Gaming Session" \
  -F "description=Playing competitive games" \
  -F "is_public=true" \
  -F "category=gaming"
```

**Response (201):**
```json
{
  "status": "Stream started",
  "stream_id": "550e8400-e29b-41d4-a716-446655440000",
  "rtmp_url": "rtmp://stream.platform.com/live/550e8400-e29b-41d4-a716-446655440000",
  "stream_key": "secret-key-abc123xyz789"
}
```

**Parameters:**
| Param | Type | Required | Example |
|-------|------|----------|---------|
| title | string | Yes | "Live Gaming" |
| description | string | No | "" |
| is_public | boolean | Yes | true |
| category | enum | Yes | gaming, music, education, sports, general |

**Rate Limit:** 10/minute

---

### 2. End Live Stream
**POST** `/live/{stream_id}/end`

```bash
curl -X POST "http://localhost:8000/live/550e8400-e29b-41d4-a716-446655440000/end" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Response (200):**
```json
{
  "status": "Stream ended",
  "stream_id": "550e8400-e29b-41d4-a716-446655440000",
  "archive_video_id": "video-abc123",
  "duration": 3600
}
```

**Rate Limit:** 10/minute

---

### 3. Get Stream Info
**GET** `/live/{stream_id}/info`

```bash
curl -X GET "http://localhost:8000/live/550e8400-e29b-41d4-a716-446655440000/info"
```

**Response (200):**
```json
{
  "stream": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Live Gaming Session",
    "description": "Playing competitive games",
    "category": "gaming",
    "status": "live",
    "viewer_count": 1245,
    "started_at": "2024-01-15T10:30:00Z",
    "creator": {
      "id": "user-xxxxx",
      "name": "Creator Name"
    }
  }
}
```

**Rate Limit:** 60/minute

---

## Monetization (3 Endpoints)

### 1. Get Creator Earnings
**GET** `/monetization/earnings`

```bash
curl -X GET "http://localhost:8000/monetization/earnings?period=month" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Query Parameters:**
| Param | Type | Values |
|-------|------|--------|
| period | string | week, month, year, all |

**Response (200):**
```json
{
  "period": "month",
  "earnings": {
    "ad_revenue": 450.50,
    "sponsor_revenue": 128.71,
    "tips_revenue": 64.36,
    "total": 643.57
  },
  "videos_count": 18,
  "total_views": 12864500,
  "currency": "USD"
}
```

**Rate Limit:** 20/minute

---

### 2. Setup Stripe Payment
**POST** `/monetization/setup-stripe`

```bash
curl -X POST "http://localhost:8000/monetization/setup-stripe" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "stripe_account_id=acct_1234567890"
```

**Response (200):**
```json
{
  "status": "Payment account verified",
  "stripe_account_id": "acct_1234567890"
}
```

**Rate Limit:** 5/minute

---

## Premium Subscriptions (2 Endpoints)

### 1. Subscribe to Premium
**POST** `/premium/subscribe`

```bash
curl -X POST "http://localhost:8000/premium/subscribe" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "plan=pro"
```

**Form Parameters:**
| Param | Type | Values | Price |
|-------|------|--------|-------|
| plan | enum | basic, pro, enterprise | See below |

**Plan Details:**
```
Basic ($4.99/month):
  - 4K uploads
  - Custom branding
  - 10GB storage

Pro ($9.99/month):
  - 8K uploads
  - Custom branding
  - 100GB storage
  - Priority support

Enterprise ($24.99/month):
  - Unlimited uploads
  - White-label platform
  - 1TB storage
  - 24/7 support
  - Advanced analytics
```

**Response (200):**
```json
{
  "status": "Premium subscribed",
  "plan": "pro",
  "features": [
    "8K uploads",
    "Custom branding",
    "100GB storage",
    "Priority support"
  ]
}
```

**Rate Limit:** 10/minute

---

### 2. Get Subscription Info
**GET** `/premium/subscription`

```bash
curl -X GET "http://localhost:8000/premium/subscription" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Response (200):**
```json
{
  "subscription": {
    "plan": "pro",
    "price": 9.99,
    "features": [
      "8K uploads",
      "Custom branding",
      "100GB storage",
      "Priority support"
    ],
    "status": "active",
    "next_billing": "2024-02-15T10:30:00Z"
  }
}
```

**Rate Limit:** 30/minute

---

## Social Features (6 Endpoints)

### 1. Like Comment
**POST** `/videos/{video_id}/comments/{comment_id}/like`

```bash
curl -X POST "http://localhost:8000/videos/video-123/comments/comment-456/like" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Response (200):**
```json
{
  "status": "Comment liked"
}
```

**Rate Limit:** 60/minute

---

### 2. Pin Comment
**POST** `/videos/{video_id}/pin-comment`

```bash
curl -X POST "http://localhost:8000/videos/video-123/pin-comment" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "comment_id=comment-456"
```

**Response (200):**
```json
{
  "status": "Comment pinned"
}
```

**Rate Limit:** 30/minute

---

### 3. Follow User
**POST** `/users/{user_id}/follow`

```bash
curl -X POST "http://localhost:8000/users/user-123/follow" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Response (200):**
```json
{
  "status": "User followed"
}
```

**Rate Limit:** 60/minute

---

### 4. Unfollow User
**DELETE** `/users/{user_id}/follow`

```bash
curl -X DELETE "http://localhost:8000/users/user-123/follow" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Response (200):**
```json
{
  "status": "User unfollowed"
}
```

**Rate Limit:** 60/minute

---

### 5. Get User Followers
**GET** `/users/{user_id}/followers`

```bash
curl -X GET "http://localhost:8000/users/user-123/followers?skip=0&limit=20"
```

**Query Parameters:**
| Param | Type | Default | Max |
|-------|------|---------|-----|
| skip | integer | 0 | - |
| limit | integer | 20 | 100 |

**Response (200):**
```json
{
  "followers": [
    {
      "follower_id": "user-abc",
      "following_id": "user-123",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 45,
  "skip": 0,
  "limit": 20
}
```

**Rate Limit:** 60/minute

---

## Direct Messaging (2 Endpoints)

### 1. Send Message
**POST** `/messages/send`

```bash
curl -X POST "http://localhost:8000/messages/send" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "recipient_id=user-123" \
  -F "message=Hey! Check out this video..."
```

**Form Parameters:**
| Param | Type | Required | Max Length |
|-------|------|----------|-----------|
| recipient_id | string | Yes | - |
| message | string | Yes | 5000 |

**Response (200):**
```json
{
  "status": "Message sent",
  "message_id": "msg-abc123"
}
```

**Rate Limit:** 60/minute

---

### 2. Get Inbox
**GET** `/messages/inbox`

```bash
curl -X GET "http://localhost:8000/messages/inbox?skip=0&limit=20&unread_only=false" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Query Parameters:**
| Param | Type | Default | Values |
|-------|------|---------|--------|
| skip | integer | 0 | - |
| limit | integer | 20 | 1-50 |
| unread_only | boolean | false | - |

**Response (200):**
```json
{
  "messages": [
    {
      "message_id": "msg-abc123",
      "sender_id": "user-xyz",
      "message": "Hey! Check out this video...",
      "read": false,
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 127,
  "unread": 23
}
```

**Rate Limit:** 30/minute

---

## Hashtags & Trending (2 Endpoints)

### 1. Get Trending Hashtags
**GET** `/hashtags/trending`

```bash
curl -X GET "http://localhost:8000/hashtags/trending?limit=20"
```

**Query Parameters:**
| Param | Type | Default | Max |
|-------|------|---------|-----|
| limit | integer | 20 | 100 |

**Response (200):**
```json
{
  "hashtags": [
    {
      "hashtag": "gaming",
      "count": 2841,
      "trend": "up"
    },
    {
      "hashtag": "vlog",
      "count": 1926,
      "trend": "stable"
    }
  ],
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Rate Limit:** 60/minute

---

### 2. Get Hashtag Videos
**GET** `/hashtags/{hashtag}/videos`

```bash
curl -X GET "http://localhost:8000/hashtags/gaming/videos?skip=0&limit=20"
```

**Query Parameters:**
| Param | Type | Default | Max |
|-------|------|---------|-----|
| skip | integer | 0 | - |
| limit | integer | 20 | 100 |

**Response (200):**
```json
{
  "hashtag": "gaming",
  "videos": [
    {
      "id": "video-123",
      "title": "Gaming Highlights",
      "view_count": 12500,
      ...
    }
  ],
  "total": 8941,
  "skip": 0,
  "limit": 20
}
```

**Rate Limit:** 60/minute

---

## Content Features (2 Endpoints)

### 1. Add Video Chapters
**POST** `/videos/{video_id}/chapters`

```bash
curl -X POST "http://localhost:8000/videos/video-123/chapters" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "chapters": [
      {"timestamp": 0, "title": "Intro"},
      {"timestamp": 120, "title": "Main Topic"},
      {"timestamp": 600, "title": "Conclusion"}
    ]
  }'
```

**Request Body:**
```json
{
  "chapters": [
    {"timestamp": integer, "title": string},
    ...
  ]
}
```

**Response (200):**
```json
{
  "status": "Chapters added",
  "count": 3
}
```

**Rate Limit:** 30/minute

---

### 2. Add Playlist Collaborator
**POST** `/playlists/{playlist_id}/collaborate`

```bash
curl -X POST "http://localhost:8000/playlists/playlist-123/collaborate" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "collaborator_id=user-456" \
  -F "permission=edit"
```

**Form Parameters:**
| Param | Type | Values |
|-------|------|--------|
| collaborator_id | string | - |
| permission | enum | view, edit, admin |

**Response (200):**
```json
{
  "status": "Collaborator added",
  "permission": "edit"
}
```

**Rate Limit:** 30/minute

---

## Video Processing & Encoding (2 Endpoints)

### 1. Set Video Quality
**POST** `/videos/process/upload-quality`

```bash
curl -X POST "http://localhost:8000/videos/process/upload-quality" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "video_id=video-123" \
  -F "quality=1080p"
```

**Form Parameters:**
| Param | Type | Values | Bitrate | Codec |
|-------|------|--------|---------|-------|
| video_id | string | - | - | - |
| quality | enum | 360p, 480p, 720p, 1080p, 4K, 8K | See below | See below |

**Quality Table:**
```
360p:   500k   H.264
480p:   1M     H.264
720p:   2M     H.264
1080p:  5M     H.264
4K:     15M    HEVC
8K:     50M    HEVC
```

**Response (200):**
```json
{
  "status": "Quality queued for processing",
  "quality": "1080p",
  "bitrate": "5M"
}
```

**Rate Limit:** 20/minute

---

### 2. Get Processing Status
**GET** `/videos/{video_id}/processing-status`

```bash
curl -X GET "http://localhost:8000/videos/video-123/processing-status"
```

**Response (200):**
```json
{
  "video_id": "video-123",
  "processing": [
    {
      "quality": "720p",
      "status": "processing",
      "progress": 45,
      "added_at": "2024-01-15T10:30:00Z"
    }
  ],
  "available_qualities": ["360p", "480p", "720p"],
  "status": "processing"
}
```

**Rate Limit:** 30/minute

---

## Advanced Search (2 Endpoints)

### 1. Advanced Search
**GET** `/search/advanced`

```bash
curl -X GET 'http://localhost:8000/search/advanced?query=gaming&filters={"category":"gaming"}&sort_by=views&skip=0&limit=20'
```

**Query Parameters:**
| Param | Type | Example |
|-------|------|---------|
| query | string | "gaming" |
| filters | JSON | `{"category":"gaming","duration_min":300}` |
| sort_by | enum | relevance, views, upload_date, duration |
| skip | integer | 0 |
| limit | integer | 20 |

**Supported Filters:**
```json
{
  "category": "gaming",
  "duration_min": 300,
  "duration_max": 3600,
  "upload_date": "last_week",
  "view_count_min": 1000
}
```

**Response (200):**
```json
{
  "query": "gaming",
  "videos": [
    {
      "id": "video-123",
      "title": "Gaming Highlights",
      ...
    }
  ],
  "total": 8941,
  "filters": {"category": "gaming"},
  "sort": "views"
}
```

**Rate Limit:** 60/minute

---

### 2. Search Suggestions
**GET** `/search/suggestions`

```bash
curl -X GET "http://localhost:8000/search/suggestions?query=gam"
```

**Query Parameters:**
| Param | Type | Max |
|-------|------|-----|
| query | string | 100 |

**Response (200):**
```json
{
  "suggestions": [
    "gaming highlights",
    "gaming tutorials",
    "gaming news",
    "gameplay",
    "gaming montage"
  ]
}
```

**Rate Limit:** 60/minute

---

## Notifications (2 Endpoints)

### 1. Get Notifications
**GET** `/notifications`

```bash
curl -X GET "http://localhost:8000/notifications?skip=0&limit=20&unread_only=false" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Query Parameters:**
| Param | Type | Default | Max |
|-------|------|---------|-----|
| skip | integer | 0 | - |
| limit | integer | 20 | 50 |
| unread_only | boolean | false | - |

**Response (200):**
```json
{
  "notifications": [
    {
      "type": "video_comment",
      "user": "Username",
      "video": "Video Title",
      "timestamp": "2024-01-15T10:30:00Z",
      "read": false
    }
  ],
  "unread": 12,
  "total": 145
}
```

**Rate Limit:** 30/minute

---

### 2. Mark Notification Read
**PUT** `/notifications/{notification_id}/read`

```bash
curl -X PUT "http://localhost:8000/notifications/notif-123/read" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Response (200):**
```json
{
  "status": "Notification marked as read"
}
```

**Rate Limit:** 60/minute

---

## User Profile Enhancements (2 Endpoints)

### 1. Upload Banner
**PUT** `/profile/banners`

```bash
curl -X PUT "http://localhost:8000/profile/banners" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "banner_url=https://cdn.example.com/banner.jpg"
```

**Form Parameters:**
| Param | Type | Required |
|-------|------|----------|
| banner_url | string | Yes |

**Response (200):**
```json
{
  "status": "Banner updated"
}
```

**Rate Limit:** 10/minute

---

### 2. Get Profile Stats
**GET** `/profile/{user_id}/stats`

```bash
curl -X GET "http://localhost:8000/profile/user-123/stats"
```

**Response (200):**
```json
{
  "user_id": "user-123",
  "stats": {
    "videos": 247,
    "followers": 12450,
    "following": 89,
    "total_views": 12864500,
    "total_likes": 450230,
    "joined_at": "2022-03-15T00:00:00Z",
    "subscriber_count": 12450
  }
}
```

**Rate Limit:** 60/minute

---

## Content Moderation (1 Endpoint)

### 1. Report Content
**POST** `/content/report`

```bash
curl -X POST "http://localhost:8000/content/report" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "content_type=video" \
  -F "content_id=video-123" \
  -F "reason=harassment" \
  -F "description=This video contains hate speech"
```

**Form Parameters:**
| Param | Type | Values | Required |
|-------|------|--------|----------|
| content_type | enum | video, comment, channel | Yes |
| content_id | string | - | Yes |
| reason | enum | inappropriate, harassment, spam, copyright, misleading | Yes |
| description | string | - | No |

**Response (200):**
```json
{
  "status": "Report submitted",
  "report_id": "report-abc123"
}
```

**Rate Limit:** 10/minute

---

## Smart Playlists (1 Endpoint)

### 1. Create Smart Playlist
**POST** `/playlists/smart-create`

```bash
curl -X POST "http://localhost:8000/playlists/smart-create" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "name=My Gaming Playlist" \
  -F "description=Auto-generated based on your watch history" \
  -F "category=gaming"
```

**Form Parameters:**
| Param | Type | Required | Max |
|-------|------|----------|-----|
| name | string | Yes | 100 |
| description | string | No | - |
| category | string | No | - |

**Response (200):**
```json
{
  "status": "Smart playlist created",
  "playlist_id": "playlist-abc123",
  "videos_added": 18
}
```

**Algorithm:**
1. Analyzes last 50 watched videos
2. Extracts all tags
3. Scores video matches by tag similarity
4. Ranks by engagement (views, likes, comments)
5. Auto-populates with top 20 matching videos

**Rate Limit:** 20/minute

---

## Error Responses

### Common Error Codes

```json
{
  "status_code": 400,
  "detail": "Invalid request parameters"
}
```

| Code | Error | Cause |
|------|-------|-------|
| 400 | Invalid request | Missing/invalid parameters |
| 401 | Unauthorized | Missing/invalid JWT token |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not found | Resource doesn't exist |
| 429 | Too many requests | Rate limit exceeded |
| 500 | Server error | Internal error |

---

## Authentication

All endpoints (except public GET) require JWT token in header:

```bash
Authorization: Bearer YOUR_JWT_TOKEN
```

Obtain token via `/login` endpoint (Phase 1).

---

## Rate Limiting

Rate limits reset every minute. Upon hitting limit:

```json
{
  "status_code": 429,
  "detail": "Rate limit exceeded"
}
```

---

## Summary

- **30 Endpoints** across 13 feature categories
- **All production-ready**
- **Full CRUD operations**
- **Real-time features**
- **Enterprise security**

**Ready for deployment! 🚀**
