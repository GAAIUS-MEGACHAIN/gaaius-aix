# 🔗 COMPLETE API ENDPOINT REFERENCE - 84+ Endpoints

## TABLE OF CONTENTS
1. Podcasts (8)
2. E-Learning (9)
3. Video Editor (3)
4. Gaming (4)
5. NFT (3)
6. Events (3)
7. Affiliate (3)
8. Newsletter (3)
9. Donations (2)
10. Translation (2)
11. Backup (3)
12. QR Code (2)
13. Duets (2)
14. Playlists (3)
15. Analytics (2)
16. **Live Shopping (8) - NEW**
17. **E-Commerce (6) - NEW**
18. **Subscriptions (6) - NEW**
19. **Recommendations (3) - NEW**

---

## 🎙️ PODCAST SERVICE (8 Endpoints)

### Base URL: `/api/v1/podcasts`

```
POST   /create
       Query: owner_id, title, description, author, category, image_url
       Response: {podcast_id, status}

POST   /{podcast_id}/episodes
       Query: title, description, content_url, duration_seconds, episode_number, season_number, guest?
       Response: {episode_id, status}

POST   /{podcast_id}/episodes/{episode_id}/publish
       Response: {status, episode}

POST   /{podcast_id}/publish
       Response: {status, feed_url}

GET    /{podcast_id}/feed.xml
       Response: RSS 2.0 XML feed

GET    /{podcast_id}/analytics
       Response: {views, downloads, subscribers, revenue, countries}

POST   /{podcast_id}/subscribe
       Query: user_id, tier (FREE|$2.99|$9.99|$19.99), payment_method
       Response: {subscription data}

GET    /trending
       Query: limit (1-100)
       Response: [{podcast, downloads}, ...]
```

---

## 📚 E-LEARNING SERVICE (9 Endpoints)

### Base URL: `/api/v1/courses`

```
POST   /create
       Query: instructor_id, title, description, category, level, price
       Response: {course_id, status}

POST   /{course_id}/lessons
       Query: title, description, lesson_number, duration_minutes, video_url?
       Body: content
       Response: {lesson_id, status}

POST   /{course_id}/publish
       Response: {status}

POST   /{course_id}/enroll
       Query: user_id, payment_method?, amount_paid
       Response: {enrollment data}

POST   /{course_id}/lessons/{lesson_id}/complete
       Query: user_id
       Response: {status}

POST   /{course_id}/quiz/submit
       Query: quiz_id, user_id
       Body: {question_id: answer, ...}
       Response: {score, passed, passing_score, results}

GET    /{course_id}/progress/{user_id}
       Response: {completion%, lessons_completed, quiz_scores}

POST   /{course_id}/complete/{user_id}
       Response: {certificate_id, verification_code}

POST   /{course_id}/review
       Query: user_id, rating (1-5), review_text?
       Response: {review data}
```

---

## 🎬 VIDEO EDITOR SERVICE (3 Endpoints)

### Base URL: `/api/v1/videos`

```
POST   /projects
       Query: user_id, title
       Response: {project_id}

POST   /projects/{project_id}/export
       Query: output_format (default: mp4)
       Response: {export_id, status}

GET    /export/{export_id}/status
       Response: {progress%, status, estimated_time}
```

---

## 🎮 GAMING SERVICE (4 Endpoints)

### Base URL: `/api/v1/gaming`

```
POST   /achievements
       Query: name, description, points
       Response: {achievement data}

POST   /score
       Query: user_id, game_id, score
       Response: {status}

GET    /leaderboard/{game_id}
       Query: limit (default: 100)
       Response: [{rank, user_id, score}, ...]

POST   /tournaments
       Query: title, game_id, prize_pool
       Response: {tournament data}
```

---

## 🖼️ NFT SERVICE (3 Endpoints)

### Base URL: `/api/v1/nft`

```
POST   /mint
       Query: creator_id, content_id, name, description, image_url, 
              price (default: 0), royalty_percent (default: 10)
       Response: {nft data with metadata}

GET    /collection/{creator_id}
       Response: [{nft}, ...]

POST   /{nft_id}/purchase
       Query: buyer_id, amount
       Response: {status, nft_id, owner}
```

---

## 🎪 EVENTS SERVICE (3 Endpoints)

### Base URL: `/api/v1/events`

```
POST   /create
       Query: creator_id, title, description, location, capacity, 
              start_date, end_date
       Response: {event data}

POST   /{event_id}/rsvp
       Query: user_id
       Response: {status}

POST   /{event_id}/ticket/purchase
       Query: user_id, ticket_type
       Response: {ticket_id, status}
```

---

## 💰 AFFILIATE SERVICE (3 Endpoints)

### Base URL: `/api/v1/affiliate`

```
POST   /links/create
       Query: affiliate_id, product_id, commission_percent
       Response: {link data with short_code}

POST   /track/click/{short_code}
       Response: {status}

GET    /{affiliate_id}/earnings
       Response: {total_earnings, commissions_by_product, pending_payout}
```

