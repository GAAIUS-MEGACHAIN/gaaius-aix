# 💖 Donation & Tipping System - Complete Guide

## 🎯 Overview

The Donation & Tipping System is a comprehensive creator monetization platform integrated throughout GAAIUS AI. It enables:

- ✅ Direct tips to creators on videos, music, courses, events, livestreams
- ✅ Donation campaigns for fundraising
- ✅ Recurring memberships/subscriptions
- ✅ Multi-currency support (USD, EUR, ZAR, NGN, KES, GBP, JPY, INR)
- ✅ Multiple payment methods (PayPal, Stripe, PayFast, Crypto)
- ✅ Creator earnings dashboard
- ✅ Top donor tracking
- ✅ Thank you messages
- ✅ Transaction history
- ✅ Tip tiers with emojis

---

## 📁 File Structure

### Backend Files
```
backend/
├── donation_tipping_service.py    # Core service (600+ lines)
├── donation_tipping_routes.py     # API endpoints (400+ lines)
└── server.py                      # Updated with routers
```

### Frontend Files
```
frontend/src/components/
├── DonationButton.jsx             # Reusable tip button
└── CreatorEarningsWidget.jsx      # Creator earnings display
```

### Existing Components Updated
```
frontend/src/components/
├── DonationTab.jsx                # Standalone donation campaigns
├── VideoPlayer.jsx                # Add tip button
├── MusicPlayer.jsx                # Add tip button
├── ChatInterface.jsx              # Direct user tips
├── CourseLesson.jsx               # Tip instructor
├── EventCard.jsx                  # Tip organizer
└── LivestreamPlayer.jsx           # Real-time tips
```

---

## 🔌 API Endpoints

### Donation Endpoints

#### Create Tip
```
POST /api/donate/{creator_id}?donor_id={user_id}
```

**Request Body:**
```json
{
  "creator_id": "string",
  "content_id": "string (optional)",
  "content_type": "video|music|audio|course|livestream|event|chat|project|product",
  "amount": 10.50,
  "currency": "usd|eur|gbp|zar|ngn|kes|jpy|inr",
  "payment_method": "paypal|stripe|payfast|crypto",
  "message": "Great content!",
  "donor_name": "John Doe",
  "visibility": "public|private|anonymous"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Tip of $10.50 created successfully",
  "tip_id": "abc123",
  "status": "pending",
  "amount": "10.50",
  "creator_fee": "9.95"
}
```

#### Get Creator Tips
```
GET /api/donate/creator/{creator_id}/tips?limit=50
```

**Response:**
```json
[
  {
    "id": "tip123",
    "donor_id": "donor456",
    "creator_id": "creator789",
    "amount": "25.00",
    "currency": "usd",
    "status": "completed",
    "timestamp": "2026-01-21T10:30:00Z",
    "visibility": "public",
    "message": "Love your work!",
    "donor_name": "Jane Smith"
  }
]
```

#### Get Content Tips
```
GET /api/donate/content/{content_id}
```

**Response:**
```json
{
  "success": true,
  "content_id": "video123",
  "tips_count": 15,
  "total_amount": "250.75",
  "tips": [...]
}
```

#### Get Top Donors
```
GET /api/donate/top-donors/{creator_id}?limit=10
```

---

### Campaign Endpoints

#### Create Campaign
```
POST /api/campaigns?creator_id={user_id}
```

**Request Body:**
```json
{
  "title": "Emergency Relief Fund",
  "description": "Help us support...",
  "goal_amount": 5000,
  "currency": "usd",
  "category": "charity|personal|community|education",
  "thumbnail_url": "https://...",
  "reward_tiers": [
    {
      "name": "$10 Supporter",
      "amount": 10,
      "emoji": "🎁",
      "description": "Your name on our supporters page",
      "perks": ["Supporter badge"]
    }
  ]
}
```

#### List Campaigns
```
GET /api/campaigns?creator_id=optional&limit=20
```

#### Get Campaign Details
```
GET /api/campaigns/{campaign_id}
```

#### Donate to Campaign
```
POST /api/campaigns/{campaign_id}/donate?donor_id={user_id}
```

**Request Body:**
```json
{
  "amount": 25.00,
  "currency": "usd",
  "payment_method": "stripe",
  "message": "Keep up the great work!"
}
```

---

### Creator Endpoints

#### Get Creator Stats
```
GET /api/creator/{creator_id}/stats
```

**Response:**
```json
{
  "total_earned": "1250.50",
  "total_tips": 45,
  "total_donors": 32,
  "monthly_earned": "350.75",
  "yearly_earned": "4200.00",
  "avg_tip": "27.81",
  "top_tip": "150.00",
  "monthly_recurring": "200.00",
  "recurring_donors": 4,
  "top_donors": [...],
  "daily_tips": {
    "2026-01-21": 5,
    "2026-01-20": 3
  }
}
```

#### Get Creator Earnings
```
GET /api/creator/{creator_id}/earnings
```

#### Get Creator Settings
```
GET /api/creator/{creator_id}/settings
```

