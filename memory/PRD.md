# GAAIUS AI - Product Requirements Document

## Original Problem Statement
Build an enhanced "GAAIUS AI" application - a unified AI assistant platform with:
- AI Chat powered by Groq
- AI Builder (Replit-like IDE for generating web apps from natural language)
- AI Document Studio (professional invoice, quote, receipt, spreadsheet generation)
- Multi-platform support (Web, Desktop EXE, Android APK, iOS)
- Monetization via PayPal subscriptions and ad system for free users

## User Personas
1. **Developers/Creators** - Use AI Builder to generate web applications
2. **Business Users** - Use Document Studio for professional invoices/receipts
3. **General Users** - Use AI Chat for general assistance

## Core Features

### Implemented ✅

#### 1. AI Chat ✅
- General purpose chatbot powered by Groq (Llama 3.3 70B)

#### 2. GAAIUS PROJECT RUNTIME v2.0.0 ✅ (Jan 2025) - **MAJOR UPDATE**
- **Full-Stack Enterprise Scaffold Generator**
- Generates 64+ TypeScript files per project (~2,200+ lines)
- React + Vite + TypeScript frontend
- Express + TypeScript backend
- MongoDB integration
- Full component library (Layout, Sidebar, Header, Card, Button, Modal, Table)
- Auth system with JWT
- API services with Axios
- State management with Zustand

**Enterprise Folder Structure:**
```
/project-root
├── frontend/
│   ├── src/
│   │   ├── pages/         # Dashboard, Settings, Profile, NotFound
│   │   ├── components/    # Layout, Sidebar, Header, Card, Button, Modal, Table
│   │   ├── services/      # api.ts, auth.ts
│   │   ├── hooks/         # useAuth.ts, useApi.ts
│   │   ├── store/         # Zustand stores
│   │   ├── types/         # TypeScript types
│   │   └── utils/         # helpers.ts, constants.ts
│   ├── package.json, vite.config.ts, tsconfig.json
│   └── tailwind.config.js, postcss.config.js
├── backend/
│   ├── src/
│   │   ├── routes/        # auth.ts, api.ts, index.ts
│   │   ├── controllers/   # authController.ts, apiController.ts
│   │   ├── models/        # User.ts
│   │   ├── middleware/    # auth.ts, errorHandler.ts
│   │   ├── config/        # database.ts, env.ts
│   │   └── types/, utils/
│   └── package.json, tsconfig.json
├── shared/
│   └── types.ts, schemas.ts, constants.ts, utils.ts
├── config/
│   └── app.json, build.json, deploy.json
├── docker/
│   ├── Dockerfile.frontend
│   └── Dockerfile.backend
├── run.sh, run.bat, Makefile   # Shell scripts for local dev
├── docker-compose.yml          # Docker containerization
├── .env.example, .gitignore, README.md
└── gaaius.json                 # Blueprint snapshot
```

**New Features in v2.0.0:**
- ✅ **Refresh Button** in preview panel
- ✅ **Staged Building** for 80,000+ line projects (10 stages)
- ✅ **Shell Scripts** - run.sh, run.bat, Makefile for local development
- ✅ **Docker Support** - docker-compose.yml, Dockerfiles
- ✅ **Multi-Agent Orchestration** - 8 specialized AI agents
- ✅ **ChatGPT-Style Chat Formatting** - Avatar icons, proper paragraph spacing (line-height: 1.7)
- ✅ **Preview Auto-Refresh** after generation

#### 3. AI Builder v2.0 - Blueprint-First Platform Assembler ✅
- Monaco code editor with enterprise file tree
- Multi-file project support (HTML, CSS, JS, TSX, TS)
- **6 App Templates** - SaaS Dashboard, E-commerce, AI Chat, Crypto/Finance, Admin Panel, Landing Page
- **Quality Gate v2** - Enhanced validation with detailed checks
- **Full-screen preview mode**
- Image generation via Pollinations AI
- Terminal output with quality checks display
- Export buttons (Web, EXE, APK, iOS)

#### 4. AI Document Studio ✅
- Professional PDF generation (invoices, quotes, receipts)
- XLSX spreadsheet generation
- Editable preview
- Auto-naming from conversation context

#### 5. Authentication ✅
- JWT-based auth
- Gmail-only email validation

#### 6. Monetization ✅
- PayPal Pro subscriptions
- Ad system (after 10 generations or 30 minutes for free users)

#### 7. PWA Support ✅
- manifest.json configured
- Service worker for offline support
- App icons (192px, 512px)
- Mobile Install Banner

---

## Tech Stack
- **Frontend:** React 19, Tailwind CSS, shadcn/ui, Monaco Editor, Zustand
- **Backend:** FastAPI, Python
- **Database:** MongoDB
- **AI Services:** Groq (LLM), Pollinations AI (images)
- **Payments:** PayPal
- **PDF/Docs:** ReportLab, OpenPyXL

## Architecture
```
/app
├── backend/
│   ├── server.py           # FastAPI backend with all API endpoints
│   ├── gaaius_builder.py   # Blueprint-First builder with templates
│   ├── gaaius_runtime.py   # PROJECT RUNTIME v2.0.0 scaffold generator
│   ├── .env                # API keys (GROQ, etc.)
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── App.js                        # Main React app
    │   └── components/
    │       ├── gaaius-ui/index.jsx       # GAAIUS UI Component Library
    │       └── PWAInstallBanner.jsx      # Mobile install banner
    ├── public/
    │   ├── manifest.json                 # PWA manifest
    │   ├── sw.js                         # Service worker
    │   ├── icon-192.png                  # App icon
    │   └── icon-512.png                  # App icon
    └── package.json
```

