"""
PROJECT RUNTIME - Master Orchestrator
Coordinates the 5 critical systems to generate, build, and run full applications
This is the CORE of the GAAIUS AI Builder transformation
"""

import json
import asyncio
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict
import uuid
import logging

try:
    from .scaffold_generator import ScaffoldGenerator, ScaffoldConfig
    from .frontend_runtime_generator import FrontendRuntimeGenerator
    from .backend_runtime_generator import BackendRuntimeGenerator
except ImportError:
    from scaffold_generator import ScaffoldGenerator, ScaffoldConfig
    from frontend_runtime_generator import FrontendRuntimeGenerator
    from backend_runtime_generator import BackendRuntimeGenerator

logger = logging.getLogger(__name__)


@dataclass
class ProjectRuntimeConfig:
    """Configuration for project runtime"""
    project_id: str
    project_name: str
    blueprint: Dict[str, Any]
    project_type: str  # "fullstack", "frontend-only", "backend-only"
    frontend_framework: str = "react"  # "react", "nextjs", "vue"
    backend_framework: str = "express"  # "express", "fastapi"
    use_typescript: bool = True
    database: Optional[str] = None
    styling: str = "tailwind"
    base_path: str = None


class ProjectRuntime:
    """
    Master orchestrator for the GAAIUS Project Runtime System.
    Coordinates 5 critical systems:
    1. Scaffold Generator
    2. Frontend Runtime Generator
    3. Backend Runtime Generator
    4. Preview Orchestrator (coming)
    5. Packaging & Export (coming)
    """
    
    def __init__(self, base_path: str = None):
        """Initialize project runtime"""
        self.base_path = Path(base_path) if base_path else Path.home() / "gaaius_projects"
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        self.scaffold_gen = ScaffoldGenerator(str(self.base_path))
        self.frontend_gen = FrontendRuntimeGenerator()
        self.backend_gen = BackendRuntimeGenerator()
        
        self.active_projects: Dict[str, Dict[str, Any]] = {}
    
    async def generate_project(self, config: ProjectRuntimeConfig) -> Dict[str, Any]:
        """
        Generate a complete, production-ready project
        
        Flow:
        1. Create scaffold (directory structure + config files)
        2. Generate frontend (React/Next components)
        3. Generate backend (Express/FastAPI routes)
        4. Install dependencies
        5. Initialize git
        
        Args:
            config: ProjectRuntimeConfig with all settings
            
        Returns:
            Dict with project info and generation status
        """
        project_path = self.base_path / config.project_id
        project_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"🚀 Starting project generation: {config.project_name}")
        
        generation_steps = []
        
        try:
            # Step 1: Generate scaffold
            logger.info("📁 Step 1/4: Generating project scaffold...")
            scaffold_config = ScaffoldConfig(
                project_id=config.project_id,
                project_name=config.project_name,
                project_type=config.project_type,
                template=config.blueprint.get("template", "blank"),
                use_typescript=config.use_typescript,
                database=config.database,
                styling=config.styling,
            )
            
            scaffold_result = self.scaffold_gen.generate_project(scaffold_config)
            generation_steps.append({
                "step": "scaffold",
                "status": "success",
                "files_created": len(scaffold_result["files"])
            })
            logger.info(f"✅ Scaffold complete: {len(scaffold_result['files'])} files created")
            
            # Step 2: Generate frontend
            if config.project_type in ["fullstack", "frontend-only"]:
                logger.info("⚛️  Step 2/4: Generating React components...")
                frontend_result = self.frontend_gen.generate_from_blueprint(
                    config.blueprint,
                    project_path
                )
                generation_steps.append({
                    "step": "frontend",
                    "status": "success",
                    "files_created": len(frontend_result)
                })
                logger.info(f"✅ Frontend generated: {len(frontend_result)} React components")
            
            # Step 3: Generate backend
            if config.project_type in ["fullstack", "backend-only"]:
                logger.info("🔙 Step 3/4: Generating API backend...")
                backend_result = self.backend_gen.generate_from_blueprint(
                    config.blueprint,
                    project_path / "backend" if config.project_type == "fullstack" else project_path,
                    backend_type=config.backend_framework
                )
                generation_steps.append({
                    "step": "backend",
                    "status": "success",
                    "files_created": len(backend_result)
                })
                logger.info(f"✅ Backend generated: {len(backend_result)} API routes")
            
            # Step 4: Install dependencies
            logger.info("📦 Step 4/4: Installing dependencies...")
            install_result = await self._install_dependencies(project_path, config.project_type)
            generation_steps.append({
                "step": "dependencies",
                "status": "success" if install_result["success"] else "warning",
                "message": install_result.get("message", "Dependencies installed")
            })
            
            # Generate gaaius.json manifest
            manifest = self._create_project_manifest(config, generation_steps)
            manifest_path = project_path / "gaaius_manifest.json"
            manifest_path.write_text(json.dumps(manifest, indent=2))
            
            # Track project
            self.active_projects[config.project_id] = {
                "path": str(project_path),
                "config": asdict(config),
                "created_at": datetime.now().isoformat(),
                "status": "ready"
            }
            
            logger.info(f"🎉 Project generated successfully: {config.project_name}")
            
            return {
                "status": "success",
                "project_id": config.project_id,
                "project_name": config.project_name,
                "path": str(project_path),
                "project_type": config.project_type,
                "generated_at": datetime.now().isoformat(),
                "steps": generation_steps,
                "next_steps": self._get_next_steps(config.project_type)
            }
        
        except Exception as e:
            logger.error(f"❌ Project generation failed: {str(e)}")
            return {
                "status": "error",
                "project_id": config.project_id,
                "error": str(e),
                "steps": generation_steps
            }
    
    async def start_dev_server(self, project_id: str) -> Dict[str, Any]:
        """
        Start development servers for a project
        (Will implement Preview Orchestrator in next system)
        
        For now, returns startup instructions
        """
        if project_id not in self.active_projects:
            return {"status": "error", "message": "Project not found"}
        
        project = self.active_projects[project_id]
        project_path = Path(project["path"])
        config = project["config"]
        project_type = config["project_type"]
        
        logger.info(f"🚀 Starting dev servers for {project_id}")
        
        commands = []
        ports = {}
        
        if project_type in ["fullstack", "frontend-only"]:
            frontend_cmd = "npm run dev" if config["project_type"] != "nextjs" else "npm run dev"
            commands.append({
                "name": "Frontend",
                "command": f"cd {project_path} && npm run dev",
                "port": 5173,
                "cwd": str(project_path)
            })
            ports["frontend"] = 5173
        
        if project_type in ["fullstack", "backend-only"]:
            if config["backend_framework"] == "express":
                commands.append({
                    "name": "Backend (Express)",
                    "command": f"cd {project_path}/backend && npm run dev",
                    "port": 3001,
                    "cwd": str(project_path / "backend")
                })
            else:
                commands.append({
                    "name": "Backend (FastAPI)",
                    "command": f"cd {project_path}/backend && uvicorn main:app --reload --port 3001",
                    "port": 3001,
                    "cwd": str(project_path / "backend")
                })
            ports["backend"] = 3001
        
        return {
            "status": "ready",
            "project_id": project_id,
            "project_path": str(project_path),
            "servers": commands,
            "ports": ports,
            "preview_url": "http://localhost:5173",
            "api_url": "http://localhost:3001"
        }
    
    async def _install_dependencies(self, project_path: Path, project_type: str) -> Dict[str, Any]:
        """Install npm and pip dependencies"""
        try:
            if project_type in ["fullstack", "frontend-only"]:
                logger.info("  Installing npm dependencies (frontend)...")
                result = subprocess.run(
                    ["npm", "install"],
                    cwd=str(project_path),
                    capture_output=True,
                    timeout=300
                )
                if result.returncode != 0:
                    logger.warning(f"  npm install warning: {result.stderr.decode()}")
            
            if project_type in ["fullstack", "backend-only"]:
                backend_path = project_path / "backend" if project_type == "fullstack" else project_path
                
                if (backend_path / "package.json").exists():
                    logger.info("  Installing npm dependencies (backend)...")
                    result = subprocess.run(
                        ["npm", "install"],
                        cwd=str(backend_path),
                        capture_output=True,
                        timeout=300
                    )
                elif (backend_path / "requirements.txt").exists():
                    logger.info("  Installing pip dependencies...")
                    result = subprocess.run(
                        ["pip", "install", "-r", "requirements.txt"],
                        cwd=str(backend_path),
                        capture_output=True,
                        timeout=300
                    )
            
            return {"success": True, "message": "All dependencies installed"}
        
        except subprocess.TimeoutExpired:
            return {"success": False, "message": "Dependency installation timed out"}
        except Exception as e:
            return {"success": False, "message": f"Dependency installation failed: {str(e)}"}
    
    def _create_project_manifest(self, config: ProjectRuntimeConfig, steps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create project manifest file"""
        return {
            "version": "1.0",
            "project_id": config.project_id,
            "project_name": config.project_name,
            "project_type": config.project_type,
            "blueprint": config.blueprint,
            "runtime_config": {
                "frontend_framework": config.frontend_framework,
                "backend_framework": config.backend_framework,
                "use_typescript": config.use_typescript,
                "styling": config.styling,
                "database": config.database,
            },
            "generated_by": "GAAIUS Project Runtime v2.0",
            "generated_at": datetime.now().isoformat(),
            "generation_steps": steps,
            "structure": {
                "frontend": "src/" if config.project_type != "fullstack" else "frontend/src/",
                "backend": "" if config.project_type != "fullstack" else "backend/",
                "shared": "shared/" if config.project_type == "fullstack" else None,
            }
        }
    
    def _get_next_steps(self, project_type: str) -> List[str]:
        """Get next steps after project generation"""
        steps = [
            "Review generated files in your IDE",
            "Read README.md in project root",
            "Start development servers:",
        ]
        
        if project_type in ["fullstack", "frontend-only"]:
            steps.append("  - Frontend: npm run dev (port 5173)")
        
        if project_type in ["fullstack", "backend-only"]:
            steps.append("  - Backend: npm run dev OR uvicorn main:app --reload (port 3001)")
        
        steps.extend([
            "Navigate to http://localhost:5173 in your browser",
            "Edit files in src/ and watch hot reload",
            "Deploy when ready with: npm run build",
        ])
        
        return steps
    
    def get_project_info(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a generated project"""
        if project_id in self.active_projects:
            return self.active_projects[project_id]
        return None
    
    def list_projects(self) -> List[Dict[str, Any]]:
        """List all active projects"""
        return list(self.active_projects.values())


# ===== USAGE EXAMPLE =====

async def example_usage():
    """Example of how to use the Project Runtime"""
    
    # Create runtime
    runtime = ProjectRuntime()
    
    # Create a fullstack project config
    blueprint = {
        "app_type": "saas_dashboard",
        "template": "saas_dashboard",
        "pages": [
            {"name": "Dashboard", "components": ["StatsGrid", "Chart"]},
            {"name": "Users", "components": ["UserTable"]},
            {"name": "Settings", "components": ["SettingsForm"]},
        ],
        "features": ["auth", "search", "notifications", "export_data"],
        "layout": {
            "type": "sidebar",
            "nav_items": ["Dashboard", "Users", "Settings"]
        }
    }
    
    config = ProjectRuntimeConfig(
        project_id=str(uuid.uuid4())[:8],
        project_name="My SaaS Dashboard",
        blueprint=blueprint,
        project_type="fullstack",
        frontend_framework="react",
        backend_framework="express",
        use_typescript=True,
        database="postgres",
        styling="tailwind"
    )
    
    # Generate project
    result = await runtime.generate_project(config)
    print(json.dumps(result, indent=2))
    
    # Get startup info
    startup = await runtime.start_dev_server(config.project_id)
    print("\n" + "="*50)
    print("READY TO START DEV SERVERS:")
    print("="*50)
    for server in startup["servers"]:
        print(f"\n{server['name']}:")
        print(f"  Command: {server['command']}")
        print(f"  Port: {server['port']}")


if __name__ == "__main__":
    # Run example
    asyncio.run(example_usage())
