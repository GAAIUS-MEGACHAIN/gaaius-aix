# Phase 1: Complete API Reference

**Status:** Production-Ready  
**Version:** 1.0  
**Last Updated:** January 17, 2026

---

## Table of Contents

1. [Video Metadata](#video-metadata)
2. [View Tracking](#view-tracking)
3. [Engagement (Likes)](#engagement-likes)
4. [Comments](#comments)
5. [Playlists](#playlists)
6. [Channels](#channels)
7. [Error Codes](#error-codes)
8. [Rate Limits](#rate-limits)

---

## Video Metadata

### PATCH /videos/videos/{video_id}

Update video metadata (title, description, tags, thumbnail, privacy).

**Authentication:** Required (Bearer Token)

**Parameters:**
- `video_id` (path, required): UUID of the video

**Request Body:**
```json
{
  "title": "string (1-500 chars)",
  "description": "string (0-10000 chars)",
  "tags": ["string", "..."],
  "thumbnail_url": "string (URL)",
  "is_public": "boolean"
}
```

All fields are optional. Only provided fields will be updated.

**Response (200 OK):**
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "title": "string",
  "description": "string",
  "tags": ["string"],
  "thumbnail": "string",
  "is_public": boolean,
  "views": 0,
  "likes": 0,
  "timestamp": "ISO-8601",
  "updated_at": "ISO-8601",
  "status": "string"
}
```

**Response (400 Bad Request):**
```json
{
  "detail": "Invalid input"
}
```

**Response (403 Forbidden):**
```json
{
  "detail": "Not authorized to edit this video"
}
```

**Response (404 Not Found):**
```json
{
  "detail": "Video not found"
}
```

**Rate Limit:** 30 requests/hour

**Example:**
```bash
curl -X PATCH "http://localhost:8000/api/videos/videos/video-123" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My Updated Video",
    "description": "Updated description",
    "tags": ["new", "tags"],
    "is_public": true
  }'
```

---

## View Tracking

### POST /videos/videos/{video_id}/view

Record a video view. Includes spam prevention (one view per user per 30 seconds).

**Authentication:** Required (Bearer Token)

**Parameters:**
- `video_id` (path, required): UUID of the video

**Request Body:** Empty

**Response (200 OK) - New View:**
```json
{
  "status": "recorded",
  "video_id": "uuid"
}
```

**Response (200 OK) - Duplicate (within 30s):**
```json
{
  "status": "duplicate",
  "message": "View already recorded recently"
}
```

**Response (404 Not Found):**
```json
{
  "detail": "Video not found"
}
```

**Rate Limit:** 300 requests/hour

**Data Tracking:**
Views are tracked in two places:
1. `view_history` collection - Raw view data for analytics
2. `user_watch_history` collection - User's personal watch history

**Example:**
```bash
curl -X POST "http://localhost:8000/api/videos/videos/video-123/view" \
  -H "Authorization: Bearer $TOKEN"
```

---

## Engagement (Likes)

### POST /videos/videos/{video_id}/like

Like a video. One like per user per video.

**Authentication:** Required (Bearer Token)

**Parameters:**
- `video_id` (path, required): UUID of the video

**Request Body:** Empty

**Response (200 OK):**
```json
{
  "status": "liked",
  "video_id": "uuid",
  "likes": 42
}
```

**Response (400 Bad Request):**
```json
{
  "detail": "Video already liked by user"
}
```

**Response (404 Not Found):**
```json
{
  "detail": "Video not found"
}
```

**Rate Limit:** 100 requests/hour

**Data Storage:**
- `video_likes` collection tracks likes per user
- Unique index on (video_id, user_id) prevents duplicates
- Video's `likes` field incremented atomically via `$inc`

**Example:**
```bash
curl -X POST "http://localhost:8000/api/videos/videos/video-123/like" \
  -H "Authorization: Bearer $TOKEN"
```

---

### POST /videos/videos/{video_id}/unlike

Unlike a video.

**Authentication:** Required (Bearer Token)

**Parameters:**
- `video_id` (path, required): UUID of the video

**Request Body:** Empty

**Response (200 OK):**
```json
{
  "status": "unliked",
  "video_id": "uuid",
  "likes": 41
}
```

**Response (400 Bad Request):**
```json
{
  "detail": "Like not found"
}
```

**Response (404 Not Found):**
```json
{
  "detail": "Video not found"
}
```

**Rate Limit:** 100 requests/hour

**Example:**
```bash
curl -X POST "http://localhost:8000/api/videos/videos/video-123/unlike" \
  -H "Authorization: Bearer $TOKEN"
```

---

## Comments

### POST /videos/videos/{video_id}/comments

Create a new comment or reply on a video.

**Authentication:** Required (Bearer Token)

**Parameters:**
- `video_id` (path, required): UUID of the video

**Request Body:**
```json
{
  "content": "string (1-5000 chars)",
  "parent_id": "uuid (optional, null for top-level comment)"
}
```

**Response (200 OK):**
```json
{
  "comment_id": "uuid",
  "video_id": "uuid",
  "user": {
    "id": "uuid",
    "email": "string"
  },
  "content": "string",
  "parent_id": "uuid or null",
  "created_at": "ISO-8601"
}
```

**Response (404 Not Found):**
```json
{
  "detail": "Video not found"
}
```

**Response (422 Unprocessable Entity):**
```json
{
  "detail": "Invalid input"
}
```

**Rate Limit:** 50 requests/hour

**Threading:**
- Comments without `parent_id` are top-level comments
- Comments with `parent_id` are replies to other comments
- Depth calculated recursively (top-level = 0, replies = 1+)

**Example - Top-level comment:**
```bash
curl -X POST "http://localhost:8000/api/videos/videos/video-123/comments" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Great video!",
    "parent_id": null
  }'
```

**Example - Reply:**
```bash
curl -X POST "http://localhost:8000/api/videos/videos/video-123/comments" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "I agree!",
    "parent_id": "comment-456"
  }'
```

---

### GET /videos/videos/{video_id}/comments

Get comments for a video with pagination and threading.

**Authentication:** Required (Bearer Token)

**Parameters:**
- `video_id` (path, required): UUID of the video
- `skip` (query, optional): Number of top-level comments to skip (default: 0)
- `limit` (query, optional): Number of top-level comments to return (default: 20, max: 100)
- `sort_by` (query, optional): Sort order - "newest" or "oldest" (default: newest)

**Response (200 OK):**
```json
{
  "video_id": "uuid",
  "comments": [
    {
      "comment_id": "uuid",
      "user_id": "uuid",
      "content": "string",
      "parent_id": null,
      "depth": 0,
      "likes": 5,
      "created_at": "ISO-8601",
      "updated_at": "ISO-8601",
      "is_deleted": false,
      "replies": [
        {
          "comment_id": "uuid",
          "user_id": "uuid",
          "content": "string",
          "parent_id": "uuid",
          "depth": 1,
          "likes": 2,
          "created_at": "ISO-8601",
          "is_deleted": false
        }
      ],
      "reply_count": 1
    }
  ],
  "total": 42,
  "skip": 0,
  "limit": 20
}
```

**Response (404 Not Found):**
```json
{
  "detail": "Video not found"
}
```

**Rate Limit:** 300 requests/hour

**Features:**
- Top-level comments paginated
- Replies nested under parent (up to 10 per parent)
- Soft-deleted comments excluded
- Sorted by creation time

**Example:**
```bash
curl -X GET "http://localhost:8000/api/videos/videos/video-123/comments?skip=0&limit=20&sort_by=newest" \
  -H "Authorization: Bearer $TOKEN"
```

---

### DELETE /videos/videos/{video_id}/comments/{comment_id}

Delete a comment (soft delete).

**Authentication:** Required (Bearer Token)

**Parameters:**
- `video_id` (path, required): UUID of the video
- `comment_id` (path, required): UUID of the comment

**Request Body:** Empty

**Response (200 OK):**
```json
{
  "status": "deleted",
  "comment_id": "uuid"
}
```

**Response (403 Forbidden):**
```json
{
  "detail": "Not authorized to delete this comment"
}
```

**Response (404 Not Found):**
```json
{
  "detail": "Comment not found"
}
```

**Rate Limit:** 100 requests/hour

**Note:** Uses soft delete - comment marked as deleted but retained in database

**Example:**
```bash
curl -X DELETE "http://localhost:8000/api/videos/videos/video-123/comments/comment-456" \
  -H "Authorization: Bearer $TOKEN"
```

---

## Playlists

### POST /videos/playlists

Create a new playlist.

**Authentication:** Required (Bearer Token)

**Request Body:**
```json
{
  "name": "string (1-200 chars)",
  "description": "string (0-2000 chars)",
  "is_public": "boolean (default: false)"
}
```

**Response (200 OK):**
```json
{
  "playlist_id": "uuid",
  "name": "string",
  "description": "string",
  "is_public": boolean,
  "video_count": 0,
  "created_at": "ISO-8601"
}
```

**Response (500 Internal Server Error):**
```json
{
  "detail": "Failed to create playlist"
}
```

**Rate Limit:** 50 requests/hour

**Example:**
```bash
curl -X POST "http://localhost:8000/api/videos/playlists" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Favorites",
    "description": "Videos I love",
    "is_public": false
  }'
```

---

### GET /videos/playlists

Get user's playlists.

**Authentication:** Required (Bearer Token)

**Parameters:**
- `skip` (query, optional): Number of playlists to skip (default: 0)
- `limit` (query, optional): Number of playlists to return (default: 20)

**Response (200 OK):**
```json
{
  "playlists": [
    {
      "playlist_id": "uuid",
      "user_id": "uuid",
      "name": "string",
      "description": "string",
      "is_public": boolean,
      "videos": ["uuid", "uuid"],
      "video_count": 5,
      "created_at": "ISO-8601",
      "updated_at": "ISO-8601"
    }
  ],
  "total": 10,
  "skip": 0,
  "limit": 20
}
```

**Rate Limit:** 100 requests/hour

**Example:**
```bash
curl -X GET "http://localhost:8000/api/videos/playlists?skip=0&limit=20" \
  -H "Authorization: Bearer $TOKEN"
```

---

### PATCH /videos/playlists/{playlist_id}

Update playlist metadata.

**Authentication:** Required (Bearer Token)

**Parameters:**
- `playlist_id` (path, required): UUID of the playlist

**Request Body:**
```json
{
  "name": "string (1-200 chars)",
  "description": "string (0-2000 chars)",
  "is_public": "boolean"
}
```

**Response (200 OK):** Returns updated playlist (same as POST response)

**Response (403 Forbidden):**
```json
{
  "detail": "Not authorized to edit this playlist"
}
```

**Response (404 Not Found):**
```json
{
  "detail": "Playlist not found"
}
```

**Rate Limit:** 50 requests/hour

**Example:**
```bash
curl -X PATCH "http://localhost:8000/api/videos/playlists/playlist-123" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Name",
    "is_public": true
  }'
```

---

### POST /videos/playlists/{playlist_id}/videos/{video_id}

Add a video to a playlist.

**Authentication:** Required (Bearer Token)

**Parameters:**
- `playlist_id` (path, required): UUID of the playlist
- `video_id` (path, required): UUID of the video

**Request Body:** Empty

**Response (200 OK):**
```json
{
  "status": "added",
  "playlist_id": "uuid",
  "video_id": "uuid"
}
```

**Response (400 Bad Request):**
```json
{
  "detail": "Video already in playlist" or "Playlist full (max 500 videos)"
}
```

**Response (403 Forbidden):**
```json
{
  "detail": "Not authorized"
}
```

**Response (404 Not Found):**
```json
{
  "detail": "Playlist not found" or "Video not found"
}
```

**Rate Limit:** 100 requests/hour

**Limits:**
- Maximum 500 videos per playlist
- Prevents duplicate videos in same playlist

**Example:**
```bash
curl -X POST "http://localhost:8000/api/videos/playlists/playlist-123/videos/video-456" \
  -H "Authorization: Bearer $TOKEN"
```

---

### DELETE /videos/playlists/{playlist_id}/videos/{video_id}

Remove a video from a playlist.

**Authentication:** Required (Bearer Token)

**Parameters:**
- `playlist_id` (path, required): UUID of the playlist
- `video_id` (path, required): UUID of the video

**Request Body:** Empty

**Response (200 OK):**
```json
{
  "status": "removed",
  "playlist_id": "uuid",
  "video_id": "uuid"
}
```

**Response (400 Bad Request):**
```json
{
  "detail": "Video not in playlist"
}
```

**Response (403 Forbidden):**
```json
{
  "detail": "Not authorized"
}
```

**Response (404 Not Found):**
```json
{
  "detail": "Playlist not found"
}
```

**Rate Limit:** 100 requests/hour

**Example:**
```bash
curl -X DELETE "http://localhost:8000/api/videos/playlists/playlist-123/videos/video-456" \
  -H "Authorization: Bearer $TOKEN"
```

---

## Channels

### GET /videos/channels/{channel_id}

Get public channel profile information.

**Authentication:** Not required (public data)

**Parameters:**
- `channel_id` (path, required): UUID of the channel (user ID)

**Response (200 OK):**
```json
{
  "channel_id": "uuid",
  "display_name": "string",
  "bio": "string",
  "avatar_url": "string (URL)",
  "banner_url": "string (URL)",
  "video_count": 42,
  "subscriber_count": 1250,
  "recent_videos": [
    {
      "id": "uuid",
      "title": "string",
      "views": 5000,
      "likes": 450
    }
  ],
  "created_at": "ISO-8601"
}
```

**Response (404 Not Found):**
```json
{
  "detail": "Channel not found"
}
```

**Rate Limit:** 200 requests/hour

**Example:**
```bash
curl -X GET "http://localhost:8000/api/videos/channels/user-123"
```

---

### PATCH /videos/channels/me

Update own channel profile.

**Authentication:** Required (Bearer Token)

**Request Body:**
```json
{
  "display_name": "string (1-100 chars)",
  "bio": "string (0-1000 chars)",
  "avatar_url": "string (URL)",
  "banner_url": "string (URL)"
}
```

**Response (200 OK):**
```json
{
  "id": "uuid",
  "email": "string",
  "display_name": "string",
  "bio": "string",
  "avatar_url": "string",
  "banner_url": "string",
  "created_at": "ISO-8601",
  "updated_at": "ISO-8601"
}
```

**Response (500 Internal Server Error):**
```json
{
  "detail": "Failed to update channel"
}
```

**Rate Limit:** 20 requests/hour

**Example:**
```bash
curl -X PATCH "http://localhost:8000/api/videos/channels/me" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "display_name": "Jane Doe",
    "bio": "Video creator and educator",
    "avatar_url": "https://..."
  }'
```

---

## Error Codes

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 400 | Bad Request | Invalid input or business logic error |
| 403 | Forbidden | User not authorized for this action |
| 404 | Not Found | Resource not found |
| 422 | Unprocessable Entity | Validation error |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | Database unavailable |

### Common Error Responses

```json
{
  "detail": "Video not found"
}
```

```json
{
  "detail": "Not authorized to edit this video"
}
```

```json
{
  "detail": "Video already liked by user"
}
```

---

## Rate Limits

| Endpoint | Limit | Window |
|----------|-------|--------|
| PATCH /videos/videos/{id} | 30/hour | Sliding |
| POST /videos/videos/{id}/view | 300/hour | Sliding |
| POST /videos/videos/{id}/like | 100/hour | Sliding |
| POST /videos/videos/{id}/unlike | 100/hour | Sliding |
| POST /videos/videos/{id}/comments | 50/hour | Sliding |
| GET /videos/videos/{id}/comments | 300/hour | Sliding |
| DELETE /videos/videos/{id}/comments/{id} | 100/hour | Sliding |
| POST /videos/playlists | 50/hour | Sliding |
| GET /videos/playlists | 100/hour | Sliding |
| PATCH /videos/playlists/{id} | 50/hour | Sliding |
| POST /videos/playlists/{id}/videos/{id} | 100/hour | Sliding |
| DELETE /videos/playlists/{id}/videos/{id} | 100/hour | Sliding |
| GET /videos/channels/{id} | 200/hour | Sliding |
| PATCH /videos/channels/me | 20/hour | Sliding |

**Rate Limit Headers:**
All responses include:
- `X-RateLimit-Limit`: Total requests allowed
- `X-RateLimit-Remaining`: Requests remaining
- `X-RateLimit-Reset`: Unix timestamp when limit resets

---

## Authentication

All endpoints requiring authentication use Bearer Token in Authorization header:

```
Authorization: Bearer <jwt_token>
```

Tokens are obtained via `/auth/register` or `/auth/login` endpoints.

**Token Format:**
- JWT (HS256)
- Valid for 30 days
- Contains: user_id, email, is_pro

---

## Data Types

### Timestamp Format
All timestamps are ISO-8601 format with UTC timezone:
```
2026-01-17T10:30:00Z
```

### UUID Format
All UUIDs are 36-character strings:
```
123e4567-e89b-12d3-a456-426614174000
```

### Pagination
All paginated endpoints support:
- `skip`: Number of records to skip (0-indexed)
- `limit`: Number of records to return (1-100)
- `total`: Total count of matching records

---

## Best Practices

### 1. Error Handling
Always check HTTP status code and handle errors gracefully:
```bash
if [ "$status_code" -ne 200 ]; then
  # Handle error
fi
```

### 2. Pagination
Always use pagination for list endpoints to avoid loading all data:
```bash
# Don't do this:
GET /videos/comments  # Could return thousands

# Do this:
GET /videos/comments?skip=0&limit=20
```

### 3. Rate Limiting
Implement exponential backoff when hitting rate limits (HTTP 429):
```python
if response.status_code == 429:
    wait_time = 2 ** retry_count
    await asyncio.sleep(wait_time)
```

### 4. View Spam Prevention
Avoid making multiple view requests rapidly. The system throttles to 1 view per 30 seconds.

### 5. Comment Threading
For better UX, display comments hierarchically:
- Top-level comments (parent_id: null) as main comments
- Nested replies under their parent

