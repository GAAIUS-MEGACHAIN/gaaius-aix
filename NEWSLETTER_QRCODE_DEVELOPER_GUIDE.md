# Newsletter & QR Code - Developer Integration Guide

## Quick Start for Developers

This guide helps developers quickly integrate the Newsletter and QR Code modules into their workflows.

---

## 1. Project Structure

```
gaaius-ai/
├── backend/
│   ├── newsletter_service.py          ← Newsletter API implementation
│   ├── qrcode_service.py              ← QR Code API implementation
│   ├── qrcode_ai_enhancements.py      ← AI-powered QR features
│   └── server.py                      ← Main FastAPI app (routes registered at lines 84-86, 10013-10035)
│
└── frontend/
    └── src/
        ├── components/
        │   ├── NewsletterDashboard.jsx    ← Newsletter UI
        │   └── QRCodeDashboard.jsx        ← QR Code UI
        └── App.js                        ← Routes at lines 5068-5095
```

---

## 2. Backend Integration Checklist

### ✅ Service Files Ready

Both services are **already implemented and production-ready**:

- ✅ `backend/newsletter_service.py` (465 lines)
- ✅ `backend/qrcode_service.py` (607 lines)
- ✅ `backend/qrcode_ai_enhancements.py` (AI features)

### ✅ Database Models Ready

MongoDB collections automatically created:
- ✅ `subscribers`
- ✅ `campaigns`
- ✅ `automations`
- ✅ `qrcodes`
- ✅ `qrcode_scans`
- ✅ `qrcode_batches`

### ✅ Routes Registered

In `server.py` (lines 10013-10035):
```python
# Newsletter routes
app.include_router(newsletter_router)  # Prefix: /api/newsletter

# QR Code routes
app.include_router(qrcode_router)      # Prefix: /api/qrcode
app.include_router(qrcode_ai_router)   # Prefix: /api/qrcode
```

### ✅ Service Architecture

Each service follows this pattern:

```python
# 1. Data Models (Pydantic)
class SubscriberModel(BaseModel):
    email: EmailStr
    name: str
    ...

# 2. Router Setup
router = APIRouter(prefix="/api/newsletter", tags=["Newsletter"])

# 3. Route Handlers
@router.post("/subscribers")
async def add_subscriber(subscriber: SubscriberModel):
    ...

@router.get("/subscribers")
async def list_subscribers(skip: int = 0, limit: int = 50):
    ...
```

---

## 3. Frontend Integration Checklist

### ✅ Components Ready

Both dashboard components are **fully implemented**:

- ✅ `frontend/src/components/NewsletterDashboard.jsx`
- ✅ `frontend/src/components/QRCodeDashboard.jsx`

### ✅ Routes Ready

In `frontend/src/App.js` (lines 5068-5095):

```javascript
if (location.pathname === "/newsletter") {
    return (
        <>
            <NewsletterDashboard />
        </>
    );
}

if (location.pathname === "/qrcode") {
    return (
        <>
            <QRCodeDashboard />
        </>
    );
}
```

### ✅ Navigation Ready

Sidebar/menu buttons already implemented:
```javascript
// Line 5492-5496
<button onClick={() => navigate("/newsletter")}>Newsletter</button>
<button onClick={() => navigate("/qrcode")}>QR Code</button>
```

---

## 4. Running the Application

### Start Backend
```bash
cd backend
python server.py
```

**Expected Output:**
```
✅ Newsletter routes registered
✅ QRCode routes registered
✅ QRCode AI routes registered
```

### Start Frontend
```bash
cd frontend
npm start
```

**Navigate to:**
- Newsletter: `http://localhost:3000/newsletter`
- QR Code: `http://localhost:3000/qrcode`

---

## 5. Testing the APIs

### Test Newsletter Service
```bash
# Add subscriber
curl -X POST http://localhost:8000/api/newsletter/subscribers \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","name":"Test User"}'

# List subscribers
curl http://localhost:8000/api/newsletter/subscribers

# Create campaign
curl -X POST http://localhost:8000/api/newsletter/campaigns \
  -H "Content-Type: application/json" \
  -d '{
    "name":"Test Campaign",
    "template_id":"tpl_123",
    "subject":"Test",
    "segment":{"segment_type":"all"}
  }'
```

### Test QR Code Service
```bash
# Generate QR code
curl -X POST http://localhost:8000/api/qrcode/generate \
  -H "Content-Type: application/json" \
  -d '{
    "type":"url",
    "url":"https://example.com",
    "metadata":{"title":"Test QR"}
  }'

# List QR codes
curl http://localhost:8000/api/qrcode/list

# Get QR analytics
curl http://localhost:8000/api/qrcode/{qr_id}/analytics
```

