"""
GAAIUS PROJECT RUNTIME v1.0
==========================

This module transforms GAAIUS from a static HTML generator into a 
full-stack project scaffold generator - the core of what makes 
Emergent/Replit-class AI builders work.

Architecture:
1. Project Scaffold Generator - Generates full repo structure
2. Frontend Runtime - React/Vite or Next.js with real package.json
3. Backend Runtime - API server with real endpoints
4. Preview Orchestrator - Conceptual dev server simulation
5. Packaging & Export - Web/Mobile/Desktop export

"""

import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

# ============================================================================
# ENTERPRISE PROJECT TEMPLATES
# ============================================================================

# The full enterprise folder structure that all GAAIUS projects will use
ENTERPRISE_SCAFFOLD = {
    # Frontend
    "frontend/package.json": None,  # Will be generated dynamically
    "frontend/vite.config.ts": None,
    "frontend/tsconfig.json": None,
    "frontend/index.html": None,
    "frontend/src/main.tsx": None,
    "frontend/src/App.tsx": None,
    "frontend/src/vite-env.d.ts": None,
    "frontend/src/index.css": None,
    "frontend/src/pages/index.ts": None,
    "frontend/src/pages/Dashboard.tsx": None,
    "frontend/src/pages/Settings.tsx": None,
    "frontend/src/pages/Profile.tsx": None,
    "frontend/src/pages/NotFound.tsx": None,
    "frontend/src/components/index.ts": None,
    "frontend/src/components/Layout.tsx": None,
    "frontend/src/components/Sidebar.tsx": None,
    "frontend/src/components/Header.tsx": None,
    "frontend/src/components/Card.tsx": None,
    "frontend/src/components/Button.tsx": None,
    "frontend/src/components/Modal.tsx": None,
    "frontend/src/components/Table.tsx": None,
    "frontend/src/services/api.ts": None,
    "frontend/src/services/auth.ts": None,
    "frontend/src/hooks/useAuth.ts": None,
    "frontend/src/hooks/useApi.ts": None,
    "frontend/src/store/index.ts": None,
    "frontend/src/store/authStore.ts": None,
    "frontend/src/types/index.ts": None,
    "frontend/src/styles/globals.css": None,
    "frontend/src/utils/helpers.ts": None,
    "frontend/src/utils/constants.ts": None,
    "frontend/public/favicon.ico": None,
    "frontend/tailwind.config.js": None,
    "frontend/postcss.config.js": None,
    
    # Backend
    "backend/package.json": None,
    "backend/tsconfig.json": None,
    "backend/src/server.ts": None,
    "backend/src/routes/index.ts": None,
    "backend/src/routes/auth.ts": None,
    "backend/src/routes/api.ts": None,
    "backend/src/controllers/authController.ts": None,
    "backend/src/controllers/apiController.ts": None,
    "backend/src/models/User.ts": None,
    "backend/src/middleware/auth.ts": None,
    "backend/src/middleware/errorHandler.ts": None,
    "backend/src/config/database.ts": None,
    "backend/src/config/env.ts": None,
    "backend/src/utils/helpers.ts": None,
    "backend/src/types/index.ts": None,
    
    # Shared (monorepo pattern)
    "shared/types.ts": None,
    "shared/schemas.ts": None,
    "shared/constants.ts": None,
    "shared/utils.ts": None,
    
    # Config
    "config/app.json": None,
    "config/build.json": None,
    "config/deploy.json": None,
    
    # Root
    ".env": None,
    ".env.example": None,
    ".gitignore": None,
    "README.md": None,
    "gaaius.json": None,  # Blueprint snapshot
}

# ============================================================================
# DEFAULT FILE CONTENTS FOR ALL PROJECT TYPES
# ============================================================================

def get_default_package_json(app_name: str, is_frontend: bool = True) -> str:
    """Generate package.json for frontend or backend"""
    if is_frontend:
        return json.dumps({
            "name": f"{app_name.lower().replace(' ', '-')}-frontend",
            "private": True,
            "version": "1.0.0",
            "type": "module",
            "scripts": {
                "dev": "vite",
                "build": "tsc && vite build",
                "lint": "eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0",
                "preview": "vite preview"
            },
            "dependencies": {
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "react-router-dom": "^6.20.0",
                "zustand": "^4.4.0",
                "axios": "^1.6.0",
                "lucide-react": "^0.290.0",
                "clsx": "^2.0.0",
                "tailwind-merge": "^2.0.0"
            },
            "devDependencies": {
                "@types/react": "^18.2.0",
                "@types/react-dom": "^18.2.0",
                "@vitejs/plugin-react": "^4.2.0",
                "autoprefixer": "^10.4.0",
                "postcss": "^8.4.0",
                "tailwindcss": "^3.3.0",
                "typescript": "^5.2.0",
                "vite": "^5.0.0"
            }
        }, indent=2)
    else:
        return json.dumps({
            "name": f"{app_name.lower().replace(' ', '-')}-backend",
            "version": "1.0.0",
            "type": "module",
            "scripts": {
                "dev": "tsx watch src/server.ts",
                "build": "tsc",
                "start": "node dist/server.js"
            },
            "dependencies": {
                "express": "^4.18.0",
                "cors": "^2.8.0",
                "dotenv": "^16.3.0",
                "jsonwebtoken": "^9.0.0",
                "bcryptjs": "^2.4.0",
                "zod": "^3.22.0",
                "mongoose": "^8.0.0"
            },
            "devDependencies": {
                "@types/express": "^4.17.0",
                "@types/cors": "^2.8.0",
                "@types/jsonwebtoken": "^9.0.0",
                "@types/bcryptjs": "^2.4.0",
                "typescript": "^5.2.0",
                "tsx": "^4.0.0"
            }
        }, indent=2)

def get_vite_config() -> str:
    return """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@components': path.resolve(__dirname, './src/components'),
      '@pages': path.resolve(__dirname, './src/pages'),
      '@services': path.resolve(__dirname, './src/services'),
      '@hooks': path.resolve(__dirname, './src/hooks'),
      '@store': path.resolve(__dirname, './src/store'),
      '@types': path.resolve(__dirname, './src/types'),
      '@utils': path.resolve(__dirname, './src/utils'),
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8001',
        changeOrigin: true,
      },
    },
  },
})
"""

def get_tsconfig_frontend() -> str:
    return json.dumps({
        "compilerOptions": {
            "target": "ES2020",
            "useDefineForClassFields": True,
            "lib": ["ES2020", "DOM", "DOM.Iterable"],
            "module": "ESNext",
            "skipLibCheck": True,
            "moduleResolution": "bundler",
            "allowImportingTsExtensions": True,
            "resolveJsonModule": True,
            "isolatedModules": True,
            "noEmit": True,
            "jsx": "react-jsx",
            "strict": True,
            "noUnusedLocals": True,
            "noUnusedParameters": True,
            "noFallthroughCasesInSwitch": True,
            "baseUrl": ".",
            "paths": {
                "@/*": ["./src/*"],
                "@components/*": ["./src/components/*"],
                "@pages/*": ["./src/pages/*"]
            }
        },
        "include": ["src"],
        "references": [{"path": "./tsconfig.node.json"}]
    }, indent=2)

def get_tsconfig_backend() -> str:
    return json.dumps({
        "compilerOptions": {
            "target": "ES2022",
            "module": "ESNext",
            "moduleResolution": "node",
            "outDir": "./dist",
            "rootDir": "./src",
            "strict": True,
            "esModuleInterop": True,
            "skipLibCheck": True,
            "forceConsistentCasingInFileNames": True,
            "resolveJsonModule": True,
            "declaration": True,
            "declarationMap": True,
            "sourceMap": True
        },
        "include": ["src/**/*"],
        "exclude": ["node_modules", "dist"]
    }, indent=2)

def get_tailwind_config() -> str:
    return """/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f5f3ff',
          100: '#ede9fe',
          500: '#8b5cf6',
          600: '#7c3aed',
          700: '#6d28d9',
        },
        dark: {
          50: '#1a1a1a',
          100: '#0f0f0f',
          200: '#0a0a0a',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
"""

def get_postcss_config() -> str:
    return """export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
"""

def get_index_html(app_name: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{app_name}</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
"""

def get_main_tsx() -> str:
    return """import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>,
)
"""

def get_index_css() -> str:
    return """@tailwind base;
@tailwind components;
@tailwind utilities;

* {
  font-family: 'Inter', system-ui, sans-serif;
}

::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: #0a0a0a;
}

