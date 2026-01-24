#!/usr/bin/env python3
"""
PHASE 3: Final Verification & Checklist
Verify all Phase 3 components are in place
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Colors
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'


class Phase3Verifier:
    """Verify Phase 3 implementation completeness"""
    
    def __init__(self):
        self.checks = []
        self.passed = 0
        self.failed = 0
        self.root = Path('.')
    
    def check(self, condition, message):
        """Record a check result"""
        if condition:
            self.checks.append((True, message))
            self.passed += 1
            print(f"{GREEN}✅{NC} {message}")
        else:
            self.checks.append((False, message))
            self.failed += 1
            print(f"{RED}❌{NC} {message}")
    
    def verify_files(self):
        """Verify all Phase 3 files exist"""
        print(f"\n{BLUE}📦 VERIFYING FILES{NC}")
        print("=" * 60)
        
        files = {
            'Security': [
                'backend/security.py',
            ],
            'Caching': [
                'backend/caching.py',
            ],
            'Database': [
                'backend/db_optimization.py',
            ],
            'Monitoring': [
                'backend/health_checks.py',
                'backend/rate_limiting.py',
                'backend/monitoring.py',
            ],
            'Tests': [
                'tests/test_phase3_security.py',
                'tests/load_test.py',
            ],
            'Infrastructure': [
                'Dockerfile',
                'nginx.conf',
                'deploy_bluegreen.sh',
            ],
            'Configuration': [
                'requirements-phase3.txt',
            ],
            'Documentation': [
                'PHASE3_INTEGRATION.md',
                'PHASE3_CODE_DELIVERY.md',
                'PHASE3_STATUS.py',
                'PHASE3_COMPLETE_FINAL.md',
            ]
        }
        
        for category, file_list in files.items():
            print(f"\n{category}:")
            for file_path in file_list:
                exists = (self.root / file_path).exists()
                self.check(exists, f"  {file_path}")
    
    def verify_code_quality(self):
        """Verify code quality metrics"""
        print(f"\n{BLUE}🔍 CODE QUALITY{NC}")
        print("=" * 60)
        
        # Check security.py has required classes
        try:
            security_file = self.root / 'backend/security.py'
            content = security_file.read_text()
            
            self.check('sanitize_string' in content, "  sanitize_string function exists")
            self.check('validate_email' in content, "  validate_email function exists")
            self.check('ValidationError' in content, "  ValidationError class exists")
            self.check('get_security_headers' in content, "  get_security_headers function exists")
        except:
            self.check(False, "  Could not read security.py")
        
        # Check caching.py has required classes
        try:
            caching_file = self.root / 'backend/caching.py'
            content = caching_file.read_text()
            
            self.check('CacheManager' in content, "  CacheManager class exists")
            self.check('cache_route' in content, "  cache_route decorator exists")
            self.check('VideoCacheService' in content, "  VideoCacheService class exists")
        except:
            self.check(False, "  Could not read caching.py")
        
        # Check db_optimization.py has required classes
        try:
            db_file = self.root / 'backend/db_optimization.py'
            content = db_file.read_text()
            
            self.check('DatabasePool' in content, "  DatabasePool class exists")
            self.check('IndexManager' in content, "  IndexManager class exists")
            self.check('QueryOptimizer' in content, "  QueryOptimizer class exists")
        except:
            self.check(False, "  Could not read db_optimization.py")
    
    def verify_tests(self):
        """Verify test files have required test cases"""
        print(f"\n{BLUE}🧪 TESTS{NC}")
        print("=" * 60)
        
        try:
            test_file = self.root / 'tests/test_phase3_security.py'
            content = test_file.read_text()
            
            self.check('TestSecurityValidation' in content, "  Security validation tests")
            self.check('test_xss_injection_prevention' in content, "  XSS injection test")
            self.check('test_sql_injection_prevention' in content, "  SQL injection test")
            self.check('TestAuthenticationSecurity' in content, "  Auth security tests")
            self.check('TestVideoEndpoints' in content, "  Video endpoint tests")
        except:
            self.check(False, "  Could not read test_phase3_security.py")
        
        # Check load test
        try:
            load_test = self.root / 'tests/load_test.py'
            content = load_test.read_text()
            
            self.check('VideoLoadTasks' in content, "  Video load test tasks")
            self.check('ChatLoadTasks' in content, "  Chat load test tasks")
            self.check('HealthCheckTasks' in content, "  Health check load test tasks")
        except:
            self.check(False, "  Could not read load_test.py")
    
    def verify_docker(self):
        """Verify Docker configuration"""
        print(f"\n{BLUE}🐳 DOCKER{NC}")
        print("=" * 60)
        
        try:
            dockerfile = self.root / 'Dockerfile'
            content = dockerfile.read_text()
            
            self.check('FROM python:3.11-slim' in content, "  Python 3.11-slim base image")
            self.check('HEALTHCHECK' in content, "  Health check configured")
            self.check('USER appuser' in content, "  Non-root user configured")
            self.check('EXPOSE 8000' in content, "  Port 8000 exposed")
        except:
            self.check(False, "  Could not read Dockerfile")
    
    def verify_nginx(self):
        """Verify Nginx configuration"""
        print(f"\n{BLUE}🌐 NGINX{NC}")
        print("=" * 60)
        
        try:
            nginx_file = self.root / 'nginx.conf'
            content = nginx_file.read_text()
            
            self.check('upstream backend' in content, "  Upstream backend configured")
            self.check('ssl_certificate' in content, "  SSL certificates configured")
            self.check('gzip on' in content, "  Gzip compression enabled")
            self.check('proxy_cache_path' in content, "  Caching configured")
            self.check('limit_req_zone' in content, "  Rate limiting configured")
        except:
            self.check(False, "  Could not read nginx.conf")
    
    def verify_deployment(self):
        """Verify deployment script"""
        print(f"\n{BLUE}🚀 DEPLOYMENT{NC}")
        print("=" * 60)
        
        try:
            deploy_script = self.root / 'deploy_bluegreen.sh'
            content = deploy_script.read_text()
            
            self.check('blue-green' in content.lower(), "  Blue-green deployment")
            self.check('health_check' in content, "  Health checks")
            self.check('smoke_tests' in content, "  Smoke tests")
            self.check('rollback' in content, "  Rollback procedure")
        except:
            self.check(False, "  Could not read deploy_bluegreen.sh")
    
    def verify_endpoints(self):
        """Verify Phase 3 endpoints"""
        print(f"\n{BLUE}📍 ENDPOINTS{NC}")
        print("=" * 60)
        
        # These endpoints should be implemented
        endpoints = [
            '/api/health',
            '/api/ready',
            '/api/metrics',
            '/api/version',
        ]
        
        for endpoint in endpoints:
            print(f"  {endpoint}")
            # These will be checked when server is running
        
        print("  (Verify endpoints by running: curl http://localhost:8000/api/health)")
    
    def verify_dependencies(self):
        """Verify all dependencies are listed"""
        print(f"\n{BLUE}📦 DEPENDENCIES{NC}")
        print("=" * 60)
        
        try:
            req_file = self.root / 'requirements-phase3.txt'
            content = req_file.read_text()
            
            dependencies = [
                'fastapi',
                'uvicorn',
                'motor',
                'pymongo',
                'redis',
                'pytest',
                'locust',
                'slowapi',
                'python-json-logger',
                'psutil',
            ]
            
            for dep in dependencies:
                self.check(dep in content, f"  {dep} listed")
        except:
            self.check(False, "  Could not read requirements-phase3.txt")
    
    def print_summary(self):
        """Print final summary"""
        print(f"\n{BLUE}{'=' * 60}{NC}")
        print(f"{BLUE}PHASE 3 VERIFICATION SUMMARY{NC}")
        print(f"{BLUE}{'=' * 60}{NC}")
        print(f"\n{GREEN}✅ PASSED: {self.passed}{NC}")
        print(f"{RED}❌ FAILED: {self.failed}{NC}")
        
        total = self.passed + self.failed
        percentage = (self.passed / total * 100) if total > 0 else 0
        
        print(f"\n{BLUE}Completion: {percentage:.0f}%{NC}")
        
        if self.failed == 0:
            print(f"\n{GREEN}🎉 PHASE 3 IMPLEMENTATION COMPLETE!{NC}")
            return 0
        else:
            print(f"\n{YELLOW}⚠️  {self.failed} items need attention{NC}")
            return 1
    
    def run_all_checks(self):
        """Run all verification checks"""
        print(f"\n{BLUE}{'=' * 60}{NC}")
        print(f"{BLUE}PHASE 3 IMPLEMENTATION VERIFICATION{NC}")
        print(f"{BLUE}Started: {datetime.now().isoformat()}{NC}")
        print(f"{BLUE}{'=' * 60}{NC}")
        
        self.verify_files()
        self.verify_code_quality()
        self.verify_tests()
        self.verify_docker()
        self.verify_nginx()
        self.verify_deployment()
        self.verify_endpoints()
        self.verify_dependencies()
        
        return self.print_summary()


if __name__ == '__main__':
    verifier = Phase3Verifier()
    exit_code = verifier.run_all_checks()
    sys.exit(exit_code)
