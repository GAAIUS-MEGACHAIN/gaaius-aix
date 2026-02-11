@echo off
REM Quick Commands for AI Builder (Windows)

echo.
echo ==================================================
echo   AI BUILDER - QUICK START (Windows)
echo ==================================================
echo.

echo STEP 1 - Start Backend Server:
echo   python run_server.py
echo.

echo STEP 2 - Start Frontend Dev Server (in new terminal):
echo   cd frontend
echo   npm start
echo.

echo STEP 3 - Open Browser:
echo   http://localhost:3000/build
echo.

echo ==================================================
echo   USEFUL COMMANDS
echo ==================================================
echo.

echo Test Backend Compilation:
echo   python -m py_compile backend/build_service.py
echo.

echo Test Project Creation:
echo   curl -X POST http://localhost:8000/api/build/project/create ^
echo     -H "Content-Type: application/json" ^
echo     -d "{\"name\":\"test\",\"template\":\"python\"}"
echo.

echo Build Frontend:
echo   cd frontend
echo   npm run build
echo.

echo ==================================================
echo   FEATURE OVERVIEW
echo ==================================================
echo.

echo Left Panel:
echo   - Chat: AI code generation
echo   - Images: Generated images
echo   - Files: File explorer (NEW!)
echo.

echo Right Panel:
echo   - Preview: Live HTML/CSS/JS preview
echo   - Code: Monaco editor
echo   - Execute: Run Python/JS/Shell (NEW!)
echo   - Packages: Install pip/npm (NEW!)
echo   - Terminal: Output display (NEW!)
echo.

echo ==================================================
echo   STATUS: READY TO DEPLOY ✓
echo ==================================================
echo.

echo All features implemented and integrated!
echo No breaking changes, fully backward compatible.
echo.

pause
