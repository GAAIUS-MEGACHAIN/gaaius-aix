"""
SCAFFOLD GENERATOR - Project Structure Foundation
Generates complete, production-ready project structures with all config files
This is the foundation for the GAAIUS Project Runtime System
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict
import uuid

@dataclass
class ScaffoldConfig:
    """Configuration for project scaffold generation"""
    project_id: str
    project_name: str
    project_type: str  # "fullstack", "frontend-only", "backend-only", "react", "nextjs", "express", "fastapi"
    template: str  # "blank", "ecommerce", "saas_dashboard", "social_platform", etc
    use_typescript: bool = True
    package_manager: str = "npm"  # "npm" or "yarn"
    database: Optional[str] = None  # "postgres", "mongodb", "sqlite"
    auth_system: bool = False
    styling: str = "tailwind"  # "tailwind", "styled-components", "css-modules"
    created_at: str = None
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()


class ScaffoldGenerator:
    """Generates complete project scaffolds with all necessary files"""
    
    def __init__(self, base_path: str = None):
        """Initialize scaffold generator"""
        self.base_path = Path(base_path) if base_path else Path(os.path.expanduser("~/gaaius_projects"))
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def generate_project(self, config: ScaffoldConfig) -> Dict[str, Any]:
        """
        Generate a complete project scaffold
        
        Args:
            config: ScaffoldConfig with project details
            
        Returns:
            Dict with project info and created files
        """
        project_path = self.base_path / config.project_id
        project_path.mkdir(parents=True, exist_ok=True)
        
        created_files = {}
        
        # Create root files
        created_files.update(self._create_root_files(project_path, config))
        
        # Create appropriate structure based on type
        if config.project_type in ["fullstack", "frontend-only", "react", "nextjs"]:
            created_files.update(self._create_frontend_structure(project_path, config))
        
        if config.project_type in ["fullstack", "backend-only", "express", "fastapi"]:
            created_files.update(self._create_backend_structure(project_path, config))
        
        if config.project_type == "fullstack":
            created_files.update(self._create_shared_structure(project_path, config))
        
        # Create config files
        created_files.update(self._create_config_files(project_path, config))
        
        # Create documentation
        created_files.update(self._create_documentation(project_path, config))
        
        return {
            "project_id": config.project_id,
            "project_name": config.project_name,
            "project_type": config.project_type,
            "path": str(project_path),
            "created_at": config.created_at,
            "files_count": len(created_files),
            "files": created_files
        }
    
    def _create_root_files(self, project_path: Path, config: ScaffoldConfig) -> Dict[str, str]:
        """Create root-level files"""
        files = {}
        
        # .gitignore
        files[".gitignore"] = self._template_gitignore(config.project_type)
        
        # .env.template
        files[".env.template"] = self._template_env(config)
        
        # gaaius.json (blueprint snapshot)
        gaaius_json = {
            "version": "1.0",
            "project_id": config.project_id,
            "project_name": config.project_name,
            "project_type": config.project_type,
            "template": config.template,
            "created_at": config.created_at,
            "generated_by": "GAAIUS AI Builder v2.0",
            "config": asdict(config)
        }
        files["gaaius.json"] = json.dumps(gaaius_json, indent=2)
        
        # Write all files
        for file_path, content in files.items():
            full_path = project_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)
        
        return files
    
    def _create_frontend_structure(self, project_path: Path, config: ScaffoldConfig) -> Dict[str, str]:
        """Create frontend directory structure"""
        files = {}
        frontend_path = "frontend" if config.project_type == "fullstack" else "."
        
        # package.json
        package_json = self._template_package_json(config, is_frontend=True)
        files[f"{frontend_path}/package.json"] = json.dumps(package_json, indent=2)
        
        # tsconfig.json or jsconfig.json
        if config.use_typescript:
            files[f"{frontend_path}/tsconfig.json"] = self._template_tsconfig()
        else:
            files[f"{frontend_path}/jsconfig.json"] = self._template_jsconfig()
        
        # vite.config.ts or next.config.js
        if config.project_type == "nextjs":
            files[f"{frontend_path}/next.config.js"] = self._template_next_config()
        else:
            files[f"{frontend_path}/vite.config.{self._ext(config)}"] = self._template_vite_config(config)
        
        # .env.local
        files[f"{frontend_path}/.env.local"] = "VITE_API_URL=http://localhost:3001\nVITE_APP_NAME=MyApp"
        
        # Source structure
        src_root = f"{frontend_path}/src"
        files[f"{src_root}/main.{self._ext(config)}"] = self._template_main_tsx(config)
        files[f"{src_root}/App.{self._ext(config)}"] = self._template_app_tsx(config)
        files[f"{src_root}/index.html"] = self._template_index_html(config)
        
        # Components directory
        files[f"{src_root}/components/.gitkeep"] = ""
        files[f"{src_root}/components/Header.{self._ext(config)}"] = self._template_component("Header")
        files[f"{src_root}/components/Footer.{self._ext(config)}"] = self._template_component("Footer")
        
        # Pages directory
        files[f"{src_root}/pages/.gitkeep"] = ""
        files[f"{src_root}/pages/Home.{self._ext(config)}"] = self._template_page("Home")
        files[f"{src_root}/pages/NotFound.{self._ext(config)}"] = self._template_page("NotFound")
        
        # Services directory
        files[f"{src_root}/services/.gitkeep"] = ""
        files[f"{src_root}/services/api.{self._ext(config)}"] = self._template_api_service(config)
        
        # Hooks directory
        files[f"{src_root}/hooks/.gitkeep"] = ""
        files[f"{src_root}/hooks/useApi.{self._ext(config)}"] = self._template_use_api()
        
        # Styles directory
        if config.styling == "tailwind":
            files[f"{src_root}/styles/globals.css"] = self._template_tailwind_globals()
        elif config.styling == "styled-components":
            files[f"{src_root}/styles/GlobalStyle.{self._ext(config)}"] = self._template_styled_globals()
        else:
            files[f"{src_root}/styles/index.css"] = self._template_css_globals()
        
        # Public directory
        files[f"{frontend_path}/public/favicon.svg"] = "<!-- Favicon SVG -->"
        files[f"{frontend_path}/public/.gitkeep"] = ""
        
        # Write all files
        for file_path, content in files.items():
            full_path = project_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            if content:  # Only write non-empty files
                full_path.write_text(content)
            else:
                full_path.touch()  # Create empty .gitkeep
        
        return files
    
    def _create_backend_structure(self, project_path: Path, config: ScaffoldConfig) -> Dict[str, str]:
        """Create backend directory structure"""
        files = {}
        backend_path = "backend" if config.project_type == "fullstack" else "."
        
        # Determine backend type (express or fastapi)
        is_express = config.project_type in ["fullstack", "express"]
        
        if is_express:
            files.update(self._create_express_backend(project_path, backend_path, config))
        else:
            files.update(self._create_fastapi_backend(project_path, backend_path, config))
        
        return files
    
    def _create_express_backend(self, project_path: Path, backend_path: str, config: ScaffoldConfig) -> Dict[str, str]:
        """Create Express.js backend structure"""
        files = {}
        
        # package.json
        package_json = self._template_package_json(config, is_frontend=False, is_express=True)
        files[f"{backend_path}/package.json"] = json.dumps(package_json, indent=2)
        
        # tsconfig.json
        files[f"{backend_path}/tsconfig.json"] = self._template_tsconfig()
        
        # .env
        files[f"{backend_path}/.env"] = self._template_backend_env(config)
        
        # src/index.ts
        files[f"{backend_path}/src/index.ts"] = self._template_express_index(config)
        
        # src/middleware
        files[f"{backend_path}/src/middleware/errorHandler.ts"] = self._template_express_error_handler()
        files[f"{backend_path}/src/middleware/auth.ts"] = self._template_express_auth()
        
        # src/routes
        files[f"{backend_path}/src/routes/index.ts"] = self._template_express_routes()
        files[f"{backend_path}/src/routes/users.ts"] = self._template_express_user_routes()
        files[f"{backend_path}/src/routes/api.ts"] = self._template_express_api_routes()
        
        # src/controllers
        files[f"{backend_path}/src/controllers/.gitkeep"] = ""
        files[f"{backend_path}/src/controllers/userController.ts"] = self._template_express_user_controller()
        
        # src/models
        files[f"{backend_path}/src/models/.gitkeep"] = ""
        if config.database == "mongodb":
            files[f"{backend_path}/src/models/User.ts"] = self._template_mongoose_user()
        else:
            files[f"{backend_path}/src/models/User.ts"] = self._template_typeorm_user()
        
        # src/types
        files[f"{backend_path}/src/types/.gitkeep"] = ""
        files[f"{backend_path}/src/types/index.ts"] = self._template_express_types()
        
        # src/utils
        files[f"{backend_path}/src/utils/.gitkeep"] = ""
        files[f"{backend_path}/src/utils/logger.ts"] = self._template_logger()
        
        # Write files
        for file_path, content in files.items():
            full_path = project_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            if content:
                full_path.write_text(content)
            else:
                full_path.touch()
        
        return files
    
    def _create_fastapi_backend(self, project_path: Path, backend_path: str, config: ScaffoldConfig) -> Dict[str, str]:
        """Create FastAPI backend structure"""
        files = {}
        
        # requirements.txt
        files[f"{backend_path}/requirements.txt"] = self._template_fastapi_requirements(config)
        
        # .env
        files[f"{backend_path}/.env"] = self._template_backend_env(config)
        
        # main.py
        files[f"{backend_path}/main.py"] = self._template_fastapi_main(config)
        
        # app/
        files[f"{backend_path}/app/__init__.py"] = ""
        files[f"{backend_path}/app/config.py"] = self._template_fastapi_config()
        
        # app/routers
        files[f"{backend_path}/app/routers/__init__.py"] = ""
        files[f"{backend_path}/app/routers/users.py"] = self._template_fastapi_user_routes()
        files[f"{backend_path}/app/routers/api.py"] = self._template_fastapi_api_routes()
        
        # app/models
        files[f"{backend_path}/app/models/__init__.py"] = ""
        files[f"{backend_path}/app/models/user.py"] = self._template_fastapi_user_model(config)
        
        # app/schemas
        files[f"{backend_path}/app/schemas/__init__.py"] = ""
        files[f"{backend_path}/app/schemas/user.py"] = self._template_fastapi_user_schema()
        
        # app/db
        files[f"{backend_path}/app/db/__init__.py"] = ""
        files[f"{backend_path}/app/db/database.py"] = self._template_fastapi_database(config)
        
        # app/utils
        files[f"{backend_path}/app/utils/__init__.py"] = ""
        files[f"{backend_path}/app/utils/logger.py"] = self._template_fastapi_logger()
        
        # Write files
        for file_path, content in files.items():
            full_path = project_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            if content:
                full_path.write_text(content)
            else:
                full_path.touch()
        
        return files
    
    def _create_shared_structure(self, project_path: Path, config: ScaffoldConfig) -> Dict[str, str]:
        """Create shared types and utilities for fullstack projects"""
        files = {}
        
        shared_path = "shared"
        files[f"{shared_path}/__init__.py"] = ""
        files[f"{shared_path}/types.ts"] = self._template_shared_types()
        files[f"{shared_path}/schemas.ts"] = self._template_shared_schemas()
        files[f"{shared_path}/constants.ts"] = self._template_shared_constants()
        
        for file_path, content in files.items():
            full_path = project_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            if content:
                full_path.write_text(content)
        
        return files
    
    def _create_config_files(self, project_path: Path, config: ScaffoldConfig) -> Dict[str, str]:
        """Create configuration files"""
        files = {}
        
        # Docker files
        files["Dockerfile"] = self._template_dockerfile(config)
        files["docker-compose.yml"] = self._template_docker_compose(config)
        
        # GitHub Actions
        files[".github/workflows/ci.yml"] = self._template_github_ci(config)
        
        # ESLint
        files[".eslintrc.json"] = self._template_eslintrc()
        
        # Prettier
        files[".prettierrc"] = self._template_prettierrc()
        
        # Write files
        for file_path, content in files.items():
            full_path = project_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)
        
        return files
    
    def _create_documentation(self, project_path: Path, config: ScaffoldConfig) -> Dict[str, str]:
        """Create documentation files"""
        files = {}
        
        files["README.md"] = self._template_readme(config)
        files["ARCHITECTURE.md"] = self._template_architecture(config)
        files["SETUP.md"] = self._template_setup(config)
        files["API.md"] = self._template_api_docs(config)
        
        for file_path, content in files.items():
            full_path = project_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)
        
        return files
    
    # ===== TEMPLATE METHODS =====
    
    def _ext(self, config: ScaffoldConfig) -> str:
        """Get file extension based on typescript setting"""
        return "tsx" if config.use_typescript else "jsx"
    
    def _template_gitignore(self, project_type: str) -> str:
        return """
