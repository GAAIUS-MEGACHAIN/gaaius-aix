"""
DESKTOP GENERATOR - Tauri / Electron EXE/DMG/AppImage Generation
Transforms GAAIUS blueprints into desktop applications
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

@dataclass
class DesktopConfig:
    """Configuration for desktop app generation"""
    project_id: str
    project_name: str
    version: str = "1.0.0"
    target: str = "tauri"  # "tauri" or "electron"
    platforms: List[str] = None  # ["windows", "macos", "linux"]
    
    def __post_init__(self):
        if self.platforms is None:
            self.platforms = ["windows", "macos", "linux"]


class DesktopGenerator:
    """Generates desktop applications from blueprints"""
    
    def generate_tauri(self, config: DesktopConfig, project_path: Path, blueprint: Dict[str, Any]) -> Dict[str, str]:
        """Generate Tauri desktop app (Rust + React)"""
        files = {}
        
        # Cargo.toml (Rust project manifest)
        files["Cargo.toml"] = self._template_cargo_toml(config)
        
        # Tauri config
        files["src-tauri/tauri.conf.json"] = self._template_tauri_config(config)
        
        # Main Rust app
        files["src-tauri/src/main.rs"] = self._template_tauri_main(config)
        
        # React frontend
        files["src/App.tsx"] = self._template_tauri_app(blueprint)
        files["src/main.tsx"] = self._template_tauri_vite_main()
        files["package.json"] = self._template_tauri_package_json(config)
        files["vite.config.ts"] = self._template_tauri_vite_config()
        
        # Build scripts
        files["build-windows.ps1"] = self._template_build_windows_script(config)
        files["build-macos.sh"] = self._template_build_macos_script(config)
        files["build-linux.sh"] = self._template_build_linux_script(config)
        
        # GitHub Actions CI/CD
        files[".github/workflows/publish.yml"] = self._template_tauri_ci_workflow(config)
        
        return files
    
    def generate_electron(self, config: DesktopConfig, project_path: Path, blueprint: Dict[str, Any]) -> Dict[str, str]:
        """Generate Electron desktop app (Node.js + React)"""
        files = {}
        
        # Main Electron process
        files["public/electron.js"] = self._template_electron_main(config)
        files["public/preload.js"] = self._template_electron_preload()
        
        # React frontend
        files["src/App.tsx"] = self._template_electron_app(blueprint)
        files["src/main.tsx"] = self._template_electron_vite_main()
        
        # Package.json
        files["package.json"] = self._template_electron_package_json(config)
        files["vite.config.ts"] = self._template_electron_vite_config()
        
        # Build scripts
        files["build-windows.bat"] = self._template_electron_build_windows(config)
        files["build-macos.sh"] = self._template_electron_build_macos(config)
        files["build-linux.sh"] = self._template_electron_build_linux(config)
        
        # GitHub Actions
        files[".github/workflows/build.yml"] = self._template_electron_ci_workflow(config)
        
        # Installer configs
        files["installers/windows.nsis"] = self._template_windows_installer(config)
        files["installers/macos-dmg.json"] = self._template_macos_dmg_config(config)
        
        return files
    
    # ============== TAURI TEMPLATES ==============
    
    def _template_cargo_toml(self, config: DesktopConfig) -> str:
        return f"""[package]
name = "{config.project_name.lower().replace(' ', '_')}"
version = "{config.version}"
description = "{config.project_name} - Desktop App"
authors = ["GAAIUS"]
edition = "2021"

[build-dependencies]
tauri-build = {{ version = "1.5" }}

[dependencies]
serde_json = "1.0"
serde = {{ version = "1.0", features = ["derive"] }}
tauri = {{ version = "1.5", features = ["all"] }}
tokio = {{ version = "1", features = ["full"] }}
reqwest = {{ version = "0.11", features = ["json"] }}

[features]
default = ["custom-protocol"]
custom-protocol = ["tauri/custom-protocol"]

