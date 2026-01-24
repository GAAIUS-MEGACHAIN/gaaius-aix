# GAAIUS Project Runtime - Server Integration Guide

**Date:** January 22, 2026

## Overview

This guide shows how to integrate the Project Runtime systems (4 new modules) into your existing FastAPI server.

## Files to Add

Four new files have been created:

1. **scaffold_generator.py** (45 KB) - Generates project scaffolds
2. **frontend_runtime_generator.py** (31 KB) - Generates React components
3. **backend_runtime_generator.py** (33 KB) - Generates Express/FastAPI APIs
4. **project_runtime.py** (15 KB) - Master orchestrator
5. **project_runtime_integration.py** (NEW) - Integration with FastAPI + MongoDB
6. **project_runtime_routes.py** (NEW) - FastAPI router endpoints

All files are in: `backend/`

## Integration Steps

### Step 1: Add Router to server.py

Find this line in `backend/server.py`:
```python
api_router = APIRouter(prefix="/api")
```

Around line 729, add the import near the top of the file with other imports:

```python
# Add this import with the other local imports (around line 50-150)
from project_runtime_routes import router as runtime_router
```

Then find where routers are included (usually near the end, around line 3500+):

```python
# Include the runtime router
app.include_router(runtime_router)
```

### Step 2: Update requirements.txt

Make sure these packages are in your requirements.txt:
```
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
motor>=3.3.0
pydantic>=2.0.0
```

These should already be there, but verify.

### Step 3: Verify Directory Structure

The system expects this structure:
```
gaaius-ai/
├── backend/
│   ├── server.py
│   ├── gaaius_builder.py
│   ├── scaffold_generator.py (NEW)
│   ├── frontend_runtime_generator.py (NEW)
│   ├── backend_runtime_generator.py (NEW)
│   ├── project_runtime.py (NEW)
│   ├── project_runtime_integration.py (NEW)
│   ├── project_runtime_routes.py (NEW)
│   └── ...other files
├── generated_projects/ (automatically created)
└── ...
```

## API Endpoints

Once integrated, you'll have these new endpoints:

### Project Generation
```bash
POST /api/runtime/projects/generate
Content-Type: application/json

{
  "project_name": "My SaaS App",
  "blueprint": {
    "app_type": "saas_dashboard",
    "pages": ["Dashboard", "Analytics", "Settings"],
    "features": ["auth", "search", "notifications"],
    "layout": {"type": "sidebar"}
  },
  "project_type": "fullstack",
  "frontend_framework": "react",
  "backend_framework": "express",
  "database": "postgresql",
  "use_typescript": true
}
```

Response:
```json
{
  "status": "success",
  "project_id": "550e8400-e29b-41d4-a716-446655440000",
  "project_name": "My SaaS App",
  "project_path": "/path/to/generated_projects/550e8400...",
  "blueprint_path": "/path/to/generated_projects/550e8400.../gaaius.json",
  "manifest_path": "/path/to/generated_projects/550e8400.../gaaius_manifest.json",
  "steps": [
    "Created project scaffold",
    "Generated frontend components",
    "Generated backend routes",
    "Installed dependencies"
  ],
  "message": "Project 'My SaaS App' generated successfully in 15234ms"
}
```

### List Projects
```bash
GET /api/runtime/projects?status=ready&limit=10
```

### Get Project Details
```bash
GET /api/runtime/projects/{project_id}
```

### Start Dev Servers
```bash
POST /api/runtime/projects/{project_id}/start-servers
```

### Get Project Structure
```bash
GET /api/runtime/projects/{project_id}/structure
```

### Get Preview URL
```bash
GET /api/runtime/projects/{project_id}/preview
```

### Delete Project
```bash
DELETE /api/runtime/projects/{project_id}
```

### Rebuild Project
```bash
POST /api/runtime/projects/{project_id}/rebuild
```

### Export Project
```bash
POST /api/runtime/projects/{project_id}/export?format=zip
```

## Integration with gaaius_builder.py

To integrate with your existing blueprint generation in gaaius_builder.py:

```python
# In your blueprint generation endpoint or method
from project_runtime_integration import ProjectRuntimeService, ProjectGenerationRequest

async def generate_full_project(blueprint_data):
    """Generate project from GAAIUS blueprint"""
    
    # Use existing GAAIUS blueprint
    service = ProjectRuntimeService()
    
    request = ProjectGenerationRequest(
        project_name=blueprint_data["app_name"],
        blueprint=blueprint_data,
        project_type="fullstack",
        frontend_framework="react",
        backend_framework="express",
        database="postgresql"
    )
    
    response = await service.generate_project(request)
    return response
```

