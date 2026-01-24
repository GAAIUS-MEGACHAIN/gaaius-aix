# GAAIUS AI - Architecture & System Design

## 🏛️ System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          GAAIUS AI PLATFORM v2.0.0                          │
│                     Unified Intelligence. One Interface.                     │
└─────────────────────────────────────────────────────────────────────────────┘

                           ┌─────────────────────┐
                           │   USER INTERFACE    │
                           │   (React Frontend)  │
                           └──────────┬──────────┘
                                      │
        ┌─────────────────────────────┼──────────────────────────────┐
        │                              │                               │
        ▼                              ▼                               ▼
┌─────────────────┐         ┌──────────────────┐         ┌──────────────────┐
│  Chat Mode      │         │  Builder Mode    │         │  Document Mode   │
│  (Groq LLM)     │         │  (Code Gen)      │         │  (PDF/Excel)     │
└─────────────────┘         └──────────────────┘         └──────────────────┘
        │                              │                               │
        ▼                              ▼                               ▼
┌─────────────────┐         ┌──────────────────┐         ┌──────────────────┐
│  Image Mode     │         │  Video Mode      │         │  Audio Mode      │
│  (HF FLUX.1)    │         │  (AI Keyframes)  │         │  (TTS/STT/Music) │
└─────────────────┘         └──────────────────┘         └──────────────────┘

                           ┌─────────────────────┐
                           │  FASTAPI BACKEND    │
                           │   (3,300+ lines)    │
                           └──────────┬──────────┘

        ┌──────────────────────────────┼───────────────────────────────┐
        │                              │                               │
        ▼                              ▼                               ▼
┌──────────────────────┐    ┌──────────────────────┐    ┌─────────────────┐
│  GAAIUS BUILD BRAIN  │    │  GAAIUS PROJECT     │    │  AI SERVICES    │
│  v2.0 (Builder)      │    │  RUNTIME v2.0       │    │  Integration    │
├──────────────────────┤    ├──────────────────────┤    ├─────────────────┤
│ • Templates (6)      │    │ • Full-Stack Gen.   │    │ • Groq Llama    │
│ • Blueprint Gen.     │    │ • 64+ Files/project │    │ • HF FLUX.1     │
│ • Quality Gate v2    │    │ • React + Express   │    │ • HF Whisper    │
│ • Component Lib.     │    │ • MongoDB           │    │ • HF MusicGen   │
│ • Code Generation    │    │ • Docker Support    │    │ • ReportLab     │
│ • Validation Engine  │    │ • 10-Stage Build    │    │ • OpenPyXL      │
│ • Layout Engine      │    │ • 8 AI Agents       │    │                 │
└──────────────────────┘    └──────────────────────┘    └─────────────────┘

                           ┌─────────────────────┐
                           │   MONGODB ATLAS     │
                           │   (Database)        │
                           └─────────────────────┘
```

---

## 🔄 Data Flow Diagram

### Chat Mode Flow
```
User Input
    │
    ▼
┌─────────────┐
│ React App   │  ──HTTP POST──> /api/chat
└─────────────┘                    │
                                   ▼
                            ┌────────────────┐
                            │ FastAPI Endpoint
                            │ /api/chat      │
                            └────────┬───────┘
                                     │
                    ┌────────────────┼────────────────┐
                    │                │                │
                    ▼                ▼                ▼
            ┌──────────────┐  ┌────────────┐  ┌────────────┐
            │ Save session │  │ Call Groq  │  │ Store msg  │
            │ to MongoDB   │  │ Llama 3.3  │  │ in MongoDB │
            └──────────────┘  └────────────┘  └────────────┘
                    │                │                │
                    └────────────────┼────────────────┘
                                     │
                                     ▼
                         ┌──────────────────────┐
                         │ Stream Response to   │
                         │ React Frontend       │
                         └──────────────────────┘
                                     │
                                     ▼
                         Display in Chat Interface
```

### Builder Mode Flow
```
User Prompt: "Create crypto dashboard"
    │
    ▼
