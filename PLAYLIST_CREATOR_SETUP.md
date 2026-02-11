# How to Integrate Playlist Creator into server.py

## Step 1: Import the Playlist Routes

Add this import at the top of your `server.py`:

```python
from backend.playlist_creator_routes import (
    router_playlist,
    router_create,
    router_share
)
```

## Step 2: Include the Routers

Add these lines where you include other routers in your `server.py`:

```python
# Add Playlist Creator routers
app.include_router(router_playlist)
app.include_router(router_create)
app.include_router(router_share)
```

Or if you use an `api_router` pattern:

```python
api_router.include_router(router_playlist)
api_router.include_router(router_create)
api_router.include_router(router_share)

# Then include the api_router in the app
app.include_router(api_router, prefix="/api")
```

## Step 3: Add to Frontend App.js

```jsx
import PlaylistCreator from '@/components/PlaylistCreator';

// Inside your route definitions:
<Route path="/playlists" element={<PlaylistCreator />} />

// Add to navigation:
<Link to="/playlists">🎵 Playlists</Link>
```

## Step 4: Database Integration (Optional but Recommended)

To persist playlists to MongoDB, update `playlist_creator.py`:

```python
# Add at top
import motor.motor_asyncio
from pymongo import ASCENDING

class PlaylistCreator:
    def __init__(self, db=None):
        self.playlists: Dict[str, Playlist] = {}
        self.db = db  # MongoDB connection
        self.templates: Dict[str, PlaylistTemplate] = self._init_templates()
    
    async def create_playlist(self, ...):
        # ... existing code ...
        
        # Save to MongoDB
        if self.db:
            await self.db.playlists.insert_one(playlist.dict())
        
        self.playlists[playlist_id] = playlist
        return playlist
```

## Step 5: Verify All Endpoints Work

Test the endpoints:

```bash
# Create playlist
curl -X POST "http://localhost:8000/api/playlists" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Playlist",
    "user_id": "user-123",
    "user_name": "Test User",
    "description": "Test Description",
    "visibility": "public"
  }'

# Get user playlists
curl "http://localhost:8000/api/playlists?user_id=user-123"

# Get templates
curl "http://localhost:8000/api/playlists/create/templates"

# Search
curl "http://localhost:8000/api/playlists/search/find?query=workout"

# Trending
curl "http://localhost:8000/api/playlists/trending/all"
```

## Complete Integration Pattern

### Option A: Minimal Integration (Use As-Is)

```python
# server.py
from backend.playlist_creator_routes import router_playlist, router_create, router_share

app = FastAPI()

# Include playlist routers
app.include_router(router_playlist)
app.include_router(router_create)
app.include_router(router_share)

# That's it! All 25+ endpoints are now available
```

### Option B: With Dependency Injection

```python
# server.py
from backend.playlist_creator import PlaylistCreator
from backend.playlist_creator_routes import (
    router_playlist, router_create, router_share,
    playlist_service
)

@app.on_event("startup")
async def startup():
    # Initialize playlist service with MongoDB
    global playlist_service
    playlist_service.db = db  # Your MongoDB connection

app.include_router(router_playlist)
app.include_router(router_create)
app.include_router(router_share)
```

### Option C: Custom Wrapper

```python
# server.py
from backend.playlist_creator_routes import playlist_service

@app.post("/api/custom/playlist")
async def custom_create(
    name: str,
    user_id: str,
    description: str = ""
):
    """Custom endpoint with additional logic"""
    # Add custom validation
    if len(name) < 3:
        raise HTTPException(status_code=400, detail="Name too short")
    
    # Use the service
    playlist = await playlist_service.create_playlist(
        name=name,
        creator_id=user_id,
        creator_name="Unknown",
        description=description
    )
    
    return {"playlist_id": playlist.playlist_id}
```

## Frontend Integration

### Update App.js

```jsx
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import PlaylistCreator from '@/components/PlaylistCreator';

function App() {
  return (
    <BrowserRouter>
      <nav>
        <Link to="/">Home</Link>
        <Link to="/playlists">🎵 Playlists</Link>
      </nav>
      
      <Routes>
        <Route path="/playlists" element={<PlaylistCreator />} />
        {/* Other routes */}
      </Routes>
    </BrowserRouter>
  );
}

export default App;
```

### Update localStorage for User Data

The component expects user data in localStorage:

```javascript
// When user logs in
localStorage.setItem('userId', user.id);
localStorage.setItem('userName', user.name);

// Component will use these for all playlist operations
```

## API Endpoint Categories

All 25+ endpoints organized by functionality:

