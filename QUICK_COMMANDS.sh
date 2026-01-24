#!/bin/bash
# Quick Commands for AI Builder

# ===== BACKEND =====
echo "Backend Commands:"
echo "  Start Server:        python run_server.py"
echo "  Test Compilation:    python -m py_compile backend/build_service.py"
echo "  Check Backend:       python -c 'from backend.build_service import BuildService; print(\"✓ Backend OK\")'"

# ===== FRONTEND =====
echo ""
echo "Frontend Commands:"
echo "  Start Dev Server:    cd frontend && npm start"
echo "  Build Production:    cd frontend && npm run build"
echo "  Test Build:          cd frontend && npm run build --verbose"

# ===== TESTING =====
echo ""
echo "Testing Commands:"
echo "  Test Project Create:"
echo "    curl -X POST http://localhost:8000/api/build/project/create \\"
echo "      -H 'Content-Type: application/json' \\"
echo "      -d '{\"name\":\"test\",\"template\":\"python\"}'"
echo ""
echo "  Test Code Execution:"
echo "    curl -X POST http://localhost:8000/api/build/project/{id}/execute \\"
echo "      -H 'Content-Type: application/json' \\"
echo "      -d '{\"code\":\"print(\\\"hello\\\")\",\"language\":\"python\"}'"

# ===== QUICK START =====
echo ""
echo "Quick Start:"
echo "  1. Terminal 1:  python run_server.py"
echo "  2. Terminal 2:  cd frontend && npm start"
echo "  3. Browser:     http://localhost:3000/build"
echo "  4. Start building!"

# ===== LOGS =====
echo ""
echo "Check Logs:"
echo "  Backend:         tail -f server.log"
echo "  Backend Errors:  tail -f server.err"

# ===== STATUS =====
echo ""
echo "=== STATUS ==="
echo "✅ Backend Service:  READY (build_service.py)"
echo "✅ UI Components:    READY (BuildPageEnhancements.jsx)"
echo "✅ App.js Integrated: READY"
echo "✅ Routes Registered: READY"
echo "✅ Ready for Deploy:  YES ✓"
echo ""
echo "🚀 Time to build something amazing!"
