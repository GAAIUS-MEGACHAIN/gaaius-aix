# 🚀 INTEGRATION QUICKSTART

**Time Estimate:** 30 minutes  
**Complexity:** Medium  
**Risk:** Low (no breaking changes)

---

## What You're About to Do

Connect all 5 runtime systems into your existing `server.py` so that:
1. Blueprint generation feeds into ProjectRuntime
2. Users can generate full-stack apps
3. Preview servers start automatically
4. Live preview shows real React app in iframe

---

## Step 1: Import the Systems (2 min)

Add to top of `server.py`:

```python
from project_runtime_integration import ProjectRuntimeIntegration
from project_runtime_routes import router as project_router
from preview_orchestrator_routes import router as preview_router
```

---

## Step 2: Initialize the Integrations (2 min)

In your FastAPI app setup:

```python
app = FastAPI()

# Initialize integrations
project_integration = ProjectRuntimeIntegration()

# Include routers
app.include_router(project_router, prefix="/api/projects", tags=["projects"])
app.include_router(preview_router, prefix="/api/preview", tags=["preview"])
```

---

## Step 3: Connect Blueprint Generator (3 min)

In your existing `/build` endpoint, after blueprint generation:

```python
@app.post("/api/build")
async def build_project(request: BuildRequest):
    # Your existing blueprint generation
    blueprint = await gaaius_builder.generate_blueprint(request)
    
    # NEW: Generate actual project
    result = await project_integration.generate_from_blueprint(
        blueprint=blueprint,
        project_name=request.project_name,
        project_id=str(uuid4())
    )
    
    return {
        "blueprint": blueprint,
        "project_id": result["project_id"],
        "project_path": result["path"],
        "next_steps": result["next_steps"]
    }
```

---

## Step 4: Update BuildPage Frontend (5 min)

In your React BuildPage component:

```javascript
// After blueprint generation
const { project_id, project_path, next_steps } = buildResponse.data;

// Show generation progress
setStep("Generating project structure...");
await api.post(`/api/projects/${project_id}/generate`);

// Start dev servers
setStep("Starting dev servers...");
const previewUrl = await api.post(`/api/projects/${project_id}/preview/start`);

// Show preview in iframe
setPreviewIframe(previewUrl);
```

---

## Step 5: Test It (15 min)

```bash
# 1. Start your server
python run_server.py

# 2. In another terminal, trigger generation
curl -X POST http://localhost:8000/api/build \
  -H "Content-Type: application/json" \
  -d '{
    "project_name": "Test App",
    "description": "A test application",
    "features": ["auth", "dashboard"]
  }'

# 3. Check projects were created
ls -la user/projects/

# 4. Verify dev servers started
curl http://localhost:5173/  # Vite frontend
curl http://localhost:3001/api/health  # Express/FastAPI
```

---

## Expected Output

### Step 1: Generation Response
```json
{
  "project_id": "proj_abc123",
  "project_path": "/user/projects/proj_abc123",
  "status": "success",
  "next_steps": [
    "Dev servers started",
    "Frontend running at localhost:5173",
    "Backend API at localhost:3001",
    "Open preview to see live app"
  ]
}
```

### Step 2: Preview Response
```json
{
  "preview_url": "http://localhost:5173",
  "frontend_status": "running",
  "backend_status": "running",
  "dev_server_pid": 12345
}
```

---

## Frontend Component Example