┌──────────────────┐
│ /api/build/      │
│ generate         │
└────────┬─────────┘
         │
         ▼
    ┌──────────────────────────────┐
    │ GAAIUS BUILD BRAIN v2.0      │
    │ ├─ Template Matching         │
    │ ├─ Blueprint Generation      │
    │ ├─ Component Selection       │
    │ └─ Layout Planning           │
    └────────┬─────────────────────┘
             │
             ▼
    ┌──────────────────────────────┐
    │ Groq Llama 3.3 Code Gen      │
    │ Generates HTML/CSS/JS/TSX    │
    └────────┬─────────────────────┘
             │
             ▼
    ┌──────────────────────────────┐
    │ Quality Gate v2              │
    │ ├─ Length validation         │
    │ ├─ Syntax checking           │
    │ ├─ Semantic quality score    │
    │ └─ Component validation      │
    └────────┬─────────────────────┘
             │
    ┌────────┴────────┐
    │                 │
   YES               NO
    │                 │
    ▼                 ▼
┌──────────┐    ┌──────────┐
│ Return   │    │ Retry    │
│ Code     │    │ & Refine │
└──────────┘    └──────────┘
```

### Project Runtime Flow
```
User Request: "Generate full e-commerce app"
    │
    ▼
┌──────────────────────────────┐
│ /api/build/generate-runtime  │
└────────┬─────────────────────┘
         │
         ▼
┌──────────────────────────────┐
│ GAAIUS PROJECT RUNTIME v2.0  │
├──────────────────────────────┤
│ 8 AI Agents Orchestration    │
│ ├─ Product Manager           │
│ ├─ System Architect          │
│ ├─ UI/UX Designer            │
│ ├─ Frontend Engineer         │
│ ├─ Backend Engineer          │
│ ├─ Database Architect        │
│ ├─ DevOps Engineer           │
│ └─ QA Validator              │
└────────┬─────────────────────┘
         │
         ▼
┌──────────────────────────────┐
│ 10-Stage Build Process       │
├──────────────────────────────┤
│ Stage 1: Foundation (~500)   │
│ Stage 2: Frontend Core (~2K) │
│ Stage 3: UI Components (~3K) │
│ Stage 4: Pages (~8K)         │
│ Stage 5: Services (~2K)      │
│ Stage 6: Backend Core (~2K)  │
│ Stage 7: Routes (~3K)        │
│ Stage 8: Models (~2K)        │
│ Stage 9: Advanced (~4K)      │
│ Stage 10: DevOps (~1.5K)     │
└────────┬─────────────────────┘
         │
         ▼
┌──────────────────────────────┐
│ Generate 64+ Files           │
├──────────────────────────────┤
│ Frontend:  25+ TS/TSX files  │
│ Backend:   20+ TS files      │
│ Config:    10+ JSON files    │
│ Docker:     5+ compose files │
│ Scripts:    3+ shell scripts │
└────────┬─────────────────────┘
         │
         ▼
Package & Download as ZIP
```

---

## 📊 Component Architecture

### Frontend Component Hierarchy

```
App.js (Root)
├── Authentication
│   ├── LoginModal
│   ├── RegisterModal
│   └── UserProfile
│
├── Navigation
│   ├── Sidebar
│   │   ├── ModeSelector
│   │   └── ChatHistory
│   └── Header
│       └── UserMenu
│
├── Chat Mode
│   ├── ChatInterface
│   │   ├── MessageList
│   │   ├── ChatInput
│   │   └── SessionManager
│   └── ChatSidebar
│       └── HistoryPanel
│
├── Builder Mode
│   ├── BuilderInterface
│   │   ├── PromptInput
│   │   ├── PreviewPanel
│   │   ├── CodeEditor (Monaco)
│   │   ├── ComponentLibrary
│   │   └── DownloadButton
│   └── BuilderSidebar
│       ├── TemplateSelector
│       └── HistoryPanel
│
├── Image Mode
│   ├── ImageGenerator
│   │   ├── PromptInput
│   │   ├── StyleSelector
│   │   ├── ImageGallery
│   │   └── DownloadButton
│   └── ImageHistory
│
├── Video Mode
│   ├── VideoGenerator
│   │   ├── PromptInput
│   │   ├── DurationSelector
│   │   ├── StyleSelector
│   │   ├── VideoPreview
│   │   └── DownloadButton
│   └── VideoHistory
│
├── Audio Mode
│   ├── AudioGenerator
│   │   ├── PromptInput
│   │   ├── LanguageSelector
│   │   ├── AudioPlayer
│   │   └── DownloadButton
│   └── AudioHistory
│
├── Document Mode
│   ├── DocumentGenerator
│   │   ├── TypeSelector
│   │   ├── FormInput
│   │   ├── PreviewPanel
│   │   └── ExportButton
│   └── DocumentHistory
│
└── Projects Page
    ├── ProjectList
    ├── ProjectCard
    ├── CreateProjectModal
    └── ProjectDetails