[[bin]]
name = "{config.project_name.lower().replace(' ', '_')}"
path = "src-tauri/src/main.rs"
"""
    
    def _template_tauri_config(self, config: DesktopConfig) -> str:
        return json.dumps({
            "build": {
                "beforeBuildCommand": "npm run build",
                "beforeDevCommand": "npm run dev",
                "devPath": "http://localhost:5173",
                "frontendDist": "../dist"
            },
            "app": {
                "windows": [
                    {
                        "title": config.project_name,
                        "width": 800,
                        "height": 600,
                        "resizable": True,
                        "fullscreen": False
                    }
                ],
                "security": {
                    "csp": None
                }
            },
            "bundle": {
                "active": True,
                "targets": "all",
                "identifier": config.project_id,
                "icon": [
                    "icons/32x32.png",
                    "icons/128x128.png",
                    "icons/128x128@2x.png",
                    "icons/icon.icns",
                    "icons/icon.ico"
                ]
            }
        }, indent=2)
    
    def _template_tauri_main(self, config: DesktopConfig) -> str:
        return f"""#![cfg_attr(
  all(not(debug_assertions), target_os = "windows"),
  windows_subsystem = "windows"
)]

use tauri::{{Manager, SystemTrayEvent, CustomMenuItem, SystemTray, SystemTrayMenu}};

fn main() {{
  let quit = CustomMenuItem::new("quit".to_string(), "Quit");
  let hide = CustomMenuItem::new("hide".to_string(), "Hide");
  let tray_menu = SystemTrayMenu::new()
    .add_item(hide)
    .add_item(quit);
  let system_tray = SystemTray::new()
    .with_menu(tray_menu);

  tauri::Builder::default()
    .system_tray(system_tray)
    .on_system_tray_event(|app, event| match event {{
      SystemTrayEvent::MenuItemClick {{ id, .. }} => {{
        match id.as_str() {{
          "quit" => {{
            std::process::exit(0);
          }}
          "hide" => {{
            let window = app.get_window("main").unwrap();
            let _ = window.hide();
          }}
          _ => {{}}
        }}
      }}
      _ => {{}}
    }})
    .run(tauri::generate_context!())
    .expect("error while running tauri application");
}}
"""
    
    def _template_tauri_app(self, blueprint: Dict[str, Any]) -> str:
        return """import { invoke } from '@tauri-apps/api/tauri'
import { useState } from 'react'

function App() {
  const [greetMsg, setGreetMsg] = useState('')

  async function greet() {
    setGreetMsg(await invoke('greet', { name: 'User' }))
  }

  return (
    <div className="container">
      <h1>Welcome to {project_name}</h1>
      <div className="row">
        <button onClick={() => greet()}>
          Greet
        </button>
      </div>
      {greetMsg && <p>{greetMsg}</p>}
    </div>
  )
}

export default App
"""
    
    def _template_tauri_vite_main(self) -> str:
        return """import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
"""
    
    def _template_tauri_package_json(self, config: DesktopConfig) -> str:
        return json.dumps({
            "name": config.project_name.lower().replace(" ", "-"),
            "private": True,
            "version": config.version,
            "type": "module",
            "scripts": {
                "dev": "vite",
                "build": "vite build",
                "preview": "vite preview",
                "tauri": "tauri"
            },
            "dependencies": {
                "@tauri-apps/api": "^1.5.0",
                "@tauri-apps/cli": "^1.5.0",
                "react": "^18.2.0",
                "react-dom": "^18.2.0"
            },
            "devDependencies": {
                "@types/react": "^18.2.0",
                "@types/react-dom": "^18.2.0",
                "@vitejs/plugin-react": "^4.0.0",
                "typescript": "^5.0.0",
                "vite": "^4.3.0"
            }
        }, indent=2)
    
    def _template_tauri_vite_config(self) -> str:
        return """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  build: {
    target: 'ES2020',
    minify: 'terser',
    sourcemap: false,
  },
  server: {
    strictPort: true,
    port: 5173,
  },
})
"""
    
    def _template_build_windows_script(self, config: DesktopConfig) -> str:
        return f"""# Build Windows EXE
Write-Host "Building {config.project_name} for Windows..." -ForegroundColor Green

npm install
npm run tauri build

$ExePath = "src-tauri/target/release/{config.project_name.lower().replace(' ', '_')}.exe"

if (Test-Path $ExePath) {{
    Write-Host "✅ EXE built: $ExePath" -ForegroundColor Green
    Write-Host "📦 Size: $(Get-Item $ExePath | Select-Object -ExpandProperty Length / 1MB)MB"
}} else {{
    Write-Host "❌ Build failed" -ForegroundColor Red
    exit 1
}}
"""
    
    def _template_build_macos_script(self, config: DesktopConfig) -> str:
        return f"""#!/bin/bash
