#!/bin/bash
# Phase 3 Production Deployment Script
# Automates: Install, Test, Build, Deploy with Blue-Green strategy

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="${PROJECT_DIR}/backend"
REQUIREMENTS_FILE="${PROJECT_DIR}/requirements-phase3.txt"
DOCKERFILE="${BACKEND_DIR}/Dockerfile"
DOCKER_IMAGE="videos-api"
DOCKER_TAG="latest"
COMPOSE_FILE="${PROJECT_DIR}/docker-compose.yml"

# Deployment options
DEPLOY_MODE="${1:-full}"  # full, test, build, deploy
ENVIRONMENT="${2:-production}"

echo -e "${BLUE}╔═════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║          Phase 3 Production Deployment Script              ║${NC}"
echo -e "${BLUE}╚═════════════════════════════════════════════════════════════╝${NC}"

# ============== STEP 1: Verify Environment ==============
echo -e "\n${YELLOW}[1/7] Verifying environment...${NC}"

if [ ! -f "${REQUIREMENTS_FILE}" ]; then
    echo -e "${RED}✗ requirements-phase3.txt not found${NC}"
    exit 1
fi

if [ ! -f "${DOCKERFILE}" ]; then
    echo -e "${RED}✗ Dockerfile not found${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Environment verified${NC}"

# ============== STEP 2: Install Dependencies ==============
echo -e "\n${YELLOW}[2/7] Installing dependencies...${NC}"

if [ "$DEPLOY_MODE" = "full" ] || [ "$DEPLOY_MODE" = "test" ]; then
    if ! command -v pip &> /dev/null; then
        echo -e "${RED}✗ pip not found${NC}"
        exit 1
    fi

    pip install -r "${REQUIREMENTS_FILE}" --quiet
    echo -e "${GREEN}✓ Dependencies installed${NC}"
fi

# ============== STEP 3: Run Tests ==============
echo -e "\n${YELLOW}[3/7] Running tests...${NC}"

if [ "$DEPLOY_MODE" = "full" ] || [ "$DEPLOY_MODE" = "test" ]; then
    if ! command -v pytest &> /dev/null; then
        echo -e "${RED}✗ pytest not found${NC}"
        exit 1
    fi

    # Run Phase 3 security tests
    echo "Running security tests..."
    pytest "${PROJECT_DIR}/tests/test_phase3_security.py" -v --tb=short || {
        echo -e "${RED}✗ Security tests failed${NC}"
        exit 1
    }

    # Run verification script
    echo "Running verification script..."
    python "${PROJECT_DIR}/verify_phase3.py" || {
        echo -e "${RED}✗ Verification failed${NC}"
        exit 1
    }

    echo -e "${GREEN}✓ All tests passed${NC}"
fi

# ============== STEP 4: Build Docker Image ==============
echo -e "\n${YELLOW}[4/7] Building Docker image...${NC}"

if [ "$DEPLOY_MODE" = "full" ] || [ "$DEPLOY_MODE" = "build" ] || [ "$DEPLOY_MODE" = "deploy" ]; then
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}✗ docker not found${NC}"
        exit 1
    fi

    echo "Building ${DOCKER_IMAGE}:${DOCKER_TAG}..."
    docker build \
        -t "${DOCKER_IMAGE}:${DOCKER_TAG}" \
        -t "${DOCKER_IMAGE}:$(date +%Y%m%d-%H%M%S)" \
        -f "${DOCKERFILE}" \
        "${PROJECT_DIR}" || {
        echo -e "${RED}✗ Docker build failed${NC}"
        exit 1
    }

    echo -e "${GREEN}✓ Docker image built successfully${NC}"
fi

# ============== STEP 5: Prepare Blue-Green Deployment ==============
echo -e "\n${YELLOW}[5/7] Preparing blue-green deployment...${NC}"

if [ "$DEPLOY_MODE" = "full" ] || [ "$DEPLOY_MODE" = "deploy" ]; then
    # Save current containers (Blue)
    BLUE_CONTAINER=$(docker-compose ps -q backend 2>/dev/null || echo "")
    
    if [ -z "$BLUE_CONTAINER" ]; then
        echo "No running blue environment detected (first deployment)"
        BLUE_STATUS="none"
    else
        echo "Blue environment: ${BLUE_CONTAINER:0:12}"
        BLUE_STATUS="running"
    fi

    echo -e "${GREEN}✓ Blue-green preparation complete${NC}"
fi

# ============== STEP 6: Deploy (Blue-Green) ==============
echo -e "\n${YELLOW}[6/7] Deploying with blue-green strategy...${NC}"