```

### Backend Route Structure

```
FastAPI App (server.py)
│
├── /api/auth
│   ├── POST /register
│   ├── POST /login
│   └── GET /me
│
├── /api/chat
│   ├── POST /chat
│   ├── GET /sessions
│   ├── GET /sessions/{id}
│   └── POST /sessions/{id}/messages
│
├── /api/image
│   ├── POST /generate
│   └── GET /styles
│
├── /api/video
│   ├── POST /generate
│   ├── POST /generate-story
│   └── GET /styles
│
├── /api/audio
│   ├── POST /generate
│   ├── POST /tts
│   └── POST /stt
│
├── /api/document
│   ├── POST /generate
│   └── GET /styles
│
├── /api/build
│   ├── GET /platform-status        (Build Brain v2.0)
│   ├── POST /generate              (Build Brain v2.0)
│   ├── GET /templates              (Build Brain v2.0)
│   ├── POST /blueprint             (Build Brain v2.0)
│   ├── GET /advanced               (Build Brain v2.0)
│   ├── GET /runtime-status         (Project Runtime v2.0)
│   ├── POST /generate-runtime      (Project Runtime v2.0)
│   ├── GET /stages                 (Project Runtime v2.0)
│   ├── GET /agents                 (Project Runtime v2.0)
│   └── POST /staged-generate       (Project Runtime v2.0)
│
├── /api/projects
│   ├── POST /
│   ├── GET /
│   ├── GET /{id}
│   ├── PUT /{id}
│   ├── DELETE /{id}
│   └── POST /{id}/share
│
├── /api/payment
│   ├── GET /config
│   ├── POST /paypal/create
│   ├── POST /paypal/capture/{order_id}
│   ├── POST /payfast/create
│   └── POST /payfast/notify
│
└── /api/health
    └── GET /
```

---

## 🔐 Security Architecture

```
                    ┌─────────────┐
                    │ User Device │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────────┐
                    │ HTTPS/WSS       │
                    │ Encrypted       │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │ API Gateway     │
                    │ CORS Middleware │
                    └────────┬────────┘
                             │
                    ┌────────▼──────────────┐
                    │ Authentication       │
                    │ ├─ JWT Validation    │
                    │ ├─ Token Verification│
                    │ └─ User Context      │
                    └────────┬──────────────┘
                             │
                    ┌────────▼──────────────┐
                    │ Route Handlers       │
                    │ ├─ Request Validation│
                    │ ├─ Business Logic    │
                    │ └─ Error Handling    │
                    └────────┬──────────────┘
                             │
                    ┌────────▼──────────────┐
                    │ Database (MongoDB)   │
                    │ ├─ Connection Auth   │
                    │ ├─ Data Encryption   │
                    │ └─ Access Control    │
                    └──────────────────────┘
```

---

## 🚀 Deployment Architecture

### Single Server Deployment

```
┌──────────────────────────────────────────┐
│          Cloud Server (AWS/GCP/Azure)    │
├──────────────────────────────────────────┤
│                                          │
│  ┌──────────────────────────────────┐  │
│  │     Docker Container             │  │
│  ├──────────────────────────────────┤  │
│  │  ┌──────────────┐  ┌──────────┐ │  │
│  │  │   Frontend   │  │ Backend  │ │  │
│  │  │   (React)    │  │(FastAPI) │ │  │
│  │  └──────────────┘  └──────────┘ │  │
│  │          │              │        │  │
│  │          └──────┬───────┘        │  │
│  │                 │                │  │
│  └─────────────────┼────────────────┘  │
│                    │                    │
└────────────────────┼────────────────────┘
                     │
           ┌─────────▼──────────┐
           │   MongoDB Atlas    │
           │   (Cloud DB)       │
           └────────────────────┘
```

### Multi-Service Deployment

```
┌─────────────────────────────────────────────────────────┐
│              Load Balancer (Nginx/Cloudflare)          │
└──────────────┬──────────────────────────┬───────────────┘
               │                          │
        ┌──────▼────────┐          ┌──────▼────────┐
        │  Frontend     │          │  Backend      │
        │  Replica 1    │          │  Replica 1    │
        └───────────────┘          └───────────────┘
               │                          │
        ┌──────▼────────┐          ┌──────▼────────┐
        │  Frontend     │          │  Backend      │
        │  Replica 2    │          │  Replica 2    │
        └───────────────┘          └───────────────┘
               │                          │
               └──────────┬───────────────┘
                          │
                    ┌─────▼──────┐
                    │  MongoDB    │
                    │   Cluster   │
                    └─────────────┘
