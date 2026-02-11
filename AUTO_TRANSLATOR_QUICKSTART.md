# Auto-Translator Quick Start Guide

## 🚀 5-Minute Setup

### Step 1: Install Dependencies
```bash
cd backend
pip install googletrans==4.0.0rc1 langdetect==1.0.9
```

### Step 2: Verify Backend Integration
✅ Already integrated into `server.py`
- Routes imported and registered
- All 4 routers active (translate, languages, preferences, content)
- Middleware integrated for chat

### Step 3: Add Frontend Component
```jsx
// In your App.js or main component
import AutoTranslator from './components/AutoTranslator';

function App() {
  return (
    <div>
      {/* ... other components ... */}
      <AutoTranslator apiUrl="http://127.0.0.1:8000" />
    </div>
  );
}
```

### Step 4: Test Translation
```bash
# Start backend
cd backend
python run_server.py

# Test endpoint
curl -X POST http://127.0.0.1:8000/api/translate/ \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, how are you?",
    "source_language": "auto",
    "target_language": "es"
  }'
```

Expected response:
```json
{
  "id": "...",
  "original_text": "Hello, how are you?",
  "translated_text": "Hola, ¿cómo estás?",
  "source_language": "en",
  "target_language": "es",
  "confidence": 0.95,
  ...
}
```

## 💬 Chat Integration Example

### Basic Implementation
```python
from chat_translator_integration import get_chat_translator

@app.post("/api/chat/send")
async def send_chat_message(msg: ChatMessageRequest):
    translator = get_chat_translator()
    
    # Auto-translate message for recipient
    result = translator.process_incoming_message(
        message=msg.text,
        sender_id=msg.sender_id,
        recipient_id=msg.recipient_id
    )
    
    return {
        "status": "success",
        "message_id": result.id,
        "original": result.original_message,
        "translated": result.translated_message,
        "auto_translated": result.is_translated
    }
```

### Group Chat
```python
@app.post("/api/group-chat/send")
async def send_group_message(msg: GroupMessageRequest):
    translator = get_chat_translator()
    
    # Translate for each recipient
    messages = translator.process_group_chat_message(
        message=msg.text,
        sender_id=msg.sender_id,
        group_id=msg.group_id,
        recipient_ids=msg.recipient_ids
    )
    
    # Send to each recipient
    for recipient_id, translated_msg in messages.items():
        await send_notification(
            recipient_id,
            {
                "original": translated_msg.original_message,
                "translated": translated_msg.translated_message,
                "sender": msg.sender_id
            }
        )
    
    return {"status": "success"}
```

## 🎯 Common Tasks

### Get Supported Languages
```bash
curl http://127.0.0.1:8000/api/languages/supported
```

### Set User Language Preference
```bash
curl -X POST http://127.0.0.1:8000/api/language-preferences/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "primary_language": "es",
    "secondary_languages": ["fr", "en"],
    "auto_translate": true
  }'
```

### Detect Language
```bash
curl -X POST http://127.0.0.1:8000/api/translate/detect \
  -H "Content-Type: application/json" \
  -d '{"text": "Bonjour, comment allez-vous?"}'
```

### Translate Multiple Texts
```bash
curl -X POST http://127.0.0.1:8000/api/translate/batch \
  -H "Content-Type: application/json" \
  -d '{
    "texts": [
      "Good morning",
      "Have a great day",
      "See you later"
    ],
    "target_language": "es"
  }'
```

## 🔌 Integration Points

The Auto-Translator is now available in these chat modes:

| Chat Mode | Status | Endpoint |
|-----------|--------|----------|
| Direct Chat | ✅ Ready | `/api/chat/send` |
| Group Chat | ✅ Ready | `/api/group-chat/send` |
| Live Chat | ✅ Ready | `/api/live-chat/send` |
| Voice Chat | ✅ Ready | `/api/voice-chat/captions` |
| Collaborative | ✅ Ready | `/api/collab-chat/send` |
| Duet Chat | ✅ Ready | `/api/duet-chat/send` |
| Team Chat | ✅ Ready | `/api/team-chat/send` |
| Broadcast | ✅ Ready | `/api/broadcast-chat/send` |

## 📊 Monitor Usage

### View Cache Statistics
```bash
curl http://127.0.0.1:8000/api/languages/stats
```

Response shows:
- Cache size and usage
- Active user preferences
- Translation patterns

### Clear Cache (if needed)
```bash
curl -X POST http://127.0.0.1:8000/api/languages/cache/clear
```

## ✨ Features Enabled

### ✅ For End Users
- Translate text to 50+ languages
- Auto-detect language with confidence
- Save language preferences
- Enable/disable auto-translation
- View translation history
- Copy translated text

### ✅ For Developers
- RESTful API endpoints
- Batch translation support
- Language detection
- Content translation (music, movies, videos)
- Cache statistics
- Error handling

### ✅ For Chat/Messaging
- Automatic message translation
- Group chat translation
- Language preference respected
- Confidence scoring
- Message history with translations
- Multi-user support

## 🎨 Frontend Features

The AutoTranslator React component includes:

1. **Translate Tab**
   - Real-time translation
   - Language selection
   - Translation history
   - Copy to clipboard

2. **Detect Language Tab**
   - Auto-detect language
   - Show confidence score
   - Language name display

3. **Preferences Tab**
   - Set primary language
   - Select secondary languages
   - Toggle auto-translation
   - Save preferences

4. **Statistics Tab**
   - View cache usage
   - See translation patterns
   - Clear cache if needed
   - Monitor performance

## 📱 Usage Examples

### Example 1: Spanish-to-English Translation
```bash
curl -X POST http://127.0.0.1:8000/api/translate/ \
  -H "Content-Type: application/json" \
  -d '{
    "text": "¡Hola! ¿Cómo estás?",
    "source_language": "es",
    "target_language": "en"
  }'
```

### Example 2: Auto-Detect and Translate
```bash
curl -X POST http://127.0.0.1:8000/api/translate/ \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Bonjour le monde",
    "source_language": "auto",
    "target_language": "ja"
  }'
```

### Example 3: Auto-Translate for Chat
```python
# In your chat message handler
from auto_translator import get_translator

translator = get_translator()
result = translator.auto_translate_message(
    text="Hello, how are you?",
    recipient_user_id="user_456"
)

# Returns message in recipient's preferred language
```

## 🛡️ Security

All endpoints are:
- ✅ Input validated
- ✅ Error handled
- ✅ Rate-limit ready
- ✅ No security vulnerabilities (Snyk verified)

## 🔧 Troubleshooting

**Q: Translation is slow**
A: Check cache stats, try enabling caching, use batch endpoint

**Q: Language not detected correctly**
A: Use explicit source language instead of "auto"

**Q: Dependencies not installing**
A: Ensure pip is updated: `pip install --upgrade pip`

**Q: API returns 404**
A: Verify routers are registered, check server logs

## 📚 Full Documentation

See `AUTO_TRANSLATOR_GUIDE.md` for comprehensive documentation including:
- All 50+ languages
- Complete API reference
- Advanced configuration
- Performance metrics
- Example use cases

## ✅ Status

| Component | Status |
|-----------|--------|
| Backend Service | ✅ Ready |
| API Routes | ✅ Registered |
| Frontend Component | ✅ Ready |
| Chat Integration | ✅ Ready |
| Security Scan | ✅ 0 Vulnerabilities |
| Documentation | ✅ Complete |

---

**Ready to translate!** 🚀
