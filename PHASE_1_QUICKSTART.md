# Phase 1: Quick Start Guide - Get Going in 10 Minutes

**Last Updated:** January 17, 2026  
**Status:** Production Ready ✅

---

## What You Get in Phase 1

- 📝 **Metadata Editing** - Update video title, description, tags
- 👁️ **View Tracking** - Count views (with spam prevention)
- ❤️ **Likes** - Like/unlike videos
- 💬 **Comments** - Threaded comments with replies
- 📋 **Playlists** - Create and manage playlists
- 👤 **Channels** - Public channel profiles
- 🔔 **Subscriptions** - Subscribe to channels

---

## Prerequisites

- Running backend server (`python run_server.py`)
- MongoDB running
- JWT authentication token

---

## Get Authentication Token

### Step 1: Register/Login

```bash
# Register
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "you@example.com",
    "password": "password123"
  }'

# Or login if already registered
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "you@example.com",
    "password": "password123"
  }'
```

**Response:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "user-uuid-123",
    "email": "you@example.com"
  }
}
```

### Step 2: Save Token

```bash
export TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

## Quick Examples

### 1. Edit Video Metadata (1 min)

**Goal:** Change video title and add tags

```bash
curl -X PATCH http://localhost:8000/api/videos/videos/YOUR_VIDEO_ID \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Amazing Tech Tutorial",
    "description": "Learn the latest tech trends",
    "tags": ["tutorial", "tech", "2026"],
    "is_public": true
  }'
```

**Response:**
```json
{
  "id": "video-uuid",
  "title": "Amazing Tech Tutorial",
  "tags": ["tutorial", "tech", "2026"],
  "updated_at": "2026-01-17T10:30:00Z"
}
```

---

### 2. Record a View (1 min)

**Goal:** Track that you watched a video

```bash
curl -X POST http://localhost:8000/api/videos/videos/VIDEO_ID/view \
  -H "Authorization: Bearer $TOKEN"
```

**Response:**
```json
{
  "status": "recorded",
  "video_id": "video-uuid"
}
```

**Note:** Same user within 30 seconds = no double count

---

### 3. Like a Video (30 sec)

**Goal:** Like a video

```bash
curl -X POST http://localhost:8000/api/videos/videos/VIDEO_ID/like \
  -H "Authorization: Bearer $TOKEN"
```

**Response:**
```json
{
  "status": "liked",
  "video_id": "video-uuid",
  "likes": 42
}
```

**Unlike:**
```bash
curl -X POST http://localhost:8000/api/videos/videos/VIDEO_ID/unlike \
  -H "Authorization: Bearer $TOKEN"
```

---

### 4. Comment on Video (2 min)

**Goal:** Add a comment

```bash
# Create comment
curl -X POST http://localhost:8000/api/videos/videos/VIDEO_ID/comments \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Great video! Really helped me understand this."
  }'
```

**Response:**
```json
{
  "comment_id": "comment-uuid",
  "content": "Great video! Really helped me understand this.",
  "created_at": "2026-01-17T10:30:00Z"
}
```

**Reply to comment:**
```bash
curl -X POST http://localhost:8000/api/videos/videos/VIDEO_ID/comments \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Thanks for watching!",
    "parent_id": "comment-uuid"
  }'
```

**Get all comments:**
```bash
curl http://localhost:8000/api/videos/videos/VIDEO_ID/comments \
  -H "Authorization: Bearer $TOKEN"
```

**Response includes threaded replies:**
```json
{
  "video_id": "video-uuid",
  "comments": [
    {
      "comment_id": "comment-123",
      "content": "Great video!",
      "replies": [
        {
          "comment_id": "reply-456",
          "content": "Thanks for watching!"
        }
      ],
      "reply_count": 1
    }
  ]
}
```

**Delete comment:**
```bash
curl -X DELETE http://localhost:8000/api/videos/videos/VIDEO_ID/comments/COMMENT_ID \
  -H "Authorization: Bearer $TOKEN"
```

---

### 5. Create Playlist (2 min)

**Goal:** Create a custom playlist

```bash
curl -X POST http://localhost:8000/api/videos/playlists \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Tech Tutorials 2026",
    "description": "All the best tech videos this year",
    "is_public": false
  }'
```

**Response:**
```json
{
  "playlist_id": "playlist-uuid",
  "name": "Tech Tutorials 2026",
  "video_count": 0,
  "created_at": "2026-01-17T10:30:00Z"
}
```

**Add video to playlist:**
```bash
curl -X POST http://localhost:8000/api/videos/playlists/PLAYLIST_ID/videos/VIDEO_ID \
  -H "Authorization: Bearer $TOKEN"
```

**List your playlists:**
```bash
curl http://localhost:8000/api/videos/playlists \
  -H "Authorization: Bearer $TOKEN"
```

**Remove video from playlist:**
```bash
curl -X DELETE http://localhost:8000/api/videos/playlists/PLAYLIST_ID/videos/VIDEO_ID \
  -H "Authorization: Bearer $TOKEN"
```