## API Endpoints

### GAAIUS PROJECT RUNTIME v2.0.0
- `GET /api/build/runtime-status` - Get runtime capabilities, version, min_target_lines
- `POST /api/build/generate-runtime` - Generate full enterprise project scaffold (64+ files)
- `POST /api/build/runtime-modify` - Modify existing project iteratively
- `GET /api/build/stages` - Get 10 build stages for 80,000+ line projects
- `GET /api/build/agents` - Get 8 multi-agent roles and pipelines
- `POST /api/build/staged-generate` - Staged building for large projects

### Legacy Builder
- `POST /api/build/generate` - Generate single HTML file (legacy)
- `GET /api/build/templates` - Get available app templates
- `POST /api/build/blueprint` - Generate structured blueprint from prompt

### Other
- `/api/document/generate_professional` - Generate documents
- `/api/chat` - Chat endpoint
- `/api/auth/signup` - Registration (Gmail only)
- `/api/auth/login` - Login
- `/api/payment/paypal/create` - PayPal payment

---

## Changelog

### January 2025 - v2.0.0 (Latest)
- ✅ **GAAIUS PROJECT RUNTIME v2.0.0** - Major update
  - Added refresh button in preview panel
  - Implemented staged building for 80,000+ line projects
  - Added shell scripts (run.sh, run.bat, Makefile)
  - Added Docker support (docker-compose.yml, Dockerfiles)
  - Implemented multi-agent orchestration system (8 agents)
  - ChatGPT-style chat formatting with avatar icons
  - Preview auto-switches after generation
  - Run commands in generate response

### January 2025 - v1.0.0
- ✅ **GAAIUS PROJECT RUNTIME v1.0.0**
  - Moved from static HTML generation to full-stack project scaffolding
  - Generates 50+ TypeScript files per project
  - React + Vite + TypeScript frontend with components, hooks, services
  - Express + TypeScript backend with routes, controllers, models
  - MongoDB integration with Mongoose
  - Full enterprise folder structure

### Previous Sessions
- ✅ Enhanced AI Builder to v2.0 with Blueprint-First architecture
- ✅ Added 6 app templates
- ✅ Implemented Quality Gate v2 with detailed checks
- ✅ Created GAAIUS UI Component Library with design tokens
- ✅ Added PWA Mobile Install Banner
- ✅ Set up PWA (manifest.json, service worker, app icons)
- ✅ Created multi-platform packaging guide

---

## Roadmap

### P1 - High Priority
- [ ] Implement packaging and export system for Mobile (Capacitor/Expo)
- [ ] Implement packaging and export system for Desktop (Tauri/Electron)
- [ ] Refactor App.js into separate components
- [ ] Language Server Protocol (LSP) for autocomplete

### P2 - Medium Priority
- [ ] AI-driven error self-fixing in Builder
- [ ] Multi-file diffing in Builder
- [ ] Containerization for independent runtime environment

### P3 - Future/Vision (GAAIUS BUILD BRAIN Roadmap)
- [ ] Phase 2 – Emergent-level: AI error self-fixing, multi-file diffing
- [ ] Phase 3 – Replit-level: LSP integration, collaboration/multiplayer
- [ ] Phase 4 – GAAIUS-native: Ecosystem integration (Wallet, Cloud, App Store, DAO)
- [ ] Ultimate Goal: Independent runtime using Docker/Firecracker

---

## Refactoring Needed
1. **frontend/src/App.js (2,800+ lines)** - Split into:
   - `components/Builder.jsx`
   - `components/DocumentStudio.jsx`
   - `components/Chat.jsx`
   - `components/Auth.jsx`

2. **backend/server.py (3,200+ lines)** - Split into:
   - `routers/builder.py`
   - `routers/documents.py`
   - `routers/auth.py`
   - `routers/chat.py`

---

## Multi-Agent System (8 Agents)

| Agent | Role | Outputs |
|-------|------|---------|
| Product Manager | Analyzes requirements, creates specs | product_spec.json, features.json, user_stories.json |
| System Architect | Designs architecture, data models | architecture.md, schema.prisma, api_spec.json |
| UI/UX Designer | Creates UI components, design system | design_system.json, components/, styles/ |
| Frontend Engineer | Implements React components, pages | pages/, components/, services/, hooks/ |
| Backend Engineer | Implements API routes, business logic | routes/, controllers/, middleware/ |
| Database Architect | Designs data models | models/, migrations/, seed.ts |
| DevOps Engineer | Sets up deployment, CI/CD | Dockerfile, docker-compose.yml, .github/ |
| QA Validator | Validates code quality, runs tests | tests/, coverage/, validation_report.json |

## Build Stages (10 Stages for 80,000+ Lines)

1. **Foundation** - Project structure, configs, base files (~500 lines)
2. **Frontend Core** - React app structure, routing (~2,000 lines)
3. **UI Components** - Reusable component library (~3,000 lines)
4. **Application Pages** - All main pages (~8,000 lines)
5. **Frontend Services** - API, auth, state management (~2,000 lines)
6. **Backend Core** - Express server, middleware (~2,000 lines)
7. **Backend Routes** - API routes, controllers (~3,000 lines)
8. **Data Models** - Database models, schemas (~2,000 lines)
9. **Advanced Features** - WebSockets, uploads, cache (~4,000 lines)
10. **DevOps** - Docker, CI/CD, scripts (~1,500 lines)