## Integration with BuildPage Frontend Component

To integrate with your UI in `frontend/src/pages/BuildPage.tsx`:

```typescript
// In your BuildPage component, after blueprint generation:

const generateProject = async (blueprint: any) => {
  try {
    setGenerating(true);
    
    const response = await fetch('/api/runtime/projects/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        project_name: blueprint.app_name || 'My App',
        blueprint: blueprint,
        project_type: 'fullstack',
        frontend_framework: 'react',
        backend_framework: 'express'
      })
    });
    
    const result = await response.json();
    
    if (result.status === 'success') {
      setProjectId(result.project_id);
      setSteps(result.steps);
      
      // Optional: Start dev servers automatically
      await startDevServers(result.project_id);
    }
  } finally {
    setGenerating(false);
  }
};

const startDevServers = async (projectId: string) => {
  const response = await fetch(`/api/runtime/projects/${projectId}/start-servers`, {
    method: 'POST'
  });
  
  const result = await response.json();
  if (result.status === 'success') {
    setPreviewUrl(result.frontend_url);
  }
};
```

## MongoDB Integration (Optional)

If you want to persist project metadata to MongoDB:

```python
# In your server.py routes
from project_runtime_routes import router as runtime_router
from motor.motor_asyncio import AsyncIOMotorDatabase

# Your database connection
db: AsyncIOMotorDatabase

@app.post("/api/runtime/projects/generate")
async def generate_project(request: ProjectGenerationRequest):
    service = get_project_runtime_service()
    response = await service.generate_project(request, db)
    return response
```

## Environment Variables

Add these to your `.env` file:

```env
# Project Runtime
GENERATED_PROJECTS_PATH=generated_projects
VITE_PORT=5173
BACKEND_PORT=3001
NODE_ENV=development
```

## Testing

You can test the integration with curl:

```bash
# Test health check
curl http://localhost:8000/api/runtime/health

# Generate a project
curl -X POST http://localhost:8000/api/runtime/projects/generate \
  -H "Content-Type: application/json" \
  -d '{
    "project_name": "Test App",
    "blueprint": {
      "app_type": "saas_dashboard",
      "features": ["auth"]
    },
    "project_type": "fullstack"
  }'

# List projects
curl http://localhost:8000/api/runtime/projects

# Get project
curl http://localhost:8000/api/runtime/projects/{PROJECT_ID}
```

## Troubleshooting

### Import Errors
If you get `ModuleNotFoundError: No module named 'project_runtime'`:
- Make sure all 6 files are in the `backend/` directory
- Check that Python can find the backend module
- Restart your server

### Permission Errors
If you get permission denied when creating directories:
- Make sure `generated_projects/` directory is writable
- Check file permissions on `backend/` directory

### npm/pip Install Failures
If dependency installation fails:
- Check that npm and pip are in your PATH
- Ensure you have internet connection
- Check that Node.js and Python are installed correctly

## Next Steps

1. **Integrate routes** into server.py (Step 1 above)
2. **Test generation** using curl or Postman
3. **Update BuildPage** to call the new endpoints
4. **Build Preview Orchestrator** (System 5) to manage live dev servers
5. **Add export functions** (zip, docker, vercel deployment)

## Architecture Diagram

```
User Creates Blueprint
    ↓
BuildPage Component
    ↓
/api/runtime/projects/generate
    ↓
ProjectRuntimeService
    ├─ ScaffoldGenerator → Directory structure
    ├─ FrontendRuntimeGenerator → React components
    ├─ BackendRuntimeGenerator → API routes
    └─ ProjectRuntime → Orchestrator + dependency install
    ↓
Generated Project Ready
    ├─ frontend/ (React + Vite)
    ├─ backend/ (Express/FastAPI)
    ├─ shared/ (TypeScript types)
    └─ Configuration files
    ↓
/api/runtime/projects/{id}/start-servers
    ↓
Dev Servers Running
    ├─ Vite dev server (port 5173)
    └─ Express/FastAPI (port 3001)
    ↓
Preview in Browser
    └─ http://localhost:5173
```

## Summary

You now have a complete project generation system integrated with FastAPI:

✅ Generate full-stack projects from blueprints
✅ Manage project lifecycle
✅ Start dev servers
✅ Export and deploy projects
✅ REST API for all operations
✅ MongoDB integration (optional)

This transforms GAAIUS from a template generator to a full application runtime - Replit-class capability.