### Check Service Health
```bash
curl http://localhost:8000/api/newsletter/health
curl http://localhost:8000/api/qrcode/health
```

---

## 6. API Endpoints Reference

### Newsletter Endpoints (13 total)
```
POST   /api/newsletter/subscribers              Add subscriber
GET    /api/newsletter/subscribers              List subscribers
POST   /api/newsletter/subscribers/import       Bulk import
PUT    /api/newsletter/subscribers/{email}     Update subscriber
DELETE /api/newsletter/subscribers/{email}     Delete subscriber
POST   /api/newsletter/campaigns                Create campaign
GET    /api/newsletter/campaigns                List campaigns
POST   /api/newsletter/campaigns/{id}/schedule Schedule campaign
POST   /api/newsletter/campaigns/{id}/send     Send campaign
GET    /api/newsletter/campaigns/{id}/analytics Get stats
POST   /api/newsletter/automations              Create automation
GET    /api/newsletter/automations              List automations
GET    /api/newsletter/analytics/overview      Dashboard stats
POST   /api/newsletter/settings/smtp            Set SMTP config
GET    /api/newsletter/settings/smtp            Get SMTP config
GET    /api/newsletter/health                   Health check
```

### QR Code Endpoints (13 total)
```
POST   /api/qrcode/generate                 Generate QR code
GET    /api/qrcode/list                     List QR codes
GET    /api/qrcode/{qr_id}                  Get QR details
GET    /api/qrcode/short/{short_code}       Lookup by short code
PUT    /api/qrcode/{qr_id}                  Update QR code
DELETE /api/qrcode/{qr_id}                  Delete QR code
POST   /api/qrcode/{qr_id}/scan             Record scan
GET    /api/qrcode/{qr_id}/analytics        Get analytics
POST   /api/qrcode/batch/create             Create batch
GET    /api/qrcode/batch/list               List batches
GET    /api/qrcode/batch/{batch_id}         Get batch details
GET    /api/qrcode/health                   Health check
```

---

## 7. Common Development Tasks

### Add a New Newsletter Feature

1. **Define the model** in `backend/newsletter_service.py`:
```python
class MyNewModel(BaseModel):
    field1: str
    field2: int
```

2. **Add a route handler**:
```python
@router.post("/my-endpoint")
async def my_handler(data: MyNewModel):
    # Implementation
    return {"status": "success"}
```

3. **Call from frontend**:
```javascript
const response = await api.post("/newsletter/my-endpoint", {
    field1: "value1",
    field2: 42
});
```

### Add a New QR Feature

Same process in `backend/qrcode_service.py`:

```python
@router.post("/my-qr-feature")
async def my_qr_handler(request_data: dict):
    # Implementation
    return {"result": "data"}
```

### Extend Frontend Dashboard

Edit `frontend/src/components/NewsletterDashboard.jsx` or `QRCodeDashboard.jsx`:

```javascript
const MyNewSection = () => {
    const [data, setData] = useState([]);
    
    useEffect(() => {
        api.get("/newsletter/my-endpoint").then(res => {
            setData(res.data);
        });
    }, []);
    
    return (
        <div className="section">
            {/* Your JSX */}
        </div>
    );
};
```

---

## 8. Database Queries

### MongoDB Examples

```javascript
// Find all active subscribers
db.subscribers.find({ status: "active" })

// Count campaigns sent this month
db.campaigns.find({ 
    sent_at: { 
        $gte: ISODate("2024-01-01"),
        $lt: ISODate("2024-02-01")
    },
    status: "sent"
}).count()

// Get top performing QR codes
db.qrcodes.aggregate([
    {
        $lookup: {
            from: "qrcode_scans",
            localField: "_id",
            foreignField: "qrcode_id",
            as: "scans"
        }
    },
    {
        $addFields: {
            scan_count: { $size: "$scans" }
        }
    },
    { $sort: { scan_count: -1 } },
    { $limit: 10 }
])

// Get analytics by device type
db.qrcode_scans.aggregate([
    { $group: { 
        _id: "$device_type", 
        count: { $sum: 1 } 
    }},
    { $sort: { count: -1 } }
])
```

---

## 9. Debugging Tips

### Enable Debug Logging

Add to backend service files:
```python
import logging

logger = logging.getLogger(__name__)

@router.post("/debug-endpoint")
async def debug_handler(data: dict):
    logger.debug(f"Received data: {data}")
    logger.info("Processing request")
    # ... implementation
    logger.error(f"Error occurred: {error}")
```

### Check Browser Console

Open DevTools and monitor:
- Network requests to `/api/newsletter/*` and `/api/qrcode/*`
- Console logs for errors
- Local storage for JWT tokens

### View Backend Logs