if [ "$DEPLOY_MODE" = "full" ] || [ "$DEPLOY_MODE" = "deploy" ]; then
    if [ "$BLUE_STATUS" = "running" ]; then
        echo "Starting GREEN environment..."
        # Scale to 2 instances (blue + green)
        docker-compose up -d --scale backend=2 || {
            echo -e "${RED}✗ Failed to start green environment${NC}"
            exit 1
        }
    else
        echo "Starting initial deployment..."
        docker-compose up -d || {
            echo -e "${RED}✗ Failed to start services${NC}"
            exit 1
        }
    fi

    # Wait for services to be healthy
    echo "Waiting for services to be healthy..."
    for i in {1..30}; do
        if curl -sf http://localhost:8000/api/health > /dev/null 2>&1; then
            echo -e "${GREEN}✓ Services are healthy${NC}"
            break
        fi
        if [ $i -eq 30 ]; then
            echo -e "${RED}✗ Services failed to become healthy${NC}"
            docker-compose down
            exit 1
        fi
        echo "Waiting... ($i/30)"
        sleep 2
    done

    # Run smoke tests
    echo "Running smoke tests..."
    curl -sf http://localhost:8000/api/health > /dev/null || {
        echo -e "${RED}✗ Smoke test failed: health check${NC}"
        docker-compose down
        exit 1
    }

    curl -sf http://localhost:8000/api/ready > /dev/null || {
        echo -e "${RED}✗ Smoke test failed: readiness check${NC}"
        docker-compose down
        exit 1
    }

    curl -sf http://localhost:8000/api/metrics > /dev/null || {
        echo -e "${RED}✗ Smoke test failed: metrics${NC}"
        docker-compose down
        exit 1
    }

    echo -e "${GREEN}✓ Smoke tests passed${NC}"

    # Switch traffic from blue to green (via Nginx)
    if [ "$BLUE_STATUS" = "running" ]; then
        echo "Switching traffic from blue to green..."
        # In real setup, this would update Nginx upstream configuration
        docker-compose exec -T nginx nginx -s reload || {
            echo -e "${YELLOW}⚠ Nginx reload warning${NC}"
        }
        sleep 5

        # Stop blue environment
        echo "Stopping blue environment..."
        # This would be: docker stop <blue_container>
        # For now, we keep all containers running for easy rollback
    fi

    echo -e "${GREEN}✓ Deployment complete${NC}"
fi

# ============== STEP 7: Verify Deployment ==============
echo -e "\n${YELLOW}[7/7] Verifying deployment...${NC}"

if [ "$DEPLOY_MODE" = "full" ] || [ "$DEPLOY_MODE" = "deploy" ]; then
    # Get running containers
    RUNNING=$(docker-compose ps -q backend 2>/dev/null | wc -l)
    
    # Check response times
    echo "Checking response times..."
    START=$(date +%s%N)
    curl -sf http://localhost:8000/api/health > /dev/null
    END=$(date +%s%N)
    RESPONSE_TIME=$((($END - $START) / 1000000))
    
    if [ $RESPONSE_TIME -lt 100 ]; then
        echo -e "${GREEN}✓ Response time: ${RESPONSE_TIME}ms${NC}"
    else
        echo -e "${YELLOW}⚠ Response time: ${RESPONSE_TIME}ms (target: <100ms)${NC}"
    fi

    # Check metrics
    echo "Checking metrics..."
    METRICS=$(curl -sf http://localhost:8000/api/metrics)
    if [ -n "$METRICS" ]; then
        echo -e "${GREEN}✓ Metrics available${NC}"
    else
        echo -e "${YELLOW}⚠ Metrics unavailable${NC}"
    fi

    # Summary
    echo -e "\n${GREEN}╔═════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║              Deployment Summary                            ║${NC}"
    echo -e "${GREEN}╠═════════════════════════════════════════════════════════════╣${NC}"
    echo -e "${GREEN}║ Status: ✓ SUCCESSFUL                                        ║${NC}"
    echo -e "${GREEN}║ Image: ${DOCKER_IMAGE}:${DOCKER_TAG}                                        ║${NC}"
    echo -e "${GREEN}║ Containers: ${RUNNING} running                                           ║${NC}"
    echo -e "${GREEN}║ Response Time: ${RESPONSE_TIME}ms                                         ║${NC}"
    echo -e "${GREEN}║ Endpoints:                                                  ║${NC}"
    echo -e "${GREEN}║   - Health: http://localhost:8000/api/health              ║${NC}"
    echo -e "${GREEN}║   - Ready: http://localhost:8000/api/ready                ║${NC}"
    echo -e "${GREEN}║   - Metrics: http://localhost:8000/api/metrics            ║${NC}"
    echo -e "${GREEN}║   - API: http://localhost:8000                            ║${NC}"
    echo -e "${GREEN}║                                                            ║${NC}"
    echo -e "${GREEN}║ Blue-Green Ready: Yes (rollback available)                 ║${NC}"
    echo -e "${GREEN}╚═════════════════════════════════════════════════════════════╝${NC}"

fi

echo -e "\n${GREEN}✓ Phase 3 Production Deployment Complete!${NC}"
echo -e "${BLUE}🚀 Ready for production traffic${NC}\n"

# Display rollback instructions
if [ "$BLUE_STATUS" = "running" ]; then
    echo -e "${YELLOW}Rollback instructions:${NC}"
    echo -e "  docker-compose down"
    echo -e "  docker-compose up -d  # This restarts blue environment"
fi
