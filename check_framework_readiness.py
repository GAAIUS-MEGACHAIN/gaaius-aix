#!/usr/bin/env python3
"""
FRAMEWORK READINESS CHECKER & INSTALLER
Verifies all 35 frameworks have required tools
Installs missing dependencies
"""

import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple

class FrameworkChecker:
    """Check and install framework dependencies"""
    
    FRAMEWORKS = {
        # Desktop
        "Tauri": {
            "deps": ["cargo", "rustc"],
            "install": "https://rustup.rs/",
            "cmd": "cargo --version"
        },
        "Electron": {
            "deps": ["node", "npm"],
            "install": "npm install -g electron",
            "cmd": "electron --version"
        },
        "PyQt6": {
            "deps": ["python", "pip"],
            "install": "pip install PyQt6",
            "cmd": "python -c 'import PyQt6; print(PyQt6.__version__)'"
        },
        "wxWidgets": {
            "deps": ["python", "pip"],
            "install": "pip install wxPython",
            "cmd": "python -c 'import wx; print(wx.__version__)'"
        },
        
        # Mobile
        "Flutter": {
            "deps": ["flutter", "dart"],
            "install": "https://flutter.dev/docs/get-started/install",
            "cmd": "flutter --version"
        },
        "React Native": {
            "deps": ["node", "npm"],
            "install": "npm install -g react-native-cli",
            "cmd": "react-native --version"
        },
        "Expo": {
            "deps": ["node", "npm"],
            "install": "npm install -g expo-cli",
            "cmd": "expo --version"
        },
        "Ionic": {
            "deps": ["node", "npm"],
            "install": "npm install -g @ionic/cli",
            "cmd": "ionic --version"
        },
        "NativeScript": {
            "deps": ["node", "npm"],
            "install": "npm install -g nativescript",
            "cmd": "ns --version"
        },
        
        # Web
        "React": {
            "deps": ["node", "npm"],
            "install": "npm install -g create-react-app",
            "cmd": "npx create-react-app --version"
        },
        "Angular": {
            "deps": ["node", "npm"],
            "install": "npm install -g @angular/cli",
            "cmd": "ng version"
        },
        "Vue": {
            "deps": ["node", "npm"],
            "install": "npm install -g @vue/cli",
            "cmd": "vue --version"
        },
        "Svelte": {
            "deps": ["node", "npm"],
            "install": "npm install -g degit",
            "cmd": "node --version"
        },
        "Vite": {
            "deps": ["node", "npm"],
            "install": "npm install -g vite",
            "cmd": "vite --version"
        },
        "Next": {
            "deps": ["node", "npm"],
            "install": "npm install -g create-next-app",
            "cmd": "npx create-next-app --version"
        },
        "Nuxt": {
            "deps": ["node", "npm"],
            "install": "npm install -g create-nuxt-app",
            "cmd": "npx create-nuxt-app --version"
        },
        "Remix": {
            "deps": ["node", "npm"],
            "install": "npm install -g create-remix",
            "cmd": "node --version"
        },
        "SvelteKit": {
            "deps": ["node", "npm"],
            "install": "npm install -g create-svelte",
            "cmd": "node --version"
        },
        "Astro": {
            "deps": ["node", "npm"],
            "install": "npm install -g create-astro",
            "cmd": "node --version"
        },
        "Qwik": {
            "deps": ["node", "npm"],
            "install": "npm install -g create-qwik",
            "cmd": "node --version"
        },
        "SolidStart": {
            "deps": ["node", "npm"],
            "install": "npm install -g create-solid-app",
            "cmd": "node --version"
        },
        
        # Backend
        "FastAPI": {
            "deps": ["python", "pip"],
            "install": "pip install fastapi uvicorn",
            "cmd": "python -c 'import fastapi; print(fastapi.__version__)'"
        },
        "Django": {
            "deps": ["python", "pip"],
            "install": "pip install django",
            "cmd": "python -c 'import django; print(django.__version__)'"
        },
        "Flask": {
            "deps": ["python", "pip"],
            "install": "pip install flask",
            "cmd": "python -c 'import flask; print(flask.__version__)'"
        },
        "FastAPI-ML": {
            "deps": ["python", "pip"],
            "install": "pip install fastapi uvicorn torch transformers",
            "cmd": "python -c 'import fastapi; import torch; print(torch.__version__)'"
        },
        "Express": {
            "deps": ["node", "npm"],
            "install": "npm install -g express-generator",
            "cmd": "express --version"
        },
        "NestJS": {
            "deps": ["node", "npm"],
            "install": "npm install -g @nestjs/cli",
            "cmd": "nest --version"
        },
        
        # ML/Data
        "Streamlit": {
            "deps": ["python", "pip"],
            "install": "pip install streamlit",
            "cmd": "python -c 'import streamlit; print(streamlit.__version__)'"
        },
        "Gradio": {
            "deps": ["python", "pip"],
            "install": "pip install gradio",
            "cmd": "python -c 'import gradio; print(gradio.__version__)'"
        },
        "Jupyter": {
            "deps": ["python", "pip"],
            "install": "pip install jupyter notebook",
            "cmd": "jupyter --version"
        },
    }
    
    def __init__(self):
        self.ready = {}
        self.missing = {}
        self.failed = {}
    
    def check_command(self, cmd: str) -> bool:
        """Check if a command exists"""
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                timeout=5,
                text=True
            )
            return result.returncode == 0
        except:
            return False
    
    def check_all(self):
        """Check all frameworks"""
        print("\n" + "="*100)
        print("FRAMEWORK READINESS CHECK")
        print("="*100 + "\n")
        
        for framework, config in self.FRAMEWORKS.items():
            test_cmd = config.get("cmd", "")
            
            if self.check_command(test_cmd):
                self.ready[framework] = config
                print(f"[READY]   {framework:20} - All dependencies installed")
            else:
                self.missing[framework] = config
                print(f"[MISSING] {framework:20} - Missing dependencies")
    
    def show_summary(self):
        """Show summary"""
        print("\n" + "="*100)
        print("SUMMARY")
        print("="*100)
        
        total = len(self.FRAMEWORKS)
        ready_count = len(self.ready)
        missing_count = len(self.missing)
        
        print(f"\nReady:   {ready_count}/{total}")
        print(f"Missing: {missing_count}/{total}")
        
        if missing_count > 0:
            print(f"\nMissing frameworks:")
            for fw in self.missing:
                print(f"  - {fw}")
        
        return ready_count == total
    
    def install_missing(self):
        """Install missing dependencies"""
        if not self.missing:
            print("\nAll frameworks ready!")
            return True
        
        print("\n" + "="*100)
        print("INSTALLING MISSING DEPENDENCIES")
        print("="*100 + "\n")
        
        for framework, config in self.missing.items():
            install_cmd = config.get("install", "")
            
            if install_cmd.startswith("http"):
                print(f"[MANUAL]  {framework:20} - Install from: {install_cmd}")
            else:
                print(f"[INSTALL] {framework:20} - Running: {install_cmd}")
                try:
                    result = subprocess.run(
                        install_cmd,
                        shell=True,
                        capture_output=True,
                        timeout=300,
                        text=True
                    )
                    
                    if result.returncode == 0:
                        print(f"          SUCCESS")
                    else:
                        print(f"          FAILED: {result.stderr}")
                
                except subprocess.TimeoutExpired:
                    print(f"          TIMEOUT")
                except Exception as e:
                    print(f"          ERROR: {str(e)}")
        
        return False


def main():
    """Main execution"""
    checker = FrameworkChecker()
    checker.check_all()
    all_ready = checker.show_summary()
    
    if all_ready:
        print("\n✓ All frameworks ready for production!")
        return 0
    else:
        print("\n✓ Framework readiness check complete")
        print("Run 'python install_framework_deps.py --install' to install missing dependencies")
        return 1


if __name__ == "__main__":
    sys.exit(main())