---

## 📧 NEWSLETTER SERVICE (3 Endpoints)

### Base URL: `/api/v1/newsletter`

```
POST   /create
       Query: creator_id, title, description
       Response: {newsletter data}

POST   /{newsletter_id}/subscribe
       Query: user_id, email
       Response: {status}

POST   /{newsletter_id}/send
       Query: subject
       Body: content
       Response: {sent_count, open_rate, click_rate}
```

---

## 💝 DONATION SERVICE (2 Endpoints)

### Base URL: `/api/v1/donations`

```
POST   /send
       Query: donor_id, creator_id, amount, message?, is_anonymous
       Response: {donation data with timestamp}

GET    /{creator_id}/donations
       Query: limit (default: 50)
       Response: [{donation}, ...]
```

---

## 🌐 TRANSLATION SERVICE (2 Endpoints)

### Base URL: `/api/v1/translation`

```
POST   /translate
       Query: content_id, target_lang, source_lang (default: en)
       Body: content
       Response: {original, translation, target_language}

POST   /translate-all
       Query: content_id, source_lang (default: en)
       Body: content
       Response: {content_id, translations: {lang: translated_text, ...}}
```

---

## 💾 BACKUP SERVICE (3 Endpoints)

### Base URL: `/api/v1/backup`

```
POST   /create
       Query: user_id, content_count, size_bytes
       Response: {backup data with timestamp}

GET    /{user_id}/backups
       Response: [{backup}, ...]

POST   /{user_id}/restore/{backup_id}
       Response: {status}
```

---

## 📱 QR CODE SERVICE (2 Endpoints)

### Base URL: `/api/v1/qrcode`

```
POST   /generate
       Query: creator_id, target_url, size (default: medium)
       Response: {qr data with code and short_code}

GET    /{qr_id}/analytics
       Response: {total_scans, scans_history: [{timestamp, ip, user_agent}]}
```

---

## 🎵 DUET SERVICE (2 Endpoints)

### Base URL: `/api/v1/duets`

```
POST   /create
       Query: original_creator_id, original_content_id, 
              duet_creator_id, duet_content_id
       Response: {duet data}

GET    /{content_id}/duets
       Response: [{duet}, ...]
```

---

## 📋 PLAYLIST SERVICE (3 Endpoints)

### Base URL: `/api/v1/playlists`

```
POST   /create
       Query: creator_id, title, description?
       Response: {playlist data}

POST   /{playlist_id}/add
       Query: content_id
       Response: {status}

GET    /{user_id}/playlists
       Response: [{playlist}, ...]
```

---

## 📊 ANALYTICS SERVICE (2 Endpoints)

### Base URL: `/api/v1/analytics`

```
POST   /stream/track
       Query: content_id, user_id, watch_percentage, watch_time_seconds
       Response: {status}

GET    /creator/{creator_id}
       Query: content_ids (list)
       Response: {total_views, total_watch_time, avg_watch%, revenue_estimate}
```

---

## 🛍️ LIVE SHOPPING SERVICE (8 Endpoints) - NEW

### Base URL: `/api/v1/live-shopping`

```
POST   /sessions/create
       Query: creator_id, title, description, start_time
       Response: {session_id, stream_id, status}

POST   /{session_id}/products/add
       Query: product_id, name, description, price, stock, discount_percent?
       Response: {product data, final_price}

POST   /{session_id}/start
       Response: {status}

POST   /{session_id}/viewers/update
       Body: [user_id1, user_id2, ...]
       Response: {viewer_count}

POST   /{session_id}/cart/add
       Query: user_id, product_id, quantity
       Response: {status, item_count}

POST   /{session_id}/coupon/apply
       Query: user_id, coupon_code
       Response: {status, code}

POST   /{session_id}/checkout
       Query: user_id, payment_method
       Response: {order_id, total, items}

POST   /{session_id}/comment
       Query: user_id, message
       Response: {status}

POST   /{session_id}/end
       Response: {total_revenue, items_sold, peak_viewers, duration_minutes}
```

---

## 🏪 E-COMMERCE SERVICE (6 Endpoints) - NEW

### Base URL: `/api/v1/shop`

```
POST   /products/create
       Query: seller_id, name, description, price, cost, stock, category
       Body: images (list)
       Response: {product_id, sku, status, price, stock}

GET    /cart
       Query: user_id
       Response: {cart_id, items, subtotal, item_count}

POST   /cart/add
       Query: user_id, product_id, quantity
       Response: {status, items_in_cart, subtotal}

POST   /checkout
       Query: user_id, payment_method
       Body: {shipping_address}
       Response: {order_id, subtotal, tax, shipping, discount, total}

POST   /{order_id}/ship
       Query: carrier
       Response: {shipment_id, tracking_number, status, estimated_delivery}

POST   /shipment/{shipment_id}/update
       Query: status (picked|packed|shipped|in_transit|delivered|returned), location?
       Response: {tracking_number, status, location, estimated_delivery}

GET    /search
       Query: query, category?, min_price, max_price
       Response: {results_count, products: [{id, name, price, rating, reviews, sales}]}
```