::-webkit-scrollbar-thumb {
  background: #7c3aed;
  border-radius: 4px;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.animate-fade-in {
  animation: fadeIn 0.6s ease-out;
}
"""

def get_vite_env_d_ts() -> str:
    return """/// <reference types="vite/client" />
"""

def get_env_example() -> str:
    return """# Frontend
VITE_API_URL=http://localhost:8001

# Backend
PORT=8001
NODE_ENV=development
MONGO_URL=mongodb://localhost:27017/app
JWT_SECRET=your-super-secret-key-change-in-production

# Optional Services
# STRIPE_SECRET_KEY=sk_test_...
# SENDGRID_API_KEY=SG....
"""

def get_gitignore() -> str:
    return """# Dependencies
node_modules/
.pnp
.pnp.js

# Testing
coverage/

# Production
dist/
build/

# Misc
.DS_Store
*.pem
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# Debug
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# IDE
.idea/
.vscode/
*.swp
*.swo

# TypeScript
*.tsbuildinfo
"""

def get_gaaius_json(app_name: str, app_type: str, blueprint: dict) -> str:
    return json.dumps({
        "name": app_name,
        "version": "1.0.0",
        "type": app_type,
        "generator": "GAAIUS PROJECT RUNTIME v1.0",
        "generated_at": datetime.now().isoformat(),
        "blueprint": blueprint,
        "runtime": {
            "frontend": "vite",
            "backend": "express",
            "database": "mongodb"
        },
        "features": blueprint.get("features", []),
        "pages": [p.get("name", "") for p in blueprint.get("pages", [])]
    }, indent=2)

def get_readme(app_name: str, app_type: str, features: List[str]) -> str:
    features_list = "\n".join([f"- {f}" for f in features]) if features else "- Core functionality"
    return f"""# {app_name}

Built with **GAAIUS PROJECT RUNTIME** - Enterprise-grade Full-Stack Application

## 🚀 Project Structure

```
├── frontend/           # React + Vite + TypeScript
│   ├── src/
│   │   ├── pages/     # Page components
│   │   ├── components/ # Reusable UI components  
│   │   ├── services/  # API services
│   │   ├── hooks/     # Custom React hooks
│   │   ├── store/     # State management (Zustand)
│   │   └── utils/     # Helper functions
│   └── package.json
│
├── backend/           # Express + TypeScript
│   ├── src/
│   │   ├── routes/    # API routes
│   │   ├── controllers/ # Route handlers
│   │   ├── models/    # Database models
│   │   ├── middleware/ # Express middleware
│   │   └── config/    # Configuration
│   └── package.json
│
├── shared/            # Shared types & utilities
├── config/            # App configuration
└── gaaius.json        # Blueprint snapshot
```

## ✨ Features

{features_list}

## 🛠️ Getting Started

### Prerequisites
- Node.js 18+
- MongoDB (local or Atlas)

### Installation

1. **Install frontend dependencies:**
```bash
cd frontend && npm install
```

2. **Install backend dependencies:**
```bash
cd backend && npm install
```

3. **Set up environment:**
```bash
cp .env.example .env
# Edit .env with your values
```

4. **Start development servers:**

Frontend (port 3000):
```bash
cd frontend && npm run dev
```

Backend (port 8001):
```bash
cd backend && npm run dev
```

## 📦 Export Options

- **Web**: `cd frontend && npm run build`
- **Desktop**: Use Electron or Tauri
- **Mobile**: Use Capacitor or Expo

---

Generated by **GAAIUS AI Builder** - Enterprise-Grade Full-Stack Runtime
"""

# ============================================================================
# COMPONENT GENERATORS
# ============================================================================

def generate_app_tsx(app_name: str, pages: List[dict], app_type: str) -> str:
    """Generate the main App.tsx with routing"""
    
    # Build imports and routes based on pages
    page_imports = []
    routes = []
    
    default_pages = [
        {"name": "Dashboard", "path": "/", "icon": "LayoutDashboard"},
        {"name": "Settings", "path": "/settings", "icon": "Settings"},
        {"name": "Profile", "path": "/profile", "icon": "User"}
    ]
    
    pages_to_use = pages if pages else default_pages
    
    for page in pages_to_use:
        name = page.get("name", "Page").replace(" ", "")
        path = page.get("path", f"/{name.lower()}")
        page_imports.append(f"import {name} from '@/pages/{name}'")
        routes.append(f'        <Route path="{path}" element={{<{name} />}} />')
    
    imports_str = "\n".join(page_imports)
    routes_str = "\n".join(routes)
    
    return f"""import {{ Routes, Route }} from 'react-router-dom'
import Layout from '@/components/Layout'
{imports_str}
import NotFound from '@/pages/NotFound'

function App() {{
  return (
    <Layout>
      <Routes>
{routes_str}
        <Route path="*" element={{<NotFound />}} />
      </Routes>
    </Layout>
  )
}}

export default App
"""

def generate_layout_component(app_name: str, app_type: str) -> str:
    """Generate the main Layout component with sidebar"""
    return f"""import {{ ReactNode }} from 'react'
import Sidebar from './Sidebar'
import Header from './Header'

interface LayoutProps {{
  children: ReactNode
}}

export default function Layout({{ children }}: LayoutProps) {{
  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white flex">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <Header title="{app_name}" />
        <main className="flex-1 p-6 overflow-auto">
          {{children}}
        </main>
      </div>
    </div>
  )
}}
"""

def generate_sidebar_component(pages: List[dict], app_type: str) -> str:
    """Generate the Sidebar component"""
    
    default_pages = [
        {"name": "Dashboard", "path": "/", "icon": "LayoutDashboard"},
        {"name": "Settings", "path": "/settings", "icon": "Settings"},
        {"name": "Profile", "path": "/profile", "icon": "User"}
    ]
    
    pages_to_use = pages if pages else default_pages
    
    nav_items = []
    icons_to_import = set(["Menu", "X"])
    
    for page in pages_to_use:
        name = page.get("name", "Page")
        path = page.get("path", f"/{name.lower()}")
        icon = page.get("icon", "Circle")
        icons_to_import.add(icon)
        nav_items.append(f"""
        <NavLink
          to="{path}"
          className={{({{ isActive }}) =>
            \`flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${{
              isActive ? 'bg-primary-600/20 text-primary-500' : 'text-white/60 hover:bg-white/5 hover:text-white'
            }}\`
          }}
        >
          <{icon} className="w-5 h-5" />
          <span className="font-medium">{name}</span>
        </NavLink>""")
    
    icons_import = ", ".join(sorted(icons_to_import))
    nav_items_str = "".join(nav_items)
    
    return f"""import {{ useState }} from 'react'
import {{ NavLink }} from 'react-router-dom'
import {{ {icons_import} }} from 'lucide-react'

export default function Sidebar() {{
  const [collapsed, setCollapsed] = useState(false)

  return (
    <aside className={{`${{collapsed ? 'w-16' : 'w-64'}} bg-[#111] border-r border-white/10 flex flex-col transition-all duration-300`}}>
      <div className="h-16 border-b border-white/10 flex items-center justify-between px-4">
        {{!collapsed && (
          <h1 className="text-xl font-bold bg-gradient-to-r from-primary-500 to-cyan-400 bg-clip-text text-transparent">
            GAAIUS
          </h1>
        )}}
        <button onClick={{() => setCollapsed(!collapsed)}} className="p-2 hover:bg-white/10 rounded-lg transition">
          {{collapsed ? <Menu className="w-5 h-5" /> : <X className="w-5 h-5" />}}
        </button>
      </div>
      
      <nav className="flex-1 p-3 space-y-1">
        {nav_items_str}
      </nav>
      
      <div className="p-4 border-t border-white/10">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary-500 to-cyan-500 flex items-center justify-center">
            <span className="text-sm font-bold">U</span>
          </div>
          {{!collapsed && (
            <div>
              <p className="text-sm font-medium">User</p>
              <p className="text-xs text-white/40">user@example.com</p>
            </div>
          )}}
        </div>
      </div>
    </aside>
  )
}}
"""

def generate_header_component() -> str:
    return """import { Bell, Search, Settings } from 'lucide-react'

interface HeaderProps {
  title?: string
}