#### Update Creator Settings
```
PUT /api/creator/{creator_id}/settings
```

**Request Body:**
```json
{
  "donations_enabled": true,
  "bio": "Support my work!",
  "allow_custom_amount": true,
  "min_custom_amount": 0.50,
  "max_custom_amount": 10000,
  "custom_tiers": [...],
  "thank_you_message": "Thanks for your support!",
  "public_leaderboard": true,
  "notification_on_tip": true,
  "preferred_currency": "usd"
}
```

#### Send Thank You Message
```
POST /api/creator/{creator_id}/thank-you/{donation_id}
```

**Request Body:**
```json
{
  "donation_id": "tip123",
  "creator_id": "creator789",
  "donor_id": "donor456",
  "message": "Thank you so much for your support!",
  "is_public": true,
  "video_url": "https://... (optional)"
}
```

---

## 🎨 Frontend Integration Examples

### Using DonationButton Component

```jsx
import DonationButton from './components/DonationButton';

// In your video player, music player, course page, etc.
export const VideoPlayer = ({ videoId, creatorId }) => {
  return (
    <div>
      <video controls src={videoUrl} />
      
      {/* Add tip button */}
      <DonationButton
        creatorId={creatorId}
        contentId={videoId}
        contentType="video"
        showLabel={true}
        onDonationSuccess={(data) => {
          console.log('Donation successful:', data);
        }}
      />
    </div>
  );
};
```

### Using CreatorEarningsWidget

```jsx
import CreatorEarningsWidget from './components/CreatorEarningsWidget';

export const CreatorProfile = ({ creatorId }) => {
  return (
    <div>
      <h1>Creator Profile</h1>
      
      {/* Show earnings */}
      <CreatorEarningsWidget creatorId={creatorId} />
    </div>
  );
};
```

### Custom Tip Implementation

```jsx
const handleTip = async (amount, currency) => {
  try {
    const response = await axios.post(
      `${API_URL}/api/donate/${creatorId}?donor_id=${userId}`,
      {
        creator_id: creatorId,
        content_id: contentId,
        content_type: 'video',
        amount: amount,
        currency: currency,
        payment_method: 'stripe',
        message: 'Great content!',
        visibility: 'public'
      },
      {
        headers: { Authorization: `Bearer ${token}` }
      }
    );
    
    if (response.data.success) {
      toast.success('Tip sent!');
    }
  } catch (error) {
    toast.error('Failed to send tip');
  }
};
```

---

## 💰 Default Tip Tiers

```javascript
[
  { name: "☕ Coffee", amount: 2, emoji: "☕" },
  { name: "🎁 Gift", amount: 5, emoji: "🎁" },
  { name: "🌟 Star", amount: 10, emoji: "🌟" },
  { name: "💎 Diamond", amount: 25, emoji: "💎" },
  { name: "👑 Royalty", amount: 50, emoji: "👑" },
  { name: "🚀 Legend", amount: 100, emoji: "🚀" }
]
```

---

## 🌍 Supported Currencies

| Code | Currency | Symbol |
|------|----------|--------|
| USD | US Dollar | $ |
| EUR | Euro | € |
| GBP | British Pound | £ |
| ZAR | South African Rand | R |
| NGN | Nigerian Naira | ₦ |
| KES | Kenyan Shilling | Ksh |
| JPY | Japanese Yen | ¥ |
| INR | Indian Rupee | ₹ |
| ETH | Ethereum | Ξ |
| BTC | Bitcoin | ₿ |

---

## 🔐 Payment Methods

1. **PayPal** - Global payment processor
2. **Stripe** - Credit/debit cards
3. **PayFast** - Popular in South Africa
4. **Cryptocurrency** - ETH, BTC (coming soon)
5. **Bank Transfer** - Direct bank deposits (coming soon)

---

## 📊 Database Models

### Tip Document
```javascript
{
  id: "unique_tip_id",
  donor_id: "user_id",
  creator_id: "creator_id",
  content_id: "video_id (optional)",
  content_type: "video|music|etc",
  amount: 25.00,
  currency: "usd",
  payment_method: "stripe",
  message: "Great work!",
  donor_name: "Jane Doe",
  visibility: "public|private|anonymous",
  transaction_id: "stripe_transaction_id",
  status: "pending|completed|failed|refunded",
  timestamp: "2026-01-21T10:30:00Z",
  platform_fee: 1.25,
  creator_net: 23.75,
  processed_at: "2026-01-21T10:31:00Z",
  refund_reason: null,
  refunded_at: null,
  thanked: false
}
```

### DonationCampaign Document
```javascript
{
  id: "campaign_id",
  creator_id: "creator_id",
  title: "Emergency Relief Fund",
  description: "Help us support local communities",
  goal_amount: 5000,
  currency: "usd",
  current_amount: 3250.75,
  donor_count: 145,
  start_date: "2026-01-20T00:00:00Z",
  end_date: "2026-02-20T00:00:00Z",
  category: "charity",
  thumbnail_url: "https://...",
  reward_tiers: [...],
  active: true,
  featured: false
}
```

