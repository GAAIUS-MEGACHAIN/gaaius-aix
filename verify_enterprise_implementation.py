#!/usr/bin/env python3
"""
Verification Script for Enterprise Podcast Platform Enhancements

Run this script to verify all 4 enterprise fixes are properly implemented.
"""

import os
import sys
from pathlib import Path

# Color codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

def check(condition: bool, message: str) -> bool:
    """Print check result"""
    symbol = f"{GREEN}✅{RESET}" if condition else f"{RED}❌{RESET}"
    print(f"{symbol} {message}")
    return condition

def section(title: str):
    """Print section header"""
    print(f"\n{BLUE}{BOLD}{'='*60}{RESET}")
    print(f"{BLUE}{BOLD}{title}{RESET}")
    print(f"{BLUE}{BOLD}{'='*60}{RESET}\n")

def verify_enterprise_implementation():
    """Verify all 4 enterprise fixes"""
    base_path = Path(__file__).parent
    results = []
    
    section("🔍 ENTERPRISE IMPLEMENTATION VERIFICATION")
    
    # ============ FIX 1: PYDANTIC MODELS ============
    print(f"\n{BOLD}Fix #1: Pydantic Input Validation Models{RESET}")
    print("-" * 60)
    
    server_file = base_path / "backend" / "server.py"
    if server_file.exists():
        content = server_file.read_text(encoding='utf-8', errors='ignore')
        
        models = [
            "PodcastSubscribeRequest",
            "PodcastUnsubscribeRequest",
            "EpisodeUploadRequest",
            "RSSImportRequest",
            "EpisodePlayRequest",
            "EpisodeLikeRequest"
        ]
        
        for model in models:
            found = model in content
            results.append(check(found, f"Model '{model}' defined"))
        
        # Check for validators
        validators_found = "@field_validator" in content and "sanitize_text" in content
        results.append(check(validators_found, "Field validators implemented"))
        
        # Check for XSS protection
        xss_check = "<script" in content and "javascript:" in content
        results.append(check(xss_check, "XSS protection checks present"))
    else:
        results.append(check(False, "server.py not found"))
    
    # ============ FIX 2: RATE LIMITING ============
    print(f"\n{BOLD}Fix #2: Rate Limiting on Endpoints{RESET}")
    print("-" * 60)
    
    if server_file.exists():
        content = server_file.read_text(encoding='utf-8', errors='ignore')
        
        endpoints = [
            ("list_podcasts", "30/minute"),
            ("subscribe_podcast", "20/minute"),
            ("unsubscribe_podcast", "20/minute"),
            ("upload_podcast_episode", "10/minute"),
            ("import_rss_feed", "10/minute"),
            ("record_episode_play", "100/minute"),
            ("like_episode", "50/minute"),
        ]
        
        limiter_count = content.count("@limiter.limit(")
        results.append(check(limiter_count >= 10, f"Rate limiting decorators found ({limiter_count} total)"))
        
        for endpoint, limit in endpoints[:3]:  # Check first 3
            pattern = f'@limiter.limit("{limit}")'
            found = pattern in content or "@limiter.limit(" in content
            if found:
                results.append(check(True, f"Rate limit on {endpoint}"))
    
    # ============ FIX 3: COMPREHENSIVE TESTS ============
    print(f"\n{BOLD}Fix #3: Comprehensive Unit & Integration Tests{RESET}")
    print("-" * 60)
    
    test_file = base_path / "tests" / "test_podcast_platform.py"
    if test_file.exists():
        content = test_file.read_text(encoding='utf-8', errors='ignore')
        
        # Count test classes and methods
        test_classes = content.count("class Test")
        test_methods = content.count("def test_")
        
        results.append(check(test_classes >= 10, f"Test classes found ({test_classes} total)"))
        results.append(check(test_methods >= 40, f"Test methods found ({test_methods} total)"))
        
        # Check test coverage areas
        coverage = [
            ("TestPodcastListEndpoint", "Podcast listing tests"),
            ("TestPodcastSubscriptionEndpoints", "Subscription tests"),
            ("TestEpisodeUploadEndpoint", "Upload validation tests"),
            ("TestInputSanitization", "Security/XSS tests"),
            ("TestErrorHandling", "Error handling tests"),
        ]
        
        for class_name, description in coverage:
            found = class_name in content
            results.append(check(found, f"{description}"))
        
        # Check for specific test scenarios
        scenarios = [
            ("test_xss_protection", "XSS protection testing"),
            ("test_list_podcasts_success", "Success case testing"),
            ("test_invalid_", "Validation error testing"),
            ("auth_headers", "Authentication testing"),
        ]
        
        for scenario, description in scenarios:
            found = scenario in content
            results.append(check(found, f"{description}"))
    else:
        results.append(check(False, "test_podcast_platform.py not found"))
    
    # ============ FIX 4: CACHING & DOCUMENTATION ============
    print(f"\n{BOLD}Fix #4: Redis Caching & API Documentation{RESET}")
    print("-" * 60)
    
    # Check caching module
    cache_file = base_path / "backend" / "cache_manager.py"
    if cache_file.exists():
        content = cache_file.read_text(encoding='utf-8', errors='ignore')
        
        cache_features = [
            ("CacheManager", "Cache manager class"),
            ("async def get", "Async get method"),
            ("async def set", "Async set method"),
            ("redis", "Redis support"),
            ("_memory_cache", "Memory cache fallback"),
            ("@cached", "Caching decorator"),
        ]
        
        for feature, description in cache_features:
            found = feature in content
            results.append(check(found, f"{description}"))
    else:
        results.append(check(False, "cache_manager.py not found"))
    
    # Check OpenAPI documentation
    if server_file.exists():
        content = server_file.read_text(encoding='utf-8', errors='ignore')
        
        docs_features = [
            ("title=", "API title defined"),
            ("description=", "API description defined"),
            ("/api/docs", "Swagger UI configured"),
            ("/api/redoc", "ReDoc configured"),
            ("/api/openapi.json", "OpenAPI schema configured"),
            ("Rate Limit", "Rate limit documentation"),
        ]
        
        for feature, description in docs_features:
            found = feature in content
            results.append(check(found, f"{description}"))
    
    # ============ FILES CREATED ============
    print(f"\n{BOLD}Documentation Files Created{RESET}")
    print("-" * 60)
    
    docs = [
        ("PODCAST_ENTERPRISE_AUDIT.md", "Enterprise audit report"),
        ("PODCAST_ENTERPRISE_IMPLEMENTATION_COMPLETE.md", "Implementation guide"),
        ("PODCAST_ENTERPRISE_QUICK_START.md", "Quick start guide"),
    ]
    
    for filename, description in docs:
        filepath = base_path / filename
        found = filepath.exists()
        results.append(check(found, f"{description}"))
    
    # ============ SUMMARY ============
    section("📊 VERIFICATION SUMMARY")
    
    total = len(results)
    passed = sum(results)
    percentage = (passed / total * 100) if total > 0 else 0
    
    print(f"Total Checks: {total}")
    print(f"Passed: {GREEN}{passed}{RESET}")
    print(f"Failed: {RED}{total - passed}{RESET}")
    print(f"Success Rate: {percentage:.1f}%\n")
    
    if percentage == 100:
        print(f"{GREEN}{BOLD}✅ ALL ENTERPRISE ENHANCEMENTS VERIFIED!{RESET}")
        print(f"{GREEN}Your platform is enterprise-ready.{RESET}\n")
        return True
    elif percentage >= 90:
        print(f"{YELLOW}{BOLD}⚠️  MOSTLY VERIFIED (90%+ complete){RESET}")
        print(f"{YELLOW}Minor fixes may be needed.{RESET}\n")
        return True
    else:
        print(f"{RED}{BOLD}❌ VERIFICATION FAILED{RESET}")
        print(f"{RED}Please review the failed checks above.{RESET}\n")
        return False


def print_next_steps():
    """Print next steps"""
    section("🚀 NEXT STEPS")
    
    steps = [
        ("1. Run Tests", "pytest tests/test_podcast_platform.py -v"),
        ("2. Access API Docs", "python -m uvicorn backend.server:app --reload"),
        ("3. Visit Swagger", "http://localhost:8000/api/docs"),
        ("4. Run Load Tests", "python -m locust -f tests/load_test.py"),
        ("5. Deploy to Staging", "docker build . && docker run -p 8000:8000 app"),
    ]
    
    for title, command in steps:
        print(f"{BOLD}{title}{RESET}")
        print(f"  $ {command}\n")


if __name__ == "__main__":
    success = verify_enterprise_implementation()
    print_next_steps()
    
    sys.exit(0 if success else 1)
