#!/bin/bash
# Lens Studio - Quick Start Script
# Production-ready Snapchat Lens Studio clone startup

echo "🚀 Starting Lens Studio - Production AR Filter Platform"
echo "=================================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python
echo -e "${BLUE}[1/5]${NC} Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Please install Python 3.8+"
    exit 1
fi
echo -e "${GREEN}✅ Python found: $(python3 --version)${NC}"

# Check Node.js
echo -e "${BLUE}[2/5]${NC} Checking Node.js installation..."
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 16+"
    exit 1
fi
echo -e "${GREEN}✅ Node.js found: $(node --version)${NC}"

# Check MongoDB
echo -e "${BLUE}[3/5]${NC} Checking MongoDB connection..."
if ! command -v mongod &> /dev/null; then
    echo "⚠️  MongoDB not installed locally - using remote instance"
else
    echo -e "${GREEN}✅ MongoDB found${NC}"
fi

# Install Python dependencies
echo -e "${BLUE}[4/5]${NC} Installing backend dependencies..."
if [ -f "backend/requirements.txt" ]; then
    pip install -r backend/requirements.txt -q
    echo -e "${GREEN}✅ Backend dependencies installed${NC}"
else
    echo "❌ requirements.txt not found"
    exit 1
fi

# Install frontend dependencies
echo -e "${BLUE}[5/5]${NC} Installing frontend dependencies..."
if [ -d "frontend" ]; then
    cd frontend
    npm install -q --legacy-peer-deps
    echo -e "${GREEN}✅ Frontend dependencies installed${NC}"
    cd ..
else
    echo "❌ Frontend directory not found"
    exit 1
fi

echo ""
echo "=================================================="
echo -e "${GREEN}✅ Setup Complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Start MongoDB: mongod --dbpath ./data"
echo "2. Start Backend: python backend/server.py"
echo "3. Start Frontend: cd frontend && npm start"
echo ""
echo "Access Lens Studio at: http://localhost:3000"
echo "API Documentation: http://localhost:8000/docs"
echo ""
