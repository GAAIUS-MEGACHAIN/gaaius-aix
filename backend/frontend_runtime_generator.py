"""
FRONTEND RUNTIME GENERATOR - React/Next.js Component Generation
Transforms GAAIUS blueprints into real React components with proper structure
Part of the GAAIUS Project Runtime System
"""

import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path

@dataclass
class ComponentTemplate:
    """Template for a React component"""
    name: str
    template_type: str  # "page", "component", "layout"
    description: str
    code: str


class FrontendRuntimeGenerator:
    """Generates React/Next.js applications from GAAIUS blueprints"""
    
    def __init__(self):
        """Initialize frontend generator"""
        self.components_library = self._init_components_library()
    
    def generate_from_blueprint(self, blueprint: Dict[str, Any], project_path: Path) -> Dict[str, str]:
        """
        Generate React components from a GAAIUS blueprint
        
        Args:
            blueprint: GAAIUS blueprint dictionary
            project_path: Path where to generate files
            
        Returns:
            Dict of created files and their content
        """
        files = {}
        src_path = project_path / "src"
        src_path.mkdir(parents=True, exist_ok=True)
        
        # Generate pages based on blueprint
        if "pages" in blueprint:
            files.update(self._generate_pages(blueprint["pages"], src_path))
        
        # Generate components from blueprint features
        if "features" in blueprint:
            files.update(self._generate_feature_components(blueprint["features"], src_path))
        
        # Generate layout
        if "layout" in blueprint:
            files.update(self._generate_layout(blueprint["layout"], src_path))
        
        # Generate store/state management
        files.update(self._generate_state_management(blueprint, src_path))
        
        # Generate routes
        files.update(self._generate_routes(blueprint, src_path))
        
        # Write all files
        for file_path, content in files.items():
            full_path = project_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)
        
        return files
    
    def _generate_pages(self, pages: List[Dict[str, Any]], src_path: Path) -> Dict[str, str]:
        """Generate page components from blueprint pages"""
        files = {}
        pages_path = "src/pages"
        
        for page in pages:
            page_name = page.get("name", "Page")
            components = page.get("components", [])
            
            code = self._template_page(page_name, components)
            files[f"{pages_path}/{page_name}.tsx"] = code
        
        return files
    
    def _generate_feature_components(self, features: List[str], src_path: Path) -> Dict[str, str]:
        """Generate components based on features"""
        files = {}
        components_path = "src/components"
        
        # Map features to component templates
        feature_components = {
            "auth": ["Login", "Register", "AuthGuard"],
            "cart": ["Cart", "CartItem", "Checkout"],
            "search": ["SearchBar", "SearchResults"],
            "notifications": ["NotificationCenter", "NotificationBell"],
            "profile": ["ProfileCard", "ProfileForm"],
            "dashboard": ["Dashboard", "Stats", "Charts"],
            "export_data": ["ExportButton", "ExportModal"],
            "dark_mode": ["ThemeToggle"],
        }
        
        for feature in features:
            if feature in feature_components:
                for component_name in feature_components[feature]:
                    code = self.components_library.get(component_name, self._template_generic_component(component_name))
                    files[f"{components_path}/{component_name}.tsx"] = code
        
        return files
    
    def _generate_layout(self, layout: Dict[str, Any], src_path: Path) -> Dict[str, str]:
        """Generate layout component based on blueprint"""
        files = {}
        layout_type = layout.get("type", "default")  # "sidebar", "navbar", "default"
        
        if layout_type == "sidebar":
            files["src/components/Layout.tsx"] = self._template_sidebar_layout(layout)
        elif layout_type == "navbar":
            files["src/components/Layout.tsx"] = self._template_navbar_layout(layout)
        else:
            files["src/components/Layout.tsx"] = self._template_default_layout(layout)
        
        return files
    
    def _generate_state_management(self, blueprint: Dict[str, Any], src_path: Path) -> Dict[str, str]:
        """Generate Zustand store for state management"""
        files = {}
        
        files["src/stores/appStore.ts"] = self._template_zustand_store(blueprint)
        files["src/hooks/useStore.ts"] = self._template_use_store_hook()
        
        return files
    
    def _generate_routes(self, blueprint: Dict[str, Any], src_path: Path) -> Dict[str, str]:
        """Generate routing configuration"""
        files = {}
        
        pages = blueprint.get("pages", [])
        routes_code = self._template_routes(pages)
        
        files["src/config/routes.ts"] = routes_code
        
        return files
    
    def _init_components_library(self) -> Dict[str, str]:
        """Initialize standard component templates"""
        return {
            "Login": self._template_login_component(),
            "Register": self._template_register_component(),
            "AuthGuard": self._template_auth_guard_component(),
            "Cart": self._template_cart_component(),
            "CartItem": self._template_cart_item_component(),
            "Checkout": self._template_checkout_component(),
            "SearchBar": self._template_search_bar_component(),
            "SearchResults": self._template_search_results_component(),
            "NotificationCenter": self._template_notification_center_component(),
            "NotificationBell": self._template_notification_bell_component(),
            "ProfileCard": self._template_profile_card_component(),
            "ProfileForm": self._template_profile_form_component(),
            "Dashboard": self._template_dashboard_component(),
            "Stats": self._template_stats_component(),
            "Charts": self._template_charts_component(),
            "ExportButton": self._template_export_button_component(),
            "ExportModal": self._template_export_modal_component(),
            "ThemeToggle": self._template_theme_toggle_component(),
        }
    
    # ===== TEMPLATE METHODS =====
    
    def _template_page(self, name: str, components: List[str]) -> str:
        """Generate a page component"""
        component_imports = "\n".join([f"import {comp} from '@/components/{comp}'" for comp in components])
        component_usage = "\n      ".join([f"<{comp} />" for comp in components])
        
        return f"""import {{ useEffect, useState }} from 'react'
{component_imports}
import {{ useStore }} from '@/hooks/useStore'

export default function {name}Page() {{
  const [loading, setLoading] = useState(false)
  const store = useStore()

  useEffect(() => {{
    // Load data on mount
    setLoading(true)
    // TODO: Fetch data
    setLoading(false)
  }}, [])

  if (loading) {{
    return <div className="flex items-center justify-center min-h-screen">Loading...</div>
  }}

  return (
    <div className="p-8">
      <h1 className="text-4xl font-bold mb-8">{name}</h1>
      <div className="grid gap-6">
        {component_usage}
      </div>
    </div>
  )
}}
"""
    
    def _template_generic_component(self, name: str) -> str:
        """Generate a generic component"""
        return f"""import {{ ReactNode }} from 'react'

interface {name}Props {{
  children?: ReactNode
  className?: string
}}

export default function {name}({{ children, className = '' }}: {name}Props) {{
  return (
    <div className={{"p-4 rounded-lg bg-white dark:bg-gray-800 shadow " + className}}>
      <h3 className="font-semibold mb-4">{name}</h3>
      {{children}}
    </div>
  )
}}
"""
    
    def _template_sidebar_layout(self, layout: Dict[str, Any]) -> str:
        """Generate sidebar layout component"""
        nav_items = layout.get("nav_items", [])
        nav_code = "\n      ".join([f'<a href="/{item.lower()}" className="block px-4 py-2 hover:bg-gray-100">{item}</a>' for item in nav_items])
        
        return """import { ReactNode } from 'react'
import { useState } from 'react'

interface LayoutProps {
  children: ReactNode
}

export default function Layout({ children }: LayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(true)

  return (
    <div className="flex h-screen">
      {/* Sidebar */}
      <aside className={"transition-all " + (sidebarOpen ? 'w-64' : 'w-20') + " bg-gray-900 text-white flex flex-col"}>
        <div className="p-4 border-b border-gray-700">
          <h1 className="text-xl font-bold">App</h1>
        </div>
        <nav className="flex-1 p-4 space-y-2">
          """ + nav_code + """
        </nav>
        <button
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className="p-4 hover:bg-gray-800"
        >
          Toggle
        </button>
      </aside>

      {/* Main */}
      <main className="flex-1 overflow-auto">
        {children}
      </main>
    </div>
  )
}
"""
    
    def _template_navbar_layout(self, layout: Dict[str, Any]) -> str:
        """Generate navbar layout component"""
        nav_items = layout.get("nav_items", [])
        nav_code = "\n          ".join([f'<a href="/{item.lower()}" className="hover:text-gray-300">{item}</a>' for item in nav_items])
        
        return f"""import {{ ReactNode }} from 'react'

interface LayoutProps {{
  children: ReactNode
}}

export default function Layout({{ children }}: LayoutProps) {{
  return (
    <div className="flex flex-col min-h-screen">
      {{/* Navbar */}}
      <nav className="bg-white dark:bg-gray-900 shadow">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <h1 className="text-2xl font-bold">App</h1>
          <div className="flex gap-6">
            {nav_code}
          </div>
        </div>
      </nav>

      {{/* Main */}}
      <main className="flex-1">
        {{children}}
      </main>

      {{/* Footer */}}
      <footer className="bg-gray-100 dark:bg-gray-900 py-8 text-center">
        <p>&copy; 2024 Your App. All rights reserved.</p>
      </footer>
    </div>
  )
}}
"""
    
    def _template_default_layout(self, layout: Dict[str, Any]) -> str:
        """Generate default layout component"""
        return """import { ReactNode } from 'react'

interface LayoutProps {
  children: ReactNode
}

export default function Layout({ children }: LayoutProps) {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <main>
        {children}
      </main>
    </div>
  )
}
"""
    
    def _template_zustand_store(self, blueprint: Dict[str, Any]) -> str:
        """Generate Zustand store"""
        app_type = blueprint.get("app_type", "web")
        
        return f"""import {{ create }} from 'zustand'

interface AppState {{
  user: any | null
  isLoading: boolean
  setUser: (user: any) => void
  setLoading: (loading: boolean) => void
  logout: () => void
}}

export const useAppStore = create<AppState>((set) => ({{
  user: null,
  isLoading: false,
  setUser: (user) => set({{ user }}),
  setLoading: (isLoading) => set({{ isLoading }}),
  logout: () => set({{ user: null }}),
}}))
"""
    
    def _template_use_store_hook(self) -> str:
        """Generate useStore hook"""
        return """import { useAppStore } from '@/stores/appStore'

export function useStore() {
  const user = useAppStore((state) => state.user)
  const isLoading = useAppStore((state) => state.isLoading)
  const setUser = useAppStore((state) => state.setUser)
  const setLoading = useAppStore((state) => state.setLoading)
  const logout = useAppStore((state) => state.logout)

  return {
    user,
    isLoading,
    setUser,
    setLoading,
    logout,
  }
}
"""
    
    def _template_routes(self, pages: List[Dict[str, Any]]) -> str:
        """Generate routes configuration"""
        routes_code = "\n  ".join([
            f'{{ path: "/{page.get("name", "page").lower()}", element: lazy(() => import("@/pages/{page.get("name", "page")}")) }},'
            for page in pages
        ])
        
        return f"""import {{ lazy }} from 'react'

export const routes = [
  {{ path: "/", element: lazy(() => import("@/pages/Home")) }},
  {routes_code}
  {{ path: "*", element: lazy(() => import("@/pages/NotFound")) }},
]
"""
    
    def _template_login_component(self) -> str:
        """Login component template"""
        return """import { useState } from 'react'
import { useStore } from '@/hooks/useStore'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const { setUser } = useStore()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      // TODO: Call login API
      setUser({ email, name: 'User' })
    } catch (err) {
      setError('Login failed')
    }
  }

  return (
    <div className="max-w-md mx-auto p-6 border rounded-lg">
      <h2 className="text-2xl font-bold mb-6">Login</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="w-full px-4 py-2 border rounded"
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full px-4 py-2 border rounded"
          required
        />
        {error && <p className="text-red-600">{error}</p>}
        <button type="submit" className="w-full bg-blue-600 text-white py-2 rounded font-semibold">
          Login
        </button>
      </form>
    </div>
  )
}
"""
    
    def _template_register_component(self) -> str:
        """Register component template"""
        return """import { useState } from 'react'
import api from '@/services/api'

export default function Register() {
  const [formData, setFormData] = useState({ email: '', password: '', name: '' })
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await api.post('/users', formData)
      // Success - redirect to login
    } catch (err) {
      setError('Registration failed')
    }
  }

  return (
    <div className="max-w-md mx-auto p-6 border rounded-lg">
      <h2 className="text-2xl font-bold mb-6">Register</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <input
          type="text"
          placeholder="Full Name"
          value={formData.name}
          onChange={(e) => setFormData({...formData, name: e.target.value})}
          className="w-full px-4 py-2 border rounded"
          required
        />
        <input
          type="email"
          placeholder="Email"
          value={formData.email}
          onChange={(e) => setFormData({...formData, email: e.target.value})}
          className="w-full px-4 py-2 border rounded"
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={formData.password}
          onChange={(e) => setFormData({...formData, password: e.target.value})}
          className="w-full px-4 py-2 border rounded"
          required
        />
        {error && <p className="text-red-600">{error}</p>}
        <button type="submit" className="w-full bg-blue-600 text-white py-2 rounded font-semibold">
          Register
        </button>
      </form>
    </div>
  )
}
"""
    
    def _template_auth_guard_component(self) -> str:
        """AuthGuard component template"""
        return """import { ReactNode } from 'react'
import { Navigate } from 'react-router-dom'
import { useStore } from '@/hooks/useStore'

interface AuthGuardProps {
  children: ReactNode
}

export default function AuthGuard({ children }: AuthGuardProps) {
  const { user } = useStore()

  if (!user) {
    return <Navigate to="/login" replace />
  }

  return <>{children}</>
}
"""
    
    def _template_cart_component(self) -> str:
        """Cart component template"""
        return """import { useState } from 'react'
import CartItem from './CartItem'

export default function Cart() {
  const [items, setItems] = useState([])

  const total = items.reduce((sum, item) => sum + (item.price * item.quantity), 0)

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-4">Shopping Cart</h2>
      <div className="space-y-4">
        {items.length === 0 ? (
          <p>Your cart is empty</p>
        ) : (
          items.map(item => <CartItem key={item.id} item={item} />)
        )}
      </div>
      <div className="mt-8 pt-4 border-t">
        <p className="text-xl font-bold">Total: ${total.toFixed(2)}</p>
        <button className="mt-4 w-full bg-blue-600 text-white py-2 rounded font-semibold">
          Checkout
        </button>
      </div>
    </div>
  )
}
"""
    
    def _template_cart_item_component(self) -> str:
        """CartItem component template"""
        return """interface CartItemProps {
  item: {
    id: string
    name: string
    price: number
    quantity: number
  }
}

export default function CartItem({ item }: CartItemProps) {
  return (
    <div className="flex items-center justify-between p-4 border rounded">
      <div>
        <h3 className="font-semibold">{item.name}</h3>
        <p className="text-gray-600">Qty: {item.quantity}</p>
      </div>
      <p className="font-bold">${(item.price * item.quantity).toFixed(2)}</p>
    </div>
  )
}
"""
    
    def _template_checkout_component(self) -> str:
        """Checkout component template"""
        return """import { useState } from 'react'

export default function Checkout() {
  const [formData, setFormData] = useState({
    address: '',
    city: '',
    zip: '',
    cardNumber: '',
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    // TODO: Process payment
    console.log('Processing payment...', formData)
  }

  return (
    <div className="max-w-2xl mx-auto p-6">
      <h2 className="text-2xl font-bold mb-6">Checkout</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <input
          type="text"
          placeholder="Address"
          value={formData.address}
          onChange={(e) => setFormData({...formData, address: e.target.value})}
          className="w-full px-4 py-2 border rounded"
        />
        <input
          type="text"
          placeholder="City"
          value={formData.city}
          onChange={(e) => setFormData({...formData, city: e.target.value})}
          className="w-full px-4 py-2 border rounded"
        />
        <input
          type="text"
          placeholder="ZIP"
          value={formData.zip}
          onChange={(e) => setFormData({...formData, zip: e.target.value})}
          className="w-full px-4 py-2 border rounded"
        />
        <input
          type="text"
          placeholder="Card Number"
          value={formData.cardNumber}
          onChange={(e) => setFormData({...formData, cardNumber: e.target.value})}
          className="w-full px-4 py-2 border rounded"
        />
        <button type="submit" className="w-full bg-green-600 text-white py-2 rounded font-semibold">
          Complete Purchase
        </button>
      </form>
    </div>
  )
}
"""
    
    def _template_search_bar_component(self) -> str:
        """SearchBar component template"""
        return """import { useState } from 'react'
import { Search } from 'lucide-react'

interface SearchBarProps {
  onSearch: (query: string) => void
}

export default function SearchBar({ onSearch }: SearchBarProps) {
  const [query, setQuery] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSearch(query)
  }

  return (
    <form onSubmit={handleSubmit} className="flex items-center gap-2">
      <input
        type="text"
        placeholder="Search..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        className="flex-1 px-4 py-2 border rounded-lg"
      />
      <button type="submit" className="p-2 bg-blue-600 text-white rounded-lg">
        <Search size={20} />
      </button>
    </form>
  )
}
"""
    
    def _template_search_results_component(self) -> str:
        """SearchResults component template"""
        return """interface SearchResultsProps {
  results: any[]
  loading: boolean
}

export default function SearchResults({ results, loading }: SearchResultsProps) {
  if (loading) return <div>Loading...</div>

  return (
    <div className="space-y-4">
      {results.length === 0 ? (
        <p className="text-gray-600">No results found</p>
      ) : (
        results.map(result => (
          <div key={result.id} className="p-4 border rounded">
            <h3 className="font-semibold">{result.title}</h3>
            <p className="text-gray-600">{result.description}</p>
          </div>
        ))
      )}
    </div>
  )
}
"""
    
    def _template_notification_center_component(self) -> str:
        """NotificationCenter component template"""
        return """import { useState, useEffect } from 'react'

interface Notification {
  id: string
  message: string
  type: 'info' | 'success' | 'error' | 'warning'
}

export default function NotificationCenter() {
  const [notifications, setNotifications] = useState<Notification[]>([])

  const removeNotification = (id: string) => {
    setNotifications(prev => prev.filter(n => n.id !== id))
  }

  return (
    <div className="fixed bottom-4 right-4 space-y-2 max-w-md">
      {notifications.map(notification => (
        <div
          key={notification.id}
          className={`p-4 rounded-lg text-white ${
            notification.type === 'success' ? 'bg-green-600' :
            notification.type === 'error' ? 'bg-red-600' :
            notification.type === 'warning' ? 'bg-yellow-600' :
            'bg-blue-600'
          }`}
        >
          <div className="flex items-center justify-between">
            <p>{notification.message}</p>
            <button onClick={() => removeNotification(notification.id)}>×</button>
          </div>
        </div>
      ))}
    </div>
  )
}
"""
    
    def _template_notification_bell_component(self) -> str:
        """NotificationBell component template"""
        return """import { useState } from 'react'
import { Bell } from 'lucide-react'

export default function NotificationBell() {
  const [unreadCount, setUnreadCount] = useState(3)

  return (
    <button className="relative p-2 hover:bg-gray-100 rounded-lg">
      <Bell size={20} />
      {unreadCount > 0 && (
        <span className="absolute -top-1 -right-1 bg-red-600 text-white text-xs font-bold rounded-full w-5 h-5 flex items-center justify-center">
          {unreadCount}
        </span>
      )}
    </button>
  )
}
"""
    
    def _template_profile_card_component(self) -> str:
        """ProfileCard component template"""
        return """interface ProfileCardProps {
  user: {
    name: string
    email: string
    avatar?: string
  }
}

export default function ProfileCard({ user }: ProfileCardProps) {
  return (
    <div className="p-6 border rounded-lg bg-white">
      <div className="flex items-center gap-4 mb-4">
        {user.avatar ? (
          <img src={user.avatar} alt={user.name} className="w-16 h-16 rounded-full" />
        ) : (
          <div className="w-16 h-16 rounded-full bg-blue-600 flex items-center justify-center text-white font-bold text-xl">
            {user.name.charAt(0)}
          </div>
        )}
        <div>
          <h3 className="text-xl font-bold">{user.name}</h3>
          <p className="text-gray-600">{user.email}</p>
        </div>
      </div>
      <button className="w-full px-4 py-2 border rounded hover:bg-gray-50">
        Edit Profile
      </button>
    </div>
  )
}
"""
    
    def _template_profile_form_component(self) -> str:
        """ProfileForm component template"""
        return """import { useState } from 'react'

interface ProfileFormProps {
  initialData: {
    name: string
    email: string
    bio?: string
  }
  onSave: (data: any) => void
}

export default function ProfileForm({ initialData, onSave }: ProfileFormProps) {
  const [formData, setFormData] = useState(initialData)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSave(formData)
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <input
        type="text"
        placeholder="Name"
        value={formData.name}
        onChange={(e) => setFormData({...formData, name: e.target.value})}
        className="w-full px-4 py-2 border rounded"
      />
      <input
        type="email"
        placeholder="Email"
        value={formData.email}
        onChange={(e) => setFormData({...formData, email: e.target.value})}
        className="w-full px-4 py-2 border rounded"
      />
      <textarea
        placeholder="Bio"
        value={formData.bio || ''}
        onChange={(e) => setFormData({...formData, bio: e.target.value})}
        className="w-full px-4 py-2 border rounded"
        rows={4}
      />
      <button type="submit" className="w-full bg-blue-600 text-white py-2 rounded font-semibold">
        Save Changes
      </button>
    </form>
  )
}
"""
    
    def _template_dashboard_component(self) -> str:
        """Dashboard component template"""
        return """import Stats from './Stats'
import Charts from './Charts'

export default function Dashboard() {
  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-8">Dashboard</h1>
      <Stats />
      <Charts />
    </div>
  )
}
"""
    
    def _template_stats_component(self) -> str:
        """Stats component template"""
        return """export default function Stats() {
  const stats = [
    { label: 'Total Users', value: '1,234' },
    { label: 'Revenue', value: '$45,231' },
    { label: 'Orders', value: '523' },
    { label: 'Conversion', value: '3.2%' },
  ]

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      {stats.map((stat, i) => (
        <div key={i} className="p-6 bg-white rounded-lg shadow">
          <p className="text-gray-600 text-sm">{stat.label}</p>
          <p className="text-2xl font-bold mt-2">{stat.value}</p>
        </div>
      ))}
    </div>
  )
}
"""
    
    def _template_charts_component(self) -> str:
        """Charts component template"""
        return """export default function Charts() {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div className="p-6 bg-white rounded-lg shadow">
        <h3 className="font-semibold mb-4">Revenue Trend</h3>
        <div className="h-64 bg-gray-100 rounded flex items-center justify-center">
          Chart placeholder
        </div>
      </div>
      <div className="p-6 bg-white rounded-lg shadow">
        <h3 className="font-semibold mb-4">User Activity</h3>
        <div className="h-64 bg-gray-100 rounded flex items-center justify-center">
          Chart placeholder
        </div>
      </div>
    </div>
  )
}
"""
    
    def _template_export_button_component(self) -> str:
        """ExportButton component template"""
        return """import { Download } from 'lucide-react'

interface ExportButtonProps {
  format: 'pdf' | 'csv' | 'json'
  onExport: () => void
}

export default function ExportButton({ format, onExport }: ExportButtonProps) {
  return (
    <button
      onClick={onExport}
      className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
    >
      <Download size={18} />
      Export ({format.toUpperCase()})
    </button>
  )
}
"""
    
    def _template_export_modal_component(self) -> str:
        """ExportModal component template"""
        return """import { useState } from 'react'

interface ExportModalProps {
  isOpen: boolean
  onClose: () => void
  onExport: (format: string) => void
}

export default function ExportModal({ isOpen, onClose, onExport }: ExportModalProps) {
  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center">
      <div className="bg-white p-6 rounded-lg shadow-lg max-w-md">
        <h2 className="text-2xl font-bold mb-4">Export Data</h2>
        <div className="space-y-2 mb-6">
          <button
            onClick={() => { onExport('pdf'); onClose() }}
            className="w-full text-left p-3 hover:bg-gray-100 rounded"
          >
            📄 Export as PDF
          </button>
          <button
            onClick={() => { onExport('csv'); onClose() }}
            className="w-full text-left p-3 hover:bg-gray-100 rounded"
          >
            📊 Export as CSV
          </button>
          <button
            onClick={() => { onExport('json'); onClose() }}
            className="w-full text-left p-3 hover:bg-gray-100 rounded"
          >
            {} Export as JSON
          </button>
        </div>
        <button
          onClick={onClose}
          className="w-full px-4 py-2 border rounded hover:bg-gray-50"
        >
          Cancel
        </button>
      </div>
    </div>
  )
}
"""
    
    def _template_theme_toggle_component(self) -> str:
        """ThemeToggle component template"""
        return """import { useState, useEffect } from 'react'
import { Moon, Sun } from 'lucide-react'

export default function ThemeToggle() {
  const [isDark, setIsDark] = useState(false)

  useEffect(() => {
    if (isDark) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }, [isDark])

  return (
    <button
      onClick={() => setIsDark(!isDark)}
      className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800"
    >
      {isDark ? <Sun size={20} /> : <Moon size={20} />}
    </button>
  )
}
"""