### CreatorDonationSettings Document
```javascript
{
  creator_id: "creator_id",
  donations_enabled: true,
  bio: "Support my work!",
  custom_tiers: [...],
  allow_custom_amount: true,
  min_custom_amount: 0.50,
  max_custom_amount: 10000,
  payment_methods: ["paypal", "stripe"],
  paypal_email: "creator@example.com",
  stripe_account_id: "acct_xxx",
  thank_you_message: "Thanks for supporting me!",
  public_leaderboard: true,
  notification_on_tip: true,
  preferred_currency: "usd",
  platform_fee_percent: 5.0,
  created_at: "2026-01-01T00:00:00Z",
  updated_at: "2026-01-21T10:30:00Z"
}
```

---

## 🎯 Integration Points

### 1. Video Players
```jsx
<DonationButton 
  creatorId={videoCreatorId} 
  contentId={videoId} 
  contentType="video" 
/>
```

### 2. Music Players
```jsx
<DonationButton 
  creatorId={artistId} 
  contentId={trackId} 
  contentType="music" 
/>
```

### 3. Chat Interface
```jsx
<DonationButton 
  creatorId={userId} 
  contentType="chat" 
  compact={true}
/>
```

### 4. Course Lessons
```jsx
<DonationButton 
  creatorId={instructorId} 
  contentId={courseId} 
  contentType="course" 
/>
```

### 5. Events
```jsx
<DonationButton 
  creatorId={organizerId} 
  contentId={eventId} 
  contentType="event" 
/>
```

### 6. Livestreams
```jsx
<DonationButton 
  creatorId={streamerID} 
  contentId={streamId} 
  contentType="livestream" 
/>
```

### 7. Creator Profiles
```jsx
<div>
  <CreatorEarningsWidget creatorId={creatorId} />
  <DonationButton creatorId={creatorId} showLabel={true} />
</div>
```

---

## 🔄 Fee Structure

- **Platform Fee**: 5% (default, configurable per creator)
- **Payment Processor Fee**: ~2.9% + $0.30 (Stripe/PayPal)
- **Creator Net**: Amount after platform fee

**Example:**
- Donor sends: $10.00
- Platform fee (5%): -$0.50
- Creator receives: $9.50

---

## 📈 Creator Dashboard Stats

The `CreatorEarningsWidget` displays:
- ✅ Total earned
- ✅ Total tips received
- ✅ Total unique donors
- ✅ Monthly earnings
- ✅ Monthly recurring revenue
- ✅ Average tip amount
- ✅ Top tip amount
- ✅ Top supporters list
- ✅ Daily tips breakdown

---

## 🚀 Getting Started

### 1. Setup Backend
```bash
cd backend
pip install -r requirements.txt
python run_server.py
```

### 2. Setup Frontend
```bash
cd frontend
npm install --legacy-peer-deps
npm start
```

### 3. Test Endpoints
```bash
# Create a tip
curl -X POST "http://localhost:8000/api/donate/creator123?donor_id=donor456" \
  -H "Content-Type: application/json" \
  -d '{
    "creator_id": "creator123",
    "content_type": "video",
    "amount": 10.50,
    "currency": "usd",
    "payment_method": "stripe",
    "message": "Great content!"
  }'

# Get creator stats
curl -X GET "http://localhost:8000/api/creator/creator123/stats" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🎨 Customization

### Change Default Tip Tiers
Edit `donation_tipping_service.py`:
```python
self.default_tiers = [
    TipTier(name="Custom", amount=Decimal("15"), emoji="🎯"),
    # Add more tiers...
]
```

### Adjust Platform Fee
In creator settings:
```python
platform_fee_percent: Decimal = Field(default=Decimal("3"))  # 3% instead of 5%
```

### Enable Crypto Payments
```python
payment_methods=[
    PaymentMethod.PAYPAL,
    PaymentMethod.STRIPE,
    PaymentMethod.CRYPTOCURRENCY
]
```

---

## 🔐 Security Considerations

- ✅ All amounts validated (min $0.50, max $10,000)
- ✅ Authentication required on all endpoints
- ✅ Decimal precision for financial calculations
- ✅ Transaction logging for audit trail
- ✅ Refund handling with reasons
- ✅ Anonymous donation support
- ✅ Rate limiting on payment endpoints

---

## 📊 Analytics & Reporting

Track:
- Creator earnings by period
- Donor retention rates
- Average tip amounts
- Top performing content
- Donation trends
- Campaign success rates

---

## 🆘 Troubleshooting

### Tip Not Processing
- Check user authentication
- Verify payment method is configured
- Ensure amount is within limits ($0.50 - $10,000)

### Creator Settings Not Saving
- Verify creator_id in request
- Check database connection
- Review error logs

### Stats Not Updating
- Wait a moment for async processing
- Verify tip status is "completed"
- Check database indexes

---

## 📞 Support

For issues or questions:
1. Check this guide
2. Review API documentation
3. Check server logs
4. Create an issue in the repository

---

**Last Updated**: January 21, 2026  
**Status**: ✅ Production Ready  
**Version**: 1.0.0