---

### 6. Channel Management (2 min)

**Goal:** Update your channel profile

```bash
# Update your channel
curl -X PATCH http://localhost:8000/api/videos/channels/me \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "display_name": "Tech Guru",
    "bio": "Creating awesome tech content",
    "avatar_url": "https://example.com/avatar.jpg",
    "banner_url": "https://example.com/banner.jpg"
  }'
```

**View public channel:**
```bash
curl http://localhost:8000/api/videos/channels/CHANNEL_ID \
  -H "Authorization: Bearer $TOKEN"
```

**Response:**
```json
{
  "channel_id": "channel-uuid",
  "display_name": "Tech Guru",
  "bio": "Creating awesome tech content",
  "video_count": 15,
  "subscriber_count": 250,
  "recent_videos": [...]
}
```

---

### 7. Subscriptions (2 min)

**Goal:** Subscribe to a channel

```bash
# Subscribe to channel
curl -X POST http://localhost:8000/api/videos/channels/CHANNEL_ID/subscribe \
  -H "Authorization: Bearer $TOKEN"
```

**Response:**
```json
{
  "status": "subscribed",
  "channel_id": "channel-uuid"
}
```

**Get my subscriptions:**
```bash
curl http://localhost:8000/api/videos/subscriptions \
  -H "Authorization: Bearer $TOKEN"
```

**Check if subscribed:**
```bash
curl http://localhost:8000/api/videos/channels/CHANNEL_ID/subscribers \
  -H "Authorization: Bearer $TOKEN"
```

**Response:**
```json
{
  "is_subscribed": true,
  "channel_id": "channel-uuid"
}
```

**Unsubscribe:**
```bash
curl -X DELETE http://localhost:8000/api/videos/channels/CHANNEL_ID/subscribe \
  -H "Authorization: Bearer $TOKEN"
```

---

## Python Client Example

```python
import requests

class YouTubeClone:
    def __init__(self, base_url="http://localhost:8000/api", token=None):
        self.base_url = base_url
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    def login(self, email, password):
        """Get authentication token"""
        response = requests.post(
            f"{self.base_url}/auth/login",
            json={"email": email, "password": password}
        )
        data = response.json()
        self.token = data["token"]
        self.headers["Authorization"] = f"Bearer {self.token}"
        return self.token
    
    def update_video(self, video_id, **kwargs):
        """Update video metadata"""
        response = requests.patch(
            f"{self.base_url}/videos/videos/{video_id}",
            headers=self.headers,
            json=kwargs
        )
        return response.json()
    
    def like_video(self, video_id):
        """Like a video"""
        response = requests.post(
            f"{self.base_url}/videos/videos/{video_id}/like",
            headers=self.headers
        )
        return response.json()
    
    def comment(self, video_id, content, parent_id=None):
        """Create a comment"""
        data = {"content": content}
        if parent_id:
            data["parent_id"] = parent_id
        
        response = requests.post(
            f"{self.base_url}/videos/videos/{video_id}/comments",
            headers=self.headers,
            json=data
        )
        return response.json()
    
    def get_comments(self, video_id, skip=0, limit=20):
        """Get video comments with replies"""
        response = requests.get(
            f"{self.base_url}/videos/videos/{video_id}/comments",
            headers=self.headers,
            params={"skip": skip, "limit": limit}
        )
        return response.json()
    
    def create_playlist(self, name, description="", is_public=False):
        """Create new playlist"""
        response = requests.post(
            f"{self.base_url}/videos/playlists",
            headers=self.headers,
            json={
                "name": name,
                "description": description,
                "is_public": is_public
            }
        )
        return response.json()
    
    def add_to_playlist(self, playlist_id, video_id):
        """Add video to playlist"""
        response = requests.post(
            f"{self.base_url}/videos/playlists/{playlist_id}/videos/{video_id}",
            headers=self.headers
        )
        return response.json()
    
    def subscribe(self, channel_id):
        """Subscribe to channel"""
        response = requests.post(
            f"{self.base_url}/videos/channels/{channel_id}/subscribe",
            headers=self.headers
        )
        return response.json()

# Usage
client = YouTubeClone()
token = client.login("user@example.com", "password123")

# Update video
video = client.update_video("video-123", title="New Title", tags=["tech"])

# Like video
result = client.like_video("video-123")
print(f"Likes: {result['likes']}")

# Comment on video
comment = client.comment("video-123", "Great video!")
print(f"Comment ID: {comment['comment_id']}")

# Get comments
comments = client.get_comments("video-123")
for c in comments["comments"]:
    print(f"{c['content']} ({c['reply_count']} replies)")

# Create playlist
playlist = client.create_playlist("My Favorites", "Best videos 2026")

# Add to playlist
client.add_to_playlist(playlist["playlist_id"], "video-123")

# Subscribe
client.subscribe("channel-456")
```

---

## JavaScript Client Example