```

---

## 📦 File Generation Output

### Project Structure Generated by Runtime

```
my-app/
├── frontend/
│   ├── src/
│   │   ├── pages/                  (4 files)
│   │   ├── components/             (8 files)
│   │   ├── services/               (2 files)
│   │   ├── hooks/                  (2 files)
│   │   ├── store/                  (2 files)
│   │   ├── types/                  (1 file)
│   │   ├── styles/                 (1 file)
│   │   ├── utils/                  (1 file)
│   │   └── App.tsx, main.tsx       (2 files)
│   ├── public/
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   └── postcss.config.js
│
├── backend/
│   ├── src/
│   │   ├── routes/                 (3 files)
│   │   ├── controllers/            (2 files)
│   │   ├── models/                 (1 file)
│   │   ├── middleware/             (2 files)
│   │   ├── config/                 (2 files)
│   │   ├── utils/                  (1 file)
│   │   ├── types/                  (1 file)
│   │   └── server.ts
│   ├── package.json
│   └── tsconfig.json
│
├── shared/
│   ├── types.ts
│   ├── schemas.ts
│   ├── constants.ts
│   └── utils.ts
│
├── config/
│   ├── app.json
│   ├── build.json
│   └── deploy.json
│
├── docker/
│   ├── Dockerfile.frontend
│   └── Dockerfile.backend
│
├── docker-compose.yml
├── .env.example
├── .gitignore
├── README.md
├── run.sh
├── run.bat
├── Makefile
└── gaaius.json              (Blueprint snapshot)
```

**Total:** 64+ files, ~2,200+ lines of code

---

## 🔄 Request/Response Flow

### Typical Build Request

```
REQUEST:
┌────────────────────────────┐
│ POST /api/build/generate   │
├────────────────────────────┤
│ {                          │
│   "prompt": "...",         │
│   "template": "...",       │
│   "options": {...}         │
│ }                          │
└────────────────────────────┘
           │
           ▼
    Process Request
           │
           ▼
RESPONSE:
┌────────────────────────────┐
│ 200 OK                     │
├────────────────────────────┤
│ {                          │
│   "code": "...",           │
│   "quality_score": 75,     │
│   "quality_passed": true,  │
│   "character_count": 7502, │
│   "lines_of_code": 142,    │
│   "components_used": 12,   │
│   "timestamp": "...",      │
│   "generation_time": 2.5   │
│ }                          │
└────────────────────────────┘
```

---

## 📈 Scaling Considerations

### Current Capacity (Single Server)
- ~1,000+ concurrent users
- ~100 code generations per minute
- ~50 chat messages per second
- MongoDB storage: 100GB+

### Horizontal Scaling
- Add more FastAPI replicas behind load balancer
- Add more frontend servers for static content
- Scale MongoDB with Atlas sharding
- Use CDN for static assets and images
- Cache API responses with Redis

### Performance Optimizations
- Code generation caching
- Result memoization
- Database indexing
- API rate limiting per user
- Queue system for large jobs

---

## 🔗 External Integrations

```
┌──────────────────────────┐
│   GAAIUS Platform        │
└───────────┬──────────────┘
            │
    ┌───────┼───────┬──────────┬──────────┐
    │       │       │          │          │
    ▼       ▼       ▼          ▼          ▼
┌────────┐ ┌────┐ ┌────────┐ ┌──────┐ ┌──────────┐
│ Groq   │ │ HF │ │PayPal  │ │PayFast│ │MongoDB   │
│ LLM    │ │    │ │        │ │      │ │Atlas     │
└────────┘ └────┘ └────────┘ └──────┘ └──────────┘
  Chat &    Image   Payments  Payments  Database
  Code Gen  Video   Stripe    ZAR       Storage
           Audio   Capture   Webhook
           TTS/STT
```

---

## 🎯 Performance Targets

| Metric | Target | Current |
|--------|--------|---------|
| API Response Time | <1s | ~0.5-2s |
| Code Generation | <10s | ~2-5s |
| Page Load | <2s | ~1-3s |
| Database Query | <100ms | ~50-150ms |
| Uptime | 99.5% | 99%+ |
| Code Quality Score | >70 | ~75 avg |
| Test Pass Rate | 100% | 100% ✓ |

---

**This architecture is designed to be scalable, maintainable, and production-ready for serving thousands of users generating millions of applications.**
