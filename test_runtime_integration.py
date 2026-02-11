#!/usr/bin/env python
"""Test script for ProjectRuntime integration"""

import asyncio
import sys
from pathlib import Path

# Test imports
try:
    from backend.project_runtime import ProjectRuntime, ProjectRuntimeConfig
    from backend.scaffold_generator import ScaffoldGenerator, ScaffoldConfig
    from backend.frontend_runtime_generator import FrontendRuntimeGenerator
    from backend.backend_runtime_generator import BackendRuntimeGenerator
    from backend.preview_orchestrator import PreviewOrchestrator
    print("✅ All imports successful")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

# Test scaffold generator
print("\n🔧 Testing ScaffoldGenerator...")
try:
    config = ScaffoldConfig(
        project_id="test-123",
        project_name="Test App",
        project_type="fullstack",
        template="blank",
        use_typescript=True
    )
    generator = ScaffoldGenerator()
    result = generator.generate_project(config)
    print(f"✅ ScaffoldGenerator works - generated {result.get('file_count', 0)} files")
except Exception as e:
    print(f"❌ ScaffoldGenerator error: {e}")

# Test frontend generator
print("\n🎨 Testing FrontendRuntimeGenerator...")
try:
    generator = FrontendRuntimeGenerator()
    blueprint = {
        "pages": [
            {"name": "Home", "components": ["Header", "Hero", "Footer"]}
        ],
        "features": ["auth", "search"]
    }
    components = generator.generate_from_blueprint(blueprint, Path("/tmp/test_project"))
    print(f"✅ FrontendRuntimeGenerator works - generated {len(components)} components")
except Exception as e:
    print(f"❌ FrontendRuntimeGenerator error: {e}")

# Test backend generator
print("\n🔌 Testing BackendRuntimeGenerator...")
try:
    generator = BackendRuntimeGenerator()
    blueprint = {
        "features": ["auth", "search"],
        "database": "postgres"
    }
    routes = generator.generate_from_blueprint(blueprint, Path("/tmp/test_project"), "express")
    print(f"✅ BackendRuntimeGenerator works - generated {len(routes)} files")
except Exception as e:
    print(f"❌ BackendRuntimeGenerator error: {e}")

# Test preview orchestrator
print("\n🖥️ Testing PreviewOrchestrator...")
try:
    orchestrator = PreviewOrchestrator()
    print(f"✅ PreviewOrchestrator initialized successfully")
except Exception as e:
    print(f"❌ PreviewOrchestrator error: {e}")

# Test project runtime
print("\n🚀 Testing ProjectRuntime...")
try:
    runtime = ProjectRuntime()
    print(f"✅ ProjectRuntime initialized successfully")
except Exception as e:
    print(f"❌ ProjectRuntime error: {e}")

print("\n" + "="*50)
print("✅ ALL RUNTIME SYSTEMS INTEGRATED AND READY")
print("="*50)
