# QUICK START: Integrate Project Runtime into server.py

**Estimated time: 5 minutes**

## Step 1: Add Imports to server.py

Find the imports section (around line 50-150) and add:

```python
# Add with other local imports
from project_runtime_integration import ProjectRuntimeService, get_project_runtime_service
from project_runtime_routes import router as runtime_router
from preview_orchestrator_routes import router as preview_router
```

## Step 2: Include Routers in FastAPI App

Find where other routers are included (search for `app.include_router`) and add:

```python
# Include runtime routers
app.include_router(runtime_router)
app.include_router(preview_router)
```

## Step 3: Create generated_projects Directory

Run this command:
```bash
mkdir generated_projects
```

## Step 4: Start Server

```bash
python run_server.py
```

## Step 5: Test It

### Health check
```bash
curl http://localhost:8000/api/runtime/health
curl http://localhost:8000/api/preview/health
```

### Generate a project
```bash
curl -X POST http://localhost:8000/api/runtime/projects/generate \
  -H "Content-Type: application/json" \
  -d '{
    "project_name": "Test SaaS App",
    "blueprint": {
      "app_type": "saas_dashboard",
      "pages": ["Dashboard", "Analytics", "Settings"],
      "features": ["auth", "search", "notifications"],
      "layout": {"type": "sidebar"}
    },
    "project_type": "fullstack",
    "frontend_framework": "react",
    "backend_framework": "express",
    "database": "postgresql"
  }'
```

You'll get back:
```json
{
  "status": "success",
  "project_id": "550e8400-e29b-41d4-a716-446655440000",
  "project_path": "generated_projects/550e8400...",
  "steps": ["Created project scaffold", ...],
  "message": "Project generated successfully in 45234ms"
}
```

### Get project
```bash
curl http://localhost:8000/api/runtime/projects/550e8400-e29b-41d4-a716-446655440000
```

### Start servers
```bash
curl -X POST http://localhost:8000/api/preview/projects/550e8400-e29b-41d4-a716-446655440000/start
```

### Check preview
```bash
curl http://localhost:8000/api/preview/projects/550e8400-e29b-41d4-a716-446655440000/status
```

## That's It!

Your project is now generated and running:
- Frontend: http://localhost:5173
- Backend API: http://localhost:3001

---

## How to Integrate with BuildPage Component

In `frontend/src/pages/BuildPage.tsx`:

```typescript
import { useState } from 'react';

export default function BuildPage() {
  const [projectId, setProjectId] = useState('');
  const [steps, setSteps] = useState<string[]>([]);
  const [previewUrl, setPreviewUrl] = useState('');
  const [loading, setLoading] = useState(false);

  const generateProject = async (blueprint: any) => {
    setLoading(true);
    try {
      const response = await fetch('/api/runtime/projects/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project_name: blueprint.app_name || 'My App',
          blueprint: blueprint,
          project_type: 'fullstack',
          frontend_framework: 'react',
          backend_framework: 'express',
          database: 'postgresql',
          use_typescript: true
        })
      });

      const result = await response.json();
      
      if (result.status === 'success') {
        setProjectId(result.project_id);
        setSteps(result.steps || []);
        
        // Start dev servers
        await startServers(result.project_id);
      } else {
        alert(`Generation failed: ${result.message}`);
      }
    } catch (error) {
      console.error('Error:', error);
      alert('Error generating project');
    } finally {
      setLoading(false);
    }
  };

  const startServers = async (id: string) => {
    try {
      const response = await fetch(`/api/preview/projects/${id}/start`, {
        method: 'POST'
      });
      
      const result = await response.json();
      
      if (result.status === 'success') {
        setPreviewUrl(result.frontend.url);
      }
    } catch (error) {
      console.error('Error starting servers:', error);
    }
  };

  return (
    <div className="p-8 bg-gradient-to-br from-slate-950 to-slate-900 min-h-screen">
      <h1 className="text-3xl font-bold text-white mb-8">Generate Application</h1>
      
      {loading && (
        <div className="mb-8 space-y-2">
          <p className="text-white">Generating application...</p>
          {steps.map((step, i) => (
            <div key={i} className="text-green-400">✓ {step}</div>
          ))}
        </div>
      )}
      
      {previewUrl && !loading && (
        <div className="space-y-4 mb-8">
          <div className="bg-green-500/20 border border-green-500 rounded-lg p-4 text-green-400">
            <p>✓ Project generated successfully!</p>
            <p>Frontend running at: {previewUrl}</p>
          </div>
          
          <div className="rounded-lg overflow-hidden border border-slate-700 h-96">
            <iframe 
              src={previewUrl}
              className="w-full h-full"
              title="Project Preview"
            />
          </div>
        </div>
      )}
      
      <div className="bg-slate-800 rounded-lg p-8 space-y-4">
        <button
          onClick={() => {
            const blueprint = {
              app_type: 'saas_dashboard',
              app_name: 'My SaaS App',
              pages: ['Dashboard', 'Analytics', 'Settings'],
              features: ['auth', 'search', 'notifications'],
              layout: { type: 'sidebar' }
            };
            generateProject(blueprint);
          }}
          disabled={loading}
          className="px-6 py-3 bg-violet-600 hover:bg-violet-700 disabled:opacity-50 text-white rounded-lg font-semibold"
        >
          {loading ? 'Generating...' : 'Generate Application'}
        </button>
      </div>
    </div>
  );
}
```