set -e

echo "🔨 Building {config.project_name} for macOS..."

npm install
npm run tauri build

APP_PATH="src-tauri/target/release/bundle/macos/{config.project_name}.app"

if [ -d "$APP_PATH" ]; then
    echo "✅ App bundle created: $APP_PATH"
    du -sh "$APP_PATH"
else
    echo "❌ Build failed"
    exit 1
fi
"""
    
    def _template_build_linux_script(self, config: DesktopConfig) -> str:
        return f"""#!/bin/bash
set -e

echo "🔨 Building {config.project_name} for Linux..."

npm install
npm run tauri build

APPIMAGE="src-tauri/target/release/bundle/appimage/{config.project_name.replace(' ', '_')}.AppImage"

if [ -f "$APPIMAGE" ]; then
    echo "✅ AppImage created: $APPIMAGE"
    ls -lh "$APPIMAGE"
else
    echo "❌ Build failed"
    exit 1
fi
"""
    
    def _template_tauri_ci_workflow(self, config: DesktopConfig) -> str:
        return f"""name: Tauri Build

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [windows-latest, ubuntu-latest, macos-latest]
    
    steps:
      - uses: actions/checkout@v3
      
      - uses: actions-rs/toolchain@v1
        with:
          toolchain: stable
      
      - uses: pnpm/action-setup@v2
      - uses: actions/setup-node@v3
        with:
          node-version: 18
          cache: 'pnpm'
      
      - run: pnpm install
      - run: pnpm run build
      - run: pnpm run tauri build
      
      - uses: softprops/action-gh-release@v1
        if: startsWith(github.ref, 'refs/tags/')
        with:
          files: |
            src-tauri/target/release/bundle/**/*
"""
    
    # ============== ELECTRON TEMPLATES ==============
    
    def _template_electron_main(self, config: DesktopConfig) -> str:
        return f"""const {{ app, BrowserWindow, Menu, ipcMain }} = require('electron');
const isDev = require('electron-is-dev');
const path = require('path');

let mainWindow;

function createWindow() {{
  mainWindow = new BrowserWindow({{
    width: 1200,
    height: 800,
    webPreferences: {{
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true,
    }},
  }});

  const startUrl = isDev
    ? 'http://localhost:5173'
    : `file://${{__dirname}}/index.html`;

  mainWindow.loadURL(startUrl);

  if (isDev) {{
    mainWindow.webContents.openDevTools();
  }}

  mainWindow.on('closed', () => {{
    mainWindow = null;
  }});
}}

app.on('ready', createWindow);

app.on('window-all-closed', () => {{
  if (process.platform !== 'darwin') {{
    app.quit();
  }}
}});

app.on('activate', () => {{
  if (mainWindow === null) {{
    createWindow();
  }}
}});

// IPC handlers
ipcMain.handle('greet', (event, name) => {{
  return `Hello, ${{name}}!`;
}});
"""
    
    def _template_electron_preload(self) -> str:
        return """const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electron', {
  invoke: (channel, args) => ipcRenderer.invoke(channel, args),
  on: (channel, func) => ipcRenderer.on(channel, (event, ...args) => func(...args)),
});
"""
    
    def _template_electron_app(self, blueprint: Dict[str, Any]) -> str:
        return """import { useState } from 'react'

function App() {
  const [message, setMessage] = useState('')

  const handleGreet = async () => {
    const msg = await (window as any).electron.invoke('greet', 'User')
    setMessage(msg)
  }

  return (
    <div className="container">
      <h1>Welcome to Desktop App</h1>
      <button onClick={handleGreet}>Greet</button>
      {message && <p>{message}</p>}
    </div>
  )
}

export default App
"""
    
    def _template_electron_vite_main(self) -> str:
        return """import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
