"""
GAAIUS AI - File Generator System
Converts agent outputs into actual project files and directory structure
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime


class FileGenerator:
    """Generates project files from agent outputs"""
    
    def __init__(self, project_name: str, output_dir: str = "./generated_projects"):
        """
        Initialize file generator
        
        Args:
            project_name: Name of the project
            output_dir: Base directory for generated projects
        """
        self.project_name = project_name
        self.output_dir = Path(output_dir) / project_name
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.generated_files = []
    
    def generate_from_orchestrator_output(
        self,
        orchestrator_outputs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate all files from orchestrator outputs
        
        Args:
            orchestrator_outputs: Dictionary with outputs from all agents
        
        Returns:
            Dictionary with file generation results
        """
        results = {
            "project_name": self.project_name,
            "output_dir": str(self.output_dir),
            "timestamp": datetime.now().isoformat(),
            "files_generated": 0,
            "files_failed": 0,
            "generated_files": [],
            "errors": []
        }
        
        # 1. Create base structure
        print("\n📁 Creating project structure...")
        self._create_project_structure(orchestrator_outputs)
        
        # 2. Generate frontend files (from frontend_engineer output)
        if "frontend_engineer" in orchestrator_outputs:
            print("⚡ Generating frontend files...")
            self._generate_frontend_files(
                orchestrator_outputs["frontend_engineer"]
            )
        
        # 3. Generate backend files (from backend_engineer output)
        if "backend_engineer" in orchestrator_outputs:
            print("🔧 Generating backend files...")
            self._generate_backend_files(
                orchestrator_outputs["backend_engineer"]
            )
        
        # 4. Generate database files (from database_architect output)
        if "database_architect" in orchestrator_outputs:
            print("💾 Generating database files...")
            self._generate_database_files(
                orchestrator_outputs["database_architect"]
            )
        
        # 5. Generate DevOps files (from devops_engineer output)
        if "devops_engineer" in orchestrator_outputs:
            print("🚀 Generating deployment files...")
            self._generate_devops_files(
                orchestrator_outputs["devops_engineer"]
            )
        
        # 6. Generate config and documentation
        print("📚 Generating documentation...")
        self._generate_documentation(orchestrator_outputs)
        
        results["files_generated"] = len(self.generated_files)
        results["generated_files"] = self.generated_files
        
        return results
    
    def _create_project_structure(self, outputs: Dict[str, Any]) -> None:
        """Create base directory structure"""
        dirs = [
            "frontend/src/components",
            "frontend/src/pages",
            "frontend/src/hooks",
            "frontend/src/services",
            "frontend/src/types",
            "frontend/src/store",
            "frontend/src/styles",
            "frontend/public",
            "backend/src/routes",
            "backend/src/controllers",
            "backend/src/services",
            "backend/src/models",
            "backend/src/middleware",
            "backend/src/lib",
            "backend/src/types",
            "backend/src/config",
            "backend/prisma",
            "backend/tests",
            ".github/workflows",
            "docs"
        ]
        
        for dir_path in dirs:
            full_path = self.output_dir / dir_path
            full_path.mkdir(parents=True, exist_ok=True)
    
    def _generate_frontend_files(self, frontend_output: Any) -> None:
        """Generate frontend code files"""
        if isinstance(frontend_output, dict) and "code" in frontend_output:
            code = frontend_output["code"]
        else:
            code = str(frontend_output)
        
        # Parse FILE: blocks
        files = self._parse_file_blocks(code)
        
        for file_path, file_content in files.items():
            # Ensure frontend/* paths
            if not file_path.startswith("frontend/"):
                file_path = f"frontend/{file_path}"
            
            self._write_file(file_path, file_content)
    
    def _generate_backend_files(self, backend_output: Any) -> None:
        """Generate backend code files"""
        if isinstance(backend_output, dict) and "code" in backend_output:
            code = backend_output["code"]
        else:
            code = str(backend_output)
        
        # Parse FILE: blocks
        files = self._parse_file_blocks(code)
        
        for file_path, file_content in files.items():
            # Ensure backend/src/* paths
            if not file_path.startswith("backend/"):
                file_path = f"backend/{file_path}"
            if "backend/src" not in file_path and "backend/prisma" not in file_path:
                file_path = file_path.replace("backend/", "backend/src/")
            
            self._write_file(file_path, file_content)
    
    def _generate_database_files(self, db_output: Any) -> None:
        """Generate database schema and migrations"""
        # Parse FILE: blocks from architect output
        if isinstance(db_output, dict):
            code = db_output.get("code", json.dumps(db_output, indent=2))
        else:
            code = str(db_output)
        
        files = self._parse_file_blocks(code)
        
        for file_path, file_content in files.items():
            # Route to prisma/ or migrations/
            if "schema" in file_path.lower():
                file_path = f"backend/prisma/{file_path.split('/')[-1]}"
            elif "migration" in file_path.lower() or ".sql" in file_path:
                file_path = f"backend/prisma/migrations/{file_path.split('/')[-1]}"
            elif not file_path.startswith("backend/"):
                file_path = f"backend/prisma/{file_path}"
            
            self._write_file(file_path, file_content)
    
    def _generate_devops_files(self, devops_output: Any) -> None:
        """Generate Docker, docker-compose, and CI/CD files"""
        if isinstance(devops_output, dict) and "code" in devops_output:
            code = devops_output["code"]
        else:
            code = str(devops_output)
        
        files = self._parse_file_blocks(code)
        
        for file_path, file_content in files.items():
            # Route to correct locations
            if "docker-compose" in file_path.lower():
                file_path = "docker-compose.yml"
            elif "dockerfile" in file_path.lower() or "dockerfile" == file_path.lower():
                file_path = file_path  # Keep as is
            elif "workflow" in file_path.lower() or ".github" in file_path:
                if not file_path.startswith(".github"):
                    file_path = f".github/workflows/{file_path.split('/')[-1]}"
            elif ".env" in file_path.lower():
                file_path = ".env.example"
            else:
                file_path = f"devops/{file_path}"
            
            self._write_file(file_path, file_content)
    
    def _generate_documentation(self, outputs: Dict[str, Any]) -> None:
        """Generate documentation files"""
        # README.md
        readme = self._generate_readme(outputs)
        self._write_file("README.md", readme)
        
        # Project spec document
        if "product_manager" in outputs:
            spec = outputs["product_manager"]
            if isinstance(spec, dict):
                spec_text = f"""# Project Specification

Generated: {datetime.now().isoformat()}

## Overview

{json.dumps(spec, indent=2)}
"""
                self._write_file("docs/PROJECT_SPEC.md", spec_text)
        
        # Design system document
        if "ui_designer" in outputs:
            design = outputs["ui_designer"]
            if isinstance(design, dict):
                design_text = f"""# Design System

Generated: {datetime.now().isoformat()}

## Design Specifications

{json.dumps(design, indent=2)}
"""
                self._write_file("docs/DESIGN_SYSTEM.md", design_text)
    
    def _generate_readme(self, outputs: Dict[str, Any]) -> str:
        """Generate project README"""
        project_name = self.project_name
        
        # Extract project description from product manager output
        description = ""
        if "product_manager" in outputs:
            spec = outputs["product_manager"]
            if isinstance(spec, dict):
                description = spec.get("description", "")
                if not description and "name" in spec:
                    project_name = spec["name"]
        
        readme = f"""# {project_name}

{description}

## Getting Started

### Prerequisites
- Node.js 18+ 
- npm or yarn
- Docker (for deployment)

### Installation

\`\`\`bash
# Frontend
cd frontend
npm install
npm start

# Backend (in separate terminal)
cd backend
npm install
npm run dev
\`\`\`

### Environment Variables

Copy `.env.example` to `.env` and fill in your values:

\`\`\`bash
cp .env.example .env
\`\`\`

## Project Structure

### Frontend
- \`src/components/\` - React components
- \`src/pages/\` - Page components
- \`src/hooks/\` - Custom React hooks
- \`src/services/\` - API client
- \`src/types/\` - TypeScript types
- \`src/store/\` - State management

### Backend
- \`src/routes/\` - API routes
- \`src/controllers/\` - Request handlers
- \`src/services/\` - Business logic
- \`src/models/\` - Database models
- \`src/middleware/\` - Middleware
- \`prisma/\` - Database schema

## Development

### Frontend Development
\`\`\`bash
cd frontend
npm start
\`\`\`

### Backend Development
\`\`\`bash
cd backend
npm run dev
\`\`\`

### Database
\`\`\`bash
cd backend
npx prisma migrate dev
npx prisma studio
\`\`\`

## Deployment

### Using Docker
\`\`\`bash
docker-compose up -d
\`\`\`

### Using GitHub Actions
Push to main branch to trigger CI/CD pipeline.

## Testing

### Frontend Tests
\`\`\`bash
cd frontend
npm test
\`\`\`

### Backend Tests
\`\`\`bash
cd backend
npm test
\`\`\`

## API Documentation

See \`docs/API.md\` for complete API documentation.

## Contributing

1. Create a feature branch
2. Commit your changes
3. Push to the branch
4. Open a Pull Request

## License

MIT

## Generated

This project was generated by GAAIUS AI on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Learn more: https://github.com/gaaius/gaaius-ai
"""
        return readme
    
    def _parse_file_blocks(self, content: str) -> Dict[str, str]:
        """Parse FILE: blocks from code content"""
        files = {}
        
        # Split by FILE: markers
        parts = content.split("FILE:")
        
        for part in parts[1:]:  # Skip the first part (before first FILE:)
            lines = part.strip().split("\n")
            if not lines:
                continue
            
            # First line is the file path
            file_path = lines[0].strip()
            
            # Rest is the content, remove code block markers if present
            file_content = "\n".join(lines[1:]).strip()
            
            # Remove markdown code block markers
            if file_content.startswith("```"):
                # Remove opening ```
                file_content = "\n".join(file_content.split("\n")[1:])
            if file_content.endswith("```"):
                # Remove closing ```
                file_content = "\n".join(file_content.split("\n")[:-1])
            
            file_content = file_content.strip()
            
            if file_path and file_content:
                files[file_path] = file_content
        
        return files
    
    def _write_file(self, relative_path: str, content: str) -> None:
        """Write file to disk"""
        try:
            file_path = self.output_dir / relative_path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_path.write_text(content, encoding="utf-8")
            
            self.generated_files.append(str(relative_path))
            print(f"  ✅ {relative_path}")
        
        except Exception as e:
            print(f"  ❌ {relative_path}: {str(e)}")
            self.generated_files.append(f"{relative_path} (ERROR)")
    
    def generate_summary(self) -> str:
        """Generate project generation summary"""
        summary = f"""
================================================================================
                    PROJECT GENERATION SUMMARY
================================================================================

Project Name: {self.project_name}
Output Directory: {self.output_dir}
Total Files Generated: {len(self.generated_files)}
Timestamp: {datetime.now().isoformat()}

Generated Files:
{chr(10).join(f"  - {f}" for f in self.generated_files)}

Next Steps:
1. Review the generated files in {self.output_dir}
2. Install dependencies:
   - cd frontend && npm install
   - cd backend && npm install
3. Configure environment variables (.env files)
4. Setup database: cd backend && npx prisma migrate dev
5. Start development:
   - Frontend: cd frontend && npm start
   - Backend: cd backend && npm run dev

================================================================================
"""
        return summary


async def generate_project_files(
    project_name: str,
    orchestrator_outputs: Dict[str, Any],
    output_dir: str = "./generated_projects"
) -> Dict[str, Any]:
    """
    Convenience function to generate all project files
    
    Args:
        project_name: Name of the project
        orchestrator_outputs: Outputs from AgentOrchestrator
        output_dir: Base output directory
    
    Returns:
        Dictionary with file generation results
    """
    generator = FileGenerator(project_name, output_dir)
    results = generator.generate_from_orchestrator_output(orchestrator_outputs)
    
    print(generator.generate_summary())
    
    return results


if __name__ == "__main__":
    # Example usage
    import sys
    
    project_name = sys.argv[1] if len(sys.argv) > 1 else "my_project"
    
    # Would be used with actual orchestrator outputs
    print(f"File Generator initialized for: {project_name}")
