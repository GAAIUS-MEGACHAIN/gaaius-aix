#!/usr/bin/env bash

# PHASE 3: Blue-Green Deployment Script
# Zero-downtime deployment with automatic rollback

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DOCKER_IMAGE="videos-api"
DOCKER_TAG="latest"
BLUE_CONTAINER="videos-api-blue"
GREEN_CONTAINER="videos-api-green"
HEALTH_CHECK_ENDPOINT="http://localhost:8000/api/health"
MAX_WAIT_TIME=300 # 5 minutes
CURRENT_ENVIRONMENT=""

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Get current active environment
get_current_environment() {
    log_info "Checking current active environment..."
    
    # Check which container is currently serving traffic
    if docker ps | grep -q "$BLUE_CONTAINER"; then
        CURRENT_ENVIRONMENT="blue"
        log_info "Current environment: BLUE"
    elif docker ps | grep -q "$GREEN_CONTAINER"; then
        CURRENT_ENVIRONMENT="green"
        log_info "Current environment: GREEN"
    else
        log_error "No active environment found!"
        exit 1
    fi
}

# Health check function
health_check() {
    local container=$1
    local port=$2
    local endpoint="http://localhost:$port/api/health"
    local wait_time=0
    
    log_info "Waiting for $container to be healthy..."
    
    while [ $wait_time -lt $MAX_WAIT_TIME ]; do
        if docker exec $container curl -f -s $endpoint > /dev/null 2>&1; then
            log_success "$container is healthy!"
            return 0
        fi
        
        wait_time=$((wait_time + 5))
        echo -ne "Waiting... ${wait_time}s\r"
        sleep 5
    done
    
    log_error "$container failed health check after ${MAX_WAIT_TIME}s"
    return 1
}

# Deploy to new environment
deploy_new_environment() {
    local new_env=$1
    local new_container=$2
    local new_port=$3
    
    log_info "Deploying to $new_env environment..."
    
    # Stop existing container if running
    if docker ps -a | grep -q "$new_container"; then
        log_warning "Stopping existing $new_container..."
        docker stop "$new_container" 2>/dev/null || true
        docker rm "$new_container" 2>/dev/null || true
    fi
    
    # Start new container
    log_info "Starting $new_container on port $new_port..."
    docker run -d \
        --name "$new_container" \
        -p "$new_port:8000" \
        -e MONGODB_URI="${MONGODB_URI}" \
        -e REDIS_HOST="${REDIS_HOST}" \
        -e JWT_SECRET="${JWT_SECRET}" \
        --health-cmd="curl -f http://localhost:8000/api/health || exit 1" \
        --health-interval=10s \
        --health-timeout=5s \
        --health-retries=3 \
        "$DOCKER_IMAGE:$DOCKER_TAG"
    
    # Wait for health check
    if health_check "$new_container" "$new_port"; then
        log_success "$new_env environment is ready!"
        return 0
    else
        log_error "$new_env environment failed health check"
        docker stop "$new_container" 2>/dev/null || true
        return 1
    fi
}

# Switch traffic using Nginx
switch_traffic() {
    local target_env=$1
    local target_port=$2
    
    log_info "Switching traffic to $target_env environment (port $target_port)..."
    
    # Update Nginx upstream configuration
    sed -i "s/listen 8001;/listen $target_port;/" /etc/nginx/conf.d/upstream.conf
    
    # Test Nginx configuration
    if ! nginx -t > /dev/null 2>&1; then
        log_error "Nginx configuration test failed!"
        return 1
    fi
    
    # Reload Nginx with zero-downtime
    nginx -s reload
    
    log_success "Traffic switched to $target_env environment"
    return 0
}