export default function Header({ title = 'Dashboard' }: HeaderProps) {
  return (
    <header className="h-16 bg-[#111] border-b border-white/10 flex items-center justify-between px-6">
      <h2 className="text-lg font-semibold">{title}</h2>
      
      <div className="flex items-center gap-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/40" />
          <input
            type="text"
            placeholder="Search..."
            className="w-64 bg-white/5 border border-white/10 rounded-lg pl-10 pr-4 py-2 text-sm focus:outline-none focus:border-primary-500/50"
          />
        </div>
        
        <button className="relative p-2 hover:bg-white/10 rounded-lg transition">
          <Bell className="w-5 h-5" />
          <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full" />
        </button>
        
        <button className="p-2 hover:bg-white/10 rounded-lg transition">
          <Settings className="w-5 h-5" />
        </button>
      </div>
    </header>
  )
}
"""

def generate_card_component() -> str:
    return """import { ReactNode } from 'react'
import { clsx } from 'clsx'

interface CardProps {
  children: ReactNode
  className?: string
  title?: string
  description?: string
}

export default function Card({ children, className, title, description }: CardProps) {
  return (
    <div className={clsx(
      'bg-white/5 border border-white/10 rounded-2xl p-6 hover:bg-white/[0.07] transition',
      className
    )}>
      {title && <h3 className="text-lg font-semibold mb-2">{title}</h3>}
      {description && <p className="text-white/60 text-sm mb-4">{description}</p>}
      {children}
    </div>
  )
}
"""

def generate_button_component() -> str:
    return """import { ReactNode, ButtonHTMLAttributes } from 'react'
import { clsx } from 'clsx'

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger'
  size?: 'sm' | 'md' | 'lg'
}

export default function Button({ 
  children, 
  variant = 'primary', 
  size = 'md',
  className,
  ...props 
}: ButtonProps) {
  return (
    <button
      className={clsx(
        'font-medium rounded-xl transition-all inline-flex items-center justify-center gap-2',
        {
          'bg-primary-600 hover:bg-primary-700 text-white': variant === 'primary',
          'bg-white/10 hover:bg-white/20 text-white': variant === 'secondary',
          'hover:bg-white/10 text-white/60 hover:text-white': variant === 'ghost',
          'bg-red-600 hover:bg-red-700 text-white': variant === 'danger',
        },
        {
          'px-3 py-1.5 text-sm': size === 'sm',
          'px-4 py-2 text-sm': size === 'md',
          'px-6 py-3 text-base': size === 'lg',
        },
        className
      )}
      {...props}
    >
      {children}
    </button>
  )
}
"""

def generate_modal_component() -> str:
    return """import { ReactNode, useEffect } from 'react'
import { X } from 'lucide-react'

interface ModalProps {
  isOpen: boolean
  onClose: () => void
  title?: string
  children: ReactNode
}

export default function Modal({ isOpen, onClose, title, children }: ModalProps) {
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = 'unset'
    }
    return () => {
      document.body.style.overflow = 'unset'
    }
  }, [isOpen])

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={onClose} />
      <div className="relative bg-[#1a1a1a] border border-white/10 rounded-2xl p-6 max-w-lg w-full mx-4 animate-fade-in">
        <div className="flex items-center justify-between mb-4">
          {title && <h3 className="text-lg font-semibold">{title}</h3>}
          <button onClick={onClose} className="p-1 hover:bg-white/10 rounded-lg transition">
            <X className="w-5 h-5" />
          </button>
        </div>
        {children}
      </div>
    </div>
  )
}
"""

def generate_table_component() -> str:
    return """interface Column {
  key: string
  label: string
  render?: (value: any, row: any) => React.ReactNode
}

interface TableProps {
  columns: Column[]
  data: any[]
  onRowClick?: (row: any) => void
}

export default function Table({ columns, data, onRowClick }: TableProps) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr className="border-b border-white/10">
            {columns.map((col) => (
              <th key={col.key} className="text-left py-3 px-4 text-sm font-medium text-white/60">
                {col.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, i) => (
            <tr 
              key={i} 
              className="border-b border-white/5 hover:bg-white/5 transition cursor-pointer"
              onClick={() => onRowClick?.(row)}
            >
              {columns.map((col) => (
                <td key={col.key} className="py-3 px-4 text-sm">
                  {col.render ? col.render(row[col.key], row) : row[col.key]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
"""

def generate_components_index() -> str:
    return """export { default as Layout } from './Layout'
export { default as Sidebar } from './Sidebar'
export { default as Header } from './Header'
export { default as Card } from './Card'
export { default as Button } from './Button'
export { default as Modal } from './Modal'
export { default as Table } from './Table'
"""

def generate_api_service() -> str:
    return """import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor - add auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response interceptor - handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default api

// API methods
export const authApi = {
  login: (email: string, password: string) => 
    api.post('/api/auth/login', { email, password }),
  register: (email: string, password: string, name: string) => 
    api.post('/api/auth/register', { email, password, name }),
  me: () => 
    api.get('/api/auth/me'),
}

export const dataApi = {
  getAll: (resource: string) => api.get(`/api/${resource}`),
  getOne: (resource: string, id: string) => api.get(`/api/${resource}/${id}`),
  create: (resource: string, data: any) => api.post(`/api/${resource}`, data),
  update: (resource: string, id: string, data: any) => api.put(`/api/${resource}/${id}`, data),
  delete: (resource: string, id: string) => api.delete(`/api/${resource}/${id}`),
}
"""

def generate_auth_service() -> str:
    return """import api, { authApi } from './api'

export interface User {
  id: string
  email: string
  name: string
}

export const authService = {
  async login(email: string, password: string): Promise<{ token: string; user: User }> {
    const { data } = await authApi.login(email, password)
    localStorage.setItem('token', data.token)
    return data
  },

  async register(email: string, password: string, name: string): Promise<{ token: string; user: User }> {
    const { data } = await authApi.register(email, password, name)
    localStorage.setItem('token', data.token)
    return data
  },

  async getCurrentUser(): Promise<User | null> {
    try {
      const { data } = await authApi.me()
      return data
    } catch {
      return null
    }
  },

  logout() {
    localStorage.removeItem('token')
    window.location.href = '/login'
  },

  isAuthenticated(): boolean {
    return !!localStorage.getItem('token')
  },
}
"""

def generate_auth_hook() -> str:
    return """import { create } from 'zustand'
import { authService, User } from '@/services/auth'

interface AuthState {
  user: User | null
  loading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string, name: string) => Promise<void>
  logout: () => void
  checkAuth: () => Promise<void>
}

export const useAuth = create<AuthState>((set) => ({
  user: null,
  loading: true,

  login: async (email, password) => {
    const { user } = await authService.login(email, password)
    set({ user })
  },

  register: async (email, password, name) => {
    const { user } = await authService.register(email, password, name)
    set({ user })
  },

  logout: () => {
    authService.logout()
    set({ user: null })
  },

  checkAuth: async () => {
    set({ loading: true })
    const user = await authService.getCurrentUser()
    set({ user, loading: false })
  },
}))
"""

def generate_use_api_hook() -> str:
    return """import { useState, useCallback } from 'react'
import { dataApi } from '@/services/api'

export function useApi<T = any>(resource: string) {
  const [data, setData] = useState<T[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchAll = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await dataApi.getAll(resource)
      setData(response.data)
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [resource])

  const create = useCallback(async (newData: Partial<T>) => {
    setLoading(true)
    try {
      const response = await dataApi.create(resource, newData)
      setData((prev) => [...prev, response.data])
      return response.data
    } catch (err: any) {
      setError(err.message)
      throw err
    } finally {
      setLoading(false)
    }
  }, [resource])

  const update = useCallback(async (id: string, updateData: Partial<T>) => {
    setLoading(true)
    try {
      const response = await dataApi.update(resource, id, updateData)
      setData((prev) => prev.map((item: any) => item.id === id ? response.data : item))
      return response.data
    } catch (err: any) {
      setError(err.message)
      throw err
    } finally {
      setLoading(false)
    }
  }, [resource])

  const remove = useCallback(async (id: string) => {
    setLoading(true)
    try {
      await dataApi.delete(resource, id)
      setData((prev) => prev.filter((item: any) => item.id !== id))
    } catch (err: any) {
      setError(err.message)
      throw err
    } finally {
      setLoading(false)
    }
  }, [resource])

  return { data, loading, error, fetchAll, create, update, remove }
}
"""

def generate_store_index() -> str:
    return """export { useAuth } from '@/hooks/useAuth'
// Add more stores here as needed
"""

def generate_auth_store() -> str:
    return """// Re-export from hook for consistency
export { useAuth } from '@/hooks/useAuth'
"""

def generate_types_index(app_type: str) -> str:
    return """// Global types for the application

export interface User {
  id: string
  email: string
  name: string
  avatar?: string
  createdAt: string
}

export interface ApiResponse<T> {
  data: T
  message?: string
  success: boolean
}

export interface PaginatedResponse<T> {
  data: T[]
  total: number
  page: number
  pageSize: number
}

// Add app-specific types below
"""

def generate_helpers() -> str:
    return """// Utility helper functions

export function formatDate(date: string | Date): string {
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  }).format(new Date(date))
}

export function formatCurrency(amount: number, currency = 'USD'): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
  }).format(amount)
}

export function cn(...classes: (string | boolean | undefined)[]): string {
  return classes.filter(Boolean).join(' ')
}

export function debounce<T extends (...args: any[]) => any>(
  fn: T,
  delay: number
): (...args: Parameters<T>) => void {
  let timeoutId: ReturnType<typeof setTimeout>
  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId)
    timeoutId = setTimeout(() => fn(...args), delay)
  }
}