# Dependencies
node_modules/
__pycache__/
.Python
env/
venv/
*.egg-info/

# Build
dist/
build/
*.o
*.so

# Environment
.env
.env.local
.env.*.local

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Temp
tmp/
temp/
.cache/
"""
    
    def _template_env(self, config: ScaffoldConfig) -> str:
        return f"""# Project Configuration
PROJECT_NAME={config.project_name}
PROJECT_ID={config.project_id}
ENVIRONMENT=development
DEBUG=true

# API
API_URL=http://localhost:3001
API_TIMEOUT=30000

# Database
DATABASE_URL=sqlite:///dev.db

# Auth
JWT_SECRET=your-secret-key-here-change-in-production
JWT_EXPIRY=24h

# Logging
LOG_LEVEL=debug
"""
    
    def _template_package_json(self, config: ScaffoldConfig, is_frontend: bool = True, is_express: bool = False) -> Dict[str, Any]:
        """Generate package.json for frontend or backend"""
        if is_frontend:
            return {
                "name": config.project_name.lower().replace(" ", "-"),
                "version": "0.1.0",
                "type": "module",
                "scripts": {
                    "dev": "vite" if config.project_type != "nextjs" else "next dev",
                    "build": "vite build" if config.project_type != "nextjs" else "next build",
                    "preview": "vite preview" if config.project_type != "nextjs" else "next start",
                    "lint": "eslint src --ext .ts,.tsx",
                    "type-check": "tsc --noEmit"
                },
                "dependencies": {
                    "react": "^18.2.0",
                    "react-dom": "^18.2.0",
                    "react-router-dom": "^6.8.0",
                    "axios": "^1.3.0",
                    "zustand": "^4.3.0"
                },
                "devDependencies": {
                    "@vitejs/plugin-react": "^3.1.0",
                    "vite": "^4.1.0",
                    "typescript": "^4.9.0",
                    "@types/react": "^18.0.0",
                    "@types/react-dom": "^18.0.0",
                    "tailwindcss": "^3.2.0",
                    "postcss": "^8.4.0",
                    "autoprefixer": "^10.4.0",
                    "eslint": "^8.32.0",
                    "prettier": "^2.8.0"
                }
            }
        elif is_express:
            return {
                "name": config.project_name.lower().replace(" ", "-"),
                "version": "0.1.0",
                "main": "dist/index.js",
                "type": "module",
                "scripts": {
                    "dev": "tsx watch src/index.ts",
                    "build": "tsc",
                    "start": "node dist/index.js",
                    "lint": "eslint src --ext .ts"
                },
                "dependencies": {
                    "express": "^4.18.0",
                    "cors": "^2.8.5",
                    "dotenv": "^16.0.0",
                    "zod": "^3.20.0",
                    "jsonwebtoken": "^9.0.0",
                    "bcryptjs": "^2.4.3",
                    "axios": "^1.3.0"
                },
                "devDependencies": {
                    "typescript": "^4.9.0",
                    "@types/node": "^18.0.0",
                    "@types/express": "^4.17.0",
                    "tsx": "^3.12.0",
                    "eslint": "^8.32.0"
                }
            }
    
    def _template_tsconfig(self) -> str:
        return json.dumps({
            "compilerOptions": {
                "target": "ES2020",
                "useDefineForClassFields": True,
                "lib": ["ES2020", "DOM", "DOM.Iterable"],
                "module": "ESNext",
                "skipLibCheck": True,
                "esModuleInterop": True,
                "allowSyntheticDefaultImports": True,
                "strict": True,
                "noUnusedLocals": True,
                "noUnusedParameters": True,
                "noFallthroughCasesInSwitch": True,
                "resolveJsonModule": True,
                "baseUrl": ".",
                "paths": {
                    "@/*": ["src/*"]
                }
            },
            "include": ["src"],
            "exclude": ["node_modules", "dist"]
        }, indent=2)
    
    def _template_jsconfig(self) -> str:
        return json.dumps({
            "compilerOptions": {
                "baseUrl": ".",
                "paths": {
                    "@/*": ["src/*"]
                }
            },
            "include": ["src"],
            "exclude": ["node_modules"]
        }, indent=2)
    
    def _template_vite_config(self, config: ScaffoldConfig) -> str:
        ext = "ts" if config.use_typescript else "js"
        return f"""import {{ defineConfig }} from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({{
  plugins: [react()],
  resolve: {{
    alias: {{
      '@': path.resolve(__dirname, './src'),
    }},
  }},
  server: {{
    port: 5173,
    proxy: {{
      '/api': {{
        target: 'http://localhost:3001',
        changeOrigin: true,
      }},
    }},
  }},
}})
"""
    
    def _template_next_config(self) -> str:
        return """/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  experimental: {
    appDir: true,
  },
}

