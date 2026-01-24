================================================================================
AI CANVAS - ITERATION & ENHANCEMENT GUIDE
================================================================================

This guide shows how to iterate and add features to the AI Canvas system.

================================================================================
CURRENT STATE
================================================================================

Completed Components:
  ✅ ai_canvas_service.py - Core design engine (1,200+ lines)
  ✅ ai_canvas_templates.py - Template library (800+ lines)
  ✅ ai_canvas_groq_enhancement.py - Groq AI (600+ lines)
  ✅ ai_canvas_ml_enhancement.py - ML models (800+ lines)
  ✅ AICanvas.jsx - Basic editor (750+ lines)
  ✅ AICanvasEnhanced.jsx - Full featured UI (650+ lines)

API Endpoints: 21 endpoints across 4 routers
Database: MongoDB with design & template collections
Frontend: React with styled-components

================================================================================
COMMON ITERATION PATTERNS
================================================================================

1. ADD NEW TEMPLATE CATEGORY
   ─────────────────────────────

   Step 1: Update TemplateCategory enum in ai_canvas_templates.py
   
     class TemplateCategory(str, Enum):
         # ... existing categories ...
         NEW_CATEGORY = "new_category"  # Add this

   Step 2: Add template definitions to init_templates()
   
     templates.append(Template(
         id=str(uuid.uuid4()),
         name="Template Name",
         category="new_category",
         description="...",
         dimensions={"width": 1080, "height": 1080},
         # ... other fields ...
     ))

   Step 3: Update frontend category tabs in AICanvasEnhanced.jsx
   
     const categories = [
       // ... existing ...
       'new_category'
     ];

   Step 4: Test
     - GET /api/ai-canvas/templates/category/new_category
     - Frontend should show new category tab

2. ADD NEW AI FEATURE
   ──────────────────

   Step 1: Add method to DesignAssistant in ai_canvas_groq_enhancement.py
   
     async def your_new_feature(self, your_param: YourType) -> Dict:
         # Implementation using Groq API
         pass

   Step 2: Add API endpoint
   
     @router.post("/your-endpoint")
     async def your_endpoint(request: YourRequest):
         return await design_assistant.your_new_feature(request.param)

   Step 3: Call from frontend
   
     const response = await axios.post(
       '/api/ai-canvas/design-ai/your-endpoint',
       { param: value }
     );

   Step 4: Update AICanvasEnhanced.jsx to display results
     - Add state for results
     - Add section to display
     - Call endpoint on trigger

3. ADD NEW ML MODEL
   ─────────────────

   Step 1: Add method to MLEnhancementService in ai_canvas_ml_enhancement.py
   
     async def your_model(self, request: YourRequest) -> Dict:
         # Call external API
         # Return results
         pass

   Step 2: Add endpoint
   
     @router.post("/your-model")
     async def your_model_endpoint(request: YourRequest):
         return await ml_service.your_model(request)

   Step 3: Update frontend to call endpoint
     - Add button or trigger
     - Call endpoint
     - Display results

4. ENHANCE FRONTEND UI
   ────────────────────

   Step 1: Add styled component for new element
   
     const NewElement = styled.div`
       // styling
     `;

   Step 2: Add state if needed
   
     const [newState, setNewState] = useState(initial);

   Step 3: Add to component JSX
   
     <NewElement>
       {/* content */}
     </NewElement>

   Step 4: Test styling and responsiveness

================================================================================
HOW TO ADD A SPECIFIC FEATURE
================================================================================

Example: Add "Color Palette Generator" Feature

Step 1: Backend - Add Groq method (ai_canvas_groq_enhancement.py)
────────────────────────────────────────────────────────────────

  async def generate_color_palette(self, prompt: str, count: int = 5):
      """Generate color palettes using Groq"""
      try:
          response = await asyncio.to_thread(
              self.client.chat.completions.create,
              model="mixtral-8x7b-32768",
              messages=[{
                  "role": "user",
                  "content": f"""Generate {count} color palettes for: {prompt}
                  
                  For each palette, provide:
                  - Name
                  - 5 hex colors
                  - Use case
                  - Mood/vibe
                  
                  Format as JSON."""
              }],
              temperature=0.8,
              max_tokens=1500
          )
          
          palettes_text = response.choices[0].message.content
          try:
              palettes = json.loads(palettes_text)
          except:
              palettes = {"palettes": palettes_text}
          
          return {
              "success": True,
              "palettes": palettes,
              "generated_at": datetime.utcnow().isoformat()
          }
      except Exception as e:
          logger.error(f"Color palette generation error: {e}")
          return {"error": str(e)}

Step 2: Backend - Add endpoint (ai_canvas_groq_enhancement.py)
──────────────────────────────────────────────────────────────

  @router.post("/color-palette")
  async def generate_color_palette(
      prompt: str = Body(...),
      count: int = Body(5, ge=1, le=10)
  ):
      """Generate color palettes for design"""
      return await design_assistant.generate_color_palette(prompt, count)