```javascript
// BuildPage.tsx - Add this section

const [generatedProject, setGeneratedProject] = useState(null);
const [previewUrl, setPreviewUrl] = useState(null);
const [generationProgress, setGenerationProgress] = useState([]);

async function handleGenerateProject() {
  try {
    // Step 1: Generate blueprint and project
    setGenerationProgress(["Generating blueprint..."]);
    const blueprintRes = await api.post("/api/build", {
      project_name: projectName,
      description: projectDescription,
      features: selectedFeatures
    });

    setGenerationProgress(prev => [
      ...prev,
      "Blueprint created ✓",
      "Scaffolding project..."
    ]);

    const { project_id } = blueprintRes.data;

    // Step 2: Start dev servers
    setGenerationProgress(prev => [
      ...prev,
      "Project scaffolded ✓",
      "Starting dev servers..."
    ]);

    const previewRes = await api.post(
      `/api/projects/${project_id}/preview/start`
    );

    setGenerationProgress(prev => [
      ...prev,
      "Dev servers started ✓",
      "Ready for preview!"
    ]);

    setGeneratedProject(blueprintRes.data);
    setPreviewUrl(previewRes.data.preview_url);

  } catch (error) {
    setGenerationProgress(prev => [
      ...prev,
      `Error: ${error.message}`
    ]);
  }
}

return (
  <div>
    {/* Generation Progress */}
    {generationProgress.length > 0 && (
      <div className="bg-blue-50 p-4 rounded">
        <h3 className="font-bold mb-2">Generation Progress</h3>
        <ul className="space-y-1">
          {generationProgress.map((step, i) => (
            <li key={i} className="text-sm text-blue-900">{step}</li>
          ))}
        </ul>
      </div>
    )}

    {/* Preview Iframe */}
    {previewUrl && (
      <div className="mt-6">
        <h3 className="font-bold mb-2">Live Preview</h3>
        <iframe
          src={previewUrl}
          className="w-full h-96 border rounded"
          title="Project Preview"
        />
      </div>
    )}

    {/* Generate Button */}
    <button
      onClick={handleGenerateProject}
      className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
    >
      Generate Full Project
    </button>
  </div>
);
```

---

## Verification Checklist

- [ ] All imports resolve without errors
- [ ] Routes register successfully
- [ ] POST /api/projects/generate responds
- [ ] Projects scaffold in filesystem
- [ ] npm install completes
- [ ] Dev servers start
- [ ] Frontend accessible at localhost:5173
- [ ] Backend accessible at localhost:3001
- [ ] Preview iframe loads and renders

---

## Troubleshooting

### Problem: Routes not found
**Solution:** Make sure routers are included before you start the server
```python
app.include_router(project_router)
app.include_router(preview_router)
# Then start: uvicorn server:app --reload
```

### Problem: npm install fails
**Solution:** Check if Node.js is installed
```bash
node --version  # Should be 16+
npm --version   # Should be 8+
```

### Problem: Port 5173 or 3001 already in use
**Solution:** Change ports in config or kill existing process
```bash
# Windows
Get-Process | Where-Object {$_.Name -like "*node*"} | Stop-Process -Force

# macOS/Linux
lsof -i :5173  # Find process
kill -9 <PID>
```

### Problem: Preview iframe is blank
**Solution:** Check browser console for CORS or 404 errors
- Make sure frontend is actually running: `curl http://localhost:5173`
- Check dev server logs in project directory
- Verify CORS headers are correct

---

## Next Steps After Integration

1. **Test with users** - Have a user generate a project
2. **Gather feedback** - What needs improvement?
3. **Add export options** - Web, mobile, desktop
4. **Build team features** - Share projects, collaborate
5. **Create templates** - Reusable starting points

---

## Files to Review (Deep Dive)

If you want to understand the systems better:

1. `backend/project_runtime.py` - Main orchestrator logic
2. `backend/scaffold_generator.py` - Directory structure creation
3. `backend/frontend_runtime_generator.py` - React component generation
4. `backend/backend_runtime_generator.py` - API generation
5. `backend/preview_orchestrator.py` - Dev server management

Each has detailed docstrings and examples.

---

## Success Indicators

After integration, you should see:

✅ **In terminal:** Dev server logs showing Vite and Express starting  
✅ **In browser:** iframe showing React app (not static HTML)  
✅ **In filesystem:** Real project structure with node_modules  
✅ **In API:** Endpoints responding with project data  
✅ **In console:** No errors, clean compilation

---

## Quick Diagnostic Command

Run this to verify everything is in place:

```bash
# Windows PowerShell
$files = @(
  "backend/project_runtime.py",
  "backend/scaffold_generator.py",
  "backend/frontend_runtime_generator.py",
  "backend/backend_runtime_generator.py",
  "backend/preview_orchestrator.py"
)

$files | ForEach-Object {
  if (Test-Path $_) {
    Write-Host "✓ $_" -ForegroundColor Green
  } else {
    Write-Host "✗ $_" -ForegroundColor Red
  }
}
```

---

## Support

If anything doesn't work:

1. Check the error message carefully
2. Review the relevant system file's docstring
3. Check that all dependencies in `requirements.txt` are installed
4. Verify Python version is 3.10+
5. Make sure Node.js 16+ is installed

All 5 systems have comprehensive error handling and logging.

---

**Ready to integrate? You've got this! 🚀**
