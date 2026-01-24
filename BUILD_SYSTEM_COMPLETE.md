# 🚀 Production Build System - GAAIUS AI

## Overview

The Production Build System is a complete multi-platform build orchestration framework that turns generated projects into **actual executable binaries** (EXE, APK, DMG, AppImage, IPA, and more).

**What This Solves:**
- ✅ Generators now create projects
- ✅ Build system compiles them into binaries
- ✅ Artifacts are stored and delivered
- ✅ Automated CI/CD via GitHub Actions
- ✅ Code signing and packaging

---

## Architecture

### Components

```
┌─────────────────────────────────────────────────────────────┐
│                      API Layer                              │
│  /builds/submit, /builds/{job_id}/execute, etc.             │
└────────────┬────────────────────────────────────┬───────────┘
             │                                    │
      ┌──────▼──────────────────┐        ┌───────▼─────────────┐
      │  Build Coordinator      │        │ Artifact Manager    │
      │  (Orchestration)        │        │ (Storage & Delivery)│
      └──────┬──────────────────┘        └────────┬────────────┘
             │                                    │
      ┌──────▼──────────────────┐        ┌───────▼─────────────┐
      │ Build Executor          │        │ Delivery Manager    │
      │ (Compilation)           │        │ (Local/S3/GitHub/  │
      │ - Desktop (Tauri,       │        │  Docker)            │
      │   Electron)             │        └─────────────────────┘
      │ - Mobile (Flutter,      │
      │   React Native)         │
      │ - Web (React, Vue, etc.)│
      │ - Languages (Python,    │
      │   Go, Rust, Java, etc.) │
      └─────────────────────────┘

      ┌──────────────────────────────────────────────────────┐
      │            GitHub Actions Workflows                 │
      │  - build-desktop.yml (Windows/macOS/Linux)           │
      │  - build-mobile.yml (Android/iOS)                    │
      │  - build-web.yml (Web apps)                          │
      └──────────────────────────────────────────────────────┘
```

---

## Build Process Flow

```
User Blueprint
    ↓
API: /builds/submit
    ↓
Build Job Created (Queued)
    ↓
API: /builds/{job_id}/execute
    ↓
┌─────────────────────────────────┐
│ Build Executor                  │
├─────────────────────────────────┤
│ 1. Validate environment         │
│ 2. Install dependencies         │
│ 3. Compile/Build source         │
│ 4. Generate artifacts           │
└─────────────────────────────────┘
    ↓
Build Artifacts Generated
    ├─ .exe (Windows)
    ├─ .dmg (macOS)
    ├─ .AppImage (Linux)
    ├─ .apk (Android)
    ├─ .ipa (iOS)
    └─ dist/ (Web)
    ↓
Artifact Manager Stores
    ├─ Local Disk
    ├─ S3 Cloud
    ├─ GitHub Releases
    └─ Docker Registry
    ↓
Artifacts Available for Download
```

---

## API Endpoints

### Submit Build Request

```http
POST /api/builds/submit
Content-Type: application/json

{
  "project_id": "my-app",
  "project_name": "My App",
  "framework": "tauri",
  "platforms": ["windows", "macos", "linux"],
  "version": "1.0.0",
  "build_type": "release",
  "description": "Production release"
}
```

**Response:**
```json
{
  "status": "submitted",
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Build job created for My App"
}
```

### Execute Build

```http
POST /api/builds/{job_id}/execute
```

**Response:**
```json
{
  "status": "completed",
  "job_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### Get Build Status

```http
GET /api/builds/{job_id}/status
```

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "request_id": "...",
  "project_id": "my-app",
  "project_name": "My App",
  "status": "success",
  "progress": 100,
  "framework": "tauri",
  "version": "1.0.0",
  "platforms": ["windows", "macos", "linux"],
  "started_at": "2026-01-22T10:30:00",
  "completed_at": "2026-01-22T10:45:30",
  "artifacts_count": 3,
  "artifacts": [
    {
      "id": "artifact-001",
      "name": "my-app.exe",
      "platform": "windows",
      "size_mb": 125.5,
      "checksum": "sha256:..."
    }
  ]
}
```

### Get Build Logs

```http
GET /api/builds/{job_id}/logs
```

### Cancel Build

```http
POST /api/builds/{job_id}/cancel
```

### Get Active Builds

```http
GET /api/builds/active
```

### Get Build History

```http
GET /api/builds/history?limit=50
```

### Deliver Artifact

```http
POST /api/builds/{job_id}/deliver

{
  "artifact_id": "artifact-001",
  "method": "local",
  "config": {}
}
```

Delivery Methods:
- `local` - Download from server
- `s3` - Push to AWS S3
- `github-release` - Create GitHub Release
- `docker` - Push to Docker registry

### Download Artifact

```http
GET /api/artifacts/download/{artifact_id}?token=...
```

---

## Supported Platforms & Frameworks

### Desktop

| Framework | Windows | macOS | Linux |
|-----------|---------|-------|-------|
| **Tauri** | ✅ EXE | ✅ DMG | ✅ AppImage |
| **Electron** | ✅ EXE/MSI | ✅ DMG | ✅ AppImage |