```javascript
class YouTubeClone {
  constructor(baseUrl = "http://localhost:8000/api") {
    this.baseUrl = baseUrl;
    this.token = null;
  }

  async login(email, password) {
    const response = await fetch(`${this.baseUrl}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password })
    });
    const data = await response.json();
    this.token = data.token;
    return this.token;
  }

  async updateVideo(videoId, updates) {
    const response = await fetch(
      `${this.baseUrl}/videos/videos/${videoId}`,
      {
        method: "PATCH",
        headers: {
          "Authorization": `Bearer ${this.token}`,
          "Content-Type": "application/json"
        },
        body: JSON.stringify(updates)
      }
    );
    return response.json();
  }

  async likeVideo(videoId) {
    const response = await fetch(
      `${this.baseUrl}/videos/videos/${videoId}/like`,
      {
        method: "POST",
        headers: { "Authorization": `Bearer ${this.token}` }
      }
    );
    return response.json();
  }

  async comment(videoId, content, parentId = null) {
    const data = { content };
    if (parentId) data.parent_id = parentId;

    const response = await fetch(
      `${this.baseUrl}/videos/videos/${videoId}/comments`,
      {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${this.token}`,
          "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
      }
    );
    return response.json();
  }

  async getComments(videoId, skip = 0, limit = 20) {
    const params = new URLSearchParams({ skip, limit });
    const response = await fetch(
      `${this.baseUrl}/videos/videos/${videoId}/comments?${params}`,
      {
        headers: { "Authorization": `Bearer ${this.token}` }
      }
    );
    return response.json();
  }

  async subscribe(channelId) {
    const response = await fetch(
      `${this.baseUrl}/videos/channels/${channelId}/subscribe`,
      {
        method: "POST",
        headers: { "Authorization": `Bearer ${this.token}` }
      }
    );
    return response.json();
  }
}

// Usage
const client = new YouTubeClone();
await client.login("user@example.com", "password123");

// Like video
const result = await client.likeVideo("video-123");
console.log(`Likes: ${result.likes}`);

// Comment
const comment = await client.comment("video-123", "Great video!");
console.log(`Comment ID: ${comment.comment_id}`);

// Subscribe
await client.subscribe("channel-456");
```

---

## Common Workflows

### Workflow 1: Complete Video Publishing

1. Upload video (existing endpoint)
2. Update metadata
3. Set as public
4. Share channel link

```bash
# Step 1: Upload (existing)
# curl -X POST /videos/upload ...

# Step 2: Update metadata
curl -X PATCH http://localhost:8000/api/videos/videos/VIDEO_ID \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My New Video",
    "description": "Check it out!",
    "tags": ["tutorial"],
    "is_public": true
  }'

# Step 3: Get channel link for sharing
curl http://localhost:8000/api/videos/channels/YOUR_CHANNEL_ID \
  -H "Authorization: Bearer $TOKEN"
```

### Workflow 2: Build Curated Playlist

```bash
# Create playlist
PLAYLIST=$(curl -X POST http://localhost:8000/api/videos/playlists \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Best Tech 2026",
    "is_public": true
  }')
PLAYLIST_ID=$(echo $PLAYLIST | jq -r '.playlist_id')

# Add videos
for vid in video-1 video-2 video-3; do
  curl -X POST http://localhost:8000/api/videos/playlists/$PLAYLIST_ID/videos/$vid \
    -H "Authorization: Bearer $TOKEN"
done

echo "Playlist ready: $PLAYLIST_ID"
```

### Workflow 3: Engage with Community

```bash
# Find video
VIDEO_ID="video-123"

# Like it
curl -X POST http://localhost:8000/api/videos/videos/$VIDEO_ID/like \
  -H "Authorization: Bearer $TOKEN"

# Comment
curl -X POST http://localhost:8000/api/videos/videos/$VIDEO_ID/comments \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Fantastic tutorial, thanks!"
  }'

# Subscribe to creator
CREATOR_ID=$(curl http://localhost:8000/api/videos/videos/$VIDEO_ID \
  -H "Authorization: Bearer $TOKEN" | jq -r '.user_id')

curl -X POST http://localhost:8000/api/videos/channels/$CREATOR_ID/subscribe \
  -H "Authorization: Bearer $TOKEN"
```

---

## Troubleshooting

### "Not authorized" Error
- Make sure token is valid: `Authorization: Bearer <token>`
- Token expires after 30 days, login again

### "Rate limit exceeded"
- You're calling too frequently
- Wait a few minutes and try again
- Check limits in API docs

### "Video not found"
- Make sure video_id is correct
- Video must be public or owned by you

### View not recording
- If you viewed it in last 30 seconds, it won't count (spam prevention)
- Wait 30 seconds and try again

---

## Next Steps

1. **Phase 2:** Add search, recommendations, trending
2. **Phase 3:** Add analytics dashboard, advanced monetization
3. **Phase 4:** Live streaming, multi-region, DRM

---

**Ready to go?** Start with [Authentication](#get-authentication-token) above! 🚀
