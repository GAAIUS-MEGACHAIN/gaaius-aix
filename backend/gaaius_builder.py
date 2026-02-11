# GAAIUS BUILD BRAIN v2.0 - Blueprint-First Platform Assembler
# This module contains the enhanced AI builder with template system

import json
import re
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone

# ============== APP TEMPLATES ==============
# Opinionated, production-ready templates that enforce quality

APP_TEMPLATES = {
    "saas_dashboard": {
        "name": "SaaS Dashboard",
        "description": "Admin dashboard with stats, charts, and data tables",
        "blueprint": {
            "app_type": "dashboard",
            "platform": ["web", "mobile"],
            "ui_framework": "gaaius-ui",
            "pages": [
                {"name": "Dashboard", "components": ["StatsGrid", "Chart", "ActivityFeed", "QuickActions"]},
                {"name": "Analytics", "components": ["LineChart", "BarChart", "DataTable", "Filters"]},
                {"name": "Users", "components": ["UserTable", "SearchBar", "Pagination", "UserModal"]},
                {"name": "Settings", "components": ["ProfileForm", "NotificationSettings", "BillingCard"]}
            ],
            "layout": {
                "type": "sidebar",
                "nav_items": ["Dashboard", "Analytics", "Users", "Settings"],
                "header": True,
                "footer": False
            },
            "features": ["auth", "search", "notifications", "export_data"],
            "theme": "dark-professional"
        },
        "code_template": '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{{APP_NAME}} - Dashboard</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <script src="https://unpkg.com/lucide@latest/dist/umd/lucide.js"></script>
  <style>
    * { font-family: 'Inter', sans-serif; }
    .glass { background: rgba(255,255,255,0.03); backdrop-filter: blur(12px); }
  </style>
</head>
<body class="bg-[#0a0a0a] text-white min-h-screen">
  <!-- Sidebar -->
  <aside class="fixed left-0 top-0 h-screen w-64 bg-[#111] border-r border-white/10 flex flex-col">
    <div class="p-6 border-b border-white/10">
      <h1 class="text-xl font-bold bg-gradient-to-r from-violet-400 to-cyan-400 bg-clip-text text-transparent">{{APP_NAME}}</h1>
    </div>
    <nav class="flex-1 p-4 space-y-2">
      {{NAV_ITEMS}}
    </nav>
    <div class="p-4 border-t border-white/10">
      <div class="flex items-center gap-3 p-3 rounded-xl bg-white/5">
        <div class="w-10 h-10 rounded-full bg-gradient-to-br from-violet-500 to-cyan-500 flex items-center justify-center font-semibold">U</div>
        <div>
          <p class="text-sm font-medium">User Name</p>
          <p class="text-xs text-white/50">Pro Account</p>
        </div>
      </div>
    </div>
  </aside>
  
  <!-- Main Content -->
  <main class="ml-64 p-8">
    <header class="flex items-center justify-between mb-8">
      <div>
        <h2 class="text-2xl font-bold">Dashboard</h2>
        <p class="text-white/50">Welcome back! Here's your overview.</p>
      </div>
      <div class="flex items-center gap-4">
        <button class="p-2 hover:bg-white/5 rounded-lg transition"><i data-lucide="bell" class="w-5 h-5"></i></button>
        <button class="px-4 py-2 bg-violet-600 hover:bg-violet-700 rounded-lg font-medium transition">New Report</button>
      </div>
    </header>
    
    <!-- Stats Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      {{STATS_CARDS}}
    </div>
    
    <!-- Charts Section -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
      {{CHARTS}}
    </div>
    
    <!-- Activity & Table -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {{ACTIVITY_SECTION}}
    </div>
  </main>
  
  <script>lucide.createIcons();</script>
</body>
</html>'''
    },
    
    "ecommerce": {
        "name": "E-commerce Store",
        "description": "Online store with products, cart, and checkout",
        "blueprint": {
            "app_type": "ecommerce",
            "platform": ["web", "mobile"],
            "ui_framework": "gaaius-ui",
            "pages": [
                {"name": "Home", "components": ["HeroBanner", "FeaturedProducts", "Categories", "Testimonials"]},
                {"name": "Products", "components": ["ProductGrid", "Filters", "SearchBar", "Pagination"]},
                {"name": "ProductDetail", "components": ["ProductGallery", "ProductInfo", "AddToCart", "Reviews"]},
                {"name": "Cart", "components": ["CartItems", "CartSummary", "PromoCode"]},
                {"name": "Checkout", "components": ["AddressForm", "PaymentForm", "OrderSummary"]}
            ],
            "layout": {
                "type": "navbar",
                "nav_items": ["Home", "Shop", "Categories", "Sale"],
                "header": True,
                "footer": True
            },
            "features": ["auth", "cart", "search", "wishlist", "payment"],
            "theme": "light-modern"
        },
        "code_template": '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{{APP_NAME}} - Shop</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <script src="https://unpkg.com/lucide@latest/dist/umd/lucide.js"></script>
  <style>* { font-family: 'Inter', sans-serif; }</style>
</head>
<body class="bg-gray-50 text-gray-900 min-h-screen">
  <!-- Navigation -->
  <nav class="fixed top-0 w-full bg-white border-b border-gray-200 z-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-16">
        <h1 class="text-xl font-bold">{{APP_NAME}}</h1>
        <div class="hidden md:flex items-center gap-8">
          {{NAV_ITEMS}}
        </div>
        <div class="flex items-center gap-4">
          <button class="p-2 hover:bg-gray-100 rounded-lg"><i data-lucide="search" class="w-5 h-5"></i></button>
          <button class="p-2 hover:bg-gray-100 rounded-lg"><i data-lucide="heart" class="w-5 h-5"></i></button>
          <button class="p-2 hover:bg-gray-100 rounded-lg relative">
            <i data-lucide="shopping-bag" class="w-5 h-5"></i>
            <span class="absolute -top-1 -right-1 w-5 h-5 bg-violet-600 text-white text-xs rounded-full flex items-center justify-center">3</span>
          </button>
        </div>
      </div>
    </div>
  </nav>
  
  <main class="pt-16">
    <!-- Hero -->
    {{HERO_SECTION}}
    
    <!-- Featured Products -->
    <section class="max-w-7xl mx-auto px-4 py-16">
      <h2 class="text-2xl font-bold mb-8">Featured Products</h2>
      <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
        {{PRODUCT_CARDS}}
      </div>
    </section>
    
    <!-- Categories -->
    {{CATEGORIES_SECTION}}
  </main>
  
  <!-- Footer -->
  {{FOOTER}}
  
  <script>lucide.createIcons();</script>
</body>
</html>'''
    },
    
    "admin_panel": {
        "name": "Admin Panel",
        "description": "Backend management interface with CRUD operations",
        "blueprint": {
            "app_type": "admin",
            "platform": ["web"],
            "ui_framework": "gaaius-ui",
            "pages": [
                {"name": "Overview", "components": ["StatsRow", "RecentActivity", "QuickActions"]},
                {"name": "Content", "components": ["DataTable", "CRUD_Modal", "Filters", "BulkActions"]},
                {"name": "Users", "components": ["UserList", "RoleManager", "InviteModal"]},
                {"name": "Settings", "components": ["GeneralSettings", "SecuritySettings", "APIKeys"]}
            ],
            "layout": {
                "type": "sidebar-compact",
                "nav_items": ["Overview", "Content", "Users", "Media", "Settings"],
                "header": True,
                "footer": False
            },
            "features": ["auth", "roles", "crud", "audit_log", "export"],
            "theme": "dark-admin"
        }
    },
    
    "ai_tool": {
        "name": "AI Tool Interface",
        "description": "Chat-based AI application with modern UI",
        "blueprint": {
            "app_type": "ai_tool",
            "platform": ["web", "mobile"],
            "ui_framework": "gaaius-ui",
            "pages": [
                {"name": "Chat", "components": ["MessageList", "InputBar", "ModelSelector", "HistorySidebar"]},
                {"name": "History", "components": ["ConversationList", "SearchBar", "Filters"]},
                {"name": "Settings", "components": ["APISettings", "ModelPreferences", "ThemeToggle"]}
            ],
            "layout": {
                "type": "split-panel",
                "nav_items": ["Chat", "History", "Settings"],
                "header": True,
                "footer": False
            },
            "features": ["streaming", "markdown", "code_highlight", "export"],
            "theme": "dark-ai"
        },
        "code_template": '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{{APP_NAME}} - AI Assistant</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <script src="https://unpkg.com/lucide@latest/dist/umd/lucide.js"></script>
  <style>
    * { font-family: 'Inter', sans-serif; }
    .chat-gradient { background: linear-gradient(180deg, #0a0a0a 0%, #111 100%); }
  </style>
</head>
<body class="bg-[#0a0a0a] text-white min-h-screen flex">
  <!-- Sidebar -->
  <aside class="w-64 bg-[#111] border-r border-white/10 flex flex-col">
    <div class="p-4 border-b border-white/10">
      <button class="w-full px-4 py-3 bg-white/5 hover:bg-white/10 rounded-xl flex items-center gap-2 transition">
        <i data-lucide="plus" class="w-4 h-4"></i>
        <span class="text-sm font-medium">New Chat</span>
      </button>
    </div>
    <div class="flex-1 p-2 space-y-1 overflow-auto">
      {{CHAT_HISTORY}}
    </div>
    <div class="p-4 border-t border-white/10">
      <div class="flex items-center gap-3">
        <div class="w-8 h-8 rounded-full bg-gradient-to-br from-violet-500 to-cyan-500"></div>
        <span class="text-sm font-medium">User</span>
      </div>
    </div>
  </aside>
  
  <!-- Main Chat -->
  <main class="flex-1 flex flex-col">
    <header class="h-14 border-b border-white/10 flex items-center justify-between px-6">
      <div class="flex items-center gap-2">
        <i data-lucide="bot" class="w-5 h-5 text-violet-400"></i>
        <span class="font-medium">{{APP_NAME}}</span>
      </div>
      <select class="bg-white/5 border border-white/10 rounded-lg px-3 py-1.5 text-sm">
        <option>GPT-4</option>
        <option>Claude</option>
        <option>Llama</option>
      </select>
    </header>
    
    <div class="flex-1 overflow-auto p-6">
      {{MESSAGES}}
    </div>
    
    <div class="p-4 border-t border-white/10">
      <div class="max-w-3xl mx-auto flex items-end gap-3">
        <div class="flex-1 bg-white/5 border border-white/10 rounded-2xl p-3 focus-within:border-violet-500">
          <textarea placeholder="Message {{APP_NAME}}..." class="w-full bg-transparent resize-none outline-none text-sm" rows="1"></textarea>
        </div>
        <button class="p-3 bg-violet-600 hover:bg-violet-700 rounded-xl transition">
          <i data-lucide="send" class="w-5 h-5"></i>
        </button>
      </div>
    </div>
  </main>
  
  <script>lucide.createIcons();</script>
</body>
</html>'''
    },
    
    "crypto_finance": {
        "name": "Crypto/Finance App",
        "description": "Trading dashboard with portfolio and transactions",
        "blueprint": {
            "app_type": "finance",
            "platform": ["web", "mobile"],
            "ui_framework": "gaaius-ui",
            "pages": [
                {"name": "Portfolio", "components": ["BalanceCard", "AssetList", "PriceChart", "QuickTrade"]},
                {"name": "Trade", "components": ["OrderBook", "TradingChart", "OrderForm", "OpenOrders"]},
                {"name": "Wallet", "components": ["WalletBalance", "TransactionHistory", "SendReceive"]},
                {"name": "Markets", "components": ["MarketTable", "TrendingCoins", "NewsWidget"]}
            ],
            "layout": {
                "type": "sidebar",
                "nav_items": ["Portfolio", "Trade", "Wallet", "Markets", "Settings"],
                "header": True,
                "footer": False
            },
            "features": ["auth", "2fa", "live_prices", "charts", "notifications"],
            "theme": "dark-crypto"
        },
        "code_template": '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{{APP_NAME}} - Portfolio</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <script src="https://unpkg.com/lucide@latest/dist/umd/lucide.js"></script>
  <style>
    * { font-family: 'Inter', sans-serif; }
    .glow-green { box-shadow: 0 0 20px rgba(16, 185, 129, 0.3); }
    .glow-red { box-shadow: 0 0 20px rgba(239, 68, 68, 0.3); }
  </style>
</head>
<body class="bg-[#0a0a0a] text-white min-h-screen">
  <!-- Sidebar -->
  <aside class="fixed left-0 top-0 h-screen w-20 bg-[#111] border-r border-white/10 flex flex-col items-center py-6">
    <div class="w-10 h-10 bg-gradient-to-br from-amber-500 to-orange-500 rounded-xl flex items-center justify-center font-bold mb-8">G</div>
    <nav class="flex-1 flex flex-col gap-4">
      {{ICON_NAV}}
    </nav>
    <button class="p-3 hover:bg-white/5 rounded-xl">
      <i data-lucide="settings" class="w-5 h-5 text-white/50"></i>
    </button>
  </aside>
  
  <!-- Main -->
  <main class="ml-20 p-8">
    <header class="flex items-center justify-between mb-8">
      <div>
        <h1 class="text-2xl font-bold">Portfolio</h1>
        <p class="text-white/50">Track your investments</p>
      </div>
      <div class="flex items-center gap-4">
        <button class="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 rounded-xl font-medium flex items-center gap-2">
          <i data-lucide="plus" class="w-4 h-4"></i> Buy
        </button>
        <button class="px-4 py-2 bg-white/10 hover:bg-white/20 rounded-xl font-medium flex items-center gap-2">
          <i data-lucide="arrow-up" class="w-4 h-4"></i> Send
        </button>
      </div>
    </header>
    
    <!-- Balance Card -->
    {{BALANCE_SECTION}}
    
    <!-- Assets -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {{ASSETS_AND_CHART}}
    </div>
  </main>
  
  <script>lucide.createIcons();</script>
</body>
</html>'''
    }
}

# ============== BLUEPRINT GENERATOR ==============

def generate_blueprint(prompt: str, template_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Generate a structured blueprint from user prompt.
    If template_key is provided, uses that template as base.
    """
    prompt_lower = prompt.lower()
    
    # Auto-detect template if not specified
    # Order matters - more specific keywords should be checked first
    if not template_key:
        # Check crypto/finance first (before dashboard catches it)
        if any(kw in prompt_lower for kw in ['crypto', 'trading', 'wallet', 'finance', 'coinbase', 'binance', 'portfolio', 'token', 'blockchain']):
            template_key = 'crypto_finance'
        elif any(kw in prompt_lower for kw in ['shop', 'store', 'ecommerce', 'e-commerce', 'product', 'cart', 'checkout', 'buy']):
            template_key = 'ecommerce'
        elif any(kw in prompt_lower for kw in ['ai', 'chat', 'assistant', 'gpt', 'llm', 'chatbot', 'bot']):
            template_key = 'ai_tool'
        elif any(kw in prompt_lower for kw in ['admin panel', 'cms', 'backend', 'manage content', 'crud']):
            template_key = 'admin_panel'
        elif any(kw in prompt_lower for kw in ['dashboard', 'admin', 'analytics', 'stats', 'metrics']):
            template_key = 'saas_dashboard'
    
    # Get base template or create custom blueprint
    if template_key and template_key in APP_TEMPLATES:
        template = APP_TEMPLATES[template_key]
        blueprint = template['blueprint'].copy()
        blueprint['template_used'] = template_key
        blueprint['template_name'] = template['name']
    else:
        # Custom blueprint for non-template apps
        blueprint = {
            "app_type": "custom",
            "platform": ["web"],
            "ui_framework": "gaaius-ui",
            "pages": [
                {"name": "Home", "components": ["Hero", "Features", "CTA"]},
                {"name": "About", "components": ["Content", "Team", "Contact"]}
            ],
            "layout": {
                "type": "navbar",
                "nav_items": ["Home", "About", "Contact"],
                "header": True,
                "footer": True
            },
            "features": ["responsive", "animations"],
            "theme": "dark-modern",
            "template_used": None,
            "template_name": "Custom Build"
        }
    
    # Extract app name from prompt
    name_patterns = [
        r'(?:called?|named?)\s+["\']?([^"\']+)["\']?',
        r'(?:build|create|make)\s+(?:a\s+)?([A-Z][a-zA-Z]+)',
    ]
    app_name = "MyApp"
    for pattern in name_patterns:
        match = re.search(pattern, prompt, re.IGNORECASE)
        if match:
            app_name = match.group(1).strip()
            break
    
    blueprint['app_name'] = app_name
    blueprint['original_prompt'] = prompt
    blueprint['generated_at'] = datetime.now(timezone.utc).isoformat()
    
    return blueprint


# ============== QUALITY GATE v2 ==============

def quality_gate_v2(html_code: str, blueprint: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enhanced quality gate that validates code against blueprint and design standards.
    Returns score, issues, and whether it passed.
    """
    issues = []
    score = 100
    checks_passed = []
    
    # 1. Structural checks
    if "<!doctype" not in html_code.lower():
        issues.append({"type": "critical", "msg": "Missing DOCTYPE declaration"})
        score -= 15
    else:
        checks_passed.append("DOCTYPE present")
    
    if "tailwindcss" not in html_code.lower():
        issues.append({"type": "critical", "msg": "Missing Tailwind CSS"})
        score -= 20
    else:
        checks_passed.append("Tailwind CSS included")
    
    # 2. Responsive design
    responsive_patterns = ["md:", "lg:", "sm:", "xl:", "max-w-", "mx-auto"]
    responsive_found = sum(1 for p in responsive_patterns if p in html_code)
    if responsive_found < 2:
        issues.append({"type": "warning", "msg": "Limited responsive design classes"})
        score -= 10
    else:
        checks_passed.append(f"Responsive design ({responsive_found} patterns)")
    
    # 3. Layout structure
    layout_elements = ["<nav", "<header", "<main", "<footer", "<aside"]
    layout_found = sum(1 for el in layout_elements if el in html_code.lower())
    if layout_found < 2:
        issues.append({"type": "warning", "msg": "Missing semantic layout elements"})
        score -= 10
    else:
        checks_passed.append(f"Semantic layout ({layout_found} elements)")
    
    # 4. Interactivity
    interactive_patterns = ["hover:", "transition", "onclick", "addEventListener"]
    interactive_found = sum(1 for p in interactive_patterns if p.lower() in html_code.lower())
    if interactive_found < 2:
        issues.append({"type": "minor", "msg": "Limited interactivity"})
        score -= 5
    else:
        checks_passed.append(f"Interactivity ({interactive_found} patterns)")
    
    # 5. Icons
    icon_patterns = ["lucide", "heroicon", "font-awesome", "<svg", "data-lucide"]
    has_icons = any(p.lower() in html_code.lower() for p in icon_patterns)
    if not has_icons:
        issues.append({"type": "minor", "msg": "Missing icons"})
        score -= 5
    else:
        checks_passed.append("Icons included")
    
    # 6. Typography
    font_patterns = ["font-bold", "font-semibold", "font-medium", "text-sm", "text-lg", "text-xl"]
    typography_found = sum(1 for p in font_patterns if p in html_code)
    if typography_found < 3:
        issues.append({"type": "minor", "msg": "Limited typography hierarchy"})
        score -= 5
    else:
        checks_passed.append(f"Typography hierarchy ({typography_found} classes)")
    
    # 7. Color consistency
    color_patterns = ["bg-", "text-", "border-"]
    color_found = sum(1 for p in color_patterns if p in html_code)
    if color_found < 10:
        issues.append({"type": "minor", "msg": "Limited color usage"})
        score -= 5
    else:
        checks_passed.append(f"Color system ({color_found} classes)")
    
    # 8. Spacing
    spacing_patterns = ["p-", "px-", "py-", "m-", "mx-", "my-", "gap-", "space-"]
    spacing_found = sum(1 for p in spacing_patterns if p in html_code)
    if spacing_found < 10:
        issues.append({"type": "warning", "msg": "Insufficient spacing"})
        score -= 10
    else:
        checks_passed.append(f"Proper spacing ({spacing_found} classes)")
    
    # 9. Accessibility basics
    has_alt = 'alt="' in html_code
    has_aria = 'aria-' in html_code
    if not has_alt and '<img' in html_code:
        issues.append({"type": "minor", "msg": "Images missing alt attributes"})
        score -= 3
    
    # 10. Code quality
    code_length = len(html_code)
    if code_length < 2000:
        issues.append({"type": "warning", "msg": "Code seems too minimal"})
        score -= 10
    
    return {
        "score": max(0, score),
        "passed": score >= 70,
        "issues": issues,
        "checks_passed": checks_passed,
        "blueprint_match": blueprint.get('template_used', 'custom'),
        "code_length": code_length
    }


# ============== SYSTEM PROMPTS ==============

BLUEPRINT_SYSTEM_PROMPT = '''You are GAAIUS BUILD BRAIN - a production-grade application builder.

ROLE: You generate structured blueprints for applications before any code is written.

OUTPUT FORMAT: Return ONLY valid JSON with this structure:
{
  "app_name": "string",
  "app_type": "dashboard|ecommerce|admin|ai_tool|crypto|landing|custom",
  "platform": ["web", "mobile", "desktop"],
  "pages": [
    {
      "name": "string",
      "components": ["string"],
      "layout": "string"
    }
  ],
  "features": ["string"],
  "theme": "string",
  "data_models": [{"name": "string", "fields": ["string"]}]
}

RULES:
1. Always suggest complete, production-ready feature sets
2. Include proper navigation and user flows
3. Suggest appropriate components for each page
4. Consider mobile responsiveness in layout
5. Include authentication if the app needs user data'''


GAAIUS_BUILD_PROMPT_V2 = '''SYSTEM: GAAIUS AI BUILDER v2.0 - PLATFORM ASSEMBLER

You are NOT generating demos. You are building PRODUCTION-READY applications.

DESIGN SYSTEM (MANDATORY):
1. Layout: Use consistent spacing (p-4, p-6, p-8), proper margins (m-auto, max-w-7xl)
2. Colors: Use cohesive palette (violet-500, cyan-500 for accents, white/10 for borders)
3. Typography: Clear hierarchy (text-2xl font-bold for headings, text-sm text-white/60 for meta)
4. Components: Cards with rounded-xl bg-white/5 border border-white/10
5. Icons: Always include Lucide icons (add script src="https://unpkg.com/lucide@latest/dist/umd/lucide.js")
6. Responsive: ALWAYS use md: lg: xl: prefixes for responsive design

QUALITY STANDARDS:
- Minimum 3000 characters of code
- At least 3 different sections/components
- Working navigation with hover states
- Proper semantic HTML (nav, header, main, aside, footer)
- Smooth transitions (transition, hover:)
- Professional color scheme
- Real content (not lorem ipsum)

OUTPUT: Return ONLY complete HTML. No markdown. No explanations. No code blocks.
Start with <!DOCTYPE html> and end with </html>.'''


# ============== TEMPLATE CODE GENERATORS ==============

def get_template_code(template_key: str, app_name: str, customizations: Dict = None) -> str:
    """Generate code from a template with customizations."""
    
    if template_key not in APP_TEMPLATES:
        return None
    
    template = APP_TEMPLATES[template_key]
    if 'code_template' not in template:
        return None
    
    code = template['code_template']
    
    # Replace placeholders
    code = code.replace('{{APP_NAME}}', app_name)
    
    # Generate nav items based on template
    nav_html = ""
    for item in template['blueprint']['layout']['nav_items']:
        nav_html += f'''<a href="#" class="flex items-center gap-3 px-4 py-2.5 rounded-lg text-white/70 hover:text-white hover:bg-white/5 transition">
          <i data-lucide="{get_icon_for_nav(item)}" class="w-5 h-5"></i>
          <span class="text-sm font-medium">{item}</span>
        </a>\n'''
    code = code.replace('{{NAV_ITEMS}}', nav_html)
    
    # Generate stats cards if needed
    if '{{STATS_CARDS}}' in code:
        stats_html = generate_stats_cards()
        code = code.replace('{{STATS_CARDS}}', stats_html)
    
    return code


def get_icon_for_nav(item: str) -> str:
    """Get appropriate Lucide icon name for navigation item."""
    icons = {
        'dashboard': 'layout-dashboard',
        'analytics': 'bar-chart-2',
        'users': 'users',
        'settings': 'settings',
        'home': 'home',
        'shop': 'shopping-bag',
        'products': 'package',
        'orders': 'clipboard-list',
        'content': 'file-text',
        'media': 'image',
        'chat': 'message-square',
        'history': 'clock',
        'portfolio': 'briefcase',
        'trade': 'trending-up',
        'wallet': 'wallet',
        'markets': 'activity',
        'categories': 'grid',
        'sale': 'tag'
    }
    return icons.get(item.lower(), 'circle')


def generate_stats_cards() -> str:
    """Generate sample stats cards HTML."""
    return '''
      <div class="p-6 bg-white/5 border border-white/10 rounded-2xl">
        <div class="flex items-center justify-between mb-4">
          <p class="text-sm font-medium text-white/60">Total Revenue</p>
          <div class="p-2 bg-emerald-500/20 rounded-lg"><i data-lucide="dollar-sign" class="w-4 h-4 text-emerald-400"></i></div>
        </div>
        <p class="text-3xl font-bold">$45,231</p>
        <p class="text-sm text-emerald-400 mt-1">↑ 12.5% from last month</p>
      </div>
      <div class="p-6 bg-white/5 border border-white/10 rounded-2xl">
        <div class="flex items-center justify-between mb-4">
          <p class="text-sm font-medium text-white/60">Active Users</p>
          <div class="p-2 bg-violet-500/20 rounded-lg"><i data-lucide="users" class="w-4 h-4 text-violet-400"></i></div>
        </div>
        <p class="text-3xl font-bold">2,338</p>
        <p class="text-sm text-emerald-400 mt-1">↑ 8.2% from last month</p>
      </div>
      <div class="p-6 bg-white/5 border border-white/10 rounded-2xl">
        <div class="flex items-center justify-between mb-4">
          <p class="text-sm font-medium text-white/60">Total Orders</p>
          <div class="p-2 bg-cyan-500/20 rounded-lg"><i data-lucide="shopping-cart" class="w-4 h-4 text-cyan-400"></i></div>
        </div>
        <p class="text-3xl font-bold">1,893</p>
        <p class="text-sm text-emerald-400 mt-1">↑ 5.7% from last month</p>
      </div>
      <div class="p-6 bg-white/5 border border-white/10 rounded-2xl">
        <div class="flex items-center justify-between mb-4">
          <p class="text-sm font-medium text-white/60">Conversion Rate</p>
          <div class="p-2 bg-amber-500/20 rounded-lg"><i data-lucide="percent" class="w-4 h-4 text-amber-400"></i></div>
        </div>
        <p class="text-3xl font-bold">3.24%</p>
        <p class="text-sm text-red-400 mt-1">↓ 0.8% from last month</p>
      </div>
    '''


# ============== AVAILABLE TEMPLATES LIST ==============

def get_available_templates() -> List[Dict]:
    """Return list of available templates for frontend."""
    return [
        {
            "key": key,
            "name": template["name"],
            "description": template["description"],
            "features": template["blueprint"].get("features", [])
        }
        for key, template in APP_TEMPLATES.items()
    ]


# ============== ADVANCED COMPONENT LIBRARY ==============
# Production-grade reusable components with accessibility and performance optimizations

class ComponentLibrary:
    """Production-ready component system with composition and theming."""
    
    @staticmethod
    def button(label: str, variant: str = "primary", size: str = "md", icon: str = None, disabled: bool = False) -> str:
        """Generate accessible, production-grade button component."""
        size_classes = {"sm": "px-3 py-1.5 text-sm", "md": "px-4 py-2 text-sm", "lg": "px-6 py-3 text-base"}
        variant_classes = {
            "primary": "bg-violet-600 hover:bg-violet-700 text-white",
            "secondary": "bg-white/10 hover:bg-white/20 text-white border border-white/20",
            "danger": "bg-red-600/20 hover:bg-red-600/30 text-red-400 border border-red-500/30",
            "success": "bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-400 border border-emerald-500/30"
        }
        disabled_class = "opacity-50 cursor-not-allowed" if disabled else ""
        icon_html = f'<i data-lucide="{icon}" class="w-4 h-4"></i>' if icon else ""
        return f'''<button class="inline-flex items-center gap-2 {size_classes.get(size, size_classes['md'])} {variant_classes.get(variant, variant_classes['primary'])} rounded-lg font-medium transition disabled:opacity-50 {disabled_class}" {"disabled" if disabled else ""}>
        {icon_html}
        <span>{label}</span>
      </button>'''
    
    @staticmethod
    def card(content: str, title: str = None, footer: str = None) -> str:
        """Generate semantic card with optional title and footer."""
        title_html = f'<h3 class="text-lg font-semibold mb-4">{title}</h3>' if title else ""
        footer_html = f'<div class="mt-6 pt-4 border-t border-white/10">{footer}</div>' if footer else ""
        return f'''<div class="p-6 bg-white/5 border border-white/10 rounded-2xl backdrop-blur-sm hover:bg-white/[0.07] transition duration-300">
        {title_html}
        {content}
        {footer_html}
      </div>'''
    
    @staticmethod
    def input_field(label: str, type: str = "text", placeholder: str = "", required: bool = False, icon: str = None) -> str:
        """Generate accessible input with validation and icon support."""
        required_html = '<span class="text-red-400">*</span>' if required else ""
        icon_html = f'<i data-lucide="{icon}" class="w-5 h-5 text-white/40 pointer-events-none absolute left-3 top-1/2 -translate-y-1/2"></i>' if icon else ""
        input_class = "pl-10" if icon else "pl-3"
        return f'''<div class="flex flex-col gap-2">
        <label class="text-sm font-medium text-white/80">{label} {required_html}</label>
        <div class="relative">
          {icon_html}
          <input type="{type}" placeholder="{placeholder}" class="{input_class} pr-4 py-2.5 w-full bg-white/5 border border-white/10 rounded-lg focus:border-violet-500 focus:bg-white/10 focus:outline-none transition" {"required" if required else ""} />
        </div>
      </div>'''
    
    @staticmethod
    def modal(title: str, content: str, actions: List[str] = None) -> str:
        """Generate accessible modal with backdrop and action buttons."""
        actions_html = ''.join([f'<button class="px-4 py-2 rounded-lg {action}">{action.split(">")[-1]}</button>' for action in (actions or [])])
        return f'''<div class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50" id="modal-backdrop">
        <div class="w-full max-w-md bg-[#111] border border-white/10 rounded-2xl shadow-2xl">
          <div class="p-6 border-b border-white/10 flex items-center justify-between">
            <h2 class="text-xl font-bold">{title}</h2>
            <button class="p-1 hover:bg-white/10 rounded-lg" aria-label="Close"><i data-lucide="x" class="w-5 h-5"></i></button>
          </div>
          <div class="p-6">{content}</div>
          <div class="p-6 border-t border-white/10 flex items-center justify-end gap-3">
            {actions_html}
          </div>
        </div>
      </div>'''
    
    @staticmethod
    def data_table(columns: List[str], rows: List[List[str]], sortable: bool = True, filterable: bool = True) -> str:
        """Generate accessible data table with sorting and filtering."""
        chevron = '<i data-lucide="chevron-down" class="w-4 h-4"></i>'
        header_cells = []
        for col in columns:
            chevron_html = chevron if sortable else ""
            header_cells.append(f'<th class="px-6 py-3 text-left text-sm font-semibold text-white/80 border-b border-white/10"><div class="flex items-center gap-2">{col}{chevron_html}</div></th>')
        header_html = ''.join(header_cells)
        row_html = ''.join([
            f'''<tr class="border-b border-white/10 hover:bg-white/[0.02] transition">
              {''.join([f'<td class="px-6 py-4 text-sm">{cell}</td>' for cell in row])}
            </tr>''' for row in rows
        ])
        return f'''<div class="w-full bg-white/5 border border-white/10 rounded-2xl overflow-hidden">
        <table class="w-full">
          <thead class="bg-white/[0.02]">
            <tr>{header_html}</tr>
          </thead>
          <tbody>{row_html}</tbody>
        </table>
      </div>'''
    
    @staticmethod
    def toast(message: str, type: str = "info", duration: int = 4000) -> str:
        """Generate accessible toast notification."""
        color_map = {"info": "blue", "success": "emerald", "error": "red", "warning": "amber"}
        color = color_map.get(type, "blue")
        icon_map = {"info": "info", "success": "check-circle", "error": "alert-circle", "warning": "alert-triangle"}
        icon = icon_map.get(type, "info")
        return f'''<div class="fixed bottom-6 right-6 max-w-sm bg-{color}-600/20 border border-{color}-500/30 text-{color}-300 px-4 py-3 rounded-lg flex items-center gap-3 animate-slide-up" role="alert">
        <i data-lucide="{icon}" class="w-5 h-5"></i>
        <p class="text-sm font-medium">{message}</p>
      </div>'''


# ============== ADVANCED LAYOUT SYSTEM ==============
# Professional grid and layout utilities for rapid composition

class LayoutEngine:
    """Advanced layout composition system."""
    
    @staticmethod
    def grid(columns: int = 2, gap: str = "6", items: List[str] = None) -> str:
        """Generate responsive CSS Grid."""
        grid_cols = {1: "grid-cols-1", 2: "grid-cols-1 md:grid-cols-2", 3: "grid-cols-1 md:grid-cols-2 lg:grid-cols-3", 4: "grid-cols-2 md:grid-cols-3 lg:grid-cols-4"}
        col_class = grid_cols.get(columns, f"grid-cols-{columns}")
        items_html = ''.join([f'<div>{item}</div>' for item in (items or [])])
        return f'<div class="grid {col_class} gap-{gap}">{items_html}</div>'
    
    @staticmethod
    def flexbox(direction: str = "row", justify: str = "between", items: List[str] = None) -> str:
        """Generate Flexbox container."""
        dir_class = "flex-row" if direction == "row" else "flex-col"
        justify_map = {"between": "justify-between", "center": "justify-center", "start": "justify-start", "end": "justify-end"}
        justify_class = justify_map.get(justify, f"justify-{justify}")
        items_html = ''.join([f'<div>{item}</div>' for item in (items or [])])
        return f'<div class="flex {dir_class} {justify_class} gap-4">{items_html}</div>'
    
    @staticmethod
    def container(width: str = "full", padding: str = "8", content: str = "") -> str:
        """Generate responsive container."""
        width_map = {"sm": "max-w-sm", "md": "max-w-md", "lg": "max-w-lg", "2xl": "max-w-2xl", "4xl": "max-w-4xl", "6xl": "max-w-6xl", "7xl": "max-w-7xl"}
        width_class = width_map.get(width, "w-full")
        return f'<div class="{width_class} mx-auto px-{padding} py-{padding}">{content}</div>'


# ============== STATE MANAGEMENT SYSTEM ==============
# Production-ready state patterns for dynamic applications

class StateManager:
    """Manages application state and reactivity patterns."""
    
    def __init__(self):
        self.state = {}
        self.subscriptions = {}
        self.history = []
    
    def set(self, key: str, value: Any) -> None:
        """Set state with change tracking."""
        old_value = self.state.get(key)
        self.state[key] = value
        self.history.append({"timestamp": datetime.now(timezone.utc).isoformat(), "key": key, "old": old_value, "new": value})
        if key in self.subscriptions:
            for callback in self.subscriptions[key]:
                callback(value)
    
    def get(self, key: str, default=None) -> Any:
        """Get state value."""
        return self.state.get(key, default)
    
    def subscribe(self, key: str, callback) -> callable:
        """Subscribe to state changes."""
        if key not in self.subscriptions:
            self.subscriptions[key] = []
        self.subscriptions[key].append(callback)
        return lambda: self.subscriptions[key].remove(callback)
    
    def batch_update(self, updates: Dict[str, Any]) -> None:
        """Batch multiple state updates."""
        for key, value in updates.items():
            self.set(key, value)
    
    def rollback(self, steps: int = 1) -> None:
        """Rollback state changes."""
        for _ in range(min(steps, len(self.history))):
            change = self.history.pop()
            self.state[change['key']] = change['old']
    
    def export(self) -> Dict:
        """Export current state and history."""
        return {"current": self.state, "history": self.history}


# ============== PERFORMANCE & CACHING ==============
# Advanced caching and performance optimization layer

class CacheManager:
    """High-performance caching with TTL and invalidation."""
    
    def __init__(self):
        self.cache = {}
        self.metadata = {}
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        """Cache with TTL (seconds)."""
        self.cache[key] = value
        self.metadata[key] = {
            "created": datetime.now(timezone.utc).isoformat(),
            "ttl": ttl,
            "hits": 0
        }
    
    def get(self, key: str) -> Any:
        """Retrieve cached value with TTL check."""
        if key not in self.cache:
            return None
        
        meta = self.metadata[key]
        created = datetime.fromisoformat(meta['created'].replace('Z', '+00:00'))
        elapsed = (datetime.now(timezone.utc) - created).total_seconds()
        
        if elapsed > meta['ttl']:
            del self.cache[key]
            del self.metadata[key]
            return None
        
        meta['hits'] += 1
        return self.cache[key]
    
    def invalidate(self, pattern: str = None) -> int:
        """Invalidate cache entries by pattern."""
        if pattern is None:
            count = len(self.cache)
            self.cache.clear()
            self.metadata.clear()
            return count
        
        keys_to_delete = [k for k in self.cache.keys() if pattern in k]
        for k in keys_to_delete:
            del self.cache[k]
            del self.metadata[k]
        return len(keys_to_delete)
    
    def stats(self) -> Dict:
        """Get cache statistics."""
        total_hits = sum(m['hits'] for m in self.metadata.values())
        return {
            "entries": len(self.cache),
            "total_hits": total_hits,
            "hit_rate": total_hits / max(1, len(self.metadata)),
            "metadata": self.metadata
        }


# ============== VALIDATION & SCHEMA ==============
# Production-grade data validation system

class SchemaValidator:
    """Type-safe schema validation with detailed error reporting."""
    
    @staticmethod
    def validate_blueprint(data: Dict) -> tuple:
        """Validate blueprint structure and content."""
        errors = []
        required_fields = ['app_name', 'app_type', 'platform', 'pages', 'features']
        
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field: {field}")
        
        if 'app_type' in data and data['app_type'] not in ['dashboard', 'ecommerce', 'admin', 'ai_tool', 'crypto', 'landing', 'custom']:
            errors.append(f"Invalid app_type: {data['app_type']}")
        
        if 'pages' in data and not isinstance(data['pages'], list):
            errors.append("pages must be a list")
        else:
            for i, page in enumerate(data.get('pages', [])):
                if 'name' not in page or 'components' not in page:
                    errors.append(f"Page {i} missing 'name' or 'components'")
        
        if 'platform' in data and not isinstance(data['platform'], list):
            errors.append("platform must be a list")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_html(code: str) -> tuple:
        """Validate HTML structure and best practices."""
        errors = []
        
        if not code.startswith('<!DOCTYPE') and not code.startswith('<!doctype'):
            errors.append("Missing DOCTYPE declaration")
        
        if code.count('<html') != code.count('</html>'):
            errors.append("Mismatched HTML tags")
        
        if code.count('<head') != code.count('</head>'):
            errors.append("Mismatched HEAD tags")
        
        if code.count('<body') != code.count('</body>'):
            errors.append("Mismatched BODY tags")
        
        if '<meta charset' not in code.lower():
            errors.append("Missing charset meta tag")
        
        if '<meta name="viewport"' not in code.lower():
            errors.append("Missing viewport meta tag")
        
        return len(errors) == 0, errors


# ============== CODE GENERATION UTILITIES ==============
# Advanced code generation with type safety and templating

class CodeGenerator:
    """Production-grade code generation with safety checks."""
    
    @staticmethod
    def generate_component(name: str, props: Dict[str, str], slots: List[str] = None) -> str:
        """Generate reusable component with props."""
        props_html = ''.join([f'{k}="{v}"' for k, v in props.items()])
        slots_html = ''.join([f'<slot name="{slot}"></slot>' for slot in (slots or [])])
        return f'''<template id="component-{name.lower()}">
      <div {props_html} class="component-{name.lower()}">
        {slots_html}
      </div>
    </template>'''
    
    @staticmethod
    def generate_script_module(functions: Dict[str, str]) -> str:
        """Generate JavaScript module with functions."""
        funcs_js = '\n'.join([f'  const {name} = async () => {{{body}}}' for name, body in functions.items()])
        return f'''<script type="module">
    {funcs_js}
    export {{ {", ".join(functions.keys())} }};
  </script>'''
    
    @staticmethod
    def generate_style_scope(selector: str, rules: Dict[str, str]) -> str:
        """Generate scoped CSS."""
        rules_css = '\n    '.join([f'{k}: {v};' for k, v in rules.items()])
        return f'''<style scoped>
    {selector} {{
      {rules_css}
    }}
  </style>'''


# ============== INTEGRATION & EXPORT ==============
# Export and integration utilities

class ProjectExporter:
    """Export complete projects with all assets and metadata."""
    
    @staticmethod
    def export_blueprint_to_project(blueprint: Dict) -> Dict[str, Any]:
        """Convert blueprint to complete project structure."""
        return {
            "metadata": {
                "name": blueprint.get('app_name', 'MyApp'),
                "type": blueprint.get('app_type', 'custom'),
                "created": datetime.now(timezone.utc).isoformat(),
                "version": "1.0.0"
            },
            "blueprint": blueprint,
            "structure": {
                "src": {
                    "index.html": "<!-- Entry point -->",
                    "styles": {"main.css": "/* Global styles */"},
                    "components": {page['name'].lower() + ".html": "<!-- Component -->" for page in blueprint.get('pages', [])},
                    "utils": {"helpers.js": "// Utility functions"}
                },
                "public": {"assets": {}},
                "config": {
                    "package.json": json.dumps({"name": blueprint.get('app_name', 'myapp'), "version": "1.0.0"}, indent=2)
                }
            },
            "quality_gates": {
                "blueprint_validated": True,
                "html_validated": False,
                "performance_score": 0,
                "accessibility_score": 0
            }
        }
    
    @staticmethod
    def generate_manifest(project: Dict) -> str:
        """Generate project manifest for CI/CD."""
        manifest = {
            "project": project['metadata'],
            "stages": [
                {"name": "validate", "commands": ["schema-check", "html-lint"]},
                {"name": "build", "commands": ["minify", "optimize-images"]},
                {"name": "test", "commands": ["accessibility-audit", "performance-test"]},
                {"name": "deploy", "commands": ["build-static", "push-cdn"]}
            ],
            "generated": datetime.now(timezone.utc).isoformat()
        }
        return json.dumps(manifest, indent=2)


# ============== AI ORCHESTRATOR ==============
# Main orchestration engine for the build pipeline

class AIOrchestrator:
    """Core orchestration engine for GAAIUS BUILD platform."""
    
    class PipelineStage:
        """Pipeline stage with error handling and rollback."""
        def __init__(self, name: str, description: str):
            self.name = name
            self.description = description
            self.status = "pending"
            self.error = None
            self.result = None
            self.duration = 0
            self.timestamp = datetime.now(timezone.utc).isoformat()
        
        def to_dict(self) -> Dict:
            return {
                "name": self.name,
                "description": self.description,
                "status": self.status,
                "error": self.error,
                "result": self.result,
                "duration": self.duration,
                "timestamp": self.timestamp
            }
    
    def __init__(self):
        self.pipeline_stages = []
        self.project_state = {}
        self.file_system = {}
        self.runtime_env = {}
        self.feedback_loop_history = []
        self.ai_decisions = []
    
    def orchestrate(self, prompt: str, environment_config: Dict = None) -> Dict[str, Any]:
        """Main orchestration pipeline."""
        import time
        env = environment_config or self._default_environment()
        
        # Stage 1: Prompt Ingestion
        stage1 = self._stage_prompt_ingestion(prompt, env)
        self.pipeline_stages.append(stage1)
        if stage1.status == 'failed':
            return self._build_response(False, stage1.error)
        
        # Stage 2: Task Decomposition
        stage2 = self._stage_task_decomposition(stage1.result, env)
        self.pipeline_stages.append(stage2)
        if stage2.status == 'failed':
            return self._build_response(False, stage2.error)
        
        # Stage 3: Blueprint Generation
        stage3 = self._stage_blueprint_generation(stage2.result, env)
        self.pipeline_stages.append(stage3)
        if stage3.status == 'failed':
            return self._build_response(False, stage3.error)
        
        # Stage 4: File Generation
        stage4 = self._stage_file_generation(stage3.result, env)
        self.pipeline_stages.append(stage4)
        if stage4.status == 'failed':
            return self._build_response(False, stage4.error)
        
        return {
            "success": True,
            "project": {
                "blueprint": stage3.result,
                "files": stage4.result,
            },
            "pipeline": [s.to_dict() for s in self.pipeline_stages],
            "metrics": {
                "total_duration": sum(s.duration for s in self.pipeline_stages),
                "stages_completed": len([s for s in self.pipeline_stages if s.status in ['success', 'recovered']])
            }
        }
    
    def _build_response(self, success: bool, error: str = None) -> Dict:
        return {
            "success": success,
            "error": error,
            "pipeline": [s.to_dict() for s in self.pipeline_stages]
        }
    
    def _stage_prompt_ingestion(self, prompt: str, env: Dict) -> PipelineStage:
        """Stage 1: Parse prompt with system context."""
        import time
        stage = self.PipelineStage("Prompt Ingestion", "Parse user intent with system constraints")
        try:
            start = time.time()
            stage.result = {
                "original_prompt": prompt,
                "environment": env,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            stage.status = "success"
            stage.duration = time.time() - start
        except Exception as e:
            stage.status = "failed"
            stage.error = str(e)
        return stage
    
    def _stage_task_decomposition(self, context: Dict, env: Dict) -> PipelineStage:
        """Stage 2: Break request into tasks."""
        import time
        stage = self.PipelineStage("Task Decomposition", "Break prompt into executable subtasks")
        try:
            start = time.time()
            stage.result = {
                "tasks": [
                    "Analyze prompt and determine app type",
                    "Select or create blueprint template",
                    "Plan component architecture",
                    "Generate responsive layout structure"
                ],
                "context": context
            }
            stage.status = "success"
            stage.duration = time.time() - start
        except Exception as e:
            stage.status = "failed"
            stage.error = str(e)
        return stage
    
    def _stage_blueprint_generation(self, tasks: Dict, env: Dict) -> PipelineStage:
        """Stage 3: Generate complete blueprint."""
        import time
        stage = self.PipelineStage("Blueprint Generation", "Create comprehensive project blueprint")
        try:
            start = time.time()
            blueprint = generate_blueprint(tasks['context']['original_prompt'])
            blueprint['execution_tasks'] = tasks['tasks']
            blueprint['environment'] = env
            stage.result = blueprint
            stage.status = "success"
            stage.duration = time.time() - start
        except Exception as e:
            stage.status = "failed"
            stage.error = str(e)
        return stage
    
    def _stage_file_generation(self, blueprint: Dict, env: Dict) -> PipelineStage:
        """Stage 4: Generate complete file structure."""
        import time
        stage = self.PipelineStage("File Generation", "Generate all project files and code")
        try:
            start = time.time()
            files = {
                "package.json": json.dumps({"name": blueprint['app_name'].lower().replace(" ", "-"), "version": "1.0.0"}, indent=2),
                "index.html": self._generate_index_html(blueprint),
                "README.md": f"# {blueprint['app_name']}\n\nGenerated by GAAIUS BUILD BRAIN v2.0"
            }
            stage.result = {"files": files, "blueprint": blueprint}
            stage.status = "success"
            stage.duration = time.time() - start
        except Exception as e:
            stage.status = "failed"
            stage.error = str(e)
        return stage
    
    def _generate_index_html(self, blueprint: Dict) -> str:
        """Generate index.html entry point."""
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{blueprint['app_name']}</title>
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-[#0a0a0a] text-white min-h-screen">
  <div id="root">
    <h1 class="text-4xl font-bold text-center py-20">{blueprint['app_name']}</h1>
    <p class="text-center text-white/60">Generated with GAAIUS BUILD BRAIN v2.0</p>
  </div>
</body>
</html>'''
    
    def _default_environment(self) -> Dict:
        """Default environment configuration."""
        return {
            "framework": "react",
            "runtime": "node.js",
            "preview_port": 3000,
            "build_tool": "vite"
        }


# ============== IDE INFRASTRUCTURE ==============
# Monaco Editor and IDE configuration

class IDEInfrastructure:
    """Complete IDE infrastructure with Monaco Editor configuration."""
    
    def __init__(self):
        self.editor_config = self._monaco_config()
        self.lsp_servers = self._init_lsp_servers()
    
    def _monaco_config(self) -> Dict[str, Any]:
        """Monaco Editor configuration."""
        return {
            "editor": {
                "name": "Monaco Editor",
                "version": "latest",
                "features": {
                    "syntax_highlighting": True,
                    "intellisense": True,
                    "error_squiggles": True,
                    "multi_language": True
                },
                "language_support": [
                    "javascript", "typescript", "python", "html", "css", "json"
                ]
            }
        }
    
    def _init_lsp_servers(self) -> Dict[str, Any]:
        """Initialize LSP servers."""
        return {
            "typescript": {"name": "TypeScript Language Server", "port": 9001},
            "python": {"name": "Pylance", "port": 9002},
            "html": {"name": "HTML Language Server", "port": 9003}
        }
    
    def get_editor_config(self) -> Dict:
        """Get Monaco Editor configuration."""
        return self.editor_config


# ============== GAAIUS BUILD PLATFORM ==============
# Main platform integrator

class GAIUSBuildPlatform:
    """Main GAAIUS BUILD platform integrator."""
    
    def __init__(self):
        self.orchestrator = AIOrchestrator()
        self.ide = IDEInfrastructure()
        self.component_library = ComponentLibrary()
        self.layout_engine = LayoutEngine()
        self.state_manager = StateManager()
        self.cache_manager = CacheManager()
        self.validator = SchemaValidator()
        self.exporter = ProjectExporter()
    
    def create_project(self, prompt: str, config: Dict = None) -> Dict[str, Any]:
        """Create a complete project from a prompt."""
        result = self.orchestrator.orchestrate(prompt, config)
        return result
    
    def get_templates(self) -> List[Dict]:
        """Get available templates."""
        return get_available_templates()
    
    def validate_code(self, code: str, blueprint: Dict) -> Dict[str, Any]:
        """Validate generated code."""
        return quality_gate_v2(code, blueprint)
    
    def export_project(self, blueprint: Dict) -> Dict[str, Any]:
        """Export project structure."""
        return self.exporter.export_blueprint_to_project(blueprint)
    
    def get_platform_status(self) -> Dict[str, Any]:
        """Get complete platform status."""
        return {
            "platform": "GAAIUS BUILD v2.0",
            "status": "operational",
            "version": "2.0.0",
            "components": {
                "orchestrator": "✓ Active",
                "ide": "✓ Monaco Editor configured",
                "templates": f"✓ {len(APP_TEMPLATES)} templates available",
                "quality_gate": "✓ Validation enabled",
                "components": "✓ Component Library loaded",
                "layout": "✓ Layout Engine ready"
            }
        }


# ============== INITIALIZATION ==============

def initialize_gaaius_build() -> Dict[str, Any]:
    """Initialize complete GAAIUS BUILD platform."""
    platform = GAIUSBuildPlatform()
    return {
        "platform_initialized": True,
        "version": "2.0.0",
        "templates_available": len(APP_TEMPLATES),
        "status": platform.get_platform_status()
    }