### Mobile

| Framework | Android | iOS |
|-----------|---------|-----|
| **Flutter** | ✅ APK/AAB | ✅ IPA/APP |
| **React Native** | ✅ APK/AAB | ✅ IPA/APP |
| **Capacitor** | ✅ APK | ✅ IPA |

### Web

| Framework | Output |
|-----------|--------|
| **React** | ✅ Static dist/ |
| **Angular** | ✅ Static dist/ |
| **Vue** | ✅ Static dist/ |
| **Vite** | ✅ Static dist/ |

### Backend Languages

| Language | Docker | Source |
|----------|--------|--------|
| **Python** | ✅ FastAPI/Flask | ✅ Source |
| **Go** | ✅ Compiled binary | ✅ Source |
| **Rust** | ✅ Compiled binary | ✅ Source |
| **Java** | ✅ Spring Boot JAR | ✅ Source |
| **C#** | ✅ .NET compiled | ✅ Source |
| **PHP** | ✅ Laravel image | ✅ Source |

---

## Build Requirements

### Windows Builds
- Node.js 18+
- Rust (for Tauri)
- Cargo

### macOS Builds
- Node.js 18+
- Xcode 14+
- Rust (for Tauri)
- CocoaPods (for iOS)

### Linux Builds
- Node.js 18+
- libssl-dev
- Build essentials
- Rust (for Tauri)

### Android Builds
- Java Development Kit (JDK) 11+
- Android SDK
- Gradle
- Flutter SDK (for Flutter projects)
- Node.js 18+ (for React Native)

### iOS Builds
- Xcode 14+
- CocoaPods
- Apple Developer account (for signing)
- Flutter SDK or Node.js 18+

---

## GitHub Actions Workflows

### Desktop Build Workflow

**File:** `.github/workflows/build-desktop.yml`

Triggers:
- Manual workflow dispatch with inputs:
  - `project_name`: Name of the project
  - `framework`: "tauri" or "electron"
  - `version`: Version to build
  - `include_windows`: Build Windows EXE
  - `include_macos`: Build macOS DMG
  - `include_linux`: Build Linux AppImage

Builds:
- Windows EXE (runs-on: windows-latest)
- macOS DMG (runs-on: macos-latest)
- Linux AppImage (runs-on: ubuntu-latest)

Outputs:
- Creates GitHub Release with all binaries

### Mobile Build Workflow

**File:** `.github/workflows/build-mobile.yml`

Triggers:
- Manual workflow dispatch with inputs:
  - `project_name`: Name of the project
  - `framework`: "flutter" or "react-native"
  - `version`: Version to build
  - `build_apk`: Build Android APK
  - `build_ios`: Build iOS App

Builds:
- Android APK (runs-on: ubuntu-latest)
- iOS App (runs-on: macos-latest)
- Android App Bundle for Play Store

Outputs:
- Creates GitHub Release with APK/IPA files

### Web Build Workflow

**File:** `.github/workflows/build-web.yml`

Triggers:
- Manual workflow dispatch with inputs:
  - `project_name`: Name of the project
  - `framework`: "react", "angular", "vue", "vite"
  - `version`: Version to build
  - `deploy_docker`: Build Docker image

Builds:
- Web distribution (tar.gz and zip)
- Optional Docker image

Outputs:
- Creates GitHub Release with web distribution

---

## Usage Examples

### Example 1: Build Desktop App (Tauri)

```bash
# 1. Submit build request
curl -X POST http://localhost:8000/api/builds/submit \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "project_id": "my-desktop-app",
    "project_name": "My Desktop App",
    "framework": "tauri",
    "platforms": ["windows", "macos", "linux"],
    "version": "1.0.0",
    "build_type": "release"
  }'

# Response: {"status": "submitted", "job_id": "..."}

# 2. Execute the build
curl -X POST http://localhost:8000/api/builds/<job_id>/execute \
  -H "Authorization: Bearer <token>"

# 3. Monitor progress
curl http://localhost:8000/api/builds/<job_id>/status \
  -H "Authorization: Bearer <token>"

# 4. Download artifact
curl http://localhost:8000/api/artifacts/download/<artifact_id> \
  -o my-app.exe
```

### Example 2: Build Mobile App (Flutter)

```bash
# Submit mobile build
curl -X POST http://localhost:8000/api/builds/submit \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "project_id": "my-mobile-app",
    "project_name": "My Mobile App",
    "framework": "flutter",
    "platforms": ["android", "ios"],
    "version": "1.0.0",
    "build_type": "release"
  }'
```

### Example 3: Deploy to S3

```bash
# Deliver artifact to S3
curl -X POST http://localhost:8000/api/builds/<job_id>/deliver \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "artifact_id": "...",
    "method": "s3",
    "config": {
      "bucket": "my-artifacts",
      "region": "us-east-1"
    }
  }'
```

---

## Environment Variables