export function truncate(str: string, length: number): string {
  return str.length > length ? str.slice(0, length) + '...' : str
}
"""

def generate_constants() -> str:
    return """// Application constants

export const APP_NAME = 'GAAIUS App'

export const API_ROUTES = {
  AUTH: {
    LOGIN: '/api/auth/login',
    REGISTER: '/api/auth/register',
    ME: '/api/auth/me',
  },
  // Add more routes as needed
}

export const BREAKPOINTS = {
  sm: 640,
  md: 768,
  lg: 1024,
  xl: 1280,
}

export const COLORS = {
  primary: '#7c3aed',
  secondary: '#06b6d4',
  success: '#10b981',
  warning: '#f59e0b',
  danger: '#ef4444',
}
"""

def generate_pages_index(pages: List[dict]) -> str:
    exports = []
    for page in pages:
        name = page.get("name", "Page").replace(" ", "")
        exports.append(f"export {{ default as {name} }} from './{name}'")
    return "\n".join(exports)

def generate_dashboard_page(app_type: str, features: List[str]) -> str:
    """Generate the main Dashboard page based on app type"""
    
    # Stats based on app type
    stats = [
        {"label": "Total Users", "value": "12,345", "change": "+12%", "icon": "Users"},
        {"label": "Revenue", "value": "$45,678", "change": "+8%", "icon": "DollarSign"},
        {"label": "Active Now", "value": "234", "change": "+3%", "icon": "Activity"},
        {"label": "Growth", "value": "23%", "change": "+5%", "icon": "TrendingUp"},
    ]
    
    return f"""import {{ {', '.join([s['icon'] for s in stats])} }} from 'lucide-react'
import Card from '@/components/Card'

const stats = {json.dumps(stats, indent=2)}

export default function Dashboard() {{
  return (
    <div className="space-y-8 animate-fade-in">
      <div>
        <h1 className="text-3xl font-bold mb-2">Dashboard</h1>
        <p className="text-white/60">Welcome back! Here's what's happening.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {{stats.map((stat, i) => (
          <Card key={{i}} className="relative overflow-hidden">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-white/60 text-sm">{{stat.label}}</p>
                <p className="text-2xl font-bold mt-1">{{stat.value}}</p>
                <p className="text-emerald-400 text-sm mt-1">{{stat.change}} from last month</p>
              </div>
              <div className="w-12 h-12 bg-primary-600/20 rounded-xl flex items-center justify-center">
                {{stat.icon === 'Users' && <Users className="w-6 h-6 text-primary-500" />}}
                {{stat.icon === 'DollarSign' && <DollarSign className="w-6 h-6 text-primary-500" />}}
                {{stat.icon === 'Activity' && <Activity className="w-6 h-6 text-primary-500" />}}
                {{stat.icon === 'TrendingUp' && <TrendingUp className="w-6 h-6 text-primary-500" />}}
              </div>
            </div>
          </Card>
        ))}}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card title="Recent Activity" className="col-span-1">
          <div className="space-y-4">
            {{[1,2,3,4,5].map((i) => (
              <div key={{i}} className="flex items-center gap-4 py-2 border-b border-white/5 last:border-0">
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary-500 to-cyan-500 flex items-center justify-center text-sm font-bold">
                  {{String.fromCharCode(64 + i)}}
                </div>
                <div className="flex-1">
                  <p className="text-sm">User {{i}} completed an action</p>
                  <p className="text-xs text-white/40">{{i}} hour{{i > 1 ? 's' : ''}} ago</p>
                </div>
              </div>
            ))}}
          </div>
        </Card>

        <Card title="Quick Actions" className="col-span-1">
          <div className="grid grid-cols-2 gap-4">
            <button className="p-4 bg-primary-600/20 hover:bg-primary-600/30 rounded-xl text-left transition">
              <Users className="w-6 h-6 text-primary-500 mb-2" />
              <p className="font-medium">Add User</p>
              <p className="text-xs text-white/40">Create new account</p>
            </button>
            <button className="p-4 bg-cyan-600/20 hover:bg-cyan-600/30 rounded-xl text-left transition">
              <Activity className="w-6 h-6 text-cyan-500 mb-2" />
              <p className="font-medium">View Reports</p>
              <p className="text-xs text-white/40">Analytics dashboard</p>
            </button>
            <button className="p-4 bg-emerald-600/20 hover:bg-emerald-600/30 rounded-xl text-left transition">
              <DollarSign className="w-6 h-6 text-emerald-500 mb-2" />
              <p className="font-medium">Payments</p>
              <p className="text-xs text-white/40">Manage billing</p>
            </button>
            <button className="p-4 bg-amber-600/20 hover:bg-amber-600/30 rounded-xl text-left transition">
              <TrendingUp className="w-6 h-6 text-amber-500 mb-2" />
              <p className="font-medium">Growth</p>
              <p className="text-xs text-white/40">Track metrics</p>
            </button>
          </div>
        </Card>
      </div>
    </div>
  )
}}
"""

def generate_settings_page() -> str:
    return """import { useState } from 'react'
import { Save, User, Bell, Shield, Palette } from 'lucide-react'
import Card from '@/components/Card'
import Button from '@/components/Button'