Step 3: Frontend - Add state (AICanvasEnhanced.jsx)
───────────────────────────────────────────────────

  const [colorPalettes, setColorPalettes] = useState([]);
  const [palettePrompt, setPalettePrompt] = useState('');
  const [paletteLoading, setPaletteLoading] = useState(false);

Step 4: Frontend - Add function (AICanvasEnhanced.jsx)
──────────────────────────────────────────────────────

  const generateColorPalettes = async () => {
      if (!palettePrompt.trim()) return;
      
      try {
          setPaletteLoading(true);
          const response = await axios.post(
              '/api/ai-canvas/design-ai/color-palette',
              { prompt: palettePrompt, count: 5 }
          );
          
          setColorPalettes(response.data.palettes || []);
          setChatMessages(prev => [...prev, {
              type: 'bot',
              message: 'Generated 5 color palettes for your design!'
          }]);
      } catch (error) {
          console.error('Palette generation failed:', error);
      } finally {
          setPaletteLoading(false);
      }
  };

Step 5: Frontend - Add UI section (AICanvasEnhanced.jsx)
────────────────────────────────────────────────────────

  <AISection>
      <h4>🎨 Color Palette Generator</h4>
      <div style={{display: 'flex', gap: '8px', marginBottom: '12px'}}>
          <input
              type="text"
              placeholder="e.g., 'Modern tech startup'"
              value={palettePrompt}
              onChange={(e) => setPalettePrompt(e.target.value)}
              style={{
                  flex: 1,
                  padding: '8px 10px',
                  background: 'rgba(255,255,255,0.05)',
                  border: '1px solid rgba(139,92,246,0.3)',
                  borderRadius: '4px',
                  color: 'white',
              }}
          />
          <button 
              onClick={generateColorPalettes}
              disabled={paletteLoading}
              style={{
                  padding: '8px 12px',
                  background: '#8b5cf6',
                  border: 'none',
                  borderRadius: '4px',
                  color: 'white',
              }}
          >
              {paletteLoading ? '⏳' : 'Generate'}
          </button>
      </div>
      
      <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px'}}>
          {colorPalettes.map((palette, idx) => (
              <div key={idx} style={{
                  background: 'rgba(139,92,246,0.1)',
                  border: '1px solid rgba(139,92,246,0.3)',
                  borderRadius: '6px',
                  padding: '10px'
              }}>
                  <p style={{margin: 0, fontSize: '12px', fontWeight: 600}}>
                      {palette.name}
                  </p>
                  <div style={{display: 'flex', gap: '4px', marginTop: '6px'}}>
                      {palette.colors?.map((color, i) => (
                          <div key={i} style={{
                              width: '20px',
                              height: '20px',
                              background: color,
                              borderRadius: '3px',
                              border: '1px solid rgba(0,0,0,0.2)'
                          }} title={color} />
                      ))}
                  </div>
              </div>
          ))}
      </div>
  </AISection>

Step 6: Test
────────────

  Backend:
  curl -X POST http://localhost:8000/api/ai-canvas/design-ai/color-palette \
    -H "Content-Type: application/json" \
    -d '{"prompt":"Modern tech startup","count":5}'

  Frontend:
  1. Visit http://localhost:3000/ai-canvas
  2. Type prompt in color generator
  3. Click Generate
  4. See color palettes appear

================================================================================
MODIFYING EXISTING FEATURES
================================================================================

To Modify Templates:

  1. Edit ai_canvas_templates.py
  2. Update template definitions in the templates list
  3. Restart backend
  4. Changes will appear immediately in frontend

To Modify AI Suggestions:

  1. Edit ai_canvas_groq_enhancement.py
  2. Update the prompt in the method
  3. Restart backend
  4. New suggestions will be generated with new logic

To Modify Frontend UI:

  1. Edit AICanvasEnhanced.jsx
  2. Update styled components or JSX
  3. Save and hot-reload in development
  4. No backend restart needed

To Add New API Response Fields:

  1. Update Pydantic model in the service file
  2. Update the return statement
  3. Update frontend to handle new field
  4. Test with curl/Postman

================================================================================
TESTING CHECKLIST FOR ITERATIONS
================================================================================

Backend Testing:
  ☐ Python syntax: python -m py_compile file.py
  ☐ Import test: python -c "from server import app"
  ☐ Endpoint test: curl -X GET http://localhost:8000/api/...
  ☐ Log check: tail -f logs/app.log
  ☐ No error messages

Frontend Testing:
  ☐ npm run build (no errors)
  ☐ npm run dev (hot reload works)
  ☐ Browser console (no errors)
  ☐ Network tab (requests succeed)
  ☐ Visual inspection (styling correct)
  ☐ Responsive design (on mobile)
  ☐ API responses displayed