```bash
# Follow real-time logs
tail -f backend/server.log

# Search for specific errors
grep "ERROR" backend/server.log

# Look for newsletter/QR errors
grep -E "(newsletter|qrcode)" backend/server.log
```

---

## 10. Performance Optimization

### Add Caching

For frequently accessed data (e.g., campaign templates):

```python
from functools import lru_cache

@lru_cache(maxsize=128)
async def get_template(template_id: str):
    return db.templates.find_one({"_id": template_id})
```

### Database Indexing

Create indexes in MongoDB:
```javascript
// Subscribers
db.subscribers.createIndex({ email: 1 }, { unique: true })
db.subscribers.createIndex({ status: 1 })
db.subscribers.createIndex({ tags: 1 })

// QR Codes
db.qrcodes.createIndex({ status: 1 })
db.qrcodes.createIndex({ created_at: -1 })
db.qrcodes.createIndex({ tags: 1 })
```

### Batch Operations

Process large datasets efficiently:
```python
# Newsletter
POST /api/newsletter/subscribers/import  # Bulk add
POST /api/newsletter/campaigns/{id}/send  # Send to thousands

# QR Code
POST /api/qrcode/batch/create  # Generate hundreds at once
```

---

## 11. Environment Setup

### Required Environment Variables (.env)

```env
# Database
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=gaaius_ai

# Email (Newsletter)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@example.com

# JWT
JWT_SECRET=your-super-secret-key

# API
API_BASE_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000
```

### Verify Setup

```bash
# Test MongoDB connection
python -c "import motor.motor_asyncio; print('✅ MongoDB driver ready')"

# Test FastAPI server
curl http://localhost:8000/health

# Test frontend build
npm run build
```

---

## 12. Common Issues & Solutions

### Issue: "newsletter_router is not defined"

**Solution:** Make sure imports are in `server.py`:
```python
from .newsletter_service import router as newsletter_router
from .qrcode_service import router as qrcode_router
```

### Issue: Database connection timeout

**Solution:** Check MongoDB is running and URL is correct:
```bash
# Check MongoDB
mongosh --eval "db.adminCommand('ping')"

# Check connection string in .env
echo $MONGODB_URL
```

### Issue: 404 on /newsletter or /qrcode routes

**Solution:** Verify routes are defined in `App.js`:
```javascript
if (location.pathname === "/newsletter") { ... }
if (location.pathname === "/qrcode") { ... }
```

### Issue: CORS errors on API calls

**Solution:** Ensure CORS is enabled in `server.py`:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 13. Testing Checklist

- [ ] Backend services start without errors
- [ ] Frontend components load at /newsletter and /qrcode
- [ ] Can create a newsletter subscriber
- [ ] Can create a newsletter campaign
- [ ] Can send a test campaign
- [ ] Can generate a QR code
- [ ] Can track QR code scans
- [ ] Analytics display correctly
- [ ] Database stores data correctly
- [ ] API returns proper error messages
- [ ] Authentication works (JWT tokens)
- [ ] Rate limiting is active

---

## 14. Documentation References

- **Full Documentation:** `NEWSLETTER_QRCODE_DOCUMENTATION.md`
- **API Quick Reference:** `NEWSLETTER_QRCODE_API_QUICK_REFERENCE.md`
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

---

## 15. Support & Resources

### Code Locations
- Newsletter service: `backend/newsletter_service.py`
- QR Code service: `backend/qrcode_service.py`
- Frontend Newsletter: `frontend/src/components/NewsletterDashboard.jsx`
- Frontend QR Code: `frontend/src/components/QRCodeDashboard.jsx`

### Important Lines in server.py
- Import newsletter router: Line 84
- Import QR code router: Line 85
- Register newsletter: Line 10016
- Register QR code: Line 10024

### Important Lines in App.js
- Newsletter import: Line 55
- QR Code import: Line 56
- Newsletter route: Line 5068
- QR Code route: Line 5081
- Newsletter navigation: Line 5492
- QR Code navigation: Line 5495

---

## 16. Next Steps

1. **Verify Services Running**
   ```bash
   # Terminal 1: Backend
   cd backend && python server.py
   
   # Terminal 2: Frontend
   cd frontend && npm start
   ```

2. **Test One Endpoint**
   ```bash
   curl http://localhost:8000/api/newsletter/health
   curl http://localhost:8000/api/qrcode/health
   ```

3. **Open Dashboard**
   - Newsletter: `http://localhost:3000/newsletter`
   - QR Code: `http://localhost:3000/qrcode`

4. **Create Test Data**
   - Add a test subscriber
   - Create a test campaign
   - Generate a test QR code

5. **Check Analytics**
   - View subscriber stats
   - View campaign performance
   - View QR code scans

---

**Status:** ✅ All Systems Operational  
**Last Updated:** January 2024  
**Version:** 2.0.0