# Run smoke tests on new environment
run_smoke_tests() {
    local port=$1
    
    log_info "Running smoke tests on port $port..."
    
    # Test health endpoint
    if ! curl -f -s "http://localhost:$port/api/health" > /dev/null; then
        log_error "Health endpoint test failed"
        return 1
    fi
    
    # Test ready endpoint
    if ! curl -f -s "http://localhost:$port/api/ready" > /dev/null; then
        log_error "Ready endpoint test failed"
        return 1
    fi
    
    # Test metrics endpoint
    if ! curl -f -s "http://localhost:$port/api/metrics" > /dev/null; then
        log_error "Metrics endpoint test failed"
        return 1
    fi
    
    # Run pytest on critical endpoints
    log_info "Running pytest on critical endpoints..."
    python -m pytest tests/test_phase3_security.py::TestVideoEndpoints -v --tb=short
    
    if [ $? -ne 0 ]; then
        log_error "Pytest failed"
        return 1
    fi
    
    log_success "Smoke tests passed!"
    return 0
}

# Rollback function
rollback() {
    local target_env=$1
    local target_port=$2
    local current_env=$3
    local current_port=$4
    
    log_warning "Rolling back to $current_env environment..."
    
    if switch_traffic "$current_env" "$current_port"; then
        log_success "Rollback successful"
        return 0
    else
        log_error "Rollback failed - manual intervention required!"
        return 1
    fi
}

# Main deployment function
main() {
    log_info "Starting blue-green deployment..."
    log_info "=================================="
    
    # Get current environment
    get_current_environment
    
    # Determine new environment
    if [ "$CURRENT_ENVIRONMENT" == "blue" ]; then
        NEW_ENV="green"
        NEW_CONTAINER=$GREEN_CONTAINER
        NEW_PORT=8001
        CURRENT_PORT=8000
    else
        NEW_ENV="blue"
        NEW_CONTAINER=$BLUE_CONTAINER
        NEW_PORT=8000
        CURRENT_PORT=8001
    fi
    
    log_info "Deploying to: $NEW_ENV"
    log_info "Current environment: $CURRENT_ENVIRONMENT"
    
    # Build new Docker image
    log_info "Building Docker image..."
    docker build -t "$DOCKER_IMAGE:$DOCKER_TAG" -f backend/Dockerfile .
    
    if [ $? -ne 0 ]; then
        log_error "Docker build failed"
        exit 1
    fi
    
    log_success "Docker image built successfully"
    
    # Deploy to new environment
    if ! deploy_new_environment "$NEW_ENV" "$NEW_CONTAINER" "$NEW_PORT"; then
        log_error "Deployment to $NEW_ENV failed"
        exit 1
    fi
    
    # Run smoke tests
    if ! run_smoke_tests "$NEW_PORT"; then
        log_error "Smoke tests failed"
        log_warning "Rolling back..."
        exit 1
    fi
    
    # Switch traffic
    if ! switch_traffic "$NEW_ENV" "$NEW_PORT"; then
        log_error "Traffic switch failed"
        log_warning "Rolling back..."
        rollback "$CURRENT_ENVIRONMENT" "$CURRENT_PORT" "$NEW_ENV" "$NEW_PORT"
        exit 1
    fi
    
    # Wait for new environment to stabilize
    log_info "Waiting for $NEW_ENV environment to stabilize (30s)..."
    sleep 30
    
    # Final health check
    log_info "Running final health check..."
    if ! health_check "$NEW_CONTAINER" "$NEW_PORT"; then
        log_error "Final health check failed"
        rollback "$CURRENT_ENVIRONMENT" "$CURRENT_PORT" "$NEW_ENV" "$NEW_PORT"
        exit 1
    fi
    
    # Clean up old container
    log_info "Cleaning up old $CURRENT_ENVIRONMENT container..."
    docker stop "videos-api-${CURRENT_ENVIRONMENT}" 2>/dev/null || true
    docker rm "videos-api-${CURRENT_ENVIRONMENT}" 2>/dev/null || true
    
    log_success "=================================="
    log_success "Deployment completed successfully!"
    log_success "Active environment: $NEW_ENV"
    log_success "=================================="
    
    # Log deployment
    echo "{
  \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",
  \"deployment\": \"blue-green\",
  \"from_environment\": \"$CURRENT_ENVIRONMENT\",
  \"to_environment\": \"$NEW_ENV\",
  \"docker_image\": \"$DOCKER_IMAGE:$DOCKER_TAG\",
  \"status\": \"success\"
}" >> deployments.log
}

# Error handling
trap 'log_error "Deployment failed!"; exit 1' ERR

# Run main function
main "$@"