Integration Testing:
  ☐ Full flow from template selection to AI response
  ☐ Error handling (graceful fallback)
  ☐ Loading states (spinner visible)
  ☐ Data persistence (refreshes show correct state)

================================================================================
DEBUGGING TIPS
================================================================================

Backend Issues:
  
  Import errors:
    - Check file path relative to server.py
    - Check spelling of imports
    - Verify file exists in backend/
    - Check sys.path configuration

  API endpoint not found:
    - Verify router is imported
    - Check router is include_router() in server.py
    - Verify endpoint path in decorator
    - Check method name matches request

  Groq API errors:
    - Check GROQ_API_KEY is set: echo $GROQ_API_KEY
    - Verify API key is valid
    - Check rate limits not exceeded
    - See fallback suggestions if key missing

  ML model errors:
    - Check API tokens are set
    - Verify Replicate/HuggingFace connection
    - Check model names are correct
    - See error response details

Frontend Issues:

  Endpoints not found (404):
    - Check backend is running
    - Verify API URL is correct
    - Check CORS is configured
    - Check request method (GET vs POST)

  Components not showing:
    - Check state is being set
    - Verify CSS styling is correct
    - Check z-index conflicts
    - Verify component is imported

  API calls not working:
    - Check network tab (see request)
    - Check response status and body
    - Verify response matches expected format
    - Check error handling in catch block

================================================================================
PERFORMANCE OPTIMIZATION
================================================================================

If AI suggestions are slow:
  - Cache Groq responses for common queries
  - Limit max tokens in API request
  - Use faster model if available
  - Implement request debouncing

If image generation is slow:
  - Use faster model (not SDXL)
  - Reduce image dimensions
  - Queue requests to avoid bottlenecks
  - Implement progress tracking

If frontend feels slow:
  - Lazy load images
  - Virtualize long lists
  - Debounce search input
  - Optimize styled components

If database is slow:
  - Add indexes on frequently queried fields
  - Paginate large result sets
  - Cache popular templates
  - Archive old designs

================================================================================
SCALING CONSIDERATIONS
================================================================================

When adding many more features:

  1. Split routers into multiple files
     - templates_router.py
     - groq_router.py
     - ml_router.py
     - Each in separate file

  2. Implement caching
     - Cache template lists
     - Cache AI suggestions
     - Use Redis for distributed cache

  3. Async operations
     - Move long-running tasks to background jobs
     - Use Celery or similar task queue
     - Return job ID, poll for results

  4. Database optimization
     - Add indexes for query performance
     - Archive old designs
     - Partition templates collection

  5. API rate limiting
     - Limit requests per user
     - Throttle AI API calls
     - Queue excess requests

================================================================================
COMMON PATTERNS
================================================================================

Pattern 1: Add Feature → Backend Method → Endpoint → Frontend Call

  Example flow for "Font Pairing Suggestion":
  1. Add async def suggest_fonts() to DesignAssistant
  2. Add @router.post("/fonts") endpoint
  3. Call from frontend: axios.post('/api/ai-canvas/design-ai/fonts', data)
  4. Display results in UI

Pattern 2: Add API Integration → Wrapper Class → Service Method → Endpoint

  Example for new ML model:
  1. Create wrapper class for API (e.g., MyModelAPI)
  2. Add method to MLEnhancementService calling wrapper
  3. Add endpoint @router.post("/my-model")
  4. Integrate in frontend

Pattern 3: Add UI Element → Styled Component → State → Event Handler

  Example for new control:
  1. Create styled component for visual
  2. Add state for value
  3. Add onClick handler calling API
  4. Display results

================================================================================
NEXT ITERATIONS (Suggested)
================================================================================

High Priority:
  1. Custom template creation UI
  2. Template versioning
  3. Design collaboration (real-time)
  4. Advanced undo/redo
  5. Component library

Medium Priority:
  6. Template marketplace
  7. Design handoff tools
  8. AI writing assistant
  9. Font library integration
  10. Stock image integration

Low Priority (Future):
  11. Design system builder
  12. 3D canvas support
  13. Video design templates
  14. AR preview
  15. Export to Figma/other tools

================================================================================
QUICK COMMANDS
================================================================================

Check syntax:
  python -m py_compile backend/ai_canvas_*.py

Verify imports:
  python -c "from server import app"

Test endpoint:
  curl http://localhost:8000/api/ai-canvas/templates

View logs:
  tail -f logs/app.log

Start backend:
  python server.py

Start frontend:
  npm run dev

Build frontend:
  npm run build

================================================================================
SUPPORT
================================================================================

For questions about:
  - Architecture: See AI_CANVAS_ENHANCEMENT_COMPLETE.md
  - Deployment: See AI_CANVAS_DEPLOYMENT_READY.md
  - Code: Check docstrings in service files
  - Endpoints: Check @router decorators
  - Components: Check JSX files

================================================================================