module.exports = nextConfig
"""
    
    def _template_index_html(self, config: ScaffoldConfig) -> str:
        return f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{config.project_name}</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.{'tsx' if config.use_typescript else 'jsx'}"></script>
  </body>
</html>
"""
    
    def _template_main_tsx(self, config: ScaffoldConfig) -> str:
        ext = "tsx" if config.use_typescript else "jsx"
        return """import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './styles/globals.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
"""
    
    def _template_app_tsx(self, config: ScaffoldConfig) -> str:
        return """import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Header from './components/Header'
import Footer from './components/Footer'
import Home from './pages/Home'
import NotFound from './pages/NotFound'

export default function App() {
  return (
    <Router>
      <div className="flex flex-col min-h-screen">
        <Header />
        <main className="flex-1">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </main>
        <Footer />
      </div>
    </Router>
  )
}
"""
    
    def _template_component(self, name: str) -> str:
        return f"""export default function {name}() {{
  return (
    <div className="p-4">
      <h2 className="text-2xl font-bold">{name}</h2>
    </div>
  )
}}
"""
    
    def _template_page(self, name: str) -> str:
        return f"""export default function {name}() {{
  return (
    <div className="p-8">
      <h1 className="text-4xl font-bold mb-4">{name} Page</h1>
      <p className="text-gray-600">Your content here</p>
    </div>
  )
}}
"""
    
    def _template_api_service(self, config: ScaffoldConfig) -> str:
        return """import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:3001'

const api = axios.create({
  baseURL: `${API_URL}/api`,
  timeout: 30000,
})

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export default api
"""
    
    def _template_use_api(self) -> str:
        return """import { useState, useCallback } from 'react'
import api from '../services/api'

export function useApi(url: string) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const fetch = useCallback(async () => {
    setLoading(true)
    try {
      const response = await api.get(url)
      setData(response.data)
    } catch (err) {
      setError(err)
    } finally {
      setLoading(false)
    }
  }, [url])

  return { data, loading, error, fetch }
}
"""
    
    def _template_tailwind_globals(self) -> str:
        return """@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  color-scheme: light dark;
}

body {
  @apply bg-white dark:bg-gray-950 text-gray-900 dark:text-white;
}

a {
  @apply text-blue-600 hover:text-blue-700 dark:text-blue-400;
}
"""
    
    def _template_styled_globals(self) -> str:
        return """import { createGlobalStyle } from 'styled-components'

export const GlobalStyle = createGlobalStyle\`
  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }

  body {
    font-family: 'Inter', sans-serif;
    background-color: #ffffff;
    color: #000000;
  }

  a {
    color: #0066cc;
    text-decoration: none;
  }
\`
"""
    
    def _template_css_globals(self) -> str:
        return """* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  background-color: #ffffff;
  color: #000000;
}

a {
  color: #0066cc;
  text-decoration: none;
}
"""
    
    def _template_express_index(self, config: ScaffoldConfig) -> str:
        return """import express from 'express'
import cors from 'cors'
import dotenv from 'dotenv'
import routes from './routes'
import errorHandler from './middleware/errorHandler'

dotenv.config()

const app = express()
const PORT = process.env.PORT || 3001

// Middleware
app.use(express.json())
app.use(cors({
  origin: process.env.FRONTEND_URL || 'http://localhost:5173',
}))

// Routes
app.use('/api', routes)

// Error handling
app.use(errorHandler)

// Start server
app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`)
})
"""
    
    def _template_express_error_handler(self) -> str:
        return """import { Request, Response, NextFunction } from 'express'

export default function errorHandler(
  error: Error,
  req: Request,
  res: Response,
  next: NextFunction
) {
  console.error(error)
  res.status(500).json({
    error: error.message || 'Internal server error',
  })
}
"""
    
    def _template_express_auth(self) -> str:
        return """import { Request, Response, NextFunction } from 'express'
import jwt from 'jsonwebtoken'

export interface AuthRequest extends Request {
  user?: any
}

export function authMiddleware(req: AuthRequest, res: Response, next: NextFunction) {
  const token = req.headers.authorization?.split(' ')[1]
  
  if (!token) {
    return res.status(401).json({ error: 'No token provided' })
  }
  
  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET || 'secret')
    req.user = decoded
    next()
  } catch (error) {
    res.status(401).json({ error: 'Invalid token' })
  }
}
"""
    
    def _template_express_routes(self) -> str:
        return """import { Router } from 'express'
import users from './users'
import api from './api'

const router = Router()

router.use('/users', users)
router.use('/', api)

export default router
"""
    
    def _template_express_user_routes(self) -> str:
        return """import { Router } from 'express'
import { getUsers, createUser } from '../controllers/userController'
import { authMiddleware } from '../middleware/auth'

const router = Router()

router.get('/', authMiddleware, getUsers)
router.post('/', createUser)

export default router
"""
    
    def _template_express_api_routes(self) -> str:
        return """import { Router } from 'express'

const router = Router()

router.get('/health', (req, res) => {
  res.json({ status: 'ok' })
})

export default router
"""
    
    def _template_express_user_controller(self) -> str:
        return """import { Request, Response } from 'express'

export async function getUsers(req: Request, res: Response) {
  try {
    // TODO: Fetch users from database
    res.json([])
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch users' })
  }
}

export async function createUser(req: Request, res: Response) {
  try {
    const { email, name } = req.body
    // TODO: Create user in database
    res.status(201).json({ email, name })
  } catch (error) {
    res.status(500).json({ error: 'Failed to create user' })
  }
}
"""
    
    def _template_express_types(self) -> str:
        return """export interface User {
  id: string
  email: string
  name: string
  createdAt: Date
}

export interface ApiResponse<T> {
  success: boolean
  data?: T
  error?: string
}
"""
    
    def _template_logger(self) -> str:
        return """export const logger = {
  info: (message: string, data?: any) => {
    console.log(`[INFO] ${message}`, data || '')
  },
  error: (message: string, error?: any) => {
    console.error(`[ERROR] ${message}`, error || '')
  },
  debug: (message: string, data?: any) => {
    if (process.env.DEBUG) {
      console.log(`[DEBUG] ${message}`, data || '')
    }
  },
}
"""
    
    def _template_mongoose_user(self) -> str:
        return """import mongoose from 'mongoose'

const userSchema = new mongoose.Schema({
  email: { type: String, required: true, unique: true },
  name: { type: String, required: true },
  password: { type: String, required: true },
  createdAt: { type: Date, default: Date.now },
})

export const User = mongoose.model('User', userSchema)
"""
    
    def _template_typeorm_user(self) -> str:
        return """import { Entity, PrimaryGeneratedColumn, Column } from 'typeorm'

@Entity()
export class User {
  @PrimaryGeneratedColumn()
  id: number

  @Column({ unique: true })
  email: string

  @Column()
  name: string

  @Column()
  password: string

  @Column({ type: 'timestamp', default: () => 'CURRENT_TIMESTAMP' })
  createdAt: Date
}
"""
    
    def _template_fastapi_requirements(self, config: ScaffoldConfig) -> str:
        requirements = [
            "fastapi==0.104.1",
            "uvicorn[standard]==0.24.0",
            "pydantic==2.5.0",
            "python-dotenv==1.0.0",
            "sqlalchemy==2.0.23",
            "pydantic-settings==2.1.0",
            "PyJWT==2.8.1",
            "python-multipart==0.0.6",
        ]
        
        if config.database == "mongodb":
            requirements.append("pymongo==4.6.0")
            requirements.append("motor==3.3.2")
        elif config.database == "postgres":
            requirements.append("psycopg2-binary==2.9.9")
            requirements.append("asyncpg==0.29.0")
        
        return "\n".join(requirements)
    
    def _template_fastapi_main(self, config: ScaffoldConfig) -> str:
        return """import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

from app.routers import users, api

load_dotenv()

app = FastAPI(
    title="API",
    version="0.1.0",
    description="API for """+ config.project_name + """",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(api.router)
app.include_router(users.router)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 3001)),
        reload=True
    )
"""
    
    def _template_fastapi_config(self) -> str:
        return """import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "API"
    DEBUG: bool = True
    DATABASE_URL: str = "sqlite:///dev.db"
    JWT_SECRET: str = "your-secret-key"
    JWT_EXPIRY: int = 86400  # 24 hours
    
    class Config:
        env_file = ".env"

settings = Settings()
"""
    
    def _template_fastapi_user_routes(self) -> str:
        return """from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/")
async def get_users():
    return []

@router.post("/")
async def create_user(user_data: dict):
    return {"user": user_data}
"""
    
    def _template_fastapi_api_routes(self) -> str:
        return """from fastapi import APIRouter

router = APIRouter(tags=["api"])

@router.get("/")
async def root():
    return {"message": "Welcome to API"}
"""
    
    def _template_fastapi_user_model(self, config: ScaffoldConfig) -> str:
        if config.database == "mongodb":
            return """from pymongo import MongoClient
import os

class User:
    def __init__(self):
        self.client = MongoClient(os.getenv("DATABASE_URL"))
        self.db = self.client.get_database()
    
    async def create(self, user_data: dict):
        result = self.db.users.insert_one(user_data)
        return result.inserted_id
    
    async def get_by_id(self, user_id: str):
        return self.db.users.find_one({"_id": user_id})
"""
        else:
            return """from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
"""
    
    def _template_fastapi_user_schema(self) -> str:
        return """from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
"""
    
    def _template_fastapi_database(self, config: ScaffoldConfig) -> str:
        return """import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///dev.db")

if "sqlite" in DATABASE_URL:
    engine = create_async_engine(f"sqlite+aiosqlite:///{DATABASE_URL.split(':///')[-1]}")
else:
    engine = create_async_engine(DATABASE_URL, echo=True)

async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def get_session():
    async with async_session() as session:
        yield session
"""
    
    def _template_fastapi_logger(self) -> str:
        return """import logging
import os

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)

handler = logging.StreamHandler()
handler.setLevel(LOG_LEVEL)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

logger.addHandler(handler)
"""
    
    def _template_backend_env(self, config: ScaffoldConfig) -> str:
        return f"""# Backend Configuration
NODE_ENV=development
PORT=3001

# Database
DATABASE_URL=postgres://user:password@localhost:5432/{config.project_name.lower()}

# JWT
JWT_SECRET=your-secret-key-change-in-production
JWT_EXPIRY=24h

# Logging
LOG_LEVEL=debug
"""
    
    def _template_shared_types(self) -> str:
        return """export interface User {
  id: string
  email: string
  name: string
  createdAt: string
}

export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  error?: string
}
"""
    
    def _template_shared_schemas(self) -> str:
        return """import { z } from 'zod'

export const UserSchema = z.object({
  id: z.string(),
  email: z.string().email(),
  name: z.string(),
  createdAt: z.string(),
})

export const ApiResponseSchema = z.object({
  success: z.boolean(),
  data: z.any().optional(),
  error: z.string().optional(),
})
"""
    
    def _template_shared_constants(self) -> str:
        return """export const API_TIMEOUT = 30000
export const API_RETRY_COUNT = 3

export const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  INTERNAL_ERROR: 500,
}
"""
    
    def _template_dockerfile(self, config: ScaffoldConfig) -> str:
        if config.project_type in ["frontend-only", "react", "nextjs"]:
            return """FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

RUN npm run build

EXPOSE 3000
CMD ["npm", "preview"]
"""
        else:
            return """FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 3001
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3001"]
"""
    
    def _template_docker_compose(self, config: ScaffoldConfig) -> str:
        services = {}
        
        if config.project_type in ["fullstack", "frontend-only", "react", "nextjs"]:
            services["frontend"] = {
                "build": {"context": ".", "dockerfile": "Dockerfile.frontend"},
                "ports": ["5173:5173"],
                "environment": ["VITE_API_URL=http://localhost:3001"],
                "depends_on": ["backend"] if config.project_type == "fullstack" else None
            }
        
        if config.project_type in ["fullstack", "backend-only", "express", "fastapi"]:
            services["backend"] = {
                "build": {"context": ".", "dockerfile": "Dockerfile"},
                "ports": ["3001:3001"],
                "environment": ["DATABASE_URL=postgres://user:pass@db:5432/myapp"],
                "depends_on": ["db"] if config.database == "postgres" else None
            }
        
        if config.database == "postgres":
            services["db"] = {
                "image": "postgres:15",
                "environment": [
                    "POSTGRES_USER=user",
                    "POSTGRES_PASSWORD=pass",
                    "POSTGRES_DB=" + config.project_name.lower()
                ],
                "volumes": ["postgres_data:/var/lib/postgresql/data"],
                "ports": ["5432:5432"]
            }
        
        compose = {
            "version": "3.8",
            "services": {k: v for k, v in services.items() if v}
        }
        
        if config.database == "postgres":
            compose["volumes"] = {"postgres_data": {}}
        
        return json.dumps(compose, indent=2)
    
    def _template_github_ci(self, config: ScaffoldConfig) -> str:
        return """name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm ci
      - run: npm run lint
      - run: npm run test
      - run: npm run build
"""
    
    def _template_eslintrc(self) -> str:
        return json.dumps({
            "env": {
                "browser": True,
                "node": True,
                "es2021": True
            },
            "extends": [
                "eslint:recommended",
                "plugin:@typescript-eslint/recommended"
            ],
            "parser": "@typescript-eslint/parser",
            "parserOptions": {
                "ecmaVersion": "latest",
                "sourceType": "module"
            },
            "rules": {
                "no-unused-vars": "off",
                "@typescript-eslint/no-unused-vars": ["error"]
            }
        }, indent=2)
    
    def _template_prettierrc(self) -> str:
        return json.dumps({
            "semi": False,
            "trailingComma": "es5",
            "singleQuote": True,
            "printWidth": 100,
            "tabWidth": 2
        }, indent=2)
    
    def _template_readme(self, config: ScaffoldConfig) -> str:
        return f"""# {config.project_name}

Generated by GAAIUS AI Builder v2.0

## Project Information

- **Type**: {config.project_type}
- **Template**: {config.template}
- **Created**: {config.created_at}
- **Project ID**: {config.project_id}

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

```bash
npm install
```

### Development

```bash
npm run dev
```

### Build

```bash
npm run build
```

### Production

```bash
npm start
```

## Project Structure

```
{config.project_name}/
├── frontend/           # React/Next.js frontend
│   ├── src/
│   │   ├── components/ # Reusable components
│   │   ├── pages/      # Page components
│   │   ├── services/   # API services
│   │   └── styles/     # Global styles
│   └── public/         # Static assets
├── backend/            # API server
│   ├── src/
│   │   ├── routes/     # API routes
│   │   ├── models/     # Database models
│   │   └── middleware/ # Express middleware
├── shared/             # Shared types
└── docker-compose.yml  # Docker setup
```

## Documentation

- [Architecture](./ARCHITECTURE.md)
- [Setup Guide](./SETUP.md)
- [API Documentation](./API.md)

## License

MIT
"""
    
    def _template_architecture(self, config: ScaffoldConfig) -> str:
        return f"""# Architecture

## Overview

This is a {config.project_type} application built with GAAIUS AI Builder.

## Tech Stack

### Frontend
- React 18
- Vite or Next.js
- React Router
- Zustand (state management)
- Tailwind CSS
- TypeScript

### Backend
- Express.js or FastAPI
- TypeScript or Python
- PostgreSQL or MongoDB
- JWT Authentication

## Data Flow

```
User
  ↓
Frontend (React/Vite)
  ↓
API (Express/FastAPI)
  ↓
Database (PostgreSQL/MongoDB)
```

## Key Features

- 🔐 Authentication
- 🗄️ Database
- 📊 Real-time updates
- 📱 Responsive design
- 🚀 Production ready

## Deployment

See SETUP.md for deployment instructions.
"""
    
    def _template_setup(self, config: ScaffoldConfig) -> str:
        return """# Setup Guide

## Local Development

### 1. Install Dependencies

```bash
npm install
```

### 2. Environment Configuration

Copy `.env.template` to `.env` and update values:

```bash
cp .env.template .env
```

### 3. Start Development Server

```bash
npm run dev
```

The app will be available at `http://localhost:5173` (frontend) and `http://localhost:3001` (backend).

## Docker Setup

### Build

```bash
docker-compose build
```

### Run

```bash
docker-compose up
```

## Production Deployment

### Build for Production

```bash
npm run build
```

### Deploy to Vercel

```bash
vercel
```

### Deploy to Docker

```bash
docker build -t myapp .
docker run -p 3000:3000 myapp
```

## Database Setup

### PostgreSQL

```sql
CREATE DATABASE myapp;
CREATE USER appuser WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE myapp TO appuser;
```

### MongoDB

```bash
mongod
mongo
use myapp
```

## Troubleshooting

- Clear node_modules: `rm -rf node_modules && npm install`
- Reset database: Check database docs
- Check logs: `npm run dev` shows all logs

## Support

For issues, check the main README or contact support.
"""
    
    def _template_api_docs(self, config: ScaffoldConfig) -> str:
        return """# API Documentation

## Authentication

All protected endpoints require a Bearer token:

```
Authorization: Bearer <token>
```

## Endpoints

### Users

#### Get All Users
```
GET /api/users
Authorization: Bearer <token>
```

Response:
```json
[
  {
    "id": "1",
    "email": "user@example.com",
    "name": "John Doe"
  }
]
```

#### Create User
```
POST /api/users
Content-Type: application/json

{
  "email": "user@example.com",
  "name": "John Doe",
  "password": "secure_password"
}
```

Response:
```json
{
  "id": "1",
  "email": "user@example.com",
  "name": "John Doe"
}
```

## Status Codes

- 200: OK
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 404: Not Found
- 500: Internal Server Error
"""