export default function Settings() {
  const [activeTab, setActiveTab] = useState('profile')

  const tabs = [
    { id: 'profile', label: 'Profile', icon: User },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'security', label: 'Security', icon: Shield },
    { id: 'appearance', label: 'Appearance', icon: Palette },
  ]

  return (
    <div className="space-y-8 animate-fade-in">
      <div>
        <h1 className="text-3xl font-bold mb-2">Settings</h1>
        <p className="text-white/60">Manage your account preferences.</p>
      </div>

      <div className="flex gap-6">
        <Card className="w-64 h-fit">
          <nav className="space-y-1">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition ${
                  activeTab === tab.id
                    ? 'bg-primary-600/20 text-primary-500'
                    : 'text-white/60 hover:bg-white/5 hover:text-white'
                }`}
              >
                <tab.icon className="w-5 h-5" />
                {tab.label}
              </button>
            ))}
          </nav>
        </Card>

        <Card className="flex-1">
          {activeTab === 'profile' && (
            <div className="space-y-6">
              <h2 className="text-xl font-semibold">Profile Settings</h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm text-white/60 mb-2">Full Name</label>
                  <input
                    type="text"
                    defaultValue="John Doe"
                    className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 focus:outline-none focus:border-primary-500"
                  />
                </div>
                <div>
                  <label className="block text-sm text-white/60 mb-2">Email</label>
                  <input
                    type="email"
                    defaultValue="john@example.com"
                    className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 focus:outline-none focus:border-primary-500"
                  />
                </div>
                <div>
                  <label className="block text-sm text-white/60 mb-2">Bio</label>
                  <textarea
                    rows={3}
                    className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 focus:outline-none focus:border-primary-500"
                    placeholder="Tell us about yourself..."
                  />
                </div>
              </div>
              <Button>
                <Save className="w-4 h-4" /> Save Changes
              </Button>
            </div>
          )}

          {activeTab === 'notifications' && (
            <div className="space-y-6">
              <h2 className="text-xl font-semibold">Notification Preferences</h2>
              <div className="space-y-4">
                {['Email notifications', 'Push notifications', 'SMS alerts', 'Weekly digest'].map((item) => (
                  <label key={item} className="flex items-center justify-between p-4 bg-white/5 rounded-xl cursor-pointer hover:bg-white/10 transition">
                    <span>{item}</span>
                    <input type="checkbox" className="w-5 h-5 accent-primary-500" defaultChecked />
                  </label>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'security' && (
            <div className="space-y-6">
              <h2 className="text-xl font-semibold">Security Settings</h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm text-white/60 mb-2">Current Password</label>
                  <input type="password" className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 focus:outline-none focus:border-primary-500" />
                </div>
                <div>
                  <label className="block text-sm text-white/60 mb-2">New Password</label>
                  <input type="password" className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 focus:outline-none focus:border-primary-500" />
                </div>
                <div>
                  <label className="block text-sm text-white/60 mb-2">Confirm New Password</label>
                  <input type="password" className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 focus:outline-none focus:border-primary-500" />
                </div>
              </div>
              <Button>Update Password</Button>
            </div>
          )}

          {activeTab === 'appearance' && (
            <div className="space-y-6">
              <h2 className="text-xl font-semibold">Appearance</h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm text-white/60 mb-3">Theme</label>
                  <div className="grid grid-cols-3 gap-4">
                    {['Dark', 'Light', 'System'].map((theme) => (
                      <button
                        key={theme}
                        className={`p-4 rounded-xl border text-center transition ${
                          theme === 'Dark' ? 'border-primary-500 bg-primary-600/20' : 'border-white/10 hover:border-white/30'
                        }`}
                      >
                        {theme}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}
        </Card>
      </div>
    </div>
  )
}
"""

def generate_profile_page() -> str:
    return """import { Camera, Mail, MapPin, Calendar, Edit } from 'lucide-react'
import Card from '@/components/Card'
import Button from '@/components/Button'

export default function Profile() {
  return (
    <div className="space-y-8 animate-fade-in">
      <div>
        <h1 className="text-3xl font-bold mb-2">Profile</h1>
        <p className="text-white/60">View and edit your profile information.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-1">
          <div className="text-center">
            <div className="relative inline-block">
              <div className="w-32 h-32 rounded-full bg-gradient-to-br from-primary-500 to-cyan-500 flex items-center justify-center text-4xl font-bold mx-auto">
                JD
              </div>
              <button className="absolute bottom-0 right-0 w-10 h-10 bg-primary-600 rounded-full flex items-center justify-center hover:bg-primary-700 transition">
                <Camera className="w-5 h-5" />
              </button>
            </div>
            <h2 className="text-xl font-semibold mt-4">John Doe</h2>
            <p className="text-white/60">Senior Developer</p>
            
            <div className="mt-6 space-y-3 text-left">
              <div className="flex items-center gap-3 text-sm">
                <Mail className="w-4 h-4 text-white/40" />
                <span className="text-white/60">john@example.com</span>
              </div>
              <div className="flex items-center gap-3 text-sm">
                <MapPin className="w-4 h-4 text-white/40" />
                <span className="text-white/60">San Francisco, CA</span>
              </div>
              <div className="flex items-center gap-3 text-sm">
                <Calendar className="w-4 h-4 text-white/40" />
                <span className="text-white/60">Joined Jan 2024</span>
              </div>
            </div>
            
            <Button variant="secondary" className="w-full mt-6">
              <Edit className="w-4 h-4" /> Edit Profile
            </Button>
          </div>
        </Card>

        <Card className="lg:col-span-2" title="Activity Overview">
          <div className="grid grid-cols-3 gap-4 mb-6">
            <div className="text-center p-4 bg-white/5 rounded-xl">
              <p className="text-2xl font-bold text-primary-500">127</p>
              <p className="text-sm text-white/60">Projects</p>
            </div>
            <div className="text-center p-4 bg-white/5 rounded-xl">
              <p className="text-2xl font-bold text-cyan-500">45</p>
              <p className="text-sm text-white/60">Followers</p>
            </div>
            <div className="text-center p-4 bg-white/5 rounded-xl">
              <p className="text-2xl font-bold text-emerald-500">89</p>
              <p className="text-sm text-white/60">Following</p>
            </div>
          </div>

          <h3 className="font-semibold mb-4">Recent Activity</h3>
          <div className="space-y-4">
            {[
              { action: 'Created a new project', time: '2 hours ago' },
              { action: 'Updated profile settings', time: '1 day ago' },
              { action: 'Completed milestone', time: '3 days ago' },
              { action: 'Joined team "Alpha"', time: '1 week ago' },
            ].map((item, i) => (
              <div key={i} className="flex items-center justify-between py-2 border-b border-white/5 last:border-0">
                <span>{item.action}</span>
                <span className="text-sm text-white/40">{item.time}</span>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  )
}
"""

def generate_notfound_page() -> str:
    return """import { Link } from 'react-router-dom'
import { Home, ArrowLeft } from 'lucide-react'
import Button from '@/components/Button'

export default function NotFound() {
  return (
    <div className="min-h-[60vh] flex items-center justify-center animate-fade-in">
      <div className="text-center">
        <h1 className="text-9xl font-bold text-white/10">404</h1>
        <h2 className="text-2xl font-semibold mt-4">Page Not Found</h2>
        <p className="text-white/60 mt-2 mb-8">
          The page you're looking for doesn't exist or has been moved.
        </p>
        <div className="flex gap-4 justify-center">
          <Link to="/">
            <Button>
              <Home className="w-4 h-4" /> Go Home
            </Button>
          </Link>
          <Button variant="secondary" onClick={() => window.history.back()}>
            <ArrowLeft className="w-4 h-4" /> Go Back
          </Button>
        </div>
      </div>
    </div>
  )
}
"""

# Backend generators
def generate_backend_server() -> str:
    return """import express from 'express'
import cors from 'cors'
import dotenv from 'dotenv'
import { connectDB } from './config/database.js'
import authRoutes from './routes/auth.js'
import apiRoutes from './routes/api.js'
import { errorHandler } from './middleware/errorHandler.js'

dotenv.config()

const app = express()

// Middleware
app.use(cors())
app.use(express.json())

// Connect to database
connectDB()

// Routes
app.use('/api/auth', authRoutes)
app.use('/api', apiRoutes)

// Health check
app.get('/api/health', (req, res) => {
  res.json({ status: 'healthy', timestamp: new Date().toISOString() })
})

// Error handling
app.use(errorHandler)

const PORT = process.env.PORT || 8001
app.listen(PORT, () => {
  console.log(`🚀 Server running on port ${PORT}`)
})
"""

def generate_backend_routes_index() -> str:
    return """export { default as authRoutes } from './auth.js'
export { default as apiRoutes } from './api.js'
"""

def generate_backend_auth_routes() -> str:
    return """import { Router } from 'express'
import { login, register, me } from '../controllers/authController.js'
import { authMiddleware } from '../middleware/auth.js'

const router = Router()

router.post('/login', login)
router.post('/register', register)
router.get('/me', authMiddleware, me)

export default router
"""

def generate_backend_api_routes() -> str:
    return """import { Router } from 'express'
import { getAll, getOne, create, update, remove } from '../controllers/apiController.js'
import { authMiddleware } from '../middleware/auth.js'

const router = Router()

// Protected routes
router.use(authMiddleware)

router.get('/:resource', getAll)
router.get('/:resource/:id', getOne)
router.post('/:resource', create)
router.put('/:resource/:id', update)
router.delete('/:resource/:id', remove)

export default router
"""

def generate_backend_auth_controller() -> str:
    return """import jwt from 'jsonwebtoken'
import bcrypt from 'bcryptjs'
import User from '../models/User.js'

export const login = async (req, res, next) => {
  try {
    const { email, password } = req.body
    
    const user = await User.findOne({ email })
    if (!user) {
      return res.status(401).json({ message: 'Invalid credentials' })
    }
    
    const isMatch = await bcrypt.compare(password, user.password)
    if (!isMatch) {
      return res.status(401).json({ message: 'Invalid credentials' })
    }
    
    const token = jwt.sign(
      { userId: user._id, email: user.email },
      process.env.JWT_SECRET,
      { expiresIn: '30d' }
    )
    
    res.json({
      token,
      user: {
        id: user._id,
        email: user.email,
        name: user.name,
      },
    })
  } catch (error) {
    next(error)
  }
}

export const register = async (req, res, next) => {
  try {
    const { email, password, name } = req.body
    
    const existingUser = await User.findOne({ email })
    if (existingUser) {
      return res.status(400).json({ message: 'Email already registered' })
    }
    
    const hashedPassword = await bcrypt.hash(password, 12)
    
    const user = new User({
      email,
      password: hashedPassword,
      name,
    })
    
    await user.save()
    
    const token = jwt.sign(
      { userId: user._id, email: user.email },
      process.env.JWT_SECRET,
      { expiresIn: '30d' }
    )
    
    res.status(201).json({
      token,
      user: {
        id: user._id,
        email: user.email,
        name: user.name,
      },
    })
  } catch (error) {
    next(error)
  }
}

export const me = async (req, res, next) => {
  try {
    const user = await User.findById(req.userId).select('-password')
    if (!user) {
      return res.status(404).json({ message: 'User not found' })
    }
    res.json(user)
  } catch (error) {
    next(error)
  }
}
"""

def generate_backend_api_controller() -> str:
    return """// Generic CRUD controller for any resource
// In production, you'd have specific controllers for each model

export const getAll = async (req, res, next) => {
  try {
    const { resource } = req.params
    // In production: const Model = getModel(resource)
    // const items = await Model.find()
    res.json({ data: [], message: `GET all ${resource}` })
  } catch (error) {
    next(error)
  }
}

export const getOne = async (req, res, next) => {
  try {
    const { resource, id } = req.params
    res.json({ data: { id }, message: `GET ${resource}/${id}` })
  } catch (error) {
    next(error)
  }
}

export const create = async (req, res, next) => {
  try {
    const { resource } = req.params
    res.status(201).json({ data: req.body, message: `Created ${resource}` })
  } catch (error) {
    next(error)
  }
}

export const update = async (req, res, next) => {
  try {
    const { resource, id } = req.params
    res.json({ data: { id, ...req.body }, message: `Updated ${resource}/${id}` })
  } catch (error) {
    next(error)
  }
}

export const remove = async (req, res, next) => {
  try {
    const { resource, id } = req.params
    res.json({ message: `Deleted ${resource}/${id}` })
  } catch (error) {
    next(error)
  }
}
"""

def generate_user_model() -> str:
    return """import mongoose from 'mongoose'

const userSchema = new mongoose.Schema({
  email: {
    type: String,
    required: true,
    unique: true,
    lowercase: true,
  },
  password: {
    type: String,
    required: true,
  },
  name: {
    type: String,
    required: true,
  },
  avatar: {
    type: String,
  },
  role: {
    type: String,
    enum: ['user', 'admin'],
    default: 'user',
  },
}, {
  timestamps: true,
})

export default mongoose.model('User', userSchema)
"""

def generate_auth_middleware() -> str:
    return """import jwt from 'jsonwebtoken'

export const authMiddleware = (req, res, next) => {
  try {
    const authHeader = req.headers.authorization
    
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res.status(401).json({ message: 'Authentication required' })
    }
    
    const token = authHeader.split(' ')[1]
    const decoded = jwt.verify(token, process.env.JWT_SECRET)
    
    req.userId = decoded.userId
    req.userEmail = decoded.email
    
    next()
  } catch (error) {
    return res.status(401).json({ message: 'Invalid or expired token' })
  }
}
"""

def generate_error_handler() -> str:
    return """export const errorHandler = (err, req, res, next) => {
  console.error('Error:', err.message)
  
  if (err.name === 'ValidationError') {
    return res.status(400).json({
      message: 'Validation Error',
      errors: Object.values(err.errors).map(e => e.message),
    })
  }
  
  if (err.name === 'CastError') {
    return res.status(400).json({ message: 'Invalid ID format' })
  }
  
  if (err.code === 11000) {
    return res.status(400).json({ message: 'Duplicate key error' })
  }
  
  res.status(500).json({
    message: process.env.NODE_ENV === 'production' 
      ? 'Internal server error' 
      : err.message,
  })
}
"""

def generate_database_config() -> str:
    return """import mongoose from 'mongoose'

export const connectDB = async () => {
  try {
    const conn = await mongoose.connect(process.env.MONGO_URL)
    console.log(`📦 MongoDB Connected: ${conn.connection.host}`)
  } catch (error) {
    console.error('Database connection error:', error.message)
    process.exit(1)
  }
}
"""

def generate_env_config() -> str:
    return """import dotenv from 'dotenv'

dotenv.config()

export const config = {
  port: process.env.PORT || 8001,
  nodeEnv: process.env.NODE_ENV || 'development',
  mongoUrl: process.env.MONGO_URL,
  jwtSecret: process.env.JWT_SECRET,
}
"""

def generate_backend_helpers() -> str:
    return """// Backend utility functions

export const asyncHandler = (fn) => (req, res, next) => {
  Promise.resolve(fn(req, res, next)).catch(next)
}

export const generateId = () => {
  return Math.random().toString(36).substring(2) + Date.now().toString(36)
}

export const paginate = (page = 1, limit = 10) => {
  const skip = (page - 1) * limit
  return { skip, limit }
}
"""

def generate_backend_types() -> str:
    return """// TypeScript types for backend

export interface UserPayload {
  userId: string
  email: string
}

declare global {
  namespace Express {
    interface Request {
      userId?: string
      userEmail?: string
    }
  }
}
"""

# Shared types
def generate_shared_types() -> str:
    return """// Shared types between frontend and backend

export interface User {
  id: string
  email: string
  name: string
  avatar?: string
  role: 'user' | 'admin'
  createdAt: string
  updatedAt: string
}

export interface AuthResponse {
  token: string
  user: Omit<User, 'createdAt' | 'updatedAt'>
}

export interface ApiError {
  message: string
  errors?: string[]
}
"""

def generate_shared_schemas() -> str:
    return """// Validation schemas (using Zod)
import { z } from 'zod'

export const loginSchema = z.object({
  email: z.string().email('Invalid email'),
  password: z.string().min(6, 'Password must be at least 6 characters'),
})

export const registerSchema = z.object({
  email: z.string().email('Invalid email'),
  password: z.string().min(6, 'Password must be at least 6 characters'),
  name: z.string().min(2, 'Name must be at least 2 characters'),
})

export type LoginInput = z.infer<typeof loginSchema>
export type RegisterInput = z.infer<typeof registerSchema>
"""

def generate_shared_constants() -> str:
    return """// Shared constants

export const API_VERSION = 'v1'
export const TOKEN_EXPIRY = '30d'

export const USER_ROLES = {
  USER: 'user',
  ADMIN: 'admin',
} as const

export const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  INTERNAL_ERROR: 500,
} as const
"""

def generate_shared_utils() -> str:
    return """// Shared utility functions

export const formatDate = (date: string | Date): string => {
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  }).format(new Date(date))
}

export const sleep = (ms: number): Promise<void> => {
  return new Promise(resolve => setTimeout(resolve, ms))
}

export const capitalizeFirst = (str: string): string => {
  return str.charAt(0).toUpperCase() + str.slice(1)
}
"""

# Config files
def generate_app_config(app_name: str, app_type: str, features: List[str]) -> str:
    return json.dumps({
        "name": app_name,
        "version": "1.0.0",
        "type": app_type,
        "description": f"{app_name} - Built with GAAIUS PROJECT RUNTIME",
        "features": features,
        "theme": "dark",
        "framework": {
            "frontend": "react-vite",
            "backend": "express",
            "database": "mongodb"
        }
    }, indent=2)

def generate_build_config() -> str:
    return json.dumps({
        "targets": {
            "web": {"enabled": True, "port": 3000},
            "mobile": {"enabled": False, "framework": "capacitor"},
            "desktop": {"enabled": False, "framework": "tauri"}
        },
        "optimization": {
            "minify": True,
            "treeshake": True,
            "sourcemap": False
        },
        "env": {
            "development": ".env.development",
            "production": ".env.production"
        }
    }, indent=2)

def generate_deploy_config() -> str:
    return json.dumps({
        "provider": "vercel",
        "regions": ["iad1"],
        "buildCommand": "npm run build",
        "outputDirectory": "dist",
        "installCommand": "npm install",
        "framework": "vite"
    }, indent=2)


# ============================================================================
# MAIN PROJECT GENERATOR CLASS
# ============================================================================

class GaaiusProjectRuntime:
    """
    GAAIUS PROJECT RUNTIME v1.0
    
    Generates full enterprise-grade project scaffolds with:
    - React + Vite + TypeScript frontend
    - Express + TypeScript backend
    - MongoDB integration
    - Full file structure
    - Working code in all files
    """
    
    def __init__(self):
        self.version = "1.0.0"
    
    def generate_project_scaffold(
        self,
        app_name: str,
        app_type: str,
        blueprint: dict,
        existing_files: Optional[Dict[str, str]] = None
    ) -> Dict[str, str]:
        """
        Generate a complete project scaffold.
        
        Args:
            app_name: Name of the application
            app_type: Type (saas, ecommerce, admin, etc.)
            blueprint: The AI-generated blueprint
            existing_files: Optional existing files to preserve/merge
        
        Returns:
            Dictionary of filepath -> file content
        """
        
        files = {}
        pages = blueprint.get("pages", [])
        features = blueprint.get("features", [])
        
        # === FRONTEND FILES ===
        files["frontend/package.json"] = get_default_package_json(app_name, is_frontend=True)
        files["frontend/vite.config.ts"] = get_vite_config()
        files["frontend/tsconfig.json"] = get_tsconfig_frontend()
        files["frontend/index.html"] = get_index_html(app_name)
        files["frontend/tailwind.config.js"] = get_tailwind_config()
        files["frontend/postcss.config.js"] = get_postcss_config()
        
        # Source files
        files["frontend/src/main.tsx"] = get_main_tsx()
        files["frontend/src/App.tsx"] = generate_app_tsx(app_name, pages, app_type)
        files["frontend/src/index.css"] = get_index_css()
        files["frontend/src/vite-env.d.ts"] = get_vite_env_d_ts()
        
        # Components
        files["frontend/src/components/index.ts"] = generate_components_index()
        files["frontend/src/components/Layout.tsx"] = generate_layout_component(app_name, app_type)
        files["frontend/src/components/Sidebar.tsx"] = generate_sidebar_component(pages, app_type)
        files["frontend/src/components/Header.tsx"] = generate_header_component()
        files["frontend/src/components/Card.tsx"] = generate_card_component()
        files["frontend/src/components/Button.tsx"] = generate_button_component()
        files["frontend/src/components/Modal.tsx"] = generate_modal_component()
        files["frontend/src/components/Table.tsx"] = generate_table_component()
        
        # Services
        files["frontend/src/services/api.ts"] = generate_api_service()
        files["frontend/src/services/auth.ts"] = generate_auth_service()
        
        # Hooks
        files["frontend/src/hooks/useAuth.ts"] = generate_auth_hook()
        files["frontend/src/hooks/useApi.ts"] = generate_use_api_hook()
        
        # Store
        files["frontend/src/store/index.ts"] = generate_store_index()
        files["frontend/src/store/authStore.ts"] = generate_auth_store()
        
        # Types & Utils
        files["frontend/src/types/index.ts"] = generate_types_index(app_type)
        files["frontend/src/utils/helpers.ts"] = generate_helpers()
        files["frontend/src/utils/constants.ts"] = generate_constants()
        
        # Pages
        files["frontend/src/pages/index.ts"] = generate_pages_index(pages if pages else [
            {"name": "Dashboard", "path": "/"},
            {"name": "Settings", "path": "/settings"},
            {"name": "Profile", "path": "/profile"}
        ])
        files["frontend/src/pages/Dashboard.tsx"] = generate_dashboard_page(app_type, features)
        files["frontend/src/pages/Settings.tsx"] = generate_settings_page()
        files["frontend/src/pages/Profile.tsx"] = generate_profile_page()
        files["frontend/src/pages/NotFound.tsx"] = generate_notfound_page()
        
        # === BACKEND FILES ===
        files["backend/package.json"] = get_default_package_json(app_name, is_frontend=False)
        files["backend/tsconfig.json"] = get_tsconfig_backend()
        files["backend/src/server.ts"] = generate_backend_server()
        files["backend/src/routes/index.ts"] = generate_backend_routes_index()
        files["backend/src/routes/auth.ts"] = generate_backend_auth_routes()
        files["backend/src/routes/api.ts"] = generate_backend_api_routes()
        files["backend/src/controllers/authController.ts"] = generate_backend_auth_controller()
        files["backend/src/controllers/apiController.ts"] = generate_backend_api_controller()
        files["backend/src/models/User.ts"] = generate_user_model()
        files["backend/src/middleware/auth.ts"] = generate_auth_middleware()
        files["backend/src/middleware/errorHandler.ts"] = generate_error_handler()
        files["backend/src/config/database.ts"] = generate_database_config()
        files["backend/src/config/env.ts"] = generate_env_config()
        files["backend/src/utils/helpers.ts"] = generate_backend_helpers()
        files["backend/src/types/index.ts"] = generate_backend_types()
        
        # === SHARED FILES ===
        files["shared/types.ts"] = generate_shared_types()
        files["shared/schemas.ts"] = generate_shared_schemas()
        files["shared/constants.ts"] = generate_shared_constants()
        files["shared/utils.ts"] = generate_shared_utils()
        
        # === CONFIG FILES ===
        files["config/app.json"] = generate_app_config(app_name, app_type, features)
        files["config/build.json"] = generate_build_config()
        files["config/deploy.json"] = generate_deploy_config()
        
        # === ROOT FILES ===
        files[".env.example"] = get_env_example()
        files[".gitignore"] = get_gitignore()
        files["README.md"] = get_readme(app_name, app_type, features)
        files["gaaius.json"] = get_gaaius_json(app_name, app_type, blueprint)
        
        # If existing files were provided, merge them (user modifications take priority)
        if existing_files:
            for filepath, content in existing_files.items():
                if content and len(content.strip()) > 0:
                    files[filepath] = content
        
        return files
    
    def update_project_files(
        self,
        existing_files: Dict[str, str],
        modifications: Dict[str, str]
    ) -> Dict[str, str]:
        """
        Update existing project files with modifications.
        Used for iterative building.
        """
        updated = existing_files.copy()
        updated.update(modifications)
        return updated


# ============================================================================
# SHELL SCRIPTS FOR LOCAL DEVELOPMENT
# ============================================================================

def generate_run_scripts(app_name: str) -> Dict[str, str]:
    """Generate shell scripts to run the project locally"""
    
    # Windows batch script
    run_bat = f"""@echo off
echo ========================================
echo  GAAIUS PROJECT RUNTIME - {app_name}
echo ========================================
echo.

echo [1/4] Installing frontend dependencies...
cd frontend
call npm install
if errorlevel 1 (
    echo ERROR: Frontend installation failed
    pause
    exit /b 1
)

echo.
echo [2/4] Installing backend dependencies...
cd ../backend
call npm install
if errorlevel 1 (
    echo ERROR: Backend installation failed
    pause
    exit /b 1
)

echo.
echo [3/4] Starting backend server...
start cmd /k "npm run dev"

echo.
echo [4/4] Starting frontend server...
cd ../frontend
start cmd /k "npm run dev"

echo.
echo ========================================
echo  {app_name} is now running!
echo ========================================
echo  Frontend: http://localhost:3000
echo  Backend:  http://localhost:8001
echo ========================================
pause
"""

    # Unix/Mac shell script
    run_sh = f"""#!/bin/bash

echo "========================================"
echo " GAAIUS PROJECT RUNTIME - {app_name}"
echo "========================================"
echo ""

# Colors
RED='\\033[0;31m'
GREEN='\\033[0;32m'
CYAN='\\033[0;36m'
NC='\\033[0m' # No Color

echo -e "${{CYAN}}[1/4] Installing frontend dependencies...${{NC}}"
cd frontend
npm install
if [ $? -ne 0 ]; then
    echo -e "${{RED}}ERROR: Frontend installation failed${{NC}}"
    exit 1
fi
echo -e "${{GREEN}}✓ Frontend dependencies installed${{NC}}"

echo ""
echo -e "${{CYAN}}[2/4] Installing backend dependencies...${{NC}}"
cd ../backend
npm install
if [ $? -ne 0 ]; then
    echo -e "${{RED}}ERROR: Backend installation failed${{NC}}"
    exit 1
fi
echo -e "${{GREEN}}✓ Backend dependencies installed${{NC}}"

echo ""
echo -e "${{CYAN}}[3/4] Starting backend server...${{NC}}"
npm run dev &
BACKEND_PID=$!
echo -e "${{GREEN}}✓ Backend started (PID: $BACKEND_PID)${{NC}}"

echo ""
echo -e "${{CYAN}}[4/4] Starting frontend server...${{NC}}"
cd ../frontend
npm run dev &
FRONTEND_PID=$!
echo -e "${{GREEN}}✓ Frontend started (PID: $FRONTEND_PID)${{NC}}"

echo ""
echo "========================================"
echo " {app_name} is now running!"
echo "========================================"
echo " Frontend: http://localhost:3000"
echo " Backend:  http://localhost:8001"
echo "========================================"
echo ""
echo "Press Ctrl+C to stop all servers"

# Wait for Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" SIGINT SIGTERM
wait
"""

    # Docker compose for containerized deployment
    docker_compose = f"""version: '3.8'

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - VITE_API_URL=http://backend:8001
    depends_on:
      - backend
    networks:
      - app-network

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8001:8001"
    environment:
      - PORT=8001
      - NODE_ENV=development
      - MONGO_URL=mongodb://mongo:27017/{app_name.lower().replace(' ', '_')}
      - JWT_SECRET=your-super-secret-key-change-in-production
    depends_on:
      - mongo
    networks:
      - app-network

  mongo:
    image: mongo:7
    ports:
      - "27017:27017"
    volumes:
      - mongo-data:/data/db
    networks:
      - app-network

networks:
  app-network:
    driver: bridge

volumes:
  mongo-data:
"""

    # Frontend Dockerfile
    dockerfile_frontend = """FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 3000
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
"""

    # Backend Dockerfile
    dockerfile_backend = """FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 8001
CMD ["npm", "run", "dev"]
"""

    # Makefile for easy commands
    makefile = f"""# GAAIUS PROJECT RUNTIME - {app_name}
# Makefile for easy project management

.PHONY: install dev build test clean docker-up docker-down

# Install all dependencies
install:
\t@echo "Installing dependencies..."
\tcd frontend && npm install
\tcd backend && npm install

# Run development servers
dev:
\t@echo "Starting development servers..."
\t@./run.sh

# Build for production
build:
\t@echo "Building for production..."
\tcd frontend && npm run build
\tcd backend && npm run build

# Run tests
test:
\t@echo "Running tests..."
\tcd frontend && npm test
\tcd backend && npm test

# Clean node_modules and build artifacts
clean:
\t@echo "Cleaning project..."
\trm -rf frontend/node_modules frontend/dist
\trm -rf backend/node_modules backend/dist

# Start with Docker
docker-up:
\t@echo "Starting Docker containers..."
\tdocker-compose up -d

# Stop Docker containers
docker-down:
\t@echo "Stopping Docker containers..."
\tdocker-compose down

# Show project info
info:
\t@echo "========================================"
\t@echo " {app_name}"
\t@echo " Generated with GAAIUS PROJECT RUNTIME"
\t@echo "========================================"
\t@echo " Frontend: React + Vite + TypeScript"
\t@echo " Backend:  Express + TypeScript"
\t@echo " Database: MongoDB"
\t@echo "========================================"
"""

    return {
        "run.bat": run_bat,
        "run.sh": run_sh,
        "docker-compose.yml": docker_compose,
        "docker/Dockerfile.frontend": dockerfile_frontend,
        "docker/Dockerfile.backend": dockerfile_backend,
        "Makefile": makefile
    }


# ============================================================================
# STAGED BUILDING FOR 80,000+ LINE PROJECTS
# ============================================================================

BUILD_STAGES = {
    "stage_1_foundation": {
        "name": "Foundation",
        "description": "Project structure, configs, and base files",
        "files": [
            "package.json", "tsconfig.json", "vite.config.ts",
            ".env.example", ".gitignore", "README.md", "gaaius.json"
        ],
        "estimated_lines": 500
    },
    "stage_2_frontend_core": {
        "name": "Frontend Core",
        "description": "React app structure, routing, and main components",
        "files": [
            "main.tsx", "App.tsx", "index.html", "index.css",
            "Layout.tsx", "Sidebar.tsx", "Header.tsx"
        ],
        "estimated_lines": 2000
    },
    "stage_3_ui_components": {
        "name": "UI Components",
        "description": "Reusable UI component library",
        "files": [
            "Card.tsx", "Button.tsx", "Modal.tsx", "Table.tsx",
            "Input.tsx", "Select.tsx", "Dropdown.tsx", "Alert.tsx",
            "Avatar.tsx", "Badge.tsx", "Tabs.tsx", "Dialog.tsx"
        ],
        "estimated_lines": 3000
    },
    "stage_4_pages": {
        "name": "Application Pages",
        "description": "All main application pages",
        "files": [
            "Dashboard.tsx", "Settings.tsx", "Profile.tsx",
            "Analytics.tsx", "Users.tsx", "Products.tsx",
            "Orders.tsx", "Messages.tsx", "Notifications.tsx"
        ],
        "estimated_lines": 8000
    },
    "stage_5_services": {
        "name": "Frontend Services",
        "description": "API services, auth, state management",
        "files": [
            "api.ts", "auth.ts", "useAuth.ts", "useApi.ts",
            "authStore.ts", "appStore.ts", "helpers.ts", "constants.ts"
        ],
        "estimated_lines": 2000
    },
    "stage_6_backend_core": {
        "name": "Backend Core",
        "description": "Express server, middleware, configuration",
        "files": [
            "server.ts", "auth.ts", "errorHandler.ts",
            "database.ts", "env.ts", "logger.ts"
        ],
        "estimated_lines": 2000
    },
    "stage_7_backend_routes": {
        "name": "Backend Routes & Controllers",
        "description": "API routes and business logic",
        "files": [
            "routes/auth.ts", "routes/api.ts", "routes/users.ts",
            "controllers/authController.ts", "controllers/apiController.ts",
            "controllers/userController.ts"
        ],
        "estimated_lines": 3000
    },
    "stage_8_models_schemas": {
        "name": "Data Models & Schemas",
        "description": "Database models and validation schemas",
        "files": [
            "models/User.ts", "models/Product.ts", "models/Order.ts",
            "schemas.ts", "types.ts", "validators.ts"
        ],
        "estimated_lines": 2000
    },
    "stage_9_advanced_features": {
        "name": "Advanced Features",
        "description": "Real-time, file uploads, notifications, caching",
        "files": [
            "websocket.ts", "upload.ts", "notifications.ts",
            "cache.ts", "queue.ts", "scheduler.ts"
        ],
        "estimated_lines": 4000
    },
    "stage_10_devops": {
        "name": "DevOps & Deployment",
        "description": "Docker, CI/CD, scripts, documentation",
        "files": [
            "Dockerfile", "docker-compose.yml", "run.sh",
            ".github/workflows/ci.yml", "deploy.sh", "ARCHITECTURE.md"
        ],
        "estimated_lines": 1500
    }
}

def get_build_stages() -> Dict:
    """Get all available build stages with their info"""
    return BUILD_STAGES

def calculate_total_lines(stages: List[str] = None) -> int:
    """Calculate total estimated lines for given stages or all stages"""
    if stages is None:
        stages = list(BUILD_STAGES.keys())
    return sum(BUILD_STAGES[s]["estimated_lines"] for s in stages if s in BUILD_STAGES)


# ============================================================================
# MULTI-AGENT ORCHESTRATION SYSTEM
# ============================================================================

AGENT_ROLES = {
    "product_manager": {
        "name": "Product Manager Agent",
        "role": "Analyzes requirements and creates product specifications",
        "outputs": ["product_spec.json", "features.json", "user_stories.json"]
    },
    "architect": {
        "name": "System Architect Agent",
        "role": "Designs system architecture and data models",
        "outputs": ["architecture.md", "schema.prisma", "api_spec.json"]
    },
    "ui_designer": {
        "name": "UI/UX Designer Agent",
        "role": "Creates UI components and design system",
        "outputs": ["design_system.json", "components/", "styles/"]
    },
    "frontend_engineer": {
        "name": "Frontend Engineer Agent",
        "role": "Implements React components and pages",
        "outputs": ["pages/", "components/", "services/", "hooks/"]
    },
    "backend_engineer": {
        "name": "Backend Engineer Agent",
        "role": "Implements API routes and business logic",
        "outputs": ["routes/", "controllers/", "middleware/"]
    },
    "database_architect": {
        "name": "Database Architect Agent",
        "role": "Designs and implements data models",
        "outputs": ["models/", "migrations/", "seed.ts"]
    },
    "devops_engineer": {
        "name": "DevOps Engineer Agent",
        "role": "Sets up deployment and CI/CD",
        "outputs": ["Dockerfile", "docker-compose.yml", ".github/"]
    },
    "qa_validator": {
        "name": "QA Validator Agent",
        "role": "Validates code quality and runs tests",
        "outputs": ["tests/", "coverage/", "validation_report.json"]
    }
}

def get_agent_pipeline(app_complexity: str = "standard") -> List[str]:
    """Get the agent execution pipeline based on app complexity"""
    
    if app_complexity == "simple":
        return ["product_manager", "frontend_engineer", "qa_validator"]
    elif app_complexity == "standard":
        return [
            "product_manager", "architect", "ui_designer",
            "frontend_engineer", "backend_engineer", "qa_validator"
        ]
    else:  # enterprise
        return list(AGENT_ROLES.keys())


# Global instance
gaaius_runtime = GaaiusProjectRuntime()

