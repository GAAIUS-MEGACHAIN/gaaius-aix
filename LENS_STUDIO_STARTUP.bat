@echo off
REM Lens Studio - Quick Start Script (Windows)
REM Production-ready Snapchat Lens Studio clone startup

echo.
echo ================================================
echo  LENS STUDIO - Production AR Filter Platform
echo ================================================
echo.

REM Check Python
echo [1/5] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found. Please install Python 3.8+
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo ✅ Python found: %PYTHON_VERSION%

REM Check Node.js
echo [2/5] Checking Node.js installation...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js not found. Please install Node.js 16+
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('node --version') do set NODE_VERSION=%%i
echo ✅ Node.js found: %NODE_VERSION%

REM Check MongoDB
echo [3/5] Checking MongoDB connection...
mongod --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  MongoDB not found locally - using remote instance
) else (
    echo ✅ MongoDB found
)

REM Install Python dependencies
echo [4/5] Installing backend dependencies...
if exist backend\requirements.txt (
    python -m pip install -q -r backend\requirements.txt
    if %errorlevel% equ 0 (
        echo ✅ Backend dependencies installed
    ) else (
        echo ❌ Failed to install backend dependencies
        pause
        exit /b 1
    )
) else (
    echo ❌ requirements.txt not found
    pause
    exit /b 1
)

REM Install frontend dependencies
echo [5/5] Installing frontend dependencies...
if exist frontend (
    cd frontend
    call npm install -q --legacy-peer-deps
    if %errorlevel% equ 0 (
        echo ✅ Frontend dependencies installed
    ) else (
        echo ❌ Failed to install frontend dependencies
        pause
        exit /b 1
    )
    cd ..
) else (
    echo ❌ Frontend directory not found
    pause
    exit /b 1
)

echo.
echo ================================================
echo ✅ Setup Complete!
echo ================================================
echo.
echo Next steps:
echo 1. Start MongoDB: mongod --dbpath .\data
echo 2. Start Backend: python backend\server.py
echo 3. Start Frontend: cd frontend ^& npm start
echo.
echo Access Lens Studio at: http://localhost:3000
echo API Documentation: http://localhost:8000/docs
echo.
pause