```bash
# Required
GROQ_API_KEY=<your-groq-api-key>
MONGO_URL=mongodb://localhost:27017
DB_NAME=gaaius

# Optional (for S3 delivery)
AWS_ACCESS_KEY_ID=<your-aws-key>
AWS_SECRET_ACCESS_KEY=<your-aws-secret>

# Optional (for GitHub Release delivery)
GITHUB_TOKEN=<your-github-token>

# Optional (for Docker Registry delivery)
DOCKER_REGISTRY=docker.io
DOCKER_USERNAME=<your-username>
DOCKER_TOKEN=<your-token>
```

---

## Monitoring & Troubleshooting

### View Build Logs

```bash
curl http://localhost:8000/api/builds/<job_id>/logs \
  -H "Authorization: Bearer <token>" | jq '.logs' | less
```

### Common Issues

**Issue:** Build fails with "tool not found"
- **Solution:** Ensure required toolchain is installed on build machine
- Windows: Install Rust, Cargo, Node.js
- macOS: Install Xcode, Rust, Node.js
- Linux: Install build-essential, Rust, Node.js

**Issue:** Android build fails
- **Solution:** Set ANDROID_HOME environment variable
  ```bash
  export ANDROID_HOME=$HOME/Library/Android/sdk
  export PATH=$PATH:$ANDROID_HOME/tools:$ANDROID_HOME/platform-tools
  ```

**Issue:** iOS build fails
- **Solution:** Ensure Xcode is properly configured
  ```bash
  sudo xcode-select --install
  sudo xcode-select --reset
  ```

**Issue:** Storage quota exceeded
- **Solution:** Clean up old artifacts (automatic via retention_days)
  ```bash
  # Default: 30 days, adjust in artifact_manager.py
  self.retention_days = 30
  ```

---

## Security Considerations

### Code Signing

For production releases:

**Windows:**
- Obtain code signing certificate (.pfx)
- Set signing_identity in build config
- Signtool will automatically sign executables

**macOS:**
- Apple Developer account required
- Certificates installed in Keychain
- Automatic code signing via Xcode

**iOS:**
- Apple Developer account required
- Provisioning profiles configured
- Team ID in Xcode project

### Artifact Integrity

All artifacts include:
- **Checksum:** SHA256 hash for integrity verification
- **Metadata:** File size, creation date, platform info
- **Signed:** Code signature status
- **Token:** Download token for access control

### Access Control

All build endpoints require:
- Bearer token authentication
- User ID validation
- Rate limiting (30 req/min default)

---

## Performance Metrics

Typical build times:

| Platform | Framework | Time |
|----------|-----------|------|
| Windows | Tauri | 8-12 min |
| macOS | Tauri | 10-15 min |
| Linux | Tauri | 6-10 min |
| Android | Flutter | 5-8 min |
| iOS | Flutter | 12-18 min |
| Web | React | 2-3 min |

**Parallel Builds:** Up to 3 concurrent builds (configurable)

---

## Advanced Features

### Artifact Storage Options

1. **Local Disk** (Default)
   - Fast, no external dependencies
   - Max size: 100GB (configurable)
   - Auto-cleanup: 30 days (configurable)

2. **AWS S3**
   - Scalable cloud storage
   - Public URL generation
   - Automatic versioning

3. **GitHub Releases**
   - Built-in to GitHub
   - Public downloads
   - Release notes support

4. **Docker Registry**
   - Push Docker images
   - Private/public registries
   - Automatic tagging

### Delivery Pipeline

```
Generated Project
    ↓
Build Executor compiles
    ↓
Artifacts created
    ↓
Artifact Manager stores
    ├─ Calculate checksums
    ├─ Store metadata
    └─ Auto-cleanup old artifacts
    ↓
Delivery Manager delivers
    ├─ Local disk download
    ├─ Push to S3
    ├─ Create GitHub Release
    └─ Push to Docker Registry
    ↓
User downloads artifact
    ├─ Verify checksum
    └─ Install/Deploy
```

---

## API Reference

See `build_coordinator.py` for complete implementation details.

Key Classes:
- `BuildCoordinator`: Main orchestrator
- `BuildExecutor`: Compilation engine
- `ArtifactStorageManager`: Storage management
- `ArtifactDeliveryManager`: Distribution
- `BuildEnvironmentValidator`: Toolchain checking

---

## What's Different Now

### Before
- Generators created templates
- Users had to manually compile
- No artifact management
- Manual deployment

### After ✅
- Generators create projects
- **Build system compiles to binaries**
- **Artifacts automatically stored**
- **Multiple delivery options**
- **GitHub Actions CI/CD included**
- **Code signing support**

---

## Next Steps

1. **Configure environment variables**
   - Set AWS credentials (for S3 delivery)
   - Set GitHub token (for GitHub Releases)

2. **Test local builds**
   ```bash
   python -m pytest tests/test_build_system.py
   ```

3. **Use via API**
   - Submit build requests
   - Monitor progress
   - Download artifacts

4. **Setup CI/CD**
   - Push generated projects to GitHub
   - GitHub Actions triggers builds
   - Artifacts automatically published

---

## Support

For issues or questions:
- Check logs: `/api/builds/{job_id}/logs`
- Review build status: `/api/builds/{job_id}/status`
- Check active builds: `/api/builds/active`
- View history: `/api/builds/history`