---

## Environment Variables (.env)

Make sure these are set:

```env
# Existing
GROQ_API_KEY=your-key
MONGO_URL=mongodb://127.0.0.1:27017
DB_NAME=gaaius

# New (optional, defaults are fine)
GENERATED_PROJECTS_PATH=generated_projects
VITE_PORT=5173
BACKEND_PORT=3001
```

---

## Troubleshooting

### Port already in use
If port 5173 or 3001 are already in use, the system will auto-select the next available port. Check the response to see which ports were assigned.

### npm install fails
Make sure you have Node.js and npm installed:
```bash
node --version
npm --version
```

### Python dependencies
Make sure uvicorn and other dependencies are installed:
```bash
pip install -r requirements.txt
```

### Generated project doesn't run
Check the project structure:
```bash
ls -la generated_projects/{project_id}/frontend
ls -la generated_projects/{project_id}/backend
```

Both should have package.json files.

---

## Architecture Diagram

```
Browser
  ↓
  └─→ BuildPage Component
       └─→ Click "Generate Application"
           ↓
           POST /api/runtime/projects/generate
           ↓
           Server (server.py)
           ├─ ProjectRuntimeService
           │  └─ Orchestrates 4 systems
           │     ├─ ScaffoldGenerator
           │     ├─ FrontendRuntimeGenerator
           │     ├─ BackendRuntimeGenerator
           │     └─ ProjectRuntime
           ↓
           Generated Project Created
           ├─ frontend/ (React + Vite)
           └─ backend/ (Express/FastAPI)
           ↓
           POST /api/preview/projects/{id}/start
           ↓
           PreviewOrchestrator
           ├─ Start Vite → localhost:5173
           └─ Start Express → localhost:3001
           ↓
           Browser
           └─→ Show Preview
               └─→ <iframe src="http://localhost:5173" />
```

---

## Full Request/Response Example

### Request
```
POST /api/runtime/projects/generate
Content-Type: application/json

{
  "project_name": "E-Commerce Platform",
  "blueprint": {
    "app_type": "ecommerce",
    "pages": ["Products", "Cart", "Checkout", "Orders"],
    "features": ["auth", "payment", "search", "notifications"],
    "layout": {"type": "navbar"}
  },
  "project_type": "fullstack",
  "frontend_framework": "react",
  "backend_framework": "express",
  "database": "postgresql",
  "use_typescript": true,
  "include_docker": true,
  "include_github_actions": true
}
```

### Response
```json
{
  "status": "success",
  "project_id": "f3b5c2d9-8e1a-4c6b-9d2e-5f8c3a1b6e9d",
  "project_name": "E-Commerce Platform",
  "project_path": "generated_projects/f3b5c2d9-8e1a-4c6b-9d2e-5f8c3a1b6e9d",
  "blueprint_path": "generated_projects/f3b5c2d9-8e1a-4c6b-9d2e-5f8c3a1b6e9d/gaaius.json",
  "manifest_path": "generated_projects/f3b5c2d9-8e1a-4c6b-9d2e-5f8c3a1b6e9d/gaaius_manifest.json",
  "steps": [
    "Created project scaffold in generated_projects/f3b5c2d9...",
    "Generated 8 React components for e-commerce",
    "Generated Express routes: /auth, /products, /cart, /orders",
    "Installed npm dependencies (frontend + backend)",
    "Created git repository",
    "Generated gaaius_manifest.json"
  ],
  "message": "Project 'E-Commerce Platform' generated successfully in 52341ms"
}
```

### Start Servers Request
```
POST /api/preview/projects/f3b5c2d9-8e1a-4c6b-9d2e-5f8c3a1b6e9d/start
```

### Start Servers Response
```json
{
  "status": "success",
  "project_id": "f3b5c2d9-8e1a-4c6b-9d2e-5f8c3a1b6e9d",
  "frontend": {
    "success": true,
    "message": "Frontend server running on http://localhost:5173",
    "url": "http://localhost:5173"
  },
  "backend": {
    "success": true,
    "message": "Express server running on http://localhost:3001",
    "url": "http://localhost:3001"
  }
}
```

---

## That's it! 

Your GAAIUS platform is now:
- ✅ Generating full-stack applications
- ✅ Running development servers
- ✅ Providing live preview
- ✅ Production-ready code

**This is Replit-class capability.**