"""
    
    def _template_electron_package_json(self, config: DesktopConfig) -> str:
        return json.dumps({
            "name": config.project_name.lower().replace(" ", "-"),
            "version": config.version,
            "description": f"{config.project_name} - Desktop Application",
            "main": "public/electron.js",
            "homepage": "./",
            "scripts": {
                "react-start": "vite",
                "react-build": "vite build",
                "react-test": "vitest",
                "electron-start": "wait-on http://localhost:5173 && electron .",
                "start": "concurrently \"npm run react-start\" \"npm run electron-start\"",
                "build": "npm run react-build && electron-builder"
            },
            "dependencies": {
                "react": "^18.2.0",
                "react-dom": "^18.2.0"
            },
            "devDependencies": {
                "@types/react": "^18.2.0",
                "@types/react-dom": "^18.2.0",
                "@vitejs/plugin-react": "^4.0.0",
                "concurrently": "^8.0.0",
                "electron": "^latest",
                "electron-builder": "^latest",
                "electron-is-dev": "^2.0.0",
                "typescript": "^5.0.0",
                "vite": "^4.3.0",
                "wait-on": "^7.0.0"
            },
            "build": {
                "appId": config.project_id,
                "files": [
                    "public/electron.js",
                    "public/preload.js",
                    "dist/**/*"
                ],
                "directories": {
                    "buildResources": "assets"
                },
                "win": {
                    "target": ["nsis", "portable"]
                },
                "nsis": {
                    "oneClick": False,
                    "allowToChangeInstallationDirectory": True
                },
                "mac": {
                    "target": ["dmg", "zip"],
                    "category": "public.app-category.utilities"
                },
                "linux": {
                    "target": ["AppImage", "deb"]
                }
            }
        }, indent=2)
    
    def _template_electron_vite_config(self) -> str:
        return """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  build: {
    target: 'ES2020',
    minify: 'terser',
  },
  server: {
    port: 5173,
  },
})
"""
    
    def _template_electron_build_windows(self, config: DesktopConfig) -> str:
        return f"""@echo off
echo Building {config.project_name} for Windows...

call npm install
call npm run build

if exist "dist\\*.exe" (
    echo ✅ EXE created
    dir /s dist\\*.exe
) else (
    echo ❌ Build failed
    exit /b 1
)
"""
    
    def _template_electron_build_macos(self, config: DesktopConfig) -> str:
        return f"""#!/bin/bash
set -e

echo "🔨 Building {config.project_name} for macOS..."

npm install
npm run build

if [ -f "dist/{config.project_name}.dmg" ]; then
    echo "✅ DMG created"
    ls -lh "dist/{config.project_name}.dmg"
else
    echo "❌ Build failed"
    exit 1
fi
"""
    
    def _template_electron_build_linux(self, config: DesktopConfig) -> str:
        return f"""#!/bin/bash
set -e

echo "🔨 Building {config.project_name} for Linux..."

npm install
npm run build

if [ -f "dist/{config.project_name}.AppImage" ] || [ -f "dist/*.deb" ]; then
    echo "✅ Packages created"
    ls -lh dist/
else
    echo "❌ Build failed"
    exit 1
fi
"""
    
    def _template_electron_ci_workflow(self, config: DesktopConfig) -> str:
        return f"""name: Electron Build

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [windows-latest, ubuntu-latest, macos-latest]
    
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 18
      
      - run: npm install
      - run: npm run build
      
      - uses: softprops/action-gh-release@v1
        if: startsWith(github.ref, 'refs/tags/')
        with:
          files: dist/**/*
"""
    
    def _template_windows_installer(self, config: DesktopConfig) -> str:
        return f"""!include "MUI2.nsh"

Name "{config.project_name} {config.version}"
OutFile "{config.project_name}-Setup.exe"
InstallDir "$PROGRAMFILES\\{config.project_name.replace(' ', '')}"

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_LANGUAGE "English"

Section "Install"
  SetOutPath "$INSTDIR"
  File "dist\\{config.project_name}.exe"
  CreateDirectory "$SMPROGRAMS\\{config.project_name}"
  CreateShortcut "$SMPROGRAMS\\{config.project_name}\\{config.project_name}.lnk" "$INSTDIR\\{config.project_name}.exe"
SectionEnd

Section "Uninstall"
  Delete "$INSTDIR\\{config.project_name}.exe"
  RMDir "$INSTDIR"
SectionEnd
"""
    
    def _template_macos_dmg_config(self, config: DesktopConfig) -> str:
        return json.dumps({
            "title": config.project_name,
            "icon": "icon.icns",
            "contents": [
                {
                    "x": 410,
                    "y": 220,
                    "type": "link",
                    "path": "/Applications"
                },
                {
                    "x": 130,
                    "y": 220,
                    "type": "file"
                }
            ]
        }, indent=2)