### Basic CRUD (5 endpoints)
```
POST   /api/playlists                     - Create
GET    /api/playlists/{id}                - Read
GET    /api/playlists                     - List
PATCH  /api/playlists/{id}                - Update
DELETE /api/playlists/{id}                - Delete
```

### Items (4 endpoints)
```
POST   /api/playlists/{id}/items          - Add
DELETE /api/playlists/{id}/items/{item}   - Remove
GET    /api/playlists/{id}/items          - List
POST   /api/playlists/{id}/reorder        - Reorder
```

### Engagement (3 endpoints)
```
POST   /api/playlists/{id}/like           - Like
POST   /api/playlists/{id}/save           - Save
POST   /api/playlists/{id}/follow         - Follow
```

### Sharing (3 endpoints)
```
POST   /api/playlists/share/{id}          - Share
POST   /api/playlists/share/{id}/duplicate - Duplicate
POST   /api/playlists/share/{id}/collaborator - Collaborate
```

### Discovery (3 endpoints)
```
GET    /api/playlists/search/find         - Search
GET    /api/playlists/trending/all        - Trending
GET    /api/playlists/recommendations     - Recommendations
```

### Creation (6 endpoints)
```
POST   /api/playlists/create/music        - Music
POST   /api/playlists/create/movies       - Movies
POST   /api/playlists/create/videos       - Videos
POST   /api/playlists/create/music-videos - Music Videos
POST   /api/playlists/create/mixed-content - Mixed
POST   /api/playlists/create/from-template - Template
```

### Templates (2 endpoints)
```
GET    /api/playlists/create/templates    - List
POST   /api/playlists/create/from-template - Create from
```

**Total: 25+ RESTful endpoints**

## Environment Setup

### Requirements

Add to `requirements.txt`:

```txt
fastapi>=0.104.0
pydantic>=2.0.0
motor>=3.3.0  # For async MongoDB
```

### Config

```python
# config.py
PLAYLIST_MAX_ITEMS = 500
PLAYLIST_MAX_NAME_LENGTH = 100
PLAYLIST_MAX_DESCRIPTION_LENGTH = 500
PLAYLIST_MAX_TAGS = 10
PLAYLIST_SEARCH_LIMIT_MAX = 100
```

## Error Handling

The API returns proper HTTP status codes:

```
200 OK              - Success
201 Created         - Resource created
400 Bad Request     - Invalid input
403 Forbidden       - Permission denied
404 Not Found       - Resource not found
500 Server Error    - Internal error
```

Example error response:

```json
{
  "status": 400,
  "detail": "Playlist name is required",
  "error_code": "INVALID_INPUT"
}
```

## Rate Limiting

Add rate limiting to prevent abuse:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/playlists")
@limiter.limit("50/hour")
async def create_playlist(...):
    # Implementation
    pass
```

## Logging

Playlist Creator logs important events:

```python
import logging

logger = logging.getLogger(__name__)

# Events logged:
# - Playlist creation
# - Item addition/removal
# - Share events
# - Collaboration changes
# - Error conditions
```

## Security Considerations

1. **Authentication**: Verify user before playlist operations
2. **Authorization**: Check ownership before modifications
3. **Validation**: All inputs are validated with Pydantic
4. **Rate Limiting**: Prevent API abuse with rate limits
5. **CORS**: Configure CORS if frontend is on different domain
6. **HTTPS**: Use HTTPS in production

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Performance Tips

1. **Use pagination**: Always use skip/limit for list endpoints
2. **Cache trending**: Cache trending results for 1 hour
3. **Batch operations**: Add multiple items in single request
4. **Index frequently searched fields**: name, creator_id, visibility
5. **Monitor database**: Track slow queries

## Testing

```bash
# Using pytest
pytest tests/test_playlist_creator.py -v

# Using curl
bash scripts/test_playlists.sh

# Using Postman
Import PLAYLIST_CREATOR_GUIDE.md examples
```

## Troubleshooting

### Issue: "Playlist not found"
- Verify playlist_id is correct
- Check user has access to playlist
- Ensure playlist wasn't deleted

### Issue: "Not authorized"
- Verify user_id matches creator_id
- Check collaboration permissions
- Confirm user is logged in

### Issue: "Max items reached"
- Remove items before adding more
- Max limit is 500 items per playlist

### Issue: "Query parameter missing"
- Check all required parameters are provided
- Verify parameter names match exactly

## Next Steps

1. ✅ Copy files to your project
2. ✅ Add imports to server.py
3. ✅ Include routers in FastAPI app
4. ✅ Update App.js with component
5. ✅ Test endpoints with curl
6. ✅ Deploy to production

**All done! Your playlist creator is ready to use.** 🎉