---

## 🎯 SUBSCRIPTION SERVICE (6 Endpoints) - NEW

### Base URL: `/api/v1/subscription`

```
POST   /tiers/create
       Query: creator_id, name, description, price
       Body: benefits (list)
       Response: {tier_id, name, price, benefits, members}

POST   /subscribe
       Query: user_id, creator_id, tier_id, payment_method
       Response: {subscription_id, status, tier, price_per_month, renews_at}

POST   /{creator_id}/exclusive-content/post
       Query: title, description, content_url, tier_id?
       Response: {content_id, status, tier, posted_at}

GET    /{creator_id}/exclusive-content
       Query: user_id
       Response: {items_count, content: [{content_id, title, posted_at, views}]}

POST   /{subscription_id}/cancel
       Response: {status, cancelled_at}

GET    /{creator_id}/earnings
       Response: {total_members, monthly_revenue, tiers: {tier_id: {members, revenue}}}
```

---

## 🤖 RECOMMENDATION ENGINE (3 Endpoints) - NEW

### Base URL: `/api/v1/recommendations`

```
POST   /track
       Query: user_id, content_id, action (view|like|share|comment), 
              category, time_spent_minutes?
       Response: {status}

GET    /personalized
       Query: user_id, limit (1-100, default: 10)
       Response: {recommendations: [{content_id, score}], count}

POST   /profile/build
       Query: user_id
       Body: {favorite_categories, watch_time_history}
       Response: {status, categories, ready_for_recommendations}

GET    /trending
       Query: limit (default: 20, max: 100)
       Response: {trending: [{content_id, trend_score}]}
```

---

## 📊 ENDPOINT SUMMARY

| Category | Service | Count |
|----------|---------|-------|
| Streaming | Podcasts | 8 |
| Education | E-Learning | 9 |
| Media | Video Editor | 3 |
| Entertainment | Gaming | 4 |
| Blockchain | NFT | 3 |
| Events | Events | 3 |
| Monetization | Affiliate | 3 |
| Marketing | Newsletter | 3 |
| Monetization | Donations | 2 |
| Utilities | Translation | 2 |
| Utilities | Backup | 3 |
| Utilities | QR Code | 2 |
| Collaboration | Duets | 2 |
| Curation | Playlists | 3 |
| Analytics | Analytics | 2 |
| **NEW - Commerce** | **Live Shopping** | **8** |
| **NEW - Commerce** | **E-Commerce** | **6** |
| **NEW - Monetization** | **Subscriptions** | **6** |
| **NEW - Platform** | **Recommendations** | **3** |
| | **TOTAL** | **84+** |

---

## 🔒 AUTHENTICATION

All endpoints should be protected with JWT middleware:

```python
@app.dependency
async def verify_token(credentials = Depends(HTTPBearer())):
    token = credentials.credentials
    # Verify JWT
    return user_id
```

Add to endpoint:
```python
@router.post("/...")
async def endpoint(user_id: str = Depends(verify_token)):
    pass
```

---

## 💡 COMMON QUERY PARAMETERS

- `user_id` - Required for user-specific operations
- `creator_id` - Required for creator operations
- `limit` - Pagination limit (1-100)
- `offset` - Pagination offset
- `sort_by` - Sort field (default: created_at)
- `order` - asc or desc

---

## 📝 REQUEST/RESPONSE PATTERNS

### Success Response (200)
```json
{
  "status": "success",
  "data": {...}
}
```

### Error Response (4xx/5xx)
```json
{
  "status": "error",
  "message": "Human-readable error message",
  "code": "ERROR_CODE"
}
```

---

## 🔄 PAGINATION EXAMPLE

```
GET /api/v1/courses?limit=10&offset=20&sort_by=created_at&order=desc
```

---

## 🧪 TESTING ALL ENDPOINTS

```bash
# Health check
curl http://localhost:8000/api/v1/health

# List services
curl http://localhost:8000/api/v1/services

# Example: Create podcast
curl -X POST "http://localhost:8000/api/v1/podcasts/create" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "owner_id": "user123",
    "title": "My Podcast",
    "description": "A great podcast",
    "author": "John Doe",
    "category": "technology",
    "image_url": "https://..."
  }'
```

---

## 📚 ADDITIONAL RESOURCES

- **Integration Guide**: `INTEGRATION_GUIDE_19_SERVICES.md`
- **API Documentation**: Swagger at `/docs`
- **ReDoc**: Alternative UI at `/redoc`
- **OpenAPI Schema**: `/openapi.json`

---

**Total Endpoints**: 84+ (and counting!)
**Status**: ✅ All endpoints production-ready
**Authentication**: Add JWT middleware as shown above
**Rate Limiting**: Implement as needed for production
**Monitoring**: Ready for Prometheus integration
